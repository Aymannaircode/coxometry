# Faisabilité refinement ASL_L post-V2 (new_26)

**Généré :** 2026-08-23T22:54:48.627378+00:00
**Mode :** lecture seule — V2 intact, aucun entraînement

## Verdict : **FEASIBLE**

- Erreur V2 brute : mean=525.40 px, median=504.43 px
- Meilleure baseline learnable : **mirror_asl_r_calibrated** (mean=105.38, median=97.37)
- Réduction vs V2 : mean **79.9%**, median **80.7%**
- Oracle ASM-relative : median=80.00 px
- Oracle sourcil polaire : median=80.00 px
- V2_ASL_L plus proche GT_ASM_L que GT_ASL_L : **25/26** cas
- Biais dx cohérent (même signe) : **26/26** cas
- CV dx/W=0.333, CV dy/H=0.683, écart angular ASM→ASL=73.2°
- Une correction simple (translation ou offset ASM global) réduit fortement l'erreur avec un biais structuré — refinement post-V2 recommandable.

## 1. Erreur vectorielle ASL_L (V2 − GT)

| Métrique | dx (px) | dy (px) | dx/W | dy/H | error_px |
|----------|---------|---------|------|------|----------|
| Moyenne | -482.67 | 173.23 | -0.1678 | 0.0694 | 525.40 |
| Médiane | -450.00 | 180.83 | -0.1572 | 0.0706 | 504.43 |

## 2. Relations spatiales

- V2_ASL_L plus proche **GT_ASM_L** que GT_ASL_L : **25/26** cas
- Distance moyenne V2_ASL_L → GT_ASM_L : **187.50** px
- Distance moyenne V2_ASL_L → GT_ASL_L : **525.40** px
- Longueur moyenne GT ASM_L→ASL_L : **524.89** px
- Longueur moyenne V2 ASM_L→ASL_L : **142.26** px
- Écart angular moyen vecteur ASM→ASL (V2 vs GT) : **84.95**°

## 3. Corrélations (Pearson vs error_px ASL_L)

| Variable | r |
|----------|---|
| v2_err_asl_r | 0.115 |
| v2_err_asm_l | -0.376 |
| v2_err_fhc_l | -0.268 |
| v2_err_fnm_l | -0.044 |
| image_width | -0.136 |
| image_height | -0.140 |
| pelvis_width_px | 0.055 |
| dist_gt_asm_to_gt_asl | 0.103 |
| dist_v2_asm_to_v2_asl | 0.145 |

## 4. Baselines de correction simple

| Baseline | Mean px | Median px | Δ mean vs V2 | Oracle |
|----------|---------|-----------|--------------|--------|
| v2_raw | 525.40 | 504.43 | 0.0% | non |
| translation_mean | 171.07 | 159.81 | 67.4% | non |
| translation_median | 168.90 | 157.82 | 67.9% | non |
| asm_global_offset | 107.11 | 93.91 | 79.6% | non |
| asm_oracle_per_case | 78.23 | 80.00 | 85.1% | oui |
| mirror_asl_r_fhc | 118.31 | 111.65 | 77.5% | non |
| mirror_asl_r_calibrated | 105.38 | 97.37 | 79.9% | non |
| eyebrow_global_polar | 107.59 | 92.97 | 79.5% | non |
| eyebrow_oracle_polar | 78.23 | 80.00 | 85.1% | oui |
| blend50_asm_global | 279.57 | 283.68 | 46.8% | non |

## 5. Détail par cas (V2 brut)

| Cas | error | dx | dy | dist→GT_ASM | angle_err ASM→ASL | pelvis_w |
|-----|-------|----|----|-------------|-------------------|----------|
| B26_09 | 813.76 | -790.27 | 194.13 | 280.42 | 149.5 | 1228.80 |
| B26_06 | 810.92 | -794.17 | 163.96 | 214.28 | 168.1 | 1137.55 |
| B26_20 | 704.02 | -662.93 | 236.99 | 217.32 | 174.8 | 1107.53 |
| B26_24 | 685.28 | -639.50 | 246.26 | 129.10 | 168.0 | 1090.80 |
| B26_21 | 679.99 | -664.57 | 144.01 | 175.37 | 161.6 | 1278.31 |
| B26_12 | 670.66 | -583.62 | 330.41 | 200.89 | 188.6 | 1063.68 |
| B26_25 | 645.09 | -636.37 | -105.72 | 223.92 | 144.8 | 1236.68 |
| B26_02 | 615.48 | -545.88 | 284.31 | 302.12 | 130.0 | 1153.51 |
| B26_16 | 585.17 | -531.53 | 244.75 | 118.12 | 131.4 | 1155.98 |
| B26_05 | 566.99 | -475.31 | 309.13 | 240.04 | 106.3 | 1202.29 |
| B26_15 | 565.14 | -562.45 | 55.12 | 74.89 | -21.2 | 1080.79 |
| B26_19 | 529.42 | -454.42 | 271.64 | 165.17 | 53.2 | 1227.80 |
| B26_07 | 524.94 | -424.85 | 308.32 | 146.08 | 41.5 | 1250.70 |
| B26_14 | 483.92 | -355.74 | 328.07 | 226.75 | 46.2 | 1126.37 |
| B26_01 | 481.35 | -369.73 | 308.22 | 77.97 | 65.2 | 1140.89 |
| B26_04 | 462.70 | -433.22 | 162.52 | 198.34 | 55.8 | 1258.72 |
| B26_11 | 456.27 | -456.06 | 13.91 | 104.68 | -17.1 | 1252.04 |
| B26_10 | 454.01 | -445.58 | 87.08 | 107.35 | 28.4 | 1073.41 |
| B26_22 | 442.15 | -403.96 | 179.75 | 250.40 | 20.4 | 1045.08 |
| B26_26 | 441.55 | -441.06 | 20.70 | 123.46 | 138.4 | 1298.72 |
| B26_03 | 414.62 | -380.51 | 164.69 | 171.70 | 24.7 | 1287.67 |
| B26_13 | 412.39 | -367.86 | 186.39 | 143.11 | 98.9 | 1240.93 |
| B26_23 | 389.49 | -344.40 | 181.91 | 207.28 | 35.4 | 1088.88 |
| B26_17 | 346.63 | -339.01 | 72.24 | 268.91 | 5.2 | 1166.61 |
| B26_18 | 263.67 | -231.80 | 125.67 | 231.33 | 23.4 | 1139.44 |
| B26_08 | 214.79 | -214.53 | -10.56 | 275.98 | -10.7 | 1071.39 |

## 6. Recommandation stratégique

- **Conserver V2** comme détecteur principal (26/26, conf box ~0.89).
- Envisager un **refinement ASL_L uniquement** si verdict FEASIBLE ou PARTIALLY FEASIBLE.
- V4 est **NO-GO** — ne pas remplacer V2 par fine-tuning global.

CSV : `asl_l_refinement_feasibility.csv`
