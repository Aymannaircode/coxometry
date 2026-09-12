# B6 — File de correction manuelle (annotations de travail)

**Généré :** 2026-08-28  
**Source :** `b6_visual_review_5cases.csv` (décision B — corrections nécessaires)  
**Statut :** **PLANIFICATION UNIQUEMENT** — aucune annotation modifiée  

**Mode :** préparation correction manuelle — **aucune modification** des labels officiels, `data.yaml`, V2/V3, backend ou Flutter.

---

## Contexte

La revue visuelle des 5 cas pilotes B6 a produit :

| Verdict | N | Action |
|---------|--:|--------|
| PASS | 1 | Aucune — `B26_01 IT_R` conservé tel quel |
| FAIL | 1 | Correction **P0** obligatoire |
| CORRECTABLE | 5 | Correction **P1** |
| UNCERTAIN | 3 | Revue clinique **P2** |

**Total à traiter : 9 landmarks** (hors `B26_01 IT_R` PASS).

---

## Règles de priorité

| Priorité | Verdict source | Signification |
|:--------:|----------------|---------------|
| **P0** | FAIL | Mauvaise structure anatomique — correction immédiate |
| **P1** | CORRECTABLE | Repère proche — déplacement manuel attendu |
| **P2** | UNCERTAIN | Revue clinique humaine avant/après repositionnement |

**Aucune coordonnée automatique n'est proposée.** Chaque correction sera faite visuellement sur l'image, avec validation humaine.

---

## File de correction priorisée

### P0 — FAIL (1)

| Ordre | Image | Landmark | Coordonnées actuelles | Verdict | Raison | Action attendue |
|------:|-------|----------|----------------------:|---------|--------|-----------------|
| 1 | **B26_24** | **IT_R** | (616.0, 2352.0) | FAIL | Point sur cortex fémoral (piège fémoral ; Δx FSD = 71 px) — mauvaise structure ; anomalie QA confirmée | Replacer visuellement sur le contour caudal de la tubérosité ischiatique droite ; vérifier médial au fémur et hors diaphyse ; ne pas extrapoler hors FOV |

**Fichier :** `b6_working_annotations/B26_24.json`

---

### P1 — CORRECTABLE (5)

| Ordre | Image | Landmark | Coordonnées actuelles | Verdict | Raison | Action attendue |
|------:|-------|----------|----------------------:|---------|--------|-----------------|
| 2 | B26_01 | IT_L | (1756.0, 2143.0) | CORRECTABLE | Piège fémoral évité mais ~15–40 px trop crânial vs apex caudal cortical | Déplacer caudalement sur bord cortical inférieur ischion G ; ne pas glisser vers fémur (candidat rejeté x ≈ 2136) |
| 3 | B26_05 | IT_L | (2472.0, 2876.0) | CORRECTABLE | PARTIAL FOV ; ~100 px trop crânial ; proximité fémorale modérée | Ajuster caudalement vers apex cortical dans FOV ; confirmer os pelvien (session supervisée) |
| 4 | B26_07 | IT_L | (1834.0, 2379.0) | CORRECTABLE | Sur ischion G mais ~90 px trop crânial ; repère latéral moins obscurci | Déplacer vers point caudal du contour osseux ischiatique |
| 5 | B26_11 | IT_L | (2052.2, 2252.6) | CORRECTABLE | Rotation ; ~120 px trop crânial vs apex local | Ajuster caudalement ; placement indépendant malgré rotation |
| 6 | B26_24 | IT_L | (1900.0, 2120.5) | CORRECTABLE | Sur ischion G mais ~97 px trop crânial ; asymétrie faussée par IT_R erroné | **Corriger après P0 IT_R** ; ajuster caudalité ; revérifier cohérence bilatérale |

**Fichiers :** `b6_working_annotations/B26_01.json`, `B26_05.json`, `B26_07.json`, `B26_11.json`, `B26_24.json`

---

### P2 — UNCERTAIN (3)

| Ordre | Image | Landmark | Coordonnées actuelles | Verdict | Raison | Action attendue |
|------:|-------|----------|----------------------:|---------|--------|-----------------|
| 7 | B26_05 | IT_R | (705.0, 2892.0) | UNCERTAIN | PARTIAL FOV ; ambiguïté apex caudal vs bord image (~115 px) ; cortex peu net | Revue clinique supervisée : trancher repère dans FOV vs `v=0` ; documenter choix |
| 8 | B26_07 | IT_R | (640.4, 2431.5) | UNCERTAIN | Gaz intestinal masque cortex ischiatique | Revue clinique : confirmer ou repositionner si os identifiable ; sinon documenter limite |
| 9 | B26_11 | IT_R | (566.7, 2298.6) | UNCERTAIN | Rotation ; faible contraste ; structure non confirmable | Revue clinique : valider sous rotation ou documenter UNCERTAIN |

**Fichiers :** `b6_working_annotations/B26_05.json`, `B26_07.json`, `B26_11.json`

---

## Ordre de traitement recommandé

```
1. B26_24 IT_R          (P0 — bloquant)
2. B26_24 IT_L          (P1 — dépend de P0)
3. B26_01 IT_L          (P1)
4. B26_05 IT_L          (P1 — avant P2 IT_R du même cas)
5. B26_05 IT_R          (P2 — session supervisée)
6. B26_07 IT_L → IT_R   (P1 puis P2)
7. B26_11 IT_L → IT_R   (P1 puis P2)
```

**Cas sans action :** `B26_01 IT_R` — PASS, référence pilote conservée.

---

## Tableau complet (export CSV)

| priority | order | image | landmark | x_current | y_current | verdict | reason | expected_action |
|:--------:|------:|-------|----------|----------:|----------:|---------|--------|-----------------|
| P0 | 1 | B26_24 | IT_R | 616.0 | 2352.0 | FAIL | Piège fémoral — point sur diaphyse | Replacer sur tubérosité ischiatique droite |
| P1 | 2 | B26_01 | IT_L | 1756.0 | 2143.0 | CORRECTABLE | Trop crânial ; piège fémoral évité | Déplacer caudal sur cortex ischiatique |
| P1 | 3 | B26_05 | IT_L | 2472.0 | 2876.0 | CORRECTABLE | Trop crânial ; PARTIAL FOV | Ajuster apex caudal dans FOV |
| P1 | 4 | B26_07 | IT_L | 1834.0 | 2379.0 | CORRECTABLE | Trop crânial | Déplacer vers bord caudal ischion |
| P1 | 5 | B26_11 | IT_L | 2052.2 | 2252.6 | CORRECTABLE | Trop crânial ; rotation | Ajuster caudalité côté L |
| P1 | 6 | B26_24 | IT_L | 1900.0 | 2120.5 | CORRECTABLE | Trop crânial ; après fix IT_R | Corriger après P0 ; revérifier symétrie |
| P2 | 7 | B26_05 | IT_R | 705.0 | 2892.0 | UNCERTAIN | Ambiguïté FOV / apex | Revue clinique supervisée |
| P2 | 8 | B26_07 | IT_R | 640.4 | 2431.5 | UNCERTAIN | Gaz intestinal | Revue clinique |
| P2 | 9 | B26_11 | IT_R | 566.7 | 2298.6 | UNCERTAIN | Rotation / contraste | Revue clinique |

*(Fichier machine : `b6_manual_correction_queue.csv`)*

---

## Procédure de validation manuelle

La correction des annotations de travail `IT_R` / `IT_L` doit être effectuée **visuellement**, case par case, avec **validation humaine explicite**. Aucun déplacement automatique ni coordonnée proposée par script.

### 1. Préparation

1. Ouvrir l'image source : `images/train/B26_XX.png`.
2. Charger l'annotation de travail : `b6_working_annotations/B26_XX.json`.
3. Afficher en superposition les coordonnées actuelles (`IT_R` rouge, `IT_L` bleu).
4. Consulter le guide : `bi_ischial_annotation_guidelines.md`.
5. Pour contexte anti-fémur, afficher en lecture seule les `FSD_*` officiels (`labels/train/B26_XX.txt`) — **sans les modifier**.

### 2. Identification anatomique

Pour chaque landmark à corriger :

1. **Localiser** la tubérosité ischiatique homolatérale (masse osseuse caudale latérale du bassin).
2. **Distinguer** du fémur (diaphyse latérale), du teardrop (`TD_*`), et du pubis.
3. **Appliquer** la définition de travail : *point caudal/inférieur identifiable du contour osseux*.
4. **Vérifier R/L** : droite patient = gauche image ; gauche patient = droite image.

### 3. Placement manuel

1. Placer le point sur le **contour cortical osseux** le plus caudal **identifiable dans le FOV**.
2. **Ne pas extrapoler** hors image si la tubérosité est coupée (règle bord FOV).
3. **Rejeter** tout candidat sur diaphyse fémorale (règle anti-fémur).
4. En cas PARTIAL (B26_05) : documenter si `v=2` ou `v=0` selon politique clinique.

### 4. Critères de validation (checklist)

| # | Critère | OK ? |
|---|---------|:----:|
| 1 | Point sur tubérosité ischiatique (pas fémur, pas TD, pas pubis) | ☐ |
| 2 | Point caudal/inférieur du contour osseux visible | ☐ |
| 3 | R/L correct (IT_R gauche image, IT_L droite image) | ☐ |
| 4 | Règle bord FOV respectée (pas d'extrapolation) | ☐ |
| 5 | Cohérence bilatérale raisonnable (Δy documenté si asymétrie) | ☐ |
| 6 | Visibilité B7 cohérente (VISIBLE / PARTIAL / UNCERTAIN) | ☐ |

### 5. Enregistrement (après validation humaine)

**Uniquement après validation visuelle explicite** — étape future, hors scope de ce document :

1. Mettre à jour `b6_working_annotations/B26_XX.json` avec les nouvelles coordonnées.
2. Ajouter une entrée dans `b6_annotation_log.csv` (date, annotateur, motif correction, verdict avant/après).
3. **Ne pas** modifier `labels/train/`, `annotation_pilot/`, ni `data.yaml`.
4. **Ne pas** promouvoir vers labels officiels YOLO.

### 6. Cas particuliers (rappel)

| Cas | Landmark | Attention |
|-----|----------|-----------|
| B26_01 | IT_L | Piège fémoral latéral — ne pas glisser vers x ≈ 2136 |
| B26_05 | IT_R, IT_L | Session supervisée ; PARTIAL bilatéral ; ambiguïté apex FOV |
| B26_07 | IT_R | Gaz intestinal — repère latéral moins obscurci côté L |
| B26_11 | IT_R, IT_L | Rotation pelvienne — R/L annotés indépendamment |
| B26_24 | IT_R | **FAIL fémoral** — corriger en priorité absolue |

### 7. Critère de clôture de la file

La file est considérée **traitée** lorsque :

- Les **9 landmarks** listés ont un verdict post-correction **PASS** ou **CORRECTABLE accepté** par validateur clinique.
- Les **3 UNCERTAIN (P2)** ont une décision documentée (repositionné + PASS, ou conservé + justification `v` / visibilité).
- Aucun **FAIL** résiduel.
- `B26_01 IT_R` reste inchangé (référence PASS).

---

## Intégrité dataset

| Élément | Modifié ? |
|---------|:---------:|
| `b6_working_annotations/*.json` | **Non** (ce document = planification) |
| Labels officiels YOLO / JSON | **Non** |
| `data.yaml` | **Non** |
| V2 / V3 | **Non** |
| Backend / Flutter | **Non** |

**Fichiers créés :**

- `b6_manual_correction_queue.md` (ce document)
- `b6_manual_correction_queue.csv`

---

*File de correction manuelle B6 — planification READ-ONLY.*
