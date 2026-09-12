# Diagnostic echec V3 — new_26

**Genere :** 2026-08-28T19:21:27.667489+00:00
**Statut V3 :** NO-GO officiel
**Mode :** lecture seule — aucune modification du projet

## Conclusion executive

**Cause probable :** effondrement du fine-tuning des **tetes box/cls/pose** pendant l'entrainement V3 (mAP pose = 0 sur 60 epochs, val recall box = 20%, train cls_loss x10 vs V2). Le modele init (copie V2) etait sain ; la degradation est **progressive puis stabilisee en etat dysfonctionnel**.

**Configuration d'entrainement :** oui, le probleme vient **principalement de la configuration** (imgsz 1280 + batch 1 + lr/cos_lr + `pretrained=false` + changement d'echelle sans warmup adaptatif), pas du dataset/YAML/labels (identiques a V2).

**Recuperabilite :** V3 best/last **non recuperables** pour usage clinique. **V2 reste la base** ; une future tentative doit repartir de V2 best.pt (epoch 80), pas de V3.

---

## Objectif 1 — V3 produit-il zero detection ?

**Reponse : B**

| Seuil conf | Cas detectes / 26 |
|------------|------------------:|
| 0.25 | 3/26 |
| 0.1 | 10/26 |
| 0.01 | 26/26 |
| 0.001 | 26/26 |

A `conf=0.001` : **26/26** cas ont au moins 1 box.
Confiance box max observee (26 cas, conf=0.001) : **0.5887**

V3 **detecte** sur la majorite des images a bas seuil, mais les confiances restent **sous 0.25** sur ~23 cas → invisible au seuil production.

### Echantillon conf=0.001 (cas sans detection @ 0.25)

| Cas | n_boxes | box_conf max | kpt_conf max | kpt valid (>=0.25) |
|-----|--------:|-------------:|-------------:|-------------------:|
| B26_01 | 300 | 0.0812 | 0.9994 | 3533 |
| B26_12 | 300 | 0.2178 | 0.9999 | 3286 |
| B26_13 | 300 | 0.0351 | 0.9992 | 3616 |
| B26_05 | 300 | 0.4241 | 0.9999 | 2888 |
| B26_17 | 300 | 0.2579 | 0.9996 | 3718 |
| B26_10 | 300 | 0.0710 | 1.0000 | 3615 |

## Objectif 2 — Inspection training V3

Run : `runs\pose\yolo_pose_new_26_v3_anatomical-2`

### Configuration (args.yaml)

| Param | V2 | V3 |
|-------|----|----|
| init | yolo11n COCO -> V1 | **V2 best epoch 80** |
| imgsz | 640 | **1280** |
| batch | 2 | **1** |
| lr0 | 0.01 | **0.0001** |
| optimizer | auto | **AdamW** |
| cos_lr | false | **true** |
| pretrained | true | **false** |
| mosaic | 1.0 | **0** |

### Metriques training — V3 vs V2 (jalons)

| Metrique | V2 epoch 1 | V2 epoch 80 | V3 epoch 1 | V3 epoch 60 | V3 best epoch |
|----------|------------|-------------|------------|-------------|---------------|
| val/pose_loss | 3.283 | 1.652 | 11.022 | 10.855 | 10.871 @ ep 52 |
| mAP50(P) | 0.995 | 0.995 | 0.000 | 0.000 | 0.000 |
| mAP50-95(P) | 0.462 | 0.692 | 0.000 | 0.000 | 0.000 |
| recall(B) val | 1.000 | 1.000 | 0.000 | 0.200 | 0.200 |
| train/cls_loss | 0.379 | 0.391 | 10.651 | 6.324 | — |

**Observations cles :**

- V3 epoch **1** : val/pose_loss ~**11.0** (V2 ~3.3) — choc immediat post-init.
- **mAP50(P) = 0** sur **toutes** les 60 epochs.
- recall(B) val plafonne a **0.20** (1/5 images val) des epoch 37+.
- train/cls_loss ~**6-10** (V2 ~0.5) — tete classification/detection dysfonctionnelle.
- best.pt V3 selectionne sur mAP50-95(**B**) ~0.00065 (epoch 54), pas sur pose.

### Checkpoints

| Checkpoint | epoch | sha256 prefix | taille |
|------------|------:|---------------|-------:|
| V2_best | -1 | 1f92d0867b4cd86e | 5947464 |
| V3_init | -1 | 1f92d0867b4cd86e | 5947464 |
| V3_best | -1 | 11f6bbcae6254d9d | 6081288 |
| V3_last | -1 | ac1589ef3db0f15a | 6081288 |

V3 init vs V2 best : max diff = **0.000000** (copie initiale OK).
V3 init vs V3 best : max diff = **10.2283**
V3 init vs V3 last : max diff = **10.2283**
V3 best vs V3 last : max diff = **0.644531** (quasi identiques en fin de run).

## Objectif 3 — Comparaison detection V2 vs V3 (@ conf=0.25)

| Metrique | V2 | V3 |
|----------|---:|---:|
| Cas detectes / 26 | 26 | 3 |
| Box conf mean | 0.8864 | 0.4236 |
| Box conf max (sur cas detectes) | 0.9212 | 0.5887 |
| Rappel detection | 100.0% | 11.5% |

### Hypotheses evaluees

| # | Hypothese | Verdict |
|---|-----------|---------|
| 1 | Effondrement tete detection | **CONFIRME** — recall val 20%, conf box effondrees |
| 2 | Mauvais fine-tuning | **CONFIRME** — pertes cls/pose non convergentes |
| 3 | Learning rate | **CONTRIBUTEUR** — lr0=1e-4 + cos_lr + warmup 1 sur imgsz x2 |
| 4 | Initialisation | **EXCLU** — init = copie bit-identique V2 |
| 5 | imgsz=1280 | **CONTRIBUTEUR MAJEUR** — changement echelle sans adapter LR/batch/warmup |
| 6 | Augmentations | **PEU PROBABLE seul** — mosaic off ne explique pas mAP=0 des epoch 1 |
| 7 | Dataset/YAML | **EXCLU** — meme data.yaml, memes labels |
| 8 | pretrained=false | **CONTRIBUTEUR** — peut reset comportement optim despite loaded weights |

## Objectif 4 — Fine-tuning : degradation progressive ou brutale ?

| Etape | val/pose_loss | mAP50(P) | recall(B) |
|-------|-------------:|---------:|----------:|
| epoch 1 | 11.022 | 0.000 | 0.000 |
| epoch 5 | 10.952 | 0.000 | 0.000 |
| epoch 10 | 10.881 | 0.000 | 0.000 |
| epoch 20 | 10.930 | 0.000 | 0.000 |
| epoch 37 | 10.881 | 0.000 | 0.200 |
| epoch 54 | 10.871 | 0.000 | 0.200 |
| epoch 60 | 10.855 | 0.000 | 0.200 |

La val/pose_loss **explose des epoch 1** (~11 vs ~1.7 fin V2). Ce n'est pas une degradation lente en fin de run — c'est un **echec de fine-tuning des le demarrage**, puis 60 epochs sans recuperation (mAP pose reste 0).

## Objectif 5 — B26_01 (TRAIN) — echelle des checkpoints

| Checkpoint | conf | n_boxes | box_conf max | bbox area px | kpt valid |
|------------|-----|--------:|-------------:|-------------:|----------:|
| V2_best @ imgsz=640 | 0.25 | 1 | 0.8881 | 3399520 | 14 |
| V2_best @ imgsz=640 | 0.001 | 1 | 0.8881 | 3399520 | 14 |
| V3_init @ imgsz=1280 | 0.25 | 2 | 0.6655 | 1517306 | 26 |
| V3_init @ imgsz=1280 | 0.001 | 7 | 0.6655 | 1517306 | 94 |
| V3_best @ imgsz=1280 | 0.25 | 0 | NA | NA | 0 |
| V3_best @ imgsz=1280 | 0.001 | 300 | 0.0812 | 235882 | 3533 |
| V3_last @ imgsz=1280 | 0.25 | 0 | NA | NA | 0 |
| V3_last @ imgsz=1280 | 0.001 | 300 | 0.0809 | 367565 | 3518 |

B26_01 est dans le **train** mais V3 best/last **ne la detectent pas** @ conf=0.25. V2 la detecte avec conf ~0.89. V3 init (copie V2) devrait se comporter comme V2 **a imgsz=640** ; a imgsz=1280 sans retraining adapte, la detection peut deja diverger.

## Recommandations pour une prochaine tentative (sans lancer now)

### A changer

- Repartir de **V2 best.pt** (pas V3).
- Monter imgsz **graduellement** (640 -> 960 -> 1280) ou garder 640 d'abord.
- lr0 **plus bas** (1e-5 a 5e-5) avec warmup **3-5 epochs**.
- `pretrained=true` ou freeze backbone early epochs.
- Valider **pixel-level + recall detection** a chaque epoch, pas mAP seul.
- Early stop si recall val < 80% ou mAP50(P) chute vs init.
- Batch >= 2 si RAM permet, ou gradient accumulation.

### A conserver

- Dataset, labels, YAML, flip_idx, 14 keypoints.
- Split 21/5, annotations GT validees.
- mosaic=0, randaugment off pour fine-tune anatomique.
- V2 en production, refinement ASL_L separe.
