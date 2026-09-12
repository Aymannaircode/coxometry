# V5 Phase 2 — IT Metric Decoder Fix QA

**Généré :** 2026-08-29 03:02 UTC
**Mode :** READ-ONLY eval — aucun training
**Verdict :** `METRIC_DECODER_FIXED`

## Correction

- Fichier : `annotation_pilot/scripts/train_yolo_pose_v5_phase2.py`
- Fonction : `_decode_it_errors()`
- Ajout : `pred_dec[..., :2] *= stride_tensor.view(1, -1, 1, 1)` après `kpts_decode`

## Nouvelles métriques

| Métrique | Valeur |
|----------|-------:|
| IT_R_mean_px | **23.77** |
| IT_L_mean_px | **25.39** |
| IT_mean_px | **24.67** |
| IT_median_px | **23.83** |
| IT_p90_px | **37.98** |
| correct <75 px | **100.0%** |
| correct <150 px | **100.0%** |
| IT_correct_rate (<50 px) | **100.0%** |
| N évalué compute_it_metrics | **90** |
| Landmarks v=2 (1er anchor FG) | **9** |

## Comparaison ancienne vs nouvelle métrique

- IT_mean_px ancienne (bug grid vs px640) : **~604.32 px**
- IT_mean_px nouvelle : **24.67 px**
- Réduction : **579.65 px**

## Vérifications

- Landmarks v=2 (1er anchor FG/image) : **True**
- compute_it_metrics évaluations : **90** (tous anchors FG)
- Loss code modifié : **False** (loss sample = 2.9589)
- Double scaling détecté : **False**

## Cas manuels

| Image | KP | grid | px640 | GT | err old | err new |
|-------|-----|------|-------|-----|--------:|--------:|
| B26_13 | IT_R | (5.32,14.20) | (170.2,454.5) | (176.5,490.5) | 506.1 | 36.5 |
| B26_17 | IT_R | (3.99,17.55) | (127.6,561.6) | (120.0,544.6) | 539.7 | 18.6 |
| B26_20 | IT_R | (4.72,17.80) | (150.9,569.7) | (163.0,545.5) | 550.9 | 27.1 |
| B26_26 | IT_L | (13.75,15.68) | (440.1,501.9) | (453.1,497.8) | 652.3 | 13.6 |
| B26_10 | IT_R | (5.18,15.24) | (165.9,487.7) | (173.1,518.7) | 530.7 | 31.8 |

### Tous les landmarks v=2

| Image | KP | err old | err new |
|-------|-----|--------:|--------:|
| B26_13 | IT_R | 506.1 | 36.5 |
| B26_13 | IT_L | 625.1 | 42.9 |
| B26_17 | IT_R | 539.7 | 18.6 |
| B26_17 | IT_L | 660.5 | 14.9 |
| B26_20 | IT_R | 550.9 | 27.1 |
| B26_20 | IT_L | 679.0 | 26.3 |
| B26_26 | IT_L | 652.3 | 13.6 |
| B26_10 | IT_R | 530.7 | 31.8 |
| B26_10 | IT_L | 636.7 | 35.8 |

## Conclusion : `METRIC_DECODER_FIXED`

CSV : `datasets/yolo_pose_new_26/v5_phase2_decoder_fix_QA.csv`