# V5 Phase 1 v3 — Final Training Analysis

**Généré :** 2026-08-29 02:03 UTC
**Mode :** READ-ONLY
**Run :** `runs/pose/yolo_pose_new_26_v5_phase1_it_v3-3`
**IT Learning :** `V5_PHASE1_IT_LEARNING_WEAK`
**Production :** `NOT_PRODUCTION_CANDIDATE`

---

## 1. Courbes d'entraînement (results.csv)

- **Epochs exécutés :** 9 / 14 demandés
- **Meilleur epoch (mAP50 pose) :** 1 (mAP50(P)=0.9950)
- **Epoch d'arrêt :** 9
- **Raison arrêt :** patience=8 : meilleur mAP50(P)=0.9950 atteint epoch 1, puis 8 epochs sans amélioration → arrêt epoch 9 (cible 14 non atteinte)

| Epoch | train pose | train kobj | val pose | mAP50(P) | mAP50-95(P) | P(P) | R(P) | lr/pg0 |
|------:|-----------:|-----------:|---------:|---------:|------------:|-----:|-----:|-------:|
| 1 | 11.3564 | 0.6748 | 3.4635 | 0.9950 | 0.3575 | 0.9902 | 1.0000 | 2.00e-06 |
| 2 | 10.7843 | 0.6738 | 3.4631 | 0.9950 | 0.3575 | 0.9902 | 1.0000 | 3.81e-06 |
| 3 | 11.3421 | 0.6679 | 3.4630 | 0.9950 | 0.3575 | 0.9902 | 1.0000 | 5.32e-06 |
| 4 | 11.3593 | 0.6687 | 3.4630 | 0.9950 | 0.3575 | 0.9902 | 1.0000 | 6.54e-06 |
| 5 | 11.3602 | 0.6668 | 3.4630 | 0.9950 | 0.3575 | 0.9902 | 1.0000 | 7.17e-06 |
| 6 | 11.3281 | 0.6668 | 3.4630 | 0.9950 | 0.3575 | 0.9902 | 1.0000 | 5.76e-06 |
| 7 | 10.7668 | 0.6706 | 3.4630 | 0.9950 | 0.3575 | 0.9902 | 1.0000 | 5.05e-06 |
| 8 | 10.7772 | 0.6725 | 3.4630 | 0.9950 | 0.3575 | 0.9902 | 1.0000 | 4.34e-06 |
| 9 | 11.3212 | 0.6667 | 3.4630 | 0.9950 | 0.3575 | 0.9902 | 1.0000 | 3.64e-06 |

- mAP50(P) plateau dès epoch 1 : **True**
- val pose loss plateau : **False**
- train pose loss varie : **True**

---

## 2. Comparaison checkpoints

| ID | Fichier |
|----|---------|
| A | `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_surgical_init.pt` |
| B | `runs\pose\yolo_pose_new_26_v5_phase1_it_v3\weights\best.pt` |
| C | `runs\pose\yolo_pose_new_26_v5_phase1_it_v3-3\weights\best.pt` |
| D | `runs\pose\yolo_pose_new_26_v5_phase1_it_v3-3\weights\last.pt` |

### A → C (surgical_init → final best) — attendu : frozen=0, IT>0

| Zone | Changed | Max Δ | Mean Δ |
|------|--------:|------:|-------:|
| backbone | 0 | 0.000000e+00 | 0.000000e+00 |
| cv2 | 0 | 0.000000e+00 | 0.000000e+00 |
| cv3 | 0 | 0.000000e+00 | 0.000000e+00 |
| dfl | 0 | 0.000000e+00 | 0.000000e+00 |
| cv4 old | 0 | 0.000000e+00 | 0.000000e+00 |
| cv4 IT | 5 | 6.579590e-02 | 3.242248e-03 |

### B → C (epoch-1 → final best) — progression IT

| cv4 IT changed | 3 | max Δ 3.791809e-02 |
| cv4 old changed | 0 |
| C ≡ D | **True** |

---

## 3. Évaluation IT directe (v≥2 uniquement)

| Modèle | Scope | N | Mean px | Median | P90 | CORR | INCERT | INCORR |
|--------|-------|--:|--------:|-------:|----:|-----:|-------:|-------:|
| epoch1_best | IT_R | 4 | 997.69 | 1048.11 | 1096.17 | 0 | 0 | 4 |
| epoch1_best | IT_L | 5 | 873.92 | 882.58 | 957.75 | 0 | 0 | 5 |
| epoch1_best | global | 9 | 928.93 | 898.29 | 1096.17 | 0 | 0 | 9 |
| final_best | IT_R | 4 | 983.48 | 1032.91 | 1082.79 | 0 | 0 | 4 |
| final_best | IT_L | 5 | 853.60 | 863.89 | 938.21 | 0 | 0 | 5 |
| final_best | global | 9 | 911.32 | 875.53 | 1082.79 | 0 | 0 | 9 |
| final_last | IT_R | 4 | 983.48 | 1032.91 | 1082.79 | 0 | 0 | 4 |
| final_last | IT_L | 5 | 853.60 | 863.89 | 938.21 | 0 | 0 | 5 |
| final_last | global | 9 | 911.32 | 875.53 | 1082.79 | 0 | 0 | 9 |

Δ IT global (final best − epoch1) : **-17.61 px** (amélioration)

---

## 4. 14 KP — régression vs V2 / surgical

| Modèle | Mean px | Median | P90 | CORR | INCERT | INCORR |
|--------|--------:|-------:|----:|-----:|-------:|-------:|
| V2_best | 134.95 | 98.18 | 293.40 | 25 | 28 | 17 |
| surgical_init | 134.95 | 98.18 | 293.40 | 25 | 28 | 17 |
| final_best | 134.95 | 98.18 | 293.40 | 25 | 28 | 17 |

Régression 14 KP détectée : **False** — identique V2 : **True**

---

## 5. Détection val (5 images, conf=0.25)

| Modèle | Détections / 5 |
|--------|:--------------:|
| V2_best | **5/5** |
| surgical_init | **5/5** |
| epoch1_best | **5/5** |
| final_best | **5/5** |
| final_last | **5/5** |

| Image | Modèle | n_boxes | conf | IoU |
|-------|--------|--------:|-----:|----:|
| B26_10 | V2_best | 1 | 0.891736 | 0.930457 |
| B26_10 | surgical_init | 1 | 0.891736 | 0.930457 |
| B26_10 | epoch1_best | 1 | 0.891736 | 0.930457 |
| B26_10 | final_best | 1 | 0.891736 | 0.930457 |
| B26_10 | final_last | 1 | 0.891736 | 0.930457 |
| B26_13 | V2_best | 1 | 0.875427 | 0.889212 |
| B26_13 | surgical_init | 1 | 0.875427 | 0.889212 |
| B26_13 | epoch1_best | 1 | 0.875427 | 0.889212 |
| B26_13 | final_best | 1 | 0.875427 | 0.889212 |
| B26_13 | final_last | 1 | 0.875427 | 0.889212 |
| B26_17 | V2_best | 1 | 0.885234 | 0.908057 |
| B26_17 | surgical_init | 1 | 0.885234 | 0.908057 |
| B26_17 | epoch1_best | 1 | 0.885234 | 0.908057 |
| B26_17 | final_best | 1 | 0.885234 | 0.908057 |
| B26_17 | final_last | 1 | 0.885234 | 0.908057 |
| B26_20 | V2_best | 1 | 0.921167 | 0.893188 |
| B26_20 | surgical_init | 1 | 0.921167 | 0.893188 |
| B26_20 | epoch1_best | 1 | 0.921167 | 0.893188 |
| B26_20 | final_best | 1 | 0.921167 | 0.893188 |
| B26_20 | final_last | 1 | 0.921167 | 0.893188 |
| B26_26 | V2_best | 1 | 0.860271 | 0.748200 |
| B26_26 | surgical_init | 1 | 0.860271 | 0.748200 |
| B26_26 | epoch1_best | 1 | 0.860271 | 0.748200 |
| B26_26 | final_best | 1 | 0.860271 | 0.748200 |
| B26_26 | final_last | 1 | 0.860271 | 0.748200 |

---

## 6. Réponses objectif principal

**A. IT_R / IT_L ont-ils appris ?** Oui, erreur IT en baisse (epoch1 mean=928.93 px → final=911.32 px).

**B. Meilleur checkpoint IT :** `final_best` (mean global IT=911.32 px).

**C. 14 KP identiques à V2 ?** Oui (final mean=134.95 vs V2=134.95 px).

**D. Détection identique à V2 ?** Oui ({'V2_best': 5, 'surgical_init': 5, 'epoch1_best': 5, 'final_best': 5, 'final_last': 5}).

**E. Early stopping dû à métrique standard ?** **Oui.** mAP50(P) bloqué à 0.3575 dès epoch 1 alors que train pose loss varie (True) — patience=8 sur fitness Ultralytics (pose mAP), pas loss IT directe.

**F. Erreur IT finale (final best, v≥2) :** mean=911.32 px, median=875.53 px, p90=1082.79 px.

---

## 7. Note méthodologique

mAP50(P)=0.3575 **ne mesure pas** spécifiquement IT_R/IT_L (indices 14–15).
L'objectif Phase 1 est l'apprentissage des 2 nouveaux KP — évalués directement ci-dessus.

---

## Conclusion IT : `V5_PHASE1_IT_LEARNING_WEAK`
## Conclusion production : `NOT_PRODUCTION_CANDIDATE`

CSV : `v5_phase1_v3_final_analysis.csv`
