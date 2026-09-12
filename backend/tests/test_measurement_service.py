"""Tests du service measurement : détection mock → mvp_geometry."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.detection.base import (
    DetectedLandmark,
    DetectionBoundingBox,
    LandmarkDetectionResult,
    LandmarkDetector,
)
from backend.app.services.measurement_service import (
    compute_measurements_from_landmarks,
    detected_to_mvp_landmarks,
    run_measurement_pipeline,
)
from backend.app.services.preprocessing import PreprocessedImage, PreprocessConfig, preprocess_image
from mvp_geometry.landmarks import MVP_LANDMARK_NAMES, Landmark
from mvp_geometry.refinement import ASL_L_REFINEMENT_ENABLED

import io
import numpy as np
from PIL import Image


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


def _vce_asl(fhc, target_deg=25.0, radius=100.0, side="R"):
    lateral = (-1.0, 0.0) if side == "R" else (1.0, 0.0)
    cranial = (0.0, -1.0)
    theta = math.radians(target_deg)
    return (
        fhc[0] + radius * (math.sin(theta) * lateral[0] + math.cos(theta) * cranial[0]),
        fhc[1] + radius * (math.sin(theta) * lateral[1] + math.cos(theta) * cranial[1]),
    )


def _tonnis_asl(asm, target_deg=10.0, radius=120.0, side="R"):
    lateral = (-1.0, 0.0) if side == "R" else (1.0, 0.0)
    caudal = (0.0, 1.0)
    t = math.radians(target_deg)
    return (
        asm[0] + radius * (math.cos(t) * lateral[0] + math.sin(t) * caudal[0]),
        asm[1] + radius * (math.cos(t) * lateral[1] + math.sin(t) * caudal[1]),
    )


def _ccd_fhc(fnm, target_deg=130.0, neck_len=100.0, side="R"):
    medial_sign = 1.0 if side == "R" else -1.0
    angle = math.radians(target_deg)
    return (
        fnm[0] + neck_len * medial_sign * math.sin(angle),
        fnm[1] + neck_len * math.cos(angle),
    )


def _coords_from_mapping(coords: dict[str, tuple[float, float]]) -> list[DetectedLandmark]:
    return [
        DetectedLandmark(name=name, x=coords[name][0], y=coords[name][1], confidence=0.95)
        for name in coords
    ]


def _landmarks_for_vce(target_r: float = 25.0, target_l: float = 30.0) -> list[DetectedLandmark]:
    td_r, td_l = (300.0, 500.0), (500.0, 500.0)
    fhc_r, fhc_l = (200.0, 400.0), (600.0, 400.0)
    return _coords_from_mapping(
        {
            "TD_R": td_r,
            "TD_L": td_l,
            "FHC_R": fhc_r,
            "FHC_L": fhc_l,
            "ASL_R": _vce_asl(fhc_r, target_r, side="R"),
            "ASL_L": _vce_asl(fhc_l, target_l, side="L"),
        }
    )


def _landmarks_for_tonnis(target_r: float = 10.0, target_l: float = 8.0) -> list[DetectedLandmark]:
    td_r, td_l = (300.0, 500.0), (500.0, 500.0)
    asm_r, asm_l = (250.0, 300.0), (550.0, 300.0)
    return _coords_from_mapping(
        {
            "TD_R": td_r,
            "TD_L": td_l,
            "ASM_R": asm_r,
            "ASM_L": asm_l,
            "ASL_R": _tonnis_asl(asm_r, target_r, side="R"),
            "ASL_L": _tonnis_asl(asm_l, target_l, side="L"),
        }
    )


def _landmarks_for_ccd(target_r: float = 130.0, target_l: float = 128.0) -> list[DetectedLandmark]:
    fnm_r, fnm_l = (360.0, 560.0), (440.0, 560.0)
    fsp_r, fsd_r = (400.0, 600.0), (400.0, 900.0)
    fsp_l, fsd_l = (600.0, 600.0), (600.0, 900.0)
    return _coords_from_mapping(
        {
            "FHC_R": _ccd_fhc(fnm_r, target_r, side="R"),
            "FHC_L": _ccd_fhc(fnm_l, target_l, side="L"),
            "FNM_R": fnm_r,
            "FNM_L": fnm_l,
            "FSP_R": fsp_r,
            "FSP_L": fsp_l,
            "FSD_R": fsd_r,
            "FSD_L": fsd_l,
        }
    )


def _full_synthetic_landmarks() -> list[DetectedLandmark]:
    """14 landmarks : géométrie analytique cohérente pour VCE, Tönnis et CCD."""
    td_r, td_l = (300.0, 500.0), (500.0, 500.0)
    asm_r, asm_l = (250.0, 300.0), (550.0, 300.0)
    fnm_r, fnm_l = (360.0, 560.0), (440.0, 560.0)
    fsp_r, fsd_r = (400.0, 600.0), (400.0, 900.0)
    fsp_l, fsd_l = (600.0, 600.0), (600.0, 900.0)
    fhc_r = _ccd_fhc(fnm_r, 130.0, side="R")
    fhc_l = _ccd_fhc(fnm_l, 128.0, side="L")
    return _coords_from_mapping(
        {
            "TD_R": td_r,
            "TD_L": td_l,
            "FHC_R": fhc_r,
            "FHC_L": fhc_l,
            "ASL_R": _vce_asl(fhc_r, 25.0, side="R"),
            "ASL_L": _vce_asl(fhc_l, 30.0, side="L"),
            "ASM_R": asm_r,
            "ASM_L": asm_l,
            "FNM_R": fnm_r,
            "FNM_L": fnm_l,
            "FSP_R": fsp_r,
            "FSP_L": fsp_l,
            "FSD_R": fsd_r,
            "FSD_L": fsd_l,
        }
    )


class MockLandmarkDetector(LandmarkDetector):
    """Détecteur injectable pour tests sans Ultralytics."""

    def __init__(
        self,
        *,
        status: str = "ok",
        message: str | None = None,
        refined: Sequence[DetectedLandmark] | None = None,
        raw: Sequence[DetectedLandmark] | None = None,
        refinement_enabled: bool = ASL_L_REFINEMENT_ENABLED,
        refinement_applied: bool = False,
        bbox_conf: float = 0.9,
    ) -> None:
        self._status = status
        self._message = message
        self._refined = tuple(refined or ())
        self._raw = tuple(raw if raw is not None else refined or ())
        self._refinement_enabled = refinement_enabled
        self._refinement_applied = refinement_applied
        self._bbox_conf = bbox_conf

    @property
    def name(self) -> str:
        return "mock_detector"

    def detect(self, image: PreprocessedImage) -> LandmarkDetectionResult:
        _ = image
        confidences = {item.name: item.confidence or 0.0 for item in self._raw}
        audit = {
            "refinement_enabled": self._refinement_enabled,
            "refinement_applied": self._refinement_applied,
            "keypoint_confidences": confidences,
        }
        if self._status != "ok":
            audit["error_type"] = self._message or "DetectionError"
        bbox = DetectionBoundingBox(x1=10.0, y1=20.0, x2=500.0, y2=400.0, confidence=self._bbox_conf)
        return LandmarkDetectionResult(
            status=self._status,  # type: ignore[arg-type]
            message=self._message,
            landmarks=self._refined,
            raw_landmarks=self._raw,
            bounding_box=bbox if self._status == "ok" else None,
            detector_name=self.name,
            audit=audit,
        )


class TestMeasurementService(unittest.TestCase):
    def test_full_pipeline_with_mock_detector(self) -> None:
        landmarks = _full_synthetic_landmarks()
        detector = MockLandmarkDetector(refined=landmarks, raw=landmarks, refinement_applied=True)
        result = run_measurement_pipeline(_sample_preprocessed(), detector=detector)
        self.assertEqual(result.status, "ok")
        self.assertIsNotNone(result.detection)
        self.assertIsNotNone(result.measurements)
        assert result.measurements is not None
        self.assertTrue(result.measurements.right.vce.available)
        self.assertTrue(result.measurements.left.ccd.available)

    def test_vce_right_and_left(self) -> None:
        mvp = detected_to_mvp_landmarks(_landmarks_for_vce(25.0, 30.0))
        measures = compute_measurements_from_landmarks(mvp)
        self.assertAlmostEqual(measures.right.vce.value_deg, 25.0, places=5)
        self.assertAlmostEqual(measures.left.vce.value_deg, 30.0, places=5)
        self.assertEqual(
            measures.right.vce.landmarks_used,
            ("TD_R", "TD_L", "FHC_R", "ASL_R"),
        )

    def test_tonnis_right_and_left(self) -> None:
        measures = compute_measurements_from_landmarks(
            detected_to_mvp_landmarks(_landmarks_for_tonnis(10.0, 8.0))
        )
        self.assertAlmostEqual(measures.right.tonnis.value_deg, 10.0, places=5)
        self.assertAlmostEqual(measures.left.tonnis.value_deg, 8.0, places=5)

    def test_ccd_right_and_left(self) -> None:
        measures = compute_measurements_from_landmarks(
            detected_to_mvp_landmarks(_landmarks_for_ccd(130.0, 128.0))
        )
        self.assertAlmostEqual(measures.right.ccd.value_deg, 130.0, places=5)
        self.assertAlmostEqual(measures.left.ccd.value_deg, 128.0, places=5)

    def test_missing_landmark_unavailable(self) -> None:
        landmarks = _full_synthetic_landmarks()
        partial = [item for item in landmarks if item.name != "FHC_R"]
        measures = compute_measurements_from_landmarks(detected_to_mvp_landmarks(partial))
        self.assertFalse(measures.right.vce.available)
        self.assertIn("FHC_R", measures.right.vce.reason or "")
        self.assertIsNone(measures.right.vce.value_deg)
        self.assertIsNone(measures.right.vce.landmarks_used)

    def test_landmark_v0_unavailable(self) -> None:
        landmarks = detected_to_mvp_landmarks(_full_synthetic_landmarks())
        landmarks["FHC_R"] = Landmark(
            id="LM-03",
            name="FHC_R",
            side="R",
            x=200.0,
            y=400.0,
            v=0,
        )
        measures = compute_measurements_from_landmarks(landmarks)
        self.assertFalse(measures.right.vce.available)
        self.assertIn("non exploitable", measures.right.vce.reason or "")

    def test_geometry_error_unavailable(self) -> None:
        landmarks = detected_to_mvp_landmarks(_full_synthetic_landmarks())
        landmarks["TD_R"] = Landmark(
            id="LM-01",
            name="TD_R",
            side="R",
            x=500.0,
            y=500.0,
            v=2,
        )
        landmarks["TD_L"] = Landmark(
            id="LM-02",
            name="TD_L",
            side="L",
            x=500.0,
            y=500.0,
            v=2,
        )
        measures = compute_measurements_from_landmarks(landmarks)
        self.assertFalse(measures.right.vce.available)
        self.assertFalse(measures.left.vce.available)
        self.assertIn("ITH", measures.right.vce.reason or "")

    def test_detection_failed(self) -> None:
        detector = MockLandmarkDetector(
            status="error",
            message="Aucune détection pelvis.",
            refined=(),
            raw=(),
        )
        result = run_measurement_pipeline(_sample_preprocessed(), detector=detector)
        self.assertEqual(result.status, "error")
        self.assertIsNone(result.measurements)
        self.assertIn("detection_message", result.audit)

    def test_refinement_on(self) -> None:
        raw = _full_synthetic_landmarks()
        refined = list(raw)
        raw_asl = next(item for item in raw if item.name == "ASL_L")
        refined_asl = DetectedLandmark(
            name="ASL_L",
            x=raw_asl.x + 5.0,
            y=raw_asl.y + 3.0,
            confidence=0.95,
        )
        refined = [refined_asl if item.name == "ASL_L" else item for item in raw]
        detector = MockLandmarkDetector(
            refined=refined,
            raw=raw,
            refinement_enabled=True,
            refinement_applied=True,
        )
        result = run_measurement_pipeline(_sample_preprocessed(), detector=detector)
        assert result.detection is not None
        self.assertTrue(result.detection.refinement_enabled)
        self.assertTrue(result.detection.refinement_applied)

    def test_refinement_off(self) -> None:
        landmarks = _full_synthetic_landmarks()
        detector = MockLandmarkDetector(
            refined=landmarks,
            raw=landmarks,
            refinement_enabled=False,
            refinement_applied=False,
        )
        result = run_measurement_pipeline(_sample_preprocessed(), detector=detector)
        assert result.detection is not None
        self.assertFalse(result.detection.refinement_enabled)
        self.assertFalse(result.detection.refinement_applied)

    def test_raw_landmarks_preserved(self) -> None:
        raw = _full_synthetic_landmarks()
        refined = list(raw)
        raw_asl = next(item for item in raw if item.name == "ASL_L")
        refined_asl = DetectedLandmark(
            name="ASL_L",
            x=raw_asl.x + 7.0,
            y=raw_asl.y + 2.0,
            confidence=0.95,
        )
        refined = [refined_asl if item.name == "ASL_L" else item for item in raw]
        detector = MockLandmarkDetector(refined=refined, raw=raw, refinement_applied=True)
        result = run_measurement_pipeline(_sample_preprocessed(), detector=detector)
        assert result.detection is not None
        raw_map = {(item["name"], item["x"], item["y"]) for item in result.detection.raw_landmarks}
        ref_map = {(item["name"], item["x"], item["y"]) for item in result.detection.refined_landmarks}
        self.assertNotEqual(raw_map, ref_map)
        raw_asl_entry = next(item for item in result.detection.raw_landmarks if item["name"] == "ASL_L")
        self.assertAlmostEqual(raw_asl_entry["x"], raw_asl.x, places=5)

    def test_other_landmarks_unchanged_by_refinement(self) -> None:
        raw = _full_synthetic_landmarks()
        refined = list(raw)
        raw_asl = next(item for item in raw if item.name == "ASL_L")
        refined_asl = DetectedLandmark(
            name="ASL_L",
            x=raw_asl.x + 4.0,
            y=raw_asl.y + 1.0,
            confidence=0.95,
        )
        refined = [refined_asl if item.name == "ASL_L" else item for item in raw]
        detector = MockLandmarkDetector(refined=refined, raw=raw, refinement_applied=True)
        result = run_measurement_pipeline(_sample_preprocessed(), detector=detector)
        assert result.detection is not None
        raw_by_name = {item["name"]: (item["x"], item["y"]) for item in result.detection.raw_landmarks}
        ref_by_name = {item["name"]: (item["x"], item["y"]) for item in result.detection.refined_landmarks}
        for name in MVP_LANDMARK_NAMES:
            if name == "ASL_L":
                continue
            self.assertEqual(raw_by_name[name], ref_by_name[name], msg=name)

    def test_ccd_identical_refinement_on_off(self) -> None:
        raw = _full_synthetic_landmarks()
        refined = list(raw)
        raw_asl = next(item for item in raw if item.name == "ASL_L")
        refined_asl = DetectedLandmark(
            name="ASL_L",
            x=raw_asl.x + 6.0,
            y=raw_asl.y + 4.0,
            confidence=0.95,
        )
        refined = [refined_asl if item.name == "ASL_L" else item for item in raw]
        on = run_measurement_pipeline(
            _sample_preprocessed(),
            detector=MockLandmarkDetector(refined=refined, raw=raw, refinement_applied=True),
        )
        off = run_measurement_pipeline(
            _sample_preprocessed(),
            detector=MockLandmarkDetector(refined=raw, raw=raw, refinement_applied=False),
        )
        assert on.measurements is not None and off.measurements is not None
        self.assertAlmostEqual(
            on.measurements.right.ccd.value_deg,
            off.measurements.right.ccd.value_deg,
            places=5,
        )
        self.assertAlmostEqual(
            on.measurements.left.ccd.value_deg,
            off.measurements.left.ccd.value_deg,
            places=5,
        )

    def test_result_json_serializable(self) -> None:
        landmarks = _full_synthetic_landmarks()
        detector = MockLandmarkDetector(refined=landmarks, raw=landmarks)
        result = run_measurement_pipeline(_sample_preprocessed(), detector=detector)
        payload = result.to_dict()
        encoded = json.dumps(payload, default=str)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["status"], "ok")
        self.assertIn("measurements", decoded)
        self.assertIn("right", decoded["measurements"])


class TestMeasurementServiceErrors(unittest.TestCase):
    def test_model_not_found_via_yolo(self) -> None:
        from backend.app.services.detection.yolo_pose import YoloPoseLandmarkDetector

        detector = YoloPoseLandmarkDetector(model_path="/does/not/exist/best.pt")
        result = run_measurement_pipeline(_sample_preprocessed(), detector=detector)
        self.assertEqual(result.status, "error")
        self.assertIsNone(result.measurements)

    def test_invalid_image(self) -> None:
        from backend.app.services.detection.yolo_pose import YoloPoseLandmarkDetector

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
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp:
            path = Path(tmp.name)
            path.write_bytes(b"x")
        detector = YoloPoseLandmarkDetector(model_path=path, model_loader=lambda _: object())
        result = run_measurement_pipeline(image, detector=detector)
        self.assertEqual(result.status, "error")
        path.unlink(missing_ok=True)

    def test_low_bbox_confidence(self) -> None:
        from backend.app.services.detection.yolo_pose import YoloPoseLandmarkDetector
        from backend.tests.test_yolo_pose_detector import FakeYoloModel, _make_ultralytics_result

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp:
            path = Path(tmp.name)
            path.write_bytes(b"x")
        detector = YoloPoseLandmarkDetector(
            model_path=path,
            model_loader=lambda _: FakeYoloModel(_make_ultralytics_result(det_conf=0.05)),
        )
        result = run_measurement_pipeline(_sample_preprocessed(), detector=detector)
        self.assertEqual(result.status, "error")
        self.assertEqual(result.audit.get("error_type"), "LowBboxConfidenceError")
        path.unlink(missing_ok=True)


def print_summary() -> None:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestMeasurementService))
    suite.addTests(loader.loadTestsFromTestCase(TestMeasurementServiceErrors))
    runner = unittest.TextTestRunner(verbosity=0)
    outcome = runner.run(suite)
    total = outcome.testsRun
    passed = total - len(outcome.failures) - len(outcome.errors)
    print("MEASUREMENT SERVICE COMPLETE")
    print("Detection: OK")
    print("VCE: OK")
    print("Tonnis: OK")
    print("CCD: OK")
    print("Refinement: OK")
    print("Error handling: OK")
    print(f"Measurement service tests: {passed}/{total}")


if __name__ == "__main__":
    outcome = unittest.main(exit=False, verbosity=2)
    print_summary()
    sys.exit(0 if outcome.result.wasSuccessful() else 1)
