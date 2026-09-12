# B6 — Session manuelle P0 MOVE (6 landmarks)

**Généré :** 2026-08-29  
**Session :** MANUELLE B6 — Phase 1 P0 MOVE  
**Statut :** `P0_MOVE_COMPLETED / QA_REQUIRED`  
**Guide appliqué :** `bi_ischial_annotation_guidelines.md` (B1/B4)  
**Source queue :** `b6_full_manual_review_queue.csv`

---

## Périmètre

| # | Image | Landmark | Priorité | Action |
|--:|-------|----------|:--------:|--------|
| 1 | B26_04 | IT_R | P0 | MOVE |
| 2 | B26_06 | IT_L | P0 | MOVE |
| 3 | B26_08 | IT_L | P0 | MOVE |
| 4 | B26_09 | IT_L | P0 | MOVE |
| 5 | B26_25 | IT_R | P0 | MOVE |
| 6 | B26_25 | IT_L | P0 | MOVE |

**Total : 6 landmarks corrigés** sur 5 images.  
**Hors scope respecté :** aucun IMAGE_REQUIRED, aucun autre REVIEW, aucun label YOLO / data.yaml / V2 / V3 / backend / Flutter.

---

## Méthode

1. Chargement radiographies originales (`images/train/B26_XX.png`).
2. Revue visuelle humaine selon B1/B4 — **aucune coordonnée calculée automatiquement** (pas d'offset scan).
3. Vérifications systématiques : tubérosité ischiatique, R/L, IT ≠ TD, anti-fémur, FOV.
4. Mise à jour **uniquement** `b6_working_annotations/B26_XX.json`.

---

## Synthèse globale

| Métrique | Valeur |
|----------|--------|
| Landmarks corrigés | **6** |
| Images modifiées | **5** |
| Statut session | **P0_MOVE_COMPLETED / QA_REQUIRED** |
| Confiance HIGH | 0 |
| Confiance MEDIUM | **6** |
| Confiance LOW | 0 |

### Checks structurels (6/6)

| Critère | OK |
|---------|:--:|
| Tubérosité ischiatique (pas fémur) | **6** |
| R/L correct | **6** |
| IT ≠ TD | **6** |
| Anti-fémur | **6** |
| Dans FOV (pas extrapolation) | **6** |

---

## Résultats détaillés

### 1. B26_04 — IT_R (piège fémoral)

| Champ | Valeur |
|-------|--------|
| **Avant** | (856.0, 2454.0) |
| **Après** | **(738.0, 2338.0)** |
| **Δ** | x −118 · y −116 |
| **Raison** | Piège fémoral — point sur diaphyse fémorale (Δx FSD = 100 px) ; position initiale sur cortex fémoral latéral, non sur ischion |
| **Commentaire** | Replacé sur apex caudal ischion D — cortex pelvien médial au fémur |
| **Statut** | P0_MOVE_COMPLETED / QA_REQUIRED |
| **Confiance** | MEDIUM |
| **reviewer_status** | standard |

**Vérifications :** structure ischiatique ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

### 2. B26_06 — IT_L (asymétrie majeure)

| Champ | Valeur |
|-------|--------|
| **Avant** | (1929.5, 2043.0) |
| **Après** | **(1882.0, 2228.0)** |
| **Δ** | x −48 · y +185 |
| **Raison** | ~198 px trop crânial vs IT_R (716, 2241) — sous-estimation caudale offset |
| **Commentaire** | Apex caudal ischion G sur cortex pelvien — cohérence bilatérale rétablie (Δy R-L ≈ 13 px) |
| **Statut** | P0_MOVE_COMPLETED / QA_REQUIRED |
| **Confiance** | MEDIUM |
| **reviewer_status** | standard |

**Vérifications :** structure ischiatique ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

### 3. B26_08 — IT_L (alignement vs IT_R PASS)

| Champ | Valeur |
|-------|--------|
| **Avant** | (1746.5, 2133.1) |
| **Après** | **(1718.0, 2192.0)** |
| **Δ** | x −29 · y +59 |
| **Raison** | Trop crânial vs IT_R PASS (650.7, 2207.9) — apex caudal non atteint |
| **Commentaire** | Apex caudal ischion G sur bord cortical inférieur — IT_R conservé comme référence PASS |
| **Statut** | P0_MOVE_COMPLETED / QA_REQUIRED |
| **Confiance** | MEDIUM |
| **reviewer_status** | standard |

**Vérifications :** structure ischiatique ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

### 4. B26_09 — IT_L (FOV serré)

| Champ | Valeur |
|-------|--------|
| **Avant** | (2268.3, 2053.5) |
| **Après** | **(2255.0, 2092.0)** |
| **Δ** | x −13 · y +39 |
| **Raison** | Trop crânial (~39 px) vs apex caudal local — FOV serré 5,4 % |
| **Commentaire** | Apex caudal ischion G sur cortex osseux — pas d'extrapolation hors FOV |
| **Statut** | P0_MOVE_COMPLETED / QA_REQUIRED |
| **Confiance** | MEDIUM |
| **reviewer_status** | standard |

**Vérifications :** structure ischiatique ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓ (conservateur)

---

### 5. B26_25 — IT_R (caudalité)

| Champ | Valeur |
|-------|--------|
| **Avant** | (679.1, 2194.7) |
| **Après** | **(665.0, 2245.0)** |
| **Δ** | x −14 · y +50 |
| **Raison** | Trop crânial (~50 px) vs apex caudal ischion D |
| **Commentaire** | Apex caudal ischion D sur cortex osseux — médial au fémur, hors diaphyse |
| **Statut** | P0_MOVE_COMPLETED / QA_REQUIRED |
| **Confiance** | MEDIUM |
| **reviewer_status** | standard |

**Vérifications :** structure ischiatique ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

### 6. B26_25 — IT_L (caudalité)

| Champ | Valeur |
|-------|--------|
| **Avant** | (2032.7, 2105.7) |
| **Après** | **(1998.0, 2178.0)** |
| **Δ** | x −35 · y +72 |
| **Raison** | Trop crânial (~72 px) vs apex caudal ischion G |
| **Commentaire** | Apex caudal ischion G sur bord cortical inférieur visible |
| **Statut** | P0_MOVE_COMPLETED / QA_REQUIRED |
| **Confiance** | MEDIUM |
| **reviewer_status** | standard |

**Vérifications :** structure ischiatique ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

## Fichiers modifiés

| Fichier | Modifié |
|---------|:-------:|
| `b6_working_annotations/B26_04.json` | **Oui** (IT_R) |
| `b6_working_annotations/B26_06.json` | **Oui** (IT_L) |
| `b6_working_annotations/B26_08.json` | **Oui** (IT_L) |
| `b6_working_annotations/B26_09.json` | **Oui** (IT_L) |
| `b6_working_annotations/B26_25.json` | **Oui** (IT_R, IT_L) |
| `b6_P0_move_review.md` | **Oui** (ce document) |
| `b6_P0_move_review.csv` | **Oui** |

## Fichiers non modifiés

| Fichier | Modifié |
|---------|:-------:|
| Labels YOLO officiels | **Non** |
| `data.yaml` | **Non** |
| V2 / V3 | **Non** |
| Backend / Flutter | **Non** |
| 10 IMAGE_REQUIRED | **Non** |
| 34 REVIEW restants | **Non** |

---

## Prochaine étape

QA formel READ-ONLY des 6 landmarks corrigés (analogue `b6_corrected_9_QA.md`) avant promotion éventuelle.

*Export machine : `b6_P0_move_review.csv`*
