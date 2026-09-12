# B6 — QA formel READ-ONLY session IMAGE_REQUIRED (10 landmarks)

**Généré :** 2026-08-29  
**Mode :** QA **READ-ONLY** — aucune annotation modifiée  
**Statut amont :** `IMAGE_REQUIRED_REVIEW_COMPLETED / QA_REQUIRED`  
**Sources :** `b6_image_required_manual_review.csv`, `b6_working_annotations/`, `bi_ischial_annotation_guidelines.md`

---

## Périmètre

| Image | Landmark | Priorité | Statut manuel |
|-------|----------|:--------:|:-------------:|
| B26_10 | IT_R | P0_IMAGE_REQUIRED | MOVE |
| B26_10 | IT_L | P0_IMAGE_REQUIRED | MOVE |
| B26_13 | IT_R | P0_IMAGE_REQUIRED | MOVE |
| B26_13 | IT_L | P0_IMAGE_REQUIRED | KEEP |
| B26_17 | IT_R | P0_IMAGE_REQUIRED | MOVE |
| B26_17 | IT_L | P0_IMAGE_REQUIRED | MOVE |
| B26_20 | IT_R | P0_IMAGE_REQUIRED | MOVE |
| B26_20 | IT_L | P0_IMAGE_REQUIRED | MOVE |
| B26_26 | IT_R | P0_IMAGE_REQUIRED | MOVE (LOW) |
| B26_26 | IT_L | P0_IMAGE_REQUIRED | MOVE |

**Total : 10 landmarks** (5 images val — PNG originaux confirmés).

---

## Méthode QA

1. Superposition visuelle sur radiographies originales (`images/val/B26_XX.png`).
2. Vérification des **9 axes** demandés :
   - tubérosité ischiatique
   - définition B1/B4 (apex caudal cortex osseux)
   - R/L
   - IT ≠ TD
   - absence de confusion fémorale
   - position dans le FOV
   - apex caudal/inférieur identifiable
   - cohérence avec correction manuelle IMAGE_REQUIRED
   - qualité de l'image
3. Comparaison coordonnées courantes vs `b6_image_required_manual_review.csv`.
4. Métriques auxiliaires : distance TD/FSD, marge caudale FOV, asymétrie bilatérale y.

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
| **PASS** | **8** | 80 % |
| **REVIEW** | **2** | 20 % |
| **FAIL** | **0** | 0 % |

| Confiance | N |
|-----------|--:|
| HIGH | **0** |
| MEDIUM | **9** |
| LOW | **1** |

### Checks structurels (10 landmarks × 9 critères)

| Critère | PASS | REVIEW | FAIL |
|---------|:----:|:------:|:----:|
| 1. Tubérosité ischiatique | **10** | 0 | 0 |
| 2. Définition B1/B4 | **9** | **1** | 0 |
| 3. R/L correct | **10** | 0 | 0 |
| 4. IT ≠ TD | **10** | 0 | 0 |
| 5. Anti-fémur | **10** | 0 | 0 |
| 6. Dans FOV | **10** | 0 | 0 |
| 7. Apex caudal identifiable | **9** | **1** | 0 |
| 8. Correction manuelle cohérente | **10** | 0 | 0 |
| 9. Qualité image | **9** | **1** | 0 |

---

## Résultats détaillés

### B26_10 — IT_R / IT_L

| Landmark | Coordonnées | Avant → Après | Verdict | Conf. |
|----------|-------------|---------------|---------|:-----:|
| **IT_R** | (822, 2258) | (830, 2222) → (822, 2258) | **PASS** | MEDIUM |
| **IT_L** | (1975, 2210) | (1970, 2173) → (1975, 2210) | **PASS** | MEDIUM |

**Vérifications communes :** structure ischiatique ✓ · B1/B4 apex caudal ✓ · R/L ✓ · IT≠TD (dist > 455 px) ✓ · anti-fémur (Δx FSD R=206 / L=366 px) ✓ · FOV 14–16 % ✓ · corrections +36/+37 px y cohérentes ✓ · qualité acceptable ✓

**Asymétrie bilatérale :** Δy = 48 px (1,8 %) — acceptable.

---

### B26_13 — IT_R / IT_L

| Landmark | Coordonnées | Avant → Après | Verdict | Conf. |
|----------|-------------|---------------|---------|:-----:|
| **IT_R** | (892, 2342) | (904, 2298) → (892, 2342) | **PASS** | MEDIUM |
| **IT_L** | (2168, 2292) | conservé (KEEP) | **PASS** | MEDIUM |

**IT_R :** correction caudale +44 px effective ; FOV confortable 20,9 % ; anti-fémur Δx FSD = 185 px.

**IT_L (KEEP) :** placement initial validé — bord caudal ischion G atteint ; symétrie y 50 px (1,7 %).

---

### B26_17 — IT_R / IT_L

| Landmark | Coordonnées | Avant → Après | Verdict | Conf. |
|----------|-------------|---------------|---------|:-----:|
| **IT_R** | (518, 2190) | (562, 2137) → (518, 2190) | **PASS** | MEDIUM |
| **IT_L** | (1820, 2155) | (1870, 2083) → (1820, 2155) | **PASS** | MEDIUM |

**IT_R :** cas FOV serré (marge 10,3 %) — bord diagonal caudal net, pas d'extrapolation. Correction médio-caudale (−44 x, +53 y) cohérente.

**IT_L :** apex caudal +72 px y ; asym R-L 35 px (1,4 %).

---

### B26_20 — IT_R / IT_L

| Landmark | Coordonnées | Avant → Après | Verdict | Conf. |
|----------|-------------|---------------|---------|:-----:|
| **IT_R** | (688, 2208) | (667, 2245) → (688, 2208) | **PASS** | MEDIUM |
| **IT_L** | (1888, 2188) | (1901, 2135) → (1888, 2188) | **PASS** | MEDIUM |

**IT_R :** correction remontée depuis zone soft-tissue (−37 px y) — cortex ischiatique caudal confirmé visuellement.

**IT_L :** apex caudal +53 px y ; cohérence bilatérale excellente post-correction (Δy R-L = 20 px, 0,8 %).

---

### B26_26 — IT_R / IT_L ⚠ cas critique

| Landmark | Coordonnées | Avant → Après | Verdict | Conf. |
|----------|-------------|---------------|---------|:-----:|
| **IT_R** | (552, 2088) | (538, 2030) → (552, 2088) | **REVIEW** | **LOW** |
| **IT_L** | (1998, 1998) | (2003, 1933) → (1998, 1998) | **REVIEW** | MEDIUM |

**IT_R — vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Masse pelvienne caudale latérale — pas fémur |
| 2 | B1/B4 | **~** | Apex caudal repéré mais **non tranchable** avec certitude (bruit local) |
| 3 | R/L | ✓ | IT_R côté droit patient (gauche image) |
| 4 | IT ≠ TD | ✓ | dy TD = +360 px |
| 5 | Anti-fémur | ✓ | Δx FSD = 205 px — médial au fémur |
| 6 | FOV | ✓ | Marge caudale 13,9 % |
| 7 | Apex caudal | **~** | Bord osseux visible mais contraste insuffisant pour validation définitive |
| 8 | Correction cohérente | ✓ | +58 px y vs offset initial — direction correcte |
| 9 | Qualité image | **~** | Contraste/bruit local élevé ; `review_recommended` + ambiguïté A-IMGREQ |

**IT_L — vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1–6, 8–9 | Structure/R/L/IT≠TD/anti-fémur/FOV/correction/qualité | ✓ | Placement individuel sur cortex pelvien G plausible |
| 7 | Apex caudal | ✓ | Bord inférieur identifiable |
| — | Cohérence bilatérale | **~** | Asymétrie y = 90 px (3,7 %) vs IT_R incertain |

**Réserve B26_26 :** point bloquant = **IT_R LOW** — validation clinique supervisée requise avant promotion. IT_L conditionnel à l'arbitrage IT_R.

---

## Landmarks nécessitant une nouvelle correction

| Image | Landmark | Verdict QA | Action recommandée |
|-------|----------|:----------:|-------------------|
| **B26_26** | **IT_R** | REVIEW LOW | **Re-correction supervisée** — confirmer ou ajuster apex caudal sous contraste faible |
| **B26_26** | **IT_L** | REVIEW MEDIUM | Re-valider asymétrie bilatérale **après** arbitrage IT_R ; correction seule si IT_R confirmé |

**Aucun FAIL structurel** — les 8 autres landmarks ne nécessitent pas de re-correction.

---

## Décision session

```
8/10 PASS · 2/10 REVIEW · 0/10 FAIL
→ IMAGE_REQUIRED_QA_REVIEW
```

Les corrections IMAGE_REQUIRED répondent globalement au problème initial (offsets non validés visuellement). Huit landmarks conformes B1/B4 pour extension working (confiance MEDIUM).

**Point bloquant :** B26_26 IT_R — contraste/bruit local, confiance LOW → **REVIEW** malgré placement cortex plausible.

**Recommandation :** revue clinique supervisée ciblée sur **B26_26 IT_R** (puis IT_L si asymétrie persistante) avant clôture définitive session IMAGE_REQUIRED.

---

## Fichiers

| Fichier | Modifié |
|---------|:-------:|
| `b6_image_required_QA.md` | **Oui** (ce document) |
| `b6_image_required_QA.csv` | **Oui** |
| `b6_working_annotations/*.json` | **Non** |
| Labels YOLO / `data.yaml` / V2 / V3 | **Non** |

*Export machine : `b6_image_required_QA.csv`*
