# V5 Phase 1 v2 — Freeze Lifecycle Diagnostic

**Généré :** 2026-08-29 01:47 UTC
**Mode :** READ-ONLY — pas de `--train`, copie `v5_phase1_freeze_lifecycle_work.pt`
**Script :** `annotation_pilot/scripts/v5_phase1_freeze_lifecycle_debug.py`
**Verdict :** `V5_FREEZE_BREAKPOINT_IDENTIFIED`
**Breakpoint :** `T0_pretrained_false_discards_surgical_init`

---

## Breakpoint identifié

**`T0_pretrained_false_discards_surgical_init`** — avant le premier batch (T0/T0b), pas pendant `optimizer.step()`.

`pretrained=False` (config V5) provoque :

1. `BaseTrainer.setup_model()` : charge le `.pt` puis `weights = None` (trainer.py L769-770)
2. `YOLO.train()` : `get_model(weights=None, cfg=yaml)` (model.py L808-813)

Résultat T0b : **453/454** tensors ≠ `v5_surgical_init.pt` (max Δ 10.23).

---

## Snapshots T0–T10

| CP | Zone | train | frozen | grad≠0 | hash≠T5 |
|----|------|------:|-------:|-------:|--------:|
| T0b | BACKBONE | 108 | 0 | 0 | 0 |
| T0b | CV2 | 96 | 0 | 0 | 0 |
| T0b | CV3 | 51 | 0 | 0 | 0 |
| T0b | DFL | 0 | 1 | 0 | 0 |
| T0b | CV4_IT | 24 | 0 | 0 | 0 |
| T2 | BACKBONE | 0 | 108 | 0 | 0 |
| T2 | CV2 | 0 | 96 | 0 | 0 |
| T2 | CV3 | 0 | 51 | 0 | 0 |
| T2 | DFL | 0 | 1 | 0 | 0 |
| T2 | CV4_IT | 24 | 0 | 0 | 0 |
| T3 | BACKBONE | 0 | 108 | 0 | 0 |
| T3 | CV2 | 0 | 96 | 0 | 0 |
| T3 | CV3 | 0 | 51 | 0 | 0 |
| T3 | DFL | 0 | 1 | 0 | 0 |
| T3 | CV4_IT | 24 | 0 | 0 | 0 |
| T4 | BACKBONE | 0 | 108 | 0 | 0 |
| T4 | CV2 | 0 | 96 | 0 | 0 |
| T4 | CV3 | 0 | 51 | 0 | 0 |
| T4 | DFL | 0 | 1 | 0 | 0 |
| T4 | CV4_IT | 24 | 0 | 0 | 0 |
| T5 | BACKBONE | 0 | 108 | 0 | 0 |
| T5 | CV2 | 0 | 96 | 0 | 0 |
| T5 | CV3 | 0 | 51 | 0 | 0 |
| T5 | DFL | 0 | 1 | 0 | 0 |
| T5 | CV4_IT | 24 | 0 | 0 | 0 |
| T6 | BACKBONE | 0 | 108 | 0 | 0 |
| T6 | CV2 | 0 | 96 | 0 | 0 |
| T6 | CV3 | 0 | 51 | 0 | 0 |
| T6 | DFL | 0 | 1 | 0 | 0 |
| T6 | CV4_IT | 24 | 0 | 8 | 0 |
| T7 | BACKBONE | 0 | 108 | 0 | 0 |
| T7 | CV2 | 0 | 96 | 0 | 0 |
| T7 | CV3 | 0 | 51 | 0 | 0 |
| T7 | DFL | 0 | 1 | 0 | 0 |
| T7 | CV4_IT | 24 | 0 | 8 | 0 |
| T8 | BACKBONE | 0 | 108 | 0 | 0 |
| T8 | CV2 | 0 | 96 | 0 | 0 |
| T8 | CV3 | 0 | 51 | 0 | 0 |
| T8 | DFL | 0 | 1 | 0 | 0 |
| T8 | CV4_IT | 24 | 0 | 0 | 8 |
| T9 | BACKBONE | 0 | 108 | 0 | 0 |
| T9 | CV2 | 0 | 96 | 0 | 0 |
| T9 | CV3 | 0 | 51 | 0 | 0 |
| T9 | DFL | 0 | 1 | 0 | 0 |
| T9 | CV4_IT | 24 | 0 | 0 | 8 |
| T10 | BACKBONE | 0 | 108 | 0 | 0 |
| T10 | CV2 | 0 | 96 | 0 | 0 |
| T10 | CV3 | 0 | 51 | 0 | 0 |
| T10 | DFL | 0 | 1 | 0 | 0 |
| T10 | CV4_IT | 24 | 0 | 0 | 8 |

---

## Optimizer (T4/T5)

Paramètres : **24** (attendu 24 cv4 IT uniquement)

| Zone | Count |
|------|------:|
| BACKBONE | 0 |
| CV2 | 0 |
| CV3 | 0 |
| CV4_IT | 24 |
| CV4_OLD | 0 |
| DFL | 0 |
| OTHER | 0 |

---

## Δ T5 → T8 (1 step, LR forcé)

| Zone | changed/total | max Δ |
|------|:-------------:|------:|
| backbone | 0/108 | 0.000000e+00 |
| cv2_box | 0/96 | 0.000000e+00 |
| cv3_cls | 0/51 | 0.000000e+00 |
| cv4_pose | 8/24 | 1.001358e-05 |
| dfl | 0/1 | 0.000000e+00 |

cv4 old: 0 | cv4 IT: 8

---

## Δ T5 → fin epoch simulée (21 batches)

**epoch_frozen_ok:** True

| Zone | changed/total |
|------|:-------------:|
| backbone | 0/108 |
| cv2_box | 0/96 |
| cv3_cls | 0/51 |
| cv4_pose | 0/24 |
| dfl | 0/1 |

---

## Gradients T6

| Métrique | Valeur |
|----------|-------:|
| backbone_grad | 0 |
| cv2_grad | 0 |
| cv3_grad | 0 |
| cv4_old_grad | 0 |
| cv4_it_grad | 8 |
| cv4_trainable_hooks | 24 |
| dfl_grad | 0 |

---

## EMA / save / callbacks

- EMA mode: `ema_restricted_trainable`
- EMA drift zones gelées: `{'BACKBONE': 0, 'CV2': 0, 'CV3': 0, 'DFL': 0, 'CV4_OLD': 0, 'CV4_IT': 0}`
- save_model live mutation: `none`
- Callbacks actifs: 34 (aucun ne reset `requires_grad`)

---

## Findings

1. T0b BREAKPOINT: `YOLO.train(pretrained=False)` + `setup_model(pretrained=False)` ignore v5_surgical_init.pt → init aléatoire YAML (453+ tensors ≠ surgical_init).
2. T2–T5: freeze IT-only OK — requires_grad 24 cv4 hooks, optimizer 24 params, backbone/cv2/cv3/dfl gelés.
3. T8: optimizer.step OK — seul cv4 IT modifié (1 batch, LR forcé).
4. T5→epoch_end (21 batches, warmup): zones gelées inchangées — le gel survive à `_do_train()` quand on mesure Δ vs T5 (pas vs surgical_init).
5. T10: save_model ne mute pas le modèle live (EMA sérialisé séparément).
6. Safety audit B→C: 100% tensors ≠ surgical_init car le run n'a jamais chargé surgical_init (pretrained=False), PAS parce que le gel est perdu pendant la boucle.

---

## Conclusion : `V5_FREEZE_BREAKPOINT_IDENTIFIED`

CSV : `v5_phase1_freeze_lifecycle_diagnostic.csv`
