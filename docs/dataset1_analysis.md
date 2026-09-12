# Analyse du dataset — Dataset1 (MTDDH Dataset 1)

**Date :** 16 juillet 2026  
**Périmètre :** structure, images et annotations uniquement  
**Contraintes respectées :** aucun entraînement, aucune modification d’image/annotation, aucune conversion, aucun modèle créé, aucun fichier de données supprimé  

**Source identifiée :** **MTDDH Dataset 1** — *A dataset for quality evaluation of pelvic X-ray and diagnosis of developmental dysplasia of the hip* (Qi et al., Scientific Data, 2025 ; DOI [10.1038/s41597-025-05146-x](https://doi.org/10.1038/s41597-025-05146-x)).  
Corpus de radiographies pelviennes **pédiatriques** (DDH), **pas** un corpus de coxométrie adulte.

---

## Verdict

| Critère | Résultat |
|---------|----------|
| Images keypoints sur disque | **1 250** JPG (`Train` 780 + `Validation` 260 + `Test` 210) |
| Images régions sur disque | **1 300** JPG (`Train` 780 + `Validation` 260 + `Test` 260) |
| Patients / examens | **1 250** (1 radio / patient selon la publication ; pas d’ID patient dans les fichiers) |
| Format images | **JPEG**, mode **RGB** |
| Annotations keypoints | COCO Pose, **8** points (`re/ry/rc/rh/le/ly/lc/lh`) — JSON **Train + Validation seulement** |
| Images avec les 8 points visibles (`v > 0`) | **987 / 988** annotées (**779** train + **208** val) |
| Annotations régions | LabelMe v5.2.1, **4** polygones/image — **Train + Validation seulement** |
| Split keypoints | **780 / 260 / 210** (annoté : **780 / 208 / 0**) |
| Compatible YOLO Pose **tel quel** | **Non** (conversion COCO → YOLO requise ; Test sans labels) |
| Suffisant pour VCE + Tönnis adulte + CCD + bi-ischiatique + offset + LLD | **Non** |

### Recommandation finale

**3. Dataset nécessitant l’ajout de landmarks** (pour les objectifs de coxométrie adulte du projet).

Compléments : les régions anatomiques sont **très utiles pour le contrôle qualité** (option 4, secondaire) ; une **combinaison avec Dataset2** (option 5) est pertinente pour élargir le corpus de keypoints DDH pédiatriques, pas pour remplacer un schéma de landmarks adulte.

---

## 1. Nombre exact d’images

### Branche Keypoints (référence « 1 250 » de la publication)

| Split | Fichiers `.jpg` sur disque |
|-------|---------------------------|
| `Keypoints/Train` | **780** |
| `Keypoints/Validation` | **260** |
| `Keypoints/Test` | **210** |
| **Total** | **1 250** |

Illisibles / corrompues : **0**.

### Branche Regions

| Split | `.jpg` | `.json` LabelMe |
|-------|--------|-----------------|
| `Regions/Train` | **780** | **780** |
| `Regions/Validation` | **260** | **260** |
| `Regions/Test` | **260** | **0** |
| **Total** | **1 300** | **1 040** |

Les copies `Keypoints/` et `Regions/` des mêmes stems (Train) ont **mêmes dimensions** mais tailles de fichier JPEG différentes (compression distincte) — ce sont des **doublons fonctionnels**, pas 2 550 examens indépendants.

**Stems uniques** (tous splits, Keypoints ∪ Regions) : **1 326**.  
Intersection globale : **1 219** ; uniquement Keypoints : **26** ; uniquement Regions : **81**.

---

## 2. Nombre exact de patients / examens

| Source | Valeur |
|--------|--------|
| Publication MTDDH | **1 250 patients**, **1** radiographie AP par patient |
| Métadonnées locales (COCO / LabelMe) | **Aucun** `patient_id`, âge, sexe ou Study UID |
| Heuristique fichiers | Noms aléatoires (ex. `a308.jpg`, `y44.jpg`, `111qy.jpg`) — **1 stem ≈ 1 examen** |

**Conclusion :** **1 250 examens / patients** pour le corpus keypoints officiel. Les **50** JPG supplémentaires de `Regions/Test` (260 vs 210) et les stems non partagés Val/Test sont des **écarts de curation locale** par rapport au décompte publié, sans métadonnée patient exploitable.

Démographie publiée (Dataset 1) : 781 F / 469 M ; âge moyen **14,57 mois** (médiane 13) — population **nourrissons / jeunes enfants**.

---

## 3. Format des images

| Propriété | Valeur observée |
|-----------|-----------------|
| Extension | `.jpg` |
| Conteneur Pillow | **JPEG** |
| Mode | **RGB** (100 % des 1 250 + 1 300 fichiers lus) |
| DICOM / PNG / TIFF | **Absent** dans Dataset1 |
| Origine | Conversion DICOM → JPEG (décrite dans l’article) |

---

## 4. Dimensions et résolutions

Dimensions **très hétérogènes** (presque une taille par image). Aucun DPI / spacing pixel dans les annotations.

### Keypoints (lecture réelle des pixels)

| Split | N | Couples W×H uniques | Largeur | Hauteur | Ratio W/H |
|-------|---|---------------------|---------|---------|-----------|
| Train | 780 | **758** | 742–2994 | 513–2750 | 1,002–2,767 |
| Validation | 260 | **260** | 742–2800 | 483–2064 | 1,113–2,264 |
| Test | 210 | **205** | 775–2223 | 551–1913 | 1,075–1,723 |

Écart JSON COCO ↔ pixels disque (Train + Val annotés) : **0**.

### Regions

Même gamme pour Train (780 images, 758 tailles uniques, w 742–2994, h 513–2750). Validation : 260 images, 259 tailles uniques.

---

## 5. Format exact des annotations

### A. Keypoints — COCO (export type Deepwise / COCO-like)

Fichiers :

- `Dataset1/Keypoints/Keypoints_Train.json` — **780** images, **780** annotations  
- `Dataset1/Keypoints/Keypoints_Validation.json` — **208** images, **208** annotations  
- **Aucun** `Keypoints_Test.json`

Structure racine : `images`, `categories`, `annotations`.

**Catégorie unique :**

```json
{
  "id": 1,
  "name": "hip",
  "supercategory": "hip",
  "keypoints": ["re", "ry", "rc", "rh", "le", "ly", "lc", "lh"],
  "skeleton": []
}
```

**Annotation** (1 instance `hip` par image) :

- `keypoints` : tableau COCO `[x, y, v] × 8` (longueur **24**)
- `v ∈ {0, 1, 2}` (0 = non marqué, 1 = annoté/occulté ou faible confiance, 2 = visible)
- `num_keypoints`, `bbox` `[x, y, w, h]`, `segmentation` (rectangle 4 sommets, `isbbox: true`)

Chemins d’origine dans le JSON : `/datasets/trainseg/...` et `/datasets/valseg/...` — à remapper vers `Keypoints/Train|Validation/`.

### B. Regions — LabelMe **5.2.1**

Un fichier JSON par image (`<stem>.json` à côté de `<stem>.jpg`).

Champs typiques : `version`, `flags`, `shapes[]`, `imagePath`, `imageHeight`, `imageWidth`.

Chaque `shape` : `label`, `points` (polygone), `shape_type: "polygon"`.

Labels **obfusqués** (non anatomiques dans le fichier) : `apple`, `bus`, `cow`, `dog`.

---

## 6. Nombre exact de points anatomiques

| Niveau | Nombre |
|--------|--------|
| Noms de landmarks déclarés | **8** |
| Points par image (schéma) | **8** (4 par hanche × 2) |
| Instances objet `hip` / image annotée | **1** (les 8 points dans une seule liste) |

---

## 7. Noms, IDs et coordonnées des 8 points

| ID (0-based) | Nom COCO local | Côté (image) | Exemple `a308.jpg` (1675×1001) |
|--------------|----------------|--------------|--------------------------------|
| 0 | `re` | droite patient (gauche image) | (422, 438), v=2 |
| 1 | `ry` | droite patient | (558, 503), v=2 |
| 2 | `rc` | droite patient | (455, 534), v=2 |
| 3 | `rh` | droite patient | (439, 584), v=2 |
| 4 | `le` | gauche patient (droite image) | (1175, 491), v=2 |
| 5 | `ly` | gauche patient | (1042, 537), v=2 |
| 6 | `lc` | gauche patient | (1138, 579), v=2 |
| 7 | `lh` | gauche patient | (1135, 633), v=2 |

Convention radiographique AP respectée : points `r*` à gauche de l’image, `l*` à droite.

---

## 8. Signification anatomique exacte de chaque point

Mapping local → nomenclature officielle MTDDH (article) :

| Nom local | Équivalent MTDDH | Signification anatomique |
|-----------|------------------|--------------------------|
| **re** | **RASM** | Marge **superolatérale de l’acétabulum droit** |
| **ry** | **RTCC** | Centre du **cartilage triradié droit** (point de Hilgenreiner côté droit) |
| **rc** | **RFHC** | **Centre de la tête fémorale droite** (noyau d’ossification) |
| **rh** | **RMOFM** | **Milieu du bord supérieur de la métaphyse fémorale** ossifiée proximale **droite** (point H / IHDI) |
| **le** | **LASM** | Marge **superolatérale de l’acétabulum gauche** |
| **ly** | **LTCC** | Centre du **cartilage triradié gauche** |
| **lc** | **LFHC** | **Centre de la tête fémorale gauche** |
| **lh** | **LMOFM** | **Milieu du bord supérieur de la métaphyse fémorale** ossifiée proximale **gauche** |

Ces 8 points sont conçus pour les classifications **IHDI** et **Tönnis pédiatrique** (grades), et pour l’**index acétabulaire** (Hilgenreiner), **pas** pour la coxométrie adulte standard.

Cohérence spatiale observée : `e` plus latéral/supérieur, `y` plus médial, `c` tête, `h` plus distal (métaphyse).

---

## 9. Images possédant les 8 points complets

Critère : les 8 slots avec **visibilité `v > 0`**.

| Split | Images annotées | 8 points complets | Détail |
|-------|-----------------|-------------------|--------|
| Train | 780 | **779** | 1 incomplète |
| Validation | 208 | **208** | 100 % des annotées |
| Test | 0 (pas de JSON) | **0** | — |
| **Total** | **988** | **987** | **99,9 %** des images annotées |

Cas incomplet : `y44.jpg` (train) — `lc` et `lh` à `v=0`, `num_keypoints=6`.

Visibilité `v=2` stricte (tous parfaitement visibles) : Train **732 / 780**, Val **151 / 208**.  
Les `v=1` concernent surtout `rc` / `lc` (têtes fémorales), cohérent avec une ossification partielle.

---

## 10. Images sans annotations ou annotations invalides

### Keypoints

| Problème | Quantité | Détail |
|----------|----------|--------|
| Images Test sans JSON | **210** | Attendu par la publication (labels test non fournis) |
| Images Validation sur disque **sans** entrée JSON | **52** | Liste : `11ebyy.jpg`, `12ex.jpg`, …, `b8.jpg` (voir analyse brute) |
| Annotation incomplète (`num_keypoints ≠ 8`) | **1** | `y44.jpg` |
| Points hors cadre | **0** | — |
| Images JSON sans fichier disque | **0** | — |
| Fichiers illisibles | **0** | — |

### Regions

| Problème | Quantité | Détail |
|----------|----------|--------|
| Test sans JSON | **260** | Attendu (« Test subset omitted » pour les régions) |
| JPG sans JSON (Train/Val) | **0** | — |
| JSON vides | **0** | — |
| Anomalies de labels | **2** | `a311.json` : 2× `apple` ; `h27.json` : 2× `dog` (manque `apple`) |

---

## 11. Annotations de régions anatomiques et signification

### Labels fichier → anatomie (inférés par centroïdes + article)

| Label LabelMe | Position moyenne (cx, cy normalisés) | Aire bbox relative | Anatomie MTDDH |
|---------------|--------------------------------------|--------------------|----------------|
| **apple** | gauche image, haut (0,32 ; 0,35) | grande (~0,070) | **RI** — ilium droit |
| **bus** | droite image, haut (0,67 ; 0,34) | grande (~0,070) | **LI** — ilium gauche |
| **cow** | gauche-centre, bas (0,41 ; 0,66) | petite (~0,005) | **ROF** — foramen obturé droit |
| **dog** | droite-centre, bas (0,59 ; 0,66) | petite (~0,005) | **LOF** — foramen obturé gauche |

Presque toutes les images Train/Val ont **exactement 4** polygones (1 de chaque label).  
Train : 779×4 régions + 1 fichier à 5 shapes ; Val : 260×4.

### Usage clinique prévu (article)

Indices de **symétrie** pour juger si la radio AP est « standard » :

- indices de rotation des foramens obturés et des iliums ;
- ratios d’aires bilatéraux ;

avec seuils publiés (ex. ORI ≈ 0,78–1,42 ; ratios d’aires obturés ≈ 0,77–1,46 ; iliums ≈ 0,71–1,22).

---

## 12. Répartition train / validation / test

### Keypoints (images sur disque)

| Split | Images | Annotations keypoints |
|-------|--------|----------------------|
| Train | **780** (62,4 %) | **780** |
| Validation | **260** (20,8 %) | **208** (80 % du split disque) |
| Test | **210** (16,8 %) | **0** |
| **Total** | **1 250** | **988** |

Conforme au Table 1 de l’article (780 / 260 / 210), sauf que **52** images Validation locales n’ont pas d’entrée dans `Keypoints_Validation.json`.

### Regions

| Split | Images | Annotations |
|-------|--------|-------------|
| Train | **780** | **780** |
| Validation | **260** | **260** |
| Test | **260** | **0** |

Chevauchement stems Keypoints ↔ Regions : Train **100 %** ; Validation **245 / 260** ; Test **194** (intersection partielle, noms parfois proches mais non identiques, ex. `117qy` vs `117qu`).

---

## 13. Compatibilité YOLO Pose / autres architectures

| Critère | Évaluation |
|---------|------------|
| Schéma pose (1 objet, K keypoints) | **Oui** — classe `hip`, **K=8** |
| Visibilité COCO | Déjà présente → mappable YOLO |
| `bbox` | Présente |
| Format YOLO `.txt` natif | **Non** — conversion COCO → YOLO Pose nécessaire |
| Labels Test | **Absents** — test officiel non supervisé localement |
| Val incomplet | 52 images sans labels keypoints |
| Regions | Adaptées à **YOLO-Seg** / Mask R-CNN **après** conversion LabelMe + remap `apple/bus/cow/dog` → noms anatomiques |
| Alternative | HRNet / DEKR / ViTPose sur COCO Pose ; segmentation U-Net pour QC |

**Conclusion :** **compatible après conversion**, pas utilisable « out of the box » pour un entraînement YOLO Pose.

---

## 14. Compatibilité des 8 points avec les mesures coxométriques cibles

| Mesure | Verdict | Justification |
|--------|---------|---------------|
| **Angle VCE / Wiberg** | **Partiellement calculable** | `rc/lc` (centre tête) + `re/le` (bord latéral acétabulaire) + verticale image. Équivalent *CE / Wiberg pédiatrique* possible ; **pas** le VCE adulte garanti (pas de sourcil médial, pas de référence pelvienne horizontale dédiée, population infantile). |
| **Angle de Tönnis (adulte)** | **Impossible avec les 8 points** | Le Tönnis adulte exige bords **médial et latéral du sourcil** + horizontale. Ici : pas de point médial du sourcil. L’**index acétabulaire** pédiatrique (`ry/ly` + `re/le`) et le **grade** Tönnis pédiatrique sont autre chose. |
| **Angle CCD** | **Impossible avec les 8 points** | Manquent axe du col et axe diaphysaire (≥ 2 points chacun). `c` + `h` insuffisants. |
| **Ligne bi-ischiatique** | **Impossible avec les 8 points** | Aucun landmark sur les tubérosités ischiatiques. Les régions = iliums + obturés, **pas** ischions. |
| **Offset fémoral** | **Impossible avec les 8 points** | Requiert centre de tête + axe diaphysaire long. |
| **Longueur des membres inférieurs** | **Impossible avec les 8 points** | Radios bassin localisées ; pas de genoux / chevilles / mensurations pleine longueur. |

### Synthèse clinique projet

Dataset1 = **DDH pédiatrique + QC radio**.  
Pour le MVP coxométrie adulte (VCE strict, Tönnis adulte, CCD, bi-ischiatique, offset, LLD) : les 8 points sont **insuffisants** ; il faut un **schéma de landmarks adulte** (ou un autre corpus).

---

## 15. Utilité des annotations de régions pour le contrôle qualité

| Objectif | Utilisable ? | Commentaire |
|----------|--------------|-------------|
| Filtrer les radios de mauvaise qualité | **Oui** | Cas d’usage principal MTDDH : symétrie obturés / iliums → indices de rotation et ratios d’aires |
| Vérifier la présence du bassin | **Oui** | Détection des 4 ROI ; absence / détection partielle ⇒ radio non exploitable |
| Contrôler le cadrage | **Oui (partiel)** | Présence et position relative des 4 régions ; ne mesure pas explicitement le champ FOV hors bassin |
| Détecter les images inexploitables | **Oui** | Hors seuils de symétrie publiés, ou régions manquantes / aberrantes |

Les labels `apple/bus/cow/dog` doivent être **renommés** avant toute exploitation métier.

---

## Structure des dossiers

```
Dataset1/
├── Keypoints/
│   ├── Keypoints_Train.json          # 780 images / 780 anns
│   ├── Keypoints_Validation.json     # 208 images / 208 anns
│   ├── Train/     *.jpg              # 780
│   ├── Validation/*.jpg              # 260 (dont 52 sans JSON)
│   └── Test/      *.jpg              # 210 (sans JSON)
└── Regions/
    ├── Train/     *.jpg + *.json     # 780 + 780
    ├── Validation/*.jpg + *.json     # 260 + 260
    └── Test/      *.jpg              # 260 (sans JSON)
```

---

## Points d’attention

1. Population **pédiatrique** (~15 mois) — transfert vers coxométrie adulte non trivial.  
2. **Test keypoints sans labels** ; **52** val keypoints sans annotation JSON.  
3. Labels régions **codés** (`apple`/`bus`/`cow`/`dog`) — documentation de mapping obligatoire.  
4. Doublons Keypoints/Regions : même stem, même taille, JPEG différent.  
5. `y44.jpg` : 6/8 points seulement.  
6. 2 fichiers régions avec labels dupliqués / incomplets (`a311`, `h27`).

---

## Recommandation claire

| # | Option | Choix |
|---|--------|-------|
| 1 | Dataset directement utilisable pour le projet | Non |
| 2 | Dataset utilisable après conversion | Oui pour YOLO Pose / Seg **DDH + QC**, insuffisant pour le cahier des charges coxométrie adulte |
| 3 | **Dataset nécessitant l’ajout de landmarks** | **Recommandation principale** |
| 4 | Dataset utile uniquement pour le contrôle qualité | Non exclusif (keypoints DDH présents), mais **forte valeur QC** via les 4 régions |
| 5 | Combinaison recommandée avec un autre dataset | **Oui en complément** : Dataset1 (QC + keypoints) + Dataset2 (keypoints COCO DDH) pour un pipeline DDH ; **ne remplace pas** un dataset / schéma adulte |

**Décision retenue : 3 — Dataset nécessitant l’ajout de landmarks.**

Pour VCE adulte, Tönnis adulte, CCD, ligne bi-ischiatique, offset fémoral et longueur des membres, il faut définir et annoter (ou acquérir) des landmarks supplémentaires.  
Conserver Dataset1 pour : (a) **préfiltre qualité** des radios bassin, (b) baseline / prétraining keypoints DDH après conversion, (c) combinaison éventuelle avec Dataset2.

---

*Analyse en lecture seule — seul fichier créé : `docs/dataset1_analysis.md`. Aucune donnée du dataset modifiée.*
