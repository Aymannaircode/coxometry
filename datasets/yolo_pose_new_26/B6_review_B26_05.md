# Revue B6 read-only — `IT_R` / `IT_L` sur **B26_05**

**Généré :** 2026-08-28  
**Mode :** revue **READ-ONLY** — **aucune modification** des labels YOLO, JSON officiels, `data.yaml`, modèles V2/V3, backend ou Flutter  

**Coordonnées pilote (NON-OFFICIAL) :** `B6_review_B26_05_coords.json`

**Contexte amont :** pilote B26_01 terminé — statut `READY_FOR_B6` ; coordonnées B26_01 restent `PILOT / NON-OFFICIAL`.

---

## Contexte

| Élément | Valeur |
|---------|--------|
| **Image** | `B26_05` — `images/train/B26_05.png` |
| **Dimensions** | 3008 × 3008 px |
| **Split** | train |
| **Visibilité B7** | **PARTIELLE** / **PARTIELLE** — qualité **MOYENNE** |
| **Motif B7** | bord de l'image — cas le plus serré du corpus pour la région ischiatique |
| **Cas** | Seul cas **PARTIEL bilatéral** du corpus `new_26` |
| **Labels officiels** | **14 kp inchangés** — `labels/train/B26_05.txt`, `annotation_pilot/annotations/new_26/B26_05.json` |

### Définition de travail évaluée

> **`IT_R` / `IT_L` = point caudal/inférieur identifiable du contour osseux de chaque tubérosité ischiatique sur la radiographie AP du bassin.**

| Attribut | Valeur |
|----------|--------|
| **STATUS** | **PROPOSED / CLINICAL VALIDATION REQUIRED** |
| **Validité** | Revue de faisabilité — **pas** validation clinique définitive |

---

## Coordonnées proposées (PILOT — revue uniquement)

| Landmark | x (px) | y (px) | x norm | y norm | v proposé | Côté patient | Position image |
|----------|-------:|-------:|-------:|-------:|:---------:|--------------|----------------|
| **`IT_R`** | **705.0** | **2892.0** | 0.2344 | 0.9614 | 2* | Droit | Gauche |
| **`IT_L`** | **2472.0** | **2876.0** | 0.8218 | 0.9561 | 2* | Gauche | Droite |

\* `v=2` **défendable mais non tranché** — voir §5 et §8. Politique stricte bord FOV → `v=0` bilatéral également défendable.

### Relations avec `TD_*` et `FSD_*` (officiels — non modifiés)

| Paire | Distance (px) | Δx | Δy | Interprétation |
|-------|--------------:|---:|---:|----------------|
| `IT_R` ↔ `TD_R` | 977 | −724 | +656 | IT latéral et **caudal** au teardrop ✓ |
| `IT_L` ↔ `TD_L` | 878 | +529 | +700 | IT latéral et **caudal** au teardrop ✓ |
| `IT_R` ↔ `FSD_R` | 168 | +164 | −17 | IT **médial** et légèrement **proximal** à la diaphyse fémorale ✓ |
| `IT_L` ↔ `FSD_L` | 145 | −119 | −38 | IT **médial** et **proximal** à la diaphyse fémorale ✓ |

**Aucune coïncidence** `IT_*` / `TD_*`. Distances IT–TD > 870 px des deux côtés.

### Marges caudales (FOV)

| Landmark | Marge au bord inférieur | % hauteur image | Proxy `FSD_*` (B7) |
|----------|------------------------:|----------------:|---------------------|
| `IT_R` (pilote) | **116 px** | 3,9 % | `FSD_R` y = 96,7 % |
| `IT_L` (pilote) | **132 px** | 4,4 % | `FSD_L` y = 96,9 % |
| Bord image (apex scan) | **~2 px** | ~0,1 % | cortex caudal atteint le bord sur les deux côtés |

---

## 1. Examen `IT_R` (droite patient — gauche image)

### 1.1 Visibilité

| Critère | Évaluation |
|---------|------------|
| **Statut revue** | **PARTIAL** |
| **Concordance B7** | Oui — seul cas PARTIELLE bilatéral du corpus |
| Structure cible identifiable | Oui — masse osseuse ischiatique latérale droite reconnaissable |
| Contour caudal | Présent mais **proche du bord inférieur du FOV** ; marge caudale minimale du corpus |
| Repère caudal net sans extrapolation | **Ambigu** — voir §5 |

### 1.2 Limites du contour osseux

| Zone | Description |
|------|-------------|
| **Proximal** | Contour ischiatique se continue vers le foramen obturé droit ; limite nette avec la branche ischio-pubienne |
| **Médial** | Bord osseux distinct de la branche ischio-pubienne et du pubis ; pas de fusion avec `TD_R` (1429, 2237) |
| **Latéral** | Transition vers le col / diaphyse fémorale droite ; **zone de piège fémoral** (x ≈ 450–550, y ≈ 2900–3008) |
| **Caudal** | Courbure inférieure de la tubérosité visible jusqu'à **~2 px** du bord image si l'on suit le cortex le plus bas ; repère « confortable » identifiable vers y ≈ 2885–2895 (x ≈ 680–730) |

**Point retenu (pilote) :** extrémité caudale du cortex ischiatique **identifiable dans le FOV** sans extrapolation hors image — (705, 2892).

### 1.3 Risques de confusion

| Structure | Risque | Détail B26_05 |
|-----------|:------:|---------------|
| **Fémur** | **Élevé** | Diaphyse droite (`FSD_R` x=541, y=2909) immédiatement latérale ; candidat (468, 3006) = bord caudal **fémoral**, non ischion |
| **`TD_R`** | Faible | Teardrop médial et proximal (+656 px en y) — pas de substitut |
| **Pubis / obturateur** | Faible | Repère médial clairement distinct |
| **Autres os** | Faible | Pas de superposition ischion–ischion ; pas d'artefact osseux parasite latéral |

### 1.4 Proximité bord image

- FOV inférieur **très serré** : `FSD_R`/`FSD_L` à ~97 % de la hauteur (proxy B7).
- Le cortex ischiatique caudal **touche ou frôle** le bord inférieur (marge scan ≈ 2 px).
- **Pas d'extrapolation hors FOV** requise si l'on retient le dernier pixel osseux **visible** dans l'image ; en revanche, **deux interprétations** du « point caudal » coexistent (§5).

---

## 2. Examen `IT_L` (gauche patient — droite image)

### 2.1 Visibilité

| Critère | Évaluation |
|---------|------------|
| **Statut revue** | **PARTIAL** |
| **Concordance B7** | Oui |
| Structure cible identifiable | Oui |
| Contour caudal | Légèrement **plus confortable** que `IT_R` (~132 px de marge au repère pilote) |
| Repère caudal net sans extrapolation | **Modérément ambigu** — même tension bord FOV qu'à droite, atténuée |

### 2.2 Limites du contour osseux

| Zone | Description |
|------|-------------|
| **Proximal** | Continuité avec branche ischio-pubienne gauche et obturateur |
| **Médial** | Séparation nette du pubis ; `TD_L` (1943, 2177) reste médial et proximal |
| **Latéral** | Transition fémorale ; diaphyse (`FSD_L` x=2591) plus latérale que l'ischion |
| **Caudal** | Courbure inférieure identifiable ; repère pilote (2472, 2876) sur le bord caudal projeté ; apex scan au bord ≈ (2491, 3006) |

### 2.3 Risques de confusion

| Structure | Risque | Détail B26_05 |
|-----------|:------:|---------------|
| **Fémur** | **Modéré** | Moins aigu que B26_01 côté L, mais candidat (2575, 2912) sur **diaphyse fémorale** latérale doit être rejeté |
| **`TD_L`** | Faible | Séparation spatiale nette |
| **Pubis / obturateur** | Faible | — |
| **Autres os** | Faible | — |

### 2.4 Proximité bord image

- Même contrainte FOV global que `IT_R`.
- Marge caudale pilote **~132 px** — légèrement supérieure à droite, mais toujours dans la classe « serrée » du corpus (comparer B26_18 FSD ~78–80 % vs B26_05 ~97 %).

---

## 3. Synthèse visibilité (échelle revue)

| Landmark | VISIBLE | PARTIAL | UNCERTAIN | NON_VISIBLE | Retenu |
|----------|:-------:|:-------:|:---------:|:-----------:|:------:|
| **`IT_R`** | — | **✓** | — | — | **PARTIAL** |
| **`IT_L`** | — | **✓** | — | — | **PARTIAL** |

**Justification :** tubérosités **présentes et annotables** (B7 : 26/26 annotables), mais repère caudal **peu confortable** et sensible au bord FOV — critère B7 PARTIELLE, pas NON VISIBLE.

**Non retenu UNCERTAIN :** la structure cible est localisable ; l'ambiguïté porte sur le **choix du pixel caudal** et le **seuil `v`**, pas sur l'identification de la tubérosité.

---

## 4. Vérifications demandées

| # | Objectif | Résultat revue |
|---|----------|----------------|
| 1 | Identifier IT_R et IT_L | **OK** — deux repères proposés (PILOT) |
| 2 | Classer visibilité | **PARTIAL / PARTIAL** — confirme B7 |
| 3 | Limites contour osseux | **Documentées** — §1.2, §2.2 |
| 4 | Confusion fémur / TD / autres | **Fémur = risque principal** (surtout IT_R) ; TD et pubis = faible |
| 5 | Comportement bord image | **Critique** — marge 2–132 px selon interprétation ; tension majeure du cas |
| 6 | Reproductibilité 2 annotateurs | **Modérée à faible sur y** — §5 |
| 7 | TD jamais utilisés comme IT | **OK** — coordonnées distinctes |
| 8 | Convention R/L | **OK** — `IT_R` x=705 (< centre 1504), `IT_L` x=2472 (> centre) ; marqueur « R » image cohérent |

---

## 5. Reproductibilité — test mental deux annotateurs

| Annotateur | Profil | `IT_R` | `IT_L` | Commentaire |
|------------|--------|--------|--------|-------------|
| **A** | Conservateur — dernier cortex **net dans FOV**, sans contact bord | (705, 2892) | (2472, 2876) | Aligné pilote revue |
| **B** | Maximaliste — pixel osseux le plus caudal **visible**, y compris au bord | (618, 3002) | (2488, 3002) | +110 à +128 px en y vs A |
| **C** | Piège fémoral — point le plus bas latéralement | (468, 3006) | (2575, 2912) | **Erreur structurelle** — diaphyse fémorale |

| Métrique | `IT_R` | `IT_L` |
|----------|--------|--------|
| Dispersion A vs B (Δy) | **~110 px** (~3,7 % hauteur) | **~126 px** (~4,2 %) |
| Dispersion A vs B (Δx) | ~87 px | ~16 px |
| Accord structure (A vs C) | **Non** — C sur fémur | **Non** — C sur fémur |
| Estimation reproductibilité | **≈ 55–65 %** | **≈ 60–70 %** |

**Lecture :** sur B26_01, la dispersion estimée était ± 8–15 px (cas EXCELLENT). Sur B26_05, la **seule ambiguïté du bord FOV** domine la variabilité inter-annotateurs — bien au-delà du seuil acceptable pour un landmark métrique sans règle B4 explicite.

---

## 6. Difficultés spécifiques B26_05

| Difficulté | Détail | Impact |
|------------|--------|--------|
| **Marge caudale minimale** | Seul cas PARTIEL bilatéral ; `FSD_*` à ~97 % hauteur | **Élevé** — référence corpus pour règle bord |
| **Ambiguïté apex caudal vs bord** | Cortex ischiatique frôle le bord (≈ 2 px) | **Élevé** — dispersion y inter-annotateurs |
| **Piège fémoral `IT_R`** | Diaphyse droite au contact latéral ; candidat bas x≈468 | **Élevé** — même mécanisme que B26_01 |
| **Piège fémoral `IT_L`** | Modéré — diaphyse x≈2591 plus latérale | **Modéré** |
| **Confusion TD** | Négligeable | Faible |
| **Qualité globale MOYENNE** | FOV bassin serré en bas | Modéré |

---

## 7. Candidats rejetés (traçabilité revue)

| Nom | x | y | Motif rejet |
|-----|--:|--:|-------------|
| `IT_R_femur` | 468 | 3006 | Trop latéral — bord caudal diaphyse fémorale droite, non tubérosité ischiatique |
| `IT_R_border_max` | 618 | 3002 | Apex caudal au bord image — interprétation B ; extrapolation implicite si apex anatomique hors FOV |
| `IT_L_femur` | 2575 | 2912 | Trop latéral — diaphyse fémorale gauche (`FSD_L` voisin) |
| `IT_L_border_max` | 2488 | 3002 | Apex caudal au bord image — interprétation B |

---

## 8. Recommandation `v` (revue — non officielle)

| Landmark | `v=2` défendable ? | `v=0` défendable ? | Recommandation revue |
|----------|:------------------:|:------------------:|----------------------|
| **`IT_R`** | Oui, si règle bord validée | Oui, si politique stricte « pas de repère au contact bord » | **`v=2` avec réserve clinique** ou **`v=0`** — **CLINICAL VALIDATION REQUIRED** |
| **`IT_L`** | Oui | Oui (moins urgent) | **`v=2` avec réserve** — légèrement plus confortable que R |

**Ne pas figer** sans validation clinique du seuil PARTIAL → `v=2` vs `v=0` (B4 §4.1, §4.4).

---

## 9. Conclusions demandées

### A. La définition proposée reste-t-elle applicable à B26_05 ?

**Oui, avec réserves importantes.**

La tubérosité ischiatique bilatérale est **identifiable** et la règle « point caudal du contour osseux » est **opérationnelle**, mais l'**interprétation du point caudal** devient **ambiguë** lorsque le cortex frôle le bord inférieur du FOV. La définition tient ; la **règle opérationnelle bord d'image** ne tient pas encore sans précision B4.

### B. Quelle difficulté spécifique existe ?

1. **Marge caudale minimale du corpus** (~2–132 px selon côté et convention).  
2. **Dispersion inter-annotateurs sur l'axe y** (≈ 110–126 px entre interprétations A et B).  
3. **Piège fémoral latéral**, surtout `IT_R`, avec candidats sur la diaphyse au lieu de l'ischion.  
4. **Décision `v=2` vs `v=0`** non tranchée pour le seul cas PARTIEL bilatéral.

### C. Faut-il modifier le guide B4 ?

**Oui — avant annotation de masse.**

| Modification proposée | Section cible | Priorité |
|-----------------------|---------------|:--------:|
| Seuil explicite **bord FOV** (ex. marge caudale < 5 % hauteur → conduite `v=0` ou revue) | §4.4 | **P0** |
| Règle **anti-fémur** : rejeter tout point caudal sur diaphyse latérale ; IT reste sur contour **pelvien** médial à la diaphyse | §3.1 / nouvelle § | **P0** |
| Illustration comparative B26_01 (piège L) + B26_05 (bord + piège R) | §9 | **P1** |
| Seuil PARTIAL → `v=2` vs `v=0` figé cliniquement | §4.1 | **P0** |

### D. Le piège fémoral observé sur B26_01 doit-il être ajouté explicitement comme règle d'annotation ?

**Oui.**

B26_05 **confirme** le mécanisme : sur `IT_R`, le point le plus bas de l'image (x ≈ 468, y ≈ 3006) correspond à la **diaphyse fémorale**, pas à l'ischion. Sans règle explicite, un annotateur non formé reproduira l'erreur A-IT01 de B26_01.

**Formulation proposée (revue, non intégrée) :**

> Ne jamais placer `IT_*` sur le contour caudal de la **diaphyse fémorale**. Le repère doit rester sur le contour **pelvien** de la tubérosité ischiatique, **médial** à l'axe fémoral proximal et distinct de `FSD_*`.

### E. Peut-on commencer la campagne B6 sur les 26 images ?

**Oui, de façon conditionnelle — statut `READY_FOR_B6` maintenu avec garde-fous.**

| Élément | Décision |
|---------|----------|
| **25 cas VISIBLE B7** | Campagne **autorisée** selon protocole B6 (après brief B4) |
| **B26_05** | Annotation **en session supervisée** uniquement ; trancher `v` et pixel caudal **avant** export |
| **B26_07, 11, 12** | Revues recommandées (déjà planifiées) — non bloquantes |
| **B4** | Mise à jour **P0** (bord + anti-fémur) **fortement recommandée** avant annotation en rafale |
| **Intégration YOLO** | **Interdite** tant que B5/B6 formels et validation clinique B1 non clos |

```
Décision revue B26_05 = READY_FOR_B6 (CONDITIONNEL)
```

**Conditions :**

1. Intégrer règles **bord FOV** et **anti-fémur** dans B4 (ou brief annotateur équivalent).
2. Annoter **B26_05** en session supervisée ; documenter choix `v` et pixel caudal.
3. Ne **pas** promouvoir les coordonnées pilote au statut officiel sans validation clinique.
4. Conserver B26_01 + B26_05 comme **duo de référence** (cas facile + cas limite) pour formation.

---

## 10. Fichiers et intégrité dataset

| Fichier | Modifié ? |
|---------|:---------:|
| `labels/train/B26_05.txt` | **Non** |
| `annotation_pilot/annotations/new_26/B26_05.json` | **Non** |
| `data.yaml` | **Non** |
| Modèles V2 / V3 | **Non** |
| Backend / Flutter | **Non** |
| Labels / coords B26_01 pilote | **Non** |

**Fichiers créés (NON-OFFICIAL) :**

- `B6_review_B26_05.md` (ce rapport)
- `B6_review_B26_05_coords.json` (coordonnées pilote revue)

---

*Revue B6 B26_05 — dataset officiel inchangé.*
