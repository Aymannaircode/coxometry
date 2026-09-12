# V5 Phase 1 v3 — Epoch-1 Safety Audit

**Généré :** 2026-08-29 01:54 UTC
**Mode :** READ-ONLY — aucun training
**Run :** `runs/pose/yolo_pose_new_26_v5_phase1_it_v3`
**Verdict :** `V5_PHASE1_V3_EPOCH1_SAFE`

---

## Checkpoints comparés

| ID | Fichier |
|----|---------|
| A | `runs\pose\runs\pose\runs\yolo_pose_new_26_v2-3\weights\best.pt` |
| B | `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_surgical_init.pt` |
| C | `runs\pose\yolo_pose_new_26_v5_phase1_it_v3\weights\best.pt` |
| D | `runs\pose\yolo_pose_new_26_v5_phase1_it_v3\weights\last.pt` |

---

## 1. Comparaison tensorielle (B = surgical_init)

### A vs B (parité V2 / surgical_init)

| Zone | Tensors | Changed | Max Δ | Mean Δ |
|------|--------:|--------:|------:|-------:|
| backbone | 216 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv2_box | 186 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv3_cls | 96 | 0 | 0.000000e+00 | 0.000000e+00 |
| dfl | 1 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv4_pose | 42 | 0 | 0.000000e+00 | 0.000000e+00 |
| other | 0 | 0 | 0.000000e+00 | 0.000000e+00 |

### B vs C (surgical_init → epoch-1 best) — **attendu : frozen=0, IT>0**

| Zone | Tensors | Changed | Max Δ | Mean Δ |
|------|--------:|--------:|------:|-------:|
| backbone | 216 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv2_box | 186 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv3_cls | 96 | 0 | 0.000000e+00 | 0.000000e+00 |
| dfl | 1 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv4_pose | 42 | 5 | 2.848816e-02 | 1.502453e-04 |
| other | 0 | 0 | 0.000000e+00 | 0.000000e+00 |

**cv4 détail B→C :**

| Sous-zone | Tensors | Changed | Max Δ | Mean Δ |
|-----------|--------:|--------:|------:|-------:|
| cv4 canaux 0–41 (old) | 36 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv4 canaux 42–47 (IT) | 9 | 3 | 1.124144e-04 | 1.298627e-05 |

### B vs D (surgical_init → epoch-1 last)

| Zone | Changed | Max Δ |
|------|--------:|------:|
| backbone | 0 | 0.000000e+00 |
| cv2_box | 0 | 0.000000e+00 |
| cv3_cls | 0 | 0.000000e+00 |
| dfl | 0 | 0.000000e+00 |
| cv4_pose | 5 | 2.848816e-02 |

---

## 2. Inférence val (imgsz=640, conf=0.25, 5 images)

| Modèle | Détections / 5 |
|--------|:--------------:|
| A_V2_best | **5/5** |
| B_v5_surgical_init | **5/5** |
| C_phase1_v3_best | **5/5** |
| D_phase1_v3_last | **5/5** |

| Image | Modèle | n_boxes | conf | IoU vs GT | cx | cy | w | h |
|-------|--------|--------:|-----:|----------:|---:|---:|--:|--:|
| B26_10 | A_V2_best | 1 | 0.891736 | 0.930457 | 0.485651 | 0.642571 | 0.697048 | 0.714605 |
| B26_10 | B_v5_surgical_init | 1 | 0.891736 | 0.930457 | 0.485651 | 0.642571 | 0.697048 | 0.714605 |
| B26_10 | C_phase1_v3_best | 1 | 0.891736 | 0.930457 | 0.485651 | 0.642571 | 0.697048 | 0.714605 |
| B26_10 | D_phase1_v3_last | 1 | 0.891736 | 0.930457 | 0.485651 | 0.642571 | 0.697048 | 0.714605 |
| B26_13 | A_V2_best | 1 | 0.875427 | 0.889212 | 0.489388 | 0.597133 | 0.678469 | 0.717273 |
| B26_13 | B_v5_surgical_init | 1 | 0.875427 | 0.889212 | 0.489388 | 0.597133 | 0.678469 | 0.717273 |
| B26_13 | C_phase1_v3_best | 1 | 0.875427 | 0.889212 | 0.489388 | 0.597133 | 0.678469 | 0.717273 |
| B26_13 | D_phase1_v3_last | 1 | 0.875427 | 0.889212 | 0.489388 | 0.597133 | 0.678469 | 0.717273 |
| B26_17 | A_V2_best | 1 | 0.885234 | 0.908057 | 0.465833 | 0.665047 | 0.745926 | 0.669907 |
| B26_17 | B_v5_surgical_init | 1 | 0.885234 | 0.908057 | 0.465833 | 0.665047 | 0.745926 | 0.669907 |
| B26_17 | C_phase1_v3_best | 1 | 0.885234 | 0.908057 | 0.465833 | 0.665047 | 0.745926 | 0.669907 |
| B26_17 | D_phase1_v3_last | 1 | 0.885234 | 0.908057 | 0.465833 | 0.665047 | 0.745926 | 0.669907 |
| B26_20 | A_V2_best | 1 | 0.921167 | 0.893188 | 0.502177 | 0.655079 | 0.812342 | 0.689842 |
| B26_20 | B_v5_surgical_init | 1 | 0.921167 | 0.893188 | 0.502177 | 0.655079 | 0.812342 | 0.689842 |
| B26_20 | C_phase1_v3_best | 1 | 0.921167 | 0.893188 | 0.502177 | 0.655079 | 0.812342 | 0.689842 |
| B26_20 | D_phase1_v3_last | 1 | 0.921167 | 0.893188 | 0.502177 | 0.655079 | 0.812342 | 0.689842 |
| B26_26 | A_V2_best | 1 | 0.860271 | 0.748200 | 0.487214 | 0.613216 | 0.819421 | 0.773569 |
| B26_26 | B_v5_surgical_init | 1 | 0.860271 | 0.748200 | 0.487214 | 0.613216 | 0.819421 | 0.773569 |
| B26_26 | C_phase1_v3_best | 1 | 0.860271 | 0.748200 | 0.487214 | 0.613216 | 0.819421 | 0.773569 |
| B26_26 | D_phase1_v3_last | 1 | 0.860271 | 0.748200 | 0.487214 | 0.613216 | 0.819421 | 0.773569 |

---

## 3. Landmarks — 14 anciens KP (val, 5 images)

### Global

| Métrique | V2 | surgical_init | epoch-1 best | epoch-1 last |
|----------|---:|--------------:|-------------:|-------------:|
| Mean px | 134.95 | 134.95 | 134.95 | 134.95 |
| Median px | 98.18 | 98.18 | 98.18 | 98.18 |
| P90 px | 293.40 | 293.40 | 293.40 | 293.40 |

**Tiers V2 :** CORRECT=25 INCERTAIN=28 INCORRECT=17
**Tiers epoch-1 best :** CORRECT=25 INCERTAIN=28 INCORRECT=17

### Par landmark (mean px, delta best − surgical)

| Landmark | V2 | surgical | best | Δ best−surg | Catastrophique |
|----------|---:|---------:|-----:|------------:|:--------------:|
| TD_R | 74.84 | 74.84 | 74.84 | 0.00 | ✓ |
| TD_L | 78.53 | 78.53 | 78.53 | 0.00 | ✓ |
| FHC_R | 62.88 | 62.88 | 62.88 | 0.00 | ✓ |
| FHC_L | 80.94 | 80.94 | 80.94 | 0.00 | ✓ |
| ASL_R | 147.73 | 147.73 | 147.73 | 0.00 | ✓ |
| ASL_L | 471.72 | 471.72 | 471.72 | 0.00 | ✓ |
| ASM_R | 81.32 | 81.32 | 81.32 | 0.00 | ✓ |
| ASM_L | 80.94 | 80.94 | 80.94 | 0.00 | ✓ |
| FNM_R | 59.72 | 59.72 | 59.72 | 0.00 | ✓ |
| FNM_L | 81.05 | 81.05 | 81.05 | 0.00 | ✓ |
| FSP_R | 127.63 | 127.63 | 127.63 | 0.00 | ✓ |
| FSP_L | 192.77 | 192.77 | 192.77 | 0.00 | ✓ |
| FSD_R | 180.98 | 180.98 | 180.98 | 0.00 | ✓ |
| FSD_L | 168.21 | 168.21 | 168.21 | 0.00 | ✓ |

Dégradation significative détectée : **False** (seuil +25.0 px vs surgical, ratio ×3.0)

---

## 4. IT (IT_R / IT_L) — images v≥2 uniquement

| Modèle | N eval | Mean px | Median | P90 | CORRECT | INCERTAIN | INCORRECT |
|--------|-------:|--------:|-------:|----:|--------:|----------:|----------:|
| epoch-1 best | 9 | 928.93 | 898.29 | 1096.17 | 0 | 0 | 9 |
| epoch-1 last | 9 | 928.93 | 898.29 | 1096.17 | — | — | — |

v=0/v=1 : non comptés comme erreur de prédiction.

---

## 5. Freeze après epoch (inféré B→C)

- backbone unchanged : **True**
- cv2 unchanged : **True**
- cv3 unchanged : **True**
- dfl unchanged : **True**
- cv4 old 0–41 unchanged : **True**
- cv4 IT 42–47 changed : **True** (3 tensors)

---

## 6. Optimizer

Optimizer **non embarqué** dans best.pt/last.pt (strip Ultralytics). Inférence post-hoc depuis deltas poids B→C :

- Seuls paramètres IT modifiés (inféré) : **True**
- Changements zones gelées : `{}`
- cv4 old changes : 0, cv4 IT changes : 5

---

## 7. EMA / checkpoint sauvegardé

| Checkpoint | ema object | optimizer object | epoch field |
|------------|:----------:|:----------------:|:-----------:|
| C_phase1_v3_best | False | False | -1 |
| D_phase1_v3_last | False | False | -1 |

Poids gelés divergents vs surgical_init dans checkpoint sauvegardé (model weights) : **0** tensors
- best ≡ last : **True**

---

## 8. Loss epoch 1 (results.csv)

| Composante | Train | Val |
|------------|------:|----:|
| box | 0.0000 | 0.9871 |
| pose | 11.3665 | 3.4651 |
| kobj | 0.6852 | 0.4933 |
| cls | 0.0000 | 0.5238 |
| dfl | 0.0000 | 1.7199 |

mAP50(B)=0.995, R(B)=1
Init run : `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_surgical_init.pt`, pretrained=True

---

## Conclusion : `V5_PHASE1_V3_EPOCH1_SAFE`

CSV : `v5_phase1_v3_epoch1_QA.csv`
