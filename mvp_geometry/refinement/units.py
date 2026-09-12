"""Unités de coordonnées pour le refinement ASL_L.

``TRAIN_ASM_OFFSET_CALIBRATION`` est défini en **pixels image originale**
(annotations GT pleine résolution). L'inférence YOLO s'exécute en espace
prétraité letterbox ; l'offset doit être converti avant application :

    dx_pre = dx_original × letterbox_scale
    dy_pre = dy_original × letterbox_scale

Aucune recalibration : seule la conversion d'unités est effectuée.
"""

from __future__ import annotations

from enum import Enum

from .calibration import AslLCalibration, TRAIN_ASM_OFFSET_CALIBRATION


class LandmarkCoordinateSpace(str, Enum):
    """Espace dans lequel des coordonnées ou offsets de landmarks sont exprimés."""

    ORIGINAL_IMAGE_PIXELS = "original_image_pixels"
    PREPROCESSED_LETTERBOX_PIXELS = "preprocessed_letterbox_pixels"


# Espace officiel de la calibration TRAIN (non modifiable).
TRAIN_CALIBRATION_COORDINATE_SPACE = LandmarkCoordinateSpace.ORIGINAL_IMAGE_PIXELS


def calibration_for_preprocessed_space(
    calibration: AslLCalibration,
    letterbox_scale: float,
) -> AslLCalibration:
    """Convertit un offset calibré en pixels originaux vers l'espace prétraité.

    Lève ``ValueError`` si ``letterbox_scale`` n'est pas strictement positif.
    """
    if letterbox_scale <= 0:
        raise ValueError(f"letterbox_scale doit être > 0, reçu {letterbox_scale!r}.")

    return AslLCalibration(
        dx=calibration.dx * letterbox_scale,
        dy=calibration.dy * letterbox_scale,
        source=calibration.source,
        n_train_cases=calibration.n_train_cases,
        method=calibration.method,
        notes=(
            f"{calibration.notes} "
            f"[unités converties : {TRAIN_CALIBRATION_COORDINATE_SPACE.value} → "
            f"{LandmarkCoordinateSpace.PREPROCESSED_LETTERBOX_PIXELS.value}, "
            f"scale={letterbox_scale}]"
        ),
    )


def expected_original_offset_from_refined(
    asm_x: float,
    asm_y: float,
    asl_refined_x: float,
    asl_refined_y: float,
) -> tuple[float, float]:
    """Offset effectif (dx, dy) en pixels originaux après refinement."""
    return (asl_refined_x - asm_x, asl_refined_y - asm_y)


__all__ = [
    "LandmarkCoordinateSpace",
    "TRAIN_ASM_OFFSET_CALIBRATION",
    "TRAIN_CALIBRATION_COORDINATE_SPACE",
    "calibration_for_preprocessed_space",
    "expected_original_offset_from_refined",
]
