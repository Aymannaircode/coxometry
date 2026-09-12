#!/usr/bin/env python3
"""Inférence YOLO Pose new_26 V2 — génère des prédictions .txt depuis best.pt.

Sources : DICOM originaux (bassin/a_annoter/) rendus en PNG 1:1.
Sortie  : datasets/yolo_pose_new_26/predictions_v2/ (labels + overlays + mapping).

Ne modifie ni DICOM, ni JSON manuels, ni labels ground truth.
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent.parent / "manual_annotation_tool"
sys.path.insert(0, str(TOOL_DIR))

from dicom_render import read_dicom_dimensions, render_dicom_png  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"
MAPPING_CSV = DATASET_ROOT / "meta" / "source_mapping.csv"
MODEL_PATH = PROJECT_ROOT / "runs" / "pose" / "runs" / "pose" / "runs" / "yolo_pose_new_26_v2-3" / "weights" / "best.pt"
PREDICTIONS_ROOT = DATASET_ROOT / "predictions_v2"
IMAGES_DIR = PREDICTIONS_ROOT / "images"
LABELS_DIR = PREDICTIONS_ROOT / "labels"
OVERLAYS_DIR = PREDICTIONS_ROOT / "overlays"
EXPECTED_LABEL_COLS = 47  # 5 bbox + 14*3 keypoints (ground truth)
EXPECTED_PRED_COLS = 48  # +1 detection confidence when save_conf=True
NKPT = 14
DETECTION_CONF_INDEX = -1  # appended after keypoints when save_conf=True
KEYPOINTS_START = 5  # after class cx cy w h


def load_cases() -> list[dict[str, str]]:
    with MAPPING_CSV.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows.sort(key=lambda row: row["pilot_id"])
    if len(rows) != 26:
        raise RuntimeError(f"Attendu 26 cas dans source_mapping.csv, trouvé {len(rows)}")
    return rows


def render_source_images(cases: list[dict[str, str]]) -> list[dict[str, str]]:
    rendered: list[dict[str, str]] = []
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for row in cases:
        pilot_id = row["pilot_id"]
        dicom_path = PROJECT_ROOT / row["source_dicom"].replace("\\", "/")
        image_name = f"{pilot_id}.png"
        png_path = IMAGES_DIR / image_name
        if not dicom_path.is_file():
            raise FileNotFoundError(f"DICOM absent pour {pilot_id}: {dicom_path}")
        width, height = read_dicom_dimensions(dicom_path)
        render_dicom_png(dicom_path, png_path)
        rendered.append(
            {
                "pilot_id": pilot_id,
                "image": str(png_path.relative_to(PREDICTIONS_ROOT)),
                "source_dicom": row["source_dicom"],
                "image_width": str(width),
                "image_height": str(height),
            }
        )
    return rendered


def run_inference() -> Path:
    from ultralytics import YOLO

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")

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
    if not raw_labels.is_dir():
        raise RuntimeError(f"Dossier labels Ultralytics absent : {raw_labels}")

    LABELS_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

    mapping_rows: list[dict[str, str]] = []
    for row in cases:
        pilot_id = row["pilot_id"]
        src_label = raw_labels / f"{pilot_id}.txt"
        dst_label = LABELS_DIR / f"{pilot_id}.txt"
        if not src_label.is_file():
            mapping_rows.append(
                {
                    "pilot_id": pilot_id,
                    "image": f"images/{pilot_id}.png",
                    "prediction_file": "",
                    "status": "missing",
                    "visible_keypoints": "0",
                    "label_columns": "0",
                    "error": "fichier prédiction absent",
                }
            )
            continue
        shutil.copy2(src_label, dst_label)

        overlay_src = run_dir / f"{pilot_id}.jpg"
        if overlay_src.is_file():
            shutil.copy2(overlay_src, OVERLAYS_DIR / f"{pilot_id}.jpg")

        line = dst_label.read_text(encoding="utf-8").strip()
        cols = line.split() if line else []
        visible = 0
        detection_conf = ""
        valid_format = len(cols) == EXPECTED_PRED_COLS
        if valid_format:
            detection_conf = cols[DETECTION_CONF_INDEX]
            kpts = [float(value) for value in cols[KEYPOINTS_START:DETECTION_CONF_INDEX]]
            for index in range(NKPT):
                kpt_conf = kpts[index * 3 + 2]
                if kpt_conf > 0.25:
                    visible += 1

        mapping_rows.append(
            {
                "pilot_id": pilot_id,
                "image": f"images/{pilot_id}.png",
                "prediction_file": f"labels/{pilot_id}.txt",
                "status": "ok" if valid_format else "invalid_format",
                "visible_keypoints": str(visible),
                "detection_confidence": detection_conf,
                "label_columns": str(len(cols)),
                "error": "" if valid_format else f"colonnes={len(cols)}",
            }
        )

    shutil.rmtree(run_dir, ignore_errors=True)
    return mapping_rows


def write_mapping(mapping_rows: list[dict[str, str]]) -> None:
    path = PREDICTIONS_ROOT / "prediction_mapping.csv"
    fieldnames = [
        "pilot_id",
        "image",
        "prediction_file",
        "status",
        "visible_keypoints",
        "detection_confidence",
        "label_columns",
        "error",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mapping_rows)


def write_report(mapping_rows: list[dict[str, str]]) -> None:
    ok = [row for row in mapping_rows if row["status"] == "ok"]
    missing = [row for row in mapping_rows if row["status"] != "ok"]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": str(MODEL_PATH.relative_to(PROJECT_ROOT)),
        "model_sha256_prefix": None,
        "source": "bassin/a_annoter/ (DICOM → PNG 1:1)",
        "predictions_root": str(PREDICTIONS_ROOT.relative_to(PROJECT_ROOT)),
        "total_cases": len(mapping_rows),
        "predictions_ok": len(ok),
        "predictions_missing_or_invalid": len(missing),
        "settings": {"save": True, "save_txt": True, "save_conf": True},
        "cases": mapping_rows,
    }
    (PREDICTIONS_ROOT / "inference_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    print(f"MODEL={MODEL_PATH.resolve()}")
    print(f"OUTPUT={PREDICTIONS_ROOT.resolve()}")
    cases = load_cases()
    print(f"Rendering {len(cases)} DICOM -> {IMAGES_DIR} ...")
    render_source_images(cases)

    print(f"Inference with {MODEL_PATH.resolve()} ...")
    run_dir = run_inference()

    print("Organizing outputs ...")
    mapping_rows = organize_outputs(run_dir, cases)
    write_mapping(mapping_rows)
    write_report(mapping_rows)

    ok_count = sum(1 for row in mapping_rows if row["status"] == "ok")
    print(f"DONE predictions_ok={ok_count}/{len(mapping_rows)}")
    print(f"MODEL={MODEL_PATH.resolve()}")
    print(f"OUTPUT={PREDICTIONS_ROOT.resolve()}")
    print(f"LABELS={LABELS_DIR.resolve()}")
    print(f"MAPPING={(PREDICTIONS_ROOT / 'prediction_mapping.csv').resolve()}")
    if ok_count != 26:
        failed = [row["pilot_id"] for row in mapping_rows if row["status"] != "ok"]
        print(f"FAILED={','.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
