# Audit anatomique landmarks — chaîne Android (post-reprojection)

**Généré :** 2026-08-28T17:30:00+01:00  
**Mode :** lecture seule. Aucun fichier de production, poids, labels, annotations ou calibration modifié.

## Image auditée

| Champ | Valeur |
|-------|--------|
| **Cas** | `B26_01` |
| **Fichier** | `datasets/yolo_pose_new_26/images/train/B26_01.png` |
| **Dimensions** | 2730 × 2665 px |
| **GT** | `annotation_pilot/annotations/new_26/B26_01.json` (v=2) |
| **Modèle** | YOLO Pose V2 (`yolo_pose_new_26_v2-3/weights/best.pt`) |
| **Pipeline API** | `run_analyze_from_bytes` (identique `POST /analyze`) |
| **Espace coordonnées final** | `original_image_pixels` (reprojection active) |

## Hypothèse validée — overlay / reprojection

Le bug d'espace de coordonnées est **corrigé**. Les landmarks exposés par `POST /analyze` sont en pixels image originale (2730 × 2665).

| Vérification | Résultat |
|--------------|----------|
| Écart API final vs YOLO offline refined | **≤ 18,7 px** sur les 14 landmarks (écart letterbox 512 vs inférence pleine résolution) |
| Écart API final vs GT | **50–420 px** sur les landmarks problématiques |
| Conclusion overlay | **L'overlay/reprojection n'est PAS la cause** des erreurs anatomiques visibles |

Les écarts résiduels API ↔ offline (5–22 px) relèvent du prétraitement letterbox en inférence API, pas d'un décalage systématique overlay.

## Synthèse globale (erreur finale vs GT)

| Statut | Seuil | Nombre |
|--------|-------|--------|
| **CORRECT** | ≤ 75 px | **6 / 14** |
| **INCERTAIN** | 76–149 px | **2 / 14** |
| **INCORRECT** | ≥ 150 px | **6 / 14** |

Landmarks **CORRECT** : TD_L, FHC_R, FHC_L, ASM_R, ASM_L, FNM_L  
Landmarks **INCERTAIN** : TD_R, FNM_R  
Landmarks **INCORRECT** : ASL_R, ASL_L, FSP_R, FSP_L, FSD_R, FSD_L

> 14/14 détectés **≠** 14/14 anatomiquement corrects.

## Top 5 landmarks les plus problématiques

| Rang | Landmark | Erreur finale (px) | Statut | Cause principale |
|------|----------|-------------------|--------|------------------|
| 1 | **FSP_R** | 419,4 | INCORRECT | Modèle YOLO — sommet de col confondu avec diaphyse proximale (~419 px trop bas) |
| 2 | **FSD_R** | 305,6 | INCORRECT | Modèle YOLO — point sur cortex diaphysaire distal / bord image |
| 3 | **FSP_L** | 273,8 | INCORRECT | Modèle YOLO — sommet de col trop caudal (~268 px) |
| 4 | **FSD_L** | 244,8 | INCORRECT | Modèle YOLO — jonction col-diaphyse confondue avec diaphyse basse |
| 5 | **ASL_R** | 230,7 | INCORRECT | Modèle YOLO — bord supérieur cotyle mal localisé (trop latéral + trop bas) |

**Note ASL_L :** erreur raw 481 px → refined 153 px (refinement améliore fortement le latéral mais reste INCORRECT car trop bas de ~145 px).

## Origine des erreurs : modèle vs refinement vs overlay

| Composant | Impact sur B26_01 | Preuve |
|-----------|-------------------|--------|
| **Modèle YOLO** | **Cause principale** | Erreurs raw offline ≈ erreurs finales pour 13/14 landmarks ; familles ASL et FSP/FSD systématiquement fausses |
| **Refinement ASL_L** | Améliore ASL_L (481 → 153 px) mais **insuffisant** seul | Δ refinement 442 px sur ASL_L ; les 13 autres landmarks inchangés |
| **Overlay / reprojection** | **Non impliqué** | API final vs offline refined ≤ 19 px ; coordonnées en `original_image_pixels` |

## Groupes anatomiques

| Groupe | Landmarks | CORRECT | INCERTAIN | INCORRECT |
|--------|-----------|---------|-----------|-----------|
| TD (trochanter mineur) | TD_R, TD_L | 1 | 1 | 0 |
| Fémoral proximal (FHC/FNM) | FHC_R/L, FNM_R/L | 3 | 1 | 0 |
| ASM (Tönnis) | ASM_R, ASM_L | 2 | 0 | 0 |
| ASL (VCE) | ASL_R, ASL_L | 0 | 0 | 2 |
| Col / diaphyse (FSP/FSD) | FSP_R/L, FSD_R/L | 0 | 0 | 4 |

**Pattern anatomique :** le modèle est fiable sur tête fémorale, Tönnis (ASM) et trochanter mineur gauche ; il échoue sur **cotyle supérieur (ASL)**, **sommet de col (FSP)** et **extrémité distale du col (FSD)** — repères distaux et acétabulaires.

## Détail des 14 landmarks

| Landmark | GT (x,y) | YOLO raw (x,y) | Refined (x,y) | Final API (x,y) | Erreur (px) | Conf | Statut |
|----------|----------|----------------|---------------|-----------------|-------------|------|--------|
| TD_R | (928.9, 1889.7) | (975.9, 2004.9) | (975.9, 2004.9) | (982.2, 2021.6) | 142.3 | 0.86 | **INCERTAIN** |
| TD_L | (1592.4, 1953.4) | (1588.4, 2009.8) | (1588.4, 2009.8) | (1599.8, 2024.6) | 71.6 | 0.90 | **CORRECT** |
| FHC_R | (751.7, 1312.6) | (723.5, 1354.8) | (723.5, 1354.8) | (714.1, 1358.5) | 59.3 | 0.64 | **CORRECT** |
| FHC_L | (1887.8, 1417.1) | (1880.3, 1450.6) | (1880.3, 1450.6) | (1888.7, 1457.5) | 40.4 | 0.77 | **CORRECT** |
| ASL_R | (565.4, 844.5) | (436.7, 1033.4) | (436.7, 1033.4) | (431.5, 1032.4) | 230.7 | 0.47 | **INCORRECT** |
| ASL_L | (2192.2, 953.6) | (1822.5, 1261.8) | (2234.3, 1099.9) | (2243.0, 1098.7) | 153.7 | 0.58 | **INCORRECT** |
| ASM_R | (888.0, 1112.6) | (959.1, 1082.4) | (959.1, 1082.4) | (955.4, 1082.5) | 73.9 | 0.66 | **CORRECT** |
| ASM_L | (1783.2, 1194.4) | (1722.7, 1192.6) | (1722.7, 1192.6) | (1731.4, 1191.3) | 51.9 | 0.60 | **CORRECT** |
| FNM_R | (551.7, 1485.3) | (583.5, 1605.9) | (583.5, 1605.9) | (578.6, 1610.6) | 128.2 | 0.71 | **INCERTAIN** |
| FNM_L | (2033.2, 1648.9) | (1970.4, 1672.9) | (1970.4, 1672.9) | (1980.6, 1682.3) | 62.3 | 0.76 | **CORRECT** |
| FSP_R | (458.5, 1616.5) | (447.2, 2029.6) | (447.2, 2029.6) | (440.3, 2035.6) | 419.4 | 0.53 | **INCORRECT** |
| FSP_L | (2124.0, 1796.0) | (2170.4, 2047.8) | (2170.4, 2047.8) | (2179.6, 2064.1) | 273.8 | 0.62 | **INCORRECT** |
| FSD_R | (395.3, 2281.5) | (584.5, 2507.2) | (584.5, 2507.2) | (581.8, 2523.5) | 305.6 | 0.47 | **INCORRECT** |
| FSD_L | (2044.4, 2361.8) | (2213.5, 2519.3) | (2213.5, 2519.3) | (2217.5, 2534.8) | 244.8 | 0.53 | **INCORRECT** |

## Analyse anatomique par landmark

### TD_R — INCERTAIN (142 px)
- **Trop bas** (~132 px caudal) et légèrement **trop médial**.
- Repère trochantérien reconnaissable mais sous le point GT.

### TD_L — CORRECT (72 px)
- Bon alignement latéral ; **léger décalage caudal** (~72 px).
- Pas de confusion gauche/droite.

### FHC_R / FHC_L — CORRECT (59 / 40 px)
- Centres de tête fémorale bien localisés.
- Biais caudal modéré (~40–45 px) sur les deux côtés.

### ASL_R — INCORRECT (231 px)
- **Trop latéral** (~134 px) et **trop bas** (~188 px).
- Point sur bord acétabulaire bas ou zone cotyloïdienne inférieure, pas le **bord supérieur du cotyle** attendu pour la VCE.
- Confiance faible (0,47).

### ASL_L — INCORRECT (154 px après refinement)
- **RAW YOLO** : trop médial (~370 px) et trop bas (~308 px) — erreur majeure modèle.
- **Refinement** : corrige le plan latéral (Δ 442 px) via offset ASM_L → ASL_L, mais reste **trop bas** (~145 px).
- Le refinement ne compense pas l'erreur verticale du modèle.

### ASM_R / ASM_L — CORRECT (74 / 52 px)
- Bords supérieurs de l'aile iliaque correctement placés.
- ASM_R légèrement trop médial et haut ; dans la tolérance Tönnis.

### FNM_R — INCERTAIN (128 px)
- **Trop bas** (~125 px) ; centre de col estimé trop distal.
- Risque de biais CCD côté droit.

### FNM_L — CORRECT (62 px)
- Col fémoral gauche acceptable.

### FSP_R — INCORRECT (419 px) — **pire landmark**
- **Massivement trop bas** (~419 px caudal).
- Point sur **diaphyse proximale / zone trochantérienne basse**, pas le sommet du col fémoral.
- Confiance modérée-faible (0,53) — le modèle « voit » une structure mais pas la bonne.

### FSP_L — INCORRECT (274 px)
- **Trop bas** (~268 px) ; même pattern que FSP_R.
- Confusion entre sommet de col et métaphyse distale.

### FSD_R — INCORRECT (306 px)
- **Trop médial** (~187 px) et **trop bas** (~242 px).
- Point sur **cortex diaphysaire** proche du bord inférieur d'image (y ≈ 2524 vs GT 2281).
- Repère col-diaphyse non identifié.

### FSD_L — INCORRECT (245 px)
- **Trop latéral** (~173 px) et **trop bas** (~173 px).
- Même confusion structurelle que FSD_R.

## RAW YOLO vs REFINED

Seul **ASL_L** est modifié par le refinement intégré.

| Landmark | Δ raw→refined (px) | Erreur raw vs GT | Erreur refined vs GT | Erreur final vs GT | Verdict refinement |
|----------|-------------------|------------------|---------------------|-------------------|-------------------|
| ASL_L | **442,4** | 481,4 | 152,2 | 153,7 | **Améliore** latéral ; reste INCORRECT (vertical) |
| Autres (×13) | 0,0 | = refined | = refined | ≈ raw + 5–19 px* | Neutre |

\* Écart API vs offline dû au letterbox 512 px en inférence API.

## Méthodologie

1. **GT** : annotations humaines `B26_01.json` (v=2, 2730 × 2665 px).
2. **YOLO raw** : inférence Ultralytics pleine résolution + parseur `mvp_geometry.yolo_adapter` (sans refinement).
3. **Refined** : pipeline `landmarks_from_yolo_label_with_refinement` (offset ASL_L calibré TRAIN).
4. **Final API** : `run_analyze_from_bytes` → `detection.refined_landmarks` en `original_image_pixels`.
5. **Erreur** : distance euclidienne final vs GT.
6. **Seuils** : CORRECT ≤ 75 px | INCERTAIN 76–149 px | INCORRECT ≥ 150 px.

CSV : `e2e_landmark_anatomical_audit_android.csv`

## Recommandations pour correction modèle (hors scope audit)

Priorité d'entraînement / annotation ciblée :

1. **FSP_R / FSP_L / FSD_R / FSD_L** — repères col et jonction col-diaphyse (4/4 INCORRECT).
2. **ASL_R / ASL_L** — bord supérieur cotyle ; ASL_L bénéficie du refinement mais nécessite aussi un meilleur ancrage vertical YOLO.
3. **TD_R / FNM_R** — affiner le placement caudal (INCERTAIN).

Aucune action requise sur overlay, reprojection ou calibration pour ce cas.
