"""Case ID policy. Hospital identifiers are never accepted as Case ID."""

from __future__ import annotations

from typing import Any

from .case_id import allocate_clinical_case_id, synthetic_case_id
from .check_result import check_result
from .constants import FORBIDDEN_CASE_ID_FIELDS, SYNTHETIC_CASE_ID


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def extract_forbidden_identifiers(dataset) -> dict[str, str]:
    found: dict[str, str] = {}
    for name in FORBIDDEN_CASE_ID_FIELDS:
        if hasattr(dataset, name):
            text = _stringify(getattr(dataset, name, None))
            if text:
                found[name] = text
    return found


def evaluate_case_id_policy(proposed: str | None, dataset=None) -> dict[str, Any]:
    clinical = allocate_clinical_case_id()
    if clinical.get("status") != "BLOCKED":
        return check_result(
            "CASE_ID_POLICY",
            "BLOCKED",
            "clinical_r27_allocator_must_stay_blocked",
            {"allocator": clinical},
        )

    if proposed is None or not str(proposed).strip():
        return check_result(
            "CASE_ID_POLICY",
            "BLOCKED",
            "case_id_missing_fail_closed",
            {"allowed": SYNTHETIC_CASE_ID, "allocator": clinical},
        )

    candidate = str(proposed).strip()
    if candidate.startswith("R27_") and not candidate.startswith("SYNTHETIC_R27_"):
        return check_result(
            "CASE_ID_POLICY",
            "BLOCKED",
            "real_r27_allocation_disabled",
            {"proposed": candidate, "allocator": clinical},
        )

    forbidden = extract_forbidden_identifiers(dataset) if dataset is not None else {}
    for field, value in forbidden.items():
        if candidate == value:
            return check_result(
                "CASE_ID_POLICY",
                "BLOCKED",
                f"case_id_equals_{field}",
                {"proposed": candidate, "field": field, "allocator": clinical},
            )

    if candidate != synthetic_case_id():
        return check_result(
            "CASE_ID_POLICY",
            "BLOCKED",
            "only_SYNTHETIC_R27_001_allowed_in_11c4",
            {"proposed": candidate, "allowed": SYNTHETIC_CASE_ID},
        )

    return check_result(
        "CASE_ID_POLICY",
        "PASS",
        "synthetic_case_id_only",
        {"case_id": SYNTHETIC_CASE_ID, "allocator": clinical},
    )
