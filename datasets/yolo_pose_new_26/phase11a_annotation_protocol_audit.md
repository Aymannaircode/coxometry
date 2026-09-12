# Phase 11A — Clinical Annotation & Data Expansion Protocol
## Read-Only Audit + Future Protocol (STOP AFTER THIS DOCUMENT)

**Date:** 2026-09-04  
**Mode:** PROTOCOL + READ-ONLY AUDIT ONLY  
**Production model (unchanged):** V5 Phase 2  
**Current workflow (unchanged):** DICOM/PNG → V5 Phase 2 → refined landmarks → optional manual correction → `/measurements` → `mvp_geometry` → VCE/Tönnis/CCD → PDF  

**This phase does not:**
- train or fine-tune any model
- modify V5 / weights / labels / original 26-image dataset
- modify `mvp_geometry`, `/analyze`, `/measurements`, Flutter, or PDF
- add heuristics, confidence gates, or promote experimental detectors
- copy images, create training splits, or create `datasets/yolo_pose_remediation_v2/`

**Final verdict:** `PHASE_11A_PROTOCOL_COMPLETE` — `TRAINING_NO_GO` — `EXPANSION_BLOCKED_INSUFFICIENT_INDEPENDENT_CASES`

---

## 1. Current dataset inventory

### 1.1 Original dataset root (FROZEN)

| Item | Path / value |
|------|----------------|
| **Original dataset root** | `datasets/yolo_pose_new_26/` |
| **Training images** | `images/train/` — **21** PNG (`B26_01`–`09`, `11`, `12`, `14`–`16`, `18`, `19`, `21`–`25`) |
| **Validation images** | `images/val/` — **5** PNG (`B26_10`, `B26_13`, `B26_17`, `B26_20`, `B26_26`) |
| **Test images** | **None** — `images/test/` does **not** exist |
| **Training labels** | `labels/train/` — **21** YOLO Pose `.txt` (16 KP) |
| **Validation labels** | `labels/val/` — **5** YOLO Pose `.txt` |
| **Test labels** | **None** — `labels/test/` does **not** exist |
| **Config** | `data.yaml` — `kpt_shape: [16, 3]`; class `pelvis`; flip_idx R↔L pairs |
| **Split manifest** | `meta/split.json` — seed **42**; train 21 / val 5 / test **0** |
| **Source mapping** | `meta/source_mapping.csv` — B26 ↔ PNG ↔ YOLO label ↔ JSON ↔ DICOM |
| **Keypoint order** | `meta/keypoint_order.md` — KP0–13 legacy + KP14 `IT_R` + KP15 `IT_L` |
| **Human JSON (source of existing GT)** | `annotation_pilot/annotations/new_26/` — 26 files `B26_01.json`…`B26_26.json` |
| **DICOM sources (used)** | `bassin/a_annoter/` — **26** files (already = B26) |

**Original 26-image dataset must remain untouched.** Future annotations must live in a **new** namespace. Phase 11A did not modify images, labels, `data.yaml`, split files, provenance, or annotations under this root (this report file is the only new artifact).

### 1.2 Patient identity on the original 26

Patient identity **is available** for all 26 B26 cases via DICOM `PatientID` (cross-checked in Phase 10C Step D inventory). Each B26 case maps to a **distinct** `PatientID` (26 unique patients).  

`meta/source_mapping.csv` stores case ID, split, image/label/JSON/DICOM paths, and dimensions — **not** PatientID. PatientID lives in:

- `datasets/yolo_pose_remediation_v1/meta/candidate_inventory.csv`
- `datasets/yolo_pose_remediation_v1/meta/_stepD_state.json` (`b26_patient_ids`, 26 values)
- source DICOM headers

If a future case lacks PatientID: mark **`UNRESOLVED_PATIENT_ID`** and **do not guess**. Do not invent a patient from filename, folder name, or visual similarity.

**De-identification note (inventory, not a change):** existing Step D CSVs also store `PatientName`. That is a **future ingestion risk**. Phase 11A does not strip or rewrite those files. Future `yolo_pose_remediation_v2` metadata must use irreversible pseudonymous IDs only (§14).

### 1.3 Remediation namespace (v1 — existing, incomplete)

| Item | Path / value |
|------|----------------|
| **Remediation namespace** | `datasets/yolo_pose_remediation_v1/` |
| **Role** | Phase 10C derived **seed copy** of original 26; original remains recoverable |
| **Images** | train 21 / val 5 / test **0** (empty dir present) |
| **Labels** | train 21 / val 5 / test **0** — byte-identical to original (SHA256 26/26) |
| **Provenance** | `meta/provenance.md`, `meta/copy_manifest.json` |
| **Split** | `meta/split.json` — `final_evaluation_ready: false`; `expansion_status: BLOCKED_INSUFFICIENT_REAL_DICOM_POOL` |
| **Continuity probe** | B26_10, B26_13, B26_17, B26_20, B26_26 (original val; **not** an independent test set) |
| **Triage renders** | `triage_renders/a_verifier/` (8) + `triage_renders/rejetees/` (2) — triage only, **not** YOLO-promoted |
| **Training on this namespace** | **None** |

### 1.4 Annotation-pilot namespace

| Path | Content | Status |
|------|---------|--------|
| `annotation_pilot/annotations/new_26/` | Official B26 JSON (14 MVP landmarks) | **FROZEN** — 26/26 valid; all 364 landmarks `v=2` |
| `annotation_pilot/annotations/remediation_v1/` | R26_01…06 stubs + worklist | **NOT_ANNOTATED**; empty `landmarks` |
| `annotation_pilot/annotations/annotator_A/` | Pediatric Dataset-1 protocol templates (P01–P16) | **Not** adult B26 GT; not for V5 training |
| `annotation_pilot/annotations/annotator_B/` | Directory exists | **0 files** — no second reader on adult set |

### 1.5 Proposed future namespace

`datasets/yolo_pose_remediation_v2/` — **does not exist**. Phase 11A **did not create it** (no images, no labels, no empty tree). See §5.

### 1.6 Other on-disk pools (read-only)

| Pool | Location | Usable DICOMs | Role |
|------|----------|--------------:|------|
| Used seed | `bassin/a_annoter/` | 26 | Already B26 |
| Verification hold | `bassin/a_verifier/` | 8 | Only unused expansion pool (6 unique patients after de-dup) |
| Rejected | `bassin/rejetees/` | 2 | Excluded unless re-qualified |
| Named patient folders | `bassin/<NAME>_…/` | **0 files** (33 empty placeholder dirs) | Names only; DICOMs consolidated elsewhere |
| `yolo_pose_remediation_v2` | — | — | **Absent** |

**Maximum unique new patients currently on disk:** **6**. Even if all were physician-cleared and annotated: **26 + 6 = 32** independent patients — below the Phase 11A minimum of 60.

### 1.7 Manually corrected data (existing)

| Source | What it is | Usable as future training GT? |
|--------|------------|-------------------------------|
| Phase 10H validation moves | Programmatic test deltas on live `/measurements` (B26_13 ASL_L, B26_10 ASL_L, B26_26 FSP_L) | **NO** — integration test only; not persisted as annotations |
| Flutter correction UI | Validated client bridge (Phase 10H PASS_WITH_MINOR_ISSUES) | **NO** — correction must never auto-become training data (§14 of this protocol) |
| `b6_working_annotations/` | IT_R / IT_L working JSON; `NON-OFFICIAL` | **NO** for ASL/FSP/FSD; IT policy unchanged this phase |
| B6 correction queues / reviews | IT-focused planning and QA | **NO** for the six priority landmarks |

**No physician-reviewed ASL/FSP/FSD correction set exists.**

---

## 2. Current annotation status

| Question | Finding |
|----------|---------|
| Who annotated B26? | Single primary annotator: `annotator_id = "annotator_A"` |
| Double-reading on B26? | **None** (no annotator_B adult files; no inter-annotator distances) |
| Physician review of B26 GT? | Geometric QA only (Phase 10C Step B / prior annotation QA). **Not** independent physician double-read |
| Visibility on ASL/FSP/FSD | **All `v=2`** on all 26 cases (364/364 MVP landmarks `v=2`) |
| `v=1` used? | **No** on new_26. Project already defines `v=1` as “estimated” and **forbids it by default** |
| YOLO ↔ JSON parity | 0 blocking mismatches (≤1 px); 16-KP labels include IT slots |
| Hard coordinate / side FAIL | **0** (Step B) |
| FSD FOV policy review | **20/26** cases flagged `FOV_SHORT` vs provisional 0.5× head-diameter — labels **not** rewritten |
| Official validation | `annotation_pilot/annotations/new_26/validation_summary.md` — 26/26 valid (2026-08-23) |
| R26 expansion annotations | Stubs only; `status: NOT_ANNOTATED` |
| Training-ready expansion? | **NO** |

### 2.1 Existing annotation record fields (schema `mvp-pilot-1.0`)

Present today (B26 JSON):

- case: `image_id`, `source_file`, `source_dataset`, `view`, `population_note`, `guidelines_version`, `image_width`, `image_height`
- annotator: `annotator_id`, `annotation_date` (often `null` on B26)
- landmark: `id`, `name`, `side`, `x`, `y`, `v`, `notes`
- image-level: `pelvic_rotation_suspected`, `fov_diaphysis_insufficient_R/L`, `overall_annotation_feasible` (often `null`)
- `ambiguity_flags` (A1–A8 codes; typically empty on B26)

**Missing for future clinical records:** reviewer ID, review timestamp, review status, adjudication ID, reason code, annotation version, image hash, patient pseudonym, visibility/validity separate from invented coordinates.

R26 stubs already add: `status`, `fov_policy_review_required`, `hard_tags`, `do_not_invent_coordinates`, `do_not_apply_0_5_head_diameter_cutoff`.

---

## 3. Existing remediation candidates

### 3.1 Phase 10C Step D selected queue (not YOLO-promoted)

| case_id | PatientID | Hard tags | FOV review | Annotation | Eligible |
|---------|-----------|-----------|------------|------------|----------|
| R26_01 | 54321 | OVERLAP; ROT_mild; SHAFT_hard; ASL_hard; QUALITY_var | YES | empty stub | PENDING_PHYSICIAN |
| R26_02 | 202607200845491 | OVERLAP; SHAFT_hard; ASL_hard | YES | empty stub | PENDING_PHYSICIAN |
| R26_03 | 202607231822531 | OVERLAP; ROT_mild; SHAFT_hard; ASL_hard | YES | empty stub | PENDING_PHYSICIAN |
| R26_04 | 202608051209231 | OVERLAP; ROT_mild; ASL_hard | YES | empty stub | PENDING_PHYSICIAN |
| R26_05 | 202608111125311 | ASL_hard; ROT_mild; OVERLAP | MAYBE | empty stub | PENDING_PHYSICIAN |
| R26_06 | 202608162107121 | ASL_hard; SHAFT_hard; OVERLAP; ROT_mild; QUALITY_var | YES | empty stub | PENDING_PHYSICIAN |

**Patient-level checks already verified in Step D:** 6/6 unique patients; no PatientID overlap with B26 seed; sibling views held out.

**Why not promoted:** adult/eligibility still `incertain`; annotations not started; promoting would inflate the dataset with non-QA’d labels.

### 3.2 Held / excluded

| Item | Reason |
|------|--------|
| DARI sibling view | Same PatientID as R26_01 |
| HADDOURI sibling view | Same PatientID as R26_04 |
| `rejetees` seam case | Quality reject |
| ZAFFOU unilateral hip | Not bilateral AP pelvis; same PatientID as B26_25 |
| 33 empty named folders | Zero DICOMs |
| Phone / synthetic | Forbidden; none added |

### 3.3 Hard-tag distribution on R26_01…06

| Tag | Count (of 6) |
|-----|-------------:|
| ASL_hard | 6 |
| OVERLAP | 6 |
| ROT_mild | 5 |
| SHAFT_hard | 4 |
| QUALITY_var | 2 |
| SIZE_var | 0 |

The unused pool is **entirely hard / uncertain**. No easy/gold new controls exist on disk.

### 3.4 Phase 10D–10G research candidates (not annotation cases)

These are **algorithm research** artifacts, not a clinical collection list:

- Phase 10D: ROI fallback design only; `REFINEMENT_NOT_SAFE_WITH_CURRENT_DATA`
- Phase 10E-0: non-learned ASL signal **YES**, shaft **NO**; `SAFE_TO_PROCEED: NO`
- Phase 10F-0: sourcil structure **PARTIAL**; ASL_L research signal **YES**; ASL_R **NO**; `SAFE_TO_IMPLEMENT: NO`
- Phase 10G-0: ASL_L localization **PARTIAL**; confidence gate **UNCERTAIN**; endpoint stability **NONE**; method agreement **NONE**; `SAFE_TO_IMPLEMENT: NO`

**Do not promote any of these detectors. Do not use their outputs as ground truth.**

---

## 4. Unresolved cases

| ID | Topic | Status |
|----|-------|--------|
| **U-N** | Independent patient count 26 (32 if R26 cleared) vs minimum 60–100 | **BLOCKING** |
| **U-TEST** | Frozen independent test set ≥15 patients | **ABSENT** |
| **U-R26** | R26 adult/eligibility + annotation | PENDING_PHYSICIAN; landmarks empty |
| **U-FOV-NUM** | Numeric FSD short-FOV cutoff (provisional 0.5× head diameter) | **PHYSICIAN_CONFIRMATION_REQUIRED** |
| **U-FOV-20** | 20 B26 cases `FOV_SHORT` still `v=2` | Policy review only; **do not rewrite original labels** |
| **U-FOV-PRIO** | Shortest provisional ratios: B26_09, B26_19, then B26_16 | Physician review list; not applied |
| **U-A1** | Sourcil vs rim exemplars for annotator training | **PHYSICIAN_CONFIRMATION_REQUIRED** (P-A1) |
| **U-A7-FSP** | Illustrated accepted FSP levels | **PHYSICIAN_CONFIRMATION_REQUIRED** (P-A7-FSP) |
| **U-V1** | Whether `v=1` is ever allowed for ASL/FSP/FSD | Default **forbidden**; P-V1 open |
| **U-TOL** | Inter-annotator / review disagreement tolerance | **UNRESOLVED — PHYSICIAN INPUT REQUIRED** |
| **U-C10** | Acceptable landmark/angle error for clinical use | Unresolved in Phase 10 doctor-requirements gap (C10) |
| **U-DR** | Independent double-reading of validation/test | **Not started** |
| **U-DEID** | Future metadata must not carry PatientName / hospital IDs / DOB | Requirement only; not implemented |
| **U-10H-OBS** | B26_19 V5 `FSD_L.y` slightly outside canvas (pre-existing) | Observe only; not a label rewrite |
| **U-ASL-DEF** | Written ASL definition locked; unique 2D localization **HIGHLY_AMBIGUOUS** (Phase 10E) | Annotation must allow `v=0`; no guessed point |

**Unresolved short-FOV cases must be marked `v=0` in future annotations** when the shaft is not identifiable / axis is unstable — **not** extrapolated. Until the numeric cutoff is physician-locked, annotators follow the directional rule and flag `FOV_SHORT` / `FOV_POLICY_REVIEW_REQUIRED` rather than inventing a coordinate.

---

## 5. Proposed future namespace

**Name:** `datasets/yolo_pose_remediation_v2/`  
**Status:** **PROPOSED ONLY** — directory **not created** in Phase 11A.

Preferred future structure (create in a later approved phase, **without** copying images or building splits until collection + de-identification + physician review allow it):

```
datasets/yolo_pose_remediation_v2/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
├── annotations/
│   ├── raw/            # annotator A placements (immutable after submit)
│   ├── reviewed/       # annotator B / physician review
│   └── adjudicated/    # disagreement resolution — training/eval source of truth
├── metadata/
│   ├── patients.csv    # pseudonymous patient_id only
│   ├── cases.csv
│   └── provenance.csv
├── manifests/
└── protocol/
    └── annotation_protocol_v1.md
```

**Hard rules for that future namespace:**

- Never overwrite `datasets/yolo_pose_new_26/`.
- Never treat `yolo_pose_remediation_v1/` seed labels as the expanded clinical GT.
- Do not copy B26 images/labels into v2 until a later phase explicitly versions them as **reference / continuity**, not as silently duplicated training IDs.
- Do not create train/val/test membership until the test set is frozen at patient level.
- `annotation_pilot/annotations/new_26/` remains frozen.

Phase 10C used `yolo_pose_remediation_v1` as a **seed copy** for a 40–80 remediation program. Phase 11A **supersedes the training-size target** to 60–100 / 100+ and requires a **new** namespace so v1 seed copies and empty R26 stubs are not mistaken for a training-ready corpus.

---

## 6. Patient-level split policy

**Unit of split = patient (DICOM PatientID or irreversible pseudonym), never image and never ROI crop.**

| Forbidden | Why |
|-----------|-----|
| Same patient in train **and** val | Leakage |
| Same patient in train **and** test | Leakage |
| Same patient in val **and** test | Leakage |
| Flip / mosaic / crop counted as a new patient | Fake N |
| Guessing PatientID from folder name when DICOM ID is missing | Silent leakage risk |

**Rules:**

1. One patient → exactly one split.  
2. Multiple views of the same patient (if legally/clinically kept) stay in the **same** split; prefer one primary AP pelvis per patient for the count of “independent cases.”  
3. If PatientID is unavailable → `UNRESOLVED_PATIENT_ID`; **do not assign a split**.  
4. Continuity probe (original 5 val IDs) may be **reported separately** for V5 baseline continuity; it is **not** a frozen independent test set.  
5. **Test set must be frozen before any training or threshold tuning.**  
6. Do **not** create the split in Phase 11A.

B26 currently has 26 unique PatientIDs, so a patient-level split is **designable in principle** for existing files. The blocker is **pool size**, not missing IDs on the seed.

---

## 7. Target dataset size

**Do not claim that 26 images are sufficient.** Phase 10D already stated learned specialists on 21 train patients are not safe; docs cite ~100–200 for heatmap-class models. Phase 10C’s 40–80 remediation aspiration is **below** the Phase 11A training gate.

| Target | Value |
|--------|-------|
| **MINIMUM** | **60–100 independent patient cases** |
| **PREFERRED** | **100+ independent patient cases** |
| **Test set** | **≥15 independent patients**, frozen before training |
| Current annotated independent patients | **26** |
| Current unused unique patients on disk | **6** (uncleared) |
| Current theoretical max if R26 all accepted | **32** |
| Gap to minimum 60 | **≥28 new independent patients** (more if some R26 are excluded) |
| Gap to preferred 100+ | **≥68+** |
| Current test patients | **0** |

**Do not create the split now.**

---

## 8. Annotation hierarchy

Future clinical annotations come from **physician-reviewed landmark positions**.

| Rank | Source | Role |
|-----:|--------|------|
| **1** | Physician annotation (or physician-accepted annotator placement) | Primary truth |
| **2** | Adjudicated annotation after disagreement | Overrides 1 when required |
| **3** | Model prediction (V5 Phase 2) | **Initial proposal / reference only** |

**Never:** model prediction → automatically accepted as ground truth.  
**Never:** Flutter / Phase 10H correction → automatically accepted as training data.  
**Never:** Phase 10E–10G experimental candidate → ground truth.

V5 may pre-fill a review UI in a **future** phase. The stored training/eval record is the reviewed/adjudicated annotation, not the proposal.

---

## 9. Landmark definitions

Preserve existing locked definitions. **IT policy is unchanged** and is out of remediation scope for this protocol except as a protected keypoint (do not reorder, do not silently replace TD).

### 9.1 Catalog (16-KP production order — do not reorder)

`TD_R, TD_L, FHC_R, FHC_L, ASL_R, ASL_L, ASM_R, ASM_L, FNM_R, FNM_L, FSP_R, FSP_L, FSD_R, FSD_L, IT_R, IT_L`

Priority landmarks for expansion: **ASL_L, ASL_R, FSP_L, FSP_R, FSD_L, FSD_R**.

### 9.2 ASL (LM-05 / LM-06) — LOCKED

Most **lateral** point of the **sclerotic acetabular sourcil** (weight-bearing roof densification).

**ASL is NOT:**
- generic lateral bony rim
- arbitrary acetabular edge
- `ASM`
- AIIS tip
- osteophyte-like extension / rim spur (that would be optional `ALB`, out of this 14-point guide)

L/R: anatomical right/left (patient right = image left). On AP: `ASL_R.x < ASM_R.x`; `ASL_L.x > ASM_L.x`.  
Measures: VCE (`FHC→ASL`) and Tönnis (`ASM→ASL`).

### 9.3 FSP (LM-11 / LM-12) — LOCKED

Point on the **median proximal femoral shaft axis**, just **below the lesser trochanter**, **or** at the first clear level where medial and lateral diaphyseal cortices are parallel and measurable. Mid-distance between cortices.

**Not FSP:** lesser trochanter tip; neck axis; trochanteric mass; `FSD`.  
Exact pixel height remains **A7**; illustrated exemplars are physician-gated. If the level is not identifiable → `v=0`.

### 9.4 FSD (LM-13 / LM-14) — LOCKED (directional)

Point on the **median shaft axis** at the **most distal still-visible stable level** where both cortices remain identifiable **inside the image**.

**Not FSD:** point outside bone; point extrapolated **below** the FOV; proximal duplicate of `FSP` “to force an axis.”  
`FSD` must be **distal** to `FSP` (larger `y` on standard AP).  
Numeric “too short” cutoff: **not invented in Phase 11A** (see §11).

### 9.5 Visibility (locked)

| `v` | Meaning | Use |
|-----|---------|-----|
| **2** | Clearly identifiable without unreasonable doubt | Structure clearly visible |
| **1** | Estimated | **Do not introduce for this program** unless a physician writes authorization. Project already defines it; default is **forbidden** |
| **0** | Not identifiable / insufficient FOV / ambiguous | Mandatory if the alternative is guessing |

Golden rule: never place a point only to complete the schema.  
JSON: `x`/`y` **null** when `v=0`. YOLO mapping already locked: `v=0` → coordinates `0,0`.

---

## 10. ASL-specific rules

Phase 10E–10G showed ASL is **structurally / projectionally ambiguous**. The written definition is locked; unique-pixel localization is not.

The physician **must** distinguish:

1. radiographic sourcil / weight-bearing sclerotic edge  
2. generic lateral acetabular bony edge  

| Situation | Required action |
|-----------|-----------------|
| Sourcil lateral end clear | `ASL` `v=2` on **sclerotic sourcil** only |
| Sourcil and rim inseparable | **`v=0`** — do **not** place a guessed point |
| Temptation to use ASM as substitute | **Forbidden** |
| Temptation to extrapolate from geometry / V5 / 10F–10G candidate | **Forbidden** |
| `ASL` medial to `ASM` (same side) | Reject; correct or `v=0` |
| Optional bone-edge documentation | Optional `ALB` only if separately commissioned — **not** stored as `ASL` |

**No automatic ASL heuristic** may be introduced. Phase 10G: automatic localization = partial; confidence gate = uncertain; endpoint stability = none; method agreement = none; safe automatic ASL correction = **NO**.

---

## 11. FSD / FOV rules

| Rule | Status |
|------|--------|
| Prefer `v=0` over inventing / extrapolating when axis unstable | **LOCKED** |
| Place `FSD` at most distal **reliable in-FOV** mid-cortical level when shaft is long enough | **LOCKED** |
| Exact numeric cutoff (proposed 0.5× apparent ipsilateral femoral head diameter) | **PHYSICIAN_CONFIRMATION_REQUIRED** |
| How to measure “apparent head diameter” for that cutoff | **PHYSICIAN_CONFIRMATION_REQUIRED** |
| Apply unconfirmed cutoff to rewrite original B26 labels | **FORBIDDEN** |
| Unresolved short-FOV in **future** annotations | **`v=0`** — do not invent a coordinate |
| IT policy | **Unchanged** |

Until the numeric cutoff is physician-confirmed, QA may **flag** `FOV_SHORT` / `FOV_POLICY_REVIEW_REQUIRED` but must not silently convert original `v=2` to `v=0`.

Phase 10H OBS-1 (B26_19 predicted `FSD_L` slightly out of canvas) is a **model** observation, not a license to invent GT below FOV.

---

## 12. Review / adjudication protocol

### 12.1 Two-stage review (future)

**Stage 1 — Annotation:** Annotator A places landmarks (V5 may be shown as proposal only).  
**Stage 2 — Independent review:** Physician / Annotator B reviews without silently inheriting A’s clicks as already-validated truth.

If disagreement exceeds a predefined tolerance → **adjudication required**.

### 12.2 Disagreement tolerance

**UNRESOLVED — PHYSICIAN INPUT REQUIRED**

Do not invent a clinical threshold in Phase 11A.

Existing **provisional engineering** language (not adopted as clinical tolerance):

- `docs/annotation_pilot_protocol.md` §6 Phase 2: alert if Euclidean distance **> 5 mm** at clinical scale **or** **> 0.02 × image width** in pixels — explicitly “à valider par le radiologue référent.”
- Phase 10 doctor-requirements gap **C10**: acceptable landmark/angle error for clinical use — **unlocked**.

Until a physician locks a tolerance, record both annotators’ points, compute pixel and (if PixelSpacing exists) millimetre deltas, and route **all** ASL disagreements plus any FSP/FSD disagreement the reviewer marks as definitional to adjudication. Do **not** auto-average.

### 12.3 Separation of roles

| Layer | Must not also be |
|-------|------------------|
| Annotation (A) | Silent validation truth |
| Review (B) | Same person as A on that case (for val/test; train may document exceptions) |
| Adjudication | Same as the disagreed pair without a third recorded decision |
| V5 proposal | Any of the above |

Future **validation and test** data should have independent double-reading. Do not let one annotation silently become both annotation and validation truth.

### 12.4 Correction-bridge concept (FUTURE — do not implement now)

```
V5 prediction
  → physician correction (existing Phase 10H UI, unmodified in 11A)
  → reviewed annotation
  → adjudication if needed
  → immutable annotation record (new namespace)
```

The correction itself must **never** automatically become training data.

---

## 13. Provenance requirements

Every future case must be traceable to:

| Field | Rule |
|-------|------|
| Unique case ID | New namespace IDs (do not recycle B26 IDs for new patients) |
| Patient ID | Irreversible pseudonym; original hospital PatientID only in a restricted linkage file if legally required — **not** in training metadata |
| Image hash | SHA256 of the de-identified training image |
| Source | Acquisition site / pool tag (e.g. AP pelvis DICOM), not free-text identity |
| Acquisition date | Only if legally/technically available **and** needed; prefer year or omit |
| Annotator | ID, not a person’s full name in public manifests |
| Reviewer | ID |
| Annotation version | Monotonic; raw/reviewed/adjudicated |
| Review status | e.g. `NOT_ANNOTATED` / `ANNOTATED` / `REVIEWED` / `ADJUDICATED` / `REJECTED` |

Do not store unnecessary patient-identifying information.

---

## 14. De-identification requirements

**Define only — do not implement a de-identification system in Phase 11A.**

Before any future dataset ingestion:

- Verify images are de-identified (burned-in PHI, overlays, face, plates).  
- Do **not** ingest patient names, hospital IDs, dates of birth, addresses, or other unnecessary identifying metadata into training metadata.  
- Existing Step D inventories that contain `PatientName` must **not** be copied forward into `yolo_pose_remediation_v2/metadata/`.  
- Prefer irreversible pseudonymous IDs.  
- DICOM tags beyond technical imaging parameters needed for rendering/QC stay out of the training tree.

---

## 15. QC requirements

**Define only — do not implement automatic QC in Phase 11A.**

Future annotation QC should verify:

| Check | Intent |
|-------|--------|
| Coordinates inside image bounds | No OOB `v=2` points |
| Correct left/right side | Patient right = image left; no R/L swap |
| Correct landmark index | 16-KP order unchanged |
| No accidental swapping | ASL↔ASM, FSP↔FSD, L↔R |
| `v=0` has no invented coordinates | JSON `x`/`y` null; YOLO `0,0` with `v=0` |
| ASL not placed on ASM | Distance / laterality |
| ASL not on generic rim when sourcil is visible | Physician/reviewer visual rule |
| FSD short-FOV policy respected | `v=0` rather than extrapolate |
| Patient split respected | No leakage |
| Image/label hash consistency | Provenance |

---

## 16. Future collection strategy

Intentionally include **hard** examples **and** enough ordinary cases so the model is not trained only on failures.

**Priority hard categories (reuse existing triage tags where they already exist):**

- ASL difficult visibility (`ASL_hard`)
- Acetabular overlap (`OVERLAP`)
- Varying pelvic rotation (`ROT_mild` / future `ROTATION`)
- Varying image quality (`QUALITY_var` / `IMAGE_QUALITY` / `LOW_CONTRAST`)
- Short FOV (`SHAFT_hard` / `FOV_SHORT`)
- Different image sizes (`SIZE_var` — currently 0 in the unused pool)
- Different acquisition conditions
- Clinically relevant variation (deformity, osteophyte/rim ambiguity)

**Do not** select only easy images. **Do not** claim statistical balance without data. Track:

- number of cases and patients
- landmark visibility (`v=2` vs `v=0` rates)
- hard-example category counts
- train/val/test counts
- patient distribution

The current unused pool is **imbalanced toward hard/uncertain cases** and **has no easy controls**. That imbalance is **identified, not solved**.

### 16.1 Proposed reason-code vocabulary (small; after audit)

Existing project conventions already use:

- Ambiguity **A1–A8** (definitional)
- Triage **hard_tags:** `ASL_hard`, `OVERLAP`, `ROT_mild`, `SHAFT_hard`, `QUALITY_var`, `SIZE_var`
- QA: `FOV_SHORT`, `FOV_POLICY_REVIEW_REQUIRED`

**Proposed controlled reason codes** for unavailable/ambiguous **landmark** records (do not create dozens of categories):

| Code | Maps from existing | Use |
|------|--------------------|-----|
| `FOV_SHORT` | FOV_SHORT / SHAFT_hard / A7 | Shaft / anatomy cut by FOV |
| `LOW_CONTRAST` | QUALITY_var (subset) | Structure present but not localizable |
| `OVERLAP` | OVERLAP | Superimposed bone / bowel / hardware |
| `ROTATION` | ROT_mild | Positioning makes the point unreliable |
| `DEFORMITY` | R26_06-style pathology notes | Anatomy not identifiable as defined |
| `OSTEOPHYTE_OR_RIM_AMBIGUITY` | A1 | Sourcil vs rim / spur inseparable |
| `IMAGE_QUALITY` | QUALITY_var / IMAGE_QUALITY | Exposure, motion, seam, artifact |
| `OTHER` | — | Free-text `notes` required |

Keep **A1–A8** as definitional ambiguity flags (separate field). Do not collapse them into reason codes.

---

## 17. Training gate

Training **MUST NOT** begin until **all** are satisfied:

- [ ] ≥60–100 independent patient cases
- [ ] ≥15 independent frozen test patients
- [ ] patient-level split verified
- [ ] physician-reviewed annotations
- [ ] ASL definition locked *(verbal definition is locked; exemplars still physician-gated)*
- [ ] FSD short-FOV rule locked *(directional locked; numeric cutoff still open)*
- [ ] annotation QC completed
- [ ] provenance manifest complete
- [ ] no patient leakage
- [ ] test set frozen
- [ ] baseline V5 metrics reproduced
- [ ] training protocol reviewed

**Phase 11A documents this gate only. No box is checked as complete for a new training run.**

Items that are **partially** true today (and must not be misread as gate-pass):

- ASL **verbal** definition locked (Step A) — exemplars and unique-point ambiguity remain open  
- FSD **directional** FOV policy locked — numeric rule open  
- V5 Phase 2 baseline metrics exist (Phase 9B / 10D) — must be **reproduced** before a new train, not merely cited  

### 17.1 Metrics to preserve (no new clinical thresholds)

Future evaluation compares **V5 baseline vs new model** for:

`ASL_L`, `ASL_R`, `FSP_L`, `FSP_R`, `FSD_L`, `FSD_R`

Use **existing project error metrics**:

| Family | Existing project use | Keep |
|--------|----------------------|------|
| Pixel error (letterbox 640) | Phase 9B mean/median/max/p90; % &lt;25/50/75/100 | Yes |
| Pixel error (original image px) | Phase 10D / 10E-0 / 10F-0 / 10G-0 | Yes |
| Normalized geometric error | Existing research normalizations (e.g. FHC–ASM scale, sourcil length) — report as **engineering** metrics already used | Yes, if reproduced from existing definitions |
| Valid landmark rate | `v=2` rate among annotated points | Yes |
| `v=0` rate | Currently 0/364 on B26 MVP points — must be reported after honest `v=0` use | Yes |

**Do not invent new clinical performance thresholds.** C10 remains physician-unlocked. Clinical validation is a **separate future phase**.

**Frozen V5 baseline to reproduce before any new train** (Phase 9B, val n=5, letterbox 640, V5 Phase 2 ≡ V2 for KP0–13):

| Landmark | Mean | Median | Max | &lt;75 px |
|----------|-----:|-------:|----:|----------:|
| ASL_L | 104.9 | 95.6 | 166.8 | 0% |
| FSP_L | 42.6 | 36.5 | 66.5 | 100% |
| FSD_R | 39.0 | 48.5 | 55.0 | 100% |
| FSD_L | 35.4 | 23.3 | 79.4 | 80% |
| ASL_R | 32.8 | 33.2 | 55.0 | 100% |
| FSP_R | 28.8 | 30.6 | 66.7 | 100% |

Original-pixel Phase 10D means (all 26): ASL_L **525.4**; FSP_L 170.0; FSD_R 159.4; FSP_R 150.9; ASL_R 143.8; FSD_L 108.0. ASL_L closer to GT ASM than GT ASL on **25/26**.

---

## 18. NO-GO conditions

Future training is **NO-GO** if any of the following hold:

| Condition | Current state |
|-----------|---------------|
| Fewer than 60 independent cases | **YES — 26 (32 theoretical)** |
| Test set not independent | **YES — test empty; val is continuity probe** |
| Patient leakage | Must be proven absent; cannot be proven on a non-existent expansion split |
| ASL definition ambiguous for annotation | Verbal lock exists; unique 2D point still **HIGHLY_AMBIGUOUS** without exemplars / `v=0` discipline |
| FSD policy unresolved | Directional lock yes; **numeric cutoff unresolved** |
| Annotations not physician-reviewed | **YES** for expansion; B26 is single-annotator |
| Missing provenance | Expansion provenance incomplete (R26 not annotated) |
| `v=0` cases contain invented coordinates | Not observed on B26 (`v=0` unused); **must not occur** in future data |
| Baseline V5 cannot be reproduced | Must be re-run before train; not re-run in 11A |

**Additional NO-GO (from prior phases, still in force):**

- Training on the 26-image seed alone and claiming ASL/FSP/FSD remediation  
- Promoting Phase 10E–10G experimental detectors  
- Introducing an ASL confidence gate  
- Rewriting original labels in place  
- Using phone-négatoscope or synthetic/flip duplicates as new patients  

---

## 19. Exact files inspected

Read-only. No inspected file was modified.

### 19.1 Phase 10C–10H reports

- `datasets/yolo_pose_new_26/phase10c_remediation_execution_plan.md`
- `datasets/yolo_pose_new_26/phase10c_stepA_definition_fov_lock.md`
- `datasets/yolo_pose_new_26/phase10c_stepB_original26_qa.md`
- `datasets/yolo_pose_new_26/phase10c_stepC_dataset_copy_audit.md`
- `datasets/yolo_pose_new_26/phase10c_stepD_source_inventory.md`
- `datasets/yolo_pose_new_26/phase10c_stepD_selection_report.md`
- `datasets/yolo_pose_new_26/phase10c_stepD_annotation_qa.md`
- `datasets/yolo_pose_new_26/phase10d_small_data_refinement_audit.md`
- `datasets/yolo_pose_new_26/phase10d_roi_feasibility.csv` *(listed; not rewritten)*
- `datasets/yolo_pose_new_26/phase10e_coxometry_domain_audit.md`
- `datasets/yolo_pose_new_26/phase10e0_nonlearned_refinement_audit.md`
- `datasets/yolo_pose_new_26/phase10f0_sourcil_structure_audit.md`
- `datasets/yolo_pose_new_26/phase10g0_asl_success_failure_analysis.md`
- `datasets/yolo_pose_new_26/phase10h_validation_report.md`
- `datasets/yolo_pose_new_26/phase10_doctor_requirements_gap_analysis.md`
- `datasets/yolo_pose_new_26/phase9b_full_landmark_accuracy_audit.md`
- `datasets/yolo_pose_new_26/landmark_annotation_quality_audit.md`
- `datasets/yolo_pose_new_26/b6_working_annotations/README.md`
- `datasets/yolo_pose_new_26/b6_manual_correction_queue.md`

### 19.2 Dataset / annotation / identity artifacts

- `datasets/yolo_pose_new_26/data.yaml`
- `datasets/yolo_pose_new_26/meta/split.json`
- `datasets/yolo_pose_new_26/meta/source_mapping.csv`
- `datasets/yolo_pose_new_26/meta/keypoint_order.md`
- Directory listing of `datasets/yolo_pose_new_26/images/{train,val}` and `labels/{train,val}`
- `datasets/yolo_pose_remediation_v1/README.md`
- `datasets/yolo_pose_remediation_v1/meta/provenance.md`
- `datasets/yolo_pose_remediation_v1/meta/split.json`
- `datasets/yolo_pose_remediation_v1/meta/keypoint_order.md`
- `datasets/yolo_pose_remediation_v1/meta/selected_cases.csv` *(header + selection context)*
- `datasets/yolo_pose_remediation_v1/meta/candidate_inventory.csv`
- `datasets/yolo_pose_remediation_v1/meta/_stepD_state.json` (PatientID lists)
- `annotation_pilot/annotations/new_26/B26_01.json`
- `annotation_pilot/annotations/new_26/validation_summary.md`
- `annotation_pilot/annotations/remediation_v1/README.md`
- `annotation_pilot/annotations/remediation_v1/worklist.csv`
- `annotation_pilot/annotations/remediation_v1/R26_01.json`
- `annotation_pilot/annotations/annotator_A/README_annotator_A.md`
- `bassin/` pool listing (`a_annoter` 26, `a_verifier` 8, `rejetees` 2, 33 empty named dirs)

### 19.3 Definition sources

- `docs/landmark_specification.md`
- `docs/annotation_guidelines.md`
- `docs/annotation_pilot_protocol.md`

### 19.4 Confirmed absent

- `datasets/yolo_pose_remediation_v2/` — **does not exist**

---

## 20. Confirmation that no data / code / model was modified

| Asset | Modified in Phase 11A? |
|-------|------------------------|
| `datasets/yolo_pose_new_26/images/` | **NO** |
| `datasets/yolo_pose_new_26/labels/` | **NO** |
| `data.yaml` / `meta/split.json` / `meta/source_mapping.csv` | **NO** |
| `annotation_pilot/annotations/new_26/` | **NO** |
| `datasets/yolo_pose_remediation_v1/` images/labels | **NO** |
| V5 Phase 2 weights / checkpoints | **NO** |
| Flutter production code | **NO** |
| `/analyze`, `/measurements`, `mvp_geometry` | **NO** |
| PDF | **NO** |
| Heuristics / confidence gates / experimental detectors | **NO** |
| Training run | **NO** |
| `yolo_pose_remediation_v2` created | **NO** |
| Images copied / labels written / splits created | **NO** |

**Sole artifact created:** this file  
`datasets/yolo_pose_new_26/phase11a_annotation_protocol_audit.md`

---

## 21. Phase 10H–10G implications for collection (audit extract)

| Finding | Implication for Phase 11A |
|---------|---------------------------|
| Manual correction bridge validated (10H) | Keep as **future** collection UI; do not modify now; corrections ≠ training data |
| ASL_L automatic localization only partial (10G) | Collect physician ASL with sourcil-vs-rim rule; no heuristic |
| Confidence gate uncertain (10G) | Do not add gates |
| Endpoint stability none; method agreement none (10G) | Do not use multi-method auto-consensus as GT |
| Sourcil detectability partial (10F) | Hard ASL cases are scientifically justified in the collection mix |
| Domain: ASL = sourcil ≠ rim (10E) | Preserve definition exactly; allow `v=0` |
| Small-data refinement unsafe (10D) | 26 cases cannot be cropped into a larger dataset |
| Step D expansion blocked | Need new real AP pelvis DICOMs, not on-disk leftovers |

---

## 22. Proposed next step (do not start automatically)

**Do not start Phase 11B in this session.**

Suggested **Phase 11B** (when explicitly approved): a **collection & de-identification protocol** only —

1. Obtain additional **real adult AP pelvis DICOM** cases (unused patients), same acquisition domain, enough to reach ≥60–100 independent patients after exclusions.  
2. Physician clearance of R26_01…06 (adult/eligibility) — still **not** YOLO promotion.  
3. De-identification checklist and pseudonym scheme (implement only after approval).  
4. Physician lock of FSD numeric FOV cutoff **or** an explicit written decision to keep directional `v=0` without a number.  
5. Physician lock of disagreement tolerance (replace UNRESOLVED).  
6. Illustrated ASL sourcil-vs-rim exemplars (P-A1).  

Still forbidden in 11B unless a later phase says otherwise: training, V5 modification, original-26 edits, automatic ASL, split fabrication.

---

*End of Phase 11A. STOP.*
