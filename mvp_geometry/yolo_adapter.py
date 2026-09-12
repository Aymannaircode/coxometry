"""Adaptateur lecture seule : labels YOLO Pose → landmarks MVP.

Convertit les fichiers `.txt` produits par l'inférence YOLO Pose (format
new_26) en `Dict[str, Landmark]` consommable par `compute_side` /
`compute_all_sides`. Aucune coordonnée n'est inventée.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence, Tuple

from .landmarks import MVP_LANDMARK_NAMES, Landmark

# Après `class cx cy w h` ; 14 keypoints × (x, y, conf) ; conf détection optionnelle.
KEYPOINTS_START = 5
NKPT = len(MVP_LANDMARK_NAMES)
VALID_LABEL_COLUMN_COUNTS = frozenset({47, 48})

# IDs source alignés sur datasets/yolo_pose_new_26/meta/keypoint_order.md
_LANDMARK_IDS = tuple(f"LM-{index:02d}" for index in range(1, NKPT + 1))


def _landmark_side(name: str) -> str:
    if name.endswith("_R"):
        return "R"
    if name.endswith("_L"):
        return "L"
    return "?"


def _parse_float_values(raw_values: Sequence[str], *, context: str) -> list[float]:
    try:
        return [float(value) for value in raw_values]
    except ValueError as error:
        raise ValueError(f"{context} : valeur numérique invalide ({error}).") from error


def parse_yolo_pose_line(
    line: str,
    image_width: float,
    image_height: float,
    *,
    keypoint_conf_threshold: float = 0.25,
) -> Dict[str, Landmark]:
    """Parse une ligne YOLO Pose et retourne les 14 landmarks MVP.

    Coordonnées normalisées `[0, 1]` converties en pixels :
    ``x_px = x_norm * image_width``, ``y_px = y_norm * image_height``.

    Keypoint avec confiance >= seuil : ``v=2`` et coordonnées en pixels.
    Keypoint sous le seuil : ``v=0``, ``x=None``, ``y=None``.
    """
    if image_width <= 0 or image_height <= 0:
        raise ValueError("Les dimensions image doivent être positives.")

    stripped = line.strip()
    if not stripped:
        raise ValueError("Label YOLO vide.")

    values = stripped.split()
    if len(values) not in VALID_LABEL_COLUMN_COUNTS:
        raise ValueError(
            f"Format YOLO inattendu : {len(values)} colonnes "
            f"(attendu 47 ou 48)."
        )

    keypoint_slice = slice(KEYPOINTS_START, -1 if len(values) == 48 else None)
    keypoint_values = _parse_float_values(
        values[keypoint_slice],
        context="Keypoints YOLO",
    )
    expected = NKPT * 3
    if len(keypoint_values) != expected:
        raise ValueError(
            f"Nombre de keypoints invalide : {len(keypoint_values) // 3} "
            f"(attendu {NKPT})."
        )

    landmarks: Dict[str, Landmark] = {}
    for index, name in enumerate(MVP_LANDMARK_NAMES):
        x_norm = keypoint_values[index * 3]
        y_norm = keypoint_values[index * 3 + 1]
        kpt_conf = keypoint_values[index * 3 + 2]
        usable = kpt_conf >= keypoint_conf_threshold
        landmarks[name] = Landmark(
            id=_LANDMARK_IDS[index],
            name=name,
            side=_landmark_side(name),
            x=round(x_norm * image_width, 2) if usable else None,
            y=round(y_norm * image_height, 2) if usable else None,
            v=2 if usable else 0,
        )
    return landmarks


def landmarks_from_yolo_label(
    label_path: str | Path,
    image_width: float,
    image_height: float,
    *,
    keypoint_conf_threshold: float = 0.25,
) -> Dict[str, Landmark]:
    """Charge un fichier label YOLO Pose V2 et retourne les landmarks MVP."""
    path = Path(label_path)
    if not path.is_file():
        raise FileNotFoundError(f"Label YOLO absent : {path}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Label YOLO vide : {path.name}")

    try:
        return parse_yolo_pose_line(
            text,
            image_width,
            image_height,
            keypoint_conf_threshold=keypoint_conf_threshold,
        )
    except ValueError as error:
        raise ValueError(f"{path.name} : {error}") from error


def landmarks_from_yolo_label_with_refinement(
    label_path: str | Path,
    image_width: float,
    image_height: float,
    *,
    keypoint_conf_threshold: float = 0.25,
    calibration=None,
    refinement_enabled: bool | None = None,
):
    """Parse un label YOLO V2 puis applique le refinement ASL_L si activé.

    Le parseur YOLO (`landmarks_from_yolo_label`) n'est pas modifié ; le
    refinement est une couche post-traitement optionnelle.
    """
    from .refinement.asl_l import refine_asl_l
    from .refinement.calibration import TRAIN_ASM_OFFSET_CALIBRATION

    landmarks = landmarks_from_yolo_label(
        label_path,
        image_width,
        image_height,
        keypoint_conf_threshold=keypoint_conf_threshold,
    )
    cal = calibration or TRAIN_ASM_OFFSET_CALIBRATION
    return refine_asl_l(
        landmarks,
        cal,
        enabled=refinement_enabled,
        image_width=image_width,
        image_height=image_height,
    )
