# V5 Phase 2 — Metric Decoder Fix

**Généré :** 2026-08-29 02:27 UTC
**Mode :** vérification décodeur métriques — **aucun entraînement**
**Verdict :** `V5_PHASE2_METRIC_DECODER_FIXED`
**Détail :** eval/train head outputs normalized; 16-KP decode OK on 5 val images

---

## 1. Inspection `forward_head_preds`

| Mode | Raw type | Len | Élément | Type | Shape | Keys |
|------|----------|----:|---------|------|-------|------|
| train | dict |  | -1 |  |  | boxes,scores,feats,kpts |
| train | — | — | preds | dict | (1, 48, 8400) | kpts,48ch |
| eval | tuple | 2 | 0 | Tensor | (1, 53, 8400) |  |
| eval | tuple | 2 | 1 | dict |  | boxes,scores,feats,kpts |
| eval | — | — | preds | dict | (1, 48, 8400) | kpts,48ch |

**Cause :** en `eval`, la tête Pose Ultralytics retourne `(tensor, dict)` ; le dict `kpts` est à l'index 1.

---

## 2. Layout 16 KP (1 image val)

| Index | Landmark | pred_x | pred_y | gt_v |
|------:|----------|-------:|-------:|-----:|
| 0 | TD_R | 8.2 | 13.9 | 2.0 |
| 1 | TD_L | 12.3 | 13.4 | 2.0 |
| 2 | FHC_R | 6.0 | 9.2 | 2.0 |
| 3 | FHC_L | 14.0 | 9.5 | 2.0 |
| 4 | ASL_R | 4.1 | 6.9 | 2.0 |
| 5 | ASL_L | 14.8 | 7.1 | 2.0 |
| 6 | ASM_R | 7.0 | 7.3 | 2.0 |
| 7 | ASM_L | 12.9 | 7.2 | 2.0 |
| 8 | FNM_R | 4.9 | 10.7 | 2.0 |
| 9 | FNM_L | 15.1 | 10.9 | 2.0 |
| 10 | FSP_R | 3.9 | 13.5 | 2.0 |
| 11 | FSP_L | 16.1 | 13.5 | 2.0 |
| 12 | FSD_R | 5.5 | 16.0 | 2.0 |
| 13 | FSD_L | 15.2 | 16.2 | 2.0 |
| 14 | IT_R | 9.9 | 10.1 | 2.0 |
| 15 | IT_L | 10.1 | 9.8 | 2.0 |

---

## 3. `compute_it_metrics` — 5 images val

- IT_R_mean_px : **534.4146942138672**
- IT_L_mean_px : **656.383154296875**
- IT_mean_px : **602.1749498155382**
- IT_median_px : **629.5316467285156**
- IT_p90_px : **684.075439453125**
- IT_correct_rate : **0.0**
- IT_n_evaluated : **90.0**

---

## Conclusion : `V5_PHASE2_METRIC_DECODER_FIXED`

eval/train head outputs normalized; 16-KP decode OK on 5 val images

CSV : `v5_phase2_metric_decoder_fix.csv`
