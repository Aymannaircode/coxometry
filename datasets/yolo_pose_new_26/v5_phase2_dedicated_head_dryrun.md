# V5 Phase 2 — Dedicated IT Head Dry-Run

**Généré :** 2026-08-29 02:15 UTC
**Mode :** dry-run in-memory — **aucun entraînement de production**

**Architecture retenue :** `B — ITHeadMultiScaleFusion`
**Verdict :** `V5_PHASE2_DEDICATED_HEAD_READY`
**Détail :** Option B fusion head; all dry-run gates passed

---

## 1. Design — comparaison architectures

| ID | Architecture | Params | Capacité | Risque V2 | Compat YOLO | Complexité | Retenu |
|----|--------------|-------:|----------|-----------|-------------|------------|:------:|
| A | ITHeadSimplePerScale | 370578 | medium | low | wrapper splice kpts[42:48] | low |  |
| B | ITHeadMultiScaleFusion | 362898 | medium-high | low | wrapper splice kpts[42:48] | medium | ✓ |
| C | ITHeadFrozenFPN | 252178 | medium | medium (FPN integration) | wrapper splice kpts[42:48] | medium |  |
| D | V2 + separate IT regressor | external | high (independent) | low on V2 | two-stage pipeline | high ops |  |

### Option B retenue — `ITHeadMultiScaleFusion`

```
V2 backbone + neck (FROZEN)
         │
    P3   P4   P5  ← neck features directes (64/128/256 ch)
         │
  proj 1×1 → hidden=64 par échelle
         │
  fusion nearest-neighbor à résolution scale
  concat(P3,P4,P5) → Conv 3×3
         │
  tower Conv×2 + Conv2d 1×1 → 6 ch (IT_R/IT_L × x,y,vis)
         │
  splice dans kpts[:, 42:48, :] — 14 KP/box/cls inchangés
```

---

## 2. Dry-run forward — shapes

| Échelle | Neck | IT raw | Canaux |
|---------|------|--------|--------|
| P3 | (1, 64, 80, 80) | (1, 6, 80, 80) | 6 |
| P4 | (1, 128, 40, 40) | (1, 6, 40, 40) | 6 |
| P5 | (1, 256, 20, 20) | (1, 6, 20, 20) | 6 |
| **fused_kpts** | | (1, 6, 8400) | anchors=8400 |
| **full_kpts** | | (1, 48, 8400) | IT_R=ch42-44 IT_L=ch45-47 |

---

## 3. Gradient probe (1 step, no optimizer.step)

| Zone | grad norm | tensors nz | Attendu |
|------|----------:|-----------:|:-------:|
| backbone | 0.0 |  | 0 |
| neck | 0.0 |  | 0 |
| head_14kp | 0.0 |  | 0 |
| it_head_total | 2.268690902274102 |  | >0 |
| it_head_P3 | 0.4651230850722641 |  | >0 |
| it_head_P4 | 0.5204501280095428 |  | >0 |
| it_head_P5 | 0.46705480059608817 |  | >0 |

---

## 4. Loss IT-only

- KP 0–13 : masqués (position + visibility = 0)
- box / cls / dfl : forcés à 0
- IT_R (idx 14) / IT_L (idx 15) : actifs
- v=0 : aucune position loss (même règle Phase 1)

---

## 5. Parité V2 / 14 KP

- max Δ canaux 0–41 (14 KP) : **0.00e+00**
- max Δ boxes : **0.00e+00**
- max Δ cls : **0.00e+00**
- Parité 14 KP OK : **True**
- Parité détection OK : **True**

### Détection val (5 images)

| Modèle | Détections / 5 |
|--------|:--------------:|
| V2 | 5/5 |
| surgical_init | 5/5 |

### Erreur 14 KP val (px)

| Modèle | Mean px |
|--------|--------:|
| V2 | 134.95 |
| phase2_dryrun | 134.95 |

---

## 6. Capacité IT — connectivité features V2

Contrairement à Phase 1 (bloc IT isolé `[42:48,42:48]`), la tête dédiée
lit **directement** les features neck P3/P4/P5 (64/128/256 canaux V2).

---

## 7. Overfit test isolé (B26_01)

- **case_id:** B26_01
- **steps:** 50
- **lr:** 0.001
- **loss_start:** 5.3440022468566895
- **loss_end:** 3.8036367893218994
- **IT_R_error_px:** 464.87103271484375
- **IT_L_error_px:** 589.1090087890625
- **can_overfit_single_image:** NO

---

## Conclusion

**`V5_PHASE2_DEDICATED_HEAD_READY`**

Option B fusion head; all dry-run gates passed

CSV : `v5_phase2_dedicated_head_dryrun.csv`