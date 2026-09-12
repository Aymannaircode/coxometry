# Validation anatomique V2 — new_26

**Généré le :** 2026-08-23 17:55:28 UTC
**Nature :** contrôle qualité automatique, pas un diagnostic médical.

## Résumé global

- Cas analysés : **26**
- OK : **0**
- WARNING : **26**
- CRITICAL : **0**

## Classement des radios les plus problématiques

| Rang | Cas | Statut | Complétude | Confiance basse | CRITICAL | WARNING |
|------|-----|--------|------------|-----------------|----------|---------|
| 1 | B26_16 | WARNING | 14/14 | 3 | 0 | 10 |
| 2 | B26_02 | WARNING | 14/14 | 2 | 0 | 9 |
| 3 | B26_09 | WARNING | 14/14 | 1 | 0 | 7 |
| 4 | B26_11 | WARNING | 14/14 | 1 | 0 | 6 |
| 5 | B26_19 | WARNING | 14/14 | 0 | 0 | 6 |
| 6 | B26_01 | WARNING | 14/14 | 2 | 0 | 5 |
| 7 | B26_14 | WARNING | 14/14 | 3 | 0 | 5 |
| 8 | B26_18 | WARNING | 14/14 | 1 | 0 | 5 |
| 9 | B26_05 | WARNING | 14/14 | 1 | 0 | 4 |
| 10 | B26_06 | WARNING | 14/14 | 1 | 0 | 4 |
| 11 | B26_07 | WARNING | 14/14 | 0 | 0 | 4 |
| 12 | B26_12 | WARNING | 14/14 | 1 | 0 | 4 |
| 13 | B26_13 | WARNING | 14/14 | 2 | 0 | 4 |
| 14 | B26_15 | WARNING | 14/14 | 1 | 0 | 4 |
| 15 | B26_17 | WARNING | 14/14 | 2 | 0 | 4 |

## B26_16 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **3**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **10**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.896 |
| TD_L | oui | 0.876 |
| FHC_R | oui | 0.718 |
| FHC_L | oui | 0.718 |
| ASL_R | oui | 0.489 |
| ASL_L | oui | 0.525 |
| ASM_R | oui | 0.721 |
| ASM_L | oui | 0.582 |
| FNM_R | oui | 0.714 |
| FNM_L | oui | 0.683 |
| FSP_R | oui | 0.560 |
| FSP_L | oui | 0.630 |
| FSD_R | oui | 0.492 |
| FSD_L | oui | 0.491 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.489 (< 0.5).
- **WARNING** [confidence] FSD_R — FSD_R : confiance=0.492 (< 0.5).
- **WARNING** [confidence] FSD_L — FSD_L : confiance=0.491 (< 0.5).
- **WARNING** [EDGE] FSD_R — FSD_R [EDGE] : coords=(669.5, 2401.0), image=3006x2401, distance bord inférieur=-1.0 px.
- **WARNING** [EDGE] FSD_L — FSD_L [EDGE] : coords=(2440.4, 2401.0), image=3006x2401, distance bord inférieur=-1.0 px.
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 140.9°, écart à la colinéarité = 39.1° (> 25°).
- **WARNING** [fsd_axis_edge] FSD_R — FSD_R : point distal proche du bord inférieur — alignement axial FNM→FSP non concluant à ce niveau (écart perpendiculaire=219.3 px, ratio/FNM→FSD=0.282, ratio/hauteur=0.091, FNM→FSD=778.3 px, distance bord inférieur=-1.0 px). Raison : FSD distal en bord d'image, sans conclusion automatique sur la qualité du point.
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 153.4°, écart à la colinéarité = 26.6° (> 25°).
- **WARNING** [fsd_axis_edge] FSD_L — FSD_L : point distal proche du bord inférieur — alignement axial FNM→FSP non concluant à ce niveau (écart perpendiculaire=169.7 px, ratio/FNM→FSD=0.224, ratio/hauteur=0.071, FNM→FSD=758.8 px, distance bord inférieur=-1.0 px). Raison : FSD distal en bord d'image, sans conclusion automatique sur la qualité du point.
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1872.2, ASM=1926.3).

## B26_02 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **2**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **9**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.916 |
| TD_L | oui | 0.869 |
| FHC_R | oui | 0.704 |
| FHC_L | oui | 0.674 |
| ASL_R | oui | 0.467 |
| ASL_L | oui | 0.506 |
| ASM_R | oui | 0.650 |
| ASM_L | oui | 0.596 |
| FNM_R | oui | 0.660 |
| FNM_L | oui | 0.677 |
| FSP_R | oui | 0.562 |
| FSP_L | oui | 0.680 |
| FSD_R | oui | 0.441 |
| FSD_L | oui | 0.513 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.467 (< 0.5).
- **WARNING** [confidence] FSD_R — FSD_R : confiance=0.441 (< 0.5).
- **WARNING** [EDGE] FSD_R — FSD_R [EDGE] : coords=(548.0, 1975.0), image=3030x1975, distance bord inférieur=-1.0 px.
- **WARNING** [EDGE] FSD_L — FSD_L [EDGE] : coords=(2290.6, 1975.0), image=3030x1975, distance bord inférieur=-1.0 px.
- **WARNING** [femoral_axis] FNM_R — Axe fémoral R : angle FHC→FNM→FSP = 146.6°, écart à la colinéarité = 33.4° (> 25°).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 150.9°, écart à la colinéarité = 29.1° (> 25°).
- **WARNING** [fsd_axis_edge] FSD_R — FSD_R : point distal proche du bord inférieur — alignement axial FNM→FSP non concluant à ce niveau (écart perpendiculaire=153.8 px, ratio/FNM→FSD=0.204, ratio/hauteur=0.078, FNM→FSD=753.7 px, distance bord inférieur=-1.0 px). Raison : FSD distal en bord d'image, sans conclusion automatique sur la qualité du point.
- **WARNING** [fsd_axis_edge] FSD_L — FSD_L : point distal proche du bord inférieur — alignement axial FNM→FSP non concluant à ce niveau (écart perpendiculaire=153.4 px, ratio/FNM→FSD=0.195, ratio/hauteur=0.078, FNM→FSD=785.0 px, distance bord inférieur=-1.0 px). Raison : FSD distal en bord d'image, sans conclusion automatique sur la qualité du point.
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1627.7, ASM=1773.7).

## B26_09 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **7**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.899 |
| TD_L | oui | 0.839 |
| FHC_R | oui | 0.796 |
| FHC_L | oui | 0.743 |
| ASL_R | oui | 0.507 |
| ASL_L | oui | 0.356 |
| ASM_R | oui | 0.771 |
| ASM_L | oui | 0.568 |
| FNM_R | oui | 0.760 |
| FNM_L | oui | 0.595 |
| FSP_R | oui | 0.699 |
| FSP_L | oui | 0.629 |
| FSD_R | oui | 0.563 |
| FSD_L | oui | 0.530 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.356 (< 0.5).
- **WARNING** [EDGE] FSD_R — FSD_R [EDGE] : coords=(641.2, 2225.0), image=2983x2225, distance bord inférieur=-1.0 px.
- **WARNING** [EDGE] FSD_L — FSD_L [EDGE] : coords=(2601.0, 2225.0), image=2983x2225, distance bord inférieur=-1.0 px.
- **WARNING** [fsd_axis_edge] FSD_R — FSD_R : point distal proche du bord inférieur — alignement axial FNM→FSP non concluant à ce niveau (écart perpendiculaire=106.7 px, ratio/FNM→FSD=0.135, ratio/hauteur=0.048, FNM→FSD=790.6 px, distance bord inférieur=-1.0 px). Raison : FSD distal en bord d'image, sans conclusion automatique sur la qualité du point.
- **WARNING** [femoral_axis] FNM_L — Axe fémoral L : angle FHC→FNM→FSP = 149.5°, écart à la colinéarité = 30.5° (> 25°).
- **WARNING** [fsd_axis_edge] FSD_L — FSD_L : point distal proche du bord inférieur — alignement axial FNM→FSP non concluant à ce niveau (écart perpendiculaire=106.7 px, ratio/FNM→FSD=0.135, ratio/hauteur=0.048, FNM→FSD=789.6 px, distance bord inférieur=-1.0 px). Raison : FSD distal en bord d'image, sans conclusion automatique sur la qualité du point.
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1868.8, ASM=2100.1).

## B26_11 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **6**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.699 |
| TD_L | oui | 0.744 |
| FHC_R | oui | 0.773 |
| FHC_L | oui | 0.749 |
| ASL_R | oui | 0.593 |
| ASL_L | oui | 0.442 |
| ASM_R | oui | 0.795 |
| ASM_L | oui | 0.641 |
| FNM_R | oui | 0.672 |
| FNM_L | oui | 0.662 |
| FSP_R | oui | 0.624 |
| FSP_L | oui | 0.555 |
| FSD_R | oui | 0.577 |
| FSD_L | oui | 0.523 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.442 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 135.8°, écart à la colinéarité = 44.2° (> 25°).
- **WARNING** [fsd_axis_geometry] FSD_R — FSD_R : écart axial normalisé élevé (écart perpendiculaire=346.7 px, ratio/FNM→FSD=0.406, ratio/hauteur=0.135, FNM→FSD=853.5 px, distance bord inférieur=76.2 px, seuil ratio/FNM→FSD=0.35) — incohérence géométrique possible, revue manuelle recommandée (sans correction automatique).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 138.4°, écart à la colinéarité = 41.6° (> 25°).
- **WARNING** [fsd_axis_geometry] FSD_L — FSD_L : écart axial normalisé élevé (écart perpendiculaire=356.2 px, ratio/FNM→FSD=0.391, ratio/hauteur=0.139, FNM→FSD=910.5 px, distance bord inférieur=24.0 px, seuil ratio/FNM→FSD=0.35) — incohérence géométrique possible, revue manuelle recommandée (sans correction automatique).
- **WARNING** [bilateral_reference] FHC_L — Segment FNM_FSP (L) : distance prédite/humaine = 2.07 (ref. humaine 210.6 px, prédite 436.2 px).

## B26_19 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **0**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **6**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.814 |
| TD_L | oui | 0.859 |
| FHC_R | oui | 0.695 |
| FHC_L | oui | 0.757 |
| ASL_R | oui | 0.522 |
| ASL_L | oui | 0.542 |
| ASM_R | oui | 0.736 |
| ASM_L | oui | 0.608 |
| FNM_R | oui | 0.717 |
| FNM_L | oui | 0.702 |
| FSP_R | oui | 0.552 |
| FSP_L | oui | 0.592 |
| FSD_R | oui | 0.538 |
| FSD_L | oui | 0.501 |

### Anomalies

- **WARNING** [EDGE] FSD_R — FSD_R [EDGE] : coords=(795.9, 2228.0), image=2825x2228, distance bord inférieur=-1.0 px.
- **WARNING** [EDGE] FSD_L — FSD_L [EDGE] : coords=(2398.9, 2228.0), image=2825x2228, distance bord inférieur=-1.0 px.
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 142.5°, écart à la colinéarité = 37.5° (> 25°).
- **WARNING** [fsd_axis_edge] FSD_R — FSD_R : point distal proche du bord inférieur — alignement axial FNM→FSP non concluant à ce niveau (écart perpendiculaire=250.1 px, ratio/FNM→FSD=0.329, ratio/hauteur=0.112, FNM→FSD=759.5 px, distance bord inférieur=-1.0 px). Raison : FSD distal en bord d'image, sans conclusion automatique sur la qualité du point.
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 141.8°, écart à la colinéarité = 38.2° (> 25°).
- **WARNING** [fsd_axis_edge] FSD_L — FSD_L : point distal proche du bord inférieur — alignement axial FNM→FSP non concluant à ce niveau (écart perpendiculaire=210.8 px, ratio/FNM→FSD=0.295, ratio/hauteur=0.095, FNM→FSD=715.8 px, distance bord inférieur=-1.0 px). Raison : FSD distal en bord d'image, sans conclusion automatique sur la qualité du point.

## B26_01 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **2**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **5**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.861 |
| TD_L | oui | 0.902 |
| FHC_R | oui | 0.643 |
| FHC_L | oui | 0.766 |
| ASL_R | oui | 0.466 |
| ASL_L | oui | 0.580 |
| ASM_R | oui | 0.663 |
| ASM_L | oui | 0.602 |
| FNM_R | oui | 0.710 |
| FNM_L | oui | 0.764 |
| FSP_R | oui | 0.523 |
| FSP_L | oui | 0.615 |
| FSD_R | oui | 0.474 |
| FSD_L | oui | 0.532 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.466 (< 0.5).
- **WARNING** [confidence] FSD_R — FSD_R : confiance=0.474 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 146.1°, écart à la colinéarité = 33.9° (> 25°).
- **WARNING** [bilateral_reference] FHC_R — Segment FNM_FSP (R) : distance prédite/humaine = 2.76 (ref. humaine 161.0 px, prédite 445.1 px).
- **WARNING** [bilateral_reference] FHC_L — Segment FNM_FSP (L) : distance prédite/humaine = 2.46 (ref. humaine 172.9 px, prédite 424.9 px).

## B26_14 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **3**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **5**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.807 |
| TD_L | oui | 0.882 |
| FHC_R | oui | 0.618 |
| FHC_L | oui | 0.792 |
| ASL_R | oui | 0.449 |
| ASL_L | oui | 0.628 |
| ASM_R | oui | 0.661 |
| ASM_L | oui | 0.639 |
| FNM_R | oui | 0.680 |
| FNM_L | oui | 0.759 |
| FSP_R | oui | 0.483 |
| FSP_L | oui | 0.630 |
| FSD_R | oui | 0.489 |
| FSD_L | oui | 0.515 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.449 (< 0.5).
- **WARNING** [confidence] FSP_R — FSP_R : confiance=0.483 (< 0.5).
- **WARNING** [confidence] FSD_R — FSD_R : confiance=0.489 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 146.4°, écart à la colinéarité = 33.6° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 154.5°, écart à la colinéarité = 25.5° (> 25°).

## B26_18 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **5**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.644 |
| TD_L | oui | 0.760 |
| FHC_R | oui | 0.673 |
| FHC_L | oui | 0.740 |
| ASL_R | oui | 0.572 |
| ASL_L | oui | 0.548 |
| ASM_R | oui | 0.724 |
| ASM_L | oui | 0.652 |
| FNM_R | oui | 0.652 |
| FNM_L | oui | 0.698 |
| FSP_R | oui | 0.561 |
| FSP_L | oui | 0.555 |
| FSD_R | oui | 0.516 |
| FSD_L | oui | 0.489 |

### Anomalies

- **WARNING** [confidence] FSD_L — FSD_L : confiance=0.489 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 129.4°, écart à la colinéarité = 50.6° (> 25°).
- **WARNING** [fsd_axis_geometry] FSD_R — FSD_R : écart axial normalisé élevé (écart perpendiculaire=372.3 px, ratio/FNM→FSD=0.446, ratio/hauteur=0.142, FNM→FSD=835.0 px, distance bord inférieur=551.3 px, seuil ratio/FNM→FSD=0.35) — incohérence géométrique possible, revue manuelle recommandée (sans correction automatique).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 139.0°, écart à la colinéarité = 41.0° (> 25°).
- **WARNING** [fsd_axis_geometry] FSD_L — FSD_L : écart axial normalisé élevé (écart perpendiculaire=309.8 px, ratio/FNM→FSD=0.363, ratio/hauteur=0.118, FNM→FSD=852.9 px, distance bord inférieur=526.5 px, seuil ratio/FNM→FSD=0.35) — incohérence géométrique possible, revue manuelle recommandée (sans correction automatique).

## B26_05 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.879 |
| TD_L | oui | 0.905 |
| FHC_R | oui | 0.708 |
| FHC_L | oui | 0.758 |
| ASL_R | oui | 0.457 |
| ASL_L | oui | 0.506 |
| ASM_R | oui | 0.691 |
| ASM_L | oui | 0.588 |
| FNM_R | oui | 0.723 |
| FNM_L | oui | 0.720 |
| FSP_R | oui | 0.573 |
| FSP_L | oui | 0.648 |
| FSD_R | oui | 0.512 |
| FSD_L | oui | 0.521 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.457 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 152.0°, écart à la colinéarité = 28.0° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 151.9°, écart à la colinéarité = 28.1° (> 25°).
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=2087.3, ASM=2110.1).

## B26_06 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.830 |
| TD_L | oui | 0.782 |
| FHC_R | oui | 0.804 |
| FHC_L | oui | 0.688 |
| ASL_R | oui | 0.538 |
| ASL_L | oui | 0.303 |
| ASM_R | oui | 0.760 |
| ASM_L | oui | 0.589 |
| FNM_R | oui | 0.706 |
| FNM_L | oui | 0.591 |
| FSP_R | oui | 0.713 |
| FSP_L | oui | 0.578 |
| FSD_R | oui | 0.630 |
| FSD_L | oui | 0.605 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.303 (< 0.5).
- **WARNING** [femoral_axis] FNM_R — Axe fémoral R : angle FHC→FNM→FSP = 148.2°, écart à la colinéarité = 31.8° (> 25°).
- **WARNING** [femoral_axis] FNM_L — Axe fémoral L : angle FHC→FNM→FSP = 150.7°, écart à la colinéarité = 29.3° (> 25°).
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1667.6, ASM=1813.7).

## B26_07 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **0**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.757 |
| TD_L | oui | 0.843 |
| FHC_R | oui | 0.670 |
| FHC_L | oui | 0.765 |
| ASL_R | oui | 0.520 |
| ASL_L | oui | 0.535 |
| ASM_R | oui | 0.714 |
| ASM_L | oui | 0.597 |
| FNM_R | oui | 0.692 |
| FNM_L | oui | 0.715 |
| FSP_R | oui | 0.553 |
| FSP_L | oui | 0.586 |
| FSD_R | oui | 0.532 |
| FSD_L | oui | 0.520 |

### Anomalies

- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 143.5°, écart à la colinéarité = 36.5° (> 25°).
- **WARNING** [fsd_axis_geometry] FSD_R — FSD_R : écart axial normalisé élevé (écart perpendiculaire=320.9 px, ratio/FNM→FSD=0.352, ratio/hauteur=0.119, FNM→FSD=911.3 px, distance bord inférieur=33.6 px, seuil ratio/FNM→FSD=0.35) — incohérence géométrique possible, revue manuelle recommandée (sans correction automatique).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 140.1°, écart à la colinéarité = 39.9° (> 25°).
- **WARNING** [bilateral_reference] FHC_L — Segment FNM_FSP (L) : distance prédite/humaine = 2.12 (ref. humaine 224.3 px, prédite 475.0 px).

## B26_12 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.801 |
| TD_L | oui | 0.786 |
| FHC_R | oui | 0.751 |
| FHC_L | oui | 0.702 |
| ASL_R | oui | 0.514 |
| ASL_L | oui | 0.336 |
| ASM_R | oui | 0.732 |
| ASM_L | oui | 0.565 |
| FNM_R | oui | 0.685 |
| FNM_L | oui | 0.603 |
| FSP_R | oui | 0.677 |
| FSP_L | oui | 0.598 |
| FSD_R | oui | 0.598 |
| FSD_L | oui | 0.572 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.336 (< 0.5).
- **WARNING** [femoral_axis] FNM_R — Axe fémoral R : angle FHC→FNM→FSP = 148.5°, écart à la colinéarité = 31.5° (> 25°).
- **WARNING** [femoral_axis] FNM_L — Axe fémoral L : angle FHC→FNM→FSP = 153.0°, écart à la colinéarité = 27.0° (> 25°).
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1744.3, ASM=1890.5).

## B26_13 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **2**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.817 |
| TD_L | oui | 0.858 |
| FHC_R | oui | 0.679 |
| FHC_L | oui | 0.753 |
| ASL_R | oui | 0.493 |
| ASL_L | oui | 0.498 |
| ASM_R | oui | 0.695 |
| ASM_L | oui | 0.562 |
| FNM_R | oui | 0.706 |
| FNM_L | oui | 0.689 |
| FSP_R | oui | 0.574 |
| FSP_L | oui | 0.615 |
| FSD_R | oui | 0.538 |
| FSD_L | oui | 0.514 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.493 (< 0.5).
- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.498 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 147.2°, écart à la colinéarité = 32.8° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 145.6°, écart à la colinéarité = 34.4° (> 25°).

## B26_15 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.746 |
| TD_L | oui | 0.768 |
| FHC_R | oui | 0.784 |
| FHC_L | oui | 0.733 |
| ASL_R | oui | 0.564 |
| ASL_L | oui | 0.394 |
| ASM_R | oui | 0.778 |
| ASM_L | oui | 0.606 |
| FNM_R | oui | 0.689 |
| FNM_L | oui | 0.650 |
| FSP_R | oui | 0.653 |
| FSP_L | oui | 0.557 |
| FSD_R | oui | 0.596 |
| FSD_L | oui | 0.542 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.394 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 141.4°, écart à la colinéarité = 38.6° (> 25°).
- **WARNING** [fsd_axis_geometry] FSD_R — FSD_R : écart axial normalisé élevé (écart perpendiculaire=286.4 px, ratio/FNM→FSD=0.367, ratio/hauteur=0.126, FNM→FSD=780.7 px, distance bord inférieur=99.1 px, seuil ratio/FNM→FSD=0.35) — incohérence géométrique possible, revue manuelle recommandée (sans correction automatique).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 147.7°, écart à la colinéarité = 32.3° (> 25°).

## B26_17 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **2**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.767 |
| TD_L | oui | 0.862 |
| FHC_R | oui | 0.632 |
| FHC_L | oui | 0.796 |
| ASL_R | oui | 0.462 |
| ASL_L | oui | 0.625 |
| ASM_R | oui | 0.698 |
| ASM_L | oui | 0.652 |
| FNM_R | oui | 0.693 |
| FNM_L | oui | 0.748 |
| FSP_R | oui | 0.484 |
| FSP_L | oui | 0.593 |
| FSD_R | oui | 0.513 |
| FSD_L | oui | 0.509 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.462 (< 0.5).
- **WARNING** [confidence] FSP_R — FSP_R : confiance=0.484 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 146.9°, écart à la colinéarité = 33.1° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 151.5°, écart à la colinéarité = 28.5° (> 25°).

## B26_20 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.853 |
| TD_L | oui | 0.812 |
| FHC_R | oui | 0.807 |
| FHC_L | oui | 0.714 |
| ASL_R | oui | 0.518 |
| ASL_L | oui | 0.307 |
| ASM_R | oui | 0.767 |
| ASM_L | oui | 0.582 |
| FNM_R | oui | 0.726 |
| FNM_L | oui | 0.606 |
| FSP_R | oui | 0.715 |
| FSP_L | oui | 0.594 |
| FSD_R | oui | 0.613 |
| FSD_L | oui | 0.596 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.307 (< 0.5).
- **WARNING** [femoral_axis] FNM_R — Axe fémoral R : angle FHC→FNM→FSP = 151.7°, écart à la colinéarité = 28.3° (> 25°).
- **WARNING** [femoral_axis] FNM_L — Axe fémoral L : angle FHC→FNM→FSP = 153.7°, écart à la colinéarité = 26.3° (> 25°).
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1623.7, ASM=1787.2).

## B26_21 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.834 |
| TD_L | oui | 0.802 |
| FHC_R | oui | 0.789 |
| FHC_L | oui | 0.704 |
| ASL_R | oui | 0.521 |
| ASL_L | oui | 0.315 |
| ASM_R | oui | 0.749 |
| ASM_L | oui | 0.575 |
| FNM_R | oui | 0.721 |
| FNM_L | oui | 0.607 |
| FSP_R | oui | 0.707 |
| FSP_L | oui | 0.582 |
| FSD_R | oui | 0.621 |
| FSD_L | oui | 0.580 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.315 (< 0.5).
- **WARNING** [femoral_axis] FNM_R — Axe fémoral R : angle FHC→FNM→FSP = 147.2°, écart à la colinéarité = 32.8° (> 25°).
- **WARNING** [femoral_axis] FNM_L — Axe fémoral L : angle FHC→FNM→FSP = 150.9°, écart à la colinéarité = 29.1° (> 25°).
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1794.3, ASM=1942.5).

## B26_24 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.839 |
| TD_L | oui | 0.783 |
| FHC_R | oui | 0.821 |
| FHC_L | oui | 0.700 |
| ASL_R | oui | 0.556 |
| ASL_L | oui | 0.315 |
| ASM_R | oui | 0.772 |
| ASM_L | oui | 0.622 |
| FNM_R | oui | 0.718 |
| FNM_L | oui | 0.607 |
| FSP_R | oui | 0.720 |
| FSP_L | oui | 0.579 |
| FSD_R | oui | 0.640 |
| FSD_L | oui | 0.591 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.315 (< 0.5).
- **WARNING** [femoral_axis] FNM_R — Axe fémoral R : angle FHC→FNM→FSP = 145.0°, écart à la colinéarité = 35.0° (> 25°).
- **WARNING** [femoral_axis] FNM_L — Axe fémoral L : angle FHC→FNM→FSP = 140.6°, écart à la colinéarité = 39.4° (> 25°).
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1615.7, ASM=1722.9).

## B26_25 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.780 |
| TD_L | oui | 0.755 |
| FHC_R | oui | 0.799 |
| FHC_L | oui | 0.708 |
| ASL_R | oui | 0.557 |
| ASL_L | oui | 0.340 |
| ASM_R | oui | 0.780 |
| ASM_L | oui | 0.616 |
| FNM_R | oui | 0.684 |
| FNM_L | oui | 0.606 |
| FSP_R | oui | 0.686 |
| FSP_L | oui | 0.578 |
| FSD_R | oui | 0.623 |
| FSD_L | oui | 0.586 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.340 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 151.1°, écart à la colinéarité = 28.9° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 152.3°, écart à la colinéarité = 27.7° (> 25°).
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1793.2, ASM=1884.4).

## B26_26 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **4**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.797 |
| TD_L | oui | 0.790 |
| FHC_R | oui | 0.785 |
| FHC_L | oui | 0.760 |
| ASL_R | oui | 0.562 |
| ASL_L | oui | 0.395 |
| ASM_R | oui | 0.781 |
| ASM_L | oui | 0.621 |
| FNM_R | oui | 0.712 |
| FNM_L | oui | 0.651 |
| FSP_R | oui | 0.663 |
| FSP_L | oui | 0.610 |
| FSD_R | oui | 0.589 |
| FSD_L | oui | 0.521 |

### Anomalies

- **WARNING** [confidence] ASL_L — ASL_L : confiance=0.395 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 149.8°, écart à la colinéarité = 30.2° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 147.9°, écart à la colinéarité = 32.1° (> 25°).
- **WARNING** [acetabular] ASL_L — ASL_L devrait être latéral à ASM_L (x ASL=1819.1, ASM=1851.9).

## B26_03 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **0**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **3**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.722 |
| TD_L | oui | 0.831 |
| FHC_R | oui | 0.666 |
| FHC_L | oui | 0.781 |
| ASL_R | oui | 0.512 |
| ASL_L | oui | 0.553 |
| ASM_R | oui | 0.714 |
| ASM_L | oui | 0.641 |
| FNM_R | oui | 0.682 |
| FNM_L | oui | 0.732 |
| FSP_R | oui | 0.557 |
| FSP_L | oui | 0.589 |
| FSD_R | oui | 0.534 |
| FSD_L | oui | 0.505 |

### Anomalies

- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 141.2°, écart à la colinéarité = 38.8° (> 25°).
- **WARNING** [fsd_axis_geometry] FSD_R — FSD_R : écart axial normalisé élevé (écart perpendiculaire=324.2 px, ratio/FNM→FSD=0.352, ratio/hauteur=0.135, FNM→FSD=920.5 px, distance bord inférieur=142.1 px, seuil ratio/FNM→FSD=0.35) — incohérence géométrique possible, revue manuelle recommandée (sans correction automatique).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 143.8°, écart à la colinéarité = 36.2° (> 25°).

## B26_04 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **3**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.820 |
| TD_L | oui | 0.885 |
| FHC_R | oui | 0.670 |
| FHC_L | oui | 0.767 |
| ASL_R | oui | 0.488 |
| ASL_L | oui | 0.515 |
| ASM_R | oui | 0.694 |
| ASM_L | oui | 0.572 |
| FNM_R | oui | 0.720 |
| FNM_L | oui | 0.721 |
| FSP_R | oui | 0.567 |
| FSP_L | oui | 0.607 |
| FSD_R | oui | 0.533 |
| FSD_L | oui | 0.539 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.488 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 148.5°, écart à la colinéarité = 31.5° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 149.2°, écart à la colinéarité = 30.8° (> 25°).

## B26_08 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **0**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **3**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.690 |
| TD_L | oui | 0.813 |
| FHC_R | oui | 0.639 |
| FHC_L | oui | 0.775 |
| ASL_R | oui | 0.514 |
| ASL_L | oui | 0.599 |
| ASM_R | oui | 0.706 |
| ASM_L | oui | 0.651 |
| FNM_R | oui | 0.672 |
| FNM_L | oui | 0.725 |
| FSP_R | oui | 0.509 |
| FSP_L | oui | 0.565 |
| FSD_R | oui | 0.510 |
| FSD_L | oui | 0.506 |

### Anomalies

- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 139.0°, écart à la colinéarité = 41.0° (> 25°).
- **WARNING** [fsd_axis_geometry] FSD_R — FSD_R : écart axial normalisé élevé (écart perpendiculaire=295.1 px, ratio/FNM→FSD=0.379, ratio/hauteur=0.122, FNM→FSD=779.5 px, distance bord inférieur=68.3 px, seuil ratio/FNM→FSD=0.35) — incohérence géométrique possible, revue manuelle recommandée (sans correction automatique).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 141.6°, écart à la colinéarité = 38.4° (> 25°).

## B26_22 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **3**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.776 |
| TD_L | oui | 0.849 |
| FHC_R | oui | 0.650 |
| FHC_L | oui | 0.766 |
| ASL_R | oui | 0.481 |
| ASL_L | oui | 0.579 |
| ASM_R | oui | 0.705 |
| ASM_L | oui | 0.607 |
| FNM_R | oui | 0.689 |
| FNM_L | oui | 0.720 |
| FSP_R | oui | 0.515 |
| FSP_L | oui | 0.587 |
| FSD_R | oui | 0.525 |
| FSD_L | oui | 0.512 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.481 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 145.3°, écart à la colinéarité = 34.7° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 147.3°, écart à la colinéarité = 32.7° (> 25°).

## B26_23 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **1**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **3**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.807 |
| TD_L | oui | 0.856 |
| FHC_R | oui | 0.682 |
| FHC_L | oui | 0.761 |
| ASL_R | oui | 0.482 |
| ASL_L | oui | 0.549 |
| ASM_R | oui | 0.714 |
| ASM_L | oui | 0.592 |
| FNM_R | oui | 0.706 |
| FNM_L | oui | 0.712 |
| FSP_R | oui | 0.541 |
| FSP_L | oui | 0.587 |
| FSD_R | oui | 0.537 |
| FSD_L | oui | 0.513 |

### Anomalies

- **WARNING** [confidence] ASL_R — ASL_R : confiance=0.482 (< 0.5).
- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 144.6°, écart à la colinéarité = 35.4° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 146.9°, écart à la colinéarité = 33.1° (> 25°).

## B26_10 — WARNING

- Complétude : **14/14**
- Confiance < 0.5 : **0**
- Anomalies CRITICAL : **0**
- Anomalies WARNING : **2**

### Confiance par landmark

| Landmark | Présent | Confiance |
|----------|---------|-----------|
| TD_R | oui | 0.733 |
| TD_L | oui | 0.829 |
| FHC_R | oui | 0.670 |
| FHC_L | oui | 0.764 |
| ASL_R | oui | 0.503 |
| ASL_L | oui | 0.529 |
| ASM_R | oui | 0.709 |
| ASM_L | oui | 0.616 |
| FNM_R | oui | 0.686 |
| FNM_L | oui | 0.717 |
| FSP_R | oui | 0.568 |
| FSP_L | oui | 0.583 |
| FSD_R | oui | 0.537 |
| FSD_L | oui | 0.517 |

### Anomalies

- **WARNING** [femoral_axis] FSP_R — Diaphyse R : angle FNM→FSP→FSD = 143.0°, écart à la colinéarité = 37.0° (> 25°).
- **WARNING** [femoral_axis] FSP_L — Diaphyse L : angle FNM→FSP→FSD = 143.6°, écart à la colinéarité = 36.4° (> 25°).

## Notes

- Les points ne sont jamais corrigés automatiquement.
- CRITICAL inclut les landmarks absents (confiance < 0.25), OUT_OF_IMAGE (> 1 px hors limites) et certaines ruptures majeures d'ordre vertical.
- EDGE signale un point sur le bord ou à ≤ 1 px d'un bord, y compris le bord inférieur (WARNING).
- Les angles proches de 180° sur l'axe fémoral sont considérés cohérents (écart ≤ 25°).
- FSD : l'écart à l'axe FNM→FSP est normalisé par la longueur FNM→FSD (seuil géométrique 0.35). Les points distaux en bord inférieur sont signalés séparément (fsd_axis_edge) sans conclusion automatique.
- Les catégories fsd_axis_geometry, fsd_axis_edge et fsd_axis_not_evaluable ne modifient jamais les coordonnées prédites.
- Les comparaisons bilatérales signalent des écarts marqués, sans conclure à une erreur certaine.
