# V5 Phase 1 v2 — Fix `initial_lr` (dry-run train setup)

**Généré :** 2026-08-29 01:35 UTC
**Mode :** DRY-RUN — `_setup_train()` + gradient probe, pas d'epoch, pas de `optimizer.step()`
**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v2.py`
**Verdict :** `V5_PHASE1_V2_INITIAL_LR_FIXED`

---

## Cause

`rebuild_optimizer_trainable_only()` remplaçait l'optimizer sans recréer le scheduler.
Ultralytics `_do_train()` warmup lit `param_group['initial_lr']`, défini par `LambdaLR`
dans `_setup_scheduler()` — d'où le `KeyError: 'initial_lr'`.

## Correction

1. Param groups reconstruits comme `build_optimizer()` (weight / bn / bias, clé `param_group`)
2. Appel `trainer._setup_scheduler()` après rebuild → `initial_lr` injecté par PyTorch `LambdaLR`

---

## Optimizer param groups (post `_setup_train`)

| Index | param_group | n_params | lr | initial_lr | weight_decay |
|------:|:-----------:|---------:|---:|-----------:|-------------:|
| 0 | weight | 9 | 1.00e-05 | 1.00e-05 | 5.00e-04 |
| 1 | bn | 6 | 1.00e-05 | 1.00e-05 | 0.00e+00 |
| 2 | bias | 9 | 1.00e-05 | 1.00e-05 | 0.00e+00 |

---

## Warmup LR path (simulation `_do_train`, ni=0)

- nb batches : 21
- nw warmup iters : 100
- LR calculés : ['0.00e+00', '0.00e+00', '1.00e-02']

---

## IT-only / freeze (backward sans step)

| IT trainable params | 24 |
| cv4 IT grad tensors | 8 |
| cv4 old grad tensors | 0 |
| box / cls / dfl loss | 0.0000 / 0.0000 / 0.0000 |

---

## Checklist

- [x] `trainer_created` → True
- [x] `setup_train_completed` → True
- [x] `all_param_groups_have_initial_lr` → True
- [x] `initial_lr_matches_lr0` → True
- [x] `warmup_lr_path_ok` → True
- [x] `optimizer_trainable_param_count` → True
- [x] `freeze_applied` → True
- [x] `cv4_it_grad_active` → True
- [x] `cv4_old_grad_zero` → True
- [x] `backbone_grad_zero` → True
- [x] `det_loss_zero` → True
- [x] `old_kp_loss_zero` → True
- [x] `no_optimizer_step` → True
- [x] `no_epoch_started` → True

---

## Conclusion : `V5_PHASE1_V2_INITIAL_LR_FIXED`

CSV : `v5_phase1_v2_initial_lr_fix.csv`
