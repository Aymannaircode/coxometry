# Audit mapping keypoints — new_26

**Généré :** 2026-08-23T20:54:32.616973+00:00

## VERDICT : D

**D — Mapping correct ; problème probablement lié à l'apprentissage YOLO** (labels train fidèles au GT, mais V2 prédit comme ASM_L).

## Chaîne auditée

1. **JSON source** : `annotation_pilot/annotations/new_26/`
2. **Labels YOLO train/val** : `datasets/yolo_pose_new_26/labels/`
3. **Métadonnées** : `datasets/yolo_pose_new_26/meta/keypoint_order.md`, `dataset.yaml`
4. **Script conversion** : `annotation_pilot/scripts/prepare_yolo_pose_new_26.py`
5. **Prédictions V2** (contrôle post-apprentissage) : `datasets/yolo_pose_new_26/predictions_v2/labels/`

## Ordre attendu (indices 4–7)

| Index | Nom attendu |
|------:|-------------|
| 4 | ASL_R |
| 5 | ASL_L |
| 6 | ASM_R |
| 7 | ASM_L |

## Cohérence métadonnées / script

- `server.LANDMARKS` : TD_R, TD_L, FHC_R, FHC_L, ASL_R, ASL_L, ASM_R, ASM_L, FNM_R, FNM_L, FSP_R, FSP_L, FSD_R, FSD_L
- `dataset.yaml` kpt_names : identique à `server.LANDMARKS`
- `flip_idx` : `[1, 0, 3, 2, 5, 4, 7, 6, ...]` — permute ASL_R↔ASL_L et ASM_R↔ASM_L en miroir (paires R/L, **pas** ASL↔ASM)
- `prepare_yolo_pose_new_26.py` : zip(`server.LANDMARKS`, `landmarks[]` JSON) + vérif `name`

## Labels d'entraînement vs GT (26 cas)

- Erreur index 5 → GT ASL_L : moyenne **0.00** px, max **0.00** px
- Erreur index 7 → GT ASM_L : moyenne **0.00** px, max **0.00** px
- JSON ordre conforme (`landmarks[i].name == EXPECTED_ORDER[i]`) : **26/26** cas

### Contrôle droit (ASL_R / ASM_R)

- Index 4 → GT ASL_R : moyenne 0.00 px | Index 6 → GT ASM_R : moyenne 0.00 px

## Prédictions V2 vs GT (contrôle apprentissage)

- Erreur V2 index 5 → GT ASL_L : moyenne **525.40** px
- Erreur V2 index 5 → GT ASM_L : moyenne **187.50** px
- V2 index 5 plus proche de GT ASM_L que ASL_L : **25/26** cas

## Tableau détaillé — labels d'entraînement (26 cas)

| case_id | err5→ASL | err5→ASM | err7→ASL | err7→ASM | idx5→ | idx7→ |
|---------|----------|----------|----------|----------|-------|-------|
| B26_01 | 0.00 | 474.64 | 474.64 | 0.00 | ASL_L | ASM_L |
| B26_02 | 0.00 | 459.00 | 459.00 | 0.00 | ASL_L | ASM_L |
| B26_03 | 0.00 | 540.68 | 540.68 | 0.00 | ASL_L | ASM_L |
| B26_04 | 0.00 | 568.70 | 568.70 | 0.00 | ASL_L | ASM_L |
| B26_05 | 0.00 | 482.90 | 482.90 | 0.00 | ASL_L | ASM_L |
| B26_06 | 0.00 | 603.56 | 603.56 | 0.00 | ASL_L | ASM_L |
| B26_07 | 0.00 | 594.16 | 594.16 | 0.00 | ASL_L | ASM_L |
| B26_08 | 0.00 | 483.04 | 483.04 | 0.00 | ASL_L | ASM_L |
| B26_09 | 0.00 | 541.88 | 541.88 | 0.00 | ASL_L | ASM_L |
| B26_10 | 0.00 | 553.30 | 553.30 | 0.00 | ASL_L | ASM_L |
| B26_11 | 0.00 | 531.45 | 531.45 | 0.00 | ASL_L | ASM_L |
| B26_12 | 0.00 | 489.39 | 489.39 | 0.00 | ASL_L | ASM_L |
| B26_13 | 0.00 | 475.63 | 475.63 | 0.00 | ASL_L | ASM_L |
| B26_14 | 0.00 | 626.54 | 626.53 | 0.00 | ASL_L | ASM_L |
| B26_15 | 0.00 | 597.58 | 597.58 | 0.00 | ASL_L | ASM_L |
| B26_16 | 0.00 | 507.37 | 507.36 | 0.00 | ASL_L | ASM_L |
| B26_17 | 0.00 | 557.60 | 557.60 | 0.00 | ASL_L | ASM_L |
| B26_18 | 0.00 | 494.54 | 494.53 | 0.00 | ASL_L | ASM_L |
| B26_19 | 0.00 | 629.24 | 629.24 | 0.00 | ASL_L | ASM_L |
| B26_20 | 0.00 | 487.17 | 487.17 | 0.00 | ASL_L | ASM_L |
| B26_21 | 0.00 | 510.88 | 510.88 | 0.00 | ASL_L | ASM_L |
| B26_22 | 0.00 | 603.56 | 603.56 | 0.00 | ASL_L | ASM_L |
| B26_23 | 0.00 | 508.79 | 508.79 | 0.00 | ASL_L | ASM_L |
| B26_24 | 0.00 | 556.18 | 556.19 | 0.00 | ASL_L | ASM_L |
| B26_25 | 0.00 | 437.26 | 437.26 | 0.00 | ASL_L | ASM_L |
| B26_26 | 0.00 | 332.08 | 332.08 | 0.00 | ASL_L | ASM_L |

## Cas focus + V2

### B26_01

| Source | idx5→ASL | idx5→ASM | idx7→ASL | idx7→ASM | idx5 closer |
|--------|----------|----------|----------|----------|-------------|
| train | 0.00 | 474.64 | 474.64 | 0.00 | ASL_L |
| V2 | 481.35 | 77.97 | 526.86 | 60.58 | ASM_L |

### B26_02

| Source | idx5→ASL | idx5→ASM | idx7→ASL | idx7→ASM | idx5 closer |
|--------|----------|----------|----------|----------|-------------|
| train | 0.00 | 459.00 | 459.00 | 0.00 | ASL_L |
| V2 | 615.48 | 302.12 | 415.72 | 132.83 | ASM_L |

### B26_06

| Source | idx5→ASL | idx5→ASM | idx7→ASL | idx7→ASM | idx5 closer |
|--------|----------|----------|----------|----------|-------------|
| train | 0.00 | 603.56 | 603.56 | 0.00 | ASL_L |
| V2 | 810.92 | 214.28 | 658.01 | 61.93 | ASM_L |

### B26_09

| Source | idx5→ASL | idx5→ASM | idx7→ASL | idx7→ASM | idx5 closer |
|--------|----------|----------|----------|----------|-------------|
| train | 0.00 | 541.88 | 541.88 | 0.00 | ASL_L |
| V2 | 813.76 | 280.42 | 559.08 | 66.85 | ASM_L |

### B26_20

| Source | idx5→ASL | idx5→ASM | idx7→ASL | idx7→ASM | idx5 closer |
|--------|----------|----------|----------|----------|-------------|
| train | 0.00 | 487.17 | 487.17 | 0.00 | ASL_L |
| V2 | 704.02 | 217.32 | 523.32 | 48.63 | ASM_L |

### B26_21

| Source | idx5→ASL | idx5→ASM | idx7→ASL | idx7→ASM | idx5 closer |
|--------|----------|----------|----------|----------|-------------|
| train | 0.00 | 510.88 | 510.88 | 0.00 | ASL_L |
| V2 | 679.99 | 175.37 | 521.30 | 10.50 | ASM_L |

### B26_25

| Source | idx5→ASL | idx5→ASM | idx7→ASL | idx7→ASM | idx5 closer |
|--------|----------|----------|----------|----------|-------------|
| train | 0.00 | 437.26 | 437.26 | 0.00 | ASL_L |
| V2 | 645.09 | 223.92 | 561.18 | 130.45 | ASM_L |

## Réponses aux questions

- **Index 5 = ASL_L dans labels train ?** Oui (err5→ASL_L max 0.00 px)
- **Index 7 = ASM_L dans labels train ?** Oui (err7→ASM_L max 0.00 px)
- **Inversion ASL_L ↔ ASM_L dans labels train ?** Non (index 5→ASL_L et index 7→ASM_L à 0 px)
- **Inversion uniquement à gauche ?** Non côté train ; droite idx4→ASL_R / idx6→ASM_R OK (~0 px)
- **Labels corrects mais modèle apprend mal ?** Oui — V2 prédit près de GT_ASM_L
