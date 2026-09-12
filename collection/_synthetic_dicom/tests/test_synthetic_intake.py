"""Synthetic-only tests. No bassin/ or clinical DICOM is opened."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian

from intake.case_id import allocate_clinical_case_id, synthetic_case_id
from intake.constants import (
    DX_SOP_CLASS,
    SENSITIVE_TAGS,
    SYNTHETIC_IMPL_UID,
    SYNTHETIC_MARKER,
    SYNTHETIC_SOP_UID,
)
from intake.deidentify import deidentify_synthetic_dicom
from intake.duplicate import classify_duplicate, register
from intake.gate import run_intake_gate
from intake.generate_synthetic_dicom import write_synthetic_dicom
from intake.hashing import sha256_file, sha256_pixels
from intake.metadata import detect_sensitive_metadata
from intake.paths import ClinicalPathError, assert_synthetic_sandbox
from intake.pixel_phi import pixel_phi_check
from pydicom import dcmread


@pytest.fixture()
def sandbox(tmp_path: Path) -> Path:
    from intake.paths import package_root

    root = package_root() / "reports" / "_pytest_tmp" / tmp_path.name
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_01_synthetic_dicom_creation(sandbox: Path) -> None:
    path = write_synthetic_dicom(sandbox / "created.dcm")
    ds = dcmread(str(path))
    assert path.is_file()
    assert ds.PatientName == "SYNTHETIC_TEST"
    assert ds.PatientID == "SYNTHETIC_001"
    assert SYNTHETIC_MARKER in str(ds.ImageComments)
    assert ds.Rows == 128
    assert ds.Columns == 128
    assert ds.pixel_array.shape == (128, 128)


def test_02_metadata_phi_detection(sandbox: Path) -> None:
    path = write_synthetic_dicom(sandbox / "phi.dcm")
    found = detect_sensitive_metadata(dcmread(str(path)))
    for tag in (
        "PatientName",
        "PatientID",
        "PatientBirthDate",
        "InstitutionName",
        "AccessionNumber",
        "ReferringPhysicianName",
    ):
        assert tag in found


def test_03_metadata_deidentification(sandbox: Path) -> None:
    source = write_synthetic_dicom(sandbox / "src.dcm")
    result = deidentify_synthetic_dicom(source, sandbox / "out.dcm")
    assert result["status"] == "DEIDENTIFIED"
    out = dcmread(str(sandbox / "out.dcm"))
    residual = detect_sensitive_metadata(out)
    assert residual == []
    for tag in SENSITIVE_TAGS:
        assert not hasattr(out, tag) or not str(getattr(out, tag, "")).strip()
    assert result["original_uids"]["StudyInstanceUID"] != result["research_uids"]["StudyInstanceUID"]


def test_04_source_immutability(sandbox: Path) -> None:
    source = write_synthetic_dicom(sandbox / "immutable.dcm")
    before = sha256_file(source)
    result = deidentify_synthetic_dicom(source, sandbox / "immutable_out.dcm")
    assert result["status"] == "DEIDENTIFIED"
    assert sha256_file(source) == before
    assert result["source_file_hash"] == before


def test_05_pixeldata_preservation(sandbox: Path) -> None:
    source = write_synthetic_dicom(sandbox / "pix.dcm")
    src_ds = dcmread(str(source))
    before = sha256_pixels(src_ds)
    result = deidentify_synthetic_dicom(source, sandbox / "pix_out.dcm")
    after = sha256_pixels(dcmread(str(sandbox / "pix_out.dcm")))
    assert result["status"] == "DEIDENTIFIED"
    assert before == after == result["pixel_hash"]


def test_06_rows_columns_preservation(sandbox: Path) -> None:
    source = write_synthetic_dicom(sandbox / "geom.dcm")
    src = dcmread(str(source))
    result = deidentify_synthetic_dicom(source, sandbox / "geom_out.dcm")
    out = dcmread(str(sandbox / "geom_out.dcm"))
    assert result["status"] == "DEIDENTIFIED"
    assert int(src.Rows) == int(out.Rows) == 128
    assert int(src.Columns) == int(out.Columns) == 128
    assert [float(v) for v in src.PixelSpacing] == [float(v) for v in out.PixelSpacing]


def test_07_sha256_generation(sandbox: Path) -> None:
    source = write_synthetic_dicom(sandbox / "hash.dcm")
    result = deidentify_synthetic_dicom(source, sandbox / "hash_out.dcm")
    assert len(result["source_file_hash"]) == 64
    assert len(result["deidentified_file_hash"]) == 64
    assert len(result["pixel_hash"]) == 64
    assert result["source_file_hash"] == sha256_file(source)
    assert result["deidentified_file_hash"] == sha256_file(sandbox / "hash_out.dcm")
    assert result["source_file_hash"] != result["deidentified_file_hash"]


def test_08_duplicate_detection(sandbox: Path) -> None:
    source = write_synthetic_dicom(sandbox / "dup.dcm")
    first = deidentify_synthetic_dicom(source, sandbox / "dup_out.dcm")
    record = {
        "source_file_hash": first["source_file_hash"],
        "deidentified_file_hash": first["deidentified_file_hash"],
        "pixel_hash": first["pixel_hash"],
        "study_uid": first["original_uids"]["StudyInstanceUID"],
    }
    index: dict = {"records": []}
    assert classify_duplicate(index, record) == "UNIQUE"
    register(index, record)
    assert classify_duplicate(index, record) == "EXACT_FILE"
    pixel_only = {
        "source_file_hash": "0" * 64,
        "deidentified_file_hash": "1" * 64,
        "pixel_hash": record["pixel_hash"],
        "study_uid": "other",
    }
    assert classify_duplicate(index, pixel_only) == "EXACT_PIXEL"


def test_09_fail_closed_behaviour(sandbox: Path) -> None:
    clinical = allocate_clinical_case_id(patient_id="would-be-real")
    assert clinical["status"] == "BLOCKED"
    assert clinical["case_id"] is None
    with pytest.raises(ClinicalPathError):
        assert_synthetic_sandbox(Path("C:/Users/g/OneDrive/Desktop/Projet-Ayman/bassin/a_annoter/x.dcm"))
    blocked = run_intake_gate(Path("C:/Users/g/OneDrive/Desktop/Projet-Ayman/bassin/a_annoter/x.dcm"))
    assert blocked["status"] == "BLOCKED"
    assert "bassin" in blocked["reason"].lower() or "refusing" in blocked["reason"].lower()


def test_10_successful_synthetic_gate(sandbox: Path) -> None:
    source = write_synthetic_dicom(sandbox / "gate.dcm")
    result = run_intake_gate(
        source,
        output_path=sandbox / "gate_out.dcm",
        index_path=sandbox / "index.json",
        manifest_path=sandbox / "manifest.json",
    )
    assert result["status"] == "PASS"
    assert result["case_id"] == synthetic_case_id()
    assert result["deidentification_status"] == "DEIDENTIFIED"
    assert result["pixel_phi_status"] == "PASS_SYNTHETIC"
    assert result["integrity_status"] == "INTEGRITY_OK"
    assert result["duplicate_status"] == "UNIQUE"
    assert result["clinical_03_written"] is False
    assert (sandbox / "manifest.json").is_file()


def test_11_corrupted_dicom_rejection(sandbox: Path) -> None:
    bad = sandbox / "corrupt.dcm"
    bad.write_bytes(b"this is not a dicom file")
    result = run_intake_gate(
        bad,
        output_path=sandbox / "corrupt_out.dcm",
        index_path=sandbox / "corrupt_index.json",
        register_index=False,
    )
    assert result["status"] == "BLOCKED"
    assert "unreadable" in result["reason"]


def test_12_missing_pixeldata_rejection(sandbox: Path) -> None:
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = DX_SOP_CLASS
    file_meta.MediaStorageSOPInstanceUID = SYNTHETIC_SOP_UID
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = SYNTHETIC_IMPL_UID
    ds = Dataset()
    ds.file_meta = file_meta
    ds.SOPClassUID = DX_SOP_CLASS
    ds.SOPInstanceUID = SYNTHETIC_SOP_UID
    ds.PatientName = "SYNTHETIC_TEST"
    ds.ImageComments = SYNTHETIC_MARKER
    ds.SeriesDescription = "SYNTHETIC_DRY_RUN"
    ds.Modality = "DX"
    ds.Rows = 8
    ds.Columns = 8
    path = sandbox / "no_pixels.dcm"
    ds.save_as(str(path), enforce_file_format=True)
    result = run_intake_gate(
        path,
        output_path=sandbox / "no_pixels_out.dcm",
        index_path=sandbox / "no_pixels_index.json",
        register_index=False,
    )
    assert result["status"] == "BLOCKED"
    assert "pixel" in result["reason"]


def test_pixel_phi_never_auto_safe_for_non_synthetic() -> None:
    ds = Dataset()
    ds.PatientName = "NOT_A_MARKER"
    check = pixel_phi_check(ds, synthetic=False)
    assert check["status"] == "NOT_IMPLEMENTED"
    assert check["safe_for_clinical_use"] is False
