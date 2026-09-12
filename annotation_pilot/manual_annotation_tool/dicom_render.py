"""Conversion DICOM → PNG locale pour l'affichage navigateur (cache uniquement).

Les fichiers DICOM originaux dans bassin/a_annoter/ ne sont jamais modifiés.
Le navigateur ne peut pas afficher le DICOM directement ; cette couche produit
une PNG 1:1 (mêmes dimensions pixel) avec fenêtrage DICOM pour l'annotation.
"""

from __future__ import annotations

from pathlib import Path


def _require_render_deps() -> tuple[object, object, object]:
    try:
        import numpy as np
        import pydicom
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - message utilisateur
        raise RuntimeError(
            "Le mode new_26 nécessite pydicom, numpy et Pillow. "
            "Lancez le serveur avec le Python du venv projet : "
            ".venv\\Scripts\\python.exe server.py --dataset new_26"
        ) from exc
    return np, pydicom, Image


def _window_to_uint8(array, window_center: float, window_width: float):
    np, _, _ = _require_render_deps()
    low = window_center - window_width / 2
    high = window_center + window_width / 2
    clipped = np.clip(array.astype(np.float32), low, high)
    scaled = ((clipped - low) / max(high - low, 1.0) * 255.0).astype(np.uint8)
    return scaled


def read_dicom_dimensions(dicom_path: Path) -> tuple[int, int]:
    _, pydicom, _ = _require_render_deps()
    dataset = pydicom.dcmread(str(dicom_path), force=True)
    rows = int(getattr(dataset, "Rows", 0))
    cols = int(getattr(dataset, "Columns", 0))
    if rows <= 0 or cols <= 0:
        raise RuntimeError(f"Dimensions DICOM invalides : {dicom_path.name}")
    return cols, rows


def render_dicom_png(dicom_path: Path, png_path: Path) -> tuple[int, int]:
    """Décode un DICOM et écrit une PNG 8 bits, retourne (width, height)."""
    np, pydicom, Image = _require_render_deps()
    dataset = pydicom.dcmread(str(dicom_path), force=True)
    pixels = dataset.pixel_array.astype(np.float32)
    rows, cols = pixels.shape[:2]

    window_center = getattr(dataset, "WindowCenter", None)
    window_width = getattr(dataset, "WindowWidth", None)
    if window_center is not None and window_width is not None:
        wc = float(window_center)
        ww = float(window_width)
    else:
        wc = float(np.mean(pixels))
        ww = float(np.std(pixels) * 4.0)

    image8 = _window_to_uint8(pixels, wc, ww)
    png_path.parent.mkdir(parents=True, exist_ok=True)

    temporary = png_path.with_suffix(".png.part")
    Image.fromarray(image8).save(temporary, format="PNG", optimize=True)
    temporary.replace(png_path)
    return cols, rows


def ensure_display_png(
    dicom_path: Path,
    png_path: Path,
    *,
    force: bool = False,
) -> Path:
    """Retourne le chemin PNG, en régénérant le cache si le DICOM est plus récent."""
    if not dicom_path.is_file():
        raise FileNotFoundError(f"DICOM introuvable : {dicom_path}")

    if (
        not force
        and png_path.is_file()
        and png_path.stat().st_mtime >= dicom_path.stat().st_mtime
    ):
        return png_path

    render_dicom_png(dicom_path, png_path)
    return png_path
