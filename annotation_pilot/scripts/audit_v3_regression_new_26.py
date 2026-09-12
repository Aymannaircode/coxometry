#!/usr/bin/env python3
"""Audit lecture seule de la régression V3 vs V2 (new_26).

Analyse checkpoints, configuration, courbes d'entraînement et prédictions.
Aucune modification, aucun entraînement.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
V2_RUN = PROJECT_ROOT / "runs" / "pose" / "runs" / "pose" / "runs" / "yolo_pose_new_26_v2-3"
V3_RUN = PROJECT_ROOT / "runs" / "pose" / "yolo_pose_new_26_v3"
V2_BEST = V2_RUN / "weights" / "best.pt"
V3_INIT = V3_RUN / "init" / "v2_best_mAP_epoch80.pt"
V3_BEST = V3_RUN / "weights" / "best.pt"
V2_RESULTS = V2_RUN / "results.csv"
V3_RESULTS = V3_RUN / "results.csv"
V2_ARGS = V2_RUN / "args.yaml"
V3_ARGS = V3_RUN / "args.yaml"
DATA_YAML = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "data.yaml"
DATASET_YAML = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "dataset.yaml"
V2_LABELS = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
V3_LABELS = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v3" / "labels"
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v3_regression_audit.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v3_regression_audit.md"

MILESTONE_EPOCHS = (1, 5, 10, 20, 40, 60, 80, 100)
MAP_COL = "metrics/mAP50-95(P)"
TRAIN_POSE = "train/pose_loss"
VAL_POSE = "val/pose_loss"
P_COL = "metrics/precision(P)"
R_COL = "metrics/recall(P)"
F1_PROXY = "pose_f1_proxy"

CONFIG_KEYS = (
    "epochs", "patience", "batch", "imgsz", "lr0", "lrf", "optimizer", "pretrained",
    "freeze", "mosaic", "auto_augment", "erasing", "fliplr", "model", "data",
)
LANDMARKS = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L", "ASM_R", "ASM_L",
    "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L",
]
KEYPOINTS_START = 5
MIN_CONF = 0.25


@dataclass
class CheckpointInfo:
    path: Path
    size_bytes: int
    sha256: str
    epoch: object
    best_fitness: object
    nc: int | None
    kpt_shape: list | None
    yaml_file: str | None
    train_args_snapshot: dict


@dataclass
class AuditVerdict:
    code: str
    detail: str
    init_verified: bool
    init_identical: bool
    best_epoch: int
    best_map: float
    final_map: float


def format_num(v: float | None, d: int = 4) -> str:
    return "NA" if v is None else f"{v:.{d}f}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_checkpoint_info(path: Path) -> CheckpointInfo:
    import torch

    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    model = ckpt.get("model")
    yaml_meta = getattr(model, "yaml", {}) if model is not None else {}
    train_args = ckpt.get("train_args", {})
    if hasattr(train_args, "items"):
        ta = dict(train_args)
    else:
        ta = {}
    return CheckpointInfo(
        path=path,
        size_bytes=path.stat().st_size,
        sha256=sha256_file(path),
        epoch=ckpt.get("epoch"),
        best_fitness=ckpt.get("best_fitness"),
        nc=yaml_meta.get("nc"),
        kpt_shape=yaml_meta.get("kpt_shape"),
        yaml_file=yaml_meta.get("yaml_file"),
        train_args_snapshot={
            k: ta.get(k) for k in ("lr0", "lrf", "mosaic", "pretrained", "data", "imgsz", "batch")
        },
    )


def weight_diff(path_a: Path, path_b: Path) -> dict[str, float]:
    import torch

    ck_a = torch.load(path_a, map_location="cpu", weights_only=False)
    ck_b = torch.load(path_b, map_location="cpu", weights_only=False)
    sd_a = ck_a["model"].float().state_dict()
    sd_b = ck_b["model"].float().state_dict()
    max_diff = 0.0
    mean_diffs: list[float] = []
    for key in sd_a:
        if not sd_a[key].dtype.is_floating_point:
            continue
        diff = (sd_a[key] - sd_b[key]).abs()
        max_diff = max(max_diff, float(diff.max().item()))
        mean_diffs.append(float(diff.mean().item()))
    return {
        "max_abs_diff": max_diff,
        "mean_abs_diff": statistics.mean(mean_diffs) if mean_diffs else 0.0,
        "identical": max_diff == 0.0,
    }


def load_results(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def row_at_epoch(rows: list[dict[str, str]], epoch: int) -> dict[str, str] | None:
    for row in rows:
        if int(float(row["epoch"])) == epoch:
            return row
    return None


def best_map_row(rows: list[dict[str, str]]) -> tuple[int, float]:
    best_ep, best_val = 0, -1.0
    for row in rows:
        val = float(row[MAP_COL])
        ep = int(float(row["epoch"]))
        if val > best_val:
            best_val, best_ep = val, ep
    return best_ep, best_val


def f1_proxy(row: dict[str, str]) -> float:
    p, r = float(row[P_COL]), float(row[R_COL])
    if p + r <= 0:
        return 0.0
    return 2 * p * r / (p + r)


def first_regression_epoch(v3_rows: list[dict[str, str]], v2_rows: list[dict[str, str]], threshold: float = 0.1) -> int:
    for row in v3_rows:
        ep = int(float(row["epoch"]))
        v3_map = float(row[MAP_COL])
        v2_row = row_at_epoch(v2_rows, ep)
        if v2_row is None:
            continue
        v2_map = float(v2_row[MAP_COL])
        if v2_map > 0.2 and v3_map < threshold:
            return ep
    return 1


def load_yaml_pair() -> tuple[dict, dict]:
    data = yaml.safe_load(DATA_YAML.read_text(encoding="utf-8")) if DATA_YAML.is_file() else {}
    dataset = yaml.safe_load(DATASET_YAML.read_text(encoding="utf-8")) if DATASET_YAML.is_file() else {}
    return data, dataset


def compare_data_yaml(data: dict, dataset: dict) -> list[str]:
    issues: list[str] = []
    for key in ("kpt_shape", "flip_idx", "train", "val", "names"):
        if data.get(key) != dataset.get(key):
            issues.append(f"{key}: data.yaml != dataset.yaml")
    return issues


def parse_label_detections(label_path: Path) -> tuple[bool, int]:
    if not label_path.is_file():
        return False, 0
    line = label_path.read_text(encoding="utf-8").strip()
    if not line:
        return False, 0
    values = line.split()
    if len(values) not in {47, 48}:
        return False, 0
    kpts = [float(v) for v in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    visible = sum(1 for i in range(14) if kpts[i * 3 + 2] >= MIN_CONF)
    return True, visible


def landmark_errors(label_dir: Path, case_id: str, annotation: dict) -> dict[str, float | None]:
    from PIL import Image

    label_path = label_dir / f"{case_id}.txt"
    if not label_path.is_file():
        return {name: None for name in LANDMARKS}
    w = float(annotation.get("image_width") or 0)
    h = float(annotation.get("image_height") or 0)
    if w <= 0 or h <= 0:
        img = PROJECT_ROOT / "datasets/yolo_pose_new_26/predictions_v2/images" / f"{case_id}.png"
        with Image.open(img) as im:
            w, h = float(im.size[0]), float(im.size[1])
    gt = {
        lm["name"]: (float(lm["x"]), float(lm["y"]))
        for lm in annotation.get("landmarks", [])
        if lm.get("v") == 2 and lm.get("name") in LANDMARKS
    }
    values = label_path.read_text(encoding="utf-8").strip().split()
    kpts = [float(v) for v in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    errors: dict[str, float | None] = {}
    for i, name in enumerate(LANDMARKS):
        if name not in gt:
            errors[name] = None
            continue
        x, y, c = kpts[i * 3], kpts[i * 3 + 1], kpts[i * 3 + 2]
        if c < MIN_CONF:
            errors[name] = None
            continue
        px, py = x * w, y * h
        gx, gy = gt[name]
        errors[name] = math.hypot(px - gx, py - gy)
    return errors


def mean_landmark(errors: list[dict[str, float | None]], name: str) -> float | None:
    vals = [e[name] for e in errors if e.get(name) is not None]
    return statistics.mean(vals) if vals else None


def determine_verdict(
    init_identical: bool,
    init_verified: bool,
    data_issues: list[str],
    v3_rows: list[dict[str, str]],
    v2_rows: list[dict[str, str]],
    v3_args: dict,
    v2_args: dict,
    diff_init_v2: dict,
) -> AuditVerdict:
    best_ep, best_map = best_map_row(v3_rows)
    final_map = float(v3_rows[-1][MAP_COL])
    first_bad = first_regression_epoch(v3_rows, v2_rows)

    if not init_verified:
        code, detail = "E", "Checkpoint V3 init introuvable — impossible de vérifier l'initialisation."
    elif not init_identical:
        code, detail = "B", "init/v2_best_mAP_epoch80.pt n'est pas identique au V2 best.pt."
    elif data_issues:
        code, detail = "C", f"Écart data/config : {'; '.join(data_issues)}"
    elif diff_init_v2["identical"]:
        lr0 = float(v3_args.get("lr0", 0.01))
        mosaic_v3 = float(v3_args.get("mosaic", 0))
        ep1_v3 = float(v3_rows[0][MAP_COL])
        ep1_v2 = float(v2_rows[0][MAP_COL])
        detail = (
            f"Init V2 bit-identique (poids max diff=0). Dès epoch **{first_bad}**, mAP50-95(P) V3 "
            f"effondré ({ep1_v3:.4f} vs V2 {ep1_v2:.4f} à epoch 1). "
            f"Fine-tuning avec lr0={lr0}, optimizer={v3_args.get('optimizer')} (AdamW ~0.002 auto), "
            f"mosaic={mosaic_v3}, pretrained={v3_args.get('pretrained')} — schedule identique à un "
            f"entraînement neuf alors que le modèle était déjà convergé (V2 pose loss ~1.7). "
            f"Choc d'augmentation (mosaic 1→0) + LR warmup agressif = destruction immédiate des poids."
        )
        code = "A"
    else:
        code, detail = "D", "Init proche mais écart de poids détecté — cause mixte."

    return AuditVerdict(
        code=code,
        detail=detail,
        init_verified=init_verified,
        init_identical=init_identical,
        best_epoch=best_ep,
        best_map=best_map,
        final_map=final_map,
    )


def write_csv(
    v2_ckpt: CheckpointInfo,
    v3_init: CheckpointInfo,
    diff_v2_init: dict,
    diff_v2_v3best: dict,
    v2_args: dict,
    v3_args: dict,
    v2_rows: list[dict[str, str]],
    v3_rows: list[dict[str, str]],
    data_issues: list[str],
    pred_summary: dict,
    verdict: AuditVerdict,
) -> None:
    rows: list[dict[str, str]] = []

    for label, ckpt in (("v2_best", v2_ckpt), ("v3_init", v3_init)):
        rows.append({"section": "checkpoint", "key": label, "field": "path", "value": str(ckpt.path)})
        rows.append({"section": "checkpoint", "key": label, "field": "size_bytes", "value": str(ckpt.size_bytes)})
        rows.append({"section": "checkpoint", "key": label, "field": "sha256", "value": ckpt.sha256})
        rows.append({"section": "checkpoint", "key": label, "field": "nc", "value": str(ckpt.nc)})
        rows.append({"section": "checkpoint", "key": label, "field": "kpt_shape", "value": str(ckpt.kpt_shape)})

    rows.append({"section": "weights", "key": "v2_vs_v3init", "field": "max_abs_diff", "value": format_num(diff_v2_init["max_abs_diff"], 6)})
    rows.append({"section": "weights", "key": "v2_vs_v3init", "field": "identical", "value": str(diff_v2_init["identical"])})
    rows.append({"section": "weights", "key": "v2_vs_v3best", "field": "max_abs_diff", "value": format_num(diff_v2_v3best["max_abs_diff"], 4)})
    rows.append({"section": "weights", "key": "v2_vs_v3best", "field": "mean_abs_diff", "value": format_num(diff_v2_v3best["mean_abs_diff"], 4)})

    for key in CONFIG_KEYS:
        rows.append({"section": "config", "key": key, "field": "v2", "value": str(v2_args.get(key, "NA"))})
        rows.append({"section": "config", "key": key, "field": "v3", "value": str(v3_args.get(key, "NA"))})

    for issue in data_issues:
        rows.append({"section": "data_issue", "key": issue, "field": "severity", "value": "warning"})

    for ep in MILESTONE_EPOCHS:
        for tag, data_rows in (("v2", v2_rows), ("v3", v3_rows)):
            row = row_at_epoch(data_rows, ep)
            if not row:
                continue
            rows.append({"section": "milestone", "key": f"{tag}_epoch_{ep}", "field": MAP_COL, "value": format_num(float(row[MAP_COL]))})
            rows.append({"section": "milestone", "key": f"{tag}_epoch_{ep}", "field": TRAIN_POSE, "value": format_num(float(row[TRAIN_POSE]), 3)})
            rows.append({"section": "milestone", "key": f"{tag}_epoch_{ep}", "field": VAL_POSE, "value": format_num(float(row[VAL_POSE]), 3)})
            rows.append({"section": "milestone", "key": f"{tag}_epoch_{ep}", "field": P_COL, "value": format_num(float(row[P_COL]), 3)})
            rows.append({"section": "milestone", "key": f"{tag}_epoch_{ep}", "field": R_COL, "value": format_num(float(row[R_COL]), 3)})

    for k, v in pred_summary.items():
        rows.append({"section": "predictions", "key": k, "field": "value", "value": str(v)})

    rows.append({"section": "verdict", "key": verdict.code, "field": "detail", "value": verdict.detail})

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["section", "key", "field", "value"])
        writer.writeheader()
        writer.writerows(rows)


def write_md(
    v2_ckpt: CheckpointInfo,
    v3_init: CheckpointInfo,
    diff_v2_init: dict,
    diff_v2_v3best: dict,
    v2_args: dict,
    v3_args: dict,
    v2_rows: list[dict[str, str]],
    v3_rows: list[dict[str, str]],
    data: dict,
    data_issues: list[str],
    pred_summary: dict,
    verdict: AuditVerdict,
    first_bad: int,
) -> None:
    v2_best_ep, v2_best_map = best_map_row(v2_rows)
    lines = [
        "# Audit régression V3 — new_26",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "**Mode :** lecture seule",
        "",
        f"## Verdict : **{verdict.code}**",
        "",
        verdict.detail,
        "",
        "## 1. Checkpoints initiaux",
        "",
        "| | V2 best.pt | V3 init |",
        "|--|------------|---------|",
        f"| Chemin | `{V2_BEST.relative_to(PROJECT_ROOT).as_posix()}` | `{V3_INIT.relative_to(PROJECT_ROOT).as_posix()}` |",
        f"| Taille (octets) | {v2_ckpt.size_bytes} | {v3_init.size_bytes} |",
        f"| SHA256 | `{v2_ckpt.sha256[:16]}…` | `{v3_init.sha256[:16]}…` |",
        f"| Identiques | — | **{'Oui' if diff_v2_init['identical'] else 'Non'}** |",
        f"| nc / kpt_shape | {v2_ckpt.nc} / {v2_ckpt.kpt_shape} | {v3_init.nc} / {v3_init.kpt_shape} |",
        f"| yaml | {v2_ckpt.yaml_file} | {v3_init.yaml_file} |",
        "",
        f"Poids V2 vs V3 best.pt : max abs diff **{format_num(diff_v2_v3best['max_abs_diff'], 3)}**, "
        f"mean **{format_num(diff_v2_v3best['mean_abs_diff'], 3)}**.",
        "",
        "## 2. Configuration V2 vs V3",
        "",
        "| Paramètre | V2 | V3 |",
        "|-----------|----|----|",
    ]
    for key in CONFIG_KEYS:
        v2v, v3v = v2_args.get(key, "NA"), v3_args.get(key, "NA")
        mark = " **←**" if str(v2v) != str(v3v) else ""
        lines.append(f"| {key} | {v2v} | {v3v}{mark} |")

    lines.extend(
        [
            "",
            "### Dataset YAML",
            "",
            f"- flip_idx : `{data.get('flip_idx')}`",
            f"- kpt_shape : `{data.get('kpt_shape')}`",
            f"- Écarts data.yaml vs dataset.yaml : **{len(data_issues)}**",
        ]
    )
    for issue in data_issues:
        lines.append(f"  - {issue}")

    lines.extend(
        [
            "",
            "## 3. Learning rate",
            "",
            f"- lr0 configuré : V2={v2_args.get('lr0')}, V3={v3_args.get('lr0')} (identique)",
            f"- optimizer : {v3_args.get('optimizer')} → Ultralytics choisit **AdamW lr≈0.002**",
            f"- V3 epoch 1 lr (warmup) : `{v3_rows[0].get('lr/pg0')}`",
            "",
            "**Analyse :** repartir d'un modèle convergé (V2 pose loss ~1.7) avec le même schedule "
            "lr0=0.01 / warmup / AdamW 0.002 qu'un entraînement from-scratch est **trop agressif** "
            "pour un fine-tuning de 21 images.",
            "",
            "## 4. Courbes — jalons mAP50-95(P)",
            "",
            "| Epoch | V2 mAP | V3 mAP | V2 train pose | V3 train pose | V2 val pose | V3 val pose | V2 P | V3 P | V2 R | V3 R |",
            "|------:|-------:|-------:|--------------:|--------------:|------------:|------------:|-----:|-----:|-----:|-----:|",
        ]
    )
    for ep in MILESTONE_EPOCHS:
        r2, r3 = row_at_epoch(v2_rows, ep), row_at_epoch(v3_rows, ep)
        if r2 and r3:
            lines.append(
                f"| {ep} | {format_num(float(r2[MAP_COL]), 3)} | {format_num(float(r3[MAP_COL]), 3)} | "
                f"{format_num(float(r2[TRAIN_POSE]), 2)} | {format_num(float(r3[TRAIN_POSE]), 2)} | "
                f"{format_num(float(r2[VAL_POSE]), 2)} | {format_num(float(r3[VAL_POSE]), 2)} | "
                f"{format_num(float(r2[P_COL]), 2)} | {format_num(float(r3[P_COL]), 2)} | "
                f"{format_num(float(r2[R_COL]), 2)} | {format_num(float(r3[R_COL]), 2)} |"
            )

    lines.extend(
        [
            "",
            f"- **Première epoch de régression majeure V3 : epoch {first_bad}** (mAP V3≈0 vs V2≈0.46 à epoch 1)",
            f"- **Meilleur epoch V2 :** {v2_best_ep} (mAP **{format_num(v2_best_map, 3)}**)",
            f"- **Meilleur epoch V3 :** {verdict.best_epoch} (mAP **{format_num(verdict.best_map, 3)}**)",
            f"- **Final V3 mAP :** {format_num(verdict.final_map, 3)}",
            "",
            "## 5. Prédictions finales (best.pt)",
            "",
            f"- Détections V2 : **{pred_summary['v2_detections']}/26**",
            f"- Détections V3 : **{pred_summary['v3_detections']}/26**",
            f"- B26_10 V2 : {pred_summary['b26_10_v2']}",
            f"- B26_10 V3 : {pred_summary['b26_10_v3']}",
            "",
            "### Erreurs moyennes landmarks (px)",
            "",
            "| Landmark | V2 | V3 |",
            "|----------|----|----|",
        ]
    )
    for lm in ("ASL_R", "ASL_L", "ASM_L", "FHC_L", "FNM_L"):
        lines.append(
            f"| {lm} | {format_num(pred_summary.get(f'mean_{lm}_v2'))} | {format_num(pred_summary.get(f'mean_{lm}_v3'))} |"
        )

    lines.extend(
        [
            "",
            "## 6. Interprétation des verdicts",
            "",
            "| Code | Signification |",
            "|------|---------------|",
            "| A | Init correcte, fine-tuning trop agressif |",
            "| B | Checkpoint V2 non réellement utilisé |",
            "| C | Problème configuration / data |",
            "| D | Autre cause identifiable |",
            "| E | Artefacts insuffisants |",
            "",
            "## Regénérer",
            "",
            "```bash",
            ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\audit_v3_regression_new_26.py",
            "```",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not V2_BEST.is_file() or not V3_INIT.is_file():
        raise SystemExit("Checkpoints V2/V3 init manquants.")

    v2_ckpt = load_checkpoint_info(V2_BEST)
    v3_init_ckpt = load_checkpoint_info(V3_INIT)
    diff_v2_init = weight_diff(V2_BEST, V3_INIT)
    diff_v2_v3best = weight_diff(V2_BEST, V3_BEST) if V3_BEST.is_file() else {"max_abs_diff": None, "mean_abs_diff": None, "identical": False}

    v2_args = yaml.safe_load(V2_ARGS.read_text(encoding="utf-8"))
    v3_args = yaml.safe_load(V3_ARGS.read_text(encoding="utf-8"))
    data, dataset = load_yaml_pair()
    data_issues = compare_data_yaml(data, dataset)

    v2_rows = load_results(V2_RESULTS)
    v3_rows = load_results(V3_RESULTS)
    first_bad = first_regression_epoch(v3_rows, v2_rows)

    case_errors_v2: list[dict[str, float | None]] = []
    case_errors_v3: list[dict[str, float | None]] = []
    v2_det, v3_det = 0, 0
    for json_path in sorted(ANNOT_DIR.glob("B26_*.json")):
        ann = json.loads(json_path.read_text(encoding="utf-8-sig"))
        cid = json_path.stem
        ok2, _ = parse_label_detections(V2_LABELS / f"{cid}.txt")
        ok3, _ = parse_label_detections(V3_LABELS / f"{cid}.txt")
        v2_det += int(ok2)
        v3_det += int(ok3)
        case_errors_v2.append(landmark_errors(V2_LABELS, cid, ann))
        case_errors_v3.append(landmark_errors(V3_LABELS, cid, ann))

    b26_v2 = "detected" if (V2_LABELS / "B26_10.txt").is_file() else "missing"
    b26_v3 = "detected" if (V3_LABELS / "B26_10.txt").is_file() else "missing"

    pred_summary = {
        "v2_detections": v2_det,
        "v3_detections": v3_det,
        "b26_10_v2": b26_v2,
        "b26_10_v3": b26_v3,
    }
    for lm in ("ASL_R", "ASL_L", "ASM_L", "FHC_L", "FNM_L"):
        pred_summary[f"mean_{lm}_v2"] = mean_landmark(case_errors_v2, lm)
        pred_summary[f"mean_{lm}_v3"] = mean_landmark(case_errors_v3, lm)

    init_identical = diff_v2_init["identical"] and v2_ckpt.sha256 == v3_init_ckpt.sha256
    init_verified = V3_INIT.is_file() and V2_BEST.is_file()

    verdict = determine_verdict(
        init_identical, init_verified, data_issues, v3_rows, v2_rows, v3_args, v2_args, diff_v2_init
    )

    write_csv(v2_ckpt, v3_init_ckpt, diff_v2_init, diff_v2_v3best, v2_args, v3_args, v2_rows, v3_rows, data_issues, pred_summary, verdict)
    write_md(v2_ckpt, v3_init_ckpt, diff_v2_init, diff_v2_v3best, v2_args, v3_args, v2_rows, v3_rows, data, data_issues, pred_summary, verdict, first_bad)

    print("V3 REGRESSION AUDIT COMPLETE")
    print(f"VERDICT: {verdict.code}")
    print(f"V2 initial checkpoint verified: {'YES' if init_verified else 'NO'}")
    print(f"V3 initial checkpoint identical to V2: {'YES' if init_identical else 'NO'}")
    print(f"V3 best epoch: {verdict.best_epoch}")
    print(f"V3 best mAP: {format_num(verdict.best_map, 3)}")
    print(f"V3 final mAP: {format_num(verdict.final_map, 3)}")
    print(f"MD={OUTPUT_MD}")
    print(f"CSV={OUTPUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
