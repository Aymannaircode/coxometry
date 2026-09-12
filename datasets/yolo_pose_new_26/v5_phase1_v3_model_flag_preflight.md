# V5 Phase 1 v3 — `--model` flag pre-flight

**Généré :** 2026-08-29 01:58 UTC
**Mode :** DRY-RUN — aucun `--train`, pas de `optimizer.step()`
**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v3.py`
**Checkpoint testé :** `runs\pose\yolo_pose_new_26_v5_phase1_it_v3\weights\best.pt`
**Verdict :** `V5_PHASE1_V3_MODEL_FLAG_READY`

---

## Comportement `--model`

| Cas | model= | pretrained | resume |
|-----|--------|:----------:|:------:|
| `--model` fourni | chemin explicite | **True** | **False** |
| défaut (sans --model) | `v5_surgical_init.pt` | **True** | **False** |

---

## Vérifications post `_setup_train()`

| # | Check | Résultat | Attendu |
|--:|-------|:--------:|:-------:|
| 1 | Checkpoint chargé = epoch-1 best | True | True |
| 2 | Poids IT ≠ surgical_init | True | True |
| 3 | Poids gelés ≡ surgical_init | True | True |
| 4 | Freeze OK (0/0/0/0 + 24 IT) | True | True |
| 5 | Optimizer 24 params IT | True | True |
| 6 | Loss IT-only (box/cls/dfl=0) | True | True |
| 7 | EMA restreinte | True | True |
| 8 | resume=False | True | True |
| 9 | epochs=15 | True | True |

### Détail poids

| Comparaison | frozen OK | cv4 old Δ | cv4 IT Δ | cv4 IT max |
|-------------|:---------:|:---------:|:--------:|-----------:|
| trainer vs epoch-1 file | True | 0 | 0 | 0.000000e+00 |
| trainer vs surgical_init | True | 0 | 5 | 2.848816e-02 |

### Freeze / optimizer / loss

| Zone | Trainable | Optimizer count |
|------|----------:|----------------:|
| backbone | 0 | 0 |
| cv2 | 0 | 0 |
| cv3 | 0 | 0 |
| dfl | 0 | 0 |
| cv4 IT | 24 | 24 |

Criterion : **Phase1ITOnlyPoseLoss** — box/cls/dfl = 0.0/0.0/0.0
EMA mode : **ema_restricted_trainable**

---

## Checklist complète

- [x] `model_path_resolved` → True
- [x] `checkpoint_is_epoch1_best` → True
- [x] `loaded_matches_epoch1_best_weights` → True
- [x] `it_weights_differ_from_surgical` → True
- [x] `frozen_zones_match_surgical_init` → True
- [x] `pretrained_true` → True
- [x] `resume_false` → True
- [x] `epochs_configurable` → True
- [x] `freeze_backbone_0` → True
- [x] `freeze_cv2_0` → True
- [x] `freeze_cv3_0` → True
- [x] `freeze_dfl_0` → True
- [x] `freeze_cv4_it_24` → True
- [x] `optimizer_it_only_24` → True
- [x] `optimizer_no_backbone` → True
- [x] `criterion_it_only` → True
- [x] `det_loss_zero` → True
- [x] `cv4_it_grad_active` → True
- [x] `cv4_old_grad_zero` → True
- [x] `ema_restricted` → True
- [x] `custom_trainer_active` → True

---

## Conclusion : `V5_PHASE1_V3_MODEL_FLAG_READY`

Commande continuation (après READY, explicite `--train`) :
```powershell
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v5_phase1_v3.py ^
  --train --epochs 15 --model runs\pose\yolo_pose_new_26_v5_phase1_it_v3\weights\best.pt
```

CSV : `v5_phase1_v3_model_flag_preflight.csv`
