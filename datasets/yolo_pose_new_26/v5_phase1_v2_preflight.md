# V5 Phase 1 v2 — Pre-flight IT-only (trainer-integrated)

**Généré :** 2026-08-29 01:29 UTC
**Mode :** PRE-FLIGHT — aucun entraînement complet, `optimizer.step()` simulé sur copie
**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v2.py`
**Verdict :** `V5_PHASE1_V2_READY`

---

## Correction v2 vs v1

| Problème v1 | Correction v2 |
|-------------|---------------|
| Gel/hooks appliqués avant `yolo.train()` | `V5Phase1PoseTrainer._setup_train()` ré-applique après Ultralytics |
| `requires_grad` reset par trainer L321-326 | `setup_phase1_model()` post-setup |
| `ITOnlyPoseLoss` perdu | `init_criterion` patché dans le trainer |
| EMA met à jour tous les poids | EMA restreint aux paramètres IT entraînables |
| box/cls/dfl actifs | `Phase1ITOnlyPoseLoss` zero box/cls/dfl |

---

## 1. État freeze APRÈS `_setup_train()`

| Zone | Paramètres trainables | Attendu |
|------|:---------------------:|:-------:|
| Backbone | 0 | 0 |
| cv2 | 0 | 0 |
| cv3 | 0 | 0 |
| DFL | 0 | 0 |
| cv4 (hooks IT) | 24 | 24 |
| Hooks gradient | 24 | ≥24 |

---

## 2. Loss IT-only (batch réel, post-trainer-init)

| Composante | Weighted loss | Attendu Phase 1 |
|------------|-------------:|:---------------:|
| box | 0.000000 | 0 |
| pose | 11.859020 | >0 |
| kobj | 0.686623 | ≥0 |
| cls | 0.000000 | 0 |
| dfl | 0.000000 | 0 |

KP 0–13 position (effective) : **0.000000**
KP 0–13 visibility (effective) : **0.000000**

---

## 3. v=0 IT (position loss = 0)

| Landmark | gt_visible | position_loss_raw |
|----------|:----------:|------------------:|
| IT_R | False | 0.000000 |

---

## 4. Gradients (forward → loss → backward, sans step)

| Zone | Tensors avec grad | Attendu |
|------|:-----------------:|:-------:|
| Backbone | 0 | 0 |
| cv2 | 0 | 0 |
| cv3 | 0 | 0 |
| DFL | 0 | 0 |
| cv4 canaux 0–41 | 0 | 0 |
| cv4 canaux 42–47 | 8 | >0 |

---

## 5. EMA

**Mode :** `ema_restricted_trainable`

EMA restreint aux paramètres IT entraînables — les zones gelées conservent leur snapshot
initial dans le modèle EMA (pas de dérive sur backbone/cv2/cv3/cv4-old).

---

## 6. Simulated `optimizer.step()` (copie `v5_phase1_v2_work_step.pt`)

| Zone | Changed / Total | Max abs diff |
|------|:---------------:|-------------:|
| backbone | 0/108 | 0.000000e+00 |
| cv2_box | 0/96 | 0.000000e+00 |
| cv3_cls | 0/51 | 0.000000e+00 |
| cv4_pose | 8/24 | 1.001358e-05 |
| dfl | 0/1 | 0.000000e+00 |

cv4 ancien bloc modifié : **0** tensors (attendu 0)
cv4 IT bloc modifié : **8** tensors (attendu >0)

---

## 7. Checkpoints

| Fichier | Rôle |
|---------|------|
| `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_surgical_init.pt` | Init Phase 0 — **intact** |
| `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_phase1_v2_work.pt` | Copie travail preflight |
| `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_phase1_v2_work_step.pt` | Copie step simulé |

---

## Checklist

- [x] `checkpoint_exists` → True
- [x] `work_checkpoint_separate` → True
- [x] `trainer_custom_subclass` → True
- [x] `freeze_applied_after_setup` → True
- [x] `gradient_hooks_installed` → True
- [x] `criterion_it_only` → True
- [x] `old_kp_position_zero` → True
- [x] `old_kp_visibility_zero` → True
- [x] `det_loss_zero_in_total` → True
- [x] `v0_it_no_position` → True
- [x] `backbone_no_grad` → True
- [x] `cv2_no_grad` → True
- [x] `cv3_no_grad` → True
- [x] `dfl_no_grad` → True
- [x] `cv4_old_blocked` → True
- [x] `cv4_it_active` → True
- [x] `ema_restricted` → True
- [x] `optimizer_trainable_only` → True
- [x] `no_optimizer_step_in_probe` → True
- [x] `simulated_step_only_it_changes` → True

---

## Conclusion : `V5_PHASE1_V2_READY`

CSV : `v5_phase1_v2_preflight.csv`

Pour entraîner (après READY) :
```
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v5_phase1_v2.py --train
```
