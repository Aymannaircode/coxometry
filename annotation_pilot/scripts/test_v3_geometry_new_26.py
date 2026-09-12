#!/usr/bin/env python3
"""Géométrie V3 (VCE / Tönnis / CCD) depuis predictions_v3/."""

from __future__ import annotations

import csv
import sys
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
LABELS_DIR = DATASET_ROOT / "predictions_v3" / "labels"
IMAGES_DIR = DATASET_ROOT / "predictions_v3" / "images"
OUTPUT_CSV = DATASET_ROOT / "v3_geometry_results.csv"
OUTPUT_MD = DATASET_ROOT / "v3_geometry_results.md"
SIDES = ("R", "L")


@dataclass
class CaseGeometryResult:
    case_id: str
    status: str = "error"
    error: str = ""
    sides: dict[str, SideResult] | None = None


def read_image_dimensions(image_path: Path) -> tuple[float, float]:
    from PIL import Image

    with Image.open(image_path) as image:
        w, h = image.size
    return float(w), float(h)


def _measure_value(measure: MeasurementResult) -> str:
    if measure.available and measure.value_deg is not None:
        return f"{measure.value_deg:.2f}"
    return ""


def process_case(case_id: str) -> CaseGeometryResult:
    result = CaseGeometryResult(case_id=case_id)
    try:
        width, height = read_image_dimensions(IMAGES_DIR / f"{case_id}.png")
        landmarks = landmarks_from_yolo_label(LABELS_DIR / f"{case_id}.txt", width, height)
        result.sides = compute_all_sides(landmarks)
        result.status = "ok"
    except Exception as exc:
        result.error = str(exc)
    return result


def main() -> int:
    case_ids = sorted(p.stem for p in LABELS_DIR.glob("B26_*.txt"))
    rows_out: list[dict[str, str]] = []
    for case_id in case_ids:
        res = process_case(case_id)
        row: dict[str, str] = {"case_id": case_id, "status": res.status}
        if res.sides:
            for side in SIDES:
                sr = res.sides[side]
                row[f"VCE_{side}"] = _measure_value(sr.vce)
                row[f"Tonnis_{side}"] = _measure_value(sr.tonnis)
                row[f"CCD_{side}"] = _measure_value(sr.ccd)
        rows_out.append(row)

    fields = ["case_id", "status"] + [f"{m}_{s}" for m in ("VCE", "Tonnis", "CCD") for s in SIDES]
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows_out)

    OUTPUT_MD.write_text(
        f"# Géométrie V3\n\nGénéré : {datetime.now(timezone.utc).isoformat()}\n\n"
        f"Source : predictions_v3/\n\nVoir `{OUTPUT_CSV.name}`\n",
        encoding="utf-8",
    )
    print(f"V3 GEOMETRY COMPLETE cases={len(rows_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
