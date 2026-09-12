"""Synthetic Case ID only. Real clinical allocation is explicitly BLOCKED."""

from __future__ import annotations

from .constants import SYNTHETIC_CASE_ID


def synthetic_case_id() -> str:
    return SYNTHETIC_CASE_ID


def allocate_clinical_case_id(*_args, **_kwargs) -> dict:
    """Future real R27_* allocator. Must stay blocked until protocol validation."""
    return {
        "status": "BLOCKED",
        "case_id": None,
        "reason": (
            "Real Case ID allocation (R27_001+) is BLOCKED until the collection "
            "protocol is validated. Dry-run IDs must use SYNTHETIC_R27_001 only."
        ),
    }
