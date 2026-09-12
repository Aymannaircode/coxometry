# Comparaison YOLO V1 vs V2 — new_26

**Généré le :** 2026-08-23 17:37:11 UTC
**Référence :** annotations humaines `annotation_pilot/annotations/new_26/B26_XX.json`
**V1 :** `datasets/yolo_pose_new_26/predictions/labels/`
**V2 :** `datasets/yolo_pose_new_26/predictions_v2/labels/`

## Résumé global

- Cas comparés : **26**
- Landmarks évalués (total, hors v=0) : **364**
- Erreur moyenne V1 : **232.02 px**
- Erreur moyenne V2 : **128.48 px**
- Amélioration V2 vs V1 : **103.54 px** (44.6 %)
- Meilleur modèle global : **V2**

## Tableau par landmark

| Landmark | V1 mean px | V2 mean px | Amélioration px | Amélioration % | Meilleur |
|----------|------------|------------|-----------------|----------------|----------|
| TD_R | 94.13 | 64.17 | 29.97 | 31.8 | V2 |
| TD_L | 89.36 | 64.45 | 24.90 | 27.9 | V2 |
| FHC_R | 254.07 | 62.19 | 191.88 | 75.5 | V2 |
| FHC_L | 49.92 | 57.96 | -8.04 | -16.1 | V1 |
| ASL_R | 130.57 | 143.79 | -13.23 | -10.1 | V1 |
| ASL_L | 1023.35 | 525.40 | 497.95 | 48.7 | V2 |
| ASM_R | 96.14 | 93.83 | 2.30 | 2.4 | V2 |
| ASM_L | 68.27 | 78.23 | -9.96 | -14.6 | V1 |
| FNM_R | 61.31 | 62.12 | -0.81 | -1.3 | V1 |
| FNM_L | 67.58 | 58.22 | 9.36 | 13.9 | V2 |
| ** FSP_R **| 251.25 | 150.86 | 100.38 | 40.0 | V2 |
| ** FSP_L **| 276.97 | 169.99 | 106.98 | 38.6 | V2 |
| ** FSD_R **| 638.65 | 159.41 | 479.23 | 75.0 | V2 |
| ** FSD_L **| 146.74 | 108.04 | 38.71 | 26.4 | V2 |

## Résumé par groupe

| Groupe | V1 mean px | V2 mean px | Amélioration px | Amélioration % | Meilleur |
|--------|------------|------------|-----------------|----------------|----------|
| TD | 91.74 | 64.31 | 27.43 | 29.9 | V2 |
| FHC | 151.99 | 60.07 | 91.92 | 60.5 | V2 |
| ASL | 576.96 | 334.60 | 242.36 | 42.0 | V2 |
| ASM | 82.20 | 86.03 | -3.83 | -4.7 | V1 |
| FNM | 64.44 | 60.17 | 4.27 | 6.6 | V2 |
| ** FSP **| 264.11 | 160.43 | 103.68 | 39.3 | V2 |
| ** FSD **| 392.70 | 133.73 | 258.97 | 65.9 | V2 |

## Points saillants FSP / FSD

- **FSP_R** : V1=251.25 px, V2=150.86 px, Δ=100.38 px (40.0 %), meilleur=V2
- **FSP_L** : V1=276.97 px, V2=169.99 px, Δ=106.98 px (38.6 %), meilleur=V2
- **FSD_R** : V1=638.65 px, V2=159.41 px, Δ=479.23 px (75.0 %), meilleur=V2
- **FSD_L** : V1=146.74 px, V2=108.04 px, Δ=38.71 px (26.4 %), meilleur=V2

## Fichiers / prédictions manquants

- ground_truth_v0_exclus : 0
- prediction_v1_absente : 0
- prediction_v2_absente : 0
- v1_landmarks_manquants : 0
- v2_landmarks_manquants : 0

## Notes

- Les landmarks ground truth avec `v=0` sont exclus.
- Une prédiction est considérée manquante si le fichier est absent ou si la confiance keypoint < 0.25.
- Amélioration positive = V2 plus proche du ground truth (erreur plus faible).
