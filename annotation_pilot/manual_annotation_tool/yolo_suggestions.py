"""Chargement des prédictions YOLO Pose comme suggestions (lecture seule)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PREDICTIONS_LABELS_DIR = (
    PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions" / "labels"
)

LANDMARKS = [
    ("LM-01", "TD_R", "right"),
    ("LM-02", "TD_L", "left"),
    ("LM-03", "FHC_R", "right"),
    ("LM-04", "FHC_L", "left"),
    ("LM-05", "ASL_R", "right"),
    ("LM-06", "ASL_L", "left"),
    ("LM-07", "ASM_R", "right"),
    ("LM-08", "ASM_L", "left"),
    ("LM-09", "FNM_R", "right"),
    ("LM-10", "FNM_L", "left"),
    ("LM-11", "FSP_R", "right"),
    ("LM-12", "FSP_L", "left"),
    ("LM-13", "FSD_R", "right"),
    ("LM-14", "FSD_L", "left"),
]

NKPT = len(LANDMARKS)
KEYPOINTS_START = 5
MIN_KEYPOINT_CONF = 0.25


def prediction_path_for(pilot_id: str) -> Path:
    return PREDICTIONS_LABELS_DIR / f"{pilot_id}.txt"


def predictions_available_for(pilot_id: str) -> bool:
    return prediction_path_for(pilot_id).is_file()


def parse_prediction_line(line: str, width: float, height: float) -> dict[str, Any]:
    values = line.strip().split()
    if len(values) not in {47, 48}:
        raise ValueError(f"Format YOLO inattendu : {len(values)} colonnes.")

    detection_conf = float(values[-1]) if len(values) == 48 else None
    keypoint_values = [float(value) for value in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    if len(keypoint_values) != NKPT * 3:
        raise ValueError("Nombre de keypoints invalide dans la prédiction YOLO.")

    suggestions: list[dict[str, Any]] = []
    for index, (landmark_id, name, side) in enumerate(LANDMARKS):
        x_norm = keypoint_values[index * 3]
        y_norm = keypoint_values[index * 3 + 1]
        kpt_conf = keypoint_values[index * 3 + 2]
        suggestions.append(
            {
                "id": landmark_id,
                "name": name,
                "side": side,
                "x": round(x_norm * width, 2) if kpt_conf >= MIN_KEYPOINT_CONF else None,
                "y": round(y_norm * height, 2) if kpt_conf >= MIN_KEYPOINT_CONF else None,
                "confidence": round(kpt_conf, 6),
                "visible": kpt_conf >= MIN_KEYPOINT_CONF,
            }
        )

    return {
        "source": "yolo_prediction",
        "pilot_id": None,
        "detection_confidence": detection_conf,
        "image_width": width,
        "image_height": height,
        "suggestions": suggestions,
    }


def load_yolo_suggestions(pilot_id: str, width: float, height: float) -> dict[str, Any] | None:
    path = prediction_path_for(pilot_id)
    if not path.is_file():
        return None
    if width <= 0 or height <= 0:
        raise ValueError("Les dimensions image doivent être positives.")

    line = path.read_text(encoding="utf-8").strip()
    if not line:
        return None
    payload = parse_prediction_line(line, width, height)
    payload["pilot_id"] = pilot_id
    payload["prediction_file"] = str(path.relative_to(PROJECT_ROOT))
    return payload
