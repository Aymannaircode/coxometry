# Audit régression V3 — new_26

**Généré :** 2026-08-23T21:31:29.509611+00:00
**Mode :** lecture seule

## Verdict : **A**

Init V2 bit-identique (poids max diff=0). Dès epoch **1**, mAP50-95(P) V3 effondré (0.0000 vs V2 0.4624 à epoch 1). Fine-tuning avec lr0=0.01, optimizer=auto (AdamW ~0.002 auto), mosaic=0.0, pretrained=False — schedule identique à un entraînement neuf alors que le modèle était déjà convergé (V2 pose loss ~1.7). Choc d'augmentation (mosaic 1→0) + LR warmup agressif = destruction immédiate des poids.

## 1. Checkpoints initiaux

| | V2 best.pt | V3 init |
|--|------------|---------|
| Chemin | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` | `runs/pose/yolo_pose_new_26_v3/init/v2_best_mAP_epoch80.pt` |
| Taille (octets) | 5947464 | 5947464 |
| SHA256 | `1f92d0867b4cd86e…` | `1f92d0867b4cd86e…` |
| Identiques | — | **Oui** |
| nc / kpt_shape | 1 / [14, 3] | 1 / [14, 3] |
| yaml | yolo11n-pose.yaml | yolo11n-pose.yaml |

Poids V2 vs V3 best.pt : max abs diff **10.228**, mean **0.337**.

## 2. Configuration V2 vs V3

| Paramètre | V2 | V3 |
|-----------|----|----|
| epochs | 100 | 100 |
| patience | 100 | 25 **←** |
| batch | 2 | 2 |
| imgsz | 640 | 640 |
| lr0 | 0.01 | 0.01 |
| lrf | 0.01 | 0.01 |
| optimizer | auto | auto |
| pretrained | True | False **←** |
| freeze | None | None |
| mosaic | 1.0 | 0.0 **←** |
| auto_augment | randaugment | None **←** |
| erasing | 0.4 | 0.0 **←** |
| fliplr | 0.5 | 0.5 |
| model | .\runs\pose\runs\yolo_pose_new_26\weights\best.pt | C:\Users\g\OneDrive\Desktop\Projet-Ayman\runs\pose\yolo_pose_new_26_v3\init\v2_best_mAP_epoch80.pt **←** |
| data | .\datasets\yolo_pose_new_26\dataset.yaml | C:\Users\g\OneDrive\Desktop\Projet-Ayman\datasets\yolo_pose_new_26\data.yaml **←** |

### Dataset YAML

- flip_idx : `[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]`
- kpt_shape : `[14, 3]`
- Écarts data.yaml vs dataset.yaml : **0**

## 3. Learning rate

- lr0 configuré : V2=0.01, V3=0.01 (identique)
- optimizer : auto → Ultralytics choisit **AdamW lr≈0.002**
- V3 epoch 1 lr (warmup) : `0.0002`

**Analyse :** repartir d'un modèle convergé (V2 pose loss ~1.7) avec le même schedule lr0=0.01 / warmup / AdamW 0.002 qu'un entraînement from-scratch est **trop agressif** pour un fine-tuning de 21 images.

## 4. Courbes — jalons mAP50-95(P)

| Epoch | V2 mAP | V3 mAP | V2 train pose | V3 train pose | V2 val pose | V3 val pose | V2 P | V3 P | V2 R | V3 R |
|------:|-------:|-------:|--------------:|--------------:|------------:|------------:|-----:|-----:|-----:|-----:|
| 1 | 0.462 | 0.000 | 4.46 | 11.29 | 3.28 | 11.10 | 0.99 | 0.00 | 1.00 | 0.00 |
| 5 | 0.314 | 0.000 | 5.38 | 11.09 | 3.55 | 10.80 | 0.99 | 0.00 | 1.00 | 0.00 |
| 10 | 0.288 | 0.000 | 5.96 | 10.58 | 3.81 | 10.43 | 0.99 | 0.00 | 1.00 | 0.00 |
| 20 | 0.255 | 0.000 | 4.84 | 9.50 | 4.12 | 10.88 | 0.98 | 0.00 | 0.80 | 0.00 |
| 40 | 0.502 | 0.000 | 4.62 | 7.87 | 2.80 | 9.01 | 0.99 | 0.00 | 1.00 | 0.00 |
| 60 | 0.510 | 0.000 | 4.05 | 6.11 | 2.76 | 7.43 | 0.87 | 0.00 | 0.80 | 0.00 |
| 80 | 0.692 | 0.000 | 3.06 | 5.41 | 1.65 | 6.40 | 0.99 | 0.00 | 1.00 | 0.00 |
| 100 | 0.646 | 0.010 | 1.71 | 4.89 | 1.67 | 5.77 | 0.99 | 0.33 | 1.00 | 0.20 |

- **Première epoch de régression majeure V3 : epoch 1** (mAP V3≈0 vs V2≈0.46 à epoch 1)
- **Meilleur epoch V2 :** 80 (mAP **0.692**)
- **Meilleur epoch V3 :** 89 (mAP **0.039**)
- **Final V3 mAP :** 0.010

## 5. Prédictions finales (best.pt)

- Détections V2 : **26/26**
- Détections V3 : **22/26**
- B26_10 V2 : detected
- B26_10 V3 : missing

### Erreurs moyennes landmarks (px)

| Landmark | V2 | V3 |
|----------|----|----|
| ASL_R | 143.7950 | 954.5660 |
| ASL_L | 525.3992 | 583.6403 |
| ASM_L | 78.2313 | 628.6491 |
| FHC_L | 57.9570 | 183.4032 |
| FNM_L | 58.2199 | 122.5321 |

## 6. Interprétation des verdicts

| Code | Signification |
|------|---------------|
| A | Init correcte, fine-tuning trop agressif |
| B | Checkpoint V2 non réellement utilisé |
| C | Problème configuration / data |
| D | Autre cause identifiable |
| E | Artefacts insuffisants |

## Regénérer

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\audit_v3_regression_new_26.py
```
