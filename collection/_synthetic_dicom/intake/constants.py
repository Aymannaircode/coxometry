"""Controlled vocabularies for the synthetic-only intake dry-run."""

from __future__ import annotations

TOOL_VERSION = "phase11c3-synthetic-intake-0.1.0"
PHASE11C4_TOOL_VERSION = "phase11c4-admission-gate-0.1.0"
SYNTHETIC_CASE_ID = "SYNTHETIC_R27_001"

# Phase 11C-4: never bypass. Real-patient import stays disabled.
REAL_PATIENT_IMPORT_DISABLED = True
BLOCKED_REAL_PATIENT_IMPORT_DISABLED = "BLOCKED_REAL_PATIENT_IMPORT_DISABLED"

ALLOWED_RADIOGRAPH_MODALITIES = ("DX", "CR")
FORBIDDEN_CASE_ID_FIELDS = (
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "AccessionNumber",
    "InstitutionName",
    "OtherPatientIDs",
    "StudyID",
)
OPEN_PHYSICIAN_DECISIONS = ("P-A1", "P-A7", "P-FOV", "P-TOL", "P-V1", "P-C10")
PROVENANCE_REQUIRED_FIELDS = (
    "Case_ID",
    "source_file_hash",
    "pixel_hash",
    "source_type",
    "modality",
    "rows",
    "columns",
    "pixel_spacing",
    "orientation",
    "deidentification_status",
    "metadata_phi_status",
    "pixel_phi_status",
    "integrity_status",
    "duplicate_status",
    "eligibility_status",
    "physician_review_status",
    "annotation_status",
    "qc_status",
    "tool_version",
    "timestamp",
)

SYNTHETIC_MARKER = "SYNTHETIC_FIXTURE_NOT_CLINICAL"
SYNTHETIC_PATIENT_NAME = "SYNTHETIC_TEST"
SYNTHETIC_PATIENT_ID = "SYNTHETIC_001"
SYNTHETIC_INSTITUTION = "SYNTHETIC_INSTITUTION"
SYNTHETIC_ACCESSION = "SYNTH-ACC-0001"
SYNTHETIC_BIRTHDATE = "19000101"
SYNTHETIC_STUDY_DATE = "20000101"
SYNTHETIC_STUDY_ID = "SYNTH-STUDY-1"
SYNTHETIC_REFERRER = "SYNTHETIC_REFERRER"
SYNTHETIC_PERFORMER = "SYNTHETIC_PERFORMER"
SYNTHETIC_OPERATOR = "SYNTHETIC_OPERATOR"
SYNTHETIC_OTHER_ID = "SYNTHETIC_OTHER_001"
SYNTHETIC_OTHER_NAME = "SYNTHETIC_OTHER_NAME"

# Fixed, obviously non-clinical UIDs (numeric, reproducible).
SYNTHETIC_STUDY_UID = "1.2.826.0.1.3680043.10.541.113.1"
SYNTHETIC_SERIES_UID = "1.2.826.0.1.3680043.10.541.113.2"
SYNTHETIC_SOP_UID = "1.2.826.0.1.3680043.10.541.113.3"
SYNTHETIC_IMPL_UID = "1.2.826.0.1.3680043.10.541.113.99"

DX_SOP_CLASS = "1.2.840.10008.5.1.4.1.1.1.1"

SENSITIVE_TAGS = (
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientSex",
    "AccessionNumber",
    "StudyID",
    "InstitutionName",
    "InstitutionAddress",
    "ReferringPhysicianName",
    "PerformingPhysicianName",
    "OperatorsName",
    "OtherPatientIDs",
    "OtherPatientNames",
)

UID_TAGS = ("StudyInstanceUID", "SeriesInstanceUID", "SOPInstanceUID")

GEOMETRY_TAGS = (
    "SOPClassUID",
    "Modality",
    "Rows",
    "Columns",
    "PixelSpacing",
    "PhotometricInterpretation",
    "BitsAllocated",
    "BitsStored",
    "HighBit",
    "PixelRepresentation",
    "SamplesPerPixel",
    "RescaleSlope",
    "RescaleIntercept",
    "PatientOrientation",
    "ImageOrientationPatient",
)

FORBIDDEN_PATH_MARKERS = (
    "bassin",
    "yolo_pose_new_26",
    "yolo_pose_remediation_v1",
    "annotation_pilot",
    "runs",
)
