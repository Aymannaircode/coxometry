# Spécification — Femoral offset (offset fémoral)

**Généré :** 2026-08-28  
**Mode :** spécification uniquement — **aucune implémentation**, **aucune modification** du code, dataset, labels, V2, V3, backend ou Flutter  
**Sources :** `docs/landmark_specification.md`, `docs/annotation_guidelines.md`, `docs/dataset1_analysis.md`, `docs/dataset_analysis.md`, `datasets/yolo_pose_new_26/missing_measurements_spec.md`, `datasets/yolo_pose_new_26/missing_measurements_audit.md`

**Statut global :** **SPECIFICATION REQUIRED** — ingrédients géométriques documentés ; métrique clinique, calibration et §3.x dédiée **non figés**.

---

## Périmètre et contraintes

| Contrainte | Statut |
|------------|--------|
| Entraînement YOLO | **Interdit** pour cette mesure (landmarks existants suffisants — T2) |
| Modification V2 / V3 | **Interdite** |
| Modification labels / dataset | **Interdite** |
| Implémentation `femoral_offset()` | **Hors scope** — document de spec uniquement |

---

## 1. Définition exacte de la mesure

### Ce que la documentation affirme

**Source principale —** `docs/landmark_specification.md` §11 « Hors MVP » :

> offset fémoral (axe diaphysaire + `FHC`, mais calibration mm/px et définition d'offset **à figer**)

**Compléments :**

| Source | Contenu documenté |
|--------|-------------------|
| §2.3 | Ligne dérivée `SHAFT_*` = droite `FSP_*` → `FSD_*` = **axe diaphysaire** |
| §11 | Ingrédients : centre de tête (`FHC`) + axe diaphysaire (`SHAFT`) |
| `docs/dataset1_analysis.md` §14 | « Requiert centre de tête + **axe diaphysaire long** » |
| `docs/dataset_analysis.md` §14 | « Requiert centre de tête + axe diaphysaire fémoral long ; **non couvert** » (corpus DDH pédiatrique) |

### Ce que la documentation n'affirme pas

La documentation **ne définit pas** le type d'offset fémoral clinique :

- distance perpendiculaire au shaft ?
- projection horizontale (parallèle à `ITH`) ?
- projection médiale / latérale ?
- référence pelvienne requise ou non ?
- lien avec l'axe du col `NECK = FHC→FNM` (§2.3) — **non cité** pour l'offset §11

**Statut :** **SPECIFICATION REQUIRED** (décision clinique **F1**, **F7**)

---

## 2. Point de référence FHC

### Définition documentée (figée pour le MVP)

| Champ | Valeur |
|-------|--------|
| **Landmarks** | `FHC_R` (LM-03), `FHC_L` (LM-04) |
| **Nom** | Centre de la tête fémorale |
| **Définition anatomique** | Centre du **cercle de meilleure approximation** (Mose / best-fit) de la tête fémorale osseuse sur l'AP |
| **Position** | Au centre géométrique de la tête, bilatéral |
| **Rôle pour offset** | Point de référence tête cité §11 |
| **Mesures MVP associées** | VCE ; CCD (origine axe col) — **pas** de §3.x offset |

### Ambiguïté A5 (validité du point)

| Situation | Conduite documentée |
|-----------|---------------------|
| Tête asphérique, coxa plana, ostéophytes, nécrose | Cercle mal défini → centre sur portion sphérique conservée |
| Cercle non ajustable | `v=0` pour `FHC` — **ne pas inventer** un centre |

**Statut FHC comme référence offset :** **DEFINED** (point tête = `FHC_side`)  
**Impact invalidité sur offset :** **SPECIFICATION REQUIRED** (conduite si `FHC` en `v=0` non décrite pour offset — par analogie CCD : mesure non calculable ce côté)

---

## 3. Axe SHAFT

### Construction documentée (figée)

**Source :** `docs/landmark_specification.md` §2.3

```
SHAFT_side = droite(FSP_side, FSD_side)
```

| Élément | Définition |
|---------|------------|
| `FSP_*` (LM-11/12) | Point proximal de l'axe diaphysaire — sous le petit trochanter, corticales parallèles |
| `FSD_*` (LM-13/14) | Point distal de l'axe diaphysaire — le plus distal **visible dans le FOV** du cliché |
| Nature de l'axe | **Corde 2D** entre deux points sur l'axe médian diaphysaire (acceptable MVP si courbure — `annotation_guidelines.md` §2.7) |
| Usage CCD | Axe diaphysaire de référence §3.3 |
| Usage offset | Mentionné §11 — **même construction** implicite |

**Landmarks non utilisés pour SHAFT :** `TD`, `ASL`, `ASM`, `FNM`.

**Statut :** **DEFINED** (construction `FSP→FSD`)

---

## 4. Distance géométrique exacte à mesurer

### État documenté

La documentation fixe les **prérequis géométriques** mais **pas** la formule numérique :

```
Étape 1 (documentée §2.3) :
  SHAFT_side ← droite passant par FSP_side et FSD_side

Étape 2 (documentée §11) :
  Point tête ← FHC_side

Étape 3 (NON FIGÉE — §11) :
  offset_fémoral_side ← relation métrique entre FHC_side et SHAFT_side
                        (type de distance / projection : à définir cliniquement)

Étape 4 (NON FIGÉE — §11) :
  offset_mm ← conversion via calibration mm/px
```

**Absence :** aucune section §3.x dédiée (contrairement à VCE §3.1, Tönnis §3.2, CCD §3.3).

**Code :** pas de `femoral_offset()`, pas de `point_to_line_distance()` dans `mvp_geometry/` (audit).

**Statut :** **SPECIFICATION REQUIRED** (décision **F1**)

---

## 5. Convention de signe

### État documenté

**Non documentée** pour l'offset fémoral.

Comparaison avec mesures MVP existantes (pour contexte uniquement — **ne pas extrapoler**) :

| Mesure | Convention documentée |
|--------|----------------------|
| Tönnis | Signe à figer — ambiguïté A4 (positif si sourcil incliné vers le bas en latéral) |
| CCD | Angle **médial** obtus (~120–135°) — pas de signe linéaire |
| Offset fémoral | **Aucune** |

Questions ouvertes (non résolues dans le projet) :

- Médial positif vs latéral positif ?
- Référence au côté patient (`R`/`L`) ?
- Comparaison bilatérale (différence R−L) ?

**Statut :** **SPECIFICATION REQUIRED** (décision **F2**)

---

## 6. Unité de sortie

### État documenté

| Aspect | Source | Statut |
|--------|--------|--------|
| Millimètres attendus cliniquement | Implicite via « calibration mm/px » §11 | **Implicite, non figé formellement** |
| Pixels seuls | Non mentionné comme sortie clinique acceptable | — |
| Degrés | Non applicable (contrairement aux mesures angulaires MVP) | — |

**Statut :** **SPECIFICATION REQUIRED** — unité cible **mm** fortement implicite mais **non formalisée** comme pour les angles MVP (décision **F2**)

---

## 7. Méthode de calibration mm/px

### État documenté

§11 exige explicitement une **calibration mm/px**, **sans en décrire la méthode**.

| Question | Réponse dans la doc projet |
|----------|---------------------------|
| Calibration requise ? | **Oui** (§11) |
| Méthode proposée | **Aucune** (pas de marker, pas de distance inter-teardrop, pas de DICOM pixel spacing, pas de diamètre tête connu) |
| Où implémenter | **Non spécifié** — absent de `mvp_geometry/`, backend, Flutter |
| Lien avec mesures angulaires MVP | VCE / Tönnis / CCD en **degrés** — **pas** de mm/px pour le MVP actuel |

**Note homonymie :** le mot « offset » dans le code (`mvp_geometry/refinement/asl_l.py`, `calibration.py`) désigne le **refinement pixel ASL_L**, **pas** l'offset fémoral clinique.

**Statut :** **SPECIFICATION REQUIRED** (décision **F3**)

---

## 8. Que faire si aucune calibration n'est disponible

### État documenté

**Non documenté** dans les sources du projet.

Conséquence logique (inférée strictement de §11 « calibration mm/px requise », **sans prescrire de comportement produit**) :

- Sans mm/px, la conversion « offset_mm » de l'étape 4 **ne peut pas être effectuée** selon la spec actuelle.

**Statut :** **SPECIFICATION REQUIRED** — conduite produit (refus, valeur nulle, pixels bruts interdits cliniquement ?) **à figer**

---

## 9. Que faire si le FOV est trop court pour un axe FSP→FSD fiable

### Règles documentées (ambiguïté A7)

**Sources :** `docs/landmark_specification.md` §4 LM-13/14, `docs/annotation_guidelines.md` §2.7

| Situation | Conduite documentée |
|-----------|---------------------|
| Diaphyse longue et nette | `FSD` en `v=2` |
| Diaphyse très courte sous `FSP` | Mesurer la distance `FSP`–`FSD` |
| Distance `FSP`–`FSD` **< 0,5 × diamètre apparent de la tête** homolatérale | → `v=0` pour `FSD` ; **CCD non calculable** pour ce côté |
| FOV coupe le fémur | Annoter le dernier niveau fiable **dans** l'image ; appliquer la règle de distance |
| Corticale d'un seul côté visible | `v=0` pour le point concerné |

**Nature du seuil 0,5 × diamètre tête :** **convention projet provisoire** — « validation radiologue / orthopédiste requise » (`annotation_guidelines.md` §2.7).

**Extension à l'offset fémoral :**

- `missing_measurements_audit.md` : axe instable pour offset « long shaft » si FOV court — **même limitation A7** que CCD, **par extension logique**, pas par règle §11 explicite.
- Décision **F4** : valider si la règle A7 CCD s'applique **identiquement** à l'offset ou avec un seuil distinct.

**Statut seuil A7 pour offset :** **PROVISIONAL** (seuil 0,5× tête documenté pour CCD ; application offset = **SPECIFICATION REQUIRED**, décision **F4**)

**Statut axe AP bassin seul :** **SPECIFICATION REQUIRED** (décision **F5** — shaft souvent trop court ; landmarks distaux additionnels éventuels ?)

---

## 10. Conditions de validité / invalidité

### Conditions documentées (extrait strict des sources)

| ID | Condition | Conduite documentée | Mesure concernée dans la source |
|----|-----------|---------------------|--------------------------------|
| **A5** | `FHC` non fiable (tête déformée) | `v=0` pour `FHC` | VCE, CCD |
| **A7** | `FSP` ≈ `FSD` (FOV court) | Axe diaphysaire **instable** ; seuil 0,5× diamètre tête → `v=0` pour `FSD` | CCD |
| **A7** | Corticale unique visible | `v=0` | Annotation diaphyse |
| **Visibilité** | Landmark requis en `v=0` ou absent | CCD impossible ce côté (checklist MVP §10) | CCD |
| **Qualité shaft** | Courbure diaphysaire marquée | Axe = corde 2D — acceptable MVP | CCD (et shaft pour offset) |
| **Cohérence** | `FSD` proximal à `FSP` | Corriger ou `v=0` | Annotation |
| **Cohérence** | Axes gauche/droit se croisant aberramment | Signe d'inversion R/L | Annotation |

### Conditions **non** documentées spécifiquement pour offset

| Condition | Statut |
|-----------|--------|
| Offset non calculable si `FHC` en `v=0` | **SPECIFICATION REQUIRED** (analogie CCD probable) |
| Offset non calculable si `FSD` en `v=0` (règle A7) | **SPECIFICATION REQUIRED** (extension audit, pas §11) |
| Offset non calculable si `FSP` en `v=0` | **SPECIFICATION REQUIRED** |
| Offset non calculable sans calibration mm/px | **SPECIFICATION REQUIRED** |
| Qualité clinique insuffisante sur AP bassin (shaft court) | **Incertaine** — A7 + analyses dataset §14 |

**Statut global validité offset :** **SPECIFICATION REQUIRED** (matrice invalidité dédiée à rédiger en §3.x — **F7**)

---

## 11. Seuils cliniques

### État documenté

**Aucun seuil clinique** (normal / pathologique) pour l'offset fémoral dans les sources du projet.

Seul seuil **géométrique/annotation** documenté, lié à A7 :

| Seuil | Valeur | Portée documentée | Statut |
|-------|--------|-------------------|--------|
| Séparation minimale `FSP`–`FSD` | **≥ 0,5 × diamètre apparent de la tête** homolatérale | CCD (annotation) | **Provisoire — à valider cliniquement** |

**Statut seuils cliniques offset :** **SPECIFICATION REQUIRED** (décision **F6** — aucun défaut dans le projet)

---

## 12. Bilatéralité

### État documenté

| Aspect | Contenu |
|--------|---------|
| Landmarks | Schéma **bilatéral** : `FHC_R/L`, `FSP_R/L`, `FSD_R/L` (14 kp) |
| Construction | Mesure **par côté** implicite (suffixes `_R` / `_L`, même logique que CCD §3.3 « sur chaque hanche ») |
| Checklist MVP §10 | Image complète bilatérale si tous landmarks `v>0` des deux côtés |
| Comparaison R vs L | **Non documentée** pour offset |
| Côté manquant / unilatéral | **Non documentée** pour offset (contrairement au MVP angles où un côté peut être `v=0`) |
| Symétrie | Règles cohérence R/L pour annotation diaphyse (§2.6–2.7 guidelines) — **QC annotation**, pas règle offset |

**Statut :** **PARTIELLEMENT DEFINED** — mesure **par hanche** implicite via landmarks R/L ; règles de restitution bilatérale (comparaison, côté unique, asymétrie) = **SPECIFICATION REQUIRED**

---

## Landmarks requis — synthèse

### Par côté (`R` ou `L`)

| Landmark | ID | Rôle offset | Dans les 14 kp ? |
|----------|-----|-------------|:----------------:|
| `FHC_side` | LM-03/04 | Centre tête — référence §11 | Oui |
| `FSP_side` | LM-11/12 | Extrémité proximale axe diaphysaire | Oui |
| `FSD_side` | LM-13/14 | Extrémité distale axe diaphysaire (FOV) | Oui |

**Ligne dérivée :** `SHAFT_side = droite(FSP_side, FSD_side)` — non annotée.

**Landmarks non requis pour offset (§11) :** `TD`, `ASL`, `ASM`, `FNM`.

---

## Les 14 landmarks actuels suffisent-ils ?

| Question | Réponse documentée |
|----------|-------------------|
| Ingrédients géométriques de base (`FHC` + `FSP` + `FSD` → `SHAFT`) | **Oui** — §11, T2 (`missing_measurements_spec.md` §5.4) |
| Nouveaux landmarks YOLO requis | **Non** identifiés pour l'offset |
| Retraining nécessaire | **Non** (T2) — implémentation software après F1–F7 |
| Mesure projet validée / déployable | **Non** — définition métrique + mm/px non figés |
| Qualité clinique sur AP bassin seul | **Incertaine** — A7, F5 ; analyses dataset : « axe diaphysaire **long** » requis |

### Verdict

```
Landmarks YOLO (14 kp) : SUFFISANTS pour les ingrédients documentés (FHC, FSP, FSD par côté)
Mesure offset fémoral   : NON CALCULABLE au sens « spec figée + validation clinique »
Blocage principal       : définition métrique (F1) + calibration mm/px (F3) — pas absence de points
```

---

## Pipeline et implémentation (état actuel — lecture seule)

| Composant | État |
|-----------|------|
| `mvp_geometry/measurements.py` | Pas de `femoral_offset()` |
| Tests | Aucun test offset fémoral |
| Backend `MeasureOut` / Flutter | Pas de champ offset fémoral |
| Homonymie `offset` code | Refinement ASL_L uniquement — **≠ offset fémoral** |

---

## Décisions cliniques ouvertes (référence)

| ID | Sujet | Source |
|----|-------|--------|
| **F1** | Métrique exacte entre `FHC` et `SHAFT` | `missing_measurements_spec.md` §5.2 |
| **F2** | Convention de signe et unité mm | idem |
| **F3** | Méthode calibration mm/px | idem |
| **F4** | Règle A7 FOV court — application à offset | idem |
| **F5** | Shaft AP bassin suffisant vs landmarks distaux | idem |
| **F6** | Seuils cliniques | idem |
| **F7** | Rédiger §3.x dans `landmark_specification.md` | idem |

---

## Tableau final — Décision | Statut | Action nécessaire

| Décision | Statut | Action nécessaire |
|----------|--------|-------------------|
| **D1 — Ingrédients géométriques** (`FHC` + axe `FSP→FSD`) | **DEFINED** | Aucune — §11, §2.3 |
| **D2 — Point de référence tête (`FHC`)** | **DEFINED** | Aucune — LM-03/04, A5 pour invalidité |
| **D3 — Axe SHAFT** (`droite(FSP, FSD)`) | **DEFINED** | Aucune — §2.3 |
| **D4 — Définition clinique exacte de l'offset** | **SPECIFICATION REQUIRED** | Revue clinique **F1** ; rédiger §3.x **F7** |
| **D5 — Distance / projection géométrique** | **SPECIFICATION REQUIRED** | **F1** — type de distance `FHC` ↔ `SHAFT` |
| **D6 — Convention de signe** | **SPECIFICATION REQUIRED** | **F2** |
| **D7 — Unité de sortie (mm)** | **SPECIFICATION REQUIRED** | **F2** — formaliser mm comme sortie unique |
| **D8 — Méthode calibration mm/px** | **SPECIFICATION REQUIRED** | **F3** |
| **D9 — Conduite sans calibration** | **SPECIFICATION REQUIRED** | Décision produit liée à **F3** |
| **D10 — Règle FOV court (A7)** | **PROVISIONAL** | **F4** — confirmer extension CCD → offset ; valider seuil 0,5× tête |
| **D11 — Suffisance shaft AP bassin** | **SPECIFICATION REQUIRED** | **F5** — shaft long vs landmarks additionnels |
| **D12 — Matrice validité / invalidité offset** | **SPECIFICATION REQUIRED** | **F7** — formaliser par côté |
| **D13 — Seuils cliniques** | **SPECIFICATION REQUIRED** | **F6** — aucun dans le projet |
| **D14 — Bilatéralité (restitution R/L)** | **PARTIELLEMENT DEFINED** | Mesure par côté implicite ; règles comparaison / unilatéral à figer |
| **D15 — Landmarks 14 kp suffisants** | **DEFINED (ingrédients)** / **NON DÉPLOYABLE (mesure)** | Pas de retraining ; implémentation après F1–F7 |
| **D16 — Entraînement** | **DEFINED (POLICY)** | **Ne pas entraîner** pour offset — T2 |

---

*Document de spécification uniquement — aucun fichier de code, dataset ou modèle modifié.*
