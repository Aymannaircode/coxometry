# Rapport ASL / ASM — new_26

**Date :** 2026-08-23 16:11:23
**Sources :** JSON MVP (`annotation_pilot/annotations/new_26/`) — non modifiés

## Résumé

- Cas analysés : **26**
- Cas signalés par heuristique automatique : **3**
- ⚠️ Le flag *suspect* est une **aide à la revue**, pas un diagnostic définitif.

## Coordonnées par image (pixels, origine haut-gauche)

| ID | split | ASL_R (x,y) | ASM_R (x,y) | ASL_L (x,y) | ASM_L (x,y) | Suspect auto |
|----|-------|-------------|-------------|-------------|-------------|--------------|
| B26_01 | train | (565.4, 844.5) | (888.0, 1112.6) | (2192.2, 953.6) | (1783.2, 1194.4) | non |
| B26_02 | train | (378.0, 594.2) | (847.0, 649.7) | (2173.5, 639.6) | (1714.6, 634.6) | non |
| B26_03 | train | (407.1, 673.1) | (1016.1, 771.7) | (2535.8, 702.1) | (2002.1, 789.1) | non |
| B26_04 | train | (669.2, 917.1) | (1197.0, 969.3) | (2589.1, 940.3) | (2020.6, 957.7) | non |
| B26_05 | train | (576.0, 1336.5) | (1088.5, 1250.2) | (2562.6, 1083.2) | (2084.7, 1152.3) | non |
| B26_06 | train | (358.7, 770.4) | (961.0, 846.0) | (2461.8, 751.6) | (1863.1, 827.7) | non |
| B26_07 | train | (393.6, 1149.9) | (876.0, 1205.7) | (2329.6, 982.5) | (1781.6, 1212.2) | non |
| B26_08 | train | (485.5, 1118.2) | (938.8, 1013.0) | (2134.9, 1153.3) | (1667.0, 1033.4) | non |
| B26_09 | train | (580.5, 709.0) | (1174.4, 868.9) | (2659.1, 857.4) | (2122.3, 931.7) | non |
| B26_10 | val | (466.9, 856.6) | (1065.1, 905.0) | (2525.5, 887.4) | (1975.7, 949.0) | non |
| B26_11 | train | (377.5, 1016.2) | (884.5, 991.3) | (2417.9, 1045.3) | (1890.2, 983.0) | non |
| B26_12 | train | (668.2, 758.4) | (1065.9, 1017.8) | (2327.9, 715.2) | (1943.3, 1017.8) | oui |
| B26_13 | val | (660.2, 906.8) | (1142.4, 939.5) | (2439.1, 817.8) | (1971.0, 902.1) | non |
| B26_14 | train | (452.2, 726.6) | (995.3, 1008.1) | (2423.3, 734.6) | (1852.1, 992.0) | non |
| B26_15 | train | (259.1, 856.7) | (812.3, 842.0) | (2224.9, 842.0) | (1627.4, 830.9) | non |
| B26_16 | train | (469.7, 1049.8) | (987.6, 1178.5) | (2403.7, 1021.2) | (1914.5, 1155.7) | non |
| B26_17 | val | (197.6, 933.1) | (849.5, 933.1) | (2300.0, 991.7) | (1750.6, 896.5) | non |
| B26_18 | train | (625.6, 694.1) | (1038.4, 820.7) | (2412.4, 570.6) | (1987.6, 823.7) | non |
| B26_19 | train | (511.9, 739.8) | (1062.2, 977.5) | (2524.4, 765.8) | (1925.2, 958.0) | non |
| B26_20 | val | (397.3, 808.7) | (899.2, 1002.8) | (2286.6, 775.5) | (1832.0, 950.7) | non |
| B26_21 | train | (418.1, 1039.0) | (1035.1, 1307.9) | (2458.9, 1181.4) | (1952.7, 1249.9) | non |
| B26_22 | train | (453.6, 1113.4) | (949.1, 1068.4) | (2435.6, 957.5) | (1832.7, 985.2) | non |
| B26_23 | train | (575.8, 833.3) | (1194.3, 881.5) | (2507.8, 773.0) | (2001.7, 825.3) | non |
| B26_24 | train | (262.0, 943.2) | (837.4, 1102.5) | (2255.2, 835.4) | (1736.3, 1035.7) | non |
| B26_25 | train | (287.4, 881.5) | (931.2, 887.3) | (2586.6, 985.0) | (1919.8, 864.3) | oui |
| B26_26 | val | (221.9, 362.9) | (859.1, 846.6) | (2543.2, 362.9) | (1934.4, 829.5) | oui |

## Heuristiques automatiques (présélection)

- ASL au-dessus de FHC (normalisé) — médiane cohorte : 0.1614
- ASM au-dessus de FHC (normalisé) — médiane cohorte : 0.1211
- Flag si valeur > médiane + 2.5×MAD, inversion latéral/médial, ASL/ASM sous FHC, écart vertical ASL/ASM > 12 % hauteur, inclinaison sourcil > 50°, ou segment très court.

## Détail des cas signalés

### B26_12
- L: écart vertical ASL/ASM important (303 px) — ligne ne suit peut-être pas le sourcil

### B26_25
- L: ASM anormalement haut vs FHC (0.182 norm, médiane 0.121) — possible ilium

### B26_26
- R: ASL anormalement haut vs FHC (0.237 norm, médiane 0.161) — possible ilium
- R: écart vertical ASL/ASM important (484 px) — ligne ne suit peut-être pas le sourcil
- L: ASL anormalement haut vs FHC (0.263 norm, médiane 0.161) — possible ilium
- L: écart vertical ASL/ASM important (467 px) — ligne ne suit peut-être pas le sourcil

## Fichiers image associés

| ID | PNG dataset | Overlay zoom |
|----|-------------|--------------|
| B26_01 | `images\train\B26_01.png` | `visual_check/asl_asm_review/overlays/B26_01_asl_asm.png` |
| B26_02 | `images\train\B26_02.png` | `visual_check/asl_asm_review/overlays/B26_02_asl_asm.png` |
| B26_03 | `images\train\B26_03.png` | `visual_check/asl_asm_review/overlays/B26_03_asl_asm.png` |
| B26_04 | `images\train\B26_04.png` | `visual_check/asl_asm_review/overlays/B26_04_asl_asm.png` |
| B26_05 | `images\train\B26_05.png` | `visual_check/asl_asm_review/overlays/B26_05_asl_asm.png` |
| B26_06 | `images\train\B26_06.png` | `visual_check/asl_asm_review/overlays/B26_06_asl_asm.png` |
| B26_07 | `images\train\B26_07.png` | `visual_check/asl_asm_review/overlays/B26_07_asl_asm.png` |
| B26_08 | `images\train\B26_08.png` | `visual_check/asl_asm_review/overlays/B26_08_asl_asm.png` |
| B26_09 | `images\train\B26_09.png` | `visual_check/asl_asm_review/overlays/B26_09_asl_asm.png` |
| B26_10 | `images\val\B26_10.png` | `visual_check/asl_asm_review/overlays/B26_10_asl_asm.png` |
| B26_11 | `images\train\B26_11.png` | `visual_check/asl_asm_review/overlays/B26_11_asl_asm.png` |
| B26_12 | `images\train\B26_12.png` | `visual_check/asl_asm_review/overlays/B26_12_asl_asm.png` |
| B26_13 | `images\val\B26_13.png` | `visual_check/asl_asm_review/overlays/B26_13_asl_asm.png` |
| B26_14 | `images\train\B26_14.png` | `visual_check/asl_asm_review/overlays/B26_14_asl_asm.png` |
| B26_15 | `images\train\B26_15.png` | `visual_check/asl_asm_review/overlays/B26_15_asl_asm.png` |
| B26_16 | `images\train\B26_16.png` | `visual_check/asl_asm_review/overlays/B26_16_asl_asm.png` |
| B26_17 | `images\val\B26_17.png` | `visual_check/asl_asm_review/overlays/B26_17_asl_asm.png` |
| B26_18 | `images\train\B26_18.png` | `visual_check/asl_asm_review/overlays/B26_18_asl_asm.png` |
| B26_19 | `images\train\B26_19.png` | `visual_check/asl_asm_review/overlays/B26_19_asl_asm.png` |
| B26_20 | `images\val\B26_20.png` | `visual_check/asl_asm_review/overlays/B26_20_asl_asm.png` |
| B26_21 | `images\train\B26_21.png` | `visual_check/asl_asm_review/overlays/B26_21_asl_asm.png` |
| B26_22 | `images\train\B26_22.png` | `visual_check/asl_asm_review/overlays/B26_22_asl_asm.png` |
| B26_23 | `images\train\B26_23.png` | `visual_check/asl_asm_review/overlays/B26_23_asl_asm.png` |
| B26_24 | `images\train\B26_24.png` | `visual_check/asl_asm_review/overlays/B26_24_asl_asm.png` |
| B26_25 | `images\train\B26_25.png` | `visual_check/asl_asm_review/overlays/B26_25_asl_asm.png` |
| B26_26 | `images\val\B26_26.png` | `visual_check/asl_asm_review/overlays/B26_26_asl_asm.png` |
