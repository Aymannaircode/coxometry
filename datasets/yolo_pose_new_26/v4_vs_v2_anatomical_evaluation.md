# V4 vs V2 — Évaluation anatomique complète

**Généré :** 2026-08-29T00:45:52.292037+00:00
**Mode :** inférence read-only → rapports uniquement (GT/labels/YAML/checkpoints inchangés)

## Protocole

| Paramètre | V2 | V4 |
|-----------|----|----|
| Checkpoint | `runs\pose\runs\pose\runs\yolo_pose_new_26_v2-3\weights\best.pt` | `runs\pose\yolo_pose_new_26_v4_16kp-2\weights\best.pt` |
| imgsz | 640 | 960 |
| conf (box + kpt) | 0.25 | 0.25 |
| Images | 26 DICOM pleine résolution (identiques) | idem |
| GT | labels 16 KP (`labels/train|val/`) | idem |

**Note checkpoint V4 :** le chemin officiel `yolo_pose_new_26_v4_16kp/weights/best.pt` est absent ; utilisation de `runs\pose\yolo_pose_new_26_v4_16kp-2\weights\best.pt` (run Ultralytics `v4_16kp-2`, `exist_ok=false`).

**GT v=0 :** landmarks non évaluables (`v<2` ou coords nulles) exclus du calcul d'erreur — pas de pénalité si non annotés visibles.

---

## 1. Détection

| Modèle | Détections /26 | Recall | Conf box moyenne |
|--------|----------------:|--------:|-----------------:|
| V2 | 26 | 1.000 | 0.8864 |
| V4 | 26 | 1.000 | 0.7513 |

**Images sans détection V2 :** 0 — aucune
**Images sans détection V4 :** 0 — aucune
**V2 détecte mais V4 non :** aucun

---

## 2–3. Métriques pixel (GT v≥2 uniquement)

### Global

| Métrique | V2 (14 KP) | V4 (14 KP communs) | V4 (16 KP) |
|----------|----------:|-------------------:|-----------:|
| n | 364 | 364 | 408 |
| mean | 128.48 | 813.00 | 813.55 |
| median | 85.77 | 765.54 | 773.13 |
| p90 | 243.20 | 1214.73 | 1212.01 |
| min | 2.03 | 67.29 | 67.29 |
| max | 813.76 | 1653.42 | 1653.42 |

**Tiers V2 (14 KP) :** CORRECT=151 INCERTAIN=123 INCORRECT=90
**Tiers V4 (14 KP) :** CORRECT=1 INCERTAIN=2 INCORRECT=361

### Par landmark (mean px)

| Landmark | V2 mean | V4 mean | Δ V4−V2 | n V2 | n V4 |
|----------|--------:|--------:|--------:|-----:|-----:|
| TD_R | 64.17 | 353.23 | 289.07 | 26 | 26 |
| TD_L | 64.45 | 340.71 | 276.26 | 26 | 26 |
| FHC_R | 62.19 | 622.26 | 560.07 | 26 | 26 |
| FHC_L | 57.96 | 670.24 | 612.28 | 26 | 26 |
| ASL_R | 143.79 | 1168.11 | 1024.32 | 26 | 26 |
| ASL_L | 525.40 | 1245.34 | 719.94 | 26 | 26 |
| ASM_R | 93.83 | 781.87 | 688.04 | 26 | 26 |
| ASM_L | 78.23 | 813.26 | 735.03 | 26 | 26 |
| FNM_R | 62.12 | 730.42 | 668.31 | 26 | 26 |
| FNM_L | 58.22 | 729.72 | 671.50 | 26 | 26 |
| FSP_R | 150.86 | 793.98 | 643.12 | 26 | 26 |
| FSP_L | 169.99 | 842.82 | 672.83 | 26 | 26 |
| FSD_R | 159.41 | 1151.16 | 991.74 | 26 | 26 |
| FSD_L | 108.04 | 1138.92 | 1030.88 | 26 | 26 |
| IT_R |  | 904.77 |  | 0 | 20 |
| IT_L |  | 745.89 |  | 0 | 24 |

### Par côté (mean px)

| Côté | V2 | V4 |
|------|----|----|
| R | 105.20 | 810.51 |
| L | 151.76 | 816.54 |

---

## 4. Focus FSP / FSD / ASL

| Landmark | V2 mean | V4 mean | Δ | Tendance |
|----------|--------:|--------:|--:|----------|
| ASL_R | 143.79 | 1168.11 | 1024.32 | ↑ dégradation |
| ASL_L | 525.40 | 1245.34 | 719.94 | ↑ dégradation |
| FSP_R | 150.86 | 793.98 | 643.12 | ↑ dégradation |
| FSP_L | 169.99 | 842.82 | 672.83 | ↑ dégradation |
| FSD_R | 159.41 | 1151.16 | 991.74 | ↑ dégradation |
| FSD_L | 108.04 | 1138.92 | 1030.88 | ↑ dégradation |

---

## 5. IT_R / IT_L (V4 seul)

| Métrique | IT_R (n=20) | IT_L (n=24) | Pooled (n=44) |
|----------|-----:|-----:|-------:|
| mean | 904.77 | 745.89 | 818.11 |
| median | 876.5 | 773.1 | 812.6 |
| p90 | 1214.7 | 1013.1 | 1212.0 |
| % CORRECT | 0.0% | 0.0% | 0.0% |
| % INCORRECT | 100.0% | 100.0% | 100.0% |
| GT v=0 exclus | 6 | 2 | 8 paires non évaluées |

---

## 6. Cas prioritaires

### B26_01
- Détection : V2=oui (conf=0.8881) | V4=oui (conf=0.7749)
- Erreur moyenne landmarks : V2=178.62 px | V4=747.80 px
- IT_R : GT v=2 | err V4=804.30 px | INCORRECT
- IT_L : GT v=2 | err V4=629.64 px | INCORRECT

### B26_05
- Détection : V2=oui (conf=0.8922) | V4=oui (conf=0.7697)
- Erreur moyenne landmarks : V2=174.52 px | V4=921.98 px
- IT_R : GT v=2 | err V4=1374.73 px | INCORRECT
- IT_L : GT v=2 | err V4=1262.90 px | INCORRECT

### B26_06
- Détection : V2=oui (conf=0.8847) | V4=oui (conf=0.6257)
- Erreur moyenne landmarks : V2=116.39 px | V4=814.46 px
- IT_R : GT v=0 | err V4= px | NA
- IT_L : GT v=2 | err V4=796.61 px | INCORRECT

### B26_11
- Détection : V2=oui (conf=0.8752) | V4=oui (conf=)
- Erreur moyenne landmarks : V2=128.50 px | V4=895.49 px
- IT_R : GT v=0 | err V4= px | NA
- IT_L : GT v=2 | err V4=989.60 px | INCORRECT

### B26_12
- Détection : V2=oui (conf=0.8958) | V4=oui (conf=0.7954)
- Erreur moyenne landmarks : V2=127.87 px | V4=754.14 px
- IT_R : GT v=2 | err V4=857.58 px | INCORRECT
- IT_L : GT v=2 | err V4=772.90 px | INCORRECT

### B26_13
- Détection : V2=oui (conf=0.8754) | V4=oui (conf=0.7986)
- Erreur moyenne landmarks : V2=135.17 px | V4=862.43 px
- IT_R : GT v=2 | err V4=1081.05 px | INCORRECT
- IT_L : GT v=2 | err V4=906.89 px | INCORRECT

### B26_14
- Détection : V2=oui (conf=0.8823) | V4=oui (conf=0.7456)
- Erreur moyenne landmarks : V2=113.40 px | V4=800.76 px
- IT_R : GT v=0 | err V4= px | NA
- IT_L : GT v=2 | err V4=773.71 px | INCORRECT

### B26_15
- Détection : V2=oui (conf=0.8829) | V4=oui (conf=0.7718)
- Erreur moyenne landmarks : V2=98.25 px | V4=753.59 px
- IT_R : GT v=0 | err V4= px | NA
- IT_L : GT v=0 | err V4= px | NA

### B26_19
- Détection : V2=oui (conf=0.8713) | V4=oui (conf=0.8155)
- Erreur moyenne landmarks : V2=128.80 px | V4=803.48 px
- IT_R : GT v=2 | err V4=872.08 px | INCORRECT
- IT_L : GT v=0 | err V4= px | NA

### B26_21
- Détection : V2=oui (conf=0.9013) | V4=oui (conf=0.8565)
- Erreur moyenne landmarks : V2=135.36 px | V4=824.44 px
- IT_R : GT v=0 | err V4= px | NA
- IT_L : GT v=2 | err V4=722.02 px | INCORRECT

### B26_24
- Détection : V2=oui (conf=0.8687) | V4=oui (conf=0.6211)
- Erreur moyenne landmarks : V2=130.93 px | V4=789.52 px
- IT_R : GT v=2 | err V4=900.73 px | INCORRECT
- IT_L : GT v=2 | err V4=829.09 px | INCORRECT

### B26_26
- Détection : V2=oui (conf=0.8603) | V4=oui (conf=)
- Erreur moyenne landmarks : V2=161.79 px | V4=880.64 px
- IT_R : GT v=0 | err V4= px | NA
- IT_L : GT v=2 | err V4=365.42 px | INCORRECT

---

## 7. Mesures cliniques (VCE / Tönnis / CCD)

Pipeline : `mvp_geometry` sur les **14 premiers keypoints** des prédictions (compatibilité V2/V4).

| Mesure | V2 médiane | V4 médiane | Commentaire |
|--------|----------:|----------:|-------------|
| VCE_L (°) | −25.1 | −174.1 | V4 plus négatif (21/26 cas négatifs des deux côtés) |
| Tönnis_L (°) | 43.5 | 59.2 | V4 plus extrême |
| CCD_L (°) | 137.3 | 166.7 | V4 dérive +29° médiane |
| VCE_R (°) | ~42 | ~175 (abs) | V4 angles instables |

Échantillon cas prioritaires :

| Cas | VCE_L V2 | VCE_L V4 | Tönnis_L V2 | Tönnis_L V4 | CCD_L V2 | CCD_L V4 |
|-----|----------|----------|-------------|-------------|----------|----------|
| B26_01 | −17.50 | 178.64 | 34.28 | 59.20 | 163.18 | 178.71 |
| B26_12 | −48.45 | −173.91 | 152.65 | 63.88 | 129.22 | 175.44 |
| B26_13 | −30.93 | −175.12 | 86.65 | 65.02 | 137.79 | 175.44 |
| B26_26 | −35.62 | 177.49 | 127.62 | 44.13 | 126.40 | 119.01 |

Voir CSV détaillé pour les 26 cas (géométrie calculée en lecture seule depuis prédictions temporaires).

---

## 8. Tableau récapitulatif

| Critère | V2 | V4 | Gagnant |
|---------|----|----|---------|
| Détection /26 | 26 | 26 | = |
| Conf box moyenne | 0.886 | 0.751 | V2 |
| Erreur mean 14 KP (px) | 128.48 | 813.00 | **V2** |
| ASL_L mean (px) | 525.40 | 1245.34 | **V2** |
| IT pooled mean (px) | NA | 818.11 | — (V4 seul, échec) |
| VCE_L médiane (°) | −25.1 | −174.1 | **V2** |

---

## 10. Verdict

**C — V4 inférieur**

Critères appliqués (priorité détection > pixel > FSP/FSD/ASL > IT > cas difficiles > géométrie) :

| # | Critère | Résultat |
|---|---------|----------|
| 1 | Détection | **Égal** — 26/26 V2 et V4 (recall 1.0) ; conf box V2 0.886 > V4 0.751 |
| 2 | Erreur pixel 14 KP | **V2 gagne** — mean 128 px vs 813 px V4 (×6.3) |
| 3 | FSP/FSD/ASL | **V2 gagne** — tous les 6 landmarks focus dégradés en V4 (+643 à +1031 px mean) |
| 4 | IT_R/IT_L | **Échec V4** — 0 % CORRECT, 100 % INCORRECT sur 44 évaluations |
| 5 | Cas difficiles | **V2 gagne** — 12/12 cas prioritaires : err moyenne V4 >> V2 |
| 6 | VCE/Tönnis/CCD | **V2 plus stable** — VCE_L médiane −25° (V2) vs −174° (V4) |

**Synthèse :** V4 détecte le bassin sur 26/26 images mais les landmarks sont **massivement décalés** (pose head 16 KP réinitialisée non convergée malgré fine-tuning). ASL_L reste le pire landmark V2 (~525 px) et **empire** en V4 (~1245 px). Les nouveaux IT_R/IT_L ne sont pas utilisables cliniquement.

**V2 reste le modèle production.**

---

## Conclusion

**`V4_ANATOMICAL_EVALUATION_COMPLETE`**

CSV détaillé : `v4_vs_v2_anatomical_evaluation.csv` (442 lignes)