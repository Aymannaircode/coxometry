# Annotateur A — Environnement d'annotation manuelle (Phase 1)

**Ne pas commencer l'annotation automatiquement.** Ce dossier ne contient que
l'environnement prêt à l'emploi. Chaque coordonnée doit être posée **manuellement**,
image par image, par l'annotateur humain.

## Ce qui est fourni

- 16 fichiers de travail JSON : `P01_a308.json` … `P16_a425.json`
  - structure identique au protocole (schéma `mvp-pilot-1.0`, 14 landmarks) ;
  - `annotator_id` = `"annotator_A"` (seul champ pré-rempli) ;
  - `x`, `y`, `v` = `null` → **à remplir manuellement** ;
  - `notes`, `image_level`, `ambiguity_flags` vides.
- Images à annoter : `../../images/P01_a308.jpg` … `P16_a425.jpg` (lecture seule).
- Ordre de travail : voir `worklist.csv` (P01 → P16).

## Règles du guide (rappel — `docs/annotation_guidelines.md`)

### Orientation
- Vue AP bassin. **Droite patient = gauche de l'image.**
- `*_R` = côté droit patient (gauche image) ; `*_L` = côté gauche patient (droite image).
- Ne jamais inverser R/L selon l'écran sans vérifier le côté patient.

### Codes de visibilité `v`
- `2` = point net, localisable sans doute raisonnable.
- `1` = estimé — **interdit par défaut** ; uniquement si un clinicien l'a validé pour ce landmark.
- `0` = non annoté / non fiable / hors champ.
- **Règle d'or :** si vous devez deviner, mettez `v=0`. Ne jamais placer un point « pour remplir ».

### Ordre d'annotation recommandé (par image)
1. `TD_R` puis `TD_L` (référence horizontale).
2. Côté droit : `FHC_R` → `ASL_R` → `ASM_R` → `FNM_R` → `FSP_R` → `FSD_R`.
3. Côté gauche : `FHC_L` → … → `FSD_L`.
4. Contrôles de cohérence bilatérale, puis checklist qualité.

### Où cliquer (14 points)
- `TD` : bas de la larme acétabulaire (pas le centre, pas l'ischion).
- `FHC` : centre du cercle best-fit (Mose) de la tête fémorale.
- `ASL` : fin **latérale** du sourcil sclérotique (pas l'ostéophyte rim — A1).
- `ASM` : début **médial** du sourcil (souvent difficile → `v=0` si douteux — A3).
- `FNM` : milieu de l'axe du col (axe = `FHC` → `FNM`).
- `FSP` : axe diaphysaire, juste sous le petit trochanter.
- `FSD` : axe diaphysaire le plus distal net dans le FOV (règle distance `FSP`–`FSD`).

### Interdits
- Ne pas copier les keypoints Dataset 1 pédiatriques (`ry`/`ly`, `rh`/`lh`, etc.).
- Ne pas annoter un côté par symétrie miroir de l'autre.
- Ne pas mettre `v=2` par confort si le point est douteux.
- Population D1 = pédiatrique DDH : images utilisées **uniquement** pour tester le protocole.

## Journaux à remplir en parallèle (dans `../../logs/`)
- `visibility_matrix.csv` — clarté C / D / N par landmark.
- `difficulty_scores.csv` — difficulté 1–5, temps, `v` utilisé.
- `ambiguity_log.csv` — codes A1–A8 rencontrés.
- `guideline_feedback.csv` — problèmes du guide à remonter.
