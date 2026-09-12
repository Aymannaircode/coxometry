# Correctif reprojection coordonnées — POST /analyze

**Date :** 2026-08-24  
**Scope :** backend uniquement (aucune modification Flutter, YOLO, labels, formules géométriques)

## Problème

Sur `B26_01` (2730×2665 px), YOLO détecte en espace prétraité **512×512** (letterbox `scale≈0.188`, `pad_y=6`).  
L'API renvoyait les landmarks **sans reprojection** → Flutter dessinait sur l'image originale → **14/14 points visuellement faux** (cluster haut-gauche ~200–450 px).

## Correction

`run_measurement_pipeline` (`backend/app/services/measurement_service.py`) applique désormais **`reproject_landmarks`** (inverse exact du letterbox) avant exposition API :

```
x_resized = x_prep - pad_x
y_resized = y_prep - pad_y
x_orig    = x_resized / scale
y_orig    = y_resized / scale
```

- **Mesures VCE/Tönnis/CCD** : inchangées (calculées toujours en espace prétraité — angles invariantes).
- **Refinement ASL_L** : inchangé (non modifié).
- **raw_landmarks** et **refined_landmarks** : coordonnées **image originale** (pixels).

## Métadonnées exposées

Bloc `detection.coordinate_space` + champs miroir dans `audit` :

| Champ | B26_01 |
|-------|--------|
| `image_width` | 2730 |
| `image_height` | 2665 |
| `preprocessed_width` | 512 |
| `preprocessed_height` | 512 |
| `scale` | 0.187546 |
| `pad_x` | 0 |
| `pad_y` | 6 |
| `landmark_coordinate_space` | `original_image_pixels` |

## Vérification B26_01 (YOLO V2 réel)

| Landmark | Avant fix (API, ~512 px) | Après fix (original px) | GT annotation |
|----------|--------------------------|-------------------------|---------------|
| TD_R | ~184, ~385 | **982.2, 2021.6** | 928.9, 1889.7 |
| TD_L | ~300, ~386 | **1599.8, 2024.6** | 1592.4, 1953.4 |
| FHC_R | ~134, ~261 | **714.1, 1358.5** | 751.7, 1312.6 |
| ASL_L raw | ~346, ~241 | **1842.5, 1253.8** | 2192.2, 953.6 |
| ASL_L refined | ~836, ~137 | **4459.1, 697.2** ⚠️ | 2192.2, 953.6 |

**Interprétation :**

- **13/14 landmarks** (hors ASL_L refined) sont maintenant dans le bon espace pour l'overlay Flutter.
- **ASL_L refined** reste hors image (`x > 2730`) — problème **préexistant du refinement**, non corrigé dans ce patch (contrainte utilisateur). L'overlay devrait utiliser `raw_landmarks` pour ASL_L ou corriger le refinement dans un ticket séparé.

## Tests exécutés

| Suite | Résultat |
|-------|----------|
| `backend/tests` (126 tests) | **OK** (1 skipped — modèle absent en CI) |
| `mvp_geometry/tests` (54 tests) | **OK** |

Nouveaux tests : `backend/tests/test_analyze_coordinate_reprojection.py`

- 2730×2665, carré, paysage, portrait
- point connu round-trip letterbox
- raw/refined reprojetés cohérents
- aucune coordonnée inventée
- métadonnées `coordinate_space` dans la réponse API

## Fichiers modifiés

- `backend/app/services/measurement_service.py` — reprojection + métadonnées
- `backend/app/schemas/analyze.py` — `AnalyzeCoordinateSpaceOut`
- `backend/app/services/analyze.py` — sérialisation schéma
- `backend/tests/test_analyze_api.py` — assertion `coordinate_space`
- `backend/tests/test_analyze_coordinate_reprojection.py` — **nouveau**

## Non modifié (conformément aux contraintes)

- Poids YOLO V2, labels, annotations, predictions
- `mvp_geometry/measurements.py`, formules VCE/Tönnis/CCD
- Refinement ASL_L
- Application Flutter mobile

## Prochaine étape recommandée (hors scope)

1. Flutter : afficher `refined_landmarks` sauf ASL_L si `refinement_out_of_bounds` (audit) — ou attendre fix refinement.
2. Ticket séparé : appliquer le refinement ASL_L **après** reprojection (ou en espace original).
