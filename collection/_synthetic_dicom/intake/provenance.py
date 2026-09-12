"""Synthetic provenance manifest. No real personal data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .constants import PHASE11C4_TOOL_VERSION, PROVENANCE_REQUIRED_FIELDS, SYNTHETIC_CASE_ID, TOOL_VERSION
from .paths import assert_synthetic_sandbox
from .safety_lock import refuse_protected_write


def build_manifest(gate_result: dict) -> dict:
    return {
        "Case_ID": gate_result.get("case_id") or SYNTHETIC_CASE_ID,
        "source_file_hash": gate_result.get("source_file_hash"),
        "deidentified_file_hash": gate_result.get("deidentified_file_hash"),
        "pixel_hash": gate_result.get("pixel_hash"),
        "source_type": "DICOM_DX_SYNTHETIC",
        "synthetic": True,
        "modality": gate_result.get("modality"),
        "rows": gate_result.get("rows"),
        "columns": gate_result.get("columns"),
        "pixel_spacing": gate_result.get("pixel_spacing"),
        "orientation": gate_result.get("orientation"),
        "deidentification_status": gate_result.get("deidentification_status"),
        "pixel_phi_check": gate_result.get("pixel_phi_status"),
        "integrity_status": gate_result.get("integrity_status"),
        "duplicate_status": gate_result.get("duplicate_status"),
        "eligibility_status": "SYNTHETIC_DRY_RUN_ONLY",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool_version": TOOL_VERSION,
        "gate_status": gate_result.get("status"),
        "would_enter_03_deidentified": gate_result.get("status") == "PASS",
        "clinical_03_written": False,
        "note": (
            "Synthetic dry-run only. PASS does not authorize real-patient import "
            "or writing into collection/03_DEIDENTIFIED."
        ),
    }


def write_manifest(manifest: dict, path: Path) -> Path:
    dest = assert_synthetic_sandbox(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return dest


def build_admission_manifest(gate_result: dict) -> dict:
    """11C-4 public manifest. No identity fields."""
    forbidden = (
        "PatientName",
        "PatientID",
        "PatientBirthDate",
        "AccessionNumber",
        "InstitutionName",
        "ReferringPhysicianName",
    )
    manifest = {
        "Case_ID": gate_result.get("case_id") or SYNTHETIC_CASE_ID,
        "source_file_hash": gate_result.get("source_file_hash"),
        "pixel_hash": gate_result.get("pixel_hash"),
        "source_type": gate_result.get("source_type") or "DICOM_DX_SYNTHETIC",
        "modality": gate_result.get("modality"),
        "rows": gate_result.get("rows"),
        "columns": gate_result.get("columns"),
        "pixel_spacing": gate_result.get("pixel_spacing"),
        "orientation": gate_result.get("orientation"),
        "deidentification_status": gate_result.get("deidentification_status") or "NOT_APPLIED_ADMISSION_ONLY",
        "metadata_phi_status": gate_result.get("metadata_phi_status"),
        "pixel_phi_status": gate_result.get("pixel_phi_status"),
        "integrity_status": gate_result.get("integrity_status"),
        "duplicate_status": gate_result.get("duplicate_status"),
        "eligibility_status": gate_result.get("eligibility_status"),
        "physician_review_status": "NOT_STARTED",
        "annotation_status": "NOT_STARTED",
        "qc_status": "NOT_STARTED",
        "tool_version": PHASE11C4_TOOL_VERSION,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    for key in forbidden:
        manifest.pop(key, None)
    missing = [name for name in PROVENANCE_REQUIRED_FIELDS if name not in manifest]
    manifest["_schema_complete"] = not missing
    return manifest


def write_admission_manifest(manifest: dict, path: Path) -> Path:
    refuse_protected_write(path)
    return write_manifest(manifest, path)
