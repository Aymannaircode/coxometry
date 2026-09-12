"""SHA256 helpers for source bytes, de-identified bytes, and PixelData."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pixel_array_bytes(dataset) -> bytes:
    array = np.ascontiguousarray(dataset.pixel_array)
    return array.tobytes()


def sha256_pixels(dataset) -> str:
    return sha256_bytes(pixel_array_bytes(dataset))
