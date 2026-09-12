# Plan B6 — Ré-annotation `IT_R` / `IT_L` sur corpus `new_26`

**Généré :** 2026-08-28  
**Décision :** B6 — plan de ré-annotation **préparatoire** (exécution future)  
**Mode :** documentation uniquement — **aucune modification** des labels, `data.yaml`, modèles, backend ou Flutter  

**Documents liés :**

- `bi_ischial_annotation_guidelines.md` (B4 — guide proposé)
- `bi_ischial_spec.md`
- `bi_ischial_visibility_audit.md` (B7 — fermé)
- `bi_ischial_B1_position_audit.md`
- `meta/keypoint_order.md`
- `annotation_pilot/annotations/new_26/` (JSON source 14 kp)

---

## REMARQUE CLINIQUE — définition de travail

**Enregistrée :** 2026-08-28

> **`IT_R` / `IT_L` = point caudal/inférieur identifiable du contour osseux de chaque tubérosité ischiatique sur la radiographie AP du bassin.**

| Attribut | Valeur |
|----------|--------|
| **STATUS** | **PROPOSED** |
| **Validation clinique** | **CLINICAL VALIDATION REQUIRED** |

**Ce n'est pas** une définition clinique définitivement validée. Ce plan B6 l'utilise comme **référence de travail** pour harmoniser la campagne de ré-annotation, sous réserve de revue clinique.

### Règles explicites

| # | Règle |
|---|--------|
| 1 | **`TD_R` / `TD_L` ne remplacent jamais `IT_R` / `IT_L`** — substitution interdite (A2) |
| 2 | **Cas partiels, superposés ou proches du bord de l'image** — attention particulière ; ne pas inventer de point |
| 3 | **`B26_05`** — **revue particulière obligatoire** (PARTIAL bilatéral, bord image) |

---

## Statut et périmètre B6

| Élément | État actuel | Action B6 (future) |
|---------|-------------|-------------------|
| Labels YOLO `.txt` | **14 keypoints** (47 colonnes) | Ajouter `IT_R`, `IT_L` → **53 colonnes** (après validation B5 + exécution) |
| `data.yaml` | `kpt_shape: [14, 3]` | **Non modifié** dans cette phase |
| Annotations JSON `new_26` | 14 landmarks / image | Enrichir de 2 champs `IT_R`, `IT_L` |
| Modèle V2 / V3 | 14 kp | **Non modifié** ; training interdit (T1) |
| Corpus | 26 images AP bassin | **26/26** annotables (B7) |

**Ce document ne déclenche aucune modification** des artefacts ci-dessus. Il décrit la procédure à exécuter **après** validation clinique de la définition de travail et confirmation B5.

---

## Prérequis avant exécution B6

| ID | Prérequis | Statut |
|----|-----------|--------|
| B7 | Audit visibilité corpus `new_26` | **FERMÉ** |
| B4 | Fiche annotation IT | **PROPOSED** (`bi_ischial_annotation_guidelines.md`) |
| B1 | Définition de travail caudale | **CANDIDATE / PROPOSED** — validation clinique **requise** |
| B5 | Ordre 16 kp + `flip_idx` | **PROVISIONAL** (indices 14–15) |
| — | Revue clinique B26_05 (+ B26_07, 11, 12 recommandée) | **À planifier** |
| — | Brief annotateur + illustrations pilotes | **Recommandé** |

---

## 1. Ordre exact `IT_R` / `IT_L`

### Schéma 16 keypoints proposé (append — B5 PROVISIONAL)

Référence opérationnelle : `bi_ischial_spec.md` §15, `missing_measurements_spec.md` §3.4, `keypoint_order.md`.

| Index YOLO | Nom | Côté patient | ID source | Notes |
|:----------:|-----|--------------|-----------|-------|
| 0–13 | *(inchangés)* | — | LM-01–LM-14 | Voir `keypoint_order.md` |
| **14** | **`IT_R`** | Droit (gauche image) | LM-17 | **Nouveau** |
| **15** | **`IT_L`** | Gauche (droite image) | LM-18 | **Nouveau** |

### Ordre d'annotation recommandé (par image)

1. **Ne pas modifier** les 14 landmarks existants (sauf correction d'erreur signalée en QC).
2. **`IT_R`** — tubérosité ischiatique droite patient.
3. **`IT_L`** — tubérosité ischiatique gauche patient.
4. Contrôles R/L, TD≠IT, visibilité — voir checklist §4.

### `flip_idx` proposé (16 kp)

```
[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14]
```

Permutation **14 ↔ 15** (`IT_R` ↔ `IT_L`). **Non appliqué** tant que B5 non confirmé et `data.yaml` non mis à jour.

### Format label futur (référence — non modifié maintenant)

| Paramètre | Actuel | Après B6 + B5 |
|-----------|--------|---------------|
| Colonnes | **47** (5 + 14×3) | **53** (5 + 16×3) |
| Triplet IT | — | `kpt14_x kpt14_y kpt14_v` (`IT_R`), puis `kpt15_*` (`IT_L`) |
| `v=0` | `(0, 0, 0)` | Idem |

---

## 2. Procédure de ré-annotation (26 images)

### Phase 0 — Préparation (1 session)

| Étape | Action |
|-------|--------|
| 0.1 | Lire `bi_ischial_annotation_guidelines.md` (REMARQUE CLINIQUE + §1–§8) |
| 0.2 | Lire `docs/annotation_guidelines.md` §1.1–§1.2 (R/L, codes `v`) |
| 0.3 | Brief clinique : définition de travail **PROPOSED** ; B26_05 = revue particulière |
| 0.4 | Vérifier accès images : `datasets/yolo_pose_new_26/images/train/` (21) + `images/val/` (5) |
| 0.5 | Vérifier annotations JSON source : `annotation_pilot/annotations/new_26/B26_XX.json` |

### Phase 1 — Annotation (26 images)

**Ordre suggéré du corpus :**

| Priorité | Images | Motif |
|----------|--------|-------|
| 1 — Pilote facile | **B26_01** | Cas standard VISIBLE / EXCELLENTE |
| 2 — Cas limites | **B26_05**, **B26_12**, **B26_07**, **B26_11** | Revue manuelle B7 |
| 3 — Reste train | B26_02–04, 06, 08–09, 14–16, 18–19, 21–25 | VISIBLE |
| 4 — Val | B26_10, 13, 17, 20, 26 | VISIBLE |

**Par image :**

1. Ouvrir l'image AP bassin (`B26_XX.png`).
2. Charger l'annotation 14 kp existante (référence — **ne pas déplacer** les points MVP sauf correction validée).
3. Localiser la tubérosité ischiatique **droite patient** (gauche image).
4. Placer **`IT_R`** sur le point caudal/inférieur identifiable du contour osseux (**proposition de travail**) ou `v=0`.
5. Localiser la tubérosité ischiatique **gauche patient** (droite image).
6. Placer **`IT_L`** (même règle) ou `v=0`.
7. Appliquer la checklist §4 avant passage à l'image suivante.
8. **B26_05** : annoter seulement après revue clinique dédiée ou en session supervisée.

### Phase 2 — Revue clinique ciblée

| Image | Action |
|-------|--------|
| **B26_05** | **Revue particulière obligatoire** — trancher `v=2` vs `v=0` bilatéral |
| B26_07 | Confirmer repère IT malgré gaz intestinal |
| B26_11 | Confirmer R/L et cohérence sous rotation pelvienne légère |
| B26_12 | Confirmer annotabilité `v=2` malgré marge caudale réduite |

### Phase 3 — Export vers artefacts YOLO (hors scope immédiat)

**Non exécuté** dans cette phase documentaire. Après QC B6 validé + B5 confirmé :

- Enrichir JSON `new_26` avec `IT_R`, `IT_L` (`x`, `y`, `v`).
- Régénérer labels `.txt` 53 colonnes.
- Mettre à jour `data.yaml`, `keypoint_order.md` (B5).

---

## 3. Liste des 26 images

| Image | Split | IT_R B7 | IT_L B7 | Qualité | Revue particulière |
|-------|-------|---------|---------|---------|:------------------:|
| B26_01 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_02 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_03 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_04 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| **B26_05** | train | **PARTIAL** | **PARTIAL** | MOYENNE | **Oui — obligatoire** |
| B26_06 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_07 | train | VISIBLE | VISIBLE | BONNE | Oui (recommandée) |
| B26_08 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_09 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_10 | val | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_11 | train | VISIBLE | VISIBLE | BONNE | Oui (recommandée) |
| B26_12 | train | VISIBLE | VISIBLE | BONNE | Oui (recommandée) |
| B26_13 | val | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_14 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_15 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_16 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_17 | val | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_18 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_19 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_20 | val | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_21 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_22 | train | VISIBLE | VISIBLE | BONNE | Non |
| B26_23 | train | VISIBLE | VISIBLE | BONNE | Non |
| B26_24 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_25 | train | VISIBLE | VISIBLE | EXCELLENTE | Non |
| B26_26 | val | VISIBLE | VISIBLE | EXCELLENTE | Non |

Source : `bi_ischial_visibility_audit.csv`

---

## 4. Checklist annotateur

### Avant annotation (par image)

- [ ] **Bonne structure** — tubérosité ischiatique, pas teardrop / obturateur / pubis
- [ ] **Bon côté R/L** — `IT_R` = droit patient (gauche image) ; latéralité vérifiée
- [ ] **Contour osseux identifiable** — bord caudal proposé visible sans extrapolation
- [ ] **Position conforme à la définition de travail** — point caudal/inférieur du contour (**PROPOSED**, validation clinique en cours)
- [ ] **TD ≠ IT** — `TD_*` existants non utilisés comme substitut

### Pendant annotation — cas à attention particulière

- [ ] **Tubérosité partiellement visible** — `v=0` ou revue si repère caudal douteux
- [ ] **Superposition osseuse** — zoom ; si doute persistant → `v=0`
- [ ] **Proximité bord image** — pas d'extrapolation hors FOV ; **B26_05** → revue clinique
- [ ] **Mauvaise qualité** — `v=0` si contour non fiable

### Après annotation (par image)

- [ ] **`IT_R` vérifié** — côté droit patient, proposition respectée ou `v=0`
- [ ] **`IT_L` vérifié** — côté gauche patient, idem
- [ ] **Aucun remplacement par TD** — distance et anatomie distinctes
- [ ] **Visibilité correctement renseignée** — `v=2` seulement si net ; pas de `v=2` par confort
- [ ] **Cas ambigu marqué** — `v=0` ou flag revue ; pas de copie miroir R→L

### Cas particulier B26_05

- [ ] **Revue clinique effectuée** avant validation finale
- [ ] Décision documentée : `v=2` bilatéral **ou** `v=0` (un ou deux côtés)
- [ ] Si `v=0` unilatéral ou bilatéral → `BI_ISCHIAL` non calculable pour ce cliché

---

## 5. Contrôle qualité prévu (post-annotation)

### 5.1 Contrôles automatiques (adaptation future)

Inspirés de `annotation_pilot/annotations/new_26/validation_summary.md` — **à étendre** pour 16 kp :

| Contrôle | Critère |
|----------|---------|
| Présence champs | `IT_R`, `IT_L` avec `x`, `y`, `v` dans chaque JSON |
| Coordonnées | `0 ≤ x < width`, `0 ≤ y < height` si `v>0` |
| `v=0` | `x=null`, `y=null` (convention JSON existante) |
| Comptage | 26 × 16 = **416** landmarks attendus (vs 364 actuels) |
| Doublons / bords | Pas de coordonnées aberrantes |

### 5.2 Contrôles anatomiques (revue humaine)

| Contrôle | Attendu | Si échec |
|----------|---------|----------|
| Latéralité | `IT_R` à gauche image, `IT_L` à droite image | Corriger inversion |
| TD vs IT | `IT_*` latéral/caudal aux teardrops ; pas de coïncidence TD/IT | Corriger |
| Hauteur caudale | `IT_*` plus caudal que `TD_*` homolatéral (contrôle grossier) | Revue |
| Symétrie | Hauteurs R/L proches si cliché peu incliné | Vérifier R/L ; noter QC |
| Pas de miroir | Coordonnées R ≠ copie L | Réannoter |
| `BI_ISCHIAL` | Les deux `IT_*` en `v=2` requis pour calcul futur | Documenter si un côté `v=0` |

### 5.3 Revue clinique post-corpus

| Étape | Contenu |
|-------|---------|
| Revue B26_05 | Validation ou rejet des points ; décision `v` figée |
| Échantillon 10 % | Double lecture sur 2–3 images aléatoires + tous cas limites |
| Consensus | Documenter écarts ; ajuster guide B4 si nécessaire |
| Clôture B1 | Confirmer ou rejeter définition de travail caudale |

### 5.4 Critères d'acceptation corpus B6

| Critère | Seuil proposé |
|---------|---------------|
| Images avec JSON enrichi | **26/26** |
| `IT_R` + `IT_L` renseignés (v=0 ou v=2) | **26/26** |
| Erreurs bloquantes QC auto | **0** |
| B26_05 revue clinique | **Obligatoire** |
| Cas limites B26_07, 11, 12 | Revue **recommandée** |
| Training | **Interdit** jusqu'à clôture B5 + validation clinique B1 |

---

## 6. Interdictions (rappel)

| Interdit | Raison |
|----------|--------|
| Modifier labels `.txt` YOLO **maintenant** | Hors scope ; B6 planification uniquement |
| Modifier `data.yaml` | B5 non confirmé |
| Entraîner V2/V3 | T1 — B1–B6 ouverts |
| Utiliser `TD_*` comme `IT_*` | A2 |
| Présenter la définition caudale comme validée cliniquement | PROPOSED / CLINICAL VALIDATION REQUIRED |
| Annoter par symétrie miroir | `annotation_guidelines.md` §3 |

---

## 7. Synthèse exécutive

```
B6 = PLANNED (procédure documentée — exécution future)
B1 = CANDIDATE / PROPOSED (définition de travail caudale)
Corpus = 26 images, 0 exclusion visibilité (B7)
Revue obligatoire = B26_05
Ordre annotation = IT_R (index 14) puis IT_L (index 15)
Labels / YAML / modèle = NON MODIFIÉS dans cette phase
```

**Prochaine étape :** validation clinique de la définition de travail → exécution annotation selon §2 → QC §5 → B5 (YAML/labels) → B6 clôturé.

---

*Plan B6 — seuls `bi_ischial_B6_annotation_plan.md`, `bi_ischial_B6_annotation_plan.csv` créés ; documentation bi-ischiale mise à jour (`bi_ischial_annotation_guidelines.md`, `bi_ischial_spec.md`) ; aucun label, YAML, modèle ou code modifié.*
