# B6 — QA formel READ-ONLY des 6 corrections P0

**Généré :** 2026-08-29  
**Mode :** QA **READ-ONLY** — aucune annotation modifiée  
**Statut amont :** `P0_MOVE_COMPLETED / QA_REQUIRED`  
**Sources :** `b6_P0_move_review.csv`, `b6_working_annotations/`, `bi_ischial_annotation_guidelines.md`

---

## Périmètre

| Image | Landmark | Priorité |
|-------|----------|:--------:|
| B26_04 | IT_R | P0 |
| B26_06 | IT_L | P0 |
| B26_08 | IT_L | P0 |
| B26_09 | IT_L | P0 |
| B26_25 | IT_R | P0 |
| B26_25 | IT_L | P0 |

**Total : 6 landmarks** (corrections manuelles du 2026-08-29).

---

## Méthode QA

1. Superposition visuelle sur radiographies originales (`images/train/B26_XX.png`).
2. Vérification des 7 axes demandés :
   - tubérosité ischiatique
   - définition B1/B4 (apex caudal cortex osseux)
   - R/L
   - IT ≠ TD
   - absence de confusion fémorale
   - position dans le FOV
   - correction avant/après cohérente
3. Comparaison **avant / après** vs `b6_P0_move_review.csv`.
4. Métriques auxiliaires : intensité osseuse locale, distance TD/FSD, marge caudale FOV, asymétrie bilatérale.

**Aucune annotation, label officiel, `data.yaml`, V2/V3 modifié. Aucun training lancé.**

---

## Grille de verdict

| Verdict | Signification |
|---------|---------------|
| **PASS** | Conforme aux critères QA — prêt pour extension |
| **REVIEW** | Structure plausible mais réserve clinique / cas limite |
| **FAIL** | Non-conforme — correction insuffisante ou erreur résiduelle |

---

## Synthèse globale

| Verdict | N | % |
|---------|--:|--:|
| **PASS** | 5 | 83,3 % |
| **REVIEW** | 1 | 16,7 % |
| **FAIL** | 0 | 0 % |

| Confiance | N |
|-----------|--:|
| HIGH | 0 |
| MEDIUM | **6** |
| LOW | 0 |

### Checks structurels (6/6 critères PASS par landmark)

| Critère | OK | KO |
|---------|:--:|:--:|
| Tubérosité ischiatique (pas fémur) | **6** | 0 |
| Définition B1/B4 (apex caudal) | **6** | 0 |
| R/L correct | **6** | 0 |
| IT ≠ TD | **6** | 0 |
| Anti-fémur | **6** | 0 |
| Dans FOV (pas extrapolation) | **6** | 0 |
| Correction cohérente vs problème initial | **6** | 0 |

---

## Résultats détaillés

### B26_04 — IT_R (piège fémoral corrigé)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|:-----:|----------|
| **IT_R** | (856, 2454) → **(738, 2338)** | **PASS** | MEDIUM | Piège fémoral corrigé ; NEW sur cortex ischiatique (bone=183) |

**Vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Masse osseuse caudale latérale pelvis — distincte du fémur |
| 2 | B1/B4 | ✓ | Apex caudal cortex osseux identifiable |
| 3 | R/L | ✓ | IT_R côté droit patient (gauche image) |
| 4 | IT ≠ TD | ✓ | dy TD = +377 px (caudal et latéral) |
| 5 | Anti-fémur | ✓ | OLD sur diaphyse → NEW sur ischion ; Δx FSD = 18 px (proximité médiale au niveau y) |
| 6 | FOV | ✓ | Marge caudale 13,0 % — pas d'extrapolation |
| 7 | Correction cohérente | ✓ | Déplacement médial + repositionnement sur pelvis vs fémur |

**Réserve :** asymétrie R-L résiduelle 3,5 % (IT_L non corrigé à y=2257).

---

### B26_06 — IT_L (asymétrie majeure corrigée)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|:-----:|----------|
| **IT_L** | (1930, 2043) → **(1882, 2228)** | **PASS** | MEDIUM | Apex caudal +185 px ; asym 0,6 % |

**Vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Cortex pelvien gauche |
| 2 | B1/B4 | ✓ | Apex caudal sur bord cortical inférieur |
| 3 | R/L | ✓ | IT_L côté gauche patient (droite image) |
| 4 | IT ≠ TD | ✓ | dy TD = +436 px |
| 5 | Anti-fémur | ✓ | Δx FSD = 395 px — médial au fémur |
| 6 | FOV | ✓ | Marge caudale 8,3 % |
| 7 | Correction cohérente | ✓ | +185 px caudal vs IT_R ; asymétrie 198 px corrigée |

---

### B26_08 — IT_L (alignement vs IT_R PASS)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|:-----:|----------|
| **IT_L** | (1747, 2133) → **(1718, 2192)** | **PASS** | MEDIUM | Apex caudal +59 px ; Δy R-L = 16 px |

**Vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Contour ischiatique gauche |
| 2 | B1/B4 | ✓ | Apex caudal aligné vs IT_R PASS (2208) |
| 3 | R/L | ✓ | IT_L homolatéral correct |
| 4 | IT ≠ TD | ✓ | dy TD = +252 px |
| 5 | Anti-fémur | ✓ | Δx FSD = 353 px |
| 6 | FOV | ✓ | Marge caudale 9,5 % |
| 7 | Correction cohérente | ✓ | Caudalité corrigée vs scan +74 px initial |

---

### B26_09 — IT_L (FOV serré)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|:-----:|----------|
| **IT_L** | (2268, 2054) → **(2255, 2092)** | **PASS** | MEDIUM | Correction modeste +39 px ; FOV 6,0 % |

**Vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Cortex osseux ischion G |
| 2 | B1/B4 | ✓ | Apex caudal sur bord osseux visible |
| 3 | R/L | ✓ | IT_L homolatéral correct |
| 4 | IT ≠ TD | ✓ | dy TD = +150 px |
| 5 | Anti-fémur | ✓ | Δx FSD = 381 px |
| 6 | FOV | ✓ | Marge 6,0 % — serré mais conservateur, pas d'extrapolation |
| 7 | Correction cohérente | ✓ | Caudalité partielle corrigée ; asym 0,6 % |

---

### B26_25 — caudalité bilatérale

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|:-----:|----------|
| **IT_R** | (679, 2195) → **(665, 2245)** | **PASS** | MEDIUM | Apex caudal D (+50 px) ; bone=70 |
| **IT_L** | (2033, 2106) → **(1998, 2178)** | **REVIEW** | MEDIUM | Apex caudal G (+72 px) ; bone=26 très faible |

**IT_R — vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1–7 | Tous | ✓ | Structure ischiatique ; B1/B4 ; R/L ; IT≠TD ; anti-fémur (Δx FSD=205) ; FOV 9,1 % ; correction effective |

**IT_L — vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Courbe corticale ischion G identifiable |
| 2 | B1/B4 | ✓ | Apex caudal sur bord cortical inférieur |
| 3 | R/L | ✓ | IT_L homolatéral correct |
| 4 | IT ≠ TD | ✓ | dy TD = +331 px |
| 5 | Anti-fémur | ✓ | Δx FSD = 451 px |
| 6 | FOV | ✓ | Marge caudale 11,8 % |
| 7 | Correction cohérente | ✓ | OLD en tissus mous → NEW sur cortex (+72 px y) |

**Réserve IT_L :** intensité osseuse locale bone=26 (VERY_LOW_CONTRAST) — placement B1 plausible mais confiance limitée sans validation clinique.

---

## Conclusion

```
5/6 PASS · 1/6 REVIEW · 0/6 FAIL
→ P0_REVIEW_REQUIRED
```

Les 6 corrections répondent au problème initial (piège fémoral B26_04, caudalité insuffisante B26_06/08/09/25). Aucun FAIL structurel.

**Point bloquant :** B26_25 IT_L — contraste osseux très faible (bone=26) → **REVIEW** malgré placement cortex plausible.

**Recommandation :** revue clinique supervisée ciblée sur B26_25 IT_L avant promotion. Les 5 autres landmarks sont **PASS MEDIUM** — conformes B1/B4 pour extension working.

---

## Fichiers

| Fichier | Modifié |
|---------|:-------:|
| `b6_P0_QA.md` | **Oui** (ce document) |
| `b6_P0_QA.csv` | **Oui** |
| `b6_working_annotations/*.json` | **Non** |
| Labels YOLO / `data.yaml` / V2 / V3 | **Non** |

*Export machine : `b6_P0_QA.csv`*
