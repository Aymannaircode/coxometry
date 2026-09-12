# Guide d'annotation proposé — `IT_R` / `IT_L` (bi-ischial)

**Généré :** 2026-08-28  
**Révisé :** 2026-08-28 (post-revues pilote B26_01 + revue B26_05 — règles FOV, PARTIAL, anti-fémur)  
**Décision :** B4 — fiche d'annotation **proposée**, prête pour campagne B6 **conditionnelle**  
**Statut B1 :** **CANDIDATE** — proposition documentée ci-dessous, **non validée cliniquement**  
**Mode :** document de travail uniquement — **aucune modification** du dataset, labels, YAML, modèles, backend ou Flutter  

**Documents liés :**

- `docs/landmark_specification.md` §11
- `docs/annotation_guidelines.md` (règles générales MVP)
- `datasets/yolo_pose_new_26/bi_ischial_spec.md`
- `datasets/yolo_pose_new_26/bi_ischial_B1_position_audit.md`
- `datasets/yolo_pose_new_26/bi_ischial_visibility_audit.md` (B7)
- `datasets/yolo_pose_new_26/B6_pilot_B26_01.md` (pilote NON-OFFICIAL)
- `datasets/yolo_pose_new_26/B6_review_B26_05.md` (revue NON-OFFICIAL)

**Usage prévu :** base reproductible pour la campagne B6. Tant que B1 n'est pas validé cliniquement, ce guide reste une **proposition opérationnelle**, pas un protocole figé.

---

## REMARQUE CLINIQUE — `IT_R` / `IT_L`

**Enregistrée :** 2026-08-28 · **Décision de travail** (non validation clinique définitive)

### Définition de travail proposée

> **`IT_R` / `IT_L` = point caudal/inférieur identifiable du contour osseux de chaque tubérosité ischiatique sur la radiographie AP du bassin.**

| Attribut | Valeur |
|----------|--------|
| **STATUS** | **PROPOSED** |
| **Validation clinique** | **CLINICAL VALIDATION REQUIRED** |

Cette formulation **n'est pas** une définition clinique définitivement validée. Elle sert de **référence de travail** pour la revue clinique et la préparation B6 (`bi_ischial_B6_annotation_plan.md`).

### Règles explicites associées

1. **`TD_R` / `TD_L` ne remplacent jamais `IT_R` / `IT_L`** — structures et rôles distincts ; substitution interdite (ambiguïté **A2**). Voir §8.
2. **Règle bord FOV** — conduite lorsque la tubérosité ischiatique est proche du bord caudal de l'image ; pas d'extrapolation hors FOV. Voir §4.4.
3. **Règle PARTIAL** — distinction VISIBLE / PARTIAL / UNCERTAIN / NON_VISIBLE et mapping `v=2` / `v=0` selon conventions MVP existantes. Voir §5.
4. **Règle anti-fémur** — un candidat `IT_*` ne doit **jamais** être placé sur la diaphyse ou le contour du fémur ; le landmark appartient à la tubérosité ischiatique (os pelvien). Voir §3.6.
5. **`B26_01`** — exemple standard + piège fémoral `IT_L` documenté (pilote B6). Voir §9.1.
6. **`B26_05`** — exemple cas limite obligatoire (PARTIAL bilatéral ; bord FOV ; piège fémoral `IT_R`). Voir §9.2.

| Règle | STATUS |
|-------|--------|
| Règles 2–4 (FOV, PARTIAL, anti-fémur) | **PROPOSED / CLINICAL VALIDATION REQUIRED** |
| Règle 1 (TD ≠ IT) | **DEFINED** |

---

## 1. Identification

| Champ | `IT_R` | `IT_L` |
|-------|--------|--------|
| **Nom** | Ischial tuberosity — côté droit patient | Ischial tuberosity — côté gauche patient |
| **Structure anatomique** | **Tubérosité ischiatique** droite | **Tubérosité ischiatique** gauche |
| **ID proposé** | LM-17 | LM-18 |
| **Rôle** | Extrémité droite de `BI_ISCHIAL = droite(IT_R, IT_L)` | Extrémité gauche de `BI_ISCHIAL` |
| **Vue** | Radiographie **AP du bassin** adulte | Idem |
| **Schéma actuel** | Absent des 14 keypoints MVP — extension 16 kp future | Idem |

**Sources :** `landmark_specification.md` §11 ; `missing_measurements_spec.md` §3.2 ; `bi_ischial_spec.md` §1–2

### Convention R/L (figée projet)

| Règle | Détail |
|-------|--------|
| Droite patient | À **gauche** de l'image |
| Gauche patient | À **droite** de l'image |
| `IT_R` | Toujours tubérosité ischiatique **droite patient** (gauche image) |
| `IT_L` | Toujours tubérosité ischiatique **gauche patient** (droite image) |

**Source :** `annotation_guidelines.md` §1.1 ; `bi_ischial_spec.md` §4

---

## 2. Proposition de placement

### Formulation proposée (B1 CANDIDATE)

> **`IT_R` / `IT_L` = point inférieur/caudal identifiable du contour osseux de la tubérosité ischiatique sur la radiographie AP du bassin.**

| Attribut | Valeur |
|----------|--------|
| **STATUS** | **PROPOSED** |
| **Validation clinique** | **CLINICAL VALIDATION REQUIRED** |
| **Origine** | Proposition d'audit `missing_measurements_audit.md` §3, reprise comme candidat B1 ; **non figée** dans les sources primaires (`landmark_specification.md` §11 ne précise pas le point sur la tubérosité) |

### Ce que cette proposition n'est pas

- Ce n'est **pas** une définition clinique définitivement validée.
- Ce n'est **pas** la règle MVP du teardrop (`TD_*`) — voir §8.
- Ce n'est **pas** le centre géométrique de la tubérosité — **non tranché** cliniquement (B1 ouvert).
- Ce n'est **pas** une règle dérivée automatiquement de l'audit de visibilité B7 — voir §5.

### Statut B1 global

```
B1 = CANDIDATE (proposition documentée)
Validation clinique formelle = REQUISE avant B6
```

---

## 3. Règle de placement (proposition opérationnelle)

**STATUS global de cette section : PROPOSED / CLINICAL VALIDATION REQUIRED**

Les étapes ci-dessous traduisent la proposition B1 en conduite annotateur **provisoire**. Elles servent à harmoniser une revue clinique pilote ; elles ne remplacent pas une validation radiologique / orthopédique.

### 3.1 Quel contour osseux suivre

**Proposition :**

1. Identifier la **tubérosité ischiatique** homolatérale sur l'AP bassin — masse osseuse caudale latérale du bassin, **distincte** du teardrop acétabulaire médial (`TD_*`).
2. Suivre le **contour osseux projeté** de cette tubérosité — bord radiographique net de l'os, pas la zone de tissus mous adjacente.
3. Ne **pas** confondre avec :
   - la **ligne ilio-ischiatique** (utilisée comme repère pour le teardrop, `annotation_guidelines.md` §2.1) ;
   - le **foramen obturé** ;
   - le **pubis** ou la **symphyse** ;
   - le **teardrop** acétabulaire (`TD_*`).

**Source partielle :** distinction TD/IT et structures voisines — `bi_ischial_spec.md` §7–8 ; repérage teardrop « entre tête fémorale et ligne ilio-ischiatique » — `annotation_guidelines.md` §2.1

| Sous-point | STATUS |
|------------|--------|
| Contour = bord osseux tubérosité ischiatique | **PROPOSED** |
| Exclusion ligne ilio-ischiatique / obturateur comme point IT | **PROPOSED** (logique spec + guide TD) |

### 3.2 Où placer le centre du point

**Proposition (B1 CANDIDATE) :**

Placer le centre du landmark sur le point **le plus inférieur / caudal** du contour osseux de la tubérosité ischiatique **identifiable sans extrapolation** sur l'AP :

- « Inférieur / caudal » = direction vers le **bas de l'image** (vers les pieds du patient en AP orthograde).
- « Identifiable » = le repère est visible sur le contour osseux ; pas de reconstruction hors os visible.

**Non tranché cliniquement :** point **cortical** strict vs sommet osseux vs « point le plus bas du contour projeté » lorsque le contour est oblique — **CLINICAL VALIDATION REQUIRED** (`bi_ischial_B1_position_audit.md` §3).

| Sous-point | STATUS |
|------------|--------|
| Point le plus inférieur/caudal identifiable sur contour osseux | **PROPOSED** (B1 CANDIDATE) |
| Cortical vs centre vs sommet | **CLINICAL VALIDATION REQUIRED** |

### 3.3 Contour large ou forme étendue

**État des sources :** aucune règle IT spécifique documentée (`bi_ischial_B1_position_audit.md` §4).

**Proposition provisoire (à valider) :**

- Si la tubérosité forme une zone osseuse **étendue** avec plusieurs points candidats « bas » :
  - retenir le point **caudal le plus net** sur le **contour osseux latéral/caudal** de la tubérosité ;
  - en cas d'égalité ou d'ambiguïté entre plusieurs points bas → **ne pas choisir au hasard** ; marquer **`v=0`** ou soumettre à revue clinique.

| Sous-point | STATUS |
|------------|--------|
| Règle contour large | **CLINICAL VALIDATION REQUIRED** |
| Conduite provisoire « point caudal le plus net ; sinon v=0 » | **PROPOSED** (alignée sur règle d'or MVP §1.2) |

### 3.4 Éviter les tissus mous

**État des sources :** pas de fiche IT ; principe général implicite dans les guides MVP (landmarks osseux).

**Proposition provisoire :**

- Placer le point **sur le contour osseux dense** (bord radiographique de la tubérosité).
- **Ne pas** placer sur :
  - ombres de tissus mous péri-ischiatiques ;
  - zones floues sans bord osseux ;
  - artefacts ou superpositions non osseuses identifiables.
- Si le bord osseux caudal n'est pas distinguable des tissus mous → **`v=0`**.

| Sous-point | STATUS |
|------------|--------|
| Landmark osseux uniquement | **PROPOSED** (cohérent MVP) |
| Seuils opérationnels tissus mous vs os | **CLINICAL VALIDATION REQUIRED** |

### 3.5 Éviter la confusion avec `TD_R` / `TD_L`

**Règle documentée (non proposition) :**

| Landmark | Structure | Rôle |
|----------|-----------|------|
| `TD_R` / `TD_L` | Teardrop acétabulaire (larme) — point le plus **inférieur** de la larme | Base de `ITH` — horizontal pelvien MVP |
| `IT_R` / `IT_L` | Tubérosité ischiatique — proposition : point caudal du contour tubérosité | Base de `BI_ISCHIAL` — hors MVP |

**Interdictions explicites (sources projet) :**

- Ne **pas** placer `IT_*` sur le teardrop.
- Ne **pas** utiliser `TD_*` comme substitut de `IT_*` (ambiguïté **A2**).
- Ne **pas** annoter les ischions « à la place » du teardrop (`annotation_guidelines.md` §2.1).

**Repérage spatial :** le teardrop est **médial** au cotyle ; la tubérosité ischiatique est **latérale et caudale** par rapport au teardrop sur un AP standard.

| Sous-point | STATUS |
|------------|--------|
| TD ≠ IT ; substitution interdite (A2) | **DEFINED** |
| Repérage spatial TD vs IT sur AP | **PROPOSED** (géométrie anatomique standard ; illustrations cliniques manquantes) |

### 3.6 Règle anti-fémur (PROPOSED)

**Motivation documentée :** piège fémoral observé en pilote / revue B6 — **B26_01** (`IT_L`) et **B26_05** (`IT_R`).

| Attribut | Valeur |
|----------|--------|
| **STATUS** | **PROPOSED / CLINICAL VALIDATION REQUIRED** |
| **Convention `v`** | Aucune nouvelle convention — rejet du candidat fémoral puis application de `annotation_guidelines.md` §1.2 |

**Règle proposée :**

> Un candidat `IT_*` ne doit **jamais** être placé sur la **diaphyse** ou le **contour du fémur**. Le landmark doit appartenir à la **tubérosité ischiatique** — contour osseux **pelvien**, distinct du fémur proximal.

**Conduite opérationnelle proposée :**

1. Localiser d'abord la masse osseuse **pelvienne** caudale latérale (tubérosité ischiatique), **médiale** à l'axe fémoral proximal et **distincte** de `FSD_*` (diaphyse fémorale).
2. Placer le point caudal sur le contour **ischiatique**, pas sur le bord caudal le plus bas de l'image si celui-ci correspond à la diaphyse.
3. Si le contour ischiatique caudal n'est pas distinguable du fémur sans deviner → **`v=0`** (règle d'or MVP §1.2).

**Pièges documentés (coordonnées PILOT / NON-OFFICIAL — ne pas intégrer aux labels officiels) :**

| Image | Côté | Candidat rejeté | Motif |
|-------|------|-----------------|-------|
| **B26_01** | `IT_L` | (2136, 2117) | Trop latéral — diaphyse fémorale gauche, non tubérosité ischiatique |
| **B26_05** | `IT_R` | (468, 3006) | Trop latéral — bord caudal diaphyse fémorale droite, non tubérosité ischiatique |
| **B26_05** | `IT_L` | (2575, 2912) | Trop latéral — diaphyse fémorale gauche, proche `FSD_L` |

**Repérage spatial proposé :** `IT_*` reste sur l'os pelvien ; le fémur est **latéral** à la tubérosité sur un AP standard. Ne pas confondre le point caudal **global** de l'image avec le point caudal **ischiatique**.

| Sous-point | STATUS |
|------------|--------|
| Interdiction placement sur diaphyse / contour fémoral | **PROPOSED** |
| IT sur contour pelvien tubérosité ischiatique uniquement | **PROPOSED** |
| Seuils de rejet latéral opérationnels | **CLINICAL VALIDATION REQUIRED** |

---

## 4. Cas particuliers

Pour chaque cas : règle proposée **uniquement** si supportée ou dérivable des sources ; sinon **CLINICAL VALIDATION REQUIRED**.

### 4.1 Tubérosité partiellement visible

| Élément | Contenu |
|---------|---------|
| **Contexte B7** | Catégorie **PARTIAL** — voir **§5 Règle PARTIAL** |
| **Règle générale MVP** | Ne jamais placer un point « pour remplir le schéma » ; si deviner → `v=0` — `annotation_guidelines.md` §1.2 |
| **Proposition conduite** | Voir §5.3 — `v=2` seulement si repère caudal net sans extrapolation et sans doute raisonnable ; sinon `v=0` ou revue clinique |
| **STATUS** | **PROPOSED** (seuil PARTIAL → `v=2` vs `v=0` — **CLINICAL VALIDATION REQUIRED**) |

**Exemple corpus :** **B26_05** — PARTIAL bilatéral (bord FOV) ; revue B6 obligatoire. Voir §9.2.

### 4.2 Superposition osseuse

| Élément | Contenu |
|---------|---------|
| **Sources IT** | Cas listé comme non documenté — `bi_ischial_spec.md` §6 |
| **Analogie documentée** | `FHC_*` : « Superposition pubis / ischion → zoomer ; si contour douteux → `v=0` » — `annotation_guidelines.md` §2.2 |
| **Proposition conduite** | Zoomer ; tenter d'isoler le contour caudal de la tubérosité ; si superposition empêche d'identifier le point caudal proposé sans deviner → **`v=0`** |
| **STATUS** | **CLINICAL VALIDATION REQUIRED** (analogie FHC non étendue formellement à IT) |

### 4.3 Contour difficile à suivre

| Élément | Contenu |
|---------|---------|
| **Sources** | Pas de fiche IT ; règle d'or MVP §1.2 |
| **Proposition conduite** | Si le contour osseux caudal de la tubérosité n'est pas suivi de façon cohérente entre annotateurs potentiels → **`v=0`** ; journaliser le cas pour revue clinique |
| **STATUS** | **CLINICAL VALIDATION REQUIRED** |

### 4.4 Règle bord FOV (PROPOSED)

**Objet :** documenter explicitement le comportement lorsque la tubérosité ischiatique est **proche du bord caudal** de l'image (champ de vue / FOV).

| Attribut | Valeur |
|----------|--------|
| **STATUS** | **PROPOSED / CLINICAL VALIDATION REQUIRED** |
| **Contexte B7** | B26_05 (cas le plus serré) ; B26_12 (marge caudale réduite) — `bi_ischial_visibility_audit.md` |
| **Convention `v`** | Aucune nouvelle convention — `annotation_guidelines.md` §1.2 |

**Principes proposés :**

| # | Règle | Base projet |
|---|-------|-------------|
| 1 | Ne **jamais extrapoler** un point caudal **hors** du FOV visible | MVP §1.2 — pas de devinette |
| 2 | Retenir le point caudal **le plus bas identifiable sur le contour osseux ischiatique**, **dans** l'image | Proposition B1 §3.2 |
| 3 | Si l'apex caudal anatomique est **coupé** par le bord et que le placement exact exige une reconstruction hors os visible → **`v=0`** pour ce côté | MVP §1.2 |
| 4 | Ne **pas** confondre la règle bord `FSD_*` (diaphyse fémorale : dernier niveau fiable **dans** l'image) avec `IT_*` — structures et règles distinctes | `annotation_guidelines.md` §2.7 ; analogie **non** transposable telle quelle |
| 5 | Cas **B26_05-type** (PARTIAL bilatéral, marge caudale minimale) → **session supervisée** ou revue clinique avant validation `v=2` | Revue B6 B26_05 |

**Comportement proposé selon situation :**

| Situation | Conduite proposée | `v` proposé |
|-----------|-------------------|-------------|
| Contour caudal ischiatique entièrement visible, marge confortable | Annoter selon B1 | **`v=2`** si net (MVP §1.2) |
| Contour caudal visible mais **proche du bord** ; repère caudal identifiable **sans extrapolation** | Annoter le dernier cortex net **dans** le FOV ; documenter marge réduite | **`v=2`** si sans doute raisonnable ; sinon **`v=0`** |
| Apex caudal coupé ; plusieurs pixels candidats entre « dernier net » et bord | Ne pas choisir arbitrairement ; revue clinique ou **`v=0`** | **`v=0`** ou revue (**PROPOSED**) |
| Structure ischiatique non identifiable dans le FOV | Ne pas inventer de coordonnées | **`v=0`** (**DEFINED** MVP §1.2) |

**Exemple corpus :** **B26_05** — seul cas PARTIAL bilatéral ; cortex caudal frôle le bord inférieur (~2 px au scan le plus bas) ; dispersion inter-annotateurs estimée ~110–126 px sur l'axe y entre interprétation conservatrice et maximaliste bord. Voir §9.2.

| Sous-point | STATUS |
|------------|--------|
| Interdiction extrapolation hors FOV | **DEFINED** (MVP §1.2) ; application IT **PROPOSED** |
| Dernier cortex identifiable dans FOV | **PROPOSED** |
| Seuil marge caudale opérationnel (ex. %) | **CLINICAL VALIDATION REQUIRED** |
| Conduite B26_05-type (supervision) | **PROPOSED** |

### 4.5 Mauvaise qualité radiographique

| Élément | Contenu |
|---------|---------|
| **Sources** | Règle générale : structure non identifiable → `v=0` — §1.2 |
| **Contexte B7** | B26_07 : gaz intestinal central — tubérosités restent VISIBLE mais revue recommandée |
| **Proposition conduite** | Sous-exposition, flou ou bruit empêchant d'identifier le contour caudal → **`v=0`** ; noter qualité en métadonnée QC si disponible |
| **STATUS** | Conduite générale **DEFINED** (v=0) ; seuils IT spécifiques **CLINICAL VALIDATION REQUIRED** |

### 4.6 Asymétrie apparente

| Élément | Contenu |
|---------|---------|
| **Sources MVP** | Hauteurs R/L **proches** sur cliché peu incliné — contrôle de cohérence ; écart important → suspecter inversion R/L — `annotation_guidelines.md` §3 |
| **Interdiction** | **Ne pas** annoter un côté par symétrie miroir de l'autre — §3 |
| **Contexte B7** | B26_11 : rotation pelvienne légère — revue cohérence R/L recommandée |
| **Proposition conduite** | Annoter **chaque côté indépendamment** selon le contour homolatéral ; asymétrie seule **ne justifie pas** correction miroir ; inclinaison pelvienne forte → noter QC ; si doute R/L → revue avant validation |
| **STATUS** | Interdiction miroir **DEFINED** ; seuils asymétrie IT **CLINICAL VALIDATION REQUIRED** |

---

## 5. Règle PARTIAL — visibilité et codes `v` (PROPOSED)

**Objet :** documenter la distinction **VISIBLE / PARTIAL / UNCERTAIN / NON_VISIBLE** et la convention **`v=2` / `v=0`** en s'appuyant **uniquement** sur les conventions existantes du projet (`annotation_guidelines.md` §1.2). **Aucune nouvelle convention `v` n'est introduite.**

| Attribut | Valeur |
|----------|--------|
| **STATUS global** | **PROPOSED / CLINICAL VALIDATION REQUIRED** (mapping B7 → `v` pour IT) |
| **Source catégories** | Audit B7 — `bi_ischial_visibility_audit.md` §Méthode |
| **Source codes `v`** | **DEFINED** — `annotation_guidelines.md` §1.2 |

### 5.1 Catégories de visibilité (B7)

Source : `bi_ischial_visibility_audit.md` §Méthode. Libellé audit français : PARTIELLE = PARTIAL ci-dessous.

| Catégorie | Critère | Annotable ? |
|-----------|---------|:-----------:|
| **VISIBLE** | Contour osseux **caudal** de la tubérosité ischiatique identifiable ; repère annotable en `v=2` **sans extrapolation** | Oui |
| **PARTIAL** | Tubérosité **présente** mais repère caudal **moins confortable** (proximité bord image, contour partiel, marge caudale réduite) | Oui, avec prudence |
| **UNCERTAIN** | Doute **persistant** sur la structure ou le repère caudal — revue clinique nécessaire | Oui, avec revue |
| **NON_VISIBLE** | Structure **absente**, **coupée** ou **non identifiable** dans le FOV | Non (`v=0`) |

**Corpus `new_26` (B7) :** 25/26 VISIBLE bilatéral ; **1/26 PARTIAL bilatéral** (`B26_05`) ; 0 NON_VISIBLE ; 0 UNCERTAIN.

### 5.2 Convention `v` — rappel MVP (DEFINED, non modifiée)

Reprise **intégrale** de `annotation_guidelines.md` §1.2 — applicable par analogie à `IT_*` :

| Code `v` | Signification | Quand l'utiliser |
|----------|---------------|------------------|
| **2** | Point **net**, localisable **sans doute raisonnable** | Structure clairement visible |
| **1** | Point **estimé** | Uniquement si clinicien a **validé** l'usage de `v=1` — **par défaut, préférer `v=0`** |
| **0** | Point **non annoté** / non fiable / hors champ | Toujours si placement = **deviner** |

**Règle d'or (DEFINED) :** ne jamais placer un point « pour remplir le schéma ». Si vous ne le voyez pas, **`v=0`**.

**Politique IT proposée pour `v=1` :** **interdit par défaut**, comme les 14 landmarks MVP — dérogation **CLINICAL VALIDATION REQUIRED**.

### 5.3 Mapping proposé catégorie B7 → `v` (PROPOSED)

| Catégorie B7 | Conduite annotation proposée | `v` proposé | STATUS |
|--------------|------------------------------|-------------|--------|
| **VISIBLE** | Placer selon proposition B1 si repère caudal net **sans extrapolation** et **sans confusion** fémur / TD | **`v=2`** | **PROPOSED** |
| **PARTIAL** | Placer **seulement** si repère caudal identifiable **sans extrapolation** et **sans doute raisonnable** ; sinon **`v=0`** ou revue clinique. **Ne pas** forcer un point au bord | **`v=2`** si net ; **`v=0`** si doute | **PROPOSED** |
| **UNCERTAIN** | **Revue clinique** obligatoire avant validation ; ne pas figer seul | **`v=0`** par défaut jusqu'à revue | **PROPOSED** |
| **NON_VISIBLE** | Ne pas inventer de coordonnées | **`v=0`** | **DEFINED** (MVP §1.2) |

**Cas PARTIAL — précisions proposées :**

- PARTIAL **≠** NON_VISIBLE : la tubérosité est **présente** ; l'annotateur peut tenter un placement **ou** choisir `v=0` si le repère caudal n'est pas fiable.
- PARTIAL **+** bord FOV → appliquer §4.4 en complément.
- PARTIAL **+** piège fémoral → appliquer §3.6 ; rejet du candidat fémoral **avant** choix de `v`.
- **`B26_05`** : seul cas PARTIAL bilatéral — **`v=2` et `v=0` bilatéraux restent défendables** ; décision clinique **non tranchée** (revue B6).

### 5.4 Limitation importante (DEFINED)

> **La règle de visibilité B7 ne constitue pas à elle seule une définition anatomique du landmark.**

L'audit B7 évalue si un repère caudal peut être localisé sur le corpus `new_26`. Il **ne valide pas** la proposition B1. Les catégories B7 sont un **outil QC pré-annotation** ; le code `v` reste régi par MVP §1.2.

**Mapping YOLO (futur, documenté) :** `v=0` → `(0, 0, 0)` — `bi_ischial_spec.md` §17.

---

## 6. `v=0` — quand le landmark n'est pas fiable

**Convention projet existante (DEFINED)** — `annotation_guidelines.md` §1.2. Voir aussi **§5.2–§5.3** pour le mapping B7 → `v`.

| Code `v` | Signification | Quand l'utiliser |
|----------|---------------|------------------|
| **2** | Point net, localisable sans doute raisonnable | Structure clairement visible |
| **1** | Point estimé | Uniquement si clinicien a **validé** l'usage de `v=1` — **par défaut, préférer `v=0`** |
| **0** | Non annoté / non fiable / hors champ | Toujours si placement = deviner |

**Règle d'or :** ne jamais placer un point « pour remplir le schéma ».

### Situations proposées pour `IT_*` → `v=0`

| Situation | Base | STATUS |
|-----------|------|--------|
| Contour caudal tubérosité non identifiable | Règle générale §1.2 | **DEFINED** |
| Placement nécessite extrapolation hors os visible | Règle générale §1.2 | **DEFINED** |
| Doute sur structure (IT vs TD vs autre) | A2 + §1.2 | **DEFINED** |
| Un seul côté en `v=0` | `BI_ISCHIAL` non calculable (2 points requis) — `bi_ischial_spec.md` §13 | **DEFINED** (logique géométrique) |
| PARTIAL B7 + repère caudal douteux | §5.3 | **PROPOSED** |
| Piège fémoral (candidat sur diaphyse) | §3.6 ; rejeter puis `v=0` si ischion non fiable | **PROPOSED** |
| Bord FOV — extrapolation ou doute | §4.4 | **PROPOSED** |
| `v=1` sur IT | Non autorisé par défaut (comme MVP) | **DEFINED** (politique MVP) ; validation explicite **CLINICAL VALIDATION REQUIRED** si dérogation |

**Mapping YOLO (futur, documenté) :** `v=0` → `(0, 0, 0)` dans les labels — `bi_ischial_spec.md` §17.

---

## 7. R/L — règles explicites

| Règle | Détail |
|-------|--------|
| **`IT_R`** | Tubérosité ischiatique **droite du patient** (côté droit anatomique) |
| **`IT_L`** | Tubérosité ischiatique **gauche du patient** (côté gauche anatomique) |
| **Position image** | `IT_R` apparaît à **gauche de l'écran** ; `IT_L` à **droite de l'écran** en AP standard |
| **Interdiction** | **Ne jamais** déduire R/L **uniquement** de la position gauche/droite de l'écran sans vérifier le côté patient |
| **Contrôle** | Vérifier marqueurs DICOM / latéralité / anatomie (têtes fémorales, courbure iliaque) en cas de doute |
| **Symétrie** | Ne **pas** copier les coordonnées d'un côté vers l'autre — `annotation_guidelines.md` §3 |

**STATUS :** **DEFINED** (convention identique aux 14 landmarks MVP)

---

## 8. TD versus IT — section explicite

### Verdict documentaire

```
TD_R / TD_L  ≠  IT_R / IT_L
```

**`TD_*` ne doit jamais être utilisé comme remplacement de `IT_*`.**

### Preuves projet

| Source | Affirmation |
|--------|-------------|
| `landmark_specification.md` §11 | Ligne bi-ischiatique **requiert** `IT_R` / `IT_L` — hors schéma MVP 14 kp |
| Ambiguïté **A2** | Horizontal pelvien MVP = **teardrops** ; ischions = landmark futur, **pas remplacement silencieux** |
| `annotation_guidelines.md` §1.4 | Tubérosités ischiatiques interdites en MVP (schéma futur) |
| `annotation_guidelines.md` §2.1 | Ne pas annoter tubérosités à la place du teardrop ; ne pas substituer ischions pour `TD` |
| `bi_ischial_spec.md` §8 | Confirmation explicite TD ≠ IT |
| `missing_measurements_spec.md` §3.3 | `TD_*` ne peuvent pas remplacer `IT_*` |

### Tableau comparatif annotateur

| | `TD_R` / `TD_L` | `IT_R` / `IT_L` |
|---|-----------------|-----------------|
| **Structure** | Teardrop acétabulaire (larme) | Tubérosité ischiatique |
| **Position (MVP / proposition)** | Point le plus **inférieur** de la larme (**DEFINED** MVP) | Point caudal contour tubérosité (**PROPOSED** B1) |
| **Rôle** | `ITH` — horizontal pelvien VCE/Tönnis | `BI_ISCHIAL` — ligne bi-ischiatique |
| **Substitution** | **Interdite** dans les deux sens (A2) | **Interdite** |

**STATUS :** distinction TD/IT et interdiction substitution — **DEFINED**

---

## 9. Exemples (corpus `new_26`)

**Aucune annotation `IT_*` officielle** n'existe dans le projet. Les exemples s'appuient sur l'audit B7, les revues pilote B6 (NON-OFFICIAL) et les chemins images documentés.

Chemins images (lecture seule) : `datasets/yolo_pose_new_26/images/train/` ou `images/val/` selon split.

### 9.1 Cas standard — `B26_01` (pilote B6)

| Champ | Valeur |
|-------|--------|
| **Fichier** | `images/train/B26_01.png` |
| **Split** | train |
| **Visibilité B7** | VISIBLE / VISIBLE — qualité EXCELLENTE |
| **Notes B7** | Tubérosités entièrement dans le FOV ; marges caudales confortables |
| **Rôle pédagogique** | **Cas standard / référence facile** pour formation annotateurs B6 |
| **Pilote B6** | Terminé — statut `READY_FOR_B6` ; rapport `B6_pilot_B26_01.md` |
| **Coordonnées pilote** | `B6_pilot_B26_01_coords.json` — **PILOT / NON-OFFICIAL** (non intégrées aux labels) |
| **Pourquoi facile** | Contour caudal bilatéral net ; marge sous ischions confortable ; repère caudal localisable sans extrapolation |

**Piège fémoral documenté — `IT_L` :**

| Élément | Détail |
|---------|--------|
| **Mécanisme** | Candidat automatique trop **latéral** — point caudal le plus bas de l'image confondu avec la **diaphyse fémorale** gauche |
| **Candidat rejeté (PILOT)** | (2136, 2117) — diaphyse fémorale, non tubérosité ischiatique |
| **Candidat retenu (PILOT)** | (1756, 2143) — contour caudal tubérosité ischiatique gauche, **médial** au piège fémoral |
| **Leçon annotateur** | Appliquer **§3.6 Règle anti-fémur** — ne pas placer sur le fémur même si c'est le point le plus bas visible latéralement |

| Sous-point | STATUS |
|------------|--------|
| Cas standard formation | **PROPOSED** |
| Piège fémoral IT_L | **PROPOSED** (illustration clinique **CLINICAL VALIDATION REQUIRED**) |
| Coordonnées pilote | **PILOT / NON-OFFICIAL** |

### 9.2 Cas limite — `B26_05` (revue B6 obligatoire)

| Champ | Valeur |
|-------|--------|
| **Fichier** | `images/train/B26_05.png` |
| **Split** | train |
| **Dimensions** | 3008 × 3008 px |
| **Visibilité B7** | **PARTIAL** / **PARTIAL** — qualité MOYENNE |
| **Unicité corpus** | **Seul cas PARTIAL bilatéral** sur 26 images (`bi_ischial_visibility_audit.csv`) |
| **Revue B6** | Terminée — statut `READY_FOR_B6 CONDITIONNEL` ; rapport `B6_review_B26_05.md` |
| **Coordonnées revue** | `B6_review_B26_05_coords.json` — **PILOT / NON-OFFICIAL** |

**Difficultés spécifiques documentées :**

| Difficulté | Détail |
|------------|--------|
| **Marge caudale réduite** | Cas le plus serré du corpus ; `FSD_*` à ~96,7–96,9 % hauteur image |
| **Contour proche du bord** | Cortex caudal frôle le bord inférieur (~2 px au scan le plus bas) ; marge pilote conservatrice ~116–132 px selon côté |
| **Ambiguïté apex caudal** | Dispersion inter-annotateurs estimée ~110–126 px sur y (conservateur vs maximaliste bord) — voir revue B6 §5 |
| **Piège fémoral `IT_R`** | Candidat (468, 3006) sur diaphyse fémorale droite — **rejeté** ; appliquer §3.6 |
| **Piège fémoral `IT_L`** | Candidat (2575, 2912) sur diaphyse — **rejeté** ; risque modéré vs B26_01 |

**Conduite proposée B6 :**

| # | Action |
|---|--------|
| 1 | Annoter **uniquement en session supervisée** |
| 2 | Appliquer **§4.4 Règle bord FOV** + **§3.6 Règle anti-fémur** |
| 3 | Trancher **`v=2` vs `v=0`** bilatéral avec validateur clinique — les deux restent défendables |
| 4 | **Ne pas** promouvoir les coordonnées pilote au statut officiel sans validation clinique |

| Sous-point | STATUS |
|------------|--------|
| Cas limite corpus | **DEFINED** (B7) |
| Conduite annotation B26_05 | **PROPOSED** |
| Seuil `v` figé | **CLINICAL VALIDATION REQUIRED** |

### 9.3 Cas marge caudale réduite — `B26_12`

| Champ | Valeur |
|-------|--------|
| **Fichier** | `images/train/B26_12.png` |
| **Split** | train |
| **Visibilité B7** | VISIBLE / VISIBLE — qualité BONNE |
| **Notes B7** | Bord inférieur juste sous tubérosités ; marge caudale limitée |
| **Revue manuelle B7** | **Oui** |
| **Pourquoi modéré/difficile** | Visibilité B7 = VISIBLE mais confort réduit ; test de la règle bord d'image |
| **STATUS placement** | **CLINICAL VALIDATION REQUIRED** (seuil VISIBLE → `v=2`) |

### 9.4 Cas gaz intestinal — `B26_07`

| Champ | Valeur |
|-------|--------|
| **Fichier** | `images/train/B26_07.png` |
| **Split** | train |
| **Visibilité B7** | VISIBLE / VISIBLE — qualité BONNE |
| **Notes B7** | Gaz intestinal/fécal central abondant (n'obstrue pas les tubérosités) |
| **Revue manuelle B7** | **Oui** — confirmer repère IT fiable |
| **Pourquoi modéré** | Qualité image dégradée au centre ; tubérosités latérales restent visibles selon B7 |
| **Proposition conduite** | Annoter si contour caudal latéral net ; sinon `v=0` |
| **STATUS placement** | **CLINICAL VALIDATION REQUIRED** |

### 9.5 Cas rotation pelvienne — `B26_11`

| Champ | Valeur |
|-------|--------|
| **Fichier** | `images/train/B26_11.png` |
| **Split** | train |
| **Visibilité B7** | VISIBLE / VISIBLE — qualité BONNE |
| **Notes B7** | Rotation/inclinaison pelvienne légère (obturateurs asymétriques) |
| **Revue manuelle B7** | **Oui** — cohérence R/L |
| **Pourquoi modéré** | Asymétrie apparente ; risque d'inversion R/L si on se fie à l'écran seul |
| **Proposition conduite** | Vérifier côté patient ; annoter indépendamment R et L ; pas de miroir |
| **STATUS placement** | R/L **DEFINED** ; seuil rotation **CLINICAL VALIDATION REQUIRED** |

---

## 10. Checklist annotateur

### Avant annotation

- [ ] **Bonne structure** — cible = tubérosité ischiatique, pas teardrop / obturateur / pubis / **fémur** (§3.6)
- [ ] **Bon côté R/L** — `IT_R` = droit patient (gauche image) ; vérification latéralité si doute
- [ ] **Contour osseux identifiable** — bord caudal proposé visible **sans extrapolation** (§4.4)
- [ ] **Position conforme à la proposition B1** — point caudal/inférieur du contour osseux (**en attente validation clinique définitive**)
- [ ] **Catégorie B7 consultée** — VISIBLE / PARTIAL / UNCERTAIN / NON_VISIBLE (§5)

### Après annotation

- [ ] **`IT_R` vérifié** — côté droit patient, proposition B1 respectée ou `v=0`
- [ ] **`IT_L` vérifié** — côté gauche patient, idem
- [ ] **Aucun remplacement par TD** — `TD_*` et `IT_*` distincts (A2)
- [ ] **Anti-fémur vérifié** — point sur tubérosité ischiatique pelvienne, pas diaphyse (§3.6)
- [ ] **Bord FOV vérifié** — pas d'extrapolation hors image (§4.4)
- [ ] **Visibilité correctement renseignée** — `v=2` seulement si net (MVP §1.2) ; pas de `v=2` par confort
- [ ] **Cas PARTIAL / ambigu** — `v=0` ou revue clinique selon §5.3 ; **B26_05** → session supervisée

---

## 11. Bloc de validation clinique

**B1 clinical validation required** — points à trancher **avant** B6 (ré-annotation) :

| Point | Statut actuel |
|-------|---------------|
| **Position exacte** | Proposition caudale/inférieure = **CANDIDATE** — **CLINICAL VALIDATION REQUIRED** |
| **Cortical vs centre** | **CLINICAL VALIDATION REQUIRED** |
| **Traitement des contours larges** | **CLINICAL VALIDATION REQUIRED** |
| **Traitement des cas partiels** | **CLINICAL VALIDATION REQUIRED** (seuil PARTIAL → `v=2` vs `v=0`) |
| **Règle bord FOV (§4.4)** | **PROPOSED** — rédigée post-revue B26_05 | **CLINICAL VALIDATION REQUIRED** (seuil marge) |
| **Règle anti-fémur (§3.6)** | **PROPOSED** — pilote B26_01 + revue B26_05 | **CLINICAL VALIDATION REQUIRED** (seuils latéraux) |
| **Règle PARTIAL (§5)** | **PROPOSED** — mapping B7 → `v` | **CLINICAL VALIDATION REQUIRED** (seuil PARTIAL → `v=2`) |
| **Règle `v=0`** | Règle générale MVP **DEFINED** ; cas limites IT **CLINICAL VALIDATION REQUIRED** |

**Ne pas décider ces points arbitrairement** dans une campagne d'annotation sans validation radiologique / orthopédique et illustrations.

---

## Tableau récapitulatif — Règles

| Règle | Statut | Source | Validation clinique requise ? |
|-------|--------|--------|:-----------------------------:|
| Structure = tubérosité ischiatique bilatérale | **DEFINED** | `landmark_specification.md` §11 ; `bi_ischial_spec.md` | Non |
| `BI_ISCHIAL = droite(IT_R, IT_L)` | **DEFINED** | `missing_measurements_spec.md` §3.2 | Non |
| Convention R/L (droit patient = gauche image) | **DEFINED** | `annotation_guidelines.md` §1.1 | Non |
| Interdiction copie miroir R/L | **DEFINED** | `annotation_guidelines.md` §3 | Non |
| `TD_R/TD_L ≠ IT_R/IT_L` | **DEFINED** | A2 ; `bi_ischial_spec.md` §8 | Non |
| Interdiction substitution TD pour IT | **DEFINED** | A2 ; §2.1 guide MVP | Non |
| Proposition B1 : point caudal/inférieur contour osseux tubérosité | **PROPOSED** | B1 CANDIDATE ; `missing_measurements_audit.md` §3 | **Oui** |
| Contour osseux tubérosité (vs tissus mous / ilio-ischiatique) | **PROPOSED** | Dérivé proposition B1 + guide TD | **Oui** |
| Point le plus caudal identifiable sans extrapolation | **PROPOSED** | B1 CANDIDATE | **Oui** |
| Cortical vs centre vs sommet | **CLINICAL VALIDATION REQUIRED** | `bi_ischial_B1_position_audit.md` §3 | **Oui** |
| Contour large / forme étendue | **CLINICAL VALIDATION REQUIRED** | `bi_ischial_B1_position_audit.md` §4 | **Oui** |
| Seuils tissus mous vs os | **CLINICAL VALIDATION REQUIRED** | — | **Oui** |
| Tubérosité partiellement visible | **CLINICAL VALIDATION REQUIRED** | B7 + §1.2 ; conduite **PROPOSED** | **Oui** |
| Superposition osseuse | **CLINICAL VALIDATION REQUIRED** | Analogie FHC §2.2 ; conduite **PROPOSED** | **Oui** |
| Contour difficile à suivre | **CLINICAL VALIDATION REQUIRED** | §1.2 ; conduite **PROPOSED** | **Oui** |
| **Règle bord FOV (§4.4)** | **PROPOSED** | B7 ; revue B26_05 ; MVP §1.2 | **Oui** |
| **Règle anti-fémur (§3.6)** | **PROPOSED** | Pilote B26_01 ; revue B26_05 | **Oui** |
| **Règle PARTIAL + mapping `v` (§5)** | **PROPOSED** | B7 + MVP §1.2 | **Oui** |
| Mauvaise qualité radiographique → `v=0` | **DEFINED** (général) | `annotation_guidelines.md` §1.2 | Partiel (seuils IT) |
| Asymétrie / rotation pelvienne | **CLINICAL VALIDATION REQUIRED** | §3 ; B7 B26_11 | **Oui** |
| Catégories VISIBLE / PARTIAL / UNCERTAIN / NON_VISIBLE | **DEFINED** (audit B7) | `bi_ischial_visibility_audit.md` ; §5 | Non (QC visibilité) |
| B7 ≠ définition anatomique IT | **DEFINED** | `bi_ischial_B1_position_audit.md` §8 ; §5.4 | Non |
| Mapping B7 → `v=2` / `v=0` | **PROPOSED** | §5.3 ; MVP §1.2 | **Oui** |
| Exemple standard B26_01 + piège fémoral `IT_L` | **PROPOSED** | §9.1 ; pilote B6 NON-OFFICIAL | **Oui** (illustration) |
| Exemple limite B26_05 (PARTIAL, bord, fémur) | **PROPOSED** | §9.2 ; revue B6 NON-OFFICIAL | **Oui** |
| `v=0` si deviner / non fiable | **DEFINED** | `annotation_guidelines.md` §1.2 | Non |
| `v=1` interdit par défaut | **DEFINED** | `annotation_guidelines.md` §1.2 | **Oui** si dérogation IT |
| Un `IT_*` en `v=0` → pas de `BI_ISCHIAL` | **DEFINED** | `bi_ischial_spec.md` §13 | Non |
| Illustrations annotées IT | **ABSENT** | — | **Oui** (prérequis B1/B4) |
| Annotations IT existantes | **ABSENT** | 14 kp seulement | — |

---

## Statut B4

```
B4 = READY FOR B6 CONDITIONALLY
B1 = CANDIDATE (proposition placement documentée, non validée cliniquement)
```

### Motivation

| Pour | Contre / réserves |
|------|-------------------|
| Règles **FOV**, **PARTIAL**, **anti-fémur** documentées (PROPOSED) | Définition B1 toujours **non validée** cliniquement |
| Pilote **B26_01** + revue **B26_05** intégrés comme exemples | Illustrations cliniques annotées encore **absentes** |
| Mapping `v=2`/`v=0` aligné sur MVP §1.2 — **aucune nouvelle convention** | Seuils opérationnels (marge bord, PARTIAL → `v=2`) **non tranchés** |
| Checklist annotateur enrichie | Validation radiologique / orthopédique **encore requise** pour figer B1 |

### Conditions campagne B6 (inchangées)

1. **25 cas VISIBLE B7** — annotation selon ce guide (règles PROPOSED).
2. **`B26_05`** — **session supervisée** obligatoire ; trancher `v=2` vs `v=0` avec validateur.
3. **`B26_07`, `B26_11`, `B26_12`** — revues recommandées (plan B6).
4. **Aucune annotation officielle** ni intégration YOLO tant que B5/B6 formels non clos.
5. Coordonnées pilote B26_01 / B26_05 restent **PILOT / NON-OFFICIAL**.

**Prochaine étape recommandée :** lancer campagne B6 sur 26 images avec ce guide ; illustrations sur B26_01, B26_05, B26_12 en parallèle ; clôture validation clinique B1 en continu.

---

*Guide B4 révisé — seuls `bi_ischial_annotation_guidelines.md` et `bi_ischial_annotation_guidelines.csv` modifiés ; aucun label, dataset, YAML, modèle, backend ou Flutter touché.*
