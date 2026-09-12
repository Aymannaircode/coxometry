# V5 Phase 0 — Surgical Initialization + Epoch-0 Parity Test

**Généré :** 2026-08-29T01:03:07.610777+00:00
**Mode :** inference / validation ONLY — **aucun entraînement** (`model.train()` non appelé)

**V2 source :** `runs\pose\runs\pose\runs\yolo_pose_new_26_v2-3\weights\best.pt`
**SHA256 V2 :** `1f92d0867b4cd86eb6a4e3ec6111f812824b1b0d4d8dcd1d1ebe6c00ef2c48b8`
**V5 checkpoint :** `runs\pose\yolo_pose_new_26_v5_16kp\weights\v5_surgical_init.pt`

---

## 1. Inspection architecture

| Paramètre | V2 | V5 |
|-----------|----|----|
| kpt_shape | `[14, 3]` | `[16, 3]` |
| nk (canaux plats) | **42** | **48** |
| KP 0–13 (V2) | flat **0–41** | flat **0–41** (identique) |
| IT_R / IT_L | N/A | flat **42–47** (indices KP 14–15) |
| cv4 tensors | 36 | 36 |
| non-cv4 matched | — | **499** |

### Tensors cv4 (échantillon)

| Paramètre | Shape V2 | Shape V5 | Zone copiée |
|-----------|----------|----------|-------------|
| `model.23.cv4.0.0.bn.bias` | (42,) | (48,) | [0:42] <- V2; [42:48] <- IT init |
| `model.23.cv4.0.0.bn.num_batches_tracked` | MISSING | () | full copy |
| `model.23.cv4.0.0.bn.running_mean` | (42,) | (48,) | [0:42] <- V2; [42:48] <- IT init |
| `model.23.cv4.0.0.bn.running_var` | (42,) | (48,) | [0:42] <- V2; [42:48] <- IT init |
| `model.23.cv4.0.0.bn.weight` | (42,) | (48,) | [0:42] <- V2; [42:48] <- IT init |
| `model.23.cv4.0.0.conv.weight` | (42, 64, 3, 3) | (48, 64, 3, 3) | rows 0:42 <- V2; rows 42:48 <- IT init |
| `model.23.cv4.0.1.bn.bias` | (42,) | (48,) | [0:42] <- V2; [42:48] <- IT init |
| `model.23.cv4.0.1.bn.num_batches_tracked` | MISSING | () | full copy |
| `model.23.cv4.0.1.bn.running_mean` | (42,) | (48,) | [0:42] <- V2; [42:48] <- IT init |
| `model.23.cv4.0.1.bn.running_var` | (42,) | (48,) | [0:42] <- V2; [42:48] <- IT init |
| `model.23.cv4.0.1.bn.weight` | (42,) | (48,) | [0:42] <- V2; [42:48] <- IT init |
| `model.23.cv4.0.1.conv.weight` | (42, 42, 3, 3) | (48, 48, 3, 3) | rows 0:42 <- V2; rows 42:48 <- IT init |
| … | … | … | *30 tensors cv4 supplémentaires* |

---

## 2. Surgical copy

**Opérations documentées :** 42

Stratégie :
- Backbone + cv2 + cv3 : copie Ultralytics `intersect_dicts` (shapes identiques)
- cv4 : bloc supérieur/gauche V2 (42×42) copié ; expansion IT initialisée séparément

| V2 tensor | V5 tensor | Shape source → dest | Zone copiée |
|-----------|-----------|---------------------|-------------|
| `model.23.cv4.0.0.conv.weight` | `model.23.cv4.0.0.conv.weight` | (42, 64, 3, 3) → (48, 64, 3, 3) | block [:,42,:,64] <- V2; hidden expansion ZERO; IT kaiming on final only |
| `model.23.cv4.0.0.bn.weight` | `model.23.cv4.0.0.bn.weight` | (42,) → (48,) | [:42] <- V2; [42:] <- zero |
| `model.23.cv4.0.0.bn.bias` | `model.23.cv4.0.0.bn.bias` | (42,) → (48,) | [:42] <- V2; [42:] <- zero |
| `model.23.cv4.0.0.bn.running_mean` | `model.23.cv4.0.0.bn.running_mean` | (42,) → (48,) | [:42] <- V2; [42:] <- zero |
| `model.23.cv4.0.0.bn.running_var` | `model.23.cv4.0.0.bn.running_var` | (42,) → (48,) | [:42] <- V2; [42:] <- zero |
| `model.23.cv4.0.0.bn.num_batches_tracked` | `model.23.cv4.0.0.bn.num_batches_tracked` | () → () | full tensor |
| `model.23.cv4.0.1.conv.weight` | `model.23.cv4.0.1.conv.weight` | (42, 42, 3, 3) → (48, 48, 3, 3) | block [:,42,:,42] <- V2; hidden expansion ZERO; IT kaiming on final only |
| `model.23.cv4.0.1.bn.weight` | `model.23.cv4.0.1.bn.weight` | (42,) → (48,) | [:42] <- V2; [42:] <- zero |
| `model.23.cv4.0.1.bn.bias` | `model.23.cv4.0.1.bn.bias` | (42,) → (48,) | [:42] <- V2; [42:] <- zero |
| `model.23.cv4.0.1.bn.running_mean` | `model.23.cv4.0.1.bn.running_mean` | (42,) → (48,) | [:42] <- V2; [42:] <- zero |
| `model.23.cv4.0.1.bn.running_var` | `model.23.cv4.0.1.bn.running_var` | (42,) → (48,) | [:42] <- V2; [42:] <- zero |
| `model.23.cv4.0.1.bn.num_batches_tracked` | `model.23.cv4.0.1.bn.num_batches_tracked` | () → () | full tensor |
| `model.23.cv4.0.2.weight` | `model.23.cv4.0.2.weight` | (42, 42, 1, 1) → (48, 48, 1, 1) | block [:,42,:,42] <- V2; hidden expansion ZERO; IT kaiming on final only |
| `model.23.cv4.0.2.bias` | `model.23.cv4.0.2.bias` | (42,) → (48,) | [:42] <- V2; [42:] <- zero |
| `model.23.cv4.1.0.conv.weight` | `model.23.cv4.1.0.conv.weight` | (42, 128, 3, 3) → (48, 128, 3, 3) | block [:,42,:,128] <- V2; hidden expansion ZERO; IT kaiming on final only |
| … | … | … | *27 ops supplémentaires — voir CSV* |

---

## 3. Vérification numérique (zones V2 copiées)

| Métrique | Valeur |
|----------|-------:|
| Valeurs copiées (zones V2) | 223404 |
| Valeurs différentes | 0 |
| Max abs diff | 0.00e+00 |
| Mean abs diff | 0.00e+00 |
| Zones identiques (tol 0) | Oui |

---

## 4. Initialisation IT_R / IT_L

| Canal | Init | Justification |
|-------|------|---------------|
| cv4 expansion rows 42–47 (conv0/conv1) | **Zéro** | Pas de signal caché IT → preserve 14 KP |
| cv4 final conv rows 42–47 | **Kaiming uniform** | Init IT output uniquement |
| bias IT | **Zéro** | Neutre à epoch 0 |

**Aucune valeur des 14 KP V2 réutilisée pour IT.**

---

## 5. Epoch-0 parity test (14 KP)

Protocole identique à `v4_vs_v2_anatomical_evaluation` : imgsz=640, conf=0.25, 26 DICOM, GT v≥2.

### Global 14 KP

| Métrique | V2 | V5 (14 KP) |
|----------|---:|----------:|
| n | 364 | 364 |
| mean | 128.48 | 128.48 |
| median | 85.77 | 85.77 |
| p90 | 243.20 | 243.20 |
| min | 2.03 | 2.03 |
| max | 813.76 | 813.76 |

**Tiers V2 :** CORRECT=151 INCERTAIN=123 INCORRECT=90
**Tiers V5 (14 KP) :** CORRECT=151 INCERTAIN=123 INCORRECT=90

### Par landmark (mean px)

| Landmark | V2 | V5 | Δ |
|----------|---:|---:|--:|
| TD_R | 64.17 | 64.17 | 0.00 |
| TD_L | 64.45 | 64.45 | 0.00 |
| FHC_R | 62.19 | 62.19 | 0.00 |
| FHC_L | 57.96 | 57.96 | 0.00 |
| ASL_R | 143.79 | 143.79 | 0.00 |
| ASL_L | 525.40 | 525.40 | -0.00 |
| ASM_R | 93.83 | 93.83 | 0.00 |
| ASM_L | 78.23 | 78.23 | 0.00 |
| FNM_R | 62.12 | 62.12 | 0.00 |
| FNM_L | 58.22 | 58.22 | 0.00 |
| FSP_R | 150.86 | 150.86 | 0.00 |
| FSP_L | 169.99 | 169.99 | 0.00 |
| FSD_R | 159.41 | 159.41 | 0.00 |
| FSD_L | 108.04 | 108.04 | 0.00 |

**Détection :** V2=26/26 · V5=26/26

---

## 6. Critère GO / NO-GO

| Critère | Seuil | Résultat | Pass |
|---------|-------|----------|:----:|
| Mean error 14 KP V5 | ≤ 150.0 px | 128.48 px | ✓ |
| Dégradation catastrophique | aucune (>×3.0 V2) | aucune | ✓ |
| Détection | V5 ≥ V2 | 26 ≥ 26 | ✓ |

---

## 7. IT (informatif — hors critère parité)

| Métrique | IT pooled (n=44) |
|----------|------:|
| mean px | 928.43 |
| median px | 904.87 |
| % CORRECT | 0.0% |

*IT non évalué pour GO/NO-GO — canaux non issus de V2.*

---

## 8. Intégrité

| Zone | Modifié |
|------|:-------:|
| V2 best.pt | **Non** |
| V4 | **Non** |
| Labels / dataset | **Non** |
| Entraînement | **Non** |

---

## Conclusion

**`V5_PHASE0_GO`**

Parité epoch-0 validée. **Phase 1 non lancée** — validation humaine requise avant IT-only fine-tuning.

CSV : `v5_surgical_init_report.csv`