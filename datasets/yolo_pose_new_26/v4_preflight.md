# V4 Pre-flight — YOLO Pose 16 keypoints (new_26)

**Genere :** 2026-08-29  
**Mode :** READ-ONLY preflight — **aucun entrainement lance**  
**Dataset QC :** `DATASET_16KP_READY_FOR_TRAINING` (B5)  
**Conclusion :** **`V4_PREFLIGHT_READY`**

---

## 1. Dataset — conformite B5 QC

Le dataset actuellement present correspond au lot valide par `b5_16kp_final_QC.md` / `.csv`.

| Controle | Resultat | Detail |
|----------|:--------:|--------|
| Images | **OK** | 26 (21 train / 5 val) |
| Keypoints | **OK** | 16 (`kpt_shape: [16, 3]`) |
| Colonnes label | **OK** | 53 (5 + 16x3) sur 26/26 labels |
| IT_R | **OK** | index **14** |
| IT_L | **OK** | index **15** |
| flip_idx | **OK** | `[1,0,3,2,5,4,7,6,9,8,11,10,13,12,15,14]` |
| data.yaml | **OK** | 16 KP, IT_R/IT_L presents |
| dataset.yaml | **OK** | identique schema 16 KP |
| meta/keypoint_order.md | **OK** | coherent |
| Anomalies | **OK** | aucune (QC B5) |

**Split officiel** (`meta/split.json`) : train 21 · val 5 — identique au QC B5.

---

## 2. Initialisation V4 — source V2 uniquement

| Element | Valeur |
|---------|--------|
| **Checkpoint source** | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` |
| **Epoch de reference** | **80** (pic mAP50-95 pose, mAP50-95(P) ~ 0.692) |
| **SHA256 (16 chars)** | `1f92d0867b4cd86e` |
| **Taille** | 5 947 464 bytes |
| **kpt_shape V2** | `[14, 3]` · nk = 42 |

### Exclus explicitement

| Source | Statut |
|--------|--------|
| V3 `best.pt` / `last.pt` | **NON utilise** (NO-GO officiel) |
| V1 | **NON utilise** |
| COCO `yolo11n-pose.pt` seul | **NON utilise** comme init |

**Copie init prevue (au lancement) :** `runs/pose/yolo_pose_new_26_v4_16kp/init/v2_best_mAP_epoch80.pt`  
→ copie bit-identique de V2 ; **V2 original jamais modifie**.

---

## 3. Point critique — transfert V2 14 KP → V4 16 KP

### Methode Ultralytics (probe experimentale, sans entrainement)

Ultralytics **ne charge pas** un checkpoint 14 KP tel quel pour entrainer en 16 KP.  
Chemin correct (valide par probe `PoseTrainer` + `PoseModel.load`) :

1. Reconstruire l'architecture **16 KP** depuis `yolo11n-pose.yaml` + `data.yaml` (`kpt_shape: [16,3]`).
2. Charger les poids V2 via `intersect_dicts` + `load_state_dict(strict=False)`.
3. Seules les tensors de **shape identique** sont copies.

**Log Ultralytics observe :**
```
Overriding model.yaml kpt_shape=[17, 3] with kpt_shape=[16, 3]
Transferred 505/541 items from pretrained weights
```

### Couches chargees depuis V2

| Bloc | Statut | Detail |
|------|:------:|--------|
| **Backbone** (layers 0-22) | **CHARGE** | poids compatibles |
| **Box head** (`cv2`) | **CHARGE** | match V2 |
| **Cls head** (`cv3`) | **CHARGE** | match V2 |
| **Pose head** (`cv4`) | **REINITIALISE** | shape mismatch 42 → 48 |

### Couches incompatibles / ignorees

Tous les tensors `model.23.cv4.*` du checkpoint V2 :

| Tensor V2 | Shape V2 | Shape V4 16 KP |
|-----------|----------|----------------|
| `cv4.{0,1,2}.0.conv.weight` | `(42, C, 3, 3)` | `(48, C, 3, 3)` |
| `cv4.{0,1,2}.2.weight` | `(42, 42, 1, 1)` | `(48, 48, 1, 1)` |
| BN / bias associes | `(42,)` | `(48,)` |

→ **36 tensors** pose head V2 **ignores** (pas de copie partielle — shape exacte requise).

### Consequences

| Question | Reponse |
|----------|---------|
| Pose head reinitialisee ? | **Oui** — entierement pour 16 KP |
| Box/cls/backbone conserves ? | **Oui** |
| Incompatibilite bloquante ? | **Non** — comportement attendu |
| Erreurs Ultralytics ? | **Aucune** |
| Warnings ? | Info : override kpt_shape depuis data.yaml |

### Strategie correcte

```
model      = yolo11n-pose.yaml
pretrained = runs/.../v2_best_mAP_epoch80.pt
data       = datasets/yolo_pose_new_26/data.yaml
```

**Ne pas** supposer que les 14 premiers keypoints du pose head V2 sont preserves dans cv4 — toute la tete pose est reapprenable, mais box/cls/backbone V2 restent intacts.

**Garde-fou epoch 0 :** comparer recall detection + box conf vs V2 sur 26 cas.

---

## 4. Configuration V4 proposee

Fichier : `datasets/yolo_pose_new_26/v4_training_config.yaml`

| Parametre | Valeur | Justification |
|-----------|--------|---------------|
| Architecture | **YOLO11n-pose** | identique V2 |
| Init | **V2 best epoch 80** | baseline clinique |
| `imgsz` | **960** | +50% vs V2 (640), pas x2 comme V3 |
| `batch` | **1** | CPU, RAM 16 GB |
| Optimizer | **AdamW** | fine-tuning stable |
| `lr0` | **3e-5** | milieu [1e-5, 5e-5] ; x3 plus bas que V3 |
| `warmup_epochs` | **4** | stabilise box/cls avant pose head |
| `mosaic` | **0** | anti-V3 |
| `auto_augment` | **null** | randaugment off |
| `erasing` | **0** | off |
| `fliplr` | **0.5** | flip_idx 16 KP valide |
| `cos_lr` | **false** | V3 avait true |
| `epochs` | **100** max | |
| `patience` | **20** | early stopping |
| Run | `runs/pose/yolo_pose_new_26_v4_16kp/` | |

---

## 5. Protection contre l'erreur V3

Reference : `v3_failure_diagnostic.md`

### Echec V3 documente

- mAP50(P) = **0** sur 60 epochs
- recall(B) val plafonne a **20%**
- conf box effondree @ conf=0.25 (3/26 cas)
- val/pose_loss ~**11** des epoch 1
- Init V2 OK → **fine-tuning destructeur**

### Facteurs V3 exclus en V4

| Facteur V3 | V4 |
|------------|-----|
| imgsz **1280** | **960** |
| cos_lr **true** | **false** |
| lr0 **1e-4** | **3e-5** |
| warmup **1** | **4** |
| evaluation mAP seule | pixel + recall + geometrie |

---

## 6. Plan d'evaluation post-training

### Metriques detection

- box detection recall
- mAP50
- mAP50-95

### Metriques pixel

- erreur moyenne / mediane / P90 (px)
- taux CORRECT / INCERTAIN / INCORRECT (75 / 150 px)

### Metriques geometriques cliniques

- FSP / FSD
- ASL
- IT_R / IT_L
- VCE
- Tonnis
- CCD

### Cas prioritaires

| Cas | Split | Note |
|-----|:-----:|------|
| **B26_01** | train | pilote IT |
| **B26_12** | train | reference stable V2 |
| **B26_13** | val | val set |
| **B26_26** | val | IT_R v=0 |

---

## 7. Pre-flight memoire

| Ressource | Valeur |
|-----------|--------|
| GPU NVIDIA | **Absent** (CPU only) |
| RAM totale | **15.9 GB** |
| Modele | YOLO11n-pose ~2.85M params |
| Config | imgsz=960, batch=1 |

**Verdict :** imgsz=960 batch=1 **raisonnable** sur cette machine CPU.

---

## 8. Fichiers crees

| Fichier | Role |
|---------|------|
| `v4_training_config.yaml` | hyperparametres |
| `v4_preflight.md` | ce rapport |
| `v4_preflight.csv` | matrice controles |
| `annotation_pilot/scripts/train_yolo_pose_v4_new_26.py` | script prep/train (**non execute**) |

---

## 9. Integrite

| Zone | Modifie ? |
|------|:---------:|
| Labels / YAML | **Non** |
| V2 / V3 | **Non** |
| Backend / Flutter | **Non** |
| Training | **Non lance** |

---

## Conclusion

**`V4_PREFLIGHT_READY`**

Dataset 16 KP valide, V2 localise, transfert 14→16 KP documente (505/541 layers, pose head reinit), configuration conservative anti-V3 prete. Entrainement via `--train` apres revue humaine uniquement.
