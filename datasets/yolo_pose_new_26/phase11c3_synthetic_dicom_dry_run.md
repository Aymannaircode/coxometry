# PHASE 11C-3

**Date:** 2026-09-04  
**Mode:** SAFE SYNTHETIC DICOM INTAKE IMPLEMENTATION + DRY-RUN  
**No clinical DICOM opened. No bassin/ read. No package installed.**

Predecessor: Phase 11C-2 `PHASE_11C2_NOT_READY`.

**Final verdict:** `PHASE_11C3_SYNTHETIC_DRY_RUN_PASS`  
**REAL_PATIENT_IMPORT = NO-GO**  
**TRAINING = NO-GO**  
**R26_PROMOTION = NO-GO**  
**PRODUCTION_MODEL_CHANGE = NO-GO**  
**CLINICAL_VALIDATION = NO-GO**

---

## Scope

Build the **minimum isolated technical pipeline** that can ingest a **synthetic / phantom DICOM**, de-identify it fail-closed, hash it, and record provenance.

This phase does **not** import real patients, allocate real `R27_*` IDs, write into `collection/03_DEIDENTIFIED`, or authorize the next clinical intake phase.

---

## Safety constraints

| Constraint | Observed |
|------------|----------|
| No real DICOM from `bassin/` | Path gate refuses any path outside `collection/_synthetic_dicom/` **before** `dcmread` |
| B26 / remediation_v1 / R26 / V5 / labels | Not modified (hashes MATCH after) |
| Flutter / FastAPI production / `mvp_geometry` | Not modified |
| No training / no new YOLO dataset / no v2 tree | `yolo_pose_remediation_v2` still ABSENT |
| No real Case ID | Only `SYNTHETIC_R27_001`; `allocate_clinical_case_id()` returns **BLOCKED** |
| No network / PACS / installs | None |
| Clinical `03_DEIDENTIFIED` | **0** files written (`clinical_03_written: false`) |

If a step had required a real patient DICOM, the rule was STOP / BLOCKED. No such step was taken.

---

## Existing dependencies

Inspected **before** creating files. Nothing installed.

| Item | Result |
|------|--------|
| Python | 3.11.9 (`.venv\Scripts\python.exe`) |
| pydicom | **YES** 3.0.2 |
| pytest | **YES** 9.1.1 |
| numpy | YES (already in venv) |
| easyocr / pytesseract / Tesseract | **NO** — pixel PHI OCR remains `NOT_IMPLEMENTED` |
| `deid` / `dicomanonymizer` / radstract (as project tool) | Not used |
| `collection/` 10-stage tree | Present, empty of clinical files |
| Existing clinical DICOM scripts (`dicom_render.py`, Step D) | **Not executed, not modified** |

---

## Synthetic fixture

Created only under `collection/_synthetic_dicom/`.

| Field | Value |
|-------|--------|
| Path | `collection/_synthetic_dicom/fixtures/synthetic_r27_001.dcm` (copy in `input/`) |
| Marker | `ImageComments = SYNTHETIC_FIXTURE_NOT_CLINICAL` + `.SYNTHETIC.txt` sidecar |
| Image | 128×128 uint16 geometric phantom (gradient + square + bar). **Not** a medical image. |
| PatientName / PatientID | `SYNTHETIC_TEST` / `SYNTHETIC_001` |
| Institution / accession / DOB | Fictitious `SYNTHETIC_*` values |
| UIDs | Fixed numeric `1.2.826.0.1.3680043.10.541.113.{1,2,3}` |
| SHA256 source/fixture | `010ea9df7e5bb67b032de95ea5852beb60ce1ea2b0c7f5e2bc666eafdb4c06de` |

---

## De-identification

Module: `collection/_synthetic_dicom/intake/deidentify.py`

| Behaviour | Result on synthetic fixture |
|-----------|-----------------------------|
| Read source, never overwrite it | Source hash unchanged |
| Detect sensitive tags | PatientName, PatientID, PatientBirthDate, PatientSex, AccessionNumber, StudyID, InstitutionName, InstitutionAddress, physician/operator names, OtherPatientIDs/Names |
| Remove those tags | Residual list **empty** |
| Replace Study/Series/SOP UIDs | Deterministic research UIDs from `generate_uid(entropy_srcs=[phase11c3-deid, SYNTHETIC_R27_001, kind])` |
| Preserve PixelData / Rows / Columns / spacing / photometric / bits | INTEGRITY_OK |
| Status | **DEIDENTIFIED** |
| Output | `collection/_synthetic_dicom/output/SYNTHETIC_R27_001_deidentified.dcm` |
| Output SHA256 | `3b44e8d5aa5950f4cd3b6e366272c7c29ec266ec7416489a8812fa0e0b1919c5` |

Any residual tag, UID leak, missing PixelData, or integrity fail → **BLOCKED** (no DEIDENTIFIED claim).

---

## Pixel PHI check

`pixel_phi_check()`:

| Input | status | `safe_for_clinical_use` |
|-------|--------|-------------------------|
| Synthetic / phantom marker | `PASS_SYNTHETIC` | **False** |
| Non-synthetic | `NOT_IMPLEMENTED` | **False** |

No OCR was implemented and none was faked. A real case **cannot** be declared pixel-safe by this module.

**Limitations:** metadata wipe ≠ pixel PHI clearance for clinical files. Visual/OCR certification is still missing (11C-2 blocker unchanged for real data).

---

## Image integrity

Compared before vs after de-id:

| Control | Synthetic result |
|---------|------------------|
| DICOM readable | YES |
| Modality | DX preserved |
| Rows / Columns | 128 / 128 unchanged |
| PixelSpacing | 0.2 / 0.2 unchanged |
| PhotometricInterpretation | MONOCHROME2 |
| BitsAllocated / BitsStored / PixelRepresentation | 16 / 16 / 0 |
| PixelData hash | identical (see SHA256) |
| RescaleSlope/Intercept | absent both sides |
| Orientation | PatientOrientation preserved |
| Unexpected geometry change | none → **INTEGRITY_OK** |

---

## SHA256

| Object | SHA256 |
|--------|--------|
| Source / fixture file | `010ea9df7e5bb67b032de95ea5852beb60ce1ea2b0c7f5e2bc666eafdb4c06de` |
| De-identified file | `3b44e8d5aa5950f4cd3b6e366272c7c29ec266ec7416489a8812fa0e0b1919c5` |
| PixelData **before** | `8c426a73d66fda0f60b17866613e2ad4e30efbea2a6663f20725feecf9d1b5b7` |
| PixelData **after** | `8c426a73d66fda0f60b17866613e2ad4e30efbea2a6663f20725feecf9d1b5b7` |

File hashes differ (tags/UIDs changed). Pixel hashes match.

---

## Duplicate detection

Local index only: `collection/_synthetic_dicom/reports/synthetic_duplicate_index.json`.

Does **not** scan B26, R26, `bassin/`, or YOLO trees.

| Class | Tested |
|-------|--------|
| Same source file hash | `EXACT_FILE` |
| Same PixelData hash | `EXACT_PIXEL` |
| Same synthetic study UID | `SAME_STUDY` |
| First dry-run | `UNIQUE` |

A second promotion of the same fixture through the gate is **BLOCKED** (`duplicate_EXACT_FILE`).

---

## Fail-closed gate

`run_intake_gate()` states: `PASS` / `BLOCKED` / `REVIEW`.

| Case | Status |
|------|--------|
| Official synthetic fixture | **PASS** |
| Path under `bassin/` (not opened) | **BLOCKED** |
| Corrupted bytes | **BLOCKED** (`unreadable_dicom`) |
| Missing PixelData | **BLOCKED** (`missing_pixel_data`) |
| `pixel_phi_check` `NOT_IMPLEMENTED` | **REVIEW** (non-synthetic path; not used for clinical files) |
| Real Case ID allocator | **BLOCKED** |
| Duplicate fixture | **BLOCKED** |

`PASS` means the case **would be allowed** to enter `03_DEIDENTIFIED` *conceptually*. The clinical folder was **not** written.

---

## Provenance manifest

`collection/_synthetic_dicom/reports/SYNTHETIC_R27_001_provenance.json`

Contains: Case_ID, source/deidentified/pixel hashes, source_type, synthetic=true, modality, rows, columns, pixel_spacing, orientation, deidentification_status, pixel_phi_check, integrity_status, duplicate_status, eligibility_status=`SYNTHETIC_DRY_RUN_ONLY`, created_at, tool_version.

No real personal data.

---

## Tests

Command: `.venv\Scripts\python.exe -m pytest collection/_synthetic_dicom/tests -q`

**13 passed / 0 failed** (12 required + 1 extra: non-synthetic pixel check never auto-safe).

| # | Test | Result |
|---|------|--------|
| 1 | synthetic DICOM creation | **PASS** |
| 2 | metadata PHI detection | **PASS** |
| 3 | metadata de-identification | **PASS** |
| 4 | source immutability | **PASS** |
| 5 | PixelData preservation | **PASS** |
| 6 | Rows/Columns preservation | **PASS** |
| 7 | SHA256 generation | **PASS** |
| 8 | duplicate detection | **PASS** |
| 9 | fail-closed (clinical path + real Case ID) | **PASS** |
| 10 | successful synthetic gate | **PASS** |
| 11 | corrupted DICOM rejection | **PASS** |
| 12 | missing PixelData rejection | **PASS** |
| extra | pixel PHI never auto-safe | **PASS** |

Official dry-run (`run_dry_run.py`): **PASS**.

---

## Protected assets verification

Hashes captured **before** implementation and recomputed **after** dry-run.

| Asset | After |
|-------|--------|
| `datasets/yolo_pose_new_26/data.yaml` | **MATCH** `aae42843…8609e8` |
| `datasets/yolo_pose_new_26/meta/split.json` | **MATCH** `011fa8ff…de654b3` |
| `datasets/yolo_pose_new_26/meta/source_mapping.csv` | **MATCH** `a12a4cc7…afb2eb4b` |
| `datasets/yolo_pose_remediation_v1/meta/split.json` | **MATCH** `1145f726…4fdbc5` |
| `datasets/yolo_pose_remediation_v1/meta/copy_manifest.json` | **MATCH** `97d1fc1b…0d37d98` |
| R26_01 / R26_06 / worklist | **MATCH** (11B hashes) |
| V5 `best_it.pt` | **MATCH** `2e3d3e48…b257f6` |
| `backend/app/services/analyze.py` | **MATCH** |
| `backend/app/api/routes/analyze.py` | **MATCH** |

`mvp_geometry/measurements.py`, `mvp_geometry/__init__.py`, `mobile/pubspec.yaml` were not edited (present; not part of this write set).

**Protected assets unchanged = YES**

---

## Limitations

1. Pipeline is **synthetic-only**. Real DICOMs are refused by path + marker checks.  
2. Pixel PHI OCR is **NOT_IMPLEMENTED**. `PASS_SYNTHETIC` is not a clinical pixel pass.  
3. No HMAC / restricted linkage for real hospital IDs (correctly unused).  
4. Duplicate index does not include B26/R26 (by design this phase).  
5. Compressed-transfer-syntax codecs remain incomplete in the venv (irrelevant for this uncompressed phantom).  
6. Physician gates P-A1 / P-A7 / P-FOV / P-TOL / P-V1 / P-C10 remain **OPEN**.  
7. `eligibility_status` is `SYNTHETIC_DRY_RUN_ONLY`, not `ELIGIBLE`.

---

## Blockers

Still blocking **real** intake (unchanged in intent from 11C-2):

- REAL_PATIENT_IMPORT  
- Pixel PHI verification for clinical images  
- Legal/consent basis (E9)  
- Real Case ID allocator (explicitly BLOCKED)  
- Patient-level index vs B26/R26  
- Physician-gated medical decisions  
- R26 promotion / training / production model change  

This phase **does not** lift those blockers.

---

## Next safe step

Do **not** import real DICOMs automatically.

A later explicit phase may: review this isolated module; decide whether a **synthetic-negative** fixture (planted burned-in text) is needed; keep clinical files out of `collection/03_DEIDENTIFIED` until PIXEL_CHECK is real.

**Do not start real import in this session.**

---

## Verdict

# **PHASE_11C3_SYNTHETIC_DRY_RUN_PASS**

The isolated technical pipeline works on a phantom DICOM. That is the only claim.

| Gate | Status |
|------|--------|
| **REAL_PATIENT_IMPORT** | **NO-GO** |
| **TRAINING** | **NO-GO** |
| **R26_PROMOTION** | **NO-GO** |
| **PRODUCTION_MODEL_CHANGE** | **NO-GO** |
| **CLINICAL_VALIDATION** | **NO-GO** |

---

*End of Phase 11C-3. STOP — no real DICOM import.*
