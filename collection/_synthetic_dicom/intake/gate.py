"""Fail-closed intake gate for SYNTHETIC files only."""

from __future__ import annotations

from pathlib import Path

from .case_id import allocate_clinical_case_id, synthetic_case_id
from .constants import SYNTHETIC_CASE_ID
from .deidentify import deidentify_synthetic_dicom
from .duplicate import classify_duplicate, load_index, register, save_index
from .hashing import sha256_file
from .paths import ClinicalPathError, assert_synthetic_sandbox, package_root
from .provenance import build_manifest, write_manifest


def run_intake_gate(
    source_path: Path,
    *,
    output_path: Path | None = None,
    index_path: Path | None = None,
    manifest_path: Path | None = None,
    register_index: bool = True,
) -> dict:
    """Return PASS, BLOCKED, or REVIEW. Never processes bassin/ clinical files."""

    try:
        source = assert_synthetic_sandbox(Path(source_path))
    except ClinicalPathError as exc:
        return {"status": "BLOCKED", "reason": str(exc), "case_id": None}

    clinical = allocate_clinical_case_id()
    if clinical["status"] != "BLOCKED":
        return {"status": "BLOCKED", "reason": "clinical_case_id_allocator_must_stay_blocked"}

    case_id = synthetic_case_id()
    dest = output_path or (package_root() / "output" / f"{case_id}_deidentified.dcm")
    try:
        dest = assert_synthetic_sandbox(dest)
    except ClinicalPathError as exc:
        return {"status": "BLOCKED", "reason": str(exc), "case_id": case_id}

    deid = deidentify_synthetic_dicom(source, dest, case_id=case_id)
    if deid.get("status") != "DEIDENTIFIED":
        return {
            "status": "BLOCKED",
            "reason": deid.get("reason", "deidentification_failed"),
            "case_id": case_id,
            "deidentification_status": "BLOCKED",
            "source_file_hash": deid.get("source_file_hash") or sha256_file(source),
            "details": deid,
        }

    pixel_status = deid["pixel_phi_check"]["status"]
    if pixel_status == "NOT_IMPLEMENTED":
        return {
            "status": "REVIEW",
            "reason": "pixel_phi_not_implemented_for_non_synthetic",
            "case_id": case_id,
            "deidentification_status": deid["status"],
            "pixel_phi_status": pixel_status,
            "details": deid,
        }
    if pixel_status != "PASS_SYNTHETIC":
        return {
            "status": "BLOCKED",
            "reason": f"pixel_phi_{pixel_status}",
            "case_id": case_id,
            "details": deid,
        }

    integrity_status = deid["integrity"]["status"]
    if integrity_status != "INTEGRITY_OK":
        return {
            "status": "BLOCKED",
            "reason": "INTEGRITY_FAIL",
            "case_id": case_id,
            "integrity_status": integrity_status,
            "details": deid,
        }

    record = {
        "case_id": case_id,
        "source_file_hash": deid["source_file_hash"],
        "deidentified_file_hash": deid["deidentified_file_hash"],
        "pixel_hash": deid["pixel_hash"],
        "study_uid": deid["original_uids"].get("StudyInstanceUID"),
    }
    index = load_index(index_path)
    duplicate_status = classify_duplicate(index, record)
    if duplicate_status != "UNIQUE":
        result = {
            "status": "BLOCKED",
            "reason": f"duplicate_{duplicate_status}",
            "case_id": case_id,
            "duplicate_status": duplicate_status,
            "deidentification_status": deid["status"],
            "pixel_phi_status": pixel_status,
            "integrity_status": integrity_status,
            **{k: deid.get(k) for k in (
                "source_file_hash",
                "deidentified_file_hash",
                "pixel_hash",
                "modality",
                "rows",
                "columns",
                "pixel_spacing",
                "orientation",
                "output_path",
            )},
        }
        if manifest_path is not None:
            write_manifest(build_manifest(result), manifest_path)
        return result

    if register_index:
        registered = register(index, record)
        save_index(registered["index"], index_path)

    result = {
        "status": "PASS",
        "reason": "synthetic_dry_run_ok",
        "case_id": SYNTHETIC_CASE_ID,
        "deidentification_status": deid["status"],
        "pixel_phi_status": pixel_status,
        "integrity_status": integrity_status,
        "duplicate_status": "UNIQUE",
        "source_file_hash": deid["source_file_hash"],
        "deidentified_file_hash": deid["deidentified_file_hash"],
        "pixel_hash": deid["pixel_hash"],
        "pixel_hash_before": deid["pixel_hash_before"],
        "modality": deid["modality"],
        "rows": deid["rows"],
        "columns": deid["columns"],
        "pixel_spacing": deid["pixel_spacing"],
        "orientation": deid["orientation"],
        "output_path": deid["output_path"],
        "source_path": deid["source_path"],
        "sensitive_tags_before": deid["sensitive_tags_before"],
        "residual_sensitive_tags": deid["residual_sensitive_tags"],
        "clinical_case_id_allocator": clinical,
        "would_enter_03_deidentified": True,
        "clinical_03_written": False,
    }
    if manifest_path is not None:
        result["manifest_path"] = str(write_manifest(build_manifest(result), manifest_path))
    return result
