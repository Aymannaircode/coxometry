# V5 Phase 1 — Post-training Diagnostic

**Généré :** 2026-08-29 01:22 UTC
**Mode :** READ-ONLY
**Conclusion :** `V5_PHASE1_DIAGNOSTIC_REQUIRED`

---

## Contexte run

| Paramètre | Valeur |
|-----------|--------|
| Run | `runs/pose/yolo_pose_new_26_v5_phase1_it` |
| Epochs | 15 |
| Init args.model | `C:\Users\g\OneDrive\Desktop\Projet-Ayman\runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_surgical_init.pt` |
| data.yaml | `C:\Users\g\OneDrive\Desktop\Projet-Ayman\datasets\yolo_pose_new_26\data.yaml` |
| imgsz | 640 |
| conf (val default) | 0.001 (Ultralytics val default) |
| inférence diagnostic | conf=**0.25**, imgsz=**640** |
| freeze | None |
| pretrained | False |
| lr0 | 1e-05 |
| optimizer | AdamW |

Métriques finales (`results.csv` epoch 15) : Box P≈0.006, R≈0.6, mAP50(B)≈0.01, Pose mAP=0.

---

## 1. Comparaison checkpoints

| Checkpoint | Rôle |
|------------|------|
| `V2 best.pt` | Référence production 14 KP |
| `v5_surgical_init.pt` | Init Phase 0 (epoch -1) |
| `V5 phase1 best.pt` | Meilleur fitness Phase 1 |
| `V5 phase1 last.pt` | Dernier epoch (15) |

---

## 2. Paramètres modifiés (surgical_init → phase1 best)

| Zone | Tensors | Changed | Max abs diff |
|------|--------:|--------:|-------------:|
| backbone | 216 | 216 | 1.022798e+01 |
| cv2_box | 186 | 186 | 9.039062e+00 |
| cv3_cls | 96 | 96 | 4.539062e+00 |
| dfl | 1 | 0 | 0.000000e+00 |
| cv4_pose | 42 | 42 | 2.069153e+00 |
| other | 0 | 0 | 0.000000e+00 |

### surgical_init → last.pt

| Zone | Changed | Max abs diff |
|------|--------:|-------------:|
| backbone | 216 | 1.022798e+01 |
| cv2_box | 186 | 9.031250e+00 |
| cv3_cls | 96 | 4.539062e+00 |
| dfl | 0 | 0.000000e+00 |
| cv4_pose | 42 | 2.070251e+00 |

### V2 → surgical_init (non-cv4 attendu identique)

| Zone | Changed | Max abs diff |
|------|--------:|-------------:|
| backbone | 0 | 0.000000e+00 |
| cv2_box | 0 | 0.000000e+00 |
| cv3_cls | 0 | 0.000000e+00 |
| dfl | 0 | 0.000000e+00 |

---

## 3. Gel prévu vs réalité training

| Mécanisme prévu | Appliqué dans trainer ? |
|-----------------|:-----------------------:|
| `apply_it_only_freeze()` avant train | **Non persistant** — trainer reset `requires_grad=True` (L321-326) |
| Hooks cv4 canaux 42–47 | **Perdus** — nouveau module dans trainer |
| `ITOnlyPoseLoss` masque KP 0–13 | **Non injecté** dans trainer |
| `freeze=null` | Aucun gel backbone/cv2/cv3 |
| EMA (`ModelEMA`) | **Met à jour tous les poids** chaque step |
| Loss box/cls/dfl | **Active** sur tête gelée en principe |

---

## 4. Inférence comparée (5 val @ conf=0.25, imgsz=640)

| Image | V2 boxes | surgical boxes | best boxes | last boxes |
|-------|:--------:|:--------------:|:----------:|:----------:|
| B26_10 | 1 | 1 | 0 | 8 |
| B26_13 | 1 | 1 | 0 | 3 |
| B26_17 | 1 | 1 | 0 | 0 |
| B26_20 | 1 | 1 | 0 | 26 |
| B26_26 | 1 | 1 | 0 | 0 |

### Détail inférence (top box par image)

| Image | Modèle | n_boxes | conf | IoU vs GT |
|-------|--------|--------:|-----:|----------:|
| B26_10 | V2_best | 1 | 0.8917 | 0.9305 |
| B26_10 | v5_surgical_init | 1 | 0.8917 | 0.9305 |
| B26_10 | V5_phase1_best | 0 | — | — |
| B26_10 | V5_phase1_last | 8 | 0.6539 | 0.0215 |
| B26_13 | V2_best | 1 | 0.8754 | 0.8892 |
| B26_13 | v5_surgical_init | 1 | 0.8754 | 0.8892 |
| B26_13 | V5_phase1_best | 0 | — | — |
| B26_13 | V5_phase1_last | 3 | 0.4625 | 0.6663 |
| B26_17 | V2_best | 1 | 0.8852 | 0.9081 |
| B26_17 | v5_surgical_init | 1 | 0.8852 | 0.9081 |
| B26_17 | V5_phase1_best | 0 | — | — |
| B26_17 | V5_phase1_last | 0 | — | — |
| B26_20 | V2_best | 1 | 0.9212 | 0.8932 |
| B26_20 | v5_surgical_init | 1 | 0.9212 | 0.8932 |
| B26_20 | V5_phase1_best | 0 | — | — |
| B26_20 | V5_phase1_last | 26 | 0.6572 | 0.1598 |
| B26_26 | V2_best | 1 | 0.8603 | 0.7482 |
| B26_26 | v5_surgical_init | 1 | 0.8603 | 0.7482 |
| B26_26 | V5_phase1_best | 0 | — | — |
| B26_26 | V5_phase1_last | 0 | — | — |

**Détections (≥1 box @ conf=0.25)** : V2 **5/5** · surgical **5/5** · best **0/5** · last **3/5**

---

## 5. Findings (cause racine)

1. BACKBONE/CV2/CV3 : **100 % des tensors modifiés** vs surgical_init (max Δ≈10.2 backbone, 9.0 cv2, 4.5 cv3). Le gel IT-only (`apply_it_only_freeze`) appelé avant `yolo.train()` n'est **pas propagé** au PoseTrainer : `freeze=null`, reset `requires_grad=True`, losses box/cls/dfl actives sur toute la tête.
2. CV4 : **42/42 tensors modifiés** (incl. canaux 0–41) — le masque IT-only cv4 n'a pas été appliqué dans la boucle trainer.
3. `pretrained=False` : Ultralytics `model.train()` peut reconstruire le modèle via `get_model(weights=None)` (model.py L808-814) — le checkpoint surgical_init est chargé via `args.model`, mais sans gel les losses détections réentraînent l'intégralité du réseau.
4. `freeze=null` — seul `.dfl` gelé nativement; aucun gel backbone/cv2/cv3/cv4-old.
5. `ITOnlyPoseLoss` (masque KP 0–13) **non branché** dans le trainer — seule la loss pose IT est masquée en design, mais box/cls/dfl continuent de mettre à jour cv2/cv3/backbone.
6. EMA (`ModelEMA.update`) appliquée à **tous** les paramètres chaque step — les checkpoints best/last reflètent cette moyenne mobile, pas un gel effectif.
7. Val `cls_loss` explose epoch 12+ (≈7.68) — symptôme d'effondrement classification ; Box P/R instables (epoch 9 spike P=0.28 puis chute).
8. Inférence val @ conf=0.25 : V2 détecte **5/5** pelvis, V5 best **0/5** — effondrement détection confirmé post-training.
9. surgical_init conserve la détection V2 sur val — la régression est **causée par Phase 1 training**, pas par l'expansion 14→16 KP seule.

---

## Conclusion : `V5_PHASE1_DIAGNOSTIC_REQUIRED`

CSV détaillé : `v5_phase1_posttraining_diagnostic.csv`
