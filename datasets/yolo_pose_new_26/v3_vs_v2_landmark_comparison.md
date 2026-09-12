# Comparaison V2 vs V3 — landmarks & géométrie

**Généré :** 2026-08-23T21:27:28.539090+00:00
**Critère :** validation pixel-level obligatoire (pas seulement mAP).

## Verdict : **V2**

ASL_L V3 n'a pas baissé de ≥20 % vs V2 (critère pixel-level).

## Erreurs moyennes (px) — landmarks focus

| Landmark | V2 train | V3 train | V2 val | V3 val |
|----------|----------|----------|--------|--------|
| ASL_R | 142.86 | 951.74 | 147.73 | 969.39 |
| ASL_L | 538.18 | 584.45 | 471.72 | 579.38 |
| ASM_L | 77.59 | 614.97 | 80.94 | 700.48 |
| FHC_L | 52.49 | 176.95 | 80.94 | 217.30 |
| FNM_L | 52.78 | 112.06 | 81.05 | 177.53 |

## ASL_L (critère principal)

- V2 ASL_L train : **538.18 px**
- V3 ASL_L train : **584.45 px**
- V2 ASL_L val : **471.72 px**
- V3 ASL_L val : **579.38 px**

## Entraînement V3

- Run : `runs/pose/yolo_pose_new_26_v3/`
- Init : copie V2 `best.pt` (meilleur mAP @ epoch 80) — V2 non modifié
- Augmentations : mosaic=0, randaugment=off, erasing=0, fliplr=0.5
- best mAP50-95(P) V3 : **0.039** (epoch 89) vs V2 **0.692** (epoch 80)
- Prédictions V3 : **25/26** (B26_10 : aucune détection pelvis)

## Géométrie gauche

- V2 VCE_L négatifs : **21** / 26
- V3 VCE_L négatifs : **22** / 26
- V2 Tönnis_L extrêmes : **6** / 26
- V3 Tönnis_L extrêmes : **22** / 26

## Tous les landmarks (mean px, train+val pooled)

| Landmark | V2 | V3 | Δ |
|----------|----|----|---|
| TD_R | 68.23 | 145.31 | 77.07 |
| TD_L | 69.82 | 118.53 | 48.71 |
| FHC_R | 62.45 | 107.81 | 45.36 |
| FHC_L | 66.71 | 197.12 | 130.41 |
| ASL_R | 145.29 | 960.57 | 815.27 |
| ASL_L | 504.95 | 581.91 | 76.97 |
| ASM_R | 89.07 | 97.86 | 8.79 |
| ASM_L | 79.26 | 657.72 | 578.46 |
| FNM_R | 61.21 | 128.68 | 67.47 |
| FNM_L | 66.92 | 144.79 | 77.87 |
| FSP_R | 142.01 | 233.36 | 91.35 |
| FSP_L | 178.67 | 158.76 | -19.91 |
| FSD_R | 167.63 | 1463.10 | 1295.47 |
| FSD_L | 130.96 | 814.82 | 683.86 |
