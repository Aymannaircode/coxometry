# B6 — Revue finale supervisée IT_R — B26_26

**Généré :** 2026-08-29  
**Mode :** correction manuelle supervisée **ciblée IT_R uniquement**  
**Image :** `datasets/yolo_pose_new_26/images/val/B26_26.png` (2822 × 2426 px)  
**Décision finale IT_R :** **`UNRESOLVABLE_REVIEW`**

---

## Contexte

| Étape amont | IT_R | Verdict |
|-------------|------|---------|
| IMAGE_REQUIRED (2026-08-29) | (538, 2030) → (552, 2088) | MOVE LOW |
| QA formelle | (552, 2088) | REVIEW LOW |
| Revue supervisée ciblée | (552, 2088) | REVIEW LOW — conservé |
| **Revue finale supervisée** | **(552, 2088)** | **UNRESOLVABLE_REVIEW — conservé** |

IT_L (1998, 1998) — **hors scope** de cette session (PASS MEDIUM revue supervisée antérieure, non modifié).

---

## Contraintes respectées

- PNG original `B26_26.png` uniquement ;
- inspection pleine résolution + **6 vues locales** agrandies ;
- **aucune symétrie** ;
- **aucun offset** B26_01 ou autre ;
- **aucun calcul automatique** de coordonnées ;
- **aucune extrapolation** hors os visible ;
- **IT_L non utilisé** pour positionner IT_R ;
- labels YOLO, `data.yaml`, V2/V3, backend, Flutter — **inchangés** ;
- **aucun training** ;
- seul fichier modifié : `b6_working_annotations/B26_26.json`.

---

## Vues inspectées

| Vue | Paramètres | Observation |
|-----|------------|-------------|
| Bassin droit inférieur | pleine résolution, crop 55–100 % h | Zone ischiatique D localisable ; repère rouge dans région caudale latérale |
| Bande caudale | TD_R → bord FOV, contraste ×2.2 | Contour inférieur = gradient bruité ; pas de bord cortical net |
| Zoom tight | ±120 px, contraste ×2.5 | Bruit salt-and-pepper ; apex = transition floue gris→noir |
| Zoom medium | ±200 px, contraste ×2.0 | Même constat — pas de ligne corticale discernable |
| Zoom wide | ±320 px, contraste ×2.0 | Contexte fémur–ischion visible ; apex caudal non tranchable |
| Bande caudale brute | sans enhancement | Contraste très faible ; ombre tissus mous / artefact horizontal |

---

## Analyse IT_R — questions B1/B4

### 1. Point sur tubérosité ischiatique ?

**Partiellement.** Le repère (552, 2088) se situe dans la **zone anatomique attendue** de l'ischion D :

- médial au fémur (Δx FSD = 205 px — anti-fémur OK) ;
- caudal au TD (dy = +360 px) ;
- latéral au foramen / masse pelvienne caudale.

En revanche, le repère ne peut pas être affirmé comme étant **exactement sur le cortex caudal** — il se trouve dans une zone de transition densité osseuse / tissus mous où le bord n'est pas net.

### 2. Apex caudal identifiable ?

**Non.** Sur l'ensemble des zooms :

- pas de point de retournement cortical net ;
- transition os → fond = **gradient adouci** noyé dans le bruit ;
- bande artefact horizontale traverse la région ischiatique droite ;
- les vues contrastées ne révèlent pas un apex reproductible — seulement une zone floue de ~30–50 px de hauteur où l'apex pourrait se situer **n'importe où**, sans critère visuel discriminant.

Placer un point dans cette zone équivalait à **inventer** une position sur un gradient — refusé conformément à B1/B4 (« identifiable sans extrapolation »).

### 3. Contraste permet validation fiable ?

**Non.** Qualité locale **insuffisante** pour validation certaine :

| Critère | Évaluation |
|---------|:----------:|
| Bruit digital | Élevé |
| Contraste os/tissus | Faible |
| Bord cortical caudal | Indéterminable |
| Artefacts | Bande horizontale + plis tissus mous |

### 4. IT_L utilisé ?

**Non.** Validation IT_R strictement unilatérale.

---

## Coordonnées

| Champ | Valeur |
|-------|--------|
| **Ancienne coordonnée** | (552.0, 2088.0) |
| **Nouvelle coordonnée** | **(552.0, 2088.0)** — **inchangée** |
| **Δ** | — |
| **Correction appliquée** | **Non** |

**Motif conservation :** le contour caudal reste réellement indéterminable ; une annotation inventée sur un gradient bruité serait moins honnête que le maintien du statut REVIEW/LOW.

---

## Qualité du contour

| Attribut | Valeur |
|----------|--------|
| **Qualité contour caudal** | **INDETERMINATE** |
| Zone ischiatique globale | Localisable |
| Apex cortical strict | Non identifiable |
| Extrapolation requise pour placer apex | Oui (refusée) |

---

## Confiance et décision

| Champ | Valeur |
|-------|--------|
| **Verdict** | **REVIEW** |
| **Confiance** | **LOW** |
| **Décision finale** | **`UNRESOLVABLE_REVIEW`** |

```
UNRESOLVABLE_REVIEW ≠ FAIL structurel
→ structure cible (ischion D) plausible
→ apex caudal B1/B4 non validable avec certitude
→ coordonnées conservées
→ revue clinique humaine requise ou exclusion cas
```

---

## Historique `correction_history` (extrait IT_R)

Entrée ajoutée session `P1_FINAL_SUPERVISED` :

| Champ | Valeur |
|-------|--------|
| x_old / y_old | 552.0 / 2088.0 |
| x_new / y_new | 552.0 / 2088.0 |
| review_status | UNRESOLVABLE_REVIEW |
| confidence | LOW |
| reviewer | agent_B6_ITR_final_supervised |

---

## Recommandation

1. **Ne pas promouvoir IT_R** en l'état vers labels YOLO 16 kp.
2. Envisager **exclusion B26_26 IT_R** de la campagne B6 working si validation clinique impossible.
3. **IT_L** reste PASS MEDIUM (validation indépendante antérieure) — non remis en cause.
4. Toute future correction IT_R devra être effectuée **par annotateur clinique** avec outil interactif pleine résolution — pas par inférence automatique ou symétrie.

---

## Fichiers

| Fichier | Modifié |
|---------|:-------:|
| `b6_B26_26_ITR_final_review.md` | **Oui** |
| `b6_B26_26_ITR_final_review.csv` | **Oui** |
| `b6_working_annotations/B26_26.json` | **Oui** (historique + statut ; coordonnées IT_R inchangées) |
| Autres fichiers | **Non** |

*Export machine : `b6_B26_26_ITR_final_review.csv`*
