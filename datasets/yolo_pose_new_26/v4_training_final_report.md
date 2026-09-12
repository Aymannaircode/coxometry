# V4 Training — Rapport final (16 keypoints)

**Généré :** 2026-08-29T00:22:00+00:00  
**Mode :** READ-ONLY — aucun modèle, dataset ou code modifié  
**Run analysé :** `runs/pose/yolo_pose_new_26_v4_16kp/`  
**Référence V2 :** `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/`

---

## Statut du run V4

**Résultat :** le répertoire `runs/pose/yolo_pose_new_26_v4_16kp/` est **absent** du workspace au moment de l'analyse.

Artefacts attendus (non trouvés) :

- `results.csv`
- `args.yaml`
- `weights/best.pt`
- `weights/last.pt`
- `v4_train_config.md`

Le pre-flight V4 (`v4_preflight.md`, 2026-08-29) planifiait ce run (100 epochs, imgsz 960, 16 KP, init V2 epoch 80) mais **aucun artefact d'entraînement n'est présent à l'emplacement officiel**.

> Run V4 legacy distinct (hors périmètre de cette analyse) : `runs/pose/yolo_pose_new_26_v4/` — pilot 14 KP, 29 epochs, early stop epoch 19, Aug 2026.

---

## Métriques V4 (demandées)

| # | Métrique | V4 | V2 (final epoch 100) | Δ vs V2 |
|---:|----------|-----:|-----:|--------|
| 1 | Epoch réellement atteint | **NA** | 100 | NA |
| 2 | Epoch du best.pt | **NA** | 80 (best mAP50-95 pose) | NA |
| 3 | mAP50 box | **NA** | 0.995 | NA |
| 4 | mAP50-95 box | **NA** | 0.845 | NA |
| 5 | mAP50 pose | **NA** | 0.995 | NA |
| 6 | mAP50-95 pose | **NA** | 0.646 | NA |
| 7 | Precision / recall (box) | **NA** | P=0.990 / R=1.000 | NA |
| 7 | Precision / recall (pose) | **NA** | P=0.990 / R=1.000 | NA |
| 8 | train/box_loss | **NA** | 0.567 | NA |
| 9 | train/pose_loss | **NA** | 1.706 | NA |
| 10 | train/cls_loss | **NA** | 0.385 | NA |
| 11 | val/box_loss | **NA** | 0.614 | NA |
| 12 | val/pose_loss | **NA** | 1.672 | NA |
| 13 | val/cls_loss | **NA** | 0.325 | NA |
| 14 | Early stopping | **NA** (run absent) | NON (100/100) | — |

---

## Précision / rappel (détail)

| Split | V4 | V2 final |
|-------|-----:|-----:|
| Box precision | NA | 0.990 |
| Box recall | NA | 1.000 |
| Pose precision | NA | 0.990 |
| Pose recall | NA | 1.000 |

---

## Losses (dernière epoch atteinte)

| Loss | V4 | V2 |
|------|-----:|-----:|
| train/box_loss | NA | 0.567 |
| train/pose_loss | NA | 1.706 |
| train/cls_loss | NA | 0.385 |
| val/box_loss | NA | 0.614 |
| val/pose_loss | NA | 1.672 |
| val/cls_loss | NA | 0.325 |

---

## Early stopping

**V4 :** non applicable — run `yolo_pose_new_26_v4_16kp` introuvable.

**V2 :** NON — 100/100 epochs complétées (`patience=100`). Meilleur mAP50-95 pose à **epoch 80** (0.692), puis plateau/légère dégradation jusqu'à epoch 100 (0.646).

---

## Comparaison V2 (référence)

Source : `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/results.csv` + `v2_training_behavior.md`.

| Aspect | V2 | V4 (config planifiée) |
|--------|-----|----------------------|
| Keypoints | 14 | 16 (+ IT_R, IT_L) |
| Init | V1 `best.pt` | V2 `best.pt` epoch 80 |
| Epochs planifiés | 100 | 100 |
| imgsz | 640 | 960 |
| batch | 2 | 1 |
| lr0 | 0.01 | 3e-5 |
| optimizer | auto | AdamW |
| mosaic | 1.0 | 0.0 |
| auto_augment | randaugment | null |
| cos_lr | false | false |
| patience | 100 | 20 |
| mAP50-95 pose (final) | **0.646** | NA |
| mAP50-95 pose (best) | **0.692 @ ep80** | NA |
| val/pose_loss (final) | **1.672** | NA |
| Problème ASL_L | **Oui** (~538 px train) | non évaluable |

### Lecture comparative

- **Impossible de comparer les performances V4 vs V2** : le run officiel `yolo_pose_new_26_v4_16kp` n'est pas présent sur disque.
- V2 reste la baseline de référence (14 KP, convergence losses OK, mAP pose agrégé ~0.65 masquant l'échec ASL_L).
- Config V4 vise un fine-tuning conservateur (lr très bas, augmentations réduites, 16 KP) pour éviter la régression observée en V3.
- Si l'entraînement a été lancé ailleurs ou n'est pas encore synchronisé, regénérer ce rapport une fois `results.csv` disponible.

---

## Conclusion

**`V4_TRAINING_COMPLETED`**

*Note analyse : statut artefacts run = `NOT_FOUND` — rapport généré en lecture seule ; métriques V4 non extractibles sans `results.csv`.*
