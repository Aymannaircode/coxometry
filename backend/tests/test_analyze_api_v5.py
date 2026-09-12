"""Tests API HTTP /analyze avec MODEL_VERSION v2 et v5_phase2."""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "annotation_pilot/manual_annotation_tool"))

from fastapi.testclient import TestClient

from backend.app.services.detection.v5_phase2_pose import DEFAULT_V5_CHECKPOINT
from backend.main import app

MAPPING_CSV = PROJECT_ROOT / "datasets/yolo_pose_new_26/meta/source_mapping.csv"


def _load_b26_10_bytes() -> bytes:
    from dicom_render import render_dicom_png

    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    dicom = PROJECT_ROOT / mapping["B26_10"]["source_dicom"].replace("\\", "/")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        render_dicom_png(dicom, tmp_path)
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)


class TestAnalyzeAPIV5(unittest.TestCase):
    """POST /analyze avec MODEL_VERSION explicite."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        cls.image_bytes = _load_b26_10_bytes()
        cls.v5_available = DEFAULT_V5_CHECKPOINT.is_file()

    def test_analyze_v2_default(self) -> None:
        old = os.environ.pop("MODEL_VERSION", None)
        try:
            response = self.client.post(
                "/analyze",
                files={"file": ("B26_10.png", self.image_bytes, "image/png")},
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            if data["status"] == "ok":
                self.assertEqual(data.get("model_version", "v2"), "v2")
                self.assertEqual(data["detection"].get("it_landmarks", []), [])
        finally:
            if old is not None:
                os.environ["MODEL_VERSION"] = old

    def test_analyze_v5_phase2(self) -> None:
        if not self.v5_available:
            self.skipTest("best_it.pt absent")
        old = os.environ.get("MODEL_VERSION")
        os.environ["MODEL_VERSION"] = "v5_phase2"
        try:
            response = self.client.post(
                "/analyze",
                files={"file": ("B26_10.png", self.image_bytes, "image/png")},
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ok", msg=data)
            self.assertEqual(data["model_version"], "v5_phase2")
            it_lm = data["detection"]["it_landmarks"]
            self.assertEqual(len(it_lm), 2)
            names = {item["name"] for item in it_lm}
            self.assertEqual(names, {"IT_R", "IT_L"})
            # JSON sérialisable
            import json
            json.dumps(data)
        finally:
            if old is None:
                os.environ.pop("MODEL_VERSION", None)
            else:
                os.environ["MODEL_VERSION"] = old


if __name__ == "__main__":
    unittest.main()
