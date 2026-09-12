# B6 — Récupération des 5 images manquantes (recherche READ-ONLY)

**Généré :** 2026-08-29  
**Mode :** recherche **READ-ONLY** — aucun fichier copié/déplacé, aucune annotation modifiée  
**Objectif :** retrouver les PNG originaux du corpus `new_26` pour B26_10, B26_13, B26_17, B26_20, B26_26

---

## Conclusion

```
5/5 FOUND
```

Les 5 PNG **existent déjà** dans le projet. Le statut « PNG absent » documenté dans `b6_remaining_21_QA.md` et `b6_full_manual_review_queue.md` provenait d'une **recherche au mauvais emplacement** (`images/train/`) alors que ces 5 cas sont en **split `val`** selon `meta/source_mapping.csv`.

**Aucune copie ni déplacement effectué** (confirmation utilisateur requise pour toute opération fichier).

---

## Méthode de recherche

Emplacements parcourus :

| Zone | Résultat |
|------|----------|
| `datasets/yolo_pose_new_26/images/val/` | **5/5 trouvés** (canonique) |
| `datasets/yolo_pose_new_26/images/train/` | **0/5** (absence attendue — split val) |
| `annotation_pilot/manual_annotation_tool/cache/new_26/` | 5/5 copies identiques |
| `datasets/yolo_pose_new_26/predictions/images/` | 5/5 copies identiques |
| `datasets/yolo_pose_new_26/predictions_v2/images/` | 5/5 copies identiques |
| `datasets/yolo_pose_new_26/predictions_v3/images/` | 5/5 copies identiques |
| `datasets/yolo_pose_new_26/predictions_v4/images/` | 5/5 copies identiques |
| `bassin/a_annoter/` (DICOM source) | 5/5 fichiers DICOM présents |

Vérifications par cas :

1. existence du PNG dans le projet ;
2. nom exact `B26_XX.png` ;
3. résolution vs `annotation_pilot/annotations/new_26/B26_XX.json` ;
4. correspondance `source_file` DICOM vs `meta/source_mapping.csv` ;
5. absence de confusion avec un autre fichier (MD5 unique, ID DICOM unique).

---

## Résultats détaillés

### B26_10

| Champ | Valeur |
|-------|--------|
| **Trouvée** | **OUI** |
| **Chemin canonique** | `datasets/yolo_pose_new_26/images/val/B26_10.png` |
| **Split dataset** | `val` |
| **Résolution attendue** | 3039 × 2625 |
| **Résolution trouvée** | 3039 × 2625 ✓ |
| **DICOM source** | `1.3.12.2.1107.5.3.63.40605.12.202608041057223734` |
| **MD5** | `2b259240ac2f10d8c8acb2ef23675fd5` |
| **Correspondance vérifiée** | **OUI** |
| **Action suivante** | Revue visuelle B6 — utiliser `images/val/B26_10.png` |

---

### B26_13

| Champ | Valeur |
|-------|--------|
| **Trouvée** | **OUI** |
| **Chemin canonique** | `datasets/yolo_pose_new_26/images/val/B26_13.png` |
| **Split dataset** | `val` |
| **Résolution attendue** | 3234 × 2961 |
| **Résolution trouvée** | 3234 × 2961 ✓ |
| **DICOM source** | `1.3.12.2.1107.5.3.63.40605.12.202608061241580770` |
| **MD5** | `f959a065c93d21ae07df2ee0b5baf176` |
| **Correspondance vérifiée** | **OUI** |
| **Action suivante** | Revue visuelle B6 — utiliser `images/val/B26_13.png` |

---

### B26_17

| Champ | Valeur |
|-------|--------|
| **Trouvée** | **OUI** |
| **Chemin canonique** | `datasets/yolo_pose_new_26/images/val/B26_17.png` |
| **Split dataset** | `val` |
| **Résolution attendue** | 2763 × 2442 |
| **Résolution trouvée** | 2763 × 2442 ✓ |
| **DICOM source** | `1.3.12.2.1107.5.3.63.40605.12.202608071737367434` |
| **MD5** | `95d0a011dc93653158fd32e64da4ced6` |
| **Correspondance vérifiée** | **OUI** |
| **Action suivante** | Revue visuelle B6 — utiliser `images/val/B26_17.png` |

---

### B26_20

| Champ | Valeur |
|-------|--------|
| **Trouvée** | **OUI** |
| **Chemin canonique** | `datasets/yolo_pose_new_26/images/val/B26_20.png` |
| **Split dataset** | `val` |
| **Résolution attendue** | 2701 × 2514 |
| **Résolution trouvée** | 2701 × 2514 ✓ |
| **DICOM source** | `1.3.12.2.1107.5.3.63.40605.12.202608121252227283` |
| **MD5** | `a5bd183a472c0fd78ae13fdff2f5d7e7` |
| **Correspondance vérifiée** | **OUI** |
| **Action suivante** | Revue visuelle B6 — utiliser `images/val/B26_20.png` |

---

### B26_26

| Champ | Valeur |
|-------|--------|
| **Trouvée** | **OUI** |
| **Chemin canonique** | `datasets/yolo_pose_new_26/images/val/B26_26.png` |
| **Split dataset** | `val` |
| **Résolution attendue** | 2822 × 2426 |
| **Résolution trouvée** | 2822 × 2426 ✓ |
| **DICOM source** | `1.3.12.2.1107.5.3.63.40605.12.202608161916140997` |
| **MD5** | `b7bf20b59c3643a23eb15c51f1218cb0` |
| **Correspondance vérifiée** | **OUI** |
| **Action suivante** | Revue visuelle B6 — utiliser `images/val/B26_26.png` |

---

## Copies secondaires (MD5 identique au canonique)

Toutes les copies listées ci-dessous sont **byte-identiques** au PNG canonique `images/val/` — pas de risque de confusion avec une autre radiographie.

| Image | Copies identiques |
|-------|-------------------|
| B26_10 | `annotation_pilot/.../cache/new_26/`, `predictions/`, `predictions_v2/`, `predictions_v3/`, `predictions_v4/` |
| B26_13 | idem |
| B26_17 | idem |
| B26_20 | idem |
| B26_26 | idem |

---

## Origine de la fausse alerte « PNG absent »

| Document B6 | Chemin recherché (erroné) | Chemin réel (canonique) |
|-------------|---------------------------|-------------------------|
| `b6_full_manual_review_queue.md` | `images/train/B26_XX.png` | `images/val/B26_XX.png` |
| `b6_remaining_21_QA.md` | « PNG absent localement » | PNG présent en `val/` |

Les `b6_working_annotations/B26_XX.json` pointent **déjà correctement** vers `images/val/B26_XX.png` pour ces 5 cas.

---

## Fichiers non modifiés

| Fichier | Modifié |
|---------|:-------:|
| Annotations (`b6_working_annotations/`, labels YOLO) | **Non** |
| `data.yaml` | **Non** |
| V2 / V3 | **Non** |
| Backend / Flutter | **Non** |
| PNG / DICOM (aucune copie) | **Non** |

---

## Prochaines étapes recommandées

1. **Mettre à jour la documentation B6** (hors scope actuel) : remplacer les références `images/train/` par `images/val/` pour ces 5 cas.
2. **Débloquer les 10 landmarks IMAGE_REQUIRED** : lancer revue visuelle B6 sur les PNG `val/`.
3. **Aucune restauration fichier nécessaire** — les originaux sont déjà en place.

*Export machine : `missing_images_recovery.csv`*
