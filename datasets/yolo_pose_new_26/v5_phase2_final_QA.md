# V5 Phase 2 — Final QA (Post-Training)

**Généré :** 2026-08-29 02:46 UTC
**Mode :** READ-ONLY
**Run :** `runs\pose\yolo_pose_new_26_v5_phase2\run_20260829_032756`
**Verdict :** `V5_PHASE2_IT_IMPROVED_BUT_INSUFFICIENT`

---

## 1. Training

| Métrique | Valeur |
|----------|--------|
| Epochs exécutés | 20 |
| Meilleur epoch | **12** |
| Meilleur IT_mean_px | **597.76 px** |
| best_it.pt | `runs\pose\yolo_pose_new_26_v5_phase2\run_20260829_032756\weights\best_it.pt` |
| last_it.pt | `runs\pose\yolo_pose_new_26_v5_phase2\run_20260829_032756\weights\last_it.pt` |
| Arrêt | early stopping patience=8 sur IT_mean_px — meilleur epoch 12, arrêt epoch 20 |

### Évolution IT_mean_px

| Epoch | train_loss | IT_mean_px | IT_R | IT_L | frozen_ok |
|------:|-----------:|-----------:|-----:|-----:|:---------:|
| 1 | 3.3338 | 600.74 | 534.05 | 654.10 | True |
| 2 | 2.9631 | 597.90 | 531.89 | 650.70 | True |
| 3 | 2.7342 | 598.02 | 532.04 | 650.81 | True |
| 4 | 2.6542 | 597.76 | 531.80 | 650.54 | True |
| 5 | 2.5932 | 598.11 | 532.16 | 650.87 | True |
| 6 | 2.5711 | 597.86 | 531.81 | 650.69 | True |
| 7 | 2.5493 | 597.83 | 531.73 | 650.72 | True |
| 8 | 2.5310 | 597.90 | 531.78 | 650.80 | True |
| 9 | 2.5257 | 597.76 | 531.66 | 650.63 | True |
| 10 | 2.5402 | 597.95 | 531.90 | 650.79 | True |
| 11 | 2.5104 | 597.95 | 531.94 | 650.75 | True |
| 12 | 2.4815 | 597.76 | 531.72 | 650.58 | True |
| 13 | 2.4720 | 597.87 | 531.83 | 650.69 | True |
| 14 | 2.4709 | 597.86 | 531.84 | 650.67 | True |
| 15 | 2.4634 | 597.93 | 531.93 | 650.72 | True |
| 16 | 2.4599 | 598.00 | 532.01 | 650.79 | True |
| 17 | 2.4605 | 597.96 | 531.92 | 650.78 | True |
| 18 | 2.4562 | 597.84 | 531.80 | 650.68 | True |
| 19 | 2.4541 | 597.83 | 531.84 | 650.63 | True |
| 20 | 2.4518 | 598.10 | 532.04 | 650.94 | True |

---

## 2. IT Performance (val, v=2 uniquement) — Phase2 best in-memory

| Métrique | Valeur |
|----------|-------:|
| IT_R_mean_px | 531.8680419921875 |
| IT_L_mean_px | 650.7371337890625 |
| IT_mean_px | 597.9064263237847 |
| IT_median_px | 625.0979614257812 |
| IT_p90_px | 679.0630493164062 |
| IT_correct_rate <75 px | 0.0% |
| IT_correct_rate <150 px | 0.0% |
| N évalué | 9 |

### Par image

| Image | IT_R px | IT_L px | IT_mean px |
|-------|--------:|--------:|-----------:|
| B26_10 | 530.7275390625 | 636.6845092773438 | 583.71 |
| B26_13 | 506.1370849609375 | 625.0979614257812 | 565.62 |
| B26_17 | 539.68408203125 | 660.5350952148438 | 600.11 |
| B26_20 | 550.9234619140625 | 679.0630493164062 | 614.99 |
| B26_26 | None | 652.3050537109375 | 652.31 |

---

## 3. Comparaison V2 / surgical_init / Phase2 best

### Détection (conf=0.25)

| Image | V2 n | V2 conf | V2 IoU | surgical n | phase2 n | phase2 conf | phase2 IoU |
|-------|-----:|--------:|-------:|-----------:|---------:|------------:|-----------:|
| B26_10 | 1 | 0.891736 | 0.9304567971752552 | 1 | 1 | 0.891736 | 0.9304567971752552 |
| B26_13 | 1 | 0.875427 | 0.8892124377628038 | 1 | 1 | 0.875427 | 0.8892124377628038 |
| B26_17 | 1 | 0.885234 | 0.9080565978081454 | 1 | 1 | 0.885234 | 0.9080565978081454 |
| B26_20 | 1 | 0.921167 | 0.8931882797269804 | 1 | 1 | 0.921167 | 0.8931882797269804 |
| B26_26 | 1 | 0.860271 | 0.7482001924791625 | 1 | 1 | 0.860271 | 0.7482001924791625 |

### 14 KP — agrégat

| Modèle | Mean px | Median | P90 | CORRECT | INCERTAIN | INCORRECT |
|--------|--------:|-------:|----:|--------:|----------:|----------:|
| V2 | 134.95 | 98.18 | 293.40 | 25 | 28 | 17 |
| surgical_init | 134.95 | 98.18 | 293.40 | 25 | 28 | 17 |
| phase2_best | 134.95 | 98.18 | 293.40 | 25 | 28 | 17 |

---

## 4. Safety / Freeze (surgical_init → best_it.pt)

**Freeze zones OK :** True
**IT head changed :** True

| Zone | Tensors | Changed | Max Δ |
|------|--------:|--------:|------:|
| backbone | 120 | 0 | 0.000000e+00 |
| neck | 60 | 0 | 0.000000e+00 |
| cv2_box | 156 | 0 | 0.000000e+00 |
| cv3_cls | 81 | 0 | 0.000000e+00 |
| dfl | 1 | 0 | 0.000000e+00 |
| cv4_pose | 36 | 0 | 0.000000e+00 |
| it_head | 66 | 62 | 7.560000e+02 |

---

## 5. Détection — régression

- V2 détections /5 : **5/5**
- Phase2 best détections /5 : **5/5**
- Régression détection : **False**

---

## 6. 14 KP vs V2

- Mean V2 : 134.95 px
- Mean Phase2 : 134.95 px
- Régression significative : **False**

---

## 7. Conclusion : `V5_PHASE2_IT_IMPROVED_BUT_INSUFFICIENT`

- Gel respecté : True
- IT head entraîné (Δ>0) : True
- IT amélioré vs epoch 1 (600.74 → 597.91 px) : True
- IT suffisant (<150 px, >50% correct) : False
- Détection stable vs V2 : True

CSV : `v5_phase2_final_QA.csv`
