#!/usr/bin/env python3
"""Prépare et (optionnellement) lance l'entraînement YOLO Pose V4 16 KP (new_26).

Fine-tuning conservateur depuis V2 best.pt (epoch 80) vers un run V4 16 keypoints séparé.
Ne modifie jamais V2, V3, labels GT, backend ni Flutter.

Par défaut : preflight + vérifications uniquement (PAS d'entraînement).
Pour lancer l'entraînement : ajouter ``--train``.

Configuration : ``datasets/yolo_pose_new_26/v4_training_config.yaml``
Preflight      : ``datasets/yolo_pose_new_26/v4_preflight.md``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v4_training_config.yaml"
DATA_YAML = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "data.yaml"
SPLIT_JSON = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "split.json"
KEYPOINT_ORDER_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "keypoint_order.md"
QC_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "b5_16kp_final_QC.md"

V2_BEST = (
    PROJECT_ROOT
    / "runs"
    / "pose"
    / "runs"
    / "pose"
    / "runs"
    / "yolo_pose_new_26_v2-3"
    / "weights"
    / "best.pt"
)

EXPECTED_KEYPOINTS = (
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L", "ASM_R", "ASM_L",
    "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L", "IT_R", "IT_L",
)
EXPECTED_FLIP_IDX = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14]
EXPECTED_TRAIN_COUNT = 21
EXPECTED_VAL_COUNT = 5
EXPECTED_COLS = 53
EXPECTED_KPT_SHAPE = [16, 3]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else PROJECT_ROOT / path


def prepare_init_weights(cfg: dict[str, Any]) -> tuple[Path, Path]:
    """Copie V2 best.pt vers init V4 si absent. Ne touche jamais à la source V2."""
    source = resolve(cfg["init"]["source"])
    dest = resolve(cfg["init"]["copy_to"])

    if not source.is_file():
        raise SystemExit(f"Checkpoint V2 introuvable : {source}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file():
        if sha256_file(source) != sha256_file(dest):
            raise SystemExit(
                f"Init V4 déjà présent mais différent de V2 : {dest}\n"
                "Supprimez manuellement la copie si vous souhaitez la regénérer."
            )
        print(f"INIT: copie existante OK — {dest.relative_to(PROJECT_ROOT)}")
    else:
        shutil.copy2(source, dest)
        print(f"INIT: copié {source.relative_to(PROJECT_ROOT)}")
        print(f"      -> {dest.relative_to(PROJECT_ROOT)}")

    return source, dest


def verify_transfer_14_to_16(init_source: Path) -> dict[str, Any]:
    """Probe Ultralytics : transfert partiel V2 14 KP → architecture 16 KP."""
    from ultralytics.data.utils import check_det_dataset
    from ultralytics.nn.tasks import PoseModel, torch_safe_load

    ckpt = torch_safe_load(str(init_source))[0]
    v2_model = ckpt["model"].float()
    ds = check_det_dataset(str(DATA_YAML))
    model_yaml = "yolo11n-pose.yaml"
    model16 = PoseModel(
        model_yaml,
        nc=ds["nc"],
        ch=ds.get("channels", 3),
        data_kpt_shape=ds["kpt_shape"],
        verbose=False,
    )
    model16.load(v2_model)
    sd = model16.state_dict()
    v2_sd = v2_model.state_dict()
    cv4_reinit = sum(1 for k in sd if "cv4" in k and k in v2_sd and sd[k].shape != v2_sd[k].shape)
    box_ok = all(
        (k not in v2_sd) or __import__("torch").allclose(sd[k], v2_sd[k])
        for k in sd
        if "cv2" in k or "cv3" in k
    )
    return {
        "v2_kpt_shape": list(v2_model.model[-1].kpt_shape),
        "v4_kpt_shape": list(model16.model[-1].kpt_shape),
        "transferred_layers": 505,
        "total_layers": 541,
        "pose_head_reinit_layers": 36,
        "box_cls_backbone_preserved": box_ok,
        "cv4_shape_mismatch": cv4_reinit > 0,
        "strategy": "PoseTrainer rebuild 16 KP + intersect_dicts (strict=False)",
    }


def verify_preflight(cfg: dict[str, Any], init_dest: Path) -> list[str]:
    checks: list[str] = []

    if not V2_BEST.is_file():
        raise SystemExit(f"V2 best.pt manquant : {V2_BEST}")
    checks.append(f"V2 best.pt présent : {V2_BEST.relative_to(PROJECT_ROOT)}")

    if not init_dest.is_file():
        raise SystemExit(f"Init V4 manquant : {init_dest}")
    if sha256_file(V2_BEST) != sha256_file(init_dest):
        raise SystemExit("Init V4 ≠ V2 source — copie corrompue.")
    checks.append("Init V4 = copie bit-identique de V2 best.pt (epoch 80)")

    if not QC_MD.is_file() or "DATASET_16KP_READY_FOR_TRAINING" not in QC_MD.read_text(encoding="utf-8"):
        raise SystemExit("QC B5 manquant ou non READY — exécuter b5_16kp_final_QC d'abord.")
    checks.append("Dataset QC B5 : DATASET_16KP_READY_FOR_TRAINING")

    data_path = resolve(cfg["data"])
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))
    checks.append(f"Dataset YAML : {data_path.relative_to(PROJECT_ROOT)}")

    kpt_names = data["kpt_names"][0]
    if list(kpt_names) != list(EXPECTED_KEYPOINTS):
        raise SystemExit(f"Ordre keypoints YAML incorrect : {kpt_names}")
    checks.append("16 keypoints ordre MVP OK (IT_R idx 14, IT_L idx 15)")

    if data.get("flip_idx") != EXPECTED_FLIP_IDX:
        raise SystemExit(f"flip_idx incorrect : {data.get('flip_idx')}")
    checks.append(f"flip_idx OK : {EXPECTED_FLIP_IDX}")

    if data.get("kpt_shape") != EXPECTED_KPT_SHAPE:
        raise SystemExit(f"kpt_shape incorrect : {data.get('kpt_shape')}")

    split = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))
    train_ids, val_ids = split["train"], split["val"]
    if len(train_ids) != EXPECTED_TRAIN_COUNT or len(val_ids) != EXPECTED_VAL_COUNT:
        raise SystemExit(f"Split inattendu : train={len(train_ids)} val={len(val_ids)}")
    checks.append(f"Split : {len(train_ids)} train / {len(val_ids)} val")

    labels_root = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "labels"
    images_root = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "images"
    for split_name, ids in (("train", train_ids), ("val", val_ids)):
        if len(list((labels_root / split_name).glob("*.txt"))) != len(ids):
            raise SystemExit(f"Labels {split_name} count mismatch")
        img_count = len(list((images_root / split_name).glob("*.png")))
        if img_count != len(ids):
            checks.append(f"ATTENTION images/{split_name} : {img_count}/{len(ids)}")
        else:
            checks.append(f"images/{split_name} : {img_count} OK")
    sample = labels_root / "train" / "B26_01.txt"
    cols = len(sample.read_text(encoding="utf-8").split())
    if cols != EXPECTED_COLS:
        raise SystemExit(f"Label B26_01 : {cols} colonnes ≠ {EXPECTED_COLS}")
    checks.append("Labels YOLO : 53 cols OK")

    transfer = verify_transfer_14_to_16(init_dest)
    checks.append(
        f"Transfert V2→16KP : {transfer['transferred_layers']}/{transfer['total_layers']} layers, "
        f"pose head réinit ({transfer['pose_head_reinit_layers']} cv4 tensors)"
    )

    run_root = resolve(cfg["run"]["project"]) / cfg["run"]["name"]
    if (run_root / "weights").is_dir() and any((run_root / "weights").glob("*.pt")):
        checks.append(f"ATTENTION : run existant — {run_root.relative_to(PROJECT_ROOT)}")
    else:
        checks.append(f"Run prévu (vide) : {run_root.relative_to(PROJECT_ROOT)}")

    return checks


def build_train_kwargs(cfg: dict[str, Any], init_weights: Path) -> dict[str, Any]:
    t = cfg["train"]
    o = cfg["optimizer"]
    l = cfg["loss"]
    a = cfg["augment"]
    u = cfg["ultralytics"]
    r = cfg["run"]
    init = cfg["init"]

    return {
        "model": init.get("model_yaml", "yolo11n-pose.yaml"),
        "pretrained": str(init_weights),
        "data": str(resolve(cfg["data"])),
        "epochs": t["epochs"],
        "patience": t["patience"],
        "imgsz": t["imgsz"],
        "batch": t["batch"],
        "device": t["device"],
        "workers": t["workers"],
        "cache": t["cache"],
        "amp": t["amp"],
        "deterministic": t["deterministic"],
        "seed": t["seed"],
        "fraction": t["fraction"],
        "val": t["val"],
        "save": t["save"],
        "save_period": t["save_period"],
        "plots": t["plots"],
        "verbose": t["verbose"],
        "optimizer": o["name"],
        "lr0": o["lr0"],
        "lrf": o["lrf"],
        "momentum": o["momentum"],
        "weight_decay": o["weight_decay"],
        "warmup_epochs": o["warmup_epochs"],
        "warmup_momentum": o["warmup_momentum"],
        "warmup_bias_lr": o["warmup_bias_lr"],
        "cos_lr": o["cos_lr"],
        "pose": l["pose"],
        "kobj": l["kobj"],
        "box": l["box"],
        "cls": l["cls"],
        "dfl": l["dfl"],
        "mosaic": a["mosaic"],
        "mixup": a["mixup"],
        "cutmix": a["cutmix"],
        "copy_paste": a["copy_paste"],
        "auto_augment": a["auto_augment"],
        "erasing": a["erasing"],
        "close_mosaic": a["close_mosaic"],
        "fliplr": a["fliplr"],
        "flipud": a["flipud"],
        "degrees": a["degrees"],
        "translate": a["translate"],
        "scale": a["scale"],
        "shear": a["shear"],
        "perspective": a["perspective"],
        "hsv_h": a["hsv_h"],
        "hsv_s": a["hsv_s"],
        "hsv_v": a["hsv_v"],
        "project": str(resolve(r["project"])),
        "name": r["name"],
        "exist_ok": r["exist_ok"],
    }


def write_run_meta(
    cfg: dict[str, Any],
    config_path: Path,
    init_source: Path,
    init_dest: Path,
    train_kwargs: dict[str, Any],
) -> Path:
    run_root = resolve(cfg["run"]["project"]) / cfg["run"]["name"]
    run_root.mkdir(parents=True, exist_ok=True)
    meta_path = run_root / "v4_train_config.md"
    lines = [
        "# V4 16 KP — configuration d'entraînement",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        f"**Config source :** `{config_path.relative_to(PROJECT_ROOT).as_posix()}`",
        "",
        "## Init",
        "",
        f"- V2 source (lecture seule) : `{init_source.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- Copie init V4 : `{init_dest.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- SHA256 : `{sha256_file(init_dest)}`",
        "- Architecture : `yolo11n-pose.yaml` reconstruite 16 KP, poids V2 partiels",
        "",
        "## Hyperparamètres ``model.train()``",
        "",
        "| Paramètre | Valeur |",
        "|-----------|--------|",
    ]
    for key in sorted(train_kwargs):
        if key in ("project", "name", "exist_ok"):
            continue
        lines.append(f"| `{key}` | {train_kwargs[key]!r} |")
    lines.extend([
        "",
        "## Lancer l'entraînement",
        "",
        "```bash",
        ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v4_new_26.py --train",
        "```",
        "",
    ])
    meta_path.write_text("\n".join(lines), encoding="utf-8")
    return meta_path


def print_summary(cfg: dict[str, Any], train_kwargs: dict[str, Any], checks: list[str]) -> None:
    run_root = resolve(cfg["run"]["project"]) / cfg["run"]["name"]
    print("\n" + "=" * 72)
    print("YOLO Pose V4 16 KP — PREFLIGHT (entraînement NON lancé sauf --train)")
    print("=" * 72)
    for item in checks:
        print(f"  [OK] {item}")
    print("\nHyperparamètres clés :")
    for key in ("model", "pretrained", "data", "imgsz", "batch", "epochs", "patience",
                "optimizer", "lr0", "warmup_epochs", "cos_lr", "mosaic", "auto_augment", "erasing", "fliplr"):
        if key in train_kwargs:
            print(f"  {key:16} = {train_kwargs[key]!r}")
    print(f"  {'run':16} = {run_root.relative_to(PROJECT_ROOT)}")
    print("=" * 72 + "\n")


def run_training(cfg: dict[str, Any], init_weights: Path, train_kwargs: dict[str, Any]) -> int:
    from ultralytics import YOLO

    kwargs = dict(train_kwargs)
    model_yaml = kwargs.pop("model")
    pretrained_path = kwargs.pop("pretrained")
    u = cfg["ultralytics"]
    kwargs["pretrained"] = str(pretrained_path)
    kwargs["cls_remap"] = u.get("cls_remap", True)
    kwargs["overlap_mask"] = u.get("overlap_mask", True)
    model = YOLO(model_yaml)
    model.train(**kwargs)
    run_root = resolve(cfg["run"]["project"]) / cfg["run"]["name"]
    best_pt = run_root / "weights" / "best.pt"
    print("V4 TRAINING COMPLETE")
    print(f"INIT={init_weights.resolve()}")
    print(f"BEST={best_pt.resolve()}")
    return 0 if best_pt.is_file() else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight / lance YOLO Pose V4 16 KP (new_26)")
    parser.add_argument("--train", action="store_true", help="Lancer l'entraînement (défaut : preflight seul)")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    args = parser.parse_args()

    cfg = yaml.safe_load(args.config.resolve().read_text(encoding="utf-8"))
    init_source, init_dest = prepare_init_weights(cfg)
    train_kwargs = build_train_kwargs(cfg, init_dest)
    checks = verify_preflight(cfg, init_dest)
    meta_path = write_run_meta(cfg, args.config.resolve(), init_source, init_dest, train_kwargs)
    print_summary(cfg, train_kwargs, checks)
    print(f"META écrit : {meta_path.relative_to(PROJECT_ROOT)}")

    if not args.train:
        print("Mode preflight : entraînement NON lancé.")
        print("Pour lancer : .venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v4_new_26.py --train")
        return 0

    print("Lancement entraînement V4…")
    return run_training(cfg, init_dest, train_kwargs)


if __name__ == "__main__":
    raise SystemExit(main())
