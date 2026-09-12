# V5 Phase 1 v3 — Pre-flight (surgical checkpoint loading fix)

**Généré :** 2026-08-29 01:50 UTC
**Mode :** PRE-FLIGHT — aucun entraînement, pas de `optimizer.step()`
**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v3.py`
**Verdict :** `V5_PHASE1_V3_READY`

---

## Fix v3 vs v2

| Problème v2 | Correction v3 |
|-------------|---------------|
| `pretrained=False` → init aléatoire YAML | `pretrained=True` — conserve `v5_surgical_init.pt` |
| `YOLO.train()` remplace le modèle | Même chemin `--train`, poids préservés via Ultralytics 8.4.96 |

---

## 1. Parité checkpoint A → D

| Point | Description | backbone/cv2/cv3/dfl/cv4-old OK |
|-------|-------------|:-------------------------------:|
| B_yolo_load | B — après `YOLO(v5_surgical_init.pt)` | **True** |
| C_trainer_created | C — après création Trainer (chemin `--train`) | **True** |
| D_post_setup_train | D — après `trainer._setup_train()` | **True** |

### Détail zones (changed / total, max Δ)

| Checkpoint | Zone | Changed | Total | Max Δ |
|------------|------|--------:|------:|------:|
| B_yolo_load | backbone | 0 | 180 | 0.000000e+00 |
| B_yolo_load | cv2_box | 0 | 156 | 0.000000e+00 |
| B_yolo_load | cv3_cls | 0 | 81 | 0.000000e+00 |
| B_yolo_load | dfl | 0 | 1 | 0.000000e+00 |
| B_yolo_load | cv4_pose | 0 | 36 | 0.000000e+00 |
| B_yolo_load | cv4 old (0–41) | 0 | — | 0.000000e+00 |
| B_yolo_load | cv4 IT (42–47) | 0 | — | 0.000000e+00 |
| C_trainer_created | backbone | 0 | 180 | 0.000000e+00 |
| C_trainer_created | cv2_box | 0 | 156 | 0.000000e+00 |
| C_trainer_created | cv3_cls | 0 | 81 | 0.000000e+00 |
| C_trainer_created | dfl | 0 | 1 | 0.000000e+00 |
| C_trainer_created | cv4_pose | 0 | 36 | 0.000000e+00 |
| C_trainer_created | cv4 old (0–41) | 0 | — | 0.000000e+00 |
| C_trainer_created | cv4 IT (42–47) | 0 | — | 0.000000e+00 |
| D_post_setup_train | backbone | 0 | 180 | 0.000000e+00 |
| D_post_setup_train | cv2_box | 0 | 156 | 0.000000e+00 |
| D_post_setup_train | cv3_cls | 0 | 81 | 0.000000e+00 |
| D_post_setup_train | dfl | 0 | 1 | 0.000000e+00 |
| D_post_setup_train | cv4_pose | 0 | 36 | 0.000000e+00 |
| D_post_setup_train | cv4 old (0–41) | 0 | — | 0.000000e+00 |
| D_post_setup_train | cv4 IT (42–47) | 0 | — | 0.000000e+00 |

---

## 2. Freeze après `_setup_train()` (D)

| Zone | Trainable | Attendu |
|------|----------:|:-------:|
| Backbone | 0 | 0 |
| cv2 | 0 | 0 |
| cv3 | 0 | 0 |
| DFL | 0 | 0 |
| cv4 (hooks IT) | 24 | 24 |

---

## 3. Optimizer (IT-only)

Paramètres entraînables : **24**

| Zone | Count |
|------|------:|
| cv4_it | 24 |

---

## 4. Gradients (backward sans step)

| Zone | Tensors grad | Attendu |
|------|:------------:|:-------:|
| Backbone | 0 | 0 |
| cv2 | 0 | 0 |
| cv3 | 0 | 0 |
| DFL | 0 | 0 |
| cv4 old | 0 | 0 |
| cv4 IT | 2 | >0 |

box/cls/dfl loss : 0.0000 / 0.0000 / 0.0000

---

## 5. Inférence pré-training (5 images val, imgsz=640, conf=0.25)

| Modèle | Détections / 5 |
|--------|:--------------:|
| V2 best | 5/5 |
| v5_surgical_init | 5/5 |
| trainer.model (D) | 5/5 |

| Image | V2 | surgical | trainer | trainer ≡ surgical |
|-------|---:|---------:|--------:|:------------------:|
| B26_10 | 1 | 1 | 1 | True |
| B26_13 | 1 | 1 | 1 | True |
| B26_17 | 1 | 1 | 1 | True |
| B26_20 | 1 | 1 | 1 | True |
| B26_26 | 1 | 1 | 1 | True |

---

## Checklist

- [x] `checkpoint_A_exists` → True
- [x] `pretrained_true_in_kwargs` → True
- [x] `B_yolo_load_frozen_ok` → True
- [x] `C_trainer_created_frozen_ok` → True
- [x] `D_post_setup_frozen_ok` → True
- [x] `checkpoint_loading_critical` → True
- [x] `backbone_trainable_0` → True
- [x] `cv2_trainable_0` → True
- [x] `cv3_trainable_0` → True
- [x] `dfl_trainable_0` → True
- [x] `cv4_it_trainable_24` → True
- [x] `optimizer_it_only_24` → True
- [x] `optimizer_no_backbone` → True
- [x] `optimizer_no_cv2` → True
- [x] `optimizer_no_cv3` → True
- [x] `optimizer_no_dfl` → True
- [x] `backbone_grad_0` → True
- [x] `cv2_grad_0` → True
- [x] `cv3_grad_0` → True
- [x] `dfl_grad_0` → True
- [x] `cv4_old_grad_0` → True
- [x] `cv4_it_grad_active` → True
- [x] `det_loss_zero` → True
- [x] `inference_5_of_5` → True
- [x] `no_optimizer_step` → True

---

## Conclusion : `V5_PHASE1_V3_READY`

CSV : `v5_phase1_v3_preflight.csv`

Pour entraîner (après READY) :
```
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v5_phase1_v3.py --train
```
