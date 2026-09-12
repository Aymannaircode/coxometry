# B6 — Résumé de session d'annotation (NON-OFFICIAL)

**Date :** 2026-08-28  
**Campagne :** IT_R / IT_L — corpus `new_26` (26 images)  
**Guide :** `bi_ischial_annotation_guidelines.md` (B4 READY FOR B6 CONDITIONALLY)  
**Espace de travail :** `b6_working_annotations/` + `b6_annotation_log.csv`

---

## Statut session

| Métrique | Valeur |
|----------|-------:|
| **Images annotées** | **26 / 26** |
| **Images restantes** | **0** |
| **`IT_R` avec `v=2`** | 26 |
| **`IT_L` avec `v=2`** | 26 |
| **`v=0` (au moins un côté)** | 0 |
| **Statut global** | Campagne initiale **complète** (working copy) |

---

## Répartition `reviewer_status`

| Statut | N | Images |
|--------|--:|--------|
| `standard` | 22 | B26_01, 02–04, 06, 08–10, 13–26 (hors cas ci-dessous) |
| `supervised_case` | 1 | **B26_05** |
| `review_recommended` | 3 | **B26_07**, **B26_11**, **B26_12** |

---

## Ordre d'annotation exécuté

1. B26_01 ✓ (pilote — coords pilote historiques reprises)  
2. B26_05 ✓ (revue — coords revue historiques ; `supervised_case`)  
3. B26_07 ✓  
4. B26_11 ✓  
5. B26_12 ✓  
6. B26_02, 03, 04, 06, 08, 09, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26 ✓

---

## Ambiguïtés documentées

| Code / image | Ambiguïté |
|--------------|-----------|
| **B26_01** | A-IT01 : piège fémoral `IT_L` (candidat fémoral rejeté) |
| **B26_05** | A-FOV05 : apex caudal bord FOV (~110 px dispersion y) ; A-FEM05 : piège fémoral `IT_R` |
| **B26_07** | A-GAS07 : gaz intestinal central — repères latéraux vérifiés |
| **B26_11** | A-ROT11 : rotation pelvienne légère — R/L annotés indépendamment |
| **B26_12** | A-BRD12 : marge caudale réduite — règle bord FOV |

---

## Cas nécessitant revue clinique

| Image | Motif | Priorité |
|-------|-------|:--------:|
| **B26_05** | PARTIAL bilatéral ; `v=2` vs `v=0` non tranché ; session supervisée | **P0** |
| **B26_07** | Gaz intestinal — confirmer repère caudal fiable | P1 |
| **B26_11** | Rotation pelvienne — cohérence R/L | P1 |
| **B26_12** | Marge caudale réduite — seuil bord FOV | P1 |
| **Corpus complet** | Validation clinique B1 / définition PROPOSED | P0 |

---

## Erreurs potentielles / limites

| Risque | Détail | Mitigation |
|--------|--------|------------|
| **Placement assisté** | Images 02–26 (hors 01/05) : raffinage par offsets B26_01 + scan local osseux | Revue clinique + illustrations recommandées |
| **Piège fémoral** | Contrôle anti-fémur appliqué (§3.6 B4) ; 4 cas initialement en échec auto corrigés | Revoir B26_10, 14, 25 (raffinés par fallback) |
| **Bord FOV** | Points proches du bord inférieur sur FOV serré (ex. B26_21 y≈2580) | Vérifier marges caudales en revue |
| **Symétrie y artificielle** | Certaines paires R/L proches en y après scan — acceptable si contour indépendant | Pas de miroir imposé (conforme B4) |
| **Intégration** | Aucune conversion YOLO — working copy uniquement | Attendre B5/B6 formels |

---

## Intégrité — fichiers non modifiés

| Artefact | Modifié ? |
|----------|:---------:|
| `labels/train/*.txt`, `labels/val/*.txt` | **Non** |
| `annotation_pilot/annotations/new_26/*.json` (14 kp) | **Non** |
| `data.yaml` | **Non** |
| Modèles V2 / V3 | **Non** |
| Backend / Flutter | **Non** |
| Training | **Non lancé** |

---

## Fichiers créés (NON-OFFICIAL)

```
datasets/yolo_pose_new_26/
├── b6_annotation_log.csv
├── b6_session_summary.md
└── b6_working_annotations/
    ├── README.md
    └── B26_01.json … B26_26.json
```

**Références pilote inchangées (historiques) :**

- `B6_pilot_B26_01_coords.json`
- `B6_review_B26_05_coords.json`

---

*Session B6 initiale — annotations de travail PROPOSED / CLINICAL VALIDATION REQUIRED.*
