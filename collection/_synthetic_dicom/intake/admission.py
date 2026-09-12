"""Phase 11C-4 admission gate. Synthetic sandbox only. Fail-closed."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .admission_checks import (
    check_bits_allocated,
    check_bits_stored,
    check_case_id,
    check_columns,
    check_dicom_readable,
    check_duplicate,
    check_eligibility,
    check_geometry_consistency,
    check_metadata_phi,
    check_modality,
    check_orientation,
    check_photometric,
    check_pixel_data,
    check_pixel_phi,
    check_pixel_representation,
    check_pixel_sha256,
    check_pixel_spacing,
    check_provenance,
    check_rescale,
    check_rows,
    check_source_sha256,
)
from .check_result import check_result
from .constants import (
    BLOCKED_REAL_PATIENT_IMPORT_DISABLED,
    PHASE11C4_TOOL_VERSION,
    REAL_PATIENT_IMPORT_DISABLED,
    SYNTHETIC_CASE_ID,
)
from .duplicate_index import DuplicateIndex
from .hashing import sha256_file
from .paths import ClinicalPathError
from .provenance import build_admission_manifest, write_admission_manifest
from .safety_lock import real_patient_import_disabled, refuse_non_synthetic_path, refuse_protected_write

try:
    import pydicom
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("pydicom is required for the synthetic admission gate") from exc


MANDATORY_CHECK_ORDER = (
    "DICOM_READABLE",
    "MODALITY",
    "ROWS",
    "COLUMNS",
    "PIXEL_DATA",
    "PIXEL_SPACING",
    "PHOTOMETRIC_INTERPRETATION",
    "BITS_ALLOCATED",
    "BITS_STORED",
    "PIXEL_REPRESENTATION",
    "RESCALE",
    "ORIENTATION",
    "METADATA_PHI_CHECK",
    "PIXEL_PHI_CHECK",
    "SOURCE_SHA256",
    "PIXEL_SHA256",
    "DUPLICATE",
    "PROVENANCE",
    "ELIGIBILITY",
    "CASE_ID_POLICY",
)

# PIXEL_PHI_CHECK is never a clinical PASS in this phase. A REVIEW here must
# not be upgraded by metadata, but it also must not veto a synthetic software
# PASS when every other mandatory check succeeded.
NON_VETO_REVIEW_CHECKS = {"PIXEL_PHI_CHECK"}


def _blocked_lock_result(reason: str, *, input_path: str) -> dict[str, Any]:
    checks = [
        check_result(name, "BLOCKED", reason, {"evaluated": False})
        for name in MANDATORY_CHECK_ORDER
    ]
    return {
        "status": "BLOCKED",
        "reason": reason,
        "case_id": None,
        "checks": checks,
        "REAL_PATIENT_IMPORT_DISABLED": True,
        "clinical_03_written": False,
        "would_enter_03_deidentified": False,
        "real_r27_allocated": False,
        "source_path": input_path,
        "tool_version": PHASE11C4_TOOL_VERSION,
    }


def _lookup(checks: list[dict[str, Any]], name: str) -> dict[str, Any]:
    for item in checks:
        if item["check_name"] == name:
            return item
    raise KeyError(name)


def _aggregate(checks: list[dict[str, Any]]) -> tuple[str, str]:
    blocked = [c for c in checks if c["status"] == "BLOCKED"]
    if blocked:
        return "BLOCKED", blocked[0]["reason"]
    review = [c for c in checks if c["status"] == "REVIEW" and c["check_name"] not in NON_VETO_REVIEW_CHECKS]
    if review:
        return "REVIEW", review[0]["reason"]
    return "PASS", "synthetic_admission_gate_ok"


def admission_gate(input_path, context=None) -> dict[str, Any]:
    """Control a future DICOM before collection admission.

    Phase 11C-4: refuses every non-synthetic path. Never opens bassin/.
    """
    context = dict(context or {})
    raw_path = Path(input_path)
    if context.get("force_enable_real_import") or context.get("REAL_PATIENT_IMPORT_DISABLED") is False:
        return _blocked_lock_result(
            BLOCKED_REAL_PATIENT_IMPORT_DISABLED,
            input_path=str(raw_path),
        )
    if not real_patient_import_disabled():
        return _blocked_lock_result(
            BLOCKED_REAL_PATIENT_IMPORT_DISABLED,
            input_path=str(raw_path),
        )

    try:
        source = refuse_non_synthetic_path(raw_path)
    except ClinicalPathError:
        return _blocked_lock_result(
            BLOCKED_REAL_PATIENT_IMPORT_DISABLED,
            input_path=str(raw_path),
        )

    if "output_path" in context and context["output_path"] is not None:
        try:
            refuse_protected_write(Path(context["output_path"]))
        except ClinicalPathError as exc:
            return _blocked_lock_result(str(exc), input_path=str(source))

    source_hash_before = sha256_file(source) if source.is_file() else None
    dataset = None
    read_error = None
    try:
        dataset = pydicom.dcmread(str(source), force=False)
    except Exception as exc:
        read_error = str(exc)

    checks: list[dict[str, Any]] = []
    readable = check_dicom_readable(dataset, read_error)
    checks.append(readable)

    if readable["status"] != "PASS":
        checks.extend(
            [
                check_modality(None),
                check_rows(None),
                check_columns(None),
                check_pixel_data(None),
                check_pixel_spacing(None),
                check_photometric(None),
                check_bits_allocated(None),
                check_bits_stored(None),
                check_pixel_representation(None),
                check_result("RESCALE", "BLOCKED", "dicom_unreadable", {}),
                check_result("ORIENTATION", "BLOCKED", "dicom_unreadable", {}),
                check_metadata_phi(None),
                check_pixel_phi(None, metadata_phi_status="BLOCKED"),
                check_source_sha256(source if source.is_file() else None),
                check_pixel_sha256(None),
                check_result("DUPLICATE", "BLOCKED", "dicom_unreadable", {}),
                check_provenance(context),
                check_result("ELIGIBILITY", "BLOCKED", "dicom_unreadable", {}),
                check_case_id({**context, "case_id": context.get("case_id", SYNTHETIC_CASE_ID)}, None),
            ]
        )
        status, reason = _aggregate(checks)
        return {
            "status": status,
            "reason": reason,
            "case_id": context.get("case_id"),
            "checks": checks,
            "REAL_PATIENT_IMPORT_DISABLED": True,
            "clinical_03_written": False,
            "real_r27_allocated": False,
            "source_path": str(source),
            "source_file_hash": source_hash_before,
            "source_hash_after": sha256_file(source) if source.is_file() else None,
            "source_immutable": source_hash_before == sha256_file(source) if source.is_file() else False,
            "tool_version": PHASE11C4_TOOL_VERSION,
        }

    rows = check_rows(dataset)
    columns = check_columns(dataset)
    metadata_phi = check_metadata_phi(dataset)
    pixel_phi = check_pixel_phi(dataset, metadata_phi_status=metadata_phi["status"])
    source_sha = check_source_sha256(source)
    pixel_sha = check_pixel_sha256(dataset)
    geometry = check_geometry_consistency(dataset, rows, columns)

    index = context.get("duplicate_index") or DuplicateIndex()
    if not isinstance(index, DuplicateIndex):
        index = DuplicateIndex()
    duplicate = check_duplicate(
        index,
        {
            "source_file_hash": source_sha.get("details", {}).get("sha256"),
            "pixel_hash": pixel_sha.get("details", {}).get("sha256"),
            "study_uid": str(getattr(dataset, "StudyInstanceUID", "") or "") or None,
            "series_uid": str(getattr(dataset, "SeriesInstanceUID", "") or "") or None,
            "patient_pseudonym": context.get("patient_pseudonym"),
        },
    )
    provenance = check_provenance(context)
    case_id = check_case_id({**context, "case_id": context.get("case_id", SYNTHETIC_CASE_ID)}, dataset)

    by_name = {
        "DICOM_READABLE": readable,
        "MODALITY": check_modality(dataset),
        "ROWS": rows,
        "COLUMNS": columns,
        "PIXEL_DATA": check_pixel_data(dataset),
        "PIXEL_SPACING": check_pixel_spacing(dataset),
        "PHOTOMETRIC_INTERPRETATION": check_photometric(dataset),
        "BITS_ALLOCATED": check_bits_allocated(dataset),
        "BITS_STORED": check_bits_stored(dataset),
        "PIXEL_REPRESENTATION": check_pixel_representation(dataset),
        "RESCALE": check_rescale(dataset),
        "ORIENTATION": check_orientation(dataset),
        "METADATA_PHI_CHECK": metadata_phi,
        "PIXEL_PHI_CHECK": pixel_phi,
        "SOURCE_SHA256": source_sha,
        "PIXEL_SHA256": pixel_sha,
        "DUPLICATE": duplicate,
        "PROVENANCE": provenance,
        "CASE_ID_POLICY": case_id,
    }
    if geometry["status"] != "PASS":
        by_name["ROWS"] = check_result(
            "ROWS",
            "BLOCKED" if geometry["status"] == "BLOCKED" else geometry["status"],
            geometry["reason"],
            geometry["details"],
        )
        by_name["COLUMNS"] = check_result(
            "COLUMNS",
            "BLOCKED" if geometry["status"] == "BLOCKED" else geometry["status"],
            geometry["reason"],
            geometry["details"],
        )
    by_name["ELIGIBILITY"] = check_eligibility(checks=by_name, context=context)
    checks = [by_name[name] for name in MANDATORY_CHECK_ORDER]

    source_hash_after = sha256_file(source)
    status, reason = _aggregate(checks)
    result = {
        "status": status,
        "reason": reason,
        "case_id": SYNTHETIC_CASE_ID if case_id["status"] == "PASS" else context.get("case_id"),
        "checks": checks,
        "REAL_PATIENT_IMPORT_DISABLED": True,
        "clinical_03_written": False,
        "real_r27_allocated": False,
        "source_path": str(source),
        "source_type": context.get("source_type", "DICOM_DX_SYNTHETIC"),
        "source_file_hash": source_sha.get("details", {}).get("sha256"),
        "pixel_hash": pixel_sha.get("details", {}).get("sha256"),
        "modality": by_name["MODALITY"].get("details", {}).get("modality"),
        "rows": rows.get("details", {}).get("rows"),
        "columns": columns.get("details", {}).get("columns"),
        "pixel_spacing": by_name["PIXEL_SPACING"].get("details", {}).get("pixel_spacing"),
        "orientation": by_name["ORIENTATION"].get("details", {}).get("PatientOrientation")
        or by_name["ORIENTATION"].get("details", {}).get("orientation"),
        "deidentification_status": "NOT_APPLIED_ADMISSION_ONLY",
        "metadata_phi_status": metadata_phi["status"],
        "pixel_phi_status": pixel_phi["status"],
        "integrity_status": "INTEGRITY_OK" if geometry["status"] == "PASS" else "INTEGRITY_FAIL",
        "duplicate_status": duplicate.get("details", {}).get("duplicate_status"),
        "eligibility_status": by_name["ELIGIBILITY"]["status"],
        "source_hash_before": source_hash_before,
        "source_hash_after": source_hash_after,
        "source_immutable": source_hash_before == source_hash_after,
        "would_enter_03_deidentified": False,
        "tool_version": PHASE11C4_TOOL_VERSION,
    }
    result["provenance"] = build_admission_manifest(result)
    if context.get("manifest_path"):
        try:
            refuse_protected_write(Path(context["manifest_path"]))
            result["manifest_path"] = str(
                write_admission_manifest(result["provenance"], Path(context["manifest_path"]))
            )
        except ClinicalPathError as exc:
            result["status"] = "BLOCKED"
            result["reason"] = str(exc)
    if context.get("register_index") and status == "PASS":
        index.register_synthetic(
            {
                "case_id": SYNTHETIC_CASE_ID,
                "source_file_hash": result["source_file_hash"],
                "pixel_hash": result["pixel_hash"],
                "study_uid": str(getattr(dataset, "StudyInstanceUID", "") or ""),
                "series_uid": str(getattr(dataset, "SeriesInstanceUID", "") or ""),
                "synthetic": True,
                "source_type": "DICOM_DX_SYNTHETIC",
            }
        )
        if context.get("index_path"):
            index.save_synthetic(Path(context["index_path"]))
    return result
