# B6 — Revue visuelle READ-ONLY (5 cas)

**Généré :** 2026-08-28  
**Mode :** revue **READ-ONLY** — aucune modification d'annotation, label officiel, `data.yaml`, V2/V3, backend ou Flutter  
**Source :** `b6_working_annotations/B26_XX.json` (NON-OFFICIAL)  
**Images :** `images/train/B26_XX.png`

---

## Objectif

Superposition visuelle de `IT_R` / `IT_L` sur les radiographies originales ; validation anatomique selon la définition de travail B6 :

> Point caudal/inférieur identifiable du contour osseux de chaque tubérosité ischiatique sur AP bassin.

**Échelle de verdict :**

| Verdict | Signification |
|---------|---------------|
| **PASS** | Position anatomiquement correcte |
| **CORRECTABLE** | Proche mais doit être déplacé |
| **UNCERTAIN** | Impossible de valider clairement |
| **FAIL** | Mauvaise structure anatomique |

---

## Méthode de revue

1. Chargement radiographie PNG + coordonnées `b6_working_annotations/`.
2. Superposition `IT_R` (rouge) / `IT_L` (bleu) + repères officiels `FSD_*` (contexte anti-fémur, non modifiés).
3. Vérifications : structure (ischion vs fémur), R/L, règle caudale, marge FOV, cas particuliers documentés.
4. Analyse complémentaire : intensité osseuse locale, distance à `FSD_*`, apex caudal osseux local (scan ±120 px).

**Aucun fichier d'annotation n'a été modifié.**

---

## Synthèse globale (10 landmarks)

| Verdict | N | % |
|---------|--:|--:|
| PASS | 1 | 10 % |
| CORRECTABLE | 5 | 50 % |
| UNCERTAIN | 4 | 40 % |
| FAIL | 1 | 10 % |

| Confiance | N |
|-----------|--:|
| HIGH | 2 |
| MEDIUM | 5 |
| LOW | 3 |

---

## Résultats par cas

### B26_01 — piège fémoral `IT_L`

| Landmark | x | y | Verdict | Confiance | Commentaire |
|----------|--:|--:|---------|-----------|-------------|
| **IT_R** | 548.0 | 2140.0 | **PASS** | HIGH | Cas pilote manuel ; tubérosité droite nette ; médial au fémur ; marge caudale confortable (19,7 %) |
| **IT_L** | 1756.0 | 2143.0 | **CORRECTABLE** | MEDIUM | Piège fémoral évité (candidat x=2136 rejeté) ; repère sur ischion mais légèrement trop crânial vs apex caudal |

**Observations visuelles :**

- `IT_R` : crosshair sur le bord caudal de l'ischion droit, latéral au foramen obturé, clairement distinct du fémur.
- `IT_L` : point médial à la diaphyse fémorale gauche (correct vs piège latéral) ; apex cortical inférieur visible ~15–40 px plus bas — déplacement caudal recommandé.

**R/L :** OK — `IT_R` à gauche image, `IT_L` à droite.  
**Règle caudale :** OK côté R ; côté L légèrement sous-estimée.  
**FOV :** OK (marges ~520 px).

---

### B26_05 — bord FOV + piège fémoral `IT_R`

| Landmark | x | y | Verdict | Confiance | Commentaire |
|----------|--:|--:|---------|-----------|-------------|
| **IT_R** | 705.0 | 2892.0 | **UNCERTAIN** | LOW | PARTIAL ; anti-fémur OK mais cortex peu net au contact FOV ; ambiguïté apex caudal (~110 px dispersion y) |
| **IT_L** | 2472.0 | 2876.0 | **CORRECTABLE** | MEDIUM | PARTIAL ; repère probablement sur ischion mais ~100 px trop crânial ; marge FOV 4,4 % |

**Observations visuelles :**

- Seul cas **PARTIAL bilatéral** ; FOV caudal très serré (`FSD_*` à ~97 % hauteur).
- `IT_R` : position conservatrice médiale au fémur (rejet candidat fémoral x=468) ; zone sombre — difficile de trancher cortex ischiatique vs tissus mous au-dessus du bord.
- `IT_L` : légèrement plus confortable que R ; relation spatiale IT médial à FSD cohérente ; apex caudal local plus bas.

**R/L :** OK.  
**Règle caudale :** Tension majeure — dispersion inter-annotateurs documentée (~110 px).  
**FOV :** **Critique** — marges 116 px (R) / 132 px (L).

---

### B26_07 — gaz intestinal

| Landmark | x | y | Verdict | Confiance | Commentaire |
|----------|--:|--:|---------|-----------|-------------|
| **IT_R** | 640.4 | 2431.5 | **UNCERTAIN** | LOW | Gaz intestinal central masque le repère ; latéralité et anti-fémur plausibles mais os non vérifiable |
| **IT_L** | 1834.0 | 2379.0 | **CORRECTABLE** | MEDIUM | Ischion gauche identifiable ; ~90 px trop crânial ; repère latéral moins obscurci |

**Observations visuelles :**

- Opacités gazeuses centrales (A-GAS07) réduisent le contraste osseux côté droit.
- `IT_R` : placé médial au fémur en zone caudale attendue, mais validation du cortex impossible.
- `IT_L` : contour ischiatique partiellement visible ; déplacement caudal ~80–100 px probablement nécessaire.

**R/L :** OK (vérifiés indépendamment malgré le gaz).  
**Règle caudale :** Non confirmable (R) ; sous-estimée (L).  
**FOV :** OK (marges 9,5 % / 11,5 %).

---

### B26_11 — rotation pelvienne

| Landmark | x | y | Verdict | Confiance | Commentaire |
|----------|--:|--:|---------|-----------|-------------|
| **IT_R** | 566.7 | 2298.6 | **UNCERTAIN** | LOW | Rotation pelvienne ; faible contraste local ; apex caudal ~96 px plus bas non atteint |
| **IT_L** | 2052.2 | 2252.6 | **CORRECTABLE** | MEDIUM | Ischion gauche reconnaissable ; ~120 px trop crânial ; R/L cohérent malgré rotation |

**Observations visuelles :**

- Légère rotation (A-ROT11) : obturateurs asymétriques ; repères R/L annotés indépendamment (cohérent).
- `IT_R` : zone de faible densité entre ischion et fémur — structure non tranchable visuellement.
- `IT_L` : masse ischiatique visible ; point au-dessus de l'apex caudal cortical.

**R/L :** OK.  
**Règle caudale :** Sous-estimation systémique (~100 px) sur les deux côtés.  
**FOV :** OK (marges ~10–12 %).

---

### B26_24 — anomalie QA

| Landmark | x | y | Verdict | Confiance | Commentaire |
|----------|--:|--:|---------|-----------|-------------|
| **IT_R** | 616.0 | 2352.0 | **FAIL** | HIGH | **Piège fémoral confirmé** — point sur diaphyse (Δx FSD=71 px, intensité osseuse élevée) ; anomalie QA validée |
| **IT_L** | 1900.0 | 2120.5 | **CORRECTABLE** | MEDIUM | Ischion gauche correct ; ~97 px trop crânial ; asymétrie Δy R-L=231 px due à l'erreur R |

**Observations visuelles :**

- `IT_R` : crosshair sur le bord latéral/medial de la diaphyse fémorale droite — **structure incorrecte**.
- `IT_L` : sur contour ischiatique gauche, médial au fémur ; apex caudal local plus bas (y≈2217).

**R/L :** Côté L OK ; côté R structure erronée (pas erreur R/L mais mauvais os).  
**Règle caudale :** R trop bas sur mauvaise structure ; L sous-estimée.  
**FOV :** R serré (114 px, 4,6 %) ; L confortable (14,0 %).

---

## Tableau complet

| Image | Landmark | x | y | Verdict | Confiance | Commentaire |
|-------|----------|--:|--:|---------|-----------|-------------|
| B26_01 | IT_R | 548.0 | 2140.0 | PASS | HIGH | Tubérosité droite nette ; anti-fémur OK ; FOV confortable |
| B26_01 | IT_L | 1756.0 | 2143.0 | CORRECTABLE | MEDIUM | Piège fémoral évité ; légèrement trop crânial |
| B26_05 | IT_R | 705.0 | 2892.0 | UNCERTAIN | LOW | PARTIAL FOV ; ambiguïté apex caudal ; cortex non net |
| B26_05 | IT_L | 2472.0 | 2876.0 | CORRECTABLE | MEDIUM | Probable ischion ; ~100 px trop crânial ; FOV serré |
| B26_07 | IT_R | 640.4 | 2431.5 | UNCERTAIN | LOW | Gaz intestinal ; os non vérifiable |
| B26_07 | IT_L | 1834.0 | 2379.0 | CORRECTABLE | MEDIUM | Ischion L identifiable ; ~90 px trop crânial |
| B26_11 | IT_R | 566.7 | 2298.6 | UNCERTAIN | LOW | Rotation ; contraste insuffisant |
| B26_11 | IT_L | 2052.2 | 2252.6 | CORRECTABLE | MEDIUM | Ischion L ; ~120 px trop crânial |
| B26_24 | IT_R | 616.0 | 2352.0 | FAIL | HIGH | **Sur fémur** — piège fémoral (QA confirmé) |
| B26_24 | IT_L | 1900.0 | 2120.5 | CORRECTABLE | MEDIUM | Ischion L OK ; caudal sous-estimé |

*(Export CSV : `b6_visual_review_5cases.csv`)*

---

## Motifs récurrents

| Motif | Cas touchés | Impact |
|-------|-------------|--------|
| **Sous-estimation caudale** (~90–120 px vs apex cortical local) | B26_01 L, B26_05 L, B26_07 L, B26_11 L, B26_24 L | CORRECTABLE systématique sur points offset |
| **Piège fémoral** | B26_01 L (évité), B26_05 R (évité), **B26_24 R (FAIL)** | Règle anti-fémur insuffisante pour offset auto |
| **Bord FOV / PARTIAL** | B26_05 bilatéral | UNCERTAIN / CORRECTABLE |
| **Gaz intestinal** | B26_07 R | UNCERTAIN |
| **Rotation pelvienne** | B26_11 R | UNCERTAIN |

---

## Points prioritaires de correction

| Priorité | Image | Landmark | Action |
|:--------:|-------|----------|--------|
| **P0** | B26_24 | IT_R | Re-placer sur tubérosité ischiatique droite (hors diaphyse fémorale) |
| **P1** | B26_05 | IT_R, IT_L | Session supervisée — trancher apex caudal vs bord FOV |
| **P1** | B26_01 | IT_L | Valider déplacement caudal ~15–40 px sur cortex ischiatique |
| **P2** | B26_07, B26_11, B26_24 | IT_L (+ IT_R si visible) | Ajuster caudalité ; revue clinique si gaz/rotation |

---

## Décision

```
Décision = B — corrections nécessaires → corriger les points identifiés
```

### Motivation

| Pour B | Contre A / C |
|--------|--------------|
| **1/10 PASS** avec confiance HIGH (`B26_01 IT_R` pilote manuel) prouve que la définition et l'annotation manuelle sont viables | **A** exclu : 9/10 landmarks non PASS dans cet échantillon (volontairement difficile) |
| **5/10 CORRECTABLE** — erreurs principalement de **position caudale** (~90–120 px), structure souvent correcte | **C** exclu : pas d'échec systémique total — la méthode offset produit des repères anatomiquement plausibles dans ~50 % des cas (CORRECTABLE, pas FAIL) |
| **1 FAIL avéré** (`B26_24 IT_R` fémur) — correction ciblée suffit | Réannotation manuelle des **52 points** non justifiée tant que les CORRECTABLE sont ajustables |
| **4 UNCERTAIN** — cas limites (FOV, gaz, rotation) requièrent revue humaine, pas rejet de la campagne | |

### Prochaines étapes recommandées

1. Corriger **P0** `B26_24 IT_R` (FAIL fémoral).
2. Ajuster les **5 CORRECTABLE** (déplacement caudal vers apex cortical).
3. Revue clinique des **4 UNCERTAIN** (B26_05 R, B26_07 R, B26_11 R + confirmation B26_05 L).
4. **Ne pas promouvoir** vers labels officiels.
5. Poursuivre le QA sur les 21 cas restants **après** correction de l'échantillon pilote.

---

## Intégrité dataset

| Élément | Modifié ? |
|---------|:---------:|
| `b6_working_annotations/*.json` | **Non** |
| Labels officiels YOLO / JSON | **Non** |
| `data.yaml` | **Non** |
| V2 / V3 | **Non** |
| Backend / Flutter | **Non** |

**Fichiers créés (revue uniquement) :**

- `b6_visual_review_5cases.md` (ce rapport)
- `b6_visual_review_5cases.csv`

---

*Revue visuelle B6 — 5 cas — READ-ONLY.*
