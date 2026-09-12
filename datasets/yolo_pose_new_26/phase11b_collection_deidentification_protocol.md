# Phase 11B — Collection & De-identification Protocol
## Read-Only Audit + Future Intake Protocol (STOP AFTER THIS DOCUMENT)

**Date:** 2026-09-04  
**Mode:** PROTOCOL + READ-ONLY AUDIT ONLY  
**Production model (unchanged):** V5 Phase 2  
**Predecessor (terminology preserved):** `datasets/yolo_pose_new_26/phase11a_annotation_protocol_audit.md`

**This phase does not:**
- train or fine-tune any model
- modify V5 / V5 weights / original 26-image dataset / existing labels / annotations / splits
- create a training, validation, or test split
- copy new clinical images into the YOLO dataset
- promote R26 cases into YOLO
- modify `mvp_geometry`, `/analyze`, `/measurements`, Flutter, or PDF
- implement automatic ASL refinement, ASL confidence gates, or FSP/FSD heuristics
- convert manual corrections into training data
- invent clinical thresholds
- rewrite B26 labels
- implement a production pseudonymization system
- create `datasets/yolo_pose_remediation_v2/`
- start Phase 11C

**Final verdict:** `PHASE_11B_PROTOCOL_COMPLETE` — `COLLECTION_REQUIRED` — `TRAINING_NO_GO` — `R26_NOT_PROMOTED`

---

## 1. Objective

Prepare the project for **future acquisition** of additional **real adult AP pelvis** radiographs needed for later clinical annotation and model remediation.

This document is **preparation only**. It:

- inventories current on-disk collection pools (read-only)
- records R26 status without annotating or promoting those cases
- defines eligibility, case-ID, pseudonym, de-identification, duplicate, metadata, domain, hard-example, ASL, FSD/FOV, two-reader, privacy, and future split **policies**
- states the remaining independent-patient gap

It does **not** collect new images, de-identify existing files, create hashes for images that do not yet exist, or allocate cases to splits.

Phase 11A conclusions are **not reinterpreted**. Current locked state remains:

| Fact | Status (Phase 11A, unchanged) |
|------|-------------------------------|
| Independent B26 patients | **26** |
| Additional R26 candidates currently available | **6** |
| Maximum theoretical total if all R26 later accepted | **32** |
| Minimum future target | **60–100 independent patients** |
| Preferred target | **100+** |
| Frozen independent test | **≥15 patients** |
| Current independent test set | **None** |
| ASL definition | Locked verbally; illustrated exemplars still required |
| FSD directional rule | Locked (`v=0` if distal shaft not sufficiently visible/stable) |
| FSD numeric cutoff | Unresolved |
| Disagreement tolerance | Unresolved |
| Physician double-reading on B26 | Absent |
| Physician-reviewed ASL/FSP/FSD expansion dataset | Does not exist |

---

## 2. Current pool inventory

Read-only re-inspection on 2026-09-04 confirms Phase 11A / Step D counts. **No files were moved or copied.**

### 2.1 On-disk clinical pools

| Pool | Location | Files | Role | Already used in B26? | Possible new patients? |
|------|----------|------:|------|----------------------|------------------------|
| Used seed | `bassin/a_annoter/` | **26** DICOMs | Official B26 sources | **YES — all 26** | **NO** |
| Verification hold | `bassin/a_verifier/` | **8** DICOMs | Only unused expansion pool | **NO** | **6 unique patients** after sibling de-dup (see §2.3) |
| Rejected | `bassin/rejetees/` | **2** DICOMs | Excluded unless later re-qualified | 1 same patient as B26_25; 1 unused reject | **NO** (not re-qualified) |
| Named patient folders | `bassin/<NAME>_…/` | **33 dirs, 0 files** | Empty placeholders; DICOMs already consolidated | Names correspond to known consolidated cases | **NO usable DICOMs** |
| Tracker CSV | `bassin/verification_radios.csv` | 1 file | Prior visual/adult/quality review | Covers a_annoter + a_verifier + rejetees | Not a new image source |

**Named folders must not become case IDs.** Folder names currently contain personal names. They are empty and are not an independent-patient source.

### 2.2 Frozen / derived dataset namespaces

| Namespace | Images | Labels | Role |
|-----------|-------:|-------:|------|
| `datasets/yolo_pose_new_26/` | train **21** / val **5** / test **absent** | train **21** / val **5** / test **absent** | **FROZEN** original B26 |
| `datasets/yolo_pose_remediation_v1/` | train **21** / val **5** / test **0** (empty dirs) | same | Seed copy of B26; **not** an expansion corpus |
| `datasets/yolo_pose_remediation_v2/` | — | — | **ABSENT** (not created) |
| `annotation_pilot/annotations/new_26/` | — | 26 JSON + validation artifacts | **FROZEN** B26 GT (`v=2` on 364/364 MVP landmarks) |
| `annotation_pilot/annotations/remediation_v1/` | — | 6 empty R26 stubs + worklist + README | **NOT_ANNOTATED**; not YOLO-promoted |
| `datasets/yolo_pose_remediation_v1/triage_renders/` | 8 `a_verifier` + 2 `rejetees` PNG | — | Triage only; **not** YOLO images |

### 2.3 `a_verifier` — 8 files / 6 unique patients

| File role | Unique patient vs B26 | Sibling-view status | Current disposition |
|-----------|----------------------|---------------------|---------------------|
| R26_01 selected view | Unique vs B26 (Step D) | **Has sibling** (same PatientID; alternate held) | PENDING_PHYSICIAN; not promoted |
| R26_01 sibling (not selected) | Same patient as R26_01 | Sibling of R26_01 | **HELD** — not a second independent patient |
| R26_02 | Unique vs B26 | No sibling in pool | PENDING_PHYSICIAN; not promoted |
| R26_03 | Unique vs B26 | No sibling in pool | PENDING_PHYSICIAN; not promoted |
| R26_04 selected view | Unique vs B26 | **Has sibling** (same PatientID; alternate held) | PENDING_PHYSICIAN; not promoted |
| R26_04 sibling (not selected) | Same patient as R26_04 | Sibling of R26_04 | **HELD** — not a second independent patient |
| R26_05 | Unique vs B26 | No sibling in pool | PENDING_PHYSICIAN; not promoted |
| R26_06 | Unique vs B26 | No sibling in pool | PENDING_PHYSICIAN; not promoted |

Different filename ≠ different patient. The 8 DICOMs are **6 patients**.

### 2.4 `rejetees` — still excluded

| Case | Reason (existing Step D / `verification_radios.csv`) | Independent new patient? |
|------|------------------------------------------------------|--------------------------|
| Seam / truncated-femur reject | Quality reject; not re-qualified | **NO** unless later physician re-qualification |
| Unilateral hip | Not bilateral AP pelvis; **same PatientID as B26_25** | **NO** — sibling/other-view of an existing B26 patient |

### 2.5 Pending physician review (current)

- All **6** R26 selected candidates: adult/eligibility and annotation still open.
- B26: geometric QA only; **no** independent physician double-read.
- No physician-reviewed ASL/FSP/FSD expansion dataset exists.

### 2.6 Confirmed vs pending counts (this phase)

| Category | Count | Counted as confirmed independent patients? |
|----------|------:|--------------------------------------------|
| B26 unique PatientIDs | **26** | **YES** |
| R26 selected unique patients | **6** | **NO — pending** |
| Held siblings in `a_verifier` | **2** views | **NO** (same patients as R26_01 / R26_04) |
| Rejected unused quality case | **1** | **NO** |
| Rejected B26 sibling hip | **1** | **NO** |
| Empty named folders | **33** | **NO** |
| **Confirmed independent patients** | **26** | — |
| **Pending unique-patient candidates** | **6** | — |
| **Theoretical maximum if all R26 later accepted** | **32** | Not current confirmed N |

---

## 3. R26 status

Inspected R26_01…R26_06 JSON stubs, worklist, Step D selection/inventory, `verification_radios.csv`, and source DICOM **tag presence** (values not copied into this report).

**Not done:** annotation, promotion, JSON stub edits, YOLO copy.

### 3.1 Status table

Values are only `CONFIRMED` / `PENDING` / `UNRESOLVED`. No guesswork.

| case | unique patient | adult confirmed | deidentified | annotation | status |
|------|----------------|-----------------|--------------|------------|--------|
| R26_01 | CONFIRMED | UNRESOLVED | UNRESOLVED | PENDING | PENDING |
| R26_02 | CONFIRMED | PENDING | UNRESOLVED | PENDING | PENDING |
| R26_03 | CONFIRMED | PENDING | UNRESOLVED | PENDING | PENDING |
| R26_04 | CONFIRMED | PENDING | UNRESOLVED | PENDING | PENDING |
| R26_05 | CONFIRMED | PENDING | UNRESOLVED | PENDING | PENDING |
| R26_06 | CONFIRMED | CONFIRMED | UNRESOLVED | PENDING | PENDING |

**How to read the columns**

| Column | Evidence |
|--------|----------|
| **unique patient** | Step D: 6/6 distinct PatientIDs; none overlap the 26 B26 PatientIDs. Sibling views of R26_01 and R26_04 are held and are **not** additional patients. |
| **adult confirmed** | `verification_radios.csv` `adulte` + official stubs. R26_01: age absent, `adulte=incertain` → **UNRESOLVED**. R26_02–R26_05: DICOM age 016Y/017Y recorded, `adulte=incertain`, stubs `PENDING_PHYSICIAN_ADULT_CONFIRM` → **PENDING**. R26_06: `adulte=oui` and age 094Y in the verification CSV → **CONFIRMED** as adult; annotation **feasibility** remains pending. |
| **deidentified** | Source DICOMs still have identifying tags (see §3.2). Pixel PHI was **not** visually certified in this phase. Existing inventories still store `PatientName`. → **UNRESOLVED** / operational state `DEID_PENDING`. **No case is claimed de-identified.** |
| **annotation** | All six stubs: `status=NOT_ANNOTATED`, `landmarks=[]`, `annotator_id=null`. → **PENDING**. |
| **status** | Official expansion gate remains **PENDING** (`PENDING_PHYSICIAN`). R26_06 adult confirmation does **not** promote the case. |

### 3.2 De-identification evidence (presence only — values not recorded here)

Read-only DICOM header inspection (`stop_before_pixels`):

| case | PatientName | PatientID | DOB tag | Accession | Institution | PixelSpacing |
|------|-------------|-----------|---------|-----------|-------------|--------------|
| R26_01 | PRESENT | PRESENT | EMPTY | EMPTY | PRESENT | PRESENT |
| R26_02 | PRESENT | PRESENT | PRESENT | PRESENT | EMPTY | PRESENT |
| R26_03 | PRESENT | PRESENT | PRESENT | PRESENT | EMPTY | PRESENT |
| R26_04 | PRESENT | PRESENT | PRESENT | PRESENT | EMPTY | PRESENT |
| R26_05 | PRESENT | PRESENT | PRESENT | PRESENT | EMPTY | PRESENT |
| R26_06 | PRESENT | PRESENT | PRESENT | PRESENT | EMPTY | PRESENT |

B26 source sample (B26_01 DICOM): PatientName **PRESENT**, PatientID **PRESENT**, DOB **PRESENT**.  
Existing `worklist.csv` and `selected_cases.csv` still contain a `PatientName` column. That is a **future ingestion risk**, not a license to rewrite those files in this phase.

Pixel burned-in PHI (names, hospital IDs, DOB on the image matrix): **not verified**. Status remains `DEID_PENDING`.

### 3.3 Other R26 fields (unchanged)

| Field | All R26_01–06 |
|-------|----------------|
| Relationship to B26 | Unused patients; **not** in YOLO images/labels |
| Sibling views | R26_01 and R26_04 each have one held sibling; others none in pool |
| Hard tags | Unchanged from Phase 11A / Step D (all six tagged hard; no easy controls) |
| FOV flag | `fov_policy_review_required` YES except R26_05 MAYBE |
| YOLO promotion | **NONE** |
| JSON stubs | Unmodified in this phase (hashes in §24) |

**R26 decision (locked for this protocol):** R26_01–R26_06 are **not** automatically part of any future training set. They remain `PENDING_PHYSICIAN` until the promotion gate in §21 is fully satisfied.

---

## 4. Future collection target

| Target | Value |
|--------|-------|
| **MINIMUM** | **60–100 independent patients** |
| **PREFERRED** | **100+ independent patients** |
| **FROZEN TEST** | **≥15 independent patients**, patient-level, frozen **before** training or threshold tuning |
| Confirmed independent patients now | **26** (B26 only) |
| Pending candidates (not counted) | **6** (R26) |
| Current theoretical maximum if all pending later accepted | **32** |
| Current independent test patients | **0** |

**Gap (pending cases are not confirmed):**

| Calculation | Result |
|-------------|--------|
| Minimum 60 − confirmed 26 | **34 additional independent patients required** |
| Preferred 100 − confirmed 26 | **74 additional independent patients required** (then 100+) |
| If every R26 case were later accepted (32 total) | still **28 short** of 60 — recorded only as a hypothetical; **not** current N |

**Therefore additional independent adult AP pelvis patients are required.** The on-disk unused pool cannot close the gap.

Do **not** create splits now. Do **not** allocate actual cases to train/val/test.

---

## 5. Eligibility criteria

Future intake checklist for **adult AP pelvis**. Only criteria already supported by project documentation are stated as rules. Anything not locked is marked **PHYSICIAN / PROJECT OWNER CONFIRMATION REQUIRED**.

| # | Criterion | Status | Source / note |
|---|-----------|--------|----------------|
| E1 | Adult patient | **Required** — age **cutoff not locked** | Project domain is adult coxometry. 016Y/017Y cases are already `incertain`. Numeric adult threshold = **PHYSICIAN / PROJECT OWNER CONFIRMATION REQUIRED** |
| E2 | AP pelvis radiograph | **Required** | Locked domain (`annotation_guidelines.md`, landmark spec, Phase 11A) |
| E3 | Bilateral pelvis visible when required by the MVP bilateral schema | **Required** for a case counted as a standard AP-pelvis training/eval case | Unilateral hip already rejected (B26_25 sibling). Isolated/unilateral hip → `DOMAIN_REVIEW_REQUIRED`, not automatic include |
| E4 | Sufficient anatomical coverage for the landmarks being annotated | **Required**, with honest `v=0` | Coverage follows locked ASL/FSP/FSD rules. Numeric FSD shortness cutoff = **PHYSICIAN / PROJECT OWNER CONFIRMATION REQUIRED** |
| E5 | Image quality sufficient for annotation **or** intentionally retained as a documented hard example | **Required** | Hard retention must be tagged; quality reject without a hard-example decision stays out |
| E6 | No unresolved patient identity | **Required** | If identity cannot be resolved → `UNRESOLVED_PATIENT_ID` and **HOLD** |
| E7 | No duplicate patient counted as a new independent case | **Required** | One patient = one independent-patient count |
| E8 | No sibling-view leakage across future splits | **Required** | All views of one patient stay in one split; siblings are not extra patients |
| E9 | Legally / clinically authorized source | **Required in principle** | Formal authorization, consent, or data-use basis for **new** collection is **not** specified in inspected project docs → **PHYSICIAN / PROJECT OWNER CONFIRMATION REQUIRED** |
| E10 | Same imaging domain as existing project | **Required** | Adult AP pelvis radiographs; see §11 |
| E11 | Pediatric studies | **Do not include automatically** | Pediatric DDH corpora are explicitly not adult GT |
| E12 | Prosthesis / post-operative / severe deformity | **Not a silent exclusion** | Annotation feasibility may be `v=0` per side. Blanket exclusion rule = **PHYSICIAN / PROJECT OWNER CONFIRMATION REQUIRED** |
| E13 | Sex, laterality prevalence, ethnicity, scanner vendor quotas | **Not defined** | **PHYSICIAN / PROJECT OWNER CONFIRMATION REQUIRED** — do not invent sampling quotas |
| E14 | Pregnancy, infection, contrast, or other clinical exclusion lists | **Not defined** | **PHYSICIAN / PROJECT OWNER CONFIRMATION REQUIRED** |

**Eligibility states (future intake):** `ELIGIBLE` / `PENDING_PHYSICIAN` / `DOMAIN_REVIEW_REQUIRED` / `UNRESOLVED_PATIENT_ID` / `REJECTED`.

---

## 6. Case ID policy

Future cases use a **new namespace**. Do **not** recycle `B26_XX` or `R26_XX`.

**Assigned future prefix:** `R27_` with zero-padded serials:

- `R27_001`
- `R27_002`
- `R27_003`
- …

| Rule | Requirement |
|------|-------------|
| Opaque serial | Sequential research ID only |
| Not derived from patient name | Forbidden |
| Must not contain | Patient name, hospital PatientID, date of birth, phone number, accession, or other direct identifiers |
| Not equal to filename / SOP Instance UID | Those may be stored only in restricted linkage, not as the public case ID |
| One case ID per **image** used for annotation | Multiple views of one patient get distinct case IDs **and** the same `patient_pseudonym` |
| B26 / R26 | Remain historical IDs; never reused for new patients |

---

## 7. Patient pseudonymization policy

**Define only — do not implement a production system in this phase.**

### 7.1 Two stores (mandatory separation)

| Store | Allowed content | Location |
|-------|-----------------|----------|
| **RESTRICTED LINKAGE DATA** | Mapping needed for legal/clinical trace-back and duplicate detection against hospital identity | **Outside** the training dataset tree; access-controlled; not committed to public/training manifests |
| **TRAINING DATA METADATA** | Irreversible `patient_pseudonym`, `case_id`, technical image fields, annotation/review fields | Future research/training namespace only |

The linkage file, if legally required, **must remain outside** the training dataset.

### 7.2 Training-side pseudonym requirements

| Requirement | Rule |
|-------------|------|
| Irreversible in training metadata | Training files contain only `patient_pseudonym`, never hospital PatientID / PatientName / DOB |
| Deterministic enough to detect duplicate patients | Same real patient → same pseudonym (computed from a restricted secret + hospital identity), so re-exports are joinable |
| No PatientName | Forbidden in training metadata |
| No hospital PatientID | Forbidden in training metadata |
| No DOB / address / phone / other direct identifier | Forbidden in training metadata |
| Not reversible from the training tree alone | Secret / salt / linkage table must not live beside YOLO images |

**Proposed construction (protocol only, not implemented):**

1. Authorized operator, on a restricted machine, reads hospital `PatientID` (or the project-approved identity key) from the source after legal clearance.  
2. Compute `patient_pseudonym = HMAC-SHA256(restricted_secret, normalized_hospital_patient_id)` and keep only a truncated hex form (e.g. `P_` + 16 hex chars).  
3. Write the mapping **only** to the restricted linkage store.  
4. Training manifests receive `patient_pseudonym` only.  
5. If hospital PatientID is missing and identity cannot be resolved → `UNRESOLVED_PATIENT_ID`, **HOLD**, do not invent a pseudonym from filename, folder name, or visual similarity.

Existing Step D CSVs that contain `PatientName` / hospital PatientID **must not be copied forward** into any future `yolo_pose_remediation_v2/metadata/` tree.

---

## 8. De-identification checklist

A future case may enter the research/training dataset only after **both** metadata and pixel checks pass. **Do not claim de-identification unless actually verified.**

### 8.1 DICOM metadata

Before creating the de-identified research image:

| Check | Action |
|-------|--------|
| PatientName | Removed |
| PatientID | Removed or replaced by irreversible pseudonym **only after** linkage is written to the restricted store |
| PatientBirthDate / DOB | Removed |
| Accession number | Removed where unnecessary |
| Institution identifiers | Removed where unnecessary |
| Other direct identifiers (address, phone, referring physician names if identifying, etc.) | Removed |
| Technical tags needed for QC | May retain modality, rows/columns, photometric interpretation, **PixelSpacing** if present and needed |

### 8.2 Image pixels

| Check | Action |
|-------|--------|
| Burned-in patient information | Absent |
| Name labels | Absent |
| Hospital identifiers | Absent |
| Dates of birth | Absent |
| Other PHI (ward, phone, barcode text that encodes identity) | Absent |

If burned-in PHI cannot be removed reliably → `DEID_REJECTED` or hold for physician/project-owner decision. Do not ship the identifiable pixels into the training tree.

### 8.3 De-identification states

| State | Meaning |
|-------|---------|
| `DEID_PENDING` | Source received; checklist not completed (**current state of R26 and B26 source DICOMs**) |
| `DEID_REVIEW` | Metadata stripped or pixels under visual review; not yet signed off |
| `DEID_CONFIRMED` | Metadata **and** pixel checks verified and recorded |
| `DEID_REJECTED` | Cannot be safely de-identified or failed review |

**Current project claim:** **0** cases are `DEID_CONFIRMED` in this audit.

---

## 9. Image hash

Future cases must have a **SHA256** of the **final de-identified image used for annotation**.

| Rule | Status in this phase |
|------|----------------------|
| Purpose | Provenance + exact-duplicate detection |
| When to compute | After de-identification, on the annotation PNG/array actually used |
| Existing B26 / v1 hashes | **Do not modify** (`copy_manifest.json` remains the seed provenance) |
| Hashes for images that do not exist yet | **Not created** |
| R26 source DICOM SHA256 already in Step D | Left untouched; those are **source** hashes, not “final de-identified annotation image” hashes |

---

## 10. Duplicate detection

Future intake must detect all of the following. **Different filename ≠ different patient.**

| Class | How | If detected |
|-------|-----|-------------|
| Exact duplicate image | SHA256 of final de-identified image (and, in restricted store, source DICOM SHA256) | Do not count twice; keep one case ID |
| Same patient, different view | Restricted identity / `patient_pseudonym` | Same patient; sibling-view rules apply |
| Same patient re-export | Identity + hash / study UID in restricted store | Same patient; not a new independent case |
| Same study duplicate | Restricted StudyInstanceUID / accession (linkage only) | Same study |
| Sibling pelvis views | Same `patient_pseudonym` | All views same future split; **do not** count as independent patients |

**Independent-patient count** = distinct `patient_pseudonym` values that are `ELIGIBLE` and not held.

If PatientID is missing and identity cannot be resolved:

- mark `UNRESOLVED_PATIENT_ID`
- **HOLD**
- do not assign a split
- do not guess identity from folder name, filename, or visual resemblance

---

## 11. Metadata policy

Track **only what is necessary**. Suggested future fields (documentation only):

| Field | Training metadata? | Notes |
|-------|--------------------|-------|
| `case_id` | YES | `R27_NNN` namespace |
| `patient_pseudonym` | YES | Irreversible |
| `source_pool` | YES | e.g. `future_clinical_intake`, not a personal name |
| `modality` | YES | XR / CR / DX as recorded |
| `view` | YES | Must be `AP_pelvis` or routed to domain review |
| `image_width` / `image_height` | YES | |
| `pixel_spacing_x` / `pixel_spacing_y` | YES if present | Technical; not an identifier |
| `acquisition_year_if_allowed` | YES only if allowed **and** needed | Prefer year or omit; no full study datetime in training files |
| `image_sha256` | YES | Final de-identified annotation image |
| `deidentification_status` | YES | Controlled vocabulary §8.3 |
| `duplicate_status` | YES | e.g. `UNIQUE` / `SIBLING` / `REEXPORT` / `EXACT_DUP` / `UNRESOLVED_PATIENT_ID` |
| `eligibility_status` | YES | |
| `annotation_status` | YES | §17 |
| Hospital PatientName / PatientID / DOB / phone / address / accession | **NO** | Restricted linkage only, if legally required |

Do **not** store unnecessary identifying information. Do **not** put patient names in CSV manifests intended for model training.

---

## 12. AP pelvis domain policy

Prioritize the **same imaging domain** as the locked project: **adult AP pelvis radiographs**.

| Out of locked domain | Action |
|----------------------|--------|
| Pediatric studies | Do not include automatically |
| Isolated hip views | Do not include automatically |
| Unilateral hip radiographs | Do not include automatically |
| Synthetic / GAN images | Forbidden as new patients |
| Phone photographs | Forbidden as new patients (existing camera-path docs do not make them adult GT) |
| Négatoscope photographs | Forbidden as silent domain mix |
| Unrelated projections (frog-leg, false-profile, axial, CT, MRI) | Do not include automatically |

If a case is potentially useful but outside the locked domain: mark **`DOMAIN_REVIEW_REQUIRED`**. Do **not** include automatically.

---

## 13. Hard-example collection strategy

The future collection **must** contain both:

- **A. Ordinary / control cases**
- **B. Hard cases**

**Do not collect only failures.** The current unused R26 pool is **entirely hard / uncertain** and has **zero easy new controls** (Phase 11A §3.3). That imbalance is **identified, not solved**.

### 13.1 Hard categories (reuse existing tags; do not invent a large new taxonomy)

| Category | Existing tag / code |
|----------|---------------------|
| ASL difficult visibility | `ASL_hard` |
| Acetabular overlap | `OVERLAP` |
| Pelvic rotation | `ROT_mild` / `ROTATION` |
| Low contrast | `LOW_CONTRAST` |
| Variable image quality | `QUALITY_var` / `IMAGE_QUALITY` |
| Short FOV | `SHAFT_hard` / `FOV_SHORT` |
| Clinically relevant deformity | `DEFORMITY` |
| Osteophyte / rim ambiguity | `OSTEOPHYTE_OR_RIM_AMBIGUITY` (A1) |
| Varying image size | `SIZE_var` (currently **0** in unused pool) |
| Varying acquisition conditions | track vendor/year only if non-identifying and allowed |

### 13.2 Counting rule

Do **not** claim balance before data exist. Track **actual** counts:

- independent patients
- ordinary vs hard
- per hard tag
- `v=2` vs `v=0` rates (after honest annotation)
- pending vs reviewed

Current unused-pool hard-tag counts remain those of Phase 11A (R26_01–06 only): ASL_hard 6; OVERLAP 6; ROT_mild 5; SHAFT_hard 4; QUALITY_var 2; SIZE_var 0.

---

## 14. ASL collection rule

**Locked definition (unchanged):** most **lateral** point of the radiographic / sclerotic acetabular sourcil / weight-bearing roof densification.

**Do not annotate as ASL:**

- generic lateral bony rim
- `ASM`
- AIIS tip
- osteophyte-like extension
- arbitrary acetabular edge

If sourcil and rim are inseparable:

- `v = 0`
- `x = null`
- `y = null`

**Do not guess.**  
**Do not use the V5 prediction as truth.**  
**Do not use Phase 10F / 10G research detectors as truth.**

Illustrated sourcil-vs-rim exemplars remain **P-A1** (physician). Until they exist, annotators follow the written rule and `v=0` discipline.

---

## 15. FSD / FOV rule

**Locked directional rule (unchanged):** if the distal shaft is not sufficiently visible / stable → `v = 0`.  
Do not extrapolate. Do not invent a distal coordinate.

The proposed numeric cutoff (**0.5 × head diameter**) remains **unresolved**.

**Therefore this phase:**

- does **not** implement the provisional 0.5 × head-diameter cutoff
- records `FOV_SHORT` and `FOV_POLICY_REVIEW_REQUIRED` until physician confirmation
- does **not** rewrite any existing B26 `v=2` labels

---

## 16. Unresolved physician decisions

Do not invent answers.

| ID | Question | Current status | Who must decide | What happens until decision |
|----|----------|----------------|-----------------|-----------------------------|
| **P-A1** | Illustrated sourcil-vs-rim exemplars for ASL | Verbal ASL definition locked; unique 2D point still highly ambiguous; exemplars absent | Physician (clinical teaching selection) | Annotate only when sourcil lateral end is clear; else `v=0`. No automatic ASL. |
| **P-A7** | Illustrated accepted FSP levels (“just below lesser trochanter” / first parallel cortices) | Verbal FSP definition locked; pixel-level calibration open | Physician | Follow written FSP rule; if level not identifiable → `v=0`. |
| **P-FOV** | FSD short-FOV numeric cutoff **or** explicit decision to remain directional-only | Directional lock yes; 0.5× head-diameter provisional; measurement method open | Physician | Flag `FOV_SHORT` / `FOV_POLICY_REVIEW_REQUIRED`; do not apply numeric rewrite; do not extrapolate. |
| **P-TOL** | Inter-annotator disagreement tolerance | Unresolved. Existing engineering language (>5 mm or >0.02× width) is **not** adopted as clinical tolerance | Physician | Record both readers; do not auto-average; route definitional ASL disagreements (and reviewer-flagged FSP/FSD) to adjudication. |
| **P-V1** | Whether `v=1` is allowed for ASL/FSP/FSD | Project default: forbidden unless written authorization | Physician | Use `v=2` or `v=0` only. |
| **P-C10** | Acceptable clinical landmark / angle error | Unresolved (Phase 10 doctor-requirements gap C10) | Physician | No new clinical performance threshold. Engineering pixel metrics may be reproduced; they are not clinical pass/fail. |

Related holds (not new answers): **U-N** insufficient N; **U-TEST** no frozen test; **U-R26** pending; **U-DR** double-reading not started; **U-DEID** de-identification not implemented.

---

## 17. Two-reader future workflow

```
Stage 0  De-identification          → DEID_CONFIRMED research image + hash
Stage 1  Annotator A                → ANNOTATED (immutable raw record)
Stage 2  Independent physician /
         Annotator B                → UNDER_REVIEW → REVIEWED
         (or ADJUDICATION_REQUIRED)
Stage 3  Adjudication if required   → ADJUDICATED
Stage 4  Final immutable annotation → training/eval source of truth
```

| Rule | Requirement |
|------|-------------|
| V5 prediction | May be **displayed as a proposal only** |
| V5 must never silently become ground truth | Locked |
| Flutter / Phase 10H correction | Must never automatically become training data |
| Phase 10F / 10G candidates | Not ground truth |
| Annotator A | Must not also be silent validation truth on that case |
| Reviewer B | Independent of A for validation/test (train exceptions must be documented) |
| Adjudication | Not the same unresolved pair without a recorded third decision |
| Tolerance | See P-TOL — do not auto-average |

---

## 18. Annotation statuses

Controlled states only (do not create dozens of states):

| State | Meaning |
|-------|---------|
| `NOT_ANNOTATED` | No landmark record (current R26 stubs) |
| `ANNOTATED` | Annotator A submitted |
| `UNDER_REVIEW` | Reviewer assigned / in progress |
| `REVIEWED` | Independent review complete; no adjudication needed |
| `ADJUDICATION_REQUIRED` | Disagreement exceeds (future) P-TOL or is definitional |
| `ADJUDICATED` | Final resolved record |
| `REJECTED` | Case not usable as annotation GT |

Training/eval ground truth, when a later phase allows it, is **`REVIEWED` or `ADJUDICATED` only**.

---

## 19. Future metadata schema

**Documented only — not implemented in production code, and no tracker file with real patient data is created.**

```
case_id
patient_pseudonym
image_sha256
source                 # pool tag, not a personal name
view
width
height
pixel_spacing_x
pixel_spacing_y
eligibility_status
deidentification_status
duplicate_status
annotator_id           # opaque staff ID, not a full legal name in public manifests
reviewer_id
adjudicator_id         # if used
annotation_version     # monotonic raw / reviewed / adjudicated
review_status          # §18
reason_codes           # small vocabulary from Phase 11A §16.1
hard_tags
fov_policy_review_required
```

Optional restricted-only (never in training CSV): hospital PatientID, original accession, original DICOM path, legal source reference.

---

## 20. Privacy / security separation

```
Clinical source data
        ↓
Restricted linkage / identity data     ← outside training tree
        ↓
De-identified research image           ← SHA256 after DEID_CONFIRMED
        ↓
Annotation metadata                    ← pseudonym + case_id only
        ↓
Training dataset                       ← no direct identifiers
```

| Forbidden in the training dataset | Required |
|-----------------------------------|----------|
| Patient names | Omit from training CSV / YOLO manifests |
| Hospital PatientID | Restricted linkage only |
| DOB, address, phone | Omit |
| Named patient folder paths as IDs | Do not recycle |
| Copying Step D `PatientName` columns into a new namespace | Forbidden |

Existing identifiable inventories (`candidate_inventory.csv`, `selected_cases.csv`, `worklist.csv`, `_stepD_state.json`) are **historical restricted-adjacent artifacts**. Phase 11B does not strip them. They must **not** be the template for future training metadata.

---

## 21. Future patient-level split policy

**DO NOT create splits in this phase. DO NOT allocate actual cases.**

| Rule | Requirement |
|------|-------------|
| Unit of split | **One patient = one split** |
| Views | All views from the same patient remain in the **same** split |
| Test | Independent, patient-level, **frozen before training**, never used for threshold tuning |
| Minimum test size | **≥15 independent patients** |
| Missing identity | `UNRESOLVED_PATIENT_ID` → no split assignment |
| Continuity probe (B26_10/13/17/20/26) | May be reported separately for V5 baseline continuity; **not** a frozen independent test set |
| Flip / mosaic / crop | Never counted as a new patient |

Current test set: **empty**. Designing membership now would be fabrication.

---

## 22. Collection tracking (fields only)

**No tracker file is created** (would risk carrying real identifiers). Proposed columns for a **future** empty template, to be instantiated only after de-identification and pseudonym processes exist:

```
case_id
patient_pseudonym
eligibility
deidentification
duplicate_check
annotation
review
adjudication
hard_tags
reason_codes
final_status
```

Do not put hospital names or PatientName in that future file.

---

## 23. R26 promotion gate

R26_01–R26_06 are **NOT** automatically part of the future training set.

They require **all** of:

1. Adult eligibility confirmation  
2. De-identification confirmation (`DEID_CONFIRMED`, metadata **and** pixels)  
3. Duplicate / sibling verification  
4. Physician annotation  
5. Independent review  
6. Adjudication if needed  

Until then: **`PENDING_PHYSICIAN`**.  
Do not modify them. Do not promote them. Do not treat empty stubs as labels.

---

## 24. Explicit NO-GO / not training ground truth

### 24.1 Not training ground truth

- V5 predictions  
- `refined_landmarks`  
- Phase 10H corrections  
- Phase 10F candidates  
- Phase 10G candidates  
- R26 empty stubs  
- B26 single-annotator labels **unless later physician-reviewed under this future protocol**

### 24.2 NO-GO conditions (still in force)

| Condition | Current state |
|-----------|---------------|
| Fewer than 60 confirmed independent cases | **YES — 26** |
| Pending cases counted as confirmed | Forbidden; 6 remain pending |
| Independent frozen test ≥15 | **ABSENT** |
| Patient leakage on a non-existent expansion split | Cannot be proven; do not fabricate a split |
| ASL exemplars absent | **YES** (P-A1 open) |
| FSD numeric policy unresolved | **YES** (P-FOV open) |
| Expansion annotations not physician-reviewed | **YES** |
| De-identification not confirmed | **YES — 0 DEID_CONFIRMED** |
| Training on the 26-image seed alone as “remediation” | Forbidden |
| Promoting 10E–10G detectors / ASL confidence gates | Forbidden |
| Rewriting original B26 labels in place | Forbidden |
| Phone-négatoscope or synthetic/flip duplicates as new patients | Forbidden |
| Implementing 0.5× head-diameter cutoff | Forbidden until P-FOV |

---

## 25. Exact files inspected

Read-only. No inspected file was modified.

### 25.1 Phase 11A / 10C–10H / definitions

- `datasets/yolo_pose_new_26/phase11a_annotation_protocol_audit.md`
- `datasets/yolo_pose_new_26/phase10c_stepA_definition_fov_lock.md`
- `datasets/yolo_pose_new_26/phase10c_stepD_source_inventory.md`
- `datasets/yolo_pose_new_26/phase10c_stepD_selection_report.md`
- `datasets/yolo_pose_new_26/phase10_doctor_requirements_gap_analysis.md` (C10)
- `docs/annotation_guidelines.md`
- `docs/annotation_pilot_protocol.md`
- `docs/landmark_specification.md` *(domain / adult AP pelvis; via prior lock)*

### 25.2 Collection pools

- Directory listing of `bassin/` (33 empty named dirs + `a_annoter` + `a_verifier` + `rejetees`)
- File listing of `bassin/a_annoter/` (26), `bassin/a_verifier/` (8), `bassin/rejetees/` (2)
- `bassin/verification_radios.csv`
- Presence-only DICOM tag read on the six R26 source files + B26_01 source sample

### 25.3 Remediation / annotation artifacts

- `datasets/yolo_pose_remediation_v1/meta/selected_cases.csv`
- `datasets/yolo_pose_remediation_v1/meta/candidate_inventory.csv` (header + empty-dir / pool schema)
- `datasets/yolo_pose_remediation_v1/meta/_stepD_state.json`
- `datasets/yolo_pose_remediation_v1/meta/provenance.md`
- `datasets/yolo_pose_remediation_v1/meta/copy_manifest.json`
- `datasets/yolo_pose_remediation_v1/meta/split.json`
- `annotation_pilot/annotations/remediation_v1/README.md`
- `annotation_pilot/annotations/remediation_v1/worklist.csv`
- `annotation_pilot/annotations/remediation_v1/R26_01.json` … `R26_06.json`
- `annotation_pilot/annotations/new_26/` listing (26 JSON + validation artifacts)
- `annotation_pilot/annotations/new_26/B26_01.json` (schema sample)
- `datasets/yolo_pose_new_26/meta/split.json`
- `datasets/yolo_pose_new_26/meta/source_mapping.csv` (header + mapping shape)
- Directory counts: original and v1 `images/{train,val}`, `labels/{train,val}`, v1 empty `test`, triage renders

### 25.4 V5 (existence / hash only — not loaded for training)

- Path reference in `backend/app/services/detection/v5_phase2_pose.py`
- File present: `runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/weights/best_it.pt`

### 25.5 Confirmed absent

- `datasets/yolo_pose_new_26/images/test/`
- `datasets/yolo_pose_new_26/labels/test/`
- `datasets/yolo_pose_remediation_v2/`

---

## 26. Confirmation of zero code / data / model modifications

### 26.1 Verification method

1. Re-counted pool and dataset directories (PowerShell listings).  
2. Recomputed SHA256 of all **26** original images and **26** original labels and compared them to `copy_manifest.json` (`image_sha256` / `label_sha256`).  
3. Recomputed SHA256 of the **26** v1 seed images and **26** v1 seed labels against the same manifest.  
4. Hashed the six R26 JSON stubs; confirmed `landmarks=[]` and `status=NOT_ANNOTATED`.  
5. Confirmed original `meta/split.json` still has train 21 / val 5 / **no test key membership** (test length 0).  
6. Confirmed v1 `meta/split.json` still `test: []`, `final_evaluation_ready: false`.  
7. Confirmed V5 `best_it.pt` still exists at the production path (size 24 963 226 bytes; SHA256 below). **Not opened for training.**  
8. Confirmed `yolo_pose_remediation_v2` absent.  
9. This session wrote **only** the present markdown file.

### 26.2 Hash results (2026-09-04)

| Check | Result |
|-------|--------|
| Original 26 images vs `copy_manifest` | **26/26 match** |
| Original 26 labels vs `copy_manifest` | **26/26 match** |
| v1 26 images vs same hashes | **26/26 match** |
| v1 26 labels vs same hashes | **26/26 match** |
| Image + label mismatches | **0** |
| Missing seed files | **0** |
| new_26 JSON | **26** files; **364** landmarks; **364** `v=2` (unchanged inventory) |

R26 stub SHA256 (unchanged; empty landmarks):

| File | SHA256 |
|------|--------|
| `R26_01.json` | `3b0fe09425b92b20187b124b08a42679e98c25b53dfc4ac8b98a7c9077f916e4` |
| `R26_02.json` | `5d80a9f1ed27b08e3fe615ca33a6da0e590f7abb7321a35981be189d55789531` |
| `R26_03.json` | `b9efefd93f39ed358a48c8f2f0a4db2985f431461cc7b1832e3e6bde46f558d0` |
| `R26_04.json` | `20f4ca54382b78ecb1c1fbbcdd62324283c656ce697457f781f03e934b152dd9` |
| `R26_05.json` | `899ae02170bf200fcd744f9f177f42083e8a554c513f329566eca6631465446a` |
| `R26_06.json` | `3bb361c0e3dc3ba180f96850dfb3f14728e46a1db4d1d01b2500cdbd90b32bbb` |

V5 checkpoint (not modified):  
`runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/weights/best_it.pt`  
SHA256 `2e3d3e48c800c1583d427844af84835ef0115e6456ec1f6096a4acecedb257f6`

### 26.3 Modification matrix

| Asset | Modified in Phase 11B? |
|-------|------------------------|
| `datasets/yolo_pose_new_26/images/` | **NO** |
| `datasets/yolo_pose_new_26/labels/` | **NO** |
| Original 26 annotations (`new_26`) | **NO** |
| `data.yaml` / `meta/split.json` / `meta/source_mapping.csv` | **NO** |
| v1 images / labels | **NO** |
| R26 JSON stubs | **NO** |
| V5 Phase 2 weights / checkpoints | **NO** |
| Flutter production code | **NO** |
| `/analyze`, `/measurements`, `mvp_geometry` | **NO** |
| PDF | **NO** |
| Training run | **NO** |
| Splits created | **NO** |
| Images copied | **NO** |
| Labels created | **NO** |
| Tracker file with patient data | **NO** |
| `yolo_pose_remediation_v2` created | **NO** |
| Phase 11C started | **NO** |

**Sole artifact created:** this file  
`datasets/yolo_pose_new_26/phase11b_collection_deidentification_protocol.md`

---

## 27. STOP

Phase 11B ends here. **Do not start Phase 11C in this session.**

Suggested later work (only when explicitly approved): obtain authorized additional real adult AP pelvis cases; implement de-identification **after** legal clearance; physician lock of P-A1 / P-A7 / P-FOV / P-TOL / P-V1 / P-C10; then — in a later phase — annotation under the two-reader protocol.

Still forbidden until a later phase says otherwise: training, V5 modification, original-26 edits, automatic ASL, split fabrication, R26 YOLO promotion.

---

*End of Phase 11B. STOP.*
