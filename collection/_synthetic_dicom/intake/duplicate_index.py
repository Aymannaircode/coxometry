"""Synthetic-only DuplicateIndex. No real patient records may be stored."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .check_result import check_result
from .constants import BLOCKED_REAL_PATIENT_IMPORT_DISABLED
from .duplicate import classify_duplicate, load_index, register, save_index
from .paths import ClinicalPathError
from .safety_lock import classify_input_path, refuse_protected_write


class DuplicateIndex:
    """Future keys: source hash, pixel hash, study, series, patient pseudonym.

    Phase 11C-4: in-memory / sandbox JSON only. Real data is refused.
    """

    def __init__(self, records: list[dict] | None = None, *, synthetic_only: bool = True):
        if not synthetic_only:
            raise ClinicalPathError(BLOCKED_REAL_PATIENT_IMPORT_DISABLED)
        self.synthetic_only = True
        self._index: dict[str, Any] = {"records": list(records or []), "synthetic_only": True}

    @classmethod
    def load_synthetic(cls, path: Path | None = None) -> "DuplicateIndex":
        if path is not None and classify_input_path(path) != "SYNTHETIC_SANDBOX":
            raise ClinicalPathError(BLOCKED_REAL_PATIENT_IMPORT_DISABLED)
        loaded = load_index(path) if path is not None else {"records": []}
        instance = cls(loaded.get("records"), synthetic_only=True)
        return instance

    def as_dict(self) -> dict[str, Any]:
        return self._index

    def lookup(
        self,
        *,
        source_hash: str | None = None,
        pixel_hash: str | None = None,
        study: str | None = None,
        series: str | None = None,
        patient_pseudonym: str | None = None,
    ) -> dict[str, Any]:
        record = {
            "source_file_hash": source_hash,
            "pixel_hash": pixel_hash,
            "study_uid": study,
            "series_uid": series,
            "patient_pseudonym": patient_pseudonym,
        }
        status = classify_duplicate(self._index, record)
        if status == "UNIQUE" and patient_pseudonym:
            for existing in self._index.get("records", []):
                if existing.get("patient_pseudonym") == patient_pseudonym:
                    status = "SAME_PSEUDONYM"
                    break
        if status == "UNIQUE" and series:
            for existing in self._index.get("records", []):
                if existing.get("series_uid") and existing.get("series_uid") == series:
                    status = "SAME_SERIES"
                    break
        return check_result(
            "DUPLICATE",
            "PASS" if status == "UNIQUE" else "BLOCKED",
            "unique_synthetic" if status == "UNIQUE" else f"duplicate_{status}",
            {"duplicate_status": status, "synthetic_only": True},
        )

    def register_synthetic(self, record: dict) -> dict[str, Any]:
        if record.get("synthetic") is False:
            raise ClinicalPathError("Refusing to index non-synthetic record")
        if record.get("source_type") and "SYNTHETIC" not in str(record["source_type"]).upper():
            raise ClinicalPathError("Refusing to index non-synthetic source_type")
        stored = dict(record)
        stored["synthetic"] = True
        result = register(self._index, stored)
        self._index = result["index"]
        self._index["synthetic_only"] = True
        return result

    def save_synthetic(self, path: Path) -> Path:
        refuse_protected_write(path)
        return save_index(self._index, path)
