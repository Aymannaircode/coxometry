"""Duplicate index for synthetic fixtures only. Does not scan real datasets."""

from __future__ import annotations

import json
from pathlib import Path

from .paths import assert_synthetic_sandbox, package_root


def default_index_path() -> Path:
    return package_root() / "reports" / "synthetic_duplicate_index.json"


def load_index(path: Path | None = None) -> dict:
    index_path = assert_synthetic_sandbox(path or default_index_path())
    if not index_path.is_file():
        return {"records": []}
    return json.loads(index_path.read_text(encoding="utf-8"))


def save_index(index: dict, path: Path | None = None) -> Path:
    index_path = assert_synthetic_sandbox(path or default_index_path())
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return index_path


def classify_duplicate(index: dict, record: dict) -> str:
    for existing in index.get("records", []):
        if existing.get("source_file_hash") and existing["source_file_hash"] == record.get(
            "source_file_hash"
        ):
            return "EXACT_FILE"
        if existing.get("deidentified_file_hash") and existing[
            "deidentified_file_hash"
        ] == record.get("deidentified_file_hash"):
            return "EXACT_FILE"
        if existing.get("pixel_hash") and existing["pixel_hash"] == record.get("pixel_hash"):
            return "EXACT_PIXEL"
        if existing.get("study_uid") and existing["study_uid"] == record.get("study_uid"):
            return "SAME_STUDY"
    return "UNIQUE"


def register(index: dict, record: dict) -> dict:
    status = classify_duplicate(index, record)
    stored = dict(record)
    stored["duplicate_status"] = status
    if status == "UNIQUE":
        index.setdefault("records", []).append(stored)
    return {"duplicate_status": status, "index": index}
