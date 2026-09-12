# B6 — Résumé corrections manuelles (9 landmarks)

**Session :** 2026-08-28  
**Statut :** `MANUAL_CORRECTION_COMPLETED / QA_REQUIRED`  
**Reviewer :** `agent_B6_manual_correction`  
**Source queue :** `b6_manual_correction_queue.md`

---

## Synthèse

| Métrique | Valeur |
|----------|--------|
| **Landmarks traités** | **9 / 9** |
| **Images modifiées** | 5 (`B26_01`, `B26_05`, `B26_07`, `B26_11`, `B26_24`) |
| **Fichiers JSON mis à jour** | 5 (`b6_working_annotations/B26_XX.json`) |
| **Labels officiels modifiés** | **Non** |
| **Passage 14 → 16 kp** | **Non** (interdit) |

**Méthode :** revue visuelle sur radiographies originales + grilles de coordonnées locales — **sans offset B26_01**, **sans extrapolation automatique**.

---

## Coordonnées avant / après

| Image | Landmark | Priorité | x_old | y_old | x_new | y_new | v | Visibilité |
|-------|----------|:--------:|------:|------:|------:|------:|:-:|------------|
| B26_24 | IT_R | P0 | 616.0 | 2352.0 | **698.0** | **2398.0** | 2 | VISIBLE |
| B26_24 | IT_L | P1 | 1900.0 | 2120.5 | **1858.0** | **2328.0** | 2 | VISIBLE |
| B26_01 | IT_L | P1 | 1756.0 | 2143.0 | **1772.0** | **2178.0** | 2 | VISIBLE |
| B26_05 | IT_R | P2 | 705.0 | 2892.0 | **648.0** | **2955.0** | 2 | PARTIAL |
| B26_05 | IT_L | P1 | 2472.0 | 2876.0 | **2395.0** | **2958.0** | 2 | PARTIAL |
| B26_07 | IT_R | P2 | 640.4 | 2431.5 | **708.0** | **2548.0** | 2 | VISIBLE |
| B26_07 | IT_L | P1 | 1834.0 | 2379.0 | **1778.0** | **2548.0** | 2 | VISIBLE |
| B26_11 | IT_R | P2 | 566.7 | 2298.6 | **632.0** | **2498.0** | 2 | VISIBLE |
| B26_11 | IT_L | P1 | 2052.2 | 2252.6 | **1958.0** | **2495.0** | 2 | VISIBLE |

**Inchangé (référence PASS) :** `B26_01 IT_R` (548.0, 2140.0)

*(Journal détaillé : `b6_manual_corrections_log.csv`)*

---

## Corrections effectuées par cas

### B26_24 — P0 + P1

| Landmark | Correction |
|----------|------------|
| **IT_R** | Replacé du cortex fémoral (piège fémoral) vers cortex caudal ischiatique droit (+82 px x, +46 px y) |
| **IT_L** | Apex caudal ischion G repositionné (+208 px y) ; cohérence bilatérale rétablie |

### B26_01 — P1

| Landmark | Correction |
|----------|------------|
| **IT_L** | Déplacement caudal ~35 px sur cortex ischiatique ; piège fémoral latéral évité |

### B26_05 — P1 + P2 (supervised_case)

| Landmark | Correction |
|----------|------------|
| **IT_R** | Repositionné sur cortex ischiatique visible (x < limite FOV ~670) ; caudal conservateur PARTIAL |
| **IT_L** | Replacé sur ischion G médial au fémur (Δx −77, Δy +82) |

### B26_07 — P1 + P2 (review_recommended)

| Landmark | Correction |
|----------|------------|
| **IT_R** | Repositionné sur cortex ischiatique D malgré gaz intestinal (+68 px x, +117 px y) |
| **IT_L** | Apex caudal ischion G (+169 px y) |

### B26_11 — P1 + P2 (review_recommended)

| Landmark | Correction |
|----------|------------|
| **IT_R** | Apex caudal ischion D sous rotation pelvienne (+65 px x, +199 px y) |
| **IT_L** | Apex caudal ischion G indépendant (+243 px y) |

---

## Vérifications appliquées (checklist)

| Critère | Résultat session |
|---------|------------------|
| Point sur tubérosité ischiatique (pas fémur) | **OK** — piège fémoral B26_24 IT_R corrigé |
| Point caudal du contour osseux | **OK** — déplacements caudaux systématiques |
| R/L correct | **OK** — IT_R gauche image, IT_L droite image |
| TD ≠ IT | **OK** — coordonnées distinctes des TD officiels |
| Règle bord FOV | **OK avec réserve** — B26_05 PARTIAL bilatéral |
| Labels officiels inchangés | **OK** |

---

## Ambiguïtés restantes

| Code / cas | Landmark | Statut |
|------------|----------|--------|
| **A-FOV05** | B26_05 IT_R, IT_L | PARTIAL bilatéral ; marge caudale ~50 px (1,7 %) ; dispersion apex documentée (~110 px) — **v=2 vs v=0 non tranché cliniquement** |
| **A-FEM05** | B26_05 IT_R | Piège fémoral documenté — repositionné mais **validation clinique requise** |
| **A-GAS07** | B26_07 IT_R | Gaz intestinal persistant — repère repositionné sur os identifiable mais **confiance réduite** |
| **A-ROT11** | B26_11 IT_R, IT_L | Rotation pelvienne — R/L annotés indépendamment ; **validation clinique recommandée** |
| **A-IT01** | B26_01 IT_L | Piège fémoral documenté — corrigé caudalement ; **validation clinique recommandée** |

---

## Points nécessitant encore une validation clinique

| Priorité | Image | Landmark(s) | Motif |
|:--------:|-------|-------------|-------|
| **P0 clinique** | B26_05 | IT_R, IT_L | Cas `supervised_case` PARTIAL — seuil v et apex FOV |
| **P1 clinique** | B26_07 | IT_R | Gaz intestinal — confirmer repère sous opacité |
| **P1 clinique** | B26_11 | IT_R | Rotation + contraste — confirmer apex caudal |
| **P2 clinique** | B26_01 | IT_L | Piège fémoral historique — confirmer placement caudal |
| **P2 clinique** | B26_24 | IT_R, IT_L | Post-correction FAIL — confirmer absence d'erreur résiduelle |
| **Global** | 5 images | 9 landmarks | **QA formelle B6** avant toute promotion |

---

## Fichiers modifiés / créés

### Annotations de travail modifiées

- `b6_working_annotations/B26_01.json` — `IT_L` uniquement
- `b6_working_annotations/B26_05.json` — `IT_R`, `IT_L`
- `b6_working_annotations/B26_07.json` — `IT_R`, `IT_L`
- `b6_working_annotations/B26_11.json` — `IT_R`, `IT_L`
- `b6_working_annotations/B26_24.json` — `IT_R`, `IT_L`

Chaque fichier inclut : `correction_history[]`, `manual_correction_session`, `manual_correction_status`.

### Fichiers créés

- `b6_manual_corrections_log.csv`
- `b6_manual_corrections_summary.md` (ce document)

### Non modifiés

- `labels/train/*.txt` (YOLO officiel)
- `annotation_pilot/annotations/new_26/*.json`
- `data.yaml`
- Modèles V2 / V3
- Backend / Flutter

---

## Statut final

```
MANUAL_CORRECTION_COMPLETED / QA_REQUIRED
```

**Prochaine étape recommandée :** revue QA clinique des 9 landmarks corrigés + 1 référence PASS (`B26_01 IT_R`) avant extension aux 21 cas restants.

**Interdit à ce stade :** passage 14 → 16 kp, création labels officiels, entraînement YOLO.

---

*Session correction manuelle B6 — 2026-08-28.*
