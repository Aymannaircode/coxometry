"""Phase 11C-4 real-patient import lock. Cannot be bypassed."""

from __future__ import annotations

from pathlib import Path

from .constants import (
    BLOCKED_REAL_PATIENT_IMPORT_DISABLED,
    FORBIDDEN_PATH_MARKERS,
    REAL_PATIENT_IMPORT_DISABLED,
)
from .paths import ClinicalPathError, assert_synthetic_sandbox, package_root


# Extra trees that must never be treated as an intake source or write target.
PROTECTED_WRITE_MARKERS = FORBIDDEN_PATH_MARKERS + (
    "03_deidentified",
    "01_inbox_raw",
    "images",
    "labels",
    "mvp_geometry",
    "backend",
    "mobile",
)

REAL_PATH_MARKERS = FORBIDDEN_PATH_MARKERS + (
    "03_deidentified",
    "01_inbox_raw",
    "restricted",
)


def real_patient_import_disabled() -> bool:
    return bool(REAL_PATIENT_IMPORT_DISABLED)


def looks_real_or_protected_path(path: Path) -> bool:
    parts = {part.lower() for part in Path(path).parts}
    return any(marker in parts for marker in REAL_PATH_MARKERS)


def classify_input_path(path: Path) -> str:
    """Return SYNTHETIC_SANDBOX or REAL_OR_PROTECTED. Never walks bassin/."""
    try:
        resolved = Path(path).resolve()
    except OSError:
        return "REAL_OR_PROTECTED"
    if looks_real_or_protected_path(resolved):
        return "REAL_OR_PROTECTED"
    root = package_root().resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return "REAL_OR_PROTECTED"
    return "SYNTHETIC_SANDBOX"


def refuse_non_synthetic_path(path: Path) -> Path:
    """Refuse every non-synthetic path before any DICOM read."""
    if not real_patient_import_disabled():
        raise RuntimeError("REAL_PATIENT_IMPORT_DISABLED must stay true in 11C-4")
    classification = classify_input_path(path)
    if classification != "SYNTHETIC_SANDBOX":
        raise ClinicalPathError(BLOCKED_REAL_PATIENT_IMPORT_DISABLED)
    return assert_synthetic_sandbox(Path(path))


def refuse_protected_write(path: Path) -> None:
    """Admission gate may only write under collection/_synthetic_dicom."""
    resolved = Path(path).resolve()
    root = package_root().resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ClinicalPathError(
            f"Refusing write outside synthetic sandbox: {resolved}"
        ) from exc
    parts = {part.lower() for part in resolved.parts}
    for marker in PROTECTED_WRITE_MARKERS:
        if marker in parts and marker not in {"_synthetic_dicom"}:
            # Allow files that merely live under the sandbox even if a name
            # collides; reject only when the marker is outside the sandbox.
            # Images/labels/backend markers must never appear as write roots.
            if marker in {
                "images",
                "labels",
                "backend",
                "mobile",
                "mvp_geometry",
                "03_deidentified",
                "01_inbox_raw",
                "bassin",
                "yolo_pose_new_26",
                "yolo_pose_remediation_v1",
                "annotation_pilot",
                "runs",
                "restricted",
            }:
                raise ClinicalPathError(
                    f"Refusing protected write marker {marker!r}: {resolved}"
                )
    if looks_real_or_protected_path(resolved):
        raise ClinicalPathError(f"Refusing protected write: {resolved}")


def scan_clinical_inbox() -> None:
    """Explicitly disabled. Do not walk bassin/ or 01_INBOX_RAW."""
    raise ClinicalPathError(BLOCKED_REAL_PATIENT_IMPORT_DISABLED)
