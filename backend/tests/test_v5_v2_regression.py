"""Non-régression V2 vs V5 Phase 2 sur les 5 images val."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "annotation_pilot/manual_annotation_tool"))

from backend.app.services.detection.v5_phase2_pose import V5Phase2LandmarkDetector
from backend.app.services.detection.yolo_pose import YoloPoseLandmarkDetector
from backend.app.services.measurement_service import run_measurement_pipeline
from backend.app.services.preprocessing_v5 import preprocess_image_v5
from mvp_geometry.landmarks import MVP_LANDMARK_NAMES

VAL_IDS = ["B26_10", "B26_13", "B26_17", "B26_20", "B26_26"]
MAPPING_CSV = PROJECT_ROOT / "datasets/yolo_pose_new_26/meta/source_mapping.csv"
KP_TOL_NORM = 1e-3
KP_TOL_ORIG = 2.0
BOX_TOL = 1e-4
CONF_TOL = 1e-4


def _load_val_image_bytes(case_id: str) -> bytes:
    from dicom_render import render_dicom_png

    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    dicom = PROJECT_ROOT / mapping[case_id]["source_dicom"].replace("\\", "/")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        render_dicom_png(dicom, tmp_path)
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)


class TestV5V2Regression(unittest.TestCase):
    """Compare V2 et V5 sur le même preprocessing 640 (KP 0–13 via sous-détecteur V2)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v2 = YoloPoseLandmarkDetector()
        cls.v5 = V5Phase2LandmarkDetector()
        cls.v5_available = cls.v5.checkpoint_path.is_file()
        cls.v2_available = cls.v2.model_path.is_file()

    def _run_v5(self, case_id: str):
        raw = _load_val_image_bytes(case_id)
        prep_v5 = preprocess_image_v5(raw)
        return prep_v5, run_measurement_pipeline(prep_v5, detector=self.v5)

    def _run_v2_on_640(self, case_id: str):
        raw = _load_val_image_bytes(case_id)
        prep_v5 = preprocess_image_v5(raw)
        return prep_v5, run_measurement_pipeline(prep_v5, detector=self.v2)

    def test_models_available(self) -> None:
        if not self.v2_available or not self.v5_available:
            self.skipTest("Checkpoints V2 ou V5 absents")

    def test_detection_parity_at_640(self) -> None:
        """V5 utilise le sous-détecteur V2 sur 640 — bbox/conf identiques."""
        if not self.v2_available or not self.v5_available:
            self.skipTest("Checkpoints absents")
        for case_id in VAL_IDS:
            with self.subTest(case_id=case_id):
                _, r_v2_640 = self._run_v2_on_640(case_id)
                _, r_v5 = self._run_v5(case_id)
                self.assertEqual(r_v2_640.status, "ok")
                self.assertEqual(r_v5.status, "ok")
                assert r_v2_640.detection and r_v5.detection
                b2 = r_v2_640.detection.bounding_box
                b5 = r_v5.detection.bounding_box
                assert b2 and b5
                self.assertAlmostEqual(b2["confidence"], b5["confidence"], delta=CONF_TOL)

    def test_kp14_at_640_original_space(self) -> None:
        """KP 0–13 V5 == V2 sur même preprocessing 640."""
        if not self.v2_available or not self.v5_available:
            self.skipTest("Checkpoints absents")
        regressions: list[str] = []
        for case_id in VAL_IDS:
            _, r_v2 = self._run_v2_on_640(case_id)
            _, r_v5 = self._run_v5(case_id)
            assert r_v2.detection and r_v5.detection
            v2_map = {lm["name"]: lm for lm in r_v2.detection.refined_landmarks}
            v5_map = {lm["name"]: lm for lm in r_v5.detection.refined_landmarks}
            for name in MVP_LANDMARK_NAMES:
                if name not in v2_map or name not in v5_map:
                    regressions.append(f"{case_id} {name}: missing")
                    continue
                dx = abs(v2_map[name]["x"] - v5_map[name]["x"])
                dy = abs(v2_map[name]["y"] - v5_map[name]["y"])
                if dx > KP_TOL_ORIG or dy > KP_TOL_ORIG:
                    regressions.append(
                        f"{case_id} {name}: delta=({dx:.2f},{dy:.2f})"
                    )
        if regressions:
            self.fail("Régressions KP 0–13 @640:\n" + "\n".join(regressions))

    def test_geometry_at_640(self) -> None:
        """VCE/Tönnis/CCD identiques V2 vs V5 sur preprocessing 640."""
        if not self.v2_available or not self.v5_available:
            self.skipTest("Checkpoints absents")
        for case_id in VAL_IDS:
            with self.subTest(case_id=case_id):
                _, r_v2 = self._run_v2_on_640(case_id)
                _, r_v5 = self._run_v5(case_id)
                assert r_v2.measurements and r_v5.measurements
                for side_attr in ("right", "left"):
                    s2 = getattr(r_v2.measurements, side_attr)
                    s5 = getattr(r_v5.measurements, side_attr)
                    for measure_attr in ("vce", "tonnis", "ccd"):
                        m2 = getattr(s2, measure_attr)
                        m5 = getattr(s5, measure_attr)
                        self.assertEqual(m2.available, m5.available)
                        if m2.available and m5.available:
                            self.assertAlmostEqual(m2.value_deg, m5.value_deg, places=2)

    def test_v5_has_it_landmarks(self) -> None:
        if not self.v5_available:
            self.skipTest("V5 absent")
        for case_id in VAL_IDS:
            with self.subTest(case_id=case_id):
                raw = _load_val_image_bytes(case_id)
                r_v5 = run_measurement_pipeline(preprocess_image_v5(raw), detector=self.v5)
                assert r_v5.detection
                self.assertEqual(len(r_v5.detection.it_landmarks), 2)
                names = {item["name"] for item in r_v5.detection.it_landmarks}
                self.assertEqual(names, {"IT_R", "IT_L"})


if __name__ == "__main__":
    unittest.main()
