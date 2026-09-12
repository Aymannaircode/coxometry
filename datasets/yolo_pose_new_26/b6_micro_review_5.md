# B6 — Micro-revue READ-ONLY (5 landmarks REVIEW)

**Généré :** 2026-08-28  
**Mode :** micro-revue **READ-ONLY** — aucune modification de coordonnées, labels, `data.yaml`, V2/V3  
**Contexte amont :** QA formel des 9 corrections → 4 PASS / 5 REVIEW / 0 FAIL  
**Landmarks examinés :** B26_05 IT_R, B26_05 IT_L, B26_07 IT_R, B26_11 IT_R, B26_11 IT_L  

**Définition B1 évaluée :**

> `IT_R` / `IT_L` = point caudal/inférieur identifiable du contour osseux de chaque tubérosité ischiatique sur AP bassin.

**Méthode :**

1. Radiographie PNG originale pleine résolution (`images/train/B26_XX.png`, 2871–3008 px).
2. Vue locale agrandie (crop ~280 px, ×4) + vue pelvienne (~500×400 px, ×2) autour de chaque point.
3. Superposition repères officiels `TD_*` (jaune) et `FSD_*` (vert) pour anti-fémur — **non modifiés**.
4. Mesures complémentaires : marge caudale FOV, distance IT–TD, Δx IT–FSD, score contraste os local.

**Aucun fichier d'annotation, label officiel ou config n'a été modifié.**

---

## Synthèse exécutive

| Verdict | N |
|---------|--:|
| **PASS** | **0** |
| **REVIEW** | **5** |
| **FAIL** | **0** |

| Confiance | N |
|-----------|--:|
| HIGH | 0 |
| MEDIUM | 2 |
| LOW | 3 |

| Recommandation | N |
|----------------|--:|
| KEEP | 2 |
| MANUAL_REVIEW | 3 |
| CORRECTION_REQUIRED | 0 |

**Décision micro-revue :** les 5 landmarks **restent en REVIEW**. Aucun n'est reclassé PASS (ambiguïtés FOV, gaz ou contraste non levées). Aucun FAIL (structure pelvienne plausible, anti-fémur et R/L cohérents sur les 5).

---

## B26_05 — IT_R

| Champ | Valeur |
|-------|--------|
| **Verdict** | **REVIEW** |
| **Confiance** | **MEDIUM** |
| **Coordonnées actuelles** | **(648.0, 2955.0)** |
| **Recommandation** | **KEEP** |

### Justification anatomique

- Point sur le **bord cortical caudal** de l'ischion droit (gauche image), **médial** à `FSD_R` (Δx = +106 px) — règle anti-fémur respectée.
- **Caudal** à `TD_R` (1429, 2237) : Δy ≈ +719 px ; distance IT–TD ≈ 1061 px — pas de substitution TD.
- `IT_R` à gauche de l'image (x = 648 < 1504) — **R/L OK**.
- Correction post-QA effective : sorti de la zone tissus mous (705, 2892) vers cortex osseux visible dans le FOV.

### Vérifications (9 axes)

| Axe | Résultat |
|-----|----------|
| Contour osseux tubérosité | Cortex ischiatique identifiable ; bord caudal frôle le FOV |
| Définition B1 | Placement conservateur sur dernier contour osseux **visible** sans extrapolation |
| Pas sur fémur | OK — médial à la diaphyse (`FSD_R` x = 541) |
| R/L | OK |
| TD ≠ IT | OK (dist ≈ 1061 px) |
| FOV | **PARTIAL** — marge caudale **53 px** (1,76 % hauteur) ; A-FOV05 |
| Ambiguïté | **Anatomique + FOV** — apex réel possible ~20 px plus bas au contact bord image ; dispersion documentée ~110 px |

### Problème restant

Cas limite **PARTIAL bilatéral** du corpus. Le point est le choix conservateur « dans FOV » le plus caudal net, mais l'apex cortical absolu n'est pas tranchable avec certitude HIGH (cortex touche le bord inférieur de l'image). `v=2` défendable ; `v=0` également documenté.

---

## B26_05 — IT_L

| Champ | Valeur |
|-------|--------|
| **Verdict** | **REVIEW** |
| **Confiance** | **MEDIUM** |
| **Coordonnées actuelles** | **(2395.0, 2958.0)** |
| **Recommandation** | **KEEP** |

### Justification anatomique

- Replacé depuis position fémorale (2472, 2876) vers ischion G **médial** au fémur (Δx vs `FSD_L` = −196 px) — correction structurelle confirmée visuellement.
- Caudal à `TD_L` (1943, 2177) : Δy ≈ +781 px ; distance IT–TD ≈ 903 px.
- `IT_L` à droite image (x = 2395 > 1504) — **R/L OK**.
- Symétrie bilatérale y avec IT_R (Δy = 3 px).

### Vérifications (9 axes)

| Axe | Résultat |
|-----|----------|
| Contour osseux tubérosité | Silhouette ischiatique latérale reconnaissable ; contraste local faible |
| Définition B1 | Apex caudal plausible dans FOV ; légèrement plus confortable que côté R |
| Pas sur fémur | OK — correction explicite hors diaphyse |
| R/L | OK |
| TD ≠ IT | OK |
| FOV | **PARTIAL** — marge caudale **50 px** (1,66 %) |
| Ambiguïté | **FOV + qualité d'image** — contraste os local faible (bone ≈ 9) ; scan apex +47 px vers bord |

### Problème restant

Même tension FOV que IT_R. Contraste local plus faible que côté droit. Validation clinique optionnelle pour trancher apex ±20–50 px au bord, mais **aucune correction coordonnée requise** sans avis clinique.

---

## B26_07 — IT_R

| Champ | Valeur |
|-------|--------|
| **Verdict** | **REVIEW** |
| **Confiance** | **LOW** |
| **Coordonnées actuelles** | **(708.0, 2548.0)** |
| **Recommandation** | **MANUAL_REVIEW** |

### Justification anatomique

- Relations spatiales **cohérentes** : médial à `FSD_R` (Δx = +275 px), caudal à `TD_R` (Δy ≈ +407 px), distance IT–TD ≈ 549 px.
- `IT_R` côté gauche image — **R/L OK**.
- Correction post-QA : repositionné depuis gap tissus mous / zone gaz (640, 2431) vers silhouette ischiatique (+117 px y).

### Vérifications (9 axes)

| Axe | Résultat |
|-----|----------|
| Contour osseux tubérosité | **Non confirmable** en vue locale — gaz intestinal central (A-GAS07) masque le contraste |
| Définition B1 | Placement **plausible** sur silhouette ischiatique caudale ; contact cortical **non prouvé** |
| Pas sur fémur | OK spatialement (médial à diaphyse) |
| R/L | OK |
| TD ≠ IT | OK |
| FOV | OK — marge caudale 139 px (5,17 %) |
| Ambiguïté | **Qualité d'image** (gaz) — pas d'ambiguïté anatomique majeure ; opacité empêche validation osseuse directe |

### Problème restant

Vue agrandie : bruit élevé, pas de bord cortical net sous le crosshair. Le repère peut chevaucher une zone radiolucide adjacente au fémur plutôt que le cortex ischiatique strict. **Confirmation radiologique recommandée** avant PASS. IT_L du même cas est PASS (repère latéral moins obscurci).

---

## B26_11 — IT_R

| Champ | Valeur |
|-------|--------|
| **Verdict** | **REVIEW** |
| **Confiance** | **LOW** |
| **Coordonnées actuelles** | **(632.0, 2498.0)** |
| **Recommandation** | **MANUAL_REVIEW** |

### Justification anatomique

- Anti-fémur : Δx vs `FSD_R` = +321 px (médial) ; caudal à `TD_R` ; distance IT–TD ≈ 659 px.
- `IT_R` côté gauche image — **R/L OK** malgré rotation légère (A-ROT11).
- Correction : apex caudal (+199 px y) depuis position trop crâniale (567, 2299).

### Vérifications (9 axes)

| Axe | Résultat |
|-----|----------|
| Contour osseux tubérosité | Contour **à peine visible** ; courbure caudale suggérée en vue élargie |
| Définition B1 | Point sur transition densité la plus caudale **identifiable** — confiance limitée |
| Pas sur fémur | OK — x = 632 vs `FSD_R` x = 311 |
| R/L | OK (annoté indépendamment sous rotation) |
| TD ≠ IT | OK |
| FOV | OK — marge 72 px (2,8 %) |
| Ambiguïté | **Qualité d'image** (contraste très faible, bone ≈ 5) + **rotation légère** |

### Problème restant

Contraste os local parmi les plus faibles du lot. Impossible de confirmer le contact cortical exact vs tissu mou adjacent. Cohérence bilatérale y avec IT_L (2498 vs 2495) rassurante mais insuffisante pour PASS formel.

---

## B26_11 — IT_L

| Champ | Valeur |
|-------|--------|
| **Verdict** | **REVIEW** |
| **Confiance** | **LOW** |
| **Coordonnées actuelles** | **(1958.0, 2495.0)** |
| **Recommandation** | **MANUAL_REVIEW** |

### Justification anatomique

- Médial à `FSD_L` (Δx = −518 px) ; caudal à `TD_L` ; distance IT–TD ≈ 516 px.
- `IT_L` côté droite image (x = 1958) — **R/L OK**.
- Correction : apex caudal indépendant (+242 px y) malgré rotation pelvienne.

### Vérifications (9 axes)

| Axe | Résultat |
|-----|----------|
| Contour osseux tubérosité | Bord diagonal faiblement visible ; bruit élevé en zoom |
| Définition B1 | Placement sur transition densité caudale plausible |
| Pas sur fémur | OK |
| R/L | OK |
| TD ≠ IT | OK |
| FOV | OK — marge 75 px (2,92 %) |
| Ambiguïté | **Qualité d'image** (bone ≈ 6) + **rotation** (A-ROT11) |

### Problème restant

Même profil que IT_R : silhouette ischiatique probable, validation corticale impossible en auto. Symétrie y bilatérale (Δy = 3 px) ne compense pas l'incertitude locale.

---

## Tableau récapitulatif

| Image | Landmark | x | y | Verdict | Conf. | Structure | R/L | IT≠TD | Anti-fémur | FOV | Ambiguïté dominante | Recommandation |
|-------|----------|--:|--:|---------|:-----:|:---------:|:---:|:-----:|:----------:|:---:|:-------------------:|:--------------:|
| B26_05 | IT_R | 648.0 | 2955.0 | REVIEW | MEDIUM | OK | OK | OK | OK | PARTIAL | FOV + anatomique | KEEP |
| B26_05 | IT_L | 2395.0 | 2958.0 | REVIEW | MEDIUM | OK | OK | OK | OK | PARTIAL | FOV + contraste | KEEP |
| B26_07 | IT_R | 708.0 | 2548.0 | REVIEW | LOW | Plausible | OK | OK | OK | OK | Gaz (qualité) | MANUAL_REVIEW |
| B26_11 | IT_R | 632.0 | 2498.0 | REVIEW | LOW | Plausible | OK | OK | OK | OK | Contraste + rotation | MANUAL_REVIEW |
| B26_11 | IT_L | 1958.0 | 2495.0 | REVIEW | LOW | Plausible | OK | OK | OK | OK | Contraste + rotation | MANUAL_REVIEW |

---

## Comptage final

| Métrique | Valeur |
|----------|--------|
| **PASS** | **0** |
| **REVIEW** | **5** |
| **FAIL** | **0** |

---

## Faisabilité QA des 52 cas

**Les 5 points ne sont pas suffisamment fiables pour un PASS formel unanime**, conformément au QA amont (4 PASS / 5 REVIEW / 0 FAIL).

En revanche, la micro-revue confirme :

- **0 FAIL structurel** — aucun point sur fémur, R/L correct, TD ≠ IT sur les 5.
- **Corrections manuelles maintenues** — B26_05 (KEEP ×2) ; pas de régression identifiée.
- **3 points nécessitent une revalidation clinique** (B26_07 IT_R, B26_11 IT_R/L) avant intégration définitive.

### Recommandation workflow

| Option | Conduite |
|--------|----------|
| **Stricte** | Ne pas lancer le QA des 52 tant que les 3 MANUAL_REVIEW ne sont pas levés ; B26_05 accepté comme cas référence PARTIAL documenté. |
| **Pragmatique** | Lancer le QA des 52 **en parallèle** sur les 21 cas restants, en conservant les 5 landmarks en statut REVIEW documenté ; spot-check radiologique ciblé sur B26_11 R/L (priorité confiance LOW). |

**Position micro-revue :** les 5 landmarks sont **utilisables comme annotations de travail B6** (pas d'erreur structurelle majeure), mais **pas comme références PASS** pour clore la campagne des 9 corrections. Le passage au QA des 52 est **conditionnel** à l'acceptation formelle du statut REVIEW résiduel ou à la levée des 3 MANUAL_REVIEW.

---

## Intégrité projet

| Élément | Modifié ? |
|---------|:---------:|
| Coordonnées | **Non** |
| Labels officiels | **Non** |
| `data.yaml` | **Non** |
| V2 / V3 | **Non** |
| Entraînement | **Non lancé** |

**Fichiers créés uniquement :**

- `b6_micro_review_5.md` (ce rapport)
- `b6_micro_review_5.csv`

---

*Micro-revue B6 — 5 landmarks REVIEW — READ-ONLY.*
