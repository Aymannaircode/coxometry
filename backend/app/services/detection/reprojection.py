"""Reprojection des landmarks : image prétraitée → image originale.

Transformée inverse du letterbox appliqué par `preprocessing._resize_keep_ratio` :

    x_resized = x_prep - pad_left
    y_resized = y_prep - pad_top
    x_orig    = x_resized / scale
    y_orig    = y_resized / scale

Seuls `scale`, `pad_left`, `pad_top` et `original_size` sont utilisés.
Aucune rotation, inversion ou correction anatomique.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from ..preprocessing import PreprocessedImage
from .base import DetectedLandmark, validate_detected_landmarks


class ReprojectionError(ValueError):
    """Métadonnées de reprojection invalides ou incohérentes."""


@dataclass(frozen=True)
class ReprojectionMeta:
    """Paramètres géométriques issus du prétraitement."""

    scale: float
    pad_left: int
    pad_top: int
    original_size: Tuple[int, int]  # (largeur, hauteur)
    processed_size: Tuple[int, int]  # (largeur, hauteur)

    def __post_init__(self) -> None:
        orig_w, orig_h = self.original_size
        proc_w, proc_h = self.processed_size
        if self.scale <= 0:
            raise ReprojectionError(f"scale doit être > 0, reçu {self.scale!r}.")
        if orig_w <= 0 or orig_h <= 0:
            raise ReprojectionError(
                f"original_size invalide : {self.original_size!r}."
            )
        if proc_w <= 0 or proc_h <= 0:
            raise ReprojectionError(
                f"processed_size invalide : {self.processed_size!r}."
            )
        if self.pad_left < 0 or self.pad_top < 0:
            raise ReprojectionError(
                f"padding négatif interdit : left={self.pad_left}, top={self.pad_top}."
            )
        content_w, content_h = self.content_size
        if self.pad_left + content_w > proc_w or self.pad_top + content_h > proc_h:
            raise ReprojectionError(
                "La zone utile dépasse processed_size : métadonnées incohérentes."
            )

    @property
    def content_size(self) -> Tuple[int, int]:
        """Taille du contenu redimensionné (hors bandes de letterbox), en pixels."""
        orig_w, orig_h = self.original_size
        return max(1, round(orig_w * self.scale)), max(1, round(orig_h * self.scale))


@dataclass(frozen=True)
class ReprojectedLandmark:
    """Landmark dans l'espace de l'image **originale**."""

    name: str
    x: float
    y: float
    in_content_area: bool
    in_image_bounds: bool
    confidence: Optional[float] = None


def reprojection_meta_from_preprocessed(image: PreprocessedImage) -> ReprojectionMeta:
    """Construit les métadonnées de reprojection depuis `PreprocessedImage`."""
    return ReprojectionMeta(
        scale=image.scale,
        pad_left=image.pad_left,
        pad_top=image.pad_top,
        original_size=image.original_size,
        processed_size=image.processed_size,
    )


def reproject_point(
    x_prep: float,
    y_prep: float,
    meta: ReprojectionMeta,
) -> Tuple[float, float, bool, bool]:
    """Reprojette un point (x, y) prétraité vers l'image originale.

    Retourne (x_orig, y_orig, in_content_area, in_image_bounds).
    """
    content_w, content_h = meta.content_size
    x_resized = x_prep - meta.pad_left
    y_resized = y_prep - meta.pad_top

    in_content = (
        0.0 <= x_resized < content_w and 0.0 <= y_resized < content_h
    )

    x_orig = x_resized / meta.scale
    y_orig = y_resized / meta.scale

    orig_w, orig_h = meta.original_size
    in_bounds = 0.0 <= x_orig < orig_w and 0.0 <= y_orig < orig_h

    return x_orig, y_orig, in_content, in_bounds


def reproject_landmark(
    landmark: DetectedLandmark,
    meta: ReprojectionMeta,
) -> ReprojectedLandmark:
    """Reprojette un seul landmark détecté."""
    x_orig, y_orig, in_content, in_bounds = reproject_point(
        landmark.x, landmark.y, meta
    )
    return ReprojectedLandmark(
        name=landmark.name,
        x=x_orig,
        y=y_orig,
        in_content_area=in_content,
        in_image_bounds=in_bounds,
        confidence=landmark.confidence,
    )


def reproject_landmarks(
    landmarks: Sequence[DetectedLandmark],
    meta: ReprojectionMeta,
) -> Tuple[ReprojectedLandmark, ...]:
    """Reprojette une séquence de landmarks détectés."""
    validate_detected_landmarks(landmarks)
    return tuple(reproject_landmark(item, meta) for item in landmarks)
