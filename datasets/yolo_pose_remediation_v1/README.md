# yolo_pose_remediation_v1

**What this is:** Versioned **remediation** YOLO Pose dataset namespace for Phase 10C (legacy ASL/FSP/FSD remediation track).

**Derived from:** `datasets/yolo_pose_new_26/` (byte-identical seed copy).

**Original dataset:** `datasets/yolo_pose_new_26/` is **untouched** and remains the recoverable production dataset.

## Current seed status

| Item | Value |
|------|-------|
| Cases | **26 only** (B26_01…B26_26) |
| Train | 21 (same IDs as source train) |
| Val | 5 = **continuity probe** (same IDs as source val) |
| Test | **0** (empty dirs; not a final held-out set) |
| Images/labels | Byte-identical to source (SHA256 verified) |
| Keypoints | 16 KP order preserved (KP0–13 legacy, KP14 IT_R, KP15 IT_L) |
| FOV_SHORT labels | **NOT changed** (pending physician numeric threshold) |
| Training | **None** performed for this namespace |
| Phone-négatoscope images | **None** at this stage |

## Expansion required

This seed is **INCOMPLETE** for final remediation evaluation. The Phase 10C plan requires a held-out **test** set (≥15 images guidance) before T1 training success claims.

**Step D** (not done here) must add **real** hard AP pelvis DICOM-derived cases, then rebuild train/val/**test**. Do not fabricate or flip-duplicate cases.

## Safety

- Do not train against this seed alone and claim ASL_L remediation success.
- Do not point production backend at this dataset until promotion gates pass (later steps).
- Do not edit files in place to “fix” FOV_SHORT without physician-confirmed policy + separate provenance.

## Meta

- `meta/split.json` — assignments + incompleteness declaration
- `meta/source_mapping.csv` — traceability to original B26_* / DICOM / JSON
- `meta/keypoint_order.md` — exact 16-KP order + flip_idx
- `meta/provenance.md` + `meta/copy_manifest.json` — SHA256 copy record
- `meta/qa_checklist.md` — integrity checks

Created UTC: 2026-09-04T18:19:12Z
