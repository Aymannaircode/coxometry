# Comparaison d'architectures — détection de landmarks coxométriques

**Date :** 17 juillet 2026  
**Périmètre :** étude technique **documentaire** pour un futur détecteur de landmarks sur radiographies **AP bassin adulte**  
**Mesures cibles MVP :** VCE / Wiberg · Tönnis · CCD  
**Pipeline logiciel existant :**

```
Image → Preprocessing → LandmarkDetector → Reprojection → mvp_geometry → VCE / Tönnis / CCD
```

**Contraintes respectées :** aucun entraînement, aucun téléchargement de poids, aucune modification de dataset / annotation, aucune coordonnée anatomique créée, aucun code de modèle implémenté, `mvp_geometry` inchangé.

**Documents liés :**

- `docs/landmark_specification.md` — 14 landmarks obligatoires ;
- `docs/retuve_feasibility_test.md` — expérience YOLO Pose (Retuve, domaine proche) ;
- `backend/app/services/detection/` — interface `LandmarkDetector.detect(PreprocessedImage)`.

---

## 1. Problème à résoudre

### 1.1 Tâche

Prédire **14 points 2D nommés** (`TD_R/L`, `FHC_*`, `ASL_*`, `ASM_*`, `FNM_*`, `FSP_*`, `FSD_*`) sur une radiographie AP du bassin, dans l’espace de l’image prétraitée, puis les reprojeter vers l’image originale avant `mvp_geometry`.

### 1.2 Particularités médicales

| Facteur | Impact sur la détection |
|---------|-------------------------|
| Contraste faible / surexposition | Points de teardrop et bord acétabulaire difficiles |
| Inclinaison / rotation pelvienne | Déplace les relations spatiales entre landmarks |
| Occlusion / superpositions | Sourcil (ASL/ASM) et col (FNM) ambigus |
| Variabilité anatomique adulte | Dysplasie, coxarthrose, prothèses (hors MVP initial) |
| Erreur de landmark → erreur d’angle | VCE/Tönnis sensibles à quelques pixels sur FHC/ASL/ASM |

### 1.3 Critères de comparaison

Pour chaque architecture : type de données, nombre de landmarks, volume minimal annoté, précision attendue, robustesse, temps d’entraînement, vitesse d’inférence, intégration dans `LandmarkDetector`, avantages / limites pour la coxométrie.

Les ordres de grandeur ci-dessous sont **indicatifs** (littérature keypoints médicaux + pratique radiographie) ; ils ne remplacent pas une validation empirique sur le futur dataset adulte.

---

## 2. Approche A — YOLO Pose (détection + keypoints)

### 2.1 Principe

Un détecteur objet (YOLO) localise une ou plusieurs boîtes (`hip_pelvis`, `hip_femur`, …) et régresse simultanément un **vecteur de keypoints** par instance (souvent via branches pose Ultralytics / YOLO Pose).

Référence projet : test Retuve (`docs/retuve_feasibility_test.md`) — YOLO X-ray pose **pré-entraîné** hors schéma MVP (classes et keypoints non alignés sur les 14 landmarks adultes).

### 2.2 Analyse

| Critère | Évaluation |
|---------|------------|
| **Type de données** | Images + annotations style pose : bbox(es) + keypoints `(x, y, v)` par instance. Formats usuels : YOLO-Pose / COCO keypoints. |
| **Nombre de landmarks** | Configurable (typiquement ≤ 17–20 en pose humaine ; **14 points MVP** sont supportables). Mapping index → nom MVP à définir (`YoloPoseLandmarkDetector`). |
| **Volume minimal annoté** | Transfert depuis poids radio génériques : **~80–150** radios bien annotées pour un premier prototype ; **≥ 200–400** pour une stabilité clinique MVP. Sans pré-entraînement adapté : plutôt **≥ 500**. |
| **Précision attendue** | Bonne sur structures « objet » (tête fémorale / bassin) ; **moins fine** sur bords subtils (ASL/ASM, teardrop) si la résolution d’entrée est basse. Erreur médiane typique (littérature orthopédique YOLO/keypoints) : ordre **2–6 px** à 512–800 px, très dépendante de l’annotation. |
| **Robustesse** | Forte aux variations d’échelle / cadrage grâce à la détection d’objet. Sensible aux faux positifs de bbox et au **nombre fixe de keypoints** (points absents mal gérés si pas de canal `v`). |
| **Temps d’entraînement** | Court à moyen : **quelques heures** (GPU grand public) pour fine-tuning ; jours si entraînement from scratch. |
| **Vitesse d’inférence** | **Excellente** : temps réel ou quasi (CPU acceptable pour MVP, GPU idéal). Compatible usage Flutter → API. |
| **Intégration `LandmarkDetector`** | **Très bonne.** Stub `YoloPoseLandmarkDetector` déjà prévu. Entrée = `PreprocessedImage.array` ; sortie = `DetectedLandmark[]` + confidences. |

### 2.3 Avantages / limites (coxométrie)

**Avantages**

- Écosystème mature (Ultralytics), déploiement simple ;
- Gestion native multi-instance (deux hanches) via bboxes ;
- Latence faible pour un MVP applicatif ;
- Aligné avec l’adaptateur déjà sketché dans le backend.

**Limites**

- Précision sub-pixel limitée vs heatmaps haute résolution ;
- Schéma keypoints figé : landmarks optionnels (`ALB_*`) ou points manquants (`v=0`) à gérer soigneusement ;
- Les poids Retuve **ne couvrent pas** le schéma MVP adulte → ré-annotation / ré-entraînement indispensables ;
- Erreurs de bbox → décalage global des keypoints d’une hanche.

---

## 3. Approche B — Heatmaps / régression de keypoints

### 3.1 Principe

Un backbone (HRNet, U-Net, Stacked Hourglass, SimpleBaseline ResNet) produit une **heatmap** par landmark (ou une régression directe `(x, y)`). La position = argmax / soft-argmax de la heatmap. Variantes : régression coordonnée pure (MLP / fully-connected) sans heatmap.

### 3.2 Analyse

| Critère | Évaluation |
|---------|------------|
| **Type de données** | Images + 14 points `(x, y, v)` ; heatmaps générées à l’entraînement (gaussiennes). Pas de bbox obligatoire (mais ROI bassin utile). |
| **Nombre de landmarks** | Naturellement **multi-canal** : 14 heatmaps = 14 landmarks MVP ; extensible à `ALB_*`. |
| **Volume minimal annoté** | Avec pré-entraînement ImageNet / médical : **~100–200** images pour un premier modèle utilisable ; **≥ 300–500** pour viser une précision angulaire stable. From scratch : nettement plus. |
| **Précision attendue** | **Meilleure localisation** sur bords fins (ASL/ASM, TD) grâce à la résolution spatiale des heatmaps. Soft-argmax → précision sub-pixel. Cible réaliste MVP bien annoté : **~1–3 px** médiane à ~512–1024 px. |
| **Robustesse** | Bonne à la qualité d’image si normalisation / CLAHE optionnelle (hors scope actuel du preprocessing). Moins robuste au **cadrage extrême** sans étape de localisation préalable. Ambiguïté gauche/droite à lever (symétrie bassin). |
| **Temps d’entraînement** | Moyen à long : **plusieurs heures à 1–2 jours** GPU selon backbone et résolution. |
| **Vitesse d’inférence** | **Bonne** (HRNet-W32) à moyenne (Hourglass profond) ; plus lente que YOLO nano/small, encore acceptable pour API asynchrone. |
| **Intégration `LandmarkDetector`** | **Bonne.** Nouvelle classe `HeatmapLandmarkDetector(LandmarkDetector)` : `detect()` → soft-argmax → `DetectedLandmark`. Compatible avec `PreprocessedImage` et la reprojection existante. |

### 3.3 Avantages / limites (coxométrie)

**Avantages**

- Précision géométrique alignée avec le besoin VCE/Tönnis/CCD ;
- Canal de confiance / heatmap peak → proxy de fiabilité (`v` / `confidence`) ;
- Gestion propre des landmarks manquants (heatmap plate → `v=0`) ;
- Standard académique en keypoints médicaux.

**Limites**

- Pipeline d’entraînement un peu plus lourd (génération heatmaps, choix σ) ;
- Sans détecteur ROI, risque de confusion gauche/droite ou de points hors bassin ;
- Latence et mémoire plus élevées que YOLO léger ;
- Moins « clé en main » qu’Ultralytics pour un MVP accéléré.

---

## 4. Approche C — Alternative : détection ROI + keypoints haute précision (deux étages)

### 4.1 Principe

1. **Étage 1** — détecteur léger (YOLO / RetinaNet) localise le bassin et/ou chaque hanche.  
2. **Étage 2** — modèle heatmap (HRNet / U-Net) sur le crop redimensionné prédit les landmarks.

Variante proche : **RTMPose / ViTPose** en single-stage haute précision ; l’idée « deux étages » reste la plus pertinente pour un petit dataset médical.

### 4.2 Analyse

| Critère | Évaluation |
|---------|------------|
| **Type de données** | Images + bboxes (bassin / hanche) + 14 keypoints. Annotation un peu plus coûteuse (bbox + points). |
| **Nombre de landmarks** | 14 (voire par hanche 7 si split R/L) — flexible. |
| **Volume minimal annoté** | **~80–150** pour un premier pipeline bout-en-bout (transfert) ; **≥ 250** recommandé avant gel MVP. |
| **Précision attendue** | **Meilleure combinaison** précision locale + cadrage : souvent le top des approches radiographiques. |
| **Robustesse** | Excellente face aux variations de champ et de zoom ; dépend de la qualité de l’étage détection. |
| **Temps d’entraînement** | Plus long (deux modèles) : **1–3 jours** GPU pour itérations complètes. |
| **Vitesse d’inférence** | Moyenne : 2 passes ; encore viable en API (centaines de ms CPU, bien moins GPU). |
| **Intégration `LandmarkDetector`** | **Bonne** via un détecteur composite : `TwoStageLandmarkDetector.detect(PreprocessedImage)` enchaîne ROI → heatmaps → coordonnées canvas prétraité. La reprojection actuelle reste valide si tout est exprimé dans l’espace prétraité (ou si un offset de crop est appliqué **avant** la reprojection letterbox). |

### 4.3 Avantages / limites (coxométrie)

**Avantages**

- Meilleur compromis précision / robustesse pour la coxométrie ;
- Permet d’annoter d’abord le bassin (QC) puis les points ;
- Facilite le traitement séparé R/L en cas d’asymétrie.

**Limites**

- Complexité d’ingénierie et de validation doublée ;
- Propagation d’erreurs étage 1 → étage 2 ;
- Surdimensionné si le volume annoté reste très faible (&lt; 100).

---

## 5. Tableau synthétique

| Critère | A — YOLO Pose | B — Heatmaps | C — ROI + heatmaps |
|---------|---------------|--------------|--------------------|
| Données | Bbox + keypoints | Keypoints (+ ROI optionnelle) | Bbox + keypoints |
| 14 landmarks MVP | Oui | Oui | Oui |
| Volume mini (1er train) | ~80–150 (fine-tune) | ~100–200 | ~80–150 |
| Volume confort MVP | ≥ 200–400 | ≥ 300–500 | ≥ 250 |
| Précision locale | Moyenne+ | **Haute** | **Haute** |
| Robustesse cadrage | **Haute** | Moyenne | **Haute** |
| Entraînement | Rapide | Moyen | Plus long |
| Inférence | **Très rapide** | Rapide | Moyenne |
| Fit `LandmarkDetector` | Excellent (stub existant) | Excellent | Bon (composite) |
| Risque MVP | Précision sourcil/TD | Cadrage / L-R | Complexité |

---

## 6. Compatibilité avec l’interface actuelle

L’interface backend impose :

```text
LandmarkDetector.detect(PreprocessedImage) → LandmarkDetectionResult
    landmarks: DetectedLandmark(name, x, y, confidence?)  # espace prétraité
```

Puis :

```text
reproject_landmarks(...) → coordonnées image originale → mvp_geometry
```

| Architecture | Compatible ? | Comment |
|--------------|--------------|---------|
| YOLO Pose | **Oui** | Implémenter le corps de `YoloPoseLandmarkDetector.detect` ; mapper indices → `MVP_LANDMARK_NAMES`. |
| Heatmaps | **Oui** | Nouvelle sous-classe `HeatmapLandmarkDetector` ; soft-argmax → `DetectedLandmark`. |
| ROI + heatmaps | **Oui** | Composite implémentant `LandmarkDetector` ; convertir coords crop → espace prétraité **avant** la reprojection letterbox. |

Aucune des trois approches n’exige de changer `mvp_geometry` ni la reprojection letterbox (`scale`, `pad_left`, `pad_top`).

---

## 7. Recommandation MVP

### 7.1 Modèle recommandé

**Phase 1 (premier entraînement / preuve de faisabilité) : YOLO Pose fine-tuné** sur le schéma des **14 landmarks MVP**, branché sur `YoloPoseLandmarkDetector`.

**Phase 2 (si l’erreur angulaire VCE/Tönnis est insuffisante) : bascule ou hybridation vers heatmaps (approche B) ou ROI + heatmaps (approche C)** sans changer le contrat `LandmarkDetector`.

### 7.2 Justification

1. **Vitesse de livraison** — l’adaptateur YOLO Pose est déjà prévu ; Ultralytics réduit le coût d’ingénierie.  
2. **Contrainte données** — l’annotation adulte est en pause ; YOLO Pose tire mieux parti d’un **petit** jeu fine-tuné qu’un HRNet from scratch.  
3. **Déploiement** — latence faible pour une future app Flutter via l’API FastAPI.  
4. **Expérience projet** — Retuve a déjà validé la *mécanique* YOLO Pose sur radio (même si le schéma de keypoints n’est **pas** celui du MVP).  
5. **Porte de sortie** — si la précision sur ASL/ASM/TD est le goulot, l’interface `LandmarkDetector` permet de remplacer l’implémentation par des heatmaps **sans** refactoriser preprocessing, reprojection ni géométrie.

En résumé : YOLO Pose pour **apprendre vite et brancher le pipeline** ; heatmaps (éventuellement deux étages) pour **verrouiller la précision coxométrique** si le budget d’annotation le permet.

### 7.3 Quantité minimale de données avant un premier entraînement

| Objectif | Volume recommandé | Qualité |
|----------|-------------------|---------|
| Smoke-test entraînement (overfit contrôlé, pipeline bout-en-bout) | **30–50** radios AP adulte | Double annotation partielle OK |
| Premier modèle évaluable (métriques landmarks) | **≥ 100** (idéalement **120–150**) | Protocole pilote, `v` renseigné |
| Cible avant gel MVP applicatif | **≥ 250** (dont ~20 % hold-out) | Revue inter-annotateur sur sous-échantillon |

**Plancher absolu avant tout fine-tuning « sérieux » : 100 images** annotées selon `docs/landmark_specification.md` / protocole pilote, avec split **train / val / test** figé (ex. 70 / 15 / 15) et **aucune fuite** patient entre splits.

Les datasets pédiatriques existants (Dataset1/2) **ne remplacent pas** l’annotation adulte MVP (schéma et anatomie différents) ; au mieux transfert de poids / pré-entraînement à évaluer plus tard, hors scope de ce rapport.

### 7.4 Stratégie de validation

1. **Métriques landmarks (espace image originale)**  
   - Erreur euclidienne par landmark (px et % de la largeur bassin / diamètre tête) ;  
   - PCK @ 2 %, 5 %, 10 % d’une longueur de référence (ex. distance `TD_R`–`TD_L`) ;  
   - Taux de détection (`confidence` / heatmap peak) vs `v` annoté.

2. **Métriques cliniques dérivées (via `mvp_geometry`, formules inchangées)**  
   - ΔVCE, ΔTönnis, ΔCCD (degrés) vs annotation humaine ;  
   - Seuils d’acceptabilité à valider avec le référent médical (ex. cibles indicatives à discuter : ΔVCE/Tönnis ≤ 3–5°, ΔCCD ≤ 5°) — **non figés ici**.

3. **Protocoles**  
   - Hold-out patient-wise ;  
   - Sous-ensemble doublement annoté → plafond d’accord humain (borne supérieure du modèle) ;  
   - Stress-tests : inclinaison pelvienne, faible contraste, crop serré (sans inventer de landmarks : uniquement sur cas réellement annotés) ;  
   - Ablation : YOLO Pose seul vs heatmap si Phase 2.

4. **Critère de go / no-go MVP**  
   - Pipeline `PreprocessedImage` → détecteur → reprojection → `mvp_geometry` exécutable en CI sur images de test **synthétiques ou hold-out** ;  
   - Aucune régression des tests backend existants (53+) ;  
   - Rapport d’erreurs angulaires sur le hold-out avant exposition Flutter.

---

## 8. Ce que ce document ne fait pas

- N’entraîne aucun modèle ;  
- Ne télécharge aucun poids ;  
- Ne modifie aucun dataset ni annotation ;  
- N’implémente aucun code de modèle ;  
- Ne choisit pas de seuils cliniques définitifs (responsabilité médicale).

---

## 9. Synthèse exécutive

| Décision | Choix |
|----------|--------|
| Architecture MVP Phase 1 | **YOLO Pose** fine-tuné (14 landmarks) |
| Fallback précision | Heatmaps (± ROI) derrière la même interface |
| Volume mini 1er train utile | **≥ 100** radios AP adulte annotées |
| Volume confort | **≥ 250** avant gel produit |
| Interface logicielle | Déjà compatible : `LandmarkDetector.detect(PreprocessedImage)` |
| Prochaine étape concrète (hors scope) | Reprendre l’annotation adulte selon le protocole pilote, puis brancher l’inférence dans `YoloPoseLandmarkDetector` |
