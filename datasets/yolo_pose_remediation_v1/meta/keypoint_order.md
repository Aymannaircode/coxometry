# Ordre fixe des 16 keypoints YOLO Pose (remediation_v1)

**Source of truth:** copied from `datasets/yolo_pose_new_26/meta/keypoint_order.md`  
**Policy:** Do **not** reorder, rename, or invent keypoints. Exact project order preserved.

Une seule instance `pelvis` par image, 16 keypoints bilatéraux.

| Index | Nom | Côté | ID source | Group |
|------:|-----|------|-----------|-------|
| 0 | TD_R | right | LM-01 | KP0–13 legacy |
| 1 | TD_L | left | LM-02 | KP0–13 legacy |
| 2 | FHC_R | right | LM-03 | KP0–13 legacy |
| 3 | FHC_L | left | LM-04 | KP0–13 legacy |
| 4 | ASL_R | right | LM-05 | KP0–13 legacy |
| 5 | ASL_L | left | LM-06 | KP0–13 legacy |
| 6 | ASM_R | right | LM-07 | KP0–13 legacy |
| 7 | ASM_L | left | LM-08 | KP0–13 legacy |
| 8 | FNM_R | right | LM-09 | KP0–13 legacy |
| 9 | FNM_L | left | LM-10 | KP0–13 legacy |
| 10 | FSP_R | right | LM-11 | KP0–13 legacy |
| 11 | FSP_L | left | LM-12 | KP0–13 legacy |
| 12 | FSD_R | right | LM-13 | KP0–13 legacy |
| 13 | FSD_L | left | LM-14 | KP0–13 legacy |
| **14** | **IT_R** | right | LM-17 | IT |
| **15** | **IT_L** | left | LM-18 | IT |

**Explicit:**
- **KP0–13** = existing legacy landmarks (TD, FHC, ASL, ASM, FNM, FSP, FSD × R/L)
- **KP14** = `IT_R`
- **KP15** = `IT_L`

## Mapping visibilité MVP → YOLO

| MVP `v` | YOLO `v` | Coordonnées |
|---------|----------|-------------|
| `null` | `0` | `0, 0` |
| `0` | `0` | `0, 0` |
| `2` | `2` | `x/W`, `y/H` normalisés |

## flip_idx (validated horizontal flip mapping)

`[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14]`

Permutation R↔L by pair (including indices 14↔15 for IT). **Do not change.**

## Format label (.txt)

Total columns: **53** (5 + 16×3) → `kpt_shape: [16, 3]`.

Seed labels are **byte-identical** copies of `yolo_pose_new_26` labels (including IT KP14–15 as present in source).
