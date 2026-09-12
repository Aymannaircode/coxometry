"""Tests du prétraitement d'image.

Toutes les images sont **synthétiques**, générées en mémoire (aucune donnée
médicale, aucun dataset, aucune annotation). On vérifie la validation, la
conversion, la normalisation de taille avec conservation des proportions et
les erreurs explicites.
"""

from __future__ import annotations

import io
import unittest

import numpy as np
from PIL import Image

from backend.app.services.preprocessing import (
    EmptyImageError,
    PreprocessConfig,
    PreprocessingError,
    PreprocessedImage,
    UnreadableImageError,
    UnsupportedFormatError,
    preprocess_image,
)


def _encode(image: Image.Image, fmt: str) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def _rgb_image(width: int, height: int) -> Image.Image:
    data = np.zeros((height, width, 3), dtype=np.uint8)
    data[..., 0] = 200  # canal rouge constant (motif neutre, non médical)
    return Image.fromarray(data)


def _gray_image(width: int, height: int, value: int = 128) -> Image.Image:
    data = np.full((height, width), value, dtype=np.uint8)
    return Image.fromarray(data)


class TestValidation(unittest.TestCase):
    def test_valid_png(self):
        result = preprocess_image(_encode(_gray_image(64, 48), "PNG"))
        self.assertIsInstance(result, PreprocessedImage)
        self.assertEqual(result.source_format, "PNG")
        self.assertEqual(result.status, "ok")

    def test_valid_jpeg(self):
        result = preprocess_image(_encode(_rgb_image(64, 48), "JPEG"))
        self.assertEqual(result.source_format, "JPEG")

    def test_empty_bytes(self):
        with self.assertRaises(EmptyImageError):
            preprocess_image(b"")

    def test_unreadable_bytes(self):
        with self.assertRaises(UnreadableImageError):
            preprocess_image(b"ceci n'est pas une image")

    def test_unsupported_format(self):
        # BMP est décodable par Pillow mais hors des formats acceptés.
        buffer = io.BytesIO()
        _gray_image(32, 32).save(buffer, format="BMP")
        with self.assertRaises(UnsupportedFormatError):
            preprocess_image(buffer.getvalue())


class TestColorModes(unittest.TestCase):
    def test_grayscale_output_is_2d(self):
        result = preprocess_image(
            _encode(_gray_image(40, 30), "PNG"),
            PreprocessConfig(color_mode="grayscale"),
        )
        self.assertEqual(result.array.ndim, 2)
        self.assertEqual(result.color_mode, "grayscale")

    def test_rgb_input_to_grayscale(self):
        result = preprocess_image(
            _encode(_rgb_image(40, 30), "PNG"),
            PreprocessConfig(color_mode="grayscale"),
        )
        self.assertEqual(result.array.ndim, 2)

    def test_rgb_output_is_3d(self):
        result = preprocess_image(
            _encode(_rgb_image(40, 30), "PNG"),
            PreprocessConfig(color_mode="rgb"),
        )
        self.assertEqual(result.array.ndim, 3)
        self.assertEqual(result.array.shape[2], 3)

    def test_grayscale_input_to_rgb(self):
        result = preprocess_image(
            _encode(_gray_image(40, 30), "PNG"),
            PreprocessConfig(color_mode="rgb"),
        )
        self.assertEqual(result.array.shape[2], 3)


class TestNormalization(unittest.TestCase):
    def test_normalized_float_range(self):
        result = preprocess_image(
            _encode(_gray_image(20, 20, value=255), "PNG"),
            PreprocessConfig(normalize=True),
        )
        self.assertEqual(result.array.dtype, np.float32)
        self.assertLessEqual(result.array.max(), 1.0)
        self.assertGreaterEqual(result.array.min(), 0.0)

    def test_unnormalized_uint8(self):
        result = preprocess_image(
            _encode(_gray_image(20, 20), "PNG"),
            PreprocessConfig(normalize=False),
        )
        self.assertEqual(result.array.dtype, np.uint8)


class TestAspectRatio(unittest.TestCase):
    def test_preserves_ratio_with_padding(self):
        # Image 100x50 (2:1) vers cible carrée 200x200.
        result = preprocess_image(
            _encode(_gray_image(100, 50), "PNG"),
            PreprocessConfig(target_size=(200, 200)),
        )
        self.assertEqual(result.processed_size, (200, 200))
        self.assertEqual(result.array.shape[:2], (200, 200))
        # scale = min(200/100, 200/50) = 2.0 ; hauteur utile 100 -> pad vertical.
        self.assertAlmostEqual(result.scale, 2.0, places=6)
        self.assertEqual(result.pad_left, 0)
        self.assertEqual(result.pad_top, (200 - 100) // 2)

    def test_no_resize_when_target_none(self):
        result = preprocess_image(
            _encode(_gray_image(77, 33), "PNG"),
            PreprocessConfig(target_size=None),
        )
        self.assertEqual(result.original_size, (77, 33))
        self.assertEqual(result.processed_size, (77, 33))
        self.assertEqual(result.scale, 1.0)

    def test_metadata_shape_consistency(self):
        result = preprocess_image(
            _encode(_rgb_image(120, 60), "PNG"),
            PreprocessConfig(target_size=(64, 64), color_mode="rgb"),
        )
        meta = result.to_metadata()
        self.assertEqual(meta["array_shape"]["height"], 64)
        self.assertEqual(meta["array_shape"]["width"], 64)
        self.assertEqual(meta["array_shape"]["channels"], 3)
        self.assertEqual(meta["original_size"], {"width": 120, "height": 60})


class TestConfigErrors(unittest.TestCase):
    def test_invalid_color_mode(self):
        with self.assertRaises(PreprocessingError):
            PreprocessConfig(color_mode="cmyk")

    def test_invalid_target_size(self):
        with self.assertRaises(PreprocessingError):
            PreprocessConfig(target_size=(0, 100))

    def test_invalid_pad_value(self):
        with self.assertRaises(PreprocessingError):
            PreprocessConfig(pad_value=999)


if __name__ == "__main__":
    unittest.main()
