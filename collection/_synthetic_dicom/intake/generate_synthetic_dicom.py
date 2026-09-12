"""Create an obviously non-clinical phantom DICOM. Never uses real images."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian

from .constants import (
    SENSITIVE_TAGS,
    DX_SOP_CLASS,
    SYNTHETIC_ACCESSION,
    SYNTHETIC_BIRTHDATE,
    SYNTHETIC_IMPL_UID,
    SYNTHETIC_INSTITUTION,
    SYNTHETIC_MARKER,
    SYNTHETIC_OPERATOR,
    SYNTHETIC_OTHER_ID,
    SYNTHETIC_OTHER_NAME,
    SYNTHETIC_PATIENT_ID,
    SYNTHETIC_PATIENT_NAME,
    SYNTHETIC_PERFORMER,
    SYNTHETIC_REFERRER,
    SYNTHETIC_SERIES_UID,
    SYNTHETIC_SOP_UID,
    SYNTHETIC_STUDY_DATE,
    SYNTHETIC_STUDY_ID,
    SYNTHETIC_STUDY_UID,
)
from .paths import assert_synthetic_sandbox


def _phantom_pixels(rows: int = 128, columns: int = 128) -> np.ndarray:
    yy, xx = np.mgrid[0:rows, 0:columns]
    array = (xx * 80 + yy * 20).astype(np.uint16)
    array[32:96, 32:96] = 3500
    array[60:68, :] = 1200
    return array


def build_synthetic_dataset() -> Dataset:
    pixels = _phantom_pixels()
    rows, columns = pixels.shape

    file_meta = FileMetaDataset()
    file_meta.FileMetaInformationVersion = b"\x00\x01"
    file_meta.MediaStorageSOPClassUID = DX_SOP_CLASS
    file_meta.MediaStorageSOPInstanceUID = SYNTHETIC_SOP_UID
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = SYNTHETIC_IMPL_UID
    file_meta.ImplementationVersionName = "11C3SYNTH"

    ds = Dataset()
    ds.file_meta = file_meta
    ds.SOPClassUID = DX_SOP_CLASS
    ds.SOPInstanceUID = SYNTHETIC_SOP_UID
    ds.StudyInstanceUID = SYNTHETIC_STUDY_UID
    ds.SeriesInstanceUID = SYNTHETIC_SERIES_UID
    ds.Modality = "DX"
    ds.PatientName = SYNTHETIC_PATIENT_NAME
    ds.PatientID = SYNTHETIC_PATIENT_ID
    ds.PatientBirthDate = SYNTHETIC_BIRTHDATE
    ds.PatientSex = "O"
    ds.AccessionNumber = SYNTHETIC_ACCESSION
    ds.StudyID = SYNTHETIC_STUDY_ID
    ds.StudyDate = SYNTHETIC_STUDY_DATE
    ds.SeriesDate = SYNTHETIC_STUDY_DATE
    ds.InstitutionName = SYNTHETIC_INSTITUTION
    ds.InstitutionAddress = "100 SYNTHETIC ROAD"
    ds.ReferringPhysicianName = SYNTHETIC_REFERRER
    ds.PerformingPhysicianName = SYNTHETIC_PERFORMER
    ds.OperatorsName = SYNTHETIC_OPERATOR
    ds.OtherPatientIDs = SYNTHETIC_OTHER_ID
    ds.OtherPatientNames = SYNTHETIC_OTHER_NAME
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1
    ds.SeriesDescription = "SYNTHETIC_DRY_RUN"
    ds.ImageComments = SYNTHETIC_MARKER
    ds.Manufacturer = "PHASE11C3_SYNTHETIC"
    ds.BodyPartExamined = "PELVIS"
    ds.ViewPosition = "AP"
    ds.PatientOrientation = "A\\F"
    ds.Rows = rows
    ds.Columns = columns
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.PixelSpacing = [0.200, 0.200]
    ds.PixelData = pixels.tobytes()
    return ds


def build_clean_synthetic_dataset() -> Dataset:
    """Valid synthetic fixture with no identifying tags. Used by the 11C-4 gate."""
    ds = build_synthetic_dataset()
    for name in SENSITIVE_TAGS:
        if name in ds:
            del ds[name]
    ds.ImageComments = SYNTHETIC_MARKER
    ds.SeriesDescription = "SYNTHETIC_DRY_RUN"
    ds.Manufacturer = "PHASE11C4_SYNTHETIC"
    return ds


def write_clean_synthetic_dicom(path: Path) -> Path:
    dest = assert_synthetic_sandbox(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dataset = build_clean_synthetic_dataset()
    dataset.save_as(str(dest), enforce_file_format=True)
    marker = dest.with_suffix(".SYNTHETIC.txt")
    marker.write_text(
        "SYNTHETIC_FIXTURE_NOT_CLINICAL\nNot a patient. Not training data.\n",
        encoding="utf-8",
    )
    return dest


def write_synthetic_dicom(path: Path) -> Path:
    dest = assert_synthetic_sandbox(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dataset = build_synthetic_dataset()
    dataset.save_as(str(dest), enforce_file_format=True)
    marker = dest.with_suffix(".SYNTHETIC.txt")
    marker.write_text(
        "SYNTHETIC_FIXTURE_NOT_CLINICAL\nNot a patient. Not training data.\n",
        encoding="utf-8",
    )
    return dest
