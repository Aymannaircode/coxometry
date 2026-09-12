# Vérification visuelle — YOLO Pose new_26

Ce dossier contient des **overlays générés automatiquement** pour contrôler les labels YOLO
sans modifier le dataset d'origine (`images/`, `labels/`, `dataset.yaml`).

## Ouvrir la galerie

1. Ouvrir `index.html` dans un navigateur (double-clic ou glisser-déposer).
2. Parcourir les 26 cas `B26_01` … `B26_26`.
3. Cliquer une vignette pour voir l'overlay pleine résolution.

Chemin complet :

```
datasets/yolo_pose_new_26/visual_check/index.html
```

## Légende des couleurs

| Élément | Couleur | Signification |
|---------|---------|---------------|
| Points `_R` | Orange | Landmarks côté **droit** (droite de l'image patient) |
| Points `_L` | Bleu | Landmarks côté **gauche** |
| Rectangle | Vert | Bounding box YOLO |
| Lignes orange | — | Chaîne fémorale / acétabulaire droite |
| Lignes bleues | — | Chaîne fémorale / acétabulaire gauche |

## Checklist de revue clinique

Pour **chaque** image, vérifier :

### Côté R / L
- [ ] Tous les points orange (`*_R`) sont à **droite** du milieu de l'image.
- [ ] Tous les points bleu (`*_L`) sont à **gauche** du milieu.
- [ ] Aucune paire R/L ne semble inversée.

### Teardrop (TD)
- [ ] `TD_R` / `TD_L` sont sur la gouttière acétabulaire (teardrop).

### Tête fémorale (FHC)
- [ ] `FHC_R` / `FHC_L` sont au **centre** de la tête fémorale.

### Acétabulum (ASL / ASM)
- [ ] `ASL_*` : sourcil acétabulaire latéral.
- [ ] `ASM_*` : bord supéro-médial / teardrop region cohérente.

### Col fémoral (FNM)
- [ ] `FNM_*` est sur l'**axe du col** (entre FHC et diaphyse).

### Diaphyse (FSP / FSD)
- [ ] `FSP_*` et `FSD_*` sont alignés sur l'**axe diaphysaire** distal.
- [ ] La ligne orange/bleue FHC→FNM→FSP→FSD suit le fémur.

### Normalisation
- [ ] Les points ne sont **pas décalés** (comparer mentalement avec l'anatomie).
- [ ] Pas de cluster anormal au coin (0,0) — signe d'erreur de conversion.

### Bounding box
- [ ] Le rectangle vert **englobe le bassin** ( deux hanches + part de diaphyse visible).
- [ ] La bbox n'est ni trop serrée ni démesurément large.

## Regénérer les overlays

```bash
.venv\Scripts\python.exe annotation_pilot\scripts\visualize_yolo_pose_new_26.py
```

Les fichiers source (JSON, DICOM, labels YOLO) ne sont **jamais modifiés**.
