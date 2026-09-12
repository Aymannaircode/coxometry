"""Security: the 11C-4 gate cannot touch protected clinical/training assets."""

from __future__ import annotations

from pathlib import Path

import pytest

from intake.case_id import allocate_clinical_case_id
from intake.constants import BLOCKED_REAL_PATIENT_IMPORT_DISABLED, SYNTHETIC_CASE_ID
from intake.duplicate_index import DuplicateIndex
from intake.generate_synthetic_dicom import write_clean_synthetic_dicom
from intake.hashing import sha256_file
from intake.paths import ClinicalPathError, package_root
from intake.safety_lock import refuse_protected_write, scan_clinical_inbox
from intake.admission import admission_gate


REPO = Path(__file__).resolve().parents[3]


def _sandbox(tmp_path: Path) -> Path:
    root = package_root() / "reports" / "_pytest_tmp" / tmp_path.name
    root.mkdir(parents=True, exist_ok=True)
    return root


def _hash_if_exists(path: Path) -> str | None:
    if not path.is_file():
        return None
    return sha256_file(path)


def test_cannot_write_b26(tmp_path: Path) -> None:
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "sec_b26.dcm")
    target = REPO / "datasets" / "yolo_pose_new_26" / "images" / "train" / "GATE_MUST_NOT_WRITE.dcm"
    before = _hash_if_exists(REPO / "datasets" / "yolo_pose_new_26" / "data.yaml")
    existed = target.exists()
    result = admission_gate(
        source,
        {"case_id": SYNTHETIC_CASE_ID, "output_path": target, "manifest_path": target},
    )
    assert result["status"] == "BLOCKED"
    assert target.exists() is existed
    assert _hash_if_exists(REPO / "datasets" / "yolo_pose_new_26" / "data.yaml") == before
    with pytest.raises(ClinicalPathError):
        refuse_protected_write(target)


def test_cannot_write_remediation_v1(tmp_path: Path) -> None:
    target = REPO / "datasets" / "yolo_pose_remediation_v1" / "meta" / "GATE_MUST_NOT_WRITE.json"
    split = REPO / "datasets" / "yolo_pose_remediation_v1" / "meta" / "split.json"
    before = _hash_if_exists(split)
    existed = target.exists()
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "sec_v1.dcm")
    result = admission_gate(
        source,
        {"case_id": SYNTHETIC_CASE_ID, "manifest_path": target},
    )
    assert result["status"] == "BLOCKED"
    assert target.exists() is existed
    assert _hash_if_exists(split) == before
    with pytest.raises(ClinicalPathError):
        refuse_protected_write(target)


def test_cannot_modify_r26(tmp_path: Path) -> None:
    r26 = REPO / "annotation_pilot" / "annotations" / "remediation_v1" / "R26_01.json"
    before = _hash_if_exists(r26)
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "sec_r26.dcm")
    result = admission_gate(
        source,
        {"case_id": SYNTHETIC_CASE_ID, "manifest_path": r26, "output_path": r26},
    )
    assert result["status"] == "BLOCKED"
    assert _hash_if_exists(r26) == before
    with pytest.raises(ClinicalPathError):
        refuse_protected_write(r26)


def test_cannot_create_real_r27() -> None:
    clinical = allocate_clinical_case_id()
    assert clinical["status"] == "BLOCKED"
    assert clinical["case_id"] is None
    collection = REPO / "collection"
    created = list(collection.rglob("R27_*"))
    assert created == []
    result = admission_gate(
        Path("C:/Users/g/OneDrive/Desktop/Projet-Ayman/collection/03_DEIDENTIFIED/R27_001.dcm"),
        {"case_id": "R27_001"},
    )
    assert result["status"] == "BLOCKED"
    assert result["reason"] == BLOCKED_REAL_PATIENT_IMPORT_DISABLED
    assert result.get("real_r27_allocated") is False
    assert list(collection.rglob("R27_*")) == []


def test_cannot_access_bassin_automatically() -> None:
    with pytest.raises(ClinicalPathError) as exc:
        scan_clinical_inbox()
    assert BLOCKED_REAL_PATIENT_IMPORT_DISABLED in str(exc.value)
    result = admission_gate(
        Path("C:/Users/g/OneDrive/Desktop/Projet-Ayman/bassin/a_annoter/not_opened.dcm"),
        {"case_id": SYNTHETIC_CASE_ID},
    )
    assert result["status"] == "BLOCKED"
    assert result["reason"] == BLOCKED_REAL_PATIENT_IMPORT_DISABLED
    for item in result["checks"]:
        assert item["details"].get("evaluated") is False


def test_no_synthetic_write_into_training_set(tmp_path: Path) -> None:
    train_img = REPO / "datasets" / "yolo_pose_new_26" / "images" / "train"
    train_lbl = REPO / "datasets" / "yolo_pose_new_26" / "labels" / "train"
    img_before = sorted(p.name for p in train_img.iterdir() if p.is_file()) if train_img.is_dir() else []
    lbl_before = sorted(p.name for p in train_lbl.iterdir() if p.is_file()) if train_lbl.is_dir() else []
    sandbox = _sandbox(tmp_path)
    source = write_clean_synthetic_dicom(sandbox / "sec_train.dcm")
    result = admission_gate(
        source,
        {
            "case_id": SYNTHETIC_CASE_ID,
            "output_path": train_img / "SYNTHETIC_MUST_NOT_LAND.dcm",
            "manifest_path": train_lbl / "SYNTHETIC_MUST_NOT_LAND.txt",
        },
    )
    assert result["status"] == "BLOCKED"
    assert result["would_enter_03_deidentified"] is False if "would_enter_03_deidentified" in result else True
    img_after = sorted(p.name for p in train_img.iterdir() if p.is_file()) if train_img.is_dir() else []
    lbl_after = sorted(p.name for p in train_lbl.iterdir() if p.is_file()) if train_lbl.is_dir() else []
    assert img_after == img_before
    assert lbl_after == lbl_before


def test_duplicate_index_refuses_real_records() -> None:
    index = DuplicateIndex(synthetic_only=True)
    with pytest.raises(ClinicalPathError):
        index.register_synthetic({"synthetic": False, "source_file_hash": "abc"})
    with pytest.raises(ClinicalPathError):
        DuplicateIndex(synthetic_only=False)
