# Correctif unités refinement ASL_L

**Date :** 2026-08-24  
**Scope :** conversion offset TRAIN (pixels originaux) → espace prétraité letterbox

## Problème

`TRAIN_ASM_OFFSET_CALIBRATION = (511.56, -92.68)` est calibré en **pixels image originale**.  
Le détecteur YOLO infère en **512×512** letterbox, mais appliquait l'offset complet avant reprojection.

**B26_01 — avant correctif unités** (reprojection API déjà fixée) :

| Landmark | Raw (original px) | Refined (original px) | Statut |
|----------|-------------------|------------------------|--------|
| ASL_L | 1842.5, 1253.8 | **4459.1, 697.2** | ❌ hors image (x > 2730) |
| ASM_L | 1731.4, 1191.3 | 1731.4, 1191.3 | ✓ |

Offset effectif erroné : `(2727, -494)` px au lieu de `(511.56, -92.68)`.

## Solution

Module explicite `mvp_geometry/refinement/units.py` :

- `TRAIN_CALIBRATION_COORDINATE_SPACE = original_image_pixels`
- `calibration_for_preprocessed_space(cal, letterbox_scale)` :
  - `dx_pre = 511.56 × scale`
  - `dy_pre = -92.68 × scale`

Dans `yolo_pose.py`, avant `refine_asl_l` :

```python
preprocessed_cal = calibration_for_preprocessed_space(
    TRAIN_ASM_OFFSET_CALIBRATION, image.scale
)
```

**Calibration TRAIN inchangée** — seule la conversion d'unités est appliquée à l'inférence.

Audit enrichi : `refinement_coordinate_space`, `calibration_coordinate_space`, `calibration_dx_applied`, `letterbox_scale`, `refinement_out_of_bounds` (vérifié après reprojection originale).

## B26_01 — après correctif

| Champ | Valeur |
|-------|--------|
| scale | 0.187546 |
| dx_applied (preprocessed) | 95.94 |
| dy_applied (preprocessed) | -17.38 |
| ASL_L raw | 1842.5, 1253.8 |
| ASL_L refined | **2243.0, 1098.7** |
| ASM_L | 1731.4, 1191.3 |
| Offset effectif reprojeté | **(511.6, -92.6)** px ✓ |
| refinement_out_of_bounds | **False** ✓ |

Comparaison pleine résolution (labels offline, référence intégration) :

| | Offline V2 + refinement pleine rés. | API après fix |
|--|-----------------------------------|---------------|
| ASL_L refined | 2234.3, 1099.9 | 2243.0, 1098.7 |

## Mesures avant / après (B26_01)

| Mesure | Réf. intégration (pleine rés.) | Avant fix unités* | Après fix unités |
|--------|-------------------------------|-------------------|------------------|
| VCE_L | 44.80° | incohérent (ASL_L OOB) | **44.37°** |
| Tönnis_L | -10.73° | incohérent | **-10.54°** |
| CCD_R | 134.82° | 135.57° | **135.57°** |
| CCD_L | 163.18° | 162.37° | **162.37°** |

\* ASL_L refined à (4459, 697) — overlay et VCE/Tönnis_L invalides côté API.

**CCD strictement inchangé** (ne dépend pas de ASL_L).  
**VCE_L / Tönnis_L** alignés sur la référence d'intégration pleine résolution.

## Tests exécutés

| Suite | Résultat |
|-------|----------|
| `backend/tests` (136 tests) | **OK** |
| `mvp_geometry/tests` (58 tests) | **OK** |

Nouveaux :

- `mvp_geometry/tests/test_refinement_units.py`
- `backend/tests/test_asl_l_refinement_coordinate_fix.py`

## Fichiers modifiés

- `mvp_geometry/refinement/units.py` — **nouveau**
- `mvp_geometry/refinement/__init__.py` — exports
- `backend/app/services/detection/yolo_pose.py` — offset scalé + audit

## Non modifié

- Poids YOLO V2, labels, annotations, predictions
- `TRAIN_ASM_OFFSET_CALIBRATION` (511.56, -92.68)
- `measurements.py`, formules VCE/Tönnis/CCD
- Refinement désactivé : toujours actif
- Flutter

## Garanties

- `raw_landmarks` / `refined_landmarks` : même `coordinate_space` (`original_image_pixels`)
- 13 autres landmarks inchangés
- ASL_L raw inchangé
- Refinement toujours actif avec offset anatomique correct après reprojection
