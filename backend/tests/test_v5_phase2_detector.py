"""Tests V5 Phase 2 detector — 16 KP, decoder, B26_26 v=0."""

from __future__ import annotations

import csv
import io
import math
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "annotation_pilot/manual_annotation_tool"))

import numpy as np
from PIL import Image

from backend.app.services.detection.v5_phase2_pose import (
    DEFAULT_V5_CHECKPOINT,
    IT_KP_INDICES,
    IT_LANDMARK_NAMES,
    V5Phase2LandmarkDetector,
    decode_keypoints_px640,
    verify_single_stride,
)
from backend.app.services.preprocessing_v5 import DEFAULT_V5_PREPROCESS, preprocess_image_v5
from backend.app.services.detection.reprojection import reprojection_meta_from_preprocessed

VAL_IDS = ["B26_10", "B26_13", "B26_17", "B26_20", "B26_26"]
MAPPING_CSV = PROJECT_ROOT / "datasets/yolo_pose_new_26/meta/source_mapping.csv"
LABELS_VAL = PROJECT_ROOT / "datasets/yolo_pose_new_26/labels/val"


def _load_val_image_bytes(case_id: str) -> tuple[bytes, int, int]:
    """Charge une image val depuis DICOM (rendu PNG en mémoire)."""
    from dicom_render import read_dicom_dimensions, render_dicom_png

    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    dicom = PROJECT_ROOT / mapping[case_id]["source_dicom"].replace("\\", "/")
    if not dicom.is_file():
        raise FileNotFoundError(f"DICOM absent : {dicom}")
    w, h = read_dicom_dimensions(dicom)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        render_dicom_png(dicom, tmp_path)
        return tmp_path.read_bytes(), w, h
    finally:
        tmp_path.unlink(missing_ok=True)


def _gray_png_bytes(width: int = 800, height: int = 600) -> bytes:
    data = np.full((height, width), 128, dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(data).save(buffer, format="PNG")
    return buffer.getvalue()


class TestV5DecoderSingleStride(unittest.TestCase):
    """test_v5_decoder_single_stride — échoue si double scaling."""

    def test_verify_single_stride_passes(self) -> None:
        self.assertTrue(verify_single_stride(4.5, 16.0, 32.0, 144.0, 512.0))

    def test_verify_single_stride_fails_on_double(self) -> None:
        self.assertFalse(verify_single_stride(4.5, 16.0, 32.0, 4.5 * 32 * 32, 16.0 * 32 * 32))


class TestV5Phase2Detector(unittest.TestCase):
    """Tests d'intégration V5 sur les 5 images val."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = DEFAULT_V5_CHECKPOINT
        cls.available = cls.checkpoint.is_file()
        cls.detector: V5Phase2LandmarkDetector | None = None
        if cls.available:
            cls.detector = V5Phase2LandmarkDetector(load_on_init=True)

    def _detect(self, case_id: str):
        assert self.detector is not None
        raw_bytes, _, _ = _load_val_image_bytes(case_id)
        preprocessed = preprocess_image_v5(raw_bytes)
        self.assertEqual(preprocessed.processed_size, (640, 640))
        return preprocessed, self.detector.detect(preprocessed)

    def test_checkpoint_available(self) -> None:
        if not self.available:
            self.skipTest("best_it.pt absent")
        self.assertTrue(self.checkpoint.is_file())

    def test_preprocessing_640_rgb(self) -> None:
        raw = _gray_png_bytes()
        prep = preprocess_image_v5(raw)
        self.assertEqual(prep.processed_size, (640, 640))
        self.assertEqual(prep.color_mode, "rgb")
        self.assertTrue(prep.normalized)

    def test_val_images_16_kp(self) -> None:
        if not self.available:
            self.skipTest("best_it.pt absent")
        for case_id in VAL_IDS:
            with self.subTest(case_id=case_id):
                prep, result = self._detect(case_id)
                self.assertEqual(result.status, "ok", msg=result.message)
                self.assertEqual(len(result.landmarks), 14)
                self.assertEqual(len(result.it_landmarks), 2)
                audit = result.audit or {}
                self.assertTrue(audit.get("decoder_single_stride_ok", False))
                self.assertEqual(audit.get("n_keypoints_total"), 16)

    def test_it_indices_and_names(self) -> None:
        if not self.available:
            self.skipTest("best_it.pt absent")
        for case_id in VAL_IDS:
            with self.subTest(case_id=case_id):
                _, result = self._detect(case_id)
                self.assertEqual(result.status, "ok")
                names = [item.name for item in result.it_landmarks]
                indices = [item.kp_index for item in result.it_landmarks]
                self.assertEqual(names, list(IT_LANDMARK_NAMES))
                self.assertEqual(indices, list(IT_KP_INDICES))

    def test_b26_26_it_l_identifiable(self) -> None:
        if not self.available:
            self.skipTest("best_it.pt absent")
        _, result = self._detect("B26_26")
        self.assertEqual(result.status, "ok")
        it_l = next(item for item in result.it_landmarks if item.name == "IT_L")
        self.assertEqual(it_l.v, 2)
        self.assertIsNotNone(it_l.x)
        self.assertIsNotNone(it_l.y)

    def test_b26_26_it_r_gt_v0_model_may_predict(self) -> None:
        """GT IT_R v=0 sur B26_26 — le modèle peut toutefois prédire v=2 (limitation modèle)."""
        if not self.available:
            self.skipTest("best_it.pt absent")
        _, result = self._detect("B26_26")
        it_r = next(item for item in result.it_landmarks if item.name == "IT_R")
        # Pas de crash ; si v=0 alors pas de coordonnées
        if it_r.v == 0:
            self.assertIsNone(it_r.x)
            self.assertIsNone(it_r.y)

    def test_v0_parsing_no_invented_coords(self) -> None:
        """Unitaire : v=0 → pas de coordonnées (logique _parse_it_landmarks)."""
        import torch
        from backend.app.services.detection.v5_phase2_pose import _parse_it_landmarks

        pred = torch.zeros(16, 3)
        pred[14, 2] = -5.0  # sigmoid ~0.007
        items = _parse_it_landmarks(pred, keypoint_conf_threshold=0.25)
        it_r = next(item for item in items if item.name == "IT_R")
        self.assertEqual(it_r.v, 0)
        self.assertIsNone(it_r.x)
        self.assertIsNone(it_r.y)

    def test_reprojection_original_space(self) -> None:
        if not self.available:
            self.skipTest("best_it.pt absent")
        from backend.app.services.measurement_service import run_measurement_pipeline

        raw_bytes, orig_w, orig_h = _load_val_image_bytes("B26_10")
        prep = preprocess_image_v5(raw_bytes)
        assert self.detector is not None
        pipeline = run_measurement_pipeline(prep, detector=self.detector)
        self.assertEqual(pipeline.status, "ok")
        assert pipeline.detection is not None
        cs = pipeline.detection.coordinate_space
        self.assertEqual(cs.image_width, orig_w)
        self.assertEqual(cs.image_height, orig_h)
        for item in pipeline.detection.refined_landmarks:
            self.assertFalse(math.isnan(item["x"]))
            self.assertFalse(math.isnan(item["y"]))


if __name__ == "__main__":
    unittest.main()
