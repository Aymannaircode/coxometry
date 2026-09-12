# Spécification — Bi-ischial (`IT_R`, `IT_L`, `BI_ISCHIAL`)

**Généré :** 2026-08-28  
**Mode :** spécification uniquement — **aucune implémentation**, **aucune modification** du code, dataset, labels, YAML, V2, V3, backend ou Flutter  
**Sources :** `docs/landmark_specification.md`, `docs/annotation_guidelines.md`, `docs/dataset_analysis.md`, `docs/dataset1_analysis.md`, `docs/retuve_feasibility_test.md`, `datasets/yolo_pose_new_26/missing_measurements_spec.md`, `datasets/yolo_pose_new_26/missing_measurements_audit.md`, `datasets/yolo_pose_new_26/meta/keypoint_order.md`, `datasets/yolo_pose_new_26/data.yaml`

**Statut global :** **NEW LANDMARKS REQUIRED** + **PROPOSED** (définition de travail B1 CANDIDATE — validation clinique requise ; métrique de sortie, calibration)

**REMARQUE CLINIQUE (2026-08-28) — définition de travail proposée :**

> `IT_R` / `IT_L` = point caudal/inférieur identifiable du contour osseux de chaque tubérosité ischiatique sur la radiographie AP du bassin.

| Attribut | Valeur |
|----------|--------|
| **STATUS B1** | **CANDIDATE / PROPOSED** |
| **Validation clinique** | **CLINICAL VALIDATION REQUIRED** — **pas** une définition clinique définitivement validée |

**Règles explicites :** `TD_*` ne remplace jamais `IT_*` (A2) · cas partiels / superposés / bord image = attention particulière · **B26_05** = revue particulière (B7).

---

## Périmètre et contraintes

| Contrainte | Statut |
|------------|--------|
| Modification dataset / labels / YAML | **Interdite** (spec uniquement) |
| Modification modèle V2 | **Interdite** |
| Training | **Interdit** tant que B1–B7 ouverts (T1, T3) |
| Implémentation mesure | **Hors scope** |

---

## 1. Définition anatomique exacte de `IT_R`

### Ce que la documentation affirme

| Champ | Valeur documentée |
|-------|-------------------|
| **Nom** | `IT_R` |
| **ID source proposé** | LM-17 (`docs/landmark_specification.md` §11 — extension catalogue LM-17+) |
| **Structure** | **Tubérosité ischiatique** droite |
| **Côté** | **Droit patient** (gauche de l'image en AP) |
| **Rôle** | Extrémité **droite** de la **ligne bi-ischiatique** (§11) |
| **Mesures** | Ligne bi-ischiatique (hors MVP actuel) |
| **Statut schéma 14 kp** | **Absent** — interdit en MVP (`annotation_guidelines.md` §1.4) |

### Ce que la documentation n'affirme pas

- Définition osseuse précise (sommet inférieur vs centre vs bord caudal vs point le plus inférieur identifiable).
- **Définition de travail (2026-08-28) :** point caudal/inférieur identifiable du contour osseux — **PROPOSED / CLINICAL VALIDATION REQUIRED** (`bi_ischial_annotation_guidelines.md` REMARQUE CLINIQUE).

**Statut :** **PARTIELLEMENT DEFINED** — structure et côté documentés ; **position = CANDIDATE B1 (PROPOSED, validation clinique requise)**

---

## 2. Définition anatomique exacte de `IT_L`

### Ce que la documentation affirme

| Champ | Valeur documentée |
|-------|-------------------|
| **Nom** | `IT_L` |
| **ID source proposé** | LM-18 |
| **Structure** | **Tubérosité ischiatique** gauche |
| **Côté** | **Gauche patient** (droite de l'image en AP) |
| **Rôle** | Extrémité **gauche** de la **ligne bi-ischiatique** (§11) |
| **Mesures** | Ligne bi-ischiatique (hors MVP actuel) |
| **Statut schéma 14 kp** | **Absent** — interdit en MVP (`annotation_guidelines.md` §1.4) |

### Ce que la documentation n'affirme pas

- Même ambiguïté de position exacte que `IT_R` (sommet vs centre vs bord — **B1**).

**Statut :** **PARTIELLEMENT DEFINED** — structure et côté documentés ; **position = CANDIDATE B1 (PROPOSED, validation clinique requise)**

---

## 3. Position exacte du landmark sur chaque tubérosité

### État documenté

| Source | Contenu |
|--------|---------|
| §11 | Exige `IT_R` / `IT_L` sans préciser le point sur la tubérosité |
| Audit §3 | Proposition **non validée** : « point le plus caudal / inférieur identifiable » |
| Décision **B1** | Figer position (sommet inférieur, centre, bord) **avec illustrations** |

**Questions ouvertes (B1) :**

- Sommet **inférieur** de la tubérosité ?
- **Centre** géométrique de la tubérosité projetée ?
- Bord **caudal** / inférieur du contour osseux ?
- Point le plus **inférieur identifiable** sur l'AP ?

**Statut :** **SPECIFICATION REQUIRED (B1)**

---

## 4. Convention R/L

### Règles documentées (figées pour le projet)

**Source :** `docs/annotation_guidelines.md` §1.1, `docs/landmark_specification.md` §2

| Règle | Détail |
|-------|--------|
| Vue | Radiographie **AP bassin** |
| Droite patient | À **gauche** de l'image |
| Gauche patient | À **droite** de l'image |
| Label `IT_R` | Toujours côté **droit patient** (gauche image) |
| Label `IT_L` | Toujours côté **gauche patient** (droite image) |
| Interdiction | **Ne jamais** inverser R/L selon « gauche/droite écran » sans vérifier le côté patient |

**Statut :** **DEFINED** (convention R/L identique aux 14 landmarks MVP)

---

## 5. Cas où la tubérosité est partiellement visible

### État documenté

**Aucune fiche d'annotation dédiée `IT_*`** dans `annotation_guidelines.md` (14 landmarks uniquement).

**Règles générales de visibilité applicables par analogie** (`annotation_guidelines.md` §1.2) :

| Code `v` | Signification | Conduite |
|----------|---------------|----------|
| **2** | Point net, localisable sans doute raisonnable | Structure clairement visible |
| **1** | Point estimé (contours flous) | Uniquement si clinicien a validé l'usage de `v=1` — **par défaut, préférer `v=0`** |
| **0** | Non annoté / non fiable / hors champ | Si placement = deviner |

**Règle d'or documentée :** ne jamais placer un point « pour remplir le schéma ».

**Conduite spécifique tubérosité partiellement visible :** **SPECIFICATION REQUIRED (B1, B4, B7)**

---

## 6. Cas où le landmark est ambigu

### Ambiguïtés documentées (liées, non résolues pour `IT_*`)

| Code | Sujet | Lien bi-ischial | Décision MVP / statut |
|------|-------|-----------------|----------------------|
| **A2** | Horizontal pelvien | Teardrops vs ischions | MVP = teardrops ; ischions = landmark **futur**, pas remplacement silencieux |
| **B1** | Position exacte sur tubérosité | Sommet vs centre vs bord | **Non validé** |
| Pilote A2 | Teardrop illisible | Tentation d'utiliser ischions pour **TD** | Journaliser — **ne pas confondre** avec annotation `IT_*` |

**Cas ambigus non documentés pour `IT_*` :**

- Superposition osseuse / rotation pelvienne forte
- Tubérosité vs ligne ilio-ischiatique
- Un seul côté visible
- Obésité / contrast faible

**Statut :** **SPECIFICATION REQUIRED (B1, B4, B7)**

---

## 7. Relation avec `TD_R` / `TD_L`

### Ce que la documentation affirme

| Élément | Relation documentée |
|---------|---------------------|
| `TD_*` | Teardrop inférieur — base de `ITH` = droite(`TD_R`, `TD_L`) — **horizontal pelvien MVP** |
| `IT_*` | Tubérosités ischiatiques — base de `BI_ISCHIAL` — **hors MVP** §11 |
| Ambiguïté **A2** | Certains protocoles utilisent ischions **à la place** des teardrops pour l'horizontal ; le MVP **fixe les teardrops** |
| Extension §11 | Ischions = landmark optionnel **futur**, pas remplacement silencieux |
| Guide §2.1 | Repérage teardrop « entre tête fémorale et **ligne ilio-ischiatique** » — structures voisines mais **distinctes** |
| Pilote A2 | Teardrop illisible → tentation ischions — à journaliser pour **TD**, pas substitution automatique |

**Dépendance `BI_ISCHIAL` ↔ `ITH` pour le calcul de sortie :** **non documentée** (voir §10).

**Statut relation structurelle :** **DEFINED** — landmarks **distincts**, rôles **distincts**

---

## 8. Confirmation explicite : `TD` ne remplace PAS `IT`

### Preuves documentaires

| Source | Affirmation |
|--------|-------------|
| §11 | Ligne bi-ischiatique **requiert** `IT_R` / `IT_L` — non couverte par le schéma MVP |
| Ambiguïté **A2** (§8) | Teardrops vs ischions : MVP = **`TD_*`** ; autre référence = landmark futur, **pas remplacement silencieux** |
| §4 LM-01 | Ischions = « landmark optionnel futur, **pas un remplacement silencieux** » des teardrops |
| `annotation_guidelines.md` §1.4 | Tubérosités ischiatiques **interdites** en MVP (sauf futur schéma) |
| `annotation_guidelines.md` §2.1 | « Ne pas annoter les **tubérosités ischiatiques** » à la place du teardrop ; « Ne pas substituer silencieusement les ischions » |
| `missing_measurements_spec.md` §3.3 | « `TD_R` / `TD_L` peuvent-ils remplacer ? → **Non** — A2 interdit le remplacement silencieux » |
| `dataset_analysis.md` §14 | Masques `ischium` ≠ keypoints tubérosité annotés |

### Verdict explicite

```
TD_R / TD_L  ≠  IT_R / IT_L
Les teardrops ne remplacent PAS les tubérosités ischiatiques pour la ligne bi-ischiatique.
```

**Statut :** **DEFINED** — confirmation explicite sans ambiguïté dans la doc projet

---

## 9. Définition géométrique de la ligne `BI_ISCHIAL`

### Construction documentée

**Source :** §11 + dérivation logique spec (`missing_measurements_spec.md` §3.2, audit §3)

```
BI_ISCHIAL = droite(IT_R, IT_L)
```

| Propriété | État documenté |
|-----------|----------------|
| Type | Droite 2D passant par les deux tubérosités |
| Landmarks requis | `IT_R` et `IT_L` (tous deux) |
| Annotée ? | **Non** — ligne **dérivée** (comme `ITH`, `SHAFT`) |
| Usage exact | **Non détaillé** — inclinaison pelvienne ? distance ? angle ? (**B2**) |

**Statut construction :** **DEFINED** (ligne = `IT_R` → `IT_L`)  
**Statut usage / métrique :** **SPECIFICATION REQUIRED (B2)**

---

## 10. Sortie attendue : distance, angle, autre métrique

### État documenté

**Non documenté dans le projet** (`missing_measurements_spec.md` §3.1, audit §3) :

| Option évoquée | Source | Statut |
|----------------|--------|--------|
| **Angle** de la ligne vs horizontal | Spec §3.1, B2 | **SPECIFICATION REQUIRED** |
| **Distance** inter-tubérosités `IT_R`–`IT_L` | Spec §3.1, B2 | **SPECIFICATION REQUIRED** |
| **Inclinaison pelvienne** (référence) | Spec §3.1, B2 | **SPECIFICATION REQUIRED** |
| Combinaison (angle + distance) | B2 | **SPECIFICATION REQUIRED** |
| Référence horizontale (`ITH` / teardrops ?) | Non documentée pour bi-ischial | **SPECIFICATION REQUIRED** |

**Code :** pas de `bi_ischial_angle()`, `bi_ischial_distance()` dans `mvp_geometry/` (audit).

**Statut :** **SPECIFICATION REQUIRED (B2)**

---

## 11. Unité de sortie

### État documenté

| Sortie hypothétique | Unité probable (doc) | Statut |
|---------------------|----------------------|--------|
| Angle | Degrés (analogie VCE/Tönnis/CCD) | **SPECIFICATION REQUIRED** — dépend de B2 |
| Distance | mm (analogie offset §11) | **SPECIFICATION REQUIRED** — dépend de B2 |
| Inclinaison pelvienne | Non définie | **SPECIFICATION REQUIRED** |

**Statut :** **SPECIFICATION REQUIRED (B2)**

---

## 12. Calibration nécessaire ou non

### État documenté

| Question | Réponse doc projet |
|----------|-------------------|
| Calibration requise si **angle** seul ? | **Non documentée** — mesures angulaires MVP actuelles sans mm/px |
| Calibration requise si **distance** mm ? | **Probable** (`missing_measurements_spec.md` §3.5) — **à confirmer cliniquement** |
| Méthode mm/px | **Non définie** (B3 — même problématique que offset fémoral F3) |
| Lien avec `ITH` / teardrops pour calibration | **Non documenté** |

**Statut :** **SPECIFICATION REQUIRED (B2, B3)** — calibration **conditionnelle** à la métrique choisie

---

## 13. Conditions de validité / invalidité

### Conditions documentées ou dérivables strictement

| Condition | Conduite | Source | Portée |
|-----------|----------|--------|--------|
| `IT_R` ou `IT_L` absent du schéma 14 kp | Mesure bi-ischiale **impossible** | §11 | Globale |
| `IT_*` interdit en MVP actuel | Pas d'annotation / pas de calcul | `annotation_guidelines.md` §1.4 | MVP 14 kp |
| Substitution `TD` pour `IT` | **Interdite** | A2, §2.1 | Annotation |
| Visibilité `v=0` (règle générale) | Ne pas inventer de point | §1.2 guidelines | Annotation |
| Segmentation `ischium` (Dataset2) | **Insuffisante** — pas de keypoint tubérosité | `dataset_analysis.md` §14 | Dataset |
| Modèle V2 / Retuve | Pas de slot `IT_*` ; bi-ischial **impossible** | `keypoint_order.md`, `retuve_feasibility_test.md` | Modèle |

### Conditions **non** documentées spécifiquement pour bi-ischial

| Condition | Statut |
|-----------|--------|
| Un seul `IT_*` en `v=0` → mesure impossible ? | **SPECIFICATION REQUIRED** (logique : 2 points requis pour une droite) |
| Seuil de qualité / distance minimale `IT_R`–`IT_L` | **SPECIFICATION REQUIRED** |
| Rotation pelvienne forte → invalidité | **SPECIFICATION REQUIRED** (A8 documenté pour CCD, pas bi-ischial) |
| Seuils cliniques normal / pathologique | **SPECIFICATION REQUIRED** |

**Statut global :** **SPECIFICATION REQUIRED (B2, B4, B7)**

---

## 14. Passage de 14 à 16 keypoints

### État documenté (planifié, non implémenté)

**Source :** `missing_measurements_spec.md` §3.4, audit, `keypoint_order.md`

| Paramètre | Valeur 14 kp (actuel) | Valeur 16 kp (proposée) |
|-----------|----------------------|-------------------------|
| Nombre keypoints | 14 | **16** (+ `IT_R`, `IT_L`) |
| IDs landmarks | LM-01–LM-14 | + LM-17, LM-18 (§11 : LM-17+ sans casser LM-01–16 ; `ALB` = LM-15/16 optionnels) |
| Modèle V2 | Entraîné 14 kp | **Incompatible** sans retraining |
| Annotations `new_26` | 14 landmarks / image | **Ré-annotation** `IT_R`, `IT_L` requise (B6) |
| Split train/val | 21/5 | Peut rester inchangé |
| Type de changement | — | **Changement de schéma**, pas simple formule |

**Statut :** **PLANNED — SPECIFICATION REQUIRED (B5)** pour validation ordre exact indices 14–15

---

## 15. Ordre exact des 16 keypoints

### Ordre actuel 14 kp (implémenté — référence)

**Source :** `datasets/yolo_pose_new_26/meta/keypoint_order.md`, `data.yaml`

| Index | Nom | ID source |
|------:|-----|-----------|
| 0 | TD_R | LM-01 |
| 1 | TD_L | LM-02 |
| 2 | FHC_R | LM-03 |
| 3 | FHC_L | LM-04 |
| 4 | ASL_R | LM-05 |
| 5 | ASL_L | LM-06 |
| 6 | ASM_R | LM-07 |
| 7 | ASM_L | LM-08 |
| 8 | FNM_R | LM-09 |
| 9 | FNM_L | LM-10 |
| 10 | FSP_R | LM-11 |
| 11 | FSP_L | LM-12 |
| 12 | FSD_R | LM-13 |
| 13 | FSD_L | LM-14 |

### Extension proposée 16 kp (non figée — B5)

**Source :** `missing_measurements_spec.md` §3.4

| Index | Nom | ID source |
|------:|-----|-----------|
| 14 | IT_R | LM-17 (proposé) |
| 15 | IT_L | LM-18 (proposé) |

**Note :** `docs/landmark_specification.md` §9 propose un ordre alternatif (blocs par côté) et mentionne `ALB` en append indices 14–15 — **différent** de l'ordre **implémenté** dans `keypoint_order.md` / `data.yaml`. Pour le lot `new_26`, la référence opérationnelle est **`keypoint_order.md`**.

**Statut :** **PROVISIONAL** (append 14–15 documenté) — **SPECIFICATION REQUIRED (B5)** pour confirmation formelle

---

## 16. Nouveau `flip_idx`

### Valeur actuelle (14 kp)

**Source :** `keypoint_order.md`, `data.yaml`

```
[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]
```

Permutation R↔L par paire.

### Extension proposée (16 kp)

**Source :** `missing_measurements_spec.md` §3.4

```
[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14]
```

Indices **14 ↔ 15** permutés (`IT_R` ↔ `IT_L`).

**Statut :** **PROVISIONAL** — **SPECIFICATION REQUIRED (B5)** pour validation

---

## 17. Impact sur les labels YOLO

### État documenté (futur — non modifié)

**Source :** `keypoint_order.md`, `missing_measurements_spec.md` §3.4

| Paramètre | 14 kp (actuel) | 16 kp (futur) |
|-----------|----------------|---------------|
| Format label `.txt` | `class cx cy w h` + 14×(`x y v`) | + 2×(`x y v`) pour `IT_R`, `IT_L` |
| Colonnes totales | **47** (5 + 14×3) | **53** (5 + 16×3) |
| Visibilité | MVP `v=2` → YOLO `v=2` ; `v=0` → `(0,0,0)` | Même mapping attendu |
| Contenu `new_26` | 26 images, 14 kp | **Ré-annotation** complète des 2 nouveaux points (B6) |
| Compatibilité V2 | Labels 47 cols | Labels 53 cols **incompatibles** |

**Statut :** **DOCUMENTED (impact futur)** — **aucune modification** dans cette révision

---

## 18. Impact sur `data.yaml`

### État actuel (lecture seule)

**Source :** `datasets/yolo_pose_new_26/data.yaml`

```yaml
kpt_shape: [14, 3]
flip_idx: [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]
kpt_names: [TD_R, TD_L, FHC_R, FHC_L, ASL_R, ASL_L, ASM_R, ASM_L, FNM_R, FNM_L, FSP_R, FSP_L, FSD_R, FSD_L]
```

### Impact futur documenté (non appliqué)

| Champ | Valeur future proposée |
|-------|------------------------|
| `kpt_shape` | `[16, 3]` |
| `flip_idx` | `[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14]` |
| `kpt_names` | … existants … + `IT_R`, `IT_L` |

**Statut :** **DOCUMENTED (impact futur)** — **SPECIFICATION REQUIRED (B5)** avant modification réelle

---

## 19. Impact sur le training futur

### Politique documentée

**Source :** `missing_measurements_spec.md` §5.4

| Règle | Contenu |
|-------|---------|
| **T1** | **Ne pas entraîner** bi-ischial tant que **B1–B7** ouverts |
| **T3** | Extension bi-ischiale ⇒ **16 keypoints** ⇒ **retraining obligatoire** |
| Init modèle | Repartir de **V2 best**, **V3 NO-GO** |
| Prérequis | Spec figée + **ré-annotation** `IT_R`/`IT_L` sur `new_26` (B6) + guide illustré (B4) |
| Split | 21/5 peut rester ; contenu labels enrichi |
| Backend / Flutter | Extension schémas — hors scope actuel |

**Ordre recommandé (audit E_step_order) :**

1. Spec + annotation `IT_R`/`IT_L`  
2. Extension dataset YOLO  
3. Training futur **uniquement après** spec + annotations

**Statut :** **DEFINED (politique)** — exécution **future**, interdite maintenant

---

## 20. Visibilité de `IT_R` / `IT_L` sur les images `new_26`

### État documenté

| Fait | Source |
|------|--------|
| Corpus `new_26` | 26 radiographies AP bassin adulte |
| Annotations actuelles | **14 landmarks uniquement** — **aucune** annotation `IT_*` |
| Audit visibilité tubérosités | **Non réalisé** — décision **B7** ouverte |
| Dataset2 / DDH | Pas de keypoints tubérosité ; masques `ischium` ≠ point IT |
| Retuve / modèles tiers | Tubérosités ischiatiques **absentes** |
| Contexte annotation inférieur bassin | A7 documente FOV court pour **diaphyse** (`FSD`) — problème voisin (cadrage bas) mais **pas d'audit IT** |

### Ce que la documentation n'affirme pas

- Taux de visibilité `IT_R`/`IT_L` sur les 26 cas
- Nombre d'images avec tubérosité unilatérale / bilatérale
- Seuil acceptable de `v=0` avant abandon bi-ischial sur AP bassin

**Statut :** **SPECIFICATION REQUIRED (B7)** — audit de visibilité **à mener** sur `new_26` avant re-annotation et training

---

## Synthèse landmarks

| Landmark | Dans 14 kp ? | Rôle bi-ischial | Statut |
|----------|:------------:|-----------------|--------|
| `IT_R` | Non (futur LM-17) | Extrémité droite `BI_ISCHIAL` | **NEW LANDMARK REQUIRED** |
| `IT_L` | Non (futur LM-18) | Extrémité gauche `BI_ISCHIAL` | **NEW LANDMARK REQUIRED** |
| `TD_R` / `TD_L` | Oui | Horizontal pelvien `ITH` — **≠ bi-ischial** | Déjà annotés ; **ne remplacent pas** `IT_*` |
| Ligne `BI_ISCHIAL` | Dérivée | `droite(IT_R, IT_L)` | Construction **DEFINED** ; usage **SPECIFICATION REQUIRED** |

### Verdict 14 landmarks

```
Les 14 landmarks actuels sont INSUFFISANTS pour la ligne bi-ischiatique.
IT_R et IT_L sont REQUIS explicitement (§11).
TD_R / TD_L ne substituent PAS IT_R / IT_L (A2).
```

---

## Décisions cliniques ouvertes

| ID | Sujet |
|----|-------|
| **B1** | Position exacte sur tubérosité + illustrations |
| **B2** | Sortie : angle vs distance vs inclinaison pelvienne |
| **B3** | Calibration mm/px si distance |
| **B4** | Fiches annotation `IT_R`/`IT_L` dans `annotation_guidelines.md` |
| **B5** | Ordre keypoints 16 et `flip_idx` |
| **B6** | Ré-annotation `new_26` |
| **B7** | Visibilité tubérosités sur corpus AP |

---

## Tableau final — Décision | Statut | Action nécessaire

| Décision | Statut | Action nécessaire |
|----------|--------|-------------------|
| **D1 — Structure `IT_R` (tubérosité droite)** | **PARTIELLEMENT DEFINED** | **B1** — position exacte |
| **D2 — Structure `IT_L` (tubérosité gauche)** | **PARTIELLEMENT DEFINED** | **B1** — position exacte |
| **D3 — Position exacte sur tubérosité** | **SPECIFICATION REQUIRED** | **B1** + illustrations |
| **D4 — Convention R/L** | **DEFINED** | Aucune |
| **D5 — Tubérosité partiellement visible** | **SPECIFICATION REQUIRED** | **B4, B7** — fiches + audit |
| **D6 — Landmark ambigu** | **SPECIFICATION REQUIRED** | **B1, B4, B7** |
| **D7 — Relation `TD` / `IT`** | **DEFINED** | Aucune — structures distinctes |
| **D8 — `TD` ne remplace PAS `IT`** | **DEFINED** | Aucune — confirmation explicite A2 |
| **D9 — Ligne `BI_ISCHIAL = droite(IT_R, IT_L)`** | **DEFINED** | Aucune pour la construction |
| **D10 — Métrique de sortie (angle / distance / autre)** | **SPECIFICATION REQUIRED** | **B2** |
| **D11 — Unité de sortie** | **SPECIFICATION REQUIRED** | **B2** |
| **D12 — Calibration mm/px** | **SPECIFICATION REQUIRED** | **B2, B3** — conditionnelle |
| **D13 — Validité / invalidité** | **SPECIFICATION REQUIRED** | **B2, B4, B7** |
| **D14 — Passage 14 → 16 kp** | **PLANNED** | **B5, B6** avant exécution |
| **D15 — Ordre 16 keypoints** | **PROVISIONAL** | **B5** — append 14=`IT_R`, 15=`IT_L` |
| **D16 — `flip_idx` 16 kp** | **PROVISIONAL** | **B5** — permuter 14↔15 |
| **D17 — Impact labels YOLO (47→53 cols)** | **DOCUMENTED** | Appliquer après B6, pas maintenant |
| **D18 — Impact `data.yaml`** | **DOCUMENTED** | Appliquer après B5, pas maintenant |
| **D19 — Training futur** | **DEFINED (POLICY)** | T1/T3 — après B1–B7 ; init V2, pas V3 |
| **D20 — Visibilité sur `new_26`** | **SPECIFICATION REQUIRED** | **B7** — audit à mener |
| **D21 — 14 kp suffisants ?** | **DEFINED (NON)** | **`IT_R` + `IT_L` obligatoires** |

---

## Préconditions avant passage 14 → 16 keypoints

Les conditions suivantes doivent être **toutes** remplies avant toute modification de labels, YAML, dataset ou lancement de training :

### Spécification clinique (bloquants B1–B3)

- [ ] **B1.** Position exacte de `IT_R` / `IT_L` sur la tubérosité ischiatique figée et **illustrée**
- [ ] **B2.** Métrique de sortie figée (angle, distance, inclinaison pelvienne, ou combinaison) + référence horizontale si angle
- [ ] **B3.** Méthode de calibration mm/px définie **si** la sortie inclut une distance en mm

### Documentation annotation (bloquant B4)

- [ ] **B4.** Fiches d'annotation `IT_R` / `IT_L` rédigées dans `annotation_guidelines.md` (visibilité partielle, ambiguïtés, cas limites)

### Schéma technique YOLO (bloquant B5)

- [ ] **B5.** Ordre des 16 keypoints **confirmé** (proposition : indices 14–15 = `IT_R`, `IT_L`)
- [ ] **B5.** `flip_idx` 16 kp **validé** (proposition : `[…, 15, 14]`)
- [ ] **B5.** Compatibilité LM-17 / LM-18 avec extension catalogue §11 confirmée

### Corpus et visibilité (bloquants B6–B7)

- [ ] **B7.** Audit de visibilité des tubérosités sur les **26 images `new_26`** (taux `v=0` attendu, cas unilatéraux)
- [ ] **B6.** **Ré-annotation** manuelle de `IT_R` et `IT_L` sur les 26 cas selon guide validé
- [ ] Revue clinique des annotations IT (qualité, cohérence R/L)

### Mise à jour artefacts (après spec + annotation — hors scope actuel)

- [ ] Extension labels YOLO : 47 → **53** colonnes
- [ ] Mise à jour `data.yaml` : `kpt_shape: [16, 3]`, `flip_idx`, `kpt_names`
- [ ] Mise à jour `meta/keypoint_order.md`
- [ ] Extension backend / Flutter / `mvp_geometry` (mesure bi-ischiale)

### Training (politique T1, T3)

- [ ] **T1.** Aucun training tant que B1–B7 ouverts
- [ ] **T3.** Retraining **obligatoire** — initialisation depuis **V2 best**, **pas V3**
- [ ] Split 21/5 : peut être conservé ; contenu labels enrichi uniquement

### Interdictions rappelées

- Ne **pas** utiliser `TD_R`/`TD_L` comme substitut de `IT_R`/`IT_L` (A2)
- Ne **pas** modifier V2, labels, YAML ou dataset **avant** complétion des préconditions ci-dessus
- Ne **pas** lancer de training dans cette phase de spécification

---

*Document de spécification uniquement — aucun fichier du projet modifié.*
