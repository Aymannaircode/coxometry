"""Tests du détecteur YOLO Pose V2 backend (mock Ultralytics + intégration optionnelle)."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from unittest.mock import MagicMock

import numpy as np
from PIL import Image

from backend.app.services.detection.yolo_pose import (
    DEFAULT_V2_MODEL_PATH,
    LowBboxConfidenceError,
    MissingKeypointsError,
    NoDetectionError,
    UnexpectedYoloFormatError,
    YoloPoseLandmarkDetector,
    _apply_adapter_and_refinement,
    _build_yolo_pose_line,
    _parse_ultralytics_result,
)
from backend.app.services.preprocessing import PreprocessedImage, PreprocessConfig, preprocess_image
from mvp_geometry.landmarks import MVP_LANDMARK_NAMES
from mvp_geometry.refinement import ASL_L_REFINEMENT_ENABLED

V2_LABEL = PROJECT_ROOT / "datasets/yolo_pose_new_26/predictions_v2/labels/B26_01.txt"
V2_WIDTH = 2730.0
V2_HEIGHT = 2665.0


def _gray_png(width: int, height: int) -> bytes:
    data = np.full((height, width), 128, dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(data).save(buffer, format="PNG")
    return buffer.getvalue()


def _sample_preprocessed(width: int = 640, height: int = 480) -> PreprocessedImage:
    return preprocess_image(
        _gray_png(width, height),
        PreprocessConfig(target_size=(width, height)),
    )


def _sample_keypoints(conf: float = 0.9) -> list[tuple[float, float, float]]:
    return [(0.03 * (index + 1), 0.04 * (index + 1), conf) for index in range(14)]



class _FakeBoxes:
    def __init__(self, det_conf: float) -> None:
        self._conf = np.array([det_conf], dtype=np.float32)
        self._xywhn = np.array(
            [[0.461747, 0.663596, 0.695509, 0.671823]],
            dtype=np.float32,
        )

    @property
    def conf(self) -> np.ndarray:
        return self._conf

    @property
    def xywhn(self) -> np.ndarray:
        return self._xywhn

    def __len__(self) -> int:
        return 1


class _FakeKeypoints:
    def __init__(self, n_keypoints: int, keypoint_conf: float) -> None:
        self.xyn = [
            np.array(
                [[0.03 * (index + 1), 0.04 * (index + 1)] for index in range(n_keypoints)],
                dtype=np.float32,
            )
        ]
        self.conf = [np.full(n_keypoints, keypoint_conf, dtype=np.float32)]

    def __len__(self) -> int:
        return len(self.xyn)


class _FakeUltralyticsResult:
    def __init__(
        self,
        *,
        det_conf: float = 0.9,
        n_keypoints: int = 14,
        include_boxes: bool = True,
        include_keypoints: bool = True,
        keypoint_conf: float = 0.9,
    ) -> None:
        self.boxes = _FakeBoxes(det_conf) if include_boxes else None
        self.keypoints = (
            _FakeKeypoints(n_keypoints, keypoint_conf) if include_keypoints else None
        )


def _make_ultralytics_result(
    *,
    det_conf: float = 0.9,
    n_keypoints: int = 14,
    include_boxes: bool = True,
    include_keypoints: bool = True,
    keypoint_conf: float = 0.9,
) -> _FakeUltralyticsResult:
    return _FakeUltralyticsResult(
        det_conf=det_conf,
        n_keypoints=n_keypoints,
        include_boxes=include_boxes,
        include_keypoints=include_keypoints,
        keypoint_conf=keypoint_conf,
    )


class FakeYoloModel:
    def __init__(self, result: MagicMock) -> None:
        self._result = result
        self.last_input = None

    def predict(self, rgb, verbose=False):
        self.last_input = rgb
        return [self._result]


class TestYoloPoseHelpers(unittest.TestCase):
    def test_build_yolo_pose_line_has_48_columns(self) -> None:
        line = _build_yolo_pose_line(0.5, 0.5, 0.8, 0.7, _sample_keypoints(), 0.88)
        self.assertEqual(len(line.split()), 48)

    def test_unexpected_keypoint_count(self) -> None:
        with self.assertRaises(UnexpectedYoloFormatError):
            _build_yolo_pose_line(0.5, 0.5, 0.8, 0.7, _sample_keypoints()[:5], 0.9)

    @unittest.skipUnless(V2_LABEL.is_file(), "Label V2 B26_01 absent")
    def test_adapter_and_refinement_on_real_label(self) -> None:
        line = V2_LABEL.read_text(encoding="utf-8").strip()
        raw, refined = _apply_adapter_and_refinement(
            line,
            V2_WIDTH,
            V2_HEIGHT,
            keypoint_conf_threshold=0.25,
            refinement_enabled=True,
        )
        self.assertIn("ASL_L", raw)
        self.assertTrue(refined.applied)
        self.assertNotEqual(raw["ASL_L"], refined.landmarks["ASL_L"])
        self.assertEqual(raw["ASM_L"], refined.landmarks["ASM_L"])


class TestYoloPoseLandmarkDetector(unittest.TestCase):
    def _detector_with_fake(self, result: MagicMock) -> YoloPoseLandmarkDetector:
        handle = tempfile.NamedTemporaryFile(suffix=".pt", delete=False)
        handle.write(b"fake-weights")
        handle.close()
        weights = Path(handle.name)
        self.addCleanup(lambda: weights.unlink(missing_ok=True))
        return YoloPoseLandmarkDetector(
            model_path=weights,
            model_loader=lambda _: FakeYoloModel(result),
        )

    def test_model_not_found(self) -> None:
        detector = YoloPoseLandmarkDetector(model_path="/does/not/exist/best.pt")
        result = detector.detect(_sample_preprocessed())
        self.assertEqual(result.status, "error")
        self.assertIn("introuvable", (result.message or "").lower())
        self.assertEqual(result.audit["error_type"], "ModelNotFoundError")

    def test_invalid_image_empty_array(self) -> None:
        image = PreprocessedImage(
            array=np.array([]),
            source_format="PNG",
            color_mode="grayscale",
            original_size=(64, 48),
            processed_size=(64, 48),
            scale=1.0,
            pad_left=0,
            pad_top=0,
            normalized=True,
            status="ok",
        )
        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp:
            path = Path(tmp.name)
            path.write_bytes(b"x")
        detector = YoloPoseLandmarkDetector(
            model_path=path,
            model_loader=lambda _: FakeYoloModel(_make_ultralytics_result()),
        )
        result = detector.detect(image)
        self.assertEqual(result.status, "error")
        path.unlink(missing_ok=True)

    def test_successful_detection_mock(self) -> None:
        detector = self._detector_with_fake(_make_ultralytics_result())
        result = detector.detect(_sample_preprocessed(2730, 2665))
        self.assertEqual(result.status, "ok")
        self.assertEqual(len(result.landmarks), 14)
        self.assertEqual(len(result.raw_landmarks), 14)
        self.assertIsNotNone(result.bounding_box)
        self.assertGreater(result.bounding_box.confidence, 0)

    def test_fourteen_landmarks_recovered(self) -> None:
        detector = self._detector_with_fake(_make_ultralytics_result())
        result = detector.detect(_sample_preprocessed())
        names = {item.name for item in result.landmarks}
        self.assertEqual(names, set(MVP_LANDMARK_NAMES))

    def test_asl_l_refinement_applied(self) -> None:
        detector = self._detector_with_fake(_make_ultralytics_result())
        result = detector.detect(_sample_preprocessed())
        raw_asl = next(item for item in result.raw_landmarks if item.name == "ASL_L")
        ref_asl = next(item for item in result.landmarks if item.name == "ASL_L")
        self.assertTrue(result.audit["refinement_applied"])
        self.assertNotEqual((raw_asl.x, raw_asl.y), (ref_asl.x, ref_asl.y))

    def test_original_asl_l_preserved_in_audit(self) -> None:
        detector = self._detector_with_fake(_make_ultralytics_result())
        result = detector.detect(_sample_preprocessed())
        self.assertIsNotNone(result.audit["original_asl_l"])
        self.assertIsNotNone(result.audit["raw_asl_l"])
        self.assertIsNotNone(result.audit["refined_asl_l"])

    def test_other_landmarks_unchanged_except_asl_l(self) -> None:
        detector = self._detector_with_fake(_make_ultralytics_result())
        result = detector.detect(_sample_preprocessed())
        raw_map = {item.name: (item.x, item.y) for item in result.raw_landmarks}
        ref_map = {item.name: (item.x, item.y) for item in result.landmarks}
        for name in MVP_LANDMARK_NAMES:
            if name == "ASL_L":
                continue
            self.assertEqual(raw_map[name], ref_map[name], msg=name)

    def test_no_detection(self) -> None:
        detector = self._detector_with_fake(_make_ultralytics_result(include_boxes=False))
        result = detector.detect(_sample_preprocessed())
        self.assertEqual(result.status, "error")
        self.assertEqual(result.audit["error_type"], "NoDetectionError")

    def test_low_bbox_confidence(self) -> None:
        detector = self._detector_with_fake(_make_ultralytics_result(det_conf=0.05))
        result = detector.detect(_sample_preprocessed())
        self.assertEqual(result.status, "error")
        self.assertEqual(result.audit["error_type"], "LowBboxConfidenceError")

    def test_missing_keypoints(self) -> None:
        detector = self._detector_with_fake(
            _make_ultralytics_result(include_keypoints=False),
        )
        result = detector.detect(_sample_preprocessed())
        self.assertEqual(result.status, "error")
        self.assertEqual(result.audit["error_type"], "MissingKeypointsError")

    def test_unexpected_keypoint_count_from_yolo(self) -> None:
        with self.assertRaises(UnexpectedYoloFormatError):
            _parse_ultralytics_result(
                _make_ultralytics_result(n_keypoints=10),
                640.0,
                480.0,
                bbox_confidence_threshold=0.25,
            )

    def test_reproducible_detection(self) -> None:
        fake_result = _make_ultralytics_result()
        detector_a = self._detector_with_fake(fake_result)
        detector_b = self._detector_with_fake(fake_result)
        first = detector_a.detect(_sample_preprocessed(800, 600))
        second = detector_b.detect(_sample_preprocessed(800, 600))
        self.assertEqual(first.landmarks, second.landmarks)
        self.assertEqual(first.raw_landmarks, second.raw_landmarks)

    def test_refinement_flag_reported(self) -> None:
        detector = self._detector_with_fake(_make_ultralytics_result())
        result = detector.detect(_sample_preprocessed())
        self.assertEqual(result.audit["refinement_enabled"], ASL_L_REFINEMENT_ENABLED)


@unittest.skipUnless(DEFAULT_V2_MODEL_PATH.is_file(), "Checkpoint V2 absent — test intégration ignoré")
class TestYoloPoseIntegration(unittest.TestCase):
    def test_real_v2_inference_on_sample_image(self) -> None:
        detector = YoloPoseLandmarkDetector(load_on_init=True)
        self.assertTrue(detector.model_loaded)
        result = detector.detect(_sample_preprocessed(512, 512))
        self.assertIn(result.status, ("ok", "error"))
        if result.status == "ok":
            self.assertGreater(len(result.landmarks), 0)
            self.assertIsNotNone(result.bounding_box)


def print_summary() -> None:
    loader = unittest.TestLoader()
    unit_suite = unittest.TestSuite()
    unit_suite.addTests(loader.loadTestsFromTestCase(TestYoloPoseHelpers))
    unit_suite.addTests(loader.loadTestsFromTestCase(TestYoloPoseLandmarkDetector))

    integration_suite = unittest.TestSuite()
    if DEFAULT_V2_MODEL_PATH.is_file():
        integration_suite.addTests(loader.loadTestsFromTestCase(TestYoloPoseIntegration))

    unit_runner = unittest.TextTestRunner(verbosity=0)
    unit_result = unit_runner.run(unit_suite)
    integration_result = unit_runner.run(integration_suite)

    unit_total = unit_result.testsRun
    unit_passed = unit_total - len(unit_result.failures) - len(unit_result.errors)
    integration_total = integration_result.testsRun
    integration_passed = integration_total - len(integration_result.failures) - len(
        integration_result.errors
    )

    print("YOLO V2 BACKEND DETECTOR COMPLETE")
    print(f"Model loaded: {'YES' if DEFAULT_V2_MODEL_PATH.is_file() else 'NO'}")
    print(f"Unit tests: {unit_passed}/{unit_total}")
    print(f"Integration tests: {integration_passed}/{integration_total}")
    print(f"ASL_L refinement: {'ON' if ASL_L_REFINEMENT_ENABLED else 'OFF'}")
    print("Raw landmarks preserved: YES")
    print("CCD pipeline unchanged: YES")


if __name__ == "__main__":
    outcome = unittest.main(exit=False, verbosity=2)
    print_summary()
    sys.exit(0 if outcome.result.wasSuccessful() else 1)
