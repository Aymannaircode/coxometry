# V5 Phase 2 — Coordinate Space Consistency Audit

**Généré :** 2026-08-29  
**Mode :** READ-ONLY — aucun training, aucun checkpoint/label/YAML/script modifié  
**Modèle évalué :** `best_it.pt` (Phase 2 epoch 12)  
**Verdict :** `DECODER_PIPELINE_ERROR`

---

## Résumé exécutif

L'audit confirme à 100 % que :

1. **Le pipeline GT est cohérent** (label → LetterBox → batch → loss).
2. **La loss compare GT et pred dans le même espace** (grille, unités cellule).
3. **La métrique IT (`_decode_it_errors`) compare des espaces différents** : GT en px640, pred en grille sans `× stride`.
4. **Pas de second bug de scaling** identifié (delta GT batch vs label-recomputed < 0.34 px).

L'IT_mean_px ≈ 600 px est un **artéfact de métrique**, pas la vraie erreur géométrique (~247 px en px640).

---

## 1. GT — espaces de coordonnées

### 1.1 Format label `.txt`

- Format YOLO pose : `cls cx cy w h` + 16×(`x_norm y_norm v`)
- Coordonnées **normalisées [0,1] relativement à l'image PNG originale** (W×H du fichier)
- Ex. B26_10 IT_R : `(0.270484, 0.86019, v=2)` → orig `(822.0, 2258.0)` px sur 3039×2625

### 1.2 Preprocessing dataloader (val)

| Étape | Code | Espace résultant |
|-------|------|------------------|
| Chargement PNG | taille native (ex. 3039×2625) | pixels orig |
| **LetterBox** | `augment.py` L1605–1821, `new_shape=(640,640)`, `center=True`, `stride=32` | image 640×640 + padding |
| Instances update | denorm(orig) → scale(r) → add_padding(pad) | **pixels canvas 640** |
| **Format.normalize** | `augment.py` L2344–2346 : `keypoints[...,0]/=w; .../=h` | **norm [0,1] × 640** |
| `batch["keypoints"]` | shape `[1, 16, 3]` | norm640 |

**Letterbox B26_10 :** r=0.2106, pad_left=0, pad_top=43  
→ `gt_px640 = label_norm × orig_WH × r + pad` coïncide avec `batch_norm × 640` à **< 0.17 px**

### 1.3 GT dans la loss

Fichier : `ultralytics/utils/loss.py` — `v8PoseLoss.loss()` L675–687

```
batch_norm × imgsz(640,640)  →  px640
÷ stride_tensor[anchor]      →  grid (unités cellule)
```

---

## 2. Prédictions — IT head → kpts_decode

### 2.1 Sortie brute IT head

- Canaux **42–47** dans le tenseur `kpts` (48 ch total = 16 KP × 3)
- IT_R : ch 42–44 (x, y, vis) ; IT_L : ch 45–47
- Forme par anchor : `[48]` flat → reshape `[16, 3]`
- **Unités : offsets bruts** (ex. B26_10 IT_R raw : 0.631, -0.305)

### 2.2 kpts_decode()

Fichier : `ultralytics/utils/loss.py` L695–701

```python
y[..., :2] *= 2.0
y[..., 0] += anchor_points[:, [0]] - 0.5
y[..., 1] += anchor_points[:, [1]] - 0.5
```

- **Unités résultat : grille** (cell units, ~0–20 pour P5), **PAS pixels**
- Docstring « image coordinates » est **trompeuse** — cohérent avec loss (÷stride sur GT)

### 2.3 Strides et échelles

| Échelle | Stride | Grille | Anchors |
|---------|-------:|--------|--------:|
| P3 | 8 | 80×80 | 6400 |
| P4 | 16 | 40×40 | 1600 |
| P5 | 32 | 20×20 | 400 |

**Tous les anchors FG val (v=2) : P5, stride=32** (fg_idx ~8227–8247)

### 2.4 Conversion grille → px640

```
pred_px640 = pred_grid × stride_tensor[anchor]
```

Ex. B26_10 IT_R : grid (8.26, 11.39) × 32 → px640 **(264.4, 364.5)**

---

## 3. Loss — cohérence d'espace ✓

| Tensor | Transformation | Espace final |
|--------|----------------|--------------|
| **GT** | batch_norm × 640 → ÷ stride | **grille** |
| **Pred** | kpts_decode | **grille** |

`calculate_keypoints_loss()` L782–783 divise GT par stride **avant** comparaison OKS.

**Verdict loss : MÊME ESPACE — cohérent.**

---

## 4. Métrique IT — incohérence ✗

Fichier : `annotation_pilot/scripts/train_yolo_pose_v5_phase2.py`  
Fonction : `_decode_it_errors()` **L508–523**

| Tensor | Transformation | Espace final |
|--------|----------------|--------------|
| **GT** | `batch_norm × imgsz` | **px640** |
| **Pred** | `kpts_decode` seul | **grille** (pas de ×stride) |

```python
# L508-523 — bug
pred_dec = base.kpts_decode(anchor_points, pred_kpts.view(...))  # → grid
gk[..., 0] *= imgsz[1]; gk[..., 1] *= imgsz[0]                 # → px640
d = ||pred_dec[...,:2] - gt[...,:2]||                           # grid vs px640 !
```

**Verdict métrique : ESPACES DIFFÉRENTS.**

Multiplications/divisions auditées :

| Facteur | Loss GT | Loss Pred | Métrique GT | Métrique Pred |
|---------|:-------:|:---------:|:-----------:|:-------------:|
| × imgsz (640) | ✓ | — | ✓ | — |
| ÷ stride | ✓ | — | ✗ | ✗ |
| × stride | — | — | ✗ | **manquant** |
| letterbox pad/r | via dataloader | — | via dataloader | — |

---

## 5. Cas manuels

### B26_10 IT_R (stride=32, P5, anchor=[7.5, 12.5])

| Étape | x | y |
|-------|---:|---:|
| Label norm | 0.270484 | 0.860190 |
| GT orig (×3039×2625) | 822.00 | 2258.00 |
| batch norm | 0.270484 | 0.810445 |
| GT px640 (batch×640) | 173.11 | 518.69 |
| GT px640 (label→LB) | 173.11 | 518.52 |
| GT grid (loss) | 5.4097 | 16.2089 |
| Pred raw | 0.6312 | -0.3047 |
| Pred grid | 8.2625 | 11.3906 |
| Pred px640 (=grid×32) | 264.40 | 364.50 |
| Pred orig ((px640-pad)/r) | 1255.49 | 1526.62 |
| **Err A (actuelle)** | **533.4 px** | |
| **Err B (corrigée px640)** | **179.2 px** | |
| **Err C (orig)** | **850.2 px** | |

### B26_10 IT_L

| Étape | x | y |
|-------|---:|---:|
| Label norm | 0.649885 | 0.841905 |
| GT orig | 1975.00 | 2210.00 |
| GT px640 | 415.93 | 508.57 |
| Pred grid | 5.8724 | 11.7255 |
| Pred px640 | 187.92 | 375.22 |
| Err A | 644.2 px | Err B | 264.1 px |

### B26_13 IT_R

| Étape | x | y |
|-------|---:|---:|
| GT px640 | 176.52 | 490.50 |
| Pred grid | 8.8190 | 10.8654 |
| Pred px640 | 282.21 | 347.69 |
| Err A | 508.1 px | Err B | 177.7 px |

### B26_17 IT_R

| Étape | x | y |
|-------|---:|---:|
| GT px640 | 119.99 | 544.59 |
| Pred grid | 7.3167 | 11.4033 |
| Pred px640 | 234.13 | 364.91 |
| Err A | 545.0 px | Err B | 212.9 px |

### B26_20 IT_R

| Étape | x | y |
|-------|---:|---:|
| GT px640 | 163.02 | 545.46 |
| Pred grid | 8.2609 | 11.3961 |
| Pred px640 | 264.35 | 364.67 |
| Err A | 556.0 px | Err B | 207.2 px |

### B26_26 IT_L (IT_R v=0, exclu)

| Étape | x | y |
|-------|---:|---:|
| GT px640 | 453.13 | 497.79 |
| Pred grid | 5.7293 | 10.6328 |
| Pred px640 | 183.34 | 340.25 |
| Err A | 661.4 px | Err B | 312.4 px |

---

## 6. Test de consistance

| Formule | Description | Mean (px) |
|---------|-------------|----------:|
| **A (actuelle)** | `‖pred_grid − gt_px640‖` — `_decode_it_errors` | **604.32** |
| **B (corrigée)** | `‖pred_grid×stride − gt_px640‖` | **246.93** |
| **C (orig)** | `‖pred_orig − label_orig‖` | 1119.14 |

- **Ratio A/B = 2.45×** — cohérent avec mélange grid/px640 (pas un facteur stride pur car erreur euclidienne)
- **Max delta GT batch vs label→LB = 0.334 px** → pipeline GT confirmé, pas de second bug
- Formule C élevée car **le modèle prédit mal** (pas un bug de conversion orig)

**Pas de second problème de scaling identifié** au-delà du manque de `× stride` en métrique.

---

## 7. Conclusion : `DECODER_PIPELINE_ERROR`

| Champ | Valeur |
|-------|--------|
| **Fonction** | `train_yolo_pose_v5_phase2._decode_it_errors` |
| **Lignes** | 508–523 |
| **Espace attendu (pred)** | px640 (identique au GT métrique) |
| **Espace actuel (pred)** | grid cell units (post-`kpts_decode`) |
| **Transformation manquante** | `pred_dec[..., :2] *= stride_tensor[fg_mask]` |
| **Loss affectée ?** | **Non** — loss déjà cohérente en grille |
| **GT pipeline** | **Cohérent** (`COORDINATE_SPACE_CONFIRMED` pour GT) |

### Chaîne complète documentée

```
Label norm [0,1]×orig
    → LetterBox → batch norm [0,1]×640
        → Loss GT: ×640 ÷stride → GRID  ←──┐
        → Metric GT: ×640 → PX640          │  INCOHÉRENT
    → IT head raw offsets                   │
        → kpts_decode → GRID ──────────────┼── Loss pred (OK)
                                           └── Metric pred (BUG: pas ×stride)
```

CSV : `datasets/yolo_pose_new_26/v5_phase2_coordinate_space_audit.csv`
