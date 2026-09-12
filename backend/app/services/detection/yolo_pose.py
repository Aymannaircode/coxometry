"""Détecteur YOLO Pose V2 — inférence Ultralytics + adaptateur MVP + refinement ASL_L.

Pipeline :

    PreprocessedImage
        ↓ Ultralytics YOLO Pose (best.pt V2)
    bbox + 14 keypoints (pixels, confiances)
        ↓ mvp_geometry.yolo_adapter (parse YOLO Pose)
    landmarks bruts MVP
        ↓ mvp_geometry.refinement (offset TRAIN converti → espace prétraité)
    landmarks refined → DetectedLandmark

Aucun poids n'est modifié. Le refinement ASL_L n'est pas dupliqué ici.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional, Sequence, Tuple

import numpy as np

from mvp_geometry.landmarks import MVP_LANDMARK_NAMES, Landmark
from mvp_geometry.refinement import (
    ASL_L_REFINEMENT_ENABLED,
    AslLRefinementResult,
    TRAIN_ASM_OFFSET_CALIBRATION,
    calibration_for_preprocessed_space,
)
from mvp_geometry.yolo_adapter import (
    landmarks_from_yolo_label,
    landmarks_from_yolo_label_with_refinement,
    parse_yolo_pose_line,
)

from ..preprocessing import PreprocessedImage
from .base import (
    DetectedLandmark,
    DetectionBoundingBox,
    LandmarkDetectionResult,
    LandmarkDetector,
)
from .reprojection import reproject_point, reprojection_meta_from_preprocessed

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_V2_MODEL_PATH = (
    PROJECT_ROOT / "runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt"
)
EXPECTED_KEYPOINTS = len(MVP_LANDMARK_NAMES)


class YoloPoseDetectorError(Exception):
    """Erreur fonctionnelle du détecteur YOLO Pose."""


class ModelNotFoundError(YoloPoseDetectorError):
    """Checkpoint V2 introuvable sur disque."""


class InvalidImageError(YoloPoseDetectorError):
    """Image prétraitée invalide ou vide."""


class NoDetectionError(YoloPoseDetectorError):
    """Aucune détection pelvis retournée par YOLO."""


class LowBboxConfidenceError(YoloPoseDetectorError):
    """Confiance bbox sous le seuil configuré."""


class MissingKeypointsError(YoloPoseDetectorError):
    """Keypoints absents ou incomplets."""


class UnexpectedYoloFormatError(YoloPoseDetectorError):
    """Structure de sortie Ultralytics inattendue."""


ModelLoader = Callable[[Path], object]


@dataclass(frozen=True)
class _ParsedYoloDetection:
    yolo_line: str
    bbox: DetectionBoundingBox
    keypoint_confidences: Dict[str, float]


def _default_model_loader(model_path: Path) -> object:
    try:
        from ultralytics import YOLO
    except ImportError as error:
        raise YoloPoseDetectorError(
            "Ultralytics non installé. Installer avec : pip install ultralytics"
        ) from error
    return YOLO(str(model_path))


def _preprocessed_to_uint8_rgb(image: PreprocessedImage) -> np.ndarray:
    array = image.array
    if array.size == 0:
        raise InvalidImageError("Tableau d'image vide.")
    if image.normalized:
        array = np.clip(array * 255.0, 0, 255).astype(np.uint8)
    else:
        array = array.astype(np.uint8)
    if array.ndim == 2:
        array = np.stack([array, array, array], axis=-1)
    elif array.ndim == 3 and array.shape[2] == 1:
        array = np.repeat(array, 3, axis=2)
    return array


def _build_yolo_pose_line(
    cx: float,
    cy: float,
    width: float,
    height: float,
    keypoints: Sequence[tuple[float, float, float]],
    detection_conf: float,
) -> str:
    if len(keypoints) != EXPECTED_KEYPOINTS:
        raise UnexpectedYoloFormatError(
            f"Nombre de keypoints inattendu : {len(keypoints)} (attendu {EXPECTED_KEYPOINTS})."
        )
    parts = ["0", f"{cx:.6f}", f"{cy:.6f}", f"{width:.6f}", f"{height:.6f}"]
    for x_norm, y_norm, conf in keypoints:
        parts.extend(f"{value:.6f}" for value in (x_norm, y_norm, conf))
    parts.append(f"{detection_conf:.6f}")
    return " ".join(parts)


def _bbox_from_xywhn(
    cx: float,
    cy: float,
    width: float,
    height: float,
    image_width: float,
    image_height: float,
    confidence: float,
) -> DetectionBoundingBox:
    cx_px = cx * image_width
    cy_px = cy * image_height
    w_px = width * image_width
    h_px = height * image_height
    return DetectionBoundingBox(
        x1=round(cx_px - w_px / 2.0, 2),
        y1=round(cy_px - h_px / 2.0, 2),
        x2=round(cx_px + w_px / 2.0, 2),
        y2=round(cy_px + h_px / 2.0, 2),
        confidence=confidence,
    )


def _tensor_values(value: object) -> np.ndarray:
    if hasattr(value, "cpu"):
        return value.cpu().numpy()
    if hasattr(value, "numpy") and callable(value.numpy):
        return value.numpy()
    return np.asarray(value)


def _scalar_value(value: object) -> float:
    if hasattr(value, "item") and callable(value.item):
        return float(value.item())
    return float(value)


def _best_detection_index(boxes: object) -> int:
    conf = boxes.conf
    if hasattr(conf, "argmax"):
        index = conf.argmax()
        if hasattr(index, "item"):
            return int(index.item())
        return int(index)
    values = _tensor_values(conf)
    return int(values.argmax())


def _parse_ultralytics_result(
    result: object,
    image_width: float,
    image_height: float,
    *,
    bbox_confidence_threshold: float,
) -> _ParsedYoloDetection:
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        raise NoDetectionError("Aucune détection pelvis.")

    best_index = _best_detection_index(boxes)
    det_conf = _scalar_value(boxes.conf[best_index])
    if det_conf < bbox_confidence_threshold:
        raise LowBboxConfidenceError(
            f"Confiance bbox insuffisante : {det_conf:.4f} < {bbox_confidence_threshold:.4f}."
        )

    xywhn_row = boxes.xywhn[best_index]
    xywhn = xywhn_row.tolist() if hasattr(xywhn_row, "tolist") else list(xywhn_row)
    if len(xywhn) != 4:
        raise UnexpectedYoloFormatError(f"BBox xywhn invalide : {xywhn!r}.")
    cx, cy, bw, bh = (float(value) for value in xywhn)

    keypoints = getattr(result, "keypoints", None)
    if keypoints is None:
        raise MissingKeypointsError("Keypoints absents dans la sortie YOLO.")

    if keypoints.xyn is None or keypoints.conf is None:
        raise MissingKeypointsError("Coordonnées ou confiances keypoints manquantes.")

    if len(keypoints.xyn) <= best_index:
        raise MissingKeypointsError("Index keypoints incohérent avec la bbox sélectionnée.")

    xyn = _tensor_values(keypoints.xyn[best_index])
    kpt_conf = _tensor_values(keypoints.conf[best_index])
    if xyn.shape[0] != EXPECTED_KEYPOINTS:
        raise UnexpectedYoloFormatError(
            f"Nombre de keypoints YOLO inattendu : {xyn.shape[0]} (attendu {EXPECTED_KEYPOINTS})."
        )

    triplets: list[tuple[float, float, float]] = []
    conf_map: Dict[str, float] = {}
    for index, name in enumerate(MVP_LANDMARK_NAMES):
        x_norm = float(xyn[index, 0])
        y_norm = float(xyn[index, 1])
        conf = float(kpt_conf[index]) if index < len(kpt_conf) else 0.0
        triplets.append((x_norm, y_norm, conf))
        conf_map[name] = conf

    line = _build_yolo_pose_line(cx, cy, bw, bh, triplets, det_conf)
    bbox = _bbox_from_xywhn(cx, cy, bw, bh, image_width, image_height, det_conf)
    return _ParsedYoloDetection(
        yolo_line=line,
        bbox=bbox,
        keypoint_confidences=conf_map,
    )


def _landmark_audit_entry(landmark: Landmark | None) -> dict | None:
    if landmark is None:
        return None
    return {
        "id": landmark.id,
        "name": landmark.name,
        "side": landmark.side,
        "x": landmark.x,
        "y": landmark.y,
        "v": landmark.v,
    }


def _mvp_landmarks_to_detected(
    landmarks: Dict[str, Landmark],
    keypoint_confidences: Dict[str, float],
) -> Tuple[DetectedLandmark, ...]:
    detected: list[DetectedLandmark] = []
    for name in MVP_LANDMARK_NAMES:
        landmark = landmarks.get(name)
        if landmark is None or not landmark.usable:
            continue
        detected.append(
            DetectedLandmark(
                name=name,
                x=float(landmark.x),
                y=float(landmark.y),
                confidence=keypoint_confidences.get(name),
            )
        )
    return tuple(detected)


def _apply_adapter_and_refinement(
    yolo_line: str,
    image_width: float,
    image_height: float,
    *,
    keypoint_conf_threshold: float,
    refinement_enabled: bool | None,
    calibration=None,
) -> tuple[Dict[str, Landmark], AslLRefinementResult]:
    """Parse YOLO + refinement ASL_L dans l'espace ``(image_width, image_height)``."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
        handle.write(yolo_line)
        temp_path = handle.name
    try:
        refinement = landmarks_from_yolo_label_with_refinement(
            temp_path,
            image_width,
            image_height,
            keypoint_conf_threshold=keypoint_conf_threshold,
            refinement_enabled=refinement_enabled,
            calibration=calibration,
        )
        raw_landmarks = landmarks_from_yolo_label(
            temp_path,
            image_width,
            image_height,
            keypoint_conf_threshold=keypoint_conf_threshold,
        )
    finally:
        os.unlink(temp_path)
    return raw_landmarks, refinement


def _refined_asl_l_out_of_bounds_original(
    image: PreprocessedImage,
    refined_x: float,
    refined_y: float,
) -> bool:
    """Vérifie ASL_L refined reprojeté dans les bornes de l'image originale."""
    meta = reprojection_meta_from_preprocessed(image)
    _, _, _, in_bounds = reproject_point(refined_x, refined_y, meta)
    return not in_bounds


class YoloPoseLandmarkDetector(LandmarkDetector):
    """Détecteur officiel YOLO Pose V2 + refinement ASL_L post-traitement."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        *,
        keypoint_conf_threshold: float = 0.25,
        bbox_confidence_threshold: float = 0.25,
        refinement_enabled: bool | None = None,
        model_loader: ModelLoader | None = None,
        load_on_init: bool = False,
    ) -> None:
        self._model_path = Path(model_path) if model_path is not None else DEFAULT_V2_MODEL_PATH
        if not self._model_path.is_absolute():
            self._model_path = PROJECT_ROOT / self._model_path
        self._keypoint_conf_threshold = keypoint_conf_threshold
        self._bbox_confidence_threshold = bbox_confidence_threshold
        self._refinement_enabled = refinement_enabled
        self._model_loader = model_loader or _default_model_loader
        self._model: object | None = None
        if load_on_init:
            self._ensure_model()

    @property
    def name(self) -> str:
        return "yolo_pose_v2"

    @property
    def model_path(self) -> Path:
        return self._model_path

    @property
    def model_loaded(self) -> bool:
        return self._model is not None

    @property
    def keypoint_names(self) -> Sequence[str]:
        return MVP_LANDMARK_NAMES

    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        if not self._model_path.is_file():
            raise ModelNotFoundError(
                f"Checkpoint V2 introuvable : {self._model_path}. "
                "Aucun poids alternatif n'est chargé."
            )
        self._model = self._model_loader(self._model_path)

    def _validate_image(self, image: PreprocessedImage) -> None:
        if image.status != "ok":
            raise InvalidImageError(f"Image prétraitée invalide (status={image.status!r}).")
        width, height = image.processed_size
        if width <= 0 or height <= 0:
            raise InvalidImageError(f"Dimensions image invalides : {image.processed_size!r}.")
        if image.array is None or image.array.size == 0:
            raise InvalidImageError("Tableau d'image vide.")

    def _run_inference(self, image: PreprocessedImage) -> object:
        self._ensure_model()
        assert self._model is not None
        rgb = _preprocessed_to_uint8_rgb(image)
        results = self._model.predict(rgb, verbose=False)
        if not results:
            raise NoDetectionError("Ultralytics n'a retourné aucun résultat.")
        return results[0]

    def detect(self, image: PreprocessedImage) -> LandmarkDetectionResult:
        """Infère YOLO V2, adapte via mvp_geometry et applique le refinement ASL_L."""
        try:
            self._validate_image(image)
            width, height = (float(image.processed_size[0]), float(image.processed_size[1]))

            yolo_result = self._run_inference(image)
            parsed = _parse_ultralytics_result(
                yolo_result,
                width,
                height,
                bbox_confidence_threshold=self._bbox_confidence_threshold,
            )

            preprocessed_cal = calibration_for_preprocessed_space(
                TRAIN_ASM_OFFSET_CALIBRATION,
                image.scale,
            )

            raw_mvp, refinement = _apply_adapter_and_refinement(
                parsed.yolo_line,
                width,
                height,
                keypoint_conf_threshold=self._keypoint_conf_threshold,
                refinement_enabled=self._refinement_enabled,
                calibration=preprocessed_cal,
            )

            refinement_out_of_bounds = refinement.out_of_bounds
            if refinement.applied and refinement.refined_x is not None and refinement.refined_y is not None:
                refinement_out_of_bounds = _refined_asl_l_out_of_bounds_original(
                    image,
                    refinement.refined_x,
                    refinement.refined_y,
                )

            raw_detected = _mvp_landmarks_to_detected(raw_mvp, parsed.keypoint_confidences)
            refined_detected = _mvp_landmarks_to_detected(
                refinement.landmarks,
                parsed.keypoint_confidences,
            )

            active_refinement = (
                ASL_L_REFINEMENT_ENABLED if self._refinement_enabled is None else self._refinement_enabled
            )

            audit = {
                "model_path": str(self._model_path),
                "refinement_enabled": active_refinement,
                "refinement_status": refinement.status.value,
                "refinement_applied": refinement.applied,
                "refinement_out_of_bounds": refinement_out_of_bounds,
                "refinement_coordinate_space": "preprocessed_letterbox_pixels",
                "calibration_coordinate_space": "original_image_pixels",
                "calibration_source": TRAIN_ASM_OFFSET_CALIBRATION.source,
                "calibration_dx": TRAIN_ASM_OFFSET_CALIBRATION.dx,
                "calibration_dy": TRAIN_ASM_OFFSET_CALIBRATION.dy,
                "calibration_dx_applied": preprocessed_cal.dx,
                "calibration_dy_applied": preprocessed_cal.dy,
                "letterbox_scale": image.scale,
                "original_asl_l": _landmark_audit_entry(refinement.original_asl_l),
                "raw_asl_l": _landmark_audit_entry(raw_mvp.get("ASL_L")),
                "refined_asl_l": _landmark_audit_entry(refinement.landmarks.get("ASL_L")),
                "detection_confidence": parsed.bbox.confidence,
                "keypoint_confidences": dict(parsed.keypoint_confidences),
                "yolo_line_columns": len(parsed.yolo_line.split()),
            }

            return LandmarkDetectionResult(
                status="ok",
                message=None,
                landmarks=refined_detected,
                raw_landmarks=raw_detected,
                bounding_box=parsed.bbox,
                detector_name=self.name,
                audit=audit,
            )
        except YoloPoseDetectorError as error:
            return LandmarkDetectionResult(
                status="error",
                message=str(error),
                landmarks=(),
                raw_landmarks=(),
                detector_name=self.name,
                audit={"model_path": str(self._model_path), "error_type": type(error).__name__},
            )
        except Exception as error:
            return LandmarkDetectionResult(
                status="error",
                message=f"Erreur inattendue YOLO Pose : {error}",
                landmarks=(),
                raw_landmarks=(),
                detector_name=self.name,
                audit={"model_path": str(self._model_path), "error_type": type(error).__name__},
            )


def build_yolo_pose_line_for_tests(
    cx: float,
    cy: float,
    width: float,
    height: float,
    keypoints: Sequence[tuple[float, float, float]],
    detection_conf: float,
) -> str:
    """Expose la construction de ligne YOLO pour les tests unitaires."""
    return _build_yolo_pose_line(cx, cy, width, height, keypoints, detection_conf)


def parse_yolo_line_to_mvp(
    line: str,
    image_width: float,
    image_height: float,
    *,
    keypoint_conf_threshold: float = 0.25,
) -> Dict[str, Landmark]:
    """Expose le parseur MVP pour les tests sans inférence."""
    return parse_yolo_pose_line(
        line,
        image_width,
        image_height,
        keypoint_conf_threshold=keypoint_conf_threshold,
    )
