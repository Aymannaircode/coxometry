# Pilote B6 — annotation `IT_R` / `IT_L` sur **B26_01**

**Généré :** 2026-08-28  
**Mode :** pilote **NON-OFFICIEL** — **aucune modification** des labels YOLO, JSON officiels, `data.yaml`, modèles ou code  

**Coordonnées pilote (NON-OFFICIAL) :** `B6_pilot_B26_01_coords.json`

---

## Contexte

| Élément | Valeur |
|---------|--------|
| **Image** | `B26_01` — `images/train/B26_01.png` |
| **Dimensions** | 2730 × 2665 px |
| **Visibilité B7** | VISIBLE / VISIBLE — qualité **EXCELLENTE** |
| **Cas** | Standard facile (référence pilote B6) |
| **Labels officiels** | **14 kp inchangés** — `labels/train/B26_01.txt`, `annotation_pilot/annotations/new_26/B26_01.json` |

### Définition de travail appliquée

> **`IT_R` / `IT_L` = point caudal/inférieur identifiable du contour osseux de chaque tubérosité ischiatique sur la radiographie AP du bassin.**

| Attribut | Valeur |
|----------|--------|
| **STATUS** | **PROPOSED / CLINICAL VALIDATION REQUIRED** |
| **Validité** | Pilote de reproductibilité — **pas** validation clinique définitive |

---

## Coordonnées proposées (PILOT)

| Landmark | x (px) | y (px) | x norm | y norm | v | Côté patient | Position image |
|----------|-------:|-------:|-------:|-------:|:-:|--------------|----------------|
| **`IT_R`** | **548.0** | **2140.0** | 0.2007 | 0.8030 | 2 | Droit | Gauche |
| **`IT_L`** | **1756.0** | **2143.0** | 0.6432 | 0.8041 | 2 | Gauche | Droite |

### Relations avec `TD_*` (officiels — non modifiés)

| Paire | Distance (px) | Δx | Δy | Interprétation |
|-------|--------------:|---:|---:|----------------|
| `IT_R` ↔ `TD_R` | 455.8 | −380.9 | +250.3 | IT latéral et **caudal** au teardrop ✓ |
| `IT_L` ↔ `TD_L` | 250.5 | +163.6 | +189.7 | IT latéral et **caudal** au teardrop ✓ |

**Aucune coïncidence** `IT_*` / `TD_*` — distances > 250 px des deux côtés.

---

## 1. Identification `IT_R` et `IT_L`

### `IT_R` (droite patient — gauche image)

- **Structure :** tubérosité ischiatique droite.
- **Repère :** point le plus **caudal** du contour osseux dense de la tubérosité, latéral au foramen obturé droit.
- **Confiance pilote :** **élevée** — bord cortical inférieur net, marge caudale confortable (B7).

### `IT_L` (gauche patient — droite image)

- **Structure :** tubérosité ischiatique gauche.
- **Repère :** point le plus **caudal** du contour osseux sur le bord inférieur de l'hémipelvis gauche, latéral au foramen obturé gauche.
- **Confiance pilote :** **modérée à élevée** — repère caudal identifiable ; **attention** à ne pas confondre avec la diaphyse fémorale plus latérale (voir §6).

---

## 2. Justification anatomique

| Critère | `IT_R` | `IT_L` |
|---------|--------|--------|
| Structure cible | Tubérosité ischiatique | Tubérosité ischiatique |
| Point sur contour osseux | Oui — bord cortical caudal | Oui — bord cortical caudal |
| Point caudal/inférieur | y = 2140 (max caudal local) | y = 2143 (max caudal local) |
| Distinction teardrop | TD médial et proximal | TD médial et proximal |
| Distinction fémur | IT médial à `FSD_R` (x=395) | IT médial à `FSD_L` (x=2044) |
| Symétrie caudale | Δy R/L = **3 px** (~0,1 % hauteur) | Cohérent cliché peu incliné |

**Construction `BI_ISCHIAL` (pilote) :** droite passant par (548, 2140) et (1756, 2143) — pente quasi horizontale (Δy = 3 px sur Δx = 1208 px).

---

## 3. Vérifications demandées

| # | Objectif | Résultat pilote |
|---|----------|-----------------|
| 1 | Identifier IT_R et IT_L | **OK** — deux points placés |
| 2 | Reproductibilité définition | **OK avec réserves** — voir §5 |
| 3 | TD jamais utilisés comme IT | **OK** — coordonnées distinctes ; IT latéral + caudal vs TD |
| 4 | Convention R/L | **OK** — IT_R x=548 (< centre 1365), IT_L x=1756 (> centre) ; marqueur « R » image cohérent |
| 5 | Points sur tubérosité ischiatique | **OK** IT_R ; **OK avec vigilance** IT_L (rejet candidat fémoral) |
| 6 | Ambiguïtés documentées | **Oui** — §6 |

---

## 4. Difficultés rencontrées

| Difficulté | Détail | Impact |
|------------|--------|--------|
| **Piège latéral `IT_L`** | Premier candidat automatique (2136, 2117) sur **diaphyse fémorale** | Élevé — sans guide illustré, erreur probable |
| **Courbure large** | Contour caudal étendu sur plusieurs pixels | Faible sur B26_01 — bord net |
| **Cortical vs centre** | Définition impose contour osseux, pas centre géométrique | Faible ici — cortex visible |
| **Validation clinique absente** | Définition PROPOSED | Bloquant pour figer B1, pas pour pilote |

---

## 5. Reproductibilité estimée

| Landmark | Estimation | Commentaire |
|----------|------------|-------------|
| **`IT_R`** | **Élevée (≈ 85–90 %)** | Cas B7 EXCELLENT ; repère caudal net ; marge confortable |
| **`IT_L`** | **Modérée à élevée (≈ 70–80 %)** | Repère caudal identifiable ; risque de glissement vers fémur si trop latéral |
| **Bilatéral** | **Élevée sur cas standard** | B26_01 conforme au profil « facile » B7 |

**Inter-annotateurs (hypothèse) :** dispersion estimée ± 8–15 px sur le contour caudal pour un annotateur formé ; ± 20–40 px sans formation sur le piège fémoral côté L.

---

## 6. Ambiguïtés documentées

| Code | Sujet | Observation B26_01 | STATUS |
|------|-------|-------------------|--------|
| **A-IT01** | Piège fémoral `IT_L` | Candidat x=2136 rejeté (fémur) | **CLINICAL VALIDATION REQUIRED** — illustration recommandée |
| **A-IT02** | Cortical vs centre | Contour caudal retenu | **PROPOSED** — cohérent définition travail |
| **A-IT03** | Courbure étendue | Plusieurs pixels caudaux proches (y=2141–2143) | Faible ambiguïté sur ce cas |
| **A-IT04** | Symétrie x R/L | IT_R plus latéral (x=548) que IT_L relatif au centre | Anatomie / rotation — pas d'erreur R/L |
| **A-IT05** | B7 ≠ définition B1 | Visibilité excellente confirme faisabilité, pas validation anatomique | Documenté |

---

## 7. Problèmes éventuels pour extension B6 (25 autres images)

| Problème | Risque | Mitigation proposée |
|----------|--------|-------------------|
| Confusion IT / fémur (surtout L) | **Élevé** | Guide illustré ; contrôle distance TD + anatomie |
| Bord image (B26_05) | **Élevé** | Revue clinique obligatoire |
| Superposition / gaz | Modéré | `v=0` si doute |
| Définition non validée | **Bloquant B1** | Pilote OK pour tester, pas pour production sans validation |

---

## 8. Candidats rejetés (traçabilité pilote)

| Nom | x | y | Motif rejet |
|-----|--:|--:|-------------|
| `IT_L_auto` | 2136 | 2117 | Trop latéral — diaphyse fémorale gauche, non tubérosité |

---

## 9. Décision pilote

```
Décision = READY_FOR_B6
```

### Motivation

| Pour | Contre |
|------|--------|
| Définition de travail **applicable** sur le cas standard B26_01 | Définition toujours **PROPOSED** — validation clinique requise |
| `IT_R` reproductible avec confiance élevée | `IT_L` sensible au piège fémoral |
| TD ≠ IT vérifié | Illustrations cliniques encore absentes |
| R/L et position caudale cohérents | B26_05 et cas limites non testés dans ce pilote |

### Conditions avant campagne B6 complète

1. **Validation clinique** de la définition de travail (B1) sur ce pilote + overlay.
2. **Illustration** du piège fémoral `IT_L` (comparaison candidat rejeté vs retenu).
3. **Revue particulière B26_05** avant annotation production.
4. **Ne pas intégrer** ces coordonnées dans les labels YOLO officiels tant que B5/B6 formels non ouverts.

### Si validation clinique rejette les coordonnées

→ Repasser en **SPECIFICATION_REVIEW_REQUIRED** et ajuster la définition ou le guide B4.

---

## 10. Fichiers et intégrité dataset

| Fichier | Modifié ? |
|---------|:---------:|
| `labels/train/B26_01.txt` | **Non** |
| `annotation_pilot/annotations/new_26/B26_01.json` | **Non** |
| `data.yaml` | **Non** |
| Modèles V2 / V3 | **Non** |
| Backend / Flutter | **Non** |

**Fichiers pilote créés (NON-OFFICIAL) :**

- `B6_pilot_B26_01.md` (ce rapport)
- `B6_pilot_B26_01_coords.json` (coordonnées pilote)

---

*Pilote B6 B26_01 — dataset officiel inchangé.*
