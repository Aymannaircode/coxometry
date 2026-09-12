# B6 — Revue manuelle visuelle IMAGE_REQUIRED (10 landmarks)

**Généré :** 2026-08-29  
**Session :** IMAGE_REQUIRED — revue visuelle post-récupération PNG  
**Statut :** `IMAGE_REQUIRED_REVIEW_COMPLETED / QA_REQUIRED`  
**Guide appliqué :** `bi_ischial_annotation_guidelines.md` (B1/B4)  
**Source PNG :** `datasets/yolo_pose_new_26/images/val/B26_XX.png` (originaux confirmés)  
**Modifications :** `b6_working_annotations/` uniquement

---

## Périmètre

| # | Image | Landmark | Priorité | Statut revue |
|--:|-------|----------|:--------:|:------------:|
| 1 | B26_10 | IT_R | P0_IMAGE_REQUIRED | MOVE |
| 2 | B26_10 | IT_L | P0_IMAGE_REQUIRED | MOVE |
| 3 | B26_13 | IT_R | P0_IMAGE_REQUIRED | MOVE |
| 4 | B26_13 | IT_L | P0_IMAGE_REQUIRED | KEEP |
| 5 | B26_17 | IT_R | P0_IMAGE_REQUIRED | MOVE |
| 6 | B26_17 | IT_L | P0_IMAGE_REQUIRED | MOVE |
| 7 | B26_20 | IT_R | P0_IMAGE_REQUIRED | MOVE |
| 8 | B26_20 | IT_L | P0_IMAGE_REQUIRED | MOVE |
| 9 | B26_26 | IT_R | P0_IMAGE_REQUIRED | MOVE |
| 10 | B26_26 | IT_L | P0_IMAGE_REQUIRED | MOVE |

**Total : 10 landmarks** sur 5 images val.  
**Hors scope respecté :** labels YOLO officiels, `data.yaml`, V2, V3, backend, Flutter — **non modifiés**. Aucun training lancé.

---

## Méthode

1. Chargement radiographies **PNG originales** (`images/val/B26_XX.png`) — fausse alerte `images/train/` corrigée (`missing_images_recovery.md`).
2. Revue visuelle humaine selon **B1/B4** — **aucune coordonnée calculée par offset B26_01** ; **aucune extrapolation** hors FOV.
3. Vérifications systématiques par point :
   - identification tubérosité ischiatique ;
   - placement apex caudal/inférieur identifiable ;
   - R/L patient ;
   - IT ≠ TD ;
   - anti-fémur (§3.6 B4) ;
   - FOV ;
   - qualité/visibilité.
4. Mise à jour **uniquement** `b6_working_annotations/B26_XX.json` avec historique de correction.

---

## Synthèse globale

| Métrique | Valeur |
|----------|--------|
| Landmarks revus | **10** |
| Images modifiées | **5** |
| Statut session | **IMAGE_REQUIRED_REVIEW_COMPLETED / QA_REQUIRED** |

### Comptage statuts revue

| Statut | N | % |
|--------|--:|--:|
| **KEEP** | **1** | 10 % |
| **MOVE** | **9** | 90 % |
| **REVIEW** | **0** | 0 % |
| **INVALID** | **0** | 0 % |

### Confiance

| Confiance | N |
|-----------|--:|
| HIGH | 0 |
| MEDIUM | **9** |
| LOW | **1** |

### Checks structurels (10/10 PASS sauf qualité)

| Critère | OK |
|---------|:--:|
| Tubérosité ischiatique (pas fémur) | **10** |
| R/L correct | **10** |
| IT ≠ TD | **10** |
| Anti-fémur | **10** |
| Dans FOV (pas extrapolation) | **10** |
| Qualité/visibilité PASS | **9** |
| Qualité/visibilité REVIEW | **1** (B26_26 IT_R) |

---

## Résultats détaillés

### 1. B26_10 — IT_R

| Champ | Valeur |
|-------|--------|
| **Avant** | (830.0, 2221.9) |
| **Après** | **(822.0, 2258.0)** |
| **Δ** | x −8 · y +36 |
| **Raison** | Offset initial — ~36 px trop crânial vs apex caudal ischion D visible |
| **Commentaire** | Replacé sur bord cortical inférieur ischion D — médial au fémur, anti-fémur OK |
| **Statut revue** | **MOVE** |
| **Confiance** | MEDIUM |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓ (marge 14,0 %)

---

### 2. B26_10 — IT_L

| Champ | Valeur |
|-------|--------|
| **Avant** | (1970.4, 2172.7) |
| **Après** | **(1975.0, 2210.0)** |
| **Δ** | x +5 · y +37 |
| **Raison** | Offset initial — ~37 px trop crânial vs bord caudal ischion G |
| **Commentaire** | Apex caudal ischion G sur cortex osseux — piège fémoral évité |
| **Statut revue** | **MOVE** |
| **Confiance** | MEDIUM |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

### 3. B26_13 — IT_R

| Champ | Valeur |
|-------|--------|
| **Avant** | (904.2, 2297.6) |
| **Après** | **(892.0, 2342.0)** |
| **Δ** | x −12 · y +44 |
| **Raison** | Offset initial — ~44 px trop crânial vs apex caudal local |
| **Commentaire** | Apex caudal ischion D sur bord cortical inférieur — FOV confortable 21 % |
| **Statut revue** | **MOVE** |
| **Confiance** | MEDIUM |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

### 4. B26_13 — IT_L

| Champ | Valeur |
|-------|--------|
| **Avant** | (2168.3, 2291.9) |
| **Après** | **(2168.3, 2291.9)** — conservé |
| **Δ** | — |
| **Raison** | Placement sur bord caudal ischion G — apex cortical atteint visuellement |
| **Commentaire** | Conservé — repère sur bord inférieur osseux identifiable ; symétrie y excellente (5,7 px) |
| **Statut revue** | **KEEP** |
| **Confiance** | MEDIUM |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

### 5. B26_17 — IT_R

| Champ | Valeur |
|-------|--------|
| **Avant** | (562.3, 2137.4) |
| **Après** | **(518.0, 2190.0)** |
| **Δ** | x −44 · y +53 |
| **Raison** | Offset initial — repère sur masse osseuse vs bord caudal diagonal inférieur |
| **Commentaire** | Replacé sur apex caudal ischion D — bord diagonal inférieur net dans FOV |
| **Statut revue** | **MOVE** |
| **Confiance** | MEDIUM |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓ (marge 10,3 %)

---

### 6. B26_17 — IT_L

| Champ | Valeur |
|-------|--------|
| **Avant** | (1869.5, 2083.3) |
| **Après** | **(1820.0, 2155.0)** |
| **Δ** | x −50 · y +72 |
| **Raison** | Offset initial — ~72 px trop crânial vs apex caudal ischion G |
| **Commentaire** | Apex caudal ischion G sur bord cortical inférieur — os pelvien confirmé |
| **Statut revue** | **MOVE** |
| **Confiance** | MEDIUM |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

### 7. B26_20 — IT_R

| Champ | Valeur |
|-------|--------|
| **Avant** | (667.2, 2245.2) |
| **Après** | **(688.0, 2208.0)** |
| **Δ** | x +21 · y −37 |
| **Raison** | Offset initial — ~37 px trop caudal ; repère en zone tissus mous sous ischion |
| **Commentaire** | Repositionné sur cortex ischiatique caudal — remonté depuis zone soft-tissue |
| **Statut revue** | **MOVE** |
| **Confiance** | MEDIUM |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓ (marge 12,2 %)

---

### 8. B26_20 — IT_L

| Champ | Valeur |
|-------|--------|
| **Avant** | (1900.6, 2135.1) |
| **Après** | **(1888.0, 2188.0)** |
| **Δ** | x −13 · y +53 |
| **Raison** | Offset initial — ~53 px trop crânial ; asymétrie y 110 px vs IT_R corrigé |
| **Commentaire** | Apex caudal ischion G sur bord osseux inférieur — cohérence bilatérale rétablie (Δy ≈ 20 px) |
| **Statut revue** | **MOVE** |
| **Confiance** | MEDIUM |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

### 9. B26_26 — IT_R

| Champ | Valeur |
|-------|--------|
| **Avant** | (538.3, 2030.0) |
| **Après** | **(552.0, 2088.0)** |
| **Δ** | x +14 · y +58 |
| **Raison** | Offset initial — ~58 px trop crânial ; contraste local faible |
| **Commentaire** | Apex caudal ischion D — bord osseux repéré malgré bruit ; **revue clinique recommandée** |
| **Statut revue** | **MOVE** |
| **Confiance** | **LOW** |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓ · qualité **REVIEW**

---

### 10. B26_26 — IT_L

| Champ | Valeur |
|-------|--------|
| **Avant** | (2002.9, 1932.9) |
| **Après** | **(1998.0, 1998.0)** |
| **Δ** | x −5 · y +65 |
| **Raison** | Offset initial — ~65 px trop crânial vs bord caudal ischion G |
| **Commentaire** | Apex caudal ischion G sur cortex pelvien — médial au fémur |
| **Statut revue** | **MOVE** |
| **Confiance** | MEDIUM |

**Vérifications :** structure ✓ · R/L ✓ · IT ≠ TD ✓ · anti-fémur ✓ · FOV ✓

---

## Cas nécessitant QA clinique

| Image | Landmark | Motif | Priorité QA |
|-------|----------|-------|:-----------:|
| **B26_26** | **IT_R** | Confiance LOW — contraste/bruit local ; bord osseux repéré mais validation clinique recommandée | **P1** |

**Note :** l'ensemble des 10 landmarks reste sous statut session `QA_REQUIRED` (validation clinique B6 non finalisée).

---

## Fichiers produits

| Fichier | Description |
|---------|-------------|
| `b6_image_required_manual_review.md` | Ce rapport |
| `b6_image_required_manual_review.csv` | Journal tabulaire (10 lignes) |
| `b6_working_annotations/B26_10.json` | Mis à jour (2 corrections) |
| `b6_working_annotations/B26_13.json` | Mis à jour (1 correction + 1 KEEP) |
| `b6_working_annotations/B26_17.json` | Mis à jour (2 corrections) |
| `b6_working_annotations/B26_20.json` | Mis à jour (2 corrections) |
| `b6_working_annotations/B26_26.json` | Mis à jour (2 corrections ; `review_recommended`) |

---

## Prochaine étape

Phase IMAGE_REQUIRED **terminée**. Enchaîner sur QA clinique supervisée des 10 landmarks + consolidation campagne B6 globale avant toute conversion label YOLO 16 kp.
