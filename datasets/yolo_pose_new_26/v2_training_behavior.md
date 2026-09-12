# Comportement d'entraînement V2 — new_26

**Généré :** 2026-08-23T21:01:11.370044+00:00
**Run :** `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/`
**Mode :** lecture seule — aucun fichier modifié

## Synthèse exécutive

- **Epochs :** 100
- **Loss pose val finale :** 1.672
- **Meilleure métrique pose (mAP50-95) :** 0.692 (epoch **80**)
- **Loss pose train finale :** 1.706 (début 4.463)
- **Convergence loss pose :** Oui — convergée globalement, plateau val en fin de run
- **Amélioration fin de run :** NON (val/pose_loss dernières 5 epochs : 1.676 vs 1.640 ; mAP50-95(P) : 0.645 vs 0.645)
- **Sous-apprentissage global :** NON
- **Problème spécifique ASL_L :** OUI

### Lien avec l'inference (diagnostic A confirmé)

| Landmark | TRAIN (px) | VAL (px) | Commentaire |
|----------|------------|----------|-------------|
| ASL_L | 538.18 | 471.72 | Échec train + val |
| ASL_R | 142.86 | 147.73 | Dégradé mais 4× mieux que ASL_L |
| ASM_L | 77.59 | 80.94 | Bon — sourcil médial appris |

**Conclusion :** les métriques Ultralytics agrégées (mAP pose ~0.65) **masquent** l'échec pixel-level sur ASL_L. Ce n'est pas un problème de généralisation val.

## Recommandation V3

V3 : repartir du checkpoint epoch 80 (meilleur mAP50-95 pose), renforcer l'apprentissage ASL_L (audit augmentations miroir, pose loss, plus de données ou focalisation keypoint), réduire l'augmentation agressive sur petit lot (mosaic/randaugment), et valider en px GT par keypoint — les métriques Ultralytics agrégées masquent l'échec ASL_L.

## Paramètres d'entraînement V2

| Paramètre | Valeur |
|-----------|--------|
| model | `.\runs\pose\runs\yolo_pose_new_26\weights\best.pt` |
| pretrained | **True** |
| data | `.\datasets\yolo_pose_new_26\dataset.yaml` |
| epochs | **100** |
| imgsz | **640** |
| batch | **2** |
| device | **cpu** |
| optimizer | **auto** |
| lr0 | **0.01** |
| lrf | **0.01** |
| patience | **100** |
| pose (loss gain) | **12.0** |
| kobj | **1.0** |
| box | **7.5** |
| cos_lr | **False** |
| amp | **True** |
| seed | **0** |

### Augmentations

- `hsv_h` : **0.015**
- `hsv_s` : **0.7**
- `hsv_v` : **0.4**
- `degrees` : **0.0**
- `translate` : **0.1**
- `scale` : **0.5**
- `shear` : **0.0**
- `perspective` : **0.0**
- `flipud` : **0.0**
- `fliplr` : **0.5**
- `mosaic` : **1.0**
- `mixup` : **0.0**
- `cutmix` : **0.0**
- `copy_paste` : **0.0**
- `auto_augment` : **randaugment**
- `erasing` : **0.4**
- `close_mosaic` : **10**

## Courbes et convergence

### Loss pose

| Split | Début | Fin | Meilleur | Epoch best |
|-------|-------|-----|----------|------------|
| train/pose_loss | 4.463 | 1.706 | 1.601 | 99 |
| val/pose_loss | 3.283 | 1.672 | 1.601 | 83 |

### Métriques pose (agrégées, toutes keypoints)

- **mAP50(P) final :** 0.995 (max dès epoch 1 — peu discriminant sur 5 val)
- **mAP50-95(P) final :** 0.646
- **mAP50-95(P) best :** 0.692 @ epoch **80**

**Note :** chute mAP50(P) à epoch 13 (~0.20) puis récupération — instabilité early training typique d'un très petit val set (5 images).

### Dernières epochs

| Epoch | train/pose | val/pose | mAP50-95(P) |
|------:|-----------:|---------:|------------:|
| 91 | 1.712 | 1.611 | 0.632 |
| 92 | 1.832 | 1.635 | 0.650 |
| 93 | 1.750 | 1.635 | 0.650 |
| 94 | 1.780 | 1.635 | 0.650 |
| 95 | 1.798 | 1.682 | 0.642 |
| 96 | 1.650 | 1.682 | 0.642 |
| 97 | 1.762 | 1.682 | 0.642 |
| 98 | 1.602 | 1.672 | 0.646 |
| 99 | 1.601 | 1.672 | 0.646 |
| 100 | 1.706 | 1.672 | 0.646 |

**Observation :** best mAP50-95(P) à epoch **80** (0.692), puis légère dégradation jusqu'à epoch 100 (0.646). `best.pt` et `last.pt` ont la même taille/timestamp — vérifier si le meilleur checkpoint correspond bien à epoch 80 pour V3.

## Métadonnées best.pt (lecture seule)

```json
{
  "available": true,
  "epoch": -1,
  "best_fitness": null,
  "date": "2026-08-23T18:10:01.683842",
  "version": "8.4.96",
  "updates": null,
  "checkpoint_train_args": {
    "epochs": 100,
    "imgsz": 640,
    "batch": 2,
    "model": ".\\runs\\pose\\runs\\yolo_pose_new_26\\weights\\best.pt",
    "data": "datasets\\yolo_pose_new_26\\dataset.yaml",
    "optimizer": "auto",
    "lr0": 0.01,
    "lrf": 0.01,
    "patience": 100,
    "pretrained": true,
    "pose": 12.0,
    "device": "cpu"
  }
}
```

## Artefacts disponibles

### config

- `args.yaml`
- `results.csv`

### metrics

- `results.png`

### curves

- `BoxF1_curve.png`
- `BoxP_curve.png`
- `BoxPR_curve.png`
- `BoxR_curve.png`
- `confusion_matrix.png`
- `confusion_matrix_normalized.png`
- `PoseF1_curve.png`
- `PoseP_curve.png`
- `PosePR_curve.png`
- `PoseR_curve.png`

### visual_debug

- `labels.jpg`
- `train_batch0.jpg`
- `train_batch1.jpg`
- `train_batch2.jpg`
- `train_batch990.jpg`
- `train_batch991.jpg`
- `train_batch992.jpg`
- `val_batch0_labels.jpg`
- `val_batch0_pred.jpg`
- `val_batch1_labels.jpg`
- `val_batch1_pred.jpg`

### weights

- `weights/best.pt`
- `weights/last.pt`

## Métriques keypoint-level pendant l'entraînement

**Non disponibles** dans les artefacts Ultralytics standard de ce run.

Ce run expose uniquement :
- losses agrégées (`train/pose_loss`, `val/pose_loss`) — **pas par keypoint** ;
- mAP pose globaux (`metrics/mAP50(P)`, `metrics/mAP50-95(P)`) — **pas par landmark** ;
- visualisations batch (`val_batch0_pred.jpg`, `train_batch*.jpg`) — inspection visuelle possible ;
- courbes `PoseP_curve.png`, `PoseR_curve.png`, `PoseF1_curve.png`, `results.png`.

Pour V3, prévoir une **validation px/keypoint** (comme `analyze_v2_train_vs_val_new_26.py`) à intervalles réguliers — seule métrique fiable pour ASL_L sur ce dataset.

## Réponses aux 5 questions

1. **Loss pose/keypoint converge ?** Loss agrégée : **Oui** (train 4.46→1.71, val 3.28→1.67). Pas de métrique keypoint-level dans le run.
2. **Dernières epochs encore en amélioration ?** **Non** — plateau/dégradation légère après epoch 80.
3. **Modèle sous-entraîné globalement ?** **Non** — mAP pose ~0.65, la plupart des landmarks < 150.0 px en inference.
4. **Problème ASL_L isolé ?** **Oui** — ASL_L ~538 px train vs ASM_L ~78 px, autres landmarks ~60–170 px.
5. **Paramètres V2 :** voir tableau ci-dessus (`epochs=100`, `batch=2`, `imgsz=640`, `device=cpu`, finetune depuis V1 `best.pt`, augmentations fortes).

## Regénérer

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\analyze_v2_training_behavior_new_26.py
```
