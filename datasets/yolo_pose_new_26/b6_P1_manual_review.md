# B6 — Revue manuelle visuelle P1 (11 landmarks)

**Généré :** 2026-08-29  
**Session :** P1 — revue visuelle prioritaire  
**Statut :** `P1_MANUAL_REVIEW_COMPLETED / QA_REQUIRED`  
**Guide appliqué :** `bi_ischial_annotation_guidelines.md` (B1/B4)  
**Source queue :** `b6_full_manual_review_queue.csv` (priorité P1 uniquement)  
**Source PNG :** `datasets/yolo_pose_new_26/images/train/B26_XX.png` (originaux pleine résolution)  
**Modifications :** `b6_working_annotations/` uniquement (4 fichiers JSON, 5 landmarks MOVE)

---

## Périmètre

| # | Image | Landmark | Priorité | Statut revue |
|--:|-------|----------|:--------:|:------------:|
| 1 | B26_04 | IT_L | P1 | KEEP |
| 2 | B26_05 | IT_R | P1 | KEEP |
| 3 | B26_05 | IT_L | P1 | MOVE |
| 4 | B26_06 | IT_R | P1 | REVIEW |
| 5 | B26_07 | IT_R | P1 | KEEP |
| 6 | B26_11 | IT_R | P1 | REVIEW |
| 7 | B26_11 | IT_L | P1 | KEEP |
| 8 | B26_12 | IT_R | P1 | MOVE |
| 9 | B26_12 | IT_L | P1 | MOVE |
| 10 | B26_21 | IT_R | P1 | REVIEW |
| 11 | B26_22 | IT_L | P1 | MOVE |

**Total : 11 landmarks** sur 8 images train.  
**Hors scope respecté :** labels YOLO officiels, `data.yaml`, V2, V3, backend, Flutter — **non modifiés**. Aucun training lancé. Aucun P2/P3 traité.

---

## Méthode

1. Chargement radiographies **PNG originales** à pleine résolution.
2. Zoom local sur chaque tubérosité ischiatique (crops pelvis + zoom raw/contrast).
3. Revue visuelle humaine selon **B1/B4** — **aucune coordonnée calculée automatiquement** ; **aucune symétrie** ; **aucun offset** ; **aucune extrapolation**.
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
| Landmarks revus | **11** |
| Images modifiées | **3** (B26_05, B26_12, B26_22) |
| JSON modifiés | **3** |
| Statut session | **P1_MANUAL_REVIEW_COMPLETED / QA_REQUIRED** |

### Comptage statuts revue

| Statut | N | % |
|--------|--:|--:|
| **KEEP** | **4** | 36 % |
| **MOVE** | **4** | 36 % |
| **REVIEW** | **3** | 27 % |
| **FAIL** | **0** | 0 % |

### Confiance

| Confiance | N |
|-----------|--:|
| HIGH | 0 |
| MEDIUM | **8** |
| LOW | **3** |

---

## Détail par landmark

### 1. B26_04 — IT_L → **KEEP** (MEDIUM)

| Champ | Valeur |
|-------|--------|
| Avant | (2193.1, 2256.9) |
| Après | (2193.1, 2256.9) |
| reviewer_status | standard |

**Raison :** Asymétrie y vs IT_R (856, 2454) notée par le QA (~81 px) — validation indépendante : apex caudal ischion G identifiable sur bord cortical inférieur. Pas de correction basée sur symétrie. R/L OK. IT ≠ TD. Anti-fémur OK. FOV confortable.

---

### 2. B26_05 — IT_R → **KEEP** (MEDIUM, PARTIAL)

| Champ | Valeur |
|-------|--------|
| Avant | (648.0, 2955.0) |
| Après | (648.0, 2955.0) |
| reviewer_status | supervised_case |

**Raison :** Cas **PARTIAL FOV** (A-FOV05). Dernier bord osseux net in-FOV conservé sans extrapolation caudale. Piège fémoral évité (A-FEM05). IT ≠ TD. Choix conservateur PARTIAL validé visuellement.

---

### 3. B26_05 — IT_L → **MOVE** (MEDIUM, PARTIAL)

| Champ | Valeur |
|-------|--------|
| Avant | (2395.0, 2958.0) |
| Après | (2412.0, 2960.0) |
| Δ | (+17, +2) |
| reviewer_status | supervised_case |
| JSON | `b6_working_annotations/B26_05.json` |

**Raison :** Repère latéral au cortex en zone soft-tissue. Replacé sur bord osseux ischion G au contact FOV. Anti-fémur OK. PARTIAL conservateur.

---

### 4. B26_06 — IT_R → **REVIEW** (LOW)

| Champ | Valeur |
|-------|--------|
| Avant | (716.0, 2241.0) |
| Après | (716.0, 2241.0) — **non modifié** |
| reviewer_status | standard |

**Raison :** Contraste local insuffisant — apex caudal ischion D non tranchable. Asymétrie y 8,2 % vs IT_L signalée par QA mais **non utilisée** pour placer le point. Contour indéterminable → ne pas inventer.

---

### 5. B26_07 — IT_R → **KEEP** (MEDIUM)

| Champ | Valeur |
|-------|--------|
| Avant | (708.0, 2548.0) |
| Après | (708.0, 2548.0) |
| reviewer_status | review_recommended |

**Raison :** Cas **A-GAS07** (gaz intestinal). Cortex ischion D identifiable malgré obscurcissement partiel. Symétrie y avec IT_L (1778, 2548) confirmée visuellement (pas utilisée pour placement). R/L OK. IT ≠ TD.

---

### 6. B26_11 — IT_R → **REVIEW** (LOW)

| Champ | Valeur |
|-------|--------|
| Avant | (632.0, 2498.0) |
| Après | (632.0, 2498.0) — **non modifié** |
| reviewer_status | review_recommended |

**Raison :** Cas **A-ROT11** (rotation) + contraste très faible. Apex caudal ischion D non identifiable — bruit local empêche repérage fiable du contour osseux. Ne pas inventer.

---

### 7. B26_11 — IT_L → **KEEP** (MEDIUM)

| Champ | Valeur |
|-------|--------|
| Avant | (1958.0, 2495.0) |
| Après | (1958.0, 2495.0) |
| reviewer_status | review_recommended |

**Raison :** Même cas A-ROT11 — validation **indépendante** côté G : apex caudal identifiable sur bord diagonal inférieur malgré faible contraste. R/L OK. IT ≠ TD. Anti-fémur OK.

---

### 8. B26_12 — IT_R → **MOVE** (MEDIUM)

| Champ | Valeur |
|-------|--------|
| Avant | (843.0, 2148.0) |
| Après | (846.0, 2198.0) |
| Δ | (+3, +50) |
| reviewer_status | review_recommended |
| JSON | `b6_working_annotations/B26_12.json` |

**Raison :** Cas **A-BRD12** (marge caudale réduite). Repère trop crânial vs ligne caudale nette. Replacé sur apex caudal ischion D — bord cortical inférieur. Marge FOV ~9,8 %.

---

### 9. B26_12 — IT_L → **MOVE** (MEDIUM)

| Champ | Valeur |
|-------|--------|
| Avant | (2041.0, 2179.0) |
| Après | (2038.0, 2210.0) |
| Δ | (−3, +31) |
| reviewer_status | review_recommended |
| JSON | `b6_working_annotations/B26_12.json` |

**Raison :** A-BRD12 — repère au-dessus du bord caudal cortical sharp ischion G. Replacé sur bord inférieur osseux. Règle bord FOV appliquée. Validation indépendante de IT_R.

---

### 10. B26_21 — IT_R → **REVIEW** (LOW)

| Champ | Valeur |
|-------|--------|
| Avant | (841.9, 2580.5) |
| Après | (841.9, 2580.5) — **non modifié** |
| reviewer_status | standard |

**Raison :** Contraste très faible. Scan automatique suggérait +38 px caudal — **non confirmé visuellement**. Contour caudal ischion D indéterminable. Ne pas extrapoler depuis scan.

---

### 11. B26_22 — IT_L → **MOVE** (MEDIUM)

| Champ | Valeur |
|-------|--------|
| Avant | (2028.4, 2154.0) |
| Après | (2024.0, 2238.0) |
| Δ | (−4.4, +84) |
| reviewer_status | standard |
| JSON | `b6_working_annotations/B26_22.json` |

**Raison :** ~154 px crânial vs IT_R (828, 2308) signalé par QA — courbe caudale ischion G identifiable **indépendamment** (sans symétrie). Replacé sur apex caudal — bord cortical inférieur. Os pelvien confirmé. IT ≠ TD.

---

## Fichiers JSON modifiés

| Fichier | Landmarks MOVE | Action |
|---------|----------------|--------|
| `b6_working_annotations/B26_05.json` | IT_L | correction_history ajouté |
| `b6_working_annotations/B26_12.json` | IT_R, IT_L | correction_history ajouté |
| `b6_working_annotations/B26_22.json` | IT_L | correction_history ajouté |

**Non modifiés (KEEP/REVIEW) :** B26_04.json, B26_06.json, B26_07.json, B26_11.json, B26_21.json

---

## Points nécessitant QA

| Priorité QA | Image | Landmark | Statut P1 | Motif |
|:-----------:|-------|----------|:---------:|-------|
| **HAUTE** | B26_06 | IT_R | REVIEW/LOW | Contour caudal indéterminable |
| **HAUTE** | B26_11 | IT_R | REVIEW/LOW | Rotation + contraste — apex non identifiable |
| **HAUTE** | B26_21 | IT_R | REVIEW/LOW | Contraste faible — contour indéterminable |
| MOYENNE | B26_05 | IT_R | KEEP/MEDIUM | PARTIAL FOV — validation clinique recommandée |
| MOYENNE | B26_05 | IT_L | MOVE/MEDIUM | PARTIAL FOV — correction au bord image |
| MOYENNE | B26_07 | IT_R | KEEP/MEDIUM | Gaz intestinal A-GAS07 |
| MOYENNE | B26_11 | IT_L | KEEP/MEDIUM | Rotation A-ROT11 — confirmer indépendamment |
| MOYENNE | B26_12 | IT_R | MOVE/MEDIUM | Marge caudale A-BRD12 |
| MOYENNE | B26_12 | IT_L | MOVE/MEDIUM | Marge caudale A-BRD12 |

---

## Résumé final

```
P1_MANUAL_REVIEW_COMPLETED / QA_REQUIRED

KEEP   = 4  (B26_04 IT_L, B26_05 IT_R, B26_07 IT_R, B26_11 IT_L)
MOVE   = 4  (B26_05 IT_L, B26_12 IT_R, B26_12 IT_L, B26_22 IT_L)
REVIEW = 3  (B26_06 IT_R, B26_11 IT_R, B26_21 IT_R)
FAIL   = 0
```

**Prochaine étape recommandée :** QA clinique sur les 3 cas REVIEW/LOW + validation des 4 MOVE MEDIUM avant passage P0/P2.
