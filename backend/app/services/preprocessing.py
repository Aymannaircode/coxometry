"""Prétraitement d'image radiographique.

Pipeline neutre, sans aucune hypothèse médicale :

    Image (bytes)
        ↓ validation (format lisible, JPG/JPEG/PNG)
        ↓ chargement (Pillow)
        ↓ conversion en représentation standard (grayscale ou RGB)
        ↓ normalisation de taille configurable (proportions conservées)
        ↓ normalisation des pixels en float32 [0, 1]
        ↓ image + métadonnées prêtes pour le futur modèle IA

Ce module NE fait PAS :
- de détection de landmarks / d'IA / d'entraînement ;
- d'inversion gauche/droite ;
- de rotation automatique ;
- de correction anatomique ;
- d'augmentation de données.

Il ne lit ni ne modifie aucun dataset ni aucune annotation : il opère
uniquement sur les octets d'image fournis par l'appelant.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError

# Formats d'entrée acceptés (valeurs `PIL.Image.format`).
# JPG et JPEG sont tous deux reportés par Pillow comme "JPEG".
SUPPORTED_FORMATS = ("JPEG", "PNG")

ColorMode = str  # "grayscale" | "rgb"
_PIL_MODE = {"grayscale": "L", "rgb": "RGB"}


class PreprocessingError(ValueError):
    """Erreur de base du prétraitement."""


class UnreadableImageError(PreprocessingError):
    """Les octets fournis ne constituent pas une image décodable."""


class UnsupportedFormatError(PreprocessingError):
    """Le format de l'image n'est pas dans SUPPORTED_FORMATS."""


class EmptyImageError(PreprocessingError):
    """Aucune donnée d'image fournie."""


@dataclass(frozen=True)
class PreprocessConfig:
    """Paramètres de prétraitement (tous explicites, aucun défaut médical).

    - `target_size` : (largeur, hauteur) de sortie en pixels, ou `None` pour
      conserver la taille d'origine (aucun redimensionnement).
    - `color_mode` : "grayscale" (défaut, adapté aux radiographies) ou "rgb".
    - `normalize` : si vrai, pixels ramenés en float32 dans [0, 1] ; sinon
      uint8 [0, 255].
    - `pad_value` : valeur de remplissage des bandes de letterbox
      (0 = noir), appliquée uniquement pour conserver les proportions.
    """

    target_size: Optional[Tuple[int, int]] = None
    color_mode: ColorMode = "grayscale"
    normalize: bool = True
    pad_value: int = 0

    def __post_init__(self) -> None:
        if self.color_mode not in _PIL_MODE:
            raise PreprocessingError(
                f"color_mode invalide : {self.color_mode!r} (attendu 'grayscale' ou 'rgb')."
            )
        if self.target_size is not None:
            width, height = self.target_size
            if width <= 0 or height <= 0:
                raise PreprocessingError(
                    f"target_size doit être strictement positif, reçu {self.target_size!r}."
                )
        if not (0 <= self.pad_value <= 255):
            raise PreprocessingError(
                f"pad_value doit être dans [0, 255], reçu {self.pad_value!r}."
            )


@dataclass(frozen=True)
class PreprocessedImage:
    """Sortie standardisée destinée au futur modèle IA.

    `array` :
    - dtype float32 dans [0, 1] si `normalize=True`, sinon uint8 [0, 255] ;
    - forme `(H, W)` en grayscale, `(H, W, 3)` en RGB ;
    - convention pixels image : ligne 0 en haut, colonne 0 à gauche.

    Les champs de géométrie (`scale`, `pad_left`, `pad_top`) permettront plus
    tard de reprojeter des coordonnées de landmarks depuis l'image prétraitée
    vers l'image d'origine, sans aucune transformation implicite.
    """

    array: np.ndarray
    source_format: str
    color_mode: ColorMode
    original_size: Tuple[int, int]  # (largeur, hauteur)
    processed_size: Tuple[int, int]  # (largeur, hauteur)
    scale: float
    pad_left: int
    pad_top: int
    normalized: bool
    status: str = "ok"

    def to_metadata(self) -> Dict[str, object]:
        """Métadonnées JSON-sérialisables (sans le tableau de pixels)."""
        height = int(self.array.shape[0])
        width = int(self.array.shape[1])
        channels = 1 if self.array.ndim == 2 else int(self.array.shape[2])
        return {
            "status": self.status,
            "source_format": self.source_format,
            "color_mode": self.color_mode,
            "original_size": {"width": self.original_size[0], "height": self.original_size[1]},
            "processed_size": {"width": self.processed_size[0], "height": self.processed_size[1]},
            "array_shape": {"height": height, "width": width, "channels": channels},
            "dtype": str(self.array.dtype),
            "value_range": [0.0, 1.0] if self.normalized else [0, 255],
            "scale": self.scale,
            "padding": {"left": self.pad_left, "top": self.pad_top},
            "normalized": self.normalized,
        }


def _validate_and_open(image_bytes: bytes) -> Image.Image:
    """Valide et ouvre les octets. Lève une erreur explicite sinon."""
    if image_bytes is None or len(image_bytes) == 0:
        raise EmptyImageError("Aucune donnée d'image fournie (bytes vides).")

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
    except UnidentifiedImageError as exc:
        raise UnreadableImageError(
            "Image illisible : format non reconnu ou fichier corrompu."
        ) from exc
    except OSError as exc:
        raise UnreadableImageError(f"Image illisible : {exc}") from exc

    image_format = (image.format or "").upper()
    if image_format not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(
            f"Format non supporté : {image_format or 'inconnu'!r}. "
            f"Formats acceptés : JPG/JPEG, PNG."
        )
    return image


def _to_color_mode(image: Image.Image, color_mode: ColorMode) -> Image.Image:
    """Convertit vers grayscale ('L') ou RGB, en aplatissant l'alpha éventuel."""
    if image.mode in ("RGBA", "LA", "P"):
        # Aplati sur fond noir pour retirer l'alpha sans inventer d'information.
        image = image.convert("RGBA")
        background = Image.new("RGBA", image.size, (0, 0, 0, 255))
        image = Image.alpha_composite(background, image)
    return image.convert(_PIL_MODE[color_mode])


def _resize_keep_ratio(
    image: Image.Image, target_size: Tuple[int, int], pad_value: int
) -> Tuple[Image.Image, float, int, int]:
    """Redimensionne en conservant les proportions puis complète (letterbox).

    Retourne (image_letterbox, scale, pad_left, pad_top). Aucune déformation :
    l'échelle est uniforme sur les deux axes.
    """
    target_w, target_h = target_size
    orig_w, orig_h = image.size

    scale = min(target_w / orig_w, target_h / orig_h)
    new_w = max(1, round(orig_w * scale))
    new_h = max(1, round(orig_h * scale))

    resized = image.resize((new_w, new_h), Image.BILINEAR)

    if image.mode == "RGB":
        canvas_fill = (pad_value, pad_value, pad_value)
    else:
        canvas_fill = pad_value
    canvas = Image.new(image.mode, (target_w, target_h), canvas_fill)

    pad_left = (target_w - new_w) // 2
    pad_top = (target_h - new_h) // 2
    canvas.paste(resized, (pad_left, pad_top))
    return canvas, scale, pad_left, pad_top


def preprocess_image(
    image_bytes: bytes,
    config: Optional[PreprocessConfig] = None,
) -> PreprocessedImage:
    """Prétraite une image radiographique en une représentation standard.

    Étapes : validation → chargement → conversion couleur → redimensionnement
    proportionnel configurable → normalisation des pixels.

    Lève :
    - `EmptyImageError` si aucun octet ;
    - `UnreadableImageError` si l'image n'est pas décodable ;
    - `UnsupportedFormatError` si le format n'est pas JPG/JPEG/PNG.
    """
    config = config or PreprocessConfig()

    image = _validate_and_open(image_bytes)
    source_format = (image.format or "").upper()
    original_size = image.size  # (largeur, hauteur)

    image = _to_color_mode(image, config.color_mode)

    if config.target_size is not None:
        image, scale, pad_left, pad_top = _resize_keep_ratio(
            image, config.target_size, config.pad_value
        )
    else:
        scale, pad_left, pad_top = 1.0, 0, 0

    processed_size = image.size

    array = np.asarray(image)
    if config.normalize:
        array = array.astype(np.float32) / 255.0
    else:
        array = array.astype(np.uint8)

    return PreprocessedImage(
        array=array,
        source_format=source_format,
        color_mode=config.color_mode,
        original_size=original_size,
        processed_size=processed_size,
        scale=scale,
        pad_left=pad_left,
        pad_top=pad_top,
        normalized=config.normalize,
    )
