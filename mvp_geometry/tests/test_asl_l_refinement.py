"""Tests unitaires du refinement ASL_L (C_asm_offset)."""

from __future__ import annotations

import copy
import unittest
from dataclasses import replace

from mvp_geometry.landmarks import Landmark, MVP_LANDMARK_NAMES
from mvp_geometry.refinement.asl_l import RefinementStatus, refine_asl_l
from mvp_geometry.refinement.calibration import (
    ASL_L_REFINEMENT_ENABLED,
    AslLCalibration,
    TRAIN_ASM_OFFSET_CALIBRATION,
)


def _landmark(name: str, x: float | None, y: float | None, v: int = 2) -> Landmark:
    side = "R" if name.endswith("_R") else "L" if name.endswith("_L") else "?"
    index = MVP_LANDMARK_NAMES.index(name) + 1
    return Landmark(id=f"LM-{index:02d}", name=name, side=side, x=x, y=y, v=v)


def _full_landmarks(
    *,
    asm_l: tuple[float, float] | None = (1000.0, 500.0),
    asl_l: tuple[float, float] | None = (1500.0, 400.0),
    asm_l_v: int = 2,
    asl_l_v: int = 2,
    include_asl_l: bool = True,
    include_asm_l: bool = True,
) -> dict[str, Landmark]:
    landmarks: dict[str, Landmark] = {}
    for index, name in enumerate(MVP_LANDMARK_NAMES):
        if name == "ASM_L":
            if not include_asm_l:
                continue
            if asm_l is None:
                landmarks[name] = _landmark(name, None, None, v=asm_l_v)
            else:
                landmarks[name] = _landmark(name, asm_l[0], asm_l[1], v=asm_l_v)
        elif name == "ASL_L":
            if not include_asl_l:
                continue
            if asl_l is None:
                landmarks[name] = _landmark(name, None, None, v=asl_l_v)
            else:
                landmarks[name] = _landmark(name, asl_l[0], asl_l[1], v=asl_l_v)
        else:
            landmarks[name] = _landmark(name, 100.0 + index, 200.0 + index)
    return landmarks


class TestAslLRefinement(unittest.TestCase):
    def setUp(self) -> None:
        self.cal = TRAIN_ASM_OFFSET_CALIBRATION

    def test_applies_dx_dy_correctly(self) -> None:
        landmarks = _full_landmarks(asm_l=(1000.0, 500.0))
        result = refine_asl_l(landmarks, self.cal, enabled=True)

        self.assertTrue(result.applied)
        self.assertEqual(result.status, RefinementStatus.APPLIED)
        asm = landmarks["ASM_L"]
        expected_x = round(float(asm.x) + self.cal.dx, 2)
        expected_y = round(float(asm.y) + self.cal.dy, 2)
        refined = result.landmarks["ASL_L"]
        self.assertAlmostEqual(refined.x, expected_x)
        self.assertAlmostEqual(refined.y, expected_y)
        self.assertEqual(refined.v, 2)

    def test_asl_l_absent_still_refines_from_asm_l(self) -> None:
        landmarks = _full_landmarks(include_asl_l=False)
        result = refine_asl_l(landmarks, self.cal, enabled=True)

        self.assertTrue(result.applied)
        self.assertIsNone(result.original_asl_l)
        self.assertIn("ASL_L", result.landmarks)
        self.assertTrue(result.landmarks["ASL_L"].usable)

    def test_asm_l_absent_no_refinement(self) -> None:
        landmarks = _full_landmarks(include_asm_l=False)
        result = refine_asl_l(landmarks, self.cal, enabled=True)

        self.assertFalse(result.applied)
        self.assertEqual(result.status, RefinementStatus.ASM_L_ABSENT)
        self.assertEqual(result.landmarks["ASL_L"], landmarks["ASL_L"])

    def test_asm_l_v0_no_refinement(self) -> None:
        landmarks = _full_landmarks(asm_l=(1000.0, 500.0), asm_l_v=0)
        result = refine_asl_l(landmarks, self.cal, enabled=True)

        self.assertFalse(result.applied)
        self.assertEqual(result.status, RefinementStatus.ASM_L_INVALID)
        self.assertEqual(result.landmarks["ASL_L"], landmarks["ASL_L"])

    def test_refinement_disabled(self) -> None:
        landmarks = _full_landmarks()
        result = refine_asl_l(landmarks, self.cal, enabled=False)

        self.assertFalse(result.applied)
        self.assertEqual(result.status, RefinementStatus.DISABLED)
        self.assertEqual(result.landmarks["ASL_L"], landmarks["ASL_L"])

    def test_other_landmarks_unchanged(self) -> None:
        landmarks = _full_landmarks()
        snapshot = copy.deepcopy(landmarks)
        result = refine_asl_l(landmarks, self.cal, enabled=True)

        for name, lm in snapshot.items():
            if name == "ASL_L":
                continue
            self.assertEqual(result.landmarks[name], lm, msg=name)

    def test_asm_l_preserved(self) -> None:
        landmarks = _full_landmarks()
        result = refine_asl_l(landmarks, self.cal, enabled=True)

        self.assertEqual(result.landmarks["ASM_L"], landmarks["ASM_L"])

    def test_original_asl_l_preserved_for_audit(self) -> None:
        landmarks = _full_landmarks(asl_l=(1500.0, 400.0))
        original = landmarks["ASL_L"]
        result = refine_asl_l(landmarks, self.cal, enabled=True)

        self.assertEqual(result.original_asl_l, original)
        self.assertNotEqual(result.landmarks["ASL_L"], original)

    def test_out_of_bounds_detected(self) -> None:
        landmarks = _full_landmarks(asm_l=(10.0, 10.0))
        result = refine_asl_l(
            landmarks,
            self.cal,
            enabled=True,
            image_width=2000.0,
            image_height=2000.0,
        )

        self.assertTrue(result.applied)
        self.assertTrue(result.out_of_bounds)

    def test_in_bounds_not_flagged(self) -> None:
        landmarks = _full_landmarks(asm_l=(1000.0, 500.0))
        result = refine_asl_l(
            landmarks,
            self.cal,
            enabled=True,
            image_width=3000.0,
            image_height=3000.0,
        )

        self.assertTrue(result.applied)
        self.assertFalse(result.out_of_bounds)

    def test_reproducibility(self) -> None:
        landmarks = _full_landmarks()
        first = refine_asl_l(landmarks, self.cal, enabled=True)
        second = refine_asl_l(landmarks, self.cal, enabled=True)

        self.assertEqual(first.landmarks["ASL_L"], second.landmarks["ASL_L"])
        self.assertEqual(first.refined_x, second.refined_x)
        self.assertEqual(first.refined_y, second.refined_y)

    def test_train_calibration_constants(self) -> None:
        self.assertAlmostEqual(self.cal.dx, 511.56)
        self.assertAlmostEqual(self.cal.dy, -92.68)
        self.assertTrue(self.cal.is_train_only)
        self.assertEqual(self.cal.n_train_cases, 21)

    def test_global_enabled_flag_default(self) -> None:
        self.assertTrue(ASL_L_REFINEMENT_ENABLED)

    def test_refines_even_when_original_asl_l_v0(self) -> None:
        """ASM_L valide suffit ; on ne dépend pas de la confiance YOLO de ASL_L."""
        landmarks = _full_landmarks(asl_l=(999.0, 999.0), asl_l_v=0)
        result = refine_asl_l(landmarks, self.cal, enabled=True)

        self.assertTrue(result.applied)
        self.assertEqual(result.landmarks["ASL_L"].v, 2)
        self.assertEqual(result.original_asl_l.v, 0)

    def test_confidence_and_identity_preserved_on_refined(self) -> None:
        """L'identité du landmark ASL_L est conservée ; l'original reste auditable."""
        landmarks = _full_landmarks(asl_l=(1500.0, 400.0))
        original = landmarks["ASL_L"]
        result = refine_asl_l(landmarks, self.cal, enabled=True)
        refined = result.landmarks["ASL_L"]

        self.assertEqual(refined.id, original.id)
        self.assertEqual(refined.name, original.name)
        self.assertEqual(refined.side, original.side)
        self.assertEqual(result.original_asl_l, original)

    def test_custom_calibration(self) -> None:
        landmarks = _full_landmarks(asm_l=(100.0, 200.0))
        custom = AslLCalibration(dx=10.0, dy=-5.0, source="TRAIN", n_train_cases=21)
        result = refine_asl_l(landmarks, custom, enabled=True)

        self.assertAlmostEqual(result.landmarks["ASL_L"].x, 110.0)
        self.assertAlmostEqual(result.landmarks["ASL_L"].y, 195.0)


if __name__ == "__main__":
    unittest.main()
