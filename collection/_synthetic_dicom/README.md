# Isolated SYNTHETIC DICOM intake (Phase 11C-3 / 11C-4)

**This tree is not a training dataset and is not a clinical inbox.**

It exists only to dry-run the future DICOM intake **on phantom / synthetic files**.

- Do not place real patient DICOMs here.
- Do not read `bassin/`.
- Do not copy B26 / R26 / YOLO images here.
- `SYNTHETIC_R27_001` is a dry-run ID only. Real `R27_*` allocation is **BLOCKED**.
- A PASS here does **not** authorize real-patient import.
- Phase 11C-4: `REAL_PATIENT_IMPORT_DISABLED = true`. `admission_gate()` refuses every non-synthetic path.

Authoritative reports:
- `datasets/yolo_pose_new_26/phase11c3_synthetic_dicom_dry_run.md`
- `datasets/yolo_pose_new_26/phase11c4_admission_gate.md`
