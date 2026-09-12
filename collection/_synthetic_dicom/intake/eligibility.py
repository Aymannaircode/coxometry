"""Conceptual eligibility gate. No invented clinical thresholds."""

from __future__ import annotations

from typing import Any

from .check_result import check_result
from .constants import OPEN_PHYSICIAN_DECISIONS


class EligibilityGate:
    """Future clinical eligibility. Phase 11C-4: synthetic / conceptual only."""

    OPEN_DECISIONS = OPEN_PHYSICIAN_DECISIONS

    CONCEPTUAL_CONDITIONS = (
        "adult",
        "pelvis_hip_radiograph",
        "projection_compatible",
        "image_exploitable",
        "no_untreated_phi",
        "unique_patient",
        "not_duplicate",
        "dicom_valid",
        "provenance_available",
    )

    def evaluate(self, evidence: dict[str, Any]) -> dict[str, Any]:
        missing: list[str] = []
        failed: list[str] = []
        notes: dict[str, Any] = {}

        for name in self.CONCEPTUAL_CONDITIONS:
            value = evidence.get(name)
            if value is None:
                missing.append(name)
                continue
            if value is False:
                failed.append(name)
            notes[name] = value

        open_items = {item: "OPEN" for item in self.OPEN_DECISIONS}
        notes["open_physician_decisions"] = open_items
        notes["no_clinical_threshold_invented"] = True
        notes["p_fov_numeric_cutoff"] = "NOT_APPLIED"

        if failed:
            return check_result(
                "ELIGIBILITY",
                "BLOCKED",
                "eligibility_condition_failed",
                {"failed": failed, "missing": missing, **notes},
            )
        if missing:
            return check_result(
                "ELIGIBILITY",
                "REVIEW",
                "eligibility_information_missing_fail_closed",
                {"missing": missing, **notes},
            )
        if not evidence.get("synthetic_fixture"):
            return check_result(
                "ELIGIBILITY",
                "REVIEW",
                "clinical_eligibility_not_authorized_in_11c4",
                notes,
            )
        return check_result(
            "ELIGIBILITY",
            "PASS",
            "synthetic_conceptual_eligibility_only",
            notes,
        )
