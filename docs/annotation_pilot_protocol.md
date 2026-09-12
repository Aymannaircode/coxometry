# Protocole de test d’annotation — Pilote MVP (14 landmarks)

**Date :** 17 juillet 2026  
**Sources :** `docs/landmark_specification.md` · `docs/annotation_guidelines.md`  
**Objectif :** valider le guide d’annotation et la faisabilité des 14 landmarks MVP sur un **petit lot pilote**, avant tout dataset adulte dédié.  
**Contraintes respectées :** aucun dataset existant modifié · aucune annotation automatique · aucune coordonnée inventée · aucun entraînement · aucun modèle IA  

---

## 1. Contexte et limites du pilote

### 1.1 Pourquoi utiliser Dataset 1 comme support visuel ?

Dataset 1 (MTDDH) contient des radiographies **pédiatriques** DDH, pas des clichés adultes. Les landmarks MVP adultes (`TD`, `ASM`, `FNM`, `FSP`, `FSD`, etc.) **ne sont pas annotés** dans ce corpus.

Le pilote sert donc à :

- tester la **compréhension** du guide d’annotation ;
- mesurer la **difficulté** et les **ambiguïtés** ;
- identifier les **révisions** nécessaires du guide ;
- préparer l’**outillage** et la **structure de fichiers** pour un futur dataset adulte.

**Ce pilote ne valide pas** la transférabilité clinique adulte des mesures VCE / Tönnis / CCD sur Dataset 1.

### 1.2 Ce que le pilote ne fait pas

| Interdit | Raison |
|----------|--------|
| Copier les keypoints Dataset 1 (`re/ry/rc/rh/…`) vers les landmarks MVP | Schéma anatomique différent |
| Générer des coordonnées par modèle ou par heuristique | Biais et fausses données |
| Modifier `Dataset1/` | Intégrité du corpus source |
| Considérer le pilote comme jeu d’entraînement | Hors périmètre |

---

## 2. Lot pilote : 16 radiographies sélectionnées

Sélection effectuée en **lecture seule** sur Dataset 1 (988 images annotées DDH + splits Test / Val sans labels).  
Critères : diversité de résolution, complétude DDH, visibilité partielle (`v=1`), absence de labels préalables, anomalies régions QC, cadrage large vs serré.

### 2.1 Tableau de sélection

| ID pilote | Fichier source | Split D1 | Dossier source | Rôle dans le pilote | Qualité / particularité |
|-----------|----------------|----------|----------------|---------------------|-------------------------|
| **P01** | `a308.jpg` | Train | `Keypoints/Train` | Référence « standard » | 1675×1001 ; 8/8 points DDH `v=2` ; régions QC présentes |
| **P02** | `a245.jpg` | Train | `Keypoints/Train` | Standard taille médiane | 1376×1020 ; tous points DDH `v=2` |
| **P03** | `e65.jpg` | Train | `Keypoints/Train` | Petite résolution | 742×513 ; surface minimale du lot annoté |
| **P04** | `w84.jpg` | Train | `Keypoints/Train` | Grande résolution | 2800×2750 ; image très grande |
| **P05** | `y44.jpg` | Train | `Keypoints/Train` | Points DDH manquants | `lc`/`lh` à `v=0` (6/8) — test discipline `v=0` |
| **P06** | `a322.jpg` | Train | `Keypoints/Train` | Têtes fémorales incertaines (D1) | `rc`/`lc` à `v=1` — proxy difficulté `FHC` |
| **P07** | `b31.jpg` | Validation | `Keypoints/Validation` | Visibilité mixte | `rc` et `ly` à `v=1` |
| **P08** | `11ebyy.jpg` | Validation | `Keypoints/Validation` | **Sans** keypoints JSON D1 | 52 images Val sur disque sans entrée COCO |
| **P09** | `b1.jpg` | Validation | `Keypoints/Validation` | **Sans** keypoints JSON D1 | Idem ; régions LabelMe présentes |
| **P10** | `170qt.jpg` | Test | `Keypoints/Test` | Annotation **à l’aveugle** | Aucun JSON keypoints Test dans D1 |
| **P11** | `259qt.jpg` | Test | `Keypoints/Test` | Annotation à l’aveugle | Idem |
| **P12** | `282qt.jpg` | Test | `Keypoints/Test` | Annotation à l’aveugle | Idem |
| **P13** | `a311.jpg` | Train | `Keypoints/Train` | Anomalie régions QC | 5 polygones LabelMe (2× `apple`) |
| **P14** | `h27.jpg` | Validation | `Keypoints/Validation` | Anomalie régions QC | Label `apple` manquant (2× `dog`) |
| **P15** | `c82.jpg` | Train | `Keypoints/Train` | Cadrage large (quartile surface) | 1072×836 |
| **P16** | `a425.jpg` | Train | `Keypoints/Train` | Ratio quasi carré | 2739×2733 ; aspect ~1,002 |

**Répartition :** Train 10 · Validation 4 · Test 3 · **16 images** (dans la fourchette 10–20 demandée).

### 2.2 Images de réserve (optionnelles, +4 → total 20)

Si le comité clinique souhaite 20 cas :

| ID | Fichier | Intérêt |
|----|---------|---------|
| P17 | `w145.jpg` | Cadrage très large (2800×1012, aspect 2,77) — FOV fémoral distal souvent court |
| P18 | `a449.jpg` | `rc`/`lc` à `v=1` (autre profil tête incertaine) |
| P19 | `12ex.jpg` | Val sans JSON + régions QC |
| P20 | `115qi.jpg` | Test à l’aveugle supplémentaire |

---

## 3. Copie de travail séparée (à créer manuellement)

**Ne pas annoter dans `Dataset1/`.** Créer un dossier indépendant à la racine du projet :

```
annotation_pilot/
├── README.md                          # Rappel : pilote MVP, pas Dataset1
├── manifest.csv                       # Liste P01–P16, chemins, statut
├── images/                            # Copies JPEG (lecture seule côté source)
│   ├── P01_a308.jpg
│   ├── P02_a245.jpg
│   └── …
├── reference_qc/                      # Copies optionnelles régions D1 (info seulement)
│   └── …                              # Ne pas confondre avec landmarks MVP
├── templates/                         # Gabarits vides (§4)
│   ├── annotation_schema.json
│   └── P01_a308.template.json
├── annotations/                       # Sorties annotateurs (futur)
│   ├── annotator_A/
│   └── annotator_B/
├── logs/                              # Fichiers d’évaluation (§6)
│   ├── visibility_matrix.csv
│   ├── difficulty_scores.csv
│   ├── ambiguity_log.csv
│   └── guideline_feedback.csv
└── reviews/                           # Synthèses et décisions cliniques
    └── pilot_report.md
```

### 3.1 Procédure de copie (sans modifier Dataset 1)

Exécuter **une seule fois** avant le pilote (exemple PowerShell) :

```powershell
$root = "C:\Users\g\OneDrive\Desktop\Projet-Ayman"
$pilot = Join-Path $root "annotation_pilot"
New-Item -ItemType Directory -Force -Path $pilot, "$pilot\images", "$pilot\templates", "$pilot\annotations", "$pilot\logs", "$pilot\reviews" | Out-Null

# Tableau ID → (fichier, sous-dossier Keypoints)
$pairs = @(
  @("P01","a308.jpg","Train"), @("P02","a245.jpg","Train"), @("P03","e65.jpg","Train"),
  @("P04","w84.jpg","Train"), @("P05","y44.jpg","Train"), @("P06","a322.jpg","Train"),
  @("P07","b31.jpg","Validation"), @("P08","11ebyy.jpg","Validation"), @("P09","b1.jpg","Validation"),
  @("P10","170qt.jpg","Test"), @("P11","259qt.jpg","Test"), @("P12","282qt.jpg","Test"),
  @("P13","a311.jpg","Train"), @("P14","h27.jpg","Validation"),
  @("P15","c82.jpg","Train"), @("P16","a425.jpg","Train")
)
foreach ($p in $pairs) {
  $id, $name, $split = $p
  $src = Join-Path $root "Dataset1\Keypoints\$split\$name"
  $dst = Join-Path $pilot "images\${id}_$name"
  Copy-Item -LiteralPath $src -Destination $dst
}
```

**Vérification :** 16 fichiers dans `annotation_pilot/images/` ; `Dataset1/` inchangé (comparer dates / hashes si besoin).

### 3.2 Fichier `manifest.csv`

Colonnes recommandées :

```csv
pilot_id,source_file,source_split,image_copy,annotator_A_status,annotator_B_status,qc_status,notes
P01,a308.jpg,Train,images/P01_a308.jpg,pending,pending,pending,standard
…
```

---

## 4. Structure d’annotation MVP (14 landmarks, sans coordonnées)

### 4.1 Schéma JSON (gabarit vide)

Chaque image possède un fichier template **sans coordonnées** — uniquement la structure et des champs de visibilité prévisionnels à remplir **manuellement** par l’annotateur.

Fichier : `annotation_pilot/templates/annotation_schema.json` (à créer à partir du bloc ci-dessous).

```json
{
  "schema_version": "mvp-pilot-1.0",
  "image_id": "P01",
  "source_file": "a308.jpg",
  "source_dataset": "Dataset1_MTDDH_pilot_only",
  "view": "AP_pelvis",
  "population_note": "pediatric_DDH_image_used_for_protocol_test_only",
  "annotator_id": null,
  "annotation_date": null,
  "guidelines_version": "annotation_guidelines.md_2026-07-17",
  "image_width": null,
  "image_height": null,
  "landmarks": [
    {"id": "LM-01", "name": "TD_R",  "side": "right",  "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-02", "name": "TD_L",  "side": "left",   "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-03", "name": "FHC_R", "side": "right",  "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-04", "name": "FHC_L", "side": "left",   "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-05", "name": "ASL_R", "side": "right",  "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-06", "name": "ASL_L", "side": "left",   "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-07", "name": "ASM_R", "side": "right",  "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-08", "name": "ASM_L", "side": "left",   "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-09", "name": "FNM_R", "side": "right",  "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-10", "name": "FNM_L", "side": "left",   "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-11", "name": "FSP_R", "side": "right",  "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-12", "name": "FSP_L", "side": "left",   "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-13", "name": "FSD_R", "side": "right",  "x": null, "y": null, "v": null, "notes": ""},
    {"id": "LM-14", "name": "FSD_L", "side": "left",   "x": null, "y": null, "v": null, "notes": ""}
  ],
  "image_level": {
    "pelvic_rotation_suspected": null,
    "fov_diaphysis_insufficient_R": null,
    "fov_diaphysis_insufficient_L": null,
    "overall_annotation_feasible": null
  },
  "ambiguity_flags": []
}
```

**Règles :**

- `x`, `y` restent `null` tant que l’annotateur n’a pas cliqué.
- `v` : `0` = non visible / non fiable · `2` = net (le pilote **déconseille `v=1`** sauf validation clinique préalable).
- `ambiguity_flags` : liste de codes `A1`…`A8` (voir §5.3).

### 4.2 Outils d’annotation manuelle (au choix)

| Option | Usage |
|--------|-------|
| LabelMe / CVAT / Roboflow | Points nommés selon `LM-XX` |
| Figma / GIMP + export CSV | Pilote très léger |
| Script interne minimal | Lecteur d’images + clic → remplit le JSON |

**Exigence :** l’outil doit permettre d’enregistrer `v=0` **sans** coordonnées (ou avec coordonnées ignorées).

### 4.3 Convention de nommage des fichiers annotés

```
annotation_pilot/annotations/<annotator_id>/P01_a308.json
```

Double lecture : deux annotateurs indépendants (`annotator_A`, `annotator_B`) sur **les 16 images**.

---

## 5. Matrice de visibilité attendue (pré-pilote, sans coordonnées)

Classification **prévisionnelle** pour guider l’évaluation — à **confirmer ou infirmer** par les annotateurs.  
Légende : **C** = clairement visible · **D** = difficile · **N** = non visible / non fiable sur ce type d’image.

### 5.1 Par landmark (tendance sur Dataset 1 pédiatrique)

| Landmark | Attendu sur D1 (pilote) | Justification |
|----------|-------------------------|---------------|
| `TD_R` / `TD_L` | **D** (souvent **N** chez le très jeune) | Teardrop adulte non annoté ; ossification pelvienne immature |
| `FHC_R` / `FHC_L` | **C** à **D** | Tête visible ; définition cercle Mose vs noyau pédiatrique (`rc`/`lc`) |
| `ASL_R` / `ASL_L` | **C** à **D** | Marge superolatérale souvent visible ; ambiguïté sourcil vs rim (**A1**) |
| `ASM_R` / `ASM_L` | **D** à **N** | Sourcil médial adulte souvent peu contrasté sur radio pédiatrique (**A3**) |
| `FNM_R` / `FNM_L` | **D** | Col étroit / cam possible ; pas de repère D1 direct |
| `FSP_R` / `FSP_L` | **D** | Petit trochanter parfois peu net |
| `FSD_R` / `FSD_L` | **D** à **N** | FOV bassin coupe souvent la diaphyse basse (**A7**) |

### 5.2 Par image pilote (hypothèses à valider)

| ID | TD | FHC | ASL | ASM | FNM | FSP | FSD | Commentaire |
|----|----|-----|-----|-----|-----|-----|-----|-------------|
| P01 | D | C | C | D | D | D | D | Cas de référence |
| P02 | D | C | C | D | D | D | D | Standard médian |
| P03 | N | D | D | N | N | N | N | Basse résolution |
| P04 | D | C | C | D | D | D | D | Grande image, détails potentiels |
| P05 | D | C | C | D | D | D | **N** (L) | Côté G : têtes D1 absentes — discipline `v=0` |
| P06 | D | **D** | C | D | D | D | D | Têtes D1 `v=1` |
| P07 | D | **D** | C | D | D | D | D | Visibilité mixte |
| P08–P09 | ? | ? | ? | ? | ? | ? | ? | À l’aveugle — **ne pas préjuger** |
| P10–P12 | ? | ? | ? | ? | ? | ? | **N**? | Test sans labels ; FOV variable |
| P13–P14 | D | C | C | D | D | D | D | QC régions aberrant — noter inclinaison |
| P15 | D | C | C | D | D | D | D | Cadrage intermédiaire |
| P16 | D | C | C | D | D | D | D | Image quasi carrée |

Les colonnes P08–P12 restent volontairement « ? » : **aucune coordonnée ni visibilité ne doit être pré-remplie**.

### 5.3 Codes d’ambiguïté à journaliser

| Code | Sujet | Déclencheur en pilote |
|------|-------|----------------------|
| A1 | Sourcil vs bord osseux | Hésitation sur `ASL` |
| A2 | Référence horizontale | Teardrop illisible ; tentation ischions |
| A3 | `ASM` peu visible | Impossible de tracer le sourcil médial |
| A6 | Axe du col | `FNM` vs corticales floues |
| A7 | Axe / FOV diaphyse | `FSD` trop proche de `FSP` ou hors champ |
| A8 | Rotation fémorale | CCD 2D douteux malgré points placés |

---

## 6. Déroulement du pilote (procédure)

### Phase 0 — Préparation (1 session)

1. Lire `landmark_specification.md` et `annotation_guidelines.md`.  
2. Créer `annotation_pilot/` (§3) par copie, pas de modification de `Dataset1/`.  
3. Générer 16 templates JSON vides (`P01`…`P16`).  
4. Brief clinique : rappeler population pédiatrique D1 et interdiction de `v=1` non validé.

### Phase 1 — Annotation individuelle (2 annotateurs)

| Étape | Action |
|-------|--------|
| 1 | Chaque annotateur traite les 16 images dans l’ordre P01→P16 |
| 2 | Remplir `visibility_matrix.csv` (§6.1) **avant** ou **après** clic, par landmark |
| 3 | Remplir `difficulty_scores.csv` (§6.2) |
| 4 | Consigner chaque ambiguïté dans `ambiguity_log.csv` (§6.3) |
| 5 | Ne jamais copier les keypoints D1 existants |

**Durée indicative :** 20–40 min / image (première passe).

### Phase 2 — Réconciliation

1. Superposer les deux JSON par image.  
2. Calculer distance euclidienne par landmark (`v>0` des deux côtés).  
3. Seuil d’alerte provisoire : **> 5 mm** à l’échelle clinique **ou** **> 0,02 × largeur image** en pixels — **à valider par le radiologue référent**.  
4. Cas au-dessus du seuil → revue conjointe ou tranche clinique.

### Phase 3 — Revue clinique

Un **radiologue ou orthopédiste** revoit :

- tous les cas `v=0` sur landmarks obligatoires ;
- tous les désaccords > seuil ;
- tous les logs `A1`–`A8` ;
- les images P05, P06, P07, P13, P14 en priorité.

### Phase 4 — Synthèse

Rédiger `annotation_pilot/reviews/pilot_report.md` avec décision : **guide OK** / **révisions mineures** / **révisions majeures**.

---

## 7. Méthodes d’évaluation

### 7.1 Difficulté d’annotation (`difficulty_scores.csv`)

Échelle **par landmark × image × annotateur** :

| Score | Libellé | Critère |
|-------|---------|---------|
| 1 | Facile | Point posé en < 30 s, sans hésitation |
| 2 | Légère | Hésitation brève, une relecture |
| 3 | Modérée | Zoom / contraste nécessaires ; 1–3 min |
| 4 | Difficile | Doute persistant ; consultation du guide |
| 5 | Très difficile / non fait | `v=0` ou placement très incertain |

Colonnes :

```csv
pilot_id,landmark_id,landmark_name,annotator_id,difficulty_1_to_5,time_seconds,v_used,completed
P01,LM-01,TD_R,annotator_A,3,120,2,yes
```

**Indicateurs agrégés :**

- médiane de difficulté par landmark (sur 16 images) ;
- % d’images avec score ≥ 4 par landmark ;
- temps total par image.

### 7.2 Clarté des landmarks (`visibility_matrix.csv`)

Échelle **C / D / N** (cf. §5.1) — **observation**, pas jugement clinique final :

```csv
pilot_id,landmark_name,annotator_id,clarity,C_or_D_or_N,confidence_1_to_5,comment
P01,ASM_R,annotator_A,D,3,"sourcil médial peu dense"
```

**Indicateurs :**

- taux **C** par landmark ;
- landmarks avec > 50 % **N** ou **D** → candidats révision du guide ou exclusion temporaire.

### 7.3 Ambiguïtés rencontrées (`ambiguity_log.csv`)

```csv
pilot_id,landmark_name,annotator_id,ambiguity_code,description,resolved_yes_no,resolution_notes
P06,ASL_R,annotator_B,A1,"rim latéral distinct du sourcil",no,"attente revue clinique"
```

**Indicateurs :**

- fréquence par code A1–A8 ;
- ambiguïtés non résolues après Phase 3 → **bloquant** pour passage en production.

### 7.4 Besoin de modifier le guide (`guideline_feedback.csv`)

Chaque annotateur peut soumettre une ligne par problème :

```csv
annotator_id,section_guide,issue_type,severity,proposed_change,example_pilot_id
annotator_A,2.4 ASM,unclear_definition,high,"ajouter schéma zoom sourcil médial",P07
```

| `issue_type` | Exemple |
|--------------|---------|
| `unclear_definition` | Texte insuffisant |
| `missing_illustration` | Besoin figure |
| `contradiction` | Conflit entre deux règles |
| `tooling` | Outil inadapté |
| `out_of_scope` | Landmark inadapté au pédiatrique |

**Règles de décision pour modifier le guide :**

| Condition | Action |
|-----------|--------|
| Même `issue_type` + `severity=high` rapporté par **≥ 2 annotateurs** | Révision **obligatoire** du guide |
| Ambiguïté A1/A3/A7 sur **> 30 %** des images | Atelier clinique + mise à jour § concerné |
| `FSD` en **N** sur **> 70 %** des images du pilote | Confirmer règle FOV (§2.7 guidelines) ou exclure CCD du MVP sur AP bassin seul |
| Désaccord inter-annotateurs > seuil sur **> 25 %** des landmarks | Renforcer critères de qualité §4 guidelines |

---

## 8. Critères de succès / échec du pilote

### Succès minimal

- [ ] 16 images copiées dans `annotation_pilot/` sans altérer Dataset 1  
- [ ] 2 passes d’annotation manuelle complètes (structure 14 landmarks)  
- [ ] Aucune coordonnée pré-remplie ou auto-générée  
- [ ] Matrices `visibility`, `difficulty`, `ambiguity`, `guideline_feedback` remplies  
- [ ] Revue clinique documentée sur les cas ambigus  
- [ ] Décision explicite sur révision du guide  

### Échec / arrêt

- Annotateurs placent systématiquement des points « pour compléter » malgré `v=0` requis  
- Impossibilité d’accord clinique sur A1 ou A2  
- > 50 % des images avec CCD non calculable (`FSD` N) **sans** stratégie FOV documentée  

---

## 9. Calendrier indicatif

| Semaine | Activité |
|---------|----------|
| S0 | Création copie de travail + templates vides |
| S1 | Formation annotateurs (guide + 2 images d’essai hors lot P01–P16) |
| S2 | Annotation A + B en parallèle |
| S3 | Réconciliation + logs |
| S4 | Revue radiologue / orthopédiste + rapport pilote |

---

## 10. Livrables du pilote

| Livrable | Emplacement |
|----------|-------------|
| Images copiées | `annotation_pilot/images/` |
| Annotations manuelles | `annotation_pilot/annotations/<id>/` |
| Scores et logs | `annotation_pilot/logs/*.csv` |
| Rapport final | `annotation_pilot/reviews/pilot_report.md` |
| Guide révisé (si besoin) | Nouvelle version de `docs/annotation_guidelines.md` — **hors scope automatique de ce protocole** |

---

## 11. Rappel éthique et données

- Dataset 1 = données pédiatriques DDH anonymisées ; usage pilote **interne** au projet.  
- Ne pas diffuser les copies hors cadre projet.  
- Le pilote **ne remplace pas** l’acquisition d’un corpus **adulte** pour la coxométrie MVP.  

---

*Protocole uniquement — aucun fichier de `Dataset1/` modifié · aucune annotation automatique · aucune coordonnée inventée dans ce document.*
