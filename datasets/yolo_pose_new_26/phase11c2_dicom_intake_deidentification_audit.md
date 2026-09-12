# PHASE 11C-2

**Date:** 2026-09-04  
**Mode:** READ-ONLY DICOM INTAKE / DE-IDENTIFICATION DRY-RUN AUDIT  
**No DICOM opened. No script executed. No package installed. No network call.**

Predecessor locks (terminology preserved, not reinterpreted):

- `datasets/yolo_pose_new_26/phase11a_annotation_protocol_audit.md`
- `datasets/yolo_pose_new_26/phase11b_collection_deidentification_protocol.md`
- `datasets/yolo_pose_new_26/phase11c0_collection_environment_audit.md`
- `datasets/yolo_pose_new_26/phase11c1_collection_infrastructure.md`

**Final verdict:** `PHASE_11C2_NOT_READY`  
**TRAINING = NO-GO**  
**REAL_PATIENT_IMPORT = NO-GO**  
**R26_PROMOTION = NO-GO**  
**DATASET_MODIFICATION = NO-GO**

---

## Scope

Audit whether the environment and **scripts required for a future DICOM intake** are correctly **defined**. Document a future de-identification specification. Do **not** import, process, or claim any real case is de-identified.

Questions covered:

1. Metadata to remove / anonymize  
2. Pixel + metadata de-identification rules  
3. Image resolution / geometric integrity  
4. SHA256  
5. Future pseudonymous Case ID  
6. Patient-level / duplicate / leakage  
7. Entry rules for `03_DEIDENTIFIED`  
8. Eligibility before physician review  
9. Provenance  
10. Fail-closed if any de-id step fails  

This phase does **not** convert DICOM → PNG, create Case IDs, create splits, or start a dry-run execution.

---

## Read-only guarantee

| Action | This phase |
|--------|------------|
| Real-patient import | **NOT DONE** |
| Clinical DICOM read / rewrite | **NOT DONE** |
| B26 / remediation_v1 / R26 / V5 / labels / images | **NOT MODIFIED** |
| New patient folder / annotation / split / training | **NOT CREATED** |
| Flutter / FastAPI / `mvp_geometry` | **NOT MODIFIED** |
| R26 promotion | **NOT DONE** |
| File deletion / external upload / PACS / network | **NOT DONE** |
| Install packages | **NOT DONE** |
| Create executables | **NOT DONE** |
| Execute `dicom_render.py`, Step D scripts, radstract, `/analyze` | **NOT DONE** |

Sample integrity after this audit (unchanged vs Phase 11B / 11C-1):

| Asset | SHA256 check |
|-------|----------------|
| `data.yaml` | **MATCH** `aae42843…8609e8` |
| `meta/split.json` | **MATCH** `011fa8ff…de654b3` |
| `R26_01.json` | **MATCH** `3b0fe094…f916e4` |
| V5 `best_it.pt` | **MATCH** `2e3d3e48…b257f6` |

`collection/` and `restricted/` contain **0** clinical files (`.dcm` / `.png` / `.jpg` / `.json`). `datasets/yolo_pose_remediation_v2/` still **ABSENT**. Any `R27_*` artifact: **0**.

**Sole artifact created:** this report.

---

## Existing environment

### Collection / restricted (from 11C-1)

Empty infrastructure exists and is **correctly separated** from training trees:

```
collection/{01_INBOX_RAW … 10_ARCHIVE}   .gitkeep + README + .gitignore
restricted/linkage/                      .gitkeep + README + .gitignore
```

No intake executable lives in either tree. No Case ID folders. No linkage table.

`datasets/yolo_pose_new_26/` remains the **frozen B26 training/report tree**. It must **not** be used as RAW inbox (11C-1). It contains historical audit reports and B26 `images/` / `labels/` only.

### Scripts that exist (project-owned) — audited, not executed

| Script | Role | De-identification? | Risk if executed now |
|--------|------|--------------------|----------------------|
| `annotation_pilot/manual_annotation_tool/dicom_render.py` | Reads full DICOM (`force=True`), decodes `pixel_array`, writes **windowed 8-bit PNG** for annotation display | **NO** — does not strip tags, does not scan burned-in PHI, does not write a de-identified DICOM. Comment: originals in `a_annoter` are never modified. | Reads identifying B26 sources; writes PNG cache under `manual_annotation_tool/cache/new_26/`. Does **not** overwrite B26 YOLO files. **Not** an intake tool. |
| `datasets/yolo_pose_remediation_v1/meta/_stepD_run_inventory_render.py` | Inventories `bassin/` DICOMs; **extracts** PatientName, PatientID, age, sex, StudyDate, SOP UID; writes identifying CSV/JSON; hashes source DICOM; renders triage PNGs | **NO — opposite of de-id** | **HIGH.** Would rewrite `candidate_inventory.csv`, `_stepD_state.json`, `triage_render_manifest.json` and triage PNGs under **immutable** `yolo_pose_remediation_v1`. Spreads identifiers. **DO NOT RUN.** |
| `datasets/yolo_pose_remediation_v1/meta/_stepD_run_selection_reports.py` | Historical R26 selection / stub writer | **NO** | **HIGH.** Would rewrite v1 meta and can touch `annotation_pilot/annotations/remediation_v1/`. Contains identifying notes. **DO NOT RUN.** |
| `annotation_pilot/manual_annotation_tool/verification_radios.py` | Reads `verification_radios.csv` | No PHI handling | Low if only read; not an intake gate |
| `annotation_pilot/manual_annotation_tool/server.py` | Annotation UI; `new_26` points at `bassin/a_annoter` + official JSON | No de-id | Would serve B26 DICOMs and can write annotation JSON if used — **do not use as intake** |
| `annotation_pilot/manual_annotation_tool/prepare_manual_annotation_new_26.py` / `validate_new_26.py` / `bootstrap_new_26.py` | B26 worklist / QA | No de-id | Can write official new_26 artifacts — **frozen; do not run** |
| Backend tests (`test_analyze_api_v5.py`, `test_v5_phase2_detector.py`, …) | Call `render_dicom_png` on B26 sources for tests | No de-id | Would read B26 DICOMs; not intake |
| `backend/app/services/analyze.py` | Production `/analyze` accepts **PNG/JPG only** | No DICOM, no PHI strip | Burned-in film text is **not** stripped (prior 6A/7B / 11C-0). Not a collection pipeline. |
| Step C copy/verify (`_phase10c_stepC_copy_temp/*.py`) | SHA256 of B26 PNG/TXT copies | Not DICOM de-id | Historical; do not re-run against frozen trees |
| Training scripts (`train_yolo_pose_v*.py`, `v5_*.py`) | Training / freeze hashes | Irrelevant | **DO NOT RUN** |

**No project script implements DICOM anonymization.**

### Third-party helper that *could* rewrite DICOM tags (not executed)

`radstract.data.dicom.exports.add_anon_tags` (venv only; **not** a project collection process):

- Replaces Study/Series/SOP UIDs with `generate_uid()`
- Sets `PatientID` / `StudyID` to `radstract-{random}`
- Sets `PatientName` to `Radstract {keyint}` (still a **name-shaped** tag)
- Sets dates/times to fixed placeholders
- Does **not** remove Institution / Accession / DOB / private tags / physician names
- Does **not** inspect pixels
- Uses **random** keyint by default → not a stable Case ID / not HMAC pseudonym
- **Not DICOM PS3.15 Basic Profile**

**Do not invoke radstract on any clinical file.** It is insufficient and would produce a false “anonymized” object.

pydicom 3.0.2 has `generate_uid` but **no** project wrapper and **no** built-in “anonymize this file” script in this repo.

### Scripts missing (required for a real future intake)

| Missing capability | Status |
|--------------------|--------|
| Dedicated intake watcher / deposit validator for `01_INBOX_RAW` | **MISSING** |
| Metadata strip + UID remapping writer (research DICOM) | **MISSING** |
| Restricted-linkage writer (`patient_pseudonym` HMAC) | **MISSING** |
| METADATA_CHECK verifier (fail-closed residual-tag scan) | **MISSING** |
| PIXEL_CHECK (visual protocol + optional OCR) | **MISSING** |
| Image-integrity comparator (geometry tags + PixelData) | **MISSING** |
| Triple-hash job (source file / de-id file / normalized pixels) | **MISSING** |
| Duplicate / B26–R26–future index (patient-level) | **MISSING** |
| Provenance manifest writer (non-identifying) | **MISSING** |
| Gate engine RAW → DEID_PENDING → DEIDENTIFIED → ELIGIBILITY | **MISSING** |
| Synthetic dry-run fixture (non-clinical) | **MISSING** |

Reusable **functions** that are **not** an intake service: `sha256_file()` in Step D / Step C (file bytes only).

### Accidental-modification risks (dataset original)

| Risk | Severity | Mitigation this phase |
|------|----------|------------------------|
| Re-running Step D inventory against `bassin/` + writing v1 meta | **HIGH** | Do not execute. v1 is IMMUTABLE. |
| Re-running Step D selection against R26 stubs | **HIGH** | Do not execute. |
| Pointing `server.py --dataset new_26` at official JSON | **HIGH** | Do not use as collection UI. |
| Dumping a new DICOM into `bassin/a_annoter` or `datasets/yolo_pose_new_26/images/` | **HIGH** | Inbox is `collection/01_INBOX_RAW` only (still empty; import NO-GO). |
| Using `dicom_render.py` as “de-id” because it writes PNG | **HIGH** | PNG is windowed display, may still show burned-in PHI, and is **not** a de-identified DICOM. |
| Using radstract `add_anon_tags` and claiming de-id | **HIGH** | Incomplete; not executed. |
| FastAPI `/analyze` on a screenshot of a named film | **MEDIUM** | Not intake; no strip. |

---

## DICOM de-identification specification

**Specification only. Not executed. 0 cases `DEID_CONFIRMED`.**

The future research object that may enter `03_DEIDENTIFIED` is a **de-identified DICOM** (same matrix geometry), not a PNG. DICOM → PNG remains a **later annotation-display** step (existing `dicom_render.py` is not that pipeline).

### A. Metadata — remove or replace

Fail-closed: any listed tag **present with a real-world value** after processing → **BLOCKED**. Empty / missing is acceptable only if documented. Replacement values must be **non-identifying**.

| Tag | Future action | Research DICOM | Restricted linkage | ML / provenance manifest |
|-----|---------------|----------------|--------------------|--------------------------|
| PatientName | **Remove** | Absent or empty | Original only if legally required | **NOT_ALLOWED** |
| PatientID | **Remove** from research file | Absent. Irreversible `patient_pseudonym` assigned **after** linkage write | Hospital ID → pseudonym map | Pseudonym only — **never** hospital ID |
| PatientBirthDate | **Remove** | Absent | Year-of-birth only if later authorized; default **omit** | **NOT_ALLOWED** |
| PatientSex | **Remove by default** | Absent unless a later written research justification exists | Optional | **NOT_ALLOWED** unless later justified. Not required for locked coxometry landmarks. Do not invent a clinical sex-quota rule. |
| AccessionNumber | **Remove** | Absent | Allowed | **NOT_ALLOWED** |
| StudyID | **Remove / replace** with opaque research study token | Non-identifying or absent | Original if required | Hash only if needed |
| SeriesNumber | **Replace** if it can act as an indirect identifier (local serial + institution) | Non-identifying research series number or omit | Original if required | **NOT_ALLOWED** as original |
| InstitutionName | **Remove** | Absent | Allowed | **NOT_ALLOWED** (no hospital name as training metadata) |
| InstitutionAddress | **Remove** | Absent | Allowed | **NOT_ALLOWED** |
| ReferringPhysicianName | **Remove** | Absent | Allowed | **NOT_ALLOWED** |
| PerformingPhysicianName | **Remove** | Absent | Allowed | **NOT_ALLOWED** |
| OperatorsName | **Remove** | Absent | Allowed | **NOT_ALLOWED** |
| OtherPatientIDs / OtherPatientIDsSequence | **Remove** | Absent | Allowed | **NOT_ALLOWED** |
| OtherPatientNames | **Remove** | Absent | Allowed | **NOT_ALLOWED** |
| Private tags | **Remove** all, or review each; any unidentified private block = **BLOCKED** | No unidentified private creator | Inventory of removed tags (no values) | **NOT_ALLOWED** |
| StudyInstanceUID / SeriesInstanceUID / SOPInstanceUID | **Replace** in research file with newly generated UIDs (pydicom `generate_uid` or deterministic UID from `case_id` + restricted secret). Originals **only** in `restricted/linkage/` | New UIDs | Original UIDs | **Hashes only** (`study_uid_hash`, `series_uid_hash`) |
| Address / phone / other identifying person names | **Remove** | Absent | Allowed | **NOT_ALLOWED** |

**May retain** on the research DICOM if present and needed for integrity / later geometry (values are technical, not identity):

SOPClassUID, Modality, Rows, Columns, PixelSpacing, PhotometricInterpretation, BitsAllocated, BitsStored, HighBit, PixelRepresentation, PixelData, SamplesPerPixel, PlanarConfiguration, ImagerPixelSpacing (if present), WindowCenter / WindowWidth (display only), RescaleSlope / RescaleIntercept, PatientOrientation / ImageOrientationPatient if present, ViewPosition / BodyPartExamined **only after** they are confirmed non-identifying free text (if free text contains a name → **BLOCKED**).

### UID strategy (coherent)

1. Read originals **once** on a restricted machine.  
2. Write originals + source SHA256 + hospital key → `restricted/linkage/` only.  
3. Compute `patient_pseudonym` (11B HMAC).  
4. Assign `case_id` (`R27_NNN`) **independent** of all clinical IDs.  
5. Write research DICOM with **new** Study/Series/SOP UIDs.  
6. Provenance stores **hashes** of original UIDs, not the UIDs.  

Random UIDs without linkage = lost traceability. Hospital UIDs in the research file = failed de-id. **Both forbidden.**

### Residual METADATA_CHECK

After write, re-open the research DICOM (`stop_before_pixels` plus private-tag walk) and search for:

- PatientName, PatientID, PatientBirthDate, AccessionNumber, Institution*, physician/operator names, OtherPatient*, raw original UIDs, any string matching the restricted hospital ID / name  

Any hit → **BLOCKED**. Do not claim metadata-clean without this scan.

---

## Pixel PHI policy

**Metadata-clean ≠ de-identified.**

Burned-in PHI (name, patient number, DOB, institution, ward, phone, identity barcode) can remain in `PixelData` after a perfect header wipe.

### Future PIXEL_CHECK (required)

1. **Human visual review** of the full frame (and zoom on corners / collimator edges / overlay bars).  
2. **Optional OCR** only as an aid — never as sole PASS. easyocr / pytesseract / Tesseract binary are **not installed** today. Absence of OCR → visual review is **mandatory**; if visual review is not recorded → `pixel_phi_check = UNVERIFIED` → **BLOCKED**.  
3. Search targets: patient name, patient number, DOB, establishment name, other directly readable identity.

| Result | Status |
|--------|--------|
| No burned-in PHI on recorded visual review | `PIXEL_CHECK_PASS` |
| PHI seen and **cannot** be redacted without changing matrix / cropping anatomy | `DEID_REJECTED` / **BLOCKED** |
| PHI seen and redacted **without** changing Rows/Columns/spacing/orientation | `PIXEL_REDACTED` then re-review; pixel_hash is of the **final** array |
| Not reviewed | `UNVERIFIED` → **BLOCKED** |

Do **not** enter `03_DEIDENTIFIED` on metadata-only success.

Existing `dicom_render.py` windowing is **not** a PIXEL_CHECK (it can **display** burned-in text more clearly; it does not detect or remove it).

Phase 11B already recorded identifying tags **PRESENT** on R26 + B26_01 sample and pixel PHI **not verified**. That historical finding is unchanged. Those files were **not** re-opened here.

---

## Image integrity policy

De-identification **must not geometrically alter** the clinical image.

### Mandatory controls (before vs after, same SOP instance lineage)

| Attribute | Rule |
|-----------|------|
| SOP Class | Must remain an acceptable radiographic SOP (e.g. DX/CR/Secondary Capture **only if** it is the source class). Unexpected class → **BLOCKED** |
| Modality | Expected `DX` / `CR` / `RG` / `XA` only if documented as plain radiograph. Other → **BLOCKED** / domain review |
| Rows | Unchanged |
| Columns | Unchanged |
| PixelSpacing | Unchanged if present; if **absent**, document `pixel_spacing = MISSING` (do not invent). Not an automatic clinical exclude; geometry later uses pixels unless spacing exists |
| PhotometricInterpretation | Unchanged |
| BitsAllocated / BitsStored / PixelRepresentation | Unchanged |
| Orientation (`PatientOrientation` / `ImageOrientationPatient`) | Unchanged if present |
| RescaleSlope / RescaleIntercept | Unchanged if present |
| PixelData | Byte-identical **unless** a documented PIXEL_REDACTED overlay wipe. Corruption (decode fail, size ≠ Rows×Columns×samples) → **BLOCKED** |

Compare:

- Tag equality for the geometry set  
- If no redaction: SHA256 of decoded ndarray (`C-order`, native dtype, **no** windowing) before vs after  
- If redaction: geometry tags equal; pixel_hash of **final** array only  

**Do not convert DICOM → PNG for the integrity gate.** Windowed uint8 PNG is a different object (lossy for hash / dynamic range).

---

## Case ID policy

| Rule | Requirement |
|------|-------------|
| Never use real PatientID as Case ID | Locked |
| Never use name / DOB / accession / filename / SOP UID as Case ID | Locked |
| Future image IDs | `R27_001`, `R27_002`, … then `R28_001+` if needed |
| Stability | Assigned once in a later phase; not recycled |
| Patient join | `patient_pseudonym` (HMAC-SHA256 of restricted secret + normalized hospital ID), truncated e.g. `P_` + 16 hex (11B) |
| Multiple views | Distinct Case IDs, **same** pseudonym |
| B26 / R26 | Historical; never reused |

Correspondence table: **`restricted/linkage/` only**.

In the dataset / annotation / training environment:

- no real patient identifier  
- no hospital name as training metadata  
- no date of birth  

**No Case ID was created in this phase.**

If hospital identity cannot be resolved: `UNRESOLVED_PATIENT_ID` → **HOLD**. Do not invent from folder name or visual resemblance.

---

## SHA256 / duplicate / leakage policy

### Hashes required (future)

| Hash | Input | Store |
|------|-------|-------|
| `source_file_hash` | SHA256 of **source DICOM bytes** as received | Restricted + provenance (hash only in public manifest) |
| `deidentified_file_hash` | SHA256 of **research DICOM bytes** after de-id | Provenance (required for `03_DEIDENTIFIED`) |
| `pixel_hash` | SHA256 of **normalized decoded pixel ndarray** (no windowing; documented dtype/order). Detects same image after UID/tag rewrite | Provenance |
| `study_uid_hash` / `series_uid_hash` | SHA256 of original UIDs (UTF-8) | Provenance; originals in restricted only |

Existing Step D `dicom_sha256` / PNG `image_sha256` / triage `render_sha256` are **not** these objects and must not be reused as de-id confirmation.

### Duplicate / leakage rules

| Situation | Rule |
|-----------|------|
| Exact file duplicate | Same `source_file_hash` or same `deidentified_file_hash` → one Case ID; no second independent patient |
| Same pixels, new DICOM wrapper | Same `pixel_hash` → same image; not a new patient |
| Same patient, different study | Same `patient_pseudonym` → **same future split**; not a new independent-patient count |
| Same patient, different image / sibling view | Distinct Case IDs; same pseudonym; **same split**; not a new independent patient |
| Re-export of the same exam | Detect via restricted UID / accession / hashes → not a new case |
| Derived / intermediate (windowed PNG, crop, flip, mosaic, Phase 10D ROI) | **Never** a new patient |
| Different SHA256 | **Does not** prove different patients. Patient-level check remains mandatory |
| Different patient, same pixel hash | **HOLD** — do not auto-resolve |
| Unresolved identity | No split assignment |

**One patient = one split.** No split is created in this phase. `08_VALIDATED` ≠ train-ready.

B26/R26 must not be mixed accidentally into a future intake split without an explicit later versioning decision.

---

## Fail-closed gates

`PENDING` / doubt → **BLOCKED / REVIEW**. Never “best effort”. Never auto-PASS.

### `01_INBOX_RAW` → `02_DEIDENTIFICATION_PENDING`

| Allow only if | Else |
|---------------|------|
| Authorized deposit recorded (`RAW_RECEIVED`) | Stay in RAW / reject deposit |
| File is a readable DICOM (parse without claiming de-id) | `REJECTED` (unreadable) |
| Not already written into any YOLO / B26 / R26 tree | Quarantine |

This transition **starts** work. It does **not** mean de-identified.

### `02_DEIDENTIFICATION_PENDING` → `03_DEIDENTIFIED`

**All** required. Any miss → stay pending or `REJECTED`.

| Condition | Fail-closed if |
|-----------|----------------|
| METADATA_CHECK | Sensitive tag residual |
| PIXEL_CHECK | PHI seen, **or UNVERIFIED** |
| `source_file_hash` + `deidentified_file_hash` + `pixel_hash` | Any hash absent |
| Provenance record (schema below) | Incomplete |
| Patient identity resolved **or** explicit `UNRESOLVED_PATIENT_ID` hold (hold ≠ enter 03 as confirmed) | Unresolved identity treated as confirmed |
| Duplicate scan vs B26 / R26 / collection index | Potential duplicate unresolved |
| PixelData decodes; Rows×Columns consistent | Corruption |
| Geometry tags equal (integrity policy) | Incoherent geometry |
| Modality / SOP class expected | Unexpected modality |
| AP-pelvis compatibility not silently assumed | Unknown view — do not mark DEID_CONFIRMED as domain-eligible (domain is the **next** gate; but a non-radiograph still **BLOCKS** 03) |
| Sufficient technical info to preserve the object | Missing required technical tags that prevent integrity compare |

`03_DEIDENTIFIED` means **`DEID_CONFIRMED` only**. It does **not** mean eligible.

### `03_DEIDENTIFIED` → `04_ELIGIBILITY_PENDING`

| Allow only if | Else |
|---------------|------|
| `deidentification_status = DEID_CONFIRMED` | Stay in 02/03 or exclude |
| Case ID + `patient_pseudonym` assigned (or explicit identity HOLD routed to review, **not** counted eligible) | BLOCKED |
| No exact duplicate promotion | BLOCKED |
| Hand-off to eligibility checklist (all boxes still unchecked / PENDING) | — |

### Always BLOCKED (examples from the brief)

- Sensitive metadata detected after processing  
- Pixel PHI detected **or not verified**  
- Hash absent  
- Provenance absent  
- Patient identity unresolved (for any path that would count a new independent case)  
- Potential duplicate  
- DICOM corruption  
- Incoherent geometry  
- Unexpected modality  
- Image not compatible with AP pelvis (for eligibility; may be `DOMAIN_REVIEW_REQUIRED` rather than silent include)  
- Insufficient clinical / technical information  

---

## Eligibility checklist

Future checklist **before** physician review. No case scored. No new clinical thresholds.

- [ ] adult  
- [ ] radiograph of pelvis / hip compatible with the locked protocol  
- [ ] appropriate AP projection  
- [ ] image exploitable (or documented hard-example retention)  
- [ ] no untreated visible PHI  
- [ ] unique patient (independent count)  
- [ ] not a duplicate  
- [ ] provenance known  
- [ ] DICOM readable  
- [ ] geometric parameters available **or clearly documented missing** (do not invent PixelSpacing)  
- [ ] no unvalidated clinical rule invented  

| Item | Note |
|------|------|
| Adult | **PHYSICIAN-GATED** — numeric cutoff not locked (11B E1; 016Y/017Y already `incertain`) |
| Compatible radiograph / AP | Locked domain: adult AP pelvis. Pediatric / unilateral hip / frog-leg / CT / MRI / phone / synthetic → do not include automatically (`DOMAIN_REVIEW_REQUIRED`) |
| Exploitable | Quality reject vs hard-retention is a documented choice, not a new cutoff |
| PHI | Requires `DEID_CONFIRMED` |
| Unique / no duplicate | Patient-level hashes + pseudonym |
| Provenance | Manifest § below |
| Geometric parameters | Presence documented; no invented spacing; P-FOV numeric cutoff **not** applied |

Physician-gated boxes left unset → **STATUS = PENDING**. Never auto-convert to PASS.

---

## Provenance manifest

Minimal **future** public / ML-adjacent manifest. **No personal data.** No values written now.

| Field | Content |
|-------|---------|
| `Case_ID` | `R27_NNN` |
| `source_file_hash` | SHA256 source DICOM |
| `deidentified_file_hash` | SHA256 research DICOM |
| `pixel_hash` | SHA256 normalized pixels |
| `source_type` | e.g. `DICOM_DX` / `DICOM_CR` |
| `modality` | DICOM Modality |
| `study_uid_hash` | Hash of **original** Study UID |
| `series_uid_hash` | Hash of **original** Series UID |
| `rows` / `columns` | Integers |
| `pixel_spacing` | Pair or `MISSING` |
| `orientation` | Tag value if present, else `MISSING` |
| `deidentification_status` | `DEID_PENDING` / `DEID_CONFIRMED` / `DEID_REJECTED` / … |
| `pixel_phi_check` | `PASS` / `UNVERIFIED` / `PIXEL_REDACTED` / `FAIL` |
| `eligibility_status` | 11B vocabulary |
| `physician_review_status` | Pending / reviewed / … |
| `annotation_status` | 11B §18 |
| `qc_status` | Pending / passed / failed |
| `created_at` | UTC timestamp |
| `operator/tool version` | Opaque operator id + tool version string |

**Forbidden in this manifest:** PatientName, hospital PatientID, DOB, address, phone, accession, institution name, original UIDs, identifying paths.

`patient_pseudonym` may be added to a **separate** ML cases table; it is not a personal name. Hospital mapping stays in `restricted/linkage/`.

---

## Dependency audit

Checked in the project `.venv` only. **Nothing installed.**

| Name | Version | Available | Future use | Risk |
|------|---------|-----------|------------|------|
| pydicom | 3.0.2 | **YES** | Read/write DICOM; `generate_uid`; tag walk | Easy to overwrite clinical files if a writer is added carelessly; `force=True` already used in `dicom_render.py` |
| pydicom.uid / dataset / pixels | 3.0.2 | **YES** | UID remap; pixel decode | Decode can fail on compressed transfer syntaxes if codecs missing |
| hashlib (stdlib) | — | **YES** | SHA256 file / pixels | None |
| hmac (stdlib) | — | **YES** | Future `patient_pseudonym` | Secret must not live beside YOLO |
| numpy | 2.4.6 | **YES** | Pixel array / integrity hash | Windowing vs raw array confusion |
| Pillow | 11.3.0 | **YES** | Later display PNG only — **not** this gate | Lossy vs DICOM hash |
| opencv-python (`cv2`) | 5.0.0 | **YES** | Optional later assist | Not an OCR stack by itself |
| scikit-image | 0.26.0 | **YES** | Not required for de-id | — |
| pylibjpeg | 2.1.0 | **YES** (meta) | Compressed pixel decode | **libjpeg / openjpeg / rle plugins ABSENT** — some DICOMs may not decode |
| gdcm | — | **NO** | Alternate decoder | Missing |
| SimpleITK | 2.5.5 | **YES** | Not selected for intake | Could rewrite images if misused |
| nibabel | 5.4.2 | **YES** | Not DICOM de-id | — |
| imageio | 2.37.3 | **YES** | Has a DICOM plugin — **not** a de-id tool | Accidental re-encode |
| radstract | present (no `__version__`) | **YES** (venv) | **Do not use** for this protocol | Incomplete “anon” tags; random IDs; no pixel PHI |
| highdicom | — | **NO** | Could help structured de-id later | Missing |
| dicomanonymizer | — | **NO** | External anonymizer | Missing |
| deid (pydicom-deid) | — | **NO** | Recipe-based de-id | Missing |
| easyocr | — | **NO** | Optional OCR aid | Missing |
| pytesseract | — | **NO** | Optional OCR aid | Missing |
| Tesseract binary | — | **NO** | Optional OCR aid | Missing |
| FastAPI stack (`backend/requirements.txt`) | listed | **YES** (prod) | PNG/JPG `/analyze` only | No DICOM intake; no PHI strip |

`backend/requirements.txt` does **not** list pydicom. pydicom is available in the **project venv** used by the annotation tool / Step D, not as a declared FastAPI collection dependency.

---

## Open physician decisions

Unchanged. **No defaults created.**

| ID | Status |
|----|--------|
| **P-A1** ASL sourcil-vs-rim exemplars | **OPEN** |
| **P-A7** FSP accepted-level exemplars | **OPEN** |
| **P-FOV** FSD numeric cutoff vs directional-only | **OPEN** — 0.5× head diameter **not** reintroduced |
| **P-TOL** Inter-annotator tolerance | **OPEN** |
| **P-V1** Whether `v=1` is allowed | **OPEN** |
| **P-C10** Acceptable clinical landmark/angle error | **OPEN** |

Also still open (11B): adult numeric cutoff (E1); legal/consent basis for new collection (E9).

---

## Risks

1. **False de-id:** metadata wipe without PIXEL_CHECK.  
2. **Existing scripts look like “DICOM tools”** but extract identifiers or write windowed PNGs.  
3. **Re-running Step D** would mutate immutable `remediation_v1`.  
4. **radstract `add_anon_tags`** looks like anonymization and is not protocol-compliant.  
5. **Compressed DICOM decode** may fail (pylibjpeg plugins missing) → fail-closed, do not force a bad PNG substitute as the research object.  
6. **Identifying inventories already on disk** (Step D CSV, R26 worklist, named `bassin/` folders) remain a leakage template if copied forward.  
7. **Hash of a windowed PNG ≠ pixel_hash ≠ source hash.**  
8. **Different SHA256 ≠ different patient.**  
9. Using `datasets/yolo_pose_new_26/` or `bassin/a_annoter` as a drop zone would contaminate the frozen seed.

---

## Blockers

1. **No project intake / de-identification implementation.** Spec only.  
2. **No PIXEL_CHECK tool** and **no OCR** — visual review process not instantiated.  
3. **No restricted HMAC / linkage writer.**  
4. **No hash / duplicate intake index** against B26 + R26 + future cases.  
5. **No gate engine** for RAW → … → `04_ELIGIBILITY_PENDING`.  
6. **Existing DICOM scripts are unsafe to reuse** for this purpose (PHI extraction / v1 writes / display PNG).  
7. **Legal authorization for new collection** still project-owner / physician gated (E9).  
8. **REAL_PATIENT_IMPORT = NO-GO** — `01_INBOX_RAW` correctly empty.  
9. Physician items P-A1 / P-A7 / P-FOV / P-TOL / P-V1 / P-C10 still **OPEN**.  
10. **R26 still PENDING_PHYSICIAN** — not in this pipeline, not promoted.

Therefore a **dry-run execution** (even on a synthetic file) is **not authorized by this phase** and **cannot be claimed ready**: the executable path does not exist, and creating it was forbidden here.

---

## Next safe step

Only when a later phase is explicitly approved, and still **without real patients**:

1. Author a **new** intake module **outside** B26 / v1 / R26 / Flutter / FastAPI / `mvp_geometry` (do not “fix” Step D into a de-id tool).  
2. First dry-run on a **synthetic / phantom DICOM** with planted tags + planted burned-in text — never on `bassin/` files.  
3. Prove fail-closed: residual tag → BLOCKED; unverified pixels → BLOCKED; missing hash → BLOCKED.  
4. Keep linkage only under `restricted/`.  
5. Do not install packages unless that later phase explicitly allows it.  
6. Do not start training, R26 promotion, or real import.

**Do not start that work in this session.**

---

## Verdict

# **PHASE_11C2_NOT_READY**

The empty 11C-1 tree and the written specification are in place. The **scripts and operational checks required to perform a DICOM intake / de-identification dry-run are not**. Existing DICOM-related code must not be executed for this purpose.

| Gate | Status |
|------|--------|
| **TRAINING** | **NO-GO** |
| **REAL_PATIENT_IMPORT** | **NO-GO** |
| **R26_PROMOTION** | **NO-GO** |
| **DATASET_MODIFICATION** | **NO-GO** |

---

*End of Phase 11C-2. STOP.*
