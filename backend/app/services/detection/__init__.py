"""Interface et types du futur détecteur de landmarks."""

from .base import (
    DetectedLandmark,
    DetectionBoundingBox,
    LandmarkDetectionResult,
    LandmarkDetector,
    LandmarkFormatError,
    NotImplementedLandmarkDetector,
    get_default_detector,
    validate_detected_landmarks,
    validate_landmark_name,
)
from .model_factory import ModelVersion, get_landmark_detector, get_model_version
from .reprojection import (
    ReprojectionError,
    ReprojectedLandmark,
    reproject_landmark,
    reproject_landmarks,
    reprojection_meta_from_preprocessed,
)
from .v5_phase2_pose import (
    ITDetectedLandmark,
    V5Phase2LandmarkDetector,
    decode_keypoints_px640,
    verify_single_stride,
)
from .yolo_pose import YoloPoseLandmarkDetector

__all__ = [
    "DetectedLandmark",
    "DetectionBoundingBox",
    "LandmarkDetectionResult",
    "LandmarkDetector",
    "LandmarkFormatError",
    "NotImplementedLandmarkDetector",
    "get_default_detector",
    "get_landmark_detector",
    "get_model_version",
    "ITDetectedLandmark",
    "ModelVersion",
    "V5Phase2LandmarkDetector",
    "decode_keypoints_px640",
    "verify_single_stride",
    "ReprojectionError",
    "ReprojectedLandmark",
    "YoloPoseLandmarkDetector",
    "reproject_landmark",
    "reproject_landmarks",
    "reprojection_meta_from_preprocessed",
    "validate_detected_landmarks",
    "validate_landmark_name",
]
