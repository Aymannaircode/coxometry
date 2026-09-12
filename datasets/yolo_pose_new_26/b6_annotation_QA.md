# Audit QA read-only — annotations B6 `IT_R` / `IT_L`

**Généré :** 2026-08-28  
**Mode :** audit **READ-ONLY** — **aucune modification** des annotations de travail, labels officiels, YAML, modèles ou code  
**Corpus audité :** `b6_working_annotations/` (26 images × 2 landmarks = **52 landmarks**)  
**Référence guide :** `bi_ischial_annotation_guidelines.md` (B4 READY FOR B6 CONDITIONALLY)  
**Référence géométrique :** labels officiels 14 kp (`annotation_pilot/annotations/new_26/`)

---

## Synthèse exécutive

| Métrique | Valeur |
|----------|-------:|
| **Landmarks examinés** | **52** |
| **PASS** | **1** (1,9 %) |
| **REVIEW** | **51** (98,1 %) |
| **FAIL** | **0** (0 %) |
| **Confiance HIGH** | **1** (1,9 %) |
| **Confiance MEDIUM** | **1** (1,9 %) |
| **Confiance LOW** | **50** (96,2 %) |
| **Revue humaine requise** | **51 / 52** (98,1 %) |

### Conclusion

```
REVIEW_REQUIRED
```

**Les annotations B6 working ne sont pas prêtes pour promotion vers labels officiels** sans revue humaine systématique et validation clinique B1.

**Motif principal :** 48/52 landmarks (92,3 %) produits par **offsets B26_01 + scan osseux local** — méthode explicitement **non clinique** (cf. `b6_session_summary.md`).

---

## Méthode d'audit

### Contrôles appliqués (par landmark)

| # | Contrôle | Source B4 |
|---|----------|-----------|
| 1 | Position tubérosité ischiatique (proxy géométrique vs TD/FSD) | §3.1–§3.2 |
| 2 | Côté patient (IT_R gauche image, IT_L droite image) | §7 |
| 3 | Distance / relation IT–TD (latéral + caudal, non coïncident) | §3.5, §8 |
| 4 | Risque fémur (Δx vs `FSD_*` ; seuil fail &lt; 60 px) | §3.6 |
| 5 | Proximité bord FOV (marge caudale %) | §4.4 |
| 6 | Règle caudale (IT.y &gt; TD.y) | §3.2 |
| 7 | IT ≠ TD (distance &gt; 80 px) | §8 |
| 8 | Hors FOV | §4.4 |
| 9 | Cohérence méthode / statut reviewer | Plan B6 |
| 10 | Asymétrie bilatérale Δy R-L | §4.6 (QC) |

### Catégories QA

| Grade | Critère |
|-------|---------|
| **PASS** | Contrôles géométriques OK ; placement manuel pilote validé ; confiance élevée |
| **REVIEW** | Échec méthodologique (offset auto), ambiguïté documentée, proximité fémur/bord, ou revue B7 requise |
| **FAIL** | Violation hard : hors FOV, mauvais côté, IT=TD, non caudal, sur diaphyse (Δx FSD &lt; 60 px) |

### Confiance

| Niveau | Critère |
|--------|---------|
| **HIGH** | PASS + pilote manuel B26_01 `IT_R` |
| **MEDIUM** | REVIEW avec pilote manuel validé (`IT_L` B26_01 — piège fémoral documenté) |
| **LOW** | Offset auto, supervised case B26_05, ou drapeaux FOV/fémur/asymétrie |

---

## Résultats globaux PASS / REVIEW / FAIL

| Grade | N | % |
|-------|--:|--:|
| **PASS** | 1 | 1,9 |
| **REVIEW** | 51 | 98,1 |
| **FAIL** | 0 | 0 |

### Distribution confiance

| Confiance | N | % |
|-----------|--:|--:|
| **HIGH** | 1 | 1,9 |
| **MEDIUM** | 1 | 1,9 |
| **LOW** | 50 | 96,2 |

---

## Détail par image

| Image | IT_R | conf R | IT_L | conf L | Méthode | Reviewer | Revue humaine |
|-------|:----:|:------:|:----:|:------:|---------|----------|:-------------:|
| B26_01 | **PASS** | HIGH | REVIEW | MEDIUM | pilot_manual | standard | IT_L oui |
| B26_02 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_03 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_04 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_05 | REVIEW | LOW | REVIEW | LOW | supervised_review | **supervised_case** | **P0 oui** |
| B26_06 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_07 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | review_recommended | **P1 oui** |
| B26_08 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_09 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_10 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_11 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | review_recommended | **P1 oui** |
| B26_12 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | review_recommended | **P1 oui** |
| B26_13 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_14 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_15 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_16 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_17 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_18 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_19 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_20 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_21 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_22 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_23 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_24 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | **P1 oui** |
| B26_25 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |
| B26_26 | REVIEW | LOW | REVIEW | LOW | offset_scan_local | standard | oui |

*Détail complet : `b6_annotation_QA.csv`*

---

## Liste exacte — images à revoir

**26 / 26 images** nécessitent au minimum une revue humaine contextuelle (méthode offset ou statut reviewer).

### Priorité P0 — obligatoire avant toute promotion

| Image | Motif |
|-------|-------|
| **B26_05** | Seul cas PARTIAL bilatéral ; `supervised_case` ; marge caudale 3,9–4,4 % ; ambiguïté apex FOV ; piège fémoral `IT_R` |

### Priorité P1 — revue B7 + drapeaux géométriques

| Image | Motif |
|-------|-------|
| **B26_07** | Gaz intestinal ; `review_recommended` B7 |
| **B26_11** | Rotation pelvienne ; `IT_R` initialement en échec auto — raffiné offset |
| **B26_12** | Marge caudale réduite ; règle bord FOV |
| **B26_24** | Proximité diaphyse `IT_R` (Δx FSD = 71 px) ; asymétrie Δy R-L = 9,4 % ; marge 4,6 % |

### Priorité P2 — offset auto (revue humaine systématique)

`B26_02`, `B26_03`, `B26_04`, `B26_06`, `B26_08`, `B26_09`, `B26_10`, `B26_13`, `B26_14`, `B26_15`, `B26_16`, `B26_17`, `B26_18`, `B26_19`, `B26_20`, `B26_21`, `B26_22`, `B26_23`, `B26_25`, `B26_26`

### Priorité P3 — pilote manuel partiel

| Image | Motif |
|-------|-------|
| **B26_01** | `IT_L` REVIEW — piège fémoral documenté ; validation clinique recommandée |

---

## Liste exacte — landmarks à corriger

**0 landmark en FAIL** — aucune correction automatique impérative par critères hard.

**51 landmarks en REVIEW** — correction ou validation humaine recommandée avant labels officiels :

### Landmarks prioritaires (drapeaux géométriques ou cliniques)

| Image | Landmark | Grade | Confiance | Motif correction |
|-------|----------|:-----:|:---------:|------------------|
| B26_05 | **IT_R** | REVIEW | LOW | PARTIAL ; bord FOV ; piège fémoral ; apex caudal ambigu |
| B26_05 | **IT_L** | REVIEW | LOW | PARTIAL ; bord FOV ; `v=2` non tranché cliniquement |
| B26_24 | **IT_R** | REVIEW | LOW | Proximité diaphyse (Δx FSD = 71 px) ; marge 4,6 % |
| B26_04 | **IT_R** | REVIEW | LOW | Proximité diaphyse (Δx FSD = 100 px) |
| B26_01 | **IT_L** | REVIEW | MEDIUM | Piège fémoral — valider placement vs candidat rejeté |

### Landmarks offset auto — correction humaine systématique (48 landmarks)

Tous les `IT_R` / `IT_L` des images **B26_02–B26_04**, **B26_06–B26_26** (hors coordonnées pilote/revue figées B26_01/05) :

```
B26_02 IT_R, IT_L | B26_03 IT_R, IT_L | B26_04 IT_R, IT_L
B26_06 IT_R, IT_L | B26_07 IT_R, IT_L | B26_08 IT_R, IT_L
B26_09 IT_R, IT_L | B26_10 IT_R, IT_L | B26_11 IT_R, IT_L
B26_12 IT_R, IT_L | B26_13 IT_R, IT_L | B26_14 IT_R, IT_L
B26_15 IT_R, IT_L | B26_16 IT_R, IT_L | B26_17 IT_R, IT_L
B26_18 IT_R, IT_L | B26_19 IT_R, IT_L | B26_20 IT_R, IT_L
B26_21 IT_R, IT_L | B26_22 IT_R, IT_L | B26_23 IT_R, IT_L
B26_24 IT_L | B26_25 IT_R, IT_L | B26_26 IT_R, IT_L
```

*(B26_24 IT_R listé aussi en P1)*

### Seul landmark sans revue humaine obligatoire

| Image | Landmark | Grade | Confiance |
|-------|----------|:-----:|:---------:|
| **B26_01** | **IT_R** | **PASS** | **HIGH** |

---

## Contrôles transversaux — résultats

| Contrôle | Résultat |
|----------|----------|
| IT_R ≠ TD_R (distance &gt; 80 px) | **52/52 OK** |
| IT_L ≠ TD_L (distance &gt; 80 px) | **52/52 OK** |
| IT_R latéral + caudal vs TD_R | **52/52 OK** |
| IT_L latéral + caudal vs TD_L | **52/52 OK** |
| IT_R côté gauche image | **52/52 OK** |
| IT_L côté droite image | **52/52 OK** |
| Aucun point hors FOV | **52/52 OK** |
| Aucun FAIL diaphyse (Δx FSD &lt; 60 px) | **52/52 OK** |
| Proximité diaphyse (60–100 px) | **2 cas** — B26_04 `IT_R`, B26_24 `IT_R` |
| Marge caudale &lt; 8 % | **10 landmarks** (voir CSV) |
| Méthode offset non clinique | **48 landmarks** |

---

## Limites de l'audit

1. **Audit géométrique + métadonnées** — pas de relecture visuelle pixel-par-pixel des 26 radiographies dans cet audit automatisé.
2. **Les offsets B26_01** peuvent produire des points **anatomiquement plausibles** mais **non validés** — d'où le classement REVIEW/LOW systématique.
3. **Validation clinique B1** toujours **REQUIRED** — définition PROPOSED.
4. **Coordonnées pilote** `B6_pilot_B26_01_coords.json` et `B6_review_B26_05_coords.json` restent des références historiques distinctes.

---

## Recommandations

| # | Action |
|---|--------|
| 1 | **Ne pas promouvoir** vers labels YOLO officiels — statut **REVIEW_REQUIRED** |
| 2 | Revue humaine **P0** sur **B26_05** (session supervisée) |
| 3 | Revue **P1** sur B26_07, B26_11, B26_12, B26_24 |
| 4 | Re-annotation manuelle ou semi-manuelle des **48 landmarks offset** |
| 5 | Conserver **B26_01 IT_R** comme référence PASS ; revalider **B26_01 IT_L** |
| 6 | Après corrections : relancer audit QA avant toute ouverture B5/B6 formelle |

---

## Intégrité

| Fichier / artefact | Modifié par cet audit ? |
|--------------------|:-----------------------:|
| `b6_working_annotations/*.json` | **Non** |
| Labels officiels 14 kp | **Non** |
| `data.yaml` | **Non** |
| Modèles V2 / V3 | **Non** |
| Training | **Non** |

**Fichiers créés :**

- `b6_annotation_QA.md` (ce rapport)
- `b6_annotation_QA.csv` (52 lignes)

---

*Audit QA B6 — 52 landmarks examinés — conclusion : **REVIEW_REQUIRED**.*
