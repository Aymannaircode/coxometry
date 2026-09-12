# Validation stricte TRAIN → VAL — refinement C_asm_offset ASL_L

**Généré :** 2026-08-23T23:00:38.002789+00:00
**Protocole :** calibrage GT sur 21 TRAIN ; application sur 5 VAL sans fuite
**Verdict :** **ROBUST**

## Calibrage (TRAIN uniquement)

- Cas TRAIN : 21
- Offset moyen GT ASM_L→ASL_L : **(511.56, -92.68)** px
- Écart-type offset : (67.24, 125.91) px
- Cas VAL (jamais utilisés pour calibrage) : B26_10, B26_13, B26_17, B26_20, B26_26

## 1. Résultat pixel-level (VAL, n=5)

| Métrique | V2 brut | Refined |
|----------|---------|---------|
| ASL_L error mean px | 471.72 | 100.73 |
| ASL_L error median px | 441.55 | 77.03 |
| Amélioration mean | — | 78.6% |
| Cas améliorés | — | 5/5 |
| Cas dégradés | — | 0/5 |

### Détail par cas VAL

| Cas | V2 px | Refined px | Δ |
|-----|-------|------------|---|
| B26_10 | 454.01 | 63.37 | -390.64 |
| B26_13 | 412.39 | 143.51 | -268.88 |
| B26_17 | 346.62 | 77.03 | -269.59 |
| B26_20 | 704.02 | 64.83 | -639.19 |
| B26_26 | 441.55 | 154.91 | -286.64 |

## 2. Résultat géométrique (VAL vs GT annotations)

### VCE_L

| Métrique | V2 | Refined |
|----------|----|---------|
| \|pred−GT\| mean ° | 70.31 | 10.04 |
| \|pred−GT\| median ° | 63.19 | 10.08 |
| négatifs | 4 | 0 |
| asymétrie \|R−L\| mean ° | 66.17 | 4.67 |

### Tönnis_L

| Métrique | V2 | Refined |
|----------|----|---------|
| \|pred−GT\| mean ° | 87.89 | 5.77 |
| \|pred−GT\| median ° | 97.77 | 4.05 |
| extrêmes | 1 | 0 |
| asymétrie \|R−L\| mean ° | 86.65 | 4.94 |

### CCD (contrôle)

- **CCD changed : NO**

## 3. Comparaison aux annotations GT

GT VAL utilisé **exclusivement** pour mesurer l'erreur finale (pixel + angles). Aucune annotation VAL n'a participé au calcul de l'offset TRAIN→VAL.

## 4. Interprétation clinique

- n=5 VAL limité statistiquement — prudence sur la généralisation.
- Amélioration géométrique vs GT ne remplace pas une validation clinique experte.
- CCD stable confirme que seul ASL_L est déplacé (landmarks fémoraux intacts).

CSV : `asl_l_refinement_train_val.csv`
