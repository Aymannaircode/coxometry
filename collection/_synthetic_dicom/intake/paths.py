"""Refuse clinical trees before any DICOM read."""

from __future__ import annotations

from pathlib import Path

from .constants import FORBIDDEN_PATH_MARKERS, SYNTHETIC_MARKER


class ClinicalPathError(ValueError):
    """Raised when a path is outside the synthetic sandbox."""


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def assert_synthetic_sandbox(path: Path) -> Path:
    resolved = path.resolve()
    root = package_root().resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ClinicalPathError(
            f"Refusing path outside collection/_synthetic_dicom: {resolved}"
        ) from exc
    parts = {part.lower() for part in resolved.parts}
    for marker in FORBIDDEN_PATH_MARKERS:
        if marker in parts:
            raise ClinicalPathError(
                f"Refusing clinical/protected path marker {marker!r}: {resolved}"
            )
    return resolved


def looks_synthetic_dataset(dataset) -> bool:
    comments = str(getattr(dataset, "ImageComments", "") or "")
    series = str(getattr(dataset, "SeriesDescription", "") or "")
    name = str(getattr(dataset, "PatientName", "") or "")
    return (
        SYNTHETIC_MARKER in comments
        or series == "SYNTHETIC_DRY_RUN"
        or name == "SYNTHETIC_TEST"
    )
