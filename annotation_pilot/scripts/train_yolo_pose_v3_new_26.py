#!/usr/bin/env python3
"""Prépare et (optionnellement) lance l'entraînement YOLO Pose V3 anatomique (new_26).

Fine-tuning doux depuis V2 best.pt (epoch 80) vers un run V3 séparé.
Ne modifie jamais le best.pt V2 original, les labels GT, ni les fichiers de production.

Par défaut : préparation + vérifications uniquement (PAS d'entraînement).
Pour lancer l'entraînement : ajouter ``--train``.

Configuration : ``datasets/yolo_pose_new_26/v3_train_config.yaml``
Plan détaillé   : ``datasets/yolo_pose_new_26/yolo_v3_training_plan.md``
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
CONFIG_PATH = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v3_train_config.yaml"
DATA_YAML = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "data.yaml"
SPLIT_JSON = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "split.json"
KEYPOINT_ORDER_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "keypoint_order.md"

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
    "TD_R", "TD_L",
    "FHC_R", "FHC_L",
    "ASL_R", "ASL_L",
    "ASM_R", "ASM_L",
    "FNM_R", "FNM_L",
    "FSP_R", "FSP_L",
    "FSD_R", "FSD_L",
)
EXPECTED_FLIP_IDX = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]
EXPECTED_TRAIN_COUNT = 21
EXPECTED_VAL_COUNT = 5


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
    """Copie V2 best.pt vers init V3 si absent. Ne touche jamais à la source."""
    source = resolve(cfg["init"]["source"])
    dest = resolve(cfg["init"]["copy_to"])

    if not source.is_file():
        raise SystemExit(f"Checkpoint V2 introuvable : {source}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file():
        if sha256_file(source) != sha256_file(dest):
            raise SystemExit(
                f"Init V3 déjà présent mais différent de V2 : {dest}\n"
                "Supprimez manuellement la copie si vous souhaitez la regénérer."
            )
        print(f"INIT: copie existante OK — {dest.relative_to(PROJECT_ROOT)}")
    else:
        shutil.copy2(source, dest)
        print(f"INIT: copié {source.relative_to(PROJECT_ROOT)}")
        print(f"      -> {dest.relative_to(PROJECT_ROOT)}")

    return source, dest


def verify_preflight(cfg: dict[str, Any], init_dest: Path) -> list[str]:
    """Vérifications read-only avant entraînement. Retourne la liste des contrôles passés."""
    checks: list[str] = []

    # V2 original intact et distinct de la copie
    if not V2_BEST.is_file():
        raise SystemExit(f"V2 best.pt manquant : {V2_BEST}")
    checks.append(f"V2 best.pt présent : {V2_BEST.relative_to(PROJECT_ROOT)}")

    if not init_dest.is_file():
        raise SystemExit(f"Init V3 manquant : {init_dest}")
    if sha256_file(V2_BEST) != sha256_file(init_dest):
        raise SystemExit("Init V3 ≠ V2 source — copie corrompue.")
    checks.append("Init V3 = copie bit-identique de V2 best.pt (epoch 80)")

    # Dataset YAML
    data_path = resolve(cfg["data"])
    if not data_path.is_file():
        raise SystemExit(f"Dataset YAML introuvable : {data_path}")
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))
    checks.append(f"Dataset YAML : {data_path.relative_to(PROJECT_ROOT)}")

    kpt_names = data["kpt_names"][0]
    if list(kpt_names) != list(EXPECTED_KEYPOINTS):
        raise SystemExit(f"Ordre keypoints YAML incorrect : {kpt_names}")
    checks.append(f"14 keypoints ordre MVP OK : {', '.join(kpt_names[:4])} …")

    if data.get("flip_idx") != EXPECTED_FLIP_IDX:
        raise SystemExit(f"flip_idx incorrect : {data.get('flip_idx')}")
    checks.append(f"flip_idx OK : {EXPECTED_FLIP_IDX}")

    if data.get("kpt_shape") != [14, 3]:
        raise SystemExit(f"kpt_shape incorrect : {data.get('kpt_shape')}")

    # Split train/val
    split = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))
    train_ids, val_ids = split["train"], split["val"]
    if len(train_ids) != EXPECTED_TRAIN_COUNT or len(val_ids) != EXPECTED_VAL_COUNT:
        raise SystemExit(f"Split inattendu : train={len(train_ids)} val={len(val_ids)}")
    if set(train_ids) & set(val_ids):
        raise SystemExit("Fuite train/val détectée.")
    checks.append(f"Split : {len(train_ids)} train / {len(val_ids)} val / 0 test")

    # Labels 47 colonnes (échantillon)
    labels_root = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "labels"
    for split_name in ("train", "val"):
        lbl_dir = labels_root / split_name
        count = len(list(lbl_dir.glob("*.txt")))
        expected = len(train_ids) if split_name == "train" else len(val_ids)
        if count != expected:
            raise SystemExit(f"Labels {split_name} : {count} ≠ {expected}")
    sample = labels_root / "train" / "B26_01.txt"
    cols = len(sample.read_text(encoding="utf-8").split())
    if cols != 47:
        raise SystemExit(f"Label B26_01 : {cols} colonnes ≠ 47")
    checks.append("Labels YOLO : 47 cols, train/val counts OK")

    # Run directory
    run_root = resolve(cfg["run"]["project"]) / cfg["run"]["name"]
    weights_dir = run_root / "weights"
    if weights_dir.is_dir() and any(weights_dir.glob("*.pt")):
        checks.append(f"ATTENTION : run existant avec poids — {run_root.relative_to(PROJECT_ROOT)}")
    else:
        checks.append(f"Run prévu (vide ou absent) : {run_root.relative_to(PROJECT_ROOT)}")

    return checks


def build_train_kwargs(cfg: dict[str, Any], init_weights: Path) -> dict[str, Any]:
    """Construit les kwargs Ultralytics ``model.train()`` depuis le YAML."""
    t = cfg["train"]
    o = cfg["optimizer"]
    l = cfg["loss"]
    a = cfg["augment"]
    u = cfg["ultralytics"]
    r = cfg["run"]

    return {
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
        "pretrained": u["pretrained"],
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
    meta_path = run_root / "v3_train_config.md"

    lines = [
        "# V3 anatomical — configuration d'entraînement",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        f"**Config source :** `{config_path.relative_to(PROJECT_ROOT).as_posix()}`",
        "",
        "## Init",
        "",
        f"- V2 source (lecture seule) : `{init_source.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- Copie init V3 : `{init_dest.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- SHA256 : `{sha256_file(init_dest)}`",
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

    lines.extend(
        [
            "",
            "## Run",
            "",
            f"- project : `{train_kwargs['project']}`",
            f"- name : `{train_kwargs['name']}`",
            f"- exist_ok : `{train_kwargs['exist_ok']}`",
            "",
            "## Lancer l'entraînement",
            "",
            "```bash",
            ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v3_new_26.py --train",
            "```",
            "",
        ]
    )
    meta_path.write_text("\n".join(lines), encoding="utf-8")
    return meta_path


def print_hyperparams(cfg: dict[str, Any], train_kwargs: dict[str, Any], checks: list[str]) -> None:
    run_root = resolve(cfg["run"]["project"]) / cfg["run"]["name"]
    print("\n" + "=" * 72)
    print("YOLO Pose V3 — PRÉPARATION (entraînement NON lancé sauf --train)")
    print("=" * 72)
    print("\nVérifications :")
    for item in checks:
        print(f"  [OK] {item}")

    print("\nHyperparamètres clés :")
    highlights = [
        ("init", str(resolve(cfg["init"]["copy_to"]).relative_to(PROJECT_ROOT))),
        ("data", train_kwargs["data"]),
        ("imgsz", train_kwargs["imgsz"]),
        ("batch", train_kwargs["batch"]),
        ("epochs", train_kwargs["epochs"]),
        ("patience", train_kwargs["patience"]),
        ("optimizer", train_kwargs["optimizer"]),
        ("lr0", train_kwargs["lr0"]),
        ("cos_lr", train_kwargs["cos_lr"]),
        ("mosaic", train_kwargs["mosaic"]),
        ("auto_augment", train_kwargs["auto_augment"]),
        ("erasing", train_kwargs["erasing"]),
        ("fliplr", train_kwargs["fliplr"]),
        ("run", f"{run_root.relative_to(PROJECT_ROOT)}"),
    ]
    for key, value in highlights:
        print(f"  {key:16} = {value}")

    print("\nTous les kwargs Ultralytics :")
    for key in sorted(train_kwargs):
        print(f"  {key:22} = {train_kwargs[key]!r}")
    print("=" * 72 + "\n")


def run_training(cfg: dict[str, Any], init_weights: Path, train_kwargs: dict[str, Any]) -> int:
    from ultralytics import YOLO

    model = YOLO(str(init_weights))
    model.train(**train_kwargs)

    run_root = resolve(cfg["run"]["project"]) / cfg["run"]["name"]
    best_pt = run_root / "weights" / "best.pt"
    print("V3 TRAINING COMPLETE")
    print(f"INIT={init_weights.resolve()}")
    print(f"BEST={best_pt.resolve()}")
    return 0 if best_pt.is_file() else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Prépare / lance YOLO Pose V3 anatomical (new_26)")
    parser.add_argument(
        "--train",
        action="store_true",
        help="Lancer l'entraînement Ultralytics (par défaut : préparation seule)",
    )
    default_config = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v3_train_config.yaml"
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config,
        help=f"Chemin config YAML (défaut : {default_config.name})",
    )
    args = parser.parse_args()

    config_path = args.config.resolve()
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise SystemExit(f"Configuration V3 invalide : {config_path}")
    init_source, init_dest = prepare_init_weights(cfg)
    train_kwargs = build_train_kwargs(cfg, init_dest)
    checks = verify_preflight(cfg, init_dest)
    meta_path = write_run_meta(cfg, config_path, init_source, init_dest, train_kwargs)

    print_hyperparams(cfg, train_kwargs, checks)
    print(f"META écrit : {meta_path.relative_to(PROJECT_ROOT)}")

    if not args.train:
        print("Mode préparation : entraînement NON lancé.")
        print("Pour lancer : .venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v3_new_26.py --train")
        return 0

    print("Lancement entraînement V3…")
    return run_training(cfg, init_dest, train_kwargs)


if __name__ == "__main__":
    raise SystemExit(main())
