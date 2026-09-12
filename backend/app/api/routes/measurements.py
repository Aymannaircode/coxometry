"""Route POST /measurements."""

from __future__ import annotations

import json
from typing import List, Literal, Optional, Union

from fastapi import APIRouter, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.datastructures import UploadFile

from ...schemas.measurements import MeasurementsRequest, MeasurementsResponse
from ...services.pipeline import run_measurements, run_measurements_from_image

router = APIRouter(tags=["measurements"])

SideLiteral = Literal["R", "L"]
_UPLOAD_FIELD_NAMES = ("file", "image")


def _parse_sides_form(raw: Optional[Union[str, bytes]]) -> Optional[List[SideLiteral]]:
    """Interprète le champ form `sides` (JSON ou liste séparée par des virgules)."""
    if raw is None:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    text = raw.strip()
    if not text:
        return None

    try:
        if text.startswith("["):
            parsed = json.loads(text)
        else:
            parsed = [part.strip() for part in text.split(",") if part.strip()]
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail="Champ 'sides' invalide : JSON ou liste 'R,L' attendu.",
        ) from exc

    if not isinstance(parsed, list) or len(parsed) == 0:
        raise HTTPException(
            status_code=422,
            detail="Champ 'sides' invalide : liste non vide attendue.",
        )
    if any(item not in ("R", "L") for item in parsed):
        raise HTTPException(
            status_code=422,
            detail="Champ 'sides' invalide : seules les valeurs 'R' et 'L' sont autorisées.",
        )
    if len(set(parsed)) != len(parsed):
        raise HTTPException(
            status_code=422,
            detail="Champ 'sides' invalide : doublons interdits.",
        )
    return parsed  # type: ignore[return-value]


async def _measurements_from_multipart(request: Request) -> MeasurementsResponse:
    form = await request.form()
    upload: Optional[UploadFile] = None
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
                "'file' (ou 'image') au format JPG, JPEG ou PNG."
            ),
        )

    try:
        image_bytes = await upload.read()
    finally:
        await upload.close()

    sides = _parse_sides_form(form.get("sides"))  # type: ignore[arg-type]
    return run_measurements_from_image(image_bytes, sides=sides)


async def _measurements_from_json(request: Request) -> MeasurementsResponse:
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Corps JSON invalide.") from exc

    try:
        body = MeasurementsRequest.model_validate(payload)
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc

    return run_measurements(body)


@router.post(
    "/measurements",
    response_model=MeasurementsResponse,
    summary="Calculer VCE, Tönnis et CCD",
    response_description=(
        "Mesures géométriques si landmarks manuels fournis ; "
        "pipeline image (upload → prétraitement → détection) avec "
        "status=not_implemented tant qu'aucun détecteur IA n'est disponible."
    ),
)
async def post_measurements(request: Request) -> MeasurementsResponse:
    """Accepte landmarks JSON ou une radiographie multipart.

    - `application/json` + `mode=landmarks` : calcule via `mvp_geometry`.
    - `application/json` + `mode=image` : `not_implemented` (pas d'octets).
    - `multipart/form-data` + fichier JPG/JPEG/PNG : prétraitement →
      LandmarkDetector → reprojection → géométrie (détecteur actuel stub).
    """
    content_type = (request.headers.get("content-type") or "").lower()
    if content_type.startswith("multipart/form-data"):
        return await _measurements_from_multipart(request)
    return await _measurements_from_json(request)
