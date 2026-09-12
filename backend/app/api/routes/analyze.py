"""Route POST /analyze — radiographie → détection landmarks → mesures."""

from __future__ import annotations

from typing import Annotated, Union

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.datastructures import UploadFile

from ...schemas.analyze import AnalyzeErrorResponse, AnalyzeSuccessResponse
from ...services.analyze import analyze_result_to_dict, run_analyze_from_bytes
from ...services.detection.base import LandmarkDetector
from ...services.detection.model_factory import get_landmark_detector

router = APIRouter(tags=["analyze"])

_UPLOAD_FIELD_NAMES = ("file", "image")


def get_landmark_detector_dep() -> LandmarkDetector:
    """Fournisseur de détecteur selon ``MODEL_VERSION`` (défaut code : v2)."""
    return get_landmark_detector()


AnalyzeResponseModel = Annotated[
    Union[AnalyzeSuccessResponse, AnalyzeErrorResponse],
    ...,
]


@router.post(
    "/analyze",
    response_model=AnalyzeResponseModel,
    summary="Analyser une radiographie pelvienne",
    response_description=(
        "Réponse ``status=ok`` : ``model_version`` (v2 ou v5_phase2), landmarks "
        "reprojetés (espace image originale), mesures VCE / Tönnis / CCD. "
        "En V5 : ``it_landmarks`` (IT_R / IT_L) avec ``quality`` "
        "accept / review / unavailable. Aucune coordonnée inventée."
    ),
)
async def post_analyze(
    request: Request,
    detector: LandmarkDetector = Depends(get_landmark_detector_dep),
) -> AnalyzeSuccessResponse | AnalyzeErrorResponse:
    """Accepte une radiographie en multipart/form-data (PNG, JPG, JPEG).

    Pipeline : validation → prétraitement (V2 512² ou V5 640² selon le modèle) →
    détection assistée par IA → reprojection → QC IT (V5) → mesures géométriques.

    Sélection du modèle via ``MODEL_VERSION`` (`v2` par défaut si absent ;
    démo : ``backend/run_demo.ps1`` → ``v5_phase2``).

    Les images ne sont pas persistées ; les octets sont traités en mémoire.
    """
    content_type = (request.headers.get("content-type") or "").lower()
    if not content_type.startswith("multipart/form-data"):
        raise HTTPException(
            status_code=422,
            detail="Content-Type multipart/form-data requis avec un fichier image.",
        )

    form = await request.form()
    upload: UploadFile | None = None
    for name in _UPLOAD_FIELD_NAMES:
        candidate = form.get(name)
        if isinstance(candidate, UploadFile):
            upload = candidate
            break

    if upload is None:
        raise HTTPException(
            status_code=422,
            detail=(
                "multipart/form-data exige un fichier image sous le champ "
                "'file' (ou 'image') au format PNG, JPG ou JPEG."
            ),
        )

    try:
        image_bytes = await upload.read()
    finally:
        await upload.close()

    result = run_analyze_from_bytes(
        image_bytes,
        filename=upload.filename,
        content_type=upload.content_type,
        detector=detector,
    )
    # FastAPI sérialise le modèle Pydantic ; conversion explicite pour cohérence.
    payload = analyze_result_to_dict(result)
    if payload["status"] == "ok":
        return AnalyzeSuccessResponse.model_validate(payload)
    return AnalyzeErrorResponse.model_validate(payload)
