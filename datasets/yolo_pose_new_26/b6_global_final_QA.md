# B6 — Synthèse QA globale finale (READ-ONLY)

**Généré :** 2026-08-29  
**Mode :** synthèse indépendante — aucune annotation modifiée  
**Corpus :** B26_01 → B26_26 · 52 landmarks IT_R / IT_L  
**Conclusion :** `B6_GLOBAL_QA_REVIEW`

---

## 1. Périmètre et traçabilité

| Phase | Fichier source | Landmarks couverts |
|-------|----------------|-------------------:|
| P0 | `b6_P0_QA.csv` | 6 |
| IMAGE_REQUIRED | `b6_image_required_QA.csv` | 10 |
| P1 | `b6_P1_QA.csv` | 11 |
| P2 | `b6_P2_QA.csv` | 18 |
| P3 | `b6_P3_manual_review.csv` | 7 |
| Revue finale | `b6_B26_26_ITR_final_review.csv` | 1 (B26_26 IT_R) |

**Règle de fusion :** dernière phase chronologique gagne (P0 < IMAGE_REQUIRED < P1 < P2 < P3).  
**Interdictions respectées :** pas de promotion automatique REVIEW→PASS ; pas de v=0 imposé ; coordonnées lues depuis `b6_working_annotations/` uniquement.

## 2. Synthèse globale

| Métrique | Valeur |
|----------|-------:|
| Landmarks tracés | **52 / 52** |
| PASS final | **31** |
| REVIEW final | **20** |
| UNRESOLVABLE_REVIEW | **1** |
| FAIL final | **0** |
| Candidats v=0 | **10** |
| Validation clinique requise | **21** |
| Duplications | **0** |
| Annotations manquantes | **0** |
| Violations anatomiques structurelles (FAIL) | **0** |

### Confiance globale

| Niveau | N |
|--------|--:|
| HIGH | 1 |
| MEDIUM | 43 |
| LOW | 8 |
| (vide) | 0 |

## 3. Contrôles anatomiques (10 axes)

| # | Contrôle | Résultat synthèse |
|:-:|----------|-------------------|
| 1 | IT sur tubérosité ischiatique | 52/52 structurellement OK (0 FAIL structure) |
| 2 | R/L correct | 52/52 PASS sur toutes phases |
| 3 | IT ≠ TD | 52/52 PASS |
| 4 | Pas de fémur | 52/52 anti-fémur PASS |
| 5 | Pas d'extrapolation FOV | 49 PASS · 3 REVIEW FOV (B26_05 bilat., B26_09 IT_R, B26_19 IT_R) |
| 6 | Définition B1/B4 (apex caudal) | 31 PASS · 21 REVIEW réserves B1/B4 ou contraste |
| 7 | Visibilité | v=2 conservé partout ; candidats v=0 listés séparément |
| 8 | Cohérence corrections | Historique `correction_history` préservé ; P2 MOVE validés |
| 9 | Historique corrections | 35/52 landmarks avec ≥1 correction documentée |
| 10 | Cas non résolubles conservés | B26_26 IT_R = UNRESOLVABLE_REVIEW explicite |

## 4. Liste complète REVIEW + UNRESOLVABLE (21)

| Image | Landmark | Phase | Conf. | v=0 ? | Motif (abrégé) |
|-------|----------|:-----:|:-----:|:-----:|----------------|
| B26_03 | IT_L | P2 | MEDIUM | no | Validation clinique contraste modéré post-MOVE / MOVE caudal +42 px plausible ;  |
| B26_05 | IT_L | P1 | MEDIUM | YES | Session supervisée ; validation clinique apex caudal PARTIAL G ; v=2 vs v=0 / P1 |
| B26_05 | IT_R | P1 | MEDIUM | YES | Session supervisée obligatoire ; trancher v=2 vs v=0 PARTIAL bilatéral ; seuil m |
| B26_06 | IT_R | P1 | LOW | YES | Apex caudal indéterminable — envisager v=0 ou repositionnement caudal (+87 px sc |
| B26_07 | IT_R | P1 | MEDIUM | no | Validation clinique repère sous gaz intestinal ; confirmer indépendance R/L / Co |
| B26_08 | IT_R | P3 | MEDIUM | no | Non déplacé — apex caudal approximatif ; réserve visuelle sans extrapolation |
| B26_09 | IT_R | P2 | MEDIUM | no | Seuil FOV serré §4.4 / MOVE caudal +33 px — cortex plausible in-FOV ; marge FOV  |
| B26_11 | IT_L | P1 | MEDIUM | no | Validation clinique contraste modéré (bone=32) ; cohérence rotation / Apex cauda |
| B26_11 | IT_R | P1 | LOW | YES | Candidat v=0 — contraste osseux très faible (bone=28) ; apex caudal non fiable / |
| B26_14 | IT_L | P2 | MEDIUM | no | Validation clinique contraste post-MOVE / MOVE caudal +37 px — direction correct |
| B26_14 | IT_R | P2 | LOW | YES | Candidat v=0 — structure ischion D non confirmable / Validation clinique obligat |
| B26_15 | IT_L | P2 | LOW | YES | Candidat v=0 — apex caudal indéterminable / Validation clinique bilatéral B26_15 |
| B26_15 | IT_R | P2 | LOW | YES | Candidat v=0 — bord osseux non net / Validation clinique ; ne pas forcer v=2 / C |
| B26_16 | IT_R | P3 | MEDIUM | no | Non déplacé — référence P2 IT_L ; validation clinique optionnelle |
| B26_18 | IT_L | P2 | MEDIUM | no | Validation clinique IT≠TD distance courte (289 px) / MOVE caudal +36 px — NEW su |
| B26_19 | IT_L | P2 | LOW | YES | Candidat v=0 — vallée soft-tissue (bone≈73) / Validation clinique obligatoire /  |
| B26_19 | IT_R | P2 | MEDIUM | no | Seuil FOV + contraste §4.4 / §4.5 / MOVE soft-tissue → cortex ischion D ; marge  |
| B26_21 | IT_R | P1 | LOW | YES | Apex caudal incertain — scan +149 px non confirmé ; envisager v=0 / Validation c |
| B26_25 | IT_L | P0 | MEDIUM | no | Apex caudal ischion G (+72 px y) sur courbe corticale — placement B1 plausible ; |
| B26_26 | IT_L | IMAGE_REQUIRED | MEDIUM | no | Placement individuel plausible (cortex pelvien G) ; asymétrie y 90 px (3,7 %) vs |
| B26_26 | IT_R | P3 | LOW | YES | Revue finale supervisée : zone ischiatique D localisable (médial FSD Δx=205 px)  |

## 5. Candidats potentiellement v=0 (10)

*Aucune conversion v=0 appliquée — liste indicative pour validation clinique.*

| Image | Landmark | Statut final | Conf. | Justification |
|-------|----------|:------------:|:-----:|---------------|
| B26_05 | IT_L | REVIEW | MEDIUM | Session supervisée ; validation clinique apex caudal PARTIAL G ; v=2 vs v=0 / P1 MOVE effectif : sof |
| B26_05 | IT_R | REVIEW | MEDIUM | Session supervisée obligatoire ; trancher v=2 vs v=0 PARTIAL bilatéral ; seuil marge FOV §4.4 / PART |
| B26_06 | IT_R | REVIEW | LOW | Apex caudal indéterminable — envisager v=0 ou repositionnement caudal (+87 px scan) / Validation cli |
| B26_11 | IT_R | REVIEW | LOW | Candidat v=0 — contraste osseux très faible (bone=28) ; apex caudal non fiable / Validation clinique |
| B26_14 | IT_R | REVIEW | LOW | Candidat v=0 — structure ischion D non confirmable / Validation clinique obligatoire ; bone≈44 VERY_ |
| B26_15 | IT_L | REVIEW | LOW | Candidat v=0 — apex caudal indéterminable / Validation clinique bilatéral B26_15 / Conservé REVIEW P |
| B26_15 | IT_R | REVIEW | LOW | Candidat v=0 — bord osseux non net / Validation clinique ; ne pas forcer v=2 / Conservé REVIEW P2 —  |
| B26_19 | IT_L | REVIEW | LOW | Candidat v=0 — vallée soft-tissue (bone≈73) / Validation clinique obligatoire / Conservé REVIEW P2 — |
| B26_21 | IT_R | REVIEW | LOW | Apex caudal incertain — scan +149 px non confirmé ; envisager v=0 / Validation clinique B1 ; asymétr |
| B26_26 | IT_R | UNRESOLVABLE_REVIEW | LOW | Revue finale supervisée : zone ischiatique D localisable (médial FSD Δx=205 px) mais apex caudal = g |

## 6. Validation clinique requise (21)

| Image | Landmark | Statut | Conf. | Raison |
|-------|----------|:------:|:-----:|--------|
| B26_03 | IT_L | REVIEW | MEDIUM | REVIEW / réserve |
| B26_05 | IT_L | REVIEW | MEDIUM | v=0 candidat |
| B26_05 | IT_R | REVIEW | MEDIUM | v=0 candidat |
| B26_06 | IT_R | REVIEW | LOW | v=0 candidat |
| B26_07 | IT_R | REVIEW | MEDIUM | REVIEW / réserve |
| B26_08 | IT_R | REVIEW | MEDIUM | REVIEW / réserve |
| B26_09 | IT_R | REVIEW | MEDIUM | REVIEW / réserve |
| B26_11 | IT_L | REVIEW | MEDIUM | REVIEW / réserve |
| B26_11 | IT_R | REVIEW | LOW | v=0 candidat |
| B26_14 | IT_L | REVIEW | MEDIUM | REVIEW / réserve |
| B26_14 | IT_R | REVIEW | LOW | v=0 candidat |
| B26_15 | IT_L | REVIEW | LOW | v=0 candidat |
| B26_15 | IT_R | REVIEW | LOW | v=0 candidat |
| B26_16 | IT_R | REVIEW | MEDIUM | REVIEW / réserve |
| B26_18 | IT_L | REVIEW | MEDIUM | REVIEW / réserve |
| B26_19 | IT_L | REVIEW | LOW | v=0 candidat |
| B26_19 | IT_R | REVIEW | MEDIUM | REVIEW / réserve |
| B26_21 | IT_R | REVIEW | LOW | v=0 candidat |
| B26_25 | IT_L | REVIEW | MEDIUM | REVIEW / réserve |
| B26_26 | IT_L | REVIEW | MEDIUM | REVIEW / réserve |
| B26_26 | IT_R | UNRESOLVABLE_REVIEW | LOW | v=0 candidat |

## 7. Cas connus vérifiés contre sources

| Image | LM | Statut attendu | Source | Aligné ? |
|-------|----|--------------:|--------|:--------:|
| B26_26 | IT_R | UNRESOLVABLE_REVIEW | `b6_B26_26_ITR_final_review.csv — apex caudal indéterminé` | ✓ |
| B26_25 | IT_L | REVIEW | `b6_P0_QA.csv — VERY_LOW_CONTRAST bone=26` | ✓ |
| B26_05 | IT_R | REVIEW | `b6_P1_QA.csv — PARTIAL FOV A-FOV05` | ✓ |
| B26_05 | IT_L | REVIEW | `b6_P1_QA.csv — PARTIAL FOV + MOVE P1` | ✓ |
| B26_06 | IT_R | REVIEW | `b6_P1_QA.csv — candidat v=0 LOW` | ✓ |
| B26_07 | IT_R | REVIEW | `b6_P1_QA.csv — A-GAS07` | ✓ |
| B26_11 | IT_R | REVIEW | `b6_P1_QA.csv — A-ROT11 LOW contrast` | ✓ |
| B26_11 | IT_L | REVIEW | `b6_P1_QA.csv — rotation + contraste` | ✓ |
| B26_21 | IT_R | REVIEW | `b6_P1_QA.csv — REVIEW LOW` | ✓ |
| B26_14 | IT_R | REVIEW | `b6_P2_QA.csv — candidat v=0 LOW` | ✓ |
| B26_15 | IT_R | REVIEW | `b6_P2_QA.csv — candidat v=0 LOW` | ✓ |
| B26_15 | IT_L | REVIEW | `b6_P2_QA.csv — candidat v=0 LOW` | ✓ |
| B26_19 | IT_L | REVIEW | `b6_P2_QA.csv — candidat v=0 LOW` | ✓ |
| B26_08 | IT_R | REVIEW | `b6_P3_manual_review.csv — KEEP→REVIEW P3` | ✓ |
| B26_16 | IT_R | REVIEW | `b6_P3_manual_review.csv — KEEP→REVIEW P3` | ✓ |

## 8. Matrice complète 52/52

| Image | LM | x | y | Phase | Verdict | Conf. | Statut final | Clinique | v=0 |
|-------|----|--:|--:|:-----:|:-------:|:-----:|:------------:|:--------:|:---:|
| B26_01 | IT_R | 548.0 | 2140.0 | P3 | PASS | HIGH | **PASS** | NO | NO |
| B26_01 | IT_L | 1772.0 | 2178.0 | P3 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_02 | IT_R | 552.0 | 1838.0 | P2 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_02 | IT_L | 1879.0 | 1826.0 | P2 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_03 | IT_R | 718.0 | 2188.0 | P2 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_03 | IT_L | 2068.0 | 2068.0 | P2 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_04 | IT_R | 738.0 | 2338.0 | P0 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_04 | IT_L | 2193.1 | 2256.9 | P1 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_05 | IT_R | 648.0 | 2955.0 | P1 | REVIEW | MEDIUM | **REVIEW** | YES | YES |
| B26_05 | IT_L | 2412.0 | 2960.0 | P1 | REVIEW | MEDIUM | **REVIEW** | YES | YES |
| B26_06 | IT_R | 716.0 | 2241.0 | P1 | REVIEW | LOW | **REVIEW** | YES | YES |
| B26_06 | IT_L | 1882.0 | 2228.0 | P0 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_07 | IT_R | 708.0 | 2548.0 | P1 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_07 | IT_L | 1778.0 | 2548.0 | P3 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_08 | IT_R | 650.7 | 2207.9 | P3 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_08 | IT_L | 1718.0 | 2192.0 | P0 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_09 | IT_R | 778.0 | 2138.0 | P2 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_09 | IT_L | 2255.0 | 2092.0 | P0 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_10 | IT_R | 822.0 | 2258.0 | IMAGE_REQUIRED | PASS | MEDIUM | **PASS** | NO | NO |
| B26_10 | IT_L | 1975.0 | 2210.0 | IMAGE_REQUIRED | PASS | MEDIUM | **PASS** | NO | NO |
| B26_11 | IT_R | 632.0 | 2498.0 | P1 | REVIEW | LOW | **REVIEW** | YES | YES |
| B26_11 | IT_L | 1958.0 | 2495.0 | P1 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_12 | IT_R | 846.0 | 2198.0 | P1 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_12 | IT_L | 2038.0 | 2210.0 | P1 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_13 | IT_R | 892.0 | 2342.0 | IMAGE_REQUIRED | PASS | MEDIUM | **PASS** | NO | NO |
| B26_13 | IT_L | 2168.3 | 2291.9 | IMAGE_REQUIRED | PASS | MEDIUM | **PASS** | NO | NO |
| B26_14 | IT_R | 743.8 | 2201.0 | P2 | REVIEW | LOW | **REVIEW** | YES | YES |
| B26_14 | IT_L | 1994.0 | 2158.0 | P2 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_15 | IT_R | 630.0 | 2028.6 | P2 | REVIEW | LOW | **REVIEW** | YES | YES |
| B26_15 | IT_L | 1725.4 | 1976.3 | P2 | REVIEW | LOW | **REVIEW** | YES | YES |
| B26_16 | IT_R | 730.4 | 2245.7 | P3 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_16 | IT_L | 1978.0 | 2198.0 | P2 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_17 | IT_R | 518.0 | 2190.0 | IMAGE_REQUIRED | PASS | MEDIUM | **PASS** | NO | NO |
| B26_17 | IT_L | 1820.0 | 2155.0 | IMAGE_REQUIRED | PASS | MEDIUM | **PASS** | NO | NO |
| B26_18 | IT_R | 772.2 | 1925.2 | P2 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_18 | IT_L | 2072.0 | 1848.0 | P2 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_19 | IT_R | 768.0 | 2138.0 | P2 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_19 | IT_L | 2028.9 | 2029.4 | P2 | REVIEW | LOW | **REVIEW** | YES | YES |
| B26_20 | IT_R | 688.0 | 2208.0 | IMAGE_REQUIRED | PASS | MEDIUM | **PASS** | NO | NO |
| B26_20 | IT_L | 1888.0 | 2188.0 | IMAGE_REQUIRED | PASS | MEDIUM | **PASS** | NO | NO |
| B26_21 | IT_R | 841.9 | 2580.5 | P1 | REVIEW | LOW | **REVIEW** | YES | YES |
| B26_21 | IT_L | 2012.0 | 2518.0 | P2 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_22 | IT_R | 828.0 | 2308.0 | P2 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_22 | IT_L | 2024.0 | 2238.0 | P1 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_23 | IT_R | 892.0 | 2108.0 | P2 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_23 | IT_L | 2178.0 | 2018.0 | P2 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_24 | IT_R | 698.0 | 2398.0 | P3 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_24 | IT_L | 1858.0 | 2328.0 | P3 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_25 | IT_R | 665.0 | 2245.0 | P0 | PASS | MEDIUM | **PASS** | NO | NO |
| B26_25 | IT_L | 1998.0 | 2178.0 | P0 | REVIEW | MEDIUM | **REVIEW** | YES | NO |
| B26_26 | IT_R | 552.0 | 2088.0 | P3 | REVIEW | LOW | **UNRESOLVABLE_REVIEW** | YES | YES |
| B26_26 | IT_L | 1998.0 | 1998.0 | IMAGE_REQUIRED | REVIEW | MEDIUM | **REVIEW** | YES | NO |

## 9. Conclusion

**`B6_GLOBAL_QA_REVIEW`** — Les 52 landmarks sont tracés sans duplication ni annotation manquante. 31 landmarks PASS, 20 REVIEW et 1 UNRESOLVABLE_REVIEW. Aucune violation anatomique structurelle (FAIL). Session de validation clinique ciblée requise avant promotion vers labels officiels.

---

*Fichiers produits : `b6_global_final_QA.csv`, `b6_global_final_QA.md` — READ-ONLY, annotations non modifiées.*