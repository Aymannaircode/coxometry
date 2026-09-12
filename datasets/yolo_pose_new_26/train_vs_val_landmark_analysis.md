# Analyse V2 TRAIN vs VAL — erreurs landmark (new_26)

**Généré :** 2026-08-23T20:59:18.288490+00:00
**Modèle V2 :** `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt`
**Prédictions :** `datasets/yolo_pose_new_26/predictions_v2/labels/` (existantes, non modifiées)
**GT :** `annotation_pilot/annotations/new_26/`
**Split :** `datasets/yolo_pose_new_26/meta/split.json`

## Résumé

- Cas **TRAIN** : **21**
- Cas **VAL** : **5**
- Seuils diagnostic : bon < 150 px, mauvais ≥ 300 px

## Diagnostic automatique : **CAS A**

ASL_L très mauvais sur TRAIN et VAL — sous-apprentissage ou difficulté intrinsèque du landmark / capacité d'apprentissage insuffisante.

## Focus ASL / ASM

| Métrique | TRAIN | VAL |
|----------|-------|-----|
| ASL_L mean (px) | 538.18 | 471.72 |
| ASL_L median (px) | 529.42 | 441.55 |
| ASL_L min / max (px) | 214.79 / 813.76 | 346.63 / 704.02 |
| ASL_R mean (px) | 142.86 | 147.73 |
| ASL_R median (px) | 153.63 | 146.21 |
| ASM_L mean (px) | 77.59 | 80.94 |
| ASM_R mean (px) | 96.81 | 81.32 |

### Ratios VAL / TRAIN (mean)

- **ASL_L_val / ASL_L_train** = 0.88
- **ASL_R_val / ASL_R_train** = 1.03

- Référence évaluation globale 26 cas (ASL_L mean) : **525.40 px**

## Tableau comparatif — 14 landmarks

| Landmark | Train mean | Train median | Val mean | Val median |
|----------|------------|--------------|----------|------------|
| TD_R | 61.62 | 53.32 | 74.84 | 54.74 |
| TD_L | 61.10 | 56.64 | 78.53 | 70.78 |
| FHC_R | 62.02 | 60.83 | 62.88 | 46.39 |
| FHC_L | 52.49 | 48.08 | 80.94 | 83.65 |
| ASL_R | 142.86 | 153.63 | 147.73 | 146.21 |
| ASL_L | 538.18 | 529.42 | 471.72 | 441.55 |
| ASM_R | 96.81 | 78.41 | 81.32 | 73.02 |
| ASM_L | 77.59 | 76.34 | 80.94 | 102.71 |
| FNM_R | 62.69 | 60.70 | 59.72 | 54.66 |
| FNM_L | 52.78 | 51.92 | 81.05 | 69.96 |
| FSP_R | 156.39 | 143.03 | 127.63 | 129.29 |
| FSP_L | 164.57 | 187.53 | 192.77 | 153.88 |
| FSD_R | 154.28 | 157.26 | 180.98 | 209.18 |
| FSD_L | 93.71 | 65.85 | 168.21 | 102.64 |

## Statistiques détaillées — TRAIN (21 cas)

### TD_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 61.62 |
| Médiane | 53.32 |
| Écart-type | 37.50 |
| Min | 6.75 |
| Max | 134.72 |

### TD_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 61.10 |
| Médiane | 56.64 |
| Écart-type | 29.03 |
| Min | 22.67 |
| Max | 133.62 |

### FHC_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 62.02 |
| Médiane | 60.83 |
| Écart-type | 34.24 |
| Min | 10.05 |
| Max | 145.86 |

### FHC_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 52.49 |
| Médiane | 48.08 |
| Écart-type | 30.48 |
| Min | 7.38 |
| Max | 114.44 |

### ASL_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 142.86 |
| Médiane | 153.63 |
| Écart-type | 60.67 |
| Min | 42.49 |
| Max | 233.60 |

### ASL_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 538.18 |
| Médiane | 529.42 |
| Écart-type | 154.30 |
| Min | 214.79 |
| Max | 813.76 |

### ASM_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 96.81 |
| Médiane | 78.41 |
| Écart-type | 51.44 |
| Min | 25.00 |
| Max | 200.41 |

### ASM_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 77.59 |
| Médiane | 76.34 |
| Écart-type | 40.37 |
| Min | 10.50 |
| Max | 133.80 |

### FNM_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 62.69 |
| Médiane | 60.70 |
| Écart-type | 32.47 |
| Min | 10.41 |
| Max | 124.77 |

### FNM_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 52.78 |
| Médiane | 51.92 |
| Écart-type | 28.57 |
| Min | 7.31 |
| Max | 100.16 |

### FSP_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 156.39 |
| Médiane | 143.03 |
| Écart-type | 76.01 |
| Min | 66.39 |
| Max | 413.23 |

### FSP_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 164.57 |
| Médiane | 187.53 |
| Écart-type | 71.47 |
| Min | 25.76 |
| Max | 285.82 |

### FSD_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 154.28 |
| Médiane | 157.26 |
| Écart-type | 68.32 |
| Min | 36.98 |
| Max | 294.56 |

### FSD_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 21 |
| Moyenne | 93.71 |
| Médiane | 65.85 |
| Écart-type | 68.86 |
| Min | 18.18 |
| Max | 252.61 |


## Statistiques détaillées — VAL (5 cas)

### TD_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 74.84 |
| Médiane | 54.74 |
| Écart-type | 36.85 |
| Min | 39.78 |
| Max | 117.82 |

### TD_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 78.53 |
| Médiane | 70.78 |
| Écart-type | 31.66 |
| Min | 48.23 |
| Max | 127.98 |

### FHC_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 62.88 |
| Médiane | 46.39 |
| Écart-type | 43.60 |
| Min | 21.21 |
| Max | 133.07 |

### FHC_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 80.94 |
| Médiane | 83.65 |
| Écart-type | 16.87 |
| Min | 53.87 |
| Max | 98.74 |

### ASL_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 147.73 |
| Médiane | 146.21 |
| Écart-type | 59.46 |
| Min | 94.05 |
| Max | 237.36 |

### ASL_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 471.72 |
| Médiane | 441.55 |
| Écart-type | 136.34 |
| Min | 346.63 |
| Max | 704.02 |

### ASM_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 81.32 |
| Médiane | 73.02 |
| Écart-type | 28.12 |
| Min | 43.17 |
| Max | 112.31 |

### ASM_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 80.94 |
| Médiane | 102.71 |
| Écart-type | 45.44 |
| Min | 17.66 |
| Max | 120.19 |

### FNM_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 59.72 |
| Médiane | 54.66 |
| Écart-type | 32.74 |
| Min | 21.30 |
| Max | 105.13 |

### FNM_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 81.05 |
| Médiane | 69.96 |
| Écart-type | 30.42 |
| Min | 46.74 |
| Max | 116.41 |

### FSP_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 127.63 |
| Médiane | 129.29 |
| Écart-type | 110.72 |
| Min | 2.03 |
| Max | 294.22 |

### FSP_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 192.77 |
| Médiane | 153.88 |
| Écart-type | 71.31 |
| Min | 130.67 |
| Max | 293.40 |

### FSD_R

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 180.98 |
| Médiane | 209.18 |
| Écart-type | 89.07 |
| Min | 80.10 |
| Max | 277.76 |

### FSD_L

| Métrique | Valeur (px) |
|----------|-------------|
| N | 5 |
| Moyenne | 168.21 |
| Médiane | 102.64 |
| Écart-type | 146.47 |
| Min | 26.23 |
| Max | 401.34 |

## Erreurs ASL_L par cas

### TRAIN

| Cas | Erreur (px) |
|-----|-------------|
| B26_09 | 813.76 |
| B26_06 | 810.92 |
| B26_24 | 685.28 |
| B26_21 | 679.99 |
| B26_12 | 670.66 |
| B26_25 | 645.09 |
| B26_02 | 615.48 |
| B26_16 | 585.17 |
| B26_05 | 566.99 |
| B26_15 | 565.14 |
| B26_19 | 529.42 |
| B26_07 | 524.94 |
| B26_14 | 483.92 |
| B26_01 | 481.35 |
| B26_04 | 462.70 |
| B26_11 | 456.27 |
| B26_22 | 442.15 |
| B26_03 | 414.62 |
| B26_23 | 389.49 |
| B26_18 | 263.67 |
| B26_08 | 214.79 |

### VAL

| Cas | Erreur (px) |
|-----|-------------|
| B26_20 | 704.02 |
| B26_10 | 454.01 |
| B26_26 | 441.55 |
| B26_13 | 412.39 |
| B26_17 | 346.63 |

## Interprétation des cas

| Cas | Description |
|-----|-------------|
| **A** | ASL_L très mauvais TRAIN + VAL → sous-apprentissage / difficulté intrinsèque |
| **B** | ASL_L bon TRAIN, mauvais VAL → généralisation / dataset petit |
| **C** | ASL_L mauvais en moyenne mais certains TRAIN bons → instabilité |
| **D** | ASL_L bon TRAIN + VAL mais évaluation 26 cas mauvaise → pipeline d'éval |

## Regénérer

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\analyze_v2_train_vs_val_new_26.py
```
