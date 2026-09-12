# Phase 10C — Step D Selection Report

**Date:** 2026-09-04  
**CSV:** `datasets/yolo_pose_remediation_v1/meta/selected_cases.csv`  
**Tags:** visual triage of DICOM→PNG renders (project renderer)

---

## Selection outcome

| Category | Count | YOLO-promoted? |
|----------|------:|----------------|
| Seed B26 cases (already in remediation_v1) | 26 | YES (Step C) |
| New unique-patient candidates queued | **6** | **NO** |
| Sibling views held (same patient) | 2 | NO |
| Rejected (not re-qualified) | 2 | NO |
| **Total cases in YOLO images/labels** | **26** | — |
| **Target total 40–80** | — | **NOT MET** |
| **Target test ≥15** | 0 | **NOT MET** |

---

## Selected new candidates (annotation queue only)

| case_id | Patient | Hard tags | Difficulty | FOV review | Eligible for annotation |
|---------|---------|-----------|------------|------------|-------------------------|
| R26_01 | DARI FATIMA | OVERLAP;ROT_mild;SHAFT_hard;ASL_hard;QUALITY_var | moderate_hard | YES | PENDING_PHYSICIAN |
| R26_02 | MOUNTASER AICHA | OVERLAP;SHAFT_hard;ASL_hard | moderate_hard | YES | PENDING_PHYSICIAN |
| R26_03 | ACHLAFY ABIR | OVERLAP;ROT_mild;SHAFT_hard;ASL_hard | moderate_hard | YES | PENDING_PHYSICIAN |
| R26_04 | HADDOURI MANAL | OVERLAP;ROT_mild;ASL_hard | moderate | YES | PENDING_PHYSICIAN |
| R26_05 | GOURID ABDELAADIM | ASL_hard;ROT_mild;OVERLAP | moderate | MAYBE | PENDING_PHYSICIAN |
| R26_06 | KABBAJ GHITA | ASL_hard;SHAFT_hard;OVERLAP;ROT_mild;QUALITY_var | hard | YES | PENDING_PHYSICIAN |

**Why these six:** only unused real AP pelvis DICOMs with ≥2 hard tags (or adult hard pathology for R26_06); one image per PatientID; no B26 reuse; no rejects.

**Why not YOLO-promoted:** adult/eligibility still `incertain` in `verification_radios.csv`; annotations not started; promoting would inflate the dataset with non-QA’d labels.

---

## Hard-tag distribution (R26_01…06)

| Tag | Count (of 6) |
|-----|-------------:|
| ASL_hard | 6 |
| OVERLAP | 6 |
| ROT_mild | 5 |
| SHAFT_hard | 4 |
| QUALITY_var | 2 |
| SIZE_var | 0 |

All six have ≥2 hard tags. No easy/gold new controls exist in the unused pool (pool is entirely verification-hold / uncertain).

---

## Explicit exclusions

| Item | Reason |
|------|--------|
| DARI sibling view | Same PatientID as R26_01 — alternate only |
| HADDOURI view A | Same PatientID as R26_04 — CSV preferred other view |
| rejetees seam case | Quality reject; not re-qualified |
| rejetees unilateral ZAFFOU | Not bilateral AP pelvis; same patient as B26_25 |
| All empty PATIENT_* dirs | Zero files |
| Phone photos / synthetics | Forbidden; none added |

---

## Patient-level leakage

| Check | Result |
|-------|--------|
| PatientID available on all DICOMs | YES |
| Selected new cases unique patients | YES (6/6) |
| No new case shares PatientID with B26 seed | YES (verified) |
| Sibling views kept out of opposing splits | YES (not promoted at all) |
| Final train/val/test redesign | **NOT PERFORMED** — insufficient N |

---

## Split status

`meta/split.json` remains the **seed** assignment:

- train 21 / val 5 continuity probe / test 0  
- Continuity probe IDs preserved: B26_10, B26_13, B26_17, B26_20, B26_26  
- `final_evaluation_ready: false`  
- `expansion_status: BLOCKED_INSUFFICIENT_REAL_DICOM_POOL`

**No silent reshuffle. No fabricated test set.**

---

## What is required to unblock expansion

1. Obtain additional **real AP pelvis DICOM** cases (unused patients), same acquisition domain.  
2. Physician clearance for `a_verifier` adult/eligibility (or replace with confirmed adult cases).  
3. Annotate + QA new cases under `annotation_pilot/annotations/remediation_v1/`.  
4. Only then build patient-safe train/val/**test** with test ≥15 and update YOLO images/labels.

---

*End of Step D selection report.*
