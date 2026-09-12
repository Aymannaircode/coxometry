# Validation LOO — refinement ASL_L post-V2 (new_26)

**Généré :** 2026-08-23T22:56:33.876314+00:00
**Protocole :** leave-one-out sur 26 cas — calibrage sur 25, test sans GT ASL_L du cas exclu
**Mode :** lecture seule

## Verdict LOO : **FEASIBLE**

- Meilleure méthode LOO : **Offset ASM_L global** (C_asm_offset)
- Mean LOO : 110.81 px (V2 brut : 525.40 px)
- Median LOO : 96.87 px (V2 brut : 504.43 px)
- Amélioration mean : 78.9%
- Cas >200 px : 1/26 (V2 : 26/26)
- Cas améliorés / dégradés : 26/0
- La correction reste efficace hors échantillon avec une marge suffisante pour un post-traitement déterministe.

## Synthèse par méthode

| Méthode | Mean | Median | Std | Min | Max | Δ vs V2 | Améliorés | Dégradés | >200 px |
|---------|------|--------|-----|-----|-----|---------|-----------|----------|---------|
| V2 brut | 525.40 | 504.43 | 150.78 | 214.79 | 813.76 | 0.0% | 0 | 0 | 26 |
| Translation globale dx/dy | 177.92 | 166.21 | 79.82 | 52.61 | 338.07 | 66.1% | 24 | 2 | 6 |
| Offset ASM_L global | 110.81 | 96.87 | 53.79 | 18.15 | 231.28 | 78.9% | 26 | 0 | 1 |
| Miroir ASL_R calibré | 118.66 | 115.11 | 54.65 | 19.06 | 234.02 | 77.4% | 26 | 0 | 3 |
| Géométrie sourcil (V2_ASM_L + polaire) | 111.38 | 98.74 | 55.10 | 16.96 | 232.53 | 78.8% | 26 | 0 | 1 |

## Pires 5 cas par méthode

### V2 brut

| Cas | Error LOO px | V2 brut px | Δ |
|-----|--------------|------------|---|
| B26_09 | 813.76 | 813.76 | 0.00 |
| B26_06 | 810.92 | 810.92 | 0.00 |
| B26_20 | 704.02 | 704.02 | 0.00 |
| B26_24 | 685.28 | 685.28 | 0.00 |
| B26_21 | 679.99 | 679.99 | 0.00 |

### Translation globale dx/dy

| Cas | Error LOO px | V2 brut px | Δ |
|-----|--------------|------------|---|
| B26_08 | 338.07 | 214.79 | 123.28 |
| B26_25 | 331.23 | 645.09 | -313.86 |
| B26_06 | 324.11 | 810.92 | -486.81 |
| B26_09 | 320.65 | 813.76 | -493.12 |
| B26_18 | 265.55 | 263.67 | 1.88 |

### Offset ASM_L global

| Cas | Error LOO px | V2 brut px | Δ |
|-----|--------------|------------|---|
| B26_25 | 231.28 | 645.09 | -413.80 |
| B26_07 | 193.73 | 524.94 | -331.21 |
| B26_12 | 184.14 | 670.66 | -486.52 |
| B26_14 | 178.76 | 483.92 | -305.16 |
| B26_01 | 163.57 | 481.35 | -317.78 |

### Miroir ASL_R calibré

| Cas | Error LOO px | V2 brut px | Δ |
|-----|--------------|------------|---|
| B26_12 | 234.02 | 670.66 | -436.64 |
| B26_26 | 210.37 | 441.55 | -231.18 |
| B26_25 | 209.34 | 645.09 | -435.75 |
| B26_17 | 172.99 | 346.63 | -173.64 |
| B26_07 | 171.86 | 524.94 | -353.08 |

### Géométrie sourcil (V2_ASM_L + polaire)

| Cas | Error LOO px | V2 brut px | Δ |
|-----|--------------|------------|---|
| B26_25 | 232.53 | 645.09 | -412.55 |
| B26_07 | 190.15 | 524.94 | -334.78 |
| B26_12 | 189.20 | 670.66 | -481.46 |
| B26_14 | 174.00 | 483.92 | -309.92 |
| B26_01 | 166.98 | 481.35 | -314.37 |

## Réponses aux questions clés

### 1. La correction reste-t-elle efficace hors échantillon ?

**Oui.** La meilleure méthode (Offset ASM_L global) réduit l'erreur médiane LOO de 504.43 px à 96.87 px (78.9% sur la moyenne).

### 2. Quelle méthode est la plus robuste ?

**Offset ASM_L global** (C_asm_offset) — plus faible erreur moyenne LOO (110.81 px) avec 26 cas améliorés vs 0 dégradés.

### 3. Quelle erreur moyenne/médiane obtient-elle ?

- Mean : **110.81 px**
- Median : **96.87 px**
- Std : 53.79 px

### 4. Combien de cas restent >200 px ?

- V2 brut : **26/26**
- Translation globale dx/dy : **6/26**
- Offset ASM_L global : **1/26**
- Miroir ASL_R calibré : **3/26**
- Géométrie sourcil (V2_ASM_L + polaire) : **1/26**

### 5. Peut-on intégrer la correction comme post-traitement déterministe ?

**Oui.** Paramètres calibrés sur N−1 cas, inférence basée uniquement sur landmarks V2 (ASM_L, ASL_R, FHC_R/L). Pipeline déterministe sans ré-entraînement YOLO.

### 6. Existe-t-il des cas où la correction dégrade fortement ASL_L ?

**Oui** — cas avec dégradation >50 px vs V2 brut (pire méthode learnable) :

| Cas | Méthode | V2 px | Δ dégradation |
|-----|---------|-------|---------------|
| B26_08 | B_translation | 214.79 | +123.28 |

CSV : `asl_l_refinement_loo.csv`

