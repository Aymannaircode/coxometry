# Outil local d'annotation manuelle — Pilote MVP et lot bassin

Interface locale pour l'Annotateur A :

- **pilot** : 16 images JPEG P01–P16 (pilote d'origine) ;
- **new_26** : 26 radiographies DICOM de `bassin/a_annoter/`.

L'outil n'utilise **aucune IA**, ne lance aucune inférence ni entraînement et
ne génère aucune coordonnée. Une coordonnée `x`/`y` ne peut être créée dans
l'interface que par un **clic gauche humain sur l'image**.

## Prérequis

- Python 3.9 ou plus récent ;
- un navigateur moderne (Edge, Chrome ou Firefox) ;
- **pilote seul** : bibliothèque Python standard uniquement ;
- **lot new_26** : Python du venv projet avec `pydicom`, `numpy`, `Pillow`
  et `pylibjpeg` (+ `pylibjpeg-libjpeg`) pour le décodage DICOM JPEG lossless.

## Lancement — pilote (16 JPEG)

```powershell
python .\annotation_pilot\manual_annotation_tool\server.py
# ou
.\annotation_pilot\manual_annotation_tool\launch.ps1
```

## Lancement — lot bassin (26 DICOM)

```powershell
.\annotation_pilot\manual_annotation_tool\launch_new_26.ps1
# ou
.\.venv\Scripts\python.exe .\annotation_pilot\manual_annotation_tool\prepare_manual_annotation_new_26.py
.\.venv\Scripts\python.exe .\annotation_pilot\manual_annotation_tool\server.py --dataset new_26
```

La worklist provient de **`bassin/verification_radios.csv`** (`utilisable_annotation=oui`, 26 cas).
Les DICOM sont lus dans `bassin/a_annoter/` (originaux jamais modifiés).

### Référence visuelle YOLO (sans import automatique)

En mode `new_26`, un lien **« Ouvrir overlay YOLO »** permet de consulter
`datasets/yolo_pose_new_26/visual_check/overlays/` en **lecture seule**.
Les prédictions YOLO **ne sont jamais chargées** dans les coordonnées d'annotation :
seul un clic humain modifie `x`/`y`/`v`.

### Priorité post-entraînement : corriger FSD

Si la diaphyse distale n'est pas fiable (FOV court), marquer **FSD_R** / **FSD_L** avec
**Marquer non visible (v=0)** — ne jamais forcer un point pour « compléter » le schéma.

Puis ouvrir manuellement : `http://127.0.0.1:8765`

### Affichage DICOM (new_26)

Les navigateurs **ne peuvent pas afficher** les DICOM directement. En mode
`new_26`, le serveur :

1. lit le DICOM original dans `bassin/a_annoter/` (**jamais modifié**) ;
2. applique le fenêtrage DICOM (`WindowCenter` / `WindowWidth`) ;
3. écrit une PNG 1:1 dans `manual_annotation_tool/cache/new_26/` ;
4. sert cette PNG au navigateur pour l'annotation.

Les coordonnées restent en **pixels image** (origine coin supérieur gauche),
identiques aux dimensions DICOM (`Rows` × `Columns`).

Initialiser les JSON vides (une seule fois si besoin) :

```powershell
.\.venv\Scripts\python.exe .\annotation_pilot\manual_annotation_tool\bootstrap_new_26.py
```

Vérifier l'accessibilité des 26 cas avant annotation :

```powershell
.\.venv\Scripts\python.exe .\annotation_pilot\manual_annotation_tool\prepare_manual_annotation_new_26.py
```

## Correction manuelle de landmarks existants

L'outil permet de **recharger une annotation complète**, sélectionner un landmark
dans la liste LM-01…LM-14 et **cliquer une nouvelle position** pour le corriger.
Seul le clic humain modifie les coordonnées ; rien n'est deviné automatiquement.

### Session ciblée — B26_25 et B26_26 (ASL)

```powershell
.\annotation_pilot\manual_annotation_tool\launch_correction_asl.ps1
```

Ou manuellement :

```powershell
.\annotation_pilot\manual_annotation_tool\launch_new_26.ps1 --cases B26_25 B26_26
```

Puis ouvrir dans le navigateur :

- `http://127.0.0.1:8765/?pilot_id=B26_25&landmark=ASL_L`
- `http://127.0.0.1:8765/?pilot_id=B26_26&landmark=ASL_R`

### Procédure de correction

1. Le serveur en mode `--cases` n'expose **que** les cas autorisés (les autres B26
   ne sont pas accessibles dans la liste).
2. Cliquer le landmark à corriger dans la liste (ex. **LM-06 ASL_L**).
3. Zoomer sur l'acétabulum (molette) et **clic gauche** sur la nouvelle position.
4. **Enregistrer le brouillon** ou **Valider cette image** pour écrire le JSON source.
5. Passer au cas suivant via la liste déroulante.

Les DICOM originaux et les autres annotations ne sont pas modifiés.

Après correction, relancer dans l'ordre : validation JSON → labels YOLO → overlays
→ entraînement (uniquement sur votre demande explicite).

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s annotation_pilot\manual_annotation_tool\tests -v
```

## Utilisation image par image

1. Vérifier l'image sélectionnée dans la liste P01 → P16.
2. Lire le landmark courant, son ID et son côté dans le panneau vert.
3. Vérifier l'orientation : **droite patient = gauche de l'image**.
4. Si le landmark est clairement localisable, cliquer dessus avec le bouton
   gauche. Le clic enregistre localement dans l'interface `x`, `y` et `v=2`.
5. Si le landmark est non visible, non fiable ou hors champ, cliquer sur
   **Marquer non visible (v=0)**. `x` et `y` restent alors `null`.
6. Continuer jusqu'aux 14 landmarks. L'interface sélectionne le prochain
   landmark incomplet, mais ne crée jamais de point à sa place.
7. Utiliser **Enregistrer le brouillon** à tout moment. Un brouillon peut être
   incomplet.
8. Utiliser **Valider cette image** seulement lorsque les 14 landmarks ont
   soit un clic valide (`v=2`), soit `v=0`. Le bouton reste désactivé sinon et
   le serveur contrôle à nouveau cette condition.
9. Naviguer vers l'image suivante. En cas de modifications non enregistrées,
   l'outil demande confirmation avant de quitter.

## Commandes

- **Clic gauche** : placer ou corriger le landmark sélectionné.
- **Molette** ou boutons `+` / `−` : zoomer ou dézoomer.
- **Espace + glisser**, clic droit + glisser ou clic molette + glisser :
  déplacer l'image.
- **Ajuster** : recentrer l'image entière.
- **Point précédent** : revenir au landmark précédent.
- Cliquer une ligne LM-01…LM-14 : sélectionner directement un landmark à
  corriger.
- **Annuler la dernière action** ou `Ctrl+Z` : revenir sur le dernier clic ou
  marquage `v=0`.

## Règles obligatoires

- `*_R` = côté droit patient = gauche image.
- `*_L` = côté gauche patient = droite image.
- `v=2` seulement pour un point net, créé par clic.
- `v=1` est désactivé conformément au protocole pilote.
- Si le point doit être deviné : `v=0`, avec `x=null` et `y=null`.
- Ne jamais reproduire un côté par symétrie.
- Ne jamais utiliser les keypoints pédiatriques de Dataset 1.
- Respecter les définitions détaillées de
  `docs/annotation_guidelines.md`.

## Données lues et écrites

### Pilote (`--dataset pilot`, défaut)

Lecture seule :

- `annotation_pilot/images/*.jpg`
- `annotation_pilot/annotations/annotator_A/worklist.csv`

Écriture :

- `annotation_pilot/annotations/annotator_A/P01_a308.json` … `P16_a425.json`

### Lot bassin (`--dataset new_26`)

Lecture seule :

- `bassin/a_annoter/*` (DICOM sans extension)

Cache d'affichage (PNG régénérées si le DICOM change) :

- `manual_annotation_tool/cache/new_26/*.png`

Écriture :

- `annotation_pilot/annotations/new_26/B26_01.json` … `B26_26.json`
- `annotation_pilot/annotations/new_26/worklist.csv` (lecture seule pour l'outil)

Le champ JSON `source_file` contient l'UID DICOM d'origine ; `image_id` vaut
`B26_01` … `B26_26`.

## Validation stricte

Avant toute sauvegarde, le serveur vérifie notamment :

- `schema_version = "mvp-pilot-1.0"` ;
- `annotator_id = "annotator_A"` ;
- exactement 14 landmarks, dans l'ordre LM-01 à LM-14 ;
- IDs, noms et côtés inchangés ;
- `v` limité à `null`, `0` ou `2` ;
- `v=0` implique `x=y=null` ;
- `v=2` implique des coordonnées numériques dans les limites de l'image ;
- une validation finale refuse tout landmark incomplet.

Une sauvegarde de brouillon conserve les landmarks encore à `null`. Elle ne
les complète jamais automatiquement.
