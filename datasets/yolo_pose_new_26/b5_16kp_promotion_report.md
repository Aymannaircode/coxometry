# B5 — Rapport promotion 16 keypoints

**Généré :** 2026-08-29  
**Statut :** **`B5_16KP_PROMOTED / QC_REQUIRED`**  
**Backup 14 kp :** `labels_14kp_backup_20260829/`  
**Sources :** `b6_working_annotations/`, `bi_ischial_final_policy.md`, `b5_16kp_dry_run.csv`

## 1. Synthèse

| Métrique | Valeur |
|----------|-------:|
| Images promues | **26** |
| IT_R v=2 | **20** |
| IT_R v=0 | **6** |
| IT_L v=2 | **24** |
| IT_L v=0 | **2** |
| Labels créés/mis à jour | **26** |
| Colonnes attendues | **53** |
| Anomalies promotion | **0** |
| Anomalies validation | **0** |

## 2. Validations schéma

| Check | Résultat |
|-------|----------|
| Keypoint order 0–13 inchangé | **PASS** (14 premiers triplets préservés) |
| IT_R index 14 | **PASS** |
| IT_L index 15 | **PASS** |
| data.yaml kpt_shape [16,3] | **PASS** |
| data.yaml flip_idx 16 kp | **PASS** |
| data.yaml kpt_names IT_R/IT_L | **PASS** |
| Tous labels 53 colonnes | **PASS** |
| meta/keypoint_order.md | **Mis à jour 16 kp** |

## 3. Décisions clés

| Cas | Décision |
|-----|----------|
| B26_26 IT_R | **v=0** — UNRESOLVABLE_REVIEW, apex non identifiable |
| B26_05 IT_R / IT_L | **v=2** — CLINICAL_GATE : cortex caudal identifiable sur image originale malgré PARTIAL FOV |
| Candidats v=0 (non identifiables) | B26_06 IT_R, B26_11 IT_R, B26_14 IT_R, B26_15 R/L, B26_19 IT_L, B26_21 IT_R → **v=0** |
| REVIEW difficiles mais identifiables | **v=2** conservé (pas v=0 par difficulté seule) |

## 4. Images v=0

- **B26_06** — IT_R v=0 · IT_L v=2
- **B26_11** — IT_R v=0 · IT_L v=2
- **B26_14** — IT_R v=0 · IT_L v=2
- **B26_15** — IT_R v=0 · IT_L v=0
- **B26_19** — IT_R v=2 · IT_L v=0
- **B26_21** — IT_R v=0 · IT_L v=2
- **B26_26** — IT_R v=0 · IT_L v=2

## 5. Matrice 26 images

| Image | Split | IT_R v | IT_L v | Cols | Label | Provenance B6 |
|-------|:-----:|:------:|:------:|:----:|:-----:|---------------|
| B26_01 | train | 2 | 2 | 53 | `labels/train/B26_01.txt` | `b6_working_annotations/B26_01.json` |
| B26_02 | train | 2 | 2 | 53 | `labels/train/B26_02.txt` | `b6_working_annotations/B26_02.json` |
| B26_03 | train | 2 | 2 | 53 | `labels/train/B26_03.txt` | `b6_working_annotations/B26_03.json` |
| B26_04 | train | 2 | 2 | 53 | `labels/train/B26_04.txt` | `b6_working_annotations/B26_04.json` |
| B26_05 | train | 2 | 2 | 53 | `labels/train/B26_05.txt` | `b6_working_annotations/B26_05.json` |
| B26_06 | train | 0 | 2 | 53 | `labels/train/B26_06.txt` | `b6_working_annotations/B26_06.json` |
| B26_07 | train | 2 | 2 | 53 | `labels/train/B26_07.txt` | `b6_working_annotations/B26_07.json` |
| B26_08 | train | 2 | 2 | 53 | `labels/train/B26_08.txt` | `b6_working_annotations/B26_08.json` |
| B26_09 | train | 2 | 2 | 53 | `labels/train/B26_09.txt` | `b6_working_annotations/B26_09.json` |
| B26_10 | val | 2 | 2 | 53 | `labels/val/B26_10.txt` | `b6_working_annotations/B26_10.json` |
| B26_11 | train | 0 | 2 | 53 | `labels/train/B26_11.txt` | `b6_working_annotations/B26_11.json` |
| B26_12 | train | 2 | 2 | 53 | `labels/train/B26_12.txt` | `b6_working_annotations/B26_12.json` |
| B26_13 | val | 2 | 2 | 53 | `labels/val/B26_13.txt` | `b6_working_annotations/B26_13.json` |
| B26_14 | train | 0 | 2 | 53 | `labels/train/B26_14.txt` | `b6_working_annotations/B26_14.json` |
| B26_15 | train | 0 | 0 | 53 | `labels/train/B26_15.txt` | `b6_working_annotations/B26_15.json` |
| B26_16 | train | 2 | 2 | 53 | `labels/train/B26_16.txt` | `b6_working_annotations/B26_16.json` |
| B26_17 | val | 2 | 2 | 53 | `labels/val/B26_17.txt` | `b6_working_annotations/B26_17.json` |
| B26_18 | train | 2 | 2 | 53 | `labels/train/B26_18.txt` | `b6_working_annotations/B26_18.json` |
| B26_19 | train | 2 | 0 | 53 | `labels/train/B26_19.txt` | `b6_working_annotations/B26_19.json` |
| B26_20 | val | 2 | 2 | 53 | `labels/val/B26_20.txt` | `b6_working_annotations/B26_20.json` |
| B26_21 | train | 0 | 2 | 53 | `labels/train/B26_21.txt` | `b6_working_annotations/B26_21.json` |
| B26_22 | train | 2 | 2 | 53 | `labels/train/B26_22.txt` | `b6_working_annotations/B26_22.json` |
| B26_23 | train | 2 | 2 | 53 | `labels/train/B26_23.txt` | `b6_working_annotations/B26_23.json` |
| B26_24 | train | 2 | 2 | 53 | `labels/train/B26_24.txt` | `b6_working_annotations/B26_24.json` |
| B26_25 | train | 2 | 2 | 53 | `labels/train/B26_25.txt` | `b6_working_annotations/B26_25.json` |
| B26_26 | val | 0 | 2 | 53 | `labels/val/B26_26.txt` | `b6_working_annotations/B26_26.json` |

## 7. Interdictions respectées

- Training **non lancé**  
- 14 keypoints originaux **non modifiés** (vérifié par append)  
- Backup 14 kp : `labels_14kp_backup_20260829/`  
- Working annotations B6 **non modifiées**

## 8. Conclusion

**`B5_16KP_PROMOTED / QC_REQUIRED`** — 26 labels officiels étendus à 16 keypoints. QC recommandé avant training : validation visuelle des 8 v=0 et revue clinique des cas REVIEW restants.