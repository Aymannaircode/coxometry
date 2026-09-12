# V5 Phase 1 — Loss Mask Check (IT-only)

**Généré :** 2026-08-29 01:12 UTC
**Mode :** READ-ONLY — aucun entraînement, aucun `optimizer.step()`
**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1.py`
**Verdict :** `V5_PHASE1_LOSS_MASK_READY`

---

## Implémentation

Classe `ITOnlyPoseLoss` : masque `kpt_mask` aux indices **14, 15** avant loss position et BCE visibility.
Normalisation IT-only : moyenne sur KP IT visibles (évite le facteur Ultralytics `16/n_visible`).

```python
it_mask = zeros(16); it_mask[14] = it_mask[15] = True
kpt_mask = (gt_v != 0) & it_mask   # exclut v=0 ET KP 0-13
kpts_loss = sum(loss_per * kpt_mask) / kpt_mask.sum()
```

---

## 1. Loss pose totale (batch réel, batch=1, imgsz=640)

| Métrique | Stock (16 KP) | Masqué IT-only |
|----------|--------------:|---------------:|
| Position (pose gain déjà inclus) | 4.523940 | **11.908966** |
| Visibility (kobj gain déjà inclus) | 0.499074 | **0.693147** |

---

## 2–4. Contributions par zone

| Zone | Position loss weighted |
|------|----------------------:|
| KP 0–13 (stock diagnostic) | 48.565115 |
| KP 0–13 (effective masked) | **0.000000** |
| Old-KP direct loss (IT fn, mask 0–13) | **0.000000** |
| IT_R (index 14) | **11.976688** |
| IT_L (index 15) | **11.841245** |
| Somme IT (per-KP isolé) | 23.817934 |
| Moyenne IT (loss masquée) | **11.908967** |
| IT dans loss stock | 23.817934 |

Avec masque actif : contribution **effective** KP 0–13 = **0** (exclues de `calculate_keypoints_loss`).

---

## 5. Comportement v=0 (batch B26_06 ou équivalent)

| Landmark | gt_visible | position_loss_raw |
|----------|:----------:|------------------:|
| IT_R | False | 0.000000 |
| IT_L | False | 0.000000 |

---

## 6–7. Gradients + hooks cv4 (backward, sans step)

| Zone | Tensors avec grad | Attendu |
|------|:-----------------:|:-------:|
| Backbone | 0 | 0 |
| cv2 | 0 | 0 |
| cv3 | 0 | 0 |
| cv4 canaux 0–41 | 0 | 0 |
| cv4 canaux 42–47 | 2 | >0 |
| cv4 hooks actifs | 24 | 24 |

---

## Checklist

- [x] `loss_mask_implemented` → True
- [x] `old_kp_direct_loss_zero` → True
- [x] `masked_pose_lte_stock_total` → True
- [x] `it_r_contributes_when_visible` → True
- [x] `it_l_contributes_when_visible` → True
- [x] `masked_matches_it_mean` → True
- [x] `v0_it_no_position` → True
- [x] `backbone_no_grad` → True
- [x] `cv2_cv3_no_grad` → True
- [x] `cv4_old_blocked` → True
- [x] `cv4_it_active` → True
- [x] `no_optimizer_step` → True

---

## Conclusion : `V5_PHASE1_LOSS_MASK_READY`

CSV : `v5_phase1_loss_mask_check.csv`
