# Diagnostic ASL_L — erreurs V2 vs GT (new_26)

**Généré :** 2026-08-23T20:51:38.824868+00:00

## Statistiques globales

| Métrique | Moyenne | Médiane | Écart-type | Min | Max |
|----------|---------|---------|------------|-----|-----|
| error_px | 525.40 | 504.43 | 150.78 | 214.79 | 813.76 |
| dx | -482.67 | -450.00 | 151.28 | -794.17 | -214.53 |
| dy | 173.23 | 180.83 | 115.95 | -105.72 | 330.41 |

## Diagnostic de biais

- **Décalage horizontal (dx = pred − GT)** : moyenne -482.67 px, médiane -450.00 px. dx < 0 (prédiction à **gauche** de GT / plus médial) : **26/26** cas ; dx > 0 : **0/26** cas.
- **Décalage vertical (dy = pred − GT)** : moyenne 173.23 px, médiane 180.83 px. dy < 0 (prédiction **au-dessus** de GT) : **2/26** cas ; dy > 0 (en dessous) : **24/26** cas.
- **Landmark GT le plus proche de V2 ASL_L** :
  - GT_ASM_L : **22/26** cas
  - GT_FHC_L : **4/26** cas
- **V2 ASL_L plus proche de GT_ASM_L que de GT_ASL_L** (confusion ASM) : **25/26** cas.
- **V2 ASL_L médial à GT_FHC_L** (x_pred < x_fhc) : **17/26** cas.
- Distance moyenne V2_ASL_L → GT_ASM_L : **187.50** px (erreur moyenne ASL_L : 525.40 px).
- Marge moyenne au bord d'image (min des 4 bords) : **921.09** px.
- **Interprétation** : biais systématique vers la **gauche image** (médial pour hanche gauche).
- **Interprétation** : dans la majorité des cas, la prédiction ressemble davantage à **ASM_L** qu'à **ASL_L**.

## Détail par cas (trié par error_px décroissant)

| Radio | error_px | dx | dy | conf | nearest_GT | dist→ASM_L | dist→FHC_L | dist→ASL_R | médial FHC |
|-------|----------|----|----|------|------------|------------|------------|------------|------------|
| B26_09 | 813.76 | -790.27 | 194.13 | 0.356 | GT_ASM_L | 280.42 | 420.88 | 1333.06 | True |
| B26_06 | 810.92 | -794.17 | 163.96 | 0.303 | GT_ASM_L | 214.28 | 406.02 | 1317.01 | True |
| B26_20 | 704.02 | -662.93 | 236.99 | 0.307 | GT_ASM_L | 217.32 | 336.60 | 1243.27 | True |
| B26_24 | 685.28 | -639.50 | 246.26 | 0.315 | GT_ASM_L | 129.10 | 314.79 | 1360.75 | True |
| B26_21 | 679.99 | -664.57 | 144.01 | 0.315 | GT_ASM_L | 175.37 | 446.34 | 1405.76 | True |
| B26_12 | 670.66 | -583.62 | 330.41 | 0.336 | GT_ASM_L | 200.89 | 350.77 | 1113.75 | True |
| B26_25 | 645.09 | -636.37 | -105.72 | 0.340 | GT_ASM_L | 223.92 | 443.84 | 1345.58 | True |
| B26_02 | 615.48 | -545.88 | 284.31 | 0.506 | GT_FHC_L | 302.12 | 245.91 | 1292.44 | True |
| B26_16 | 585.17 | -531.53 | 244.75 | 0.525 | GT_ASM_L | 118.12 | 194.71 | 1419.02 | True |
| B26_05 | 566.99 | -475.31 | 309.13 | 0.506 | GT_FHC_L | 240.04 | 151.18 | 1512.29 | True |
| B26_15 | 565.14 | -562.45 | 55.12 | 0.394 | GT_ASM_L | 74.89 | 321.50 | 1403.92 | True |
| B26_19 | 529.42 | -454.42 | 271.64 | 0.542 | GT_ASM_L | 165.17 | 233.05 | 1586.26 | True |
| B26_07 | 524.94 | -424.85 | 308.32 | 0.535 | GT_ASM_L | 146.08 | 275.76 | 1517.68 | False |
| B26_14 | 483.92 | -355.74 | 328.07 | 0.628 | GT_FHC_L | 226.75 | 180.49 | 1649.90 | False |
| B26_01 | 481.35 | -369.73 | 308.22 | 0.580 | GT_ASM_L | 77.97 | 168.45 | 1324.59 | True |
| B26_04 | 462.70 | -433.22 | 162.52 | 0.515 | GT_ASM_L | 198.34 | 205.35 | 1498.22 | True |
| B26_11 | 456.27 | -456.06 | 13.91 | 0.442 | GT_ASM_L | 104.68 | 358.74 | 1584.98 | True |
| B26_10 | 454.01 | -445.58 | 87.08 | 0.529 | GT_ASM_L | 107.35 | 254.53 | 1617.39 | False |
| B26_22 | 442.15 | -403.96 | 179.75 | 0.579 | GT_FHC_L | 250.40 | 186.26 | 1578.25 | False |
| B26_26 | 441.55 | -441.06 | 20.70 | 0.395 | GT_ASM_L | 123.46 | 278.84 | 1314.71 | True |
| B26_03 | 414.62 | -380.51 | 164.69 | 0.553 | GT_ASM_L | 171.70 | 272.87 | 1758.90 | False |
| B26_13 | 412.39 | -367.86 | 186.39 | 0.498 | GT_ASM_L | 143.11 | 220.50 | 1414.33 | True |
| B26_23 | 389.49 | -344.40 | 181.91 | 0.549 | GT_ASM_L | 207.28 | 213.21 | 1592.28 | False |
| B26_17 | 346.63 | -339.01 | 72.24 | 0.625 | GT_ASM_L | 268.91 | 268.98 | 1768.24 | False |
| B26_18 | 263.67 | -231.80 | 125.67 | 0.548 | GT_ASM_L | 231.33 | 338.65 | 1554.99 | False |
| B26_08 | 214.79 | -214.53 | -10.56 | 0.599 | GT_ASM_L | 275.98 | 317.67 | 1435.10 | False |
