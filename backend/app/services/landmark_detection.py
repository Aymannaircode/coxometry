"""Façade détection de landmarks : détecteur + reprojection optionnelle.

Orchestration :

    PreprocessedImage
        ↓ LandmarkDetector.detect()
    DetectedLandmark (espace prétraité)
        ↓ reproject_landmarks()
    ReprojectedLandmark (image originale)
        ↓ adaptateur → mvp_geometry

Aucune inférence, aucun poids, aucune coordonnée anatomique inventée.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from .detection import (
    DetectedLandmark,
    LandmarkDetectionResult,
    LandmarkDetector,
    ReprojectedLandmark,
    get_default_detector,
    reproject_landmarks,
    reprojection_meta_from_preprocessed,
)
from .preprocessing import PreprocessedImage


@dataclass(frozen=True)
class DetectionResult:
    """Résultat exposé au pipeline / API (compatibilité ascendante)."""

    status: str
    message: str
    landmarks: Optional[list] = None
    preprocessed_landmarks: Tuple[DetectedLandmark, ...] = ()
    original_landmarks: Tuple[ReprojectedLandmark, ...] = ()
    detector_name: Optional[str] = None


def detect_landmarks(
    preprocessed: PreprocessedImage | None = None,
    detector: LandmarkDetector | None = None,
    *,
    reproject: bool = True,
) -> DetectionResult:
    """Exécute le détecteur sur une image prétraitée.

    - `preprocessed=None` : retourne `not_implemented` (JSON mode=image sans octets).
    - `reproject=True` : reprojette les landmarks vers l'image originale
      lorsque la détection renvoie `status=ok` et des points.
    """
    if preprocessed is None:
        return DetectionResult(
            status="not_implemented",
            message=(
                "La détection IA des landmarks (image → landmarks) n'est pas encore "
                "implémentée. Aucune coordonnée n'est générée automatiquement. "
                "Utiliser mode=landmarks avec des points fournis manuellement, "
                "ou uploader une image (multipart) une fois un détecteur disponible."
            ),
            detector_name="not_implemented",
        )

    active = detector or get_default_detector()
    raw: LandmarkDetectionResult = active.detect(preprocessed)

    original: Tuple[ReprojectedLandmark, ...] = ()
    if reproject and raw.status == "ok" and raw.landmarks:
        meta = reprojection_meta_from_preprocessed(preprocessed)
        original = reproject_landmarks(raw.landmarks, meta)

    return DetectionResult(
        status=raw.status,
        message=raw.message or "",
        preprocessed_landmarks=raw.landmarks,
        original_landmarks=original,
        detector_name=raw.detector_name or active.name,
    )


def reprojected_to_geometry_inputs(
    landmarks: Sequence[ReprojectedLandmark],
) -> list[dict]:
    """Prépare des entrées compatibles `LandmarkIn` / `mvp_geometry`.

    Seuls les points `in_image_bounds` reçoivent `v=2` ; les autres `v=0`.
    Aucune coordonnée n'est inventée.
    """
    return [
        {
            "name": item.name,
            "x": item.x if item.in_image_bounds else None,
            "y": item.y if item.in_image_bounds else None,
            "v": 2 if item.in_image_bounds else 0,
        }
        for item in landmarks
    ]
