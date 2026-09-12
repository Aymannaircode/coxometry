# Analyse géométrique — refinement LOO C_asm_offset sur ASL_L

**Généré :** 2026-08-23T22:59:12.749144+00:00
**Méthode :** C_asm_offset LOO (calibrage 25 cas, test sans GT ASL_L du cas exclu)
**Post-traitement :** couche indépendante — V2 prédictions non modifiées sur disque

## Verdict : **IMPROVED**

- Distance moyenne |VCE_L − GT| : 69.36° → 8.35°
- Distance moyenne |Tönnis_L − GT| : 83.65° → 11.57°
- Asymétrie |R−L| VCE mean : 67.78° → 4.13°
- Asymétrie |R−L| Tönnis mean : 79.07° → 4.09°
- Amélioration vs GT et cohérence interne (asymétrie / comptages).

## 1. Cohérence mathématique (prédictions V2 brutes vs refined)

### VCE_L

| Stat | Brut | Refined |
|------|------|---------|
| mean | -24.96 | 40.90 |
| median | -25.13 | 41.20 |
| min | -70.61 | 35.42 |
| max | 15.41 | 48.27 |
| négatifs | 21 | 0 |
| asymétrie \|R−L\| mean | 67.78 | 4.13 |

### Tönnis_L

| Stat | Brut | Refined |
|------|------|---------|
| mean | 71.56 | -9.74 |
| median | 43.49 | -9.42 |
| min | -19.93 | -12.99 |
| max | 163.76 | -6.22 |
| négatifs | 3 | 26 |
| extrêmes | 6 | 0 |
| asymétrie \|R−L\| mean | 79.07 | 4.09 |

### CCD (contrôle — landmarks fémoraux non modifiés)

| Stat | CCD_R brut | CCD_R refined | CCD_L brut | CCD_L refined | Δ R−L brut | Δ R−L refined |
|------|------------|---------------|------------|---------------|------------|-----------------|
| mean | 131.30 | 131.30 | 138.62 | 138.62 | 8.83 | 8.83 |
| **CCD changed** | — | — | — | — | — | **NO** |

## 2. Proximité aux annotations GT (référence manuelle)

| Mesure | Mean \|pred−GT\| brut | Mean \|pred−GT\| refined |
|--------|---------------------|------------------------|
| VCE_L | 69.36 | 8.35 |
| Tonnis_L | 83.65 | 11.57 |

## 3. Interprétation clinique (descriptive, sans seuil arbitraire imposé)

- **VCE_L** et **Tönnis_L** dépendent directement de ASL_L ; le refinement déplace ces angles.
- **CCD** ne dépend pas de ASL_L — toute variation signalerait un bug de pipeline.
- Les comptages « négatif » et « extrême » Tönnis sont des indicateurs de cohérence interne, pas des diagnostics cliniques autonomes.
- La validation clinique finale requiert une revue expert indépendante des cas individuels.

## 4. Variation par cas

### Top 5 améliorations (réduction \|VCE_L−GT\| + \|Tönnis_L−GT\|)

| Cas | Gain composite ° |
|-----|------------------|
| B26_20 | 256.85 |
| B26_09 | 253.67 |
| B26_06 | 250.22 |
| B26_24 | 241.30 |
| B26_21 | 240.89 |

### Top 5 dégradations éventuelles

| Cas | Perte composite ° |
|-----|-------------------|
| — | aucune |

CSV : `v2_asl_refined_geometry_results.csv`

