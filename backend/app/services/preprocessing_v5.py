"""Prétraitement dédié V5 Phase 2 — entrée 640×640 RGB (pipeline validé en audit).

Réutilise ``preprocessing.preprocess_image`` sans modifier le module V2.
Le backend V2 conserve ``target_size=(512, 512)`` en grayscale.
V5 Phase 2 utilise ``target_size=(640, 640)`` en RGB, letterbox, float32 [0, 1].
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from .preprocessing import PreprocessConfig, PreprocessedImage, preprocess_image

# Aligné sur v5_phase2_training_config.yaml (imgsz=640) et l'audit checkpoint.
V5_IMGSZ = 640

DEFAULT_V5_PREPROCESS = PreprocessConfig(
    target_size=(V5_IMGSZ, V5_IMGSZ),
    color_mode="rgb",
    normalize=True,
    pad_value=0,
)


def preprocess_image_v5(
    image_bytes: bytes,
    config: Optional[PreprocessConfig] = None,
) -> PreprocessedImage:
    """Prétraite une image pour l'inférence V5 Phase 2 (640×640 RGB letterbox)."""
    return preprocess_image(image_bytes, config or DEFAULT_V5_PREPROCESS)


def preprocessed_to_rgb_chw_float(image: PreprocessedImage) -> np.ndarray:
    """Convertit ``PreprocessedImage`` en tenseur NCHW float32 [0, 1] pour V5."""
    array = image.array
    if array.ndim == 2:
        array = np.stack([array, array, array], axis=-1)
    elif array.ndim == 3 and array.shape[2] == 1:
        array = np.repeat(array, 3, axis=2)
    if image.normalized:
        chw = np.transpose(array.astype(np.float32), (2, 0, 1))
    else:
        chw = np.transpose(array.astype(np.float32) / 255.0, (2, 0, 1))
    return chw
