# Phase 10C — Step C Dataset Copy Audit

**Generated UTC:** 2026-09-04T18:20:10Z  
**Mode:** READ-ONLY verification after byte-identical copy  
**Source:** `datasets/yolo_pose_new_26/`  
**Target:** `datasets/yolo_pose_remediation_v1/`  
**Copy UTC (from provenance):** 2026-09-04T18:19:12Z

---

## Counts

| Metric | Value |
|--------|------:|
| Source images | 26 |
| Source labels | 26 |
| Target images | 26 |
| Target labels | 26 |
| Target train images | 21 |
| Target val images | 5 |
| Target test images | 0 |
| Identical image SHA256 (src↔dst) | **26/26** |
| Identical label SHA256 (src↔dst) | **26/26** |
| Labels with 16-KP shape (src+dst) | **26/26** |
| Visibility vectors unchanged | **26/26** |
| FOV_SHORT cases label-hash unchanged | **20/20** |

---

## Split summary

| Split | Seed assignment | Notes |
|-------|----------------:|-------|
| train | 21 | Same IDs as source train (no reshuffle) |
| val | 5 | = continuity probe (original source val IDs) |
| test | 0 | **EMPTY** — dirs exist; no fabricated cases |

**Continuity probe IDs:** B26_10, B26_13, B26_17, B26_20, B26_26

**Final-evaluation readiness:** `final_evaluation_ready = False`  
Seed is **INCOMPLETE** for T1 gates (≥15 test images required by Phase 10C plan). Step D must expand before claiming remediation success.

---

## SHA256 verification

| Check | Result |
|-------|--------|
| Every copied image SHA256 == source image | PASS |
| Every copied label SHA256 == source label | PASS |
| Destination hashes == precopy source snapshot | PASS |

Machine-readable: `datasets/yolo_pose_remediation_v1/meta/copy_manifest.json`

---

## KP16 / order / visibility

| Check | Result |
|-------|--------|
| `kpt_shape [16,3]` in all labels | PASS |
| Order documented KP0–13 legacy, KP14 IT_R, KP15 IT_L | PASS (`meta/keypoint_order.md`) |
| Validated `flip_idx` in `data.yaml` | PASS |
| Visibility values unchanged vs source | PASS |
| FOV_SHORT labels not altered | PASS |

---

## data.yaml

| Check | Result |
|-------|--------|
| Points only to remediation_v1 | PASS (`path: C:/Users/g/OneDrive/Desktop/Projet-Ayman/datasets/yolo_pose_remediation_v1`) |
| Does not point to yolo_pose_new_26 | PASS |
| `kpt_shape: [16, 3]` | PASS |

---

## Source modification check

| Check | Result |
|-------|--------|
| Source images/labels still match precopy SHA256 | PASS — no source modification detected |
| Training artifacts under remediation_v1 | none |

---

## Mismatches

**None.**

---

## Final verdict

| Field | Value |
|-------|-------|
| **STEP_C_STATUS** | PASS |
| **SOURCE_DATASET_UNTOUCHED** | YES |
| **COPIED_CASES** | 26 |
| **IMAGE_HASH_MATCH** | YES |
| **LABEL_HASH_MATCH** | YES |
| **KP16_INTEGRITY** | YES |
| **SPLIT_STATUS** | train=21 / val=5 continuity probe / test=0 EMPTY (seed incomplete for final eval) |
| **CONTINUITY_PROBE_IDS** | B26_10, B26_13, B26_17, B26_20, B26_26 |
| **FOV_SHORT_CASES_UNCHANGED** | YES |
| **TRAINING_STARTED** | NO |
| **SOURCE_MODIFICATION_DETECTED** | NO |
| **SAFE_TO_PROCEED_TO_STEP_D** | YES |

---

*End of Phase 10C Step C audit. STOP — do not proceed to Step D without approval.*
