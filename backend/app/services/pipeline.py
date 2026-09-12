"""Orchestration du pipeline backend MVP.

Flux cible :

    Image → prétraitement → IA landmarks → landmarks structurés
         → mvp_geometry → VCE / Tönnis / CCD → réponse API

État actuel :
- branche `landmarks` : opérationnelle (saisie manuelle → géométrie) ;
- branche `image` : upload + prétraitement + reprojection branchés ;
  le détecteur IA par défaut reste `not_implemented` (pas de faux landmarks).
"""

from __future__ import annotations

from typing import List, Literal, Optional, Sequence

from ..schemas.landmarks import LandmarkIn
from ..schemas.measurements import (
    InputMode,
    MeasurementsRequest,
    MeasurementsResponse,
)
from . import landmark_detection
from .geometry import compute_measurements
from .preprocessing import (
    PreprocessConfig,
    PreprocessingError,
    preprocess_image,
)

# Configuration API du prétraitement (letterbox prêt pour un futur modèle).
DEFAULT_IMAGE_PREPROCESS = PreprocessConfig(target_size=(512, 512))

SideLiteral = Literal["R", "L"]


def run_measurements(request: MeasurementsRequest) -> MeasurementsResponse:
    """Exécute le pipeline selon le mode demandé (corps JSON)."""
    if request.mode == InputMode.image:
        # JSON mode=image sans octets : pas d'upload → pas de détection inventée.
        detection = landmark_detection.detect_landmarks(None)
        return MeasurementsResponse(
            status="not_implemented",
            mode=InputMode.image,
            source="image",
            message=detection.message,
            sides=None,
        )

    # mode=landmarks : les points viennent exclusivement de l'appelant.
    assert request.landmarks is not None  # garanti par le validateur Pydantic
    sides = compute_measurements(request.landmarks, sides=request.sides)
    return MeasurementsResponse(
        status="ok",
        mode=InputMode.landmarks,
        source="manual_landmarks",
        message=None,
        sides=sides,
    )


def run_measurements_from_image(
    image_bytes: bytes,
    sides: Optional[Sequence[SideLiteral]] = None,
) -> MeasurementsResponse:
    """Pipeline image uploadée → prétraitement → détection → géométrie.

    Si le détecteur actif n'est pas opérationnel, retourne `not_implemented`
    sans inventer de landmarks ni appeler `mvp_geometry` avec des points fictifs.
    """
    try:
        preprocessed = preprocess_image(image_bytes, DEFAULT_IMAGE_PREPROCESS)
    except PreprocessingError as exc:
        return MeasurementsResponse(
            status="error",
            mode=InputMode.image,
            source="image",
            message=str(exc),
            sides=None,
        )

    detection = landmark_detection.detect_landmarks(preprocessed)

    if detection.status != "ok":
        status = detection.status if detection.status in ("not_implemented", "error") else "error"
        return MeasurementsResponse(
            status=status,  # type: ignore[arg-type]
            mode=InputMode.image,
            source="image",
            message=detection.message or None,
            sides=None,
        )

    geometry_inputs = landmark_detection.reprojected_to_geometry_inputs(
        detection.original_landmarks
    )
    landmarks = [LandmarkIn.model_validate(item) for item in geometry_inputs]
    if not landmarks:
        return MeasurementsResponse(
            status="error",
            mode=InputMode.image,
            source="image",
            message=(
                "Détection signalée ok mais aucun landmark exploitable "
                "après reprojection."
            ),
            sides=None,
        )

    side_list: Optional[List[SideLiteral]] = list(sides) if sides is not None else None
    measured = compute_measurements(landmarks, sides=side_list)
    return MeasurementsResponse(
        status="ok",
        mode=InputMode.image,
        source="image",
        message=None,
        sides=measured,
    )
