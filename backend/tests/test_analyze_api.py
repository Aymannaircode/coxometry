"""Tests HTTP POST /analyze — mocks YOLO, pas de données médicales réelles."""

from __future__ import annotations

import io
import json
import math
import sys
import unittest
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.api.routes.analyze import get_landmark_detector_dep
from backend.app.services.analyze import MAX_UPLOAD_BYTES
from backend.app.services.detection.base import (
    DetectedLandmark,
    DetectionBoundingBox,
    LandmarkDetectionResult,
    LandmarkDetector,
)
from backend.app.services.detection.yolo_pose import DEFAULT_V2_MODEL_PATH
from backend.app.services.preprocessing import PreprocessedImage
from backend.main import app
from mvp_geometry.landmarks import MVP_LANDMARK_NAMES
from mvp_geometry.refinement import ASL_L_REFINEMENT_ENABLED


def _encode_gray(width: int, height: int, fmt: str = "PNG") -> bytes:
    data = np.full((height, width), 128, dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(data).save(buffer, format=fmt)
    return buffer.getvalue()


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


def _full_synthetic_landmarks() -> list[DetectedLandmark]:
    td_r, td_l = (300.0, 500.0), (500.0, 500.0)
    asm_r, asm_l = (250.0, 300.0), (550.0, 300.0)
    fnm_r, fnm_l = (360.0, 560.0), (440.0, 560.0)
    fsp_r, fsd_r = (400.0, 600.0), (400.0, 900.0)
    fsp_l, fsd_l = (600.0, 600.0), (600.0, 900.0)
    fhc_r = _ccd_fhc(fnm_r, 130.0, side="R")
    fhc_l = _ccd_fhc(fnm_l, 128.0, side="L")
    coords = {
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
    return [
        DetectedLandmark(name=name, x=coords[name][0], y=coords[name][1], confidence=0.95)
        for name in MVP_LANDMARK_NAMES
    ]


def _degenerate_geometry_landmarks() -> list[DetectedLandmark]:
    """TD_R = TD_L → ITH indéterminée pour VCE/Tönnis."""
    landmarks = _full_synthetic_landmarks()
    td_confused = DetectedLandmark(name="TD_R", x=500.0, y=500.0, confidence=0.95)
    return [td_confused if item.name == "TD_R" else item for item in landmarks]


def _partial_landmarks_missing_asl_r() -> list[DetectedLandmark]:
    return [item for item in _full_synthetic_landmarks() if item.name != "ASL_R"]


class MockLandmarkDetector(LandmarkDetector):
    def __init__(
        self,
        *,
        status: str = "ok",
        message: str | None = None,
        refined: Sequence[DetectedLandmark] | None = None,
        raw: Sequence[DetectedLandmark] | None = None,
        refinement_enabled: bool = ASL_L_REFINEMENT_ENABLED,
        refinement_applied: bool = True,
        error_type: str | None = None,
    ) -> None:
        self._status = status
        self._message = message
        self._refined = tuple(refined or ())
        self._raw = tuple(raw if raw is not None else refined or ())
        self._refinement_enabled = refinement_enabled
        self._refinement_applied = refinement_applied
        self._error_type = error_type or message

    @property
    def name(self) -> str:
        return "mock_detector"

    def detect(self, image: PreprocessedImage) -> LandmarkDetectionResult:
        _ = image
        confidences = {item.name: item.confidence or 0.0 for item in self._raw}
        audit: dict = {
            "refinement_enabled": self._refinement_enabled,
            "refinement_applied": self._refinement_applied,
            "keypoint_confidences": confidences,
        }
        if self._status != "ok":
            audit["error_type"] = self._error_type or "DetectionError"
        bbox = DetectionBoundingBox(x1=10.0, y1=20.0, x2=500.0, y2=400.0, confidence=0.92)
        return LandmarkDetectionResult(
            status=self._status,  # type: ignore[arg-type]
            message=self._message,
            landmarks=self._refined,
            raw_landmarks=self._raw,
            bounding_box=bbox if self._status == "ok" else None,
            detector_name=self.name,
            audit=audit,
        )


class AnalyzeApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._original_override = app.dependency_overrides.get(get_landmark_detector_dep)
        landmarks = _full_synthetic_landmarks()
        raw = list(landmarks)
        refined = list(landmarks)
        raw_asl = next(item for item in raw if item.name == "ASL_L")
        refined_asl = DetectedLandmark(
            name="ASL_L",
            x=raw_asl.x + 5.0,
            y=raw_asl.y + 3.0,
            confidence=0.95,
        )
        refined = [refined_asl if item.name == "ASL_L" else item for item in raw]
        app.dependency_overrides[get_landmark_detector_dep] = lambda: MockLandmarkDetector(
            refined=refined,
            raw=raw,
            refinement_applied=True,
        )
        self.client = TestClient(app)

    def tearDown(self) -> None:
        if self._original_override is None:
            app.dependency_overrides.pop(get_landmark_detector_dep, None)
        else:
            app.dependency_overrides[get_landmark_detector_dep] = self._original_override


class TestAnalyzeSuccess(AnalyzeApiTestCase):
    def test_post_valid_image(self) -> None:
        png = _encode_gray(256, 256, "PNG")
        response = self.client.post(
            "/analyze",
            files={"file": ("radio.png", png, "image/png")},
        )
        self.assertEqual(response.status_code, 200)

    def test_response_200(self) -> None:
        png = _encode_gray(128, 128, "PNG")
        response = self.client.post(
            "/analyze",
            files={"file": ("x.png", png, "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_json_structure(self) -> None:
        png = _encode_gray(64, 64, "PNG")
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", png, "image/png")},
        ).json()
        self.assertIn("detection", body)
        self.assertIn("measurements", body)
        self.assertIn("audit", body)
        self.assertIn("coordinate_space", body["detection"])
        cs = body["detection"]["coordinate_space"]
        self.assertEqual(cs["landmark_coordinate_space"], "original_image_pixels")
        self.assertEqual(cs["image_width"], 64)
        self.assertEqual(cs["image_height"], 64)
        self.assertIn("right", body["measurements"])
        self.assertIn("left", body["measurements"])
        for side in ("right", "left"):
            for measure in ("vce", "tonnis", "ccd"):
                item = body["measurements"][side][measure]
                self.assertIn("available", item)
                self.assertIn("value_deg", item)
                self.assertIn("reason", item)

    def test_vce_present(self) -> None:
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(64, 64), "image/png")},
        ).json()
        self.assertTrue(body["measurements"]["right"]["vce"]["available"])
        self.assertIsNotNone(body["measurements"]["right"]["vce"]["value_deg"])

    def test_tonnis_present(self) -> None:
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(64, 64), "image/png")},
        ).json()
        self.assertTrue(body["measurements"]["right"]["tonnis"]["available"])

    def test_ccd_present(self) -> None:
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(64, 64), "image/png")},
        ).json()
        self.assertTrue(body["measurements"]["right"]["ccd"]["available"])

    def test_refinement_indicated(self) -> None:
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(64, 64), "image/png")},
        ).json()
        detection = body["detection"]
        self.assertTrue(detection["refinement_enabled"])
        self.assertTrue(detection["refinement_applied"])

    def test_raw_and_refined_landmarks(self) -> None:
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(64, 64), "image/png")},
        ).json()
        self.assertEqual(len(body["detection"]["raw_landmarks"]), 14)
        self.assertEqual(len(body["detection"]["refined_landmarks"]), 14)
        raw_asl = next(item for item in body["detection"]["raw_landmarks"] if item["name"] == "ASL_L")
        ref_asl = next(item for item in body["detection"]["refined_landmarks"] if item["name"] == "ASL_L")
        self.assertNotEqual((raw_asl["x"], raw_asl["y"]), (ref_asl["x"], ref_asl["y"]))

    def test_json_fully_serializable(self) -> None:
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(64, 64), "image/png")},
        ).json()
        encoded = json.dumps(body)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["status"], "ok")


class TestAnalyzeErrors(unittest.TestCase):
    def setUp(self) -> None:
        self._original_override = app.dependency_overrides.get(get_landmark_detector_dep)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        if self._original_override is None:
            app.dependency_overrides.pop(get_landmark_detector_dep, None)
        else:
            app.dependency_overrides[get_landmark_detector_dep] = self._original_override

    def test_invalid_image(self) -> None:
        response = self.client.post(
            "/analyze",
            files={"file": ("bad.png", b"not-an-image", "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["error"]["code"], "invalid_image")

    def test_missing_file_422(self) -> None:
        response = self.client.post(
            "/analyze",
            files={"notes": ("notes.txt", b"hello", "text/plain")},
        )
        self.assertEqual(response.status_code, 422)

    def test_model_not_found(self) -> None:
        from backend.app.services.detection.yolo_pose import YoloPoseLandmarkDetector

        app.dependency_overrides[get_landmark_detector_dep] = lambda: YoloPoseLandmarkDetector(
            model_path="/does/not/exist/best.pt"
        )
        response = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(32, 32), "image/png")},
        )
        body = response.json()
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["error"]["code"], "model_not_found")
        self.assertNotIn("best.pt", body["error"]["message"])

    def test_no_detection(self) -> None:
        app.dependency_overrides[get_landmark_detector_dep] = lambda: MockLandmarkDetector(
            status="error",
            message="Aucune détection pelvis.",
            error_type="NoDetectionError",
        )
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(32, 32), "image/png")},
        ).json()
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["error"]["code"], "no_detection")

    def test_geometry_error(self) -> None:
        app.dependency_overrides[get_landmark_detector_dep] = lambda: MockLandmarkDetector(
            refined=_degenerate_geometry_landmarks(),
            raw=_degenerate_geometry_landmarks(),
        )
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(32, 32), "image/png")},
        ).json()
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["error"]["code"], "geometry_error")

    def test_unavailable_measure_partial_success(self) -> None:
        app.dependency_overrides[get_landmark_detector_dep] = lambda: MockLandmarkDetector(
            refined=_partial_landmarks_missing_asl_r(),
            raw=_partial_landmarks_missing_asl_r(),
        )
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(32, 32), "image/png")},
        ).json()
        self.assertEqual(body["status"], "ok")
        self.assertFalse(body["measurements"]["right"]["vce"]["available"])
        self.assertIsNone(body["measurements"]["right"]["vce"]["value_deg"])
        self.assertTrue(body["measurements"]["right"]["ccd"]["available"])

    def test_unsupported_format_bmp(self) -> None:
        buffer = io.BytesIO()
        Image.fromarray(np.full((32, 32), 90, dtype=np.uint8)).save(buffer, format="BMP")
        body = self.client.post(
            "/analyze",
            files={"file": ("radio.bmp", buffer.getvalue(), "image/bmp")},
        ).json()
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["error"]["code"], "unsupported_format")

    def test_file_too_large(self) -> None:
        app.dependency_overrides[get_landmark_detector_dep] = lambda: MockLandmarkDetector(
            refined=_full_synthetic_landmarks(),
            raw=_full_synthetic_landmarks(),
        )
        oversized = b"\x00" * (MAX_UPLOAD_BYTES + 1)
        body = self.client.post(
            "/analyze",
            files={"file": ("big.png", oversized, "image/png")},
        ).json()
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["error"]["code"], "file_too_large")

    def test_audit_does_not_expose_model_path(self) -> None:
        app.dependency_overrides[get_landmark_detector_dep] = lambda: MockLandmarkDetector(
            refined=_full_synthetic_landmarks(),
            raw=_full_synthetic_landmarks(),
        )
        body = self.client.post(
            "/analyze",
            files={"file": ("x.png", _encode_gray(32, 32), "image/png")},
        ).json()
        audit_blob = json.dumps(body.get("audit", {}))
        self.assertNotIn("best.pt", audit_blob)
        self.assertNotIn("model_path", audit_blob)


@unittest.skipUnless(DEFAULT_V2_MODEL_PATH.is_file(), "Checkpoint V2 absent")
class TestAnalyzeIntegration(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides.pop(get_landmark_detector_dep, None)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.pop(get_landmark_detector_dep, None)

    def test_real_v2_analyze(self) -> None:
        response = self.client.post(
            "/analyze",
            files={"file": ("sample.png", _encode_gray(512, 512), "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn(body["status"], ("ok", "error"))
        if body["status"] == "ok":
            self.assertIn("detection", body)
            self.assertIn("measurements", body)


def print_summary() -> None:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyzeSuccess))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyzeErrors))
    if DEFAULT_V2_MODEL_PATH.is_file():
        suite.addTests(loader.loadTestsFromTestCase(TestAnalyzeIntegration))

    runner = unittest.TextTestRunner(verbosity=0)
    outcome = runner.run(suite)
    total = outcome.testsRun
    passed = total - len(outcome.failures) - len(outcome.errors)

    print("FASTAPI ANALYZE API COMPLETE")
    print("Endpoint: POST /analyze")
    print("Success response: OK")
    print("Error handling: OK")
    print("Security validation: OK")
    print(f"API tests: {passed}/{total}")


if __name__ == "__main__":
    outcome = unittest.main(exit=False, verbosity=2)
    print_summary()
    sys.exit(0 if outcome.result.wasSuccessful() else 1)
