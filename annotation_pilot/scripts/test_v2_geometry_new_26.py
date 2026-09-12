#!/usr/bin/env python3
"""Calcul VCE / Tönnis / CCD à partir des prédictions YOLO Pose V2 (new_26).

Parcourt les labels V2, convertit en landmarks MVP via `landmarks_from_yolo_label`,
appelle `compute_all_sides`, et écrit un CSV + un rapport Markdown.

Lecture seule sur labels, images et annotations humaines.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mvp_geometry.hip_measures import MeasurementResult, SideResult  # noqa: E402
from mvp_geometry.yolo_adapter import landmarks_from_yolo_label  # noqa: E402
from mvp_geometry import compute_all_sides  # noqa: E402

DATASET_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"
LABELS_DIR = DATASET_ROOT / "predictions_v2" / "labels"
IMAGES_DIR = DATASET_ROOT / "predictions_v2" / "images"
OUTPUT_CSV = DATASET_ROOT / "v2_geometry_results.csv"
OUTPUT_MD = DATASET_ROOT / "v2_geometry_results.md"

MEASURE_KEYS = ("VCE", "Tonnis", "CCD")
SIDES = ("R", "L")


@dataclass
class CaseGeometryResult:
    case_id: str
    image_width: float | None = None
    image_height: float | None = None
    usable_landmarks: int = 0
    status: str = "error"
    error: str = ""
    sides: dict[str, SideResult] | None = None
    unavailable_reasons: list[str] = field(default_factory=list)


def read_image_dimensions(image_path: Path) -> tuple[float, float]:
    if not image_path.is_file():
        raise FileNotFoundError(f"Image absente : {image_path}")
    try:
        from PIL import Image
    except ImportError as error:
        raise RuntimeError("Pillow requis pour lire les dimensions PNG.") from error

    with Image.open(image_path) as image:
        width, height = image.size
    if width <= 0 or height <= 0:
        raise ValueError(f"Dimensions invalides pour {image_path.name}.")
    return float(width), float(height)


def _measure_value(measure: MeasurementResult) -> str:
    if measure.available and measure.value_deg is not None:
        return f"{measure.value_deg:.2f}"
    return ""


def _collect_unavailable_reasons(sides: dict[str, SideResult]) -> list[str]:
    reasons: list[str] = []
    for side in SIDES:
        side_result = sides[side]
        for measure in (side_result.vce, side_result.tonnis, side_result.ccd):
            if not measure.available:
                label = f"{measure.name}_{side}"
                reason = measure.reason or "raison inconnue"
                reasons.append(f"{label}: {reason}")
    return reasons


def process_case(case_id: str) -> CaseGeometryResult:
    result = CaseGeometryResult(case_id=case_id)
    label_path = LABELS_DIR / f"{case_id}.txt"
    image_path = IMAGES_DIR / f"{case_id}.png"

    try:
        width, height = read_image_dimensions(image_path)
        result.image_width = width
        result.image_height = height

        landmarks = landmarks_from_yolo_label(label_path, width, height)
        result.usable_landmarks = sum(item.usable for item in landmarks.values())

        sides = compute_all_sides(landmarks)
        result.sides = sides
        result.unavailable_reasons = _collect_unavailable_reasons(sides)
        result.status = "ok"
    except Exception as error:
        result.status = "error"
        result.error = str(error)

    return result


def load_case_ids() -> list[str]:
    if not LABELS_DIR.is_dir():
        raise FileNotFoundError(f"Dossier labels V2 absent : {LABELS_DIR}")
    case_ids = sorted(path.stem for path in LABELS_DIR.glob("*.txt"))
    if not case_ids:
        raise RuntimeError(f"Aucun label V2 dans {LABELS_DIR}")
    return case_ids


def write_csv(rows: list[CaseGeometryResult], path: Path) -> None:
    fieldnames = [
        "case_id",
        "image_width",
        "image_height",
        "usable_landmarks",
        "status",
        "error",
        "VCE_R",
        "Tonnis_R",
        "CCD_R",
        "VCE_L",
        "Tonnis_L",
        "CCD_L",
        "unavailable_reasons",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            payload = {
                "case_id": row.case_id,
                "image_width": row.image_width if row.image_width is not None else "",
                "image_height": row.image_height if row.image_height is not None else "",
                "usable_landmarks": row.usable_landmarks,
                "status": row.status,
                "error": row.error,
                "unavailable_reasons": " | ".join(row.unavailable_reasons),
            }
            if row.sides is not None:
                payload["VCE_R"] = _measure_value(row.sides["R"].vce)
                payload["Tonnis_R"] = _measure_value(row.sides["R"].tonnis)
                payload["CCD_R"] = _measure_value(row.sides["R"].ccd)
                payload["VCE_L"] = _measure_value(row.sides["L"].vce)
                payload["Tonnis_L"] = _measure_value(row.sides["L"].tonnis)
                payload["CCD_L"] = _measure_value(row.sides["L"].ccd)
            else:
                for key in ("VCE_R", "Tonnis_R", "CCD_R", "VCE_L", "Tonnis_L", "CCD_L"):
                    payload[key] = ""
            writer.writerow(payload)


def _count_available_measures(rows: list[CaseGeometryResult]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        if row.sides is None:
            continue
        for side in SIDES:
            side_result = row.sides[side]
            for measure_name, measure in (
                ("VCE", side_result.vce),
                ("Tonnis", side_result.tonnis),
                ("CCD", side_result.ccd),
            ):
                if measure.available:
                    counts[f"{measure_name}_{side}"] += 1
    return counts


def write_markdown(rows: list[CaseGeometryResult], path: Path) -> None:
    ok_rows = [row for row in rows if row.status == "ok"]
    error_rows = [row for row in rows if row.status != "ok"]
    available_counts = _count_available_measures(ok_rows)
    total_cases = len(rows)
    total_slots = total_cases * len(SIDES) * len(MEASURE_KEYS)

    lines = [
        "# Résultats géométrie V2 — new_26",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        f"**Source labels :** `{LABELS_DIR.relative_to(PROJECT_ROOT).as_posix()}/`",
        f"**Source images :** `{IMAGES_DIR.relative_to(PROJECT_ROOT).as_posix()}/`",
        "",
        "## Résumé",
        "",
        f"- Radios traitées : **{total_cases}**",
        f"- Succès (`status=ok`) : **{len(ok_rows)}**",
        f"- Erreurs de parsing/chargement : **{len(error_rows)}**",
        "",
        "## Mesures disponibles par type",
        "",
        "| Mesure | Disponibles | Sur 26 |",
        "|--------|-------------|--------|",
    ]

    for measure in MEASURE_KEYS:
        for side in SIDES:
            key = f"{measure}_{side}"
            count = available_counts.get(key, 0)
            lines.append(f"| {key} | {count} | 26 |")

    total_available = sum(available_counts.values())
    lines.extend(
        [
            "",
            f"**Total mesures disponibles :** {total_available} / {total_slots}",
            "",
            "## Valeurs par radio (degrés)",
            "",
            "| Radio | VCE_R | Tönnis_R | CCD_R | VCE_L | Tönnis_L | CCD_L | Landmarks v=2 |",
            "|-------|-------|----------|-------|-------|----------|-------|---------------|",
        ]
    )

    for row in rows:
        if row.sides is None:
            lines.append(
                f"| {row.case_id} | — | — | — | — | — | — | {row.usable_landmarks} |"
            )
            continue
        sides = row.sides
        lines.append(
            "| {case_id} | {vce_r} | {tonnis_r} | {ccd_r} | {vce_l} | {tonnis_l} | {ccd_l} | {usable} |".format(
                case_id=row.case_id,
                vce_r=_measure_value(sides["R"].vce) or "—",
                tonnis_r=_measure_value(sides["R"].tonnis) or "—",
                ccd_r=_measure_value(sides["R"].ccd) or "—",
                vce_l=_measure_value(sides["L"].vce) or "—",
                tonnis_l=_measure_value(sides["L"].tonnis) or "—",
                ccd_l=_measure_value(sides["L"].ccd) or "—",
                usable=row.usable_landmarks,
            )
        )

    unavailable_rows = [row for row in ok_rows if row.unavailable_reasons]
    lines.extend(
        [
            "",
            "## Mesures indisponibles",
            "",
        ]
    )
    if not unavailable_rows:
        lines.append("Toutes les mesures sont disponibles pour les 26 radios.")
    else:
        for row in unavailable_rows:
            lines.append(f"### {row.case_id}")
            for reason in row.unavailable_reasons:
                lines.append(f"- {reason}")
            lines.append("")

    if error_rows:
        lines.extend(["", "## Erreurs de traitement", ""])
        for row in error_rows:
            lines.append(f"- **{row.case_id}** : {row.error}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    case_ids = load_case_ids()
    print(f"Traitement de {len(case_ids)} labels V2…")

    rows: list[CaseGeometryResult] = []
    for case_id in case_ids:
        row = process_case(case_id)
        rows.append(row)
        if row.status == "ok" and row.sides is not None:
            vce_r = _measure_value(row.sides["R"].vce) or "N/A"
            print(f"  {case_id}: ok — VCE_R={vce_r}, landmarks v=2={row.usable_landmarks}")
        else:
            print(f"  {case_id}: {row.status} — {row.error}")

    write_csv(rows, OUTPUT_CSV)
    write_markdown(rows, OUTPUT_MD)

    available_counts = _count_available_measures([row for row in rows if row.status == "ok"])
    print(f"\nCSV  : {OUTPUT_CSV.relative_to(PROJECT_ROOT)}")
    print(f"MD   : {OUTPUT_MD.relative_to(PROJECT_ROOT)}")
    print(f"Radios traitées : {len(rows)}")
    print(
        "Mesures disponibles — "
        f"VCE: R={available_counts.get('VCE_R', 0)}, L={available_counts.get('VCE_L', 0)} | "
        f"Tönnis: R={available_counts.get('Tonnis_R', 0)}, L={available_counts.get('Tonnis_L', 0)} | "
        f"CCD: R={available_counts.get('CCD_R', 0)}, L={available_counts.get('CCD_L', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
