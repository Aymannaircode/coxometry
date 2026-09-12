# Phase 11C-1 — Controlled Collection Infrastructure

**Date:** 2026-09-04  
**Mode:** INFRASTRUCTURE ONLY — no real-patient import, no training, no inference for data creation  
**Predecessor documents (terminology preserved, not reinterpreted):**
- `datasets/yolo_pose_new_26/phase11a_annotation_protocol_audit.md`
- `datasets/yolo_pose_new_26/phase11b_collection_deidentification_protocol.md`
- `datasets/yolo_pose_new_26/phase11c0_collection_environment_audit.md`

**This phase does not:**
- import, copy, de-identify, or hash any real medical file
- create any Case ID (`R27_*`, `R28_*`, …) or fake patient
- modify B26 / R26 / official JSON / V5 weights / Flutter / FastAPI / `mvp_geometry` / PDF / calibration / existing annotations
- create `datasets/yolo_pose_remediation_v2/`
- use `datasets/yolo_pose_new_26/` as a raw inbox
- create a train/val/test split
- promote R26
- start Phase 11C-2

**Final verdict:** `PHASE_11C1_INFRASTRUCTURE_READY_WITH_BLOCKERS`  
**TRAINING = NO-GO**  
**R26_PROMOTION = NO-GO**  
**REAL_PATIENT_IMPORT = NO-GO_DURING_THIS_PHASE**

---

## 1. Scope

Prepare an **empty, traceable future intake tree** so that later authorized adult AP-pelvis cases can be received **without** mixing them into the frozen training dataset.

This phase instantiates only:

- a dedicated collection staging tree (empty)
- a restricted-linkage tree (empty; no identities)
- the present protocol report

It does **not** receive patients, run DICOM tools, or claim any case is de-identified, eligible, annotated, or train-ready.

Phase 10D–10H implications remain locked and are not reopened:

| Phase | Locked implication (unchanged) |
|-------|--------------------------------|
| 10D | Learned remediation on 21 train patients is **not safe**; crops are not new patients |
| 10E | ASL = sourcil ≠ rim; unique 2D point remains ambiguous without exemplars / `v=0` |
| 10F | Sourcil detectability **PARTIAL**; research candidates are **not** GT |
| 10G | Automatic ASL localization **PARTIAL**; confidence gate **UNCERTAIN**; do not implement |
| 10H | Flutter correction bridge works; corrections are **not** training GT |

Physician-gated items **P-A1, P-A7, P-FOV, P-TOL, P-V1, P-C10** remain **OPEN**. No default numeric values were created. The provisional **0.5 × head diameter** FSD cutoff is **not** reintroduced.

---

## 2. Documents inspected

Read before any filesystem creation. No inspected official dataset / label / weight / production file was modified.

### 2.1 Required protocol documents

- `datasets/yolo_pose_new_26/phase11a_annotation_protocol_audit.md`
- `datasets/yolo_pose_new_26/phase11b_collection_deidentification_protocol.md`
- `datasets/yolo_pose_new_26/phase11c0_collection_environment_audit.md`

### 2.2 Phase 10D–10H (headers / locked verdicts only)

- `datasets/yolo_pose_new_26/phase10d_small_data_refinement_audit.md` — `REFINEMENT_NOT_SAFE_WITH_CURRENT_DATA`
- `datasets/yolo_pose_new_26/phase10e_coxometry_domain_audit.md` — domain / ASL sourcil ≠ rim
- `datasets/yolo_pose_new_26/phase10f0_sourcil_structure_audit.md` — sourcil **PARTIAL**; not GT
- `datasets/yolo_pose_new_26/phase10g0_asl_success_failure_analysis.md` — auto-ASL **PARTIAL**; do not implement
- `datasets/yolo_pose_new_26/phase10h_validation_report.md` — Flutter bridge ≠ training GT

### 2.3 Location inspection (existence only)

| Path | Status before this phase |
|------|--------------------------|
| Project root | `annotation_pilot`, `backend`, `bassin`, `datasets`, `docs`, `mobile`, `mvp_geometry`, `runs`, … |
| `datasets/` | `yolo_pose_new_26/`, `yolo_pose_remediation_v1/` only |
| `datasets/yolo_pose_remediation_v2/` | **ABSENT** (not created) |
| `collection/` | **ABSENT** |
| `restricted/` | **ABSENT** |
| `bassin/incoming`, `bassin/a_collecter` | **ABSENT** |
| `datasets/incoming`, `datasets/collection` | **ABSENT** |
| Any `R27_*` | **ABSENT** |

11C-0 conclusion reused: there was **no** project-approved landing folder for a new DICOM. Existing `bassin/a_annoter`, `a_verifier`, `rejetees`, and named folders are **not** a future inbox.

---

## 3. Structure created

### 3.1 Location decision

| Candidate | Used? | Reason |
|-----------|-------|--------|
| `datasets/yolo_pose_new_26/` | **NO** | Frozen training tree. Phase 11B/11C-0 forbid using it as raw inbox. |
| `datasets/yolo_pose_remediation_v1/` | **NO** | Seed copy of B26 + identifying Step D inventories. |
| `datasets/yolo_pose_remediation_v2/` | **NO** | Explicitly forbidden to create. |
| `bassin/` / named patient folders | **NO** | Used B26/R26 pools; folder names are identifying; 11B forbids recycling them as Case IDs. |
| `datasets/collection/` | **NO** | Would sit inside the `datasets/` training family. |
| **`collection/` (project root)** | **YES** | Dedicated, empty, **outside** every YOLO/training tree. |
| **`restricted/linkage/` (project root)** | **YES** | Required 11B two-store separation. Outside training **and** outside de-identified collection stages. |

No existing inbox satisfied the raw/training separation, so a dedicated collection tree was created.

### 3.2 Empty staging tree

```
collection/                          NOT a training dataset
├── README.md                        safety banner
├── .gitignore                       ignore future deposits
├── 01_INBOX_RAW/                    .gitkeep only
├── 02_DEIDENTIFICATION_PENDING/     .gitkeep only
├── 03_DEIDENTIFIED/                 .gitkeep only
├── 04_ELIGIBILITY_PENDING/          .gitkeep only
├── 05_PHYSICIAN_REVIEW/             .gitkeep only
├── 06_ANNOTATION_PENDING/           .gitkeep only
├── 07_QC_PENDING/                   .gitkeep only
├── 08_VALIDATED/                    .gitkeep only
├── 09_EXCLUDED/                     .gitkeep only
└── 10_ARCHIVE/                      .gitkeep only
```

### 3.3 Restricted linkage tree

```
restricted/                          EMPTY — no identities
├── README.md
├── .gitignore
└── linkage/                         .gitkeep only
```

No linkage CSV, no HMAC secret, no hospital identifiers, and no Case IDs were created.

### 3.4 Explicitly not created

| Item | Status |
|------|--------|
| `datasets/yolo_pose_remediation_v2/` | **NOT CREATED** |
| Any `R27_*` / `R28_*` folder or file | **NOT CREATED** |
| Train/val/test directories or `split.json` | **NOT CREATED** |
| Copies of B26 / R26 / `bassin/` DICOMs | **NOT COPIED** |
| Fake patients / placeholder images | **NOT CREATED** |
| De-identification scripts | **NOT CREATED** |
| Annotation files | **NOT CREATED** |

---

## 4. RAW / DEID separation

Conceptual pipeline (empty; no files moved):

```
RAW
 ↓
DE-IDENTIFICATION
 ↓
DE-IDENTIFIED
 ↓
ELIGIBILITY
 ↓
PHYSICIAN REVIEW
 ↓
ANNOTATION
 ↓
QC
 ↓
VALIDATED
```

| Rule | Meaning |
|------|---------|
| A file in `01_INBOX_RAW` | Identifying source. **Never** training-ready. Restricted access. |
| A file in `02_DEIDENTIFICATION_PENDING` | Checklist not finished. Still **not** de-identified. |
| A file in `03_DEIDENTIFIED` | Metadata + pixel checks recorded as `DEID_CONFIRMED` **only after proof**. **Not** automatically clinically eligible. |
| A file in `04_ELIGIBILITY_PENDING` | Eligibility checklist incomplete or physician-gated item = `PENDING`. |
| A file in `08_VALIDATED` | Collection QC passed. **Not** automatically train-ready until a **future** patient-level split is defined **and frozen**. |
| B26 / R26 | Remain in their current trees. They were **not** copied into this structure. |

**Status is never acquired without the corresponding proof** (see §10 and §16).

---

## 5. Restricted linkage policy

Phase 11B §7 two-store rule is now instantiated as **empty locations**, not as data.

| Store | Path | Allowed later | Present now |
|-------|------|---------------|-------------|
| **A. Restricted linkage** | `restricted/linkage/` | Hospital identity ↔ `patient_pseudonym` / source SHA256 / Study UIDs, if legally required | Empty `.gitkeep` |
| **B. ML / collection metadata** | future manifests beside de-identified cases — **never** in RAW | `case_id`, irreversible `patient_pseudonym`, technical + workflow fields | None (no cases) |

**Never in ML metadata**

- PatientName
- Real hospital PatientID
- Full date of birth
- Address
- Telephone number
- Real identity
- Administrative / accession numbers
- Identifying folder names from `bassin/<NAME>_…/`

**Proposed construction (protocol only — not implemented, no secret created):**

`patient_pseudonym = HMAC-SHA256(restricted_secret, normalized_hospital_patient_id)`  
truncated form e.g. `P_` + 16 hex chars (Phase 11B §7.2).

If identity cannot be resolved: `UNRESOLVED_PATIENT_ID` → **HOLD**. Do not invent a pseudonym from filename, folder name, or visual similarity.

Historical identifying inventories (`candidate_inventory.csv`, `selected_cases.csv`, R26 `worklist.csv`, `_stepD_state.json`) **must not be copied** into `restricted/linkage/` or any future training metadata. They remain historical artifacts and were not moved.

The linkage table **must never** be placed in a future training dataset.

---

## 6. Case-ID policy

Documented only. **No Case ID was created.**

Future independent intake images use a **new namespace**:

```
R27_001
R27_002
R27_003
…
```

Later waves, if needed, may continue as `R28_001+`, `R29_001+`, etc. **No such folders exist.**

| Rule | Requirement |
|------|-------------|
| Unique | One Case ID per **image** used for annotation |
| Non-identifying | Must not contain name, hospital ID, DOB, phone, accession |
| Independent of patient name | Never derived from `bassin/<NAME>_` folders or filenames |
| Stable | Once assigned (in a later phase), not recycled |
| Traceable | Joinable to `patient_pseudonym` and provenance, not to raw identity in ML files |
| Multiple views | Distinct Case IDs, **same** `patient_pseudonym` |
| Historical IDs | `B26_*` and `R26_*` remain historical; never reused for new patients |

---

## 7. Provenance schema

Schema only. **No values for real patients.**

| Field | Classification | Notes |
|-------|----------------|-------|
| `case_id` | **REQUIRED** | `R27_NNN` (or later wave). Assigned only when a future intake case is accepted. |
| `patient_pseudonym` | **REQUIRED** once identity is resolved; otherwise HOLD | Irreversible. Do not invent. |
| `source` | **REQUIRED** | Pool tag, e.g. `future_clinical_intake`. Not a personal name. |
| `source_type` | **REQUIRED** | Controlled technical type (e.g. `DICOM_XR` / `DICOM_CR` / `DICOM_DX`). |
| `acquisition_year` | **OPTIONAL** | Year only, and only if allowed **and** needed. Full study datetime **NOT_ALLOWED** in ML metadata. |
| `view` | **REQUIRED** | Must be `AP_pelvis` or routed to `DOMAIN_REVIEW_REQUIRED`. |
| `image_hash_sha256` | **REQUIRED** after `DEID_CONFIRMED` | SHA256 of the **final de-identified** annotation image. Source-DICOM hashes stay restricted. |
| `deidentification_status` | **REQUIRED** | Controlled vocabulary §8 / §10. Never claimed without METADATA_CHECK + PIXEL_CHECK + FINAL_DEID_CHECK. |
| `eligibility_status` | **REQUIRED** | Adult / domain / independence items may be **PHYSICIAN-GATED**. `PENDING` must not auto-become `PASS`. |
| `annotation_status` | **REQUIRED** | Compatible with Phase 11B §18 (`NOT_ANNOTATED` / `ANNOTATED` / `UNDER_REVIEW` / `REVIEWED` / `ADJUDICATION_REQUIRED` / `ADJUDICATED` / `REJECTED`). |
| `review_status` | **REQUIRED** | Independent of annotation_status. Not acquired without reviewer proof. |
| `annotation_version` | **REQUIRED** once annotation starts; otherwise omit | Monotonic raw / reviewed / adjudicated. |
| `annotator_id` | **REQUIRED** when annotated | Opaque staff ID. Full legal name **NOT_ALLOWED** in public manifests. |
| `reviewer_id` | **REQUIRED** when reviewed | Independent of annotator A on val/test. |
| `adjudication_id` | **OPTIONAL**; **REQUIRED** if adjudication occurs | Not the same unresolved pair without a third recorded decision. |
| `exclusion_reason` | **REQUIRED** if excluded / rejected | Controlled reason / Phase 11A codes. |
| `hard_tags` | **OPTIONAL** | Existing vocabulary only (`ASL_hard`, `OVERLAP`, `ROT_mild`, `SHAFT_hard`, `QUALITY_var`, `SIZE_var`, …). |
| `provenance_notes` | **OPTIONAL** | Free text **without** identifiers. |

**NOT_ALLOWED** in this schema / any future ML CSV:

PatientName, hospital PatientID, full DOB, address, phone, real identity, administrative numbers, AccessionNumber, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID, InstitutionName, InstitutionAddress, ReferringPhysicianName, private identifying tags, identifying source paths.

Those UIDs / hospital keys, if legally required for duplicate control, live **only** in `restricted/linkage/`.

**PHYSICIAN-GATED** (no defaults written):

- Adult numeric cutoff (E1)
- Legal / consent basis for new collection (E9)
- Prosthesis / deformity blanket exclusion (E12)
- Sampling quotas (E13)
- Clinical exclusion lists (E14)
- P-A1, P-A7, P-FOV, P-TOL, P-V1, P-C10
- Physician clearance checkbox on the eligibility gate

---

## 8. DICOM de-identification checklist

**Specification only. No DICOM was opened or rewritten. 0 cases are `DEID_CONFIRMED`.**

A future case may leave RAW only after the four recorded gates below. Claiming de-identification without those proofs is forbidden.

### 8.1 Metadata checklist (METADATA_CHECK)

| Tag / class | Action |
|-------------|--------|
| PatientName | Remove |
| PatientID | Remove from research file; replace by irreversible pseudonym **only after** restricted linkage is written |
| PatientBirthDate | Remove |
| InstitutionName | Remove where unnecessary |
| InstitutionAddress | Remove |
| ReferringPhysicianName | Remove |
| AccessionNumber | Remove from research file |
| StudyInstanceUID | Remove / replace in research file; original only in restricted store if required |
| SeriesInstanceUID | Same |
| SOPInstanceUID | Same |
| Private Tags | Remove or review; identifying private tags must not remain |
| Other identifying tags (address, phone, other physician / operator names, etc.) | Remove |

Technical tags that may be retained if needed for QC: modality, rows/columns, photometric interpretation, **PixelSpacing** if present.

### 8.2 Pixel checklist (PIXEL_CHECK)

Burned-in PHI in pixels must be absent:

- patient name labels
- hospital identifiers
- dates of birth
- ward / phone / barcode text encoding identity
- other burned-in PHI

If burned-in PHI cannot be removed reliably → `DEID_REJECTED` or physician/project-owner hold. Identifiable pixels must not enter `03_DEIDENTIFIED` or any training tree.

### 8.3 Final gates

| Gate | Meaning |
|------|---------|
| **METADATA_CHECK** | Listed tags absent from the research object |
| **PIXEL_CHECK** | Visual / documented absence of burned-in PHI |
| **FINAL_DEID_CHECK** | Both checks recorded; operator/process signed |
| **SHA256_AFTER_DEID** | SHA256 of the **final de-identified** annotation image |

Existing B26/R26 source DICOMs remain `DEID_PENDING` / **UNRESOLVED** (Phase 11B/11C-0). This phase does **not** change that.

Project-owned tools (`dicom_render.py`, Step D inventory) are **not** a de-identification pipeline and were not run.

---

## 9. Duplicate policy

**Specification only. No hash was computed on a real DICOM.**

Future control uses SHA256 of the **final de-identified** file (`SHA256_AFTER_DEID`). Restricted store may also keep source-DICOM SHA256 and study/series UIDs.

| Class | Definition | Action |
|-------|------------|--------|
| **exact duplicate** | Same SHA256 of the final de-identified image (or same source-DICOM SHA256) | Do not count twice; keep one Case ID |
| **same patient / different study** | Same `patient_pseudonym` (or restricted hospital key); different study | Same independent patient; not a new patient count; all studies stay in one future split |
| **same patient / different image** | Same patient; sibling / other view | Distinct Case IDs; same pseudonym; **not** a second independent patient |
| **different patient / same image hash** | Hash collision or shared file attributed to two identities | **HOLD** — do not auto-resolve; restricted review |

**A different SHA256 does NOT prove two images come from different patients.** Patient-level control remains mandatory (restricted identity / `patient_pseudonym`). Different filename ≠ different patient.

If PatientID is missing and identity cannot be resolved: `UNRESOLVED_PATIENT_ID` → HOLD → no Case ID promotion, no split.

Existing Step D hashes are **source / triage** hashes, not de-id confirmation, and were not recomputed.

---

## 10. Workflow statuses

Controlled pipeline statuses. A status is **never** acquired without the listed proof.

| Status | Meaning | Minimum proof |
|--------|---------|---------------|
| `RAW_RECEIVED` | File landed in `01_INBOX_RAW` under authorized intake | Deposit record (timestamp, actor). **Not** created this phase. |
| `DEID_PENDING` | Source received; checklist incomplete | Absence of FINAL_DEID_CHECK |
| `DEID_CONFIRMED` | METADATA_CHECK + PIXEL_CHECK + FINAL_DEID_CHECK + SHA256_AFTER_DEID | Signed checklist + hash |
| `ELIGIBILITY_PENDING` | De-identified (or held pending de-id policy) but eligibility incomplete | Any eligibility box `PENDING` |
| `ELIGIBLE` | All required eligibility boxes PASS | No physician-gated box left PENDING |
| `PHYSICIAN_REVIEW_PENDING` | Awaiting independent physician / project-owner medical gate | Open P-* or adult/domain hold |
| `PHYSICIAN_REVIEWED` | Physician review recorded | Reviewer ID + decision |
| `ANNOTATION_PENDING` | Cleared for annotation; no Annotator A record | Empty landmarks |
| `ANNOTATED` | Annotator A submitted immutable raw record | Annotator ID + annotation version |
| `QC_PENDING` | Annotation exists; QC not signed | QC checklist open |
| `QC_PASSED` | QC checklist complete | QC actor + version |
| `VALIDATED` | Collection validation complete | QC_PASSED + required review/adjudication per §13 |
| `EXCLUDED` | Out of corpus with recorded reason | `exclusion_reason` |
| `REJECTED` | Failed a hard gate (de-id, identity, quality without hard-retention, etc.) | Reason + actor |

Compatible Phase 11B annotation sub-states remain: `NOT_ANNOTATED`, `UNDER_REVIEW`, `REVIEWED`, `ADJUDICATION_REQUIRED`, `ADJUDICATED`. Training/eval GT, when a later phase allows it, is **`REVIEWED` or `ADJUDICATED` only**.

`PENDING` must never be converted to `PASS` automatically.

---

## 11. Eligibility gate

Future checklist (no case evaluated):

- [ ] adult confirmed
- [ ] AP pelvis confirmed
- [ ] domaine radiographique compatible
- [ ] image exploitable
- [ ] patient indépendant
- [ ] aucun doublon connu
- [ ] DICOM dé-identifié
- [ ] absence de PHI dans pixels
- [ ] provenance complète
- [ ] médecin clearance si nécessaire

| Item | Gate type |
|------|-----------|
| adult confirmed | **PHYSICIAN-GATED** (numeric cutoff not locked; 016Y/017Y already `incertain`) |
| AP pelvis confirmed | Required; else `DOMAIN_REVIEW_REQUIRED` |
| compatible radiographic domain | Required; pediatric / unilateral hip / non-AP / synthetic / phone / négatoscope → do not include automatically |
| exploitable image | Required **or** documented hard-example retention |
| independent patient | Required; unresolved identity → HOLD |
| no known duplicate | Required; no live detector yet |
| DICOM de-identified | Required `DEID_CONFIRMED` |
| no PHI in pixels | Required PIXEL_CHECK |
| complete provenance | Required schema §7 |
| physician clearance if needed | **PHYSICIAN-GATED** |

If any criterion is physician-gated and unset: **STATUS = PENDING**.  
Do **not** convert PENDING → PASS automatically.

Phase 11B eligibility states remain valid: `ELIGIBLE` / `PENDING_PHYSICIAN` / `DOMAIN_REVIEW_REQUIRED` / `UNRESOLVED_PATIENT_ID` / `REJECTED`.

---

## 12. Physician review gate

Independent physician / Reviewer B is **required** before a future case can become validation/test GT.

| Still OPEN — no default created |
|--------------------------------|
| **P-A1** ASL sourcil-vs-rim illustrated exemplars |
| **P-A7** FSP accepted-level exemplars |
| **P-FOV** FSD numeric cutoff vs directional-only |
| **P-TOL** Inter-annotator disagreement tolerance |
| **P-V1** Whether `v=1` is allowed |
| **P-C10** Acceptable clinical landmark/angle error |

**P-FOV:** the directional rule remains locked (`v=0` if distal shaft not sufficiently visible/stable). The numeric **0.5 × head diameter** cutoff is **not** implemented and is **not** written as a default.

Until these are locked: annotate only when the locked verbal definition is clear; otherwise `v=0`; flag `FOV_SHORT` / `FOV_POLICY_REVIEW_REQUIRED`; do not auto-average disagreements.

`annotation_pilot/annotations/annotator_B/` remains empty. This phase does not populate it.

---

## 13. Annotation / review workflow

```
Annotator A
    ↓
Independent Physician / Reviewer B
    ↓
Adjudication if disagreement
```

| Forbidden automatic promotion to ground truth |
|-----------------------------------------------|
| V5 predictions |
| Flutter / Phase 10H manual corrections |
| Phase 10F / 10G research candidates |
| `refined_landmarks` |
| R26 empty stubs |
| B26 single-annotator labels unless later physician-reviewed under this protocol |

ASL / FSP / FSD must follow Phase 11A/11B definitions:

- **ASL:** most lateral point of the sclerotic acetabular sourcil — **not** generic rim, ASM, AIIS, osteophyte. If inseparable → `v=0`, `x=null`, `y=null`.
- **FSP:** median proximal shaft axis just below lesser trochanter **or** first parallel cortices. If not identifiable → `v=0`.
- **FSD:** most distal still-visible stable mid-cortical level **inside** the image. Do not extrapolate. Numeric shortness cutoff remains **OPEN**.

Default visibility: `v=2` or `v=0` only unless P-V1 later authorizes `v=1`.

---

## 14. Future split policy

**No train/val/test split was created. No future patient was assigned to a split.**

| Rule | Requirement |
|------|-------------|
| Unit | **Patient-level** (`patient_pseudonym`), never image, never crop |
| Membership | **One patient = one split** |
| Views | All views of one patient stay in the **same** split |
| Test size | **≥15 independent patients** |
| Freeze | Test frozen **before** any training or threshold tuning |
| Optimization | **None** on the frozen test |
| Isolation | No accidental mix of B26/R26 into a future intake split without an explicit later versioning decision |
| Missing identity | `UNRESOLVED_PATIENT_ID` → no split assignment |
| Continuity probe (B26 val 5) | **Not** a frozen independent test |

`08_VALIDATED` ≠ train-ready. A later phase must define and freeze the split.

Current independent test patients: **0**. Confirmed independent patients: **26**. Pending R26: **6** (not counted). Gap to minimum 60: **34**.

---

## 15. Security model

| Asset | Classification | Access |
|-------|----------------|--------|
| `collection/01_INBOX_RAW` | **HIGHLY SENSITIVE** | Restricted. Identifying DICOM tags expected. |
| `collection/02_DEIDENTIFICATION_PENDING` | **HIGHLY SENSITIVE** | Restricted until FINAL_DEID_CHECK. |
| `restricted/linkage/` | **HIGHLY SENSITIVE** when populated | Restricted; **never** in the training dataset. |
| `collection/03_DEIDENTIFIED` … `08_VALIDATED` | De-identified research objects + workflow | Separated from linkage. Still not public training until a later phase. |
| Future ML metadata | Pseudonym + Case ID + technical/workflow fields | No direct identity. |
| HMAC secret | Restricted, off training tree | **Not created** in this phase. Must not live beside YOLO images. |

Local `.gitignore` files ignore future stage deposits and linkage contents so that a later accidental add does not commit RAW/PHI.

Named `bassin/<NAME>_` folders must not be used as drop zones or Case IDs.

---

## 16. Safety gates

| Transition | Necessary conditions | Required proof | Responsible | Rollback possible? | Failure status |
|------------|----------------------|----------------|-------------|--------------------|----------------|
| **RAW → DEID** | Authorized deposit; file in `01_INBOX_RAW`; de-id process started | `RAW_RECEIVED` record; handoff to `02_*` | Authorized operator / later de-id process | Yes — return to RAW if process aborted before overwrite | Stay `DEID_PENDING` or `REJECTED` |
| **DEID → ELIGIBILITY** | METADATA_CHECK + PIXEL_CHECK + FINAL_DEID_CHECK + SHA256_AFTER_DEID | `DEID_CONFIRMED` + hash | De-id operator + recorded check | Yes — if re-identification suspected, quarantine and do not advance | `DEID_PENDING` / `REJECTED` (`DEID_REJECTED`) |
| **ELIGIBILITY → PHYSICIAN REVIEW** | De-id confirmed; non-gated eligibility boxes complete; no unresolved identity/duplicate | Eligibility checklist; physician-gated items may still be PENDING | Eligibility reviewer | Yes — return to `ELIGIBILITY_PENDING` | `EXCLUDED` / `REJECTED` / `UNRESOLVED_PATIENT_ID` / `DOMAIN_REVIEW_REQUIRED` |
| **PHYSICIAN REVIEW → ANNOTATION** | Physician decision recorded; adult/domain/P-* items needed for annotation are not silently defaulted | `PHYSICIAN_REVIEWED` + reviewer_id | Physician / Reviewer B (medical) | Yes — hold if OPEN items block annotation | `PHYSICIAN_REVIEW_PENDING` / `EXCLUDED` |
| **ANNOTATION → QC** | Annotator A immutable record; V5/Flutter/10F–10G not used as GT | `ANNOTATED` + annotation_version | Annotator A | Yes — new version; do not overwrite raw | `ANNOTATION_PENDING` / `REJECTED` |
| **QC → VALIDATED** | QC checklist; independent review complete; adjudication if required | `QC_PASSED` + `REVIEWED` or `ADJUDICATED` | QC process + Reviewer B / adjudicator | Yes — reopen QC / adjudication | `QC_PENDING` / `EXCLUDED` / `REJECTED` |
| **VALIDATED → FUTURE DATASET** | Frozen patient-level split exists; training gate of Phase 11A §17 satisfied | Explicit later-phase promotion record | Project owner + later protocol | Yes — validated cases may remain in `08_VALIDATED` without entering YOLO | Stay in `08_VALIDATED` — **not** train-ready |

No transition was executed. No file crossed a gate.

---

## 17. Verification results

### 17.1 New tree contents

Only empty-folder markers and control text:

| Path | Files |
|------|-------|
| `collection/01_INBOX_RAW` … `10_ARCHIVE` | `.gitkeep` only (0-byte) |
| `collection/README.md`, `collection/.gitignore` | control text |
| `restricted/linkage` | `.gitkeep` only |
| `restricted/README.md`, `restricted/.gitignore` | control text |

**Real patient files in the new trees: 0.**  
**DICOM / PNG / JSON annotations copied: 0.**  
**R27 / R28 case folders: 0.**

### 17.2 Unchanged protected assets

Hashes / counts recomputed after infrastructure creation. Match Phase 11B / pre-change baseline.

| Asset | Result |
|-------|--------|
| B26 `images/train` | **21** — unchanged |
| B26 `images/val` | **5** — unchanged |
| B26 `labels/train` | **21** — unchanged |
| B26 `labels/val` | **5** — unchanged |
| B26 `images/test`, `labels/test` | **ABSENT** — no split created |
| Official B26 JSON | **26** files — not modified |
| `data.yaml` SHA256 | `aae42843f570406dd944e8bf407b08fa7a9166b22970eb6ba8f06039fa8609e8` |
| `meta/split.json` SHA256 | `011fa8ff21bc4a54cb3e5d172623317f1ab99f178323484251418b481de654b3` |
| `meta/source_mapping.csv` SHA256 | `a12a4cc719d4ce75cbc737f185b85a900cef17138cac7a1f1d1d8661afb2eb4b` |
| `R26_01.json` | `3b0fe09425b92b20187b124b08a42679e98c25b53dfc4ac8b98a7c9077f916e4` |
| `R26_02.json` | `5d80a9f1ed27b08e3fe615ca33a6da0e590f7abb7321a35981be189d55789531` |
| `R26_03.json` | `b9efefd93f39ed358a48c8f2f0a4db2985f431461cc7b1832e3e6bde46f558d0` |
| `R26_04.json` | `20f4ca54382b78ecb1c1fbbcdd62324283c656ce697457f781f03e934b152dd9` |
| `R26_05.json` | `899ae02170bf200fcd744f9f177f42083e8a554c513f329566eca6631465446a` |
| `R26_06.json` | `3bb361c0e3dc3ba180f96850dfb3f14728e46a1db4d1d01b2500cdbd90b32bbb` |
| R26 `worklist.csv` | `30ac8f1e0bc23c13c77e78fa985bd9a232931e9d0dfc3405836ddeacbaf2c73d` |
| V5 `best_it.pt` | `2e3d3e48c800c1583d427844af84835ef0115e6456ec1f6096a4acecedb257f6` |
| `bassin/a_annoter` | **26** files — not copied |
| `bassin/a_verifier` | **8** files — not copied |
| `bassin/rejetees` | **2** files — not copied |
| `datasets/yolo_pose_remediation_v2/` | **still ABSENT** |

| Asset class | Modified? |
|-------------|-----------|
| B26 images / labels / official JSON | **NO** |
| R26 stubs / worklist | **NO** |
| V5 weights | **NO** |
| Flutter / FastAPI / `mvp_geometry` / PDF / calibration | **NO** |
| Training run / inference for data creation | **NO** |
| Train/val/test created | **NO** |
| Existing files renamed or deleted | **NO** |

### 17.3 Inventory of what this phase created

1. `collection/` empty 10-stage tree + README + `.gitignore`
2. `restricted/linkage/` empty store + README + `.gitignore`
3. `datasets/yolo_pose_new_26/phase11c1_collection_infrastructure.md` (this file)

---

## 18. Remaining blockers

Infrastructure folders exist. Operational collection is **not** unblocked.

1. **REAL_PATIENT_IMPORT = NO-GO during this phase** — folders are empty by design.  
2. **De-identification pipeline still missing** — checklist only; no strip/verify/pixel-PHI tool.  
3. **Legal / consent basis for new collection** still **PHYSICIAN / PROJECT OWNER CONFIRMATION REQUIRED** (11B E9).  
4. **P-A1, P-A7, P-FOV, P-TOL, P-V1, P-C10 remain OPEN** — no defaults.  
5. **No operational HMAC / patient_pseudonym process** (correctly not implemented).  
6. **No live SHA256 / duplicate intake job.**  
7. **Historical identifying inventories** still sit in v1 / R26 worklist (not stripped; not copied forward).  
8. **R26_01–06 remain `PENDING_PHYSICIAN`** — promotion **NO-GO**.  
9. **Confirmed N = 26**; remaining_to_minimum = **34**; frozen test = **0**.  
10. **annotator_B still empty** — two-reader workflow not operational.  
11. **Unused on-disk pool is hard-only** — future collection must not be failure-only (11B §13).  
12. **Phase 11A training gate** still fully unchecked.

Audit-trail **schema** (timestamp, actor/process, old_status, new_status, reason, case_id, hash/version) is defined for later use. **No real medical audit events were written.**

---

## 19. Final verdict

# **PHASE_11C1_INFRASTRUCTURE_READY_WITH_BLOCKERS**

Empty collection staging and restricted-linkage locations now exist **outside** the training trees. Policies for Case IDs, provenance, de-identification, duplicates, workflow, eligibility, physician review, splits, security, and safety gates are documented.

The environment can **host** a future intake process. It **cannot** yet execute one.

| Gate | Status |
|------|--------|
| **TRAINING** | **NO-GO** |
| **R26_PROMOTION** | **NO-GO** |
| **REAL_PATIENT_IMPORT** | **NO-GO_DURING_THIS_PHASE** |
| New splits | **NO-GO** |
| V5 / Flutter / 10F–10G as GT | **NO-GO** |
| Phase 11C-2 | **NOT STARTED** |

---

## 20. STOP

Phase 11C-1 ends here.

Do **not** start Phase 11C-2.  
Do **not** download data.  
Do **not** process any DICOM.  
Do **not** create any patient, Case ID, or label.  
Do **not** launch any training.

---

*End of Phase 11C-1. STOP.*
