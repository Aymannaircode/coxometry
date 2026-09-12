"""Post-traitement ASL_L indépendant : ASL_L_refined = ASM_L + offset.

Couche insérée entre la détection YOLO V2 et `mvp_geometry` (mesures).
Ne modifie ni les poids V2, ni les fichiers de prédiction, ni les annotations.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Dict, Optional

from ..landmarks import Landmark
from .calibration import ASL_L_REFINEMENT_ENABLED, AslLCalibration, TRAIN_ASM_OFFSET_CALIBRATION


class RefinementStatus(str, Enum):
    """État du post-traitement pour audit."""

    APPLIED = "applied"
    DISABLED = "disabled"
    ASM_L_ABSENT = "asm_l_absent"
    ASM_L_INVALID = "asm_l_invalid"


@dataclass(frozen=True)
class AslLRefinementResult:
    """Résultat du refinement avec landmarks modifiés et trace d'audit."""

    landmarks: Dict[str, Landmark]
    original_asl_l: Optional[Landmark]
    status: RefinementStatus
    applied: bool
    out_of_bounds: Optional[bool] = None
    refined_x: Optional[float] = None
    refined_y: Optional[float] = None
    calibration: Optional[AslLCalibration] = None


def _copy_landmarks(landmarks: Dict[str, Landmark]) -> Dict[str, Landmark]:
    return dict(landmarks)


def _is_out_of_bounds(
    x: float,
    y: float,
    image_width: Optional[float],
    image_height: Optional[float],
) -> Optional[bool]:
    if image_width is None or image_height is None:
        return None
    if image_width <= 0 or image_height <= 0:
        return None
    return x < 0 or y < 0 or x > image_width or y > image_height


def refine_asl_l(
    landmarks: Dict[str, Landmark],
    calibration: AslLCalibration,
    *,
    enabled: Optional[bool] = None,
    image_width: Optional[float] = None,
    image_height: Optional[float] = None,
) -> AslLRefinementResult:
    """Applique le refinement C_asm_offset sur ASL_L.

    Principe : ``ASL_L_refined = ASM_L + (dx, dy)`` avec offset TRAIN-only.

    Si ``ASM_L`` est absent ou non exploitable (``v != 2``), les landmarks
    sont retournés inchangés — on n'invente jamais ASL_L.

    L'``ASL_L`` original est conservé dans ``original_asl_l`` pour audit.
    Les autres landmarks (y compris ``ASM_L``) ne sont pas modifiés.
    """
    active = ASL_L_REFINEMENT_ENABLED if enabled is None else enabled
    working = _copy_landmarks(landmarks)
    original_asl = landmarks.get("ASL_L")

    if not active:
        return AslLRefinementResult(
            landmarks=working,
            original_asl_l=original_asl,
            status=RefinementStatus.DISABLED,
            applied=False,
            calibration=calibration,
        )

    asm = landmarks.get("ASM_L")
    if asm is None:
        return AslLRefinementResult(
            landmarks=working,
            original_asl_l=original_asl,
            status=RefinementStatus.ASM_L_ABSENT,
            applied=False,
            calibration=calibration,
        )

    if not asm.usable or asm.x is None or asm.y is None:
        return AslLRefinementResult(
            landmarks=working,
            original_asl_l=original_asl,
            status=RefinementStatus.ASM_L_INVALID,
            applied=False,
            calibration=calibration,
        )

    new_x = round(float(asm.x) + calibration.dx, 2)
    new_y = round(float(asm.y) + calibration.dy, 2)
    oob = _is_out_of_bounds(new_x, new_y, image_width, image_height)

    if original_asl is not None:
        refined_asl = replace(original_asl, x=new_x, y=new_y, v=2)
    else:
        refined_asl = Landmark(
            id="LM-06",
            name="ASL_L",
            side="L",
            x=new_x,
            y=new_y,
            v=2,
        )

    working["ASL_L"] = refined_asl

    return AslLRefinementResult(
        landmarks=working,
        original_asl_l=original_asl,
        status=RefinementStatus.APPLIED,
        applied=True,
        out_of_bounds=oob,
        refined_x=new_x,
        refined_y=new_y,
        calibration=calibration,
    )


def refine_asl_l_landmarks(
    landmarks: Dict[str, Landmark],
    calibration: Optional[AslLCalibration] = None,
    **kwargs,
) -> Dict[str, Landmark]:
    """Raccourci : retourne uniquement le dict de landmarks (refined ou inchangé)."""
    cal = calibration or TRAIN_ASM_OFFSET_CALIBRATION
    return refine_asl_l(landmarks, cal, **kwargs).landmarks
