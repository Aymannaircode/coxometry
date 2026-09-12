#!/usr/bin/env python3
"""Analyse V2 train vs val — erreurs landmark par split (new_26).

Compare les prédictions V2 existantes aux annotations GT, séparément
sur les cas TRAIN et VAL. Lecture seule — aucun entraînement ni modification.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
SPLIT_JSON = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "split.json"
MODEL_PATH = (
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
LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "train_vs_val_landmark_analysis.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "train_vs_val_landmark_analysis.md"

LANDMARKS = [
    "TD_R", "TD_L",
    "FHC_R", "FHC_L",
    "ASL_R", "ASL_L",
    "ASM_R", "ASM_L",
    "FNM_R", "FNM_L",
    "FSP_R", "FSP_L",
    "FSD_R", "FSD_L",
]
FOCUS_LANDMARKS = ("ASL_R", "ASL_L", "ASM_R", "ASM_L")

KEYPOINTS_START = 5
MIN_KEYPOINT_CONF = 0.25
NKPT = 14

# Seuils heuristiques pour le diagnostic automatique (px)
GOOD_THRESHOLD = 150.0
BAD_THRESHOLD = 300.0
GENERALIZATION_RATIO = 2.0
UNSTABLE_MIN_GOOD = 120.0
UNSTABLE_STDEV_RATIO = 0.25


@dataclass
class ErrorRecord:
    case_id: str
    split: str
    landmark: str
    error_px: float


@dataclass
class SplitLandmarkStats:
    landmark: str
    split: str
    count: int = 0
    mean: float | None = None
    median: float | None = None
    stdev: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    records: list[ErrorRecord] = field(default_factory=list)


def format_num(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def load_split() -> tuple[list[str], list[str]]:
    data = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))
    train_ids = sorted(data["train"])
    val_ids = sorted(data["val"])
    return train_ids, val_ids


def image_dimensions(annotation: dict, case_id: str) -> tuple[float, float]:
    width = annotation.get("image_width")
    height = annotation.get("image_height")
    if isinstance(width, (int, float)) and isinstance(height, (int, float)):
        if float(width) > 0 and float(height) > 0:
            return float(width), float(height)
    from PIL import Image

    with Image.open(IMAGE_DIR / f"{case_id}.png") as image:
        return float(image.size[0]), float(image.size[1])


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


def euclidean_error(gt: tuple[float, float], pred: tuple[float, float] | None) -> float | None:
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
        }
    return {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values) if len(values) >= 2 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def build_error_records(case_ids: list[str], split: str) -> list[ErrorRecord]:
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
            records.append(ErrorRecord(case_id=case_id, split=split, landmark=name, error_px=err))
    return records


def stats_for(records: list[ErrorRecord], split: str, landmark: str) -> SplitLandmarkStats:
    subset = [r for r in records if r.split == split and r.landmark == landmark]
    values = [r.error_px for r in subset]
    stats = compute_stats(values)
    return SplitLandmarkStats(
        landmark=landmark,
        split=split,
        count=int(stats["count"] or 0),
        mean=stats["mean"],
        median=stats["median"],
        stdev=stats["stdev"],
        minimum=stats["min"],
        maximum=stats["max"],
        records=subset,
    )


def safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return numerator / denominator


def is_good(mean: float | None) -> bool:
    return mean is not None and mean < GOOD_THRESHOLD


def is_bad(mean: float | None) -> bool:
    return mean is not None and mean >= BAD_THRESHOLD


def diagnose(
    asl_l_train: SplitLandmarkStats,
    asl_l_val: SplitLandmarkStats,
    overall_asl_l_mean: float | None,
) -> tuple[str, str]:
    train_mean = asl_l_train.mean
    val_mean = asl_l_val.mean
    train_min = asl_l_train.minimum
    train_stdev = asl_l_train.stdev or 0.0

    if is_good(train_mean) and is_good(val_mean):
        if overall_asl_l_mean is not None and overall_asl_l_mean >= BAD_THRESHOLD:
            return (
                "D",
                "ASL_L bon sur TRAIN et VAL dans cette analyse, mais l'évaluation globale 26 cas "
                "reste mauvaise — vérifier le pipeline d'évaluation (images, dimensions, mapping).",
            )
        return (
            "D",
            "ASL_L performant sur TRAIN et VAL — le problème signalé sur 26 cas ne se reproduit pas ici.",
        )

    if is_good(train_mean) and is_bad(val_mean):
        return (
            "B",
            "ASL_L acceptable sur TRAIN mais dégradé sur VAL — problème de généralisation "
            "(dataset petit, split train/val, distribution).",
        )

    if is_bad(train_mean) and is_bad(val_mean):
        unstable = (
            train_min is not None
            and train_min < UNSTABLE_MIN_GOOD
            and train_stdev > (train_mean or 0) * UNSTABLE_STDEV_RATIO
        )
        if unstable:
            return (
                "C",
                "ASL_L mauvais en moyenne sur TRAIN et VAL, mais certains cas TRAIN restent bons — "
                "comportement instable ; analyser les images difficiles.",
            )
        return (
            "A",
            "ASL_L très mauvais sur TRAIN et VAL — sous-apprentissage ou difficulté intrinsèque "
            "du landmark / capacité d'apprentissage insuffisante.",
        )

    if is_bad(train_mean) or is_bad(val_mean):
        ratio = safe_ratio(val_mean, train_mean)
        if ratio is not None and ratio >= GENERALIZATION_RATIO and is_good(train_mean):
            return (
                "B",
                "Ratio VAL/TRAIN élevé avec TRAIN acceptable — tendance généralisation.",
            )
        if (
            train_min is not None
            and train_min < UNSTABLE_MIN_GOOD
            and train_stdev > (train_mean or 0) * UNSTABLE_STDEV_RATIO
        ):
            return (
                "C",
                "Erreurs ASL_L hétérogènes — certains cas TRAIN corrects, d'autres très mauvais.",
            )
        return (
            "A",
            "ASL_L dégradé sur au moins un split avec moyennes élevées — sous-apprentissage probable.",
        )

    return (
        "A",
        "ASL_L au-dessus des landmarks typiques (~60–160 px) sur TRAIN et/ou VAL.",
    )


def write_csv(
    train_records: list[ErrorRecord],
    val_records: list[ErrorRecord],
    train_stats: dict[str, SplitLandmarkStats],
    val_stats: dict[str, SplitLandmarkStats],
    diagnosis: str,
    ratios: dict[str, float | None],
) -> None:
    rows: list[dict[str, str]] = []

    rows.append({"section": "meta", "split": "", "landmark": "model", "metric": "path", "value": str(MODEL_PATH)})
    rows.append({"section": "meta", "split": "", "landmark": "predictions", "metric": "path", "value": str(LABEL_DIR)})
    rows.append({"section": "meta", "split": "", "landmark": "diagnosis", "metric": "case", "value": diagnosis})

    for split_name, split_stats in (("TRAIN", train_stats), ("VAL", val_stats)):
        for landmark in LANDMARKS:
            stats = split_stats[landmark]
            for metric, val in (
                ("count", stats.count),
                ("mean", stats.mean),
                ("median", stats.median),
                ("stdev", stats.stdev),
                ("min", stats.minimum),
                ("max", stats.maximum),
            ):
                rows.append(
                    {
                        "section": "landmark_stats",
                        "split": split_name,
                        "landmark": landmark,
                        "metric": metric,
                        "value": format_num(float(val)) if isinstance(val, float) else str(val),
                    }
                )

    for landmark in LANDMARKS:
        tr = train_stats[landmark]
        va = val_stats[landmark]
        rows.append(
            {
                "section": "comparison",
                "split": "ALL",
                "landmark": landmark,
                "metric": "train_mean",
                "value": format_num(tr.mean),
            }
        )
        rows.append(
            {
                "section": "comparison",
                "split": "ALL",
                "landmark": landmark,
                "metric": "train_median",
                "value": format_num(tr.median),
            }
        )
        rows.append(
            {
                "section": "comparison",
                "split": "ALL",
                "landmark": landmark,
                "metric": "val_mean",
                "value": format_num(va.mean),
            }
        )
        rows.append(
            {
                "section": "comparison",
                "split": "ALL",
                "landmark": landmark,
                "metric": "val_median",
                "value": format_num(va.median),
            }
        )

    for key, ratio in ratios.items():
        rows.append(
            {
                "section": "ratio",
                "split": "ALL",
                "landmark": key,
                "metric": "val_over_train",
                "value": format_num(ratio) if ratio is not None else "NA",
            }
        )

    for rec in train_records + val_records:
        if rec.landmark in FOCUS_LANDMARKS:
            rows.append(
                {
                    "section": "case_detail",
                    "split": rec.split.upper(),
                    "landmark": rec.landmark,
                    "metric": rec.case_id,
                    "value": format_num(rec.error_px),
                }
            )

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["section", "split", "landmark", "metric", "value"])
        writer.writeheader()
        writer.writerows(rows)


def write_md(
    train_ids: list[str],
    val_ids: list[str],
    train_stats: dict[str, SplitLandmarkStats],
    val_stats: dict[str, SplitLandmarkStats],
    ratios: dict[str, float | None],
    diagnosis: str,
    diagnosis_detail: str,
    overall_asl_l_mean: float | None,
) -> None:
    asl_l_train = train_stats["ASL_L"]
    asl_l_val = val_stats["ASL_L"]
    asl_r_train = train_stats["ASL_R"]
    asl_r_val = val_stats["ASL_R"]

    lines = [
        "# Analyse V2 TRAIN vs VAL — erreurs landmark (new_26)",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        f"**Modèle V2 :** `{MODEL_PATH.relative_to(PROJECT_ROOT).as_posix()}`",
        f"**Prédictions :** `{LABEL_DIR.relative_to(PROJECT_ROOT).as_posix()}/` (existantes, non modifiées)",
        f"**GT :** `{ANNOT_DIR.relative_to(PROJECT_ROOT).as_posix()}/`",
        f"**Split :** `{SPLIT_JSON.relative_to(PROJECT_ROOT).as_posix()}`",
        "",
        "## Résumé",
        "",
        f"- Cas **TRAIN** : **{len(train_ids)}**",
        f"- Cas **VAL** : **{len(val_ids)}**",
        f"- Seuils diagnostic : bon < {GOOD_THRESHOLD:.0f} px, mauvais ≥ {BAD_THRESHOLD:.0f} px",
        "",
        f"## Diagnostic automatique : **CAS {diagnosis}**",
        "",
        diagnosis_detail,
        "",
        "## Focus ASL / ASM",
        "",
        "| Métrique | TRAIN | VAL |",
        "|----------|-------|-----|",
        f"| ASL_L mean (px) | {format_num(asl_l_train.mean)} | {format_num(asl_l_val.mean)} |",
        f"| ASL_L median (px) | {format_num(asl_l_train.median)} | {format_num(asl_l_val.median)} |",
        f"| ASL_L min / max (px) | {format_num(asl_l_train.minimum)} / {format_num(asl_l_train.maximum)} | "
        f"{format_num(asl_l_val.minimum)} / {format_num(asl_l_val.maximum)} |",
        f"| ASL_R mean (px) | {format_num(asl_r_train.mean)} | {format_num(asl_r_val.mean)} |",
        f"| ASL_R median (px) | {format_num(asl_r_train.median)} | {format_num(asl_r_val.median)} |",
        f"| ASM_L mean (px) | {format_num(train_stats['ASM_L'].mean)} | {format_num(val_stats['ASM_L'].mean)} |",
        f"| ASM_R mean (px) | {format_num(train_stats['ASM_R'].mean)} | {format_num(val_stats['ASM_R'].mean)} |",
        "",
        "### Ratios VAL / TRAIN (mean)",
        "",
        f"- **ASL_L_val / ASL_L_train** = {format_num(ratios['ASL_L'])}",
        f"- **ASL_R_val / ASL_R_train** = {format_num(ratios['ASL_R'])}",
        "",
    ]
    if overall_asl_l_mean is not None:
        lines.append(
            f"- Référence évaluation globale 26 cas (ASL_L mean) : **{format_num(overall_asl_l_mean)} px**"
        )
        lines.append("")

    lines.extend(
        [
            "## Tableau comparatif — 14 landmarks",
            "",
            "| Landmark | Train mean | Train median | Val mean | Val median |",
            "|----------|------------|--------------|----------|------------|",
        ]
    )
    for landmark in LANDMARKS:
        tr = train_stats[landmark]
        va = val_stats[landmark]
        lines.append(
            f"| {landmark} | {format_num(tr.mean)} | {format_num(tr.median)} | "
            f"{format_num(va.mean)} | {format_num(va.median)} |"
        )

    for split_title, split_stats, case_ids in (
        ("TRAIN", train_stats, train_ids),
        ("VAL", val_stats, val_ids),
    ):
        lines.extend([f"", f"## Statistiques détaillées — {split_title} ({len(case_ids)} cas)", ""])
        for landmark in LANDMARKS:
            stats = split_stats[landmark]
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
                    "",
                ]
            )

    lines.extend(
        [
            "## Erreurs ASL_L par cas",
            "",
            "### TRAIN",
            "",
            "| Cas | Erreur (px) |",
            "|-----|-------------|",
        ]
    )
    for rec in sorted(asl_l_train.records, key=lambda r: r.error_px, reverse=True):
        lines.append(f"| {rec.case_id} | {format_num(rec.error_px)} |")

    lines.extend(["", "### VAL", "", "| Cas | Erreur (px) |", "|-----|-------------|"])
    for rec in sorted(asl_l_val.records, key=lambda r: r.error_px, reverse=True):
        lines.append(f"| {rec.case_id} | {format_num(rec.error_px)} |")

    lines.extend(
        [
            "",
            "## Interprétation des cas",
            "",
            "| Cas | Description |",
            "|-----|-------------|",
            "| **A** | ASL_L très mauvais TRAIN + VAL → sous-apprentissage / difficulté intrinsèque |",
            "| **B** | ASL_L bon TRAIN, mauvais VAL → généralisation / dataset petit |",
            "| **C** | ASL_L mauvais en moyenne mais certains TRAIN bons → instabilité |",
            "| **D** | ASL_L bon TRAIN + VAL mais évaluation 26 cas mauvaise → pipeline d'éval |",
            "",
            "## Regénérer",
            "",
            "```bash",
            ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\analyze_v2_train_vs_val_new_26.py",
            "```",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def overall_asl_l_mean(all_records: list[ErrorRecord]) -> float | None:
    values = [r.error_px for r in all_records if r.landmark == "ASL_L"]
    return statistics.mean(values) if values else None


def main() -> int:
    if not MODEL_PATH.is_file():
        raise SystemExit(f"Modèle V2 introuvable (lecture seule) : {MODEL_PATH}")
    if not SPLIT_JSON.is_file():
        raise SystemExit(f"Split introuvable : {SPLIT_JSON}")

    train_ids, val_ids = load_split()
    train_records = build_error_records(train_ids, "train")
    val_records = build_error_records(val_ids, "val")
    all_records = train_records + val_records

    train_stats = {name: stats_for(all_records, "train", name) for name in LANDMARKS}
    val_stats = {name: stats_for(all_records, "val", name) for name in LANDMARKS}

    ratios = {
        "ASL_L": safe_ratio(val_stats["ASL_L"].mean, train_stats["ASL_L"].mean),
        "ASL_R": safe_ratio(val_stats["ASL_R"].mean, train_stats["ASL_R"].mean),
    }

    overall_mean = overall_asl_l_mean(all_records)
    diagnosis, diagnosis_detail = diagnose(train_stats["ASL_L"], val_stats["ASL_L"], overall_mean)

    write_csv(train_records, val_records, train_stats, val_stats, diagnosis, ratios)
    write_md(
        train_ids,
        val_ids,
        train_stats,
        val_stats,
        ratios,
        diagnosis,
        diagnosis_detail,
        overall_mean,
    )

    print("TRAIN VS VAL ANALYSIS COMPLETE")
    print(f"Train cases: {len(train_ids)}")
    print(f"Val cases: {len(val_ids)}")
    print("")
    print(f"ASL_L TRAIN mean: {format_num(train_stats['ASL_L'].mean)} px")
    print(f"ASL_L VAL mean: {format_num(val_stats['ASL_L'].mean)} px")
    print(f"ASL_R TRAIN mean: {format_num(train_stats['ASL_R'].mean)} px")
    print(f"ASL_R VAL mean: {format_num(val_stats['ASL_R'].mean)} px")
    print("")
    print(f"DIAGNOSIS: {diagnosis}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
