# Ordre fixe des 16 keypoints YOLO Pose (new_26)

Une seule instance `pelvis` par image, 16 keypoints bilatéraux.

| Index | Nom | Côté | ID source |
|------:|-----|------|-----------|
| 0 | TD_R | right | LM-01 |
| 1 | TD_L | left | LM-02 |
| 2 | FHC_R | right | LM-03 |
| 3 | FHC_L | left | LM-04 |
| 4 | ASL_R | right | LM-05 |
| 5 | ASL_L | left | LM-06 |
| 6 | ASM_R | right | LM-07 |
| 7 | ASM_L | left | LM-08 |
| 8 | FNM_R | right | LM-09 |
| 9 | FNM_L | left | LM-10 |
| 10 | FSP_R | right | LM-11 |
| 11 | FSP_L | left | LM-12 |
| 12 | FSD_R | right | LM-13 |
| 13 | FSD_L | left | LM-14 |
| **14** | **IT_R** | right | LM-17 |
| **15** | **IT_L** | left | LM-18 |

## Mapping visibilité MVP → YOLO

| MVP `v` | YOLO `v` | Coordonnées |
|---------|----------|-------------|
| `null` | `0` | `0, 0` |
| `0` | `0` | `0, 0` |
| `2` | `2` | `x/W`, `y/H` normalisés |

## flip_idx (augmentation miroir horizontal)

`[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14]` — permutation R↔L par paire (indices 14↔15 pour IT).

## Format label (.txt)

Total colonnes : **53** (5 + 16×3).

**Promotion B5 :** 2026-08-29 — source `b6_working_annotations/`, politique `bi_ischial_final_policy.md`.
