# Phase 11C-0 — Strict Collection-Environment Audit

**Date:** 2026-09-04  
**Mode:** READ-ONLY ENVIRONMENT AUDIT ONLY  
**Predecessor documents (terminology preserved, not reinterpreted):**
- `datasets/yolo_pose_new_26/phase11a_annotation_protocol_audit.md`
- `datasets/yolo_pose_new_26/phase11b_collection_deidentification_protocol.md`

**This phase does not:**
- train or fine-tune any model
- modify V5 / weights / B26 / labels / annotations / splits
- create a training dataset or train/val/test split
- copy images, create annotations, or promote R26
- modify Flutter, FastAPI, `mvp_geometry`, PDF, calibration, or ASL/FSP/FSD rules
- download or import new data
- delete or rename existing files
- create any folder structure that does not already exist
- start Phase 11C-1

**Final verdict:** `PHASE_11C0_AUDIT_COMPLETE_WITH_BLOCKERS`  
**TRAINING = NO-GO**  
**R26_PROMOTION = NO-GO**  
**DATASET_MODIFICATION = NO-GO**

---

## 1. Scope

Audit **only** whether the current repository can **receive** additional independent adult AP-pelvis cases under the Phase 11A/11B protocol.

Questions A–I (collection drop zone, dedicated inbox, raw/de-id/validation separation, provenance, SHA256, duplicates, patient-level split protection, pseudonym, identity/training separation) are answered from **existing** files and directories. Missing capability is reported as missing. No missing folder is created.

Phase 10D–10H are used only for locked implications:

| Phase | Locked implication for collection |
|-------|-----------------------------------|
| 10D | Learned remediation on 21 train patients is **not safe**; crops are not new patients; need real additional cases |
| 10E | ASL = sourcil ≠ rim; unique 2D point remains ambiguous without exemplars / `v=0` |
| 10F | Sourcil detectability **PARTIAL**; research candidates are **not** GT |
| 10G | Automatic ASL localization **PARTIAL**; confidence gate **UNCERTAIN**; do not implement |
| 10H | Flutter correction bridge works; corrections are **not** training GT |

Physician-gated items P-A1, P-A7, P-FOV, P-TOL, P-V1, P-C10 remain **unresolved**. This audit does not answer them.

---

## 2. Files / directories inspected

Read-only. No inspected file was modified.

### 2.1 Protocol / prior audits

- `datasets/yolo_pose_new_26/phase11a_annotation_protocol_audit.md`
- `datasets/yolo_pose_new_26/phase11b_collection_deidentification_protocol.md`
- `datasets/yolo_pose_new_26/phase10c_stepD_source_inventory.md`
- `datasets/yolo_pose_new_26/phase10c_stepD_selection_report.md`
- `datasets/yolo_pose_new_26/phase10c_stepA_definition_fov_lock.md`
- `datasets/yolo_pose_new_26/phase10d_small_data_refinement_audit.md` (header / verdict)
- `datasets/yolo_pose_new_26/phase10e_coxometry_domain_audit.md` (header)
- `datasets/yolo_pose_new_26/phase10f0_sourcil_structure_audit.md` (header / verdict)
- `datasets/yolo_pose_new_26/phase10g0_asl_success_failure_analysis.md` (header / verdict)
- `datasets/yolo_pose_new_26/phase10h_validation_report.md` (verdict)
- `docs/annotation_guidelines.md` *(domain: adult AP pelvis; via prior lock)*

### 2.2 B26 / R26 / pool artifacts

- `datasets/yolo_pose_new_26/data.yaml`
- `datasets/yolo_pose_new_26/meta/split.json`
- `datasets/yolo_pose_new_26/meta/source_mapping.csv` (header + mapping shape)
- `annotation_pilot/annotations/new_26/validation_summary.md`
- `annotation_pilot/annotations/new_26/worklist.csv` (header)
- `annotation_pilot/annotations/remediation_v1/README.md`
- `annotation_pilot/annotations/remediation_v1/worklist.csv`
- `annotation_pilot/annotations/remediation_v1/R26_01.json` … `R26_06.json` *(presence/status only; not edited)*
- `datasets/yolo_pose_remediation_v1/README.md`
- `datasets/yolo_pose_remediation_v1/meta/provenance.md`
- `datasets/yolo_pose_remediation_v1/meta/copy_manifest.json` (hash schema)
- `datasets/yolo_pose_remediation_v1/meta/candidate_inventory.csv` (header)
- `datasets/yolo_pose_remediation_v1/meta/selected_cases.csv`
- `datasets/yolo_pose_remediation_v1/meta/_stepD_state.json`
- `datasets/yolo_pose_remediation_v1/meta/_stepD_run_inventory_render.py`
- `datasets/yolo_pose_remediation_v1/meta/qa_checklist.md`
- `datasets/yolo_pose_remediation_v1/meta/split.json`
- `bassin/verification_radios.csv`
- Directory listing of `bassin/` (33 empty named dirs + `a_annoter` + `a_verifier` + `rejetees`)

### 2.3 Tools that could relate to DICOM / PHI / hash

- `annotation_pilot/manual_annotation_tool/dicom_render.py`
- `annotation_pilot/manual_annotation_tool/verification_radios.py`
- Project-wide search for anonymization / de-identification / PHI-removal scripts (**none in project code**)
- Project-wide search for `R27_` case IDs (**protocol text only; no cases exist**)

### 2.4 Confirmed absent (not created)

| Path | Status |
|------|--------|
| Dedicated intake inbox (`bassin/incoming`, `bassin/a_collecter`, `datasets/incoming`, `datasets/collection`) | **ABSENT** |
| Raw / de-identified / validated staging (`bassin/raw`, `bassin/deidentified`, `bassin/validees`) | **ABSENT** |
| Restricted linkage store (`restricted/`, `linkage/`) | **ABSENT** |
| `datasets/yolo_pose_remediation_v2/` | **ABSENT** |
| `annotation_pilot/annotations/annotator_B/` files | Directory empty (**0 files**) |
| Any `R27_*` case file | **ABSENT** |

---

## 3. Answers A–I (collection environment)

### A. Where can new DICOMs currently be deposited?

**There is no designated future-collection drop zone.**

If a file were added today, the only existing clinical directories are:

| Path | What it actually is | Safe inbox for new independent cases? |
|------|---------------------|----------------------------------------|
| `bassin/a_annoter/` | **26 used B26 source DICOMs** | **NO** — mixing would contaminate the frozen seed source pool |
| `bassin/a_verifier/` | **8** hold DICOMs (6 unique pending patients + 2 siblings) | **NO** — already an R26/eligibility hold, not an empty intake inbox |
| `bassin/rejetees/` | **2** rejected DICOMs | **NO** — reject sink, not intake |
| `bassin/<NAME>_…/` (33 dirs) | Empty placeholders; **names are identifying** | **NO** — 0 files; using these as IDs violates the Phase 11B case-ID rule |
| YOLO `images/{train,val}` | Frozen B26 PNGs | **NO** — training tree; Phase 11B forbids copying new clinical images here |

**Factual deposit answer:** a new DICOM has **no project-approved landing folder**. The filesystem could physically accept a file in `bassin/` or elsewhere, but that would be an **ad-hoc drop**, not a collection environment.

### B. Dedicated collection folder?

**NO.**

No `incoming` / `intake` / `collection` / `a_collecter` directory exists. Phase 11B documented a **future** namespace and tracker fields only. Phase 11A’s proposed `yolo_pose_remediation_v2/` was **not created**.

### C. Clear separation of raw / de-identified / pending validation / validated / rejected?

**NO — only an informal clinical-triage split, not a de-identification pipeline.**

| Needed stage (Phase 11B) | Current analogue | Fit? |
|--------------------------|------------------|------|
| Raw / not de-identified | `bassin/a_annoter`, `a_verifier`, `rejetees` (all still carry identifying DICOM tags) | All current DICOMs are **raw-identifiable**. There is no “raw-only” inbox distinct from used seed. |
| De-identified research image | — | **MISSING** |
| Pending physician / eligibility | `bassin/a_verifier/` + `verification_radios.csv` `incertain` | **PARTIAL** (eligibility hold only; not de-id review) |
| Validated for annotation / training | B26 already in YOLO + `new_26` JSON | **PARTIAL** for the frozen 26; **MISSING** for future cases |
| Rejected | `bassin/rejetees/` | **PARTIAL** (quality/view reject, not DEID_REJECTED) |

`DEID_PENDING` / `DEID_REVIEW` / `DEID_CONFIRMED` / `DEID_REJECTED` are **protocol states only**. No folders or manifests implement them.

### D. Traceability / provenance mechanism?

**PARTIAL — historical B26/R26 provenance exists; future intake provenance does not.**

| Existing mechanism | What it traces | Gap |
|--------------------|----------------|-----|
| `meta/source_mapping.csv` (B26) | `B26_XX` ↔ YOLO PNG/TXT ↔ JSON ↔ source DICOM path + size | No PatientID, no SHA256, no de-id status, no reviewer |
| v1 `copy_manifest.json` + `provenance.md` | Byte-identical seed copy of 26 PNG/TXT | Copy audit only |
| Step D `candidate_inventory.csv` / `_stepD_state.json` | DICOM path, **hospital PatientID + PatientName**, `dicom_sha256`, eligibility | Identifiable; one-shot inventory; not a future intake ledger |
| R26 worklist + JSON stubs | Case ID ↔ source DICOM filename ↔ hard tags | Contains `patient_name`; empty landmarks |
| `verification_radios.csv` | Filename ↔ adult/quality/usable flags | No patient key; no hash |

There is **no** restricted linkage file, **no** `patient_pseudonym` store, and **no** live provenance writer for new deposits.

### E. SHA256 mechanism?

**PARTIAL — one-shot hash functions exist; no intake hash of a final de-identified image.**

| What exists | Role |
|-------------|------|
| `copy_manifest.json` `image_sha256` / `label_sha256` | Frozen B26 PNG + YOLO labels |
| Step D `dicom_sha256` | Source DICOM bytes (identifiable files) |
| Step D `render_sha256` | Triage PNG bytes (not de-identified research images) |
| `_stepD_run_inventory_render.py` `sha256_file()` | Reusable **function** used once for inventory |

Phase 11B requires SHA256 of the **final de-identified annotation image**. That object **does not exist** for future cases, and no script computes it on intake. Existing hashes must **not** be treated as de-id confirmation.

### F. Duplicate-detection mechanism?

**PARTIAL — a completed Step D inventory, not an operational intake gate.**

Step D already demonstrated, **once**, on the current disk pool:

- same PatientID across two `a_verifier` files (siblings of R26_01 and R26_04)
- same PatientID as B26_25 in `rejetees` (unilateral hip)
- `already_used_as_b26` via DICOM filename ↔ `source_mapping.csv`
- `dicom_sha256` per inventoried file
- explicit rule: different filename ≠ different patient

What does **not** exist:

- an intake job that hashes a newly dropped file and compares it to B26 + R26 + future cases
- a study/series UID index for re-exports
- a de-identified-image hash index
- a non-identifying `patient_pseudonym` join key for future files
- protection against a human dropping a new file into `a_annoter` or a named folder without running Step D again

**If a new DICOM arrived tomorrow, no automatic duplicate check would run.**

### G. Mechanism to keep one patient out of multiple future splits?

**PARTIAL policy, no operational mechanism for future cases.**

| Exists | Missing |
|--------|---------|
| Phase 11A/11B rule: one patient = one split | No future split (and none may be created now) |
| B26: 26 distinct PatientIDs; current train/val are case-level and happen to be 1:1 with patients | `split.json` stores **case IDs**, not patient keys |
| Step D held siblings out of YOLO | No patient-level registry for **new** intake |
| Continuity probe documented as **not** an independent test | Frozen test set **absent** |

`source_mapping.csv` has no patient field. Training metadata cannot currently join two future views of the same person without reading identifiable DICOM tags or the Step D name/ID CSVs.

### H. Metadata that identifies a patient **without** keeping real identity in training data?

**MISSING in implementation. Documented only.**

Phase 11B proposed `patient_pseudonym = HMAC-SHA256(restricted_secret, hospital_patient_id)` and a restricted linkage store. **Neither is implemented.**

Current identity handles:

| Handle | In training tree? | Identifying? |
|--------|-------------------|--------------|
| `B26_XX` / `R26_XX` | Case IDs in YOLO / stubs | Opaque **case** IDs, not a patient pseudonym system |
| Hospital PatientID | Step D CSVs + DICOM headers | **YES — real ID** |
| PatientName | Step D CSVs, R26 worklist, named folders, DICOM | **YES** |
| `patient_pseudonym` | — | **Does not exist** |

B26 `source_mapping.csv` correctly omits PatientID — but then **no** irreversible patient key exists on the training side at all.

### I. Separation between potentially identifying clinical data and training metadata?

**INSUFFICIENT.**

```
Actual current layout (not the Phase 11B target):

  bassin/*.dcm          ← identifying DICOM tags PRESENT (Phase 11B sample)
  bassin/<NAME>_…/      ← identifying folder names; empty
  remediation_v1/meta/* ← PatientName + PatientID in inventory CSVs/JSON
  remediation_v1 worklist ← PatientName
  yolo_pose_new_26/     ← B26_XX PNG/TXT + source_mapping without PatientID
        but no de-id status, no pseudonym, no restricted store
```

Phase 11B required:

```
Clinical source → Restricted linkage → De-identified image → Annotation metadata → Training dataset
```

That chain is **not instantiated**. Identifying inventories sit **inside** `datasets/yolo_pose_remediation_v1/meta/` and `annotation_pilot/annotations/remediation_v1/`. Phase 11A/11B already flagged this as a future ingestion risk and forbade copying those columns forward. This audit confirms the risk is **still present** and **not remediated** (by design: this phase does not strip files).

---

## 4. Current patient state

Pending cases are **not** counted as confirmed.

### 4.1 B26 — confirmed

| Item | Value |
|------|--------|
| Confirmed independent patients | **26** (distinct DICOM PatientIDs, Step D / Phase 11A) |
| Cases / images | **26** PNG (train 21 + val 5); **26** YOLO labels; **26** JSON |
| Locations | Sources: `bassin/a_annoter/` (26 DICOM). Training images: `datasets/yolo_pose_new_26/images/{train,val}`. Labels: `labels/{train,val}`. GT: `annotation_pilot/annotations/new_26/` |
| Status | **FROZEN** seed. Single annotator `annotator_A`. All 364 MVP landmarks `v=2`. Geometric QA only. **No** physician double-read. **No** `DEID_CONFIRMED`. `data.yaml` has **no test** set. |
| Independent frozen test | **0** |

`new_26/worklist.csv` still lists annotation `status=pending` as a historical worklist field; `validation_summary.md` (2026-08-23) reports 26/26 JSON valid. That worklist word does **not** mean the JSON is empty. Official GT files are complete and frozen.

### 4.2 R26_01–R26_06 — pending (not confirmed)

| case | Present | Patient key | Pseudonym | Annotation | Validation / review | Dup vs B26 | Eligibility |
|------|---------|-------------|-----------|------------|---------------------|------------|-------------|
| R26_01 | YES (stub + source DICOM + sibling held) | Hospital PatientID in Step D / worklist | **NONE** | `NOT_ANNOTATED` | None | Unique vs B26; **sibling view** held | Adult **UNRESOLVED**; `PENDING_PHYSICIAN` |
| R26_02 | YES | Hospital PatientID | **NONE** | `NOT_ANNOTATED` | None | Unique vs B26 | Adult **PENDING**; `PENDING_PHYSICIAN` |
| R26_03 | YES | Hospital PatientID | **NONE** | `NOT_ANNOTATED` | None | Unique vs B26 | Adult **PENDING**; `PENDING_PHYSICIAN` |
| R26_04 | YES | Hospital PatientID | **NONE** | `NOT_ANNOTATED` | None | Unique vs B26; **sibling view** held | Adult **PENDING**; `PENDING_PHYSICIAN` |
| R26_05 | YES | Hospital PatientID | **NONE** | `NOT_ANNOTATED` | None | Unique vs B26 | Adult **PENDING**; `PENDING_PHYSICIAN` |
| R26_06 | YES | Hospital PatientID | **NONE** | `NOT_ANNOTATED` | None | Unique vs B26 | Adult **CONFIRMED** in `verification_radios.csv`; annotation feasibility still **PENDING_PHYSICIAN** |

Hospital PatientIDs and names are **not repeated here**. They remain in existing Step D / worklist files. They are **not** training pseudonyms.

**R26 promotion:** **NO-GO** (Phase 11B §23 unchanged).

### 4.3 Other pools

| Pool | Files | Independent new confirmed patients? |
|------|------:|-------------------------------------|
| `bassin/a_annoter` | 26 | **NO** — already B26 |
| `bassin/a_verifier` | 8 | **NO** — 6 pending unique + 2 siblings |
| `bassin/rejetees` | 2 | **NO** — 1 quality reject; 1 B26_25 sibling hip |
| 33 named folders | 0 | **NO** |
| `annotator_B` | 0 | **NO** second reader |

**Confirmed independent patients = 26. Pending unique-patient candidates = 6.**

---

## 5. Future collection capacity

| Quantity | Value |
|----------|------:|
| `confirmed_patients_current` | **26** |
| `minimum_target` | **60** |
| `preferred_target` | **100** |
| `frozen_test_target` | **15** |
| `remaining_to_minimum` | **34** |
| `remaining_to_preferred` | **74** |
| Current independent test patients | **0** |
| Theoretical max if all R26 later accepted | **32** (hypothetical; **not** current N) |

**Can the project currently host ≥60 / ≥100 / ≥15 frozen-test patients as a collection environment?**

| Need | Exists? |
|------|---------|
| Physical disk space in the repo | Irrelevant — no intake tree |
| Dedicated inbox + staging for 60–100 arrivals | **NO** |
| De-identified store sized for 100+ | **NO** |
| Patient-level registry to reserve ≥15 test patients | **NO** |
| Empty YOLO `test/` on v1 | Empty dirs only; **not** a collection capacity |

The environment **cannot** currently receive the target corpus under the Phase 11B protocol. This audit **does not create** that structure.

---

## 6. DICOM / de-identification

**No DICOM was modified.**

### 6.1 Project-owned tools

| Asset | De-identification role |
|-------|------------------------|
| `dicom_render.py` | Reads full DICOM (including pixels) and writes a **display PNG**. Does **not** strip tags, does **not** scan burned-in PHI, does **not** produce a de-identified DICOM. Comment states originals in `a_annoter` are never modified. |
| `verification_radios.py` | Reads `verification_radios.csv`; no PHI handling |
| Step D inventory script | **Extracts** PatientName, PatientID, age, study/series text into CSV/JSON — the opposite of de-identification |
| FastAPI / Flutter | Phase 6A/7B already note burned-in film text is **not stripped**; not a collection de-id pipeline |
| Search in `annotation_pilot/` and `backend/` for anonymize / de-identify / PatientBirthDate / AccessionNumber / burned-in | **No project implementation** |

Third-party packages under `.venv` (e.g. radstract DICOM export helpers) are **not** a project collection process and were not invoked.

### 6.2 Process checklist (exists vs missing)

| Step | Exists? |
|------|---------|
| 1. Identify sensitive fields | **PARTIAL** — Phase 11B checklist names PatientName, PatientID, DOB, accession, institution, pixel PHI. Phase 11B performed **presence-only** tag reads on R26 + B26_01 sample (identifiers **PRESENT**). No reusable QC tool. |
| 2. Remove / replace them | **MISSING** |
| 3. Verify they actually disappeared | **MISSING** |
| 4. Control pixels for burned-in PHI | **MISSING** (explicitly unverified in Phase 11B) |
| 5. Produce a de-identified version | **MISSING** |
| 6. SHA256 the final de-identified image | **MISSING** (only source/copy/triage hashes exist) |

**Current de-identification status of on-disk cases:** `DEID_PENDING` / **UNRESOLVED**. **0** `DEID_CONFIRMED`.

Private tags / StudyInstanceUID / SeriesInstanceUID: not systematically inventoried as a de-id pipeline. Step D reads SOP Instance UID into inventory; that is provenance extraction, not anonymization.

---

## 7. Duplicates / patient leakage

| Risk | Existing control | Operational for new intake? |
|------|------------------|-----------------------------|
| Same patient, different filenames | Step D PatientID grouping (`multi_patient_images`) | **NO** — one-shot |
| Exact image copy | `dicom_sha256` / PNG SHA256 in manifests | **NO** live compare |
| Same DICOM, several paths | Inventory by filename + hash | **NO** watch on new paths |
| Same patient, several folders | Named folders empty; DICOMs consolidated | Fragile; named folders still invite identity-based drops |
| Same study, several series | Not indexed as a study/series registry | **MISSING** |
| Exact hash duplicate | Functions exist; no intake index | **NOT_READY** |
| Patient in two future splits | Policy only | **NOT_READY** — no future split, no patient key in `split.json` |

**Clear statement:** there is **no reliable operational mechanism** that would prevent a newly dropped case from being a duplicate or a B26/R26 sibling. Historical Step D was reliable **for the files then on disk**. It is not an intake service.

---

## 8. Future Case ID (`R27_001` …)

| Check | Result |
|-------|--------|
| Convention proposed in Phase 11B | `R27_` + zero-padded serial (`R27_001`, …) |
| Collision with B26 / R26 | **None** — different prefix |
| Any `R27_*` already created | **NO** — this phase creates none |
| Contains name / DOB / hospital ID | Convention **forbids** it; current **named bassin folders** would violate it if reused as IDs |
| Ambiguity | **Low** if operators use only `R27_NNN` and never derive IDs from `bassin/<NAME>_` |

The convention **can** be applied without ambiguity **once an intake process exists**. It is **not applied** in this phase.

---

## 9. Future provenance fields

Implementation status of the Phase 11B / requested field list. **No data created.**

| Field | Status | Evidence |
|-------|--------|----------|
| `case_id` | **PARTIAL** | B26 / R26 IDs exist; `R27_` namespace unused |
| `patient_pseudonym` | **MISSING** | Protocol only |
| `source` | **PARTIAL** | Pool tags (`a_annoter`, `a_verifier`) on existing cases |
| `source_type` | **MISSING** | Not a controlled field today |
| `acquisition_year_if_allowed` | **MISSING** in training metadata | StudyDate exists on some DICOMs (identifying store), not extracted as year-only training field |
| `view` | **PARTIAL** | B26/R26 JSON `view: AP_pelvis`; verification CSV `AP` |
| `image_hash_sha256` | **PARTIAL** | Source/copy/triage hashes; not final-de-id-image hashes |
| `deidentification_status` | **MISSING** | Protocol vocabulary only; all current = pending/unresolved |
| `eligibility_status` | **PARTIAL** | Step D / verification CSV for existing files only |
| `annotation_status` | **PARTIAL** | R26 `NOT_ANNOTATED`; B26 complete JSON; Phase 11B states not used as a live tracker |
| `reviewer_status` / review | **MISSING** | No annotator_B adult files |
| `annotation_version` | **MISSING** | `guidelines_version` on JSON ≠ versioned raw/reviewed/adjudicated |
| `annotator_id` | **PARTIAL** | B26 `annotator_A`; R26 `null` |
| `reviewer_id` | **MISSING** | |
| `adjudication_id` | **MISSING** | |
| `exclusion_reason` | **PARTIAL** | `verification_radios.csv` / Step D `exclusion_reason` for current pool |
| `provenance_notes` | **PARTIAL** | Free-text notes on R26 stubs / Step D |

---

## 10. Future eligibility (protocol distinction — not applied to new cases)

Phase 11B already distinguishes include vs hold. This audit **does not** decide physician-gated medical cutoffs.

| Intended class | Covered by existing protocol? | Still physician-gated? |
|----------------|-------------------------------|------------------------|
| INCLUDE: adult | Yes as required criterion | **YES** — numeric age cutoff not locked (016Y/017Y already `incertain`) |
| INCLUDE: AP pelvis in domain | Yes | Domain mix → `DOMAIN_REVIEW_REQUIRED` |
| INCLUDE: exploitable **or** documented hard example | Yes | Quality vs hard-retention is a documented choice |
| INCLUDE: independent patient | Yes | Identity unresolved → HOLD |
| INCLUDE: acceptable de-identification | Yes as gate | Process **not implemented** |
| HOLD/EXCLUDE: pediatric | Yes — do not include automatically | Adult definition open |
| HOLD/EXCLUDE: non-AP / unilateral hip | Yes (ZAFFOU-type reject already used) | — |
| HOLD/EXCLUDE: unusable image | Yes (`rejetees` quality) | — |
| HOLD/EXCLUDE: duplicate / already present | Yes in policy | No live detector |
| HOLD/EXCLUDE: identity not de-identifiable / burned-in PHI | Yes in Phase 11B | No pixel review tool |
| HOLD/EXCLUDE: insufficient data / physician confirm | Yes (`PENDING_PHYSICIAN`) | **YES** |

No new case was selected or classified in this phase.

---

## 11. Sampling

Phase 11A/11B require **ordinary/control and hard** cases. Current unused pool (R26) is **entirely hard/uncertain** and has **zero new easy controls**.

| Desired mix | On-disk unused pool |
|-------------|---------------------|
| Ordinary / gold | **0** new |
| ASL difficult | 6/6 R26 tagged `ASL_hard` |
| Overlap | 6/6 |
| Rotation | 5/6 |
| Shaft / FOV | 4/6 `SHAFT_hard` |
| Quality variation | 2/6 |
| Morphological / deformity | R26_06 notes pathology; not a balanced stratum |

**Do not select new cases now.** Future collection must not be failure-only. Balance is **not claimable** before data exist.

---

## 12. Physician-gated decisions (still open)

Do not resolve by assumption.

| ID | Question | Status |
|----|----------|--------|
| **P-A1** | ASL sourcil vs rim illustrated exemplars | **OPEN** — verbal definition locked; exemplars absent |
| **P-A7** | FSP accepted-level exemplars | **OPEN** — verbal definition locked |
| **P-FOV** | FSD numeric cutoff vs directional-only | **OPEN** — directional lock only; 0.5× head diameter not implemented |
| **P-TOL** | Inter-annotator disagreement tolerance | **OPEN** — do not auto-average |
| **P-V1** | Whether `v=1` is allowed | **OPEN** — default forbidden |
| **P-C10** | Acceptable clinical landmark/angle error | **OPEN** |

---

## 13. Readiness matrix

| Gate | Status | Factual justification |
|------|--------|------------------------|
| **COLLECTION_ENVIRONMENT_READY** | **NOT_READY** | No dedicated inbox; no raw/de-id/validated staging; existing `bassin/` pools are used seed / R26 hold / rejects / empty identifying folders. |
| **DEIDENTIFICATION_READY** | **NOT_READY** | Checklist on paper only. No strip/verify/pixel-PHI/export pipeline. 0 cases `DEID_CONFIRMED`. Source DICOMs still have identifying tags. |
| **PROVENANCE_READY** | **PARTIAL** | B26 path mapping + v1 copy hashes + Step D one-shot inventory exist. Future fields (`patient_pseudonym`, de-id status, reviewer, annotation version, restricted linkage) are missing. |
| **DUPLICATE_CONTROL_READY** | **PARTIAL** | Step D PatientID + `dicom_sha256` worked on the current pool. No intake comparator, no study/series index, no final-image hash index. |
| **PATIENT_LEAKAGE_CONTROL_READY** | **PARTIAL** | Policy “one patient = one split” is written. No patient key in training splits; no frozen test; no pseudonym; siblings known only via identifying Step D files. |
| **PHYSICIAN_REVIEW_READY** | **NOT_READY** | `annotator_B` empty. No two-reader workflow instantiated. P-A1/P-A7/P-FOV/P-TOL/P-V1/P-C10 open. B26 not double-read. |
| **ANNOTATION_READY** | **PARTIAL** | Tooling exists for B26 (`manual_annotation_tool`, frozen JSON schema). R26 stubs empty. Future statuses / adjudication / `v=0` discipline documented but not operational for new intake. ASL/FSP exemplars missing. |
| **FROZEN_TEST_READY** | **NOT_READY** | Test set empty. Need ≥15 independent patients. None reserved. Creating a split now is forbidden. |

**COLLECTION_ENVIRONMENT_READY = NOT_READY** is the blocking headline for Phase 11C-0.

---

## 14. Blockers

1. **No dedicated collection environment** — nowhere approved to deposit new DICOMs without mixing with B26 or R26.  
2. **No de-identification implementation** — cannot legally/technically graduate a new case to training metadata.  
3. **Identifying metadata already lives next to dataset inventories** — PatientName/PatientID in Step D / R26 worklist; named folders.  
4. **No patient_pseudonym / restricted linkage** — cannot detect future duplicates without keeping real IDs in working files.  
5. **Confirmed N = 26**; **remaining_to_minimum = 34**; pending 6 must not be counted.  
6. **No frozen independent test** (need ≥15).  
7. **R26 still PENDING_PHYSICIAN** — promotion NO-GO.  
8. **Physician decisions P-A1, P-A7, P-FOV, P-TOL, P-V1, P-C10 open** — annotation of a new corpus would lack locked exemplars/tolerances.  
9. **Unused pool is hard-only** — even if R26 were later cleared, the mix would lack ordinary controls.  
10. **No operational duplicate/leakage gate** for a file that arrives after Step D.

None of these blockers is solved by creating folders in this phase. Phase 11C-0 **does not** create them.

---

## 15. Explicit NO-GO confirmations

| Item | Status |
|------|--------|
| **TRAINING** | **NO-GO** |
| **R26_PROMOTION** | **NO-GO** |
| **DATASET_MODIFICATION** | **NO-GO** |
| New splits | **NO-GO** |
| Automatic import of new data | **NO-GO** (none performed) |
| Flutter corrections as GT | **NO-GO** (Phase 10H / 11A / 11B) |
| Phase 10F/10G candidates as GT | **NO-GO** |
| V5 predictions as GT | **NO-GO** |

---

## 16. Confirmation that no other file was created or modified

**Sole artifact of Phase 11C-0:**  
`datasets/yolo_pose_new_26/phase11c0_collection_environment_audit.md`

| Asset | Modified? |
|-------|-----------|
| B26 images / labels / JSON / `data.yaml` / splits | **NO** |
| R26 JSON stubs / worklist | **NO** |
| V5 weights | **NO** |
| Flutter / FastAPI / `mvp_geometry` / PDF | **NO** |
| Any DICOM | **NO** |
| Any new folder (`incoming`, `v2`, `restricted`, …) | **NO** |
| Any new case ID | **NO** |
| Training run | **NO** |

**Phase 11C-1 was not started.**

---

*End of Phase 11C-0. STOP.*
