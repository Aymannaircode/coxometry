# Rapport de préparation YOLO Pose — new_26

**Date :** 2026-08-23 17:50:22
**Sources (non modifiées) :** `annotation_pilot\annotations\new_26`
**Dataset YOLO :** `datasets\yolo_pose_new_26`

## Résumé

| Métrique | Valeur |
|----------|--------|
| Images train | 21 |
| Images val | 5 |
| Labels train | 21 |
| Labels val | 5 |
| Keypoints par image | 14 |
| Keypoints total (train+val) | 364 |
| Classe | `pelvis` (id=0) |
| kpt_shape | [14, 3] |
| Colonnes par label | 47 |
| Split seed | 42 |
| Anomalies | 0 |

## Split reproductible

- **Train (21) :** `B26_01`, `B26_02`, `B26_03`, `B26_04`, `B26_05`, `B26_06`, `B26_07`, `B26_08`, `B26_09`, `B26_11`, `B26_12`, `B26_14`, `B26_15`, `B26_16`, `B26_18`, `B26_19`, `B26_21`, `B26_22`, `B26_23`, `B26_24`, `B26_25`
- **Val (5) :** `B26_10`, `B26_13`, `B26_17`, `B26_20`, `B26_26`

## Dimensions des images

| pilot_id | split | width | height | keypoints visibles |
|----------|-------|------:|-------:|-------------------:|
| B26_01 | train | 2730 | 2665 | 14 |
| B26_02 | train | 3030 | 1975 | 14 |
| B26_03 | train | 3030 | 2410 | 14 |
| B26_04 | train | 3030 | 2688 | 14 |
| B26_05 | train | 3008 | 3008 | 14 |
| B26_06 | train | 2751 | 2430 | 14 |
| B26_07 | train | 2998 | 2687 | 14 |
| B26_08 | train | 2672 | 2423 | 14 |
| B26_09 | train | 2983 | 2225 | 14 |
| B26_10 | val | 3039 | 2625 | 14 |
| B26_11 | train | 2871 | 2570 | 14 |
| B26_12 | train | 2986 | 2437 | 14 |
| B26_13 | val | 3234 | 2961 | 14 |
| B26_14 | train | 2779 | 2592 | 14 |
| B26_15 | train | 2548 | 2279 | 14 |
| B26_16 | train | 3006 | 2401 | 14 |
| B26_17 | val | 2763 | 2442 | 14 |
| B26_18 | train | 3006 | 2625 | 14 |
| B26_19 | train | 2825 | 2228 | 14 |
| B26_20 | val | 2701 | 2514 | 14 |
| B26_21 | train | 3008 | 2998 | 14 |
| B26_22 | train | 3006 | 2470 | 14 |
| B26_23 | train | 3030 | 2327 | 14 |
| B26_24 | train | 2548 | 2466 | 14 |
| B26_25 | train | 2851 | 2469 | 14 |
| B26_26 | val | 2822 | 2426 | 14 |

## Conversion appliquée

1. Lecture JSON MVP (`landmarks[].x/y/v` en pixels).
2. Ordre des 14 keypoints conservé : TD_R, TD_L, FHC_R, FHC_L, …, FSD_R, FSD_L.
3. Normalisation YOLO : `x_norm = x / image_width`, `y_norm = y / image_height`.
4. Visibilité : v=2 → visible ; v=0/null → (0, 0, 0).
5. Bbox instance dérivée de l'enveloppe des keypoints visibles (+2 % marge).
6. PNG 1:1 générées depuis DICOM (sources DICOM intactes).

## Vérification des labels

- Tous les labels passent les contrôles de format, bornes et visibilité.

## Fichiers produits

- `dataset.yaml`
- `images/train/`, `images/val/`
- `labels/train/`, `labels/val/`
- `meta/split.json`
- `meta/source_mapping.csv`
- `meta/keypoint_order.md`
- `preparation_report.md`

---
*Aucune annotation source, DICOM ou schéma JSON modifié. Entraînement non lancé.*
