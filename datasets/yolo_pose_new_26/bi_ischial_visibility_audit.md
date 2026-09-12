# Audit read-only B7 — Visibilité `IT_R` / `IT_L` sur corpus `new_26`

**Généré :** 2026-08-28  
**Mode :** audit read-only — **aucune modification** du dataset, labels, YAML, modèles, annotations ou code  
**Corpus :** 26 radiographies AP bassin adulte `B26_01` … `B26_26`  
**Répertoire :** `datasets/yolo_pose_new_26/`  
**Référence spec :** `bi_ischial_spec.md` (décision B7)

---

## Méthode

| Élément | Détail |
|---------|--------|
| Images inspectées | 26 PNG (`images/train/` n=21, `images/val/` n=5) |
| Convention R/L | `IT_R` = droit patient (gauche image) ; `IT_L` = gauche patient (droite image) |
| Échelle de visibilité | **VISIBLE** · **PARTIELLE** · **NON VISIBLE** · **INCERTAINE** |
| Landmarks placés | **Aucun** — inspection visuelle uniquement |
| Labels modifiés | **Aucun** |
| Complément objectif | Position `FSD_*` (labels 14 kp existants) comme proxy FOV inférieur ; métadonnées `fov_diaphysis_insufficient_*` = `null` sur les 26 JSON |

**Critères appliqués :**

- **VISIBLE** : contour osseux caudal de la tubérosité ischiatique identifiable ; repère annotable en `v=2` sans extrapolation.
- **PARTIELLE** : tubérosité présente mais repère caudal moins confortable (proximité bord image, contour partiel).
- **NON VISIBLE** : structure absente, coupée ou non identifiable.
- **INCERTAINE** : doute persistant nécessitant revue clinique.

---

## Résultats par image

| Image | Split | IT_R | IT_L | Qualité globale | Raison problème | Revue manuelle |
|-------|-------|------|------|-----------------|-----------------|:--------------:|
| B26_01 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_02 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_03 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_04 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_05 | train | **PARTIELLE** | **PARTIELLE** | MOYENNE | bord de l'image | **Oui** |
| B26_06 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_07 | train | VISIBLE | VISIBLE | BONNE | autre (gaz intestinal central) | **Oui** |
| B26_08 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_09 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_10 | val | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_11 | train | VISIBLE | VISIBLE | BONNE | autre (rotation pelvienne légère) | **Oui** |
| B26_12 | train | VISIBLE | VISIBLE | BONNE | bord de l'image (marge réduite) | **Oui** |
| B26_13 | val | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_14 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_15 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_16 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_17 | val | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_18 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_19 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_20 | val | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_21 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_22 | train | VISIBLE | VISIBLE | BONNE | autre (gaz intestinal haut) | Non |
| B26_23 | train | VISIBLE | VISIBLE | BONNE | autre (crête iliaque sup. coupée) | Non |
| B26_24 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_25 | train | VISIBLE | VISIBLE | EXCELLENTE | — | Non |
| B26_26 | val | VISIBLE | VISIBLE | EXCELLENTE | — | Non |

**CSV détaillé :** `bi_ischial_visibility_audit.csv`

---

## Statistiques globales (N = 26)

| Métrique | N | % |
|----------|---:|---:|
| **IT_R = VISIBLE** | 25 | **96,2 %** |
| **IT_L = VISIBLE** | 25 | **96,2 %** |
| **IT_R et IT_L tous deux VISIBLE** | 25 | **96,2 %** |
| IT_R = PARTIELLE | 1 | 3,8 % |
| IT_L = PARTIELLE | 1 | 3,8 % |
| IT_R ou IT_L = NON VISIBLE | 0 | 0 % |
| IT_R ou IT_L = INCERTAINE | 0 | 0 % |
| **Annotables (VISIBLE + PARTIELLE)** — IT_R | 26 | **100 %** |
| **Annotables (VISIBLE + PARTIELLE)** — IT_L | 26 | **100 %** |
| **Annotables bilatéralement** | 26 | **100 %** |
| Images problématiques (PARTIELLE ou pire, au moins un côté) | 1 | 3,8 % |
| Qualité EXCELLENTE | 20 | 76,9 % |
| Qualité BONNE | 5 | 19,2 % |
| Qualité MOYENNE | 1 | 3,8 % |

---

## Images problématiques et revue manuelle

### Cas problématique (visibilité dégradée)

| Image | Problème | Détail |
|-------|----------|--------|
| **B26_05** | bord de l'image | Seul cas **PARTIELLE / PARTIELLE** — tubérosités visibles mais très proches du bord caudal ; repère caudal moins confortable |

### Liste exacte — revue manuelle recommandée

| Image | Motif |
|-------|-------|
| **B26_05** | PARTIELLE bilatérale — confirmer repère caudal vs `v=0` |
| **B26_07** | Gaz intestinal central abondant — confirmer que le repère IT reste fiable |
| **B26_11** | Rotation pelvienne légère — confirmer cohérence R/L |
| **B26_12** | Marge caudale réduite — confirmer annotabilité en `v=2` |

**Aucune image** ne requiert exclusion du corpus sur la base de visibilité **NON VISIBLE**.

---

## Observations FOV (proxy `FSD_*`)

Les labels existants placent `FSD_*` souvent entre **94 % et 99 %** de la hauteur image (diaphyse basse proche du bord), alors que les tubérosités ischiatiques se situent **plus proximalement** (~80–92 % typiquement). Conséquence :

- FOV **serré en bas** pour la diaphyse fémorale (contexte A7 documenté pour `FSD`) ;
- Tubérosités ischiatiques **généralement encore visibles** sur ce corpus AP bassin ;
- **Exception notable :** `B26_05` (marge caudale minimale pour les ischions).

Aucune annotation `fov_diaphysis_insufficient_R/L` n'est renseignée dans les JSON `new_26` (toutes `null`).

---

## Conclusions (questions B7)

### 1. Le corpus `new_26` est-il suffisamment adapté à l'ajout de `IT_R` / `IT_L` ?

**Oui, globalement.** Sur 26 radiographies AP bassin adulte :

- **100 %** des images permettent au minimum une annotation **PARTIELLE** bilatérale ;
- **96,2 %** atteignent une visibilité **VISIBLE** stricte des deux côtés ;
- **1 cas** (`B26_05`) nécessite une attention particulière (bord de l'image).

Le corpus est **adapté** à une extension 16 keypoints + ré-annotation pilote, sous réserve de finaliser **B1** (position exacte sur tubérosité) et **B4** (fiches annotation).

### 2. Combien de radios peuvent être annotées de façon fiable ?

| Niveau | Nombre | % |
|--------|--------|---|
| Fiable stricte (`v=2` attendu, VISIBLE bilatéral) | **25** | **96,2 %** |
| Annotable avec prudence (PARTIELLE ≥1 côté) | **1** (`B26_05`) | 3,8 % |
| Non annotable | **0** | 0 % |

**Recommandation :** viser **25 cas haute confiance** + **1 revue clinique** (`B26_05`) avant figer les labels IT.

### 3. Les 26 radios doivent-elles toutes être conservées ?

**Oui.** Aucune image ne présente `IT_R` ou `IT_L` **NON VISIBLE**. Exclure un cas n'est **pas justifié** par cet audit. `B26_05` doit être **conservée** avec politique explicite (`v=2` si validé en revue, sinon `v=0` côté concerné).

### 4. Faut-il prévoir une politique « non visible / non annotable » ?

**Oui, obligatoirement** — conformément à :

- `annotation_guidelines.md` §1.2 (`v=0` si non fiable) ;
- `bi_ischial_spec.md` (B4, validité) ;
- présent audit : cas limites (`B26_05`, revues manuelles).

**Politique recommandée (audit, non implémentée) :**

| Situation | Conduite |
|-----------|----------|
| Tubérosité nette, repère caudal identifiable | `v=2` |
| Tubérosité partielle / bord image / doute | `v=0` **ou** revue clinique préalable — **pas** de point inventé |
| Un seul côté `v=0` | `BI_ISCHIAL` non calculable ce cliché (2 points requis) |
| Gaz intestinal / rotation | Annoter si os visible ; sinon `v=0` |

### 5. Y a-t-il un risque important de biais lié au FOV ?

**Risque modéré, non bloquant pour ce corpus, mais à documenter.**

| Facteur | Évaluation |
|---------|------------|
| Coupure ischions par bord image | **Faible** — 0/26 NON VISIBLE ; 1/26 PARTIELLE |
| FOV bas serré (fémur au bord) | **Fréquent** — `FSD` souvent > 95 % hauteur ; **n'empêche pas** la visualisation des ischions sur ce lot |
| Variabilité marge caudale | **Présente** — de généreux (`B26_17`, `B26_18`) à serrés (`B26_05`, `B26_12`) |
| Biais entraînement futur | **Modéré** — si le modèle apprend IT sur AP bassin standard, performance sur FOV plus courts pourrait dégrader ; prévoir `v=0` à l'annotation et QC FOV en inférence |

**Verdict FOV :** pas de biais **majeur** identifié sur `new_26` ; surveiller les clichés à marge caudale minimale lors de la ré-annotation (B6).

---

## Synthèse exécutive

```
Corpus new_26 — visibilité IT_R / IT_L (audit B7)
─────────────────────────────────────────────────
IT_R VISIBLE          : 25/26 (96,2 %)
IT_L VISIBLE          : 25/26 (96,2 %)
IT_R + IT_L VISIBLE   : 25/26 (96,2 %)
Annotables (≥PARTIELLE): 26/26 (100 %)
NON VISIBLE           : 0/26
Revue manuelle        : B26_05, B26_07, B26_11, B26_12
Décision B7           : FERMÉE (audit réalisé)
Blocage restant       : B1, B2, B3, B4, B5, B6 (hors visibilité)
```

**Décision B7 :** le corpus AP bassin `new_26` **supporte** l'ajout de `IT_R`/`IT_L` ; l'extension 14 → 16 keypoints n'est **pas** limitée par la visibilité sur ce lot, sous réserve de la politique `v=0` et de la revue des 4 cas signalés.

---

*Audit read-only — aucun fichier du projet modifié (dataset, labels, YAML, modèles, annotations).*
