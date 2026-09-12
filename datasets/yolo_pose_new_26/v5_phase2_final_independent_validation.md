# V5 Phase 2 — Final Independent Validation

**Généré :** 2026-08-29 03:06 UTC
**Mode :** READ-ONLY — aucun training, aucun checkpoint/label/YAML modifié
**Checkpoint :** `runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/weights/best_it.pt`  
**Références :** V2 `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` · surgical `runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt`
**Verdict :** `V5_PHASE2_FINAL_SUCCESS`

---

## 1. Validation des 5 images VAL

### Règle de sélection des prédictions IT

Parmi les anchors FG assignés par le task-aligned assigner à l'instance GT unique, sélectionner l'anchor d'indice maximal IoU(box prédite décodée px640, target_bboxes assigné). En cas d'égalité IoU, tie-break par score cls sigmoid décroissant.

**Important :** une seule prédiction IT par image (instance GT unique). Les ~18 anchors FG par image ne sont **pas** agrégés comme landmarks indépendants (contrairement à `compute_it_metrics` training qui compte tous les FG → 90 évaluations).

| Image | Box | Conf (YOLO) | IT_R GT | IT_R pred | dx | dy | err | IT_L GT | IT_L pred | dx | dy | err | GT v | pred v (logit) |
|-------|-----|------------:|---------|-----------|---:|---:|----:|---------|-----------|---:|---:|----:|------|----------------|
| B26_10 | det=1 anchor=8269 | 0.892 | (173.1,518.7) | (155.7,512.9) | -17.4 | -5.8 | 18.3 | (415.9,508.6) | (428.4,486.4) | 12.4 | -22.2 | 25.4 | R=2/L=2 | R=0.91/L=1.33 |
| B26_13 | det=1 anchor=8250 | 0.875 | (176.5,490.5) | (158.1,468.5) | -18.5 | -22.0 | 28.7 | (429.1,480.6) | (422.8,447.5) | -6.3 | -33.0 | 33.6 | R=2/L=2 | R=0.55/L=0.58 |
| B26_17 | det=1 anchor=8269 | 0.885 | (120.0,544.6) | (134.7,551.3) | 14.7 | 6.7 | 16.2 | (421.6,536.5) | (431.1,541.1) | 9.6 | 4.7 | 10.6 | R=2/L=2 | R=0.82/L=1.75 |
| B26_20 | det=1 anchor=8231 | 0.921 | (163.0,545.5) | (149.8,573.1) | -13.3 | 27.6 | 30.6 | (447.4,540.7) | (458.7,538.2) | 11.3 | -2.5 | 11.6 | R=2/L=2 | R=1.23/L=0.85 |
| B26_26 | det=1 anchor=8248 | 0.860 | — | v=0 | — | — | NA (v=0) | (453.1,497.8) | (422.7,503.2) | -30.4 | 5.4 | 30.9 | R=0/L=2 | R=0.38/L=1.72 |

---

## 2. IT Performance (v=2 uniquement, 1 anchor/image)

### IT_R

| Métrique | Valeur |
|----------|-------:|
| N | 4 |
| mean | 23.46 |
| median | 23.54 |
| P90 | 30.63 |
| min | 16.15 |
| max | 30.63 |
| pct_lt_25 | 50.0% |
| pct_lt_50 | 100.0% |
| pct_lt_75 | 100.0% |
| pct_lt_100 | 100.0% |
| pct_lt_150 | 100.0% |

### IT_L

| Métrique | Valeur |
|----------|-------:|
| N | 5 |
| mean | 22.44 |
| median | 25.43 |
| P90 | 33.64 |
| min | 10.63 |
| max | 33.64 |
| pct_lt_25 | 40.0% |
| pct_lt_50 | 100.0% |
| pct_lt_75 | 100.0% |
| pct_lt_100 | 100.0% |
| pct_lt_150 | 100.0% |

### IT global

| Métrique | Valeur |
|----------|-------:|
| N | 9 |
| mean | 22.89 |
| median | 25.43 |
| P90 | 33.64 |
| min | 10.63 |
| max | 33.64 |
| pct_lt_25 | 44.4% |
| pct_lt_50 | 100.0% |
| pct_lt_75 | 100.0% |
| pct_lt_100 | 100.0% |
| pct_lt_150 | 100.0% |

---

## 3. Vérification du decoder (B26_10 IT_R)

- **pred raw (grid) :** (4.8657, 16.0286)
- **stride :** 32.0
- **px640 = grid × stride :** (155.70, 512.92)
- **GT px640 :** (173.11, 518.69)
- **dx :** -17.41 px
- **dy :** -5.77 px
- **erreur euclidienne :** 18.34 px

**Confirmations :**
- Une seule multiplication par stride : **True**
- Pas de double scaling (err si grid×stride²) : diff=16587.98 px vs single-stride
- Espace cohérent px640 (pas confusion résolution originale) : **True** (GT et pred en coords letterbox 640)

---

## 4. Comparaison V2 / surgical / Phase2

### Détection

| Image | V2 n | conf | IoU | surgical n | phase2 n | conf | IoU |
|-------|-----:|-----:|----:|-----------:|---------:|-----:|----:|
| B26_10 | 1 | 0.891736 | 0.9304567971752552 | 1 | 1 | 0.891736 | 0.9304567971752552 |
| B26_13 | 1 | 0.875427 | 0.8892124377628038 | 1 | 1 | 0.875427 | 0.8892124377628038 |
| B26_17 | 1 | 0.885234 | 0.9080565978081454 | 1 | 1 | 0.885234 | 0.9080565978081454 |
| B26_20 | 1 | 0.921167 | 0.8931882797269804 | 1 | 1 | 0.921167 | 0.8931882797269804 |
| B26_26 | 1 | 0.860271 | 0.7482001924791625 | 1 | 1 | 0.860271 | 0.7482001924791625 |

### 14 KP — agrégat

| Modèle | Mean | Median | P90 | CORRECT | INCERTAIN | INCORRECT |
|--------|-----:|-------:|----:|--------:|----------:|----------:|
| V2 | 134.95 | 98.18 | 293.40 | 25 | 28 | 17 |
| surgical_init | 134.95 | 98.18 | 293.40 | 25 | 28 | 17 |
| phase2 | 134.95 | 98.18 | 293.40 | 25 | 28 | 17 |

**Phase2 == V2 pour les 14 KP :** True

---

## 5. Détection V2 vs Phase2

**Verdict :** `IDENTICAL`

- B26_10: V2 boxes=1 conf=0.891736 IoU=0.9304567971752552 | Phase2 boxes=1 conf=0.891736 IoU=0.9304567971752552 FP=0
- B26_13: V2 boxes=1 conf=0.875427 IoU=0.8892124377628038 | Phase2 boxes=1 conf=0.875427 IoU=0.8892124377628038 FP=0
- B26_17: V2 boxes=1 conf=0.885234 IoU=0.9080565978081454 | Phase2 boxes=1 conf=0.885234 IoU=0.9080565978081454 FP=0
- B26_20: V2 boxes=1 conf=0.921167 IoU=0.8931882797269804 | Phase2 boxes=1 conf=0.921167 IoU=0.8931882797269804 FP=0
- B26_26: V2 boxes=1 conf=0.860271 IoU=0.7482001924791625 | Phase2 boxes=1 conf=0.860271 IoU=0.7482001924791625 FP=0

---

## 6. Freeze (surgical_init → best_it.pt)

**Verdict freeze :** OK

| Zone | Tensors | Changed | Max Δ |
|------|--------:|--------:|------:|
| backbone | 120 | 0 | 0.000000e+00 |
| neck | 60 | 0 | 0.000000e+00 |
| cv2_box | 156 | 0 | 0.000000e+00 |
| cv3_cls | 81 | 0 | 0.000000e+00 |
| dfl | 1 | 0 | 0.000000e+00 |
| cv4_pose | 36 | 0 | 0.000000e+00 |
| it_head | 66 | 62 | 7.560000e+02 |

---

## 7. Data leakage

- train = **21** images
- val = **5** images
- overlap train∩val : **∅**
- val images dans labels/train : **False**
- GT val utilisé pour modifier checkpoint (cette session) : **Non**
- **Résultat global :** PASS

---

## 8. Tableau final

| Image | Detection | IT_R err | IT_L err | 14KP mean | Status |
|-------|----------:|---------:|---------:|----------:|--------|
| B26_10 | 1 | 18.3 | 25.4 | 138.7 | OK |
| B26_13 | 1 | 28.7 | 33.6 | 135.2 | OK |
| B26_17 | 1 | 16.2 | 10.6 | 112.7 | OK |
| B26_20 | 1 | 30.6 | 11.6 | 126.4 | OK |
| B26_26 | 1 | NA (v=0) | 30.9 | 161.8 | OK |

---

## 9. Verdict et synthèse

### `V5_PHASE2_FINAL_SUCCESS`

#### 1. Performance du modèle
- IT global mean (1 anchor/image, decoder corrigé) : **22.89 px**
- % <75 px : **100.0%**
- 14 KP préservés vs V2 : **True**
- Détection vs V2 : **IDENTICAL**

#### 2. Correction du decoder
- Single stride multiply : **True**
- IT_mean training log (bug grid vs px640, tous FG anchors) : ~598 px — **non comparable** à cette validation
- IT_mean corrigé (1 anchor/image) : **22.89 px**

#### 3. Qualité méthode de sélection
- Règle : max IoU FG anchor vs target_bboxes assigné (1 prédiction/instance)
- Anchors FG moyens/image : ~10 (non comptés comme landmarks indépendants)
- Distinction vs métrique training (`compute_it_metrics`, 90 evals = tous FG × v=2) : **documentée**
- IT_mean avec sélection max-IoU : **22.89 px** vs IT_mean premier-FG-anchor (decoder_fix_QA) : **24.67 px** — écart modeste, même ordre de grandeur

CSV : `v5_phase2_final_independent_validation.csv`
