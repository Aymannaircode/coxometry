# V5 — Session Checkpoint (fin de session)

**Date :** 2026-08-29  
**Mode :** READ-ONLY — aucun training, aucun fichier dataset/checkpoint modifié  
**État projet :** V5 Phase 2 entraînée et validée indépendamment  
**Verdict final validé :** `V5_PHASE2_FINAL_SUCCESS`

---

## 1. Checkpoint V5 Phase 2 (principal)

| Fichier | Chemin | Présent | Taille | Date (UTC) | SHA256 |
|---------|--------|:-------:|-------:|------------|--------|
| **best_it.pt** | `runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/weights/best_it.pt` | ✅ | 24 963 226 B (~23.8 MB) | 2026-08-29 02:36:09 | `2E3D3E48C800C1583D427844AF84835EF0115E6456EC1F6096A4ACECEDB257F6` |
| **last_it.pt** | `runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/weights/last_it.pt` | ✅ | 24 963 226 B (~23.8 MB) | 2026-08-29 02:41:25 | `8575F2B7B44E7195C96F3C5FCBFB65A28E0BB5ACA23C4D18BF4E4E538691C82D` |

**Run associé :** `runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/`  
**Training report :** `runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/training_report.json`  
**Config :** `datasets/yolo_pose_new_26/v5_phase2_training_config.yaml`

> ⚠️ Ne pas écraser `best_it.pt`. Aucune modification effectuée lors de cette session de shutdown.

---

## 2. Checkpoints de référence

| Rôle | Chemin effectif | Présent | Taille | Date (UTC) | SHA256 |
|------|-----------------|:-------:|-------:|------------|--------|
| **V2 production** | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` | ✅ | 5 947 464 B (~5.7 MB) | 2026-08-23 17:12:41 | `1F92D0867B4CD86EB6A4E3EC6111F812824B1B0D4D8DCD1D1EBE6C00EF2C48B8` |
| **V5 surgical init** | `runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt` | ✅ | 11 745 287 B (~11.2 MB) | 2026-08-29 01:01:58 | `4C31985AB02863CD086F0C3D8272CE267E3AC70F54324B3266EC47C0F24D3E3A` |

**Note chemin V2 :** le chemin raccourci `runs/pose/yolo_pose_new_26_v2-3/weights/best.pt` **n'existe pas** sur disque. Le chemin réel utilisé par tous les scripts V5 est celui ci-dessus (triple `runs/pose/`).

### V4 (historique uniquement — ne pas modifier)

| Élément | Chemin / statut |
|---------|-----------------|
| Run legacy 14 KP | `runs/pose/yolo_pose_new_26_v4/` (29 epochs, early stop epoch 19) |
| Run 16 KP planifié | `runs/pose/yolo_pose_new_26_v4_16kp/` — **absent** (pas de `best.pt`) |
| Run alternatif | `runs/pose/yolo_pose_new_26_v4_16kp-2/` (args.yaml, results.csv) |
| Rapport | `datasets/yolo_pose_new_26/v4_training_final_report.md` |

V4 documenté comme historique/abandonné au profit de V5. Aucun checkpoint V4 utilisé en production.

---

## 3. Dataset final (`datasets/yolo_pose_new_26/`)

| Vérification | Valeur | Statut |
|--------------|--------|:------:|
| Images totales | 26 (21 train + 5 val) | ✅ |
| Labels train | 21 fichiers | ✅ |
| Labels val | 5 fichiers | ✅ |
| Images train | 21 | ✅ |
| Images val | 5 | ✅ |
| Keypoints | 16 (14 anatomiques + IT_R + IT_L) | ✅ |
| Colonnes label | 53 (1 cls + 4 box + 16×3 kpts) | ✅ |
| IT_R index | 14 | ✅ |
| IT_L index | 15 | ✅ |
| `flip_idx` | `[1,0,3,2,5,4,7,6,9,8,11,10,13,12,15,14]` | ✅ |
| `data.yaml` | présent | ✅ |
| `dataset.yaml` | présent | ✅ |
| `meta/split.json` | train=21, val=5, seed=42 | ✅ |

**Val set (figé) :** B26_10, B26_13, B26_17, B26_20, B26_26  
**Aucun overlap train∩val.**

Aucun fichier dataset modifié lors de cette session.

---

## 4. Index des rapports importants

Tous sous `datasets/yolo_pose_new_26/` sauf mention contraire.

### B6 (annotation IT)

| Rapport | Chemin |
|---------|--------|
| b6_global_final_QA.md | `datasets/yolo_pose_new_26/b6_global_final_QA.md` |
| b6_P0_QA.md | `datasets/yolo_pose_new_26/b6_P0_QA.md` |
| b6_P1_QA.md | `datasets/yolo_pose_new_26/b6_P1_QA.md` |
| b6_P2_QA.md | `datasets/yolo_pose_new_26/b6_P2_QA.md` |
| b6_P3_manual_review.md | `datasets/yolo_pose_new_26/b6_P3_manual_review.md` |
| b6_B26_26_ITR_final_review.md | `datasets/yolo_pose_new_26/b6_B26_26_ITR_final_review.md` |
| bi_ischial_final_policy.md | `datasets/yolo_pose_new_26/bi_ischial_final_policy.md` |

### B5 (promotion 16 KP)

| Rapport | Chemin |
|---------|--------|
| b5_16kp_promotion_report.md | `datasets/yolo_pose_new_26/b5_16kp_promotion_report.md` |
| b5_16kp_final_QC.md | `datasets/yolo_pose_new_26/b5_16kp_final_QC.md` |
| b5_16kp_dry_run.md | `datasets/yolo_pose_new_26/b5_16kp_dry_run.md` |

### V4

| Rapport | Chemin |
|---------|--------|
| v4_preflight.md | `datasets/yolo_pose_new_26/v4_preflight.md` |
| v4_vs_v2_anatomical_evaluation.md | `datasets/yolo_pose_new_26/v4_vs_v2_anatomical_evaluation.md` |
| v4_training_launch_diagnostic.md | `datasets/yolo_pose_new_26/v4_training_launch_diagnostic.md` |
| v4_training_final_report.md | *(complément)* `datasets/yolo_pose_new_26/v4_training_final_report.md` |

### V5 Phase 0

| Rapport | Chemin |
|---------|--------|
| v5_surgical_init_report.md | `datasets/yolo_pose_new_26/v5_surgical_init_report.md` |

### V5 Phase 1

| Rapport | Chemin |
|---------|--------|
| v5_phase1_v2_preflight.md | `datasets/yolo_pose_new_26/v5_phase1_v2_preflight.md` |
| v5_phase1_v2_epoch1_safety_audit.md | `datasets/yolo_pose_new_26/v5_phase1_v2_epoch1_safety_audit.md` |
| v5_phase1_freeze_lifecycle_diagnostic.md | `datasets/yolo_pose_new_26/v5_phase1_freeze_lifecycle_diagnostic.md` |
| v5_phase1_v3_preflight.md | `datasets/yolo_pose_new_26/v5_phase1_v3_preflight.md` |
| v5_phase1_v3_epoch1_QA.md | `datasets/yolo_pose_new_26/v5_phase1_v3_epoch1_QA.md` |
| v5_phase1_v3_final_analysis.md | `datasets/yolo_pose_new_26/v5_phase1_v3_final_analysis.md` |

### V5 Phase 2

| Rapport | Chemin |
|---------|--------|
| v5_phase2_dedicated_head_dryrun.md | `datasets/yolo_pose_new_26/v5_phase2_dedicated_head_dryrun.md` |
| v5_phase2_training_preflight.md | `datasets/yolo_pose_new_26/v5_phase2_training_preflight.md` |
| v5_phase2_final_QA.md | `datasets/yolo_pose_new_26/v5_phase2_final_QA.md` |
| v5_phase2_learning_diagnostic.md | `datasets/yolo_pose_new_26/v5_phase2_learning_diagnostic.md` |
| v5_phase2_coordinate_space_audit.md | `datasets/yolo_pose_new_26/v5_phase2_coordinate_space_audit.md` |
| v5_phase2_decoder_fix_QA.md | `datasets/yolo_pose_new_26/v5_phase2_decoder_fix_QA.md` |
| v5_phase2_final_independent_validation.md | `datasets/yolo_pose_new_26/v5_phase2_final_independent_validation.md` |
| v5_phase2_metric_decoder_fix.md | *(complément)* `datasets/yolo_pose_new_26/v5_phase2_metric_decoder_fix.md` |

---

## 5. Scripts importants (V5)

| Rôle | Chemin |
|------|--------|
| Phase 0 — surgical init | `annotation_pilot/scripts/v5_surgical_init_phase0.py` |
| Phase 1 v1 | `annotation_pilot/scripts/train_yolo_pose_v5_phase1.py` |
| Phase 1 v2 | `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v2.py` |
| Phase 1 v3 | `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v3.py` |
| Phase 2 — dedicated head dryrun | `annotation_pilot/scripts/v5_phase2_dedicated_head_dryrun.py` |
| Phase 2 — training | `annotation_pilot/scripts/train_yolo_pose_v5_phase2.py` |
| Phase 2 — final QA | `annotation_pilot/scripts/v5_phase2_final_QA.py` |
| IT head capacity diagnostic | `annotation_pilot/scripts/v5_it_head_capacity_diagnostic.py` |
| Phase 1 freeze lifecycle debug | `annotation_pilot/scripts/v5_phase1_freeze_lifecycle_debug.py` |
| Phase 1 v2 epoch1 safety audit | `annotation_pilot/scripts/v5_phase1_v2_epoch1_safety_audit.py` |
| Phase 1 posttraining diagnostic | `annotation_pilot/scripts/v5_phase1_posttraining_diagnostic.py` |
| Validation indépendante Phase 2 (temp) | `datasets/yolo_pose_new_26/_v5_phase2_final_independent_validation_temp/run_independent_validation.py` |

Aucun script modifié lors de cette session.

---

## 6. Architecture actuelle

```
V2 (production)
  └── backbone + neck + head (cv2/cv3/dfl/cv4)
      └── 14 KP production (indices 0–13)

V5 surgical (Phase 0)
  └── V2 conservé intégralement
      └── cv4 étendu : IT_R (idx 14) + IT_L (idx 15) ajoutés
      └── checkpoint : v5_surgical_init.pt

V5 Phase 2 (best_it.pt)
  └── backbone + neck + cv2 + cv3 + dfl + cv4 (14 KP) : GELÉS (Δ=0 vs surgical)
  └── ITHeadMultiScaleFusion : ENTRAÎNÉE (62/66 tensors modifiés)
      └── P3 / P4 / P5 (64/128/256 ch)
      └── fusion multi-échelle → 6 canaux IT
      └── splice kpts[:, 42:48] :
          IT_R = canaux 42–44 (x, y, vis)
          IT_L = canaux 45–47 (x, y, vis)
```

| Paramètre | Valeur |
|-----------|--------|
| IT head architecture | `ITHeadMultiScaleFusion` (Option B) |
| IT head params | **362 898** (dryrun) |
| Params gelés | backbone (120 tensors), neck (60), cv2 (156), cv3 (81), dfl (1), cv4 14KP (36) |
| Stratégie freeze | `requires_grad=False` sur base ; seul `it_head` entraînable |
| Loss | IT-only : box/cls/dfl=0, KP 0–13 masqués, IT_R/IT_L actifs |
| Visibilité v=0 | aucune position loss (IT_R sur B26_26 exclu) |
| Decoder métrique | `pred_dec[..., :2] *= stride_tensor` après `kpts_decode` |

---

## 7. Résultat final validé

**Verdict :** `V5_PHASE2_FINAL_SUCCESS`  
**Source :** `v5_phase2_final_independent_validation.md` (2026-08-29)

| Métrique | Valeur |
|----------|--------|
| IT global mean | **22.89 px** |
| % IT < 75 px | **100 %** |
| 14 KP mean | **134.95 px** (identique V2) |
| Détection val | **5/5** (identique V2, conf/IoU identiques) |
| Freeze zones gelées | Δ = 0 |
| IT head | 62/66 tensors modifiés |
| Leakage | train=21, val=5, overlap=∅ |

### Résultats IT par image (px640, 1 anchor/image, v=2)

| Image | IT_R | IT_L |
|-------|-----:|-----:|
| B26_10 | 18.3 | 25.4 |
| B26_13 | 28.7 | 33.6 |
| B26_17 | 16.2 | 10.6 |
| B26_20 | 30.6 | 11.6 |
| B26_26 | **NA (v=0)** | 30.9 |

---

## 8. Bug du decoder (CRITIQUE — ne pas oublier)

L'ancienne métrique d'entraînement **~600 px** (`IT_mean_px` dans `training_report.json`) était **incorrecte**.

| | Détail |
|---|--------|
| **Cause** | Prédictions en coordonnées **grille** comparées au GT en **px640** sans multiplication par `stride_tensor` |
| **Symptôme** | IT_mean ≈ 598 px sur 20 epochs malgré IT head entraîné |
| **Correction** | `pred_dec[..., :2] *= stride_tensor.view(1, -1, 1, 1)` dans `_decode_it_errors()` |
| **Fichier** | `annotation_pilot/scripts/train_yolo_pose_v5_phase2.py` |
| **Validation corrigée** | **~22.89 px** (1 anchor/image, independent validation) |
| **Règle** | **NE PAS revenir à l'ancienne métrique** pour évaluer Phase 2 |

---

## 9. Vérification finale (shutdown)

| Check | Statut |
|-------|:------:|
| best_it.pt existe | ✅ |
| last_it.pt existe | ✅ |
| v5_surgical_init.pt existe | ✅ |
| V2 best.pt existe | ✅ |
| labels train/val existent | ✅ |
| data.yaml / dataset.yaml existent | ✅ |
| Aucun fichier critique supprimé | ✅ |
| Aucun checkpoint critique modifié | ✅ |
| Aucun training YOLO en cours | ✅ (uvicorn backend port 8001 uniquement) |

```
SAFE_TO_SHUTDOWN = YES
```

---

## NEXT SESSION

NEXT SESSION:
1. Ne pas refaire B6.
2. Ne pas refaire B5.
3. Ne pas refaire V4.
4. Ne pas refaire V5 Phase 0.
5. Ne pas relancer Phase 1.
6. Conserver V2 comme modèle production.
7. Conserver v5_surgical_init.pt comme référence.
8. Conserver best_it.pt comme checkpoint V5 Phase 2 principal.
9. Commencer par décider de la prochaine étape de validation/intégration.
10. Aucun training supplémentaire avant décision.

---

**Manifeste compagnon :** `datasets/yolo_pose_new_26/V5_SESSION_MANIFEST_2026-08-29.txt`
