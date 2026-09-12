# Phase 10C — Step D1 Source Inventory

**Date:** 2026-09-04  
**Mode:** Inventory + triage only — no training, no YOLO promotion of new cases, no production edits  
**Machine CSV:** `datasets/yolo_pose_remediation_v1/meta/candidate_inventory.csv`

---

## Pool summary

| Pool | Location | DICOM files | Role |
|------|----------|------------:|------|
| Named patient dirs | `bassin/<PATIENT_*>/` | **0** (33 empty dirs) | Placeholder dirs only; no usable files |
| Used seed | `bassin/a_annoter/` | **26** | Already = B26_01…26 |
| Verification hold | `bassin/a_verifier/` | **8** | Only unused expansion pool |
| Rejected | `bassin/rejetees/` | **2** | Excluded unless re-qualified |
| Other repo DICOMs | — | **0** found outside `bassin/` pools above | — |

**CSV inventory rows:** 69 (= 33 empty dirs + 26 + 8 + 2)

---

## Critical finding

**The repository does not currently contain enough unused real AP pelvis DICOMs to expand remediation_v1 to 40–80 cases or to build ≥15 held-out test cases.**

Maximum unique new patients from `a_verifier` after de-duplication: **6**.  
Even if all were physician-cleared and annotated: **26 + 6 = 32** total — below the 40 minimum target.

---

## Patient identity

| Question | Answer |
|----------|--------|
| Can patient identity be established? | **YES** for all on-disk DICOMs via `PatientID` (+ `PatientName`) |
| Empty PATIENT_* folder names | Match known patients whose DICOMs were consolidated into `a_annoter` / `a_verifier` / `rejetees` |
| Multi-image same patient | DARI FATIMA (2), HADDOURI MANAL (2), ZAFFOU ABOUCH (B26_25 + rejected unilateral) |

Patient-level split is **possible in principle** for existing files. It is **not** the blocker — **pool size** is.

---

## a_annoter (already B26)

All 26 files are AP pelvis (or bilateral hip-as-pelvis), adult, previously selected `utilisable_annotation=oui`.  
**Eligible for NEW expansion:** NO (already used).  
Mapped 1:1 in `datasets/yolo_pose_new_26/meta/source_mapping.csv`.

---

## a_verifier (8 candidates)

| DICOM (suffix) | Patient | Age | Verification | Eligible |
|----------------|---------|-----|--------------|----------|
| …1448193835…0003 | DARI FATIMA | (absent) | incertain | PENDING_PHYSICIAN |
| …1451251017…0003 | DARI FATIMA | (absent) | incertain | PENDING_PHYSICIAN (sibling) |
| …202607200851078206 | MOUNTASER AICHA | 016Y | incertain | PENDING_PHYSICIAN |
| …202607231823530408 | ACHLAFY ABIR | 016Y | incertain | PENDING_PHYSICIAN |
| …202608051210254689 | HADDOURI MANAL | 017Y | incertain | PENDING_PHYSICIAN (sibling) |
| …202608051215434223 | HADDOURI MANAL | 017Y | incertain | PENDING_PHYSICIAN |
| …202608111126260582 | GOURID ABDELAADIM | 016Y | incertain | PENDING_PHYSICIAN |
| …202608162110024587 | KABBAJ GHITA | 094Y | incertain (pathology) | PENDING_PHYSICIAN |

**Eligible YES (strict adult + utilisable=oui, unused):** **0**

---

## rejetees (2)

| DICOM | Patient | Reason | Eligible |
|-------|---------|--------|----------|
| …202608031038074414 | bennani asmae | Seam artifact + truncated proximal femurs | NO |
| …202608161539116335 | ZAFFOU ABOUCH | Unilateral hip; incomplete bilateral pelvis; same PatientID as B26_25 | NO |

Not re-qualified → excluded.

---

## Domain filters applied

| Filter | Result |
|--------|--------|
| Synthetic / GAN | None present |
| Flip-as-new / mosaic GT | Not used |
| Phone-négatoscope | None in pools; not added |
| B26 reuse | Prevented via filename ↔ source_mapping |

---

## Triage renders (D2)

Rendered with project `annotation_pilot/manual_annotation_tool/dicom_render.py` (DICOM originals untouched):

- `datasets/yolo_pose_remediation_v1/triage_renders/a_verifier/` (8 PNG)
- `datasets/yolo_pose_remediation_v1/triage_renders/rejetees/` (2 PNG)
- Manifest: `meta/triage_render_manifest.json`

These renders are **for triage only** — not promoted into `images/{train,val,test}`.

---

## Implication for Step D gates

| Gate | Status |
|------|--------|
| Inventory complete | YES |
| Enough cases for 40–80 | **NO** |
| Enough for ≥15 test | **NO** |
| Patient-level split designable later | YES (IDs available) |
| Final split redesign now | **DEFERRED / BLOCKED** |

---

*End of Step D1 inventory report.*
