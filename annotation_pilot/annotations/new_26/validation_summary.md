# Rapport de validation — dataset new_26

**Date de génération :** 2026-08-23 17:49:58
**Répertoire :** `C:\Users\g\OneDrive\Desktop\Projet-Ayman\annotation_pilot\annotations\new_26`

## Résumé exécutif

| Métrique | Valeur |
|----------|--------|
| Annotations attendues | 26 |
| Fichiers JSON présents | 26 |
| Fichiers JSON manquants | 0 |
| **Annotations valides** | **26** |
| **Annotations à vérifier** | **0** |
| Erreurs (ERROR) | 0 |
| Avertissements (WARNING) | 0 |

## Statistiques landmarks

- Total landmarks vérifiés : 364 (attendu : 364 = 26×14)
- Landmarks visibles (v=2) : 364
- Landmarks non visibles (v=0) : 0
- Landmarks non renseignés (v=null) : 0
- Incohérences dimensions JSON/DICOM : 0

## Critères vérifiés

1. Présence des 14 landmarks (TD, FHC, ASL, ASM, FNM, FSP, FSD — R/L)
2. Champs x, y, v pour chaque landmark
3. Coordonnées x/y dans les dimensions réelles de l'image (0 ≤ x < width, 0 ≤ y < height)
4. Gestion v=0 : x=null et y=null obligatoires
5. Détection coordonnées nulles ou manquantes
6. Détection doublons et coordonnées aberrantes (bords, inversion R/L)
7. Correspondance image_id / source_file ↔ B26_XX / DICOM worklist
8. Présence des 26 fichiers B26_01.json à B26_26.json
9. Cohérence dimensions annotation ↔ DICOM source

## Annotations valides

`B26_01`, `B26_02`, `B26_03`, `B26_04`, `B26_05`, `B26_06`, `B26_07`, `B26_08`, `B26_09`, `B26_10`, `B26_11`, `B26_12`, `B26_13`, `B26_14`, `B26_15`, `B26_16`, `B26_17`, `B26_18`, `B26_19`, `B26_20`, `B26_21`, `B26_22`, `B26_23`, `B26_24`, `B26_25`, `B26_26`

## Fichiers générés

- Rapport détaillé CSV : `C:\Users\g\OneDrive\Desktop\Projet-Ayman\annotation_pilot\annotations\new_26\validation_report.csv`
- Ce résumé : `C:\Users\g\OneDrive\Desktop\Projet-Ayman\annotation_pilot\annotations\new_26\validation_summary.md`

---
*Validation en lecture seule — aucune annotation modifiée.*
