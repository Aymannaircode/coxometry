# B6 — Revue manuelle visuelle P2 (18 landmarks)

**Généré :** 2026-08-29  
**Session :** P2 — revue visuelle offset / contraste faible  
**Statut :** `P2_MANUAL_REVIEW_COMPLETED / QA_REQUIRED`  
**Guide appliqué :** `bi_ischial_annotation_guidelines.md` (B1/B4)  
**Source queue :** `b6_full_manual_review_queue.csv` (priorité P2 uniquement)  
**Source PNG :** `datasets/yolo_pose_new_26/images/train/B26_XX.png` (originaux pleine résolution)  
**Modifications :** `b6_working_annotations/` uniquement (9 fichiers JSON, 11 landmarks MOVE)

---

## Périmètre

| # | Image | Landmark | Priorité | Statut revue |
|--:|-------|----------|:--------:|:------------:|
| 1 | B26_02 | IT_R | P2 | MOVE |
| 2 | B26_02 | IT_L | P2 | KEEP |
| 3 | B26_03 | IT_R | P2 | MOVE |
| 4 | B26_03 | IT_L | P2 | MOVE |
| 5 | B26_09 | IT_R | P2 | MOVE |
| 6 | B26_14 | IT_R | P2 | REVIEW |
| 7 | B26_14 | IT_L | P2 | MOVE |
| 8 | B26_15 | IT_R | P2 | REVIEW |
| 9 | B26_15 | IT_L | P2 | REVIEW |
| 10 | B26_16 | IT_L | P2 | MOVE |
| 11 | B26_18 | IT_R | P2 | KEEP |
| 12 | B26_18 | IT_L | P2 | MOVE |
| 13 | B26_19 | IT_R | P2 | MOVE |
| 14 | B26_19 | IT_L | P2 | REVIEW |
| 15 | B26_21 | IT_L | P2 | MOVE |
| 16 | B26_22 | IT_R | P2 | KEEP |
| 17 | B26_23 | IT_R | P2 | MOVE |
| 18 | B26_23 | IT_L | P2 | MOVE |

**Total : 18 landmarks** sur 11 images train.  
**Hors scope respecté :** labels YOLO officiels, `data.yaml`, V2, V3, backend, Flutter — **non modifiés**. Aucun training lancé. Aucun P0/P1/P3/IMAGE_REQUIRED traité.

---

## Méthode

1. Chargement radiographies **PNG originales** à pleine résolution.
2. Zoom local sur chaque tubérosité ischiatique (crops pelvis + zoom contrasté).
3. Revue visuelle selon **B1/B4** — **aucune coordonnée calculée automatiquement** ; **aucune symétrie** ; **aucun offset** ; **aucune extrapolation**.
4. Vérifications systématiques par point :
   - identification tubérosité ischiatique ;
   - placement apex caudal/inférieur identifiable ;
   - R/L patient ;
   - IT ≠ TD ;
   - anti-fémur (§3.6 B4) ;
   - FOV ;
   - qualité/visibilité.
5. Mise à jour **uniquement** `b6_working_annotations/B26_XX.json` pour les cas **MOVE**, avec `correction_history`.

---

## Synthèse globale

| Métrique | Valeur |
|----------|--------|
| Landmarks revus | **18** |
| Images modifiées | **9** |
| JSON modifiés | **9** |
| Statut session | **P2_MANUAL_REVIEW_COMPLETED / QA_REQUIRED** |

### Comptage statuts revue

| Statut | N | % |
|--------|--:|--:|
| **KEEP** | **3** | 16,7 % |
| **MOVE** | **11** | 61,1 % |
| **REVIEW** | **4** | 22,2 % |
| **FAIL** | **0** | 0 % |

### Confiance

| Confiance | N |
|-----------|--:|
| HIGH | 0 |
| MEDIUM | **14** |
| LOW | **4** |

---

## Détail par landmark

### B26_02 — offset B26_01

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_R** | (544, 1805) → **(552, 1838)** | **MOVE** | MEDIUM | Apex caudal ischion D +33 px y |
| **IT_L** | (1879, 1826) → **(1879, 1826)** | **KEEP** | MEDIUM | Marge caudale arrondie conforme B1 |

---

### B26_03 — offset + contraste faible

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_R** | (732, 2141) → **(718, 2188)** | **MOVE** | MEDIUM | Soft-tissue → cortex ischion D |
| **IT_L** | (2074, 2026) → **(2068, 2068)** | **MOVE** | MEDIUM | Apex caudal ischion G +42 px y |

---

### B26_09 — FOV serré (IT_R seul P2)

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_R** | (769, 2105) → **(778, 2138)** | **MOVE** | MEDIUM | Apex caudal in-FOV ; marge 5,4 % |

*Note : IT_L corrigé en P0 — hors périmètre P2.*

---

### B26_14 — contraste très faible

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_R** | (744, 2201) → **(744, 2201)** | **REVIEW** | LOW | bone≈7 — structure non confirmable ; candidat v=0 |
| **IT_L** | (2000, 2121) → **(1994, 2158)** | **MOVE** | MEDIUM | Apex caudal G repositionné malgré contraste faible |

---

### B26_15 — contraste faible bilatéral

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_R** | (630, 2029) → **(630, 2029)** | **REVIEW** | LOW | Zone grainy sans bord osseux net |
| **IT_L** | (1725, 1976) → **(1725, 1976)** | **REVIEW** | LOW | Soft-tissue sous crête osseuse — apex indéterminable |

---

### B26_16 — IT_L (IT_R = P3)

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_L** | (1988, 2158) → **(1978, 2198)** | **MOVE** | MEDIUM | Corps ischion → apex caudal +40 px y |

---

### B26_18 — FOV large

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_R** | (772, 1925) → **(772, 1925)** | **KEEP** | MEDIUM | Bord médial ischion D ; anti-fémur OK |
| **IT_L** | (2077, 1812) → **(2072, 1848)** | **MOVE** | MEDIUM | Corps → apex caudal ischion G +36 px y |

---

### B26_19 — contraste très faible

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_R** | (777, 2103) → **(768, 2138)** | **MOVE** | MEDIUM | Soft-tissue obturateur → cortex ischion D |
| **IT_L** | (2029, 2029) → **(2029, 2029)** | **REVIEW** | LOW | bone≈4 — vallée soft-tissue ; validation clinique |

---

### B26_21 — IT_L (IT_R = P1 REVIEW)

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_L** | (2017, 2488) → **(2012, 2518)** | **MOVE** | MEDIUM | Apex caudal ischion G +30 px y |

---

### B26_22 — IT_R (IT_L corrigé P1)

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_R** | (828, 2308) → **(828, 2308)** | **KEEP** | MEDIUM | Contour ischion D médial fémur ; asym 6,2 % notée |

---

### B26_23 — offset standard

| Landmark | Avant → Après | Statut | Conf. | Synthèse |
|----------|---------------|--------|:-----:|----------|
| **IT_R** | (903, 2077) → **(892, 2108)** | **MOVE** | MEDIUM | Gap soft-tissue → cortex ischion D |
| **IT_L** | (2184, 1992) → **(2178, 2018)** | **MOVE** | MEDIUM | Apex caudal ischion G +26 px y |

---

## Points nécessitant QA

| # | Image | Landmark | Motif QA |
|---|-------|----------|----------|
| 1 | B26_02 | IT_R | MOVE caudal — valider repositionnement offset |
| 2 | B26_03 | IT_R, IT_L | MOVE bilatéral — valider cortex caudal |
| 3 | B26_09 | IT_R | MOVE FOV serré 5,4 % — pas d'extrapolation |
| 4 | B26_14 | IT_R | **REVIEW** — candidat v=0 (contraste très faible) |
| 5 | B26_14 | IT_L | MOVE malgré contraste faible |
| 6 | B26_15 | IT_R, IT_L | **REVIEW** bilatéral — structure non tranchable |
| 7 | B26_16 | IT_L | MOVE caudal vs IT_R PASS |
| 8 | B26_18 | IT_L | MOVE caudal — IT≠TD distance courte |
| 9 | B26_19 | IT_R | MOVE soft-tissue → cortex ; FOV 5,6 % |
| 10 | B26_19 | IT_L | **REVIEW** — candidat v=0 |
| 11 | B26_21 | IT_L | MOVE — cohérence vs IT_R P1 REVIEW |
| 12 | B26_23 | IT_R, IT_L | MOVE bilatéral gap soft-tissue |

**Landmarks KEEP sans QA prioritaire :** B26_02 IT_L, B26_18 IT_R, B26_22 IT_R.

---

## Fichiers modifiés

| Fichier | Modifié |
|---------|:-------:|
| `b6_P2_manual_review.md` | **Oui** (ce document) |
| `b6_P2_manual_review.csv` | **Oui** |
| `b6_working_annotations/B26_02.json` | **Oui** (IT_R) |
| `b6_working_annotations/B26_03.json` | **Oui** (IT_R, IT_L) |
| `b6_working_annotations/B26_09.json` | **Oui** (IT_R) |
| `b6_working_annotations/B26_14.json` | **Oui** (IT_L) |
| `b6_working_annotations/B26_16.json` | **Oui** (IT_L) |
| `b6_working_annotations/B26_18.json` | **Oui** (IT_L) |
| `b6_working_annotations/B26_19.json` | **Oui** (IT_R) |
| `b6_working_annotations/B26_21.json` | **Oui** (IT_L) |
| `b6_working_annotations/B26_23.json` | **Oui** (IT_R, IT_L) |
| Labels YOLO / `data.yaml` / V2 / V3 | **Non** |

*Export machine : `b6_P2_manual_review.csv`*

---

## Conclusion

```
3 KEEP · 11 MOVE · 4 REVIEW · 0 FAIL
→ P2_MANUAL_REVIEW_COMPLETED / QA_REQUIRED
```

La session P2 a corrigé **11 landmarks offset-dérivés** repositionnés sur le cortex caudal ischiatique identifiable (B1/B4). **4 landmarks REVIEW** (B26_14 IT_R, B26_15 bilatéral, B26_19 IT_L) restent non tranchables visuellement — candidats **`v=0`** ou validation clinique.

**Prochaine étape :** QA formel READ-ONLY P2 (`b6_P2_QA.md` / `.csv`).
