#!/usr/bin/env python3
"""Comparaison pixel-level V2 vs V3 + géométrie (new_26).

Critère : V3 meilleure seulement si ASL_L baisse significativement sans dégrader
fortement les autres landmarks focus.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
SPLIT_JSON = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "split.json"
V2_LABELS = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
V3_LABELS = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v3" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
V2_GEOM = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_geometry_results.csv"
V3_GEOM = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v3_geometry_results.csv"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v3_vs_v2_landmark_comparison.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v3_vs_v2_landmark_comparison.md"

LANDMARKS = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L", "ASM_R", "ASM_L",
    "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L",
]
FOCUS = ("ASL_R", "ASL_L", "ASM_L", "FHC_L", "FNM_L")
KEYPOINTS_START = 5
MIN_KEYPOINT_CONF = 0.25
NKPT = 14
ASL_IMPROVE_RATIO = 0.20
OTHER_DEGRADE_RATIO = 0.25
TONNIS_EXTREME_ABS = 150.0


def format_num(v: float | None, d: int = 2) -> str:
    return "NA" if v is None else f"{v:.{d}f}"


def load_split() -> tuple[set[str], set[str]]:
    data = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))
    return set(data["train"]), set(data["val"])


def image_dimensions(annotation: dict, case_id: str) -> tuple[float, float]:
    w, h = annotation.get("image_width"), annotation.get("image_height")
    if w and h:
        return float(w), float(h)
    from PIL import Image

    with Image.open(IMAGE_DIR / f"{case_id}.png") as img:
        return float(img.size[0]), float(img.size[1])


def parse_pred(path: Path, width: float, height: float) -> dict[str, tuple[float, float] | None]:
    if not path.is_file():
        return {}
    values = path.read_text(encoding="utf-8").strip().split()
    kpts = [float(v) for v in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    out: dict[str, tuple[float, float] | None] = {}
    for i, name in enumerate(LANDMARKS):
        x, y, c = kpts[i * 3], kpts[i * 3 + 1], kpts[i * 3 + 2]
        out[name] = (x * width, y * height) if c >= MIN_KEYPOINT_CONF else None
    return out


def load_gt(annotation: dict) -> dict[str, tuple[float, float]]:
    pts: dict[str, tuple[float, float]] = {}
    for lm in annotation.get("landmarks", []):
        if lm.get("v") == 2 and lm.get("name") in LANDMARKS:
            pts[lm["name"]] = (float(lm["x"]), float(lm["y"]))
    return pts


def errors_for_version(label_dir: Path, train_ids: set[str], val_ids: set[str]) -> dict[tuple[str, str, str], float]:
    """(version, split, landmark) -> mean error px. version in v2/v3."""
    version = label_dir.parent.name.replace("predictions_", "")
    buckets: dict[tuple[str, str], list[float]] = {}
    for json_path in sorted(ANNOT_DIR.glob("B26_*.json")):
        case_id = json_path.stem
        split = "train" if case_id in train_ids else "val"
        ann = json.loads(json_path.read_text(encoding="utf-8-sig"))
        w, h = image_dimensions(ann, case_id)
        gt = load_gt(ann)
        pred = parse_pred(label_dir / f"{case_id}.txt", w, h)
        for name in LANDMARKS:
            if name not in gt or pred.get(name) is None:
                continue
            err = math.hypot(pred[name][0] - gt[name][0], pred[name][1] - gt[name][1])
            buckets.setdefault((split, name), []).append(err)
    return {
        (version, split, name): statistics.mean(vals)
        for (split, name), vals in buckets.items()
    }


def load_geom(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_vce_l_negative(rows: list[dict[str, str]]) -> int:
    n = 0
    for row in rows:
        v = row.get("VCE_L", "").strip()
        if v and float(v) < 0:
            n += 1
    return n


def count_tonnis_l_extreme(rows: list[dict[str, str]]) -> int:
    n = 0
    for row in rows:
        v = row.get("Tonnis_L", "").strip()
        if not v:
            continue
        fv = float(v)
        if abs(fv) > TONNIS_EXTREME_ABS or fv < -15 or fv > 165:
            n += 1
    return n


def assess_winner(v2: dict, v3: dict, train_ids: set[str], val_ids: set[str]) -> tuple[str, str]:
    asl_l_v2 = statistics.mean([v2[("v2", "train", "ASL_L")], v2[("v2", "val", "ASL_L")]])
    asl_l_v3 = statistics.mean([v3[("v3", "train", "ASL_L")], v3[("v3", "val", "ASL_L")]])
    asl_improved = asl_l_v3 < asl_l_v2 * (1 - ASL_IMPROVE_RATIO)

    degraded = []
    for lm in FOCUS:
        if lm == "ASL_L":
            continue
        for split in ("train", "val"):
            k2, k3 = ("v2", split, lm), ("v3", split, lm)
            if k2 in v2 and k3 in v3 and v3[k3] > v2[k2] * (1 + OTHER_DEGRADE_RATIO):
                degraded.append(f"{lm}_{split}")

    if asl_improved and not degraded:
        return "V3", "ASL_L ↓ significatif, autres landmarks focus stables."
    if asl_improved and degraded:
        return "INCONCLUSIVE", f"ASL_L ↓ mais dégradation : {', '.join(degraded)}"
    return "V2", "ASL_L V3 n'a pas baissé de ≥20 % vs V2 (critère pixel-level)."


def write_outputs(v2: dict, v3: dict, v2_geom: list[dict], v3_geom: list[dict], verdict: str, detail: str) -> None:
    rows: list[dict[str, str]] = []
    for split in ("train", "val"):
        for lm in FOCUS:
            rows.append(
                {
                    "section": "landmark_mean_px",
                    "split": split,
                    "landmark": lm,
                    "v2": format_num(v2.get(("v2", split, lm))),
                    "v3": format_num(v3.get(("v3", split, lm))),
                    "delta_v3_minus_v2": format_num(
                        (v3.get(("v3", split, lm)) or 0) - (v2.get(("v2", split, lm)) or 0)
                        if ("v3", split, lm) in v3 and ("v2", split, lm) in v2
                        else None
                    ),
                }
            )

    rows.append({"section": "geometry", "split": "all", "landmark": "VCE_L_negative_count", "v2": str(count_vce_l_negative(v2_geom)), "v3": str(count_vce_l_negative(v3_geom)), "delta_v3_minus_v2": ""})
    rows.append({"section": "geometry", "split": "all", "landmark": "Tonnis_L_extreme_count", "v2": str(count_tonnis_l_extreme(v2_geom)), "v3": str(count_tonnis_l_extreme(v3_geom)), "delta_v3_minus_v2": ""})
    rows.append({"section": "verdict", "split": "", "landmark": verdict, "v2": "", "v3": detail, "delta_v3_minus_v2": ""})

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["section", "split", "landmark", "v2", "v3", "delta_v3_minus_v2"])
        w.writeheader()
        w.writerows(rows)

    lines = [
        "# Comparaison V2 vs V3 — landmarks & géométrie",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "**Critère :** validation pixel-level obligatoire (pas seulement mAP).",
        "",
        f"## Verdict : **{verdict}**",
        "",
        detail,
        "",
        "## Erreurs moyennes (px) — landmarks focus",
        "",
        "| Landmark | V2 train | V3 train | V2 val | V3 val |",
        "|----------|----------|----------|--------|--------|",
    ]
    for lm in FOCUS:
        lines.append(
            f"| {lm} | {format_num(v2.get(('v2','train',lm)))} | {format_num(v3.get(('v3','train',lm)))} | "
            f"{format_num(v2.get(('v2','val',lm)))} | {format_num(v3.get(('v3','val',lm)))} |"
        )

    lines.extend(
        [
            "",
            "## ASL_L (critère principal)",
            "",
            f"- V2 ASL_L train : **{format_num(v2.get(('v2','train','ASL_L')))} px**",
            f"- V3 ASL_L train : **{format_num(v3.get(('v3','train','ASL_L')))} px**",
            f"- V2 ASL_L val : **{format_num(v2.get(('v2','val','ASL_L')))} px**",
            f"- V3 ASL_L val : **{format_num(v3.get(('v3','val','ASL_L')))} px**",
            "",
            "## Géométrie gauche",
            "",
            f"- V2 VCE_L négatifs : **{count_vce_l_negative(v2_geom)}** / 26",
            f"- V3 VCE_L négatifs : **{count_vce_l_negative(v3_geom)}** / 26",
            f"- V2 Tönnis_L extrêmes : **{count_tonnis_l_extreme(v2_geom)}** / 26",
            f"- V3 Tönnis_L extrêmes : **{count_tonnis_l_extreme(v3_geom)}** / 26",
            "",
            "## Tous les landmarks (mean px, train+val pooled)",
            "",
            "| Landmark | V2 | V3 | Δ |",
            "|----------|----|----|---|",
        ]
    )
    for lm in LANDMARKS:
        v2_all = [v2.get(("v2", s, lm)) for s in ("train", "val") if ("v2", s, lm) in v2]
        v3_all = [v3.get(("v3", s, lm)) for s in ("train", "val") if ("v3", s, lm) in v3]
        if v2_all and v3_all:
            m2, m3 = statistics.mean(v2_all), statistics.mean(v3_all)
            lines.append(f"| {lm} | {format_num(m2)} | {format_num(m3)} | {format_num(m3 - m2)} |")

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    train_ids, val_ids = load_split()
    if not V3_LABELS.is_dir():
        raise SystemExit(f"Prédictions V3 absentes : {V3_LABELS} — lancer inference V3 d'abord.")

    v2 = errors_for_version(V2_LABELS, train_ids, val_ids)
    v3 = errors_for_version(V3_LABELS, train_ids, val_ids)
    v2_geom = load_geom(V2_GEOM)
    v3_geom = load_geom(V3_GEOM)
    verdict, detail = assess_winner(v2, v3, train_ids, val_ids)
    write_outputs(v2, v3, v2_geom, v3_geom, verdict, detail)

    print("V2 vs V3 COMPARISON COMPLETE")
    print(f"Verdict: {verdict}")
    print(f"V2 ASL_L train: {format_num(v2.get(('v2','train','ASL_L')))} px")
    print(f"V3 ASL_L train: {format_num(v3.get(('v3','train','ASL_L')))} px")
    print(f"V2 ASL_L val: {format_num(v2.get(('v2','val','ASL_L')))} px")
    print(f"V3 ASL_L val: {format_num(v3.get(('v3','val','ASL_L')))} px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
