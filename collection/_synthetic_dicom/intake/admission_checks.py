"""Mandatory admission checks. Each returns check_name/status/reason/details."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .case_id_policy import evaluate_case_id_policy
from .check_result import check_result
from .constants import ALLOWED_RADIOGRAPH_MODALITIES
from .duplicate_index import DuplicateIndex
from .eligibility import EligibilityGate
from .hashing import sha256_file, sha256_pixels
from .metadata import detect_sensitive_metadata
from .paths import looks_synthetic_dataset
from .pixel_phi import pixel_phi_check


def _tag(dataset, name: str):
    return getattr(dataset, name, None) if dataset is not None else None


def _present(dataset, name: str) -> bool:
    value = _tag(dataset, name)
    if value is None:
        return False
    text = str(value).strip()
    return bool(text)


def check_dicom_readable(dataset, error: str | None) -> dict[str, Any]:
    if error or dataset is None:
        return check_result(
            "DICOM_READABLE",
            "BLOCKED",
            "unreadable_dicom",
            {"error": error or "no_dataset"},
        )
    return check_result("DICOM_READABLE", "PASS", "dicom_readable", {})


def check_modality(dataset) -> dict[str, Any]:
    if not _present(dataset, "Modality"):
        return check_result("MODALITY", "BLOCKED", "modality_missing", {})
    modality = str(dataset.Modality).strip()
    if modality not in ALLOWED_RADIOGRAPH_MODALITIES:
        return check_result(
            "MODALITY",
            "BLOCKED",
            "invalid_modality",
            {"modality": modality, "allowed": list(ALLOWED_RADIOGRAPH_MODALITIES)},
        )
    return check_result("MODALITY", "PASS", "modality_ok", {"modality": modality})


def check_rows(dataset) -> dict[str, Any]:
    if not _present(dataset, "Rows"):
        return check_result("ROWS", "BLOCKED", "rows_missing", {})
    try:
        rows = int(dataset.Rows)
    except (TypeError, ValueError):
        return check_result("ROWS", "BLOCKED", "rows_invalid", {"value": str(dataset.Rows)})
    if rows <= 0:
        return check_result("ROWS", "BLOCKED", "rows_non_positive", {"rows": rows})
    return check_result("ROWS", "PASS", "rows_present", {"rows": rows})


def check_columns(dataset) -> dict[str, Any]:
    if not _present(dataset, "Columns"):
        return check_result("COLUMNS", "BLOCKED", "columns_missing", {})
    try:
        columns = int(dataset.Columns)
    except (TypeError, ValueError):
        return check_result(
            "COLUMNS", "BLOCKED", "columns_invalid", {"value": str(dataset.Columns)}
        )
    if columns <= 0:
        return check_result("COLUMNS", "BLOCKED", "columns_non_positive", {"columns": columns})
    return check_result("COLUMNS", "PASS", "columns_present", {"columns": columns})


def check_pixel_data(dataset) -> dict[str, Any]:
    if dataset is None or not hasattr(dataset, "PixelData") or not dataset.PixelData:
        return check_result("PIXEL_DATA", "BLOCKED", "missing_pixel_data", {})
    return check_result(
        "PIXEL_DATA",
        "PASS",
        "pixel_data_present",
        {"nbytes": len(dataset.PixelData)},
    )


def check_pixel_spacing(dataset) -> dict[str, Any]:
    if not _present(dataset, "PixelSpacing"):
        return check_result("PIXEL_SPACING", "BLOCKED", "pixel_spacing_missing", {})
    try:
        spacing = [float(v) for v in dataset.PixelSpacing]
    except (TypeError, ValueError):
        return check_result(
            "PIXEL_SPACING", "BLOCKED", "pixel_spacing_invalid", {"value": str(dataset.PixelSpacing)}
        )
    if len(spacing) < 2 or any(v <= 0 for v in spacing[:2]):
        return check_result(
            "PIXEL_SPACING",
            "BLOCKED",
            "pixel_spacing_non_positive",
            {"pixel_spacing": spacing},
        )
    return check_result("PIXEL_SPACING", "PASS", "pixel_spacing_present", {"pixel_spacing": spacing})


def check_photometric(dataset) -> dict[str, Any]:
    if not _present(dataset, "PhotometricInterpretation"):
        return check_result(
            "PHOTOMETRIC_INTERPRETATION",
            "BLOCKED",
            "photometric_interpretation_missing",
            {},
        )
    value = str(dataset.PhotometricInterpretation)
    return check_result(
        "PHOTOMETRIC_INTERPRETATION",
        "PASS",
        "photometric_interpretation_present",
        {"photometric_interpretation": value},
    )


def check_bits_allocated(dataset) -> dict[str, Any]:
    if not _present(dataset, "BitsAllocated"):
        return check_result("BITS_ALLOCATED", "BLOCKED", "bits_allocated_missing", {})
    return check_result(
        "BITS_ALLOCATED",
        "PASS",
        "bits_allocated_present",
        {"bits_allocated": int(dataset.BitsAllocated)},
    )


def check_bits_stored(dataset) -> dict[str, Any]:
    if not _present(dataset, "BitsStored"):
        return check_result("BITS_STORED", "BLOCKED", "bits_stored_missing", {})
    return check_result(
        "BITS_STORED",
        "PASS",
        "bits_stored_present",
        {"bits_stored": int(dataset.BitsStored)},
    )


def check_pixel_representation(dataset) -> dict[str, Any]:
    if not hasattr(dataset, "PixelRepresentation"):
        return check_result(
            "PIXEL_REPRESENTATION",
            "BLOCKED",
            "pixel_representation_missing",
            {},
        )
    return check_result(
        "PIXEL_REPRESENTATION",
        "PASS",
        "pixel_representation_present",
        {"pixel_representation": int(dataset.PixelRepresentation)},
    )


def check_rescale(dataset) -> dict[str, Any]:
    slope_present = hasattr(dataset, "RescaleSlope")
    intercept_present = hasattr(dataset, "RescaleIntercept")
    if not slope_present and not intercept_present:
        return check_result(
            "RESCALE",
            "PASS",
            "rescale_absent_optional",
            {"present": False},
        )
    details: dict[str, Any] = {"present": True}
    try:
        if slope_present:
            details["RescaleSlope"] = float(dataset.RescaleSlope)
        if intercept_present:
            details["RescaleIntercept"] = float(dataset.RescaleIntercept)
    except (TypeError, ValueError):
        return check_result("RESCALE", "BLOCKED", "rescale_invalid", details)
    return check_result("RESCALE", "PASS", "rescale_present_recorded", details)


def check_orientation(dataset) -> dict[str, Any]:
    patient = str(getattr(dataset, "PatientOrientation", "") or "")
    iop = getattr(dataset, "ImageOrientationPatient", None)
    if not patient and iop is None:
        return check_result(
            "ORIENTATION",
            "PASS",
            "orientation_absent_optional",
            {"present": False, "orientation": None},
        )
    details = {
        "present": True,
        "PatientOrientation": patient or None,
        "ImageOrientationPatient": [float(v) for v in iop] if iop is not None else None,
    }
    return check_result("ORIENTATION", "PASS", "orientation_present_recorded", details)


def check_metadata_phi(dataset) -> dict[str, Any]:
    found = detect_sensitive_metadata(dataset) if dataset is not None else ["NO_DATASET"]
    if found:
        return check_result(
            "METADATA_PHI_CHECK",
            "BLOCKED",
            "metadata_phi_present",
            {"residual_tags": found},
        )
    return check_result(
        "METADATA_PHI_CHECK",
        "PASS",
        "no_residual_identifying_metadata",
        {"residual_tags": []},
    )


def check_pixel_phi(dataset, *, metadata_phi_status: str) -> dict[str, Any]:
    """Never inherit PASS from metadata. Never fake OCR."""
    is_synth = bool(dataset is not None and looks_synthetic_dataset(dataset))
    raw = pixel_phi_check(dataset, synthetic=is_synth) if dataset is not None else {
        "ocr": "NOT_IMPLEMENTED",
        "note": "no_dataset",
    }
    ocr = raw.get("ocr", "NOT_IMPLEMENTED")
    status = "REVIEW" if is_synth and ocr != "IMPLEMENTED" else "BLOCKED"
    return check_result(
        "PIXEL_PHI_CHECK",
        status,
        "pixel_phi_not_verified_ocr_not_implemented",
        {
            "ocr": ocr,
            "safe_for_clinical_use": False,
            "metadata_phi_status": metadata_phi_status,
            "inherited_from_metadata": False,
            "metadata_pass_does_not_imply_pixel_pass": True,
            "note": raw.get("note"),
        },
    )


def check_source_sha256(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return check_result("SOURCE_SHA256", "BLOCKED", "source_file_missing", {})
    digest = sha256_file(path)
    if len(digest) != 64:
        return check_result("SOURCE_SHA256", "BLOCKED", "source_hash_invalid", {})
    return check_result("SOURCE_SHA256", "PASS", "source_sha256_computed", {"sha256": digest})


def check_pixel_sha256(dataset) -> dict[str, Any]:
    if dataset is None or not hasattr(dataset, "PixelData") or not dataset.PixelData:
        return check_result("PIXEL_SHA256", "BLOCKED", "pixel_hash_unavailable", {})
    try:
        digest = sha256_pixels(dataset)
    except Exception as exc:
        return check_result("PIXEL_SHA256", "BLOCKED", "pixel_hash_failed", {"error": str(exc)})
    return check_result("PIXEL_SHA256", "PASS", "pixel_sha256_computed", {"sha256": digest})


def check_geometry_consistency(dataset, rows_check: dict, columns_check: dict) -> dict[str, Any]:
    if rows_check["status"] != "PASS" or columns_check["status"] != "PASS":
        return check_result(
            "GEOMETRY_CONSISTENCY",
            "BLOCKED",
            "geometry_tags_incomplete",
            {},
        )
    if dataset is None or not hasattr(dataset, "PixelData") or not dataset.PixelData:
        return check_result(
            "GEOMETRY_CONSISTENCY",
            "BLOCKED",
            "geometry_mismatch_missing_pixels",
            {},
        )
    try:
        array = dataset.pixel_array
    except Exception as exc:
        return check_result(
            "GEOMETRY_CONSISTENCY",
            "BLOCKED",
            "geometry_mismatch_unreadable_pixels",
            {"error": str(exc)},
        )
    expected = (int(dataset.Rows), int(dataset.Columns))
    actual = tuple(int(v) for v in array.shape[:2])
    if expected != actual:
        return check_result(
            "GEOMETRY_CONSISTENCY",
            "BLOCKED",
            "geometry_mismatch_rows_columns",
            {"rows_columns": expected, "pixel_array_shape": actual},
        )
    return check_result(
        "GEOMETRY_CONSISTENCY",
        "PASS",
        "geometry_consistent",
        {"rows_columns": expected},
    )


def check_duplicate(index: DuplicateIndex, record: dict[str, Any]) -> dict[str, Any]:
    return index.lookup(
        source_hash=record.get("source_file_hash"),
        pixel_hash=record.get("pixel_hash"),
        study=record.get("study_uid"),
        series=record.get("series_uid"),
        patient_pseudonym=record.get("patient_pseudonym"),
    )


def check_provenance(context: dict[str, Any] | None) -> dict[str, Any]:
    context = context or {}
    if context.get("omit_provenance") or context.get("provenance") is None:
        if context.get("provenance") is None and not context.get("allow_auto_provenance", True):
            return check_result("PROVENANCE", "BLOCKED", "provenance_missing", {})
        if context.get("omit_provenance"):
            return check_result("PROVENANCE", "BLOCKED", "provenance_missing", {})
    if context.get("provenance") == {}:
        return check_result("PROVENANCE", "BLOCKED", "provenance_missing", {})
    return check_result(
        "PROVENANCE",
        "PASS",
        "provenance_context_available",
        {"source_type": context.get("source_type", "DICOM_DX_SYNTHETIC")},
    )


def check_eligibility(
    *,
    checks: dict[str, dict],
    context: dict[str, Any],
) -> dict[str, Any]:
    gate = EligibilityGate()
    metadata_blocked = checks.get("METADATA_PHI_CHECK", {}).get("status") == "BLOCKED"
    duplicate_blocked = checks.get("DUPLICATE", {}).get("status") == "BLOCKED"
    readable = checks.get("DICOM_READABLE", {}).get("status") == "PASS"
    provenance_ok = checks.get("PROVENANCE", {}).get("status") == "PASS"
    evidence = {
        "synthetic_fixture": True,
        "adult": context.get("adult", "SYNTHETIC_NOT_CLINICAL"),
        "pelvis_hip_radiograph": context.get("pelvis_hip_radiograph", True),
        "projection_compatible": context.get("projection_compatible", True),
        "image_exploitable": context.get("image_exploitable", True),
        "no_untreated_phi": not metadata_blocked,
        "unique_patient": not duplicate_blocked,
        "not_duplicate": not duplicate_blocked,
        "dicom_valid": readable,
        "provenance_available": provenance_ok,
    }
    if context.get("eligibility_incomplete"):
        evidence.pop("adult", None)
    return gate.evaluate(evidence)


def check_case_id(context: dict[str, Any], dataset) -> dict[str, Any]:
    proposed = context.get("case_id", context.get("Case_ID"))
    return evaluate_case_id_policy(proposed, dataset)
