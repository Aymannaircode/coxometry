# Guide d’annotation — 14 landmarks MVP (coxométrie adulte)

**Date :** 17 juillet 2026  
**Source :** `docs/landmark_specification.md`  
**Périmètre :** annotation manuelle sur radiographie **AP du bassin** adulte  
**Landmarks couverts :** les **14 obligatoires** uniquement (`TD`, `FHC`, `ASL`, `ASM`, `FNM`, `FSP`, `FSD` × 2 côtés)  
**Contraintes :** aucun dataset modifié · aucun entraînement · aucun modèle créé  

---

## 1. Règles générales (lire avant d’annoter)

### 1.1 Orientation image

| Règle | Détail |
|-------|--------|
| Vue | Radiographie **AP bassin** |
| Droite patient | À **gauche** de l’image |
| Gauche patient | À **droite** de l’image |
| Labels `*_R` | Toujours côté **droit patient** (gauche image) |
| Labels `*_L` | Toujours côté **gauche patient** (droite image) |

**Ne jamais** inverser R/L selon « gauche/droite de l’écran » sans vérifier le côté patient.

### 1.2 Codes de visibilité (obligatoires)

| Code `v` | Signification | Quand l’utiliser |
|----------|---------------|------------------|
| **2** | Point **net**, localisable sans doute raisonnable | Structure clairement visible |
| **1** | Point **estimé** : structure présente mais contours flous ; placement approximatif | Uniquement si un clinicien a validé l’usage de `v=1` pour ce landmark — **par défaut, préférer `v=0`** |
| **0** | Point **non annoté** / non fiable / hors champ / inventable seulement | Toujours si vous devez « deviner » |

**Règle d’or :** ne jamais placer un point « pour remplir le schéma ». Si vous ne le voyez pas, `v=0`.

### 1.3 Ordre d’annotation recommandé

1. `TD_R` puis `TD_L` (référence horizontale)  
2. Pour le côté droit : `FHC_R` → `ASL_R` → `ASM_R` → `FNM_R` → `FSP_R` → `FSD_R`  
3. Idem côté gauche : `FHC_L` … `FSD_L`  
4. Contrôles de cohérence bilatérale (§3)  
5. Checklist qualité (§4)

### 1.4 Ce qui n’est jamais un landmark MVP

- Tubérosités ischiatiques (sauf futur schéma hors MVP)  
- Centre du foramen obturé  
- Grand / petit trochanter (comme point nommé) — utiles seulement comme **repères** pour placer `FNM` / `FSP`  
- Ostéophyte rim latéral pour `ASL` (voir §2.3 et ambiguïté A1)  
- Cartilage triradié / points pédiatriques Dataset 1 (`ry`/`ly`, `rh`/`lh`)

---

## 2. Fiches d’annotation par landmark

---

### 2.1 `TD_R` / `TD_L` — Teardrop inférieur (LM-01 / LM-02)

#### 1. Structure anatomique exacte

Figure en **larme acétabulaire** (teardrop) : projection radiographique de la paroi médiale de l’acétabulum.

#### 2. Position exacte du point

Le point le plus **inférieur** (le plus bas) de la larme, au sommet inférieur de la densification en « U » / « V » du teardrop.

#### 3. Comment le repérer

1. Zoomer sur la région médiale du cotyle, entre tête fémorale et ligne ilio-ischiatique.  
2. Identifier la densification en larme bilatérale.  
3. Placer le point sur l’**extrémité inférieure** de cette densification, pas au milieu de la larme.  
4. Répéter de l’autre côté.

#### 4. Ce qu’il ne faut PAS annoter

- Le centre de la larme  
- Un point sur la ligne ilio-ischiatique seule  
- Les tubérosités ischiatiques  
- Le bas de la symphyse pubienne  
- Un teardrop « inventé » si la larme n’est pas visible

#### 5. Si mal visible

→ `v=0`.  
Ne pas substituer silencieusement les ischions ou les centres de tête.

**Ambiguïté A2 (référence horizontale) :** d’autres protocoles utilisent ischions ou droite des `FHC`. Le MVP **impose les teardrops**.  
**Validation radiologue / orthopédiste requise** si, sur un lot d’images, les teardrops sont systématiquement illisibles et qu’une référence de secours doit être définie.

#### 6. Cas difficiles

| Situation | Conduite |
|-----------|----------|
| Rotation / inclinaison pelvienne forte | Annoter le teardrop **tel qu’il apparaît** ; noter la mauvaise qualité cliché en métadonnée QC |
| Teardrop unilatéral effacé (chirurgie, dysplasie sévère) | `v=0` de ce côté ; l’autre côté seul ne suffit **pas** à construire `ITH` → VCE/Tönnis bilatéraux incomplets |
| Double contour | Choisir le contour **le plus inférieur net** ; si doute, `v=0` |

#### 7. Cohérence gauche / droite

- Les deux teardrops doivent être à des hauteurs **proches** sur un cliché peu incliné.  
- Écart vertical très important → suspecter inversion R/L ou mauvaise identification.  
- `TD_R` toujours à gauche de l’image, `TD_L` à droite.

#### 8. Règle de qualité

`TD_R` et `TD_L` tous deux en `v=2` (ou politique clinique validée pour `v=1`), et la droite qui les joint ne traverse pas de façon absurde hors du bassin (contrôle visuel).

---

### 2.2 `FHC_R` / `FHC_L` — Centre de la tête fémorale (LM-03 / LM-04)

#### 1. Structure anatomique exacte

Tête fémorale osseuse adulte sur l’AP.

#### 2. Position exacte du point

**Centre du cercle de meilleure approximation** (best-fit / Mose) de la tête.

#### 3. Comment le repérer

1. Ajuster le contraste pour voir le contour céphalique.  
2. Mentalement (ou avec outil cercle si disponible) ajuster un cercle sur le pourtour osseux de la tête.  
3. Placer `FHC` au **centre** de ce cercle.  
4. Vérifier que le cercle épouse la majeure partie du contour, pas seulement un ostéophyte.

#### 4. Ce qu’il ne faut PAS annoter

- Le centre du cotyle  
- Le « milieu » approximatif sans tenter le cercle  
- Un noyau d’ossification pédiatrique (hors population MVP)  
- Le centre d’une prothèse / tête métallique sans protocole spécifique (hors MVP standard → `v=0` si non applicable)

#### 5. Si mal visible

Contour < ~180° utilisable, ou tête franchement asphérique sans portion circulaire fiable → `v=0`.  
**Ne pas inventer** un centre « au milieu de la zone grise ».

#### 6. Cas difficiles

| Situation | Conduite |
|-----------|----------|
| Ostéophytes périphériques | Ajuster le cercle sur la tête **sous** les ostéophytes |
| Nécrose, coxa plana, collapsus | Si best-fit impossible → `v=0` |
| Subluxation / luxation | Annoter le centre de la **tête** (où elle est), pas le centre du cotyle |
| Superposition pubis / ischion | Zoomer ; si contour douteux → `v=0` |

**Ambiguïté A5 :** best-fit vs estimation visuelle. Le guide impose le **best-fit**.  
Toute autre méthode (barycentre manuel sans cercle) nécessite **validation radiologue / orthopédiste**.

#### 7. Cohérence gauche / droite

- Diamètres apparents des deux têtes proches sur un cliché standard.  
- Les deux `FHC` approximativement à la même hauteur si bassin peu incliné.  
- `FHC_R` à gauche de l’image.

#### 8. Règle de qualité

Un cercle mental/outil centré sur `FHC` doit coller au contour céphalique sur **au moins une demi-circonférence** visible ; sinon `v=0`.

---

### 2.3 `ASL_R` / `ASL_L` — Extrémité latérale du sourcil (LM-05 / LM-06)

#### 1. Structure anatomique exacte

**Sourcil acétabulaire** : bande sclérotique du toit porteur (weight-bearing zone).

#### 2. Position exacte du point

Point le plus **latéral** de cette bande sclérotique.

#### 3. Comment le repérer

1. Suivre le toit acétabulaire de médial vers latéral.  
2. Identifier la densification horizontale / arquée du sourcil.  
3. Placer le point à l’endroit où cette densification **se termine latéralement**.  
4. Si un éperon / rim osseux continue plus latéralement **en dehors** du sourcil dense → **ne pas** le prendre pour `ASL` (voir A1).

#### 4. Ce qu’il ne faut PAS annoter

- L’ostéophyte rim le plus latéral (**ce n’est pas `ASL`** ; ce serait `ALB`, optionnel hors de ce guide)  
- Le bord latéral du labrum (non osseux, non visible comme os)  
- Un point « au hasard » sur le toit sans suivre le sourcil  
- Le point médial du sourcil (`ASM`)

#### 5. Si mal visible

Sourcil non identifiable (arthrose destructive, sous-exposition, chirurgie) → `v=0`.

#### 6. Cas difficiles — Ambiguïté A1 (sourcil vs bord osseux)

| Observation | Conduite MVP |
|-------------|--------------|
| Sourcil et bord osseux **coïncident** | Un seul point = `ASL` |
| Éperon / rim **plus latéral** que le sourcil | `ASL` = fin du **sourcil** uniquement |
| Impossible de distinguer sourcil et rim | `v=0` pour `ASL` — **ne pas choisir au hasard** |

**Validation radiologue / orthopédiste requise** pour :
- former les annotateurs sur des cas « sourcil ≠ rim » ;
- décider si le projet annotera aussi `ALB` (hors guide des 14 points).

#### 7. Cohérence gauche / droite

- `ASL_R` plus latéral (vers le bord gauche image) que `ASM_R` et que `FHC_R` en couverture normale.  
- Symétrie approximative des hauteurs `ASL_R` / `ASL_L` si bassin peu incliné.

#### 8. Règle de qualité

`ASL` doit se situer sur une zone **plus dense** (sclérose) que l’os adjacent ; s’il est placé sur un éperon clairement hors sourcil → **rejeter** et corriger.

---

### 2.4 `ASM_R` / `ASM_L` — Extrémité médiale du sourcil (LM-07 / LM-08)

#### 1. Structure anatomique exacte

Début **médial** de la zone sclérotique du toit porteur (sourcil).

#### 2. Position exacte du point

Point le plus **médial** où la densification du sourcil commence de façon nette.

#### 3. Comment le repérer

1. Partir du bord latéral du sourcil (`ASL`) et remonter vers le médial le long du toit.  
2. Repérer où la bande sclérotique **débute** (transition densité).  
3. Placer `ASM` à cette transition médiale.

#### 4. Ce qu’il ne faut PAS annoter

- Le teardrop (`TD`)  
- Le fond du cotyle / « U » acétabulaire profond  
- Un point médial inventé « au-dessus de la tête »  
- La variante « modified Tönnis » (autre construction) — **hors MVP**

#### 5. Si mal visible — Ambiguïté A3

Le bord médial est souvent le point le **plus difficile**.

| Situation | Conduite |
|-----------|----------|
| Transition densité identifiable | `v=2` |
| Transition douteuse | **`v=0`** (pas d’estimation improvisée) |
| Tentation d’utiliser une méthode alternative (modified Tönnis) | **Interdit** dans ce guide tant qu’un clinicien n’a pas validé un protocole écrit |

**Validation radiologue / orthopédiste requise** avant d’autoriser `v=1` sur `ASM` ou toute méthode de substitution.

#### 6. Cas difficiles

| Situation | Conduite |
|-----------|----------|
| Sourcil très court | `ASM` et `ASL` proches mais distincts ; s’ils fusionnent visuellement → `v=0` pour l’un ou les deux |
| Toit « en marche d’escalier » | Suivre la **bande sclérotique principale** porteuse ; si plusieurs bandes → `v=0` + revue clinique |
| Coxa profunda / protrusio | Anatomie déformée : annoter seulement si le sourcil reste identifiable |

#### 7. Cohérence gauche / droite

- Sur chaque côté : `ASM` **plus médial** que `ASL`.  
- La droite `ASM`–`ASL` doit suivre le toit (pas descendre dans le cotyle).  
- Inversion médial/latéral = erreur bloquante.

#### 8. Règle de qualité

Distance `ASM`–`ASL` > 0 (points non confondus) et segment aligné sur le toit sclérotique ; sinon annotation invalide pour le Tönnis.

---

### 2.5 `FNM_R` / `FNM_L` — Milieu de l’axe du col (LM-09 / LM-10)

#### 1. Structure anatomique exacte

Col fémoral : segment osseux entre tête et massif trochantérien.

#### 2. Position exacte du point

Point sur l’**axe médian du col** (équidistant des corticales supérieure et inférieure), à mi-longueur du col visible (entre jonction tête-col et jonction col-trochanter).

#### 3. Comment le repérer — Ambiguïté A6 (axe du col)

**Méthode MVP imposée :**

1. Avoir déjà placé `FHC`.  
2. Visualiser les corticales supérieure et inférieure du col.  
3. Au milieu de la longueur du col, placer un point **à mi-distance** des deux corticales.  
4. L’axe du col utilisé pour le CCD sera la droite **`FHC` → `FNM`**.

#### 4. Ce qu’il ne faut PAS annoter

- Le grand trochanter  
- Le petit trochanter  
- Un point sur une corticale (supérieure ou inférieure)  
- Un second « centre de tête »  
- Un axe de col **qui ignore** `FHC` (autre protocole)

#### 5. Si mal visible

Col trop court, cam sévère, fracture, matériel, superposition → `v=0`.

#### 6. Cas difficiles

| Situation | Conduite |
|-----------|----------|
| Corticales mal vues | `v=0` |
| Col en forte antéversion / rotation | Placer selon l’apparence 2D ; noter que le CCD 2D peut être biaisé (**A8** — validation clinique du protocole d’acquisition) |
| `FNM` presque confondu avec `FHC` | Col trop court → `v=0` pour `FNM` (CCD non fiable) |

**Validation radiologue / orthopédiste requise** si l’équipe souhaite passer à un protocole à **deux** milieux de largeur de col (sans forcer le passage par `FHC`).

#### 7. Cohérence gauche / droite

- `FNM` entre `FHC` et le massif trochantérien.  
- La droite `FHC`–`FNM` doit rester **dans** le col, pas sortir dans le grand trochanter.

#### 8. Règle de qualité

Segment `FHC`–`FNM` contenu dans le col ; longueur du segment nettement inférieure à la diaphyse visible ; sinon revoir ou `v=0`.

---

### 2.6 `FSP_R` / `FSP_L` — Axe diaphysaire proximal (LM-11 / LM-12)

#### 1. Structure anatomique exacte

Diaphyse fémorale proximale (canal médullaire / axe médian entre corticales).

#### 2. Position exacte du point

Sur l’axe médian, **juste au-dessous du petit trochanter** (ou au premier niveau sous le petit trochanter où les deux corticales diaphysaires sont clairement parallèles et mesurables).

#### 3. Comment le repérer — Ambiguïté A7 (axe diaphysaire)

1. Identifier le petit trochanter.  
2. Descendre immédiatement sous son niveau.  
3. Placer le point à mi-distance des corticales **médiale** et **latérale** de la diaphyse.

#### 4. Ce qu’il ne faut PAS annoter

- Le centre du petit trochanter lui-même  
- Un point dans le massif trochantérien  
- Un point sur une seule corticale  
- Le même emplacement que `FSD`

#### 5. Si mal visible

Petit trochanter non vu, diaphyse coupée trop haut, matériel → `v=0`.

#### 6. Cas difficiles

| Situation | Conduite |
|-----------|----------|
| Petit trochanter ambigu (rotation) | Utiliser le niveau où les corticales deviennent parallèles sous le massif proximal ; si doute → `v=0` |
| Niveau exact contesté entre annotateurs | **Ne pas improvisir** une « moyenne » d’équipe sans règle écrite |

**Validation radiologue / orthopédiste requise** pour figer, sur un set d’exemples illustrés, le niveau exact « sous petit trochanter » accepté par le projet.

#### 7. Cohérence gauche / droite

- `FSP` sous le petit trochanter **homolatéral**.  
- Hauteurs `FSP_R` / `FSP_L` proches si cadrage symétrique.

#### 8. Règle de qualité

`FSP` clairement **distal** au col et au petit trochanter ; corticales visibles de part et d’autre.

---

### 2.7 `FSD_R` / `FSD_L` — Axe diaphysaire distal dans le FOV (LM-13 / LM-14)

#### 1. Structure anatomique exacte

Diaphyse fémorale, le plus bas possible dans le champ de la radio.

#### 2. Position exacte du point

Sur l’axe médian (mi-corticales), au point **le plus distal** où les deux corticales restent nettes dans l’image.

#### 3. Comment le repérer

1. Suivre la diaphyse vers le bas depuis `FSP`.  
2. S’arrêter avant le bord de l’image ou avant la perte de contraste.  
3. Placer `FSD` à mi-distance des corticales à ce niveau.

#### 4. Ce qu’il ne faut PAS annoter

- Un point hors de l’os  
- Un point proximal proche de `FSP` « pour faire un axe »  
- Condyle / genou (hors FOV bassin typique)

#### 5. Si mal visible / FOV insuffisant — Ambiguïté A7

| Situation | Conduite |
|-----------|----------|
| Diaphyse longue et nette | `v=2` |
| Diaphyse très courte sous `FSP` | Mesurer la distance `FSP`–`FSD` |
| Distance `FSP`–`FSD` **&lt; 0,5 × diamètre apparent de la tête** homolatérale | → `v=0` pour `FSD` ; **CCD non calculable** pour ce côté |

Cette règle de distance **0,5 × diamètre de tête** est une **convention projet provisoire**.  
**Validation radiologue / orthopédiste requise** avant de la considérer comme seuil définitif.

#### 6. Cas difficiles

| Situation | Conduite |
|-----------|----------|
| Bord d’image coupe le fémur | Annoter le dernier niveau fiable **dans** l’image ; appliquer la règle de distance |
| Corticale d’un seul côté visible | `v=0` |
| Courbure diaphysaire marquée | L’axe `FSP`–`FSD` reste une **corde** 2D ; acceptable pour le MVP si les points sont sur l’axe médian local |

#### 7. Cohérence gauche / droite

- `FSD` toujours **plus distal** que `FSP` du même côté.  
- Les axes `FSP`–`FSD` gauche et droit ne doivent pas se croiser de façon aberrante au milieu du bassin (signe d’inversion de points).

#### 8. Règle de qualité

`FSD` distal à `FSP`, distance ≥ seuil provisoire (ou `v=0`), point centré entre corticales.

---

## 3. Règles de cohérence gauche / droite (globales)

Appliquer **après** l’annotation complète :

| Contrôle | Attendu | Si échec |
|----------|---------|----------|
| Latéralité labels | Tous les `*_R` à gauche de l’image | Corriger inversion |
| Teardrops | `TD_R` et `TD_L` présents pour VCE/Tönnis | Sinon mesures incomplètes |
| Sourcil | Sur chaque côté : `ASM` médial par rapport à `ASL` | Corriger |
| Tête / col | `FNM` entre tête et trochanters | Corriger ou `v=0` |
| Diaphyse | `FSD` plus bas que `FSP` | Corriger ou `v=0` |
| Symétrie grossière | Hauteurs R/L proches si cliché peu incliné | Vérifier mauvaise ID ; sinon noter QC pelvien |
| Pas de copie miroir | Ne pas dupliquer les coordonnées d’un côté vers l’autre | Réannoter |

**Interdiction :** annoter un côté par symétrie miroir de l’autre.

---

## 4. Checklist qualité par image

Une image est **acceptée MVP bilatéral** seulement si :

- [ ] `TD_R`, `TD_L` en `v=2` (sauf dérogation clinique écrite)  
- [ ] Pour **chaque** côté : `FHC`, `ASL`, `ASM`, `FNM`, `FSP`, `FSD` en `v=2`  
- [ ] Aucun point placé « par estimation » non autorisée  
- [ ] Contrôles §3 OK  
- [ ] Sourcil : `ASL` ≠ bord osseux ostéophytique si celui-ci est distinct  
- [ ] Diaphyse : distance `FSP`–`FSD` respectant la règle provisoire, sinon `v=0` + CCD impossible  

### Acceptation partielle

| Cas | Autorisé | Conséquence |
|-----|----------|-------------|
| Un côté prothésé / hors champ | Oui | Annoter le côté sain ; `v=0` sur l’autre |
| `ASM` invisible unilatéral | Oui avec `v=0` | Tönnis impossible ce côté ; VCE/CCD possibles si autres points OK |
| FOV diaphysaire insuffisant | Oui avec `FSD` en `v=0` | CCD impossible ce côté |
| Teardrops invisibles | `v=0` | VCE et Tönnis impossibles (réf. horizontale manquante) |

---

## 5. Traitement explicite des ambiguïtés (rappel opérationnel)

| Code | Ambiguïté | Règle d’annotation MVP | Validation clinique |
|------|-----------|------------------------|---------------------|
| **A1** | Sourcil vs bord osseux | `ASL` = **sourcil latéral uniquement** | Oui — cas rim/ostéophyte |
| **A2** | Référence horizontale | **Teardrops uniquement** ; pas ischions / pas `FHC–FHC` | Oui — si teardrops souvent illisibles |
| **A3** | `ASM` peu visible | `v=0` ; pas de « modified Tönnis » improvisé | Oui — avant d’autoriser une variante |
| **A6** | Axe du col | Toujours `FHC`–`FNM` | Oui — avant protocole à 2 milieux de col |
| **A7** | Axe / FOV diaphyse | `FSP` sous petit trochanter ; `FSD` le plus distal ; seuil distance provisoire | Oui — figer niveau + seuil |
| **A8** | Rotation fémorale / CCD 2D | Annoter l’apparence 2D ; ne pas « corriger » mentalement la rotation | Oui — protocole d’acquisition |

**A4** (seuils cliniques Tönnis) ne change **pas** le placement des points ; elle concerne l’interprétation des angles après calcul.

---

## 6. Erreurs fréquentes à éviter

1. Placer `ASL` sur un ostéophyte rim.  
2. Confondre `ASM` et `TD`.  
3. Estimer `FHC` sans tenter un cercle.  
4. Inverser droite patient / gauche image.  
5. Forcer `FSD` trop près de `FSP` pour « avoir un CCD ».  
6. Remplacer les teardrops par les ischions sans validation.  
7. Annoter des points Dataset 1 pédiatriques (`ry`/`ly`, `rh`/`lh`) sur un cliché adulte.  
8. Mettre `v=2` par confort alors que le point est douteux.

---

## 7. Synthèse : « où cliquer » (14 points)

| ID | Nom | Où cliquer (rappel) |
|----|-----|---------------------|
| LM-01 | `TD_R` | Bas de la larme droite |
| LM-02 | `TD_L` | Bas de la larme gauche |
| LM-03 | `FHC_R` | Centre du cercle tête droite |
| LM-04 | `FHC_L` | Centre du cercle tête gauche |
| LM-05 | `ASL_R` | Fin **latérale du sourcil** droit |
| LM-06 | `ASL_L` | Fin **latérale du sourcil** gauche |
| LM-07 | `ASM_R` | Début **médial du sourcil** droit |
| LM-08 | `ASM_L` | Début **médial du sourcil** gauche |
| LM-09 | `FNM_R` | Milieu du col droit (axe médian) |
| LM-10 | `FNM_L` | Milieu du col gauche |
| LM-11 | `FSP_R` | Axe diaphyse droite sous petit trochanter |
| LM-12 | `FSP_L` | Axe diaphyse gauche sous petit trochanter |
| LM-13 | `FSD_R` | Axe diaphyse droite le plus bas possible |
| LM-14 | `FSD_L` | Axe diaphyse gauche le plus bas possible |

---

## 8. Prochaine étape recommandée (hors scope)

Avant campagne d’annotation à grande échelle :

1. Faire valider ce guide par un **radiologue** et/ou un **orthopédiste**.  
2. Annoter un **set pilote** (ex. 20–30 radios) à double lecture.  
3. Trancher A1–A3–A7 sur exemples réels illustrés.  
4. Ensuite seulement verrouiller le protocole et produire le dataset adulte.

---

*Guide pratique uniquement — aligné sur `docs/landmark_specification.md` — aucun fichier de données modifié.*
