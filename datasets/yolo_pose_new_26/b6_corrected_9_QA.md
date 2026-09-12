# B6 — QA formel READ-ONLY des 9 landmarks corrigés

**Généré :** 2026-08-28  
**Mode :** QA **READ-ONLY** — aucune annotation modifiée  
**Statut amont :** `MANUAL_CORRECTION_COMPLETED / QA_REQUIRED`  
**Sources :** `b6_manual_corrections_log.csv`, `b6_working_annotations/`, `bi_ischial_annotation_guidelines.md`

---

## Périmètre

| Image | Landmarks QA |
|-------|--------------|
| B26_24 | IT_R, IT_L |
| B26_01 | IT_L |
| B26_05 | IT_R, IT_L |
| B26_07 | IT_R, IT_L |
| B26_11 | IT_R, IT_L |

**Total : 9 landmarks** (coordonnées post-correction manuelle du 2026-08-28).

---

## Méthode QA

1. Superposition visuelle sur radiographies originales (`images/train/B26_XX.png`).
2. Vérification des 5 axes demandés (structure, R/L, IT≠TD, position B1/FOV, cas particuliers).
3. Comparaison **avant / après** vs problème identifié dans `b6_manual_corrections_log.csv`.
4. Métriques auxiliaires : intensité osseuse locale, distance TD/FSD, marge caudale FOV.

**Aucune annotation, label officiel, `data.yaml`, V2/V3 modifié.**

---

## Grille de verdict

| Verdict | Signification |
|---------|---------------|
| **PASS** | Conforme aux critères QA — prêt pour extension |
| **REVIEW** | Structure plausible mais réserve clinique / cas limite |
| **FAIL** | Non-conforme — correction insuffisante ou erreur résiduelle |

---

## Synthèse globale

| Verdict | N | % |
|---------|--:|--:|
| **PASS** | 4 | 44,4 % |
| **REVIEW** | 5 | 55,6 % |
| **FAIL** | 0 | 0 % |

| Confiance | N |
|-----------|--:|
| HIGH | 2 |
| MEDIUM | 5 |
| LOW | 2 |

### Checks structurels (9/9)

| Critère | OK | KO |
|---------|----|----|
| Tubérosité ischiatique (pas fémur) | **9** | 0 |
| R/L correct | **9** | 0 |
| IT ≠ TD | **9** | 0 |
| Caudal à TD + latéral à TD | **9** | 0 |
| Dans FOV (pas extrapolation) | **9** | 0 |
| Correction répond au problème initial | **9** | 0 |

---

## Résultats détaillés

### B26_24 — piège fémoral (P0 + P1)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|-------|----------|
| **IT_R** | (616, 2352) → **(698, 2398)** | **PASS** | HIGH | FAIL fémoral corrigé ; cortex ischiatique caudal D ; Δx FSD = +154 px |
| **IT_L** | (1900, 2120) → **(1858, 2328)** | **PASS** | MEDIUM | Apex caudal G (+208 px y) ; asymétrie R-L rétablie (70 px) |

**Cas particulier :** piège fémoral IT_R — **résolu**. Avant : point sur diaphyse (Δx FSD = 72 px). Après : médial au fémur, os pelvien confirmé visuellement.

---

### B26_01 — piège fémoral IT_L (P1)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|-------|----------|
| **IT_L** | (1756, 2143) → **(1772, 2178)** | **PASS** | HIGH | Caudal +35 px sur cortex ; A-IT01 respecté ; cohérent avec IT_R PASS (Δy = 38 px) |

---

### B26_05 — FOV PARTIAL (P1 + P2)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|-------|----------|
| **IT_R** | (705, 2892) → **(648, 2955)** | **REVIEW** | MEDIUM | Sorti de zone tissus mous → cortex visible ; PARTIAL marge 53 px ; A-FOV05 persiste |
| **IT_L** | (2472, 2876) → **(2395, 2958)** | **REVIEW** | MEDIUM | Sorti du fémur → ischion G ; PARTIAL marge 50 px ; validation clinique recommandée |

**Cas particulier FOV :** les deux points sont sur os pelvien identifiable **dans le FOV** sans extrapolation. Ambiguïté apex caudal (~110 px dispersion documentée) **non résolue** — justifie REVIEW, pas FAIL.

---

### B26_07 — gaz intestinal (P1 + P2)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|-------|----------|
| **IT_R** | (640, 2431) → **(708, 2548)** | **REVIEW** | MEDIUM | Repositionné sur cortex (+117 px y) ; A-GAS07 masque encore le contraste (bone = 71) |
| **IT_L** | (1834, 2379) → **(1778, 2548)** | **PASS** | MEDIUM | Apex caudal G clair (+169 px y) ; repère latéral moins obscurci |

**Cas particulier gaz :** correction structurelle effective bilatéralement ; confiance réduite côté R uniquement.

---

### B26_11 — rotation / contraste (P1 + P2)

| Landmark | Avant → Après | Verdict | Conf. | Synthèse |
|----------|---------------|---------|-------|----------|
| **IT_R** | (567, 2299) → **(632, 2498)** | **REVIEW** | LOW | Apex caudal (+199 px y) ; contraste très faible (bone = 28) ; A-ROT11 |
| **IT_L** | (2052, 2253) → **(1958, 2495)** | **REVIEW** | LOW | Apex caudal (+242 px y) ; contraste faible (bone = 32) ; validation clinique obligatoire |

**Cas particulier rotation :** R/L indépendamment cohérents ; placement sur silhouette ischiatique plausible mais **confiance insuffisante pour PASS** sans revalidation clinique.

---

## Tableau complet

| Image | Landmark | x_new | y_new | Δx | Δy | Structure | R/L | IT≠TD | B1/FOV | Correction OK | Verdict | Conf. |
|-------|----------|------:|------:|---:|---:|:---------:|:---:|:-----:|:------:|:-------------:|:-------:|:-----:|
| B26_24 | IT_R | 698.0 | 2398.0 | +82 | +46 | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** | HIGH |
| B26_24 | IT_L | 1858.0 | 2328.0 | −42 | +208 | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** | MEDIUM |
| B26_01 | IT_L | 1772.0 | 2178.0 | +16 | +35 | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** | HIGH |
| B26_05 | IT_R | 648.0 | 2955.0 | −57 | +63 | ✓ | ✓ | ✓ | ✓* | ✓ | **REVIEW** | MEDIUM |
| B26_05 | IT_L | 2395.0 | 2958.0 | −77 | +82 | ✓ | ✓ | ✓ | ✓* | ✓ | **REVIEW** | MEDIUM |
| B26_07 | IT_R | 708.0 | 2548.0 | +68 | +117 | ✓ | ✓ | ✓ | ✓ | ✓ | **REVIEW** | MEDIUM |
| B26_07 | IT_L | 1778.0 | 2548.0 | −56 | +169 | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** | MEDIUM |
| B26_11 | IT_R | 632.0 | 2498.0 | +65 | +199 | ✓ | ✓ | ✓ | ✓ | ✓ | **REVIEW** | LOW |
| B26_11 | IT_L | 1958.0 | 2495.0 | −94 | +242 | ✓ | ✓ | ✓ | ✓ | ✓ | **REVIEW** | LOW |

\* B26_05 : PARTIAL FOV — dans FOV sans extrapolation, ambiguïté apex documentée.

*(Export CSV : `b6_corrected_9_QA.csv`)*

---

## Analyse avant / après

| Problème initial | Landmarks | Correction effective ? |
|------------------|-----------|:----------------------:|
| Piège fémoral (FAIL) | B26_24 IT_R | **Oui** — structure pelvienne confirmée |
| Trop crânial | B26_24 IT_L, B26_01 IT_L, B26_07 IT_L, B26_11 IT_L/R | **Oui** — déplacements caudaux +35 à +242 px |
| Zone tissus mous / void | B26_05 IT_R, B26_07 IT_R, B26_11 IT_R | **Oui** — repositionnés sur os |
| Sur fémur | B26_05 IT_L | **Oui** — Δx −77 px vers ischion |
| FOV PARTIAL | B26_05 bilatéral | **Partiellement** — os in FOV ; ambiguïté apex persiste |
| Gaz / rotation | B26_07 R, B26_11 R/L | **Partiellement** — structure OK ; confiance limitée |

**Aucune correction n'a aggravé la situation.** 0 régression FAIL identifiée.

---

## Landmarks en REVIEW — action recommandée

| Image | Landmark | Motif REVIEW | Action |
|-------|----------|--------------|--------|
| B26_05 | IT_R, IT_L | PARTIAL FOV ; A-FOV05 | Validation clinique apex + seuil v |
| B26_07 | IT_R | A-GAS07 ; contraste faible | Confirmation radiologique |
| B26_11 | IT_R, IT_L | A-ROT11 ; contraste très faible | Revalidation clinique ou micro-ajustement |

---

## Conclusion

```
Décision QA = CORRECTION_REQUIRED
```

### Motivation

| Critère | Résultat |
|---------|----------|
| **9/9 PASS requis pour READY_FOR_52_QA** | **Non** — 4/9 PASS seulement |
| **FAIL résiduel** | 0 — aucune erreur structurelle majeure |
| **REVIEW en attente** | 5/9 — cas limites FOV, gaz, rotation/contraste |

Les corrections manuelles ont **résolu les problèmes structurels identifiés** (piège fémoral, caudalité, placement hors os). En revanche, **5 landmarks** restent en **REVIEW** avec confiance MEDIUM ou LOW, insuffisants pour un PASS formel unanime.

### Prochaines étapes

1. **Revalidation clinique** des 5 landmarks REVIEW (priorité B26_11 R/L confiance LOW).
2. Si validation clinique → repasser en PASS et réévaluer `READY_FOR_52_QA`.
3. Si échec clinique → nouvelle correction ciblée sur les landmarks concernés.
4. **Ne pas** lancer le QA des 21 cas restants tant que les 5 REVIEW ne sont pas levés ou acceptés formellement.

**Interdit :** passage 14 → 16 kp, labels officiels, entraînement YOLO.

---

## Intégrité dataset

| Élément | Modifié ? |
|---------|:---------:|
| `b6_working_annotations/*.json` | **Non** |
| Labels officiels | **Non** |
| `data.yaml` | **Non** |
| V2 / V3 | **Non** |

**Fichiers créés :**

- `b6_corrected_9_QA.md` (ce rapport)
- `b6_corrected_9_QA.csv`

---

*QA formel B6 — 9 landmarks corrigés — READ-ONLY.*
