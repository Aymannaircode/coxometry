"""Calibration TRAIN-only pour le refinement ASL_L (méthode C_asm_offset).

L'offset est fixé une fois à partir des 21 images TRAIN (annotations GT).
Il ne doit jamais être recalculé automatiquement à l'inférence.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Active le post-traitement ASL_L entre YOLO V2 et mvp_geometry.
# Peut être désactivé via variable d'environnement ASL_L_REFINEMENT_ENABLED=0|false.
ASL_L_REFINEMENT_ENABLED: bool = True

if "ASL_L_REFINEMENT_ENABLED" in os.environ:
    _raw = os.environ["ASL_L_REFINEMENT_ENABLED"].strip().lower()
    ASL_L_REFINEMENT_ENABLED = _raw in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class AslLCalibration:
    """Offset pixel ASM_L → ASL_L, calibré hors inférence."""

    dx: float
    dy: float
    source: str
    n_train_cases: int
    method: str = "C_asm_offset"
    notes: str = ""

    @property
    def is_train_only(self) -> bool:
        return self.source.upper() == "TRAIN"


# Calibration officielle — mean(GT ASL_L − GT ASM_L) sur 21 TRAIN (split seed=42).
# Ne pas recalculer à l'inférence ; VAL/GT du cas courant exclus du calibrage.
TRAIN_ASM_OFFSET_CALIBRATION = AslLCalibration(
    dx=511.56,
    dy=-92.68,
    source="TRAIN",
    n_train_cases=21,
    method="C_asm_offset",
    notes=(
        "Calibré exclusivement sur 21 images TRAIN (datasets/yolo_pose_new_26/meta/split.json). "
        "Validation VAL (5 cas) sans fuite : 471.72 px → 100.73 px, amélioration 78.6 %."
    ),
)
