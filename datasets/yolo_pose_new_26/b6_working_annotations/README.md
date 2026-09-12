# B6 — Annotations de travail `IT_R` / `IT_L` (NON-OFFICIAL)

**Créé :** 2026-08-28  
**Statut :** `PROPOSED / CLINICAL VALIDATION REQUIRED`  
**Guide appliqué :** `../bi_ischial_annotation_guidelines.md` (B4 = READY FOR B6 CONDITIONALLY)

## Avertissement

```
NON-OFFICIAL — NOT for YOLO training, official labels, or production integration
```

- **Ne pas** convertir en labels YOLO 16 kp sans validation B5/B6 formelle.
- **Ne pas** modifier les 14 keypoints officiels existants.
- Coordonnées pilote historiques `B6_pilot_B26_01_coords.json` et `B6_review_B26_05_coords.json` restent des références séparées.

## Contenu

| Fichier | Description |
|---------|-------------|
| `B26_XX.json` | Annotation de travail par image (26 fichiers) |
| `../b6_annotation_log.csv` | Journal tabulaire de campagne |
| `../b6_session_summary.md` | Résumé de session |

## Schéma JSON (`b6-working-annotation-1.0`)

Champs principaux par image :

- `IT_R` / `IT_L` : `{ x, y, v, visibility }`
- `visibility_b7` : catégorie B7 (VISIBLE / PARTIAL)
- `reviewer_status` : `standard` | `review_recommended` | `supervised_case`
- `ambiguities` : codes d'ambiguïté documentés
- `official_labels_modified` : toujours `false`

## Ordre d'annotation

1. B26_01 → 2. B26_05 → 3. B26_07 → 4. B26_11 → 5. B26_12 → 6. B26_02 … B26_26 (reste)

## Cas particuliers

| Image | `reviewer_status` | Note |
|-------|-------------------|------|
| **B26_05** | `supervised_case` | Seul cas PARTIAL bilatéral ; bord FOV |
| **B26_07, B26_11, B26_12** | `review_recommended` | Revue B7 recommandée |
