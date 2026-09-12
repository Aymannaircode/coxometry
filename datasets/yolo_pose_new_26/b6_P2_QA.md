# B6 — QA formel READ-ONLY des 18 landmarks P2

**Généré :** 2026-08-29  
**Mode :** QA **READ-ONLY** — aucune annotation modifiée  
**Statut amont :** `P2_MANUAL_REVIEW_COMPLETED / QA_REQUIRED`  
**Sources :** `b6_P2_manual_review.csv`, `b6_working_annotations/`, `bi_ischial_annotation_guidelines.md`

---

## Périmètre

| Image | Landmark | Priorité | Revue manuelle |
|-------|----------|:--------:|----------------|
| B26_02 | IT_R | P2 | MOVE |
| B26_02 | IT_L | P2 | KEEP |
| B26_03 | IT_R | P2 | MOVE |
| B26_03 | IT_L | P2 | MOVE |
| B26_09 | IT_R | P2 | MOVE |
| B26_14 | IT_R | P2 | REVIEW |
| B26_14 | IT_L | P2 | MOVE |
| B26_15 | IT_R | P2 | REVIEW |
| B26_15 | IT_L | P2 | REVIEW |
| B26_16 | IT_L | P2 | MOVE |
| B26_18 | IT_R | P2 | KEEP |
| B26_18 | IT_L | P2 | MOVE |
| B26_19 | IT_R | P2 | MOVE |
| B26_19 | IT_L | P2 | REVIEW |
| B26_21 | IT_L | P2 | MOVE |
| B26_22 | IT_R | P2 | KEEP |
| B26_23 | IT_R | P2 | MOVE |
| B26_23 | IT_L | P2 | MOVE |

**Total : 18 landmarks** (revue manuelle P2 du 2026-08-29).

---

## Méthode QA

1. Superposition visuelle sur radiographies originales (`images/train/B26_XX.png`).
2. Vérification des **10 axes** demandés :
   - tubérosité ischiatique
   - définition B1/B4 (apex caudal cortex osseux)
   - R/L
   - IT ≠ TD
   - absence de confusion fémorale
   - position dans le FOV
   - position caudale/inférieure identifiable
   - cohérence du déplacement manuel si MOVE
   - qualité visuelle
   - cohérence avant/après vs `b6_P2_manual_review.csv`
3. Métriques auxiliaires : intensité osseuse locale (`bone`), distance TD/FSD, marge caudale FOV, asymétrie bilatérale.
4. **Vérification spécifique des 11 MOVE** : superposition OLD (rouge) / NEW (vert) — confirmation placement sur cortex caudal ischiatique et non autre structure.

**Aucune annotation, label officiel, JSON, `data.yaml`, V2/V3 modifié. Aucun training lancé.**

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
| **PASS** | 9 | 50,0 % |
| **REVIEW** | 9 | 50,0 % |
| **FAIL** | 0 | 0 % |

| Confiance | N |
|-----------|--:|
| HIGH | 0 |
| MEDIUM | **14** |
| LOW | **4** |

### Checks structurels (18 landmarks × 10 critères)

| Critère | PASS | REVIEW | FAIL |
|---------|:----:|:------:|:----:|
| Tubérosité ischiatique | **14** | **4** | 0 |
| Définition B1/B4 (apex caudal) | **9** | **9** | 0 |
| R/L correct | **18** | 0 | 0 |
| IT ≠ TD | **18** | 0 | 0 |
| Anti-fémur | **18** | 0 | 0 |
| Dans FOV (pas extrapolation) | **15** | **3** | 0 |
| Position caudale | **12** | **6** | 0 |
| Correction MOVE cohérente | **11** | 0 | 0 |
| Qualité visuelle | **9** | **5** | **4** |
| Cohérence avant/après | **18** | 0 | 0 |

---

## Vérification spécifique des 11 MOVE

| # | Image | Landmark | Avant → Après | MOVE sur cortex caudal ? | Verdict MOVE | Conf. |
|---|-------|----------|---------------|:------------------------:|:------------:|:-----:|
| 1 | B26_02 | IT_R | (544, 1805) → **(552, 1838)** | ✓ courbe caudale ischion D | **PASS** | MEDIUM |
| 2 | B26_03 | IT_R | (732, 2141) → **(718, 2188)** | ✓ bord cortical vertical ischion D | **PASS** | MEDIUM |
| 3 | B26_03 | IT_L | (2074, 2026) → **(2068, 2068)** | △ caudal plausible, grain élevé | **REVIEW** | MEDIUM |
| 4 | B26_09 | IT_R | (769, 2105) → **(778, 2138)** | △ caudal in-FOV ; marge 3,9 % | **REVIEW** | MEDIUM |
| 5 | B26_14 | IT_L | (2000, 2121) → **(1994, 2158)** | △ direction caudale ; bone≈53 | **REVIEW** | MEDIUM |
| 6 | B26_16 | IT_L | (1988, 2158) → **(1978, 2198)** | ✓ bord caudal cortical sharp | **PASS** | MEDIUM |
| 7 | B26_18 | IT_L | (2077, 1812) → **(2072, 1848)** | △ caudal ; contraste modéré | **REVIEW** | MEDIUM |
| 8 | B26_19 | IT_R | (777, 2103) → **(768, 2138)** | △ soft-tissue → cortex ; FOV 4,0 % | **REVIEW** | MEDIUM |
| 9 | B26_21 | IT_L | (2017, 2488) → **(2012, 2518)** | ✓ bord caudal courbe ischion G | **PASS** | MEDIUM |
| 10 | B26_23 | IT_R | (903, 2077) → **(892, 2108)** | ✓ gap soft-tissue → cortex ischion D | **PASS** | MEDIUM |
| 11 | B26_23 | IT_L | (2184, 1992) → **(2178, 2018)** | ✓ courbe corticale inférieure G | **PASS** | MEDIUM |

**Synthèse MOVE : 6/11 PASS · 5/11 REVIEW · 0/11 FAIL**

Aucun MOVE n'a placé le repère sur le fémur, le teardrop ou une structure non ischiatique. Les 5 REVIEW concernent principalement le contraste faible ou le FOV serré post-déplacement, pas une erreur de structure cible.

---

## Cas d'attention particulière

### B26_14 — IT_R (candidat v=0)

| Champ | Valeur |
|-------|--------|
| Coordonnées | **(744, 2201)** — inchangé (REVIEW P2) |
| Verdict | **REVIEW** · **LOW** |
| bone | **44** (VERY_LOW_CONTRAST) |
| Problème | Structure ischion D non confirmable — repère en zone sombre adjacente fémur |

**Action :** validation clinique ou **`v=0`** prioritaire.

---

### B26_15 — IT_R + IT_L (contraste faible bilatéral)

| Landmark | Coordonnées | Verdict | Conf. | bone |
|----------|-------------|---------|:-----:|-----:|
| **IT_R** | (630, 2029) | **REVIEW** | LOW | 95 |
| **IT_L** | (1725, 1976) | **REVIEW** | LOW | 62 |

**Problème :** bord osseux caudal non net identifiable — repères en zone grainy / soft-tissue.

**Action :** **`v=0`** bilatéral défendable ; ne pas forcer `v=2` sans validation radiologique.

---

### B26_19 — IT_L (candidat v=0)

| Champ | Valeur |
|-------|--------|
| Coordonnées | **(2029, 2029)** — inchangé (REVIEW P2) |
| Verdict | **REVIEW** · **LOW** |
| bone | **73** |
| Problème | Vallée soft-tissue entre bords osseux — contraste extrêmement faible |

**Action :** validation clinique ou **`v=0`**.

*Note : B26_19 IT_R (MOVE) → REVIEW MEDIUM — déplacement soft-tissue → cortex validé visuellement mais FOV 4,0 %.*

---

## Résultats détaillés — KEEP (3 landmarks)

### B26_02 — IT_L

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1–10 | Tous | ✓ | Apex caudal ischion G ; bone=143 ; asym 0,7 % |

**Verdict : PASS · MEDIUM**

---

### B26_18 — IT_R

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1–8, 10 | | ✓ | Bord médial ischion D ; anti-fémur OK |
| 9 | Qualité | ✓ | bone=92 modéré ; FOV 26,7 % |

**Verdict : PASS · MEDIUM**

---

### B26_22 — IT_R

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1–8, 10 | | ✓ | Contour ischion D médial fémur |
| 6 | FOV | △ | Marge 6,6 % — acceptable |
| 9 | Qualité | ✓ | bone=149 bon |

**Verdict : PASS · MEDIUM** (asym 3,0 % vs IT_L P1 notée)

---

## Points à corriger

| # | Image | Landmark | Action recommandée |
|---|-------|----------|-------------------|
| 1 | B26_14 | IT_R | **`v=0`** ou validation clinique — structure non confirmable |
| 2 | B26_15 | IT_R | **`v=0`** — bord osseux absent |
| 3 | B26_15 | IT_L | **`v=0`** — apex caudal indéterminable |
| 4 | B26_19 | IT_L | **`v=0`** — vallée soft-tissue |
| 5 | B26_09 | IT_R | Valider apex in-FOV marge 3,9 % post-MOVE |
| 6 | B26_14 | IT_L | Valider MOVE malgré contraste faible (bone≈53) |
| 7 | B26_03 | IT_L | Confirmer apex caudal post-MOVE (grain élevé) |
| 8 | B26_18 | IT_L | Confirmer apex caudal post-MOVE |
| 9 | B26_19 | IT_R | Valider MOVE FOV 4,0 % |

---

## Points nécessitant validation clinique

| # | Sujet | Landmarks concernés |
|---|-------|----------------------|
| 1 | Candidats **`v=0`** — contraste extrêmement faible | B26_14 IT_R, B26_15 IT_R/L, B26_19 IT_L |
| 2 | Seuil FOV serré post-MOVE (§4.4) | B26_09 IT_R (3,9 %), B26_19 IT_R (4,0 %) |
| 3 | MOVE validés mais contraste limite | B26_14 IT_L, B26_03 IT_L, B26_18 IT_L |
| 4 | Définition B1 — cortical vs sommet sur grain élevé | B26_03 IT_L, B26_14 IT_L |
| 5 | IT≠TD distance courte | B26_18 IT_L (289 px) — confirmé visuellement mais réserve |

---

## Conclusion

```
9/18 PASS · 9/18 REVIEW · 0/18 FAIL
→ P2_QA_REVIEW
```

Les **6 MOVE PASS** (B26_02 IT_R, B26_03 IT_R, B26_16 IT_L, B26_21 IT_L, B26_23 IT_R/L) placent le repère sur le **cortex caudal ischiatique** identifiable — correction offset/soft-tissue effective. Les **5 MOVE REVIEW** sont structurellement cohérents mais limités par contraste ou FOV serré.

**Points bloquants QA :**

1. **4 landmarks REVIEW LOW** — B26_14 IT_R, B26_15 bilatéral, B26_19 IT_L — candidats **`v=0`** prioritaires.
2. **Aucun FAIL** — R/L, IT≠TD, anti-fémur : **18/18 OK**.
3. **50 % REVIEW** — principalement contraste faible et FOV serré, pas erreur structurelle systématique.

**Recommandation :** session validation clinique ciblée sur les 4 candidats v=0 et les 5 MOVE REVIEW avant promotion working → officiel. Les 9 landmarks PASS MEDIUM sont conformes B1/B4 pour extension working sous réserve validation B1 globale.

---

## Fichiers

| Fichier | Modifié |
|---------|:-------:|
| `b6_P2_QA.md` | **Oui** (ce document) |
| `b6_P2_QA.csv` | **Oui** |
| `b6_working_annotations/*.json` | **Non** |
| Labels YOLO / `data.yaml` / V2 / V3 | **Non** |

*Export machine : `b6_P2_QA.csv`*
