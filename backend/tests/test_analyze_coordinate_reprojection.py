"""Tests reprojection landmarks API /analyze → espace image originale."""

from __future__ import annotations

import io
import math
import sys
import unittest
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from PIL import Image

from backend.app.services.analyze import DEFAULT_ANALYZE_PREPROCESS, run_analyze_from_bytes
from backend.app.services.detection.base import (
    DetectedLandmark,
    DetectionBoundingBox,
    LandmarkDetectionResult,
    LandmarkDetector,
)
from backend.app.services.detection.reprojection import reproject_point
from backend.app.services.measurement_service import ORIGINAL_IMAGE_COORDINATE_SPACE, run_measurement_pipeline
from backend.app.services.preprocessing import PreprocessConfig, preprocess_image
from mvp_geometry.landmarks import MVP_LANDMARK_NAMES

TARGET = DEFAULT_ANALYZE_PREPROCESS.target_size
assert TARGET is not None


def _gray_png(width: int, height: int) -> bytes:
    data = np.full((height, width), 128, dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(data).save(buffer, format="PNG")
    return buffer.getvalue()


def _prep_point_for_original(
    ox: float,
    oy: float,
    *,
    original_size: tuple[int, int],
    scale: float,
    pad_left: int,
    pad_top: int,
) -> tuple[float, float]:
    """Forward letterbox : original → prétraité (inverse de reproject_point)."""
    x_prep = ox * scale + pad_left
    y_prep = oy * scale + pad_top
    _ = original_size
    return x_prep, y_prep


class FixedPointDetector(LandmarkDetector):
    """Retourne un ensemble fixe de landmarks en espace prétraité."""

    def __init__(self, landmarks: Sequence[DetectedLandmark]) -> None:
        self._landmarks = tuple(landmarks)

    @property
    def name(self) -> str:
        return "fixed_point_detector"

    def detect(self, image) -> LandmarkDetectionResult:
        _ = image
        return LandmarkDetectionResult(
            status="ok",
            landmarks=self._landmarks,
            raw_landmarks=self._landmarks,
            bounding_box=DetectionBoundingBox(x1=0.0, y1=0.0, x2=10.0, y2=10.0, confidence=0.99),
            detector_name=self.name,
            audit={
                "refinement_enabled": False,
                "refinement_applied": False,
                "keypoint_confidences": {item.name: item.confidence or 1.0 for item in self._landmarks},
            },
        )


class RefinementSplitDetector(LandmarkDetector):
    """Raw et refined divergent uniquement sur ASL_L (espace prétraité)."""

    def __init__(self, raw: Sequence[DetectedLandmark], refined: Sequence[DetectedLandmark]) -> None:
        self._raw = tuple(raw)
        self._refined = tuple(refined)

    @property
    def name(self) -> str:
        return "refinement_split_detector"

    def detect(self, image) -> LandmarkDetectionResult:
        _ = image
        return LandmarkDetectionResult(
            status="ok",
            landmarks=self._refined,
            raw_landmarks=self._raw,
            bounding_box=DetectionBoundingBox(x1=0.0, y1=0.0, x2=10.0, y2=10.0, confidence=0.99),
            detector_name=self.name,
            audit={
                "refinement_enabled": True,
                "refinement_applied": True,
                "keypoint_confidences": {item.name: 0.9 for item in self._raw},
            },
        )


def _landmarks_at_original_points(
    points: dict[str, tuple[float, float]],
    preprocessed,
) -> list[DetectedLandmark]:
    out: list[DetectedLandmark] = []
    for name in MVP_LANDMARK_NAMES:
        ox, oy = points[name]
        px, py = _prep_point_for_original(
            ox,
            oy,
            original_size=preprocessed.original_size,
            scale=preprocessed.scale,
            pad_left=preprocessed.pad_left,
            pad_top=preprocessed.pad_top,
        )
        out.append(DetectedLandmark(name=name, x=px, y=py, confidence=0.9))
    return out


def _default_original_points(width: int, height: int) -> dict[str, tuple[float, float]]:
    """14 points distincts dans l'image originale (géométrie factice)."""
    return {
        "TD_R": (width * 0.35, height * 0.75),
        "TD_L": (width * 0.65, height * 0.75),
        "FHC_R": (width * 0.28, height * 0.50),
        "FHC_L": (width * 0.72, height * 0.50),
        "ASL_R": (width * 0.20, height * 0.32),
        "ASL_L": (width * 0.80, height * 0.32),
        "ASM_R": (width * 0.33, height * 0.42),
        "ASM_L": (width * 0.67, height * 0.42),
        "FNM_R": (width * 0.22, height * 0.58),
        "FNM_L": (width * 0.78, height * 0.58),
        "FSP_R": (width * 0.18, height * 0.78),
        "FSP_L": (width * 0.82, height * 0.78),
        "FSD_R": (width * 0.15, height * 0.92),
        "FSD_L": (width * 0.85, height * 0.92),
    }


class TestCoordinateReprojection(unittest.TestCase):
    def _run_pipeline(self, width: int, height: int, detector: LandmarkDetector):
        png = _gray_png(width, height)
        preprocessed = preprocess_image(png, DEFAULT_ANALYZE_PREPROCESS)
        return run_measurement_pipeline(preprocessed, detector=detector), preprocessed, png

    def test_b26_01_size_metadata(self) -> None:
        width, height = 2730, 2665
        points = _default_original_points(width, height)
        preprocessed = preprocess_image(_gray_png(width, height), DEFAULT_ANALYZE_PREPROCESS)
        landmarks = _landmarks_at_original_points(points, preprocessed)
        result, _, _ = self._run_pipeline(width, height, FixedPointDetector(landmarks))
        assert result.detection is not None
        cs = result.detection.coordinate_space
        self.assertEqual(cs.image_width, width)
        self.assertEqual(cs.image_height, height)
        self.assertEqual(cs.preprocessed_width, TARGET[0])
        self.assertEqual(cs.preprocessed_height, TARGET[1])
        self.assertEqual(cs.landmark_coordinate_space, ORIGINAL_IMAGE_COORDINATE_SPACE)
        self.assertGreater(cs.scale, 0)
        self.assertGreaterEqual(cs.pad_x, 0)
        self.assertGreaterEqual(cs.pad_y, 0)

    def test_known_point_2730x2665(self) -> None:
        width, height = 2730, 2665
        known = {"TD_R": (928.9, 1889.73)}
        points = _default_original_points(width, height)
        points.update(known)
        preprocessed = preprocess_image(_gray_png(width, height), DEFAULT_ANALYZE_PREPROCESS)
        landmarks = _landmarks_at_original_points(points, preprocessed)
        result, _, _ = self._run_pipeline(width, height, FixedPointDetector(landmarks))
        assert result.detection is not None
        td = next(item for item in result.detection.refined_landmarks if item["name"] == "TD_R")
        self.assertAlmostEqual(td["x"], known["TD_R"][0], places=1)
        self.assertAlmostEqual(td["y"], known["TD_R"][1], places=1)

    def test_square_image(self) -> None:
        self._assert_all_landmarks_reprojected(512, 512)

    def test_landscape_image(self) -> None:
        self._assert_all_landmarks_reprojected(1920, 1080)

    def test_portrait_image(self) -> None:
        self._assert_all_landmarks_reprojected(1080, 1920)

    def _assert_all_landmarks_reprojected(self, width: int, height: int) -> None:
        points = _default_original_points(width, height)
        preprocessed = preprocess_image(_gray_png(width, height), DEFAULT_ANALYZE_PREPROCESS)
        meta_scale = preprocessed.scale
        meta_pad = (preprocessed.pad_left, preprocessed.pad_top)
        landmarks = _landmarks_at_original_points(points, preprocessed)
        result, _, _ = self._run_pipeline(width, height, FixedPointDetector(landmarks))
        assert result.detection is not None
        for name in MVP_LANDMARK_NAMES:
            expected = points[name]
            item = next(lm for lm in result.detection.refined_landmarks if lm["name"] == name)
            self.assertAlmostEqual(item["x"], expected[0], places=1, msg=f"{name} x @ {width}x{height}")
            self.assertAlmostEqual(item["y"], expected[1], places=1, msg=f"{name} y @ {width}x{height}")
        # Round-trip géométrique explicite sur le premier point
        px, py = landmarks[0].x, landmarks[0].y
        ox, oy, in_content, in_bounds = reproject_point(
            px,
            py,
            __import__(
                "backend.app.services.detection.reprojection",
                fromlist=["reprojection_meta_from_preprocessed"],
            ).reprojection_meta_from_preprocessed(preprocessed),
        )
        self.assertTrue(in_content)
        self.assertTrue(in_bounds)
        self.assertAlmostEqual(ox, points[MVP_LANDMARK_NAMES[0]][0], places=1)
        self.assertAlmostEqual(oy, points[MVP_LANDMARK_NAMES[0]][1], places=1)
        _ = meta_scale, meta_pad

    def test_raw_refined_both_reprojected_consistently(self) -> None:
        width, height = 2730, 2665
        points = _default_original_points(width, height)
        preprocessed = preprocess_image(_gray_png(width, height), DEFAULT_ANALYZE_PREPROCESS)
        raw = _landmarks_at_original_points(points, preprocessed)
        refined = list(raw)
        asl = next(item for item in raw if item.name == "ASL_L")
        refined_asl = DetectedLandmark(
            name="ASL_L",
            x=asl.x + 12.0,
            y=asl.y + 8.0,
            confidence=0.9,
        )
        refined = [refined_asl if item.name == "ASL_L" else item for item in raw]
        result, preprocessed, _ = self._run_pipeline(
            width,
            height,
            RefinementSplitDetector(raw, refined),
        )
        assert result.detection is not None
        meta = __import__(
            "backend.app.services.detection.reprojection",
            fromlist=["reprojection_meta_from_preprocessed"],
        ).reprojection_meta_from_preprocessed(preprocessed)
        raw_asl = next(item for item in result.detection.raw_landmarks if item["name"] == "ASL_L")
        ref_asl = next(item for item in result.detection.refined_landmarks if item["name"] == "ASL_L")
        self.assertNotEqual((raw_asl["x"], raw_asl["y"]), (ref_asl["x"], ref_asl["y"]))
        exp_raw_x, exp_raw_y, _, _ = reproject_point(asl.x, asl.y, meta)
        exp_ref_x, exp_ref_y, _, _ = reproject_point(refined_asl.x, refined_asl.y, meta)
        self.assertAlmostEqual(raw_asl["x"], exp_raw_x, places=1)
        self.assertAlmostEqual(raw_asl["y"], exp_raw_y, places=1)
        self.assertAlmostEqual(ref_asl["x"], exp_ref_x, places=1)
        self.assertAlmostEqual(ref_asl["y"], exp_ref_y, places=1)
        for name in MVP_LANDMARK_NAMES:
            if name == "ASL_L":
                continue
            raw_item = next(item for item in result.detection.raw_landmarks if item["name"] == name)
            ref_item = next(item for item in result.detection.refined_landmarks if item["name"] == name)
            self.assertEqual((raw_item["x"], raw_item["y"]), (ref_item["x"], ref_item["y"]), msg=name)

    def test_no_invented_coordinates(self) -> None:
        width, height = 800, 600
        points = _default_original_points(width, height)
        preprocessed = preprocess_image(_gray_png(width, height), DEFAULT_ANALYZE_PREPROCESS)
        landmarks = _landmarks_at_original_points(points, preprocessed)
        result, _, _ = self._run_pipeline(width, height, FixedPointDetector(landmarks))
        assert result.detection is not None
        raw_names = {item["name"] for item in result.detection.raw_landmarks}
        ref_names = {item["name"] for item in result.detection.refined_landmarks}
        self.assertEqual(raw_names, set(MVP_LANDMARK_NAMES))
        self.assertEqual(ref_names, set(MVP_LANDMARK_NAMES))
        for item in result.detection.raw_landmarks + result.detection.refined_landmarks:
            self.assertIsInstance(item["x"], float)
            self.assertIsInstance(item["y"], float)
            self.assertFalse(math.isnan(item["x"]))
            self.assertFalse(math.isnan(item["y"]))

    def test_measurements_use_preprocessed_space_unchanged(self) -> None:
        """Les mesures restent calculées en espace prétraité (invariance angulaire)."""
        width, height = 640, 480
        points = _default_original_points(width, height)
        preprocessed = preprocess_image(
            _gray_png(width, height),
            PreprocessConfig(target_size=(width, height)),
        )
        landmarks = _landmarks_at_original_points(points, preprocessed)
        result = run_measurement_pipeline(preprocessed, detector=FixedPointDetector(landmarks))
        self.assertEqual(result.status, "ok")
        assert result.measurements is not None
        self.assertIsNotNone(result.measurements.right.vce.value_deg)

    def test_analyze_api_coordinate_space_block(self) -> None:
        width, height = 2730, 2665
        points = _default_original_points(width, height)
        preprocessed = preprocess_image(_gray_png(width, height), DEFAULT_ANALYZE_PREPROCESS)
        landmarks = _landmarks_at_original_points(points, preprocessed)
        png = _gray_png(width, height)
        response = run_analyze_from_bytes(
            png,
            filename="B26_01.png",
            content_type="image/png",
            detector=FixedPointDetector(landmarks),
        )
        from backend.app.schemas.analyze import AnalyzeSuccessResponse

        self.assertIsInstance(response, AnalyzeSuccessResponse)
        cs = response.detection.coordinate_space
        self.assertEqual(cs.image_width, width)
        self.assertEqual(cs.image_height, height)
        self.assertEqual(cs.landmark_coordinate_space, "original_image_pixels")


class TestB26_01RealModel(unittest.TestCase):
    """Inférence réelle si le checkpoint V2 est présent."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.image_path = PROJECT_ROOT / "datasets/yolo_pose_new_26/predictions_v2/images/B26_01.png"
        cls.model_path = PROJECT_ROOT / "datasets/yolo_pose_new_26/weights/best.pt"
        cls.available = cls.image_path.is_file() and cls.model_path.is_file()

    def test_b26_01_analyze_returns_original_space_coords(self) -> None:
        if not self.available:
            self.skipTest("B26_01.png ou best.pt absent")
        from backend.app.services.detection.yolo_pose import YoloPoseLandmarkDetector

        raw_bytes = self.image_path.read_bytes()
        response = run_analyze_from_bytes(
            raw_bytes,
            filename="B26_01.png",
            content_type="image/png",
            detector=YoloPoseLandmarkDetector(model_path=self.model_path),
        )
        from backend.app.schemas.analyze import AnalyzeSuccessResponse

        self.assertIsInstance(response, AnalyzeSuccessResponse)
        cs = response.detection.coordinate_space
        self.assertEqual(cs.image_width, 2730)
        self.assertEqual(cs.image_height, 2665)
        td = next(lm for lm in response.detection.refined_landmarks if lm["name"] == "TD_R")
        # Avant fix ~184 px ; après reprojection ~980 px (ordre de grandeur GT ~929)
        self.assertGreater(td["x"], 500.0)
        self.assertGreater(td["y"], 1500.0)
        self.assertLess(td["x"], 1500.0)
        self.assertLess(td["y"], 2500.0)


if __name__ == "__main__":
    unittest.main()
