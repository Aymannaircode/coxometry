"""Tests unitaires du pipeline image — aucune IA, aucun landmark inventé."""

from __future__ import annotations

import io
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from backend.app.schemas.measurements import InputMode, MeasurementsRequest
from backend.app.services.detection.base import (
    DetectedLandmark,
    LandmarkDetectionResult,
    LandmarkDetector,
)
from backend.app.services.landmark_detection import detect_landmarks
from backend.app.services.pipeline import (
    run_measurements,
    run_measurements_from_image,
)
from backend.app.services.preprocessing import PreprocessedImage


def _encode_gray(width: int, height: int, fmt: str = "PNG") -> bytes:
    data = np.full((height, width), 128, dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(data).save(buffer, format=fmt)
    return buffer.getvalue()


class _FakeOkDetector(LandmarkDetector):
    """Détecteur de test uniquement : renvoie des landmarks synthétiques."""

    @property
    def name(self) -> str:
        return "fake_ok"

    def detect(self, image: PreprocessedImage) -> LandmarkDetectionResult:
        w, h = image.processed_size
        return LandmarkDetectionResult(
            status="ok",
            message=None,
            landmarks=(
                DetectedLandmark(name="TD_R", x=w / 2.0, y=h / 2.0, confidence=1.0),
                DetectedLandmark(name="TD_L", x=w / 2.0 + 10.0, y=h / 2.0, confidence=1.0),
            ),
            detector_name=self.name,
        )


class TestRunMeasurementsFromImage(unittest.TestCase):
    def test_default_detector_not_implemented(self):
        result = run_measurements_from_image(_encode_gray(40, 30))
        self.assertEqual(result.status, "not_implemented")
        self.assertEqual(result.mode, InputMode.image)
        self.assertEqual(result.source, "image")
        self.assertIsNone(result.sides)
        self.assertIsNotNone(result.message)

    def test_invalid_format_returns_error(self):
        buffer = io.BytesIO()
        Image.fromarray(np.zeros((16, 16), dtype=np.uint8)).save(buffer, format="BMP")
        result = run_measurements_from_image(buffer.getvalue())
        self.assertEqual(result.status, "error")
        self.assertIsNone(result.sides)
        self.assertIn("non supporté", (result.message or "").lower())

    def test_unreadable_returns_error(self):
        result = run_measurements_from_image(b"not-an-image")
        self.assertEqual(result.status, "error")
        self.assertIsNone(result.sides)

    def test_ok_path_with_injected_detector(self):
        """Vérifie le branchement reprojection → géométrie sans modèle réel."""

        def _with_fake(preprocessed, detector=None, *, reproject=True):
            return detect_landmarks(
                preprocessed,
                detector=_FakeOkDetector(),
                reproject=reproject,
            )

        with patch(
            "backend.app.services.pipeline.landmark_detection.detect_landmarks",
            side_effect=_with_fake,
        ):
            result = run_measurements_from_image(_encode_gray(64, 48), sides=["R"])

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.source, "image")
        self.assertIsNotNone(result.sides)
        assert result.sides is not None
        self.assertIn("R", result.sides)
        # TD seuls : VCE indisponible, mais structure présente.
        self.assertFalse(result.sides["R"].vce.available)


class TestJsonImageModeStillStub(unittest.TestCase):
    def test_json_image_without_bytes(self):
        response = run_measurements(MeasurementsRequest(mode=InputMode.image))
        self.assertEqual(response.status, "not_implemented")
        self.assertIsNone(response.sides)


if __name__ == "__main__":
    unittest.main()
