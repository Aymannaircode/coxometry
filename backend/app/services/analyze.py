"""Orchestration API POST /analyze : upload → prétraitement → measurement pipeline."""

from __future__ import annotations

import re
from typing import Any, Union

from ..schemas.analyze import (
    AnalyzeCoordinateSpaceOut,
    AnalyzeDetectionOut,
    AnalyzeErrorDetail,
    AnalyzeErrorResponse,
    AnalyzeMeasureOut,
    AnalyzeMeasurementsOut,
    AnalyzeSideOut,
    AnalyzeSuccessResponse,
)
from .detection.base import LandmarkDetector
from .detection.model_factory import get_landmark_detector, get_model_version
from .detection.yolo_pose import YoloPoseLandmarkDetector
from .measurement_service import MeasurementServiceResult, MeasurementsOut, run_measurement_pipeline
from .preprocessing import (
    EmptyImageError,
    PreprocessConfig,
    PreprocessingError,
    UnreadableImageError,
    UnsupportedFormatError,
    preprocess_image,
)
from .preprocessing_v5 import preprocess_image_v5

# Limite raisonnable pour une radiographie (25 Mo).
MAX_UPLOAD_BYTES = 25 * 1024 * 1024

ALLOWED_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg"})
ALLOWED_CONTENT_TYPES = frozenset({"image/png", "image/jpeg"})

DEFAULT_ANALYZE_PREPROCESS = PreprocessConfig(target_size=(512, 512))

# Clés d'audit internes à ne pas exposer au client.
_SENSITIVE_AUDIT_KEYS = frozenset(
    {
        "model_path",
        "checkpoint_path",
        "error_type",
        "yolo_line_columns",
        "calibration_source",
        "calibration_dx",
        "calibration_dy",
        "original_asl_l",
        "raw_asl_l",
        "refined_asl_l",
    }
)

_ERROR_TYPE_TO_CODE: dict[str, str] = {
    "ModelNotFoundError": "model_not_found",
    "InvalidImageError": "invalid_image",
    "NoDetectionError": "no_detection",
    "LowBboxConfidenceError": "low_bbox_confidence",
    "MissingKeypointsError": "insufficient_landmarks",
    "UnexpectedYoloFormatError": "insufficient_landmarks",
}

_PREPROCESS_EXCEPTION_TO_CODE: dict[type[BaseException], tuple[str, str]] = {
    EmptyImageError: ("invalid_image", "Aucune donnée d'image fournie."),
    UnreadableImageError: ("invalid_image", "Image illisible ou corrompue."),
    UnsupportedFormatError: ("unsupported_format", "Format non supporté. Formats acceptés : PNG, JPG, JPEG."),
}

_GEOMETRY_REASON_KEYWORDS = (
    "indéterminée",
    "ITH",
    "confondus",
    "quasi nulle",
    "inconnue",
    "longueur quasi nulle",
)

_PATH_PATTERN = re.compile(r"(?:[A-Za-z]:\\|/)[^\s\"']+")


AnalyzeResponse = Union[AnalyzeSuccessResponse, AnalyzeErrorResponse]


def _default_detector() -> LandmarkDetector:
    return get_landmark_detector()


def _sanitize_message(message: str) -> str:
    """Retire chemins locaux et détails internes des messages client."""
    if not message:
        return "Erreur de traitement."
    if "introuvable" in message.lower() and ("checkpoint" in message.lower() or "best.pt" in message.lower()):
        return "Modèle de détection indisponible."
    cleaned = _PATH_PATTERN.sub("[chemin masqué]", message)
    if "Erreur inattendue" in cleaned:
        return "Erreur interne de détection."
    return cleaned


def _sanitize_audit(audit: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in audit.items():
        if key in _SENSITIVE_AUDIT_KEYS:
            continue
        if isinstance(value, str):
            sanitized[key] = _sanitize_message(value)
        elif isinstance(value, dict):
            sanitized[key] = {
                inner_key: inner_value
                for inner_key, inner_value in value.items()
                if inner_key not in _SENSITIVE_AUDIT_KEYS
            }
        else:
            sanitized[key] = value
    return sanitized


def validate_upload_metadata(
    *,
    filename: str | None,
    content_type: str | None,
    size_bytes: int,
) -> AnalyzeErrorResponse | None:
    """Valide taille, extension et type MIME avant décodage."""
    if size_bytes <= 0:
        return AnalyzeErrorResponse(
            error=AnalyzeErrorDetail(
                code="invalid_image",
                message="Fichier image vide.",
            )
        )
    if size_bytes > MAX_UPLOAD_BYTES:
        return AnalyzeErrorResponse(
            error=AnalyzeErrorDetail(
                code="file_too_large",
                message=f"Fichier trop volumineux (max {MAX_UPLOAD_BYTES // (1024 * 1024)} Mo).",
            )
        )

    extension = ""
    if filename:
        dot = filename.rfind(".")
        if dot >= 0:
            extension = filename[dot:].lower()

    if extension and extension not in ALLOWED_EXTENSIONS:
        return AnalyzeErrorResponse(
            error=AnalyzeErrorDetail(
                code="unsupported_format",
                message="Extension non supportée. Formats acceptés : PNG, JPG, JPEG.",
            )
        )

    if content_type:
        normalized = content_type.split(";", 1)[0].strip().lower()
        if normalized and normalized not in ALLOWED_CONTENT_TYPES:
            return AnalyzeErrorResponse(
                error=AnalyzeErrorDetail(
                    code="unsupported_format",
                    message="Type MIME non supporté. Formats acceptés : image/png, image/jpeg.",
                )
            )

    return None


def _measure_to_schema(measure) -> AnalyzeMeasureOut:
    landmarks_used = list(measure.landmarks_used) if measure.landmarks_used else None
    return AnalyzeMeasureOut(
        value_deg=measure.value_deg,
        available=measure.available,
        reason=measure.reason,
        landmarks_used=landmarks_used,
    )


def _side_to_schema(side) -> AnalyzeSideOut:
    return AnalyzeSideOut(
        vce=_measure_to_schema(side.vce),
        tonnis=_measure_to_schema(side.tonnis),
        ccd=_measure_to_schema(side.ccd),
    )


def _measurements_to_schema(measurements: MeasurementsOut) -> AnalyzeMeasurementsOut:
    return AnalyzeMeasurementsOut(
        right=_side_to_schema(measurements.right),
        left=_side_to_schema(measurements.left),
    )


def _detection_to_schema(detection) -> AnalyzeDetectionOut:
    cs = detection.coordinate_space
    from ..schemas.analyze import AnalyzeITLandmarkOut

    it_items = [
        AnalyzeITLandmarkOut(
            name=item["name"],
            kp_index=item["kp_index"],
            v=item["v"],
            x=item.get("x"),
            y=item.get("y"),
            confidence=item.get("confidence"),
            quality=item.get("quality"),
            quality_reasons=item.get("quality_reasons"),
        )
        for item in detection.it_landmarks
    ]
    return AnalyzeDetectionOut(
        bounding_box=detection.bounding_box,
        raw_landmarks=list(detection.raw_landmarks),
        refined_landmarks=list(detection.refined_landmarks),
        it_landmarks=it_items,
        refinement_enabled=detection.refinement_enabled,
        refinement_applied=detection.refinement_applied,
        coordinate_space=AnalyzeCoordinateSpaceOut(
            image_width=cs.image_width,
            image_height=cs.image_height,
            preprocessed_width=cs.preprocessed_width,
            preprocessed_height=cs.preprocessed_height,
            scale=cs.scale,
            pad_x=cs.pad_x,
            pad_y=cs.pad_y,
            landmark_coordinate_space="original_image_pixels",
        ),
    )


def _map_detection_failure(result: MeasurementServiceResult) -> AnalyzeErrorResponse:
    audit = result.audit or {}
    error_type = str(audit.get("error_type", ""))
    code = _ERROR_TYPE_TO_CODE.get(error_type, "detection_failed")
    raw_message = str(audit.get("detection_message") or "Échec de la détection.")
    return AnalyzeErrorResponse(
        error=AnalyzeErrorDetail(
            code=code,
            message=_sanitize_message(raw_message),
        )
    )


def _pelvis_geometry_failure(measurements: MeasurementsOut) -> bool:
    """VCE/Tönnis des deux côtés indisponibles pour cause géométrique."""
    pelvis_measures = (
        measurements.right.vce,
        measurements.left.vce,
        measurements.right.tonnis,
        measurements.left.tonnis,
    )
    if not all(not measure.available for measure in pelvis_measures):
        return False
    return any(
        measure.reason and any(keyword in measure.reason for keyword in _GEOMETRY_REASON_KEYWORDS)
        for measure in pelvis_measures
    )


def _success_from_pipeline(result: MeasurementServiceResult) -> AnalyzeResponse:
    assert result.detection is not None
    assert result.measurements is not None

    landmark_count = int(result.audit.get("landmark_count", 0))
    if landmark_count == 0:
        return AnalyzeErrorResponse(
            error=AnalyzeErrorDetail(
                code="insufficient_landmarks",
                message="Landmarks insuffisants pour le calcul des mesures.",
            )
        )

    if _pelvis_geometry_failure(result.measurements):
        first_reason = next(
            (
                measure.reason
                for side in (result.measurements.right, result.measurements.left)
                for measure in (side.vce, side.tonnis)
                if measure.reason
            ),
            "Construction géométrique indéterminée.",
        )
        return AnalyzeErrorResponse(
            error=AnalyzeErrorDetail(
                code="geometry_error",
                message=first_reason,
            )
        )

    model_version = str(result.audit.get("model_version", "v2"))
    if model_version not in ("v2", "v5_phase2"):
        model_version = "v2"

    return AnalyzeSuccessResponse(
        model_version=model_version,  # type: ignore[arg-type]
        detection=_detection_to_schema(result.detection),
        measurements=_measurements_to_schema(result.measurements),
        audit=_sanitize_audit(result.audit),
    )


def run_analyze_from_bytes(
    image_bytes: bytes,
    *,
    filename: str | None = None,
    content_type: str | None = None,
    detector: LandmarkDetector | None = None,
    model_version: str | None = None,
) -> AnalyzeResponse:
    """Pipeline complet analyze : validation → preprocess → measurement."""
    validation_error = validate_upload_metadata(
        filename=filename,
        content_type=content_type,
        size_bytes=len(image_bytes),
    )
    if validation_error is not None:
        return validation_error

    version = model_version or get_model_version()
    if detector is not None and detector.name == "yolo_pose_v5_phase2":
        version = "v5_phase2"
    elif detector is not None and detector.name == "yolo_pose_v2":
        version = "v2"
    if version not in ("v2", "v5_phase2"):
        version = "v2"

    try:
        if version == "v5_phase2":
            preprocessed = preprocess_image_v5(image_bytes)
        else:
            preprocessed = preprocess_image(image_bytes, DEFAULT_ANALYZE_PREPROCESS)
    except PreprocessingError as exc:
        mapped = _PREPROCESS_EXCEPTION_TO_CODE.get(type(exc))
        if mapped:
            code, message = mapped
        else:
            code, message = "invalid_image", _sanitize_message(str(exc))
        return AnalyzeErrorResponse(error=AnalyzeErrorDetail(code=code, message=message))
    except Exception:
        return AnalyzeErrorResponse(
            error=AnalyzeErrorDetail(
                code="invalid_image",
                message="Image illisible ou corrompue.",
            )
        )

    try:
        active_detector = detector or get_landmark_detector(version)  # type: ignore[arg-type]
        pipeline_result = run_measurement_pipeline(
            preprocessed,
            detector=active_detector,
        )
    except Exception:
        return AnalyzeErrorResponse(
            error=AnalyzeErrorDetail(
                code="internal_error",
                message="Erreur interne lors de l'analyse.",
            )
        )

    if pipeline_result.status != "ok":
        return _map_detection_failure(pipeline_result)

    return _success_from_pipeline(pipeline_result)


def analyze_result_to_dict(response: AnalyzeResponse) -> dict[str, Any]:
    """Sérialisation JSON stable."""
    if isinstance(response, AnalyzeSuccessResponse):
        return response.model_dump()
    return response.model_dump()
