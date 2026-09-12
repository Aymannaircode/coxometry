# V5 Phase 1 v2 — Post Epoch-1 Safety Audit

**Généré :** 2026-08-29 01:40 UTC
**Mode :** READ-ONLY — aucun training
**Run :** `runs/pose/yolo_pose_new_26_v5_phase1_it_v2-2`
**Verdict :** `V5_PHASE1_V2_FREEZE_BROKEN`

---

## Checkpoints comparés

| ID | Fichier |
|----|---------|
| A | `runs\pose\runs\pose\runs\yolo_pose_new_26_v2-3\weights\best.pt` |
| B | `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_surgical_init.pt` |
| C | `runs\pose\yolo_pose_new_26_v5_phase1_it_v2-2\weights\best.pt` |
| D | `runs\pose\yolo_pose_new_26_v5_phase1_it_v2-2\weights\last.pt` |

---

## 1. Comparaison tensorielle

### A vs B (parité V2 / surgical_init)

| Zone | Tensors | Changed | Max Δ | Mean Δ |
|------|--------:|--------:|------:|-------:|
| backbone | 216 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv2_box | 186 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv3_cls | 96 | 0 | 0.000000e+00 | 0.000000e+00 |
| dfl | 1 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv4_pose | 42 | 0 | 0.000000e+00 | 0.000000e+00 |
| other | 0 | 0 | 0.000000e+00 | 0.000000e+00 |

### B vs C (surgical_init → phase1 v2 best)

| Zone | Tensors | Changed | Max Δ | Mean Δ |
|------|--------:|--------:|------:|-------:|
| backbone | 216 | 216 | 1.023438e+01 | 5.408659e-01 |
| cv2_box | 186 | 186 | 6.652344e+00 | 5.428559e-01 |
| cv3_cls | 96 | 96 | 4.539062e+00 | 4.511602e-01 |
| dfl | 1 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv4_pose | 42 | 42 | 1.191406e+00 | 3.023147e-01 |
| other | 0 | 0 | 0.000000e+00 | 0.000000e+00 |

**cv4 détail B→C :**

| Sous-zone | Tensors | Changed | Max Δ | Mean Δ |
|-----------|--------:|--------:|------:|-------:|
| cv4 canaux 0–41 (old) | 36 | 36 | 1.191406e+00 | 1.627858e-01 |
| cv4 canaux 42–47 (IT) | 9 | 9 | 5.274441e-01 | 8.485173e-02 |

### B vs D (surgical_init → phase1 v2 last)

| Zone | Changed | Max Δ |
|------|--------:|------:|
| backbone | 216 | 1.023438e+01 |
| cv2_box | 186 | 6.652344e+00 |
| cv3_cls | 96 | 4.539062e+00 |
| dfl | 0 | 0.000000e+00 |
| cv4_pose | 42 | 1.191406e+00 |

---

## 2. Détection val (imgsz=640, conf=0.25, 5 images)

| Modèle | Détections / 5 |
|--------|:--------------:|
| A_V2_best | **5/5** |
| B_v5_surgical_init | **5/5** |
| C_phase1_v2_best | **0/5** |
| D_phase1_v2_last | **0/5** |

| Image | Modèle | n_boxes | conf | IoU vs GT |
|-------|--------|--------:|-----:|----------:|
| B26_10 | A_V2_best | 1 | 0.891736 | 0.9304567971752552 |
| B26_10 | B_v5_surgical_init | 1 | 0.891736 | 0.9304567971752552 |
| B26_10 | C_phase1_v2_best | 0 | — | — |
| B26_10 | D_phase1_v2_last | 0 | — | — |
| B26_13 | A_V2_best | 1 | 0.875427 | 0.8892124377628038 |
| B26_13 | B_v5_surgical_init | 1 | 0.875427 | 0.8892124377628038 |
| B26_13 | C_phase1_v2_best | 0 | — | — |
| B26_13 | D_phase1_v2_last | 0 | — | — |
| B26_17 | A_V2_best | 1 | 0.885234 | 0.9080565978081454 |
| B26_17 | B_v5_surgical_init | 1 | 0.885234 | 0.9080565978081454 |
| B26_17 | C_phase1_v2_best | 0 | — | — |
| B26_17 | D_phase1_v2_last | 0 | — | — |
| B26_20 | A_V2_best | 1 | 0.921167 | 0.8931882797269804 |
| B26_20 | B_v5_surgical_init | 1 | 0.921167 | 0.8931882797269804 |
| B26_20 | C_phase1_v2_best | 0 | — | — |
| B26_20 | D_phase1_v2_last | 0 | — | — |
| B26_26 | A_V2_best | 1 | 0.860271 | 0.7482001924791625 |
| B26_26 | B_v5_surgical_init | 1 | 0.860271 | 0.7482001924791625 |
| B26_26 | C_phase1_v2_best | 0 | — | — |
| B26_26 | D_phase1_v2_last | 0 | — | — |

---

## 3. EMA / checkpoint sauvegardé

| Checkpoint | ema object | optimizer object | epoch field |
|------------|:----------:|:----------------:|:-----------:|
| C_phase1_v2_best | False | False | -1 |
| D_phase1_v2_last | False | False | -1 |

Poids gelés divergents vs surgical_init dans checkpoint sauvegardé : **417** tensors

---

## 4. Optimizer (dans checkpoint)

Optimizer **non embarqué** dans best.pt (Ultralytics strip à la sauvegarde finale).

---

## 5. Freeze après epoch (inféré B→C)

- backbone/cv2/cv3/dfl unchanged : **False**
- cv4 old 0–41 unchanged : **False**
- cv4 IT 42–47 changed : **True** (9 tensors)

---

## 6. Loss epoch 1 (results.csv train + val)

| Composante | Train (logged) | Val (checkpoint metrics) |
|------------|---------------:|-------------------------:|
| box | 0.0000 | 1.9494 |
| pose | 11.3443 | 11.5073 |
| kobj | 0.6782 | 0.6893 |
| cls | 0.0000 | 3.5149 |
| dfl | 0.0000 | 4.1589 |

Train box/cls/dfl = 0 confirme Phase1ITOnlyPoseLoss actif pendant training.
Val box/cls/dfl > 0 = métriques calculées par validator stock (non masquées).

**Paradoxe observé :** loss train box/cls/dfl = 0 mais **100 % des poids**
backbone/cv2/cv3/cv4-old ont changé (max Δ backbone ≈ 10.2). Cela indique que
le gel/hooks appliqués dans `_setup_train()` **ne survivent pas** à la boucle
`_do_train()` réelle, ou que le checkpoint sauvegardé reflète le modèle live
(EMA stripé : `ema=None`, `optimizer=None`, `epoch=-1`).

La loss pose IT-only backpropage toujours via le graphe complet ; si `requires_grad`
est réactivé sur backbone/cv2/cv3, un seul epoch suffit à effondrer la détection.

---

## 7. Checkpoint validation

- Validation terminale utilise : **`runs\pose\yolo_pose_new_26_v5_phase1_it_v2-2\weights\best.pt`** (best.pt du run v2-2)
- best ≡ last (1 epoch) : **True**
- Init run : `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_surgical_init.pt`
- Métriques results.csv : P(B)=0.00333, R(B)=1, mAP50(B)=0.01417

---

## Conclusion : `V5_PHASE1_V2_FREEZE_BROKEN`

CSV : `v5_phase1_v2_epoch1_safety_audit.csv`
