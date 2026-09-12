#!/usr/bin/env python3
"""Comparaison pixel-level V2 vs V4 + géométrie + décision GO/NO-GO (new_26).

Mesure les 14 landmarks séparément en TRAIN et VAL.
Compare VCE/Tönnis/CCD R/L. Produit v4_vs_v2_decision.md.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
SPLIT_JSON = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "split.json"
V2_LABELS = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
V4_LABELS = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v4" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
V2_GEOM = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_geometry_results.csv"
V4_GEOM = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v4_geometry_results.csv"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v4_vs_v2_landmark_comparison.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v4_vs_v2_landmark_comparison.md"
DECISION_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v4_vs_v2_decision.md"

LANDMARKS = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L", "ASM_R", "ASM_L",
    "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L",
]
CRITICAL_OTHER = ("ASL_R", "ASM_L", "ASM_R", "FHC_L", "FHC_R", "FNM_L")
KEYPOINTS_START = 5
MIN_KEYPOINT_CONF = 0.25
ASL_IMPROVE_RATIO = 0.20
OTHER_DEGRADE_RATIO = 0.25
TONNIS_EXTREME_ABS = 150.0
CCD_MEDIAN_DRIFT_DEG = 20.0
MIN_DETECTIONS = 26
V2_BASELINE = {
    "ASL_L_train": 538.18,
    "ASL_L_val": 471.72,
}


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
    version = label_dir.parent.name.replace("predictions_", "")
    buckets: dict[tuple[str, str], list[float]] = {}
    detections = 0
    for json_path in sorted(ANNOT_DIR.glob("B26_*.json")):
        case_id = json_path.stem
        split = "train" if case_id in train_ids else "val"
        ann = json.loads(json_path.read_text(encoding="utf-8-sig"))
        w, h = image_dimensions(ann, case_id)
        gt = load_gt(ann)
        pred_path = label_dir / f"{case_id}.txt"
        if pred_path.is_file():
            detections += 1
        pred = parse_pred(pred_path, w, h)
        for name in LANDMARKS:
            if name not in gt or pred.get(name) is None:
                continue
            err = math.hypot(pred[name][0] - gt[name][0], pred[name][1] - gt[name][1])
            buckets.setdefault((split, name), []).append(err)
    out = {
        (version, split, name): statistics.mean(vals)
        for (split, name), vals in buckets.items()
    }
    out[(version, "all", "detections")] = float(detections)
    return out


def load_geom(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_vce_negative(rows: list[dict[str, str]], side: str) -> int:
    n = 0
    for row in rows:
        v = row.get(f"VCE_{side}", "").strip()
        if v and float(v) < 0:
            n += 1
    return n


def count_tonnis_extreme(rows: list[dict[str, str]], side: str) -> int:
    n = 0
    for row in rows:
        v = row.get(f"Tonnis_{side}", "").strip()
        if not v:
            continue
        fv = float(v)
        if abs(fv) > TONNIS_EXTREME_ABS or fv < -15 or fv > 165:
            n += 1
    return n


def median_measure(rows: list[dict[str, str]], measure: str, side: str) -> float | None:
    vals: list[float] = []
    for row in rows:
        v = row.get(f"{measure}_{side}", "").strip()
        if v:
            vals.append(float(v))
    return statistics.median(vals) if vals else None


def assess_go_nogo(v2: dict, v4: dict, v2_geom: list[dict], v4_geom: list[dict]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    failures: list[str] = []

    asl_l_v2_train = v2.get(("v2", "train", "ASL_L"), V2_BASELINE["ASL_L_train"])
    asl_l_v2_val = v2.get(("v2", "val", "ASL_L"), V2_BASELINE["ASL_L_val"])
    asl_l_v4_train = v4.get(("v4", "train", "ASL_L"))
    asl_l_v4_val = v4.get(("v4", "val", "ASL_L"))

    if asl_l_v4_train is None or asl_l_v4_val is None:
        failures.append("ASL_L : métriques V4 manquantes")
    else:
        train_ok = asl_l_v4_train <= asl_l_v2_train * (1 - ASL_IMPROVE_RATIO)
        val_ok = asl_l_v4_val <= asl_l_v2_val * (1 - ASL_IMPROVE_RATIO)
        reasons.append(
            f"ASL_L train : V2={asl_l_v2_train:.1f} → V4={asl_l_v4_train:.1f} px "
            f"({'OK' if train_ok else 'FAIL'}, seuil −{ASL_IMPROVE_RATIO*100:.0f}%)"
        )
        reasons.append(
            f"ASL_L val : V2={asl_l_v2_val:.1f} → V4={asl_l_v4_val:.1f} px "
            f"({'OK' if val_ok else 'FAIL'}, seuil −{ASL_IMPROVE_RATIO*100:.0f}%)"
        )
        if not (train_ok and val_ok):
            failures.append("ASL_L n'a pas baissé de ≥20 % sur train ET val")

    for lm in CRITICAL_OTHER:
        for split in ("train", "val"):
            k2, k4 = ("v2", split, lm), ("v4", split, lm)
            if k2 not in v2 or k4 not in v4:
                continue
            if v4[k4] > v2[k2] * (1 + OTHER_DEGRADE_RATIO):
                failures.append(f"{lm} {split} dégradé >25 % ({v2[k2]:.1f}→{v4[k4]:.1f} px)")

    det_v4 = int(v4.get(("v4", "all", "detections"), 0))
    reasons.append(f"Détections V4 : {det_v4}/{MIN_DETECTIONS}")
    if det_v4 < MIN_DETECTIONS:
        failures.append(f"Détections insuffisantes : {det_v4}/{MIN_DETECTIONS}")

    for side in ("R", "L"):
        v2_neg = count_vce_negative(v2_geom, side)
        v4_neg = count_vce_negative(v4_geom, side)
        reasons.append(f"VCE_{side} négatifs : V2={v2_neg}/26, V4={v4_neg}/26")
        if v4_neg > v2_neg:
            failures.append(f"VCE_{side} négatifs V4 pire que V2 ({v4_neg}>{v2_neg})")

        v2_tex = count_tonnis_extreme(v2_geom, side)
        v4_tex = count_tonnis_extreme(v4_geom, side)
        reasons.append(f"Tönnis_{side} extrêmes : V2={v2_tex}/26, V4={v4_tex}/26")
        if v4_tex > v2_tex:
            failures.append(f"Tönnis_{side} extrêmes V4 pire que V2 ({v4_tex}>{v2_tex})")

        for measure in ("CCD",):
            m2 = median_measure(v2_geom, measure, side)
            m4 = median_measure(v4_geom, measure, side)
            if m2 is not None and m4 is not None:
                drift = abs(m4 - m2)
                reasons.append(f"{measure}_{side} médiane : V2={m2:.1f}°, V4={m4:.1f}° (Δ={drift:.1f}°)")
                if drift > CCD_MEDIAN_DRIFT_DEG:
                    failures.append(f"{measure}_{side} dérive médiane >{CCD_MEDIAN_DRIFT_DEG}° vs V2")

    if failures:
        return "NO-GO", reasons + ["", "Échecs :"] + [f"- {f}" for f in failures]
    return "GO", reasons


def write_outputs(
    v2: dict,
    v4: dict,
    v2_geom: list[dict],
    v4_geom: list[dict],
    verdict: str,
    detail_lines: list[str],
) -> None:
    rows: list[dict[str, str]] = []
    for split in ("train", "val"):
        for lm in LANDMARKS:
            k2, k4 = ("v2", split, lm), ("v4", split, lm)
            rows.append(
                {
                    "section": "landmark_mean_px",
                    "split": split,
                    "landmark": lm,
                    "v2": format_num(v2.get(k2)),
                    "v4": format_num(v4.get(k4)),
                    "delta_v4_minus_v2": format_num(
                        (v4.get(k4) or 0) - (v2.get(k2) or 0)
                        if k4 in v4 and k2 in v2
                        else None
                    ),
                }
            )

    for side in ("R", "L"):
        for measure in ("VCE", "Tonnis", "CCD"):
            m2 = median_measure(v2_geom, measure, side)
            m4 = median_measure(v4_geom, measure, side)
            rows.append(
                {
                    "section": "geometry_median",
                    "split": side,
                    "landmark": measure,
                    "v2": format_num(m2, 1),
                    "v4": format_num(m4, 1),
                    "delta_v4_minus_v2": format_num((m4 or 0) - (m2 or 0) if m2 and m4 else None, 1),
                }
            )

    rows.append({"section": "verdict", "split": "", "landmark": verdict, "v2": "", "v4": "", "delta_v4_minus_v2": ""})

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["section", "split", "landmark", "v2", "v4", "delta_v4_minus_v2"])
        w.writeheader()
        w.writerows(rows)

    lines = [
        "# Comparaison V2 vs V4 — landmarks & géométrie",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "**Baseline :** V2 | **Candidate :** V4",
        "**Critère :** validation pixel-level obligatoire (mAP secondaire).",
        "",
        f"## Verdict : **{verdict}**",
        "",
        *detail_lines,
        "",
        "## Erreurs moyennes (px) — 14 landmarks",
        "",
        "| Landmark | V2 train | V4 train | V2 val | V4 val |",
        "|----------|----------|----------|--------|--------|",
    ]
    for lm in LANDMARKS:
        lines.append(
            f"| {lm} | {format_num(v2.get(('v2','train',lm)))} | {format_num(v4.get(('v4','train',lm)))} | "
            f"{format_num(v2.get(('v2','val',lm)))} | {format_num(v4.get(('v4','val',lm)))} |"
        )

    lines.extend(
        [
            "",
            "## Géométrie R/L",
            "",
            "| Mesure | V2 R | V4 R | V2 L | V4 L |",
            "|--------|------|------|------|------|",
        ]
    )
    for measure in ("VCE", "Tonnis", "CCD"):
        lines.append(
            f"| {measure} (médiane °) | "
            f"{format_num(median_measure(v2_geom, measure, 'R'), 1)} | "
            f"{format_num(median_measure(v4_geom, measure, 'R'), 1)} | "
            f"{format_num(median_measure(v2_geom, measure, 'L'), 1)} | "
            f"{format_num(median_measure(v4_geom, measure, 'L'), 1)} |"
        )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision = [
        "# Décision GO / NO-GO — V4 vs V2",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        f"**Verdict : {verdict}**",
        "",
        *detail_lines,
        "",
        f"Voir aussi : `{OUTPUT_MD.name}`, `{OUTPUT_CSV.name}`",
    ]
    DECISION_MD.write_text("\n".join(decision) + "\n", encoding="utf-8")


def main() -> int:
    train_ids, val_ids = load_split()
    if not V4_LABELS.is_dir():
        raise SystemExit(f"Prédictions V4 absentes : {V4_LABELS} — lancer inference V4 d'abord.")

    v2 = errors_for_version(V2_LABELS, train_ids, val_ids)
    v4 = errors_for_version(V4_LABELS, train_ids, val_ids)
    v2_geom = load_geom(V2_GEOM)
    v4_geom = load_geom(V4_GEOM)
    verdict, detail_lines = assess_go_nogo(v2, v4, v2_geom, v4_geom)
    write_outputs(v2, v4, v2_geom, v4_geom, verdict, detail_lines)

    print("V2 vs V4 COMPARISON COMPLETE")
    print(f"Verdict: {verdict}")
    print(f"V2 ASL_L train: {format_num(v2.get(('v2','train','ASL_L')))} px")
    print(f"V4 ASL_L train: {format_num(v4.get(('v4','train','ASL_L')))} px")
    print(f"V2 ASL_L val: {format_num(v2.get(('v2','val','ASL_L')))} px")
    print(f"V4 ASL_L val: {format_num(v4.get(('v4','val','ASL_L')))} px")
    print(f"DECISION={DECISION_MD.resolve()}")
    return 0 if verdict == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
