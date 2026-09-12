# Analyse du dataset — Dataset2 (DeepWise-DDH / MTDDH Dataset 2)

**Date :** 16 juillet 2026  
**Périmètre :** structure, images et annotations uniquement  
**Contraintes respectées :** aucun entraînement, aucune modification d’image/annotation, aucune conversion, aucun modèle créé  

**Source identifiée :** dataset **DeepWise-DDH** (métadonnées COCO : `version: DeepWise-DDH`, `year: 2019`, `contributor: gongping@deepwise.com`). Correspond au **Dataset 2** du corpus public MTDDH (radiographies pelviennes **pédiatriques** pour DDH), pas à un corpus de coxométrie adulte.

---

## Verdict

| Critère | Résultat |
|---------|----------|
| Images sur disque | **994** fichiers `img.png` dans **906** dossiers patients |
| Images référencées par les annotations COCO | **908** |
| Annotations COCO totales | **10 796** |
| Dont zones keypoints (`keypoint_area`) | **1 816** (exactement **2 par image** annotée) |
| Points anatomiques nommés par hanche | **4** : `A`, `B`, `C`, `H` → **8 par image** (G+D) |
| Images COCO avec les 8 points visibles | **857 / 908** (94,4 %) |
| Split train / val / test | **731 / 89 / 88** (sans chevauchement patient) |
| Compatible YOLO Pose **tel quel** | **Non** (format COCO ; conversion requise) |
| Suffisant pour VCE + Tönnis adulte + CCD + bi-ischiatique + offset | **Non** |

### Recommandation finale

**Dataset nécessitant l’ajout de landmarks** (pour les objectifs de coxométrie adulte du projet).

Secondairement : le jeu est **utilisable après conversion** pour entraîner un détecteur de pose sur les landmarks DDH pédiatriques existants (`A/B/C/H` bilatéraux), mais cela ne couvre pas le cahier des charges coxométrie adulte.

---

## 1. Nombre total exact d’images

| Niveau | Quantité | Détail |
|--------|----------|--------|
| Dossiers patients (`Dataset2/png/<id>/`) | **906** | Tous non vides |
| Fichiers PNG sur disque (`**/img.png`) | **994** | + 32 `.DS_Store` ignorables |
| Entrées `images` dans les JSON COCO | **908** | train 731 + val 89 + test 88 |
| Patients avec >1 image | **34** (122 images au total dans ces dossiers) | Ex. 2 à 7 clichés / patient |

**Écart disque ↔ COCO :**

- **0** image COCO manquante sur disque
- **86** images présentes sur disque **sans** entrée COCO (extraits de séries multi-clichés non retenus dans le split annoté)
- **1** image COCO **illisible** / corrompue côté disque :  
  `png/6e7f91f1/.../img.png` (référencée dans train, `id=63`, 1068×660 dans le JSON ; Pillow : `cannot identify image file`)

**Lecture pratique :** le chiffre « 906 » du corpus publié correspond aux **patients / cas**. Le split annoté local contient **908** radiographies référencées ; le dossier contient **994** PNG.

---

## 2. Nombre total exact d’annotations

| Split | Images | Annotations (toutes catégories) | Dont os (cat. 1–5) | Dont `keypoint_area` (cat. 6) |
|-------|--------|----------------------------------|--------------------|-------------------------------|
| train | 731 | 8 701 | 7 239 | 1 462 |
| val | 89 | 1 052 | 874 | 178 |
| test | 88 | 1 043 | 867 | 176 |
| **Total** | **908** | **10 796** | **8 980** | **1 816** |

Répartition par catégorie (tous splits) :

| `category_id` | Nom | Nombre |
|---------------|-----|--------|
| 1 | `ilium` | 1 816 |
| 2 | `pubis` | 1 816 |
| 3 | `ischium` | 1 816 |
| 4 | `femoral_head` | 1 716 |
| 5 | `femur` | 1 816 |
| 6 | `keypoint_area` | 1 816 |

Points keypoints visibles (visibilité COCO `v > 0`) : **7 169 / 7 264** slots (908 × 8).

---

## 3. Structure des dossiers

```
Dataset2/
├── coco/
│   ├── ddh_keypoint_train.json
│   ├── ddh_keypoint_val.json
│   └── ddh_keypoint_test.json
└── png/
    └── <patient_hash_8hex>/
        └── <StudyInstanceUID>/
            └── <SeriesInstanceUID>/
                └── <SOPInstanceUID>/
                    └── img.png
```

- Pas de sous-dossiers `train/` / `val/` / `test/` pour les images : le split est **uniquement** dans les JSON.
- Chemins COCO d’origine (Linux) du type :  
  `/data2/ddh/data/c1/b1/png/<patient>/.../img.png`  
  → équivalent local : `Dataset2/png/<patient>/.../img.png`.

---

## 4. Format des images

| Propriété | Valeur observée |
|-----------|-----------------|
| Extension | `.png` (nom fixe `img.png`) |
| Format Pillow | `PNG` |
| Mode | **`L`** (niveaux de gris, 8 bits) pour 993/994 images lisibles |
| Origine | Conversion DICOM → PNG (documentée pour MTDDH Dataset 2) |

---

## 5. Dimensions des images

### Métadonnées COCO (908 images)

| Statistique | Largeur (px) | Hauteur (px) |
|-------------|--------------|--------------|
| Min | 740 | 519 |
| Max | 2 992 | 2 514 |
| Moyenne | 1 325,8 | 977,8 |
| Couples (W×H) uniques | **899** | |

Dimensions très hétérogènes (presque une taille par image).

### Fichiers disque lisibles (993 PNG)

| Statistique | Largeur (px) | Hauteur (px) |
|-------------|--------------|--------------|
| Min | 352 | 480 |
| Max | 3 000 | 3 223 |
| Moyenne | 1 307,5 | 1 010,9 |
| Couples uniques | **984** | |

- **0** écart de dimensions entre JSON et PNG pour les 907 images COCO lisibles.
- Les 86 PNG hors COCO expliquent l’écart min/max disque vs COCO.

---

## 6. Format exact des annotations

Format **COCO** standard, 3 fichiers JSON indépendants.

### Clés racine

`info`, `licenses`, `images`, `categories`, `annotations`

### `images[]`

```json
{
  "file_name": "/data2/ddh/data/c1/b1/png/<...>/img.png",
  "height": 578,
  "width": 783,
  "id": 0
}
```

### `categories[]` (6 classes)

1. `ilium` — segmentation  
2. `pubis` — segmentation  
3. `ischium` — segmentation  
4. `femoral_head` — segmentation  
5. `femur` — segmentation  
6. `keypoint_area` — pose / keypoints :

```json
{
  "supercategory": "bone",
  "id": 6,
  "name": "keypoint_area",
  "keypoints": ["A", "B", "C", "H"],
  "skeleton": [[1, 2], [3, 4]]
}
```

### `annotations[]`

Deux types d’instances :

**A. Os (categories 1–5)** — instance segmentation  

Champs : `id`, `image_id`, `category_id`, `segmentation` (polygone), `area`, `bbox` `[x,y,w,h]`, `iscrowd` (toujours 0).

**B. Keypoints (category 6)** — une instance par hanche  

Champs : `id`, `image_id`, `category_id`, `area`, `bbox`, `keypoints`, `num_keypoints`, `iscrowd`  
**Pas** de `segmentation` sur ces entrées.

`keypoints` au format COCO : `[x1,y1,v1, x2,y2,v2, x3,y3,v3, x4,y4,v4]` (longueur **12**), avec `v ∈ {0,2}` observé ici (`0` = non marqué, `2` = visible).

Exemple (hanche incomplète, point C absent) :

```json
"keypoints": [214.38, 283.1, 2, 257.03, 318.49, 2, 0, 0, 0, 203.49, 378.38, 2],
"num_keypoints": 3
```

---

## 7. Nombre de points par image

| Configuration | Images |
|---------------|--------|
| Exactement **2** instances `keypoint_area` (G et D) | **908 / 908** |
| **8** points visibles (4×2) | **857** |
| **7** points visibles | **7** |
| **6** points visibles | **44** |

Interprétation : **4 noms × 2 hanches = 8 landmarks** par radiographie complète. Les cas à 6–7 points correspondent à l’absence du point `C` (voir §11).

---

## 8. Noms / IDs exacts des 8 points

Noms **exactement** déclarés dans COCO (par instance hanche) :

| Index COCO (1-based skeleton) | ID / label | Ordre dans le tableau `keypoints` |
|-------------------------------|------------|-------------------------------------|
| 1 | **A** | indices 0–2 |
| 2 | **B** | indices 3–5 |
| 3 | **C** | indices 6–8 |
| 4 | **H** | indices 9–11 |

Squelette déclaré : `A—B` et `C—H`.

Les 8 points « globaux » d’une image sont donc, en pratique :

`A_left`, `B_left`, `C_left`, `H_left`, `A_right`, `B_right`, `C_right`, `H_right`  

(le côté n’est **pas** un champ COCO : il se déduit de la position en x du `bbox` / des points, centre image).

Équivalents anatomiques publiés (MTDDH / DeepWise, 8 landmarks bilatéraux) :

`RTCC`, `LTCC`, `RASM`, `LASM`, `RFHC`, `LFHC`, `RMOFM`, `LMOFM`.

---

## 9. Signification anatomique de chaque point

D’après la littérature DeepWise / MTDDH / Frontiers (DDH pédiatrique) et la cohérence des données locales (seul `C` est parfois à `v=0`, typique d’une tête fémorale non ossifiée) :

| Label | Signification anatomique | Équivalent MTDDH (par côté) |
|-------|--------------------------|-----------------------------|
| **A** | Marge **superolatérale de l’acétabulum** (bord supérieur externe du cotyle) | ASM (`RASM` / `LASM`) |
| **B** | Centre du **cartilage triradié** (point de Hilgenreiner côté hanche) | TCC (`RTCC` / `LTCC`) |
| **C** | **Centre de la tête fémorale** (noyau d’ossification) | FHC (`RFHC` / `LFHC`) |
| **H** | **Milieu du bord supérieur de la métaphyse fémorale** ossifiée proximale | MOFM (`RMOFM` / `LMOFM`) |

Population cible du dataset (MTDDH Dataset 2) : âge moyen ≈ **14–15 mois** — landmarks et mesures sont ceux de la **DDH pédiatrique** (ligne de Hilgenreiner, Perkins, index acétabulaire, classifications Tönnis/IHDI), **pas** ceux de la coxométrie adulte standard.

---

## 10. Images sans annotation

| Cas | Nombre |
|-----|--------|
| Images COCO sans aucune annotation | **0** |
| Images COCO sans `keypoint_area` | **0** |
| Images COCO sans annotations osseuses | **0** |
| PNG sur disque **hors** COCO (donc sans annotation) | **86** |

Les 86 PNG non annotés ne doivent pas être utilisés pour l’apprentissage tant qu’ils n’ont pas d’entrée COCO.

---

## 11. Annotations incomplètes ou invalides

### Keypoints

| Problème | Quantité |
|----------|----------|
| Tableaux `keypoints` de longueur ≠ 12 | **0** |
| Points hors cadre image (x,y visibles) | **0** |
| Instances `keypoint_area` avec `num_keypoints = 3` (point manquant) | **95** |
| Point manquant = toujours **`C`** | **95 / 95** |
| Images touchées par au moins un `C` manquant | **51** (train 36, val 8, test 7) |
| `bbox` keypoint avec origine négative (`x<0` ou `y<0`) | **81** |
| `bbox` débordant légèrement du cadre | **162** (keypoints eux-mêmes restent dans l’image) |

### Segmentations osseuses

| Problème | Quantité |
|----------|----------|
| Pattern complet bilatéral `(2,2,2,2,2)` ilium/pubis/ischium/tête/fémur | **854** images |
| Aucune `femoral_head` (0/2) | **46** images |
| Une seule `femoral_head` (1/2) | **8** images |
| Segmentations osseuses vides | **0** |
| `area ≤ 0` | **0** |
| `iscrowd ≠ 0` | **0** |
| IDs d’annotation dupliqués | **0** |

### Fichier image

| Problème | Quantité |
|----------|----------|
| PNG corrompu / illisible (mais listé dans COCO train) | **1** (`6e7f91f1/.../img.png`) |

---

## 12. Répartition train / validation / test

| Split | Images COCO | % | Patients distincts |
|-------|-------------|---|--------------------|
| train | **731** | 80,5 % | 730 |
| val | **89** | 9,8 % | 89 |
| test | **88** | 9,7 % | 87 |
| **Total** | **908** | 100 % | — |

- Chevauchement patients train∩val / train∩test / val∩test : **0** (bon cloisonnement).
- Split **prédéfini** dans les JSON ; pas de dossiers image séparés.
- Légère différence vs table MTDDH publiée (≈ 730 / 88 / 87) : version / curation locale **731 / 89 / 88**.

---

## 13. Compatibilité avec YOLO Pose

| Aspect | Évaluation |
|--------|------------|
| Format natif YOLO (`labels/*.txt`, `data.yaml`) | **Absent** |
| Format actuel | COCO JSON (segmentation + keypoints) |
| Structure pose naturelle | **Oui** : 1 classe objet `keypoint_area` (ou `hip`), **4** keypoints, **2** instances / image |
| Alternative | Fusionner G+D → 1 instance « pelvis » à **8** keypoints (conversion custom) |
| Visibilité | Déjà encodée (COCO `v`) → mappable vers YOLO `v` |
| Chemins `file_name` absolus Linux | À remapper vers chemins locaux Windows |
| Segmentations osseuses | Utiles pour YOLO-Seg / Mask R-CNN, **hors** schéma YOLO Pose pur |

**Conclusion :** **compatible après conversion** COCO → YOLO Pose (et éventuel aplatissement 4×2 → 8 keypoints). **Pas directement utilisable** sans étape de conversion / remapping des chemins / exclusion du PNG corrompu et des 86 images non annotées.

---

## 14. Les 8 points permettent-ils les mesures coxométriques cibles ?

Légende : **Oui** / **Partiel** / **Non**

| Mesure (objectif projet) | Avec les 8 points seuls | Commentaire |
|--------------------------|-------------------------|-------------|
| **VCE / angle de Wiberg** | **Partiel** | Besoin du centre de tête (`C`) + bord latéral acétabulaire (`A`) + verticale. Calculable *au sens CE pédiatrique* quand `C` est présent ; **pas** équivalent garanti au VCE adulte (sourcil, référence horizontale pelvienne). Impossible si `C` manquant (51 images). |
| **Angle de Tönnis (adulte)** | **Non** | Le Tönnis **adulte** exige le bord **médial et latéral du sourcil** + horizontale. Ici : pas de point médial du sourcil. L’**index acétabulaire** pédiatrique (Hilgenreiner `B` + `A`) est autre chose que l’angle de Tönnis adulte. |
| **Angle CCD (caput-collum-diaphyse)** | **Non** | Il manque l’axe du col et l’axe diaphysaire (2+ points fémoraux chacun). Seuls `C` + `H` (tête + métaphyse) sont insuffisants. |
| **Ligne bi-ischiatique** | **Non** (keypoints) | Aucun landmark sur les tubérosités ischiatiques. Les masques `ischium` existent mais **ne fournissent pas** les points de référence bi-ischiatiques annotés. |
| **Offset fémoral** | **Non** | Requiert centre de tête + axe diaphysaire fémoral long ; non couvert. |

### Synthèse clinique pour le projet

Ce dataset est conçu pour la **DDH pédiatrique** (Hilgenreiner, Perkins, index acétabulaire, grades Tönnis/IHDI).  
Il **ne constitue pas** un jeu de landmarks de coxométrie adulte (VCE strict, Tönnis adulte, CCD, bi-ischiatique, offset).

---

## Synthèse exécutive

1. **Corpus solide et cohérent** pour de la détection de keypoints DDH : 908 radios annotées, 8 points/image (dont 857 complètes), split propre, segmentations osseuses riches.  
2. **Pas prêt « out of the box » pour YOLO Pose** : conversion COCO → YOLO + remap des chemins nécessaires.  
3. **Pas aligné sur la coxométrie adulte** : population pédiatrique, labels `A/B/C/H` DDH, mesures cibles du projet majoritairement **non calculables**.  
4. Points d’attention qualité : 95 absences de `C`, 46 images sans tête fémorale segmentée, 86 PNG non annotés, 1 PNG corrompu.

---

## Recommandation claire

> **Dataset nécessitant l’ajout de landmarks.**

Pour atteindre VCE/Wiberg adulte, angle de Tönnis adulte, CCD, ligne bi-ischiatique et offset fémoral, il faut **définir et annoter un schéma de landmarks adulte** (ou un corpus adulte dédié).  
La conversion de Dataset2 vers YOLO Pose reste pertinente seulement comme **baseline / transfert** sur des points DDH, pas comme solution directe au cahier des charges coxométrie adulte.

---

*Analyse en lecture seule — aucun fichier du dataset modifié.*
