# Diagnostic V4 — pourquoi le training officiel n'a pas produit de run

**Généré :** 2026-08-29T00:30:00+00:00  
**Mode :** READ-ONLY — aucun entraînement lancé, aucun fichier modifié hors ce rapport  
**Run officiel attendu :** `runs/pose/yolo_pose_new_26_v4_16kp/`  
**Références :** `v4_preflight.md`, `v4_training_final_report.md`

---

## Conclusion

**`TRAINING_NOT_LAUNCHED`**

Le training officiel V4 16 keypoints **n'a jamais été démarré**. Le pre-flight a validé la configuration (`V4_PREFLIGHT_READY`) mais l'instruction explicite et le comportement par défaut du script ont empêché tout appel à `model.train()`. Aucune trace de `--train` dans l'historique terminal capturé.

> **Note secondaire :** un run V4 **legacy** distinct existe à `runs/pose/yolo_pose_new_26_v4/` (pilot 14 KP, 23 août 2026). Ce n'est **pas** le run officiel `v4_16kp` et peut expliquer une confusion si le message `V4 TRAINING COMPLETE` y est associé.

---

## Synthèse exécutive

| Question | Réponse |
|----------|---------|
| Le run `yolo_pose_new_26_v4_16kp` existe-t-il ? | **Non** — répertoire entièrement absent |
| `--train` est-il requis ? | **Oui** — obligatoire pour lancer Ultralytics |
| Une commande `--train` a-t-elle été exécutée ? | **Non** — aucune dans les terminaux indexés |
| Le pre-flight a-t-il lancé le training ? | **Non** — instruction utilisateur + mode par défaut |
| V2 `best.pt` disponible ? | **Oui** — intact (5 947 464 bytes) |
| Erreur avant création du run ? | **Non** — pas d'échec ; le pipeline n'a pas été invoqué |
| Run V4 ailleurs ? | **Oui (legacy)** — `yolo_pose_new_26_v4/` ≠ officiel |

---

## 1. Comportement du script (`train_yolo_pose_v4_new_26.py`)

Le script distingue **deux modes** :

| Mode | Commande | Effet |
|------|----------|-------|
| Preflight (défaut) | `python train_yolo_pose_v4_new_26.py` | Copie init V2, vérifs, écrit `v4_train_config.md`, **n'appelle pas** `model.train()` |
| Entraînement | `python train_yolo_pose_v4_new_26.py --train` | Preflight + `YOLO(...).train(...)` → `results.csv`, `weights/best.pt` |

Extrait clé :

```362:368:annotation_pilot/scripts/train_yolo_pose_v4_new_26.py
    if not args.train:
        print("Mode preflight : entraînement NON lancé.")
        print("Pour lancer : .venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v4_new_26.py --train")
        return 0

    print("Lancement entraînement V4…")
    return run_training(cfg, init_dest, train_kwargs)
```

**Sans `--train`, Ultralytics ne démarre jamais** → pas de `results.csv`, pas de `best.pt`.

---

## 2. Configuration officielle (`v4_training_config.yaml`)

| Paramètre | Valeur officielle |
|-----------|-------------------|
| `run.name` | **`yolo_pose_new_26_v4_16kp`** |
| `run.project` | `runs/pose` |
| `run.exist_ok` | **false** |
| `epochs` | 100 |
| `imgsz` | 960 |
| `batch` | 1 |
| Init copy | `runs/pose/yolo_pose_new_26_v4_16kp/init/v2_best_mAP_epoch80.pt` |

Commande documentée pour lancer le training :

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v4_new_26.py --train
```

---

## 3. Pre-flight (`v4_preflight.md`) — ce qui s'est passé

Le pre-flight du **29 août 2026 (~01:14)** a explicitement :

- validé dataset 16 KP, transfert V2→16 KP, config conservative ;
- conclu **`V4_PREFLIGHT_READY`** ;
- indiqué **« aucun entrainement lance »** ;
- enregistré dans `v4_preflight.csv` : `INT05,training_not_run,OK,no training launched`.

**Instruction utilisateur lors du pre-flight :**

> « Préparer et vérifier le training V4, mais **NE PAS lancer le training** »

Le rapport final V4 (`v4_training_final_report.md`, ~01:18) a confirmé l'absence du run **4 minutes plus tard** — délai incompatible avec 100 epochs @ imgsz 960 sur CPU.

---

## 4. Historique / logs disponibles

### Terminaux Cursor (grep `train_yolo_pose_v4`)

| Recherche | Résultat |
|-----------|----------|
| `train_yolo_pose_v4_new_26.py` | **Aucune occurrence** |
| `train_yolo_pose_v4_new_26.py --train` | **Aucune occurrence** |
| `V4 TRAINING COMPLETE` | **1 occurrence** → chemin **`yolo_pose_new_26_v4`** (legacy), pas `v4_16kp` |

### Session pre-flight (transcript agent)

1. Tentative d'exécution du script **sans** `--train` (probe).
2. Puis rédaction **manuelle** des rapports pre-flight « à partir des vérifications déjà effectuées ».
3. Aucune preuve que le script preflight ait matérialisé le dossier `v4_16kp/` (même le preflight seul devrait créer `init/` + `v4_train_config.md`).

### Probes expérimentales (sans run officiel)

Des probes Ultralytics existent sous `runs/pose/_preflight_tmp/` (`_v4_preflight_probe`, `probe`, `probe2`) — epochs=1, pas de weights finaux, **≠ run officiel**.

---

## 5. État exact de `runs/pose/`

| Dossier | Présent | Rôle |
|---------|:-------:|------|
| `yolo_pose_new_26_v4_16kp/` | **Non** | **Run officiel 16 KP (attendu)** |
| `yolo_pose_new_26_v4/` | Oui | Pilot legacy 14 KP (23 août) |
| `yolo_pose_new_26_v3/` | Oui | V3 |
| `yolo_pose_new_26_v3_anatomical/` | Oui | V3 variant |
| `yolo_pose_new_26_v3_anatomical-2/` | Oui | V3 variant |
| `_preflight_tmp/` | Oui | Probes 1 epoch |
| `train/` | Oui | args.yaml orphan (1 epoch probe) |
| `runs/` (nested) | Oui | V2 nested path |

**Artefacts officiels manquants :**

- `runs/pose/yolo_pose_new_26_v4_16kp/results.csv`
- `runs/pose/yolo_pose_new_26_v4_16kp/args.yaml`
- `runs/pose/yolo_pose_new_26_v4_16kp/weights/best.pt`
- `runs/pose/yolo_pose_new_26_v4_16kp/init/v2_best_mAP_epoch80.pt`
- `runs/pose/yolo_pose_new_26_v4_16kp/v4_train_config.md`

---

## 6. Logs d'erreur

**Aucun log d'échec d'entraînement officiel** — le training n'a pas été tenté.

Pas de `TRAINING_FAILED_BEFORE_RUN` : il n'y a pas de trace d'un `--train` interrompu avant la première epoch Ultralytics sur `v4_16kp`.

---

## 7. Différence `v4_16kp` (officiel) vs `v4` (legacy)

| Aspect | **`yolo_pose_new_26_v4_16kp`** (officiel) | **`yolo_pose_new_26_v4`** (legacy) |
|--------|-------------------------------------------|-------------------------------------|
| Date config | 29 août 2026 | 23 août 2026 |
| Keypoints | **16** (+ IT_R/IT_L) | **14** (doc `v4_train_config.md`) |
| Run name | `yolo_pose_new_26_v4_16kp` | `yolo_pose_new_26_v4` |
| Epochs | 100 | 30 |
| imgsz | 960 | 640 |
| batch | 1 | 2 |
| lr0 | 3e-5 | 1e-4 |
| mosaic | 0 | 0.2 |
| cos_lr | false | true |
| exist_ok | false | true |
| Run produit ? | **Non** | **Oui** (29 epochs, early stop ep 19) |
| Script générateur | `train_yolo_pose_v4_new_26.py` (version 16 KP) | Ancienne version script (écrit dans `v4/`) |

Le message terminal `V4 TRAINING COMPLETE` (terminal 33) pointe vers :

```
BEST=C:\...\runs\pose\yolo_pose_new_26_v4\weights\best.pt
```

→ **legacy**, antérieur au dataset 16 KP officiel.

---

## 8. `--train` requis ?

**Oui.** C'est le seul chemin vers `model.train()` dans le script actuel. Le pre-flight seul ne produit pas un run Ultralytics complet.

---

## 9. Commande réellement exécutée ?

| Commande | Exécutée ? | Preuve |
|----------|:----------:|--------|
| `train_yolo_pose_v4_new_26.py` (sans flag) | **Non confirmée** (tentative agent, pas de dossier créé) | Absence `v4_16kp/` |
| `train_yolo_pose_v4_new_26.py --train` | **Non** | Aucun terminal, aucun artefact |
| Training legacy `yolo_pose_new_26_v4` | **Oui** (23 août) | `results.csv`, `best.pt` présents |

---

## 10. V2 `best.pt` — toujours disponible

| Attribut | Valeur |
|----------|--------|
| Chemin | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` |
| Existe | **Oui** |
| Taille | 5 947 464 bytes |
| mtime | 2026-08-23T18:12:41 |
| SHA256 (16 chars) | `1f92d0867b4cd86e` |
| Modifié depuis pre-flight | **Non** |

L'absence du run officiel **n'est pas** due à un checkpoint V2 manquant.

---

## Chaîne causale (root cause)

```mermaid
flowchart TD
    A[Dataset 16 KP QC OK] --> B[Preflight V4_PREFLIGHT_READY]
    B --> C{Instruction: NE PAS lancer training}
    C --> D[Script default: sans --train]
    D --> E[Pas de model.train]
    E --> F[Pas de runs/pose/yolo_pose_new_26_v4_16kp/]
    G[Legacy v4 pilot Aug 23] -.-> H[Confusion possible V4 TRAINING COMPLETE]
    H -.x F
```

1. Pre-flight **volontairement** sans entraînement (instruction utilisateur + design script).
2. Aucune commande `--train` ultérieure dans l'historique capturé.
3. Le rapport `v4_training_final_report.md` a supposé à tort un training terminé alors que seul le pre-flight avait eu lieu.
4. Le run legacy `yolo_pose_new_26_v4` peut induire en erreur (nom « V4 » proche, config différente).

---

## Action corrective (hors scope — non exécutée)

Pour produire le run officiel, après revue humaine :

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\train_yolo_pose_v4_new_26.py --train
```

Puis regénérer `v4_training_final_report.md` depuis `runs/pose/yolo_pose_new_26_v4_16kp/results.csv`.

---

## Conclusion (obligatoire)

**`TRAINING_NOT_LAUNCHED`**
