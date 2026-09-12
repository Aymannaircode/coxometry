# Plan V4 — fine-tuning doux depuis V2 (new_26)

**Généré :** 2026-08-23T21:37:48.964917+00:00
**Statut :** planification uniquement — **aucun entraînement lancé**
**Baseline officielle :** V2 (`runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/`)

---

## 1. Baseline officielle — V2

V2 reste le modèle de référence pour toute décision clinique ou technique.

| Métrique | Valeur |
|----------|--------|
| Checkpoint | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` |
| Meilleur epoch (mAP50-95 pose) | **80** |
| mAP50-95(P) best | **0.692** |
| mAP50-95(P) final (epoch 100) | 0.646 |
| ASL_L train / val | **538.18** / **471.72** px |
| ASL_R train / val | 142.86 / 147.73 px |
| ASM_L train / val | 77.59 / 80.94 px |
| Détections 26 cas | 26/26 |
| Dataset train / val | 21 / 5 images |

**Problème connu V2 :** ASL_L sous-appris (~538 px train) malgré labels et mapping corrects.
Tous les autres audits (géométrie, mapping, flip, couverture) sont **OK**.

---

## 2. Échec V3 — synthèse

| Métrique | V3 | vs V2 |
|----------|-----|-------|
| Diagnostic régression | **A** (init OK, fine-tuning destructeur) | — |
| mAP50-95(P) best (epoch 89) | 0.039 | −0.653 |
| mAP50-95(P) final | 0.010 | −0.636 |
| ASL_L train / val | 584 / 579 px | **pire** |
| ASL_R train | 952 px | **effondrement global** |
| ASM_L train | 615 px | **effondrement global** |
| Détections | 25/26 (B26_10 absent) | régression |

Run V3 conservé (non supprimé) : `runs/pose/yolo_pose_new_26_v3/`

---

## 3. Hypothèse principale

**Fine-tuning trop agressif** (verdict audit V3 = A), et non :

- erreur de checkpoint (init bit-identique à V2) ;
- inversion flip_idx (audit flip = D) ;
- labels / mapping incorrects (audits OK).

Facteurs identifiés :

1. **lr0 = 0.01** + AdamW auto (~0.002) — schedule « entraînement neuf » sur modèle convergé ;
2. **mosaic 1.0 → 0.0** — choc d'augmentation dès epoch 1 ;
3. **100 epochs** — sur-apprentissage / dérive prolongée ;
4. **pretrained=false** — sémantique Ultralytics inadaptée au fine-tuning ;
5. mAP agrégé masque l'échec ASL_L — validation pixel-level obligatoire.

---

## 4. Expérience V4 proposée — fine-tuning doux

### Objectif

Améliorer **ASL_L** (priorité) sans dégrader les 13 autres landmarks ni la géométrie,
en partant du **V2 best.pt** (pic mAP epoch 80).

### Init (lecture seule sur V2)

- Source : `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt`
- Copie init V4 : `runs/pose/yolo_pose_new_26_v4/init/v2_best_mAP_epoch80.pt`
- **Ne jamais modifier** le run V2 ni ses poids.

### Architecture & dataset (inchangés)

- **14 keypoints** : TD_R, TD_L, FHC_R, FHC_L, ASL_R, ASL_L, ASM_R, ASM_L, FNM_R, FNM_L, FSP_R, FSP_L, FSD_R, FSD_L
- **kpt_shape** : `[14, 3]`
- **flip_idx** : `[1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]` (validé par audit horizontal flip)
- **data** : `datasets/yolo_pose_new_26/data.yaml`
- **fliplr** : 0.5

### Hyperparamètres conservateurs proposés

| Param | V2 | V3 (échec) | **V4 proposé** | Rationale |
|-------|----|------------|----------------|-----------|
| lr0 | 0.01 | 0.01 | **0.0001** | ×100 plus bas — fine-tuning doux |
| lrf | 0.01 | 0.01 | 0.01 | decay final |
| optimizer | auto | auto | **AdamW** | explicite, lr contrôlé |
| warmup_epochs | 3 | 3 | **1.0** | warmup minimal |
| cos_lr | false | false | **True** | decay doux |
| epochs | 100 | 100 | **30** | limiter la dérive |
| patience | 100 | 25 | **10** | early stop si plateau |
| mosaic | 1.0 | 0.0 | **0.2** | réduction progressive, pas coupure brutale |
| auto_augment | randaugment | null | **null** | éviter bruit sur 21 images |
| erasing | 0.4 | 0.0 | **0.0** | idem |
| fliplr | 0.5 | 0.5 | **0.5** | conservé (flip_idx validé) |
| imgsz / batch | 640 / 2 | 640 / 2 | **640 / 2** | identique V2 |
| pose (loss gain) | 12.0 | 12.0 | **12.0** | inchangé initialement |

### Garde-fous pendant l'entraînement (implémentés dans `train_yolo_pose_v4_new_26.py`)

1. **Epoch 0 = checkpoint V2 best.pt** (copie init read-only) ;
2. **Validation epoch 0** : inférence sur 26 cas — les labels doivent correspondre à V2 (`predictions_v2/`) ;
3. **Après epoch 1** : comparaison pixel-level des 14 landmarks vs epoch 0 (pas vs mAP) ;
   - **Abandon** si dérive catastrophique : ≥1 landmark focus (ASL_R, ASM_L, ASM_R, FHC_L, FHC_R) dégradé de >25 % vs epoch 0 sur train ;
   - mAP50-95(P) reste **secondaire** pour ce garde-fou ;
4. Sauvegarder `results.csv` + best.pt dans `runs/pose/yolo_pose_new_26_v4/` ;
5. **Ne pas écraser V2 ni V3.**

---

## 5. Critères GO / NO-GO (obligatoires post-entraînement)

La décision **GO** (remplacer V2 par V4) exige **toutes** les conditions suivantes :

### 5.1 Pixel-level — 14 landmarks (priorité absolue)

Scripts : `compare_v2_v4_landmarks_new_26.py`, `test_v4_geometry_new_26.py`.

| Critère | Seuil | Baseline V2 |
|---------|-------|-------------|
| ASL_L train mean | baisse ≥ **20 %** | 538.18 px |
| ASL_L val mean | baisse ≥ **20 %** | 471.72 px |
| Autres 13 landmarks (train+val mean) | dégradation ≤ **25 %** chacun | voir V2 landmark analysis |
| Détections | **26/26** | 26/26 |

**NO-GO immédiat** si :

- ASL_L ne baisse pas de ≥20 % sur train **et** val ;
- ASL_R, ASM_L, ASM_R, FHC_L ou FHC_R augmente de >25 % ;
- moins de 26 détections ;
- un landmark médian > 300 px alors que V2 < 200 px.

### 5.2 Géométrie — VCE / Tönnis / CCD

Scripts : `test_v4_geometry_new_26.py` + comparaison vs `v2_geometry_results.csv`.

| Critère | Seuil NO-GO | V2 référence |
|---------|-------------|--------------|
| VCE_L négatifs | ≤ V2 (21/26) ou amélioration | 21/26 |
| Tönnis_L extrêmes | ≤ V2 (6/26) ou amélioration | 6/26 |
| CCD_L / CCD_R | pas de dérive > 20° vs V2 en médiane | — |

### 5.3 mAP (secondaire — ne pas décider sur mAP seul)

- mAP50-95(P) V4 ≥ V2 best − 0.05 (≥ 0.642) — **informatif seulement** ;
- un bon mAP avec ASL_L dégradé = **NO-GO** (leçon V2/V3).

### 5.4 Verdict final

| Résultat | Action |
|----------|--------|
| **GO** | V4 devient candidate ; revue manuelle des pires cas ASL_L |
| **NO-GO** | Conserver V2 ; archiver V4 ; documenter |
| **PARTIEL** | ASL_L ↓ mais autre landmark ↓ → NO-GO, analyser |

---

## 6. Pipeline post-V4 (à exécuter après entraînement futur)

Ordre strict :

1. `train_yolo_pose_v4_new_26.py` — fine-tuning doux (future) ;
2. `run_yolo_pose_inference_v4_new_26.py` — 26 DICOM → `predictions_v4/` ;
3. `test_v4_geometry_new_26.py` — VCE/Tönnis/CCD ;
4. `compare_v2_v4_landmarks_new_26.py` — 14 landmarks train/val ;
5. Rapport GO/NO-GO automatique → `v4_vs_v2_decision.md`.

---

## 7. Risques résiduels

- **21 images train** — variance élevée, un run peut échouer par hasard ;
- ASL_L peut rester difficile même avec LR bas (landmark intrinsèquement dur) ;
- mosaic=0.2 est un compromis conservateur — ajuster si epoch 1 stable mais ASL_L stagnant ;
- Envisager à terme : plus de données, focal loss keypoint, ou callback px/keypoint.

---

## 8. Fichiers de référence (lecture seule)

| Document | Contenu |
|----------|---------|
| `v3_regression_audit.md` | Verdict A, init V2 vérifié |
| `v3_vs_v2_landmark_comparison.md` | Pixel-level V2 vs V3 |
| `train_vs_val_landmark_analysis.md` | ASL_L train/val V2 |
| `horizontal_flip_audit.md` | flip_idx validé |
| `v2_training_behavior.md` | Courbes V2, epoch 80 best |

---

## 9. Commande de regénération de ce plan

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\prepare_v4_plan_new_26.py
```

**TRAINING: NOT RUN** — ce document est une planification uniquement.
