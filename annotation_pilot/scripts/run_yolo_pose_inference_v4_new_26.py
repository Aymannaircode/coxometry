#!/usr/bin/env python3
"""Inférence YOLO Pose V4 new_26 — 26 DICOM → prédictions predictions_v4/."""

from __future__ import annotations

import csv
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent.parent / "manual_annotation_tool"
sys.path.insert(0, str(TOOL_DIR))

from dicom_render import render_dicom_png  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"
MAPPING_CSV = DATASET_ROOT / "meta" / "source_mapping.csv"
MODEL_PATH = PROJECT_ROOT / "runs" / "pose" / "yolo_pose_new_26_v4" / "weights" / "best.pt"
PREDICTIONS_ROOT = DATASET_ROOT / "predictions_v4"
IMAGES_DIR = PREDICTIONS_ROOT / "images"
LABELS_DIR = PREDICTIONS_ROOT / "labels"
OVERLAYS_DIR = PREDICTIONS_ROOT / "overlays"


def load_cases() -> list[dict[str, str]]:
    with MAPPING_CSV.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows.sort(key=lambda row: row["pilot_id"])
    return rows


def render_source_images(cases: list[dict[str, str]]) -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for row in cases:
        pilot_id = row["pilot_id"]
        dicom_path = PROJECT_ROOT / row["source_dicom"].replace("\\", "/")
        png_path = IMAGES_DIR / f"{pilot_id}.png"
        render_dicom_png(dicom_path, png_path)


def run_inference() -> Path:
    from ultralytics import YOLO

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Modèle V4 introuvable : {MODEL_PATH}")
    model = YOLO(str(MODEL_PATH))
    run_dir = PREDICTIONS_ROOT / "_ultralytics_run"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    model.predict(
        source=str(IMAGES_DIR),
        save=True,
        save_txt=True,
        save_conf=True,
        project=str(PREDICTIONS_ROOT),
        name="_ultralytics_run",
        exist_ok=True,
        verbose=False,
    )
    return run_dir


def organize_outputs(run_dir: Path, cases: list[dict[str, str]]) -> list[dict[str, str]]:
    raw_labels = run_dir / "labels"
    LABELS_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)
    mapping_rows: list[dict[str, str]] = []
    for row in cases:
        pilot_id = row["pilot_id"]
        src_label = raw_labels / f"{pilot_id}.txt"
        dst_label = LABELS_DIR / f"{pilot_id}.txt"
        if not src_label.is_file():
            mapping_rows.append({"pilot_id": pilot_id, "status": "missing"})
            continue
        shutil.copy2(src_label, dst_label)
        overlay_src = run_dir / f"{pilot_id}.jpg"
        if overlay_src.is_file():
            shutil.copy2(overlay_src, OVERLAYS_DIR / f"{pilot_id}.jpg")
        mapping_rows.append({"pilot_id": pilot_id, "status": "ok"})
    shutil.rmtree(run_dir, ignore_errors=True)
    return mapping_rows


def main() -> int:
    cases = load_cases()
    render_source_images(cases)
    run_dir = run_inference()
    mapping_rows = organize_outputs(run_dir, cases)
    ok = sum(1 for r in mapping_rows if r["status"] == "ok")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": str(MODEL_PATH.relative_to(PROJECT_ROOT)),
        "predictions_ok": ok,
        "total_cases": len(cases),
    }
    (PREDICTIONS_ROOT / "inference_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(f"V4 INFERENCE COMPLETE ok={ok}/{len(cases)}")
    print(f"MODEL={MODEL_PATH.resolve()}")
    print(f"LABELS={LABELS_DIR.resolve()}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
