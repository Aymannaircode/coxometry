# Plan d'entraînement YOLO Pose V3 — new_26

**Généré :** 2026-08-28  
**Statut :** configuration prête — **entraînement non lancé**  
**Mode :** fine-tuning anatomique depuis V2, run séparé, V2 intact

---

## Objectif

Améliorer la **précision pixel-level** des landmarks cliniques prioritaires :

1. FSP_R  
2. FSD_R  
3. FSP_L  
4. FSD_L  
5. ASL_R  
6. ASL_L  

Les annotations GT sont validées. L'overlay et la reprojection sont validés.  
La cause des erreurs E2E (ex. B26_01) est le **modèle YOLO**, pas les labels.

---

## Fichiers de configuration V3

| Fichier | Rôle |
|---------|------|
| `datasets/yolo_pose_new_26/v3_train_config.yaml` | Hyperparamètres reproductibles |
| `annotation_pilot/scripts/train_yolo_pose_v3_new_26.py` | Préparation + lancement (`--train`) |
| `runs/pose/yolo_pose_new_26_v3_anatomical/init/v2_best_mAP_epoch80.pt` | Copie init (créée à la préparation) |
| `runs/pose/yolo_pose_new_26_v3_anatomical/v3_train_config.md` | Snapshot auto des kwargs |

**Dataset :** `datasets/yolo_pose_new_26/data.yaml` (identique V2, **non modifié**)

---

## A. Justification de chaque paramètre V3

### Initialisation

| Paramètre | Valeur | Pourquoi |
|-----------|--------|----------|
| Source | V2 `best.pt` (epoch 80) | Meilleur mAP50-95 pose V2 (0.692) ; pose loss val ~1.65 |
| Copie locale | `init/v2_best_mAP_epoch80.pt` | **Ne jamais modifier** le fichier V2 original |
| Architecture | YOLO11n-pose (héritée) | Même tête 14 kpts ; pas de from-scratch |

### Résolution

| Paramètre | V2 | V3 | Pourquoi |
|-----------|----|----|----------|
| `imgsz` | 640 | **1280** | Images natives ~2900×2500 px ; V2 downscale ~4,5× masque l'axe diaphysaire (FSP/FSD) et le sourcil (ASL). 1280 ≈ 2,3× downscale — meilleur compromis détail / CPU |

### Fine-tuning / optimiseur

| Paramètre | V2 | V3 | Pourquoi |
|-----------|----|----|----------|
| `lr0` | 0.01 | **0.0001** | V3 précédent (lr0=0.01) a **détruit** les poids dès epoch 1 (mAP→0). Fine-tune depuis modèle convergé exige LR ×100 plus bas |
| `optimizer` | auto (~AdamW 0.002) | **AdamW** explicite | Reproductibilité |
| `cos_lr` | false | **true** | Décroissance douce en fin de run |
| `warmup_epochs` | 3.0 | **1.0** | Warmup court — modèle déjà warm-started |
| `epochs` | 100 | **60** | Fine-tune ciblé ; pas besoin de 100 epochs agressives |
| `patience` | 100 | **15** | Early stopping sur val loss ; évite sur-apprentissage tardif |
| `pretrained` | true | **false** | Checkpoint custom chargé via `YOLO(init.pt)` — pas de reset COCO |

### Batch / compute

| Paramètre | V3 | Pourquoi |
|-----------|-----|----------|
| `batch` | **1** (configurable → 2) | `imgsz=1280` sur CPU multiplie la RAM ~4× vs 640 ; batch=1 sécurise ; tester batch=2 si RAM OK |
| `device` | cpu | Contrainte environnement actuel (identique V2) |
| `workers` | 4 | Suffisant pour 26 images |
| `cache` | false | Évite pic RAM |

### Augmentations

| Paramètre | V2 | V3 | Pourquoi |
|-----------|----|----|----------|
| `mosaic` | 1.0 | **0.0** | Mosaic sur 21 images déforme les repères anatomiques localisés ; cause probable de confusion FSP/ASL |
| `auto_augment` | randaugment | **null** | Trop agressif pour petit lot médical |
| `erasing` | 0.4 | **0.0** | Efface des zones contenant sourcil / diaphyse |
| `fliplr` | 0.5 | **0.5** | Conservé — `flip_idx` validé (`horizontal_flip_audit.md`, verdict D : flip OK, pas cause ASL_L) |
| `flipud` | 0.0 | **0.0** | Radios AP : pas de flip vertical |
| `scale` | 0.5 | **0.2** | Variation taille réduite — repères fins |
| `translate` | 0.1 | **0.05** | Translation réduite |
| `hsv_*` | 0.015/0.7/0.4 | **0.01/0.4/0.3** | Légère variation photométrique seulement |
| `degrees/shear/perspective` | 0 | **0** | Pas de rotation — anatomie fixe AP |

### Loss pose

| Paramètre | V3 | Pourquoi |
|-----------|-----|----------|
| `pose` | 12.0 | Identique V2 — pas de surpondération par keypoint (Ultralytics ne le supporte pas nativement) |
| `kobj`, `box`, `cls`, `dfl` | identiques V2 | Stabilité |

### Dataset / keypoints

| Élément | Action |
|---------|--------|
| 14 keypoints | **Inchangés** — ordre MVP strict |
| Labels GT | **Non modifiés** |
| Split | **21 train / 5 val / 0 test** — identique V2 |
| `flip_idx` | `[1,0,3,2,5,4,7,6,9,8,11,10,13,12]` — inchangé |

---

## B. Tableau comparatif V2 vs V3

| Paramètre | V2 (production) | V3 (plan) | Δ |
|-----------|-----------------|-----------|---|
| Init | V1 best.pt | **V2 best.pt epoch 80** | ↑ |
| `imgsz` | 640 | **1280** | ↑ |
| `batch` | 2 | **1** (→2 si RAM) | ↓ |
| `epochs` | 100 | **60** | ↓ |
| `patience` | 100 | **15** | ↓ |
| `lr0` | 0.01 | **0.0001** | ↓↓ |
| `optimizer` | auto | **AdamW** | = |
| `cos_lr` | false | **true** | ↑ |
| `warmup_epochs` | 3 | **1** | ↓ |
| `mosaic` | 1.0 | **0.0** | ↓↓ |
| `auto_augment` | randaugment | **null** | ↓↓ |
| `erasing` | 0.4 | **0.0** | ↓↓ |
| `fliplr` | 0.5 | **0.5** | = |
| `scale` | 0.5 | **0.2** | ↓ |
| `translate` | 0.1 | **0.05** | ↓ |
| Run | `yolo_pose_new_26_v2-3` | **`yolo_pose_new_26_v3_anatomical`** | nouveau |
| Poids prod | `…v2-3/weights/best.pt` | `…v3_anatomical/weights/best.pt` | séparé |

**Note :** l'ancien run `runs/pose/yolo_pose_new_26_v3` (2026-08-23) est une **tentative échouée** (lr trop élevé). Le run V3 officiel planifié est `yolo_pose_new_26_v3_anatomical`.

---

## C. Comment V3 sera évalué

### Pipeline d'évaluation (post-training, read-only)

1. **Inférence 26 cas** avec `best.pt` V3 (script dédié à créer, sur le modèle de `run_yolo_pose_inference_new_26.py`) → `predictions_v3_anatomical/`
2. **Comparaison GT** via adaptateur `mvp_geometry` (même chemin que V2)
3. **Analyse train vs val** (même méthode que `analyze_v2_train_vs_val_new_26.py`)
4. **Cas de contrôle** :
   - **B26_01** (train, cas E2E Android)
   - **B26_12** (train, gold GT)
   - **B26_13** (val, gold GT)
5. **Audit anatomique E2E** sur B26_01 via pipeline `/analyze` (sans modifier backend)

### Métriques par landmark (26 cas, pixels natifs)

Pour chaque landmark, calculer sur l'ensemble **train+val** et par split :

| Métrique | Description |
|----------|-------------|
| **Mean** | Erreur euclidienne moyenne vs GT |
| **Median** | Robustesse aux outliers |
| **P90** | Queue haute — détecte échecs ponctuels graves |
| **Min / Max** | Plage |

### Taux de statut clinique (seuils E2E Android)

| Statut | Seuil (px) |
|--------|------------|
| **CORRECT** | ≤ 75 |
| **INCERTAIN** | 76 – 149 |
| **INCORRECT** | ≥ 150 |

Calculer le taux **CORRECT / INCERTAIN / INCORRECT** :
- globalement (14 landmarks × 26 cas)
- **par landmark prioritaire** (FSP/FSD/ASL)
- **par cas** (ex. B26_01 : objectif ≥ 10/14 CORRECT)

### Baseline V2 (référence actuelle)

Source : `train_vs_val_landmark_analysis.md`, `e2e_landmark_anatomical_audit_android.md`

| Landmark | V2 mean ~px | B26_01 final px |
|----------|------------:|----------------:|
| ASL_L | 525 | 153 (refined) / 481 raw |
| ASL_R | 144 | 231 |
| FSP_R | 151 | 419 |
| FSP_L | 170 | 274 |
| FSD_R | 159 | 306 |
| FSD_L | 108 | 245 |

---

## D. Critères de succès — V3 meilleur que V2 ?

### ❌ Insuffisant seul

- mAP50-95(P) ↑ sans amélioration pixel-level
- mAP50(P) ≈ 0.995 (non discriminant sur 5 val)
- val/pose_loss ↓ sans baisse erreur FSP/FSD/ASL

### ✅ V3 considéré meilleur si **tous** les critères suivants sont remplis

#### 1. Landmarks prioritaires (26 cas, train+val)

Pour **chaque** landmark parmi FSP_R, FSD_R, FSP_L, FSD_L, ASL_R, ASL_L :

| Critère | Seuil vs V2 |
|---------|-------------|
| Mean ↓ | **≥ 15 %** de réduction |
| Median ↓ | **≥ 10 %** de réduction |
| P90 ↓ | **≥ 15 %** de réduction |

#### 2. Taux CORRECT sur les 6 prioritaires

| Critère | Seuil |
|---------|-------|
| Taux CORRECT (≤75 px) | **≥ +10 points** vs V2 sur les 156 mesures (6 lm × 26 cas) |
| Taux INCORRECT (≥150 px) | **≤ −10 points** vs V2 |

#### 3. Cas E2E B26_01 (train)

| Landmark | V2 final px | Objectif V3 |
|----------|------------:|------------:|
| FSP_R | 419 | **≤ 150** (CORRECT ou INCERTAIN) |
| FSD_R | 306 | **≤ 150** |
| FSP_L | 274 | **≤ 150** |
| FSD_L | 245 | **≤ 150** |
| ASL_R | 231 | **≤ 150** |
| ASL_L | 153 (refined) | **≤ 75** raw YOLO (refinement inchangé) |

#### 4. Pas de régression majeure sur landmarks déjà bons

Sur ASM_L, ASM_R, FHC, TD, FNM (mean train+val) :

- Aucun landmark **> +25 %** de dégradation vs V2

#### 5. Stabilité train vs val

- Ratio val_mean / train_mean sur ASL_L **< 1.5** (pas de sur-apprentissage extrême)
- Pas de chute mAP → 0 dès epoch 1 (garde-fou régression V3)

---

## Emplacements prévus

| Élément | Chemin |
|---------|--------|
| V2 best (lecture seule) | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` |
| Init V3 (copie) | `runs/pose/yolo_pose_new_26_v3_anatomical/init/v2_best_mAP_epoch80.pt` |
| Run V3 | `runs/pose/yolo_pose_new_26_v3_anatomical/` |
| Poids V3 (post-training) | `runs/pose/yolo_pose_new_26_v3_anatomical/weights/best.pt` |
| Dataset YAML | `datasets/yolo_pose_new_26/data.yaml` |
| Prédictions V3 (futur) | `datasets/yolo_pose_new_26/predictions_v3_anatomical/` |

---

## Lancer la préparation (sans entraînement)

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v3_new_26.py
```

Vérifie : V2 best.pt, copie init, dataset YAML, 14 keypoints, split 21/5, hyperparamètres, emplacement run.

## Lancer l'entraînement (quand prêt)

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v3_new_26.py --train
```

**Durée estimée :** plusieurs heures sur CPU (imgsz 1280, 60 epochs, 26 images).

---

## Garde-fous recommandés avant validation production

1. Comparer epoch-0 V3 init vs prédictions V2 (identiques attendues)
2. Surveiller epoch 1 : si mAP50-95(P) < 0.1 → **stop** (régression type V3 2026-08-23)
3. Évaluer pixel-level à epoch 15, 30, 60 — pas seulement mAP
4. **Ne pas remplacer V2 en production** tant que critères §D non atteints
5. Ne pas modifier backend / refinement / Flutter avant validation V3

---

## Historique

| Date | Événement |
|------|-----------|
| 2026-08-23 | V3 v1 échoué (lr0=0.01, imgsz=640) — `v3_regression_audit.md` |
| 2026-08-28 | Audit config V2 — `yolo_training_config_audit.md` |
| 2026-08-28 | Plan V3 anatomical — ce document |

**Entraînement V3 : NON lancé.**
