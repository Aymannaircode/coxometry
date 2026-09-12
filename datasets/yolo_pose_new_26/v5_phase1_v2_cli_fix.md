# V5 Phase 1 v2 — CLI fix (`--epochs`)

**Généré :** 2026-08-29  
**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v2.py`  
**Verdict :** `V5_PHASE1_CLI_READY`

---

## Problème

```text
python ... train_yolo_pose_v5_phase1_v2.py --train --epochs 1
→ error: unrecognized arguments: --epochs 1
```

Le script n'exposait que `--train` ; la valeur `epochs` venait uniquement de
`v5_phase1_training_config.yaml` (15 par défaut).

---

## Correction

Ajout de l'argument CLI :

```text
--epochs N    Nombre maximum d'epochs du run (défaut sans option: 15, config)
```

| Commande | Epochs effectifs |
|----------|-----------------:|
| `--train` | **15** (config `train.epochs`) |
| `--train --epochs 1` | **1** |
| `--train --epochs 15` | **15** |

Validation : `--epochs` doit être `>= 1` (sinon `parser.error`).

Transmission : la valeur est injectée dans `kwargs["epochs"]` passé à
`yolo.train(trainer=..., **kwargs)` — même chemin que les autres hyperparamètres Ultralytics.

---

## Périmètre non modifié

Freeze, hooks cv4, `Phase1ITOnlyPoseLoss`, optimizer IT-only, EMA restreint,
dataset, V2/V4, `v5_surgical_init.pt` — **inchangés**.

---

## Exemples

```powershell
# Aide (vérifier que --epochs apparaît)
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v5_phase1_v2.py --help

# Preflight (sans training)
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v5_phase1_v2.py

# Training 1 epoch (après preflight READY)
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v5_phase1_v2.py --train --epochs 1

# Training 15 epochs (comportement par défaut explicite)
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v5_phase1_v2.py --train --epochs 15
```

---

## Conclusion : `V5_PHASE1_CLI_READY`
