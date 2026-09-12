"""Structured check result for the 11C-4 admission gate."""

from __future__ import annotations

from typing import Any


VALID_STATUSES = ("PASS", "REVIEW", "BLOCKED")


def check_result(
    check_name: str,
    status: str,
    reason: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid check status: {status}")
    return {
        "check_name": check_name,
        "status": status,
        "reason": reason,
        "details": details or {},
    }


def worst_status(statuses: list[str]) -> str:
    if "BLOCKED" in statuses:
        return "BLOCKED"
    if "REVIEW" in statuses:
        return "REVIEW"
    return "PASS"
