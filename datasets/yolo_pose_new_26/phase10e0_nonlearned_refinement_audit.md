# Phase 10E-0 — Non-Learned Anatomical Refinement Audit

**Date:** 2026-09-04  
**Mode:** READ-ONLY feasibility audit — no training, no production/V5/`mvp_geometry` changes  
**Corpus:** 26 verified cases (21 train / 5 continuity val)  
**Frozen predictions:** `predictions_v2/labels/*.txt` (V5 Phase 2 ≡ V2 for KP0–13 per Phase 9B)  
**Isolated script:** `_phase10e0_audit_temp/run_nonlearned_refinement_audit.py`  
**Metrics CSV:** `phase10e0_nonlearned_refinement_metrics.csv`  
**Renders:** `phase10e0_nonlearned_refinement_renders/`  

## 1. Executive verdict

| Field | Value |
|-------|-------|
| ASL non-learned promising | **YES** |
| Shaft non-learned promising | **NO** |
| Best ASL method | `gradient_search` |
| Best shaft method | `NONE` |
| SAFE_TO_PROCEED (to implementation) | **NO** |
| Training started | NO |
| Production modified | NO |

ASL_L shows **real image-driven signal** (lateral sourcil search reduces medial ASM collapse), but residual error remains large, ASL_R is not clearly improved, shaft methods are **UNSAFE**, and there is no independent test set. Treat as research signal only — **do not implement** a production adapter yet.

## 2. Methods tested

### ASL (5)
1. `gradient_search` — Sobel magnitude band lateral of ASM
2. `radial_angular` — radial/angular sampling from FHC constrained by TD/ASM
3. `sourcil_line` — Canny + Probabilistic Hough endpoint near roof
4. `asm_lateral_search` — image-driven walk from ASM along superior edge
5. `combined_rank` — anatomical scoring + disagreement fail-open

### FSP/FSD (4)
1. `hough_axis` — Hough lines → shaft axis → anatomical level search
2. `cortical_edge` — bilateral cortical peaks → midline PCA
3. `ransac_shaft` — RANSAC on Canny edge points
4. `combined_shaft` — consensus / disagreement fail-open

**Explicitly excluded:** `ASL = ASM + constant_offset` (formula-only).
V5 ASL used only as weak prior / fail-open fallback, never as ROI anchor.

### TRAIN-only constants (frozen before VAL look)
| Constant | Value |
|----------|------:|
| mean_sourcil | 536.59 |
| std_sourcil | 63.83 |
| p10_sourcil | 463.42 |
| p90_sourcil | 616.78 |
| mean_shaft | 608.44 |
| std_shaft | 90.24 |
| p10_shaft | 503.88 |
| p90_shaft | 691.80 |
| mean_fhc_asm | 341.21 |
| mean_fhc_fnm | 282.39 |
| mean_asm_asl_angle | -0.67 |
| n_train_hips | 42 |

## 3. ASL candidate generation

Acetabular ROI uses **TD + FHC + ASM** predictions plus TRAIN mean-sourcil lateral expansion (Phase 10D-0 fallback family). ASL prediction is **not** required for ROI.
Each method emits `{x,y,score,method,region,in_bounds,evidence,status}` with `OK | UNAVAILABLE | KEEP_V5`. Effective adapter point = candidate if OK else V5.

## 4. ASL results

### 4.1 V5 baseline (original px)

| Landmark/split | mean | median | p90 | max | mean Δx | mean Δy | %<25 | %<50 | %<75 | ASM confusion |
|----------------|-----:|-------:|----:|----:|--------:|--------:|-----:|-----:|-----:|-------------:|
| V5 ASL_R all | 143.8 | 149.9 | 222.0 | 237.4 | 75.6 | 6.3 | 0.0 | 3.8 | 15.4 | — |
| V5 ASL_L all | 525.4 | 504.4 | 694.6 | 813.8 | -482.7 | 173.2 | 0.0 | 0.0 | 0.0 | 96.2% |
| V5 ASL_L train | 538.2 | 529.4 | 685.3 | 813.8 | -490.1 | 185.7 | 0.0 | 0.0 | 0.0 | 95.2% |
| V5 ASL_L val | 471.7 | 441.5 | 604.0 | 704.0 | -451.3 | 120.7 | 0.0 | 0.0 | 0.0 | 100% |

### 4.2 Per-method ASL_L (original px)

| Method | split | mean | median | p90 | max | mean Δx | mean Δy | %<50 | ASM conf | class |
|--------|-------|-----:|-------:|----:|----:|--------:|--------:|-----:|---------:|-------|
| `gradient_search` | train | 178.7 | 168.3 | 289.9 | 346.2 | -85.2 | 115.9 | 0.0 | 14.3% |  |
| `gradient_search` | val | 132.9 | 135.6 | 184.5 | 205.8 | -47.3 | 62.4 | 0.0 | 0% | POSSIBLE |
| `gradient_search` | all | 169.8 | 155.9 | 287.3 | 346.2 | -77.9 | 105.7 | 0.0 | 11.5% |  |
| `radial_angular` | train | 315.1 | 257.3 | 483.9 | 813.8 | -200.4 | -113.2 | 0.0 | 23.8% |  |
| `radial_angular` | val | 320.2 | 326.9 | 357.8 | 365.3 | -123.8 | -218.2 | 0.0 | 20.0% | POSSIBLE |
| `radial_angular` | all | 316.1 | 294.9 | 482.6 | 813.8 | -185.6 | -133.3 | 0.0 | 23.1% |  |
| `sourcil_line` | train | 538.2 | 529.4 | 685.3 | 813.8 | -490.1 | 185.7 | 0.0 | 95.2% |  |
| `sourcil_line` | val | 471.7 | 441.5 | 604.0 | 704.0 | -451.3 | 120.7 | 0.0 | 100% | NO_BENEFIT |
| `sourcil_line` | all | 525.4 | 504.4 | 694.6 | 813.8 | -482.7 | 173.2 | 0.0 | 96.2% |  |
| `asm_lateral_search` | train | 457.5 | 534.7 | 716.1 | 792.9 | 29.6 | 398.7 | 9.5 | 9.5% |  |
| `asm_lateral_search` | val | 352.2 | 391.9 | 536.6 | 602.7 | 41.9 | 188.9 | 0.0 | 0% | UNSAFE |
| `asm_lateral_search` | all | 437.3 | 485.2 | 714.0 | 792.9 | 32.0 | 358.3 | 7.7 | 7.7% |  |
| `combined_rank` | train | 181.2 | 153.8 | 451.6 | 474.4 | -61.3 | 50.6 | 9.5 | 9.5% |  |
| `combined_rank` | val | 115.6 | 79.9 | 188.5 | 211.2 | -48.3 | -50.9 | 0.0 | 0% | POSSIBLE |
| `combined_rank` | all | 168.6 | 141.5 | 349.4 | 474.4 | -58.8 | 31.1 | 7.7 | 7.7% |  |

### 4.3 Per-method ASL_R (original px, all 26)

| Method | mean | median | p90 | max | %<50 |
|--------|-----:|-------:|----:|----:|-----:|
| `gradient_search` | 158.4 | 167.0 | 245.7 | 292.1 | 7.7 |
| `radial_angular` | 143.8 | 149.9 | 222.0 | 237.4 | 3.8 |
| `sourcil_line` | 143.8 | 149.9 | 222.0 | 237.4 | 3.8 |
| `asm_lateral_search` | 448.9 | 441.5 | 772.1 | 842.4 | 3.8 |
| `combined_rank` | 279.4 | 245.1 | 491.3 | 529.2 | 3.8 |

### 4.4 Method classification (ASL_L-focused)

| Method | Class | Note |
|--------|-------|------|
| `gradient_search` | **POSSIBLE** | large relative gain but residual still coarse (val_mean=132.9, %<50=0.0); train_imp=0.67 val_imp=0.72; asm_conf_train=0.14, asm_conf_val=0.00 |
| `radial_angular` | **POSSIBLE** | large relative gain but residual still coarse (val_mean=320.2, %<50=0.0); train_imp=0.41 val_imp=0.32; asm_conf_train=0.24, asm_conf_val=0.20 |
| `sourcil_line` | **NO_BENEFIT** | no clear gain; train_imp=0.00 val_imp=0.00; asm_conf_train=0.95, asm_conf_val=1.00 |
| `asm_lateral_search` | **UNSAFE** | ASL_R regression with weak/unstable ASL_L gain; asm_conf_train=0.10, asm_conf_val=0.00, ASL_R_regressed |
| `combined_rank` | **POSSIBLE** | ASL_L improves but ASL_R worsens; train_imp=0.66 val_imp=0.76; asm_conf_train=0.10, asm_conf_val=0.00, ASL_R_regressed |

## 5. FSP/FSD candidate generation

Shaft ROI from FHC+FNM+soft V5 FSP/FSD extent (ROI only). Axis from Hough / cortical / RANSAC. FSP searched as proximal shaft level caudal to FNM with cortical evidence; FSD is last caudal axis point with bilateral cortical evidence still inside the image (no extrapolation outside FOV → UNAVAILABLE).

## 6. FSP/FSD results

### 6.1 V5 baseline (original px)

| Landmark | mean | median | p90 | max | mean Δx | mean Δy | %<25 | %<50 | %<75 |
|----------|-----:|-------:|----:|----:|--------:|--------:|-----:|-----:|-----:|
| V5 FSP all | 160.4 | 153.4 | 243.1 | 413.2 | 18.1 | 126.0 | 1.9 | 5.8 | 11.5 |
| V5 FSD all | 133.7 | 123.3 | 242.3 | 401.3 | 57.7 | -32.5 | 3.8 | 17.3 | 28.8 |
| V5 FSP_R | 150.9 | 141.8 | 229.8 | 413.2 | -67.3 | 123.5 | 3.8 | 3.8 | 11.5 |
| V5 FSP_L | 170.0 | 185.5 | 249.1 | 293.4 | 103.6 | 128.5 | 0.0 | 7.7 | 11.5 |
| V5 FSD_R | 159.4 | 161.0 | 256.0 | 294.6 | 112.8 | -36.7 | 0.0 | 7.7 | 11.5 |
| V5 FSD_L | 108.0 | 75.7 | 222.2 | 401.3 | 2.7 | -28.3 | 7.7 | 26.9 | 46.2 |

### 6.2 Per-method shaft errors (original px)

| Method | KP | split | mean | median | p90 | max | %<50 | replace_rate | class |
|--------|----|-------|-----:|-------:|----:|----:|-----:|-------------:|-------|
| `hough_axis` | FSP | train | 201.4 | 189.2 | 364.8 | 419.4 | 4.8 | 21.4% |  |
| `hough_axis` | FSP | val | 248.4 | 197.1 | 434.1 | 562.8 | 0.0 | 50.0% | UNSAFE |
| `hough_axis` | FSP | all | 210.4 | 189.2 | 378.7 | 562.8 | 3.8 | 26.9% |  |
| `hough_axis` | FSD | train | 223.1 | 159.1 | 422.7 | 1711.1 | 19.0 | 23.8% |  |
| `hough_axis` | FSD | val | 317.4 | 228.3 | 694.6 | 799.4 | 10.0 | 50.0% |  |
| `hough_axis` | FSD | all | 241.3 | 179.9 | 432.1 | 1711.1 | 17.3 | 28.8% |  |
| `cortical_edge` | FSP | train | 324.8 | 307.8 | 407.4 | 480.6 | 0.0 | 100.0% |  |
| `cortical_edge` | FSP | val | 355.5 | 342.6 | 442.7 | 524.4 | 0.0 | 100.0% | UNSAFE |
| `cortical_edge` | FSP | all | 330.7 | 315.3 | 418.0 | 524.4 | 0.0 | 100.0% |  |
| `cortical_edge` | FSD | train | 292.7 | 292.9 | 410.9 | 548.4 | 0.0 | 100.0% |  |
| `cortical_edge` | FSD | val | 434.1 | 401.5 | 597.4 | 795.4 | 0.0 | 100.0% |  |
| `cortical_edge` | FSD | all | 319.9 | 301.8 | 444.5 | 795.4 | 0.0 | 100.0% |  |
| `ransac_shaft` | FSP | train | 300.2 | 309.7 | 409.3 | 461.9 | 0.0 | 76.2% |  |
| `ransac_shaft` | FSP | val | 336.8 | 331.8 | 455.3 | 503.2 | 0.0 | 90.0% | UNSAFE |
| `ransac_shaft` | FSP | all | 307.2 | 314.9 | 413.2 | 503.2 | 0.0 | 78.8% |  |
| `ransac_shaft` | FSD | train | 373.9 | 328.7 | 594.3 | 1835.1 | 4.8 | 83.3% |  |
| `ransac_shaft` | FSD | val | 465.8 | 492.7 | 657.5 | 689.3 | 0.0 | 90.0% |  |
| `ransac_shaft` | FSD | all | 391.6 | 345.5 | 633.2 | 1835.1 | 3.8 | 84.6% |  |
| `combined_shaft` | FSP | train | 326.5 | 311.2 | 401.2 | 470.9 | 0.0 | 97.6% |  |
| `combined_shaft` | FSP | val | 322.2 | 331.0 | 440.4 | 527.5 | 0.0 | 90.0% | UNSAFE |
| `combined_shaft` | FSP | all | 325.6 | 313.2 | 405.8 | 527.5 | 0.0 | 96.2% |  |
| `combined_shaft` | FSD | train | 219.4 | 218.1 | 360.7 | 438.5 | 4.8 | 50.0% |  |
| `combined_shaft` | FSD | val | 301.0 | 260.6 | 489.4 | 748.5 | 10.0 | 50.0% |  |
| `combined_shaft` | FSD | all | 235.1 | 237.1 | 388.9 | 748.5 | 5.8 | 50.0% |  |

### 6.3 Shaft method classification

| Method | Class | Note |
|--------|-------|------|
| `hough_axis` | **UNSAFE** | worsens or unstable; train_imp=-0.49 val_imp=-0.69;  |
| `cortical_edge` | **UNSAFE** | worsens or unstable; train_imp=-1.17 val_imp=-1.36;  |
| `ransac_shaft` | **UNSAFE** | worsens or unstable; train_imp=-1.37 val_imp=-1.40;  |
| `combined_shaft` | **UNSAFE** | worsens or unstable; train_imp=-0.92 val_imp=-0.86;  |

## 7. Continuity validation

Frozen cases: `B26_10`, `B26_13`, `B26_17`, `B26_20`, `B26_26`.
Shown for render methods: ASL=`gradient_search`, shaft=`hough_axis` (letterbox-640 px).

| Case | KP | err V5 | err effective | Δ (V5−eff) | mode | status |
|------|----|-------:|--------------:|-----------:|------|--------|
| B26_10 | ASL_R | 35.1 | 47.5 | -12.4 | REPLACE | OK |
| B26_10 | ASL_L | 95.6 | 19.1 | 76.5 | REPLACE | OK |
| B26_10 | FSP_R | 32.5 | 32.5 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_10 | FSP_L | 51.0 | 51.0 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_10 | FSD_R | 51.3 | 51.3 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_10 | FSD_L | 44.9 | 44.9 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_13 | ASL_R | 18.7 | 24.1 | -5.4 | REPLACE | OK |
| B26_13 | ASL_L | 81.6 | 30.2 | 51.5 | REPLACE | OK |
| B26_13 | FSP_R | 0.4 | 111.4 | -111.0 | REPLACE | OK |
| B26_13 | FSP_L | 25.9 | 83.1 | -57.2 | REPLACE | OK |
| B26_13 | FSD_R | 55.0 | 135.1 | -80.2 | REPLACE | OK |
| B26_13 | FSD_L | 79.4 | 158.2 | -78.8 | REPLACE | OK |
| B26_17 | ASL_R | 55.0 | 42.3 | 12.7 | REPLACE | OK |
| B26_17 | ASL_L | 80.3 | 18.5 | 61.8 | REPLACE | OK |
| B26_17 | FSP_R | 13.5 | 13.5 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_17 | FSP_L | 33.3 | 33.3 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_17 | FSD_R | 48.5 | 48.5 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_17 | FSD_L | 6.1 | 6.1 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_20 | ASL_R | 22.3 | 39.6 | -17.3 | REPLACE | OK |
| B26_20 | ASL_L | 166.8 | 48.8 | 118.0 | REPLACE | OK |
| B26_20 | FSP_R | 30.6 | 84.2 | -53.5 | REPLACE | OK |
| B26_20 | FSP_L | 36.5 | 36.5 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_20 | FSD_R | 19.0 | 102.6 | -83.6 | REPLACE | OK |
| B26_20 | FSD_L | 23.1 | 23.1 | 0.0 | UNAVAILABLE | UNAVAILABLE |
| B26_26 | ASL_R | 33.2 | 37.9 | -4.8 | REPLACE | OK |
| B26_26 | ASL_L | 100.1 | 30.8 | 69.4 | REPLACE | OK |
| B26_26 | FSP_R | 66.7 | 53.7 | 13.0 | REPLACE | OK |
| B26_26 | FSP_L | 66.5 | 35.7 | 30.8 | REPLACE | OK |
| B26_26 | FSD_R | 21.4 | 66.5 | -45.0 | REPLACE | OK |
| B26_26 | FSD_L | 23.3 | 40.0 | -16.7 | REPLACE | OK |

### Continuity aggregates (lb640, both hips)

| Family | V5 mean | Best-method mean |
|--------|--------:|-----------------:|
| ASL | 68.9 | 33.9 |
| FSP+FSD | 36.4 | 60.5 |

ASL_L closer to ASM_L than ASL_L (val): V5 **100%** → best method **0%**.

## 8. Protected landmark parity

**Parity:** PASS

By construction, adapter replaces only ASL_R/L and FSP_R/L and FSD_R/L. TD/FHC/ASM/FNM/IT are passed through from frozen V5 without modification.

Protected set (must equal V5): TD_R, TD_L, FHC_R, FHC_L, ASM_R, ASM_L, FNM_R, FNM_L, IT_R, IT_L

Replaceable set only: ASL_R, ASL_L, FSP_R, FSP_L, FSD_R, FSD_L

## 9. Fail-open analysis

Adapter contract evaluated offline: replace target KP only if `status==OK` with image evidence; otherwise `KEEP_V5` / `UNAVAILABLE`.

### ASL (`gradient_search`) counts over 26×2 hips
- OK (replace): 52
- KEEP_V5: 0
- UNAVAILABLE: 0

### Shaft (`hough_axis`) counts over 26×2×2 endpoints
- OK (replace): 29
- KEEP_V5: 0
- UNAVAILABLE: 75

Fail-open is implemented in scoring, but when evidence fires it often still selects the wrong edge — fail-open alone does not make the method safe.

## 10. Failure cases

Cases where effective candidate error exceeds V5 by >20 px (ASL) or >40 px (shaft):

| Case | split | KP | err V5 | err cand | mode | status |
|------|-------|----|-------:|---------:|------|--------|
| B26_04 | train | FSD_L | 130.9 | 1711.1 | REPLACE | OK |
| B26_13 | val | FSP_R | 2.0 | 562.8 | REPLACE | OK |
| B26_07 | train | FSD_L | 57.7 | 539.2 | REPLACE | OK |
| B26_04 | train | FSD_R | 135.8 | 594.6 | REPLACE | OK |
| B26_13 | val | FSD_R | 277.8 | 682.9 | REPLACE | OK |
| B26_13 | val | FSD_L | 401.3 | 799.4 | REPLACE | OK |
| B26_22 | train | FSD_L | 57.1 | 420.4 | REPLACE | OK |
| B26_23 | train | FSP_R | 66.4 | 419.4 | REPLACE | OK |
| B26_20 | val | FSD_R | 80.1 | 433.0 | REPLACE | OK |
| B26_16 | train | FSD_L | 76.2 | 382.6 | REPLACE | OK |
| B26_08 | train | FSP_R | 95.0 | 395.0 | REPLACE | OK |
| B26_22 | train | FSD_R | 127.7 | 417.4 | REPLACE | OK |
| B26_13 | val | FSP_L | 130.7 | 419.8 | REPLACE | OK |
| B26_22 | train | FSP_R | 97.6 | 380.0 | REPLACE | OK |
| B26_07 | train | FSD_R | 157.3 | 422.9 | REPLACE | OK |
| B26_08 | train | FSD_R | 175.0 | 424.2 | REPLACE | OK |
| B26_20 | val | FSP_R | 129.3 | 355.2 | REPLACE | OK |
| B26_04 | train | FSP_R | 143.0 | 366.9 | REPLACE | OK |
| B26_07 | train | FSP_R | 140.5 | 345.2 | REPLACE | OK |
| B26_26 | val | FSD_R | 94.4 | 293.0 | REPLACE | OK |
| B26_15 | train | FSP_L | 98.0 | 281.6 | REPLACE | OK |
| B26_16 | train | ASL_R | 71.9 | 185.3 | REPLACE | OK |
| B26_12 | train | ASL_R | 183.0 | 292.1 | REPLACE | OK |
| B26_15 | train | FSD_L | 76.6 | 176.2 | REPLACE | OK |
| B26_22 | train | FSP_L | 203.1 | 290.1 | REPLACE | OK |
| B26_09 | train | ASL_R | 121.0 | 202.2 | REPLACE | OK |
| B26_26 | val | FSD_L | 102.6 | 176.2 | REPLACE | OK |
| B26_20 | val | ASL_R | 94.1 | 167.1 | REPLACE | OK |
| B26_23 | train | FSD_R | 185.2 | 254.9 | REPLACE | OK |
| B26_14 | train | ASL_R | 180.5 | 239.2 | REPLACE | OK |
| B26_10 | val | ASL_R | 166.8 | 225.5 | REPLACE | OK |
| B26_01 | train | ASL_R | 228.5 | 281.7 | REPLACE | OK |
| B26_07 | train | FSP_L | 285.8 | 331.3 | REPLACE | OK |
| B26_02 | train | ASL_R | 125.0 | 169.2 | REPLACE | OK |
| B26_19 | train | ASL_R | 201.9 | 239.8 | REPLACE | OK |
| B26_21 | train | ASL_R | 215.5 | 251.7 | REPLACE | OK |
| B26_13 | val | ASL_R | 94.2 | 121.8 | REPLACE | OK |
| B26_11 | train | ASL_R | 42.5 | 64.8 | REPLACE | OK |
| B26_06 | train | ASL_R | 167.4 | 188.7 | REPLACE | OK |
| B26_26 | val | ASL_R | 146.2 | 167.2 | REPLACE | OK |

## 11. Best candidate method

- **ASL:** `gradient_search` — large relative gain but residual still coarse (val_mean=132.9, %<50=0.0); train_imp=0.67 val_imp=0.72; asm_conf_train=0.14, asm_conf_val=0.00
- **Shaft:** `NONE` — worsens or unstable; train_imp=-0.49 val_imp=-0.69; 

Renders use these methods (or combined fallback if NONE). 26 overlays written including all 5 continuity cases.

## 12. Risks

- **Wrong-edge risk:** strongest acetabular/shaft gradients are often not the sourcil lateral endpoint or FOV shaft end.
- **ASL_L medial collapse:** if search fails early, candidates remain near ASM (same failure mode as V5).
- **Small-n overfitting of constants:** TRAIN sourcil/shaft length priors can bias VAL if anatomy differs.
- **ROI not independent:** 52 hips ≠ 52 patients; apparent gains can be case-specific.
- **No clinical validity** claimed; pixel error only.
- Implementing a fragile adapter would look like remediation while leaving catastrophic tails.

## 13. Recommendation

**Do not implement** non-learned ASL/FSP/FSD refinement in production or as a wired adapter. Shaft non-learned search is unsafe (wrong-edge / catastrophic tails). ASL_L gradient/lateral search shows that the **image contains recoverable lateral sourcil signal** (ASM-confusion collapses), but residual localization remains too coarse for a safe always-on correction on this 26-case corpus with 0 independent test cases. Prefer waiting for adequate independent data (Phase 10C Step D) before any learned specialist; keep V5 frozen; do not treat formula ASL offsets as the primary remediation.

Optional research only (non-production): stricter multi-method consensus fail-open for ASL_L, evaluated offline without touching production.

---

PHASE_10E0_STATUS:
NONLEARNED_AUDIT_COMPLETE

ASL_NONLEARNED_PROMISING:
YES

SHAFT_NONLEARNED_PROMISING:
NO

BEST_ASL_METHOD:
gradient_search

BEST_SHAFT_METHOD:
NONE

TRAINING_STARTED:
NO

PRODUCTION_MODIFIED:
NO

V5_MODIFIED:
NO

MVP_GEOMETRY_MODIFIED:
NO

SAFE_TO_PROCEED:
NO

RECOMMENDATION:
ASL_L image signal exists but residual/bilateral/test-set limits block implementation; shaft non-learned UNSAFE; do not train; keep V5 frozen.
