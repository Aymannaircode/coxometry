# V5 Phase 1 v3 — Continuation Pre-flight (→ 15 epochs)

**Généré :** 2026-08-29 01:57 UTC
**Mode :** DRY-RUN / inspection — aucun `--train`
**Run source :** `runs/pose/yolo_pose_new_26_v5_phase1_it_v3`
**Checkpoint source :** `weights/best.pt` (epoch-1 validé SAFE)
**Verdict :** `V5_PHASE1_V3_CONTINUATION_READY`

---

## Contexte

Le test 1 epoch est validé (`V5_PHASE1_V3_EPOCH1_SAFE`). Objectif : continuer
jusqu'à **15 epochs total** sans réinitialiser les poids IT ni les zones gelées.

---

## 1. État des checkpoints epoch-1

| Fichier | epoch field | optimizer | ema | train_args.epochs |
|---------|------------:|:---------:|:---:|------------------:|
| `runs\pose\yolo_pose_new_26_v5_phase1_it_v3\weights\best.pt` | -1 | False | False | 1 |
| `runs\pose\yolo_pose_new_26_v5_phase1_it_v3\weights\last.pt` | -1 | False | False | 1 |

- best ≡ last (max Δ) : **True** (0.00e+00)

**Note Ultralytics :** `final_eval()` appelle `strip_optimizer()` sur best/last →
`epoch=-1`, optimizer/ema/scaler supprimés. Les checkpoints epoch-1 sont des
artefacts d'inférence, pas des checkpoints de reprise natifs.

---

## 2. Préservation poids IT (best vs surgical_init)

| Métrique | Valeur |
|----------|-------:|
| cv4 old changed | 0 |
| cv4 IT changed | 5 |
| cv4 IT max Δ | 2.848816e-02 |

Les poids IT appris en epoch-1 sont bien présents dans best.pt.

---

## 3. Ultralytics `resume=True` — incompatible

| Test | Résultat |
|------|----------|
| epoch field | **-1** |
| start_epoch = epoch+1 | **0** |
| assert 0 < start < epochs(15) | **False** |
| optimizer embarqué | **False** |
| Stripped par final_eval | **True** |

`resume=True` sur last.pt **échouerait** (`start_epoch=0`, assertion impossible)
et restaurerait un optimizer incompatible même s'il existait (tous paramètres, pas IT-only).

Dry-run `_setup_train()` avec `resume=True` : **échec confirmé** —
`last.pt training to 1 epochs is finished, nothing to resume` (epochs remis à 1 depuis train_args stripé).

**Recommandation :** ne pas utiliser `resume=True`.

---

## 4. Continuation contrôlée (recommandée)

Charger **epoch-1 best.pt** comme point de départ, avec le custom trainer v3 :

```
model  = runs/pose/yolo_pose_new_26_v5_phase1_it_v3/weights/best.pt
epochs = 15
pretrained = True    # conserve les poids chargés (fix v3)
resume = False       # pas de resume Ultralytics
trainer = V5Phase1PoseTrainer  # freeze + IT-only loss ré-appliqués dans _setup_train()
```

### Comportement attendu

| Étape | Effet |
|-------|-------|
| `YOLO(best.pt)` | Charge poids epoch-1 incl. IT entraîné |
| `_setup_train()` | Re-applique gel, hooks, Phase1ITOnlyPoseLoss |
| `rebuild_optimizer_trainable_only()` | Optimizer IT-only (24 params) |
| `restrict_ema_to_trainable()` | EMA restreinte aux canaux IT |
| Compteur epoch | Repart à 1 (14 passes additionnelles si epochs=15) |

**Note :** avec `epochs=15` et `resume=False`, le compteur Ultralytics repart de 1
mais les **poids** repartent de epoch-1 best (IT non réinitialisé). Équivalent
fonctionnel à epochs 2→15 en termes de poids, avec 1 epoch de plus si on compte
strictement. Alternative : `--epochs 14` pour exactement 14 passes additionnelles.

### Dry-run post `_setup_train()`

| Check | Valeur | Attendu |
|-------|-------:|:-------:|
| backbone trainable | 0 | 0 |
| cv2 trainable | 0 | 0 |
| cv3 trainable | 0 | 0 |
| dfl trainable | 0 | 0 |
| cv4 IT trainable | 24 | 24 |
| optimizer IT params | 24 | 24 |
| criterion | Phase1ITOnlyPoseLoss | Phase1ITOnlyPoseLoss |
| box/cls/dfl loss | 0.0/0.0/0.0 | 0/0/0 |
| cv4 IT grad | 3 | >0 |
| cv4 old grad | 0 | 0 |
| EMA mode | ema_restricted_trainable | ema_restricted_trainable |
| poids ≡ epoch-1 best (gelé) | True | True |
| IT non reset surgical | True | True |

---

## 5. Commande proposée (NE PAS exécuter automatiquement)

Option A — 15 epochs total depuis best.pt (compteur 1→15, poids epoch-1) :

```powershell
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v5_phase1_v3.py ^
  --train --epochs 15 --model runs\pose\yolo_pose_new_26_v5_phase1_it_v3\weights\best.pt
```

*(Nécessite ajout CLI `--model` au script — voir section 6.)*

Option B — workaround sans modifier le script (copie work, read-only sur best.pt) :

```powershell
Copy-Item runs\pose\yolo_pose_new_26_v5_phase1_it_v3\weights\best.pt `
  runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_phase1_v3_continue_work.pt
# Puis ajouter --model sur le script v3 pointant vers ce work copy
```

Option C — 14 epochs additionnelles exactes : `--epochs 14` avec model=best.pt

---

## 6. Écart script actuel

`train_yolo_pose_v5_phase1_v3.py --train` charge toujours `v5_surgical_init.pt`
via `build_train_kwargs_v3(cfg)` — **pas epoch-1 best.pt**.

Pour continuer sans réinitialiser IT, il faut soit :
1. Ajouter `--model` / `--resume-from` au script v3, ou
2. Mettre à jour temporairement le chemin init dans un kwargs override explicite
   (work copy de best.pt, sans toucher les fichiers protégés).

---

## Checklist

- [x] `epoch1_best_exists` → True
- [x] `epoch1_best_unmodified_readable` → True
- [x] `best_equals_last` → True
- [x] `it_weights_preserved_vs_surgical` → True
- [x] `frozen_zones_match_surgical` → True
- [x] `cv4_old_unchanged_vs_surgical` → True
- [x] `native_resume_blocked_stripped_ckpt` → True
- [x] `native_resume_no_optimizer` → True
- [x] `controlled_uses_best_not_surgical` → True
- [x] `controlled_pretrained_true` → True
- [x] `controlled_epochs_15` → True
- [x] `controlled_resume_false` → True
- [x] `custom_trainer_active` → True
- [x] `freeze_backbone_0` → True
- [x] `freeze_cv2_0` → True
- [x] `freeze_cv3_0` → True
- [x] `freeze_dfl_0` → True
- [x] `freeze_cv4_it_24` → True
- [x] `optimizer_it_only_24` → True
- [x] `optimizer_no_backbone` → True
- [x] `criterion_it_only` → True
- [x] `det_loss_zero` → True
- [x] `cv4_it_grad_active` → True
- [x] `cv4_old_grad_zero` → True
- [x] `ema_restricted` → True
- [x] `post_setup_matches_epoch1_best_frozen` → True
- [x] `post_setup_cv4_old_unchanged` → True
- [x] `post_setup_it_preserved` → True
- [x] `it_not_reset_to_surgical` → True

---

## Conclusion : `V5_PHASE1_V3_CONTINUATION_READY`

**Stratégie :** continuation contrôlée depuis `best.pt`, `pretrained=True`,
`resume=False`, `V5Phase1PoseTrainer`, `epochs=15` (ou 14 additionnelles).

**Bloquant natif :** `resume=True` incompatible (checkpoint stripé).

CSV : `v5_phase1_v3_continuation_preflight.csv`
