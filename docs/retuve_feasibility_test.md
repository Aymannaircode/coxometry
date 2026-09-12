# Rapport de test Retuve — Installation et inférence

**Date :** 16 juillet 2026  
**Statut global :** **PARTIEL** — installation OK, inférence YOLO réelle OK, pipeline Retuve (`analyse_hip_xray_2D`) **échoué**

---

## 1. Environnement

### 1.1 Python

| Vérification | Résultat |
|--------------|----------|
| `py -3.11 --version` | **Python 3.11.9** |
| Interpréteur système | `C:\Users\g\AppData\Local\Programs\Python\Python311\python.exe` |
| Environnement virtuel | `.venv` créé avec `py -3.11 -m venv .venv` |
| Python dans `.venv` | **3.11.9** (`.\.venv\Scripts\python.exe`) |

### 1.2 Versions installées

| Package | Version |
|---------|---------|
| **retuve** | **1.0.0** |
| **retuve-yolo-plugin** | **1.1.0** |
| **ultralytics** | **8.4.96** |
| **torch** | **2.13.0+cpu** |

Installation : `pip install retuve retuve-yolo-plugin` dans `.venv` — **réussie**.

---

## 2. Modèle testé

| Élément | Valeur |
|---------|--------|
| Modèle | YOLO X-ray **pose** (`hip-yolo-xray-pose.pt`) |
| Chemin | `.venv\Lib\site-packages\retuve_yolo_plugin\weights\v1.0\hip-yolo-xray-pose.pt` |
| Device | CPU |
| Seuil conf (predict) | 0.5 |
| imgsz | 800 |

Classes détectées par Ultralytics (sortie réelle) : `hip_pelvis` (class 0), `hip_femour` (class 1).

---

## 3. Image utilisée

| Élément | Valeur |
|---------|--------|
| Source | **Officielle Retuve** : `Cases.XRAY_JPG` |
| Fichier | `331_DDH_115.jpg` (radoss-creative-commons) |
| Licence | CC BY-NC-SA 3.0 |
| Taille | **331 × 331** px |
| Copie locale | `docs/artifacts/retuve_xray_input.jpg` |

---

## 4. Résultats d'inférence YOLO (réels)

L'inférence Ultralytics a **réellement** produit **3 détections** :

### 4.1 Détections (boîtes + keypoints)

| # | Classe | Confiance boîte | Keypoints (x, y) | Confiance keypoints |
|---|--------|-----------------|------------------|---------------------|
| 0 | `hip_pelvis` (0) — côté gauche (x centre < milieu) | **0.8376** | (50.64, 148.94), (88.64, 164.56) | **0.9992**, **1.0000** |
| 1 | `hip_pelvis` (0) — côté droit | **0.8202** | (263.03, 135.53), (229.88, 155.36) | **0.9991**, **0.9998** |
| 2 | `hip_femour` (1) — côté droit uniquement | **0.5398** | (264.15, 169.61), (265.46, 182.95) | **0.9990**, **0.9997** |

**Total keypoints bruts obtenus : 6** (attendu par Retuve pour un frame complet : **8**).

**Manquant :** détection `hip_femour` côté **gauche** (aucune détection class 1 à gauche).

Journal JSON brut : `docs/artifacts/retuve_inference_raw.json`

### 4.2 Noms exacts et coordonnées des sorties

Le modèle YOLO retourne des **classes d'objets et des indices de keypoints**, pas directement six objets `LandmarksXRay` nommés. Les seuls noms factuels disponibles au stade brut sont donc :

| Sortie brute exacte | Côté attribué par le plugin | Coordonnées (x, y) | Confiance keypoint |
|---------------------|-----------------------------|--------------------|---------------------|
| `hip_pelvis[0]` | gauche | (50.6445, 148.9395) | 0.999189 |
| `hip_pelvis[1]` | gauche | (88.6375, 164.5621) | 0.999990 |
| `hip_pelvis[0]` | droite | (263.0304, 135.5330) | 0.999144 |
| `hip_pelvis[1]` | droite | (229.8794, 155.3559) | 0.999810 |
| `hip_femour[0]` | droite | (264.1451, 169.6134) | 0.998953 |
| `hip_femour[1]` | droite | (265.4640, 182.9467) | 0.999672 |

Le mapping prévu par `xray_pose.py`, uniquement lorsqu'il existe 8 points, est :

`pel_l_o`, `pel_l_i`, `fem_l`, `h_point_l`, `pel_r_o`, `pel_r_i`, `fem_r`, `h_point_r`.

Dans ce test, ce mapping **n'a pas été appliqué**, car le fémur gauche manque. Il serait donc incorrect de présenter les six coordonnées brutes comme six landmarks anatomiques Retuve officiellement retournés.

Une incohérence interne du plugin est aussi constatée : `utils.py` expose la liste `pel_l_o`, `pel_l_i`, `h_point_l`, `fem_l`, … tandis que `xray_pose.py` assigne les deux points fémoraux dans l'ordre `fem_l`, `h_point_l`, … Cette ambiguïté empêche d'attribuer honnêtement un nom anatomique plus précis aux indices `hip_femour[0/1]` sans validation supplémentaire.

### 4.3 Image annotée

| Fichier | Contenu |
|---------|---------|
| `docs/artifacts/retuve_xray_annotated_raw_yolo.jpg` | Annotation dessinée à partir des **détections YOLO réelles** (boîtes + keypoints + confiances) |
| Image annotée Retuve (`analyse_hip_xray_2D`) | **Non produite** — pipeline en erreur |

---

## 5. Landmarks Retuve structurés

| Élément | Résultat |
|---------|----------|
| `LandmarksXRay` via `analyse_hip_xray_2D` | **Non obtenus** |
| `pel_l_o`, `pel_l_i`, `fem_l`, `h_point_l`, … | — |

Cause : `yolo_predict_xray` (plugin) n'accepte un frame que si `len(landmarks) == 8`. Avec 6 points, le frame est **ignoré** (`continue` sans append).

En conséquence, le résultat exact est : **6 keypoints YOLO bruts détectés, 0 landmark Retuve structuré retourné**.

---

## 6. Mesures Retuve

| Mesure | Résultat |
|--------|----------|
| ace_index (Acetabular Index) | **Non calculée** |
| wiberg_index | **Non calculée** |
| ihdi_grade | **Non calculée** |
| tonnis_grade | **Non calculée** |

Aucune mesure n'a été inventée. Le pipeline géométrique Retuve n'a pas été atteint.

---

## 7. Erreur rencontrée

### Symptôme

```text
File "...\retuve\funcs.py", line 173, in analyse_hip_xray_2D
    img = image_arrays[0]
IndexError: list index out of range
```

### Chaîne causale (factuelle)

1. YOLO pose détecte **3 objets** → **6 keypoints** (manque fémur gauche).
2. `retuve_yolo_plugin.xray_pose.yolo_predict_xray` exige **8** landmarks ; sinon n'ajoute rien à `landmark_results`.
3. `landmark_results` reste **vide**.
4. `process_landmarks_xray` renvoie une liste d'images vide.
5. `analyse_hip_xray_2D` plante sur `image_arrays[0]`.

**Décision :** arrêt ici — pas de contournement, pas de mesures simulées, pas de landmarks inventés pour « compléter » les 8 points.

---

## 8. Limites par rapport à la coxométrie adulte (MVP)

Même en cas de succès Retuve, le schéma de sortie resterait insuffisant pour le MVP :

| Besoin MVP | Couverture Retuve / YOLO X-ray observée |
|------------|------------------------------------------|
| Centre tête fémorale G/D | Non nommé ainsi ; au mieux keypoints `hip_femour` (2 pts / côté, et **1 côté manquant** sur cette image) |
| Bord latéral acétabulum | Approximé via keypoints `hip_pelvis` (2 pts / côté) |
| Toit acétabulaire / Tönnis angle | Mesure Retuve = `ace_index` + grade Tönnis — **non obtenue ici** |
| Axe col fémoral | **Absent** du modèle |
| Axe diaphyse | **Absent** du modèle |
| Tubérosités ischiatiques | **Absentes** du modèle |
| CCD | **Impossible** avec ce modèle |
| Ligne bi-ischiatique | **Impossible** avec ce modèle |

De plus, l'image de test officielle est une radio **DDH pédiatrique** (331×331), pas une radio bassin adulte AP.

---

## 9. Conclusion de faisabilité (après test réel)

| Critère | Verdict |
|---------|---------|
| Installation Retuve + plugin YOLO sur Python 3.11 | **OK** |
| Chargement réel de `hip-yolo-xray-pose.pt` | **OK** |
| Inférence réelle sur image officielle | **OK** (détections + confidences) |
| 8 landmarks Retuve + mesures cliniques | **ÉCHEC** sur cette image (6/8 points) |
| Utilisable directement pour coxométrie adulte MVP | **Non** |

**Recommandation inchangée :** Retuve YOLO X-ray est un outil DDH utile à étudier, mais **pas** un détecteur complet pour VCE + Tönnis + CCD + ligne bi-ischiatique adultes. Un modèle custom annoté (ou pipeline hybride avec correction manuelle) reste nécessaire.

---

## 10. Artefacts produits

```text
docs/artifacts/retuve_xray_input.jpg
docs/artifacts/retuve_xray_annotated_raw_yolo.jpg
docs/artifacts/retuve_inference_raw.json
scripts/retuve_feasibility_inference.py
scripts/annotate_raw_yolo.py
.venv/   (Python 3.11.9)
```

---

*Aucun résultat simulé. Aucun landmark inventé. Rapport basé uniquement sur l'exécution réelle du 16/07/2026.*
