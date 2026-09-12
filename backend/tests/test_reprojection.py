"""Tests de reprojection prétraité → image originale.

Points de test purement géométriques (aucune donnée médicale).
"""

from __future__ import annotations

import unittest

from backend.app.services.detection.base import DetectedLandmark
from backend.app.services.detection.reprojection import (
    ReprojectionError,
    ReprojectionMeta,
    reproject_landmark,
    reproject_landmarks,
    reproject_point,
    reprojection_meta_from_preprocessed,
)
from backend.app.services.preprocessing import PreprocessConfig, preprocess_image


def _meta_letterbox() -> ReprojectionMeta:
    """100×50 → canvas 200×200, scale=2, contenu 200×100, pad_top=50."""
    return ReprojectionMeta(
        scale=2.0,
        pad_left=0,
        pad_top=50,
        original_size=(100, 50),
        processed_size=(200, 200),
    )


class TestReprojectPoint(unittest.TestCase):
    def test_center_of_content_maps_to_center_of_original(self):
        meta = _meta_letterbox()
        # Centre du contenu utile : (100, 100) en prétraité.
        x, y, in_content, in_bounds = reproject_point(100.0, 100.0, meta)
        self.assertTrue(in_content)
        self.assertTrue(in_bounds)
        self.assertAlmostEqual(x, 50.0, places=6)
        self.assertAlmostEqual(y, 25.0, places=6)

    def test_origin_of_content_maps_to_origin_of_original(self):
        meta = _meta_letterbox()
        x, y, in_content, in_bounds = reproject_point(0.0, 50.0, meta)
        self.assertTrue(in_content)
        self.assertTrue(in_bounds)
        self.assertAlmostEqual(x, 0.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)

    def test_padding_zone_out_of_content(self):
        meta = _meta_letterbox()
        _, _, in_content, in_bounds = reproject_point(10.0, 10.0, meta)
        self.assertFalse(in_content)
        self.assertFalse(in_bounds)

    def test_reprojected_outside_original_bounds(self):
        # Arrondi de content_w peut dépasser légèrement original_size / scale.
        meta = ReprojectionMeta(
            scale=1.51,
            pad_left=0,
            pad_top=0,
            original_size=(5, 5),
            processed_size=(8, 8),
        )
        _, _, in_content, in_bounds = reproject_point(7.99, 0.0, meta)
        self.assertTrue(in_content)
        self.assertFalse(in_bounds)


class TestReprojectLandmark(unittest.TestCase):
    def test_round_trip_via_detected_landmark(self):
        meta = _meta_letterbox()
        detected = DetectedLandmark(name="TD_R", x=0.0, y=50.0)
        result = reproject_landmark(detected, meta)
        self.assertEqual(result.name, "TD_R")
        self.assertAlmostEqual(result.x, 0.0, places=6)
        self.assertAlmostEqual(result.y, 0.0, places=6)
        self.assertTrue(result.in_content_area)
        self.assertTrue(result.in_image_bounds)

    def test_meta_from_preprocessed_matches_letterbox(self):
        import io

        import numpy as np
        from PIL import Image

        data = np.full((50, 100), 0, dtype=np.uint8)
        buffer = io.BytesIO()
        Image.fromarray(data).save(buffer, format="PNG")
        preprocessed = preprocess_image(
            buffer.getvalue(),
            PreprocessConfig(target_size=(200, 200)),
        )
        meta = reprojection_meta_from_preprocessed(preprocessed)
        self.assertAlmostEqual(meta.scale, 2.0, places=6)
        self.assertEqual(meta.pad_left, 0)
        self.assertEqual(meta.pad_top, 50)
        self.assertEqual(meta.original_size, (100, 50))

    def test_batch_reprojection(self):
        meta = _meta_letterbox()
        landmarks = (
            DetectedLandmark(name="TD_R", x=0.0, y=50.0),
            DetectedLandmark(name="TD_L", x=199.0, y=149.0),
        )
        results = reproject_landmarks(landmarks, meta)
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].in_image_bounds)
        self.assertTrue(results[1].in_image_bounds)


class TestInvalidMetadata(unittest.TestCase):
    def test_zero_scale(self):
        with self.assertRaises(ReprojectionError):
            ReprojectionMeta(
                scale=0.0,
                pad_left=0,
                pad_top=0,
                original_size=(100, 100),
                processed_size=(100, 100),
            )

    def test_negative_padding(self):
        with self.assertRaises(ReprojectionError):
            ReprojectionMeta(
                scale=1.0,
                pad_left=-1,
                pad_top=0,
                original_size=(100, 100),
                processed_size=(100, 100),
            )

    def test_content_exceeds_canvas(self):
        with self.assertRaises(ReprojectionError):
            ReprojectionMeta(
                scale=2.0,
                pad_left=0,
                pad_top=0,
                original_size=(100, 100),
                processed_size=(100, 100),
            )


if __name__ == "__main__":
    unittest.main()
