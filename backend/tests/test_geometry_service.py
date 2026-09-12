"""Tests du service géométrie — points synthétiques analytiques uniquement."""

from __future__ import annotations

import math
import unittest

from backend.app.schemas.landmarks import LandmarkIn, LandmarkName
from backend.app.services.geometry import compute_measurements, landmarks_to_geometry


def _vce_asl(fhc, target_deg=25.0, radius=100.0, side="R"):
    """ASL synthétique donnant un VCE exact (ITH horizontale)."""
    lateral = (-1.0, 0.0) if side == "R" else (1.0, 0.0)
    cranial = (0.0, -1.0)
    theta = math.radians(target_deg)
    return (
        fhc[0] + radius * (math.sin(theta) * lateral[0] + math.cos(theta) * cranial[0]),
        fhc[1] + radius * (math.sin(theta) * lateral[1] + math.cos(theta) * cranial[1]),
    )


class TestGeometryService(unittest.TestCase):
    def test_conversion_preserves_names(self):
        items = [
            LandmarkIn(name=LandmarkName.TD_R, x=1.0, y=2.0, v=2),
            LandmarkIn(name=LandmarkName.FHC_L, x=3.0, y=4.0, v=0),
        ]
        indexed = landmarks_to_geometry(items)
        self.assertIn("TD_R", indexed)
        self.assertTrue(indexed["TD_R"].usable)
        self.assertFalse(indexed["FHC_L"].usable)

    def test_vce_synthetic_right(self):
        fhc = (200.0, 400.0)
        asl = _vce_asl(fhc, target_deg=25.0, side="R")
        landmarks = [
            LandmarkIn(name=LandmarkName.TD_R, x=300.0, y=500.0, v=2),
            LandmarkIn(name=LandmarkName.TD_L, x=500.0, y=500.0, v=2),
            LandmarkIn(name=LandmarkName.FHC_R, x=fhc[0], y=fhc[1], v=2),
            LandmarkIn(name=LandmarkName.ASL_R, x=asl[0], y=asl[1], v=2),
        ]
        sides = compute_measurements(landmarks, sides=["R"])
        self.assertTrue(sides["R"].vce.available)
        self.assertAlmostEqual(sides["R"].vce.value_deg, 25.0, places=5)
        # Tönnis / CCD absents → indisponibles, pas inventés
        self.assertFalse(sides["R"].tonnis.available)
        self.assertFalse(sides["R"].ccd.available)

    def test_unusable_visibility(self):
        landmarks = [
            LandmarkIn(name=LandmarkName.TD_R, x=300.0, y=500.0, v=2),
            LandmarkIn(name=LandmarkName.TD_L, x=500.0, y=500.0, v=2),
            LandmarkIn(name=LandmarkName.FHC_R, x=200.0, y=400.0, v=0),
            LandmarkIn(name=LandmarkName.ASL_R, x=150.0, y=300.0, v=2),
        ]
        sides = compute_measurements(landmarks, sides=["R"])
        self.assertFalse(sides["R"].vce.available)
        self.assertIn("non exploitable", sides["R"].vce.reason)


if __name__ == "__main__":
    unittest.main()
