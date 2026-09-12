# B6 — Revue supervisée ciblée B26_26 (IT_R / IT_L)

**Généré :** 2026-08-29  
**Mode :** revue supervisée **READ-ONLY** — aucune coordonnée modifiée  
**Image :** `datasets/yolo_pose_new_26/images/val/B26_26.png` (2822 × 2426 px)  
**Sources :** `b6_working_annotations/B26_26.json`, `b6_image_required_QA.csv`, `bi_ischial_annotation_guidelines.md`

---

## Périmètre et contraintes

| Point | Coordonnées courantes | Session amont |
|-------|----------------------:|---------------|
| **IT_R** | (552.0, 2088.0) | IMAGE_REQUIRED MOVE (LOW) |
| **IT_L** | (1998.0, 1998.0) | IMAGE_REQUIRED MOVE (MEDIUM) |

**Contraintes respectées :**

- aucune coordonnée modifiée automatiquement ;
- aucune symétrie utilisée comme méthode d'annotation ;
- aucune coordonnée calculée ;
- labels YOLO officiels, `data.yaml`, V2/V3 — **inchangés** ;
- aucun training lancé ;
- **aucun autre cas modifié**.

---

## Méthode de revue supervisée

1. Examen radiographie **originale pleine résolution** (`B26_26.png`).
2. Vues locales agrandies par tubérosité :
   - zoom brut 560 × 680 px centré sur chaque IT ;
   - zoom contraste ×2 (aide visuelle, non utilisée pour calcul de coordonnées) ;
   - bande caudale (TD → bord inférieur FOV) par hémipelvis.
3. Évaluation indépendante IT_R et IT_L selon B1/B4.
4. Asymétrie bilatérale **notée** (Δy = 90 px, 3,7 %) — **non utilisée** pour repositionner un point.

**Aucune correction appliquée** — décision basée sur identification visuelle directe uniquement.

---

## Synthèse

| Landmark | Verdict | Confiance | Correction |
|----------|---------|:---------:|:----------:|
| **IT_R** | **REVIEW** | **LOW** | Non — coordonnées conservées |
| **IT_L** | **PASS** | **MEDIUM** | Non — coordonnées conservées |

### Conclusion session B26_26

```
→ B26_26_REVIEW_REQUIRED
```

**Motif :** IT_R non validable avec confiance suffisante — apex caudal et contraste local insuffisants pour clôture. IT_L validé indépendamment.

---

## IT_R — revue détaillée

**Coordonnées :** (552.0, 2088.0) — inchangées  
**Historique amont :** (538.3, 2030.0) → (552.0, 2088.0) [+14 x, +58 y]

### Questions supervisées

| Question | Réponse | Détail |
|----------|:-------:|--------|
| Point sur tubérosité ischiatique ? | **Oui** | Repère sur masse osseuse pelvienne caudale latérale — médial au fémur (Δx FSD = 205 px), distinct du TD |
| Apex caudal identifiable ? | **Non tranchable** | Vue caudale : contour inférieur flou ; apex arrondi possible **légèrement caudal** au repère actuel (~15–25 px visuels estimés) mais **non identifiable avec certitude** |
| Contraste permet validation fiable ? | **Non** | Bruit élevé, bande artefact horizontale traversant la zone ischiatique droite, bord cortical adouci |
| Anti-fémur (§3.6 B4) ? | **Oui** | Hors diaphyse ; FSD_R (347, 2223) sur fémur latéral — IT_R clairement médial |
| Dans FOV ? | **Oui** | Marge caudale 338 px (13,9 %) — pas d'extrapolation |

### Verdict IT_R

| Champ | Valeur |
|-------|--------|
| **Verdict** | **REVIEW** |
| **Confiance** | **LOW** |
| **Correction appliquée** | **Non** |

**Justification :** la structure cible (ischion D) est correcte et le repère n'est pas sur le fémur. En revanche, l'apex caudal strict selon B1/B4 ne peut pas être validé de façon fiable compte tenu du contraste/bruit local. Conformément à la consigne (« si impossible à trancher, conserver REVIEW »), les coordonnées sont **conservées** sans correction automatique.

**Recommandation (hors scope automatique) :** re-correction manuelle supervisée par annotateur clinique avec outil de zoom pleine résolution — repositionnement caudal possible si apex osseux net identifié visuellement.

---

## IT_L — revue détaillée (indépendante)

**Coordonnées :** (1998.0, 1998.0) — inchangées  
**Historique amont :** (2002.9, 1932.9) → (1998.0, 1998.0) [−5 x, +65 y]

### Questions supervisées

| Question | Réponse | Détail |
|----------|:-------:|--------|
| Validation indépendante placement ? | **Oui** | Repère sur bord cortical inférieur ischion G — os pelvien confirmé visuellement |
| Apex caudal identifiable ? | **Oui (approx.)** | Bande caudale : bord inférieur ischiatique nettement plus lisible que côté R ; repère sur ou immédiatement adjacent au bord caudal (écart apex strict estimé ≤ ~15 px — non utilisé pour calcul) |
| Anti-fémur ? | **Oui** | Δx FSD = 323 px — médial au fémur |
| IT ≠ TD ? | **Oui** | dist IT–TD = 334 px ; dy TD = +275 px caudal |
| Qualité image locale ? | **Acceptable** | Bruit présent mais contraste osseux suffisant pour validation indépendante |
| Asymétrie vs IT_R ? | **Notée, non utilisée** | Δy = 90 px (IT_L plus crânial) — peut refléter inclinaison pelvienne visible ; **aucun ajustement symétrique** |

### Verdict IT_L

| Champ | Valeur |
|-------|--------|
| **Verdict** | **PASS** |
| **Confiance** | **MEDIUM** |
| **Correction appliquée** | **Non** |

**Justification :** validation anatomique indépendante réussie — tubérosité ischiatique gauche, apex caudal/inférieur identifiable sur cortex osseux, critères B1/B4 satisfaits au niveau working annotation. L'asymétrie bilatérale avec IT_R (incertain) n'invalide pas le placement IT_L pris isolément.

---

## Asymétrie bilatérale (information uniquement)

| Métrique | Valeur | Interprétation |
|----------|--------:|----------------|
| Δy IT_R − IT_L | 90 px | IT_R plus caudal |
| Δy % (hauteur image) | 3,7 % | Au-dessus seuil P0 typique (~2 %) |
| Utilisation | **Aucune** | Notée pour traçabilité ; pas de repositionnement automatique |

L'asymétrie peut être partiellement expliquée par l'incertitude IT_R plutôt qu'une erreur IT_L — d'où la validation indépendante de IT_L.

---

## Historique des coordonnées (conservé, non modifié)

| Landmark | Offset initial | Post IMAGE_REQUIRED | Post revue supervisée | Δ supervisée |
|----------|---------------:|--------------------:|----------------------:|:------------:|
| IT_R | (538.3, 2030.0) | (552.0, 2088.0) | **(552.0, 2088.0)** | — |
| IT_L | (2002.9, 1932.9) | (1998.0, 1998.0) | **(1998.0, 1998.0)** | — |

Aucune entrée ajoutée à `correction_history` — revue READ-ONLY.

---

## Fichiers

| Fichier | Modifié |
|---------|:-------:|
| `b6_B26_26_supervised_review.md` | **Oui** (ce document) |
| `b6_B26_26_supervised_review.csv` | **Oui** |
| `b6_working_annotations/B26_26.json` | **Non** |
| Autres cas B6 | **Non** |
| Labels YOLO / `data.yaml` / V2 / V3 | **Non** |

*Export machine : `b6_B26_26_supervised_review.csv`*

---

## Prochaine étape

Re-correction **manuelle supervisée** de **IT_R uniquement** par annotateur clinique (identification visuelle directe apex caudal ischion D). Après arbitrage IT_R, re-évaluer si clôture `B26_26_VALIDATED` est atteignable. IT_L **PASS MEDIUM** — aucune action requise sauf si IT_R est repositionné et qu'une cohérence clinique globale est souhaitée (sans symétrie automatique).
