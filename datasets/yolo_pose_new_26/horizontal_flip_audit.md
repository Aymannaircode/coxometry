# Audit flip horizontal — new_26

**Généré :** 2026-08-23T21:03:03.332796+00:00
**Mode :** lecture seule

## Verdict : **D**

Flip horizontal correctement configuré (flip_idx, paires R/L, simulation x'=1-x). Compte tenu du diagnostic V2 (ASL_L ~538 px sur TRAIN, ASL_R/ASM_L corrects, mapping validé), le flip n'est probablement pas la cause principale de l'échec ASL_L.

## Configuration Ultralytics V2

| Paramètre | Valeur | Source |
|-----------|--------|--------|
| fliplr | **0.5** | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/args.yaml` |
| flipud | **0.0** | args.yaml |
| mosaic | **1.0** | args.yaml |
| auto_augment | **randaugment** | args.yaml |
| erasing | **0.4** | args.yaml |
| data | `.\datasets\yolo_pose_new_26\dataset.yaml` | args.yaml |

## Dataset pose (`dataset.yaml`)

- **kpt_shape :** `[14, 3]`
- **flip_idx :** `[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]`
- **prepare_yolo FLIP_IDX :** `[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]`
- **flip_idx == prepare :** Oui

### kpt_names

| Index | Nom |
|------:|-----|
| 0 | TD_R |
| 1 | TD_L |
| 2 | FHC_R |
| 3 | FHC_L |
| 4 | ASL_R |
| 5 | ASL_L |
| 6 | ASM_R |
| 7 | ASM_L |
| 8 | FNM_R |
| 9 | FNM_L |
| 10 | FSP_R |
| 11 | FSP_L |
| 12 | FSD_R |
| 13 | FSD_L |

## Mapping flip_idx attendu (7 paires R/L)

Ultralytics applique : `x' = w - x` puis `kpt[i] = kpt_mirrored[flip_idx[i]]`.

| Paire | Index R | Index L | flip_idx[R]→ | flip_idx[L]→ | Attendu |
|-------|--------:|--------:|-------------:|-------------:|---------|
| TD_R↔TD_L | 0 | 1 | 1 | 0 | OK |
| FHC_R↔FHC_L | 2 | 3 | 3 | 2 | OK |
| ASL_R↔ASL_L | 4 | 5 | 5 | 4 | OK |
| ASM_R↔ASM_L | 6 | 7 | 7 | 6 | OK |
| FNM_R↔FNM_L | 8 | 9 | 9 | 8 | OK |
| FSP_R↔FSP_L | 10 | 11 | 11 | 10 | OK |
| FSD_R↔FSD_L | 12 | 13 | 13 | 12 | OK |

### Vérification ASL / ASM (confusion potentielle)

- flip_idx[4] (ASL_R) = **5** — attendu **5** (ASL_L), pas 7 (ASM_L)
- flip_idx[5] (ASL_L) = **4** — attendu **4** (ASL_R), pas 6 (ASM_R)
- flip_idx[6] (ASM_R) = **7** — attendu **7** (ASM_L)
- flip_idx[7] (ASM_L) = **6** — attendu **6** (ASM_R)

- Pattern ASL↔ASM inversé ? **Non**

## Simulation sur labels TRAIN

- Cas audités : **21**
- Paires R/L par cas : **7**
- Simulation conforme (tolérance 1e-05) : **Oui**

### Détail par paire (erreur max sur tous les cas train)

| Paire | Max error | Tous OK |
|-------|-----------|---------|
| TD_R/TD_L | 0.000000 | Oui |
| FHC_R/FHC_L | 0.000000 | Oui |
| ASL_R/ASL_L | 0.000000 | Oui |
| ASM_R/ASM_L | 0.000000 | Oui |
| FNM_R/FNM_L | 0.000000 | Oui |
| FSP_R/FSP_L | 0.000000 | Oui |
| FSD_R/FSD_L | 0.000000 | Oui |

### Exemple ASL (premier cas train)

**Cas :** B26_01

| Keypoint | x orig | y orig | x après flip | y après flip | Attendu si miroir R/L |
|----------|--------|--------|--------------|--------------|------------------------|
| ASL_R | 0.2071 | 0.3169 | 0.1970 | 0.3578 | x=1-x(ASL_L)=0.1970 |
| ASL_L | 0.8030 | 0.3578 | 0.7929 | 0.3169 | x=1-x(ASL_R)=0.7929 |

## Comportement Ultralytics (référence code)

- `ultralytics/data/augment.py` : `RandomFlip` miroir horizontal + `keypoints[:, flip_idx, :]`.
- Si `flip_idx` absent et `fliplr > 0` → flip **désactivé** avec warning.
- Si `len(flip_idx) != kpt_shape[0]` → **ValueError** au build des augmentations.

## Interprétation des verdicts

| Verdict | Signification |
|---------|---------------|
| **A** | Flip parfaitement configuré |
| **B** | Flip R/L mal configuré |
| **C** | Flip non configuré / ambigu |
| **D** | Flip correct mais probablement pas la cause ASL_L |

## Regénérer

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\audit_horizontal_flip_new_26.py
```
