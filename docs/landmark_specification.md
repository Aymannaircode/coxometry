# Spécification des landmarks — MVP coxométrie adulte

**Date :** 17 juillet 2026  
**Périmètre :** définition des landmarks pour un **futur dataset adulte annoté**  
**Mesures cibles MVP :** VCE / Wiberg · Angle de Tönnis · CCD  
**Contraintes respectées :** aucun entraînement, aucune modification de dataset / annotation, aucune conversion, aucun modèle créé  

**Documents liés :** `docs/dataset1_analysis.md` (MTDDH Dataset 1, landmarks pédiatriques DDH)

---

## 1. Objectif et principes

Produire un schéma de landmarks **minimal, nommé de façon unique, géométriquement suffisant** pour calculer sur une radiographie **AP du bassin** (adulte, orthograde) :

1. l’**angle VCE / LCEA de Wiberg** ;
2. l’**angle de Tönnis** (inclinaison du sourcil / HTE) ;
3. l’**angle CCD** (caput-collum-diaphysaire = neck-shaft angle).

### Conventions de nommage

| Élément | Règle |
|---------|--------|
| Identifiant | `LM-XX` (stable, ne change pas) |
| Nom standardisé | `{STRUCTURE}_{COTE}` en ASCII, majuscules |
| Côté | `R` = droit patient · `L` = gauche patient · `M` = médian / dérivé (pas de point annoté) |
| Coordonnées | pixels image, origine coin supérieur gauche ; côté patient = convention radio AP (droite patient à **gauche** de l’image) |

### Hypothèses d’acquisition (prérequis mesure)

- Radio **AP bassin** (idéalement orthograde / « standard ») ;
- Les mesures VCE et Tönnis sont **sensibles** à l’inclinaison / rotation pelvienne ;
- Le CCD est **sensible** à la rotation fémorale (rotation externe → surestimation fréquente).

Ces prérequis ne sont **pas** des landmarks ; ils doivent être documentés au niveau examen (QC), éventuellement via les régions type Dataset 1.

---

## 2. Synthèse : catalogue MVP

### 2.1 Landmarks obligatoires (14 points)

| ID | Nom | Côté | Obligatoire | Rôle principal |
|----|-----|------|-------------|----------------|
| LM-01 | `TD_R` | Droit | Oui | Référence horizontale pelvienne |
| LM-02 | `TD_L` | Gauche | Oui | Référence horizontale pelvienne |
| LM-03 | `FHC_R` | Droit | Oui | VCE, CCD (axe col) |
| LM-04 | `FHC_L` | Gauche | Oui | VCE, CCD (axe col) |
| LM-05 | `ASL_R` | Droit | Oui | VCE + Tönnis (extrémité latérale sourcil) |
| LM-06 | `ASL_L` | Gauche | Oui | VCE + Tönnis |
| LM-07 | `ASM_R` | Droit | Oui | Tönnis (extrémité médiale sourcil) |
| LM-08 | `ASM_L` | Gauche | Oui | Tönnis |
| LM-09 | `FNM_R` | Droit | Oui | CCD (2ᵉ point axe du col) |
| LM-10 | `FNM_L` | Gauche | Oui | CCD |
| LM-11 | `FSP_R` | Droit | Oui | CCD (axe diaphysaire proximal) |
| LM-12 | `FSP_L` | Gauche | Oui | CCD |
| LM-13 | `FSD_R` | Droit | Oui | CCD (axe diaphysaire distal) |
| LM-14 | `FSD_L` | Gauche | Oui | CCD |

### 2.2 Landmarks optionnels MVP (recommandés pour lever une ambiguïté VCE)

| ID | Nom | Côté | Obligatoire | Rôle |
|----|-----|------|-------------|------|
| LM-15 | `ALB_R` | Droit | **Optionnel** | VCE « bord osseux latéral » si distinct du sourcil |
| LM-16 | `ALB_L` | Gauche | **Optionnel** | Idem |

### 2.3 Points / lignes dérivés (non annotés)

| Nom dérivé | Construction | Usage |
|------------|--------------|-------|
| `ITH` | Droite `TD_R`–`TD_L` | Axe transverse pelvien (horizontal de référence) |
| `VERT_R` / `VERT_L` | Droite passant par `FHC_*`, **perpendiculaire** à `ITH` | Branche verticale du VCE |
| `SOURCIL_R` / `SOURCIL_L` | Droite `ASM_*`–`ASL_*` | Toit acétabulaire (Tönnis) |
| `NECK_R` / `NECK_L` | Droite `FHC_*`–`FNM_*` | Axe du col |
| `SHAFT_R` / `SHAFT_L` | Droite `FSP_*`–`FSD_*` | Axe diaphysaire |

---

## 3. Définition mesure par mesure

### 3.1 VCE / angle de Wiberg (LCEA)

#### Géométrie retenue pour le MVP

Sur chaque hanche :

1. Construire `ITH` = `TD_R` → `TD_L`.
2. Construire la verticale pelvienne `VERT` : droite par `FHC`, **⟂** à `ITH` (vers le haut).
3. Construire la droite `FHC` → `ASL` (méthode **sourcil** / Ogata, privilégiée ici).
4. **VCE** = angle entre `VERT` et `FHC→ASL`, côté latéral de couverture.

**Variante optionnelle :** remplacer `ASL` par `ALB` si l’on souhaite aussi le VCE au **bord osseux** le plus latéral (méthode « classique » parfois utilisée ; voir ambiguïté A1).

#### Points anatomiques nécessaires

| Rôle | Landmark | Obligatoire |
|------|----------|-------------|
| Centre tête | `FHC_R` / `FHC_L` | Oui |
| Bord latéral de couverture (sourcil) | `ASL_R` / `ASL_L` | Oui |
| Horizontal pelvien | `TD_R`, `TD_L` | Oui |
| Bord osseux latéral (variante) | `ALB_R` / `ALB_L` | Optionnel |

#### Réutilisation Dataset 1

| Landmark MVP | Dataset 1 | Verdict |
|--------------|-----------|---------|
| `FHC_*` | `rc` / `lc` (RFHC / LFHC) | **Réutilisable conceptuellement** seulement : même *idée* (centre tête), mais D1 = noyau d’ossification **pédiatrique**, pas le centre géométrique adulte d’un cercle de Mose. **À redéfinir** sur dataset adulte. |
| `ASL_*` | `re` / `le` (RASM / LASM) | **Partiellement proche** (marge superolatérale), mais D1 n’impose pas le **sourcil sclérotique adulte**. **Ne pas copier** les labels D1 tels quels. |
| `TD_*` | — | **Absent** → **nouveau** |
| `ALB_*` | — | **Absent** → **nouveau** (optionnel) |

#### Nouveaux landmarks à ajouter (vs Dataset 1)

`TD_R`, `TD_L`, et redéfinition adulte de `FHC_*` / `ASL_*` ; optionnellement `ALB_*`.

---

### 3.2 Angle de Tönnis (adulte)

Aussi appelé : acetabular index of the weight-bearing zone, **HTE**, sourcil angle, acetabular roof obliquity.

#### Géométrie retenue pour le MVP

Sur chaque hanche :

1. `ITH` = `TD_R`–`TD_L` (même référence que VCE).
2. Droite du sourcil = `ASM` → `ASL`.
3. Horizontale de mesure = droite passant par `ASM`, **parallèle** à `ITH`.
4. **Angle de Tönnis** = angle entre cette horizontale et `ASM→ASL`.

Convention de signe à figer lors de l’annotation guide : valeur **positive** si le sourcil s’incline vers le bas en latéral (dysplasie typique) — à valider avec le clinicien référent (ambiguïté A4).

#### Points anatomiques nécessaires

| Rôle | Landmark | Obligatoire |
|------|----------|-------------|
| Extrémité médiale du sourcil | `ASM_R` / `ASM_L` | Oui |
| Extrémité latérale du sourcil | `ASL_R` / `ASL_L` | Oui (partagé avec VCE) |
| Horizontal pelvien | `TD_R`, `TD_L` | Oui |

**Note :** aucune dépendance à `FHC` pour le Tönnis « standard ». Une variante « modified Tönnis » (si `ASM` mal visible) existe dans la littérature ; **non retenue** dans le MVP de base (ambiguïté A3).

#### Réutilisation Dataset 1

| Landmark MVP | Dataset 1 | Verdict |
|--------------|-----------|---------|
| `ASL_*` | `re` / `le` | Proche mais **non équivalent** (voir §3.1) |
| `ASM_*` | — | **Absent** → **nouveau** (critique) |
| `TD_*` | — | **Absent** → **nouveau** |
| `ry` / `ly` (RTCC / LTCC) | cartilage triradié | **Non réutilisable** pour Tönnis adulte (cartilage fermé chez l’adulte) |

#### Nouveaux landmarks à ajouter

`ASM_R`, `ASM_L`, `TD_R`, `TD_L` (+ redéfinition `ASL_*`).

---

### 3.3 Angle CCD (caput-collum-diaphysaire)

Synonymes : neck-shaft angle (NSA), collodiaphyseal angle, femoral inclination angle.

#### Géométrie retenue pour le MVP

Sur chaque hanche :

1. Axe du col `NECK` = `FHC` → `FNM`.
2. Axe diaphysaire `SHAFT` = `FSP` → `FSD`.
3. **CCD** = angle **médial** (obtus typiquement ~120–135°) entre `NECK` et `SHAFT`.

Pas de dépendance aux teardrops pour le calcul géométrique pur ; la qualité du cliché (rotation fémorale) reste critique.

#### Points anatomiques nécessaires

| Rôle | Landmark | Obligatoire |
|------|----------|-------------|
| Centre tête (origine axe col) | `FHC_R` / `FHC_L` | Oui |
| 2ᵉ point axe col | `FNM_R` / `FNM_L` | Oui |
| Point proximal axe diaphyse | `FSP_R` / `FSP_L` | Oui |
| Point distal axe diaphyse | `FSD_R` / `FSD_L` | Oui |

#### Réutilisation Dataset 1

| Landmark MVP | Dataset 1 | Verdict |
|--------------|-----------|---------|
| `FHC_*` | `rc` / `lc` | Concept seulement (voir §3.1) |
| `FNM_*` | — | **Absent** → **nouveau** |
| `FSP_*`, `FSD_*` | — | **Absent** → **nouveau** |
| `rh` / `lh` (RMOFM / LMOFM) | milieu bord supérieur métaphyse ossifiée **pédiatrique** | **Non équivalent** à un axe de col / diaphyse adulte → **ne pas réutiliser** pour le CCD |

#### Nouveaux landmarks à ajouter

`FNM_*`, `FSP_*`, `FSD_*` (+ redéfinition `FHC_*`).

---

## 4. Fiches détaillées par landmark

### LM-01 / LM-02 — `TD_R` / `TD_L`

| Champ | Contenu |
|-------|---------|
| **ID** | LM-01 (`TD_R`), LM-02 (`TD_L`) |
| **Nom** | Teardrop inférieur droit / gauche |
| **Côté** | Droit / Gauche |
| **MVP** | **Obligatoire** |
| **Définition anatomique** | Point le plus **inférieur** de la figure en larme acétabulaire (teardrop) sur le cliché AP — landmark osseux de la paroi médiale acétabulaire projetée. |
| **Position sur AP bassin** | À la partie basse médiale de chaque cotyle, entre tête fémorale et ligne ilio-ischiatique ; paire symétrique servant de base à `ITH`. |
| **Mesures** | VCE (vertical ⟂ `ITH`) ; Tönnis (horizontal ∥ `ITH`) |
| **Dataset 1** | Absent → **nouveau** |
| **Ambiguïtés** | **A2** : certains protocoles utilisent les **tubérosités ischiatiques** ou la droite des centres de tête à la place des teardrops. Le MVP **fixe les teardrops** ; toute autre référence doit être un landmark optionnel futur, pas un remplacement silencieux. Le « point exact » du teardrop (extrémité inférieure vs centre de la larme) doit être illustré dans le guide d’annotation. |

### LM-03 / LM-04 — `FHC_R` / `FHC_L`

| Champ | Contenu |
|-------|---------|
| **ID** | LM-03 / LM-04 |
| **Nom** | Centre de la tête fémorale |
| **Côté** | Droit / Gauche |
| **MVP** | **Obligatoire** |
| **Définition anatomique** | Centre du **cercle de meilleure approximation** (Mose / best-fit) de la tête fémorale osseuse sur l’AP. |
| **Position sur AP bassin** | Au centre géométrique de la tête, bilatéral. |
| **Mesures** | VCE ; CCD (origine de l’axe du col) |
| **Dataset 1** | Analogue `rc`/`lc` — **réutilisation conceptuelle uniquement** ; redéfinition adulte obligatoire |
| **Ambiguïtés** | **A5** : tête asphérique, coxa plana, ostéophytes, nécrose → cercle mal défini. Protocole recommandé : annoter le centre du cercle ajusté sur la portion **sphérique conservée** ; si impossible, marquer `v=0` (invisible / non fiable) plutôt qu’un centre inventé. L’annotation d’un **cercle** (centre + rayon) est plus robuste qu’un point seul, mais le MVP pose ne stocke que le **centre** ; le rayon peut être métadonnée d’annotation hors keypoints. |

### LM-05 / LM-06 — `ASL_R` / `ASL_L`

| Champ | Contenu |
|-------|---------|
| **ID** | LM-05 / LM-06 |
| **Nom** | Extrémité **latérale du sourcil** (acetabular sourcil lateral) |
| **Côté** | Droit / Gauche |
| **MVP** | **Obligatoire** |
| **Définition anatomique** | Point le plus **latéral** de la zone sclérotique du toit acétabulaire porteur (**sourcil**), **sans** inclure un ostéophyte rim / éperon latéral non porteur lorsque celui-ci se distingue du sourcil. |
| **Position sur AP bassin** | Bord superolatéral du cotyle, sur la densification du toit. |
| **Mesures** | VCE (méthode sourcil) ; Tönnis (avec `ASM`) |
| **Dataset 1** | Proche de `re`/`le` (RASM/LASM) — **pas une équivalence stricte** |
| **Ambiguïtés** | **A1** (critique) : littérature divergente entre (a) bord **latéral du sourcil** et (b) bord osseux **le plus latéral** de l’acétabulum pour le VCE. Le MVP **choisit (a) pour `ASL`**. Si (b) est requis en parallèle → annoter aussi `ALB` (LM-15/16). |

### LM-07 / LM-08 — `ASM_R` / `ASM_L`

| Champ | Contenu |
|-------|---------|
| **ID** | LM-07 / LM-08 |
| **Nom** | Extrémité **médiale du sourcil** (acetabular sourcil medial) |
| **Côté** | Droit / Gauche |
| **MVP** | **Obligatoire** |
| **Définition anatomique** | Point le plus **médial** de la zone sclérotique du toit porteur (début médial du sourcil). |
| **Position sur AP bassin** | Partie superomédiale du toit, au début de la densification horizontale du sourcil. |
| **Mesures** | Tönnis uniquement (dans ce MVP) |
| **Dataset 1** | **Absent** → **nouveau** |
| **Ambiguïtés** | **A3** : le bord médial du sourcil est parfois **peu contrasté**. La littérature décrit une variante « modified Tönnis » lorsque ce point est difficile ; **non spécifiée comme landmark MVP** — si `ASM` non identifiable, laisser `v=0` et ne pas inventer. |

### LM-09 / LM-10 — `FNM_R` / `FNM_L`

| Champ | Contenu |
|-------|---------|
| **ID** | LM-09 / LM-10 |
| **Nom** | Point milieu de l’axe du col fémoral (femoral neck midline) |
| **Côté** | Droit / Gauche |
| **MVP** | **Obligatoire** |
| **Définition anatomique** | Point situé sur l’**axe médullaire / médian du col**, au niveau du **milieu de la longueur du col** visible (entre tête et jonction cervico-trochantérienne), à égale distance approximative des corticales supérieure et inférieure du col. |
| **Position sur AP bassin** | Sur le col, entre tête et massif trochantérien. |
| **Mesures** | CCD (avec `FHC` → axe du col) |
| **Dataset 1** | **Absent** → **nouveau** |
| **Ambiguïtés** | **A6** : certains protocoles construisent l’axe du col par **deux** milieux de largeur (proximal + distal) sans passer explicitement par `FHC` ; d’autres forcent l’axe à passer par `FHC`. Le MVP **force** `NECK = FHC–FNM` (cohérent avec les descriptions NSA / CCD courantes). Col court, cam, fracture, prothèse → annotation difficile. |

### LM-11 / LM-12 — `FSP_R` / `FSP_L`

| Champ | Contenu |
|-------|---------|
| **ID** | LM-11 / LM-12 |
| **Nom** | Point proximal de l’axe diaphysaire fémoral |
| **Côté** | Droit / Gauche |
| **MVP** | **Obligatoire** |
| **Définition anatomique** | Point sur l’**axe médian de la diaphyse proximale**, juste **au-dessous du petit trochanter** (ou au niveau le plus proximal où les deux corticales diaphysaires sont clairement parallèles). |
| **Position sur AP bassin** | Diaphyse haute, sous le petit trochanter. |
| **Mesures** | CCD |
| **Dataset 1** | **Absent** → **nouveau** |
| **Ambiguïtés** | **A7** : le niveau exact « sous petit trochanter » varie selon les auteurs ; il doit être **illustré** dans le guide. Sur un AP bassin, le fémur distal peut être **coupé** → voir `FSD`. |

### LM-13 / LM-14 — `FSD_R` / `FSD_L`

| Champ | Contenu |
|-------|---------|
| **ID** | LM-13 / LM-14 |
| **Nom** | Point distal de l’axe diaphysaire fémoral (dans le FOV) |
| **Côté** | Droit / Gauche |
| **MVP** | **Obligatoire** |
| **Définition anatomique** | Point sur l’**axe médian diaphysaire**, le plus **distal possible** encore visible sur le cliché, où les corticales médiale et latérale restent identifiables. |
| **Position sur AP bassin** | Diaphyse moyenne / basse selon le cadrage. |
| **Mesures** | CCD |
| **Dataset 1** | **Absent** → **nouveau** |
| **Ambiguïtés** | **A7** : si le FOV est trop court, `FSP` et `FSD` sont trop proches → axe diaphysaire **instable**. Règle proposée : exiger une séparation minimale (ex. ≥ 0,5× diamètre de tête) ; sinon `v=0` pour `FSD` et CCD non calculable. Cette règle de distance est une **convention projet** à valider, non une norme unique universelle. |

### LM-15 / LM-16 — `ALB_R` / `ALB_L` (optionnels)

| Champ | Contenu |
|-------|---------|
| **ID** | LM-15 / LM-16 |
| **Nom** | Bord osseux acétabulaire latéral (acetabular lateral bone) |
| **Côté** | Droit / Gauche |
| **MVP** | **Optionnel** |
| **Définition anatomique** | Point osseux **le plus latéral** du rebord acétabulaire supérieur, **y compris** rim / ostéophyte si présent et distinct du sourcil. |
| **Position sur AP bassin** | Souvent latéral à `ASL` en cas d’éperon. |
| **Mesures** | VCE variante « bord osseux » |
| **Dataset 1** | Absent (D1 `re`/`le` peut être plus proche de `ASL` ou `ALB` selon cas — **non tranché**) |
| **Ambiguïtés** | Sert uniquement à documenter **A1** ; ne pas mélanger `ASL` et `ALB` dans le même calcul sans le dire. |

---

## 5. Matrice landmark × mesure

| Landmark | VCE | Tönnis | CCD |
|----------|-----|--------|-----|
| `TD_R` / `TD_L` | Oui (réf.) | Oui (réf.) | Non |
| `FHC_R` / `FHC_L` | Oui | Non | Oui |
| `ASL_R` / `ASL_L` | Oui | Oui | Non |
| `ASM_R` / `ASM_L` | Non | Oui | Non |
| `FNM_R` / `FNM_L` | Non | Non | Oui |
| `FSP_R` / `FSP_L` | Non | Non | Oui |
| `FSD_R` / `FSD_L` | Non | Non | Oui |
| `ALB_R` / `ALB_L` | Optionnel | Non | Non |

---

## 6. Réutilisation Dataset 1 — synthèse

| Dataset 1 | Nom MTDDH | Réutilisable pour MVP adulte ? |
|-----------|-----------|--------------------------------|
| `re` / `le` | RASM / LASM | **Partiel** → inspirer `ASL` (redéfinir) |
| `ry` / `ly` | RTCC / LTCC | **Non** (pédiatrique Hilgenreiner) |
| `rc` / `lc` | RFHC / LFHC | **Partiel** → inspirer `FHC` (redéfinir) |
| `rh` / `lh` | RMOFM / LMOFM | **Non** pour CCD / VCE / Tönnis adulte |
| Régions apple/bus/cow/dog | RI / LI / ROF / LOF | **QC seulement**, pas landmarks de mesure MVP |

**Aucun landmark Dataset 1 n’est transférable tel quel** vers un dataset adulte sans redéfinition anatomique et re-annotation.

### Nouveaux landmarks obligatoires à créer

`TD_R`, `TD_L`, `ASM_R`, `ASM_L`, `FNM_R`, `FNM_L`, `FSP_R`, `FSP_L`, `FSD_R`, `FSD_L`  
+ redéfinition adulte de `FHC_*` et `ASL_*`.

### Optionnels

`ALB_R`, `ALB_L`.

---

## 7. Vérification de cohérence géométrique

| Mesure | Construction | Landmarks suffisants ? | Statut |
|--------|--------------|------------------------|--------|
| **VCE** | ∠( ⟂`ITH` en `FHC` , `FHC→ASL` ) | `TD×2` + `FHC` + `ASL` | **Cohérent** |
| **Tönnis** | ∠( ∥`ITH` en `ASM` , `ASM→ASL` ) | `TD×2` + `ASM` + `ASL` | **Cohérent** |
| **CCD** | ∠( `FHC→FNM` , `FSP→FSD` ) | `FHC` + `FNM` + `FSP` + `FSD` | **Cohérent** |

### Partages voulus (pas de conflit)

- `ASL` sert **à la fois** VCE (sourcil) et Tönnis → une seule annotation latérale du sourcil.
- `FHC` sert VCE et CCD → une seule annotation de centre de tête.
- `TD_R`/`TD_L` partagés VCE + Tönnis → une seule horizontale pelvienne.

### Indépendances

- Le CCD **ne dépend pas** des teardrops ni du sourcil.
- Le Tönnis standard **ne dépend pas** de `FHC`.

### Risques géométriques (non bloquants mais à gérer)

1. Si `ASL` = `ASM` (sourcil trop court / mal vu) → Tönnis indéterminé.  
2. Si `FNM` colinéaire mal conditionné avec `FHC` (col très court) → CCD bruité.  
3. Si `FSP≈FSD` (FOV court) → CCD bruité.  
4. Inclinaison pelvienne forte : VCE/Tönnis biaisés même avec landmarks « justes » — problème d’**acquisition**, pas de schéma.

---

## 8. Ambiguïtés explicites (ne pas inventer une « vérité » unique)

| Code | Sujet | Ce qui est ambigu dans la littérature / la pratique | Décision MVP (provisoire) |
|------|-------|-----------------------------------------------------|---------------------------|
| **A1** | Point latéral du VCE | Sourcil latéral vs bord osseux le plus latéral | MVP calcule VCE sur **`ASL`** ; `ALB` optionnel pour l’autre méthode |
| **A2** | Horizontal pelvien | Teardrops vs ischions vs droite des `FHC` | MVP = **teardrops** `TD_*` |
| **A3** | `ASM` peu visible | Variante « modified Tönnis » | **Hors MVP de base** ; `v=0` si non visible |
| **A4** | Signe / intervalle normal Tönnis | Seuils rapportés varient (ex. 0–10° vs −10–+10° selon sources) | Spécifier le **calcul d’angle** ; les seuils cliniques seront figés plus tard avec le référent médical |
| **A5** | Définition de `FHC` | Cercle best-fit vs estimation visuelle ; têtes déformées | Best-fit ; sinon `v=0` |
| **A6** | Axe du col | 1 point milieu + tête vs 2 milieux de largeur du col | MVP = **`FHC`–`FNM`** |
| **A7** | Niveaux diaphysaires | Hauteur exacte de `FSP`/`FSD` non universellement normalisée | Définitions §4 + règle de distance minimale à valider |
| **A8** | CCD sur AP bassin seul | Rotation fémorale modifie l’angle | Exiger un protocole de pose ; signaler CCD comme **estimation 2D** |

Aucune de ces ambiguïtés n’est « résolue » par invention : elles sont **documentées** pour le guide d’annotation et la revue clinique.

---

## 9. Schéma d’annotation recommandé (futur dataset)

Format cible suggéré (hors scope conversion actuelle) : COCO Pose ou YOLO Pose, **une instance `hip` par côté** (2 instances / image) **ou** une instance bilatérale à 14 keypoints — à trancher à l’implémentation.

Ordre keypoints proposé (instance bilatérale unique) :

```
0 TD_R, 1 TD_L,
2 FHC_R, 3 ASL_R, 4 ASM_R, 5 FNM_R, 6 FSP_R, 7 FSD_R,
8 FHC_L, 9 ASL_L, 10 ASM_L, 11 FNM_L, 12 FSP_L, 13 FSD_L
```

Optionnel en append : `14 ALB_R`, `15 ALB_L`.

Visibilité COCO : `0` absent / non fiable · `1` estimé · `2` net.

---

## 10. Checklist minimale par image annotée (MVP)

Pour déclarer une image **complète MVP** (bilatéral) :

- [ ] `TD_R`, `TD_L` (v>0)  
- [ ] Pour chaque côté : `FHC`, `ASL`, `ASM`, `FNM`, `FSP`, `FSD` (v>0)  
- [ ] → permet VCE + Tönnis + CCD **gauche et droit**

Si un côté est hors champ ou prothésé : annoter l’autre côté ; documenter le côté manquant en `v=0`.

---

## 11. Hors MVP (rappel)

Non couverts par ce schéma (conformément au périmètre demandé) :

- ligne bi-ischiatique (il faudrait `IT_R` / `IT_L`) ;
- offset fémoral (axe diaphysaire + `FHC`, mais calibration mm/px et définition d’offset à figer) ;
- longueur des membres (cliché pleine longueur, genoux, chevilles).

Ils pourront étendre le catalogue (`LM-17+`) sans casser les IDs 01–16.

---

## 12. Conclusion

Le schéma MVP adulte comporte **14 landmarks obligatoires** (+ 2 optionnels `ALB`) et est **géométriquement suffisant et cohérent** pour VCE (sourcil), Tönnis et CCD sur AP bassin.

Par rapport au Dataset 1 : **aucun transfert direct** ; seulement une parenté conceptuelle pour centre de tête et marge latérale. Les ajouts critiques sont les **teardrops**, le **sourcil médial**, et la **chaîne col–diaphyse**.

Prochaine étape naturelle (hors de ce document) : guide d’annotation illustré + revue clinique des ambiguïtés A1–A8 — **sans** entraîner de modèle ni modifier les datasets existants.

---

*Document de spécification uniquement — aucun fichier de données modifié.*
