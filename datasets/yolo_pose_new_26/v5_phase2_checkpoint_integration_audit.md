# V5 Phase 2 — Checkpoint Integration Audit

**Généré :** 2026-09-02 00:05 UTC
**Mode :** READ-ONLY — aucun training, aucune modification checkpoint/label/YAML/backend/Flutter
**Checkpoint :** `runs\pose\yolo_pose_new_26_v5_phase2\run_20260829_032756\weights\best_it.pt`
**Verdict :** `CHECKPOINT_INFERENCE_READY`

---

## 1. Chargement (processus Python neuf)

- Chargement **OK** sans état mémoire d'entraînement
- Clés checkpoint top-level : `best_fitness, date, docs, ema, epoch, git, license, model, optimizer, scaler, train_args, train_metrics, train_results, updates, v5_meta, v5_phase2, version`
- `v5_phase2.wrapper_state` : 1148 tenseurs
- Instanciation via `build_model()` + `load_state_dict(wrapper_state)` + `attach_hyp()`

### Dépendances custom

| Fichier | Rôle |
|---------|------|
| `train_yolo_pose_v5_phase2.py` | build_model, V5Phase2DedicatedModel, decode |
| `v5_phase2_dedicated_head_dryrun.py` | ITHeadMultiScaleFusion |
| `train_yolo_pose_v5_phase1.py` | ITOnlyPoseLoss |
| `v5_surgical_init.pt` | base gelée (requis par build_model) |
| `v5_phase2_training_config.yaml` | config architecture |
| `dicom_render.py` | rendu DICOM |
| `ultralytics` | pose head, kpts_decode, YOLO.predict |

---

## 2. Architecture

| Composant | Attendu | Observé | OK |
|-----------|---------|---------|:--:|
| Backbone | gelé | changed=0 | ✓ |
| Neck | gelé | changed=0 | ✓ |
| cv4 (14 KP) | gelé | changed=0 | ✓ |
| IT head | ITHeadMultiScaleFusion | ITHeadMultiScaleFusion | ✓ |
| IT_R | index 14, ch 42-44 | confirmé | ✓ |
| IT_L | index 15, ch 45-47 | confirmé | ✓ |
| Sortie | 16 KP × 3 = 48 ch | (1, 48, 8400) | ✓ |


---

## 3. Inférence (5 images val)

| Image | Det | Anchor | Conf | IT_R err | IT_L err | infer_ms |
|-------|----:|-------:|-----:|---------:|---------:|---------:|
| B26_10 | 1 | 8269 | 0.891736 | 24.6 | 26.8 | 176.3 |
| B26_13 | 1 | 8250 | 0.875427 | 30.6 | 29.4 | 164.1 |
| B26_17 | 1 | 8269 | 0.885234 | 16.2 | 21.7 | 123.3 |
| B26_20 | 1 | 8231 | 0.921167 | 39.7 | 17.7 | 127.3 |
| B26_26 | 1 | 8248 | 0.860271 | NA (v=0) | 24.4 | 130.1 |

### Coordonnées IT (px640 / origine)

| Image | Landmark | GT px640 | Pred px640 | Orig px | Orig py | err px | v GT | v pred |
|-------|----------|----------|------------|--------:|--------:|-------:|-----:|-------:|
| B26_10 | IT_R | (173.1,518.7) | (148.6,518.0) | 163.7 | 1721.5 | 24.6 | 2 | 1.01 |
| B26_10 | IT_L | (415.9,508.6) | (436.8,491.7) | 481.4 | 1634.8 | 26.8 | 2 | 1.44 |
| B26_13 | IT_R | (176.5,490.5) | (151.5,472.9) | 166.8 | 1627.5 | 30.6 | 2 | 0.64 |
| B26_13 | IT_L | (429.1,480.6) | (430.2,451.2) | 473.9 | 1554.8 | 29.4 | 2 | 0.66 |
| B26_17 | IT_R | (120.0,544.6) | (129.4,557.8) | 142.5 | 1806.5 | 16.2 | 2 | 0.88 |
| B26_17 | IT_L | (421.6,536.5) | (439.5,548.6) | 483.6 | 1776.5 | 21.7 | 2 | 1.88 |
| B26_20 | IT_R | (163.0,545.5) | (144.0,580.2) | 158.6 | 1808.3 | 39.7 | 2 | 1.32 |
| B26_20 | IT_L | (447.4,540.7) | (464.7,544.2) | 511.5 | 1790.6 | 17.7 | 2 | 0.91 |
| B26_26 | IT_R | — | — | — | — | NA | 0 | 0.44 |
| B26_26 | IT_L | (453.1,497.8) | (431.7,509.5) | 475.4 | 1650.8 | 24.4 | 2 | 1.83 |

**IT_mean (v=2) :** 25.67 px — 9/9 < 75 px

## 4. Comparaison V2 vs V5 Phase2

### Détection

| Image | V2 n | V2 conf | V2 IoU | P2 n | P2 conf | P2 IoU | Identique |
|-------|-----:|--------:|-------:|-----:|--------:|-------:|:---------:|
| B26_10 | 1 | 0.891736 | 0.9304567971752552 | 1 | 0.891736 | 0.9304567971752552 | ✓ |
| B26_13 | 1 | 0.875427 | 0.8892124377628038 | 1 | 0.875427 | 0.8892124377628038 | ✓ |
| B26_17 | 1 | 0.885234 | 0.9080565978081454 | 1 | 0.885234 | 0.9080565978081454 | ✓ |
| B26_20 | 1 | 0.921167 | 0.8931882797269804 | 1 | 0.921167 | 0.8931882797269804 | ✓ |
| B26_26 | 1 | 0.860271 | 0.7482001924791625 | 1 | 0.860271 | 0.7482001924791625 | ✓ |

**14 KP (0–13) identiques V2 :** True (70/70 paires, tolérance 1e-5 ; seul artefact float B26_26 FNM_R dx=1e-6)


---

## 5. Décodage

```
raw logits → kpts_decode(anchor_points) → grid units
grid × stride[anchor] → px640 (letterbox)
px640 × (orig_w/640, orig_h/640) → pixels originaux
```

Exemple B26_10 IT_R: raw=(4.6425,16.1891) stride=32.0 px640=(148.56,518.05) err=24.56px
- single_stride_ok: **True**
- Pas de double scaling: **True**


---

## 6. Robustesse

| Cas | Résultat |
| Images normales | 9/9 IT < 75 px |
| B26_26 IT_R v=0 | OK — pas d erreur positionnelle |
| Pas de coord inventée | OK |


---

## 7. Performance

- Moyenne: **144.2 ms**
- Min/Max: 123.3 / 176.3 ms
- RSS: **583 MB**


---

## 8. Dépendances pour inférence autonome

Le checkpoint `best_it.pt` **ne se charge pas** via `YOLO(path)` seul. Procédure:

1. `build_model(cfg)` — instancie base chirurgicale + ITHeadMultiScaleFusion
2. `model.load_state_dict(ckpt['v5_phase2']['wrapper_state'])`
3. `attach_hyp(model.base)`
4. `model.forward_head_preds(img)` pour 16 KP
5. Option YOLO: `export_phase2_for_predict(model, shell.pt)` puis `YOLO(shell).predict()` (14 KP via shell)

---

## 9. Conclusion

### `CHECKPOINT_INFERENCE_READY`

- IT_mean = **25.67 px**, 100% < 75 px (9 landmarks v=2)
- Détection identique V2 (boxes, conf, IoU)
- 14 KP identiques V2 (coords normalisées YOLO.predict, ε ≤ 1e-5)
- IT_R (index 14) et IT_L (index 15) disponibles via `forward_head_preds` + decode grid×stride
- Freeze backbone/neck/cv4 confirmé — seul `it_head` modifié
- Décodage correct (single stride, pas de double scaling)
- B26_26 IT_R v=0 : pas d'erreur positionnelle inventée
- Chargeable en processus Python neuf via `wrapper_state` (sans état optimizer/EMA)

**Réserve d'intégration :** `best_it.pt` ne se charge pas via `YOLO(path)` seul. Inférence 16 KP requiert `build_model()` + `load_state_dict()` + `attach_hyp()` (ou export shell via `export_phase2_for_predict`). Ce n'est pas un blocage fonctionnel — c'est le contrat d'intégration documenté.

CSV : `datasets\yolo_pose_new_26\v5_phase2_checkpoint_integration_audit.csv`