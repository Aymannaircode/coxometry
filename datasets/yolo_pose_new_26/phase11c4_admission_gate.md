# PHASE 11C-4

**Date:** 2026-09-04  
**Mode:** REAL DICOM ADMISSION GATE / FAIL-CLOSED PREPARATION  
**No clinical DICOM opened. No bassin/ scan. No package installed. No network/PACS call.**

Predecessor: Phase 11C-3 `PHASE_11C3_SYNTHETIC_DRY_RUN_PASS`.

**Final verdict:** `PHASE_11C4_PASS`

REAL_PATIENT_IMPORT = NO-GO  
TRAINING = NO-GO  
R27_ALLOCATION = NO-GO  
R26_PROMOTION = NO-GO  
PRODUCTION_MODEL_CHANGE = NO-GO  
CLINICAL_VALIDATION = NO-GO

---

## Scope

Build the **software admission gate** that will later control a real DICOM **before** it may enter the collection pipeline.

This phase does **not**:

- import, copy, open, analyze, or modify a real patient DICOM
- create a real `R27_*` case
- write into `collection/03_DEIDENTIFIED`
- allocate a clinical Case ID
- change B26, `remediation_v1`, R26, V5, labels, Flutter, FastAPI production, or `mvp_geometry`
- start training

It only adds isolated code, synthetic fixtures, synthetic tests, and this report.

---

## Safety lock

`REAL_PATIENT_IMPORT_DISABLED = true` is a hard constant (`intake/constants.py`, `intake/safety_lock.py`).

| Rule | Behaviour |
|------|-----------|
| Lock value | `True` — cannot be turned off by context |
| `force_enable_real_import` / `REAL_PATIENT_IMPORT_DISABLED=False` | Still **BLOCKED** |
| Path outside `collection/_synthetic_dicom/` | `BLOCKED_REAL_PATIENT_IMPORT_DISABLED` **before** `dcmread` |
| Path containing `bassin/`, B26, `remediation_v1`, `03_DEIDENTIFIED`, `01_INBOX_RAW` | Same lock, no file open |
| `scan_clinical_inbox()` | Raises `BLOCKED_REAL_PATIENT_IMPORT_DISABLED` |
| Write outside the synthetic sandbox | Refused |

There is no bypass.

---

## Gate architecture

Public interface:

```text
admission_gate(input_path, context) -> {status, reason, checks[], ...}
```

Module: `collection/_synthetic_dicom/intake/admission.py`

States: **PASS** / **REVIEW** / **BLOCKED**.

Fail-closed:

- missing mandatory tag or hash → **BLOCKED** (never PASS)
- missing provenance → **BLOCKED**
- non-synthetic path → **BLOCKED_REAL_PATIENT_IMPORT_DISABLED**
- each of the 20 checks returns `{check_name, status, reason, details}`

`PIXEL_PHI_CHECK` is the only **REVIEW** that does not veto an otherwise valid **synthetic** software PASS. That REVIEW is never rewritten to PASS by a metadata result.

Supporting modules:

| Module | Role |
|--------|------|
| `safety_lock.py` | Import lock + protected-write refusal |
| `admission_checks.py` | 20 structured checks |
| `check_result.py` | Result schema |
| `duplicate_index.py` | `DuplicateIndex` (synthetic only) |
| `eligibility.py` | `EligibilityGate` (no clinical thresholds) |
| `case_id_policy.py` | `SYNTHETIC_R27_001` only; hospital IDs rejected |
| `provenance.py` | 11C-4 manifest schema (no identity) |

The 11C-3 `run_intake_gate()` dry-run is unchanged.

---

## Metadata PHI

`METADATA_PHI_CHECK` uses `detect_sensitive_metadata()` (PatientName, PatientID, DOB, accession, institution, physician/operator names, private tags).

| Input | Check status |
|-------|----------------|
| Clean synthetic (identifying tags removed) | **PASS** |
| Synthetic fixture still carrying `PatientName` / `PatientID` / DOB / hospital tags | **BLOCKED** (`metadata_phi_present`) |

A metadata **PASS** does **not** change `PIXEL_PHI_CHECK`.

---

## Pixel PHI

`METADATA_PHI_CHECK` and `PIXEL_PHI_CHECK` are independent.

| Rule | Implementation |
|------|----------------|
| OCR | **NOT_IMPLEMENTED** — never faked |
| If not actually verified | `PIXEL_PHI_CHECK` = **REVIEW** (synthetic) or **BLOCKED** (non-synthetic / no dataset) |
| Metadata PASS → pixel PASS | **Forbidden** (`inherited_from_metadata: false`) |
| `safe_for_clinical_use` | Always **False** |

`PASS_SYNTHETIC` from the 11C-3 helper is **not** accepted as a clinical pixel pass by this gate.

---

## DICOM integrity

Mandatory presence / validity:

1. DICOM readable  
2. Modality (`DX` / `CR` only for this software gate)  
3. Rows  
4. Columns  
5. PixelData  
6. PixelSpacing (two positive values)  
7. PhotometricInterpretation  
8. BitsAllocated  
9. BitsStored  
10. PixelRepresentation  

Optional if present: RescaleSlope/Intercept, orientation.

Rows/Columns must match `pixel_array.shape`. Mismatch → `INTEGRITY_FAIL` / **BLOCKED**.

No clinical spacing or FOV cutoff is invented.

---

## SHA256

| Object | Check |
|--------|--------|
| Source file bytes | `SOURCE_SHA256` — required, 64 hex chars |
| PixelData | `PIXEL_SHA256` — required if pixels exist |
| Source after gate | Compared to before → immutability |

The gate never overwrites the source file.

---

## Duplicate protection

`DuplicateIndex` (synthetic-only):

- source hash  
- pixel hash  
- study UID  
- series UID  
- patient pseudonym (reserved; unused on real data)

`synthetic_only=False` raises. A record with `synthetic=False` or a non-synthetic `source_type` is refused.

No B26 / R26 / `bassin/` index is built.

---

## Leakage protection

| Control | Result |
|---------|--------|
| Case ID ← PatientName / PatientID / DOB / accession / institution | **BLOCKED** |
| Real `R27_*` allocator | Stays **BLOCKED** |
| Only allowed fixture ID | `SYNTHETIC_R27_001` |
| Indexing real records | Refused |
| Writing into B26 / v1 / R26 / training images-labels / `03_DEIDENTIFIED` | Refused |
| Automatic `bassin/` walk | Disabled |

---

## Eligibility gate

`EligibilityGate` conceptual boxes (no numeric clinical thresholds):

- adult  
- pelvis/hip radiograph  
- compatible projection  
- exploitable image  
- no untreated metadata PHI  
- unique patient  
- not a duplicate  
- valid DICOM  
- provenance available  

Missing box → **REVIEW**. Failed box → **BLOCKED**.  
A **PASS** here means `synthetic_conceptual_eligibility_only`, not clinical eligibility.

Physician items remain **OPEN**: P-A1, P-A7, P-FOV, P-TOL, P-V1, P-C10.  
The 0.5 × head-diameter FSD cutoff is **not** applied.

---

## Provenance

`build_admission_manifest()` public fields (no identity):

Case_ID, source_file_hash, pixel_hash, source_type, modality, rows, columns, pixel_spacing, orientation, deidentification_status, metadata_phi_status, pixel_phi_status, integrity_status, duplicate_status, eligibility_status, physician_review_status, annotation_status, qc_status, tool_version, timestamp.

Forbidden in the manifest: PatientName, PatientID, DOB, accession, institution, physician names.

If provenance is omitted (`omit_provenance=True`) → **BLOCKED**.

`clinical_03_written` is always **false**. `would_enter_03_deidentified` is **false**.

---

## Synthetic test matrix

Command: `.venv\Scripts\python.exe -m pytest collection/_synthetic_dicom/tests -q`

**34 passed / 0 failed** (13 existing 11C-3 tests unchanged + 21 new 11C-4 tests).

| ID | Case | Expected | Observed |
|----|------|----------|----------|
| A | Valid clean synthetic DICOM | PASS | **PASS** |
| B | Corrupted bytes | BLOCKED | **BLOCKED** |
| C | Missing PixelData | BLOCKED | **BLOCKED** |
| D | PHI metadata present | BLOCKED/REVIEW | **BLOCKED** |
| E | Pixel PHI not verified | NOT PASS | **REVIEW** (not PASS) |
| F | Duplicate synthetic case | BLOCKED/REVIEW | **BLOCKED** |
| G | Missing provenance | BLOCKED | **BLOCKED** |
| H | Invalid modality (`CT`) | BLOCKED/REVIEW | **BLOCKED** |
| I | Geometry mismatch (Rows ≠ pixels) | BLOCKED/REVIEW | **BLOCKED** |
| J | Case ID = PatientID | BLOCKED | **BLOCKED** |
| K | Source immutability | PASS | **PASS** (hash unchanged) |
| L | Fail-closed (missing Rows) | never PASS | **BLOCKED** |

Extra software-lock tests: real `bassin/` path blocked without open; lock cannot be forced off.

---

## Security tests

| Attempt | Result |
|---------|--------|
| Write into B26 (`images/train`) | **BLOCKED** — file not created; `data.yaml` hash unchanged |
| Write into `remediation_v1/meta` | **BLOCKED** — `split.json` hash unchanged |
| Modify `R26_01.json` | **BLOCKED** — hash unchanged |
| Create real `R27_001` / write `03_DEIDENTIFIED/R27_001.dcm` | **BLOCKED**; `allocate_clinical_case_id()` still BLOCKED; **0** `R27_*` artifacts |
| Automatic `bassin/` access | `scan_clinical_inbox()` raises; path gate does not `dcmread` |
| Write synthetic bytes into B26 train images/labels | **BLOCKED** — directory listings unchanged (21/5) |

---

## Limitations

1. The gate is **synthetic-only**. A real path is refused before any DICOM read.  
2. Pixel PHI OCR is still **NOT_IMPLEMENTED**. `PIXEL_PHI_CHECK` cannot be PASS.  
3. Overall synthetic PASS does **not** mean pixel PHI is clinically cleared.  
4. Eligibility PASS is conceptual / synthetic, not physician-approved.  
5. `DuplicateIndex` does not contain B26/R26/real patients.  
6. No HMAC patient-pseudonym linkage.  
7. No write into `collection/03_DEIDENTIFIED` even on synthetic PASS.  
8. Compressed-transfer-syntax codecs remain out of scope.

---

## Open decisions

Still **OPEN** — no default invented:

- **P-A1** ASL sourcil-vs-rim exemplars  
- **P-A7** FSP accepted-level exemplars  
- **P-FOV** FSD numeric cutoff vs directional-only (0.5 × head diameter **not** applied)  
- **P-TOL** inter-annotator tolerance  
- **P-V1** whether `v=1` is allowed  
- **P-C10** acceptable clinical landmark/angle error  

---

## Blockers

Unchanged for any **real** intake:

- REAL_PATIENT_IMPORT  
- Clinical pixel-PHI verification  
- Legal/consent basis (E9)  
- Real Case ID allocator (`R27_*`)  
- Patient-level index vs B26/R26  
- Physician-gated medical decisions  
- R26 promotion / training / production model change  

This phase does **not** lift those blockers.

---

## Next safe step

Keep `REAL_PATIENT_IMPORT_DISABLED = true`.

A later explicit phase may review this gate with a clinician present, define a real pixel-PHI protocol, and only then consider a **manual**, consented, one-case import path.

**Do not import a real patient DICOM in this session.**

---

## Protected assets verification

Hashes captured before implementation and recomputed after tests. All **MATCH**.

| Asset | After |
|-------|--------|
| `datasets/yolo_pose_new_26/data.yaml` | **MATCH** `aae42843…8609e8` |
| `meta/split.json` | **MATCH** `011fa8ff…de654b3` |
| `meta/source_mapping.csv` | **MATCH** `a12a4cc7…afb2eb4b` |
| `yolo_pose_remediation_v1/meta/split.json` | **MATCH** `1145f726…4fdbc5` |
| `yolo_pose_remediation_v1/meta/copy_manifest.json` | **MATCH** `97d1fc1b…0d37d98` |
| R26_01 … R26_06 | **MATCH** (11C-1 hashes) |
| V5 `best_it.pt` | **MATCH** `2e3d3e48…b257f6` |
| `backend/app/services/analyze.py` | **MATCH** |
| `backend/app/api/routes/analyze.py` | **MATCH** |
| B26 images/labels train/val counts | **21 / 5 / 21 / 5** unchanged |
| Real `R27_*` | **0** |
| `yolo_pose_remediation_v2/` | still **ABSENT** |

Flutter / FastAPI production / `mvp_geometry` were not edited.

**Protected assets unchanged = YES**  
**Real patient access attempted = NO**

---

## Verdict

# **PHASE_11C4_PASS**

The isolated admission gate works on synthetic fixtures and refuses real paths. That is the only claim.

REAL_PATIENT_IMPORT = NO-GO  
TRAINING = NO-GO  
R27_ALLOCATION = NO-GO  
R26_PROMOTION = NO-GO  
PRODUCTION_MODEL_CHANGE = NO-GO  
CLINICAL_VALIDATION = NO-GO

---

*End of Phase 11C-4. STOP — no real DICOM import.*
