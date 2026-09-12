# Comparaison landmarks V2 vs V3 — new_26

**Genere :** 2026-08-28T19:17:27.628335+00:00
**Mode :** lecture seule — aucun fichier de production modifie.

## Protocole

| Element | V2 | V3 |
|---------|----|----|
| Modele | `runs\pose\runs\pose\runs\yolo_pose_new_26_v2-3\weights\best.pt` | `runs\pose\yolo_pose_new_26_v3_anatomical-2\weights\best.pt` |
| Images | `predictions_v2/images/` (DICOM PNG 1:1, 26 cas) | **memes images** |
| GT | `annotation_pilot/annotations/new_26/*.json` | idem |
| Inference V2 | predictions existantes (`predictions_v2/labels/`) | — |
| Inference V3 | — | Ultralytics predict, `imgsz=1280`, `conf=0.25`, `save_conf=True` |
| Detection conf min | 0.25 (defaut Ultralytics, identique V2) | 0.25 |
| Keypoint conf min (parsing) | 0.25 | 0.25 |
| Erreur | euclidienne pixels natifs | idem |

### Seuils statut

| Statut | Seuil |
|--------|------:|
| CORRECT | <= 75 px |
| INCERTAIN | 76-149 px |
| INCORRECT | >= 150 px |

**Detections :** V2 26/26 cas | V3 3/26 cas

**Cas V3 avec detection (conf>=0.25) :** B26_03, B26_05, B26_17

### Cas sans detection V3 valide (conf=0.25)

- B26_01:missing_label
- B26_02:missing_label
- B26_04:missing_label
- B26_06:missing_label
- B26_07:missing_label
- B26_08:missing_label
- B26_09:missing_label
- B26_10:missing_label
- B26_11:missing_label
- B26_12:missing_label
- B26_13:missing_label
- B26_14:missing_label
- B26_15:missing_label
- B26_16:missing_label
- B26_18:missing_label
- B26_19:missing_label
- B26_20:missing_label
- B26_21:missing_label
- B26_22:missing_label
- B26_23:missing_label
- B26_24:missing_label
- B26_25:missing_label
- B26_26:missing_label

## Synthese — cas communs (detection V2 et V3)

Cas : B26_03, B26_05, B26_17 (3/26)

| Metrique | V2 | V3 | Delta |
|----------|---:|---:|------:|
| mean px focus | 207.3 | 1771.8 | 1564.5 |
| median px focus | 196.7 | 1885.8 | 1689.1 |
| P90 px focus | 414.6 | 3054.5 | 2639.9 |
| % CORRECT | 16.7 | 0.0 | -16.7 |
| % INCORRECT | 66.7 | 92.3 | 25.6 |

## Synthese executive — FSP/FSD/ASL

| Scope | Metrique | V2 | V3 | Delta (V3-V2) |
|-------|----------|---:|---:|---:|
| 26 cas | mean px (focus) | 209.6 | 1771.8 | +1562.2 |
| 26 cas | median px (focus) | 160.0 | 1885.8 | +1725.8 |
| 26 cas | P90 px (focus) | 462.7 | 3054.5 | +2591.8 |
| 26 cas | % CORRECT focus | 16.0 | 0.0 | -16.0 |
| 26 cas | % INCERTAIN focus | 27.6 | 7.7 | -19.9 |
| 26 cas | % INCORRECT focus | 55.1 | 92.3 | +37.2 |
| Val 5 | mean px (focus) | 214.8 | 1478.0 | +1263.2 |
| Val 5 | median px (focus) | 160.5 | 1807.2 | +1646.7 |
| Val 5 | P90 px (focus) | 412.4 | 2210.4 | +1798.0 |
| Val 5 | % CORRECT focus | 10.0 | 0.0 | -10.0 |
| Val 5 | % INCERTAIN focus | 33.3 | 25.0 | -8.3 |
| Val 5 | % INCORRECT focus | 56.7 | 75.0 | +18.3 |
| B26_01 | mean px (focus) | 317.5 | NA | NA |
| B26_01 | median px (focus) | 275.3 | NA | NA |
| B26_01 | P90 px (focus) | 481.4 | NA | NA |
| B26_01 | % CORRECT focus | 0.0 | NA | NA |
| B26_01 | % INCERTAIN focus | 0.0 | NA | NA |
| B26_01 | % INCORRECT focus | 100.0 | NA | NA |
| B26_12 | mean px (focus) | 213.5 | NA | NA |
| B26_12 | median px (focus) | 156.9 | NA | NA |
| B26_12 | P90 px (focus) | 670.7 | NA | NA |
| B26_12 | % CORRECT focus | 16.7 | NA | NA |
| B26_12 | % INCERTAIN focus | 33.3 | NA | NA |
| B26_12 | % INCORRECT focus | 50.0 | NA | NA |
| B26_13 | mean px (focus) | 219.7 | NA | NA |
| B26_13 | median px (focus) | 204.2 | NA | NA |
| B26_13 | P90 px (focus) | 412.4 | NA | NA |
| B26_13 | % CORRECT focus | 16.7 | NA | NA |
| B26_13 | % INCERTAIN focus | 33.3 | NA | NA |
| B26_13 | % INCORRECT focus | 50.0 | NA | NA |

## Verdict

V3 **DEGRADE** vs V2 sur la precision anatomique pixel-level (focus FSP/FSD/ASL). **Conserver V2 en production.** Ne pas brancher V3.

## Cas prioritaires — detail par landmark (px)

### B26_01 (train)

| Landmark | V2 px | V2 statut | V3 px | V3 statut | Delta |
|----------|------:|-----------|------:|-----------|------:|
| ASL_R | 228.48 | INCORRECT | NA | - | NA |
| ASL_L | 481.35 | INCORRECT | NA | - | NA |
| ASM_R | 77.29 | INCERTAIN | NA | - | NA |
| ASM_L | 60.58 | CORRECT | NA | - | NA |
| FHC_R | 50.77 | CORRECT | NA | - | NA |
| FHC_L | 34.28 | CORRECT | NA | - | NA |
| FNM_R | 124.77 | INCERTAIN | NA | - | NA |
| FNM_L | 67.25 | CORRECT | NA | - | NA |
| TD_R | 124.37 | INCERTAIN | NA | - | NA |
| TD_L | 56.64 | CORRECT | NA | - | NA |
| FSP_R | 413.23 | INCORRECT | NA | - | NA |
| FSP_L | 256.07 | INCORRECT | NA | - | NA |
| FSD_R | 294.56 | INCORRECT | NA | - | NA |
| FSD_L | 231.11 | INCORRECT | NA | - | NA |

### B26_12 (train)

| Landmark | V2 px | V2 statut | V3 px | V3 statut | Delta |
|----------|------:|-----------|------:|-----------|------:|
| ASL_R | 183.02 | INCORRECT | NA | - | NA |
| ASL_L | 670.66 | INCORRECT | NA | - | NA |
| ASM_R | 25.0 | CORRECT | NA | - | NA |
| ASM_L | 76.34 | INCERTAIN | NA | - | NA |
| FHC_R | 37.49 | CORRECT | NA | - | NA |
| FHC_L | 48.08 | CORRECT | NA | - | NA |
| FNM_R | 98.58 | INCERTAIN | NA | - | NA |
| FNM_L | 51.92 | CORRECT | NA | - | NA |
| TD_R | 85.96 | INCERTAIN | NA | - | NA |
| TD_L | 85.57 | INCERTAIN | NA | - | NA |
| FSP_R | 183.43 | INCORRECT | NA | - | NA |
| FSP_L | 130.78 | INCERTAIN | NA | - | NA |
| FSD_R | 77.23 | INCERTAIN | NA | - | NA |
| FSD_L | 36.09 | CORRECT | NA | - | NA |

### B26_13 (val)

| Landmark | V2 px | V2 statut | V3 px | V3 statut | Delta |
|----------|------:|-----------|------:|-----------|------:|
| ASL_R | 94.25 | INCERTAIN | NA | - | NA |
| ASL_L | 412.39 | INCORRECT | NA | - | NA |
| ASM_R | 105.76 | INCERTAIN | NA | - | NA |
| ASM_L | 102.71 | INCERTAIN | NA | - | NA |
| FHC_R | 46.39 | CORRECT | NA | - | NA |
| FHC_L | 89.69 | INCERTAIN | NA | - | NA |
| FNM_R | 21.3 | CORRECT | NA | - | NA |
| FNM_L | 109.53 | INCERTAIN | NA | - | NA |
| TD_R | 50.29 | CORRECT | NA | - | NA |
| TD_L | 48.23 | CORRECT | NA | - | NA |
| FSP_R | 2.03 | CORRECT | NA | - | NA |
| FSP_L | 130.67 | INCERTAIN | NA | - | NA |
| FSD_R | 277.76 | INCORRECT | NA | - | NA |
| FSD_L | 401.34 | INCORRECT | NA | - | NA |

### B26_10 (val)

| Landmark | V2 px | V2 statut | V3 px | V3 statut | Delta |
|----------|------:|-----------|------:|-----------|------:|
| ASL_R | 166.79 | INCORRECT | NA | - | NA |
| ASL_L | 454.01 | INCORRECT | NA | - | NA |
| ASM_R | 43.17 | CORRECT | NA | - | NA |
| ASM_L | 17.66 | CORRECT | NA | - | NA |
| FHC_R | 74.15 | CORRECT | NA | - | NA |
| FHC_L | 78.73 | INCERTAIN | NA | - | NA |
| FNM_R | 39.77 | CORRECT | NA | - | NA |
| FNM_L | 46.74 | CORRECT | NA | - | NA |
| TD_R | 39.78 | CORRECT | NA | - | NA |
| TD_L | 127.98 | INCERTAIN | NA | - | NA |
| FSP_R | 154.24 | INCORRECT | NA | - | NA |
| FSP_L | 242.16 | INCORRECT | NA | - | NA |
| FSD_R | 243.43 | INCORRECT | NA | - | NA |
| FSD_L | 213.21 | INCORRECT | NA | - | NA |

### B26_17 (val)

| Landmark | V2 px | V2 statut | V3 px | V3 statut | Delta |
|----------|------:|-----------|------:|-----------|------:|
| ASL_R | 237.36 | INCORRECT | 87.23 | INCERTAIN | -150.1 |
| ASL_L | 346.63 | INCORRECT | 1965.68 | INCORRECT | 1619.1 |
| ASM_R | 72.35 | CORRECT | NA | - | NA |
| ASM_L | 115.52 | INCERTAIN | 1416.52 | INCORRECT | 1301.0 |
| FHC_R | 21.21 | CORRECT | NA | - | NA |
| FHC_L | 53.87 | CORRECT | 1385.54 | INCORRECT | 1331.7 |
| FNM_R | 54.66 | CORRECT | NA | - | NA |
| FNM_L | 69.96 | CORRECT | 1769.66 | INCORRECT | 1699.7 |
| TD_R | 111.57 | INCERTAIN | 699.61 | INCORRECT | 588.0 |
| TD_L | 56.67 | CORRECT | NA | - | NA |
| FSP_R | 58.38 | CORRECT | NA | - | NA |
| FSP_L | 143.73 | INCERTAIN | 1648.78 | INCORRECT | 1505.0 |
| FSD_R | 209.18 | INCORRECT | NA | - | NA |
| FSD_L | 26.23 | CORRECT | 2210.39 | INCORRECT | 2184.2 |

### B26_20 (val)

| Landmark | V2 px | V2 statut | V3 px | V3 statut | Delta |
|----------|------:|-----------|------:|-----------|------:|
| ASL_R | 94.05 | INCERTAIN | NA | - | NA |
| ASL_L | 704.02 | INCORRECT | NA | - | NA |
| ASM_R | 73.02 | CORRECT | NA | - | NA |
| ASM_L | 48.63 | CORRECT | NA | - | NA |
| FHC_R | 39.59 | CORRECT | NA | - | NA |
| FHC_L | 83.65 | INCERTAIN | NA | - | NA |
| FNM_R | 77.75 | INCERTAIN | NA | - | NA |
| FNM_L | 62.62 | CORRECT | NA | - | NA |
| TD_R | 54.74 | CORRECT | NA | - | NA |
| TD_L | 70.78 | CORRECT | NA | - | NA |
| FSP_R | 129.29 | INCERTAIN | NA | - | NA |
| FSP_L | 153.88 | INCORRECT | NA | - | NA |
| FSD_R | 80.1 | INCERTAIN | NA | - | NA |
| FSD_L | 97.62 | INCERTAIN | NA | - | NA |

### B26_26 (val)

| Landmark | V2 px | V2 statut | V3 px | V3 statut | Delta |
|----------|------:|-----------|------:|-----------|------:|
| ASL_R | 146.21 | INCERTAIN | NA | - | NA |
| ASL_L | 441.55 | INCORRECT | NA | - | NA |
| ASM_R | 112.31 | INCERTAIN | NA | - | NA |
| ASM_L | 120.19 | INCERTAIN | NA | - | NA |
| FHC_R | 133.07 | INCERTAIN | NA | - | NA |
| FHC_L | 98.74 | INCERTAIN | NA | - | NA |
| FNM_R | 105.13 | INCERTAIN | NA | - | NA |
| FNM_L | 116.41 | INCERTAIN | NA | - | NA |
| TD_R | 117.82 | INCERTAIN | NA | - | NA |
| TD_L | 88.99 | INCERTAIN | NA | - | NA |
| FSP_R | 294.22 | INCORRECT | NA | - | NA |
| FSP_L | 293.4 | INCORRECT | NA | - | NA |
| FSD_R | 94.43 | INCERTAIN | NA | - | NA |
| FSD_L | 102.64 | INCERTAIN | NA | - | NA |

## Split validation (5 cas) — par landmark

| Landmark | V2 mean | V2 med | V2 P90 | V2 %CORR | V3 mean | V3 med | V3 P90 | V3 %CORR |
|----------|--------:|-------:|-------:|---------:|--------:|-------:|-------:|---------:|
| ASL_R | 147.7 | 146.2 | 237.4 | 0.0 | 87.2 | 87.2 | 87.2 | 0.0 |
| ASL_L | 471.7 | 441.6 | 704.0 | 0.0 | 1965.7 | 1965.7 | 1965.7 | 0.0 |
| ASM_R | 81.3 | 73.0 | 112.3 | 60.0 | NA | NA | NA | NA |
| ASM_L | 80.9 | 102.7 | 120.2 | 40.0 | 1416.5 | 1416.5 | 1416.5 | 0.0 |
| FHC_R | 62.9 | 46.4 | 133.1 | 80.0 | NA | NA | NA | NA |
| FHC_L | 80.9 | 83.7 | 98.7 | 20.0 | 1385.5 | 1385.5 | 1385.5 | 0.0 |
| FNM_R | 59.7 | 54.7 | 105.1 | 60.0 | NA | NA | NA | NA |
| FNM_L | 81.1 | 70.0 | 116.4 | 60.0 | 1769.7 | 1769.7 | 1769.7 | 0.0 |
| TD_R | 74.8 | 54.7 | 117.8 | 60.0 | 699.6 | 699.6 | 699.6 | 0.0 |
| TD_L | 78.5 | 70.8 | 128.0 | 60.0 | NA | NA | NA | NA |
| FSP_R | 127.6 | 129.3 | 294.2 | 40.0 | NA | NA | NA | NA |
| FSP_L | 192.8 | 153.9 | 293.4 | 0.0 | 1648.8 | 1648.8 | 1648.8 | 0.0 |
| FSD_R | 181.0 | 209.2 | 277.8 | 0.0 | NA | NA | NA | NA |
| FSD_L | 168.2 | 102.6 | 401.3 | 20.0 | 2210.4 | 2210.4 | 2210.4 | 0.0 |

## Focus FSP/FSD/ASL — 26 cas

| Landmark | V2 mean | V2 P90 | V2 %INCORR | V3 mean | V3 P90 | V3 %INCORR | Gagnant |
|----------|--------:|-------:|-----------:|--------:|-------:|-----------:|---------:|
| ASL_R | 143.8 | 228.5 | 50.0 | 251.9 | 416.5 | 50.0 | V2 |
| ASL_L | 525.4 | 704.0 | 100.0 | 2179.8 | 2325.9 | 100.0 | V2 |
| FSP_R | 150.9 | 243.2 | 46.2 | 1197.2 | 1216.6 | 100.0 | V2 |
| FSP_L | 170.0 | 256.1 | 57.7 | 1648.8 | 1648.8 | 100.0 | V2 |
| FSD_R | 159.4 | 268.5 | 57.7 | 1813.3 | 1885.8 | 100.0 | V2 |
| FSD_L | 108.0 | 231.1 | 19.2 | 2773.5 | 3055.8 | 100.0 | V2 |

## Notes

- Comparaison fondee sur **erreur pixel vs GT**, pas mAP.
- V2 reste le modele de production ; V3 non branche.
- Refinement ASL_L **non applique** (YOLO raw vs GT, protocole identique a `analyze_v2_train_vs_val_new_26.py`).
- V2 inferenced a sa resolution d'entrainement (640, via predictions existantes) ; V3 a `imgsz=1280`.
- **Limitation majeure V3 :** seulement **3/26 detections** a `conf=0.25` (B26_03, B26_05, B26_17). Les 23 autres cas n'ont **aucune sortie** — echec bloquant pour un usage clinique.
- Les agregats V3 « 26 cas » ne portent que sur les mesures disponibles (3 cas detectes), pas sur l'ensemble du dataset.
- Sur B26_17 (val, seul cas val detecte par V3), V3 ameliore ASL_R (87 vs 237 px) mais **degrade massivement** ASL_L, FSP_L, FSD_L (>1600 px).
