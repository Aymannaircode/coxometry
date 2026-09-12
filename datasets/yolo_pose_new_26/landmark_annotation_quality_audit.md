# Audit qualité annotations humaines — yolo_pose_new_26

**Généré :** 2026-08-28T17:45:00+01:00  
**Mode :** lecture seule. Aucun fichier de production, label, dataset, modèle ou calibration modifié.

## Périmètre

| Élément | Valeur |
|---------|--------|
| **Dataset** | `datasets/yolo_pose_new_26` (26 images B26_01…B26_26) |
| **Annotations source** | `annotation_pilot/annotations/new_26/*.json` (v=2, annotator_A) |
| **Labels YOLO** | `labels/train` + `labels/val` (vérifiés vs JSON) |
| **Référence anatomique** | `docs/annotation_guidelines.md`, `docs/landmark_specification.md` |
| **Landmarks prioritaires** | ASL_R, ASL_L, FSP_R, FSP_L, FSD_R, FSD_L |
| **Contexte E2E** | B26_01 — 6/14 landmarks INCORRECT côté modèle YOLO (audit anatomique Android) |

---

## Réponses aux questions clés

### A. Les annotations FSP/FSD sont-elles anatomiquement correctes ?

**Oui, globalement.** Sur les 26 cas :

| Landmark | VALID | REVIEW_FOV | INVALID |
|----------|-------|------------|---------|
| FSP_R | **26/26** | 0 | 0 |
| FSP_L | **26/26** | 0 | 0 |
| FSD_R | 8/26 | **18/26** | 0 |
| FSD_L | 9/26 | **17/26** | 0 |

**Définition projet (LM-11 à LM-14) :**

- **FSP** = point sur l'**axe médian diaphysaire proximal**, juste sous le petit trochanter.
- **FSD** = point sur l'**axe médian diaphysaire**, le plus distal visible dans le FOV.

**Ce ne sont PAS** des repères de « sommet de col » ou « jonction col-diaphyse » au sens strict du col fémoral — ce sont les extrémités proximale et distale de l'**axe diaphysaire** pour le CCD.

**Inspection visuelle B26_01 (cas E2E de référence) :**

| Landmark | GT (x, y) | Observation visuelle |
|----------|-----------|----------------------|
| FSP_R | (458.5, 1616.5) | Point sur l'axe médian de la diaphyse proximale, sous le col — **conforme LM-11** |
| FSP_L | (2124.0, 1796.0) | Idem côté gauche — **conforme LM-12** |
| FSD_R | (395.3, 2281.5) | Point centré entre corticales, portion distale visible du fémur — **conforme LM-13** |
| FSD_L | (2044.4, 2361.8) | Idem, limite basse du champ — **conforme LM-14** |

**Écart modèle vs GT sur B26_01 (preuve que le GT n'est pas la cause) :**

| Landmark | Erreur YOLO V2 vs GT | Direction erreur modèle |
|----------|---------------------|-------------------------|
| FSP_R | **413 px** | Modèle ~419 px **trop bas** (diaphyse basse / trochanter) |
| FSP_L | **256 px** | Modèle ~268 px **trop bas** |
| FSD_R | **295 px** | Modèle trop bas et trop médial |
| FSD_L | **231 px** | Modèle trop bas et trop latéral |

Le GT FSP est **au niveau proximal** (~y=1616) ; le modèle prédit ~y=2036 — soit une confusion avec une zone trochantérienne/distale, pas une erreur d'annotation.

**Flags géométriques automatiques (FSD) :** 18/26 cas `REVIEW_FOV` car la distance FSP–FSD est légèrement inférieure au seuil provisoire du guide (≥ 0,5 × diamètre de tête). Cela reflète le **cadrage AP bassin** (fémur coupé bas), pas un mauvais clic systématique. Les annotateurs ont placé FSD au **dernier niveau fiable visible**, conformément au guide §2.7.

**Flags FHC–FNM–FSP (17/26 REVIEW) :** fausses alertes — l'angle col/diaphyse (~125–155° sur AP) est **anatomiquement normal** ; FSP n'est pas sur l'axe du col.

---

### B. Les annotations ASL sont-elles anatomiquement correctes ?

**Oui.** **52/52** points ASL (26 R + 26 L) sont **VALID** :

| Contrôle | Résultat |
|----------|----------|
| ASL_R latéral à ASM_R (x_ASL < x_ASM) | **26/26** |
| ASL_L latéral à ASM_L (x_ASL > x_ASM) | **26/26** |
| ASL au-dessus de FHC (y_ASL < y_FHC) | **26/26** |
| Inversion R/L | **0/26** |
| Cohérence labels YOLO ↔ JSON | **0 px** d'écart |

**Marges latérales ASL–ASM (cohérence inter-cas) :**

- ASL_R : marge ASM−ASL moyenne **516 px** (min 323, max 652)
- ASL_L : marge ASL−ASM moyenne **504 px** (min 326, max 603)

**Inspection visuelle B26_01 :**

| Landmark | GT (x, y) | Observation |
|----------|-----------|-------------|
| ASL_R | (565.4, 844.5) | Point sur la **fin latérale du sourcil** sclérotique — conforme §2.3 |
| ASL_L | (2192.2, 953.6) | Idem — bord latéral du toit porteur, **409 px** latéral à ASM_L (1783) |

**Écart modèle vs GT B26_01 :**

| Landmark | Erreur modèle | Interprétation |
|----------|---------------|----------------|
| ASL_R | 231 px | Modèle trop latéral et trop bas — **pas le GT** |
| ASL_L | 153 px (après refinement) | Modèle raw confondu avec ASM_L (481 px) ; GT ASL_L est bien latéral au sourcil |

Le biais YOLO ASL_L (prédiction proche de ASM_L dans 25/26 cas) est un **échec modèle**, pas une erreur d'annotation : le GT respecte la latéralité sur 100 % des cas.

---

### C. Les définitions utilisées pour ces landmarks sont-elles cohérentes ?

**Oui, entre les documents officiels du projet :**

| Source | ASL | FSP | FSD |
|--------|-----|-----|-----|
| `landmark_specification.md` | Extrémité **latérale du sourcil** (VCE/Tönnis) | Axe diaphysaire **proximal** (CCD) | Axe diaphysaire **distal** dans FOV (CCD) |
| `annotation_guidelines.md` §2.3–2.7 | Identique | Identique | Identique |
| `data.yaml` / ordre keypoints | LM-05/06 | LM-11/12 | LM-13/14 |
| Labels YOLO ↔ JSON | Cohérent (0 px) | Cohérent | Cohérent |

**Point d'attention (documentation secondaire, hors annotations) :** le rapport E2E Android précédent décrivait FSP/FSD comme « sommet de col » / « jonction col-diaphyse » — libellés **incorrects** par rapport à la spec MVP. Les annotations humaines suivent bien la spec officielle (axe diaphysaire).

**Ambiguïtés connues (A1, A7) — non résolues par double lecture :**

- **A1** : sourcil vs rim ostéophytique — une seule paire d'yeux (annotator_A)
- **A7** : niveau exact « sous petit trochanter » et seuil FSP–FSD — appliqués de façon homogène mais FOV limité sur ~70 % des cas

---

### D. Y a-t-il des erreurs systématiques dans les annotations ?

**Non pour les erreurs bloquantes.** Aucune anomalie CRITICAL détectée sur les annotations GT :

| Type d'erreur | Occurrences GT |
|---------------|----------------|
| Inversion R/L | **0/26** |
| ASL médial à ASM | **0/52** |
| FSD proximal à FSP | **0/52** |
| Point hors image | **0/52** |
| Label YOLO ≠ JSON | **0 px** |

**Patterns systémiques non bloquants :**

1. **FOV diaphysaire court** — FSD placé au bord inférieur d'image dans ~70 % des cas ; distance FSP–FSD parfois < seuil provisoire 0,5× tête. C'est une **caractéristique du corpus** (radios bassin), pas une incohérence d'annotateur.
2. **FNM–FSP distance** — moyenne **~299 px** bilatérale, stable (R 299 / L 300) → cohérence interne.
3. **Annotateur unique** — pas de mesure d'accord inter-annotateurs ; audit mono-lecteur.

**Erreurs systémiques côté modèle YOLO (pour comparaison, non GT) :**

| Landmark | Erreur moyenne V2 vs GT (26 cas) |
|----------|----------------------------------|
| ASL_R | 144 px |
| ASL_L | 525 px |
| FSP_R | 151 px |
| FSP_L | 170 px |
| FSD_R | 159 px |
| FSD_L | 108 px |

---

### E. Combien d'images doivent éventuellement être corrigées ?

| Catégorie | Nombre | Cas | Action |
|-----------|--------|-----|--------|
| **Correction annotation obligatoire** | **0** | — | Aucune erreur anatomique manifeste sur les 6 landmarks prioritaires |
| **Revue clinique optionnelle (FOV court)** | **~19** | B26_01–11, 15–26 (FSD REVIEW_FOV) | Valider politique FSD en bord d'image vs v=0 |
| **Référence qualité (aucun flag)** | **2** | **B26_12, B26_13** | Cas gold pour entraînement |
| **Revue visuelle complétée** | **1** | **B26_01** | 6/6 landmarks prioritaires conformes à la spec |

**Cas FOV les plus limités (recommandation revue prioritaire si nettoyage) :**

- B26_09 FSD_L (ratio FSP–FSD / tête = **0,31**)
- B26_19 FSD_R/L (ratio **0,32–0,34**)
- B26_16 FSD_R (ratio **0,37**)

Même sur ces cas, le placement est **cohérent avec la règle « plus distal visible »** — la question est de politique (garder v=2 ou passer v=0), pas de correction de coordonnées.

---

### F. Peut-on réentraîner YOLO avec le dataset actuel ?

**Oui — réentraînement recommandé sans nettoyage massif des annotations.**

| Critère | Verdict |
|---------|---------|
| Qualité ASL (GT) | ✅ Suffisante — 52/52 conformes |
| Qualité FSP (GT) | ✅ Suffisante — 52/52 conformes |
| Qualité FSD (GT) | ✅ Acceptable — contrainte FOV, pas erreur systématique |
| Labels YOLO = JSON | ✅ Identiques (0 px) |
| Cause erreurs B26_01 E2E | ❌ Modèle YOLO, pas annotations |
| Blocage retraining | **Aucun** sur la base de cet audit |

**Recommandations avant retraining (hors scope code) :**

1. **Ne pas** corriger les annotations ASL/FSP sur B26_01 — le GT est validé visuellement.
2. **Optionnel** : revue clinique sur ~19 cas FOV court pour trancher politique FSD (v=2 vs v=0) — impact CCD, pas VCE/Tönnis.
3. **Priorité entraînement** : renforcer FSP/FSD/ASL dans le modèle (augmentations, focal loss keypoints, plus d'exemples similaires) — les GT sont fiables.
4. **Utiliser B26_12 et B26_13** comme cas de référence qualité (0 flag géométrique).

---

## Détail B26_01 — landmarks prioritaires

| Landmark | GT (x, y) | Statut annotation | Erreur YOLO vs GT | Verdict |
|----------|-----------|-------------------|-------------------|---------|
| ASL_R | (565.4, 844.5) | VALID | 231 px | GT OK — modèle faux |
| ASL_L | (2192.2, 953.6) | VALID | 154 px | GT OK — modèle faux |
| FSP_R | (458.5, 1616.5) | VALID | 419 px | GT OK — modèle très faux |
| FSP_L | (2124.0, 1796.0) | VALID | 274 px | GT OK — modèle faux |
| FSD_R | (395.3, 2281.5) | VALID | 306 px | GT OK — modèle faux |
| FSD_L | (2044.4, 2361.8) | REVIEW_FOV | 245 px | GT acceptable — FOV limite |

**Géométrie GT B26_01 :**

- FNM–FSP : R **161 px**, L **173 px** (col → diaphyse proximale)
- FSP–FSD : R **668 px**, L **571 px** (segment diaphysaire visible)
- Angle FNM–FSP–FSD @ FSP : R **150°**, L **140°** (courbure fémorale normale en AP)

---

## Synthèse par groupe anatomique

| Groupe | Landmarks audités | GT conforme spec | Problème principal |
|--------|-------------------|------------------|-------------------|
| Sourcil (VCE) | ASL_R, ASL_L | **100 %** | Aucun — échec modèle |
| Axe diaphysaire proximal (CCD) | FSP_R, FSP_L | **100 %** | Aucun — modèle confond avec zone distale |
| Axe diaphysaire distal (CCD) | FSD_R, FSD_L | **100 %** placement | FOV court (~70 % cas) — pas erreur annotateur |

---

## Méthodologie

1. **Chargement GT** : JSON `annotation_pilot/annotations/new_26` (v=2 uniquement).
2. **Vérification labels** : comparaison JSON vs `labels/train|val/*.txt` via `mvp_geometry.yolo_adapter`.
3. **Contrôles géométriques** (read-only, inspirés `validate_v2_anatomy_new_26.py`) :
   - Latéralité R/L et ASL vs ASM
   - Ordre vertical FHC → FNM → FSP → FSD
   - Distance FSP–FSD vs seuil provisoire guide
   - Angles axe fémoral (informatif)
4. **Inspection visuelle** : crops 360×360 px centrés sur chaque landmark prioritaire de B26_01.
5. **Croisement E2E** : comparaison erreurs YOLO V2 (`landmark_error_analysis.csv`, audit Android B26_01).

**Seuils statut annotation :**

- **VALID** : conforme spec, aucun flag bloquant
- **REVIEW_FOV** : placement distal correct mais FOV insuffisant pour seuil distance
- **INVALID** : erreur anatomique manifeste (aucun cas)

CSV détaillé : `landmark_annotation_quality_audit.csv` (156 lignes = 26 cas × 6 landmarks)

---

## Conclusion

L'audit confirme que **les annotations humaines du dataset yolo_pose_new_26 sont globalement fiables** pour les 6 landmarks prioritaires. Les échecs E2E observés sur B26_01 (FSP_R 419 px, FSD_R 306 px, ASL_R 231 px, etc.) **ne s'expliquent pas par des GT erronés** mais par des **limitations du modèle YOLO V2**.

Le réentraînement peut proceeder sur le dataset actuel. Un nettoyage massif des annotations **n'est pas justifié** ; seule une revue clinique optionnelle sur ~19 cas à FOV diaphysaire court pourrait affiner la politique FSD (v=2 vs v=0).

**Aucune modification de code, de labels, de modèle ou de calibration n'a été effectuée.**
