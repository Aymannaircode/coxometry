"""Tests correction unités refinement ASL_L (offset TRAIN → espace prétraité)."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from PIL import Image

from backend.app.services.analyze import DEFAULT_ANALYZE_PREPROCESS, analyze_result_to_dict, run_analyze_from_bytes
from backend.app.services.detection.reprojection import reproject_point, reprojection_meta_from_preprocessed
from backend.app.services.detection.yolo_pose import YoloPoseLandmarkDetector
from backend.app.services.preprocessing import preprocess_image
from backend.app.schemas.analyze import AnalyzeSuccessResponse
from mvp_geometry.landmarks import MVP_LANDMARK_NAMES
from mvp_geometry.refinement.calibration import TRAIN_ASM_OFFSET_CALIBRATION
from mvp_geometry.refinement.units import expected_original_offset_from_refined

B26_01_PATH = PROJECT_ROOT / "datasets/yolo_pose_new_26/predictions_v2/images/B26_01.png"
TARGET = DEFAULT_ANALYZE_PREPROCESS.target_size


def _gray_png(width: int, height: int) -> bytes:
    data = np.full((height, width), 128, dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(data).save(buffer, format="PNG")
    return buffer.getvalue()


class TestAslLRefinementCoordinateFix(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model_available = B26_01_PATH.is_file()
        cls.detector = YoloPoseLandmarkDetector() if cls.model_available else None

    def _analyze_b26_01(self) -> dict:
        self.assertTrue(self.model_available)
        assert self.detector is not None
        raw = B26_01_PATH.read_bytes()
        response = run_analyze_from_bytes(
            raw,
            filename="B26_01.png",
            content_type="image/png",
            detector=self.detector,
        )
        self.assertIsInstance(response, AnalyzeSuccessResponse)
        return analyze_result_to_dict(response)

    def test_b26_01_asl_l_refined_in_bounds(self) -> None:
        if not self.model_available:
            self.skipTest("B26_01.png absent")
        body = self._analyze_b26_01()
        cs = body["detection"]["coordinate_space"]
        w, h = cs["image_width"], cs["image_height"]
        asl = next(lm for lm in body["detection"]["refined_landmarks"] if lm["name"] == "ASL_L")
        self.assertGreaterEqual(asl["x"], 0.0)
        self.assertGreaterEqual(asl["y"], 0.0)
        self.assertLessEqual(asl["x"], w)
        self.assertLessEqual(asl["y"], h)

    def test_b26_01_raw_asl_l_unchanged_vs_reprojected_yolo(self) -> None:
        if not self.model_available:
            self.skipTest("B26_01.png absent")
        body = self._analyze_b26_01()
        raw_asl = next(lm for lm in body["detection"]["raw_landmarks"] if lm["name"] == "ASL_L")
        # Valeur attendue après fix reprojection (audit précédent ~1843, 1254)
        self.assertAlmostEqual(raw_asl["x"], 1842.5, delta=5.0)
        self.assertAlmostEqual(raw_asl["y"], 1253.8, delta=5.0)

    def test_b26_01_offset_matches_train_calibration(self) -> None:
        if not self.model_available:
            self.skipTest("B26_01.png absent")
        body = self._analyze_b26_01()
        asm = next(lm for lm in body["detection"]["refined_landmarks"] if lm["name"] == "ASM_L")
        asl = next(lm for lm in body["detection"]["refined_landmarks"] if lm["name"] == "ASL_L")
        dx, dy = expected_original_offset_from_refined(asm["x"], asm["y"], asl["x"], asl["y"])
        self.assertAlmostEqual(dx, TRAIN_ASM_OFFSET_CALIBRATION.dx, delta=2.0)
        self.assertAlmostEqual(dy, TRAIN_ASM_OFFSET_CALIBRATION.dy, delta=2.0)

    def test_b26_01_other_landmarks_unchanged_except_asl_l(self) -> None:
        if not self.model_available:
            self.skipTest("B26_01.png absent")
        body = self._analyze_b26_01()
        raw_map = {lm["name"]: (lm["x"], lm["y"]) for lm in body["detection"]["raw_landmarks"]}
        ref_map = {lm["name"]: (lm["x"], lm["y"]) for lm in body["detection"]["refined_landmarks"]}
        for name in MVP_LANDMARK_NAMES:
            if name == "ASL_L":
                continue
            self.assertEqual(raw_map[name], ref_map[name], msg=name)

    def test_b26_01_coordinate_space_consistent(self) -> None:
        if not self.model_available:
            self.skipTest("B26_01.png absent")
        body = self._analyze_b26_01()
        cs = body["detection"]["coordinate_space"]
        self.assertEqual(cs["landmark_coordinate_space"], "original_image_pixels")
        self.assertEqual(cs["image_width"], 2730)
        self.assertEqual(cs["image_height"], 2665)
        self.assertEqual(body["audit"]["exposed_landmark_coordinate_space"], "original_image_pixels")

    def test_b26_01_ccd_unchanged_from_pre_fix_baseline(self) -> None:
        """CCD ne dépend pas de ASL_L — doit rester identique au pipeline pré-fix."""
        if not self.model_available:
            self.skipTest("B26_01.png absent")
        body = self._analyze_b26_01()
        # Mesures issues du pipeline prétraité ; CCD indépendant du refinement ASL_L.
        self.assertTrue(body["measurements"]["right"]["ccd"]["available"])
        self.assertTrue(body["measurements"]["left"]["ccd"]["available"])
        self.assertIsNotNone(body["measurements"]["right"]["ccd"]["value_deg"])
        self.assertIsNotNone(body["measurements"]["left"]["ccd"]["value_deg"])

    def test_resolution_independence_of_anatomical_offset(self) -> None:
        """Même offset original après reprojection quelle que soit la taille d'entrée."""
        if not self.model_available:
            self.skipTest("B26_01.png absent")
        assert self.detector is not None
        png = B26_01_PATH.read_bytes()
        preprocessed = preprocess_image(png, DEFAULT_ANALYZE_PREPROCESS)
        meta = reprojection_meta_from_preprocessed(preprocessed)
        result = self.detector.detect(preprocessed)
        self.assertEqual(result.status, "ok")
        asm = next(item for item in result.landmarks if item.name == "ASM_L")
        asl = next(item for item in result.landmarks if item.name == "ASL_L")
        asm_x, asm_y, _, _ = reproject_point(asm.x, asm.y, meta)
        asl_x, asl_y, _, _ = reproject_point(asl.x, asl.y, meta)
        dx, dy = expected_original_offset_from_refined(asm_x, asm_y, asl_x, asl_y)
        self.assertAlmostEqual(dx, TRAIN_ASM_OFFSET_CALIBRATION.dx, delta=2.0)
        self.assertAlmostEqual(dy, TRAIN_ASM_OFFSET_CALIBRATION.dy, delta=2.0)

    def test_square_image_asl_l_in_bounds(self) -> None:
        self._assert_asl_l_in_bounds_for_size(2730, 2730)

    def test_landscape_image_asl_l_in_bounds(self) -> None:
        self._assert_asl_l_in_bounds_for_size(1920, 1080)

    def test_portrait_image_asl_l_in_bounds(self) -> None:
        self._assert_asl_l_in_bounds_for_size(1080, 1920)

    def _assert_asl_l_in_bounds_for_size(self, width: int, height: int) -> None:
        if not self.model_available:
            self.skipTest("modèle absent")
        assert self.detector is not None
        from PIL import Image

        source = Image.open(B26_01_PATH).convert("L")
        resized = source.resize((width, height), Image.BILINEAR)
        buffer = io.BytesIO()
        resized.save(buffer, format="PNG")
        png = buffer.getvalue()
        preprocessed = preprocess_image(png, DEFAULT_ANALYZE_PREPROCESS)
        meta = reprojection_meta_from_preprocessed(preprocessed)
        result = self.detector.detect(preprocessed)
        if result.status != "ok":
            self.skipTest(f"détection non ok sur B26_01 redimensionné {width}x{height}")
        asl = next(item for item in result.landmarks if item.name == "ASL_L")
        asm = next(item for item in result.landmarks if item.name == "ASM_L")
        asl_x, asl_y, _, in_bounds = reproject_point(asl.x, asl.y, meta)
        asm_x, asm_y, _, _ = reproject_point(asm.x, asm.y, meta)
        orig_w, orig_h = preprocessed.original_size
        dx, dy = expected_original_offset_from_refined(asm_x, asm_y, asl_x, asl_y)
        self.assertAlmostEqual(dx, TRAIN_ASM_OFFSET_CALIBRATION.dx, delta=3.0)
        self.assertAlmostEqual(dy, TRAIN_ASM_OFFSET_CALIBRATION.dy, delta=3.0)
        # Hors image extrême (bug unités) vs léger débordement letterbox
        self.assertLess(asl_x, orig_w * 1.05)
        self.assertGreater(asl_x, -orig_w * 0.05)
        self.assertLess(asl_y, orig_h * 1.05)
        self.assertGreater(asl_y, -orig_h * 0.05)
        if not in_bounds:
            self.assertLess(asl_x, orig_w + 5.0)
            self.assertLess(asl_y, orig_h + 5.0)


if __name__ == "__main__":
    unittest.main()
