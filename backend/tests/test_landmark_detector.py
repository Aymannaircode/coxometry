"""Tests de l'interface LandmarkDetector — stub par défaut ; YOLO V2 testé séparément."""

from __future__ import annotations

import io
import unittest

import numpy as np
from PIL import Image

from backend.app.services.detection.base import (
    DetectedLandmark,
    LandmarkFormatError,
    NotImplementedLandmarkDetector,
    get_default_detector,
    validate_detected_landmarks,
    validate_landmark_name,
)
from backend.app.services.landmark_detection import detect_landmarks
from backend.app.services.preprocessing import PreprocessConfig, preprocess_image


def _gray_png(width: int, height: int) -> bytes:
    data = np.full((height, width), 128, dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(data).save(buffer, format="PNG")
    return buffer.getvalue()


class TestLandmarkFormat(unittest.TestCase):
    def test_valid_name(self):
        validate_landmark_name("FHC_R")

    def test_invalid_name_raises(self):
        with self.assertRaises(LandmarkFormatError):
            validate_landmark_name("UNKNOWN")

    def test_duplicate_landmarks_raises(self):
        items = (
            DetectedLandmark(name="TD_R", x=1.0, y=2.0),
            DetectedLandmark(name="TD_R", x=3.0, y=4.0),
        )
        with self.assertRaises(LandmarkFormatError):
            validate_detected_landmarks(items)


class TestNotImplementedDetector(unittest.TestCase):
    def test_default_detector_is_stub(self):
        detector = get_default_detector()
        self.assertEqual(detector.name, "not_implemented")

    def test_detect_returns_no_landmarks(self):
        preprocessed = preprocess_image(
            _gray_png(64, 48),
            PreprocessConfig(target_size=(128, 128)),
        )
        result = NotImplementedLandmarkDetector().detect(preprocessed)
        self.assertEqual(result.status, "not_implemented")
        self.assertEqual(len(result.landmarks), 0)
        self.assertIn("Aucune coordonnée", result.message or "")

    def test_facade_without_image(self):
        result = detect_landmarks(None)
        self.assertEqual(result.status, "not_implemented")
        self.assertEqual(len(result.preprocessed_landmarks), 0)

    def test_facade_with_preprocessed_image(self):
        preprocessed = preprocess_image(_gray_png(32, 32))
        result = detect_landmarks(preprocessed)
        self.assertEqual(result.status, "not_implemented")
        self.assertEqual(len(result.original_landmarks), 0)


if __name__ == "__main__":
    unittest.main()
