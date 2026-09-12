"""Tests QC anatomique IT V5 Phase 2."""

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

from backend.app.services.detection.v5_it_qc import (
    assess_it_landmarks_qc,
)
from backend.app.services.detection.v5_phase2_pose import (
    DEFAULT_V5_CHECKPOINT,
    V5Phase2LandmarkDetector,
)
from backend.app.services.measurement_service import run_measurement_pipeline
from backend.app.services.preprocessing_v5 import preprocess_image_v5

VAL_IDS = ["B26_10", "B26_13", "B26_17", "B26_20", "B26_26"]
MAPPING_CSV = PROJECT_ROOT / "datasets/yolo_pose_new_26/meta/source_mapping.csv"


def _mvp_landmarks_baseline() -> list[dict]:
    """Repères pelviens plausibles pour tests unitaires (espace original)."""
    return [
        {"name": "TD_R", "x": 1200.0, "y": 1800.0},
        {"name": "TD_L", "x": 1900.0, "y": 1850.0},
        {"name": "FHC_R", "x": 900.0, "y": 1200.0},
        {"name": "FHC_L", "x": 2100.0, "y": 1250.0},
        {"name": "FSD_R", "x": 800.0, "y": 2280.0},
        {"name": "FSD_L", "x": 2050.0, "y": 2220.0},
    ]


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


class TestITQCUnit(unittest.TestCase):
    """Tests unitaires des règles QC."""

    def test_v0_unavailable(self) -> None:
        results = assess_it_landmarks_qc(
            [{"name": "IT_R", "v": 0, "x": None, "y": None, "confidence": 0.1}],
            image_width=3000,
            image_height=2600,
            mvp_landmarks=_mvp_landmarks_baseline(),
        )
        self.assertEqual(results["IT_R"].quality, "unavailable")
        self.assertIn("model_v0", results["IT_R"].quality_reasons)

    def test_out_of_bounds_unavailable(self) -> None:
        results = assess_it_landmarks_qc(
            [
                {
                    "name": "IT_R",
                    "v": 2,
                    "x": -50.0,
                    "y": 2200.0,
                    "confidence": 0.9,
                }
            ],
            image_width=3000,
            image_height=2600,
            mvp_landmarks=_mvp_landmarks_baseline(),
        )
        self.assertEqual(results["IT_R"].quality, "unavailable")
        self.assertIn("out_of_image_bounds", results["IT_R"].quality_reasons)

    def test_wrong_side_unavailable(self) -> None:
        """IT_R sur le côté gauche de l'image (côté patient L)."""
        results = assess_it_landmarks_qc(
            [
                {
                    "name": "IT_R",
                    "v": 2,
                    "x": 2000.0,
                    "y": 2200.0,
                    "confidence": 0.8,
                }
            ],
            image_width=3000,
            image_height=2600,
            mvp_landmarks=_mvp_landmarks_baseline(),
        )
        self.assertEqual(results["IT_R"].quality, "unavailable")
        self.assertIn("wrong_patient_side", results["IT_R"].quality_reasons)

    def test_insufficient_caudal_review(self) -> None:
        results = assess_it_landmarks_qc(
            [
                {
                    "name": "IT_R",
                    "v": 2,
                    "x": 1000.0,
                    "y": 1810.0,
                    "confidence": 0.7,
                }
            ],
            image_width=3000,
            image_height=2600,
            mvp_landmarks=_mvp_landmarks_baseline(),
        )
        self.assertEqual(results["IT_R"].quality, "review")
        self.assertTrue(
            any(
                r in results["IT_R"].quality_reasons
                for r in ("insufficient_caudal_vs_teardrop", "insufficient_caudal_vs_fhc")
            )
        )

    def test_low_confidence_review(self) -> None:
        results = assess_it_landmarks_qc(
            [
                {
                    "name": "IT_L",
                    "v": 2,
                    "x": 2100.0,
                    "y": 2200.0,
                    "confidence": 0.30,
                }
            ],
            image_width=3000,
            image_height=2600,
            mvp_landmarks=_mvp_landmarks_baseline(),
        )
        self.assertEqual(results["IT_L"].quality, "review")
        self.assertIn("low_model_confidence", results["IT_L"].quality_reasons)

    def test_high_confidence_marginal_it_fsd_review(self) -> None:
        """Sur-confiance avec IT trop proche du FSD (motif B26_26-like)."""
        results = assess_it_landmarks_qc(
            [
                {
                    "name": "IT_R",
                    "v": 2,
                    "x": 1000.0,
                    "y": 2270.0,
                    "confidence": 0.85,
                }
            ],
            image_width=3000,
            image_height=2600,
            mvp_landmarks=_mvp_landmarks_baseline(),
        )
        self.assertEqual(results["IT_R"].quality, "review")
        self.assertIn("high_confidence_marginal_it_fsd", results["IT_R"].quality_reasons)

    def test_bilateral_vertical_asymmetry_review(self) -> None:
        results = assess_it_landmarks_qc(
            [
                {"name": "IT_R", "v": 2, "x": 1000.0, "y": 2100.0, "confidence": 0.7},
                {"name": "IT_L", "v": 2, "x": 2100.0, "y": 2400.0, "confidence": 0.7},
            ],
            image_width=3000,
            image_height=2600,
            mvp_landmarks=_mvp_landmarks_baseline(),
        )
        self.assertEqual(results["IT_R"].quality, "review")
        self.assertIn("bilateral_vertical_asymmetry", results["IT_R"].quality_reasons)

    def test_bilateral_order_violation_unavailable(self) -> None:
        """IT_R à droite de IT_L sur l'image — ordre bilatéral impossible."""
        results = assess_it_landmarks_qc(
            [
                {"name": "IT_R", "v": 2, "x": 2000.0, "y": 2200.0, "confidence": 0.7},
                {"name": "IT_L", "v": 2, "x": 1200.0, "y": 2200.0, "confidence": 0.7},
            ],
            image_width=3000,
            image_height=2600,
            mvp_landmarks=_mvp_landmarks_baseline(),
        )
        self.assertEqual(results["IT_R"].quality, "unavailable")
        self.assertTrue(
            "bilateral_order_violation" in results["IT_R"].quality_reasons
            or "wrong_patient_side" in results["IT_R"].quality_reasons
        )

    def test_plausible_accept(self) -> None:
        results = assess_it_landmarks_qc(
            [
                {"name": "IT_R", "v": 2, "x": 1000.0, "y": 2200.0, "confidence": 0.72},
                {"name": "IT_L", "v": 2, "x": 2100.0, "y": 2180.0, "confidence": 0.75},
            ],
            image_width=3000,
            image_height=2600,
            mvp_landmarks=_mvp_landmarks_baseline(),
        )
        self.assertEqual(results["IT_R"].quality, "accept")
        self.assertEqual(results["IT_L"].quality, "accept")


class TestITQCIntegration(unittest.TestCase):
    """Tests intégration pipeline + 5 images val."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.available = DEFAULT_V5_CHECKPOINT.is_file()
        cls.detector: V5Phase2LandmarkDetector | None = None
        if cls.available:
            cls.detector = V5Phase2LandmarkDetector(load_on_init=True)

    def _pipeline(self, case_id: str):
        assert self.detector is not None
        prep = preprocess_image_v5(_load_val_image_bytes(case_id))
        return run_measurement_pipeline(prep, detector=self.detector)

    def test_v2_no_qc_fields(self) -> None:
        from backend.app.services.detection.yolo_pose import YoloPoseLandmarkDetector
        from backend.app.services.preprocessing import PreprocessConfig, preprocess_image

        prep = preprocess_image(
            _load_val_image_bytes("B26_10"), PreprocessConfig(target_size=(512, 512))
        )
        result = run_measurement_pipeline(prep, detector=YoloPoseLandmarkDetector())
        self.assertEqual(result.status, "ok")
        assert result.detection is not None
        self.assertEqual(result.detection.it_landmarks, [])
        self.assertNotIn("it_landmarks_qc", result.audit)

    def test_pipeline_attaches_quality_fields(self) -> None:
        if not self.available:
            self.skipTest("best_it.pt absent")
        result = self._pipeline("B26_10")
        self.assertEqual(result.status, "ok")
        assert result.detection is not None
        for item in result.detection.it_landmarks:
            self.assertIn("quality", item)
            self.assertIn("quality_reasons", item)
            self.assertIn(item["quality"], ("accept", "review", "unavailable"))
        self.assertIn("it_landmarks_qc", result.audit)

    def test_normal_validation_cases_accept(self) -> None:
        if not self.available:
            self.skipTest("best_it.pt absent")
        for case_id in ("B26_10", "B26_13", "B26_17", "B26_20"):
            with self.subTest(case_id=case_id):
                result = self._pipeline(case_id)
                assert result.detection is not None
                for item in result.detection.it_landmarks:
                    if item["v"] == 2:
                        self.assertEqual(
                            item["quality"],
                            "accept",
                            msg=f"{case_id} {item['name']}: {item.get('quality_reasons')}",
                        )

    def test_b26_26_it_r_not_accept(self) -> None:
        """IT_R B26_26 : prédiction brute conservée, fiabilité non ACCEPT."""
        if not self.available:
            self.skipTest("best_it.pt absent")
        result = self._pipeline("B26_26")
        assert result.detection is not None
        it_r = next(x for x in result.detection.it_landmarks if x["name"] == "IT_R")
        self.assertEqual(it_r["v"], 2)
        self.assertIsNotNone(it_r["x"])
        self.assertIsNotNone(it_r["y"])
        self.assertGreater(it_r.get("confidence") or 0, 0.75)
        self.assertIn(it_r["quality"], ("review", "unavailable"))

    def test_b26_26_it_l_usable(self) -> None:
        if not self.available:
            self.skipTest("best_it.pt absent")
        result = self._pipeline("B26_26")
        assert result.detection is not None
        it_l = next(x for x in result.detection.it_landmarks if x["name"] == "IT_L")
        self.assertEqual(it_l["quality"], "accept")
        self.assertEqual(it_l["v"], 2)


if __name__ == "__main__":
    unittest.main()
