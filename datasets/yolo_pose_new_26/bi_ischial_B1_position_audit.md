# Audit read-only B1 — Position anatomique exacte `IT_R` / `IT_L`

**Généré :** 2026-08-28  
**Mode :** audit read-only — **aucune modification** du dataset, labels, YAML, modèles, annotations ou code  
**Prérequis :** B7 **FERMÉ** (visibilité corpus `new_26` documentée)  
**Sources inspectées uniquement :**

- `docs/landmark_specification.md`
- `docs/annotation_guidelines.md`
- `datasets/yolo_pose_new_26/bi_ischial_spec.md`
- `datasets/yolo_pose_new_26/missing_measurements_spec.md`
- `datasets/yolo_pose_new_26/missing_measurements_audit.md`
- `datasets/yolo_pose_new_26/bi_ischial_visibility_audit.md`
- `docs/dataset_analysis.md` §14
- `docs/annotation_pilot_protocol.md` (A2)
- `docs/dataset1_analysis.md` §14 (contexte)
- `docs/retuve_feasibility_test.md` (absence IT dans modèles tiers)

**Landmarks placés :** aucun — lecture documentaire uniquement  
**Hypothèses complétées :** aucune — toute information absente des sources est marquée **SPECIFICATION REQUIRED**

---

## Contexte B7 (entrée B1)

| Métrique | Résultat |
|----------|----------|
| IT_R VISIBLE | 25/26 (96,2 %) |
| IT_L VISIBLE | 25/26 (96,2 %) |
| IT_R et IT_L tous deux VISIBLE | 25/26 (96,2 %) |
| Annotables (VISIBLE + PARTIELLE) | 26/26 (100 %) |
| Cas particulier | **B26_05** — PARTIELLE bilatérale (bord image) |
| Exclusions visibilité | **Aucune** |

Source : `bi_ischial_visibility_audit.md`

---

## 1. Structure anatomique exacte représentée par `IT_R` / `IT_L`

### Ce que les sources affirment

| Élément | `IT_R` | `IT_L` |
|---------|--------|--------|
| **Structure** | **Tubérosité ischiatique** droite | **Tubérosité ischiatique** gauche |
| **ID proposé** | LM-17 (extension catalogue §11) | LM-18 |
| **Rôle** | Extrémité **droite** de la ligne bi-ischiatique | Extrémité **gauche** de la ligne bi-ischiatique |
| **Ligne dérivée** | `BI_ISCHIAL = droite(IT_R, IT_L)` | Idem |
| **Statut schéma actuel** | Absent des 14 keypoints MVP | Absent des 14 keypoints MVP |

**Sources :** `landmark_specification.md` §11 ; `missing_measurements_spec.md` §3.2 ; `bi_ischial_spec.md` §1–2, §9

### Ce que les sources n'affirment pas

- Morphologie osseuse détaillée (corps ischiatique vs tubérosité seule vs ramus ischiatique).
- Relation précise avec la **ligne ilio-ischiatique** (mentionnée pour le repérage du teardrop, pas pour IT).
- Correspondance avec les masques segmentation `ischium` (Dataset2) : les masques **ne fournissent pas** de keypoint tubérosité annoté.

**Statut question 1 :** **PARTIELLEMENT DEFINED** — structure = tubérosité ischiatique bilatérale ; détail morphologique au-delà = **SPECIFICATION REQUIRED**

---

## 2. Position du point sur cette structure

### État documenté dans les sources primaires

| Source | Contenu sur la position |
|--------|-------------------------|
| `landmark_specification.md` §11 | Exige `IT_R` / `IT_L` pour la ligne bi-ischiatique — **sans préciser** le point sur la tubérosité |
| `annotation_guidelines.md` | **Aucune fiche** `IT_*` (14 landmarks MVP uniquement) ; §1.4 interdit les tubérosités en MVP |
| `missing_measurements_spec.md` §5.3 B1 | Liste ouverte : sommet inférieur, centre, bord — **avec illustrations** (non réalisées) |
| `missing_measurements_audit.md` §3 | Proposition **non validée** : « point le plus caudal / inférieur identifiable » — suivie de « **À figer en spec** avant annotation » |
| `bi_ischial_spec.md` §3 | Questions ouvertes B1 : sommet inférieur ? centre géométrique ? bord caudal ? point le plus inférieur sur l'AP ? |

### Analogie documentée (teardrop `TD_*`, structure voisine mais distincte)

Pour `TD_R`/`TD_L`, le guide impose le point le plus **inférieur** de la larme acétabulaire — **pas** le centre (`annotation_guidelines.md` §2.1). Cette règle s'applique au teardrop, **pas** aux tubérosités ischiatiques ; aucune source ne dit que la même règle s'applique à `IT_*`.

**Statut question 2 :** **SPECIFICATION REQUIRED**

---

## 3. Point cortical vs centre de structure

### État documenté

| Landmark | Règle documentée | Source |
|----------|------------------|--------|
| `TD_*` | Extrémité inférieure, **pas** le centre de la larme | `annotation_guidelines.md` §2.1 |
| `FHC_*` | **Centre** géométrique (cercle best-fit) | `landmark_specification.md` §4 LM-03 |
| `IT_*` | **Non documenté** | — |

Aucune source ne tranche si `IT_*` doit être :

- un point **cortical** (bord osseux projeté),
- le **centre** géométrique de la tubérosité projetée,
- un **sommet** osseux,
- un point sur l'**axe médian** de la tubérosité.

**Statut question 3 :** **SPECIFICATION REQUIRED**

---

## 4. Comment choisir le point lorsque la tubérosité a une forme étendue

### État documenté

**Aucune règle spécifique `IT_*`** dans les sources inspectées.

Règles analogiques **non transférables sans validation clinique** :

| Analogie | Règle | Applicabilité IT |
|----------|-------|------------------|
| `TD_*` | Choisir l'extrémité la plus inférieure nette ; pas le centre | **Non affirmée** pour IT |
| `ASL_*` | Point le plus latéral de la bande sclérotique | Structure différente |
| `FSD_*` | Point le plus distal **identifiable** dans le FOV | Diaphyse, pas tubérosité |

**Statut question 4 :** **SPECIFICATION REQUIRED**

---

## 5. Comment gérer une superposition osseuse

### État documenté pour `IT_*`

**Non documenté** spécifiquement.

### Règle analogique documentée (autre landmark)

`annotation_guidelines.md` §2.2 (`FHC_*`), cas « Superposition pubis / ischion » :

> Zoomer ; si contour douteux → `v=0`

Cette conduite concerne le **contour céphalique**, pas la tubérosité ischiatique. Aucune source ne l'étend explicitement à `IT_*`.

Cas ambigus listés dans `bi_ischial_spec.md` §6 comme **non documentés** : superposition osseuse, rotation pelvienne forte, confusion tubérosité / ligne ilio-ischiatique.

**Statut question 5 :** **SPECIFICATION REQUIRED**

---

## 6. Comment gérer une tubérosité partiellement visible

### Sources applicables

| Source | Contenu |
|--------|---------|
| `annotation_guidelines.md` §1.2 | Règles générales `v=0` / `v=1` / `v=2` ; règle d'or : ne jamais placer un point « pour remplir le schéma » |
| `bi_ischial_spec.md` §5 | Pas de fiche IT ; conduite spécifique = **SPECIFICATION REQUIRED (B1, B4, B7)** |
| `bi_ischial_visibility_audit.md` | Critères B7 et recommandations opérationnelles (audit, non spec B1 validée) |

### Critères et conduite B7 (audit visibilité — langage « repère caudal », position B1 non figée)

| Situation (audit B7) | Conduite recommandée (audit, non implémentée) |
|--------------------|-----------------------------------------------|
| Tubérosité nette, repère caudal identifiable | `v=2` attendu |
| Tubérosité partielle / bord image / doute | `v=0` **ou** revue clinique — **pas** de point inventé |
| Un seul côté `v=0` | `BI_ISCHIAL` non calculable (2 points requis) |
| Gaz intestinal / rotation | Annoter si os visible ; sinon `v=0` |

**Note méthodologique :** l'audit B7 utilise le terme « repère caudal » et « contour osseux caudal » pour **évaluer la visibilité**, pas comme définition anatomique validée pour B1 (`bi_ischial_spec.md` §3, §39).

**Statut question 6 :** **SPECIFICATION REQUIRED** pour la conduite d'annotation IT — seules les règles générales `v=0`/`v=2` sont **DEFINED** par analogie

---

## 7. Comment gérer une limite d'image proche

### État documenté

| Source | Contenu |
|--------|---------|
| `bi_ischial_visibility_audit.md` | **B26_05** : seul cas PARTIELLE bilatérale — tubérosités visibles mais très proches du bord caudal ; repère caudal moins confortable |
| `bi_ischial_visibility_audit.md` | **B26_12** : marge caudale réduite — revue manuelle recommandée malgré VISIBLE |
| `annotation_guidelines.md` §2.7 (`FSD_*`) | Bord d'image coupe le fémur → annoter le dernier niveau fiable **dans** l'image ; règle de distance — **pour diaphyse, pas IT** |

Recommandation audit B7 pour bord image : `v=0` ou revue clinique ; conserver **B26_05** dans le corpus (aucune exclusion).

**Statut question 7 :** **SPECIFICATION REQUIRED** pour règle IT formelle — contexte corpus et recommandations B7 **documentés** mais **non validés** comme spec d'annotation B1/B4

---

## 8. Critères VISIBLE / PARTIELLE / INCERTAINE / NON VISIBLE

### Définition documentée (audit B7 uniquement)

Source : `bi_ischial_visibility_audit.md` §Méthode

| Niveau | Critère documenté (B7) |
|--------|------------------------|
| **VISIBLE** | Contour osseux **caudal** de la tubérosité ischiatique identifiable ; repère annotable en `v=2` sans extrapolation |
| **PARTIELLE** | Tubérosité présente mais repère caudal moins confortable (proximité bord image, contour partiel) |
| **NON VISIBLE** | Structure absente, coupée ou non identifiable |
| **INCERTAINE** | Doute persistant nécessitant revue clinique |

### Résultats corpus `new_26` (B7 fermé)

| Niveau | IT_R | IT_L |
|--------|------|------|
| VISIBLE | 25/26 | 25/26 |
| PARTIELLE | 1/26 (B26_05) | 1/26 (B26_05) |
| NON VISIBLE | 0/26 | 0/26 |
| INCERTAINE | 0/26 | 0/26 |

**Limitation :** ces critères servent l'**audit de visibilité** (B7). Ils **ne constituent pas** la définition anatomique de la position du point (B1). Le terme « repère caudal » présuppose une orientation du point non figée cliniquement.

**Statut question 8 :** critères B7 **DEFINED** pour l'audit visibilité ; lien avec position anatomique exacte IT = **SPECIFICATION REQUIRED**

---

## 9. Quand utiliser `v=0`

### Règles générales documentées (`annotation_guidelines.md` §1.2)

| Code `v` | Signification | Quand l'utiliser |
|----------|---------------|------------------|
| **2** | Point net, localisable sans doute raisonnable | Structure clairement visible |
| **1** | Point estimé (contours flous) | Uniquement si clinicien a validé l'usage de `v=1` — **par défaut, préférer `v=0`** |
| **0** | Non annoté / non fiable / hors champ | Toujours si placement = deviner |

**Règle d'or :** ne jamais placer un point « pour remplir le schéma ».

### Règles spécifiques `IT_*` documentées

| Situation | Conduite | Source |
|-----------|----------|--------|
| Point non identifiable / deviner seulement | `v=0` | Règle générale §1.2 |
| Teardrop illisible — tentation ischions pour **TD** | Ne pas substituer ; journaliser A2 | `annotation_guidelines.md` §2.1, A2 |
| Tubérosité partielle / bord image / doute (IT) | `v=0` ou revue clinique | `bi_ischial_visibility_audit.md` (recommandation audit) |
| Un seul `IT_*` en `v=0` | `BI_ISCHIAL` non calculable | `bi_ischial_spec.md` §13 (logique 2 points) |
| `v=1` sur IT | **Non autorisé par défaut** — validation clinique requise (analogie MVP) | §1.2 |

**Statut question 9 :** règles générales **DEFINED** ; seuils et cas limites IT **SPECIFICATION REQUIRED** (B4)

---

## 10. Règle de symétrie R/L

### Règles documentées (figées projet)

Source : `annotation_guidelines.md` §1.1, §3 ; `landmark_specification.md` conventions

| Règle | Détail |
|-------|--------|
| Vue | Radiographie **AP bassin** |
| `IT_R` | Côté **droit patient** = **gauche** de l'image |
| `IT_L` | Côté **gauche patient** = **droite** de l'image |
| Interdiction | **Ne jamais** inverser R/L selon gauche/droite écran sans vérifier le côté patient |
| Symétrie | Hauteurs R/L **proches** sur cliché peu incliné — contrôle de cohérence, pas preuve d'identification |
| Copie miroir | **Interdite** — « Ne pas dupliquer les coordonnées d'un côté vers l'autre » (`annotation_guidelines.md` §3) |

**Statut question 10 :** **DEFINED** (identique aux 14 landmarks MVP)

---

## 11. Exemples de cas faciles et difficiles (sources existantes)

### Annotations / exemples IT dans le projet

| Élément | État |
|---------|------|
| Annotations `new_26` | **14 landmarks uniquement** — **aucune** annotation `IT_R` / `IT_L` existante |
| Fiches illustrées IT | **Absentes** (`annotation_guidelines.md` ne couvre pas IT) |
| Modèles Retuve / V2 | Tubérosités ischiatiques **absentes** (`retuve_feasibility_test.md`) |
| Masques `ischium` | Présents Dataset2 — **insuffisants** comme substitut keypoint (`dataset_analysis.md` §14) |

### Cas faciles documentés (audit B7 — visibilité, pas placement validé)

| Catégorie | Images | Détail source |
|-----------|--------|---------------|
| VISIBLE bilatéral, qualité EXCELLENTE | 20/26 | `bi_ischial_visibility_audit.md` |
| VISIBLE bilatéral, qualité BONNE | 5/26 | B26_07, B26_11, B26_12, B26_22, B26_23 — certaines avec revue manuelle recommandée |
| FOV inférieur généreux pour ischions | B26_17, B26_18 | Large marge caudale (audit B7) |

### Cas difficiles documentés (audit B7)

| Image | Problème documenté | Visibilité B7 | Revue manuelle |
|-------|-------------------|---------------|:--------------:|
| **B26_05** | Bord de l'image ; marge caudale minimale | PARTIELLE / PARTIELLE | **Oui** — confirmer repère caudal vs `v=0` |
| **B26_07** | Gaz intestinal central abondant | VISIBLE / VISIBLE | **Oui** — confirmer repère IT fiable |
| **B26_11** | Rotation pelvienne légère | VISIBLE / VISIBLE | **Oui** — cohérence R/L |
| **B26_12** | Marge caudale réduite | VISIBLE / VISIBLE | **Oui** — annotabilité `v=2` |

### Cas analogiques documentés (structures voisines, pas IT)

| Situation | Landmark | Conduite | Source |
|-----------|----------|----------|--------|
| Teardrop illisible | `TD_*` | `v=0` ; ne pas substituer ischions | §2.1 |
| Superposition pubis/ischion | `FHC_*` | Zoomer ; si doute → `v=0` | §2.2 |
| Pilote A2 | `TD_*` | Teardrop illisible ; tentation ischions — journaliser | `annotation_pilot_protocol.md` |

**Statut question 11 :** exemples visibilité B7 **documentés** ; **aucun** exemple d'annotation IT placée ; cas limites placement = **SPECIFICATION REQUIRED** + illustrations B1/B4

---

## Synthèse par question

| # | Question | Statut | Source principale |
|---|----------|--------|-------------------|
| 1 | Structure anatomique | **PARTIELLEMENT DEFINED** | §11 ; `bi_ischial_spec.md` |
| 2 | Position sur la structure | **SPECIFICATION REQUIRED** | §11 ; B1 ouvert |
| 3 | Cortical vs centre | **SPECIFICATION REQUIRED** | — |
| 4 | Forme étendue | **SPECIFICATION REQUIRED** | — |
| 5 | Superposition osseuse | **SPECIFICATION REQUIRED** | Analogie FHC non étendue |
| 6 | Visibilité partielle | **SPECIFICATION REQUIRED** (IT) ; règles `v` générales **DEFINED** | §1.2 ; B7 audit |
| 7 | Limite d'image | **SPECIFICATION REQUIRED** (règle IT) ; contexte B7 **documenté** | B7 ; B26_05 |
| 8 | VISIBLE / PARTIELLE / … | **DEFINED** (B7 audit) ; lien position B1 **SPECIFICATION REQUIRED** | `bi_ischial_visibility_audit.md` |
| 9 | Quand `v=0` | Général **DEFINED** ; cas IT **SPECIFICATION REQUIRED** | §1.2 ; B7 recommandations |
| 10 | Symétrie R/L | **DEFINED** | §1.1, §3 |
| 11 | Exemples faciles / difficiles | Visibilité B7 **documentée** ; placement IT **absent** | B7 ; pas d'annotations IT |

---

## Éléments DEFINED (supportés par les sources)

Les éléments suivants sont **établis** sans hypothèse additionnelle :

1. **`IT_R` / `IT_L`** désignent la **tubérosité ischiatique** droite et gauche patient respectivement.
2. **`BI_ISCHIAL = droite(IT_R, IT_L)`** — construction géométrique de la ligne bi-ischiatique.
3. **`TD_R` / `TD_L` ≠ `IT_R` / `IT_L`** — teardrops et ischions sont des landmarks **distincts** ; substitution interdite (A2).
4. **Convention R/L** identique au MVP (droite patient = gauche image).
5. **Interdiction** d'annoter IT en MVP 14 kp ; ré-annotation requise pour extension 16 kp.
6. **Règles générales de visibilité** `v=0`/`v=2` et interdiction de copie miroir R/L.
7. **Corpus `new_26`** : 26/26 annotables en visibilité (B7) ; 1 cas PARTIELLE (B26_05).

---

## Proposition documentée mais NON VALIDÉE (ne pas traiter comme définition B1)

Source : `missing_measurements_audit.md` §3, citée aussi dans `bi_ischial_spec.md` §3 :

> Tubérosité ischiatique — **point le plus caudal / inférieur identifiable**

Cette formulation est explicitement suivie de :

> **À figer en spec avant annotation** : définition exacte du point sur la tubérosité (sommet vs centre vs bord inférieur)

**Verdict :** proposition d'audit, **pas** définition clinique validée. **Ne pas** utiliser comme base de ré-annotation tant que B1 n'est pas fermé cliniquement.

---

## Définition finale proposée (uniquement si supportée par les sources)

```
IT_R = landmark sur la tubérosité ischiatique du côté droit patient (gauche image),
       extrémité droite de BI_ISCHIAL = droite(IT_R, IT_L).

IT_L = landmark sur la tubérosité ischiatique du côté gauche patient (droite image),
       extrémité gauche de BI_ISCHIAL.

Position exacte du point SUR la tubérosité : SPECIFICATION REQUIRED (B1 non fermé).
```

Aucune définition plus précise (sommet, bord, centre, cortical) n'est **supportée** par les sources primaires validées.

---

## Points restant à valider cliniquement

| Priorité | Sujet | Bloquant pour |
|----------|-------|---------------|
| **P0** | Position exacte sur la tubérosité (sommet inférieur vs bord caudal cortical vs centre vs point le plus inférieur AP) | B1, B4, B6 |
| **P0** | Illustrations annotées sur cas standards et cas limites (≥ B26_05, B26_12) | B1, B4 |
| **P1** | Conduite tubérosité partiellement visible (seuil PARTIELLE → `v=2` vs `v=0`) | B4 |
| **P1** | Superposition osseuse / confusion ligne ilio-ischiatique | B4 |
| **P1** | Forme étendue de la tubérosité — règle de choix unique | B1, B4 |
| **P1** | Autorisation ou interdiction formelle de `v=1` pour IT | B4 |
| **P2** | Métrique de sortie bi-ischiale (angle, distance, inclinaison) | B2 |
| **P2** | Calibration mm/px si distance | B3 |
| **P2** | Revue clinique des 4 cas B7 signalés (B26_05, 07, 11, 12) avec position IT figée | B6 |

---

## Impact sur la réannotation des 26 images

| Aspect | Impact |
|--------|--------|
| **Blocage immédiat** | Ré-annotation IT (B6) **impossible** tant que B1 position exacte + B4 fiches ne sont pas validés |
| **Corpus eligible** | 26/26 images annotables en visibilité (B7) — **aucune exclusion** |
| **Haute confiance attendue** | 25/26 si critère VISIBLE strict B7 |
| **Revue obligatoire post-B1** | **B26_05** (PARTIELLE, bord image) — politique `v=2` vs `v=0` à trancher avec position figée |
| **Revue recommandée** | B26_07, B26_11, B26_12 — selon règles IT validées |
| **Labels actuels** | 14 kp inchangés — ajout futur de 2 triplets (`IT_R`, `IT_L`) → 53 colonnes |
| **Training** | Interdit (T1) tant que B1–B6 ouverts |
| **Risque inter-annotateurs** | **Élevé** sans spec B1 — proposition « caudal » non validée créerait variabilité |

### Scénarios post-validation B1

| Scénario | Images concernées | Action |
|----------|-------------------|--------|
| Position caudale/inferieure validée + B26_05 acceptée | 26 | Annoter les 26 ; revue clinique B26_05 |
| Position validée mais B26_05 rejetée en `v=2` | 25 + 1 partielle | IT bilatéral `v=0` ou unilatéral sur B26_05 → pas de `BI_ISCHIAL` ce cliché |
| Position non validée (B1 ouvert) | 26 | **Ne pas réannoter** |

---

## Verdict final B1

```
B1 = SPECIFICATION REQUIRED
```

**Motif :** la structure (tubérosité ischiatique bilatérale), la convention R/L, la construction `BI_ISCHIAL`, la distinction avec `TD_*` et les règles générales `v=0` sont documentées ; en revanche, **la position anatomique exacte du point sur la tubérosité ischiatique n'est figée dans aucune source primaire validée** du projet.

La proposition « point le plus caudal / inférieur identifiable » (`missing_measurements_audit.md`) et le langage « repère caudal » de l'audit B7 **ne suffisent pas** à fermer B1 sans validation clinique explicite et illustrations.

**Prochaine étape recommandée (hors scope de cet audit) :** validation radiologique / orthopédique de la position sur tubérosité + rédaction fiches B4 — **sans** modifier labels, dataset ou YAML.

---

*Audit read-only B1 — seuls `bi_ischial_B1_position_audit.md` et `bi_ischial_B1_position_audit.csv` créés ; aucun autre fichier du projet modifié.*
