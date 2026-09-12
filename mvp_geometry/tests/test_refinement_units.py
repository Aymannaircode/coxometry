"""Tests unités refinement ASL_L — offset TRAIN vs espace prétraité."""

from __future__ import annotations

import unittest

from mvp_geometry.refinement.calibration import TRAIN_ASM_OFFSET_CALIBRATION
from mvp_geometry.refinement.units import (
    LandmarkCoordinateSpace,
    TRAIN_CALIBRATION_COORDINATE_SPACE,
    calibration_for_preprocessed_space,
    expected_original_offset_from_refined,
)


class TestRefinementUnits(unittest.TestCase):
    def test_train_calibration_space_is_original(self) -> None:
        self.assertEqual(
            TRAIN_CALIBRATION_COORDINATE_SPACE,
            LandmarkCoordinateSpace.ORIGINAL_IMAGE_PIXELS,
        )

    def test_scales_offset_by_letterbox_scale(self) -> None:
        scale = 0.18754578754578755
        scaled = calibration_for_preprocessed_space(TRAIN_ASM_OFFSET_CALIBRATION, scale)
        self.assertAlmostEqual(scaled.dx, TRAIN_ASM_OFFSET_CALIBRATION.dx * scale, places=6)
        self.assertAlmostEqual(scaled.dy, TRAIN_ASM_OFFSET_CALIBRATION.dy * scale, places=6)
        self.assertEqual(scaled.source, "TRAIN")

    def test_invalid_scale_raises(self) -> None:
        with self.assertRaises(ValueError):
            calibration_for_preprocessed_space(TRAIN_ASM_OFFSET_CALIBRATION, 0.0)

    def test_expected_original_offset_helper(self) -> None:
        dx, dy = expected_original_offset_from_refined(1000.0, 500.0, 1511.56, 407.32)
        self.assertAlmostEqual(dx, 511.56)
        self.assertAlmostEqual(dy, -92.68)


if __name__ == "__main__":
    unittest.main()
