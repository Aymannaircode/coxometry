"""Phase 11C-4 synthetic admission-gate matrix. No clinical DICOM is opened."""

from __future__ import annotations

from pathlib import Path

from pydicom import dcmread
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian

from intake.admission import admission_gate
from intake.constants import (
    BLOCKED_REAL_PATIENT_IMPORT_DISABLED,
    DX_SOP_CLASS,
    REAL_PATIENT_IMPORT_DISABLED,
    SYNTHETIC_CASE_ID,
    SYNTHETIC_IMPL_UID,
    SYNTHETIC_MARKER,
    SYNTHETIC_PATIENT_ID,
    SYNTHETIC_SOP_UID,
)
from intake.duplicate_index import DuplicateIndex
from intake.generate_synthetic_dicom import write_clean_synthetic_dicom, write_synthetic_dicom
from intake.hashing import sha256_file
from intake.paths import package_root


def _sandbox(tmp_path: Path) -> Path:
    root = package_root() / "reports" / "_pytest_tmp" / tmp_path.name
    root.mkdir(parents=True, exist_ok=True)
    return root


def _check(result: dict, name: str) -> dict:
    for item in result["checks"]:
        if item["check_name"] == name:
            return item
    raise AssertionError(f"missing check {name}")


def test_A_valid_synthetic_dicom_pass(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "valid.dcm")
    result = admission_gate(
        source,
        {
            "case_id": SYNTHETIC_CASE_ID,
            "source_type": "DICOM_DX_SYNTHETIC",
            "duplicate_index": DuplicateIndex(),
        },
    )
    assert result["status"] == "PASS"
    assert result["case_id"] == SYNTHETIC_CASE_ID
    assert result["REAL_PATIENT_IMPORT_DISABLED"] is True
    assert result["clinical_03_written"] is False
    assert _check(result, "METADATA_PHI_CHECK")["status"] == "PASS"
    assert _check(result, "PIXEL_PHI_CHECK")["status"] != "PASS"


def test_B_corrupted_dicom_blocked(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    bad = sandbox / "corrupt.dcm"
    bad.write_bytes(b"this is not a dicom file")
    result = admission_gate(bad, {"case_id": SYNTHETIC_CASE_ID})
    assert result["status"] == "BLOCKED"
    assert _check(result, "DICOM_READABLE")["status"] == "BLOCKED"


def test_C_missing_pixeldata_blocked(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = DX_SOP_CLASS
    file_meta.MediaStorageSOPInstanceUID = SYNTHETIC_SOP_UID
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = SYNTHETIC_IMPL_UID
    ds = Dataset()
    ds.file_meta = file_meta
    ds.SOPClassUID = DX_SOP_CLASS
    ds.SOPInstanceUID = SYNTHETIC_SOP_UID
    ds.ImageComments = SYNTHETIC_MARKER
    ds.SeriesDescription = "SYNTHETIC_DRY_RUN"
    ds.Modality = "DX"
    ds.Rows = 8
    ds.Columns = 8
    path = sandbox / "no_pixels.dcm"
    ds.save_as(str(path), enforce_file_format=True)
    result = admission_gate(path, {"case_id": SYNTHETIC_CASE_ID})
    assert result["status"] == "BLOCKED"
    assert _check(result, "PIXEL_DATA")["status"] == "BLOCKED"


def test_D_phi_metadata_present_blocked(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_synthetic_dicom(sandbox / "phi_meta.dcm")
    result = admission_gate(source, {"case_id": SYNTHETIC_CASE_ID})
    assert result["status"] in {"BLOCKED", "REVIEW"}
    assert result["status"] != "PASS"
    assert _check(result, "METADATA_PHI_CHECK")["status"] in {"BLOCKED", "REVIEW"}


def test_E_pixel_phi_not_verified_not_pass(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "pixel_phi.dcm")
    result = admission_gate(source, {"case_id": SYNTHETIC_CASE_ID})
    pixel = _check(result, "PIXEL_PHI_CHECK")
    assert pixel["status"] != "PASS"
    assert pixel["status"] in {"REVIEW", "BLOCKED"}
    assert _check(result, "METADATA_PHI_CHECK")["status"] == "PASS"
    assert pixel["details"]["inherited_from_metadata"] is False


def test_F_duplicate_synthetic_blocked(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "dup.dcm")
    index = DuplicateIndex()
    first = admission_gate(
        source,
        {
            "case_id": SYNTHETIC_CASE_ID,
            "duplicate_index": index,
            "register_index": True,
        },
    )
    assert first["status"] == "PASS"
    second = admission_gate(
        source,
        {"case_id": SYNTHETIC_CASE_ID, "duplicate_index": index},
    )
    assert second["status"] in {"BLOCKED", "REVIEW"}
    assert second["status"] != "PASS"
    assert _check(second, "DUPLICATE")["status"] in {"BLOCKED", "REVIEW"}


def test_G_missing_provenance_blocked(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "no_prov.dcm")
    result = admission_gate(
        source,
        {"case_id": SYNTHETIC_CASE_ID, "omit_provenance": True},
    )
    assert result["status"] == "BLOCKED"
    assert _check(result, "PROVENANCE")["status"] == "BLOCKED"


def test_H_invalid_modality_blocked(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "ct.dcm")
    ds = dcmread(str(source))
    ds.Modality = "CT"
    ds.save_as(str(source), enforce_file_format=True)
    result = admission_gate(source, {"case_id": SYNTHETIC_CASE_ID})
    assert result["status"] in {"BLOCKED", "REVIEW"}
    assert result["status"] != "PASS"
    assert _check(result, "MODALITY")["status"] in {"BLOCKED", "REVIEW"}


def test_I_geometry_mismatch_blocked(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "geom.dcm")
    ds = dcmread(str(source))
    ds.Rows = 64
    ds.save_as(str(source), enforce_file_format=True)
    result = admission_gate(source, {"case_id": SYNTHETIC_CASE_ID})
    assert result["status"] in {"BLOCKED", "REVIEW"}
    assert result["status"] != "PASS"
    assert result["integrity_status"] == "INTEGRITY_FAIL"


def test_J_case_id_using_patient_id_blocked(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_synthetic_dicom(sandbox / "patientid_case.dcm")
    result = admission_gate(source, {"case_id": SYNTHETIC_PATIENT_ID})
    assert result["status"] == "BLOCKED"
    assert _check(result, "CASE_ID_POLICY")["status"] == "BLOCKED"
    assert "PatientID" in _check(result, "CASE_ID_POLICY")["reason"]


def test_K_source_immutability_pass(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "immutable.dcm")
    before = sha256_file(source)
    result = admission_gate(source, {"case_id": SYNTHETIC_CASE_ID})
    assert result["status"] == "PASS"
    assert sha256_file(source) == before
    assert result["source_immutable"] is True


def test_L_fail_closed_missing_rows(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "norows.dcm")
    ds = dcmread(str(source))
    del ds.Rows
    ds.save_as(str(source), enforce_file_format=True)
    result = admission_gate(source, {"case_id": SYNTHETIC_CASE_ID})
    assert result["status"] != "PASS"
    assert result["status"] in {"BLOCKED", "REVIEW"}
    assert _check(result, "ROWS")["status"] != "PASS"


def test_real_path_blocked_without_opening() -> None:
    assert REAL_PATIENT_IMPORT_DISABLED is True
    target = Path("C:/Users/g/OneDrive/Desktop/Projet-Ayman/bassin/a_annoter/x.dcm")
    result = admission_gate(target, {"case_id": SYNTHETIC_CASE_ID})
    assert result["status"] == "BLOCKED"
    assert result["reason"] == BLOCKED_REAL_PATIENT_IMPORT_DISABLED
    assert result["case_id"] is None


def test_lock_cannot_be_bypassed(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "bypass.dcm")
    result = admission_gate(
        source,
        {
            "case_id": SYNTHETIC_CASE_ID,
            "force_enable_real_import": True,
            "REAL_PATIENT_IMPORT_DISABLED": False,
        },
    )
    assert result["status"] == "BLOCKED"
    assert result["reason"] == BLOCKED_REAL_PATIENT_IMPORT_DISABLED
