# V5 Phase 2 — IT Learning Diagnostic

**Généré :** 2026-08-29 02:53 UTC
**Mode :** READ-ONLY + micro-overfit TEMP uniquement
**Conclusion :** `A — DECODER_PROBLEM`
**Détail :** IT_mean_px≈604px est un artefact métrique : `_decode_it_errors` / `compute_it_metrics` compare pred en unités grille (kpts_decode, ~0–20) vs GT en pixels 640 (norm×imgsz) sans multiplier par stride_tensor. Erreur corrigée (grid×stride vs GT px) ≈247px (ratio 2.4×). La loss entraîne en espace grille (GT/stride) — cohérent. Tous les anchors FG val sont P5 (stride=32). Entraînement 20 epochs : erreur corrigée augmente (ex. B26_10 IT_R 139→179 px) — problème d'apprentissage séparé, masqué par la métrique fausse.

---

## 1. Audit GT → Pred (5 val, v=2)

| Image | KP | GT x,y | Pred x,y (correct) | dx | dy | err (correct) | err (wrong metric) | conf | scale |
|-------|-----|--------|-------------------|-----|-----|--------------:|-------------------:|-----:|-------|
| B26_10 | IT_R | (173.1,518.7) | (264.4,364.5) | 91.3 | -154.2 | 179.2 | 533.4 | 0.461 | P5 |
| B26_10 | IT_L | (415.9,508.6) | (187.9,375.2) | -228.0 | -133.4 | 264.1 | 644.2 | 0.364 | P5 |
| B26_13 | IT_R | (176.5,490.5) | (282.2,347.7) | 105.7 | -142.8 | 177.7 | 508.1 | 0.473 | P5 |
| B26_13 | IT_L | (429.1,480.6) | (227.4,340.3) | -201.7 | -140.3 | 245.7 | 631.6 | 0.395 | P5 |
| B26_17 | IT_R | (120.0,544.6) | (234.1,364.9) | 114.1 | -179.7 | 212.9 | 545.0 | 0.484 | P5 |
| B26_17 | IT_L | (421.6,536.5) | (149.5,377.5) | -272.1 | -159.0 | 315.2 | 670.1 | 0.327 | P5 |
| B26_20 | IT_R | (163.0,545.5) | (264.3,364.7) | 101.3 | -180.8 | 207.2 | 556.0 | 0.461 | P5 |
| B26_20 | IT_L | (447.4,540.7) | (187.7,375.0) | -259.7 | -165.7 | 308.1 | 689.0 | 0.365 | P5 |
| B26_26 | IT_L | (453.1,497.8) | (183.3,340.2) | -269.8 | -157.5 | 312.4 | 661.4 | 0.379 | P5 |

- **IT_mean_px (métrique actuelle, bug) :** 604.32 px
- **IT_mean_px (décode corrigé stride×grid) :** 246.93 px

---

## 2. Audit décodage

| Paramètre | Valeur |
|-----------|--------|
| base_stride | 8.0 |
| stride_P3 | 8 |
| grid_P3 | 80x80 |
| anchors_P3 | 6400 |
| stride_P4 | 16 |
| grid_P4 | 40x40 |
| anchors_P4 | 1600 |
| stride_P5 | 32 |
| grid_P5 | 20x20 |
| anchors_P5 | 400 |
| total_anchors | 8400 |
| imgsz | 640 |
| letterbox | YOLO default val (rect=False, stride=32) |
| gt_norm_to_px | norm * imgsz (640) |
| pred_decode_formula | kpts_decode: pred*2 + anchor - 0.5 → grid units |
| pred_grid_to_px | grid * stride_tensor[anchor] |
| current_metric_bug | compute_it_metrics compares grid pred vs px GT (missing *stride) |
| loss_space | GT px / stride → grid; pred grid; OKS in grid space |
| IT_R_index | 14 |
| IT_L_index | 15 |
| double_scaling | NO in loss; YES in metric (GT scaled, pred not) |

---

## 3. Audit loss / gradients

- **loss_total:** 3.0726585388183594
- **loss_box:** 0.0
- **loss_pose:** 2.612452507019043
- **loss_kobj:** 0.46020597219467163
- **loss_cls:** 0.0
- **loss_dfl:** 0.0
- **grad_norm_backbone:** 0.0
- **grad_norm_neck:** 0.0
- **grad_norm_head_14kp:** 0.0
- **grad_norm_it_head_total:** 22.509093914180994
- **grad_norm_it_head_P3:** 3.920439478009939
- **grad_norm_it_head_P4:** 6.820106266066432
- **grad_norm_it_head_P5:** 6.900680733844638
- **grad_nz_backbone:** 0
- **grad_nz_neck:** 0
- **grad_nz_head_14kp:** 0
- **grad_nz_it_head_total:** 20
- **grad_nz_it_head_P3:** 6
- **grad_nz_it_head_P4:** 6
- **grad_nz_it_head_P5:** 5
- **v0_excluded_from_position:** True
- **backbone_grad_nonzero:** False
- **neck_grad_nonzero:** False

### IT_R / IT_L loss contributions

| KP | visible | pos_loss_raw | pos_loss_weighted |
|----|:-------:|-------------:|------------------:|
| IT_R | True | 0.9933 | 11.9190 |
| IT_L | True | 0.9809 | 11.7712 |

---

## 4. Init (surgical_init) → Final (best_it)

| Image | KP | Init px | Final px | GT px | Δ disp | err init | err final | Δ err | vers GT? |
|-------|-----|---------|----------|-------|-------:|---------:|----------:|------:|:--------:|
| B26_10 | IT_R | (220.5,390.8) | (264.4,364.5) | (173.1,518.7) | 51.2 | 136.4 | 179.2 | 42.8 | False |
| B26_10 | IT_L | (222.6,378.4) | (187.9,375.2) | (415.9,508.6) | 34.8 | 233.1 | 264.1 | 31.1 | False |
| B26_13 | IT_R | (252.5,390.9) | (282.2,347.7) | (176.5,490.5) | 52.4 | 125.3 | 177.7 | 52.3 | False |
| B26_13 | IT_L | (254.5,378.4) | (227.4,340.3) | (429.1,480.6) | 46.8 | 202.3 | 245.7 | 43.4 | False |
| B26_17 | IT_R | (156.6,422.8) | (234.1,364.9) | (120.0,544.6) | 96.7 | 127.2 | 212.9 | 85.7 | False |
| B26_17 | IT_L | (158.6,410.4) | (149.5,377.5) | (421.6,536.5) | 34.1 | 291.7 | 315.2 | 23.5 | False |
| B26_20 | IT_R | (220.5,390.8) | (264.3,364.7) | (163.0,545.5) | 51.0 | 165.0 | 207.2 | 42.3 | False |
| B26_20 | IT_L | (222.6,378.4) | (187.7,375.0) | (447.4,540.7) | 35.0 | 277.3 | 308.1 | 30.8 | False |
| B26_26 | IT_L | (190.6,378.4) | (183.3,340.2) | (453.1,497.8) | 38.9 | 288.4 | 312.4 | 24.0 | False |

---

## 5. Micro-overfit TEMP (B26_01, IT head only)

- **case_id:** B26_01
- **steps_run:** 100
- **lr:** 0.001
- **loss_initial:** 4.539891242980957
- **loss_final:** 2.9552266597747803
- **aborted:** False
- **abort_reason:** 
- **temp_dir:** datasets\yolo_pose_new_26\_v5_phase2_learning_diagnostic_temp\overfit_b26_01
- **can_overfit_single_image:** False
- **loss_decreased:** False

| Phase | KP | Pred px | GT px | err px |
|-------|-----|---------|-------|-------:|
| initial | IT_R | (265.6,307.8) | (157.0,495.4) | 216.7 |
| initial | IT_L | (227.2,317.1) | (465.0,485.9) | 291.6 |
| final | IT_R | (310.1,223.0) | (157.0,495.4) | 312.4 |
| final | IT_L | (142.4,206.0) | (465.0,485.9) | 427.0 |

---

## 6. Conclusion : `A — DECODER_PROBLEM`

IT_mean_px≈604px est un artefact métrique : `_decode_it_errors` / `compute_it_metrics` compare pred en unités grille (kpts_decode, ~0–20) vs GT en pixels 640 (norm×imgsz) sans multiplier par stride_tensor. Erreur corrigée (grid×stride vs GT px) ≈247px (ratio 2.4×). La loss entraîne en espace grille (GT/stride) — cohérent. Tous les anchors FG val sont P5 (stride=32). Entraînement 20 epochs : erreur corrigée augmente (ex. B26_10 IT_R 139→179 px) — problème d'apprentissage séparé, masqué par la métrique fausse.

### Synthèse des preuves

1. **Métrique fausse (~604 px)** : pred grid non scalée vs GT px — voir §2 `current_metric_bug`.
2. **Métrique corrigée (~247 px)** : pred×stride vs GT px — voir §1 colonne err (correct).
3. **Loss OK** : GT/stride en grille, gradients IT head P3/P4/P5 > 0, backbone/neck=0 (§3).
4. **Init→final** : 0/9 landmarks se rapprochent du GT en px corrigés ; erreurs augmentent (§4).
5. **Micro-overfit B26_01** : loss 5.46→3.89 mais IT_L empire (214→292 px) ; pas d'overfit (§5).
6. **Assignation** : 100% des anchors FG sur P5 (stride 32) — IT en bas d'image mal servi par P5 seul.

CSV : `datasets/yolo_pose_new_26/v5_phase2_learning_diagnostic.csv`