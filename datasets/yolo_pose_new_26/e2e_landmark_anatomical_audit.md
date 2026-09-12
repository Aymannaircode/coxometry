# Audit anatomique landmarks — test E2E mobile

**Généré :** 2026-08-24T00:02:30Z
**Mode :** lecture seule. Aucun fichier de production, poids, labels ou annotations modifié.

## Image auditée

| Champ | Valeur |
|-------|--------|
| **Cas** | `B26_01` |
| **Fichier** | `C:\Users\g\OneDrive\Desktop\Projet-Ayman\datasets\yolo_pose_new_26\predictions_v2\images\B26_01.png` |
| **Dimensions** | 2730 × 2665 px |
| **Hypothèse E2E** | Radiographie **`B26_01.png`** du corpus new_26 (référence « test connue »). Si une autre B26_xx a été importée, appliquer la même méthode. |

## Cause principale overlay E2E (observation read-only)

`POST /analyze` renvoie les landmarks dans l'**espace prétraité 512×512**, alors que Flutter affiche l'**image originale** (~3000 px). Sans reprojection côté API, l'overlay regroupe tous les points en haut-gauche → **apparence anatomiquement fausse même si YOLO est acceptable**.

- Statut **overlay E2E** (coords API vs GT) : CORRECT 0/14, INCORRECT 14/14
- Statut **modèle YOLO V2** (coords reprojectées read-only vs GT) : CORRECT 6/14, INCORRECT 6/14, INCERTAIN 2/14

> 14/14 détectés **≠** 14/14 anatomiquement corrects.

## Synthèse — questions clés

1. **Landmarks faux (modèle reprojecté, INCORRECT) :** ASL_R, ASL_L, FSP_R, FSP_L, FSD_R, FSD_L
2. **Landmarks corrects (modèle reprojecté) :** TD_L, FHC_R, FHC_L, ASM_R, ASM_L, FNM_L
3. **Incertains :** TD_R, FNM_R
4. **Problème global ou local ?** **Localisé** — ASL_L reste le landmark le plus erroné sur le corpus ; FHC/FNM modérés ; FSP/FSD très variables. Ce n'est pas un échec uniforme du modèle.
5. **ASL_L seul problème ?** **Non** sur `B26_01` : 5 autres landmarks INCORRECT ou INCERTAIN côté modèle.

### Réponses ciblées (YOLO V2 reprojecté + offline, cas `B26_01`)

| Question | Réponse |
|----------|---------|
| **TD_R / TD_L** | TD_L **CORRECT** (72 px). TD_R **INCERTAIN** (142 px) — placement acceptable latéralement, léger décalage vertical. |
| **ASM_R / ASM_L** | **CORRECT** (74 px et 52 px) — Tönnis fiables sur ce cas. |
| **ASL_R / ASL_L** | **INCORRECT** (231 px et 481 px offline raw). ASL_L est le pire point ; ASL_R aussi hors tolérance. Confiance &lt; 0.5 sur ASL_R. |
| **FHC / FNM** | FHC_R/L et FNM_L **CORRECT** (40–62 px). FNM_R **INCERTAIN** (128 px). Proximal fémoral globalement bon. |
| **FSP / FSD** | **INCORRECT** (4/4) — 256–419 px. Points distaux mal ancrés ; FSD_R/FSD_L proches du bord inférieur d'image. |

**Deux causes distinctes de l'overlay E2E faux :**

1. **Bug d'espace de coordonnées** — l'API renvoie ~512 px, Flutter dessine ~2730 px → **14/14 INCORRECT** à l'écran (même TD_L correct anatomiquement).
2. **Erreurs modèle réelles** — même reprojecté, **6/14 INCORRECT**, **2/14 INCERTAIN** ; offline V2 confirme ASL et diaphyse distale comme familles faibles.

**ASL_L — RAW vs REFINED (comparaison explicite) :**

| Source | Coords (x, y) | vs GT (px) | Statut |
|--------|---------------|------------|--------|
| YOLO V2 **raw** offline | (1822.5, 1261.8) | 481 | INCORRECT |
| Refinement intégration (pleine rés.) | (2234.3, 1099.9) | ~152 | INCORRECT (améliore VCE mais reste &gt;150 px) |
| API refined (512 px, overlay Flutter) | (836.3, 136.8) | 1583 | INCORRECT |
| Reproj refined (audit read-only) | (4459.1, 697.2) | 2281 | INCORRECT — **hors image**, artefact reprojection+refinement |

Le refinement ASL_L aide la géométrie VCE en espace image pleine résolution, mais **ne suffit pas** à placer ASL_L correctement vs GT. Combiné à l'absence de reprojection API, l'overlay mobile est doublement faussé.

### Groupes anatomiques (statut modèle reprojecté vs GT)

| Groupe | Landmarks | CORRECT | INCORRECT | INCERTAIN |
|--------|-----------|---------|-----------|-----------|
| TD | 2 | 1 | 0 | 1 |
| Fémoral FHC/FNM/FSP/FSD | 8 | 3 | 4 | 1 |
| ASM (Tönnis) | 2 | 2 | 0 | 0 |
| ASL (VCE) | 2 | 0 | 2 | 0 |

## Détail des 14 landmarks

| Landmark | API raw (x,y) | Conf | API refined (overlay) | Reproj refined | Offline V2 | vs GT (overlay/modèle/offline) | Position reproj | Notes | Statut overlay | Statut modèle |
|----------|---------------|------|----------------------|----------------|------------|--------------------------------|-----------------|-------|----------------|---------------|
| TD_R | (184.2, 385.1) | 0.854 | (184.2, 385.1) | (982.2, 2021.6) | (975.9, 2004.9) | 1678.8 / 142.3 / 124.4 | patient D, bas — (982, 2022) px | API vs reprojecté 1821px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 142px; offline V2 vs GT 124px | **INCORRECT** | **INCERTAIN** |
| TD_L | (300.0, 385.7) | 0.901 | (300.0, 385.7) | (1599.8, 2024.6) | (1588.4, 2009.8) | 2031.7 / 71.6 / 56.6 | patient G, bas — (1600, 2025) px | API vs reprojecté 2092px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 72px; offline V2 vs GT 57px | **INCORRECT** | **CORRECT** |
| FHC_R | (133.9, 260.8) | 0.644 | (133.9, 260.8) | (714.1, 1358.5) | (723.5, 1354.8) | 1219.8 / 59.3 / 50.8 | patient D, milieu — (714, 1358) px | API vs reprojecté 1242px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 59px; offline V2 vs GT 51px | **INCORRECT** | **CORRECT** |
| FHC_L | (354.2, 279.3) | 0.772 | (354.2, 279.3) | (1888.7, 1457.5) | (1880.3, 1450.6) | 1909.5 / 40.4 / 34.3 | patient G, milieu — (1889, 1457) px | API vs reprojecté 1935px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 40px; offline V2 vs GT 34px | **INCORRECT** | **CORRECT** |
| ASL_R | (80.9, 199.6) | 0.470 | (80.9, 199.6) | (431.5, 1032.4) | (436.7, 1033.4) | 806.6 / 230.7 / 228.5 | patient D, milieu — (431, 1032) px | API vs reprojecté 904px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 231px; offline V2 vs GT 228px | **INCORRECT** | **INCORRECT** |
| ASL_L | (345.6, 241.2) | 0.580 | (836.3, 136.8) | (4459.1, 697.2) | (1822.5, 1261.8) | 1583.0 / 2281.3 / 481.4 | patient G, haut — (4459, 697) px | API vs reprojecté 3666px — overlay E2E ≠ coords anatomiques; reprojecté hors image; écart GT (modèle reprojecté) 2281px; offline V2 vs GT 481px | **INCORRECT** | **INCORRECT** |
| ASM_R | (179.2, 209.0) | 0.670 | (179.2, 209.0) | (955.4, 1082.5) | (959.1, 1082.4) | 1148.5 / 73.9 / 77.3 | patient D, milieu — (955, 1082) px | API vs reprojecté 1169px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 74px; offline V2 vs GT 77px | **INCORRECT** | **CORRECT** |
| ASM_L | (324.7, 229.4) | 0.607 | (324.7, 229.4) | (1731.4, 1191.3) | (1722.7, 1192.6) | 1748.9 / 51.9 / 60.6 | patient G, milieu — (1731, 1191) px | API vs reprojecté 1704px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 52px; offline V2 vs GT 61px | **INCORRECT** | **CORRECT** |
| FNM_R | (108.5, 308.1) | 0.715 | (108.5, 308.1) | (578.6, 1610.6) | (583.5, 1605.9) | 1257.9 / 128.2 / 124.8 | patient D, milieu — (579, 1611) px | API vs reprojecté 1385px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 128px; offline V2 vs GT 125px | **INCORRECT** | **INCERTAIN** |
| FNM_L | (371.4, 321.5) | 0.766 | (371.4, 321.5) | (1980.6, 1682.3) | (1970.4, 1672.9) | 2126.8 / 62.3 / 67.2 | patient G, milieu — (1981, 1682) px | API vs reprojecté 2107px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 62px; offline V2 vs GT 67px | **INCORRECT** | **CORRECT** |
| FSP_R | (82.6, 387.8) | 0.527 | (82.6, 387.8) | (440.3, 2035.6) | (447.2, 2029.6) | 1285.0 / 419.4 / 413.2 | patient D, bas — (440, 2036) px | API vs reprojecté 1686px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 419px; offline V2 vs GT 413px | **INCORRECT** | **INCORRECT** |
| FSP_L | (408.8, 393.1) | 0.608 | (408.8, 393.1) | (2179.6, 2064.1) | (2170.4, 2047.8) | 2215.9 / 273.8 / 256.1 | patient G, bas — (2180, 2064) px | API vs reprojecté 2435px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 274px; offline V2 vs GT 256px | **INCORRECT** | **INCORRECT** |
| FSD_R | (109.1, 479.3) | 0.481 | (109.1, 479.3) | (581.8, 2523.5) | (584.5, 2507.2) | 1824.8 / 305.6 / 294.6 | patient D, bas — (582, 2524) px | API vs reprojecté 2098px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 306px; offline V2 vs GT 295px | **INCORRECT** | **INCORRECT** |
| FSD_L | (415.9, 481.4) | 0.529 | (415.9, 481.4) | (2217.5, 2534.8) | (2213.5, 2519.3) | 2487.5 / 244.8 / 231.1 | patient G, bas — (2218, 2535) px | API vs reprojecté 2732px — overlay E2E ≠ coords anatomiques; écart GT (modèle reprojecté) 245px; offline V2 vs GT 231px | **INCORRECT** | **INCORRECT** |

## RAW YOLO V2 vs REFINED

Seul **ASL_L** est raffiné par le pipeline. Les autres landmarks : raw = refined.

| Landmark | Δ raw→refined API (512 px) | Offline V2 raw vs GT | Reproj refined vs GT | Refinement (pleine rés.) vs GT | Verdict refinement |
|----------|----------------------------|----------------------|----------------------|--------------------------------|--------------------|
| TD_R | 0.0 | 124.4 | 142.3 | — | neutre |
| TD_L | 0.0 | 56.6 | 71.6 | — | neutre |
| FHC_R | 0.0 | 50.8 | 59.3 | — | neutre |
| FHC_L | 0.0 | 34.3 | 40.4 | — | neutre |
| ASL_R | 0.0 | 228.5 | 230.7 | — | neutre |
| **ASL_L** | **501.7** | **481.4** | 2281.3* | **~152** | améliore en pleine rés. ; **dégrade** via API sans reprojection |
| ASM_R | 0.0 | 77.3 | 73.9 | — | neutre |
| ASM_L | 0.0 | 60.6 | 51.9 | — | neutre |
| FNM_R | 0.0 | 124.8 | 128.2 | — | neutre |
| FNM_L | 0.0 | 67.2 | 62.3 | — | neutre |
| FSP_R | 0.0 | 413.2 | 419.4 | — | neutre |
| FSP_L | 0.0 | 256.1 | 273.8 | — | neutre |
| FSD_R | 0.0 | 294.6 | 305.6 | — | neutre |
| FSD_L | 0.0 | 231.1 | 244.8 | — | neutre |

\* Reproj refined ASL_L hors image (2730 px) — artefact audit, pas position anatomique fiable.

## Méthodologie

- **API** : `run_analyze_from_bytes` (identique Flutter E2E).
- **Reprojection audit** : calcul read-only via `reproject_landmarks` — **non** appliqué dans `measurement_service` actuel.
- **Offline V2** : labels `predictions_v2` (inférence pleine résolution, non modifiés).
- **GT** : annotations humaines v=2.
- Seuils : CORRECT ≤75px, INCORRECT ≥150px.

CSV : `e2e_landmark_anatomical_audit.csv`