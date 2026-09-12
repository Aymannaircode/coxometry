"""Factory de détecteurs — V2 (compatibilité) ou V5 Phase 2 (démo / 16 KP).

Le défaut **code** reste ``v2`` lorsque ``MODEL_VERSION`` est absent
(compatibilité et tests). Pour une démonstration V5, utiliser
``backend/run_demo.ps1`` ou exporter explicitement
``MODEL_VERSION=v5_phase2`` avant uvicorn.
"""

from __future__ import annotations

import os
from typing import Literal

from .base import LandmarkDetector
from .yolo_pose import YoloPoseLandmarkDetector

ModelVersion = Literal["v2", "v5_phase2"]

_DEFAULT_VERSION: ModelVersion = "v2"
_ENV_VAR = "MODEL_VERSION"


def get_model_version() -> ModelVersion:
    """Lit ``MODEL_VERSION``.

    Valeurs acceptées : ``v2``, ``v5``, ``v5_phase2``, ``phase2``.
    Absent / autre → ``v2`` (compatibilité). Démo → forcer ``v5_phase2``.
    """
    raw = os.environ.get(_ENV_VAR, _DEFAULT_VERSION).strip().lower()
    if raw in ("v5", "v5_phase2", "phase2"):
        return "v5_phase2"
    return "v2"


def get_landmark_detector(version: ModelVersion | None = None) -> LandmarkDetector:
    """Retourne le détecteur demandé (défaut code : V2 via ``get_model_version``)."""
    active = version or get_model_version()
    if active == "v5_phase2":
        from .v5_phase2_pose import V5Phase2LandmarkDetector

        return V5Phase2LandmarkDetector()
    return YoloPoseLandmarkDetector()
