# Phase 10C — Step B  
## QA Confirm on Original 26 (Read-Only)

**Date:** 2026-09-04  
**Mode:** READ-ONLY QA — original `annotation_pilot/annotations/new_26/` and `datasets/yolo_pose_new_26/labels/` **not modified**  
**Definition lock:** `datasets/yolo_pose_new_26/phase10c_stepA_definition_fov_lock.md`  
**Evidence:**
- Live geometric checks on all 26 JSON annotations (L/R, ASL↔ASM, FSD distal to FSP, bounds, JSON↔YOLO KP parity with correct 16-KP order)
- Prior human annotation QA: `landmark_annotation_quality_audit.md` / `.csv` (FOV ratios)
- Phase 10B label geometry audit (0 blocking fails)
- Official validation: `annotation_pilot/annotations/new_26/validation_summary.md` (26/26 valid; all 14 KP `v=2`)

**Correction directory decision:**  
`annotation_pilot/annotations/remediation_v1/` was **not** created.  
Reason: no hard coordinate/side FAIL requiring immediate JSON copies; FOV cases need a **physician-confirmed numeric threshold** before rewriting `FSD` visibility to `v=0`. Creating remediation annotation files now would either invent that clinical cutoff or prematurely start the remediation dataset pipeline (Step C). Per approved safety rule → **QA report only**.

---

## Status legend (table)

| Status | Meaning |
|--------|---------|
| **OK** | Consistent with locked definition + geometric self-checks; no invented-point evidence |
| **FOV_SHORT** | Coordinates consistent with “most distal visible in FOV”; shaft length below **provisional** 0.5× head-diameter flag from prior audit → visibility `v=2` vs `v=0` is `REVIEW_REQUIRED` until physician confirms numeric cutoff |
| **FAIL_*** | Blocking geometric contradiction (none found) |
| **REVIEW_REQUIRED** | Ambiguous without guessing (used in notes / visibility column when FOV policy pending) |

**Correction required = YES** only for hard anatomical/side/coordinate failures.  
FOV policy visibility changes are **not** counted as YES until the numeric threshold is physician-confirmed (avoids inventing a clinical rule).

---

## Per-case QA table (26/26)

| case ID | ASL_R | ASL_L | FSP_R | FSP_L | FSD_R | FSD_L | visibility issue | side/geometry issue | correction required | reviewer note |
|---------|-------|-------|-------|-------|-------|-------|------------------|---------------------|---------------------|---------------|
| B26_01 | OK | OK | OK | OK | OK | FOV_SHORT | FSD_L prior ratio 0.47 | none | NO | ASL/ASM/FSP OK; FSD_L last-visible OK; short-FOV `v` pending physician threshold |
| B26_02 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.42; FSD_L 0.44 | none | NO | Bilateral short FOV flags; no R/L or ASL/ASM fail |
| B26_03 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.43; FSD_L 0.48 | none | NO | Same pattern; coords at FOV edge, not extrapolated |
| B26_04 | OK | OK | OK | OK | OK | FOV_SHORT | FSD_L 0.47 | none | NO | FSD_R OK length; FSD_L FOV_SHORT |
| B26_05 | OK | OK | OK | OK | OK | OK | none | none | NO | No FOV flag; locked defs appear applied |
| B26_06 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.47; FSD_L 0.49 | none | NO | Borderline short FOV both sides |
| B26_07 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.42; FSD_L 0.47 | none | NO | No invented distal points detected |
| B26_08 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.44; FSD_L 0.43 | none | NO | Geometry chain FSD distal to FSP OK |
| B26_09 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.38; FSD_L **0.31** | none | NO | **Highest priority FOV review** (shortest ratios); still last-visible placement, not invent |
| B26_10 | OK | OK | OK | OK | OK | OK | none | none | NO | Val set member; shaft length OK vs provisional flag |
| B26_11 | OK | OK | OK | OK | FOV_SHORT | OK | FSD_R 0.48 | none | NO | Unilateral R short FOV |
| B26_12 | OK | OK | OK | OK | OK | OK | none | none | NO | Prior gold reference (0 FOV flag) |
| B26_13 | OK | OK | OK | OK | OK | OK | none | none | NO | Prior gold reference; val set |
| B26_14 | OK | OK | OK | OK | OK | OK | none | none | NO | No FOV flag |
| B26_15 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.41; FSD_L 0.44 | none | NO | Short FOV both sides |
| B26_16 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R **0.37**; FSD_L 0.40 | none | NO | Priority FOV review (short R) |
| B26_17 | OK | OK | OK | OK | OK | OK | none | none | NO | Val set; no FOV flag |
| B26_18 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.48; FSD_L 0.43 | none | NO | Short FOV both sides |
| B26_19 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R **0.34**; FSD_L **0.32** | none | NO | **Highest priority FOV review** with B26_09 |
| B26_20 | OK | OK | OK | OK | FOV_SHORT | OK | FSD_R 0.48 | none | NO | Val set; unilateral R short FOV |
| B26_21 | OK | OK | OK | OK | FOV_SHORT | OK | FSD_R 0.47 | none | NO | Unilateral R short FOV |
| B26_22 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.40; FSD_L 0.43 | none | NO | Short FOV both sides |
| B26_23 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.44; FSD_L 0.49 | none | NO | Borderline L |
| B26_24 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.47; FSD_L 0.49 | none | NO | Borderline both sides |
| B26_25 | OK | OK | OK | OK | OK | FOV_SHORT | FSD_L 0.47 | none | NO | Unilateral L short FOV |
| B26_26 | OK | OK | OK | OK | FOV_SHORT | FOV_SHORT | FSD_R 0.48; FSD_L 0.46 | none | NO | Val set; short FOV both sides |

**ASM_R / ASM_L (spot geometry):** All 26 cases: ASL lateral to ASM both sides; no medial/lateral inversion. (Checked live; not every cell duplicated above.)

---

## Summary counts

| Metric | Count |
|--------|------:|
| Cases with **hard correction required (YES)** | **0** |
| Cases with ASL geometric/definition fail | **0** |
| Cases with FSP geometric/definition fail | **0** |
| Cases with FSD geometric fail (proximal to FSP, OOB, invent below FOV) | **0** |
| Cases with FSD **FOV_SHORT** / policy review | **20** |
| Cases with no FOV flag (B26_05, 10, 12, 13, 14, 17) | **6** |
| R/L inversions | **0** |
| JSON visibility not `v=2` on ASL/FSP/FSD | **0** (all `v=2`) |
| JSON ↔ YOLO label coordinate mismatch (KP0–13) | **0** (≤1 px) |

### Issue tallies (requested)

| Category | Count | Interpretation |
|----------|------:|----------------|
| Cases requiring **correction** (hard YES) | **0** | No coordinate/side rewrite mandatory now |
| Cases with **ASL issues** | **0** geometric | Residual **A1** sourcil-vs-rim risk remains (single annotator; no FAIL evidence). Ambiguous A1 without image double-read → do not guess |
| Cases with **FSP issues** | **0** geometric | Residual **A7** height variability possible; no FAIL |
| Cases with **FSD issues** | **20** FOV_SHORT policy; **0** invent/extrapolate FAIL | Visibility may become correction after physician threshold |

---

## Systematic annotation concerns

1. **AP-pelvis short femoral FOV is corpus-wide (~77% of cases)** — annotators consistently placed `FSD` at the last visible mid-cortical level (`v=2`), matching the “most distal visible” half of the locked definition, while the locked **directional** short-FOV rule prefers `v=0` when the axis is unstable. **Numeric cutoff still physician-gated** → these are policy reviews, not proven inventing.
2. **Single primary annotator (`annotator_A`)** — no inter-annotator agreement; A1/A7 residual ambiguity cannot be closed by geometry alone.
3. **All problem KP currently `v=2` including shortest shafts (B26_09, B26_19)** — after physician confirms threshold, remediation may set selected `FSD` to `v=0` in a **separate** annotation tree (not in-place).
4. **Locked definitions are consistently applied for ASL lateralization, FSP proximal-to-FSD order, and no FOV extrapolation** — consistent with Phase 10B / prior annotation QA: GT is not the primary cause of model ASL_L failure.

---

## Locked definitions — consistency verdict

| Definition (Step A) | Applied consistently on original 26? |
|---------------------|--------------------------------------|
| ASL = lateral sclerotic sourcil | **Yes** geometrically (52/52 ASL lateral to ASM; prior visual OK on reviewed cases) |
| FSP = median proximal shaft under lesser trochanter / first parallel cortices | **Yes** geometrically (52/52; FSP below head/neck chain; no FAIL) |
| FSD = most distal visible stable shaft in FOV | **Yes** for “in FOV / no extrapolate”; **partial** for “stable” until numeric threshold confirmed |
| Prefer `v=0` over inventing when too short | **Directional policy not yet batch-applied** (all FSD still `v=2`) — expected until physician confirms cutoff |

---

## Corrections identified (inventory — not written to disk)

| Type | Action taken | Files written |
|------|--------------|---------------|
| Hard ASL/FSP/FSD coordinate fails | None found | — |
| FOV visibility `FSD` → `v=0` candidates | Listed as FOV_SHORT (20 cases); **not** applied | **No** `annotations/remediation_v1/` |
| Original labels / JSON | Untouched | — |

Priority FOV physician review (shortest ratios): **B26_09**, **B26_19**, then **B26_16**.

---

## STEP_B_STATUS

**COMPLETE** (read-only QA of all 26; no original modification; no remediation annotation directory created).

---

*End of Phase 10C Step B. STOP — do not proceed to Step C without explicit approval.*
