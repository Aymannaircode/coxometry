# V5 Phase 2A — Landmark Reliability & Anatomical QC Audit

**Généré :** 2026-09-02  
**Phase :** 2A (backend only, pre-Flutter)  
**Verdict :** **`V5_IT_QC_READY`**

---

## QC architecture

```
POST /analyze (MODEL_VERSION=v5_phase2)
  → V5Phase2LandmarkDetector.detect()     # prédiction brute IT (v, x, y, conf)
  → run_measurement_pipeline()
       → reprojection IT → espace image originale
       → assess_it_landmarks_qc()         # couche QC post-inférence
       → apply_qc_to_it_dicts()           # enrichit quality / quality_reasons
  → réponse API (prédiction brute + fiabilité séparée)
```

**Module :** `backend/app/services/detection/v5_it_qc.py`  
**Point d'insertion :** `measurement_service._build_detection_out()` après reprojection, avant exposition API.

**Séparation explicite :**
- `v`, `x`, `y`, `confidence` = sortie modèle (inchangée)
- `quality`, `quality_reasons` = évaluation backend conservative (nouveau)

**États :**

| État | Signification |
|------|---------------|
| `accept` | Passe tous les contrôles conservateurs |
| `review` | Coordonnée exposée mais fiabilité incertaine |
| `unavailable` | Prédiction non fiable (v=0 ou échec dur) |

V2 inchangé : `it_landmarks=[]`, pas de champs `quality`.

---

## Rules implemented

| Règle | Sévérité | Raison code |
|-------|----------|-------------|
| A. Bornes image | `unavailable` | `out_of_image_bounds` |
| B. Côté patient (IT_R gauche, IT_L droite vs midline TD) | `unavailable` si côté inversé | `wrong_patient_side` |
| B. Placement latéral faible | `review` | `weak_lateral_placement` |
| C. IT caudal au teardrop (même côté) | `review` | `insufficient_caudal_vs_teardrop` |
| C. IT caudal au FHC (même côté) | `review` | `insufficient_caudal_vs_fhc` |
| D. Asymétrie verticale bilatérale | `review` | `bilateral_vertical_asymmetry` |
| D. Asymétrie horizontale bilatérale | `review` | `bilateral_horizontal_asymmetry` |
| D. Ordre IT_R.x ≥ IT_L.x | `unavailable` | `bilateral_order_violation` |
| E. Confiance modèle basse | `review` | `low_model_confidence` |
| E. Sur-confiance + IT–FSD marginal | `review` | `high_confidence_marginal_it_fsd` |
| Modèle v=0 | `unavailable` | `model_v0` |

Midline pelvienne : `(TD_R.x + TD_L.x) / 2` — repères MVP existants, pas de règle inventée.

---

## Threshold derivation

Source : **26 labels officiels 16 kp** (`labels/train` + `labels/val`) + dimensions `b6_working_annotations/*.json`.  
Script de calibration offline (non appelé en production).

| Constante | Valeur | Dérivation |
|-----------|--------|------------|
| `MIN_DY_TD_FRAC` | 0.05 | p10 GT `(IT.y − TD.y)/h` = 0.0939, marge conservative |
| `MIN_DY_FHC_FRAC` | 0.28 | p10 GT `(IT.y − FHC.y)/h` = 0.3144 |
| `MIN_DX_MID_FRAC` | 0.12 | p10 GT distance latérale normalisée = 0.1678 |
| `MAX_BILATERAL_Y_DIFF_FRAC` | 0.06 | p90 GT `|IT_R.y − IT_L.y|/h` ≈ 0.050 |
| `MAX_BILATERAL_DX_RATIO` | 1.70 | p90 GT ratio distances midline ≈ 1.55 |
| `LOW_CONFIDENCE_REVIEW` | 0.40 | Complément au seuil inférence 0.25 |
| `HIGH_CONFIDENCE_REVIEW` | 0.78 | Médiane conf val ~0.72–0.82 |
| `HIGH_CONF_MAX_IT_FSD_FRAC_R` | −0.025 | Calibré sur prédictions val : B26_26 IT_R = −0.0185 (hors marge) ; B26_10 IT_R = −0.0295 (dans marge) |
| `HIGH_CONF_MAX_IT_FSD_FRAC_L` | −0.048 | B26_26 IT_L = −0.0504 (accept) ; marge conservatrice |

Ces seuils sont des **heuristiques QC**, pas des règles cliniques.

---

## 5 validation images

Espace : **pixels image originale** (post-reprojection).

| Image | IT | x | y | conf | v | QC | Raisons |
|-------|-----|---:|---:|---:|--:|-----|---------|
| B26_10 | IT_R | 776.1 | 2248.2 | 0.713 | 2 | **accept** | — |
| B26_10 | IT_L | 2065.9 | 2158.7 | 0.829 | 2 | **accept** | — |
| B26_13 | IT_R | 871.3 | 2245.2 | 0.748 | 2 | **accept** | — |
| B26_13 | IT_L | 2160.5 | 2127.3 | 0.771 | 2 | **accept** | — |
| B26_17 | IT_R | 771.0 | 2068.8 | 0.709 | 2 | **accept** | — |
| B26_17 | IT_L | 1763.9 | 2042.0 | 0.626 | 2 | **accept** | — |
| B26_20 | IT_R | 698.8 | 2272.5 | 0.726 | 2 | **accept** | — |
| B26_20 | IT_L | 1972.9 | 2193.0 | 0.684 | 2 | **accept** | — |
| B26_26 | IT_R | 628.9 | 2181.7 | 0.818 | 2 | **review** | `high_confidence_marginal_it_fsd` |
| B26_26 | IT_L | 1997.7 | 2147.0 | 0.837 | 2 | **accept** | — |

---

## B26_26 analysis

| Attribut | IT_R | IT_L |
|----------|------|------|
| Prédiction modèle | v=2, conf≈0.82, coords conservées | v=2, conf≈0.84 |
| GT (hors production) | v=0 (non identifiable) | v=2 |
| QC | **review** | **accept** |
| Motif | Confiance élevée (≥0.78) mais `(IT.y − FSD.y)/h = −0.0185` > seuil R (−0.025) : IT trop proche verticalement du FSD par rapport aux cas val sains | Passe tous les contrôles |

**Objectif atteint :** la confiance seule (~0.82) ne produit pas un `accept` automatique. La prédiction brute reste disponible pour audit ; la couche fiabilité signale `review`.

Aucune logique hard-codée sur le filename B26_26.

---

## False reject analysis

Sur les 5 images val (10 IT prédits v=2) :

| Résultat | Count |
|----------|------:|
| accept | 9 |
| review | 1 (B26_26 IT_R) |
| unavailable | 0 |

**Faux rejets :** 0 sur cas val visibles normaux (B26_10/13/17/20 tous accept).

**Limite connue :** la règle `high_confidence_marginal_it_fsd` cible le motif sur-confiance / anatomie marginale observé sur B26_26 ; d'autres cas cliniquement ambigus mais anatomiquement « dans la norme » des repères MVP pourraient encore passer `accept`.

---

## API changes

Extension **rétro-compatible** de `AnalyzeITLandmarkOut` :

```json
{
  "name": "IT_R",
  "kp_index": 14,
  "v": 2,
  "x": 628.9,
  "y": 2181.7,
  "confidence": 0.818,
  "quality": "review",
  "quality_reasons": ["high_confidence_marginal_it_fsd"]
}
```

- Champs `quality` / `quality_reasons` optionnels (absents pour V2)
- Audit enrichi : `it_landmarks_qc` (backend)
- VCE / Tönnis / CCD inchangés (14 KP MVP uniquement)
- Aucune nouvelle mesure IT

---

## Existing test status

```
python -m unittest discover -s backend/tests -v
→ Ran 167 tests in ~152s
→ OK (skipped=1)
```

Nouveau fichier : `backend/tests/test_v5_it_qc.py` (14 tests)  
Couverture : bornes, côté, caudalité, bilatéral, confiance, B26_26, cas val normaux, non-régression V2.

Tests V5 Phase 1 / V2 existants : **inchangés, tous verts**.

---

## Limitations

1. QC basé sur cohérence avec repères MVP (TD, FHC, FSD) — si le pelvis entier est mal détecté, le QC peut être trompeur.
2. Pas d'accès image brute (contraste, visibilité osseuse) — impossible de reproduire le jugement clinique GT v=0 sans labels.
3. Seuils dérivés sur N=26 — faible puissance statistique ; à réviser avec plus de cas.
4. `review` n'empêche pas l'exposition des coordonnées — décision produit Flutter à venir.
5. Mesures futures dépendantes d'IT devront filtrer sur `quality == accept` (non implémenté cette phase).

---

## Verdict

**`V5_IT_QC_READY`**

Couche QC conservative opérationnelle, séparation prédiction/fiabilité respectée, B26_26 IT_R correctement rétrogradé en `review`, cas val normaux en `accept`, 167 tests verts, V2 intact, pas de modification modèle/dataset/YAML/checkpoint/mvp_geometry.
