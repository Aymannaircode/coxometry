# V5 Phase 1 — Pre-flight IT-only

**Généré :** 2026-08-29 01:07 UTC
**Mode :** PRE-FLIGHT — aucun entraînement, aucun `optimizer.step()`
**Checkpoint Phase 0 :** `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_surgical_init.pt`
**Verdict :** `V5_PHASE1_READY`

---

## Contexte Phase 0

| Métrique | V2 | V5 epoch-0 | Δ |
|----------|-----|------------|---|
| Mean error 14 KP | 128.48 px | 128.48 px | **0.00 px** |

Phase 0 validée (`V5_PHASE0_GO`). Les 14 KP communs sont bit-identiques à V2 au niveau inférence.

---

## 1. Gel des 14 KP (canaux plats 0–41)

### Mapping flat → keypoint

```
flat = kp_index × 3 + dim   (dim: 0=x, 1=y, 2=v)
KP 0–13 (TD_R … FSD_L) → canaux plats 0–41
IT_R (index 14) → 42, 43, 44
IT_L (index 15) → 45, 46, 47
```

### Limitation API Ultralytics

| Mécanisme | Effet | Suffisant Phase 1 ? |
|-----------|-------|:-------------------:|
| `freeze=22` | Gèle backbone (layers 0–22) | Partiel — cv2/cv3/cv4 restent trainables |
| `freeze=23` | Gèle toute la tête Pose | **Non** — gèle aussi IT |
| Gel par canal cv4 | Masque gradient sur lignes/colonnes 0:42 | **Oui — requis** |

### Tensors cv4 gelables (×3 échelles P3/P4/P5)

| Tensor | Shape (ex. P3) | Zone gelée (14 KP) | Zone entraînable (IT) |
|--------|----------------|--------------------|-----------------------|
| `model.23.cv4.0.0.conv.weight` | (48, C_in, 3, 3) | rows 0:42 ALL | rows 42:48 ALL |
| `model.23.cv4.0.0.bn.weight/bias/running_*` | (48,) | [0:42] | [42:48] |
| `model.23.cv4.0.1.conv.weight` | (48, 48, 3, 3) | block [0:42,:] and [:,0:42] | block [42:48,42:48] ONLY |
| `model.23.cv4.0.1.bn.*` | (48,) | [0:42] | [42:48] |
| `model.23.cv4.0.2.weight` | (48, 48, 1, 1) | rows 0:42 ALL; cols 0:42 for rows 42:48 | block [42:48,42:48] |
| `model.23.cv4.0.2.bias` | (48,) | [0:42] | [42:48] |
| … | × échelles 1, 2 | idem | idem |

**Total cv4 :** 36 tensors · **499** tensors non-cv4 (backbone + cv2 + cv3) → `requires_grad=False` intégral.

### Stratégie double (obligatoire)

1. **`requires_grad=False`** sur backbone (0–22), `cv2`, `cv3`, `dfl`, et **tout cv4**.
2. **Réactivation IT-only** : `requires_grad=True` sur cv4 + **hooks de masquage** zeroing gradients hors bloc `[42:48, 42:48]` (conv1/conv2/final) et rows `[42:48]` (conv0, bias, BN).

Sans masque gradient, la loss stock Ultralytics sur les 14 KP (v=2) produirait des gradients sur les canaux 0–41 même si `requires_grad=False` sur ces slices — d'où le hook.

---

## 2. IT-only — paramètres entraînables

| Keypoint | Index KP | Canaux plats | Statut |
|----------|:--------:|:------------:|--------|
| IT_R | **14** | 42, 43, 44 | **Trainable** |
| IT_L | **15** | 45, 46, 47 | **Trainable** |

### Chemin loss → gradients → update

```
batch (640×640) → backbone [FROZEN] → cv4 [PARTIAL]
  → pred_kpts (16, 3) → v8PoseLoss.calculate_keypoints_loss
  → KeypointLoss (position) + BCE (visibility)
  → backward → hooks masquent grad sur canaux 0–41
  → optimizer.step() [Phase 1 training — NON exécuté ici]
```

**Recommandation loss Phase 1 :** masquer en plus la loss aux indices KP **0–13** (Phase 1 script) pour éviter tout signal résiduel vers cv4 ancien via chemins croisés conv1 `W[0:42,42:48]`. Ultralytics natif calcule la loss sur **tous** les KP visibles.

Paramètres cv4 avec hook IT actif : **24**

---

## 3. Test gradient (sans training)

Procédure exécutée :

1. Charger `v5_surgical_init.pt`
2. Appliquer gel + hooks IT
3. Un batch train (`batch=1`, `imgsz=640`)
4. `forward` → `loss` → `backward`
5. Inspection gradients — **pas de `optimizer.step()`**

| Loss totale | 6.475607 |
| Loss items (box, pose, kobj, cls, dfl) | [0.7276060581207275, 3.614544153213501, 0.5008847713470459, 0.31177112460136414, 1.320801019668579] |

### Résultats gradient

| Zone | Gradients non-nuls ? | Attendu |
|------|:--------------------:|:-------:|
| Backbone (0–22) | NON ✓ | NON |
| cv2 (box) | NON ✓ | NON |
| cv3 (cls) | NON ✓ | NON |
| cv4 canaux 0–41 | Bloqués ✓ | Bloqués |
| cv4 canaux 42–47 | Actifs ✓ | Présents |


**Canaux IT avec gradient (échantillon) :**
- `model.23.cv4.2.1.bn.bias` it_max_abs=8.439523e-03
- `model.23.cv4.2.2.bias` it_max_abs=3.125000e-02

---

## 4. Configuration proposée (premier test — non lancé)

| Paramètre | Valeur | Note |
|-----------|--------|------|
| init | `v5_surgical_init.pt` | Phase 0 validée |
| imgsz | **640** | Identique V2 |
| batch | **1** | |
| lr0 | **1e-5** (≤ 1e-5) | AdamW |
| cos_lr | **false** | |
| epochs (premier test) | **15** | Pas 100 directement |
| patience | **8** | Early stop sur métriques pixel IT + parity 14 KP |
| mosaic | **0** | |
| randaugment | **off** (`auto_augment: null`) | |
| erasing | **0** | |
| fliplr | **0.5** | flip_idx 16 KP validé |
| pose / kobj | 12.0 / 1.0 | Identique V2/V4 |

Script préparé (non exécuté) : `annotation_pilot/scripts/train_yolo_pose_v5_phase1.py`
Config : `datasets/yolo_pose_new_26/v5_phase1_training_config.yaml`

---

## 5. v=0 — exclusion loss position

Convention labels (`prepare_yolo_pose_new_26.py`) : `v=0` → `(0, 0, 0)` — **aucune transformation arbitraire**.

Ultralytics `loss.py` :

```python
kpt_mask = gt_kpt[..., 2] != 0   # v=0 exclu de KeypointLoss (position)
kpts_obj_loss = BCE(pred_v, kpt_mask.float())  # v=0 → cible visibility=0
```

### IT v=0 sur train (21 images)

| Comptage | IT_R | IT_L | Total |
|----------|-----:|-----:|------:|
| v=2 (supervision position) | 16 | 19 | 35 |
| v=0 (exclus position) | 5 | 2 | **7** |

**7 landmarks IT v=0** sur train (5× IT_R + 2× IT_L) : position loss = 0, BCE visibility uniquement.

| Image | IT_R v | IT_L v | Position loss IT_R | Position loss IT_L |
|-------|:------:|:------:|:------------------:|:------------------:|
| B26_01 | 2 | 2 | oui | oui |
| B26_02 | 2 | 2 | oui | oui |
| B26_03 | 2 | 2 | oui | oui |
| B26_04 | 2 | 2 | oui | oui |
| B26_05 | 2 | 2 | oui | oui |
| B26_06 | 0 | 2 | non | oui |
| B26_07 | 2 | 2 | oui | oui |
| B26_08 | 2 | 2 | oui | oui |
| B26_09 | 2 | 2 | oui | oui |
| B26_11 | 0 | 2 | non | oui |
| B26_12 | 2 | 2 | oui | oui |
| B26_14 | 0 | 2 | non | oui |
| B26_15 | 0 | 0 | non | non |
| B26_16 | 2 | 2 | oui | oui |
| B26_18 | 2 | 2 | oui | oui |
| B26_19 | 2 | 0 | oui | non |
| B26_21 | 0 | 2 | non | oui |
| B26_22 | 2 | 2 | oui | oui |
| B26_23 | 2 | 2 | oui | oui |
| B26_24 | 2 | 2 | oui | oui |
| B26_25 | 2 | 2 | oui | oui |

---

## 6. Critères de sécurité

### Avant training (epoch 0)

| Critère | Seuil | Phase 0 |
|---------|-------|---------|
| Mean error 14 KP vs V2 | ≤ **150 px** | **128.48 px ✓** |
| Δ mean 14 KP | ≤ **1 px** | **0.00 px ✓** |

### Après epoch 1 (abort si dépassé)

| Critère | Seuil abort | Seuil warning |
|---------|-------------|---------------|
| Mean error 14 KP | **> 200 px** | **> 135 px** (Δ > 7 px vs V2) |
| Ratio vs V2 | **> 1.5×** (192 px) | **> 1.05×** (135 px) |
| Tier CORRECT 14 KP | chute > 20 pts | — |

**Seuil régression acceptable post epoch 1 :** mean 14 KP ≤ **135 px** (≤ 5 % vs baseline 128.48 px).

---

## 7. Checklist pre-flight

- [x] `checkpoint_exists` → True
- [x] `backbone_frozen_no_grad` → True
- [x] `cv2_frozen_no_grad` → True
- [x] `cv3_frozen_no_grad` → True
- [x] `cv4_old_channels_blocked` → True
- [x] `cv4_it_channels_active` → True
- [x] `loss_finite` → True

---

## Conclusion : `V5_PHASE1_READY`

Aucun entraînement lancé. CSV détaillé : `v5_phase1_preflight.csv`
