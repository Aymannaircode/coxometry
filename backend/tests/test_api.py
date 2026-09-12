"""Tests HTTP de l'API FastAPI — aucune image médicale, aucun landmark inventé."""

from __future__ import annotations

import io
import math
import unittest

import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from backend.main import app


def _vce_asl(fhc, target_deg=25.0, radius=100.0):
    lateral = (-1.0, 0.0)
    cranial = (0.0, -1.0)
    theta = math.radians(target_deg)
    return (
        fhc[0] + radius * (math.sin(theta) * lateral[0] + math.cos(theta) * cranial[0]),
        fhc[1] + radius * (math.sin(theta) * lateral[1] + math.cos(theta) * cranial[1]),
    )


def _encode_gray(width: int, height: int, fmt: str = "PNG") -> bytes:
    """Image synthétique neutre (aucune donnée médicale)."""
    data = np.full((height, width), 128, dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(data).save(buffer, format=fmt)
    return buffer.getvalue()


class TestHealth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertIn(body.get("model_version"), ("v2", "v5_phase2"))


class TestPostMeasurements(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_image_mode_not_implemented(self):
        response = self.client.post("/measurements", json={"mode": "image"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_implemented")
        self.assertEqual(body["source"], "image")
        self.assertIsNone(body["sides"])
        self.assertIn("pas encore", body["message"].lower())

    def test_landmarks_mode_ok_synthetic(self):
        fhc = (200.0, 400.0)
        asl = _vce_asl(fhc, 25.0)
        payload = {
            "mode": "landmarks",
            "sides": ["R"],
            "landmarks": [
                {"name": "TD_R", "x": 300.0, "y": 500.0, "v": 2},
                {"name": "TD_L", "x": 500.0, "y": 500.0, "v": 2},
                {"name": "FHC_R", "x": fhc[0], "y": fhc[1], "v": 2},
                {"name": "ASL_R", "x": asl[0], "y": asl[1], "v": 2},
            ],
        }
        response = self.client.post("/measurements", json=payload)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["source"], "manual_landmarks")
        self.assertTrue(body["sides"]["R"]["vce"]["available"])
        self.assertAlmostEqual(body["sides"]["R"]["vce"]["value_deg"], 25.0, places=5)

    def test_landmarks_mode_missing_payload_422(self):
        response = self.client.post(
            "/measurements",
            json={"mode": "landmarks"},
        )
        self.assertEqual(response.status_code, 422)

    def test_default_both_sides(self):
        payload = {
            "mode": "landmarks",
            "landmarks": [
                {"name": "TD_R", "x": 300.0, "y": 500.0, "v": 2},
                {"name": "TD_L", "x": 500.0, "y": 500.0, "v": 2},
            ],
        }
        response = self.client.post("/measurements", json=payload)
        self.assertEqual(response.status_code, 200)
        sides = response.json()["sides"]
        self.assertIn("R", sides)
        self.assertIn("L", sides)


class TestPostMeasurementsUpload(unittest.TestCase):
    """Upload multipart : validation, formats invalides, détecteur stub."""

    def setUp(self):
        self.client = TestClient(app)

    def test_upload_png_not_implemented(self):
        png = _encode_gray(64, 48, "PNG")
        response = self.client.post(
            "/measurements",
            files={"file": ("radio.png", png, "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_implemented")
        self.assertEqual(body["mode"], "image")
        self.assertEqual(body["source"], "image")
        self.assertIsNone(body["sides"])
        self.assertIn("aucune coordonnée", body["message"].lower())

    def test_upload_jpeg_not_implemented(self):
        jpeg = _encode_gray(64, 48, "JPEG")
        response = self.client.post(
            "/measurements",
            files={"file": ("radio.jpg", jpeg, "image/jpeg")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "not_implemented")
        self.assertIsNone(body["sides"])

    def test_upload_image_field_alias(self):
        png = _encode_gray(32, 32, "PNG")
        response = self.client.post(
            "/measurements",
            files={"image": ("x.png", png, "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "not_implemented")

    def test_upload_missing_file_422(self):
        # Multipart sans champ file/image → 422 explicite.
        response = self.client.post(
            "/measurements",
            files={"notes": ("notes.txt", b"pas une image", "text/plain")},
        )
        self.assertEqual(response.status_code, 422)

    def test_upload_invalid_bytes_error(self):
        response = self.client.post(
            "/measurements",
            files={"file": ("bad.png", b"ceci n'est pas une image", "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["source"], "image")
        self.assertIsNone(body["sides"])
        self.assertIn("illisible", body["message"].lower())

    def test_upload_unsupported_format_bmp(self):
        buffer = io.BytesIO()
        Image.fromarray(np.full((32, 32), 90, dtype=np.uint8)).save(buffer, format="BMP")
        response = self.client.post(
            "/measurements",
            files={"file": ("radio.bmp", buffer.getvalue(), "image/bmp")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "error")
        self.assertIsNone(body["sides"])
        self.assertIn("non supporté", body["message"].lower())

    def test_upload_empty_file_error(self):
        response = self.client.post(
            "/measurements",
            files={"file": ("empty.png", b"", "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "error")
        self.assertIsNone(body["sides"])


if __name__ == "__main__":
    unittest.main()
