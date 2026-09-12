#!/usr/bin/env python3
"""Compare les prédictions YOLO V1/V2 aux annotations humaines new_26 (lecture seule)."""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent.parent / "manual_annotation_tool"
sys.path.insert(0, str(TOOL_DIR))

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
V1_LABELS_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions" / "labels"
V2_LABELS_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
PNG_FALLBACK_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions" / "images"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "comparison_v1_v2.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "comparison_v1_v2_summary.md"

LANDMARKS = [
    ("LM-01", "TD_R"),
    ("LM-02", "TD_L"),
    ("LM-03", "FHC_R"),
    ("LM-04", "FHC_L"),
    ("LM-05", "ASL_R"),
    ("LM-06", "ASL_L"),
    ("LM-07", "ASM_R"),
    ("LM-08", "ASM_L"),
    ("LM-09", "FNM_R"),
    ("LM-10", "FNM_L"),
    ("LM-11", "FSP_R"),
    ("LM-12", "FSP_L"),
    ("LM-13", "FSD_R"),
    ("LM-14", "FSD_L"),
]

LANDMARK_GROUPS = {
    "TD": ("TD_R", "TD_L"),
    "FHC": ("FHC_R", "FHC_L"),
    "ASL": ("ASL_R", "ASL_L"),
    "ASM": ("ASM_R", "ASM_L"),
    "FNM": ("FNM_R", "FNM_L"),
    "FSP": ("FSP_R", "FSP_L"),
    "FSD": ("FSD_R", "FSD_L"),
}

HIGHLIGHT_LANDMARKS = {"FSP_R", "FSP_L", "FSD_R", "FSD_L"}

KEYPOINTS_START = 5
MIN_KEYPOINT_CONF = 0.25
NKPT = 14


@dataclass
class PredictionPoint:
    x: float | None
    y: float | None
    confidence: float
    available: bool


@dataclass
class CaseComparison:
    pilot_id: str
    width: float
    height: float
    v1_errors: dict[str, float | None] = field(default_factory=dict)
    v2_errors: dict[str, float | None] = field(default_factory=dict)
    v1_missing: list[str] = field(default_factory=list)
    v2_missing: list[str] = field(default_factory=list)
    skipped_v0: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


def read_png_dimensions(pilot_id: str) -> tuple[int, int] | None:
    png_path = PNG_FALLBACK_DIR / f"{pilot_id}.png"
    if not png_path.is_file():
        return None
    try:
        from PIL import Image

        with Image.open(png_path) as image:
            return image.size
    except Exception:
        return None


def image_dimensions(annotation: dict, pilot_id: str) -> tuple[float, float]:
    width = annotation.get("image_width")
    height = annotation.get("image_height")
    if isinstance(width, (int, float)) and isinstance(height, (int, float)):
        if float(width) > 0 and float(height) > 0:
            return float(width), float(height)

    png_dims = read_png_dimensions(pilot_id)
    if png_dims is not None:
        return float(png_dims[0]), float(png_dims[1])

    raise ValueError(f"Dimensions image introuvables pour {pilot_id}")


def parse_prediction_file(path: Path, width: float, height: float) -> dict[str, PredictionPoint]:
    if not path.is_file():
        return {}

    line = path.read_text(encoding="utf-8").strip()
    if not line:
        return {}

    values = line.split()
    if len(values) not in {47, 48}:
        raise ValueError(f"Format YOLO inattendu ({path.name}) : {len(values)} colonnes.")

    keypoint_values = [float(value) for value in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    if len(keypoint_values) != NKPT * 3:
        raise ValueError(f"Nombre de keypoints invalide ({path.name}).")

    points: dict[str, PredictionPoint] = {}
    for index, (_landmark_id, name) in enumerate(LANDMARKS):
        x_norm = keypoint_values[index * 3]
        y_norm = keypoint_values[index * 3 + 1]
        kpt_conf = keypoint_values[index * 3 + 2]
        available = kpt_conf >= MIN_KEYPOINT_CONF
        points[name] = PredictionPoint(
            x=x_norm * width if available else None,
            y=y_norm * height if available else None,
            confidence=kpt_conf,
            available=available,
        )
    return points


def euclidean_error(
    gt_x: float, gt_y: float, prediction: PredictionPoint | None
) -> float | None:
    if prediction is None or not prediction.available:
        return None
    if prediction.x is None or prediction.y is None:
        return None
    return math.hypot(prediction.x - gt_x, prediction.y - gt_y)


def compare_case(pilot_id: str) -> CaseComparison:
    json_path = ANNOT_DIR / f"{pilot_id}.json"
    if not json_path.is_file():
        raise FileNotFoundError(f"Annotation absente : {json_path}")

    annotation = json.loads(json_path.read_text(encoding="utf-8-sig"))
    width, height = image_dimensions(annotation, pilot_id)
    result = CaseComparison(pilot_id=pilot_id, width=width, height=height)

    v1_points = parse_prediction_file(V1_LABELS_DIR / f"{pilot_id}.txt", width, height)
    v2_points = parse_prediction_file(V2_LABELS_DIR / f"{pilot_id}.txt", width, height)
    if not v1_points:
        result.issues.append("prediction_v1_absente")
    if not v2_points:
        result.issues.append("prediction_v2_absente")

    landmarks = annotation.get("landmarks", [])
    by_name = {str(item.get("name")): item for item in landmarks if isinstance(item, dict)}

    for _landmark_id, name in LANDMARKS:
        gt = by_name.get(name)
        if not gt:
            result.issues.append(f"ground_truth_manquant:{name}")
            continue
        if gt.get("v") == 0:
            result.skipped_v0.append(name)
            continue
        if gt.get("v") != 2:
            result.issues.append(f"ground_truth_non_evalue:{name}:v={gt.get('v')}")
            continue

        gt_x, gt_y = gt.get("x"), gt.get("y")
        if gt_x is None or gt_y is None:
            result.issues.append(f"ground_truth_sans_coords:{name}")
            continue

        v1_pred = v1_points.get(name)
        v2_pred = v2_points.get(name)
        v1_err = euclidean_error(float(gt_x), float(gt_y), v1_pred)
        v2_err = euclidean_error(float(gt_x), float(gt_y), v2_pred)

        result.v1_errors[name] = v1_err
        result.v2_errors[name] = v2_err
        if v1_err is None:
            result.v1_missing.append(name)
        if v2_err is None:
            result.v2_missing.append(name)

    return result


def summarize_errors(errors_by_case: list[CaseComparison], version: str) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for case in errors_by_case:
        error_map = case.v1_errors if version == "v1" else case.v2_errors
        for name, error in error_map.items():
            if error is not None:
                grouped[name].append(error)
    return grouped


def stats(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"mean": float("nan"), "median": float("nan"), "max": float("nan"), "count": 0}
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "max": max(values),
        "count": len(values),
    }


def improvement(v1_mean: float, v2_mean: float) -> tuple[float, float]:
    if math.isnan(v1_mean) or math.isnan(v2_mean):
        return float("nan"), float("nan")
    delta = v1_mean - v2_mean
    pct = (delta / v1_mean * 100.0) if v1_mean > 0 else float("nan")
    return delta, pct


def best_model(v1_mean: float, v2_mean: float) -> str:
    if math.isnan(v1_mean) and math.isnan(v2_mean):
        return "aucun"
    if math.isnan(v1_mean):
        return "V2"
    if math.isnan(v2_mean):
        return "V1"
    if abs(v1_mean - v2_mean) < 1e-9:
        return "egal"
    return "V2" if v2_mean < v1_mean else "V1"


def format_num(value: float, digits: int = 2) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:.{digits}f}"


def write_csv(
    landmark_rows: list[dict[str, str]],
    group_rows: list[dict[str, str]],
    global_row: dict[str, str],
    detail_rows: list[dict[str, str]],
) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "section",
                "landmark",
                "group",
                "pilot_id",
                "v1_mean_px",
                "v2_mean_px",
                "improvement_px",
                "improvement_pct",
                "v1_median_px",
                "v2_median_px",
                "v1_max_px",
                "v2_max_px",
                "evaluated_count",
                "v1_available",
                "v2_available",
                "best_model",
                "v1_error_px",
                "v2_error_px",
            ],
        )
        writer.writeheader()
        for row in landmark_rows:
            writer.writerow(row)
        for row in group_rows:
            writer.writerow(row)
        writer.writerow(global_row)
        for row in detail_rows:
            writer.writerow(row)


def write_markdown(
    landmark_rows: list[dict[str, str]],
    group_rows: list[dict[str, str]],
    global_row: dict[str, str],
    cases: list[CaseComparison],
    missing_summary: dict[str, int],
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Comparaison YOLO V1 vs V2 — new_26",
        "",
        f"**Généré le :** {now}",
        "**Référence :** annotations humaines `annotation_pilot/annotations/new_26/B26_XX.json`",
        "**V1 :** `datasets/yolo_pose_new_26/predictions/labels/`",
        "**V2 :** `datasets/yolo_pose_new_26/predictions_v2/labels/`",
        "",
        "## Résumé global",
        "",
        f"- Cas comparés : **{len(cases)}**",
        f"- Landmarks évalués (total, hors v=0) : **{global_row['evaluated_count']}**",
        f"- Erreur moyenne V1 : **{global_row['v1_mean_px']} px**",
        f"- Erreur moyenne V2 : **{global_row['v2_mean_px']} px**",
        f"- Amélioration V2 vs V1 : **{global_row['improvement_px']} px** ({global_row['improvement_pct']} %)",
        f"- Meilleur modèle global : **{global_row['best_model']}**",
        "",
        "## Tableau par landmark",
        "",
        "| Landmark | V1 mean px | V2 mean px | Amélioration px | Amélioration % | Meilleur |",
        "|----------|------------|------------|-----------------|----------------|----------|",
    ]

    for row in landmark_rows:
        name = row["landmark"]
        cell = f"**{name}**" if name in HIGHLIGHT_LANDMARKS else name
        lines.append(
            f"| {cell} | {row['v1_mean_px']} | {row['v2_mean_px']} | "
            f"{row['improvement_px']} | {row['improvement_pct']} | {row['best_model']} |"
        )

    lines.extend(
        [
            "",
            "## Résumé par groupe",
            "",
            "| Groupe | V1 mean px | V2 mean px | Amélioration px | Amélioration % | Meilleur |",
            "|--------|------------|------------|-----------------|----------------|----------|",
        ]
    )
    for row in group_rows:
        group = row["group"]
        cell = f"**{group}**" if group in {"FSP", "FSD"} else group
        lines.append(
            f"| {cell} | {row['v1_mean_px']} | {row['v2_mean_px']} | "
            f"{row['improvement_px']} | {row['improvement_pct']} | {row['best_model']} |"
        )

    lines.extend(["", "## Points saillants FSP / FSD", ""])
    for row in landmark_rows:
        if row["landmark"] in HIGHLIGHT_LANDMARKS:
            lines.append(
                f"- **{row['landmark']}** : V1={row['v1_mean_px']} px, V2={row['v2_mean_px']} px, "
                f"Δ={row['improvement_px']} px ({row['improvement_pct']} %), meilleur={row['best_model']}"
            )

    if missing_summary:
        lines.extend(["", "## Fichiers / prédictions manquants", ""])
        for key, count in sorted(missing_summary.items()):
            lines.append(f"- {key} : {count}")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Les landmarks ground truth avec `v=0` sont exclus.",
            "- Une prédiction est considérée manquante si le fichier est absent ou si la confiance keypoint < "
            f"{MIN_KEYPOINT_CONF}.",
            "- Amélioration positive = V2 plus proche du ground truth (erreur plus faible).",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    pilot_ids = [f"B26_{index:02d}" for index in range(1, 27)]
    cases: list[CaseComparison] = []
    load_errors: list[str] = []

    print(f"Comparaison V1/V2 — {len(pilot_ids)} cas attendus")
    print(f"GROUND TRUTH={ANNOT_DIR}")
    print(f"V1={V1_LABELS_DIR}")
    print(f"V2={V2_LABELS_DIR}")

    for pilot_id in pilot_ids:
        try:
            cases.append(compare_case(pilot_id))
        except Exception as exc:
            load_errors.append(f"{pilot_id}: {exc}")
            print(f"ERROR {pilot_id}: {exc}")

    if not cases:
        print("Aucun cas comparable.")
        return 1

    v1_grouped = summarize_errors(cases, "v1")
    v2_grouped = summarize_errors(cases, "v2")

    landmark_rows: list[dict[str, str]] = []
    all_v1_errors: list[float] = []
    all_v2_errors: list[float] = []

    for _landmark_id, name in LANDMARKS:
        v1_values = v1_grouped.get(name, [])
        v2_values = v2_grouped.get(name, [])
        all_v1_errors.extend(v1_values)
        all_v2_errors.extend(v2_values)
        v1_stat = stats(v1_values)
        v2_stat = stats(v2_values)
        delta, pct = improvement(float(v1_stat["mean"]), float(v2_stat["mean"]))
        v1_available = sum(1 for case in cases if case.v1_errors.get(name) is not None)
        v2_available = sum(
            1 for case in cases if case.v2_errors.get(name) is not None
        )
        evaluated = sum(
            1
            for case in cases
            if name in case.v1_errors or name in case.v2_errors
        )
        landmark_rows.append(
            {
                "section": "landmark",
                "landmark": name,
                "group": name.rsplit("_", 1)[0],
                "pilot_id": "",
                "v1_mean_px": format_num(float(v1_stat["mean"])),
                "v2_mean_px": format_num(float(v2_stat["mean"])),
                "improvement_px": format_num(delta),
                "improvement_pct": format_num(pct, 1),
                "v1_median_px": format_num(float(v1_stat["median"])),
                "v2_median_px": format_num(float(v2_stat["median"])),
                "v1_max_px": format_num(float(v1_stat["max"])),
                "v2_max_px": format_num(float(v2_stat["max"])),
                "evaluated_count": str(evaluated),
                "v1_available": str(v1_available),
                "v2_available": str(v2_available),
                "best_model": best_model(float(v1_stat["mean"]), float(v2_stat["mean"])),
                "v1_error_px": "",
                "v2_error_px": "",
            }
        )

    group_rows: list[dict[str, str]] = []
    for group_name, members in LANDMARK_GROUPS.items():
        v1_values = [err for name in members for err in v1_grouped.get(name, [])]
        v2_values = [err for name in members for err in v2_grouped.get(name, [])]
        v1_stat = stats(v1_values)
        v2_stat = stats(v2_values)
        delta, pct = improvement(float(v1_stat["mean"]), float(v2_stat["mean"]))
        group_rows.append(
            {
                "section": "group",
                "landmark": "",
                "group": group_name,
                "pilot_id": "",
                "v1_mean_px": format_num(float(v1_stat["mean"])),
                "v2_mean_px": format_num(float(v2_stat["mean"])),
                "improvement_px": format_num(delta),
                "improvement_pct": format_num(pct, 1),
                "v1_median_px": format_num(float(v1_stat["median"])),
                "v2_median_px": format_num(float(v2_stat["median"])),
                "v1_max_px": format_num(float(v1_stat["max"])),
                "v2_max_px": format_num(float(v2_stat["max"])),
                "evaluated_count": str(int(v1_stat["count"])),
                "v1_available": str(len(v1_values)),
                "v2_available": str(len(v2_values)),
                "best_model": best_model(float(v1_stat["mean"]), float(v2_stat["mean"])),
                "v1_error_px": "",
                "v2_error_px": "",
            }
        )

    global_v1 = stats(all_v1_errors)
    global_v2 = stats(all_v2_errors)
    global_delta, global_pct = improvement(float(global_v1["mean"]), float(global_v2["mean"]))
    global_row = {
        "section": "global",
        "landmark": "ALL",
        "group": "ALL",
        "pilot_id": "",
        "v1_mean_px": format_num(float(global_v1["mean"])),
        "v2_mean_px": format_num(float(global_v2["mean"])),
        "improvement_px": format_num(global_delta),
        "improvement_pct": format_num(global_pct, 1),
        "v1_median_px": format_num(float(global_v1["median"])),
        "v2_median_px": format_num(float(global_v2["median"])),
        "v1_max_px": format_num(float(global_v1["max"])),
        "v2_max_px": format_num(float(global_v2["max"])),
        "evaluated_count": str(int(global_v1["count"])),
        "v1_available": str(len(all_v1_errors)),
        "v2_available": str(len(all_v2_errors)),
        "best_model": best_model(float(global_v1["mean"]), float(global_v2["mean"])),
        "v1_error_px": "",
        "v2_error_px": "",
    }

    detail_rows: list[dict[str, str]] = []
    for case in cases:
        for name in sorted(set(case.v1_errors) | set(case.v2_errors)):
            detail_rows.append(
                {
                    "section": "detail",
                    "landmark": name,
                    "group": name.rsplit("_", 1)[0],
                    "pilot_id": case.pilot_id,
                    "v1_mean_px": "",
                    "v2_mean_px": "",
                    "improvement_px": "",
                    "improvement_pct": "",
                    "v1_median_px": "",
                    "v2_median_px": "",
                    "v1_max_px": "",
                    "v2_max_px": "",
                    "evaluated_count": "",
                    "v1_available": "",
                    "v2_available": "",
                    "best_model": "",
                    "v1_error_px": format_num(case.v1_errors[name])
                    if case.v1_errors.get(name) is not None
                    else "missing",
                    "v2_error_px": format_num(case.v2_errors[name])
                    if case.v2_errors.get(name) is not None
                    else "missing",
                }
            )

    missing_summary = {
        "prediction_v1_absente": sum(1 for case in cases if "prediction_v1_absente" in case.issues),
        "prediction_v2_absente": sum(1 for case in cases if "prediction_v2_absente" in case.issues),
        "v1_landmarks_manquants": sum(len(case.v1_missing) for case in cases),
        "v2_landmarks_manquants": sum(len(case.v2_missing) for case in cases),
        "ground_truth_v0_exclus": sum(len(case.skipped_v0) for case in cases),
    }

    write_csv(landmark_rows, group_rows, global_row, detail_rows)
    write_markdown(landmark_rows, group_rows, global_row, cases, missing_summary)

    print(f"CASES={len(cases)}")
    print(f"EVALUATED_LANDMARKS={global_row['evaluated_count']}")
    print(f"V1_MEAN_PX={global_row['v1_mean_px']}")
    print(f"V2_MEAN_PX={global_row['v2_mean_px']}")
    print(f"BEST_GLOBAL={global_row['best_model']}")
    print(f"CSV={OUTPUT_CSV}")
    print(f"MD={OUTPUT_MD}")
    if load_errors:
        print("LOAD_ERRORS=" + "; ".join(load_errors))
    if missing_summary["prediction_v2_absente"]:
        print(f"WARN prediction_v2_absente={missing_summary['prediction_v2_absente']} cas")
    if missing_summary["prediction_v1_absente"]:
        print(f"WARN prediction_v1_absente={missing_summary['prediction_v1_absente']} cas")

    return 1 if load_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
