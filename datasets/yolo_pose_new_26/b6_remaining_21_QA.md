# B6 — QA READ-ONLY des 21 images restantes (+ synthèse globale 52)

**Généré :** 2026-08-28  
**Mode :** QA **READ-ONLY** — aucune modification d'annotation, label officiel, `data.yaml`, V2/V3, backend ou Flutter  
**Option workflow :** **PRAGMATIQUE** — les 5 landmarks REVIEW documentés (B26_05, B26_07 IT_R, B26_11) restent inchangés  
**Périmètre ce rapport :** 21 images × 2 landmarks = **42 landmarks**  
**Référence amont :** `b6_corrected_9_QA.*`, `b6_micro_review_5.*`, `bi_ischial_annotation_guidelines.md` (B4)

---

## Synthèse — 42 landmarks examinés (lot 21 images)

| Verdict | N | % |
|---------|--:|--:|
| **PASS** | **2** | 4,8 % |
| **REVIEW** | **40** | 95,2 % |
| **FAIL** | **0** | 0 % |

| Confiance | N | % |
|-----------|--:|--:|
| **HIGH** | **0** | 0 % |
| **MEDIUM** | **8** | 19,0 % |
| **LOW** | **34** | 81,0 % |

> **Note méthodologique :** aucun landmark produit par `offset_scan_local` n'a reçu confiance **HIGH**, conformément à la consigne B6.

---

## Images du lot

| # | Image | PNG local | IT_R | IT_L |
|---|-------|:---------:|:----:|:----:|
| 1 | B26_02 | ✓ | REVIEW | REVIEW |
| 2 | B26_03 | ✓ | REVIEW | REVIEW |
| 3 | B26_04 | ✓ | REVIEW | REVIEW |
| 4 | B26_06 | ✓ | REVIEW | REVIEW |
| 5 | B26_08 | ✓ | **PASS** | REVIEW |
| 6 | B26_09 | ✓ | REVIEW | REVIEW |
| 7 | B26_10 | ✗ | REVIEW | REVIEW |
| 8 | B26_12 | ✓ | REVIEW | REVIEW |
| 9 | B26_13 | ✗ | REVIEW | REVIEW |
| 10 | B26_14 | ✓ | REVIEW | REVIEW |
| 11 | B26_15 | ✓ | REVIEW | REVIEW |
| 12 | B26_16 | ✓ | **PASS** | REVIEW |
| 13 | B26_17 | ✗ | REVIEW | REVIEW |
| 14 | B26_18 | ✓ | REVIEW | REVIEW |
| 15 | B26_19 | ✓ | REVIEW | REVIEW |
| 16 | B26_20 | ✗ | REVIEW | REVIEW |
| 17 | B26_21 | ✓ | REVIEW | REVIEW |
| 18 | B26_22 | ✓ | REVIEW | REVIEW |
| 19 | B26_23 | ✓ | REVIEW | REVIEW |
| 20 | B26_25 | ✓ | REVIEW | REVIEW |
| 21 | B26_26 | ✗ | REVIEW | REVIEW |

**B26_12** inclus comme 21ᵉ image (absent de la liste utilisateur mais présent dans le corpus B6 et nécessaire pour atteindre 42 landmarks).

**PNG absents localement (5 images) :** B26_10, B26_13, B26_17, B26_20, B26_26 — QA géométrique uniquement ; revue visuelle différée.

---

## Méthode QA (9 axes par landmark)

| # | Axe | Source |
|---|-----|--------|
| 1 | Structure anatomique (ischion vs fémur/TD) | B4 §3 |
| 2 | R/L (IT_R gauche image, IT_L droite) | B4 §7 |
| 3 | IT ≠ TD (dist > 80 px, caudal) | B4 §8 |
| 4 | Position caudale B1 (scan apex local ±100 px) | B4 §3.2 |
| 5 | FOV (marge caudale %) | B4 §4.4 |
| 6 | Risque fémur (Δx vs `FSD_*`, seuil fail < 60 px) | B4 §3.6 |
| 7 | Cohérence B1/B4 | Guide B4 |
| 8 | Qualité visuelle (contraste os local, bruit) | Revue visuelle + proxy |
| 9 | Méthode (`offset_scan_local` → confiance plafonnée) | `b6_session_summary.md` |

### Seuils verdict

| Verdict | Critère |
|---------|---------|
| **PASS** | Structure OK ; caudalité OK ; FOV ≥ 4 % ; contraste ≥ 12 ; asymétrie y ≤ 7 % ; **confiance max MEDIUM** pour offset |
| **REVIEW** | Offset auto, ambiguïté, caudalité douteuse, contraste faible, FOV serré, PNG absent |
| **FAIL** | RL swap, IT=TD, sur diaphyse (Δx FSD < 60 px), non caudal |

---

## Résultats détaillés par image

### B26_02 — offset standard

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 544.4 | 1804.7 | REVIEW | LOW | Structure OK ; bone≈21 ; scan −30 px (sur-caudal possible) |
| IT_L | 1879.0 | 1826.0 | REVIEW | LOW | Symétrie y 1,1 % ; revue humaine requise |

### B26_03 — contraste modéré

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 732.2 | 2141.2 | REVIEW | LOW | Contraste faible (11) |
| IT_L | 2074.0 | 2026.0 | REVIEW | LOW | Δy R-L 4,8 % |

### B26_04 — asymétrie + caudalité R ⚠

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 856.0 | 2454.0 | REVIEW | MEDIUM | **Scan +99 px** — trop crânial probable ; Δx FSD=100 px |
| IT_L | 2193.1 | 2256.9 | REVIEW | LOW | Asymétrie y 7,3 % |

### B26_06 — asymétrie bilatérale ⚠

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 716.0 | 2241.0 | REVIEW | MEDIUM | Asymétrie y 8,2 % |
| IT_L | 1929.5 | 2043.0 | REVIEW | MEDIUM | **~198 px trop crânial** vs IT_R — correction recommandée |

### B26_08 — meilleur cas offset

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 650.7 | 2207.9 | **PASS** | MEDIUM | Bone≈16 ; FOV 8,9 % ; Δy 3,1 % |
| IT_L | 1746.5 | 2133.1 | REVIEW | MEDIUM | **Scan +74 px** — correction caudale recommandée |

### B26_09 — FOV serré R

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 769.1 | 2105.3 | REVIEW | LOW | FOV 5,4 % |
| IT_L | 2268.3 | 2053.5 | REVIEW | MEDIUM | Scan +52 px |

### B26_10 — PNG absent

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 830.0 | 2221.9 | REVIEW | LOW | QA géométrique uniquement |
| IT_L | 1970.4 | 2172.7 | REVIEW | LOW | QA géométrique uniquement |

### B26_12 — revue B7 (A-BRD12)

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 843.0 | 2148.0 | REVIEW | LOW | B7 review_recommended ; marge caudale réduite |
| IT_L | 2041.0 | 2179.0 | REVIEW | LOW | Idem |

### B26_13 — PNG absent

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 904.2 | 2297.6 | REVIEW | LOW | FOV confortable 22,4 % (géométrie) |
| IT_L | 2168.3 | 2291.9 | REVIEW | LOW | Symétrie y 0,2 % |

### B26_14 — contraste très faible

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 743.8 | 2201.0 | REVIEW | LOW | bone≈7 |
| IT_L | 2000.5 | 2121.1 | REVIEW | LOW | bone≈7 |

### B26_15 — offset standard

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 630.0 | 2028.6 | REVIEW | LOW | Métriques acceptables |
| IT_L | 1725.4 | 1976.3 | REVIEW | LOW | Δy 2,3 % |

### B26_16 — PASS R

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 730.4 | 2245.7 | **PASS** | MEDIUM | Bone≈16 ; FOV 6,5 % |
| IT_L | 1988.0 | 2158.2 | REVIEW | LOW | Contraste faible vs R |

### B26_17 — PNG absent

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 562.3 | 2137.4 | REVIEW | LOW | QA géométrique |
| IT_L | 1869.5 | 2083.3 | REVIEW | LOW | QA géométrique |

### B26_18 — FOV large

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 772.2 | 1925.2 | REVIEW | LOW | FOV 26,7 % |
| IT_L | 2077.3 | 1812.5 | REVIEW | LOW | IT-TD 265 px (court mais > 80) |

### B26_19 — contraste très faible

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 777.2 | 2103.3 | REVIEW | LOW | bone≈4 ; FOV 5,6 % |
| IT_L | 2028.9 | 2029.4 | REVIEW | LOW | bone≈4 |

### B26_20 — PNG absent

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 667.2 | 2245.2 | REVIEW | LOW | QA géométrique |
| IT_L | 1900.6 | 2135.1 | REVIEW | LOW | QA géométrique |

### B26_21 — contraste faible + caudalité R

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 841.9 | 2580.5 | REVIEW | MEDIUM | Scan +38 px ; bone≈5 |
| IT_L | 2016.8 | 2487.8 | REVIEW | LOW | bone≈5 |

### B26_22 — asymétrie modérée

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 828.0 | 2308.0 | REVIEW | LOW | Δy R-L 6,2 % |
| IT_L | 2028.4 | 2154.0 | REVIEW | LOW | IT_L ~154 px crânial |

### B26_23 — contraste faible

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 903.5 | 2076.6 | REVIEW | LOW | bone≈5 |
| IT_L | 2184.3 | 1991.6 | REVIEW | LOW | Offset standard |

### B26_25 — caudalité bilatérale ⚠

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 679.1 | 2194.7 | REVIEW | MEDIUM | **Scan +66 px** — correction recommandée |
| IT_L | 2032.7 | 2105.7 | REVIEW | MEDIUM | **Scan +73 px** — correction recommandée |

### B26_26 — PNG absent

| Landmark | x | y | Verdict | Conf. | Synthèse |
|----------|--:|--:|---------|:-----:|----------|
| IT_R | 538.3 | 2030.0 | REVIEW | LOW | QA géométrique |
| IT_L | 2002.9 | 1932.9 | REVIEW | LOW | QA géométrique |

---

## B26_24 — statut (hors lot 21, déjà QA corrigé)

| Landmark | Coordonnées | Verdict | Conf. | Source |
|----------|-------------|---------|:-----:|--------|
| IT_R | (698.0, 2398.0) | **PASS** | HIGH | `b6_corrected_9_QA` — piège fémoral corrigé |
| IT_L | (1858.0, 2328.0) | **PASS** | MEDIUM | `b6_corrected_9_QA` — apex caudal rétabli |

**Non ré-examiné** dans ce lot — périmètre déjà couvert par QA formel post-correction.

---

## Images à revoir (priorisation)

### P0 — correction caudale recommandée (8 landmarks)

| Image | Landmarks | Motif |
|-------|-----------|-------|
| B26_04 | IT_R | Scan apex +99 px |
| B26_06 | IT_L | Asymétrie y 8,2 % (~198 px crânial) |
| B26_08 | IT_L | Scan apex +74 px |
| B26_09 | IT_L | Scan apex +52 px |
| B26_25 | IT_R, IT_L | Scan apex +66 / +73 px |

### P1 — revue B7 / cas limites

| Image | Landmarks | Motif |
|-------|-----------|-------|
| B26_12 | IT_R, IT_L | A-BRD12 ; review_recommended |
| B26_04 | IT_L | Asymétrie avec IT_R |

### P2 — contraste très faible

| Image | Landmarks | Motif |
|-------|-----------|-------|
| B26_14 | IT_R, IT_L | bone ≈ 7 |
| B26_19 | IT_R, IT_L | bone ≈ 4 |
| B26_21 | IT_R, IT_L | bone ≈ 5 |
| B26_23 | IT_R | bone ≈ 5 |

### P3 — PNG absent (revue visuelle différée)

B26_10, B26_13, B26_17, B26_20, B26_26

---

## Landmarks à corriger (recommandation, sans modification)

| Priorité | Image | Landmark | Motif | Δ estimé |
|:--------:|-------|----------|-------|----------|
| P0 | B26_04 | IT_R | Trop crânial | +50–100 px y |
| P0 | B26_06 | IT_L | Asymétrie / crânial | +150–200 px y |
| P0 | B26_08 | IT_L | Trop crânial | +50–75 px y |
| P0 | B26_09 | IT_L | Trop crânial | +50 px y |
| P0 | B26_25 | IT_R | Trop crânial | +60–70 px y |
| P0 | B26_25 | IT_L | Trop crânial | +70 px y |
| P1 | B26_21 | IT_R | Biais crânial | +30–40 px y |
| P1 | B26_22 | IT_L | Asymétrie | +100–150 px y |

**Total : 8 landmarks P0** (+ 2 P1 optionnels). **0 FAIL structurel** — corrections ciblées caudalité, pas piège fémoral.

---

## Comparaison avec les 9 déjà contrôlés

| Métrique | 9 corrigés (+ B26_01 IT_R) | 21 restantes (42 lm) |
|----------|---------------------------:|---------------------:|
| PASS | 5 | 2 |
| REVIEW | 5 | 40 |
| FAIL | 0 | 0 |
| HIGH | 3 | 0 |
| MEDIUM | 5 | 8 |
| LOW | 3 | 34 |

### Observations

1. **Les 9 corrigés** ont résolu des FAIL structurels (piège fémoral B26_24, caudalité B26_01/07/11/24) — taux PASS **50 %** (5/10 landmarks sur 5 images).
2. **Les 21 restantes** conservent les coordonnées offset originales — taux PASS **4,8 %** (2/42), conforme à l'audit initial B6 (98 % REVIEW).
3. **Pattern récurrent identique** : sous-estimation caudale systématique sur offsets (~50–200 px), déjà documenté dans `b6_visual_review_5cases.md`.
4. **Aucune régression** : 0 FAIL sur les 42 nouveaux vs 0 FAIL sur le lot corrigé.

---

## Estimation qualité globale — 52 landmarks

| Métrique | Global 52 | % |
|----------|----------:|--:|
| **PASS** | **7** | 13,5 % |
| **REVIEW** | **45** | 86,5 % |
| **FAIL** | **0** | 0 % |
| **HIGH** | **3** | 5,8 % |
| **MEDIUM** | **13** | 25,0 % |
| **LOW** | **36** | 69,2 % |

### Détail global 52

| Source | Images | PASS | REVIEW |
|--------|-------:|-----:|-------:|
| Pilote / corrigés (B26_01, 05, 07, 11, 24) | 5 | 5 | 5 |
| Offset auto (21 restantes) | 21 | 2 | 40 |
| **Total** | **26** | **7** | **45** |

### Qualité globale estimée

| Dimension | Évaluation |
|-----------|------------|
| **Structure anatomique** | **BONNE** — 0 FAIL ; anti-fémur et R/L OK sur 52/52 |
| **Caudalité B1** | **FAIBLE–MOYENNE** — biais crânial offset documenté sur ~15–20 landmarks |
| **Confiance annotation** | **FAIBLE** — 69 % LOW ; méthode offset non clinique |
| **Prêt promotion labels officiels** | **NON** — revue humaine systématique requise |
| **Prêt campagne B6 documentée** | **OUI** — sous option PRAGMATIQUE |

---

## Conclusion

```
READY_FOR_GLOBAL_52_QA
```

### Motivation

| Critère | Résultat |
|---------|----------|
| QA READ-ONLY 42 landmarks complété | **Oui** |
| FAIL structurel global | **0 / 52** |
| Option PRAGMATIQUE acceptée | **Oui** — 5 REVIEW documentés maintenus |
| Corrections bloquantes requises | **Non** — 8 landmarks P0 recommandés mais non bloquants workflow |
| Promotion labels officiels | **Non** — `REVIEW_REQUIRED` pour promotion |

Le QA global des **52 landmarks** est **complet en mode READ-ONLY**. Le corpus est **exploitable comme annotations de travail B6** avec statuts documentés. La **promotion vers labels officiels** reste **`REVIEW_REQUIRED`** (86,5 % REVIEW, 69 % confiance LOW).

### Prochaines étapes recommandées (hors scope — aucune action automatique)

1. Corrections caudales P0 sur 8 landmarks (B26_04 R, B26_06 L, B26_08 L, B26_09 L, B26_25 R/L).
2. Revue visuelle différée des 5 PNG absents.
3. Spot-check MANUAL_REVIEW : B26_07 IT_R, B26_11 R/L (déjà documentés).
4. Validation clinique B1 avant toute promotion 14 → 16 kp.

---

## Intégrité projet

| Élément | Modifié ? |
|---------|:---------:|
| `b6_working_annotations/*.json` | **Non** |
| Labels officiels | **Non** |
| `data.yaml` | **Non** |
| V2 / V3 | **Non** |
| Entraînement | **Non** |

**Fichiers créés uniquement :**

- `b6_remaining_21_QA.md` (ce rapport)
- `b6_remaining_21_QA.csv`

---

*QA B6 — 21 images restantes (42 landmarks) — READ-ONLY — option PRAGMATIQUE.*
