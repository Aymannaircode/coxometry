# Audit read-only — mesures manquantes (Alpha angle, Femoral offset, Bi-ischial)

**Généré :** 2026-08-28  
**Mode :** lecture seule — aucune modification du projet  
**État conservé :** V2 production · V3 NO-GO · 14 keypoints · pas de training

---

## Sources inspectées

| Zone | Fichiers / modules |
|------|-------------------|
| Spécification landmarks | `docs/landmark_specification.md` |
| Guide annotation | `docs/annotation_guidelines.md` |
| Protocole pilote | `docs/annotation_pilot_protocol.md` |
| Analyses datasets | `docs/dataset1_analysis.md`, `docs/dataset_analysis.md` |
| Géométrie MVP | `mvp_geometry/measurements.py`, `mvp_geometry/hip_measures.py`, `mvp_geometry/landmarks.py` |
| Backend | `backend/app/services/geometry.py`, `backend/app/schemas/measurements.py`, `backend/app/schemas/landmarks.py` |
| Flutter | `mobile/lib/models/measurement.dart`, `mobile/lib/models/analysis_result.dart` |
| Tests | `mvp_geometry/tests/test_measurements.py`, `backend/tests/test_geometry_service.py` |
| Keypoints YOLO | `datasets/yolo_pose_new_26/meta/keypoint_order.md` |
| Cahier des charges | **Aucun fichier standalone** ; exigences distribuées dans les docs ci-dessus (références à « cahier des charges coxométrie adulte » dans `docs/dataset_analysis.md` §Recommandation) |

### Mesures actuellement implémentées (référence)

| Mesure | Fonction | Fichier |
|--------|----------|---------|
| VCE / Wiberg | `vce_angle()` | `mvp_geometry/measurements.py` L89–110 |
| Tönnis | `tonnis_angle()` | `mvp_geometry/measurements.py` L112–135 |
| CCD | `ccd_angle()` | `mvp_geometry/measurements.py` L138–155 |
| Orchestration | `compute_side()` / `compute_all_sides()` | `mvp_geometry/hip_measures.py` |
| API | `compute_measurements()` | `backend/app/services/geometry.py` |

Les 14 landmarks obligatoires (LM-01 à LM-14) : `TD_R/L`, `FHC_R/L`, `ASL_R/L`, `ASM_R/L`, `FNM_R/L`, `FSP_R/L`, `FSD_R/L`.

---

## Tableau de synthèse

| Mesure | Définition utilisée dans le projet | Landmarks requis | Disponibles actuellement | Calculable maintenant ? | Nouveaux landmarks nécessaires ? |
|--------|-------------------------------------|------------------|--------------------------|-------------------------|----------------------------------|
| **Alpha angle** | **Non définie** — absente de la spec MVP, du code et des tests | **Non spécifiés** | N/A | **Non** | **Indéterminé** — impossible à trancher sans définition clinique projet |
| **Femoral offset** | Mention hors MVP §11 : « axe diaphysaire + `FHC`, calibration mm/px et définition d'offset **à figer** » | `FHC_*`, `FSP_*`, `FSD_*` (axe `SHAFT`) | **Partiellement** — landmarks présents, formule et calibration absents | **Non** (mesure projet non validée) | **Non** pour les landmarks de base ; **oui** pour pipeline mm/px et définition clinique |
| **Bi-ischial / ligne bi-ischiatique** | Mention hors MVP §11 : « il faudrait `IT_R` / `IT_L` » ; teardrops **non substituables** (A2) | `IT_R`, `IT_L` (tubérosités ischiatiques) | **Non** — explicitement exclus du MVP (`annotation_guidelines.md` §1.4) | **Non** | **Oui** — `IT_R` et `IT_L` (LM-17+ selon spec §11) |

---

## 1. Alpha angle

### Définition dans le projet

**Aucune.** Recherche exhaustive dans `docs/`, `mvp_geometry/`, `backend/`, `mobile/lib/`, `datasets/`, `annotation_pilot/` :

- Aucune occurrence de « alpha angle », « angle alpha » ou « femoral alpha » dans la documentation ou le code applicatif du projet.
- `docs/landmark_specification.md` §1 et §3 ne listent que **VCE, Tönnis, CCD** comme mesures cibles MVP.
- §11 « Hors MVP » ne mentionne **pas** l'alpha angle (contrairement à bi-ischial et offset fémoral).
- Le backend et Flutter n'exposent que VCE / Tönnis / CCD (`backend/app/schemas/measurements.py`, `mobile/lib/models/measurement.dart`).

**Note externe (hors projet) :** la bibliothèque `retuve` (dans `.venv`, non intégrée) définit un enum `ALPHA` pour l'échographie pédiatrique DDH — **non applicable** à la radiographie AP adulte du MVP et **non référencée** par le projet.

### Points / landmarks nécessaires

**Non spécifiés.** Sans définition clinique projet, on ne peut pas identifier quels landmarks seraient requis. **Aucun landmark inventé** dans cet audit.

Hypothèses courantes en coxométrie (à **valider avec le référent clinique**, pas déduites du projet) :

| Hypothèse externe | Landmarks potentiels | Présents dans les 14 ? |
|-------------------|---------------------|------------------------|
| Alpha angle échographique (Graf) | Ligne basale + ligne col — **échographie, pas RX AP** | N/A |
| Angle de couverture tête/col (RX) | Souvent lié à `FHC`, col, sourcil — chevauche partiellement VCE/CCD | Partiel (`FHC`, `ASL`, `FNM`) — **pas une mesure distincte dans le projet** |

### Fonction de calcul existante

**Aucune.** Pas de `alpha_angle()` dans `mvp_geometry/measurements.py`. Pas de test associé.

### Les 14 landmarks permettent-ils le calcul ?

**Non applicable / Non** — la mesure n'est pas définie dans le périmètre projet. Impossible de conclure « calculable » ou « non calculable » sans d'abord figer **quelle** alpha angle est visée et sa géométrie.

### Verdict Alpha angle

| Critère | Résultat |
|---------|----------|
| Dans le périmètre MVP documenté | **Non** |
| Définition figée | **Non** |
| Code existant | **Non** |
| Calculable avec 14 landmarks | **Non** (définition absente) |
| Action immédiate possible | **Spécification clinique préalable obligatoire** |

---

## 2. Femoral offset

### Définition exacte dans le projet

**Partielle, hors MVP**, `docs/landmark_specification.md` §11 :

> offset fémoral (axe diaphysaire + `FHC`, mais calibration mm/px et définition d'offset **à figer**)

**Éléments documentés :**

- Ingrédients géométriques : centre de tête (`FHC`) + axe diaphysaire (`SHAFT` = `FSP` → `FSD`, §2.3).
- Unité clinique attendue : millimètres (implicite via « calibration mm/px »).
- **Non documenté :** type d'offset (distance perpendiculaire au shaft ? horizontale ? médiale vs latérale ?), ligne de référence pelvienne ou non, convention de signe, seuils normaux.

`docs/dataset1_analysis.md` §14 et `docs/dataset_analysis.md` §14 confirment : « Requiert centre de tête + axe diaphysaire long » — **non couvert** par les schémas DDH pédiatriques.

### Landmarks requis (d'après la spec)

| Landmark | ID | Rôle | Dans les 14 ? | Annoté new_26 / V2 ? |
|----------|-----|------|:-------------:|:--------------------:|
| `FHC_R` / `FHC_L` | LM-03/04 | Centre tête | Oui | Oui |
| `FSP_R` / `FSP_L` | LM-11/12 | Axe diaphysaire proximal | Oui | Oui |
| `FSD_R` / `FSD_L` | LM-13/14 | Axe diaphysaire distal (FOV) | Oui | Oui |

Ligne dérivée `SHAFT_*` = `FSP_*` → `FSD_*` (§2.3).

**Limitation documentée (A7) :** sur AP bassin, `FSD` peut être trop proximal (FOV court) → axe diaphysaire **instable** pour un offset fémoral « long shaft ». La spec recommande une séparation minimale FSP–FSD ; sinon CCD (et par extension offset) non fiable.

### Fonction de calcul existante

**Aucune** pour l'offset fémoral clinique.

**Homonymie importante :** le mot « offset » dans le code désigne le **refinement ASL_L** (`ASM_L + (dx,dy)`), pas l'offset fémoral :

| Module | Objet |
|--------|-------|
| `mvp_geometry/refinement/calibration.py` | `TRAIN_ASM_OFFSET_CALIBRATION` |
| `mvp_geometry/refinement/asl_l.py` | `refine_asl_l()` |
| `backend/app/services/detection/yolo_pose.py` | application refinement |

Aucune fonction `point_to_line_distance()`, `femoral_offset()` ou calibration mm/px dans `mvp_geometry/`.

### Les 14 landmarks permettent-ils le calcul ?

| Aspect | Verdict |
|--------|---------|
| Landmarks de base | **Oui** — `FHC` + `FSP` + `FSD` suffisent géométriquement pour une distance point–droite en pixels |
| Mesure projet validée | **Non** — définition clinique et calibration mm/px **non figées** |
| Qualité clinique sur AP bassin seul | **Incertaine** — A7 : shaft souvent trop court sur cliché bassin |
| Pipeline backend / Flutter | **Absent** — pas de champ dans `MeasureOut` / `SideMeasurements` |

**Conclusion :** les 14 landmarks couvrent les **ingrédients** mentionnés dans la spec, mais l'offset fémoral **n'est pas calculable maintenant** au sens « mesure projet prête à déployer ».

### Nouveaux landmarks nécessaires ?

**Non** pour la géométrie de base décrite (§11).  
**Oui** pour une mesure clinique complète si le référent exige un shaft plus long (points diaphysaires supplémentaires distaux, hors FOV actuel) — **non spécifié** à ce stade.

---

## 3. Bi-ischial / ligne bi-ischiatique

### Définition exacte dans le projet

**Partielle, hors MVP**, `docs/landmark_specification.md` §11 :

> ligne bi-ischiatique (il faudrait `IT_R` / `IT_L`)

**Précisions documentées :**

- Landmarks futurs proposés : **`IT_R`** (tubérosité ischiatique droite patient), **`IT_L`** (gauche).
- Extension catalogue : LM-17+ sans casser LM-01–16 (§11).
- **Non substituables par les teardrops** — ambiguïté **A2** : le MVP fixe `TD_R`/`TD_L` pour l'horizontal pelvien ; ischions = « landmark optionnel futur, pas remplacement silencieux » (§4 LM-01, §8 A2).
- `docs/annotation_guidelines.md` §1.4 : « Tubérosités ischiatiques (sauf futur schéma hors MVP) » — **interdites** comme landmarks MVP actuels.
- **Non documenté :** la sortie attendue (angle de la ligne vs horizontal ? distance inter-tubérosités ? référence pour inclinaison pelvienne ?).

### Landmarks requis

| Landmark | Rôle | Dans les 14 ? |
|----------|------|:-------------:|
| `IT_R` | Tubérosité ischiatique droite patient | **Non** |
| `IT_L` | Tubérosité ischiatique gauche patient | **Non** |

**Substituts invalides (spec) :**

| Point | Pourquoi insuffisant |
|-------|---------------------|
| `TD_R` / `TD_L` | Teardrops ≠ ischions (A2) |
| Masques `ischium` (Dataset2) | Segmentation sans keypoint tubérosité annoté (`docs/dataset_analysis.md` §14) |
| Ligne ilio-ischiatique | Explicitement exclue du placement teardrop (`annotation_guidelines.md` §2.1) |

Ligne dérivée attendue (inférée, non codée) : `BI_ISCHIAL` = droite `IT_R` → `IT_L`.

### Fonction de calcul existante

**Aucune.** Pas de `bi_ischial_angle()`, `bi_ischial_distance()` ou équivalent dans `mvp_geometry/`, `backend/`, Flutter.

### Les 14 landmarks permettent-ils le calcul ?

**Non.** Confirmation convergente :

- `docs/landmark_specification.md` §11
- `docs/dataset1_analysis.md` §14 : « Impossible avec les 8 points » / schéma adulte requis
- `docs/dataset_analysis.md` §14 : « Aucun landmark sur les tubérosités ischiatiques »
- `docs/retuve_feasibility_test.md` : « Ligne bi-ischiatique — Impossible avec ce modèle »
- Modèle V2 : 14 keypoints (`keypoint_order.md`) — pas de slot `IT_*`

### Nouveaux landmarks exactement nécessaires

| ID proposé (spec §11) | Nom | Côté | Structure anatomique |
|----------------------|-----|------|----------------------|
| LM-17 (futur) | `IT_R` | Droit patient | Tubérosité ischiatique — point le plus caudal / inférieur identifiable |
| LM-18 (futur) | `IT_L` | Gauche patient | Idem |

**Minimum : 2 nouveaux landmarks** (1 paire bilatérale).

À figer en spec avant annotation : définition exacte du point sur la tubérosité (sommet vs centre vs bord inférieur), visibilité sur AP bassin, et métrique de sortie (distance mm, angle vs horizontal, ou les deux).

---

## Matrice landmark × mesure (étendue audit)

| Landmark | VCE | Tönnis | CCD | Alpha* | Femoral offset | Bi-ischial |
|----------|:---:|:------:|:---:|:------:|:--------------:|:----------:|
| `TD_R/L` | Oui | Oui | — | — | — | **Non** (substitut interdit) |
| `FHC_R/L` | Oui | — | Oui | ? | **Oui** | — |
| `ASL/ASM` | Oui | Oui | — | ? | — | — |
| `FNM` | — | — | Oui | ? | — | — |
| `FSP/FSD` | — | — | Oui | ? | **Oui** | — |
| `IT_R/L` | — | — | — | — | — | **Oui (futur)** |

\* Alpha : non défini — colonne indicative uniquement.

---

## Tests existants (couverture)

| Fichier | Mesures testées |
|---------|-----------------|
| `mvp_geometry/tests/test_measurements.py` | VCE, Tönnis, CCD uniquement |
| `backend/tests/test_geometry_service.py` | VCE, Tönnis, CCD via API |
| `mvp_geometry/tests/test_asl_l_refinement.py` | Refinement ASL_L (offset pixel, **pas** offset fémoral) |

**Aucun test** pour alpha angle, femoral offset ou bi-ischial.

---

## Recommandation finale

### A. Mesures calculables immédiatement avec les 14 landmarks

**Uniquement les trois mesures MVP déjà implémentées :**

1. **VCE / Wiberg** — `TD_R`, `TD_L`, `FHC`, `ASL`
2. **Tönnis** — `TD_R`, `TD_L`, `ASM`, `ASL`
3. **CCD** — `FHC`, `FNM`, `FSP`, `FSD`

**Aucune** des trois mesures auditées (Alpha, Femoral offset, Bi-ischial) n'est calculable **maintenant** au sens « spec figée + code + tests + pipeline API/Flutter ».

### B. Mesures nécessitant de nouveaux landmarks

| Mesure | Nouveaux landmarks ? | Détail |
|--------|---------------------|--------|
| **Alpha angle** | **Indéterminé** | Définition absente — impossible de lister des landmarks sans spec clinique |
| **Femoral offset** | **Non** (landmarks de base) | `FHC` + `FSP` + `FSD` déjà présents ; blocage = définition + mm/px, pas absence de points |
| **Bi-ischial** | **Oui** | **`IT_R` + `IT_L`** obligatoires |

### C. Liste exacte des nouveaux landmarks éventuellement nécessaires

| Priorité | Landmarks | Mesure(s) | Statut spec |
|----------|-----------|-----------|-------------|
| **Confirmé** | `IT_R`, `IT_L` (LM-17, LM-18) | Bi-ischial | Mention explicite §11 |
| **Conditionnel** | Aucun landmark additionnel identifié pour offset | Femoral offset | Spec indique suffisance `FHC` + shaft |
| **À définir** | TBD après validation clinique | Alpha angle | **Hors spec actuelle** |

**Optionnels déjà prévus (hors audit) :** `ALB_R`, `ALB_L` (LM-15/16) — variante VCE uniquement, pas bi-ischial.

### D. Impact sur le prochain entraînement

| Scénario | Impact modèle YOLO | Impact dataset |
|----------|-------------------|----------------|
| **Continuer MVP actuel (V2, 14 kp)** | Aucun changement requis pour VCE/Tönnis/CCD | Aucun |
| **Femoral offset seul** | **Pas de retraining** si définition validée sur landmarks existants + implémentation `mvp_geometry` | Annotations existantes réutilisables ; valider qualité FSP/FSD (A7) |
| **Bi-ischial** | **Retraining obligatoire** — passage 14 → **16 keypoints** minimum ; nouveau `flip_idx`, YAML, ordre keypoints | **Ré-annotation** de `IT_R`/`IT_L` sur les 26 cas (+ guide illustré) ; split inchangé possible |
| **Alpha angle** | **Indéterminé** — bloqué par absence de spec ; possiblement 0, 2 ou plus de landmarks | **Indéterminé** |
| **V3** | **Ne pas utiliser** — NO-GO confirmé ; toute évolution repart de **V2** | — |

**Ne pas modifier le modèle** tant que :

1. Alpha angle n'est pas défini cliniquement dans le projet ;
2. Femoral offset n'a pas sa définition et calibration mm/px figées ;
3. Bi-ischial n'a pas sa fiche landmark `IT_*` validée.

### E. Ordre recommandé des prochaines étapes

1. **Revue clinique — Alpha angle**  
   Décider si la mesure entre dans le périmètre RX AP adulte ; rédiger définition, landmarks, formule, unités dans `landmark_specification.md` (sans coder ni entraîner).

2. **Revue clinique — Femoral offset**  
   Figer définition (distance perpendiculaire ? référence ? signe), méthode mm/px (marker, distance inter-teardrop, autre), règle A7 pour FOV court. **Ensuite** implémenter dans `mvp_geometry` (sans toucher V2).

3. **Spécification — Bi-ischial**  
   Rédiger fiches `IT_R`/`IT_L` (position exacte, visibilité, métrique de sortie). Mettre à jour guide d'annotation. **Ensuite** seulement : annotation pilote → extension dataset/YOLO → futur training (pas V3).

4. **Stabiliser la production actuelle**  
   V2 + refinement ASL_L + VCE/Tönnis/CCD — ne pas diluer l'effort tant que les trois mesures manquantes ne sont pas spécifiées.

5. **Training modèle**  
   **Dernier** — uniquement après spec + annotations pour bi-ischial (16 kp) ; repartir de V2 best, pas de V3.

---

## Conclusion

Le projet documente clairement **14 landmarks pour 3 mesures angulaires** (VCE, Tönnis, CCD). Les trois mesures auditées sont **hors MVP implémenté** :

- **Alpha angle** : **absente de la spec** — blocage principal = définition clinique, pas landmarks.
- **Femoral offset** : **ingrédients landmarks présents**, mais **définition et calibration non figées** — non déployable.
- **Bi-ischial** : **impossible avec 14 landmarks** — **`IT_R` et `IT_L` requis** explicitement.

**Aucune modification du modèle V2, du dataset, du backend ou de Flutter n'est recommandée** tant que cet audit n'a pas été suivi des étapes de spécification clinique ci-dessus.

---

*Audit read-only — aucun fichier du projet modifié sauf ce rapport et son CSV.*
