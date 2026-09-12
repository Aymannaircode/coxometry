# V5 Strategy Diagnostic — YOLO11n-pose 14→16 KP

**Généré :** 2026-08-29  
**Mode :** READ-ONLY — aucun entraînement, aucune modification dataset/labels/V2/V4  
**Sources :** `v4_preflight.md`, `v4_vs_v2_anatomical_evaluation.md`, `v4_training_config.yaml`, `meta/keypoint_order.md`, probe architecture Ultralytics (session V5), `runs/pose/yolo_pose_new_26_v4_16kp-2/results.csv`

---

## Synthèse exécutive

| Constats | Valeur |
|----------|--------|
| V2 (14 KP) | mean error **128 px** — production |
| V4 (16 KP, run `-2`) | 14 KP communs **813 px** · IT **818 px** · **0 % CORRECT IT** |
| Cause racine V4 | Transfert Ultralytics **réinitialise 100 % de `cv4`** (pose head) — les 14 KP V2 ne sont **pas** préservés |
| Prérequis V5 | **Chirurgie tensorielle V2→V16** + validation epoch-0 **avant** tout entraînement |
| Dataset train IT | IT_R **16/21** v=2 · IT_L **19/21** v=2 — marginal mais non nul |

**Verdict :** la voie V4 standard (init V2 + fine-tuning global) est **invalidée**. V5 doit impérativement préserver les poids pose des 14 KP existants par surgery manuelle, puis n'entraîner que les canaux IT.

---

## 1. Architecture exacte YOLO11n-pose

| Paramètre | Valeur |
|-----------|--------|
| Fichier | `yolo11n-pose.yaml` → `ultralytics/cfg/models/11/yolo11-pose.yaml` |
| Scale **n** | depth=0.50 · width=0.25 · max_channels=1024 |
| Paramètres | ~**2.81 M** (14 KP) · ~**2.85 M** (16 KP) |
| GFLOPs | ~7.7 (doc Ultralytics) |
| Classes | **1** (`pelvis`) — override `nc=80` COCO |
| Entrée V2 | `kpt_shape: [14, 3]` · `nk = 42` |
| Entrée V5/V4 | `kpt_shape: [16, 3]` · `nk = 48` |
| Tête détection | Layer **23** — module `Pose(Detect)` sur P3/P4/P5 |

### Backbone (layers 0–10)

Conv + C3k2 + SPPF + C2PSA — identique détection/pose, **inchangé** entre V2 et V4.

### Neck + head (layers 11–23)

FPN bidirectionnel (Upsample/Concat/C3k2) → trois sorties **[16, 19, 22]** → `Pose(nc=1, kpt_shape=[16,3])`.

### Branches du module `Pose` (layer 23)

| Branche | Rôle | Tensor prefix |
|---------|------|---------------|
| `cv2` | Box (DFL) | `model.23.cv2.*` |
| `cv3` | Classification | `model.23.cv3.*` |
| `cv4` | Keypoints | `model.23.cv4.*` |

Structure `cv4` par échelle (P3, P4, P5) :

```
Conv(in_ch → c4, k=3) → Conv(c4 → c4, k=3) → Conv2d(c4 → nk, k=1)
```

où **`c4 = max(ch[0]//4, nk)`** — pour YOLO11n, `ch[0]=64` → **`c4 = nk`**.

| Modèle | nk | c4 | Params cv4 |
|--------|---:|---:|----------:|
| V2 14 KP | 42 | 42 | 222 894 |
| V4/V5 16 KP | 48 | 48 | 263 376 |

---

## 2. Structure de la pose head (`cv4`)

### Par échelle (ex. P3 / scale 0)

| Couche | V2 14 KP | V5 16 KP | Compatible `intersect_dicts` |
|--------|----------|----------|:------------------------------:|
| `cv4.0` conv1 weight | `(42, 64, 3, 3)` | `(48, 64, 3, 3)` | **Non** |
| `cv4.0` conv2 weight | `(42, 42, 3, 3)` | `(48, 48, 3, 3)` | **Non** |
| `cv4.0` conv_out weight | `(42, 42, 1, 1)` | `(48, 48, 1, 1)` | **Non** |
| × 3 échelles | 36 tensors cv4 | 36 tensors cv4 | **0/36 copiés** |

**Conséquence :** `PoseModel.load(V2)` via Ultralytics copie **505/541** tensors ; les **36 tensors cv4** sont **ignorés** et réinitialisés aléatoirement.

Box (`cv2`) et cls (`cv3`) : shapes **identiques** → copiés intégralement depuis V2.

---

## 3. Mapping exact 14 KP → 16 KP

Ordre fixe (`meta/keypoint_order.md`, `data.yaml`) :

| Index | Nom | Origine V2 | Statut |
|------:|-----|------------|--------|
| 0–13 | TD_R … FSD_L | LM-01 … LM-14 | **Identique V2** — labels inchangés B5 |
| **14** | **IT_R** | LM-17 | **Nouveau** |
| **15** | **IT_L** | LM-18 | **Nouveau** |

`flip_idx` : `[1,0,3,2,5,4,7,6,9,8,11,10,13,12,15,14]` — permutation R↔L incluant **14↔15**.

Format label : **53 colonnes** (5 + 16×3).

---

## 4. Tensors correspondant aux anciens KP

La sortie pose est un vecteur plat **`nk = 48`** (16 KP × 3 dims). Mapping **flat index → keypoint** :

```
flat = kp_index × 3 + dim   (dim: 0=x, 1=y, 2=v)
```

| Keypoint V2 | Index KP | Canaux plats (x, y, v) |
|-------------|----------|------------------------|
| TD_R | 0 | 0, 1, 2 |
| TD_L | 1 | 3, 4, 5 |
| … | … | … |
| FSD_L | 13 | 39, 40, 41 |
| IT_R | 14 | **42, 43, 44** |
| IT_L | 15 | **45, 46, 47** |

Dans **`cv4`** (chaque échelle), les **42 premières lignes** de chaque conv produisent les 14 KP V2 ; les **6 lignes 42–47** sont réservées à IT_R/IT_L.

---

## 5. Transfert direct des poids 14 KP → tête 16 KP

| Question | Réponse |
|----------|---------|
| Transfert automatique Ultralytics ? | **Non** — shape mismatch intégral sur cv4 |
| Transfert manuel possible ? | **Oui** — chirurgie par blocs |
| Procédure validée (probe V5) | Copier bloc supérieur/gauche V2 dans tensors 48×48 |

### Chirurgie tensorielle proposée (par échelle s ∈ {0,1,2})

| Tensor | Opération |
|--------|-----------|
| `cv4[s][0].weight` `(48,64,3,3)` | `W[:42] ← V2` · `W[42:48] ← 0` (ou petit bruit) |
| `cv4[s][1].weight` `(48,48,3,3)` | `W[:42,:42] ← V2` · reste ← 0 |
| `cv4[s][2].weight` `(48,48,1,1)` | `W[:42,:42] ← V2` · `W[42:,:42] ← 0` · IT block init séparée |
| BN / bias | Même logique par canal |

**Objectif :** avec entrées identiques, les sorties **canaux 0–41** du modèle 16 KP reproduisent V2 (à valider inference epoch-0).

**Non couvert par Ultralytics natif** — script custom obligatoire avant `--train`.

---

## 6. Initialisation séparée IT_R / IT_L

| Aspect | Faisabilité |
|--------|:-----------:|
| Canaux plats 42–47 isolés dans `cv4[s][2]` | **Oui** |
| Init IT indépendante des 14 KP V2 | **Oui** — lignes 42–47 + colonnes croisées à zéro |
| Init recommandée IT | Xavier/kaiming sur 6 canaux · ou régression géométrique depuis FSD (caudal) comme warm-start |
| `one2one_cv4` (end2end) | Non actif sur ce run (`end2end=false`) |

Les canaux IT **peuvent** être initialisés et entraînés séparément **si** les colonnes de cross-talk (42–47) restent gelées ou nulles pendant la phase IT-only.

---

## 7. Stratégie freeze

| Composant | Freeze V5 recommandé | Mécanisme |
|-----------|:----------------------:|-----------|
| **Backbone** (layers 0–22) | **Oui** | `requires_grad=False` ou `freeze=22` |
| **Box head** `cv2` | **Oui** | gel paramètres layer 23.cv2 |
| **Cls head** `cv3` | **Oui** | gel paramètres layer 23.cv3 |
| **Pose head** canaux 0–41 | **Oui** | gel lignes/colonnes 0:42 dans cv4 |
| **Pose head** canaux 42–47 (IT) | **Non** | seul bloc entraînable phase 1 |
| `freeze=23` (API Ultralytics) | **Insuffisant** | gèle toute la tête — inclut IT |
| `freeze=22` | **Partiel** | gèle backbone ; cv2/cv3/cv4 restent trainables → **risque V4** |

**Conclusion freeze :** l'API `freeze=N` d'Ultralytics ne permet **pas** le gel par canal KP. V5 requiert un **gel manuel par masque de gradient** sur les paramètres cv4 (ou deux phases : epoch-0 validation → masque IT-only).

---

## 8. Fine-tuning faible IT-only

| Paramètre V4 (échec) | V5 recommandé |
|----------------------|---------------|
| imgsz **960** | **640** (identique V2 — évite décalage d'échelle) |
| lr0 **3e-5** global | **≤ 1e-5** · **IT canaux seuls** |
| pose head réinit aléatoire | **Surgery V2** + gel 14 KP |
| Entraînement 16 KP joint | **Loss masquée IT** (indices 14–15) |
| warmup 4 | **10+** epochs IT-only |
| batch 1 | batch 1–2 |
| patience 20 | patience 30+ · early stop sur **erreur pixel IT** (pas mAP) |

### Garde-fous obligatoires (avant et pendant)

1. **Epoch-0 parity test** : mean error 14 KP ≤ **150 px** vs V2 sur 26 images (même imgsz/conf).
2. **Abort** si erreur 14 KP > 200 px après epoch 1.
3. Métriques : pixel IT + tiers CORRECT/INCERTAIN — **pas mAP seul** (V4 : mAP50(P)=0 malgré recall box=1).

---

## 9. Impact v=0 sur IT

Convention YOLO (`bi_ischial_final_policy.md`) : `v=0` → `(0,0,0)`.

Ultralytics (`loss.py`) :

```python
kpt_mask = gt_kpt[..., 2] != 0   # v=0 exclu de la loss position
kpts_obj_loss = BCE(pred_v, kpt_mask)  # v=0 → pas de pénalité position
```

| Landmark | v=2 (26) | v=0 (26) | v=2 **train** (21) |
|----------|--------:|--------:|-------------------:|
| IT_R | 20 | **6** | **16** |
| IT_L | 24 | **2** | **19** |

| Impact | Détail |
|--------|--------|
| Supervision effective IT_R train | **16 images** (76 % du train) |
| Cas v=0 train IT_R | B26_06, B26_11, B26_14, B26_15, B26_21, B26_26 |
| B26_26 IT_R | UNRESOLVABLE_REVIEW — v=0 correct en label, pas de signal position |
| Risque | Le modèle peut prédire IT sur v=0 sans pénalité position — acceptable cliniquement si inférence filtre conf/v |
| Facteur loss | `kpt_loss_factor = n_kpts / n_visible` — renormalise par KP visibles |

**v=0 réduit la supervision IT de ~24 % (IT_R)** — contribue à la difficulté mais n'explique pas l'échec V4 (813 px sur les **14 KP toujours v=2**).

---

## 10. 21 images train — suffisance

| Tâche | 21 images suffisantes ? | Justification |
|-------|:-----------------------:|---------------|
| Réapprendre **16 KP** joint (V4) | **Non** | V4 : 22 epochs · val/pose_loss ~**11** (vs V2 **1.67**) · 14 KP détruits |
| Préserver **14 KP** (surgery + freeze) | **Oui** | Poids V2 copiés — pas de réapprentissage |
| Apprendre **IT seul** (16–19 samples) | **Marginal** | V4 IT 0 % CORRECT ; anatomie difficile ; 20/52 REVIEW en QA B6 |
| ASL_L (déjà faible V2 ~525 px) | **Non** | Problème structurel indépendant — V5 ne doit pas aggraver |

**Conclusion dataset :** 21 images **insuffisantes** pour un fine-tuning pose global 16 KP ; **potentiellement suffisantes** pour IT-only **si** 14 KP gelés et métriques pixel strictes. En cas d'échec IT après 50 epochs → collecte supplémentaire ou détecteur IT séparé.

---

## 11. Alternative : V2 14 KP + détecteur IT séparé

| Critère | Single model V5 (surgery) | V2 + IT séparé |
|---------|:-------------------------:|:--------------:|
| Préservation 14 KP | Risque résiduel cross-talk cv4 | **Garantie** (V2 intact) |
| Complexité implémentation | Chirurgie + masque gradient custom | Deux modèles · ROI pelvis |
| Inférence | 1 passe | 2 passes (ou crop sur box V2) |
| Données IT | 16–19 samples | Idem — petit head sur features gelées V2 |
| Risque régression V2 | Faible si parity OK | **Nul** |
| Maintenance | Un artifact | Deux artifacts |

**Quand choisir l'alternative :** si epoch-0 parity échoue après surgery, ou si IT-only n'atteint pas CORRECT > 50 % sur val.

Architecture IT séparée recommandée : **petite tête conv** sur feature maps P3/P4 du backbone V2 gelé (pas retraining YOLO complet).

---

## 12. Preuve d'échec V4 (contexte décisionnel)

Run analysé : `runs/pose/yolo_pose_new_26_v4_16kp-2/` (22 epochs, early stop implicite).

| Métrique | V2 | V4 `-2` |
|----------|----|---------|
| mean error 14 KP | 128 px | **813 px** |
| mean error IT | — | **818 px** |
| % CORRECT IT | — | **0 %** |
| val/pose_loss | 1.67 | **~10.7** (stagnant) |
| mAP50(P) | 0.995 | **0.0** (22 epochs) |
| recall box | 1.0 | 1.0 |

**Mécanisme :** pose head aléatoire → prédictions 14 KP garbage ; fine-tuning global insuffisant pour reconverger sur 21 images ; box/cls OK mais **pose inutilisable cliniquement**.

---

## Stratégie V5 recommandée (UNE)

### Phase 0 — PRÉ-REQUIS (aucun training)

1. Script `surgical_init_v2_to_v16.py` : copie bloc V2 dans cv4 16 KP (§5).
2. Charger V2 best epoch 80 · copier backbone + cv2 + cv3 intacts.
3. **Epoch-0 parity test** : 14 KP mean error ≤ 150 px vs V2 @ imgsz=640 conf=0.25.
4. **STOP** si parity échoue — corriger surgery avant toute suite.

### Phase 1 — IT-only fine-tuning

| Paramètre | Valeur |
|-----------|--------|
| Init | Modèle chirurgien validé phase 0 |
| Gel | Backbone + cv2 + cv3 + cv4 canaux 0–41 |
| Trainable | cv4 canaux 42–47 uniquement |
| imgsz | **640** |
| lr0 | **1e-5** (AdamW) |
| epochs | 50 max · patience 30 |
| Loss | Pose/kobj sur KP 14–15 ; v=0 masqué (natif) |
| Augment | fliplr=0.5 · mosaic=0 · randaugment=null (identique V4 conservateur) |
| Évaluation | Pixel IT + parity 14 KP chaque epoch |

### Phase 2 — Fallback

Si IT mean > 300 px après phase 1 → **V2 production + tête IT séparée** sur features gelées (§11).

### Ce qu'il ne faut PAS refaire (leçon V4/V3)

- Fine-tuning global 16 KP sans surgery cv4
- imgsz 960/1280 sans validation parity
- mAP comme seule métrique de succès
- Entraînement avant epoch-0 parity 14 KP

---

## Matrice décisionnelle

| # | Question | Réponse V5 |
|---|----------|------------|
| 1 | Architecture | YOLO11n-pose · layer 23 Pose · nk 42→48 |
| 2 | Pose head | cv4 3-scale · c4=nk · **36 tensors non transférables** |
| 3 | Mapping 14→16 | Indices 0–13 identiques · 14=IT_R · 15=IT_L |
| 4 | Tensors anciens KP | Canaux plats 0–41 |
| 5 | Transfert direct auto | **Non** · surgery manuelle **Oui** |
| 6 | Init IT séparée | **Oui** · canaux 42–47 |
| 7 | Freeze | Backbone+cv2+cv3+cv4[0:42] · masque gradient custom |
| 8 | FT faible IT-only | **Oui** · lr≤1e-5 · imgsz 640 |
| 9 | Impact v=0 | 6 IT_R + 2 IT_L exclus loss · 16+19 samples train |
| 10 | 21 images | OK preservation · marginal IT · insuffisant joint 16 KP |
| 11 | Alternative | V2 + IT head séparé — fallback robuste |
| 12 | Stratégie principale | **Surgery + gel 14 KP + IT-only FT @ 640** |

---

## Conclusion

**`STRATEGY_RECOMMENDED`**

La stratégie V5 principale est : **chirurgie tensorielle cv4 V2→V16, validation epoch-0 des 14 KP, puis fine-tuning IT-only à très faible lr sur imgsz 640 avec gel complet du reste du modèle.** Aucun entraînement ne doit démarrer tant que la parity epoch-0 n'est pas validée. L'approche V2 + détecteur IT séparé reste le plan B si la parity ou la convergence IT échoue.

CSV détaillé : `v5_strategy_diagnostic.csv`
