# V5 IT Head Capacity Diagnostic

**Généré :** 2026-08-29 02:11 UTC
**Mode :** READ-ONLY — aucun entraînement de production

**Verdict capacité :** `IT_HEAD_CAPACITY_INSUFFICIENT`
**Recommandation :** `V5_PHASE2_DEDICATED_HEAD`

---

## 1. Paramètres entraînables IT (cv4)

**Total paramètres entraînables (masque IT) :** 18558
**Tensors avec hooks :** 24 (attendu 24)

**Mapping canaux plats :**
- KP 14 `IT_R` → canaux 42 (x), 43 (y), 44 (vis)
- KP 15 `IT_L` → canaux 45 (x), 46 (y), 47 (vis)

**Échelles cv4 :** P3=`model.23.cv4.0`, P4=`model.23.cv4.1`, P5=`model.23.cv4.2`

| Paramètre | Shape | Trainable | Échelle | Couche |
|-----------|-------|----------:|---------|--------|
| `model.23.cv4.0.0.conv.weight` | (48, 64, 3, 3) | 1188 | P3 | 0 |
| `model.23.cv4.0.0.bn.weight` | (48,) | 6 | P3 | 0 |
| `model.23.cv4.0.0.bn.bias` | (48,) | 6 | P3 | 0 |
| `model.23.cv4.0.1.conv.weight` | (48, 48, 3, 3) | 324 | P3 | 1 |
| `model.23.cv4.0.1.bn.weight` | (48,) | 6 | P3 | 1 |
| `model.23.cv4.0.1.bn.bias` | (48,) | 6 | P3 | 1 |
| `model.23.cv4.0.2.weight` | (48, 48, 1, 1) | 36 | P3 | 2 |
| `model.23.cv4.0.2.bias` | (48,) | 6 | P3 | 2 |
| `model.23.cv4.1.0.conv.weight` | (48, 128, 3, 3) | 4644 | P4 | 0 |
| `model.23.cv4.1.0.bn.weight` | (48,) | 6 | P4 | 0 |
| `model.23.cv4.1.0.bn.bias` | (48,) | 6 | P4 | 0 |
| `model.23.cv4.1.1.conv.weight` | (48, 48, 3, 3) | 324 | P4 | 1 |
| `model.23.cv4.1.1.bn.weight` | (48,) | 6 | P4 | 1 |
| `model.23.cv4.1.1.bn.bias` | (48,) | 6 | P4 | 1 |
| `model.23.cv4.1.2.weight` | (48, 48, 1, 1) | 36 | P4 | 2 |
| `model.23.cv4.1.2.bias` | (48,) | 6 | P4 | 2 |
| `model.23.cv4.2.0.conv.weight` | (48, 256, 3, 3) | 11556 | P5 | 0 |
| `model.23.cv4.2.0.bn.weight` | (48,) | 6 | P5 | 0 |
| `model.23.cv4.2.0.bn.bias` | (48,) | 6 | P5 | 0 |
| `model.23.cv4.2.1.conv.weight` | (48, 48, 3, 3) | 324 | P5 | 1 |
| `model.23.cv4.2.1.bn.weight` | (48,) | 6 | P5 | 1 |
| `model.23.cv4.2.1.bn.bias` | (48,) | 6 | P5 | 1 |
| `model.23.cv4.2.2.weight` | (48, 48, 1, 1) | 36 | P5 | 2 |
| `model.23.cv4.2.2.bias` | (48,) | 6 | P5 | 2 |

---

## 2. Chemin gradient / isolation IT

Le bloc trainable `[42:48, 42:48]` isole les canaux IT des activations V2 (0–41).

| Tensor | Échelle | IT→old cols | IT→IT cols | Isolé V2 |
|--------|---------|------------:|-----------:|:--------:|
| `model.23.cv4.0.0.conv.weight` | P3 | 0.00e+00 | 0.00e+00 | True |
| `model.23.cv4.0.1.conv.weight` | P3 | 0.00e+00 | 0.00e+00 | True |
| `model.23.cv4.0.2.weight` | P3 | 0.00e+00 | 7.15e+00 | True |
| `model.23.cv4.1.0.conv.weight` | P4 | 0.00e+00 | 0.00e+00 | True |
| `model.23.cv4.1.1.conv.weight` | P4 | 0.00e+00 | 0.00e+00 | True |
| `model.23.cv4.1.2.weight` | P4 | 0.00e+00 | 7.11e+00 | True |
| `model.23.cv4.2.0.conv.weight` | P5 | 0.00e+00 | 0.00e+00 | True |
| `model.23.cv4.2.1.conv.weight` | P5 | 0.00e+00 | 0.00e+00 | True |
| `model.23.cv4.2.2.weight` | P5 | 0.00e+00 | 8.03e+00 | True |

---

## 3. Gradients sur batch réel (final checkpoint, 1 step)

| Tensor | Échelle | grad_norm IT | grad_max |
|--------|---------|-------------:|---------:|
| `model.23.cv4.2.0.conv.weight` | P5 | 1.538736e+00 | 8.429044e-02 |
| `model.23.cv4.2.2.bias` | P5 | 5.446452e-01 | 3.601620e-01 |
| `model.23.cv4.2.1.conv.weight` | P5 | 1.906859e-01 | 3.996727e-02 |
| `model.23.cv4.2.2.weight` | P5 | 1.730690e-01 | 7.474717e-02 |
| `model.23.cv4.2.1.bn.bias` | P5 | 5.834167e-02 | 3.582806e-02 |
| `model.23.cv4.2.0.bn.weight` | P5 | 2.797856e-02 | 2.326475e-02 |
| `model.23.cv4.2.1.bn.weight` | P5 | 1.785646e-02 | 1.112244e-02 |
| `model.23.cv4.2.0.bn.bias` | P5 | 1.325710e-02 | 1.052739e-02 |
| `model.23.cv4.0.0.conv.weight` | P3 | 0.000000e+00 | 0.000000e+00 |
| `model.23.cv4.0.0.bn.weight` | P3 | 0.000000e+00 | 0.000000e+00 |
| `model.23.cv4.0.0.bn.bias` | P3 | 0.000000e+00 | 0.000000e+00 |
| `model.23.cv4.0.1.conv.weight` | P3 | 0.000000e+00 | 0.000000e+00 |
| `model.23.cv4.0.1.bn.weight` | P3 | 0.000000e+00 | 0.000000e+00 |
| `model.23.cv4.0.1.bn.bias` | P3 | 0.000000e+00 | 0.000000e+00 |
| `model.23.cv4.0.2.weight` | P3 | 0.000000e+00 | 0.000000e+00 |

**Par échelle (L2 agrégé) :**

| Échelle | grad_norm IT |
|---------|-------------:|
| P3 | 0.000000e+00 |
| P4 | 0.000000e+00 |
| P5 | 1.653887e+00 |

---

## 4. Activations IT vs V2 (surgical_init, forward)

| Échelle | Couche | mean|old| | mean|IT| | ratio IT/old |
|---------|--------|----------:|---------:|-------------:|
| P3 | 0 | 0.396651 | 0.000000e+00 | 0.000000e+00 |
| P3 | 1 | 0.357788 | 0.000000e+00 | 0.000000e+00 |
| P3 | 2 | 0.278419 | 0.000000e+00 | 0.000000e+00 |
| P4 | 0 | 0.392922 | 0.000000e+00 | 0.000000e+00 |
| P4 | 1 | 0.338348 | 0.000000e+00 | 0.000000e+00 |
| P4 | 2 | 0.269024 | 0.000000e+00 | 0.000000e+00 |
| P5 | 0 | 0.348551 | 0.000000e+00 | 0.000000e+00 |
| P5 | 1 | 0.321043 | 0.000000e+00 | 0.000000e+00 |
| P5 | 2 | 0.328839 | 0.000000e+00 | 0.000000e+00 |

*Couches 0–1 : IT activations ≈ 0 (poids hidden IT initialisés à zéro).*

---

## 5. Prédictions IT brutes (val v≥2)

| Modèle | Case | Landmark | GT px | Pred px | Erreur px |
|--------|------|----------|------:|--------:|----------:|
| surgical_init | B26_10 | IT_R | (822,2258) | (1520,1467) | 1054.4 |
| surgical_init | B26_10 | IT_L | (1975,2210) | (1520,1467) | 871.3 |
| surgical_init | B26_13 | IT_R | (892,2342) | (1617,1561) | 1065.3 |
| surgical_init | B26_13 | IT_L | (2168,2292) | (1617,1561) | 915.2 |
| surgical_init | B26_17 | IT_R | (518,2190) | (1382,1498) | 1106.5 |
| surgical_init | B26_17 | IT_L | (1820,2155) | (1382,1498) | 789.8 |
| surgical_init | B26_20 | IT_R | (688,2208) | (1215,1595) | 808.5 |
| surgical_init | B26_20 | IT_L | (1888,2188) | (1215,1595) | 896.5 |
| surgical_init | B26_26 | IT_R | (0,0) | (1270,1354) | 1856.1 |
| surgical_init | B26_26 | IT_L | (1998,1998) | (1270,1354) | 972.3 |
| epoch1_best | B26_10 | IT_R | (822,2258) | (1511,1475) | 1043.0 |
| epoch1_best | B26_10 | IT_L | (1975,2210) | (1529,1480) | 855.5 |
| epoch1_best | B26_13 | IT_R | (892,2342) | (1608,1570) | 1053.2 |
| epoch1_best | B26_13 | IT_L | (2168,2292) | (1627,1575) | 898.3 |
| epoch1_best | B26_17 | IT_R | (518,2190) | (1374,1505) | 1096.2 |
| epoch1_best | B26_17 | IT_L | (1820,2155) | (1390,1509) | 775.5 |
| epoch1_best | B26_20 | IT_R | (688,2208) | (1208,1602) | 798.4 |
| epoch1_best | B26_20 | IT_L | (1888,2188) | (1224,1606) | 882.6 |
| epoch1_best | B26_26 | IT_R | (0,0) | (1262,1361) | 1856.2 |
| epoch1_best | B26_26 | IT_L | (1998,1998) | (1279,1365) | 957.8 |
| final_best | B26_10 | IT_R | (822,2258) | (1500,1485) | 1028.3 |
| final_best | B26_10 | IT_L | (1975,2210) | (1543,1496) | 834.3 |
| final_best | B26_13 | IT_R | (892,2342) | (1597,1581) | 1037.5 |
| final_best | B26_13 | IT_L | (2168,2292) | (1642,1593) | 875.5 |
| final_best | B26_17 | IT_R | (518,2190) | (1364,1514) | 1082.8 |
| final_best | B26_17 | IT_L | (1820,2155) | (1403,1525) | 756.1 |
| final_best | B26_20 | IT_R | (688,2208) | (1199,1611) | 785.3 |
| final_best | B26_20 | IT_L | (1888,2188) | (1236,1621) | 863.9 |
| final_best | B26_26 | IT_R | (0,0) | (1252,1370) | 1856.3 |
| final_best | B26_26 | IT_L | (1998,1998) | (1291,1381) | 938.2 |

---

## 6. Initialisation zero-hidden + Kaiming conv_out

**Effet :**
- conv0/conv1 IT `[42:48,:]` = **zéro** → activations IT hidden nulles au forward
- conv2 IT `[42:48,42:48]` = Kaiming, mais entrée IT hidden = 0 → sortie IT ≈ biais seul
- Les features backbone (64/128/256 ch) alimentent les canaux V2 0–41, **pas** les canaux IT 42–47

**Conséquence :** l'IT head démarre sans accès aux représentations V2 ; il doit reconstruire
une chaîne de features IT from scratch via un sous-réseau 6-canaux isolé.

---

## 7. Suffisance gradient (ordre de grandeur)

- **total_it_grad_norm:** 2.5645697759464383
- **mean_it_error_px:** 1005.8262017871518
- **lr:** 1e-05
- **est_weight_delta_per_step:** 2.5645697759464387e-05
- **heuristic_steps_for_100px_reduction:** 784401.5095404903
- **verdict:** INSUFFICIENT

---

## 8. Architectures alternatives (dry-run)

| ID | Architecture | Params | Risque V2 | Compat 14 KP |
|----|--------------|--------|-----------|--------------|
| A | Current (cv4 expansion + zero hidden + IT block trainable)… | 18558 | None if freeze holds | Full parity (frozen V2 block) |
| B | IT head more trainable params (unfreeze IT rows x all input … | ~9000 | Medium — needs hook on old cols zero grad | Risk if conv2 old cols drift |
| C | Dedicated IT head on frozen neck features (parallel conv tow… | ~50000-150000 | None on V2 weights | Full — V2 head untouched |
| D | V2 + separate IT regressor model… | Independent model | None | Perfect — V2 unchanged |

### A. Current (cv4 expansion + zero hidden + IT block trainable)
- **Chemin gradient :** IT rows 42-47 only; isolated from V2 hidden 0-41
- **Avantages :** Minimal diff vs V2; 14 KP exact parity
- **Inconvénients :** IT path disconnected from rich V2 features; zero-init hidden bottleneck

### B. IT head more trainable params (unfreeze IT rows x all input cols in conv2)
- **Chemin gradient :** IT output rows connect to all 48 hidden channels incl. V2 0-41
- **Avantages :** IT preds can leverage frozen V2 hidden activations immediately
- **Inconvénients :** More complex freeze; partial coupling to 14 KP representation

### C. Dedicated IT head on frozen neck features (parallel conv tower)
- **Chemin gradient :** Direct from P3/P4/P5 features to 2 KP
- **Avantages :** Clean separation; full feature access; tunable capacity
- **Inconvénients :** Custom module; export/inference integration; more training data needed

### D. V2 + separate IT regressor model
- **Chemin gradient :** V2 frozen inference → IT model input
- **Avantages :** Fastest path to production IT; no YOLO surgery
- **Inconvénients :** Two-stage pipeline; alignment with box; maintenance overhead

---

## 9. Overfit test (1 image, checkpoint temporaire)

- **case_id:** B26_01
- **steps:** 50
- **lr:** 0.001
- **loss_start:** 12.654488563537598
- **loss_end:** 8.473082542419434
- **IT_R_error_px:** None
- **IT_L_error_px:** None
- **surgical_mean_err_px:** None
- **can_overfit_single_image:** NO
- **temp_checkpoint:** C:\Users\g\OneDrive\Desktop\Projet-Ayman\datasets\yolo_pose_new_26\_v5_it_overfit_temp\overfit_probe.pt

---

## Conclusion

**`IT_HEAD_CAPACITY_INSUFFICIENT`**

**Recommandation : `V5_PHASE2_DEDICATED_HEAD`**

Phase 1 v3 a montré une amélioration IT de ~18 px sur 900 px avec 9 epochs —
gradient actif mais capacité/connectivité insuffisante pour converger vers <75 px.

CSV : `v5_it_head_capacity_diagnostic.csv`