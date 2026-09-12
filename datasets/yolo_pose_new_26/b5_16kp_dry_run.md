# B5 — Dry-run 14 → 16 keypoints

**Généré :** 2026-08-29  
**Mode :** DRY-RUN **READ-ONLY** — aucun label officiel, `data.yaml`, modèle ou training modifié  
**Statut :** **`B5_DRY_RUN_READY`**  
**Sources :** `b6_working_annotations/`, `bi_ischial_final_policy.md`, `b6_global_final_QA.csv`

---

## 1. Schéma proposé (non appliqué)

| Index | Keypoint | Origine |
|------:|----------|---------|
| 0–13 | TD_R … FSD_L | Labels officiels 14 kp — **inchangés** |
| **14** | **IT_R** | Working B6 |
| **15** | **IT_L** | Working B6 |

`flip_idx` proposé : `[1,0,3,2,5,4,7,6,9,8,11,10,13,12,15,14]` — **non modifié**.

## 2. Règles dry-run appliquées

| Règle | Conduite |
|-------|----------|
| v=2 | Repère caudal identifiable (PASS ou REVIEW difficile) |
| v=0 | Repère **non identifiable** uniquement — pas par difficulté seule |
| REVIEW | Conservé — pas de promotion auto PASS |
| Coordonnées | Lues depuis working ; v=0 → (0,0,0) YOLO ; coords working en référence |
| B26_26 IT_R | UNRESOLVABLE → v=0 proposé, décision documentée |
| B26_05 | CLINICAL_GATE — v=2 proposé, v=0 reste défendable |

## 3. Statistiques

| Métrique | Valeur |
|----------|-------:|
| Images | **26** |
| IT_R v=2 (index 14) | **20** |
| IT_R v=0 (index 14) | **6** |
| IT_L v=2 (index 15) | **24** |
| IT_L v=0 (index 15) | **2** |
| Landmarks REVIEW source | **20** |
| Landmarks UNRESOLVABLE source | **1** |
| Images avec REVIEW ou UNRESOLVABLE | **15** |
| Images avec v=0 proposé | **7** |
| Images CLINICAL_GATE (B26_05) | **1** |

### IT_R v=0 proposé (6)

- **B26_06** — PROPOSE_V0 — source REVIEW
- **B26_11** — PROPOSE_V0 — source REVIEW
- **B26_14** — PROPOSE_V0 — source REVIEW
- **B26_15** — PROPOSE_V0 — source REVIEW
- **B26_21** — PROPOSE_V0 — source REVIEW
- **B26_26** — PROPOSE_V0_UNRESOLVABLE — source UNRESOLVABLE_REVIEW

### IT_L v=0 proposé (2)

- **B26_15** — PROPOSE_V0 — source REVIEW
- **B26_19** — PROPOSE_V0 — source REVIEW

### Images REVIEW / UNRESOLVABLE

- **B26_03** — `PASS/REVIEW`
- **B26_05** — `REVIEW/REVIEW`
- **B26_06** — `REVIEW/PASS`
- **B26_07** — `REVIEW/PASS`
- **B26_08** — `REVIEW/PASS`
- **B26_09** — `REVIEW/PASS`
- **B26_11** — `REVIEW/REVIEW`
- **B26_14** — `REVIEW/REVIEW`
- **B26_15** — `REVIEW/REVIEW`
- **B26_16** — `REVIEW/PASS`
- **B26_18** — `PASS/REVIEW`
- **B26_19** — `REVIEW/REVIEW`
- **B26_21** — `REVIEW/PASS`
- **B26_25** — `PASS/REVIEW`
- **B26_26** — `UNRESOLVABLE_REVIEW/REVIEW`

## 4. Cas spécial B26_26 IT_R

| Attribut | Valeur |
|----------|--------|
| Statut source | UNRESOLVABLE_REVIEW |
| Working ref | (552.0, 2088.0) v=2 |
| Dry-run proposé | (0, 0) v=0 — index 14 |
| Décision | **PROPOSE_V0_UNRESOLVABLE** |
| Justification | Apex caudal indéterminable après revue supervisée ; annotation inventée refusée ; v=0 requis avant label officiel |
| B26_26 IT_L | v=2 proposé (1998, 1998) — REVIEW, re-valider après arbitrage IT_R |

## 5. Matrice 26 images

| Image | IT_R (idx14) x/y/v | IT_L (idx15) x/y/v | Source | Décision |
|-------|-------------------:|-------------------:|--------|----------|
| B26_01 | 548.0/2140.0/2 | 1772.0/2178.0/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_02 | 552.0/1838.0/2 | 1879.0/1826.0/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_03 | 718.0/2188.0/2 | 2068.0/2068.0/2 | `PASS/REVIEW` | PROPOSE_V2_PASS / PROPOSE_V2_REVIEW |
| B26_04 | 738.0/2338.0/2 | 2193.1/2256.9/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_05 | 648.0/2955.0/2 | 2412.0/2960.0/2 | `REVIEW/REVIEW` | CLINICAL_GATE_V2 / CLINICAL_GATE_V2 |
| B26_06 | 0.0/0.0/0 | 1882.0/2228.0/2 | `REVIEW/PASS` | PROPOSE_V0 / PROPOSE_V2_PASS |
| B26_07 | 708.0/2548.0/2 | 1778.0/2548.0/2 | `REVIEW/PASS` | PROPOSE_V2_REVIEW / PROPOSE_V2_PASS |
| B26_08 | 650.7/2207.9/2 | 1718.0/2192.0/2 | `REVIEW/PASS` | PROPOSE_V2_REVIEW / PROPOSE_V2_PASS |
| B26_09 | 778.0/2138.0/2 | 2255.0/2092.0/2 | `REVIEW/PASS` | PROPOSE_V2_REVIEW / PROPOSE_V2_PASS |
| B26_10 | 822.0/2258.0/2 | 1975.0/2210.0/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_11 | 0.0/0.0/0 | 1958.0/2495.0/2 | `REVIEW/REVIEW` | PROPOSE_V0 / PROPOSE_V2_REVIEW |
| B26_12 | 846.0/2198.0/2 | 2038.0/2210.0/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_13 | 892.0/2342.0/2 | 2168.3/2291.9/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_14 | 0.0/0.0/0 | 1994.0/2158.0/2 | `REVIEW/REVIEW` | PROPOSE_V0 / PROPOSE_V2_REVIEW |
| B26_15 | 0.0/0.0/0 | 0.0/0.0/0 | `REVIEW/REVIEW` | PROPOSE_V0 / PROPOSE_V0 |
| B26_16 | 730.4/2245.7/2 | 1978.0/2198.0/2 | `REVIEW/PASS` | PROPOSE_V2_REVIEW / PROPOSE_V2_PASS |
| B26_17 | 518.0/2190.0/2 | 1820.0/2155.0/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_18 | 772.2/1925.2/2 | 2072.0/1848.0/2 | `PASS/REVIEW` | PROPOSE_V2_PASS / PROPOSE_V2_REVIEW |
| B26_19 | 768.0/2138.0/2 | 0.0/0.0/0 | `REVIEW/REVIEW` | PROPOSE_V2_REVIEW / PROPOSE_V0 |
| B26_20 | 688.0/2208.0/2 | 1888.0/2188.0/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_21 | 0.0/0.0/0 | 2012.0/2518.0/2 | `REVIEW/PASS` | PROPOSE_V0 / PROPOSE_V2_PASS |
| B26_22 | 828.0/2308.0/2 | 2024.0/2238.0/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_23 | 892.0/2108.0/2 | 2178.0/2018.0/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_24 | 698.0/2398.0/2 | 1858.0/2328.0/2 | `PASS/PASS` | PROPOSE_V2_PASS / PROPOSE_V2_PASS |
| B26_25 | 665.0/2245.0/2 | 1998.0/2178.0/2 | `PASS/REVIEW` | PROPOSE_V2_PASS / PROPOSE_V2_REVIEW |
| B26_26 | 0.0/0.0/0 | 1998.0/1998.0/2 | `UNRESOLVABLE_REVIEW/REVIEW` | PROPOSE_V0_UNRESOLVABLE / PROPOSE_V2_REVIEW |

## 6. Interdictions respectées

- Aucun label YOLO officiel modifié  
- Aucune modification `data.yaml`  
- V2 / V3 / backend / Flutter intouchés  
- Aucun training lancé  
- Working annotations non modifiées

## 7. Conclusion

**`B5_DRY_RUN_READY`** — Extension 16 kp simulée sur 26 images. 20 IT_R et 24 IT_L en v=2 ; 6 IT_R et 2 IT_L en v=0 proposé. 20 landmarks REVIEW et 1 UNRESOLVABLE conservés sans promotion auto. Prochaine étape : validation clinique puis écriture labels officiels (hors scope dry-run).

---
*Fichiers : `b5_16kp_dry_run.csv`, `b5_16kp_dry_run.md`*