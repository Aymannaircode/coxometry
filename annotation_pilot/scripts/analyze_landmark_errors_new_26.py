#!/usr/bin/env python3
"""Analyse quantitative des erreurs landmark V2 vs annotations humaines (new_26).

Calcule l'erreur euclidienne en pixels pour chaque landmark exploitable.
Lecture seule — ne modifie aucune source.
"""

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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
GEOMETRY_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_geometry_results.csv"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "landmark_error_analysis.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "landmark_error_analysis.md"

LANDMARKS = [
    "TD_R", "TD_L",
    "FHC_R", "FHC_L",
    "ASL_R", "ASL_L",
    "ASM_R", "ASM_L",
    "FNM_R", "FNM_L",
    "FSP_R", "FSP_L",
    "FSD_R", "FSD_L",
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

KEYPOINTS_START = 5
MIN_KEYPOINT_CONF = 0.25
NKPT = 14
TOP_N_LANDMARK = 5
TOP_N_ASL = 10
EXPECTED_CASES = 26


@dataclass
class ErrorRecord:
    case_id: str
    landmark: str
    error_px: float


@dataclass
class LandmarkStats:
    landmark: str
    count: int = 0
    mean: float | None = None
    median: float | None = None
    stdev: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    q1: float | None = None
    q3: float | None = None
    records: list[ErrorRecord] = field(default_factory=list)


def format_num(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def load_geometry() -> dict[str, dict[str, str]]:
    if not GEOMETRY_CSV.is_file():
        return {}
    with GEOMETRY_CSV.open("r", encoding="utf-8-sig", newline="") as stream:
        return {row["case_id"]: row for row in csv.DictReader(stream)}


def image_dimensions(annotation: dict, case_id: str) -> tuple[float, float]:
    width = annotation.get("image_width")
    height = annotation.get("image_height")
    if isinstance(width, (int, float)) and isinstance(height, (int, float)):
        if float(width) > 0 and float(height) > 0:
            return float(width), float(height)
    from PIL import Image

    png_path = IMAGE_DIR / f"{case_id}.png"
    with Image.open(png_path) as image:
        w, h = image.size
    return float(w), float(h)


def parse_v2_prediction(path: Path, width: float, height: float) -> dict[str, tuple[float, float] | None]:
    if not path.is_file():
        return {}
    line = path.read_text(encoding="utf-8").strip()
    if not line:
        return {}

    values = line.split()
    if len(values) not in {47, 48}:
        raise ValueError(f"Format YOLO inattendu ({path.name}) : {len(values)} colonnes.")

    keypoint_values = [float(v) for v in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    if len(keypoint_values) != NKPT * 3:
        raise ValueError(f"Keypoints invalides ({path.name}).")

    points: dict[str, tuple[float, float] | None] = {}
    for index, name in enumerate(LANDMARKS):
        x_norm = keypoint_values[index * 3]
        y_norm = keypoint_values[index * 3 + 1]
        conf = keypoint_values[index * 3 + 2]
        if conf >= MIN_KEYPOINT_CONF:
            points[name] = (x_norm * width, y_norm * height)
        else:
            points[name] = None
    return points


def load_gt_points(annotation: dict) -> dict[str, tuple[float, float]]:
    points: dict[str, tuple[float, float]] = {}
    for entry in annotation.get("landmarks", []):
        name = entry.get("name")
        if name not in LANDMARKS:
            continue
        if entry.get("v") != 2:
            continue
        x, y = entry.get("x"), entry.get("y")
        if x is None or y is None:
            continue
        points[name] = (float(x), float(y))
    return points


def euclidean_error(
    gt: tuple[float, float],
    pred: tuple[float, float] | None,
) -> float | None:
    if pred is None:
        return None
    return math.hypot(pred[0] - gt[0], pred[1] - gt[1])


def compute_stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "stdev": None,
            "min": None,
            "max": None,
            "q1": None,
            "q3": None,
        }
    result: dict[str, float | None] = {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) >= 2 else 0.0,
    }
    if len(values) >= 4:
        q1, _, q3 = statistics.quantiles(values, n=4)
        result["q1"] = q1
        result["q3"] = q3
    elif len(values) == 1:
        result["q1"] = values[0]
        result["q3"] = values[0]
    else:
        result["q1"] = min(values)
        result["q3"] = max(values)
    return result


def build_error_records(case_ids: list[str]) -> list[ErrorRecord]:
    records: list[ErrorRecord] = []
    for case_id in case_ids:
        json_path = ANNOT_DIR / f"{case_id}.json"
        label_path = LABEL_DIR / f"{case_id}.txt"
        annotation = json.loads(json_path.read_text(encoding="utf-8-sig"))
        width, height = image_dimensions(annotation, case_id)
        gt_points = load_gt_points(annotation)
        pred_points = parse_v2_prediction(label_path, width, height)

        for name in LANDMARKS:
            if name not in gt_points:
                continue
            err = euclidean_error(gt_points[name], pred_points.get(name))
            if err is None:
                continue
            records.append(ErrorRecord(case_id=case_id, landmark=name, error_px=err))
    return records


def stats_for_landmark(records: list[ErrorRecord], landmark: str) -> LandmarkStats:
    subset = [r for r in records if r.landmark == landmark]
    values = [r.error_px for r in subset]
    stats = compute_stats(values)
    return LandmarkStats(
        landmark=landmark,
        count=int(stats["count"] or 0),
        mean=stats["mean"],
        median=stats["median"],
        stdev=stats["stdev"],
        minimum=stats["min"],
        maximum=stats["max"],
        q1=stats["q1"],
        q3=stats["q3"],
        records=subset,
    )


def stats_for_group(records: list[ErrorRecord], group_name: str) -> dict[str, float | None]:
    names = set(LANDMARK_GROUPS[group_name])
    values = [r.error_px for r in records if r.landmark in names]
    return compute_stats(values)


def side_mean(records: list[ErrorRecord], side: str) -> float | None:
    suffix = f"_{side}"
    values = [r.error_px for r in records if r.landmark.endswith(suffix)]
    if not values:
        return None
    return statistics.mean(values)


def top_errors(records: list[ErrorRecord], n: int) -> list[ErrorRecord]:
    return sorted(records, key=lambda r: r.error_px, reverse=True)[:n]


def write_csv(
    records: list[ErrorRecord],
    landmark_stats: dict[str, LandmarkStats],
    ranking: list[tuple[str, float]],
) -> None:
    rows: list[dict[str, str]] = []

    rows.append({"section": "summary", "key": "cases", "value": str(EXPECTED_CASES), "case_id": "", "detail": ""})
    rows.append({"section": "summary", "key": "landmarks", "value": str(len(LANDMARKS)), "case_id": "", "detail": ""})
    rows.append(
        {
            "section": "summary",
            "key": "total_evaluations",
            "value": str(len(records)),
            "case_id": "",
            "detail": "",
        }
    )

    for landmark in LANDMARKS:
        stats = landmark_stats[landmark]
        for metric, val in (
            ("count", stats.count),
            ("mean", stats.mean),
            ("median", stats.median),
            ("stdev", stats.stdev),
            ("min", stats.minimum),
            ("max", stats.maximum),
            ("q1", stats.q1),
            ("q3", stats.q3),
        ):
            rows.append(
                {
                    "section": "landmark_stats",
                    "key": landmark,
                    "value": format_num(float(val)) if isinstance(val, float) else str(val),
                    "case_id": "",
                    "detail": metric,
                }
            )
        for rank, rec in enumerate(top_errors(stats.records, TOP_N_LANDMARK), start=1):
            rows.append(
                {
                    "section": "landmark_top_errors",
                    "key": landmark,
                    "value": format_num(rec.error_px),
                    "case_id": rec.case_id,
                    "detail": f"rank_{rank}",
                }
            )

    for group in LANDMARK_GROUPS:
        gstats = stats_for_group(records, group)
        for metric, val in gstats.items():
            rows.append(
                {
                    "section": "group_stats",
                    "key": group,
                    "value": format_num(float(val)) if isinstance(val, float) else str(val),
                    "case_id": "",
                    "detail": metric,
                }
            )

    for side in ("R", "L"):
        mean_val = side_mean(records, side)
        rows.append(
            {
                "section": "side_mean",
                "key": side,
                "value": format_num(mean_val),
                "case_id": "",
                "detail": "mean_error_px",
            }
        )

    for rank, (landmark, mean_val) in enumerate(ranking, start=1):
        rows.append(
            {
                "section": "ranking",
                "key": str(rank),
                "value": format_num(mean_val),
                "case_id": "",
                "detail": landmark,
            }
        )

    asl_l_records = [r for r in records if r.landmark == "ASL_L"]
    for rank, rec in enumerate(top_errors(asl_l_records, TOP_N_ASL), start=1):
        rows.append(
            {
                "section": "asl_l_top",
                "key": "ASL_L",
                "value": format_num(rec.error_px),
                "case_id": rec.case_id,
                "detail": f"rank_{rank}",
            }
        )

    geometry = load_geometry()
    for rank, rec in enumerate(top_errors(asl_l_records, TOP_N_ASL), start=1):
        geo = geometry.get(rec.case_id, {})
        rows.append(
            {
                "section": "asl_l_impact",
                "key": rec.case_id,
                "value": format_num(rec.error_px),
                "case_id": rec.case_id,
                "detail": f"VCE_L={geo.get('VCE_L', 'NA')} | Tonnis_L={geo.get('Tonnis_L', 'NA')}",
            }
        )

    for rec in records:
        rows.append(
            {
                "section": "detail",
                "key": rec.landmark,
                "value": format_num(rec.error_px),
                "case_id": rec.case_id,
                "detail": "",
            }
        )

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["section", "key", "value", "case_id", "detail"])
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    records: list[ErrorRecord],
    landmark_stats: dict[str, LandmarkStats],
    ranking: list[tuple[str, float]],
) -> None:
    geometry = load_geometry()
    asl_r = landmark_stats["ASL_R"]
    asl_l = landmark_stats["ASL_L"]
    asl_diff = None
    if asl_r.mean is not None and asl_l.mean is not None:
        asl_diff = asl_l.mean - asl_r.mean

    lines = [
        "# Analyse des erreurs landmark V2 — new_26",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        f"**GT :** `{ANNOT_DIR.relative_to(PROJECT_ROOT).as_posix()}/`",
        f"**V2 :** `{LABEL_DIR.relative_to(PROJECT_ROOT).as_posix()}/`",
        "",
        "## Résumé",
        "",
        f"- Cas analysés : **{EXPECTED_CASES}**",
        f"- Landmarks : **{len(LANDMARKS)}**",
        f"- Évaluations totales (GT v=2 + prédiction disponible) : **{len(records)}**",
        "",
        "## Classement des 14 landmarks (meilleur → pire, erreur moyenne px)",
        "",
        "| Rang | Landmark | Moyenne (px) | Médiane (px) | Max (px) |",
        "|------|----------|--------------|--------------|----------|",
    ]

    for rank, (landmark, mean_val) in enumerate(ranking, start=1):
        stats = landmark_stats[landmark]
        lines.append(
            f"| {rank} | {landmark} | {format_num(mean_val)} | {format_num(stats.median)} | {format_num(stats.maximum)} |"
        )

    lines.extend(["", "## Statistiques par landmark", ""])
    for landmark in LANDMARKS:
        stats = landmark_stats[landmark]
        lines.extend(
            [
                f"### {landmark}",
                "",
                "| Métrique | Valeur (px) |",
                "|----------|-------------|",
                f"| N | {stats.count} |",
                f"| Moyenne | {format_num(stats.mean)} |",
                f"| Médiane | {format_num(stats.median)} |",
                f"| Écart-type | {format_num(stats.stdev)} |",
                f"| Min | {format_num(stats.minimum)} |",
                f"| Max | {format_num(stats.maximum)} |",
                f"| Q1 | {format_num(stats.q1)} |",
                f"| Q3 | {format_num(stats.q3)} |",
                "",
                "**Top 5 erreurs**",
                "",
                "| Rang | Radio | Erreur (px) |",
                "|------|-------|-------------|",
            ]
        )
        for rank, rec in enumerate(top_errors(stats.records, TOP_N_LANDMARK), start=1):
            lines.append(f"| {rank} | {rec.case_id} | {format_num(rec.error_px)} |")
        lines.append("")

    lines.extend(["## Statistiques par groupe anatomique", ""])
    lines.extend(
        [
            "| Groupe | N | Moyenne | Médiane | Écart-type | Min | Max | Q1 | Q3 |",
            "|--------|---|---------|---------|------------|-----|-----|----|----|",
        ]
    )
    for group in LANDMARK_GROUPS:
        g = stats_for_group(records, group)
        lines.append(
            "| {group} | {count} | {mean} | {median} | {stdev} | {minv} | {maxv} | {q1} | {q3} |".format(
                group=group,
                count=int(g["count"] or 0),
                mean=format_num(g["mean"]),
                median=format_num(g["median"]),
                stdev=format_num(g["stdev"]),
                minv=format_num(g["min"]),
                maxv=format_num(g["max"]),
                q1=format_num(g["q1"]),
                q3=format_num(g["q3"]),
            )
        )

    lines.extend(
        [
            "",
            "## Moyenne par côté",
            "",
            f"- **Droit (_R)** : {format_num(side_mean(records, 'R'))} px",
            f"- **Gauche (_L)** : {format_num(side_mean(records, 'L'))} px",
            "",
            "## ASL — comparaison R / L",
            "",
            "| Landmark | Moyenne (px) | Médiane (px) | Max (px) |",
            "|----------|--------------|--------------|----------|",
            f"| ASL_R | {format_num(asl_r.mean)} | {format_num(asl_r.median)} | {format_num(asl_r.maximum)} |",
            f"| ASL_L | {format_num(asl_l.mean)} | {format_num(asl_l.median)} | {format_num(asl_l.maximum)} |",
            f"| **Différence L − R (moyenne)** | **{format_num(asl_diff)}** | | |",
            "",
            "### Top 10 cas problématiques — ASL_L",
            "",
            "| Rang | Radio | Erreur ASL_L (px) |",
            "|------|-------|-------------------|",
        ]
    )

    asl_l_top = top_errors([r for r in records if r.landmark == "ASL_L"], TOP_N_ASL)
    for rank, rec in enumerate(asl_l_top, start=1):
        lines.append(f"| {rank} | {rec.case_id} | {format_num(rec.error_px)} |")

    lines.extend(
        [
            "",
            "## Impact sur les mesures (ASL_L — top 10 erreurs)",
            "",
            "| Radio | Erreur ASL_L (px) | VCE_L (°) | Tönnis_L (°) |",
            "|-------|-------------------|-----------|--------------|",
        ]
    )
    for rec in asl_l_top:
        geo = geometry.get(rec.case_id, {})
        lines.append(
            f"| {rec.case_id} | {format_num(rec.error_px)} | {geo.get('VCE_L', 'NA')} | {geo.get('Tonnis_L', 'NA')} |"
        )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def list_case_ids() -> list[str]:
    ids = sorted(path.stem for path in ANNOT_DIR.glob("B26_*.json"))
    if len(ids) != EXPECTED_CASES:
        raise RuntimeError(f"Attendu {EXPECTED_CASES} annotations, trouvé {len(ids)}")
    return ids


def main() -> int:
    case_ids = list_case_ids()
    records = build_error_records(case_ids)

    landmark_stats = {name: stats_for_landmark(records, name) for name in LANDMARKS}
    ranking = sorted(
        [(name, landmark_stats[name].mean) for name in LANDMARKS if landmark_stats[name].mean is not None],
        key=lambda item: item[1],
    )

    write_csv(records, landmark_stats, ranking)
    write_markdown(records, landmark_stats, ranking)

    print("LANDMARK ERROR ANALYSIS COMPLETE")
    print(f"Cases: {len(case_ids)}")
    print(f"Landmarks: {len(LANDMARKS)}")
    print(f"Total landmark evaluations: {len(records)}")
    print("Ranking (mean error px, best -> worst):")
    for rank, (landmark, mean_val) in enumerate(ranking, start=1):
        print(f"  {rank:2d}. {landmark:6s}  {mean_val:.2f} px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
