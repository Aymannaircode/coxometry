"""Détecteur V5 Phase 2 — 16 KP via ``forward_head_preds`` (pas ``YOLO(best_it.pt)``).

Pipeline :
    PreprocessedImage 640×640 RGB
        ↓ YOLO V2 predict (14 KP + bbox, logique production identique)
        ↓ V5 forward_head_preds
        ↓ anchor = max IoU avec bbox YOLO (sans GT)
        ↓ IT_R / IT_L depuis V5 à cet anchor
"""

from __future__ import annotations

import importlib.util
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

import torch
import yaml

from mvp_geometry.landmarks import MVP_LANDMARK_NAMES
from mvp_geometry.refinement import (
    ASL_L_REFINEMENT_ENABLED,
    TRAIN_ASM_OFFSET_CALIBRATION,
    calibration_for_preprocessed_space,
)

from ..preprocessing import PreprocessedImage
from ..preprocessing_v5 import V5_IMGSZ, preprocessed_to_rgb_chw_float
from .base import (
    DetectedLandmark,
    DetectionBoundingBox,
    LandmarkDetectionResult,
    LandmarkDetector,
)
from .yolo_pose import (
    InvalidImageError,
    ModelNotFoundError,
    NoDetectionError,
    YoloPoseDetectorError,
    YoloPoseLandmarkDetector,
    _apply_adapter_and_refinement,
    _landmark_audit_entry,
    _mvp_landmarks_to_detected,
    _parse_ultralytics_result,
    _preprocessed_to_uint8_rgb,
    _refined_asl_l_out_of_bounds_original,
)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_V5_CHECKPOINT = (
    PROJECT_ROOT
    / "runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/weights/best_it.pt"
)
V5_CONFIG_PATH = PROJECT_ROOT / "datasets/yolo_pose_new_26/v5_phase2_training_config.yaml"

IT_LANDMARK_NAMES: Tuple[str, str] = ("IT_R", "IT_L")
IT_KP_INDICES: Tuple[int, int] = (14, 15)

_TRAIN_SCRIPT = PROJECT_ROOT / "annotation_pilot/scripts/train_yolo_pose_v5_phase2.py"
_spec = importlib.util.spec_from_file_location("v5p2_train", _TRAIN_SCRIPT)
_p2 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.path.insert(0, str(PROJECT_ROOT))
_spec.loader.exec_module(_p2)


@dataclass(frozen=True)
class ITDetectedLandmark:
    """Landmark IT (index 14/15) avec visibilité explicite."""

    name: str
    v: int
    x: Optional[float] = None
    y: Optional[float] = None
    confidence: Optional[float] = None
    kp_index: int = 14


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_v = math.exp(value)
    return exp_v / (1.0 + exp_v)


def decode_keypoints_px640(
    base: Any,
    anchor_points: torch.Tensor,
    pred_kpts: torch.Tensor,
    stride_tensor: torch.Tensor,
    anchor_idx: int,
    kpt_shape: Tuple[int, ...],
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Decode 16 KP : retourne (grid, px640) pour l'anchor donné — une seule × stride."""
    bs = pred_kpts.shape[0]
    pred_dec = base.kpts_decode(
        anchor_points, pred_kpts.view(bs, -1, *kpt_shape)
    )
    pred_grid = pred_dec[0, anchor_idx].clone()
    pred_px = pred_dec.clone()
    pred_px[..., :2] *= stride_tensor.view(1, -1, 1, 1)
    pred_px640 = pred_px[0, anchor_idx]
    return pred_grid, pred_px640


def verify_single_stride(
    raw_x: float,
    raw_y: float,
    stride: float,
    px_x: float,
    px_y: float,
    *,
    tol: float = 0.05,
) -> bool:
    """Vérifie qu'une seule multiplication stride a été appliquée."""
    return abs(px_x - raw_x * stride) <= tol and abs(px_y - raw_y * stride) <= tol


def _box_iou(
    a: Tuple[float, float, float, float],
    b: Tuple[float, float, float, float],
) -> float:
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if inter <= 0:
        return 0.0
    aa = (a[2] - a[0]) * (a[3] - a[1])
    bb = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (aa + bb - inter + 1e-9)


def select_anchor_by_yolo_bbox(
    base: Any,
    preds: dict[str, torch.Tensor],
    yolo_bbox: DetectionBoundingBox,
) -> Tuple[int, float, torch.Tensor, torch.Tensor]:
    """Sélectionne l'anchor V5 avec max IoU sur la bbox YOLO (production, sans GT)."""
    from ultralytics.utils.tal import make_anchors

    pred_distri = preds["boxes"].permute(0, 2, 1).contiguous()
    anchor_points, stride_tensor = make_anchors(preds["feats"], base.stride, 0.5)
    pred_bboxes_px = base.bbox_decode(anchor_points, pred_distri) * stride_tensor

    target = (yolo_bbox.x1, yolo_bbox.y1, yolo_bbox.x2, yolo_bbox.y2)
    best_idx, best_iou = 0, -1.0
    for ai in range(pred_bboxes_px.shape[1]):
        pb = pred_bboxes_px[0, ai]
        box = (float(pb[0]), float(pb[1]), float(pb[2]), float(pb[3]))
        iou_v = _box_iou(box, target)
        if iou_v > best_iou:
            best_idx, best_iou = ai, iou_v
    return best_idx, best_iou, anchor_points, stride_tensor


def _parse_it_landmarks(
    pred_px640: torch.Tensor,
    *,
    keypoint_conf_threshold: float,
) -> Tuple[ITDetectedLandmark, ...]:
    """Extrait IT_R / IT_L — v=0 si confiance insuffisante (pas de coordonnées inventées)."""
    results: list[ITDetectedLandmark] = []
    for name, ki in zip(IT_LANDMARK_NAMES, IT_KP_INDICES):
        vis_logit = float(pred_px640[ki, 2].item())
        vis_conf = _sigmoid(vis_logit)
        if vis_conf >= keypoint_conf_threshold:
            results.append(
                ITDetectedLandmark(
                    name=name,
                    v=2,
                    x=float(pred_px640[ki, 0].item()),
                    y=float(pred_px640[ki, 1].item()),
                    confidence=vis_conf,
                    kp_index=ki,
                )
            )
        else:
            results.append(
                ITDetectedLandmark(
                    name=name,
                    v=0,
                    x=None,
                    y=None,
                    confidence=vis_conf,
                    kp_index=ki,
                )
            )
    return tuple(results)


class V5Phase2LandmarkDetector(LandmarkDetector):
    """Détecteur V5 Phase 2 — 14 KP via YOLO V2 + IT via V5 ``forward_head_preds``."""

    def __init__(
        self,
        checkpoint_path: str | Path | None = None,
        config_path: str | Path | None = None,
        *,
        keypoint_conf_threshold: float = 0.25,
        bbox_confidence_threshold: float = 0.25,
        refinement_enabled: bool | None = None,
        device: str = "cpu",
        load_on_init: bool = False,
        v2_detector: YoloPoseLandmarkDetector | None = None,
    ) -> None:
        self._checkpoint_path = Path(checkpoint_path) if checkpoint_path else DEFAULT_V5_CHECKPOINT
        if not self._checkpoint_path.is_absolute():
            self._checkpoint_path = PROJECT_ROOT / self._checkpoint_path
        self._config_path = Path(config_path) if config_path else V5_CONFIG_PATH
        self._keypoint_conf_threshold = keypoint_conf_threshold
        self._bbox_confidence_threshold = bbox_confidence_threshold
        self._refinement_enabled = refinement_enabled
        self._device = torch.device(device)
        self._model: Any | None = None
        self._cfg: dict[str, Any] | None = None
        self._v2 = v2_detector or YoloPoseLandmarkDetector(
            keypoint_conf_threshold=keypoint_conf_threshold,
            bbox_confidence_threshold=bbox_confidence_threshold,
            refinement_enabled=refinement_enabled,
        )
        if load_on_init:
            self._ensure_model()

    @property
    def name(self) -> str:
        return "yolo_pose_v5_phase2"

    @property
    def model_version(self) -> str:
        return "v5_phase2"

    @property
    def checkpoint_path(self) -> Path:
        return self._checkpoint_path

    @property
    def model_loaded(self) -> bool:
        return self._model is not None

    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        if not self._checkpoint_path.is_file():
            raise ModelNotFoundError(
                f"Checkpoint V5 Phase 2 introuvable : {self._checkpoint_path}."
            )
        if not self._config_path.is_file():
            raise ModelNotFoundError(
                f"Config V5 Phase 2 introuvable : {self._config_path}."
            )
        cfg = yaml.safe_load(self._config_path.read_text(encoding="utf-8"))
        ckpt = torch.load(self._checkpoint_path, map_location="cpu", weights_only=False)
        model = _p2.build_model(cfg)
        model.load_state_dict(ckpt["v5_phase2"]["wrapper_state"])
        _p2.attach_hyp(model.base)
        model.eval()
        model.to(self._device)
        self._model = model
        self._cfg = cfg

    def _validate_image(self, image: PreprocessedImage) -> None:
        if image.status != "ok":
            raise InvalidImageError(f"Image prétraitée invalide (status={image.status!r}).")
        width, height = image.processed_size
        if width <= 0 or height <= 0:
            raise InvalidImageError(f"Dimensions invalides : {image.processed_size!r}.")
        if image.array is None or image.array.size == 0:
            raise InvalidImageError("Tableau d'image vide.")
        if width != V5_IMGSZ or height != V5_IMGSZ:
            raise InvalidImageError(
                f"V5 attend {V5_IMGSZ}×{V5_IMGSZ}, reçu {width}×{height}. "
                "Utiliser preprocess_image_v5()."
            )

    def _image_to_tensor(self, image: PreprocessedImage) -> torch.Tensor:
        chw = preprocessed_to_rgb_chw_float(image)
        return torch.from_numpy(chw).unsqueeze(0).to(self._device)

    def detect(self, image: PreprocessedImage) -> LandmarkDetectionResult:
        """14 KP via YOLO V2 + IT via V5 à l'anchor aligné sur la bbox YOLO."""
        try:
            self._validate_image(image)
            self._ensure_model()
            assert self._model is not None

            width, height = (float(image.processed_size[0]), float(image.processed_size[1]))

            # 14 KP + bbox : même logique YOLO V2 que production (sur image 640).
            v2_result = self._v2.detect(image)
            if v2_result.status != "ok":
                return LandmarkDetectionResult(
                    status=v2_result.status,
                    message=v2_result.message,
                    landmarks=v2_result.landmarks,
                    raw_landmarks=v2_result.raw_landmarks,
                    bounding_box=v2_result.bounding_box,
                    detector_name=self.name,
                    audit={
                        "model_version": "v5_phase2",
                        "v2_subdetector_failed": True,
                        **(v2_result.audit or {}),
                    },
                )

            assert v2_result.bounding_box is not None
            bbox = v2_result.bounding_box

            img_tensor = self._image_to_tensor(image)
            with torch.no_grad():
                preds, _, _ = self._model.forward_head_preds(img_tensor)

            crit = self._model.init_criterion()
            base = crit._base

            anchor_idx, anchor_iou, anchor_points, stride_tensor = select_anchor_by_yolo_bbox(
                base, preds, bbox
            )

            pred_kpts = preds["kpts"].permute(0, 2, 1).contiguous()
            kpt_shape = tuple(base.kpt_shape)
            pred_grid, pred_px640 = decode_keypoints_px640(
                base,
                anchor_points,
                pred_kpts,
                stride_tensor,
                anchor_idx,
                kpt_shape,
            )
            stride_val = float(stride_tensor.view(-1)[anchor_idx].item())
            it_landmarks = _parse_it_landmarks(
                pred_px640,
                keypoint_conf_threshold=self._keypoint_conf_threshold,
            )

            active_refinement = (
                ASL_L_REFINEMENT_ENABLED
                if self._refinement_enabled is None
                else self._refinement_enabled
            )

            it_with_coords = [item for item in it_landmarks if item.v == 2]
            decoder_ok = True
            if it_with_coords:
                sample = it_with_coords[0]
                ki = sample.kp_index
                decoder_ok = verify_single_stride(
                    float(pred_grid[ki, 0].item()),
                    float(pred_grid[ki, 1].item()),
                    stride_val,
                    float(pred_px640[ki, 0].item()),
                    float(pred_px640[ki, 1].item()),
                )

            audit: dict[str, Any] = {
                "model_version": "v5_phase2",
                "checkpoint_path": str(self._checkpoint_path),
                "selected_anchor_idx": anchor_idx,
                "anchor_selection": "max_iou_yolo_bbox",
                "anchor_iou_vs_yolo": anchor_iou,
                "anchor_stride": stride_val,
                "decoder_single_stride_ok": decoder_ok,
                "n_keypoints_total": 16,
                "refinement_enabled": active_refinement,
                "refinement_applied": (v2_result.audit or {}).get("refinement_applied", False),
                "refinement_status": (v2_result.audit or {}).get("refinement_status"),
                "detection_confidence": bbox.confidence,
                "keypoint_confidences": (v2_result.audit or {}).get("keypoint_confidences", {}),
                "it_landmarks_v": {item.name: item.v for item in it_landmarks},
            }
            if v2_result.audit:
                for key in (
                    "refinement_out_of_bounds",
                    "calibration_coordinate_space",
                    "calibration_source",
                    "letterbox_scale",
                    "original_asl_l",
                    "raw_asl_l",
                    "refined_asl_l",
                ):
                    if key in v2_result.audit:
                        audit[key] = v2_result.audit[key]

            return LandmarkDetectionResult(
                status="ok",
                message=None,
                landmarks=v2_result.landmarks,
                raw_landmarks=v2_result.raw_landmarks,
                bounding_box=bbox,
                detector_name=self.name,
                audit=audit,
                it_landmarks=it_landmarks,
            )
        except YoloPoseDetectorError as error:
            return LandmarkDetectionResult(
                status="error",
                message=str(error),
                landmarks=(),
                raw_landmarks=(),
                detector_name=self.name,
                audit={
                    "model_version": "v5_phase2",
                    "checkpoint_path": str(self._checkpoint_path),
                    "error_type": type(error).__name__,
                },
            )
        except Exception as error:
            return LandmarkDetectionResult(
                status="error",
                message=f"Erreur inattendue V5 Phase 2 : {error}",
                landmarks=(),
                raw_landmarks=(),
                detector_name=self.name,
                audit={
                    "model_version": "v5_phase2",
                    "checkpoint_path": str(self._checkpoint_path),
                    "error_type": type(error).__name__,
                },
            )
