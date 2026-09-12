"""Pixel PHI interface. No fake OCR. Synthetic-only PASS."""

from __future__ import annotations

from .paths import looks_synthetic_dataset


def pixel_phi_check(dataset, *, synthetic: bool | None = None) -> dict:
    """Return an explicit pixel-PHI status.

    OCR is not implemented. A real clinical file must never be auto-declared safe.
    """
    is_synth = looks_synthetic_dataset(dataset) if synthetic is None else bool(synthetic)
    if is_synth:
        return {
            "status": "PASS_SYNTHETIC",
            "ocr": "NOT_IMPLEMENTED",
            "safe_for_clinical_use": False,
            "note": (
                "Phantom fixture only. No OCR was run. "
                "This PASS_SYNTHETIC must never be reused as a clinical pixel-PHI pass."
            ),
        }
    return {
        "status": "NOT_IMPLEMENTED",
        "ocr": "NOT_IMPLEMENTED",
        "safe_for_clinical_use": False,
        "note": (
            "No robust OCR/visual certification is available. "
            "Unverified pixel PHI → fail-closed. Never auto-safe for a real case."
        ),
    }
