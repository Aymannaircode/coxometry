# V5 Phase 2 — Training Pre-flight

**Généré :** 2026-08-29 02:23 UTC
**Mode :** PRE-FLIGHT — forward / loss / backward / sim-step — **aucun entraînement**
**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase2.py`
**Architecture :** `ITHeadMultiScaleFusion` (Option B)
**Verdict :** `V5_PHASE2_TRAINING_READY`
**Détail :** ITHeadMultiScaleFusion preflight passed; ready for --train

---

## 1. Paramètres

| Métrique | Valeur |
|----------|-------:|
| Trainable (IT head) | 362898 |
| Frozen (base) | 2853411 |
| Optimizer param count | 362898 |

---

## 2. Gradient probe (backward sans optimizer.step)

| Zone | grad norm | Attendu |
|------|----------:|:-------:|
| backbone | 0.0 | 0 |
| neck | 0.0 | 0 |
| head_14kp | 0.0 | 0 |
| it_head_total | 2.6343189566396177 | >0 |
| it_head_P3 | 0.5686169671826065 | >0 |
| it_head_P4 | 0.6138790883123875 | >0 |
| it_head_P5 | 0.5399644067510962 | >0 |

---

## 3. Simulated optimizer.step (mémoire)

- IT head changed : **True**
- Base frozen OK : **True**

---

## 4. Parité initiale

- 14 KP max Δ : **0.00e+00**
- boxes max Δ : **0.00e+00**
- cls max Δ : **0.00e+00**

---

## 5. Loss IT-only

- KP 0–13 : position=0, visibility=0
- box / cls / dfl : 0
- IT_R / IT_L : actifs si v=2
- v=0 : exclu des métriques et de la position loss

---

## 6. Config entraînement initial (non lancé)

| Param | Valeur |
|-------|--------|
| imgsz | 640 |
| batch | 1 |
| lr0 | 1e-4 |
| optimizer | AdamW |
| epochs | 30 |
| patience | 8 |
| mosaic | 0 |
| randaugment | off |
| erasing | 0 |

---

## Checklist

- [x] `dryrun_ready` → True
- [x] `trainable_it_head_expected` → True
- [x] `frozen_base_gt_0` → True
- [x] `optimizer_it_only` → True
- [x] `backbone_grad_0` → True
- [x] `neck_grad_0` → True
- [x] `head_14kp_grad_0` → True
- [x] `it_head_grad_gt_0` → True
- [x] `p3_grad_gt_0` → True
- [x] `p4_grad_gt_0` → True
- [x] `p5_grad_gt_0` → True
- [x] `det_loss_zero` → True
- [x] `parity_14kp` → True
- [x] `parity_det` → True
- [x] `sim_it_changed` → True
- [x] `sim_base_frozen` → True
- [x] `init_base_matches_surgical` → True
- [x] `no_optimizer_step_in_preflight` → True
- [x] `detection_v2_preserved` → True

---

## Conclusion : `V5_PHASE2_TRAINING_READY`

ITHeadMultiScaleFusion preflight passed; ready for --train

Pour entraîner (après READY, explicite) :
```powershell
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v5_phase2.py --train
```

CSV : `v5_phase2_training_preflight.csv`
