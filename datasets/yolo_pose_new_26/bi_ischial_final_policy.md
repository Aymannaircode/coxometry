# Politique finale B1/B4 — `IT_R` / `IT_L` (bi-ischial)

**Généré :** 2026-08-29  
**Mode :** finalisation documentaire **READ-ONLY** — aucune annotation, label, YAML, modèle, backend ou Flutter modifié  
**Statut :** **`B1_B4_FINAL_POLICY_READY`**

**Sources :**

- `bi_ischial_spec.md`
- `bi_ischial_annotation_guidelines.md`
- `b6_global_final_QA.md` (+ `b6_global_final_QA.csv`)

**Interdictions respectées :** labels YOLO · working annotations · `data.yaml` · V2 · V3 · backend · Flutter · training — **aucune modification**.

---

## 1. Contexte et objectif

Cette étape **fige la règle d'annotation** `IT_R` / `IT_L` avant le passage officiel de **14 à 16 keypoints** (étape B5). Elle s'appuie sur :

- la spécification bi-ischiale existante ;
- le guide d'annotation B4 (campagnes pilote et revues) ;
- la synthèse QA globale B6 sur 52 landmarks (B26_01 → B26_26).

La campagne B6 a produit des **working annotations** et une matrice QA finale (`B6_GLOBAL_QA_REVIEW`). Cette politique **ne promeut pas** automatiquement les REVIEW en PASS et **n'applique pas** de v=0 aux coordonnées working.

---

## 2. Définition opérationnelle finale

### Formulation figée

> **`IT_R` / `IT_L` = point caudal/inférieur identifiable du contour osseux de chaque tubérosité ischiatique sur la radiographie AP du bassin.**

| Attribut | Valeur |
|----------|--------|
| **Statut B1** | **FINAL** (définition opérationnelle du projet) |
| **Structure** | Tubérosité ischiatique — os pelvien |
| **Position** | Apex caudal/inférieur du **contour osseux** identifiable |
| **Vue** | Radiographie AP bassin adulte |
| **Rôle géométrique** | `BI_ISCHIAL = droite(IT_R, IT_L)` |
| **IDs proposés** | LM-17 (`IT_R`), LM-18 (`IT_L`) |

### Ce que cette définition n'est pas

| Exclusion | Motif |
|-----------|-------|
| Centre géométrique de la tubérosité | Non tranché cliniquement ; rejeté par la formulation caudale |
| Point le plus bas de l'image | Risque piège fémoral (B26_01, B26_05) |
| Teardrop acétabulaire (`TD_*`) | Structure distincte — A2 |
| Point estimé sans contour net | Interdit — règle MVP §1.2 |

### Validation B6

Sur 52 landmarks working : **31 PASS** · **20 REVIEW** · **1 UNRESOLVABLE_REVIEW** · **0 FAIL structurel**. La définition B1/B4 est **applicable** sur le corpus ; 21 cas conservent une réserve documentée.

---

## 3. Règles de placement obligatoires

### 3.1 Contour osseux ischiatique

1. Identifier la tubérosité ischiatique homolatérale — masse osseuse caudale latérale, **distincte** du teardrop médial.
2. Suivre le **contour osseux projeté** (bord radiographique net).
3. Placer le centre du landmark sur le point **le plus caudal/inférieur identifiable** de ce contour, **sans extrapolation**.

### 3.2 Règle anti-fémur

> Un candidat `IT_*` ne doit **jamais** être placé sur la diaphyse ou le contour du fémur.

| Conduite | Détail |
|----------|--------|
| Vérification | Repère sur os pelvien, **médial** à l'axe fémoral proximal |
| Piège documenté | B26_01 `IT_L`, B26_05 `IT_R` — candidats fémoraux rejetés en campagne B6 |
| Si ischion non distinguable du fémur sans deviner | **`v=0`** |

**Validation B6 :** 52/52 anti-fémur PASS.

### 3.3 Règle TD ≠ IT

```
TD_R / TD_L  ≠  IT_R / IT_L
```

| | `TD_*` | `IT_*` |
|---|--------|--------|
| Structure | Teardrop acétabulaire | Tubérosité ischiatique |
| Rôle | Horizontal pelvien MVP (`ITH`) | Ligne bi-ischiatique (`BI_ISCHIAL`) |
| Substitution | **Interdite** dans les deux sens (A2) | **Interdite** |

**Validation B6 :** 52/52 IT ≠ TD PASS.

### 3.4 Convention R/L

| Label | Côté patient | Position image AP |
|-------|--------------|-------------------|
| `IT_R` | Droite | Gauche de l'écran |
| `IT_L` | Gauche | Droite de l'écran |

- Vérifier latéralité patient en cas de doute (DICOM, anatomie).
- **Interdiction** de symétrie miroir entre côtés.

**Validation B6 :** 52/52 R/L PASS.

---

## 4. Règles FOV

| # | Règle | Statut |
|:-:|-------|--------|
| 1 | **Aucune extrapolation** hors FOV visible | FINAL |
| 2 | Retenir le dernier cortex caudal **identifiable dans l'image** | FINAL |
| 3 | Apex caudal coupé par le bord → **`v=0`** si placement exact exige reconstruction hors os | FINAL |
| 4 | Cas PARTIAL (B26_05) → session supervisée ; v=2 et v=0 restent défendables | FINAL |

**Validation B6 :** 49 PASS FOV · 3 REVIEW FOV (B26_05 bilat., B26_09 IT_R, B26_19 IT_R).

---

## 5. Règle de visibilité et v=0

### 5.1 Convention `v` (alignée MVP — aucune nouvelle convention)

| Code | Signification | Usage IT |
|:----:|---------------|----------|
| **2** | Point net, localisable sans doute raisonnable | **Si contour caudal identifiable** |
| **1** | Point estimé | **Interdit par défaut** |
| **0** | Non annoté / non fiable | **Si repère non identifiable ou deviner requis** |

### 5.2 Règle v=0 — formulation finale

> **`v=0` lorsque le landmark anatomique requis (apex caudal du contour ischiatique) n'est pas suffisamment identifiable pour être annoté de manière fiable.**

> **Ne jamais utiliser `v=0` simplement parce que le point est difficile mais identifiable.**

| Situation | `v` | Exemple corpus |
|-----------|:---:|----------------|
| Contour caudal net, sans extrapolation | **2** | B26_01 bilatéral |
| Contour identifiable malgré contraste réduit | **2** (REVIEW possible) | B26_25 IT_L — REVIEW mais v=2 conservé |
| Apex indéterminable malgré revue | **0 candidat** | B26_06 IT_R, B26_11 IT_R, B26_14 IT_R |
| Apex caudal non tranchable — cas non résoluble | **0 candidat** | **B26_26 IT_R** |
| PARTIAL FOV — trancher v=2 vs v=0 | **REVIEW** | B26_05 bilatéral |
| Placement = deviner | **0** | Règle d'or MVP |

### 5.3 Mapping YOLO futur (documenté, non appliqué)

`v=0` → `(0, 0, 0)` dans les labels YOLO 16 kp. **Non modifié à cette étape.**

### 5.4 Candidats v=0 identifiés (10 — liste indicative)

Aucune conversion appliquée aux working annotations.

| Image | Landmark | Statut QA |
|-------|----------|-----------|
| B26_05 | IT_R, IT_L | REVIEW |
| B26_06 | IT_R | REVIEW |
| B26_11 | IT_R | REVIEW |
| B26_14 | IT_R | REVIEW |
| B26_15 | IT_R, IT_L | REVIEW |
| B26_19 | IT_L | REVIEW |
| B26_21 | IT_R | REVIEW |
| B26_26 | IT_R | UNRESOLVABLE_REVIEW |

---

## 6. Traitement des cas REVIEW

### Politique

| Principe | Conduite |
|----------|----------|
| Conservation | Les **20 REVIEW** restent documentés dans `b6_global_final_QA.csv` |
| Pas de promotion auto | **Aucune** conversion automatique REVIEW → PASS |
| Pas de v=0 auto | **Aucune** conversion automatique REVIEW → v=0 |
| Promotion | Uniquement après **validation clinique explicite** du cas |
| Working annotations | Coordonnées **conservées** telles quelles en attendant arbitrage |

### Liste complète REVIEW (20)

B26_03 IT_L · B26_05 IT_R/L · B26_06 IT_R · B26_07 IT_R · B26_08 IT_R · B26_09 IT_R · B26_11 IT_R/L · B26_14 IT_R/L · B26_15 IT_R/L · B26_16 IT_R · B26_18 IT_L · B26_19 IT_R/L · B26_21 IT_R · B26_25 IT_L · B26_26 IT_L

### Validation clinique requise : 21 landmarks

Les 20 REVIEW + 1 UNRESOLVABLE_REVIEW (B26_26 IT_R).

---

## 7. Traitement de B26_26 IT_R — cas non résoluble

| Attribut | Valeur |
|----------|--------|
| **Statut QA** | **UNRESOLVABLE_REVIEW** |
| **Source** | `b6_B26_26_ITR_final_review.csv` |
| **Coordonnées working** | (552.0, 2088.0) — **conservées, non modifiées** |
| **v working** | 2 — **conservé** (pas de v=0 imposé automatiquement) |
| **Diagnostic** | Zone ischiatique D localisable (médial FSD Δx≈205 px) ; apex caudal = gradient bruité sans bord cortical net |
| **Décision** | Annotation inventée **refusée** ; revue supervisée n'a pas permis d'identifier un point caudal certain selon B1/B4 |

### Politique finale B26_26 IT_R

1. **Ne pas modifier** automatiquement les coordonnées working.
2. **Candidat v=0 prioritaire** — arbitrage clinique requis avant label officiel.
3. Statut **UNRESOLVABLE_REVIEW** conservé jusqu'à décision clinique explicite.
4. B26_26 IT_L reste **REVIEW** (dépendance asymétrie vs IT_R incertain).

---

## 8. Synthèse corpus B6 (référence policy)

| Verdict final | N | % |
|---------------|--:|--:|
| **PASS** | 31 | 59,6 % |
| **REVIEW** | 20 | 38,5 % |
| **UNRESOLVABLE_REVIEW** | 1 | 1,9 % |
| **FAIL** | 0 | 0 % |

| Contrôle | Résultat |
|----------|----------|
| Landmarks tracés | 52/52 |
| Duplications | 0 |
| Annotations manquantes | 0 |
| Violations anatomiques structurelles | 0 |

---

## 9. Décision de préparation pour B5

### 9.1 Ce que B1/B4 finalise

| Décision | Statut |
|----------|--------|
| Définition opérationnelle IT (apex caudal contour osseux) | **FINAL** |
| Règles placement, anti-fémur, TD≠IT, R/L, FOV | **FINAL** |
| Règle v=0 (non identifiable vs difficile mais identifiable) | **FINAL** |
| Traitement REVIEW et UNRESOLVABLE | **FINAL** |
| Guide annotateur B4 (sections §3–§8) | **Confirmé** comme base officielle |

### 9.2 Ce que B5 doit encore confirmer (PROVISIONAL)

| Item | Proposition documentée | Action B5 |
|------|------------------------|-----------|
| Ordre 16 keypoints | Index **14** = `IT_R`, **15** = `IT_L` | Confirmation formelle |
| `flip_idx` 16 kp | `[1,0,3,2,5,4,7,6,9,8,11,10,13,12,15,14]` | Validation |
| `kpt_shape` | `[16, 3]` | Mise à jour `data.yaml` (hors scope actuel) |
| Labels YOLO | 47 → **53** colonnes | Création labels officiels (hors scope actuel) |
| `meta/keypoint_order.md` | Extension LM-17/LM-18 | Mise à jour |

### 9.3 Prérequis avant labels officiels et training

| # | Prérequis | Statut |
|:-:|-----------|--------|
| 1 | B1/B4 policy figée | **READY** (`B1_B4_FINAL_POLICY_READY`) |
| 2 | B6 QA globale 52/52 | **READY** (`B6_GLOBAL_QA_REVIEW`) |
| 3 | Validation clinique 21 cas REVIEW/UNRESOLVABLE | **REQUIRED** |
| 4 | Arbitrage v=0 sur 10 candidats (si applicable) | **REQUIRED** |
| 5 | B5 schéma 16 kp confirmé | **PENDING** |
| 6 | Création labels officiels 16 kp | **PENDING** (après 3–5) |
| 7 | Training | **INTERDIT** (T1/T3) |

### 9.4 Ordre recommandé post-policy

```
B1/B4 FINAL (cette étape)
    ↓
Validation clinique ciblée (21 cas)
    ↓
B5 — confirmation schéma 16 kp + flip_idx
    ↓
Promotion working → labels officiels (52 × IT_R/IT_L)
    ↓
Mise à jour data.yaml + keypoint_order.md
    ↓
Training V2-extended (T3 — init V2 best, pas V3)
```

---

## 10. Checklist annotateur finale (B1/B4)

### Avant annotation

- [ ] Cible = tubérosité ischiatique pelvienne (pas TD, pas fémur, pas obturateur)
- [ ] Côté R/L patient vérifié
- [ ] Contour caudal identifiable sans extrapolation
- [ ] Catégorie visibilité B7 consultée (VISIBLE / PARTIAL)

### Placement

- [ ] Point caudal/inférieur du contour osseux ischiatique
- [ ] Anti-fémur vérifié (§3.2)
- [ ] Pas d'extrapolation FOV (§4)
- [ ] Chaque côté annoté indépendamment

### Visibilité

- [ ] `v=2` si repère net et fiable
- [ ] `v=0` si repère non identifiable (pas par confort)
- [ ] Pas de `v=1` par défaut
- [ ] REVIEW documenté si doute persistant — pas de promotion auto

---

## 11. Tableau récapitulatif des règles

| Règle | Statut final | Validation B6 |
|-------|:------------:|:-------------:|
| Définition apex caudal contour osseux | **FINAL** | 31 PASS B1/B4 |
| IT sur ischion, jamais fémur | **FINAL** | 52/52 PASS |
| TD ≠ IT, pas de substitution | **FINAL** | 52/52 PASS |
| R/L côté patient | **FINAL** | 52/52 PASS |
| Pas d'extrapolation FOV | **FINAL** | 49/52 PASS |
| v=2 si identifiable | **FINAL** | v=2 sur 52/52 working |
| v=0 si non identifiable (pas par difficulté) | **FINAL** | 10 candidats listés |
| Ne pas inventer coordonnées | **FINAL** | B26_26 IT_R conservé |
| REVIEW conservés, pas de PASS auto | **FINAL** | 21 cas documentés |
| B26_26 IT_R UNRESOLVABLE | **FINAL** | Statut explicite |

---

## 12. Conclusion

**Statut : `B1_B4_FINAL_POLICY_READY`**

La définition opérationnelle `IT_R` / `IT_L` et l'ensemble des règles B1/B4 sont **figés au niveau documentaire** pour le passage 14 → 16 keypoints. La campagne B6 confirme l'applicabilité de la règle (31 PASS, 0 FAIL structurel) tout en identifiant **21 cas** nécessitant validation clinique avant promotion vers labels officiels.

**Aucune annotation, label officiel, YAML, modèle ou training n'a été modifié.**

---

*Fichiers produits : `bi_ischial_final_policy.md`, `bi_ischial_final_policy.csv` — étape documentaire READ-ONLY.*
