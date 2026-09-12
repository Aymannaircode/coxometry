# Audit configuration entraînement YOLO Pose V2 — new_26

**Généré :** 2026-08-28T18:00:00+01:00  
**Mode :** lecture seule — aucun entraînement lancé, aucun fichier de production modifié.

## Synthèse exécutive

| Élément | Valeur |
|---------|--------|
| **Modèle production (V2)** | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` |
| **Chaîne d'init** | COCO `yolo11n-pose.pt` → V1 `best.pt` → V2 `best.pt` |
| **Architecture** | YOLO11n-pose (`nc=1`, `kpt_shape=[14,3]`) |
| **Dataset** | 26 images — train **21**, val **5**, test **0** |
| **Meilleure métrique V2** | mAP50-95(P) = **0.692 @ epoch 80** |
| **Échec clinique** | ASL_L ~525 px, FSP/FSD 150–420 px sur cas prioritaires malgré mAP élevé |
| **Fuite train/val** | **Aucune** détectée |
| **Cohérence keypoints** | **OK** partout (YAML = labels = MVP = flip_idx) |

**Recommandation finale :** **reconstruire une configuration V3** — ne pas conserver la config V2 telle quelle pour un futur retraining (voir §24).

---

## 1. Modèle de base utilisé pour V2

V2 est un **fine-tune de V1**, pas un départ direct depuis COCO.

| Étape | Checkpoint init | Run | Rôle |
|-------|-----------------|-----|------|
| **Pré-V1** | `yolo11n-pose.pt` (Ultralytics, poids COCO 17 kpts) | — | Transfer learning initial |
| **V1** | `yolo11n-pose.pt` | `runs/pose/runs/yolo_pose_new_26/` | Premier entraînement sur new_26 |
| **V2 (officiel)** | `runs/pose/runs/yolo_pose_new_26/weights/best.pt` | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/` | Fine-tune production |

Source : `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/args.yaml` → `model: .\runs\pose\runs\yolo_pose_new_26\weights\best.pt`

---

## 2. Architecture / variante YOLO

| Paramètre | Valeur |
|-----------|--------|
| Famille | **YOLO11** (Ultralytics 8.4.96) |
| Variante | **nano pose** — `yolo11n-pose.yaml` |
| Tâche | `pose` |
| Paramètres modèle | ~5,9 Mo (`best.pt` = 5 947 464 octets) |
| Head | Pose head COCO remappée → 14 keypoints custom (`cls_remap: true`) |

---

## 3. Nombre de classes

**1 classe** : `pelvis` (id `0`)

```yaml
names:
  0: pelvis
```

---

## 4. Nombre de keypoints

**14 keypoints** × 3 dimensions (x, y, visibilité) → `kpt_shape: [14, 3]`

Format label : **47 colonnes** = 5 (bbox) + 14×3 — vérifié sur les 26 fichiers `.txt`.

---

## 5. Ordre exact des 14 keypoints

| Index | Nom | Côté | ID source |
|------:|-----|------|-----------|
| 0 | TD_R | right | LM-01 |
| 1 | TD_L | left | LM-02 |
| 2 | FHC_R | right | LM-03 |
| 3 | FHC_L | left | LM-04 |
| 4 | ASL_R | right | LM-05 |
| 5 | ASL_L | left | LM-06 |
| 6 | ASM_R | right | LM-07 |
| 7 | ASM_L | left | LM-08 |
| 8 | FNM_R | right | LM-09 |
| 9 | FNM_L | left | LM-10 |
| 10 | FSP_R | right | LM-11 |
| 11 | FSP_L | left | LM-12 |
| 12 | FSD_R | right | LM-13 |
| 13 | FSD_L | left | LM-14 |

**Cohérence vérifiée (read-only) :**

| Source | Identique |
|--------|-----------|
| `datasets/yolo_pose_new_26/dataset.yaml` → `kpt_names` | ✅ |
| `datasets/yolo_pose_new_26/data.yaml` → `kpt_names` | ✅ |
| `datasets/yolo_pose_new_26/meta/keypoint_order.md` | ✅ |
| `mvp_geometry/landmarks.py` → `MVP_LANDMARK_NAMES` | ✅ |
| `annotation_pilot/manual_annotation_tool/server.py` → `LANDMARKS` | ✅ |
| `annotation_pilot/scripts/prepare_yolo_pose_new_26.py` → `KEYPOINT_NAMES` | ✅ |

---

## 6. Configuration dataset YAML

**Fichiers :** `datasets/yolo_pose_new_26/dataset.yaml` (V2 officiel) et `data.yaml` (alias V3, **contenu identique**).

```yaml
path: C:/Users/g/OneDrive/Desktop/Projet-Ayman/datasets/yolo_pose_new_26
train: images/train
val: images/val

kpt_shape: [14, 3]
flip_idx: [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]

names:
  0: pelvis

kpt_names:
  0: [TD_R, TD_L, FHC_R, FHC_L, ASL_R, ASL_L, ASM_R, ASM_L,
      FNM_R, FNM_L, FSP_R, FSP_L, FSD_R, FSD_L]
```

**Note :** pas de clé `test:` — split test absent du YAML et du disque.

**Génération :** `annotation_pilot/scripts/prepare_yolo_pose_new_26.py` (seed split = 42).

---

## 7. Nombre d'images train / validation / test

| Split | Images | Labels | Dossier |
|-------|-------:|-------:|---------|
| **Train** | **21** | 21 | `images/train/`, `labels/train/` |
| **Val** | **5** | 5 | `images/val/`, `labels/val/` |
| **Test** | **0** | — | dossier absent |
| **Total** | **26** | 26 | — |

---

## 8. Répartition des images

Split fixe (`meta/split.json`, seed=42, ratio val cible ≈ 19,2 %) :

**Train (21) :**  
B26_01, B26_02, B26_03, B26_04, B26_05, B26_06, B26_07, B26_08, B26_09, B26_11, B26_12, B26_14, B26_15, B26_16, B26_18, B26_19, B26_21, B26_22, B26_23, B26_24, B26_25

**Val (5) :**  
B26_10, B26_13, B26_17, B26_20, B26_26

**Résolutions natives (26 images) :**

| Stat | Largeur (px) | Hauteur (px) |
|------|-------------:|-------------:|
| Min | 2548 | 1975 |
| Max | 3234 | 3008 |
| Moyenne | ~2894 | ~2513 |

Exemple : B26_01 = **2730 × 2665 px**.

---

## 9. Résolution `imgsz` utilisée

**640 px** (côté le plus long, redimensionnement Ultralytics standard).

Rapport de downscale typique : ~**4,5×** par rapport aux images natives (~2900 px). Impact probable sur FSP/FSD (structures fines sur l'axe diaphysaire).

---

## 10. Epochs

**100 epochs** (V1 et V2).

V2 : entraînement complet jusqu'à epoch 100 ; meilleur checkpoint sélectionné à **epoch 80** (mAP50-95 pose).

---

## 11. Batch

| Run | Batch |
|-----|------:|
| V1 | **4** |
| V2 | **2** |

Device : **CPU** (`device: cpu`).

---

## 12. Optimizer

**`optimizer: auto`** → Ultralytics sélectionne **AdamW** avec LR effective ≈ **0,002** (batch=2, `nbs=64`, `lr0=0.01`).

Autres paramètres optim :

| Paramètre | Valeur |
|-----------|--------|
| `momentum` | 0.937 |
| `weight_decay` | 0.0005 |
| `warmup_epochs` | 3.0 |
| `warmup_momentum` | 0.8 |
| `warmup_bias_lr` | 0.1 |
| `cos_lr` | false (décroissance linéaire) |

---

## 13. Learning rate

| Paramètre | V1 | V2 |
|-----------|----|----|
| `lr0` | 0.01 | 0.01 |
| `lrf` | 0.01 | 0.01 |
| LR final (théorique) | 0.0001 | 0.0001 |
| `seed` | **42** | **0** |

**Observation V3 (historique) :** repartir de V2 convergé avec `lr0=0.01` a provoqué une régression immédiate (mAP50-95 pose ≈ 0 dès epoch 1). Un futur fine-tune nécessite un LR **nettement plus bas**.

---

## 14. Patience / early stopping

| Run | Patience | Effet |
|-----|----------|-------|
| V1 | **30** | early stopping possible |
| V2 | **100** | = nombre d'epochs → **pas d'arrêt anticipé** ; run complet 100 epochs |

`best.pt` V2 = checkpoint **epoch 80** (meilleur mAP50-95 pose), pas `last.pt` (epoch 100).

---

## 15. Augmentations

Configuration V2 (`args.yaml`) — **augmentations fortes** :

| Paramètre | V2 |
|-----------|-----|
| `mosaic` | **1.0** |
| `auto_augment` | **randaugment** |
| `erasing` | **0.4** |
| `fliplr` | **0.5** |
| `flipud` | 0.0 |
| `hsv_h` / `hsv_s` / `hsv_v` | 0.015 / 0.7 / 0.4 |
| `degrees` | 0.0 |
| `translate` | 0.1 |
| `scale` | 0.5 |
| `shear` | 0.0 |
| `perspective` | 0.0 |
| `mixup` / `cutmix` / `copy_paste` | 0.0 |
| `close_mosaic` | **10** (mosaic désactivé 10 dernières epochs) |
| `bgr` | 0.0 |

**Risque identifié :** mosaic + randaugment + erasing sur **21 images** déforme fortement les repères ASL/FSP/FSD (structures localisées, parfois proches les unes des autres).

`flip_idx` cohérent avec paires R/L — audit flip : `datasets/yolo_pose_new_26/horizontal_flip_audit.md`.

---

## 16. Pretrained ou entraînement from scratch

| Run | `pretrained` | Interprétation |
|-----|--------------|----------------|
| V1 | **true** | Fine-tune depuis COCO `yolo11n-pose.pt` |
| V2 | **true** | Fine-tune depuis V1 `best.pt` (poids déjà adaptés à 14 kpts) |

V2 **n'est pas** un entraînement from scratch.

---

## 17. Poids initiaux utilisés

| Run | Poids init | Chemin absolu |
|-----|------------|---------------|
| V1 | COCO pretrained | `yolo11n-pose.pt` (téléchargé Ultralytics, hors repo) |
| V2 | V1 best | `C:\Users\g\OneDrive\Desktop\Projet-Ayman\runs\pose\runs\yolo_pose_new_26\weights\best.pt` |

**Poids V2 production (sortie) :**

```
C:\Users\g\OneDrive\Desktop\Projet-Ayman\runs\pose\runs\pose\runs\yolo_pose_new_26_v2-3\weights\best.pt
```

Taille : 5 947 464 octets.  
Artefact complémentaire : `last.pt` (epoch 100, même taille).

---

## 18. Workers / cache

| Paramètre | V1 | V2 |
|-----------|----|----|
| `workers` | 4 | **8** |
| `cache` | false | false |
| `amp` | true | true |
| `deterministic` | true | true |
| `fraction` | 1.0 | 1.0 |

Pas de cache disque/RAM des images.

---

## 19. Paramètres spécifiques pose

| Paramètre | Valeur | Rôle |
|-----------|--------|------|
| `task` | pose | — |
| `pose` | **12.0** | Gain loss keypoints |
| `kobj` | **1.0** | Gain loss objectness keypoints |
| `box` | **7.5** | Gain loss bbox |
| `cls` | 0.5 | Gain loss classe |
| `dfl` | 1.5 | Distribution focal loss |
| `dis` | 6.0 | Distance OKS (pose) |
| `overlap_mask` | true | — |
| `mask_ratio` | 4 | — |
| `kpt_shape` | [14, 3] | via YAML |
| `flip_idx` | [1,0,3,2,5,4,7,6,9,8,11,10,13,12] | via YAML |

Pas de pondération par keypoint (ASL/FSP/FSD non surpondérés).

---

## 20. Métriques obtenues par V2

### Métriques Ultralytics agrégées (`results.csv`, run v2-3)

| Métrique | Epoch 80 (best) | Epoch 100 (last) |
|----------|----------------:|-----------------:|
| **mAP50-95(P)** | **0.692** | 0.646 |
| mAP50(P) | 0.995 | 0.995 |
| precision(P) | 0.991 | 0.990 |
| recall(P) | 1.000 | 1.000 |
| val/pose_loss | 1.652 | 1.672 |
| train/pose_loss | 3.065 | 1.706 |
| mAP50-95(B) | 0.824 | — |

### Métriques V1 (référence)

| Métrique | Best (epoch 97) |
|----------|----------------:|
| mAP50-95(P) | 0.388 |
| mAP50(P) | 0.995 |
| val/pose_loss | 3.414 |

V2 améliore fortement le mAP agrégé vs V1, mais **masque** les échecs landmark-level.

### Erreurs pixel-level post-entraînement (V2 vs GT, 26 cas)

Source : `datasets/yolo_pose_new_26/train_vs_val_landmark_analysis.md`, `predictions_v2/`

| Landmark | Train mean (px) | Val mean (px) | Global ~mean |
|----------|----------------:|--------------:|-------------:|
| ASL_R | 142.9 | 147.7 | ~144 |
| **ASL_L** | **538.2** | **471.7** | **~525** |
| FSP_R | 156.4 | 127.6 | ~151 |
| FSP_L | 164.6 | 192.8 | ~170 |
| FSD_R | 154.3 | 181.0 | ~159 |
| FSD_L | 93.7 | 168.2 | ~108 |
| ASM_L (réf.) | 77.6 | 80.9 | ~78 |

### E2E B26_01 (cas train, audit Android 2026-08-28)

| Landmark | Erreur finale vs GT |
|----------|-------------------:|
| FSP_R | **419 px** |
| FSD_R | **306 px** |
| FSP_L | **274 px** |
| FSD_L | **245 px** |
| ASL_R | **231 px** |
| ASL_L | **153 px** (après refinement ; raw ~481 px) |

**Point critique :** B26_01 est dans le **train** — l'échec n'est pas une simple généralisation val.

---

## 21. Emplacement exact des poids V2

| Artefact | Chemin |
|----------|--------|
| **Production `best.pt`** | `C:\Users\g\OneDrive\Desktop\Projet-Ayman\runs\pose\runs\pose\runs\yolo_pose_new_26_v2-3\weights\best.pt` |
| `last.pt` | `...\yolo_pose_new_26_v2-3\weights\last.pt` |
| Config run | `...\yolo_pose_new_26_v2-3\args.yaml` |
| Courbes / métriques | `...\yolo_pose_new_26_v2-3\results.csv`, `results.png`, `Pose*.png` |
| Référence backend | `backend/app/services/detection/yolo_pose.py` |

---

## 22. Scripts exacts utilisés pour lancer V2

### Préparation dataset (amont, reproductible)

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\prepare_yolo_pose_new_26.py
```

Produit : images, labels, `dataset.yaml`, `meta/split.json`, `meta/keypoint_order.md`.

### Entraînement V1 et V2 — **aucun script dédié dans le repo**

Les runs V1/V2 ont été lancés via l'**API Ultralytics** (ou CLI équivalente).  
Preuve : `args.yaml` dans chaque run ; pas de `train_yolo_pose_v2_new_26.py`.

**V1 — commande équivalente reconstruite** (`runs/pose/runs/yolo_pose_new_26/args.yaml`) :

```python
from ultralytics import YOLO
model = YOLO("yolo11n-pose.pt")
model.train(
    data="C:/Users/g/OneDrive/Desktop/Projet-Ayman/datasets/yolo_pose_new_26/dataset.yaml",
    epochs=100, imgsz=640, batch=4, patience=30, device="cpu",
    workers=4, project="runs", name="yolo_pose_new_26",
    pretrained=True, seed=42,
)
```

**V2 officiel (v2-3) — commande équivalente reconstruite** :

```python
from ultralytics import YOLO
model = YOLO(r"runs/pose/runs/yolo_pose_new_26/weights/best.pt")
model.train(
    data=r"datasets/yolo_pose_new_26/dataset.yaml",
    epochs=100, imgsz=640, batch=2, patience=100, device="cpu",
    workers=8, project=r"runs/pose/runs", name="yolo_pose_new_26_v2-3",
    pretrained=True, seed=0,
)
# Augmentations par défaut Ultralytics conservées (mosaic=1, randaugment, etc.)
```

**Tentatives intermédiaires V2 (non retenues) :**

| Run | `args.yaml` présent | `results.csv` / poids |
|-----|--------------------|-----------------------|
| `yolo_pose_new_26_v2` | ✅ | ❌ (run aborté) |
| `yolo_pose_new_26_v2-2` | ✅ | ❌ (run aborté) |
| **`yolo_pose_new_26_v2-3`** | ✅ | ✅ **officiel** |

### Scripts post-entraînement (analyse / inférence, read-only)

| Script | Rôle |
|--------|------|
| `annotation_pilot/scripts/run_yolo_pose_inference_new_26.py` | Inférence V2 → `predictions_v2/` |
| `annotation_pilot/scripts/analyze_v2_train_vs_val_new_26.py` | Erreurs px train vs val |
| `annotation_pilot/scripts/analyze_v2_training_behavior_new_26.py` | Analyse courbes V2 |

### Scripts V3/V4 (tentatives ultérieures, **non production**)

- `annotation_pilot/scripts/train_yolo_pose_v3_new_26.py`
- `annotation_pilot/scripts/train_yolo_pose_v4_new_26.py`

---

## 23. Vérifications intégrité dataset / convention

### Fuite train / val / test

| Contrôle | Résultat |
|----------|----------|
| `train ∩ val` (split.json) | **∅** (0 cas) |
| split.json vs filesystem | **100 % concordant** (21 train, 5 val) |
| Dossier test | **Absent** — pas de hold-out indépendant |
| Duplicats inter-split | **0** |

### B26_01 dans le split attendu

| Cas | Split officiel | Fichiers présents |
|-----|----------------|-------------------|
| **B26_01** | **train** | `images/train/B26_01.png`, `labels/train/B26_01.txt` |

Cohérent avec `meta/split.json`. L'audit E2E B26_01 mesure donc un **échec de mémorisation / apprentissage** sur un cas d'entraînement.

### B26_12 et B26_13 comme références qualité

| Cas | Split | Flags annotation (audit 2026-08-28) | Usage recommandé |
|-----|-------|-------------------------------------|------------------|
| **B26_12** | train | **0 flag géométrique** | Gold standard train |
| **B26_13** | val | **0 flag géométrique** | Gold standard val |

Source : `datasets/yolo_pose_new_26/landmark_annotation_quality_audit.md`

Erreurs V2 sur ces cas (prédictions existantes) :

| Cas | ASL_L (px) | FSP_R (px) | FSP_L (px) |
|-----|----------:|----------:|----------:|
| B26_12 (train) | 670.7 | — | — |
| B26_13 (val) | 412.4 | — | — |

Les GT sont propres ; les erreurs restent **modèle**, pas annotation.

### Ordre des 14 keypoints — cohérence globale

✅ Identique dans YAML, labels, JSON MVP, adaptateur `mvp_geometry`, outil d'annotation.

### Labels YOLO vs YAML — même convention

| Élément | Statut |
|---------|--------|
| `kpt_shape [14,3]` | ✅ |
| `flip_idx` paires R/L | ✅ |
| Visibilité MVP `v=2` → YOLO `v=2`, coords normalisées | ✅ |
| Labels 47 cols / 26 fichiers | ✅ |
| JSON ↔ label YOLO | **0 px** d'écart (audit annotations) |
| `dataset.yaml` vs `data.yaml` | **0 écart** |

---

## 24. Comparaison config actuelle vs besoins FSP / FSD / ASL

### Besoins du problème (landmarks prioritaires)

| Landmark | Difficulté | Exigence clinique | Erreur V2 typique |
|----------|------------|-------------------|-------------------|
| **ASL_L** | Très haute | Sourcil latéral, proche ASM en x | **~525 px** — confusion systématique avec ASM_L |
| **ASL_R** | Haute | Même structure, autre côté | ~144 px |
| **FSP_R/L** | Haute | Point fin sur axe diaphysaire proximal | ~151–170 px ; **419 px** sur B26_01 |
| **FSD_R/L** | Haute | Point distal dans FOV, souvent bord image | ~108–159 px ; **306 px** sur B26_01 |

Les **annotations GT sont validées** (52/52 ASL, 52/52 FSP, FSD conforme) — le gap est **capacité modèle + config training**, pas labels.

### Adéquation de la config V2

| Aspect config V2 | Adéquat pour FSP/FSD/ASL ? | Commentaire |
|--------------------|----------------------------|-------------|
| Variante YOLO11n (nano) | ⚠️ Limite | Capacité réduite pour 14 repères fins sur radiographies ~2900 px |
| `imgsz=640` | ❌ Insuffisant | Downscale ~4,5× ; perte de détail diaphysaire / sourcil |
| `mosaic=1` + `randaugment` + `erasing=0.4` | ❌ Contre-productif | 21 images train — déformations excessives pour repères anatomiques localisés |
| `lr0=0.01` (fine-tune V2) | ⚠️ Acceptable pour V1→V2 | Trop élevé pour fine-tune ultérieur (preuve V3) |
| Val = 5 images | ❌ Peu fiable | mAP50(P)≈0.995 dès epoch 1 — métrique non discriminante |
| Pas de métrique px/keypoint en training | ❌ Manque | mAP masque l'échec ASL_L |
| `pose=12.0` uniforme | ⚠️ Neutre | Pas de focalisation ASL/FSP/FSD |
| `fliplr=0.5` + `flip_idx` correct | ✅ OK | Mapping R/L validé |
| Split sans fuite | ✅ OK | — |
| GT annotations | ✅ OK | Dataset utilisable tel quel |

### Leçons V3 (tentative documentée, non production)

Réduction naïve des augmentations **sans** baisser le LR → régression catastrophique (mAP50-95 pose **0.039** best).  
Toute V3 doit combiner : **LR bas**, **augmentations modérées**, **init depuis epoch 80**, **validation px/keypoint**.

---

## 25. Recommandation

### ❌ Ne pas conserver la configuration V2 telle quelle

Raisons :

1. Échec **train+val** sur ASL_L (~525 px) malgré mAP50-95(P)=0.692.
2. Échec **train** sur B26_01 pour FSP/FSD (274–419 px) — GT validé.
3. Augmentations agressives inadaptées à 21 images et repères fins.
4. `imgsz=640` probablement sous-dimensionné pour l'axe fémoral.
5. Métriques Ultralytics **non corrélées** à la qualité clinique sur ce petit val set.
6. V3 naïf a montré que les ajustements doivent être **co-conçus** (LR + aug + init).

### ⚠️ Modifier certains paramètres seul — insuffisant

Ajuster un seul levier (ex. désactiver mosaic seul, comme V3) **sans** LR bas et sans métrique px/keypoint a déjà échoué.

### ✅ Reconstruire une configuration V3 (recommandé)

Proposition de principes (sans lancer d'entraînement maintenant) :

| Levier | Direction V3 suggérée |
|--------|----------------------|
| Init | Checkpoint V2 **epoch 80** (`best.pt` actuel) |
| LR | **≤ 1e-4 – 1e-3** (fine-tune), warmup court |
| Augmentations | Mosaic **0**, randaugment **off**, erasing **0** ; conserver `fliplr=0.5` |
| Résolution | Tester **imgsz 960–1280** (compromis CPU / détail) |
| Modèle | Envisager **YOLO11s-pose** si budget compute |
| Validation | **Métrique px/keypoint** (FSP/FSD/ASL) à chaque N epochs |
| Early stopping | Patience **15–25** sur métrique px priorités, pas mAP seul |
| Split | Conserver split actuel ; B26_12/B26_13 comme cas de contrôle |

**Statut actuel :** le modèle V2 en production reste inchangé ; cet audit prépare uniquement la décision de retraining futur.

---

## 26. Artefacts consultés (read-only)

- `runs/pose/runs/yolo_pose_new_26/args.yaml`, `results.csv`
- `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/args.yaml`, `results.csv`
- `datasets/yolo_pose_new_26/dataset.yaml`, `data.yaml`, `meta/split.json`
- `datasets/yolo_pose_new_26/v2_training_behavior.md`
- `datasets/yolo_pose_new_26/train_vs_val_landmark_analysis.md`
- `datasets/yolo_pose_new_26/landmark_annotation_quality_audit.md`
- `datasets/yolo_pose_new_26/e2e_landmark_anatomical_audit_android.md`
- `datasets/yolo_pose_new_26/v3_regression_audit.md`

**Aucun entraînement lancé. Aucun fichier de production modifié.**
