# B6 — Queue revue manuelle complète (52 landmarks)

**Généré :** 2026-08-28  
**Statut :** `MANUAL_REVIEW_52_REQUIRED`  
**Mode :** planification uniquement — **aucune coordonnée modifiée** à cette étape  

**Contexte QA global :** 52 landmarks · 7 PASS · 45 REVIEW · 0 FAIL · conclusion `REVIEW_REQUIRED`  
**Biais identifié :** pré-annotations `offset + scan` systématiquement **trop crâniales** sur ~15–20 cas  

---

## Règles de session

| Interdit | Autorisé |
|----------|----------|
| Promotion vers labels officiels | Revue visuelle manuelle |
| Modification `data.yaml` | KEEP / MOVE / REVIEW / INVALID |
| Modification V2/V3 | Notes dans log de session (étape suivante) |
| Training YOLO | |
| Code production | |
| **Calcul auto de nouvelles coordonnées** | **Placement visuel uniquement** |

### Actions reviewer

| Action | Signification |
|--------|---------------|
| **KEEP** | Point correctement placé selon B1/B4 — aucun déplacement |
| **MOVE** | Correction visuelle nécessaire (caudalité, anti-fémur, FOV…) |
| **REVIEW** | Ambiguïté — décision différée ou confirmation requise |
| **INVALID** | Structure non identifiable — `v=0` ou exclusion |
| **IMAGE_REQUIRED** | PNG absent — **ne pas inventer** de position |

### Checklist par landmark (8 axes)

1. Tubérosité ischiatique (pas autre os)
2. Point caudal/inférieur B1 (contour osseux identifiable)
3. R/L (IT_R gauche image, IT_L droite image)
4. IT ≠ TD
5. Pas sur fémur (anti-fémur §3.6 B4)
6. Pas d'extrapolation hors FOV
7. Qualité / visibilité (`VISIBLE` / `PARTIAL` / `v`)
8. Cohérence guide B4

**Référence :** `bi_ischial_annotation_guidelines.md` · `b6_working_annotations/B26_XX.json`

---

## Synthèse queue

| Action recommandée | N | % |
|--------------------|--:|--:|
| **MOVE** | 8 | 15,4 % |
| **REVIEW** | 34 | 65,4 % |
| **IMAGE_REQUIRED** | 10 | 19,2 % |
| **KEEP** | 0 | 0 % |
| **INVALID** | 0 | 0 % |

> **Note :** aucun KEEP pré-assigné — les 7 PASS QA passent en **REVIEW P3** (« confirmer KEEP visuellement »). Le KEEP n'est enregistré qu'après validation humaine.

| Priorité | N | Description |
|----------|--:|-------------|
| **P0** | 16 | MOVE caudal prioritaire (6) + IMAGE_REQUIRED (10) |
| **P1** | 11 | Cas limites (9 REVIEW) + MOVE secondaire (2) : B26_21 R, B26_22 L |
| **P2** | 18 | Offset standard REVIEW |
| **P3** | 7 | QA PASS — confirmer KEEP |

| PNG disponible | N |
|----------------|--:|
| Oui | 42 |
| **Non (IMAGE_REQUIRED)** | **10** |

---

## P0 — Priorité immédiate (16 landmarks)

### MOVE caudal (6) — biais offset confirmé

| Image | Landmark | x | y | QA | Action | Commentaire |
|-------|----------|--:|--:|----|--------|-------------|
| **B26_04** | **IT_R** | 856.0 | 2454.0 | REVIEW | **MOVE** | Scan apex ~+99 px |
| **B26_06** | **IT_L** | 1929.5 | 2043.0 | REVIEW | **MOVE** | ~198 px crânial vs IT_R |
| **B26_08** | **IT_L** | 1746.5 | 2133.1 | REVIEW | **MOVE** | Scan apex ~+74 px |
| **B26_09** | **IT_L** | 2268.3 | 2053.5 | REVIEW | **MOVE** | Scan apex ~+52 px |
| **B26_25** | **IT_R** | 679.1 | 2194.7 | REVIEW | **MOVE** | Scan apex ~+66 px |
| **B26_25** | **IT_L** | 2032.7 | 2105.7 | REVIEW | **MOVE** | Scan apex ~+73 px |

### IMAGE_REQUIRED (10) — PNG absents

| Image | Landmark | x | y | Action | Commentaire |
|-------|----------|--:|--:|--------|-------------|
| B26_10 | IT_R | 830.0 | 2221.9 | **IMAGE_REQUIRED** | Restaurer `images/train/B26_10.png` |
| B26_10 | IT_L | 1970.4 | 2172.7 | **IMAGE_REQUIRED** | Ne pas valider sans visuel |
| B26_13 | IT_R | 904.2 | 2297.6 | **IMAGE_REQUIRED** | Restaurer `images/train/B26_13.png` |
| B26_13 | IT_L | 2168.3 | 2291.9 | **IMAGE_REQUIRED** | Ne pas valider sans visuel |
| B26_17 | IT_R | 562.3 | 2137.4 | **IMAGE_REQUIRED** | Restaurer `images/train/B26_17.png` |
| B26_17 | IT_L | 1869.5 | 2083.3 | **IMAGE_REQUIRED** | Ne pas valider sans visuel |
| B26_20 | IT_R | 667.2 | 2245.2 | **IMAGE_REQUIRED** | Restaurer `images/train/B26_20.png` |
| B26_20 | IT_L | 1900.6 | 2135.1 | **IMAGE_REQUIRED** | Ne pas valider sans visuel |
| B26_26 | IT_R | 538.3 | 2030.0 | **IMAGE_REQUIRED** | Restaurer `images/train/B26_26.png` |
| B26_26 | IT_L | 2002.9 | 1932.9 | **IMAGE_REQUIRED** | Ne pas valider sans visuel |

---

## P1 — Cas limites (11 landmarks)

| Image | Landmark | x | y | QA | Action | Motif |
|-------|----------|--:|--:|----|--------|-------|
| B26_04 | IT_L | 2193.1 | 2256.9 | REVIEW | REVIEW | Asymétrie vs IT_R P0 |
| B26_05 | IT_R | 648.0 | 2955.0 | REVIEW | REVIEW | PARTIAL FOV ; micro-revue → KEEP à confirmer |
| B26_05 | IT_L | 2395.0 | 2958.0 | REVIEW | REVIEW | PARTIAL FOV ; micro-revue → KEEP à confirmer |
| B26_06 | IT_R | 716.0 | 2241.0 | REVIEW | REVIEW | Référence asymétrie avant correction IT_L |
| B26_07 | IT_R | 708.0 | 2548.0 | REVIEW | REVIEW | A-GAS07 ; MANUAL_REVIEW |
| B26_11 | IT_R | 632.0 | 2498.0 | REVIEW | REVIEW | A-ROT11 ; contraste faible |
| B26_11 | IT_L | 1958.0 | 2495.0 | REVIEW | REVIEW | A-ROT11 ; MANUAL_REVIEW |
| B26_12 | IT_R | 843.0 | 2148.0 | REVIEW | REVIEW | A-BRD12 ; B7 |
| B26_12 | IT_L | 2041.0 | 2179.0 | REVIEW | REVIEW | A-BRD12 ; B7 |
| B26_21 | IT_R | 841.9 | 2580.5 | REVIEW | MOVE | Scan +38 px ; MOVE si confirmé |
| B26_22 | IT_L | 2028.4 | 2154.0 | REVIEW | MOVE | ~154 px crânial vs IT_R |

---

## P3 — QA PASS à confirmer KEEP (7 landmarks)

| Image | Landmark | x | y | QA | Conf. | Commentaire |
|-------|----------|--:|--:|----|:-----:|-------------|
| B26_01 | IT_R | 548.0 | 2140.0 | PASS | HIGH | Pilote manuel — référence B6 |
| B26_01 | IT_L | 1772.0 | 2178.0 | PASS | HIGH | Post-correction manuelle |
| B26_07 | IT_L | 1778.0 | 2548.0 | PASS | MEDIUM | Post-correction ; gaz périphérique |
| B26_08 | IT_R | 650.7 | 2207.9 | PASS | MEDIUM | Meilleur offset — confirmer KEEP |
| B26_16 | IT_R | 730.4 | 2245.7 | PASS | MEDIUM | Confirmer KEEP |
| B26_24 | IT_R | 698.0 | 2398.0 | PASS | HIGH | Piège fémoral corrigé |
| B26_24 | IT_L | 1858.0 | 2328.0 | PASS | MEDIUM | Asymétrie rétablie |

---

## P2 — Offset standard (18 landmarks)

| Image | IT_R (x, y) | IT_L (x, y) | Action |
|-------|-------------|-------------|--------|
| B26_02 | (544.4, 1804.7) | (1879.0, 1826.0) | REVIEW ×2 |
| B26_03 | (732.2, 2141.2) | (2074.0, 2026.0) | REVIEW ×2 |
| B26_09 | (769.1, 2105.3) | — | REVIEW (IT_R) |
| B26_14 | (743.8, 2201.0) | (2000.5, 2121.1) | REVIEW ×2 |
| B26_15 | (630.0, 2028.6) | (1725.4, 1976.3) | REVIEW ×2 |
| B26_16 | — | (1988.0, 2158.2) | REVIEW (IT_L) |
| B26_18 | (772.2, 1925.2) | (2077.3, 1812.5) | REVIEW ×2 |
| B26_19 | (777.2, 2103.3) | (2028.9, 2029.4) | REVIEW ×2 |
| B26_21 | — | (2016.8, 2487.8) | REVIEW (IT_L) |
| B26_22 | (828.0, 2308.0) | — | REVIEW (IT_R) |
| B26_23 | (903.5, 2076.6) | (2184.3, 1991.6) | REVIEW ×2 |

---

## Ordre de revue recommandé

```
Phase 1 — P0 MOVE (6)          → B26_04 R, B26_06 L, B26_08 L, B26_09 L, B26_25 R/L
Phase 2 — P0 IMAGE_REQUIRED    → Restaurer PNG B26_10, 13, 17, 20, 26 puis revue
Phase 3 — P1 cas limites (11)  → B26_05, 07, 11, 12 + asymétries + MOVE P1
Phase 4 — P3 confirmer KEEP (7)→ B26_01, 07 L, 08 R, 16 R, 24
Phase 5 — P2 offset restant (18)
```

---

## Tableau complet (52 landmarks)

| # | Image | LM | x | y | QA | Conf. | PNG | Action | P | Commentaire |
|--:|-------|-----|--:|--:|----|:-----:|:---:|--------|---|-------------|
| 1 | B26_01 | IT_R | 548.0 | 2140.0 | PASS | HIGH | ✓ | REVIEW | P3 | Confirmer KEEP |
| 2 | B26_01 | IT_L | 1772.0 | 2178.0 | PASS | HIGH | ✓ | REVIEW | P3 | Confirmer KEEP |
| 3 | B26_02 | IT_R | 544.4 | 1804.7 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 4 | B26_02 | IT_L | 1879.0 | 1826.0 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 5 | B26_03 | IT_R | 732.2 | 2141.2 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 6 | B26_03 | IT_L | 2074.0 | 2026.0 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 7 | B26_04 | IT_R | 856.0 | 2454.0 | REVIEW | MED | ✓ | **MOVE** | **P0** | +99 px crânial |
| 8 | B26_04 | IT_L | 2193.1 | 2256.9 | REVIEW | LOW | ✓ | REVIEW | P1 | Asymétrie |
| 9 | B26_05 | IT_R | 648.0 | 2955.0 | REVIEW | MED | ✓ | REVIEW | P1 | PARTIAL FOV |
| 10 | B26_05 | IT_L | 2395.0 | 2958.0 | REVIEW | MED | ✓ | REVIEW | P1 | PARTIAL FOV |
| 11 | B26_06 | IT_R | 716.0 | 2241.0 | REVIEW | MED | ✓ | REVIEW | P1 | Réf. asymétrie |
| 12 | B26_06 | IT_L | 1929.5 | 2043.0 | REVIEW | MED | ✓ | **MOVE** | **P0** | +198 px crânial |
| 13 | B26_07 | IT_R | 708.0 | 2548.0 | REVIEW | MED | ✓ | REVIEW | P1 | Gaz A-GAS07 |
| 14 | B26_07 | IT_L | 1778.0 | 2548.0 | PASS | MED | ✓ | REVIEW | P3 | Confirmer KEEP |
| 15 | B26_08 | IT_R | 650.7 | 2207.9 | PASS | MED | ✓ | REVIEW | P3 | Confirmer KEEP |
| 16 | B26_08 | IT_L | 1746.5 | 2133.1 | REVIEW | MED | ✓ | **MOVE** | **P0** | +74 px crânial |
| 17 | B26_09 | IT_R | 769.1 | 2105.3 | REVIEW | LOW | ✓ | REVIEW | P2 | FOV serré |
| 18 | B26_09 | IT_L | 2268.3 | 2053.5 | REVIEW | MED | ✓ | **MOVE** | **P0** | +52 px crânial |
| 19 | B26_10 | IT_R | 830.0 | 2221.9 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |
| 20 | B26_10 | IT_L | 1970.4 | 2172.7 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |
| 21 | B26_11 | IT_R | 632.0 | 2498.0 | REVIEW | LOW | ✓ | REVIEW | P1 | Rotation |
| 22 | B26_11 | IT_L | 1958.0 | 2495.0 | REVIEW | LOW | ✓ | REVIEW | P1 | Rotation |
| 23 | B26_12 | IT_R | 843.0 | 2148.0 | REVIEW | LOW | ✓ | REVIEW | P1 | A-BRD12 |
| 24 | B26_12 | IT_L | 2041.0 | 2179.0 | REVIEW | LOW | ✓ | REVIEW | P1 | A-BRD12 |
| 25 | B26_13 | IT_R | 904.2 | 2297.6 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |
| 26 | B26_13 | IT_L | 2168.3 | 2291.9 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |
| 27 | B26_14 | IT_R | 743.8 | 2201.0 | REVIEW | LOW | ✓ | REVIEW | P2 | Contraste faible |
| 28 | B26_14 | IT_L | 2000.5 | 2121.1 | REVIEW | LOW | ✓ | REVIEW | P2 | Contraste faible |
| 29 | B26_15 | IT_R | 630.0 | 2028.6 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 30 | B26_15 | IT_L | 1725.4 | 1976.3 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 31 | B26_16 | IT_R | 730.4 | 2245.7 | PASS | MED | ✓ | REVIEW | P3 | Confirmer KEEP |
| 32 | B26_16 | IT_L | 1988.0 | 2158.2 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 33 | B26_17 | IT_R | 562.3 | 2137.4 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |
| 34 | B26_17 | IT_L | 1869.5 | 2083.3 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |
| 35 | B26_18 | IT_R | 772.2 | 1925.2 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 36 | B26_18 | IT_L | 2077.3 | 1812.5 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 37 | B26_19 | IT_R | 777.2 | 2103.3 | REVIEW | LOW | ✓ | REVIEW | P2 | Contraste faible |
| 38 | B26_19 | IT_L | 2028.9 | 2029.4 | REVIEW | LOW | ✓ | REVIEW | P2 | Contraste faible |
| 39 | B26_20 | IT_R | 667.2 | 2245.2 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |
| 40 | B26_20 | IT_L | 1900.6 | 2135.1 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |
| 41 | B26_21 | IT_R | 841.9 | 2580.5 | REVIEW | MED | ✓ | MOVE | P1 | +38 px crânial |
| 42 | B26_21 | IT_L | 2016.8 | 2487.8 | REVIEW | LOW | ✓ | REVIEW | P2 | Contraste faible |
| 43 | B26_22 | IT_R | 828.0 | 2308.0 | REVIEW | LOW | ✓ | REVIEW | P2 | Asymétrie |
| 44 | B26_22 | IT_L | 2028.4 | 2154.0 | REVIEW | LOW | ✓ | MOVE | P1 | +154 px crânial |
| 45 | B26_23 | IT_R | 903.5 | 2076.6 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 46 | B26_23 | IT_L | 2184.3 | 1991.6 | REVIEW | LOW | ✓ | REVIEW | P2 | Offset |
| 47 | B26_24 | IT_R | 698.0 | 2398.0 | PASS | HIGH | ✓ | REVIEW | P3 | Confirmer KEEP |
| 48 | B26_24 | IT_L | 1858.0 | 2328.0 | PASS | MED | ✓ | REVIEW | P3 | Confirmer KEEP |
| 49 | B26_25 | IT_R | 679.1 | 2194.7 | REVIEW | MED | ✓ | **MOVE** | **P0** | +66 px crânial |
| 50 | B26_25 | IT_L | 2032.7 | 2105.7 | REVIEW | MED | ✓ | **MOVE** | **P0** | +73 px crânial |
| 51 | B26_26 | IT_R | 538.3 | 2030.0 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |
| 52 | B26_26 | IT_L | 2002.9 | 1932.9 | REVIEW | LOW | ✗ | **IMAGE_REQ** | **P0** | PNG absent |

*Export machine : `b6_full_manual_review_queue.csv`*

---

## Conclusion

```
MANUAL_REVIEW_52_REQUIRED
```

Les **52 pré-annotations** (`b6_working_annotations/`) restent des **WORKING ANNOTATIONS** non officielles. Cette queue lance la **revue manuelle complète** sans modifier aucune coordonnée.

**Prochaine étape (hors scope actuel) :** session manuelle landmark par landmark → log `b6_manual_review_log.csv` → mise à jour `b6_working_annotations/` uniquement après validation humaine explicite.

---

## Intégrité projet

| Élément | Modifié ? |
|---------|:---------:|
| Coordonnées working | **Non** |
| Labels officiels | **Non** |
| `data.yaml` | **Non** |
| V2 / V3 | **Non** |
| Entraînement | **Non** |
| Code production | **Non** |

**Fichiers créés uniquement :**

- `b6_full_manual_review_queue.md` (ce document)
- `b6_full_manual_review_queue.csv`

---

*Queue revue manuelle B6 — 52 landmarks — PRE-ANNOTATIONS.*
