# B6 — Revue manuelle visuelle P3 (7 landmarks PASS)

**Généré :** 2026-08-29  
**Session :** P3 — confirmation visuelle des points QA PASS  
**Statut :** `P3_MANUAL_REVIEW_COMPLETED / QA_REQUIRED`  
**Guide appliqué :** `bi_ischial_annotation_guidelines.md` (B1/B4)  
**Source queue :** `b6_full_manual_review_queue.csv` (priorité P3 uniquement)  
**Source PNG :** `datasets/yolo_pose_new_26/images/train/B26_XX.png` (originaux pleine résolution)  
**Modifications :** **aucune** — 0 JSON modifié

---

## Périmètre

| # | Image | Landmark | Priorité | QA amont | Statut P3 |
|--:|-------|----------|:--------:|:--------:|:---------:|
| 1 | B26_01 | IT_R | P3 | PASS · HIGH | **KEEP** |
| 2 | B26_01 | IT_L | P3 | PASS · HIGH | **KEEP** |
| 3 | B26_07 | IT_L | P3 | PASS · MEDIUM | **KEEP** |
| 4 | B26_08 | IT_R | P3 | PASS · MEDIUM | **REVIEW** |
| 5 | B26_16 | IT_R | P3 | PASS · MEDIUM | **REVIEW** |
| 6 | B26_24 | IT_R | P3 | PASS · HIGH | **KEEP** |
| 7 | B26_24 | IT_L | P3 | PASS · MEDIUM | **KEEP** |

**Total : 7 landmarks** sur 5 images train.  
**Hors scope respecté :** labels YOLO officiels, `data.yaml`, V2, V3, backend, Flutter — **non modifiés**. Aucun training lancé. Aucun P0/P1/P2/IMAGE_REQUIRED traité.

---

## Méthode

1. Chargement radiographies **PNG originales** à pleine résolution.
2. Zoom local sur chaque tubérosité ischiatique (crops pelvis + zoom contrasté).
3. Revue visuelle de confirmation selon **B1/B4** — **aucune coordonnée calculée automatiquement** ; **aucune symétrie** ; **aucun offset** ; **aucune extrapolation**.
4. Vérifications systématiques par point :
   - identification tubérosité ischiatique ;
   - placement apex caudal/inférieur identifiable (B1/B4) ;
   - R/L patient ;
   - IT ≠ TD ;
   - anti-fémur (§3.6 B4) ;
   - FOV ;
   - qualité/visibilité.
5. Objectif P3 : **confirmer** les points déjà classés PASS — KEEP si conforme, REVIEW si réserve, MOVE uniquement si correction visuelle nécessaire.

---

## Synthèse globale

| Métrique | Valeur |
|----------|--------|
| Landmarks revus | **7** |
| Images modifiées | **0** |
| JSON modifiés | **0** |
| Statut session | **P3_MANUAL_REVIEW_COMPLETED / QA_REQUIRED** |

### Comptage statuts revue

| Statut | N | % |
|--------|--:|--:|
| **KEEP** | **5** | 71,4 % |
| **MOVE** | **0** | 0 % |
| **REVIEW** | **2** | 28,6 % |
| **FAIL** | **0** | 0 % |

### Confiance

| Confiance | N |
|-----------|--:|
| HIGH | **1** |
| MEDIUM | **6** |
| LOW | **0** |

---

## Détail par landmark

### B26_01 — cas standard pilote (référence B6)

| Landmark | Coordonnées | Statut | Conf. | Synthèse |
|----------|-------------|--------|:-----:|----------|
| **IT_R** | **(548, 2140)** | **KEEP** | HIGH | Apex caudal ischion D sur bord cortical inférieur net ; anti-fémur OK ; marge FOV 19,7 % |
| **IT_L** | **(1772, 2178)** | **KEEP** | MEDIUM | Piège fémoral évité ; cortex ischion G caudal ; validation indépendante |

**Vérifications IT_R :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Masse osseuse caudale latérale pelvis |
| 2 | B1/B4 | ✓ | Point caudal/inférieur cortex osseux identifiable |
| 3 | R/L | ✓ | IT_R côté droit patient (gauche image) |
| 4 | IT ≠ TD | ✓ | dy TD = +250 px |
| 5 | Anti-fémur | ✓ | Δx FSD = 153 px — médial fémur |
| 6 | FOV | ✓ | Marge caudale 19,7 % — confortable |
| 7 | Qualité | ✓ | Cas standard EXCELLENT B7 |

**Vérifications IT_L :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1–6 | Structure, B1/B4, R/L, IT≠TD, anti-fémur, FOV | ✓ | Piège fémoral A-IT01 corrigé ; asym y vs IT_R = 38 px |
| 7 | Qualité | ✓ | Contraste modéré acceptable |

---

### B26_07 — IT_L (gaz intestinal — côté G)

| Landmark | Coordonnées | Statut | Conf. | Synthèse |
|----------|-------------|--------|:-----:|----------|
| **IT_L** | **(1778, 2548)** | **KEEP** | MEDIUM | Apex caudal ischion G — bord inférieur osseux net malgré A-GAS07 |

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Cortex ischion G latéral au gaz central |
| 2 | B1/B4 | ✓ | Point caudal sur bord cortical inférieur |
| 3 | R/L | ✓ | IT_L côté gauche patient |
| 4 | IT ≠ TD | ✓ | dy TD = +374 px |
| 5 | Anti-fémur | ✓ | Δx FSD = 447 px |
| 6 | FOV | ✓ | Marge 5,2 % — acceptable |
| 7 | Qualité | ✓ | Repère latéral moins obscurci que IT_R (P1) |

*Note : IT_R reste en P1 REVIEW — hors périmètre P3.*

---

### B26_08 — IT_R (offset — réserve caudalité)

| Landmark | Coordonnées | Statut | Conf. | Synthèse |
|----------|-------------|--------|:-----:|----------|
| **IT_R** | **(651, 2208)** | **REVIEW** | MEDIUM | Repère légèrement crânial vs bord caudal cortical visible |

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Zone ischion D — distincte fémur |
| 2 | B1/B4 | △ | Apex caudal approximatif — bord inférieur visible sous le repère |
| 3–5 | R/L, IT≠TD, anti-fémur | ✓ | dy TD = +276 px ; Δx FSD = 164 px |
| 6 | FOV | ✓ | Marge 8,9 % |
| 7 | Qualité | △ | Contraste modéré ; grain élevé |

**Motif REVIEW :** PASS QA amont maintenu structurellement mais apex caudal non optimal visuellement — **non déplacé** (pas d'extrapolation). Validation clinique ou P2-style MOVE futur si confirmé.

---

### B26_16 — IT_R (offset — référence P2 IT_L)

| Landmark | Coordonnées | Statut | Conf. | Synthèse |
|----------|-------------|--------|:-----:|----------|
| **IT_R** | **(730, 2246)** | **REVIEW** | MEDIUM | Contraste faible — apex caudal peu net ; structure plausible |

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1 | Tubérosité ischiatique | ✓ | Masse osseuse ischion D identifiable |
| 2 | B1/B4 | △ | Courbe caudale faible contraste — apex non tranchable |
| 3–5 | R/L, IT≠TD, anti-fémur | ✓ | dy TD = +225 px ; Δx FSD = 200 px |
| 6 | FOV | ✓ | Marge 6,5 % |
| 7 | Qualité | △ | Grain élevé — confiance visuelle limitée |

**Motif REVIEW :** utilisé comme référence P2 pour IT_L MOVE — structure OK mais B1 peu net. **Non déplacé.**

---

### B26_24 — post-correction piège fémoral

| Landmark | Coordonnées | Statut | Conf. | Synthèse |
|----------|-------------|--------|:-----:|----------|
| **IT_R** | **(698, 2398)** | **KEEP** | MEDIUM | Piège fémoral corrigé — cortex ischion D confirmé |
| **IT_L** | **(1858, 2328)** | **KEEP** | MEDIUM | Apex caudal ischion G — asymétrie rétablie |

**IT_R — vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1–5 | Structure, B1/B4, R/L, IT≠TD, anti-fémur | ✓ | Hors diaphyse fémorale ; Δx FSD = 153 px |
| 6 | FOV | △ | Marge 2,8 % — serré mais in-FOV |
| 7 | Qualité | ✓ | Contraste modéré |

**IT_L — vérifications :**

| # | Critère | Résultat | Détail |
|---|---------|:--------:|--------|
| 1–6 | | ✓ | Apex caudal G ; dy TD = +450 px |
| 7 | Qualité | △ | Contraste modéré — acceptable |

---

## Points nécessitant QA post-P3

| # | Image | Landmark | Motif |
|---|-------|----------|-------|
| 1 | B26_08 | IT_R | REVIEW P3 — apex caudal légèrement crânial ; confirmer KEEP vs MOVE |
| 2 | B26_16 | IT_R | REVIEW P3 — contraste faible ; cohérence vs IT_L P2 MOVE |

**Landmarks KEEP sans QA prioritaire :** B26_01 IT_R/L, B26_07 IT_L, B26_24 IT_R/L.

---

## Fichiers

| Fichier | Modifié |
|---------|:-------:|
| `b6_P3_manual_review.md` | **Oui** (ce document) |
| `b6_P3_manual_review.csv` | **Oui** |
| `b6_working_annotations/*.json` | **Non** |
| Labels YOLO / `data.yaml` / V2 / V3 | **Non** |

*Export machine : `b6_P3_manual_review.csv`*

---

## Conclusion

```
5/7 KEEP · 0/7 MOVE · 2/7 REVIEW · 0/7 FAIL
→ P3_MANUAL_REVIEW_COMPLETED / QA_REQUIRED
```

**5 landmarks PASS confirmés visuellement** (KEEP) — dont le cas standard **B26_01** (référence B6) et la paire **B26_24** post-correction piège fémoral.

**2 landmarks REVIEW** (B26_08 IT_R, B26_16 IT_R) — structure ischiatique plausible mais réserve sur apex caudal B1 ; **aucun déplacement** effectué conformément aux règles anti-extrapolation.

**Prochaine étape :** QA formel READ-ONLY P3 (`b6_P3_QA.md` / `.csv`).
