"""Tests des schémas Pydantic — aucune donnée médicale."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from backend.app.schemas.landmarks import LandmarkIn, LandmarkName
from backend.app.schemas.measurements import InputMode, MeasurementsRequest


class TestLandmarkIn(unittest.TestCase):
    def test_valid_landmark(self):
        item = LandmarkIn(name=LandmarkName.TD_R, x=10.0, y=20.0, v=2)
        self.assertEqual(item.name, LandmarkName.TD_R)
        self.assertEqual(item.v, 2)

    def test_partial_coordinates_rejected(self):
        with self.assertRaises(ValidationError):
            LandmarkIn(name=LandmarkName.FHC_R, x=1.0, y=None, v=2)

    def test_invalid_visibility_rejected(self):
        with self.assertRaises(ValidationError):
            LandmarkIn(name=LandmarkName.ASL_L, x=1.0, y=2.0, v=9)

    def test_missing_coords_allowed(self):
        item = LandmarkIn(name=LandmarkName.ASM_R, v=0)
        self.assertIsNone(item.x)
        self.assertIsNone(item.y)


class TestMeasurementsRequest(unittest.TestCase):
    def test_landmarks_mode_requires_list(self):
        with self.assertRaises(ValidationError):
            MeasurementsRequest(mode=InputMode.landmarks, landmarks=None)

    def test_landmarks_mode_rejects_empty_list(self):
        with self.assertRaises(ValidationError):
            MeasurementsRequest(mode=InputMode.landmarks, landmarks=[])

    def test_image_mode_without_landmarks(self):
        req = MeasurementsRequest(mode=InputMode.image)
        self.assertEqual(req.mode, InputMode.image)
        self.assertIsNone(req.landmarks)

    def test_sides_no_duplicates(self):
        with self.assertRaises(ValidationError):
            MeasurementsRequest(
                mode=InputMode.landmarks,
                sides=["R", "R"],
                landmarks=[
                    LandmarkIn(name=LandmarkName.TD_R, x=0.0, y=0.0, v=2),
                ],
            )

    def test_valid_landmarks_request(self):
        req = MeasurementsRequest(
            mode=InputMode.landmarks,
            sides=["R", "L"],
            landmarks=[
                LandmarkIn(name=LandmarkName.TD_R, x=300.0, y=500.0, v=2),
                LandmarkIn(name=LandmarkName.TD_L, x=500.0, y=500.0, v=2),
            ],
        )
        self.assertEqual(len(req.landmarks), 2)


if __name__ == "__main__":
    unittest.main()
