# B6 — QA formel READ-ONLY des 11 landmarks P1

**Généré :** 2026-08-29  
**Mode :** QA **READ-ONLY** — aucune annotation modifiée  
**Statut amont :** `P1_MANUAL_REVIEW_COMPLETED / QA_REQUIRED`  
**Sources :** `b6_P1_manual_review.csv`, `b6_working_annotations/`, `bi_ischial_annotation_guidelines.md`

---

## Périmètre

| Image | Landmark | Priorité | Revue manuelle |
|-------|----------|:--------:|----------------|
| B26_04 | IT_L | P1 | KEEP |
| B26_05 | IT_R | P1 | KEEP |
| B26_05 | IT_L | P1 | MOVE |
| B26_06 | IT_R | P1 | REVIEW |
| B26_07 | IT_R | P1 | KEEP |
| B26_11 | IT_R | P1 | REVIEW |
| B26_11 | IT_L | P1 | KEEP |
| B26_12 | IT_R | P1 | MOVE |
| B26_12 | IT_L | P1 | MOVE |
| B26_21 | IT_R | P1 | REVIEW |
| B26_22 | IT_L | P1 | MOVE |

**Total : 11 landmarks** (revue manuelle P1 du 2026-08-29).

---

## Méthode QA

1. Superposition visuelle sur radiographies originales (`images/train/B26_XX.png`).
2. Vérification des **9 axes** demandés :
   - tubérosité ischiatique
   - définition B1/B4 (apex caudal cortex osseux)
   - R/L
   - IT ≠ TD
   - absence de confusion fémorale
   - position dans le FOV
   - position caudale
   - cohérence avant/après vs `b6_P1_manual_review.csv`
   - qualité visuelle
3. Métriques auxiliaires : intensité osseuse locale (`bone`), distance TD/FSD, marge caudale FOV, asymétrie bilatérale, scan caudal local (±40 px bande latérale).
4. Croisement avec statuts revue manuelle et ambiguïtés documentées (`A-FOV05`, `A-GAS07`, `A-ROT11`, `A-BRD12`).

**Aucune annotation, label officiel, `data.yaml`, V2/V3 modifié. Aucun training lancé.**

---

## Grille de verdict

| Verdict | Signification |
|---------|---------------|
| **PASS** | Conforme aux critères QA — prêt pour extension working |
| **REVIEW** | Structure plausible mais réserve clinique / cas limite |
| **FAIL** | Non-conforme — correction insuffisante ou erreur résiduelle |

---

## Synthèse globale

| Verdict | N | % |
|---------|--:|--:|
| **PASS** | 4 | 36,4 % |
| **REVIEW** | 7 | 63,6 % |
| **FAIL** | 0 | 0 % |

| Confiance | N |
|-----------|--:|
| HIGH | 0 |
| MEDIUM | **7** |
| LOW | **4** |

### Checks structurels (11 landmarks × 9 critères)

| Critère | OK | REVIEW | FAIL |
|---------|:--:|:------:|:----:|
| Tubérosité ischiatique | **8** | **3** | 0 |
| Définition B1/B4 (apex caudal) | **5** | **6** | 0 |
| R/L correct | **11** | 0 | 0 |
| IT ≠ TD | **11** | 0 | 0 |
| Anti-fémur | **11** | 0 | 0 |
| Dans FOV (pas extrapolation) | **9** | **2** | 0 |
| Position caudale | **5** | **6** | 0 |
| Cohérence avant/après | **11** | 0 | 0 |
| Qualité visuelle | **6** | **4** | **1** |

---

## Cas d'attention particulière

### B26_06 — IT_R

| Champ | Valeur |
|-------|--------|
| Coordonnées | **(716, 2241)** — inchangé P1 |
| Verdict | **REVIEW** · **LOW** |
| Problème | Contraste local insuffisant — apex caudal ischion D non tranchable |
| Scan caudal | +87 px sous IT (non confirmé visuellement comme ischion) |
| bone | 150 (modéré) — ne compense pas l'ambiguïté B1 |

**Action :** validation clinique ou **`v=0`** si apex caudal non défendable.

---

### B26_11 — IT_R

| Champ | Valeur |
|-------|--------|
| Coordonnées | **(632, 2498)** — inchangé P1 |
| Verdict | **REVIEW** · **LOW** |
| Problème | Rotation pelvienne (A-ROT11) + contraste osseux très faible |
| bone | **28** (VERY_LOW_CONTRAST) — qualité visuelle **FAIL** |
| IT_L homolatéral | KEEP MEDIUM — repère G plus net (bone=32) |

**Action :** candidat **`v=0`** prioritaire ; revue clinique rotation + contraste.

---

### B26_21 — IT_R

| Champ | Valeur |
|-------|--------|
| Coordonnées | **(842, 2581)** — inchangé P1 |
| Verdict | **REVIEW** · **LOW** |
| Problème | Contour caudal indéterminable ; scan +149 px non validé |
| bone | 101 (modéré) |
| Asymétrie | 3,6 % vs IT_L |

**Action :** validation clinique B1 ; envisager repositionnement caudal ou **`v=0`**.

---

### B26_05 — IT_R + IT_L (PARTIAL bilatéral)

| Landmark | Avant → Après | Verdict | Conf. |
|----------|---------------|---------|:-----:|
| **IT_R** | (648, 2955) → **(648, 2955)** | **REVIEW** | MEDIUM |
| **IT_L** | (2395, 2958) → **(2412, 2960)** | **REVIEW** | MEDIUM |

**Contexte :** seul cas PARTIAL bilatéral du corpus (B7). Marge FOV **1,6–1,8 %** — la plus serrée du lot.

| # | Critère | IT_R | IT_L |
|---|---------|:----:|:----:|
| 1 | Tubérosité ischiatique | ✓ | ✓ |
| 2 | B1/B4 | △ | △ |
| 3 | R/L | ✓ | ✓ |
| 4 | IT ≠ TD | ✓ | ✓ |
| 5 | Anti-fémur | ✓ | ✓ |
| 6 | FOV | △ | △ |
| 7 | Cohérence correction | ✓ (KEEP) | ✓ (+17 px x) |

**Réserve :** ambiguïté apex caudal A-FOV05 persiste (~47–52 px scan caudal vs bord image). **`v=2` et `v=0` bilatéraux restent défendables** (§9.2 guidelines).

**Action :** session supervisée obligatoire ; trancher `v=2` vs `v=0` avec validateur clinique.

---

### B26_07 — IT_R (gaz intestinal)

| Landmark | Coordonnées | Verdict | Conf. |
|----------|-------------|---------|:-----:|
| **IT_R** | **(708, 2548)** | **REVIEW** | MEDIUM |

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Cortex ischion D latéral au gaz |
| 2 | B1/B4 | △ | Apex caudal repéré mais scan +138 px (risque fémur) |
| 3 | R/L | ✓ | IT_R côté droit patient |
| 4 | IT ≠ TD | ✓ | dy TD = +407 px |
| 5 | Anti-fémur | ✓ | Δx FSD = 275 px |
| 6 | FOV | ✓ | Marge 5,2 % |
| 7 | Cohérence | ✓ | KEEP cohérent avec revue manuelle |
| 8 | Qualité | △ | bone=72 ; gaz central A-GAS07 |

**Action :** confirmer repère caudal indépendamment du gaz ; valider symétrie y parfaite IT_R=IT_L (0 %).

---

### B26_12 — IT_R + IT_L (bord FOV)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|:-----:|----------|
| **IT_R** | (843, 2148) → **(846, 2198)** | **PASS** | MEDIUM | +50 px caudal ; marge FOV 9,8 % |
| **IT_L** | (2041, 2179) → **(2038, 2210)** | **PASS** | MEDIUM | +31 px caudal ; marge FOV 9,3 % |

**Vérifications communes :**

| # | Critère | Résultat |
|---|---------|:--------:|
| 1–5 | Structure, B1/B4, R/L, IT≠TD, anti-fémur | ✓ |
| 6 | FOV | ✓ (marge ~9–10 % post-correction) |
| 7 | Correction P1 | ✓ — repositionnement caudal effectif |
| 8 | Qualité | ✓ — bone=144/153 |

**Réserve :** validation clinique seuil VISIBLE → `v=2` recommandée (§9.3 guidelines) — non bloquante QA.

---

## Résultats détaillés — autres landmarks

### B26_04 — IT_L

| Landmark | Coordonnées | Verdict | Conf. |
|----------|-------------|---------|:-----:|
| **IT_L** | **(2193, 2257)** | **PASS** | MEDIUM |

Conservé sans déplacement. Apex caudal ischion G sur bord cortical (bone=97). Asymétrie y vs IT_R = 3,5 % documentée — pas de symétrie miroir.

---

### B26_11 — IT_L

| Landmark | Coordonnées | Verdict | Conf. |
|----------|-------------|---------|:-----:|
| **IT_L** | **(1958, 2495)** | **REVIEW** | MEDIUM |

Apex caudal ischion G identifiable sur bord diagonal malgré rotation. Contraste faible (bone=32) — validation clinique recommandée. Asymétrie vs IT_R = 0,1 %.

---

### B26_22 — IT_L

| Landmark | Avant → Après | Verdict | Conf. |
|----------|---------------|---------|:-----:|
| **IT_L** | (2028, 2154) → **(2024, 2238)** | **PASS** | MEDIUM |

Correction P1 majeure (+84 px caudal). Apex ischion G sur bord cortical inférieur ; os pelvien confirmé (bone=125). Asymétrie y 3,0 % vs IT_R — acceptable sans miroir.

---

## Points à corriger

| # | Image | Landmark | Action recommandée |
|---|-------|----------|-------------------|
| 1 | B26_06 | IT_R | Apex caudal indéterminable → **`v=0`** ou repositionnement après validation clinique |
| 2 | B26_11 | IT_R | Contraste très faible (bone=28) → candidat **`v=0`** prioritaire |
| 3 | B26_21 | IT_R | Contour caudal incertain (+149 px scan) → validation ou **`v=0`** |
| 4 | B26_05 | IT_R, IT_L | Trancher **`v=2` vs `v=0`** en session supervisée (PARTIAL bilatéral) |
| 5 | B26_07 | IT_R | Confirmer apex caudal sous gaz intestinal A-GAS07 |

---

## Points à validation clinique

| # | Sujet | Landmarks concernés |
|---|-------|----------------------|
| 1 | Définition B1 — point caudal vs cortical vs sommet | B26_06, B26_11 IT_R, B26_21 |
| 2 | Seuil PARTIAL → `v=2` vs `v=0` (§5.3) | B26_05 IT_R, IT_L |
| 3 | Seuil marge FOV opérationnel (§4.4) | B26_05, B26_12 |
| 4 | Contraste osseux minimal acceptable pour `v=2` | B26_11 IT_R (bone=28), B26_11 IT_L (bone=32) |
| 5 | Rotation pelvienne — cohérence R/L indépendante | B26_11 |
| 6 | Gaz intestinal — repère latéral fiable | B26_07 IT_R |
| 7 | Seuil VISIBLE → `v=2` marge caudale réduite | B26_12 IT_R, IT_L |

---

## Conclusion

```
4/11 PASS · 7/11 REVIEW · 0/11 FAIL
→ P1_QA_REVIEW
```

Les 4 corrections P1 (B26_05 IT_L, B26_12 bilatéral, B26_22 IT_L) sont **structurellement cohérentes** et répondent au problème initial (soft-tissue, caudalité insuffisante). Aucun **FAIL** structurel (piège fémoral, inversion R/L, substitution TD).

**Points bloquants QA :**

1. **B26_11 IT_R** — contraste osseux très faible (bone=28) — cas le plus fragile du lot.
2. **B26_05 bilatéral** — PARTIAL FOV unique du corpus — `v=2` non tranchable sans validateur.
3. **B26_06 IT_R, B26_21 IT_R** — apex caudal B1 non défendable visuellement → candidats `v=0`.

**Recommandation :** session de validation clinique ciblée sur les 7 landmarks REVIEW avant promotion working → officiel. Les 4 landmarks PASS MEDIUM (B26_04, B26_12×2, B26_22) sont conformes B1/B4 pour extension working sous réserve validation B1 globale.

---

## Fichiers

| Fichier | Modifié |
|---------|:-------:|
| `b6_P1_QA.md` | **Oui** (ce document) |
| `b6_P1_QA.csv` | **Oui** |
| `b6_working_annotations/*.json` | **Non** |
| Labels YOLO / `data.yaml` / V2 / V3 | **Non** |

*Export machine : `b6_P1_QA.csv`*
