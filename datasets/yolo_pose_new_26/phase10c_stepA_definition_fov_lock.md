# Phase 10C — Step A  
## Definition / FOV Policy Lock

**Date:** 2026-09-04  
**Mode:** DOCUMENT LOCK ONLY — no training, no dataset creation, no production / label / Flutter / PDF / `mvp_geometry` / checkpoint edits  
**Sources (existing only):**
- `docs/landmark_specification.md`
- `docs/annotation_guidelines.md`
- `datasets/yolo_pose_new_26/femoral_offset_spec.md` (shaft / A7 FOV language)
- `datasets/yolo_pose_new_26/phase10c_remediation_execution_plan.md` §4
- Phase 10B definition audit (read-only confirmation)

**Rule for this lock:** Prefer statements already written in project docs. If a clinical numeric rule is still marked provisional in those docs, record it as `PHYSICIAN_CONFIRMATION_REQUIRED` — do not invent a new clinical rule.

---

## 1. Locked ASL definition

| Field | Locked value |
|-------|----------------|
| **IDs** | LM-05 `ASL_R`, LM-06 `ASL_L` |
| **Name** | Acetabular sourcil lateral |
| **Anatomical definition** | Most **lateral** point of the **sclerotic acetabular sourcil** (weight-bearing roof densification) |
| **Not ASL** | Osteophyte / rim spur outside the dense sourcil (that would be optional `ALB`, out of remediation scope unless separately annotated) |
| **Not ASL** | Medial sourcil end (`ASM`), femoral head center (`FHC`), arbitrary roof point |
| **L/R geometry** | Anatomical right/left (patient right = image left). On AP: `ASL_R.x < ASM_R.x`; `ASL_L.x > ASM_L.x` |
| **Measures** | VCE (`FHC→ASL`) and Tönnis (`ASM→ASL`) |
| **Lock status** | **LOCKED** from `landmark_specification.md` LM-05/06 + `annotation_guidelines.md` §2.3 + Phase 10C plan §4.1 |

**Ambiguity A1 (documented residual):** If sourcil and bony rim cannot be distinguished → do **not** guess; use visibility `v=0`. Illustrated sourcil≠rim exemplars for annotator training remain physician-confirmed materials (see §6).

---

## 2. Locked FSP definition

| Field | Locked value |
|-------|----------------|
| **IDs** | LM-11 `FSP_R`, LM-12 `FSP_L` |
| **Name** | Femoral shaft proximal (diaphyseal axis proximal point) |
| **Anatomical definition** | Point on the **median proximal femoral shaft axis**, just **below the lesser trochanter**, **or** at the first clear level where medial and lateral diaphyseal cortices are parallel and measurable |
| **Not FSP** | Lesser trochanter tip itself; neck axis; trochanteric mass; `FSD` |
| **Placement** | Mid-distance between medial and lateral cortices at that level |
| **L/R** | Homolateral to femoral side |
| **Measures** | CCD (with `FSD` → `SHAFT`) |
| **Lock status** | **LOCKED** from `landmark_specification.md` LM-11/12 + `annotation_guidelines.md` §2.6 + Phase 10C plan §4.2 |

**Ambiguity A7 (height):** Exact pixel height “just below lesser trochanter” is not a universal radiographic constant. The **verbal definition above is locked**; illustrated accepted examples for inter-annotator calibration remain `PHYSICIAN_CONFIRMATION_REQUIRED` (see §6). Until exemplars exist, annotators follow the written rule and use `v=0` if the level is not identifiable.

---

## 3. Locked FSD definition

| Field | Locked value |
|-------|----------------|
| **IDs** | LM-13 `FSD_R`, LM-14 `FSD_L` |
| **Name** | Femoral shaft distal (diaphyseal axis distal point **in FOV**) |
| **Anatomical definition** | Point on the **median shaft axis** at the **most distal still visible stable level** where both cortices remain identifiable **inside the image** |
| **Not FSD** | Point outside bone; point extrapolated **below** the FOV / image border; proximal duplicate of `FSP` “to force an axis” |
| **L/R** | Homolateral; `FSD` must be **distal** to `FSP` (larger `y` on standard AP image coordinates) |
| **Measures** | CCD (with `FSP` → `SHAFT`) |
| **Lock status** | **LOCKED** from `landmark_specification.md` LM-13/14 + `annotation_guidelines.md` §2.7 + Phase 10C plan §4.3 |

---

## 4. Visibility rules (locked)

| `v` | Meaning | Locked use |
|-----|---------|------------|
| **2** | Clear, localizable without unreasonable doubt | Structure clearly visible |
| **1** | Estimated | **Not authorized by default** for remediation QA — prefer `v=0` unless a physician has written authorization for that landmark |
| **0** | Absent / unreliable / not identifiable | **Mandatory** if the annotator would otherwise invent or guess |

**Golden rule (locked):** Never place a point only to complete the schema. If not identifiable → `v=0` and do **not** invent coordinates (JSON: `x`/`y` null or ignored; YOLO: `0,0` with `v=0` per project mapping).

**Partial acceptance (locked):** One side may be `v=0` (prosthesis, out of field, invisible). CCD on that side is not calculable if `FSP` or `FSD` is `v=0`.

---

## 5. FSD short-FOV decision (locked directional policy)

### 5.1 Locked decision (directional)

**LOCKED:** If the visible femoral shaft is **too short for a stable diaphyseal axis**, set **`FSD` to `v=0`** rather than inventing or extrapolating a distal point.

This matches:
- `annotation_guidelines.md` §2.7 / A7 (no inventing; FOV insufficient → `v=0` for `FSD`; CCD unavailable)
- Phase 10C plan §4.3 FOV policy intent approved for Step A
- Explicit ban on FOV extrapolation

### 5.2 What “last visible level” still means

When the shaft **is** long enough for a stable axis: place `FSD` at the most distal **reliable** mid-cortical level **still inside the image**. That is **not** extrapolation.

### 5.3 Numeric “too short” threshold — NOT invented here

The project documents propose a **provisional** engineering convention:

> distance `FSP`–`FSD` ≥ **0.5 × apparent ipsilateral femoral head diameter**; else `FSD` → `v=0`

**Status of 0.5× head diameter:** documented as **provisional / project convention**, explicitly requiring radiologist/orthopaedist validation (`annotation_guidelines.md` §2.7; `landmark_specification.md` A7; `femoral_offset_spec.md` D10).

| Item | Status |
|------|--------|
| Prefer `v=0` over inventing/extrapolating when axis unstable | **LOCKED** |
| Exact numeric cutoff (0.5× head diameter vs other) | **PHYSICIAN_CONFIRMATION_REQUIRED** |
| How to measure “apparent head diameter” on each case for the cutoff | **PHYSICIAN_CONFIRMATION_REQUIRED** |

Until the numeric cutoff is physician-confirmed, QA may **flag** short-FOV cases as `FOV_SHORT` / `REVIEW_REQUIRED` but must **not** silently rewrite original labels to `v=0` using an unconfirmed threshold.

---

## 6. PHYSICIAN_CONFIRMATION_REQUIRED

| ID | Topic | Why not locked by AI |
|----|-------|----------------------|
| **P-A1** | Illustrated sourcil vs rim (`ASL` vs optional `ALB`) training set | Docs lock sourcil definition; exemplar cases need clinical teaching selection |
| **P-A7-FSP** | Illustrated accepted `FSP` levels “just below lesser trochanter” | Verbal definition locked; pixel-level calibration needs clinician-agreed examples |
| **P-A7-FSD-THRESH** | Numeric short-FOV cutoff (proposed 0.5× head diameter) and diameter measurement method | Explicitly provisional in project docs |
| **P-V1** | Whether `v=1` is ever allowed for ASL/FSP/FSD in remediation | Guidelines default to forbid `v=1` without clinical authorization |

**Not listed as physician blockers for Step A lock of definitions 1–4 and directional FOV policy §5.1.**

---

## 7. Exact annotation consequences

| Situation | Annotator action | Downstream |
|-----------|------------------|------------|
| Sourcil lateral end clear | `ASL` `v=2` at lateral end of **sclerotic sourcil** | VCE + Tönnis usable |
| Sourcil vs rim inseparable | `ASL` `v=0` | VCE/Tönnis that side unavailable |
| Proximal shaft / lesser-trochanter level clear | `FSP` `v=2` on median axis | CCD possible if `FSD` also visible |
| Proximal shaft not clear | `FSP` `v=0` | CCD unavailable that side |
| Distal shaft clear and axis stable | `FSD` `v=2` at most distal reliable in-FOV level | CCD possible |
| Would require inventing below FOV or guessing | **Forbidden** → `FSD` `v=0` | CCD unavailable that side |
| Shaft visible but **too short for stable axis** (per §5) | `FSD` `v=0` (after physician confirms numeric rule for batch application) | CCD unavailable; do not keep unstable `v=2` solely to fill schema |
| `ASL` medial to `ASM` (same side) | **Reject** placement; correct or `v=0` | Geometry fail |
| `FSD` proximal to `FSP` (same side) | **Reject** placement; correct or `v=0` | Geometry fail |
| R/L label vs patient side wrong | **Reject**; fix side | Geometry fail |

**Remediation program consequence:** New/corrected annotations for training must follow this lock. Original `annotation_pilot/annotations/new_26/` and `datasets/yolo_pose_new_26/labels/` remain **untouched**; any future corrections go only to a separate remediation annotation path after Step C approval.

---

## 8. Step A verdict

| Definition | Status |
|------------|--------|
| ASL | **LOCKED** |
| FSP | **LOCKED** |
| FSD | **LOCKED** |
| Visibility rules | **LOCKED** |
| FSD short-FOV directional policy (`v=0` > invent/extrapolate) | **LOCKED** |
| Numeric short-FOV threshold | **PHYSICIAN_CONFIRMATION_REQUIRED** |

**STEP_A_STATUS:** COMPLETE (definitions + directional FOV policy locked; numeric threshold open)

---

*End of Phase 10C Step A.*
