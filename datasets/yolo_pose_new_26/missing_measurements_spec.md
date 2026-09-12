# Spécification des mesures manquantes — coxométrie adulte

**Généré :** 2026-08-28 (Alpha angle — mise à jour bibliographique)  
**Mode :** préparation de spécification — **aucune modification** du code, dataset, labels, V2, V3, backend ou Flutter  
**Sources :** `docs/landmark_specification.md`, `docs/annotation_guidelines.md`, `docs/dataset1_analysis.md`, `docs/dataset_analysis.md`, `datasets/yolo_pose_new_26/missing_measurements_audit.md`, recherche bibliographique (méthode de Nötzli)

---

## Tableau récapitulatif

| Mesure | Définition | Landmarks | Formule | Calibration | Statut |
|--------|------------|-----------|---------|-------------|--------|
| VCE / Wiberg | Spec §3.1 — angle entre verticale ⟂ ITH par FHC et FHC→ASL | `TD_R`, `TD_L`, `FHC`, `ASL` | `vce_angle()` | Degrés (aucune mm/px) | **IMPLEMENTED** |
| Tönnis | Spec §3.2 — angle entre horizontale ∥ ITH par ASM et ASM→ASL | `TD_R`, `TD_L`, `ASM`, `ASL` | `tonnis_angle()` | Degrés | **IMPLEMENTED** |
| CCD | Spec §3.3 — angle médial entre axe col FHC→FNM et axe diaphyse FSP→FSD | `FHC`, `FNM`, `FSP`, `FSD` | `ccd_angle()` | Degrés | **IMPLEMENTED** |
| **Femoral offset** | Spec §11 (partielle) — offset fémoral basé sur axe diaphysaire + `FHC` ; définition et mm/px **à figer** | `FHC_*`, `FSP_*`, `FSD_*` (ligne dérivée `SHAFT_*`) | Construction documentée ; **métrique non figée** | **mm/px requis, méthode non définie** | **SPECIFICATION REQUIRED** |
| **Alpha angle** | Angle entre l'axe du col fémoral et la ligne FHC → point de perte de sphéricité (cercle de meilleure adaptation) ; méthode classique de **Nötzli** ; **vue et seuils à figer** | Éléments géométriques conceptuels (voir §2) — **aucun nouveau landmark YOLO** pour l'instant | Construction Nötzli documentée ; **seuil et vue cible non figés** | Degrés ; pas de mm/px | **SPECIFICATION REQUIRED** |
| **Bi-ischial / ligne bi-ischiatique** | Spec §11 — ligne bi-ischiatique ; nécessite `IT_R` / `IT_L` ; teardrops non substituables (A2) | `IT_R`, `IT_L` (**absents** du schéma 14 kp) | **Non définie** (sortie angle vs distance non figée) | Dépend de la métrique choisie | **NEW LANDMARKS REQUIRED** |

---

## 1. Femoral offset

### 1.1 Définition actuellement proposée (documentation existante)

**Source principale :** `docs/landmark_specification.md` §11 « Hors MVP » :

> offset fémoral (axe diaphysaire + `FHC`, mais calibration mm/px et définition d'offset **à figer**)

**Compléments documentés :**

| Source | Contenu |
|--------|---------|
| §2.3 | Ligne dérivée `SHAFT_R` / `SHAFT_L` = droite `FSP_*` → `FSD_*` = **axe diaphysaire** |
| §4 LM-03/04 | `FHC_*` = centre de la tête fémorale (cercle Mose / best-fit) |
| §4 LM-11/12 | `FSP_*` = point proximal de l'axe diaphysaire, sous le petit trochanter |
| §4 LM-13/14 | `FSD_*` = point distal de l'axe diaphysaire **dans le FOV** du cliché |
| Ambiguïté **A7** | Si FOV trop court, `FSP` ≈ `FSD` → axe diaphysaire **instable** ; règle proposée : séparation minimale ou `v=0` pour `FSD` |
| `docs/dataset1_analysis.md` §14 | « Requiert centre de tête + **axe diaphysaire long** » |
| `docs/dataset_analysis.md` §14 | « Requiert centre de tête + axe diaphysaire fémoral long ; **non couvert** » |

**Ce que la documentation affirme :** l'offset fémoral dépend géométriquement du **centre de tête** et de l'**axe diaphysaire** construit à partir des landmarks shaft existants.

**Ce que la documentation n'affirme pas :** le type exact d'offset (distance perpendiculaire, horizontale, médiale/latérale, signe, intervalles normaux). La formulation « **à figer** » interdit toute supposition clinique dans ce document.

### 1.2 Landmarks utilisés

Par côté (`R` ou `L`), d'après la spec :

| Landmark | ID | Rôle documenté |
|----------|-----|----------------|
| `FHC_R` / `FHC_L` | LM-03 / LM-04 | Centre tête fémorale — point de référence tête (§11) |
| `FSP_R` / `FSP_L` | LM-11 / LM-12 | Extrémité **proximale** de l'axe diaphysaire |
| `FSD_R` / `FSD_L` | LM-13 / LM-14 | Extrémité **distale** de l'axe diaphysaire (limitée au FOV) |

**Ligne dérivée (non annotée) :**

```
SHAFT_side = droite(FSP_side, FSD_side)
```

**Landmarks non mentionnés pour l'offset dans §11 :** `TD`, `ASL`, `ASM`, `FNM`. L'axe du col `NECK = FHC→FNM` (§2.3) n'est **pas** cité pour l'offset fémoral.

**Disponibilité actuelle :** les 6 landmarks (3 × 2 côtés) font partie des **14 obligatoires** ; annotés dans `new_26` ; détectables par V2.

### 1.3 Formule actuellement envisagée (extrait strict de la doc)

La documentation ne fournit **pas** de formule numérique close. Elle fixe uniquement les **prérequis géométriques** :

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

**Formule métrique :** **indéterminée dans le projet.** Aucune section §3.x dédiée (contrairement à VCE §3.1, Tönnis §3.2, CCD §3.3).

### 1.4 Ce qui manque pour valider la mesure

| Élément manquant | Détail |
|------------------|--------|
| **Définition clinique de l'offset** | Quelle distance ou projection entre `FHC` et `SHAFT` ? Référence pelvienne requise ou non ? |
| **Convention de signe** | Médial positif / latéral positif ? Bilatéral comparé comment ? |
| **Unité de sortie figée** | mm attendus cliniquement ; pas de valeur en pixels seule |
| **Formule §3.x** | Absence d'une section « mesure par mesure » au même niveau que VCE/Tönnis/CCD |
| **Implémentation** | Pas de `femoral_offset()` dans `mvp_geometry/measurements.py` |
| **Pipeline API / Flutter** | Pas de champ dans `MeasureOut` / `SideMeasurements` |
| **Tests** | Aucun test analytique |
| **Validité FOV (A7)** | Règle de distance minimale FSP–FSD à valider pour offset (axe « long » requis par analyses dataset) |
| **Seuils cliniques** | Non documentés (analogue ambiguïté A4 pour Tönnis) |

### 1.5 Calibration mm/px

**État documenté :** la spec §11 exige explicitement une **calibration mm/px**, sans en décrire la méthode.

| Question | Réponse dans la doc projet |
|----------|---------------------------|
| Calibration requise ? | **Oui** (§11 : « calibration mm/px ») |
| Méthode proposée | **Aucune** (pas de marker, pas de distance inter-teardrop, pas de DICOM pixel spacing) |
| Où implémenter | **Non spécifié** — absent de `mvp_geometry/`, backend, Flutter |
| Relation avec mesures angulaires | VCE/Tönnis/CCD en **degrés** — pas de mm/px pour le MVP actuel |

**Conséquence :** même si les landmarks existent, l'offset fémoral **ne peut pas être validé cliniquement** sans décision sur la méthode mm/px.

### 1.6 Statut

**SPECIFICATION REQUIRED** — landmarks de base présents ; définition métrique, calibration et section §3 dédiée **manquantes**.

---

## 2. Alpha angle

### 2.1 Contexte projet

| Constat | Détail |
|---------|--------|
| Périmètre MVP actuel (`landmark_specification.md` §1) | VCE, Tönnis, CCD uniquement — alpha angle **hors MVP implémenté** |
| Code / API / Flutter | **Non implémenté** |
| Schéma YOLO V2 (14 keypoints) | **Aucun nouveau landmark YOLO défini pour l'instant** (décision explicite) |
| Corpus actuel `new_26` | Radiographies **AP bassin** — voir §2.4 : **≠ vue Dunn** |

Cette section documente la définition anatomique et la méthode classique issues de la **recherche bibliographique** (Nötzli). Elle **ne fige pas** la vue cible, les seuils cliniques ni l'extension du schéma d'annotation.

### 2.2 Définition anatomique (Nötzli)

L'**alpha angle** (angle alpha fémoral) est l'angle formé entre :

1. **L'axe du col fémoral** — droite représentant l'axe longitudinal du col ;
2. **La ligne de couverture latérale** — droite passant par le **centre du cercle de meilleure adaptation** de la tête fémorale et le **point où le contour osseux de la tête quitte le cercle de meilleure adaptation** (point de **perte de sphéricité** / départ du col par rapport à la portion sphérique ajustée).

**Interprétation clinique (littérature) :** mesure de la **couverture latérale** de la tête par le col osseux ; valeur diminuée en cas de déformité cam / impingement fémoral.

**Méthode classique de référence :** **Nötzli et al.** — mesure radiographique sur vues **latérales / Dunn**, pas sur une simple AP bassin standard.

### 2.3 Construction géométrique (méthode de Nötzli)

```
Étape 1 — Cercle de meilleure adaptation (best-fit) :
  Ajuster un cercle sur le contour osseux de la portion sphérique
  conservée de la tête fémorale.
  → Centre du cercle = FHC (conceptuel ; aligné sur LM-03/04 du MVP
    lorsque la méthode de fit est identique).

Étape 2 — Point de perte de sphéricité :
  Identifier sur le contour de la tête le point où le bord osseux
  **quitte** le cercle de meilleure adaptation (transition tête → col).
  → Point P_sphericity_loss (conceptuel — non modélisé en landmark YOLO
    pour l'instant).

Étape 3 — Axe du col fémoral :
  Construire l'axe du col (méthode exacte à figer — voir §2.7).

Étape 4 — Alpha angle :
  α = angle entre l'axe du col et la droite FHC → P_sphericity_loss
  (côté latéral de la couverture, selon convention de la vue retenue).
```

**Prérequis non négociables (littérature) :**

- Un **cercle de meilleure adaptation** de la tête est **obligatoire** ; un centre de tête estimé visuellement sans fit de cercle **ne suffit pas** pour la méthode de Nötzli.
- Le **point de perte de sphéricité** dépend du fit du cercle : deux méthodes de cercle différentes produisent des α différents.

**Unité de sortie :** degrés (pas de calibration mm/px pour l'angle lui-même).

### 2.4 Vues radiographiques — distinctions obligatoires

L'alpha angle **n'est pas une mesure unique** : sa valeur dépend de la **vue** et de la **méthode**. Les vues suivantes **ne sont pas interchangeables** :

| Vue / modalité | Description | Usage alpha angle (littérature) |
|----------------|-------------|----------------------------------|
| **AP bassin** | Radiographie frontale du bassin (corpus actuel `new_26`) | **Non équivalente** à une vue Dunn ; rotation fémorale et projection superposent tête/col → **α non fiable** selon Nötzli |
| **Dunn 45°** | Flexion ~45°, abduction modérée, beam orienté | Vue **courante** pour α en clinique |
| **Dunn 90°** | Flexion ~90° (variante) | Valeurs **≠ Dunn 45°** ; protocole distinct |
| **Cross-table lateral** | Latérale cross-table hanche | Alternative à Dunn ; valeurs **≠ Dunn** |
| **IRM** | Coupes morphologiques (souvent obliques / radial) | Définition et seuils **≠ radiographie** ; repères et plans différents |

**Règle projet (documentation) :**

> **Ne pas considérer l'AP bassin comme équivalente à une vue Dunn** pour le calcul ou l'interprétation de l'alpha angle.

Le pipeline actuel (V2, annotations `new_26`, mesures VCE/Tönnis/CCD) est calibré sur **AP bassin**. L'alpha angle, s'il est un jour intégré, exige une **décision explicite** sur la vue acceptée (§2.7 point 7).

### 2.5 Valeurs et seuils cliniques

| Principe | Application |
|----------|-------------|
| Variabilité inter-vues | Les valeurs normales et pathologiques **varient selon la vue** (Dunn 45° vs 90° vs cross-table vs IRM) |
| Variabilité inter-méthodes | Le fit du cercle, l'axe du col et la définition du point de perte de sphéricité modifient α |
| Seuil projet | **Aucun seuil clinique fixé** dans ce document — ne pas choisir arbitrairement un cut-off (ex. pas de « α < X° = cam » sans validation référent) |
| Comparaison inter-patient | Un α mesuré en AP **ne doit pas** être comparé à une norme publiée en Dunn 45° |

### 2.6 Landmarks et schéma YOLO

**Décision actuelle : aucun nouveau landmark YOLO défini pour l'instant.**

Éléments géométriques **conceptuels** (non tranchés comme keypoints YOLO) :

| Élément | Rôle | Lien schéma MVP 14 kp |
|---------|------|------------------------|
| Centre cercle tête (`FHC`) | Origine de la ligne de couverture | `FHC_R` / `FHC_L` (LM-03/04) — **centre best-fit** déjà défini pour VCE/CCD ; **méthode de fit à figer** pour α |
| Axe du col | Première branche de l'angle | `FNM` (LM-09/10) + `FHC` définissent `NECK` en MVP — **peut différer** de l'axe col retenu par Nötzli |
| Point perte de sphéricité | Extrémité de la ligne FHC → P | **Absent** du schéma 14 kp ; **non ajouté** au schéma YOLO dans cette révision |
| Contour tête / cercle | Entrée du fit | Non stocké comme landmark ; nécessite **contour ou cercle** (annotation ou segmentation future) |

**Conséquence :** l'alpha angle **n'est pas calculable** avec le pipeline V2 actuel tel quel, même si `FHC` et `FNM` existent — il manque le point de perte de sphéricité et une vue latérale/Dunn adaptée.

### 2.7 Décisions cliniques à valider

Avant toute implémentation (spec §3, code, annotation, entraînement), le référent clinique doit trancher :

| # | Décision | État |
|---|----------|------|
| **1** | **Vue radiographique cible** — Dunn 45°, Dunn 90°, cross-table, IRM, ou autre ? Quelle vue est la référence produit ? | ☐ Non validé |
| **2** | **Méthode de définition de l'axe du col** — `FHC→FNM` (MVP) vs deux milieux de largeur du col vs autre protocole Nötzli ? | ☐ Non validé |
| **3** | **Méthode de fit du cercle de la tête** — algorithme, portion de contour incluse, exclusion ostéophytes / zone non sphérique (cf. ambiguïté A5 MVP) | ☐ Non validé |
| **4** | **Définition exacte du point de perte de sphéricité** — premier point de départ du contour par rapport au cercle ; côté latéral vs médial ; règle si contour ambigu | ☐ Non validé |
| **5** | **Seuil clinique** — valeur(s) normale(s) et pathologique(s) **pour la vue et la méthode retenues** ; pas de seuil par défaut dans l'application | ☐ Non validé |
| **6** | **Bilateralité** — α calculé et affiché pour R et L séparément ? comparaison bilatérale requise ? conduite si un côté non mesurable ? | ☐ Non validé |
| **7** | **Périmètre acquisition application** — accepter **uniquement** vues Dunn/latérales (rejet AP) **ou** autoriser AP avec **avertissement explicite** de non-conformité Nötzli ? | ☐ Non validé |

### 2.8 Relation avec les mesures MVP existantes

| Mesure | Distinction vs alpha angle |
|--------|---------------------------|
| **VCE / Wiberg** | Angle de couverture **acétabulaire** (sourcil, référence pelvienne ITH) — pas l'angle tête/col osseux |
| **Tönnis** | Inclinaison du **sourcil** — indépendant de la géométrie tête/col |
| **CCD** | Angle **col–diaphyse** (FHC→FNM vs FSP→FSD) — autre plan et autre paire de droites |

L'alpha angle est une mesure **distincte** ; il ne remplace ni ne déduit des mesures MVP actuelles.

### 2.9 Statut

**SPECIFICATION REQUIRED** — définition anatomique et méthode Nötzli **documentées** ; vue cible, fit cercle, point de sphéricité, seuils et politique AP vs Dunn **non figés** ; **aucun nouveau landmark YOLO** ; **pas d'implémentation** tant que §2.7 non validé.

---

## 3. Bi-ischial / ligne bi-ischiatique

### 3.1 Définition actuellement proposée

**Source principale :** `docs/landmark_specification.md` §11 :

> ligne bi-ischiatique (il faudrait `IT_R` / `IT_L`)

**Contexte et contraintes documentées :**

| Élément | Source | Contenu |
|---------|--------|---------|
| Substitut interdit | Ambiguïté **A2** (§4 LM-01, §8) | Horizontal pelvien MVP = **teardrops** `TD_*` ; ischions = « landmark optionnel **futur**, pas remplacement silencieux » |
| Exclusion MVP actuel | `annotation_guidelines.md` §1.4 | « Tubérosités ischiatiques (sauf futur schéma hors MVP) » |
| Placement teardrop | `annotation_guidelines.md` §2.1 | Ne pas annoter les tubérosités ischiatiques à la place du teardrop |
| Extension catalogue | §11 | Landmarks futurs en **LM-17+** sans casser LM-01–16 |
| Dataset2 | `dataset_analysis.md` §14 | Masques `ischium` existent mais **ne fournissent pas** les points bi-ischiatiques annotés |
| Modèle V2 | `keypoint_order.md` | **14 keypoints** — pas de slot `IT_*` |

**Non documenté dans le projet :** la métrique de sortie exacte (angle de la ligne vs horizontal ? distance inter-tubérosités en mm ? inclinaison pelvienne ?).

### 3.2 Landmarks `IT_R` et `IT_L`

#### `IT_R` (proposé LM-17)

| Champ | Valeur documentée / dérivée |
|-------|----------------------------|
| **Nom** | `IT_R` |
| **Côté** | Droit patient (gauche de l'image en AP) |
| **Structure** | **Tubérosité ischiatique** droite |
| **Rôle** | Extrémité droite de la **ligne bi-ischiatique** |
| **Mesures** | Ligne bi-ischiatique (§11) |
| **Statut schéma actuel** | **Absent** — hors MVP 14 landmarks |
| **Annotation actuelle** | **Interdite** en MVP (`annotation_guidelines.md` §1.4) |

#### `IT_L` (proposé LM-18)

| Champ | Valeur documentée / dérivée |
|-------|----------------------------|
| **Nom** | `IT_L` |
| **Côté** | Gauche patient (droite de l'image en AP) |
| **Structure** | **Tubérosité ischiatique** gauche |
| **Rôle** | Extrémité gauche de la **ligne bi-ischiatique** |
| **Mesures** | Ligne bi-ischiatique (§11) |
| **Statut schéma actuel** | **Absent** |
| **Annotation actuelle** | **Interdite** en MVP |

#### Ligne dérivée (non annotée, logique spec)

```
BI_ISCHIAL = droite(IT_R, IT_L)
```

**Usage exact de `BI_ISCHIAL` :** non détaillé dans §3 — à figer cliniquement (référence d'inclinaison pelvienne, distance, autre).

### 3.3 Nécessité des deux nouveaux landmarks

| Question | Réponse (doc projet) |
|----------|---------------------|
| Les 14 landmarks suffisent-ils ? | **Non** — §11 exige explicitement `IT_R` / `IT_L` |
| `TD_R` / `TD_L` peuvent-ils remplacer ? | **Non** — A2 interdit le remplacement silencieux |
| Segmentation ischium suffit-elle ? | **Non** — pas de keypoint tubérosité annoté (`dataset_analysis.md`) |
| Combien de nouveaux points ? | **Minimum 2** (paire bilatérale) |

### 3.4 Impact passage 14 → 16 keypoints

**État actuel (documenté, non modifié) :**

| Paramètre | Valeur 14 kp | Impact 16 kp |
|-----------|--------------|--------------|
| Indices YOLO | 0–13 (`keypoint_order.md`) | +14 `IT_R`, +15 `IT_L` (ordre exact à trancher à l'implémentation) |
| Colonnes label `.txt` | 47 (5 + 14×3) | 53 (5 + 16×3) |
| `flip_idx` | `[1,0,3,2,5,4,7,6,9,8,11,10,13,12]` | Étendre : indices 14↔15 permutés |
| `data.yaml` YOLO | `kpt_shape: [14, 3]` | `[16, 3]` |
| Modèle V2 | Entraîné 14 kp | **Incompatible** sans retraining |
| Annotations `new_26` | 14 landmarks / image | **Ré-annotation** `IT_R`, `IT_L` requise |
| Guide annotation | 14 obligatoires | Nouvelles fiches §2.x pour `IT_*` |
| Backend / Flutter | 14 `LandmarkName` enum | Extension schémas (hors scope actuel) |
| Split train/val | 21/5 | Peut rester ; contenu labels enrichi |

**Conséquence :** l'extension bi-ischiale est un **changement de schéma** (LM-17+), pas une simple formule sur landmarks existants. Entraînement futur requis **après** spec + annotation — **repartir de V2**, pas V3.

### 3.5 Formule et calibration

| Élément | État |
|---------|------|
| Formule (angle, distance, les deux) | **Non définie** |
| Calibration mm/px | **Non définie** — probable si distance inter-tubérosités ; à confirmer cliniquement |
| Dépendance `ITH` (teardrops) | **Non documentée** pour bi-ischial |

### 3.6 Statut

**NEW LANDMARKS REQUIRED** — `IT_R` et `IT_L` obligatoires ; définition métrique de sortie encore **SPECIFICATION REQUIRED** au sens clinique.

---

## 4. Mesures implémentées (référence)

Pour comparaison — **ne pas modifier** :

| Mesure | Statut | Module |
|--------|--------|--------|
| VCE | IMPLEMENTED | `mvp_geometry/measurements.py` → `vce_angle()` |
| Tönnis | IMPLEMENTED | `tonnis_angle()` |
| CCD | IMPLEMENTED | `ccd_angle()` |

---

## 5. Décisions cliniques à valider avant le prochain entraînement

Aucun entraînement ne doit être lancé tant que les décisions suivantes ne sont pas tranchées et reflétées dans une mise à jour de `docs/landmark_specification.md` (hors scope de ce document).

### 5.1 Alpha angle — définition documentée, décisions §2.7 en attente

- [ ] **A1.** Vue radiographique cible (Dunn 45°, Dunn 90°, cross-table, IRM) — §2.7.1
- [ ] **A2.** Méthode de définition de l'axe du col — §2.7.2
- [ ] **A3.** Méthode de fit du cercle de la tête — §2.7.3
- [ ] **A4.** Définition exacte du point de perte de sphéricité — §2.7.4
- [ ] **A5.** Seuil clinique pour la vue/méthode retenues (**aucun seuil par défaut**) — §2.7.5
- [ ] **A6.** Bilatéralité (R/L, comparaison, côté manquant) — §2.7.6
- [ ] **A7.** Périmètre application : Dunn/latérales seules vs AP avec avertissement — §2.7.7

**Rappel :** AP bassin ≠ vue Dunn ; **aucun nouveau landmark YOLO** tant que A1–A7 non validés.

### 5.2 Femoral offset — landmarks OK, spec incomplète

- [ ] **F1.** Définir la métrique exacte entre `FHC` et `SHAFT` (type de distance / projection).
- [ ] **F2.** Figer convention de signe et unité de sortie (mm).
- [ ] **F3.** Choisir et documenter la **méthode de calibration mm/px** (marker, DICOM, distance anatomique de référence, autre).
- [ ] **F4.** Valider règle **A7** pour FOV court : séparation minimale FSP–FSD acceptable pour offset ; conduite si non respectée (`v=0`, mesure indisponible).
- [ ] **F5.** Confirmer que l'axe `FSP→FSD` sur AP bassin seul est suffisant ou exiger shaft plus long (landmarks additionnels ?).
- [ ] **F6.** Fournir seuils cliniques (normal / pathologique).
- [ ] **F7.** Rédiger §3.x dans `landmark_specification.md` au format VCE/Tönnis/CCD.

### 5.3 Bi-ischial — nouveaux landmarks + spec métrique

- [ ] **B1.** Figer position exacte sur la tubérosité ischiatique (sommet inférieur, centre, bord — avec illustrations).
- [ ] **B2.** Définir la **sortie** : angle vs horizontal ? distance IT_R–IT_L en mm ? inclinaison pelvienne ? combinaison ?
- [ ] **B3.** Si distance en mm : choisir méthode **calibration mm/px** (même décision que F3 ou distincte).
- [ ] **B4.** Rédiger fiches annotation `IT_R` / `IT_L` dans `annotation_guidelines.md`.
- [ ] **B5.** Confirmer ordre keypoints 16 (indices 14–15) et compatibilité avec extension LM-17+.
- [ ] **B6.** Planifier ré-annotation des 26 cas `new_26` (+ futurs cas) avant tout retraining.
- [ ] **B7.** Valider visibilité des tubérosités sur le corpus AP bassin (taux `v=0` attendu).

### 5.4 Entraînement — conditions globales

- [ ] **T1.** **Ne pas entraîner** pour l'alpha angle tant que A1–A7 (§2.7) sont ouverts ; bi-ischial : B1–B7 ouverts.
- [ ] **T2.** Femoral offset seul **ne nécessite pas** de retraining (14 landmarks suffisants selon §11) — implémentation software après F1–F7.
- [ ] **T3.** Extension bi-ischiale ⇒ **16 keypoints** ⇒ retraining obligatoire ; init depuis **V2 best**, V3 NO-GO.
- [ ] **T4.** Alpha angle : **aucun retraining** tant que vue cible et landmarks (post-validation A1–A7) non figés ; schéma YOLO **14 kp inchangé** pour l'instant.

---

## 6. Synthèse des statuts

```
IMPLEMENTED              → VCE, Tönnis, CCD (14 landmarks, V2 production)
SPECIFICATION REQUIRED   → Femoral offset (landmarks OK, formule + mm/px manquants)
SPECIFICATION REQUIRED   → Alpha angle (Nötzli documenté §2 ; vue/seuils/landmarks YOLO non figés)
NEW LANDMARKS REQUIRED   → Bi-ischial (IT_R, IT_L) + spec métrique à figer
```

---

*Document de préparation de spécification — aucun fichier du projet modifié sauf ce rapport et son CSV.*
