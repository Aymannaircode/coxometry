#!/usr/bin/env python3
"""Validation anatomique des prédictions YOLO V2 — contrôle qualité (lecture seule)."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_anatomy_validation.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_anatomy_validation.md"

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

KEYPOINTS_START = 5
MIN_PRESENT_CONF = 0.25
WARN_CONF = 0.50
SIDE_MARGIN_RATIO = 0.05
AXIS_ANGLE_WARN_DEG = 25.0
BILATERAL_RATIO_WARN = 2.0
EDGE_TOLERANCE_PX = 1.0
FSD_NAMES = {"FSD_R", "FSD_L"}
FSD_AXIS_NORM_WARN = 0.35
FSD_MIN_AXIS_HEIGHT_RATIO = 0.02


@dataclass
class PredictedLandmark:
    id: str
    name: str
    x: float | None
    y: float | None
    confidence: float
    present: bool


@dataclass
class Anomaly:
    level: str
    category: str
    landmark: str
    message: str


@dataclass
class CaseReport:
    case_id: str
    width: float
    height: float
    landmarks: dict[str, PredictedLandmark] = field(default_factory=dict)
    anomalies: list[Anomaly] = field(default_factory=list)

    @property
    def present_count(self) -> int:
        return sum(1 for item in self.landmarks.values() if item.present)

    @property
    def low_confidence_count(self) -> int:
        return sum(
            1
            for item in self.landmarks.values()
            if item.present and item.confidence < WARN_CONF
        )

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.anomalies if item.level == "WARNING")

    @property
    def critical_count(self) -> int:
        return sum(1 for item in self.anomalies if item.level == "CRITICAL")

    @property
    def status(self) -> str:
        if self.critical_count > 0:
            return "CRITICAL"
        if self.warning_count > 0 or self.low_confidence_count > 0:
            return "WARNING"
        return "OK"


def read_image_size(case_id: str) -> tuple[float, float]:
    png_path = IMAGE_DIR / f"{case_id}.png"
    if not png_path.is_file():
        raise FileNotFoundError(f"Image absente : {png_path}")
    with Image.open(png_path) as image:
        return float(image.size[0]), float(image.size[1])


def parse_prediction(case_id: str, width: float, height: float) -> dict[str, PredictedLandmark]:
    label_path = LABEL_DIR / f"{case_id}.txt"
    if not label_path.is_file():
        raise FileNotFoundError(f"Label V2 absent : {label_path}")

    values = label_path.read_text(encoding="utf-8").strip().split()
    if len(values) not in {47, 48}:
        raise ValueError(f"Format YOLO inattendu ({case_id}) : {len(values)} colonnes.")

    keypoint_values = [float(value) for value in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    points: dict[str, PredictedLandmark] = {}
    for index, (landmark_id, name) in enumerate(LANDMARKS):
        x_norm = keypoint_values[index * 3]
        y_norm = keypoint_values[index * 3 + 1]
        conf = keypoint_values[index * 3 + 2]
        present = conf >= MIN_PRESENT_CONF
        points[name] = PredictedLandmark(
            id=landmark_id,
            name=name,
            x=x_norm * width if present else None,
            y=y_norm * height if present else None,
            confidence=conf,
            present=present,
        )
    return points


def point(report: CaseReport, name: str) -> tuple[float, float] | None:
    landmark = report.landmarks.get(name)
    if not landmark or not landmark.present or landmark.x is None or landmark.y is None:
        return None
    return landmark.x, landmark.y


def add(report: CaseReport, level: str, category: str, landmark: str, message: str) -> None:
    report.anomalies.append(Anomaly(level=level, category=category, landmark=landmark, message=message))


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def angle_at_middle(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    v1 = (a[0] - b[0], a[1] - b[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    norm1 = math.hypot(*v1)
    norm2 = math.hypot(*v2)
    if norm1 == 0 or norm2 == 0:
        return float("nan")
    cosine = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (norm1 * norm2)))
    return math.degrees(math.acos(cosine))


def deviation_from_line(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    ax, ay = a
    bx, by = b
    cx, cy = c
    denom = math.hypot(bx - ax, by - ay)
    if denom == 0:
        return float("nan")
    return abs((by - ay) * cx - (bx - ax) * cy + bx * ay - by * ax) / denom


def check_completeness_and_confidence(report: CaseReport) -> None:
    missing = [name for name, item in report.landmarks.items() if not item.present]
    if missing:
        add(
            report,
            "CRITICAL",
            "completeness",
            ",".join(missing),
            f"Landmarks manquants (confiance < {MIN_PRESENT_CONF}) : {', '.join(missing)}.",
        )

    for name, item in report.landmarks.items():
        if not item.present:
            add(
                report,
                "CRITICAL",
                "confidence",
                name,
                f"{name} : confiance={item.confidence:.3f} (< {MIN_PRESENT_CONF}, landmark absent).",
            )
        elif item.confidence < WARN_CONF:
            add(
                report,
                "WARNING",
                "confidence",
                name,
                f"{name} : confiance={item.confidence:.3f} (< {WARN_CONF}).",
            )


def axis_collinearity_deviation(angle: float) -> float:
    return abs(180.0 - angle)


def distance_to_bottom_edge(y: float, height: float) -> float:
    return (height - 1.0) - y


def classify_bounds(x: float, y: float, width: float, height: float) -> tuple[str, dict[str, float]]:
    dist_bottom = distance_to_bottom_edge(y, height)
    dist_top = y
    dist_left = x
    dist_right = (width - 1.0) - x
    details = {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "dist_bottom": dist_bottom,
    }

    if (
        x < -EDGE_TOLERANCE_PX
        or x >= width + EDGE_TOLERANCE_PX
        or y < -EDGE_TOLERANCE_PX
        or y >= height + EDGE_TOLERANCE_PX
    ):
        return "OUT_OF_IMAGE", details

    near_edge = (
        dist_left < EDGE_TOLERANCE_PX
        or dist_right < EDGE_TOLERANCE_PX
        or dist_top < EDGE_TOLERANCE_PX
        or dist_bottom < EDGE_TOLERANCE_PX
    )
    if near_edge:
        return "EDGE", details
    return "OK", details


def format_fsd_bounds_message(name: str, status: str, details: dict[str, float]) -> str:
    return (
        f"{name} [{status}] : coords=({details['x']:.1f}, {details['y']:.1f}), "
        f"image={details['width']:.0f}x{details['height']:.0f}, "
        f"distance bord inférieur={details['dist_bottom']:.1f} px."
    )


def check_bounds_and_side(report: CaseReport) -> None:
    mid = report.width / 2
    margin = report.width * SIDE_MARGIN_RATIO
    for name, item in report.landmarks.items():
        if not item.present or item.x is None or item.y is None:
            continue

        status, details = classify_bounds(item.x, item.y, report.width, report.height)
        if status == "OUT_OF_IMAGE":
            level = "CRITICAL"
            category = "OUT_OF_IMAGE"
            if name in FSD_NAMES:
                message = format_fsd_bounds_message(name, status, details)
            else:
                message = (
                    f"{name} [OUT_OF_IMAGE] : coords=({item.x:.1f}, {item.y:.1f}), "
                    f"image={report.width:.0f}x{report.height:.0f}."
                )
            add(report, level, category, name, message)
        elif status == "EDGE":
            if name in FSD_NAMES:
                message = format_fsd_bounds_message(name, status, details)
            else:
                message = (
                    f"{name} [EDGE] : coords=({item.x:.1f}, {item.y:.1f}), "
                    f"image={report.width:.0f}x{report.height:.0f}, "
                    f"distance bord inférieur={details['dist_bottom']:.1f} px."
                )
            add(report, "WARNING", "EDGE", name, message)

        if name.endswith("_R") and item.x > mid + margin:
            add(
                report,
                "WARNING",
                "side_rl",
                name,
                f"{name} : côté droit patient mais x={item.x:.1f} > milieu+5%.",
            )
        if name.endswith("_L") and item.x < mid - margin:
            add(
                report,
                "WARNING",
                "side_rl",
                name,
                f"{name} : côté gauche patient mais x={item.x:.1f} < milieu-5%.",
            )


def check_vertical_order(report: CaseReport, suffix: str) -> None:
    chain = [f"FHC_{suffix}", f"FNM_{suffix}", f"FSP_{suffix}", f"FSD_{suffix}"]
    coords = [(name, point(report, name)) for name in chain]
    present = [(name, coord) for name, coord in coords if coord is not None]
    for index in range(len(present) - 1):
        upper_name, (ux, uy) = present[index]
        lower_name, (lx, ly) = present[index + 1]
        if uy >= ly:
            level = "CRITICAL" if ly + 5 < uy else "WARNING"
            add(
                report,
                level,
                "vertical_order",
                lower_name,
                (
                    f"Chaîne {suffix} : ordre vertical incohérent entre {upper_name} "
                    f"(y={uy:.1f}) et {lower_name} (y={ly:.1f}) — attendu haut → bas."
                ),
            )


def is_fsd_near_bottom_edge(y: float, height: float) -> bool:
    return distance_to_bottom_edge(y, height) < EDGE_TOLERANCE_PX


def check_fsd_axis_alignment(report: CaseReport, suffix: str) -> None:
    fsd_name = f"FSD_{suffix}"
    fnm = point(report, f"FNM_{suffix}")
    fsp = point(report, f"FSP_{suffix}")
    fsd = point(report, fsd_name)
    fsd_item = report.landmarks.get(fsd_name)

    if not fsd_item or not fsd_item.present or fsd is None:
        return

    bounds_status, bounds_details = classify_bounds(fsd[0], fsd[1], report.width, report.height)
    near_bottom = is_fsd_near_bottom_edge(fsd[1], report.height)

    if bounds_status == "OUT_OF_IMAGE":
        add(
            report,
            "WARNING",
            "fsd_axis_not_evaluable",
            fsd_name,
            (
                f"{fsd_name} : alignement axial non évaluable — point hors image "
                f"(coords=({fsd[0]:.1f}, {fsd[1]:.1f}), image={report.width:.0f}x{report.height:.0f}, "
                f"distance bord inférieur={bounds_details['dist_bottom']:.1f} px)."
            ),
        )
        return

    if not fnm or not fsp:
        add(
            report,
            "WARNING",
            "fsd_axis_not_evaluable",
            fsd_name,
            (
                f"{fsd_name} : alignement axial non évaluable — "
                f"axe FNM→FSP incomplet (FNM={'ok' if fnm else 'absent'}, FSP={'ok' if fsp else 'absent'})."
            ),
        )
        return

    axis_length = distance(fnm, fsp)
    min_axis_length = report.height * FSD_MIN_AXIS_HEIGHT_RATIO
    if axis_length < min_axis_length:
        add(
            report,
            "WARNING",
            "fsd_axis_not_evaluable",
            fsd_name,
            (
                f"{fsd_name} : alignement axial non évaluable — segment FNM→FSP trop court "
                f"({axis_length:.1f} px < {min_axis_length:.1f} px)."
            ),
        )
        return

    perpendicular = deviation_from_line(fnm, fsp, fsd)
    if math.isnan(perpendicular):
        add(
            report,
            "WARNING",
            "fsd_axis_not_evaluable",
            fsd_name,
            f"{fsd_name} : alignement axial non évaluable — distance perpendiculaire indéfinie.",
        )
        return

    fnm_fsd_length = distance(fnm, fsd)
    if fnm_fsd_length <= 0:
        add(
            report,
            "WARNING",
            "fsd_axis_not_evaluable",
            fsd_name,
            f"{fsd_name} : alignement axial non évaluable — longueur FNM→FSD nulle.",
        )
        return

    norm_fnm_fsd = perpendicular / fnm_fsd_length
    norm_height = perpendicular / report.height
    dist_bottom = bounds_details["dist_bottom"]

    metrics = (
        f"écart perpendiculaire={perpendicular:.1f} px, "
        f"ratio/FNM→FSD={norm_fnm_fsd:.3f}, ratio/hauteur={norm_height:.3f}, "
        f"FNM→FSD={fnm_fsd_length:.1f} px, distance bord inférieur={dist_bottom:.1f} px"
    )

    if near_bottom or bounds_status == "EDGE":
        add(
            report,
            "WARNING",
            "fsd_axis_edge",
            fsd_name,
            (
                f"{fsd_name} : point distal proche du bord inférieur — alignement axial FNM→FSP "
                f"non concluant à ce niveau ({metrics}). "
                f"Raison : FSD distal en bord d'image, sans conclusion automatique sur la qualité du point."
            ),
        )
        return

    if norm_fnm_fsd > FSD_AXIS_NORM_WARN:
        add(
            report,
            "WARNING",
            "fsd_axis_geometry",
            fsd_name,
            (
                f"{fsd_name} : écart axial normalisé élevé ({metrics}, "
                f"seuil ratio/FNM→FSD={FSD_AXIS_NORM_WARN:.2f}) — "
                f"incohérence géométrique possible, revue manuelle recommandée "
                f"(sans correction automatique)."
            ),
        )


def check_femoral_coherence(report: CaseReport, suffix: str) -> None:
    fhc = point(report, f"FHC_{suffix}")
    fnm = point(report, f"FNM_{suffix}")
    fsp = point(report, f"FSP_{suffix}")
    fsd = point(report, f"FSD_{suffix}")

    if fhc and fnm and fsp:
        angle = angle_at_middle(fhc, fnm, fsp)
        deviation = axis_collinearity_deviation(angle)
        if not math.isnan(deviation) and deviation > AXIS_ANGLE_WARN_DEG:
            add(
                report,
                "WARNING",
                "femoral_axis",
                f"FNM_{suffix}",
                (
                    f"Axe fémoral {suffix} : angle FHC→FNM→FSP = {angle:.1f}°, "
                    f"écart à la colinéarité = {deviation:.1f}° (> {AXIS_ANGLE_WARN_DEG:.0f}°)."
                ),
            )

    if fnm and fsp and fsd:
        angle_fsp = angle_at_middle(fnm, fsp, fsd)
        deviation_fsp = axis_collinearity_deviation(angle_fsp)
        if not math.isnan(deviation_fsp) and deviation_fsp > AXIS_ANGLE_WARN_DEG:
            add(
                report,
                "WARNING",
                "femoral_axis",
                f"FSP_{suffix}",
                (
                    f"Diaphyse {suffix} : angle FNM→FSP→FSD = {angle_fsp:.1f}°, "
                    f"écart à la colinéarité = {deviation_fsp:.1f}° (> {AXIS_ANGLE_WARN_DEG:.0f}°)."
                ),
            )

    check_fsd_axis_alignment(report, suffix)

    if fsp and fsd and fsd[1] <= fsp[1]:
        add(
            report,
            "WARNING",
            "femoral_distal",
            f"FSD_{suffix}",
            (
                f"FSD_{suffix} devrait être plus distal que FSP_{suffix} "
                f"(y FSD={fsd[1]:.1f}, y FSP={fsp[1]:.1f})."
            ),
        )


def check_acetabular(report: CaseReport, suffix: str) -> None:
    asl = point(report, f"ASL_{suffix}")
    asm = point(report, f"ASM_{suffix}")
    fhc = point(report, f"FHC_{suffix}")
    if asl and asm:
        if suffix == "R" and asl[0] > asm[0]:
            add(
                report,
                "WARNING",
                "acetabular",
                f"ASL_{suffix}",
                f"ASL_{suffix} devrait être latéral à ASM_{suffix} (x ASL={asl[0]:.1f}, ASM={asm[0]:.1f}).",
            )
        if suffix == "L" and asl[0] < asm[0]:
            add(
                report,
                "WARNING",
                "acetabular",
                f"ASL_{suffix}",
                f"ASL_{suffix} devrait être latéral à ASM_{suffix} (x ASL={asl[0]:.1f}, ASM={asm[0]:.1f}).",
            )
    if asl and fhc and asl[1] >= fhc[1]:
        add(
            report,
            "WARNING",
            "acetabular",
            f"ASL_{suffix}",
            f"ASL_{suffix} devrait être au-dessus de FHC_{suffix} (y ASL={asl[1]:.1f}, FHC={fhc[1]:.1f}).",
        )
    if asm and fhc and asm[1] >= fhc[1]:
        add(
            report,
            "WARNING",
            "acetabular",
            f"ASM_{suffix}",
            f"ASM_{suffix} devrait être au-dessus de FHC_{suffix} (y ASM={asm[1]:.1f}, FHC={fhc[1]:.1f}).",
        )


def human_chain_distances(case_id: str, suffix: str) -> dict[str, float] | None:
    json_path = ANNOT_DIR / f"{case_id}.json"
    if not json_path.is_file():
        return None
    data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    by_name = {str(item.get("name")): item for item in data.get("landmarks", []) if isinstance(item, dict)}

    def human_point(name: str) -> tuple[float, float] | None:
        item = by_name.get(name)
        if not item or item.get("v") != 2:
            return None
        x, y = item.get("x"), item.get("y")
        if x is None or y is None:
            return None
        return float(x), float(y)

    chain = [f"FHC_{suffix}", f"FNM_{suffix}", f"FSP_{suffix}", f"FSD_{suffix}"]
    coords = [human_point(name) for name in chain]
    if any(coord is None for coord in coords):
        return None
    return {
        "FHC_FNM": distance(coords[0], coords[1]),
        "FNM_FSP": distance(coords[1], coords[2]),
        "FSP_FSD": distance(coords[2], coords[3]),
    }


def predicted_chain_distances(report: CaseReport, suffix: str) -> dict[str, float] | None:
    chain = [f"FHC_{suffix}", f"FNM_{suffix}", f"FSP_{suffix}", f"FSD_{suffix}"]
    coords = [point(report, name) for name in chain]
    if any(coord is None for coord in coords):
        return None
    assert all(coord is not None for coord in coords)
    return {
        "FHC_FNM": distance(coords[0], coords[1]),
        "FNM_FSP": distance(coords[1], coords[2]),
        "FSP_FSD": distance(coords[2], coords[3]),
    }


def check_bilateral(report: CaseReport) -> None:
    for suffix in ("R", "L"):
        pred = predicted_chain_distances(report, suffix)
        human = human_chain_distances(report.case_id, suffix)
        if pred and human:
            for key in pred:
                if human[key] <= 0:
                    continue
                ratio = pred[key] / human[key]
                if ratio > BILATERAL_RATIO_WARN or ratio < 1 / BILATERAL_RATIO_WARN:
                    add(
                        report,
                        "WARNING",
                        "bilateral_reference",
                        f"FHC_{suffix}",
                        (
                            f"Segment {key} ({suffix}) : distance prédite/humaine = {ratio:.2f} "
                            f"(ref. humaine {human[key]:.1f} px, prédite {pred[key]:.1f} px)."
                        ),
                    )

    for key in ("FHC_FNM", "FNM_FSP", "FSP_FSD"):
        right = predicted_chain_distances(report, "R")
        left = predicted_chain_distances(report, "L")
        if not right or not left:
            continue
        if right[key] <= 0 or left[key] <= 0:
            continue
        ratio = right[key] / left[key]
        if ratio > BILATERAL_RATIO_WARN or ratio < 1 / BILATERAL_RATIO_WARN:
            add(
                report,
                "WARNING",
                "bilateral_symmetry",
                "BILATERAL",
                (
                    f"Segment {key} : ratio droite/gauche = {ratio:.2f} "
                    f"(R={right[key]:.1f} px, L={left[key]:.1f} px)."
                ),
            )


def validate_case(case_id: str) -> CaseReport:
    width, height = read_image_size(case_id)
    report = CaseReport(case_id=case_id, width=width, height=height, landmarks=parse_prediction(case_id, width, height))

    check_completeness_and_confidence(report)
    check_bounds_and_side(report)
    for suffix in ("R", "L"):
        check_vertical_order(report, suffix)
        check_femoral_coherence(report, suffix)
        check_acetabular(report, suffix)
    check_bilateral(report)
    return report


def warnings_summary(report: CaseReport) -> str:
    if not report.anomalies:
        return "none"
    parts = [f"{item.category}:{item.landmark}" for item in report.anomalies[:8]]
    if len(report.anomalies) > 8:
        parts.append(f"+{len(report.anomalies) - 8} more")
    return "; ".join(parts)


def write_csv(reports: list[CaseReport]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "case_id",
                "completeness",
                "low_confidence_count",
                "critical_count",
                "warnings",
                "status",
            ],
        )
        writer.writeheader()
        for report in reports:
            writer.writerow(
                {
                    "case_id": report.case_id,
                    "completeness": f"{report.present_count}/14",
                    "low_confidence_count": report.low_confidence_count,
                    "critical_count": report.critical_count,
                    "warnings": report.warning_count,
                    "status": report.status,
                }
            )


def write_markdown(reports: list[CaseReport]) -> None:
    ok = sum(1 for report in reports if report.status == "OK")
    warning = sum(1 for report in reports if report.status == "WARNING")
    critical = sum(1 for report in reports if report.status == "CRITICAL")
    ranked = sorted(
        reports,
        key=lambda report: (report.critical_count, report.warning_count, -report.present_count),
        reverse=True,
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Validation anatomique V2 — new_26",
        "",
        f"**Généré le :** {now}",
        "**Nature :** contrôle qualité automatique, pas un diagnostic médical.",
        "",
        "## Résumé global",
        "",
        f"- Cas analysés : **{len(reports)}**",
        f"- OK : **{ok}**",
        f"- WARNING : **{warning}**",
        f"- CRITICAL : **{critical}**",
        "",
        "## Classement des radios les plus problématiques",
        "",
        "| Rang | Cas | Statut | Complétude | Confiance basse | CRITICAL | WARNING |",
        "|------|-----|--------|------------|-----------------|----------|---------|",
    ]

    for index, report in enumerate(ranked[:15], start=1):
        lines.append(
            f"| {index} | {report.case_id} | {report.status} | {report.present_count}/14 | "
            f"{report.low_confidence_count} | {report.critical_count} | {report.warning_count} |"
        )

    for report in ranked:
        lines.extend(
            [
                "",
                f"## {report.case_id} — {report.status}",
                "",
                f"- Complétude : **{report.present_count}/14**",
                f"- Confiance < {WARN_CONF} : **{report.low_confidence_count}**",
                f"- Anomalies CRITICAL : **{report.critical_count}**",
                f"- Anomalies WARNING : **{report.warning_count}**",
                "",
                "### Confiance par landmark",
                "",
                "| Landmark | Présent | Confiance |",
                "|----------|---------|-----------|",
            ]
        )
        for _landmark_id, name in LANDMARKS:
            item = report.landmarks[name]
            lines.append(
                f"| {name} | {'oui' if item.present else 'non'} | {item.confidence:.3f} |"
            )

        if report.anomalies:
            lines.extend(["", "### Anomalies", ""])
            for anomaly in report.anomalies:
                lines.append(
                    f"- **{anomaly.level}** [{anomaly.category}] {anomaly.landmark} — {anomaly.message}"
                )
        else:
            lines.extend(["", "### Anomalies", "", "- Aucune anomalie détectée."])

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Les points ne sont jamais corrigés automatiquement.",
            "- CRITICAL inclut les landmarks absents (confiance < 0.25), OUT_OF_IMAGE (> 1 px hors limites) et certaines ruptures majeures d'ordre vertical.",
            "- EDGE signale un point sur le bord ou à ≤ 1 px d'un bord, y compris le bord inférieur (WARNING).",
            "- Les angles proches de 180° sur l'axe fémoral sont considérés cohérents (écart ≤ 25°).",
            "- FSD : l'écart à l'axe FNM→FSP est normalisé par la longueur FNM→FSD (seuil géométrique "
            f"{FSD_AXIS_NORM_WARN:.2f}). Les points distaux en bord inférieur sont signalés séparément "
            "(fsd_axis_edge) sans conclusion automatique.",
            "- Les catégories fsd_axis_geometry, fsd_axis_edge et fsd_axis_not_evaluable ne modifient "
            "jamais les coordonnées prédites.",
            "- Les comparaisons bilatérales signalent des écarts marqués, sans conclure à une erreur certaine.",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    case_ids = [f"B26_{index:02d}" for index in range(1, 27)]
    reports: list[CaseReport] = []
    errors: list[str] = []

    for case_id in case_ids:
        try:
            reports.append(validate_case(case_id))
        except Exception as exc:
            errors.append(f"{case_id}: {exc}")
            print(f"ERROR {case_id}: {exc}")

    if reports:
        write_csv(reports)
        write_markdown(reports)

    ok = sum(1 for report in reports if report.status == "OK")
    warning = sum(1 for report in reports if report.status == "WARNING")
    critical = sum(1 for report in reports if report.status == "CRITICAL")

    print("VALIDATION COMPLETE")
    print(f"Cases: {len(case_ids)}")
    print(f"OK: {ok}")
    print(f"WARNING: {warning}")
    print(f"CRITICAL: {critical}")
    print(f"CSV={OUTPUT_CSV}")
    print(f"MD={OUTPUT_MD}")
    if errors:
        print("ERRORS=" + "; ".join(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
