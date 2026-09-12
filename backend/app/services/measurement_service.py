"""Pipeline image → détection YOLO V2 → mesures coxométriques (mvp_geometry).

Flux :

    PreprocessedImage
        ↓ YoloPoseLandmarkDetector.detect()
    result.landmarks (refined)
        ↓ compute_all_sides()
    VCE / Tönnis / CCD (R et L)
        ↓
    résultat structuré {status, detection, measurements, audit}

Aucune formule géométrique n'est recopiée ici. Aucune coordonnée inventée.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Literal, Optional, Sequence

from mvp_geometry.hip_measures import MeasurementResult, SideResult, compute_all_sides
from mvp_geometry.landmarks import MVP_LANDMARK_NAMES, Landmark

from .detection.base import DetectedLandmark, DetectionBoundingBox, LandmarkDetector
from .detection.reprojection import (
    ReprojectedLandmark,
    reproject_landmarks,
    reprojection_meta_from_preprocessed,
)
from .detection.yolo_pose import YoloPoseLandmarkDetector
from .preprocessing import PreprocessedImage

ORIGINAL_IMAGE_COORDINATE_SPACE = "original_image_pixels"

ServiceStatus = Literal["ok", "error"]

_MEASURE_LANDMARKS = {
    "vce": lambda side: ("TD_R", "TD_L", f"FHC_{side}", f"ASL_{side}"),
    "tonnis": lambda side: ("TD_R", "TD_L", f"ASM_{side}", f"ASL_{side}"),
    "ccd": lambda side: (f"FHC_{side}", f"FNM_{side}", f"FSP_{side}", f"FSD_{side}"),
}


@dataclass
class MeasureOut:
    """Mesure unitaire exposée par le service."""

    value_deg: Optional[float] = None
    available: bool = False
    reason: Optional[str] = None
    landmarks_used: Optional[tuple[str, ...]] = None


@dataclass
class SideMeasurementsOut:
    vce: MeasureOut
    tonnis: MeasureOut
    ccd: MeasureOut


@dataclass
class MeasurementsOut:
    right: SideMeasurementsOut
    left: SideMeasurementsOut


@dataclass
class CoordinateSpaceOut:
    """Métadonnées de reprojection prétraité → image originale."""

    image_width: int
    image_height: int
    preprocessed_width: int
    preprocessed_height: int
    scale: float
    pad_x: int
    pad_y: int
    landmark_coordinate_space: str = ORIGINAL_IMAGE_COORDINATE_SPACE


@dataclass
class DetectionOut:
    bounding_box: Optional[dict]
    raw_landmarks: list[dict]
    refined_landmarks: list[dict]
    it_landmarks: list[dict]
    confidences: dict[str, float]
    refinement_enabled: bool
    refinement_applied: bool
    coordinate_space: CoordinateSpaceOut


@dataclass
class MeasurementServiceResult:
    status: ServiceStatus
    detection: Optional[DetectionOut] = None
    measurements: Optional[MeasurementsOut] = None
    audit: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _landmark_side(name: str) -> str:
    if name.endswith("_R"):
        return "R"
    if name.endswith("_L"):
        return "L"
    return "?"


def _landmark_id(name: str) -> str:
    index = MVP_LANDMARK_NAMES.index(name)
    return f"LM-{index + 1:02d}"


def detected_to_mvp_landmarks(
    detected: Sequence[DetectedLandmark],
) -> Dict[str, Landmark]:
    """Convertit les landmarks détectés (v=2 implicite) en dict MVP."""
    result: Dict[str, Landmark] = {}
    for item in detected:
        result[item.name] = Landmark(
            id=_landmark_id(item.name),
            name=item.name,
            side=_landmark_side(item.name),
            x=item.x,
            y=item.y,
            v=2,
        )
    return result


def _detected_landmark_to_dict(item: DetectedLandmark) -> dict:
    payload: dict[str, Any] = {
        "name": item.name,
        "x": item.x,
        "y": item.y,
    }
    if item.confidence is not None:
        payload["confidence"] = item.confidence
    return payload


def _reprojected_landmark_to_dict(item: ReprojectedLandmark) -> dict:
    """Sérialise un landmark reprojeté (espace image originale)."""
    payload: dict[str, Any] = {
        "name": item.name,
        "x": item.x,
        "y": item.y,
    }
    if item.confidence is not None:
        payload["confidence"] = item.confidence
    return payload


def _coordinate_space_out(image: PreprocessedImage) -> CoordinateSpaceOut:
    orig_w, orig_h = image.original_size
    prep_w, prep_h = image.processed_size
    return CoordinateSpaceOut(
        image_width=orig_w,
        image_height=orig_h,
        preprocessed_width=prep_w,
        preprocessed_height=prep_h,
        scale=image.scale,
        pad_x=image.pad_left,
        pad_y=image.pad_top,
    )


def _bbox_to_dict(bbox: DetectionBoundingBox) -> dict:
    return {
        "x1": bbox.x1,
        "y1": bbox.y1,
        "x2": bbox.x2,
        "y2": bbox.y2,
        "confidence": bbox.confidence,
    }


def _measure_out(result: MeasurementResult, measure_key: str) -> MeasureOut:
    landmarks_used: Optional[tuple[str, ...]] = None
    if result.available:
        landmarks_used = _MEASURE_LANDMARKS[measure_key](result.side)
    return MeasureOut(
        value_deg=result.value_deg,
        available=result.available,
        reason=result.reason,
        landmarks_used=landmarks_used,
    )


def _side_out(side_result: SideResult) -> SideMeasurementsOut:
    return SideMeasurementsOut(
        vce=_measure_out(side_result.vce, "vce"),
        tonnis=_measure_out(side_result.tonnis, "tonnis"),
        ccd=_measure_out(side_result.ccd, "ccd"),
    )


def compute_measurements_from_landmarks(
    landmarks: Dict[str, Landmark],
) -> MeasurementsOut:
    """Calcule VCE / Tönnis / CCD via ``compute_all_sides`` sans détection."""
    sides = compute_all_sides(landmarks)
    return MeasurementsOut(
        right=_side_out(sides["R"]),
        left=_side_out(sides["L"]),
    )


def _it_landmark_to_dict(item) -> dict:
    """Sérialise un landmark IT (espace prétraité ou reprojeté)."""
    payload: dict[str, Any] = {
        "name": item.name,
        "kp_index": item.kp_index,
        "v": item.v,
    }
    if item.confidence is not None:
        payload["confidence"] = item.confidence
    if item.v == 2 and item.x is not None and item.y is not None:
        payload["x"] = item.x
        payload["y"] = item.y
    else:
        payload["x"] = None
        payload["y"] = None
    return payload


def _reproject_it_landmarks(it_landmarks, meta) -> list[dict]:
    """Reprojette les IT identifiables (v=2) vers l'image originale."""
    from .detection.reprojection import reproject_point

    out: list[dict] = []
    for item in it_landmarks:
        if item.v != 2 or item.x is None or item.y is None:
            out.append(_it_landmark_to_dict(item))
            continue
        x_orig, y_orig, _, _ = reproject_point(item.x, item.y, meta)
        out.append(
            {
                "name": item.name,
                "kp_index": item.kp_index,
                "v": item.v,
                "x": x_orig,
                "y": y_orig,
                "confidence": item.confidence,
            }
        )
    return out


def _build_detection_out(
    detection_result,
    *,
    image: PreprocessedImage,
    refinement_enabled: bool,
    refinement_applied: bool,
    confidences: dict[str, float],
) -> tuple[DetectionOut, dict[str, Any]]:
    meta = reprojection_meta_from_preprocessed(image)
    raw_original = reproject_landmarks(detection_result.raw_landmarks, meta)
    refined_original = reproject_landmarks(detection_result.landmarks, meta)
    it_original = _reproject_it_landmarks(
        getattr(detection_result, "it_landmarks", ()), meta
    )

    it_qc_audit: dict[str, Any] = {}
    if it_original:
        from .detection.v5_it_qc import apply_qc_to_it_dicts, assess_it_landmarks_qc

        coord = _coordinate_space_out(image)
        qc_results = assess_it_landmarks_qc(
            it_original,
            image_width=coord.image_width,
            image_height=coord.image_height,
            mvp_landmarks=[
                _reprojected_landmark_to_dict(item) for item in refined_original
            ],
        )
        it_original = apply_qc_to_it_dicts(it_original, qc_results)
        it_qc_audit = {
            name: {"quality": result.quality, "quality_reasons": list(result.quality_reasons)}
            for name, result in qc_results.items()
        }

    bbox_dict = (
        _bbox_to_dict(detection_result.bounding_box)
        if detection_result.bounding_box is not None
        else None
    )
    return DetectionOut(
        bounding_box=bbox_dict,
        raw_landmarks=[_reprojected_landmark_to_dict(item) for item in raw_original],
        refined_landmarks=[_reprojected_landmark_to_dict(item) for item in refined_original],
        it_landmarks=it_original,
        confidences=dict(confidences),
        refinement_enabled=refinement_enabled,
        refinement_applied=refinement_applied,
        coordinate_space=_coordinate_space_out(image),
    ), it_qc_audit


def run_measurement_pipeline(
    image: PreprocessedImage,
    detector: LandmarkDetector | None = None,
) -> MeasurementServiceResult:
    """Exécute détection YOLO V2 puis calcul géométrique sur l'image prétraitée."""
    active = detector or YoloPoseLandmarkDetector()
    detection_result = active.detect(image)

    coord_meta = _coordinate_space_out(image)
    base_audit: dict[str, Any] = {
        "detector": detection_result.detector_name or active.name,
        "model_version": (
            detection_result.audit.get("model_version", "v2")
            if detection_result.audit
            else ("v5_phase2" if active.name == "yolo_pose_v5_phase2" else "v2")
        ),
        "detector_coordinate_space": detection_result.coordinate_space,
        "exposed_landmark_coordinate_space": ORIGINAL_IMAGE_COORDINATE_SPACE,
        "image_width": coord_meta.image_width,
        "image_height": coord_meta.image_height,
        "preprocessed_width": coord_meta.preprocessed_width,
        "preprocessed_height": coord_meta.preprocessed_height,
        "scale": coord_meta.scale,
        "pad_x": coord_meta.pad_x,
        "pad_y": coord_meta.pad_y,
    }
    if detection_result.audit:
        base_audit.update(detection_result.audit)

    if detection_result.status != "ok":
        return MeasurementServiceResult(
            status="error",
            detection=None,
            measurements=None,
            audit={
                **base_audit,
                "detection_status": detection_result.status,
                "detection_message": detection_result.message,
            },
        )

    confidences = {}
    if detection_result.audit and "keypoint_confidences" in detection_result.audit:
        confidences = dict(detection_result.audit["keypoint_confidences"])

    refinement_enabled = bool(
        detection_result.audit.get("refinement_enabled", False)
        if detection_result.audit
        else False
    )
    refinement_applied = bool(
        detection_result.audit.get("refinement_applied", False)
        if detection_result.audit
        else False
    )

    detection_out, it_qc_audit = _build_detection_out(
        detection_result,
        image=image,
        refinement_enabled=refinement_enabled,
        refinement_applied=refinement_applied,
        confidences=confidences,
    )

    # Mesures calculées en espace prétraité (comportement inchangé, angles invariantes).
    mvp_landmarks = detected_to_mvp_landmarks(detection_result.landmarks)
    measurements = compute_measurements_from_landmarks(mvp_landmarks)

    ok_audit: dict[str, Any] = {
        **base_audit,
        "detection_status": "ok",
        "landmark_count": len(detection_result.landmarks),
        "raw_landmark_count": len(detection_result.raw_landmarks),
    }
    if it_qc_audit:
        ok_audit["it_landmarks_qc"] = it_qc_audit

    return MeasurementServiceResult(
        status="ok",
        detection=detection_out,
        measurements=measurements,
        audit=ok_audit,
    )
