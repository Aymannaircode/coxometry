"""De-identify a SYNTHETIC DICOM. Never overwrites the source file."""

from __future__ import annotations

import copy
from pathlib import Path

from pydicom.uid import generate_uid

from .constants import SENSITIVE_TAGS, SYNTHETIC_CASE_ID, SYNTHETIC_MARKER, UID_TAGS
from .hashing import sha256_file, sha256_pixels
from .integrity import compare_integrity, read_integrity_snapshot
from .metadata import collect_uids, detect_sensitive_metadata
from .paths import ClinicalPathError, assert_synthetic_sandbox, looks_synthetic_dataset
from .pixel_phi import pixel_phi_check

try:
    import pydicom
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("pydicom is required for the synthetic dry-run") from exc


def _research_uid(kind: str, case_id: str) -> str:
    return str(generate_uid(entropy_srcs=["phase11c3-deid", case_id, kind]))


def deidentify_synthetic_dicom(
    source_path: Path,
    output_path: Path,
    *,
    case_id: str = SYNTHETIC_CASE_ID,
) -> dict:
    source = assert_synthetic_sandbox(source_path)
    dest = assert_synthetic_sandbox(output_path)
    source_hash = sha256_file(source)

    try:
        dataset = pydicom.dcmread(str(source), force=False)
    except Exception as exc:
        return {
            "status": "BLOCKED",
            "reason": f"unreadable_dicom: {exc}",
            "source_path": str(source),
            "source_file_hash": source_hash,
        }

    if not looks_synthetic_dataset(dataset):
        return {
            "status": "BLOCKED",
            "reason": "not_synthetic_marker",
            "source_path": str(source),
            "source_file_hash": source_hash,
        }

    if not hasattr(dataset, "PixelData") or not dataset.PixelData:
        return {
            "status": "BLOCKED",
            "reason": "missing_pixel_data",
            "source_path": str(source),
            "source_file_hash": source_hash,
            "sensitive_tags_before": detect_sensitive_metadata(dataset),
        }

    before = read_integrity_snapshot(dataset)
    original_uids = collect_uids(dataset)
    sensitive_before = detect_sensitive_metadata(dataset)

    work = copy.deepcopy(dataset)
    for name in SENSITIVE_TAGS:
        if name in work:
            del work[name]

    private_tags = [elem.tag for elem in work if elem.tag.is_private]
    for tag in private_tags:
        del work[tag]

    new_study = _research_uid("study", case_id)
    new_series = _research_uid("series", case_id)
    new_sop = _research_uid("sop", case_id)
    work.StudyInstanceUID = new_study
    work.SeriesInstanceUID = new_series
    work.SOPInstanceUID = new_sop
    if hasattr(work, "file_meta") and work.file_meta is not None:
        work.file_meta.MediaStorageSOPInstanceUID = new_sop

    work.ImageComments = SYNTHETIC_MARKER
    work.SeriesDescription = "SYNTHETIC_DRY_RUN_DEIDENTIFIED"
    work.Manufacturer = "PHASE11C3_SYNTHETIC"

    residual = detect_sensitive_metadata(work)
    uid_leak = [name for name, value in original_uids.items() if value and value == str(getattr(work, name, ""))]
    after = read_integrity_snapshot(work)
    integrity = compare_integrity(before, after)
    pixel_phi = pixel_phi_check(work, synthetic=True)

    if residual or uid_leak or integrity["status"] != "INTEGRITY_OK":
        return {
            "status": "BLOCKED",
            "reason": "deidentification_incomplete_or_integrity_fail",
            "residual_sensitive_tags": residual,
            "uid_leak": uid_leak,
            "integrity": integrity,
            "pixel_phi_check": pixel_phi,
            "source_path": str(source),
            "source_file_hash": source_hash,
            "sensitive_tags_before": sensitive_before,
        }

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    work.save_as(str(dest), enforce_file_format=True)

    if sha256_file(source) != source_hash:
        raise ClinicalPathError("Source file changed during de-identification")

    return {
        "status": "DEIDENTIFIED",
        "case_id": case_id,
        "source_path": str(source),
        "output_path": str(dest),
        "source_file_hash": source_hash,
        "deidentified_file_hash": sha256_file(dest),
        "pixel_hash": sha256_pixels(work),
        "pixel_hash_before": before["pixel_hash"],
        "sensitive_tags_before": sensitive_before,
        "residual_sensitive_tags": residual,
        "original_uids": original_uids,
        "research_uids": collect_uids(work),
        "integrity": integrity,
        "pixel_phi_check": pixel_phi,
        "modality": str(getattr(work, "Modality", "")),
        "rows": int(work.Rows),
        "columns": int(work.Columns),
        "pixel_spacing": [float(v) for v in work.PixelSpacing],
        "orientation": str(getattr(work, "PatientOrientation", "") or ""),
    }
