# B5 — QC technique final dataset 16 keypoints

**Généré :** 2026-08-29  
**Mode :** READ-ONLY — aucun label, YAML, V2/V3 ou training modifié  
**Conclusion :** **`DATASET_16KP_READY_FOR_TRAINING`**

## Synthèse globale

| Contrôle | Résultat | Détail |
|----------|:--------:|--------|
| Labels vérifiés | **26/26** | 26 images B26_01→B26_26 |
| Split train/val | **21 train / 5 val** | cohérent avec labels |
| 53 colonnes | **OK** | 26/26 |
| 16 keypoints | **OK** | 26/26 |
| KP 0–13 inchangés (backup 14) | **OK** | 26/26 |
| IT_R (idx 14) / IT_L (idx 15) | **OK** | coords B6 + politique v |
| v=0 encodés (0,0,0) | **OK** | 26/26 |
| Aucun v=0 erroné | **OK** | 26/26 |
| data.yaml kpt_shape [16,3] | **OK** | [16, 3] |
| dataset.yaml kpt_shape [16,3] | **OK** | [16, 3] |
| YAML kpt_names (16, IT_R/IT_L) | **OK** | TD_R…FSD_L, IT_R, IT_L |
| flip_idx IT_R↔IT_L | **OK** | [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14] |
| meta/keypoint_order.md | **OK** | ordre 16 KP + flip |
| Labels malformés | **OK** | |
| Doublons image | **OK** | |
| Fichiers image | **OK** | 26/26 fichiers dans images/ (workspace) |

## Politique v=0 attendue (IT uniquement)

| Image | IT_R v | IT_L v |
|-------|:------:|:------:|
| B26_01 | 2 | 2 |
| B26_02 | 2 | 2 |
| B26_03 | 2 | 2 |
| B26_04 | 2 | 2 |
| B26_05 | 2 | 2 |
| B26_06 | 0 | 2 |
| B26_07 | 2 | 2 |
| B26_08 | 2 | 2 |
| B26_09 | 2 | 2 |
| B26_10 | 2 | 2 |
| B26_11 | 0 | 2 |
| B26_12 | 2 | 2 |
| B26_13 | 2 | 2 |
| B26_14 | 0 | 2 |
| B26_15 | 0 | 0 |
| B26_16 | 2 | 2 |
| B26_17 | 2 | 2 |
| B26_18 | 2 | 2 |
| B26_19 | 2 | 0 |
| B26_20 | 2 | 2 |
| B26_21 | 0 | 2 |
| B26_22 | 2 | 2 |
| B26_23 | 2 | 2 |
| B26_24 | 2 | 2 |
| B26_25 | 2 | 2 |
| B26_26 | 0 | 2 |

## Matrice par image

| Image | Split | Cols | 16KP | KP14 | IT | v=0 enc | v=0 err | Anomalies |
|-------|:-----:|:----:|:----:|:----:|:--:|:-------:|:-------:|-----------|
| B26_01 | train | OK | OK | OK | OK | OK | OK | — |
| B26_02 | train | OK | OK | OK | OK | OK | OK | — |
| B26_03 | train | OK | OK | OK | OK | OK | OK | — |
| B26_04 | train | OK | OK | OK | OK | OK | OK | — |
| B26_05 | train | OK | OK | OK | OK | OK | OK | — |
| B26_06 | train | OK | OK | OK | OK | OK | OK | — |
| B26_07 | train | OK | OK | OK | OK | OK | OK | — |
| B26_08 | train | OK | OK | OK | OK | OK | OK | — |
| B26_09 | train | OK | OK | OK | OK | OK | OK | — |
| B26_10 | val | OK | OK | OK | OK | OK | OK | — |
| B26_11 | train | OK | OK | OK | OK | OK | OK | — |
| B26_12 | train | OK | OK | OK | OK | OK | OK | — |
| B26_13 | val | OK | OK | OK | OK | OK | OK | — |
| B26_14 | train | OK | OK | OK | OK | OK | OK | — |
| B26_15 | train | OK | OK | OK | OK | OK | OK | — |
| B26_16 | train | OK | OK | OK | OK | OK | OK | — |
| B26_17 | val | OK | OK | OK | OK | OK | OK | — |
| B26_18 | train | OK | OK | OK | OK | OK | OK | — |
| B26_19 | train | OK | OK | OK | OK | OK | OK | — |
| B26_20 | val | OK | OK | OK | OK | OK | OK | — |
| B26_21 | train | OK | OK | OK | OK | OK | OK | — |
| B26_22 | train | OK | OK | OK | OK | OK | OK | — |
| B26_23 | train | OK | OK | OK | OK | OK | OK | — |
| B26_24 | train | OK | OK | OK | OK | OK | OK | — |
| B26_25 | train | OK | OK | OK | OK | OK | OK | — |
| B26_26 | val | OK | OK | OK | OK | OK | OK | — |

## Conclusion

**`DATASET_16KP_READY_FOR_TRAINING`**

Les 26 labels officiels 16 KP, les YAML et l'ordre des keypoints passent tous les contrôles techniques obligatoires.