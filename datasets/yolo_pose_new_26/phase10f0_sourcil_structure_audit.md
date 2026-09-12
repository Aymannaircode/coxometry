# Phase 10F-0 — Acetabular Sourcil Structure Audit

**Mode:** isolated audit artifacts only; no training/inference or production/model/label/dataset/calibration/Flutter/PDF/`mvp_geometry` changes.  
**Frozen predictions:** `predictions_v2` (V5 KP0–13 equivalent).  
**Cases:** 21 TRAIN calibration cases, then 5 frozen continuity validation cases.  

## 1. Executive verdict

Sourcil structure detectability is **PARTIAL**. The frozen research candidate is `ASL_L:oriented_path+raw_lateral+geometry; ASL_R:NONE`. ASL_L research signal: **YES**; ASL_R: **NO**. A mean-error or coarse lateral gain is not evidence that the sourcil structure is localized: detectability additionally requires meaningful <75 px accuracy and limited systematic vertical bias. The endpoint remains projection-dependent, confounders are not independently identified, and there is no independent test set.

## 2. ASL definition used

ASL is the lateral edge of the radiographic/sclerotic sourcil (weight-bearing acetabular roof), not the lateral bony rim, osteophyte tip, or strongest acetabular pixel. The detected object is treated as a projected segment whose lateral endpoint can be ambiguous. Repository keypoint order was respected: `TD_R, TD_L, FHC_R, FHC_L, ASL_R, ASL_L, ASM_R, ASM_L, FNM_R, FNM_L, FSP_R, FSP_L, FSD_R, FSD_L, IT_R, IT_L`.

## 3. ROI construction

ROI uses frozen TD/FHC/ASM only. A TRAIN-only grid adaptively expanded lateral and superior ranges (and supporting medial/inferior ranges) until full containment, then chose the smallest mean-image-area candidate with exactly 42/42 TRAIN ASL and 126/126 frozen anchors.

Frozen measured margins in FHC–ASM scale units: `{"lateral": 1.8, "medial": 0.1, "superior": 1.0, "inferior": 0.15}`. Chosen at adaptive stage 2 after 768 candidates; TRAIN counts are 42/42 ASL and 126/126 anchors. Mean image fraction is `17.5%`.

| Split | mean width | mean height | mean area px² | image % | GT ASL contained | TD/FHC/ASM contained |
|---|---:|---:|---:|---:|---:|---:|
| TRAIN | 946.5 | 1320.8 | 1257250.3 | 17.5 | 100.0% | 100.0% |
| VAL | 967.2 | 1348.4 | 1307786.9 | 17.5 | 100.0% | 100.0% |

## 4. Candidate sourcil detection methods

Multiple coherent segments per hip were generated from: Sobel thresholded connected components + local line fitting; Scharr components + fitting; Canny components + fitting; Canny probabilistic Hough segments; and local oriented traces over the frozen TRAIN orientation range. For each trace, the fixed algorithm derives a 75th-percentile threshold from positive ROI Sobel response, closes only bounded gaps of at most two samples, isolates contiguous strong-evidence runs, and emits up to three meaningful runs. Oriented-path endpoints are evidence-run ends—not max trace length or ROI boundaries. No method selects a single strongest pixel. CSV metadata includes run threshold, point count, span, strong fraction, and closed-gap count.

## 5. Candidate scoring

TRAIN-only search independently froze method scope, endpoint, profile, confidence threshold, and side gate for R and L. Score features: gradient mean/std, local contrast, continuity, orientation consistency/residual, distances to ASM/FHC/TD, laterality, ROI membership, length plausibility, and cross-method endpoint agreement.

| Side | raw method | endpoint | profile | raw TRAIN objective | V5 TRAIN objective | selective policy |
|---|---|---|---|---:|---:|---|
| ASL_R | oriented_path | raw_lateral | continuity | 284.2 | 196.7 | STATIC_KEEP_V5 |
| ASL_L | oriented_path | raw_lateral | geometry | 139.8 | 709.5 | NONSELECTIVE_REPLACE |

TRAIN-frozen geometry: `{"length_mean": 536.5893317128607, "length_std": 63.82581355302022, "length_p05": 438.34560895500164, "length_p50": 530.9233587719646, "length_p95": 626.2305037247463, "length_p10": 463.41559771991734, "length_p90": 616.7764661546319, "angle_p05": -0.5758675232222633, "angle_p50": -0.13600189624247205, "angle_p95": 0.22515175807866572}`.

**Leakage controls:**
- Train split loaded first; validation labels not loaded during calibration.
- Adaptive ROI grid, margins, orientation/length ranges, per-side method/endpoint/profile, per-side gate, and per-side confidence threshold use TRAIN GT only.
- Validation candidate generation/ranking uses image pixels, frozen TD/FHC/ASM predictions, and frozen parameters only.
- Validation GT is loaded only after frozen_calibration_complete=true and used only for metrics/renders.

## 6. ASL endpoint extraction

Every segment tests five definitions: raw anatomical lateral endpoint; robust 90th-percentile lateral endpoint; fitted-line endpoint; continuity-trimmed endpoint; and `extra_articular_guard`, which retracts excessive/inconsistent extensions using only segment length, orientation residual, and continuity. The guard does not detect or label AIIS.

## 7. ASL_R results

| Split/method | mean | median | p90 | max | mean dx | mean dy | %<25 | %<50 | %<75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train V5 | 142.9 | 153.6 | 215.5 | 233.6 | 75.9 | 16.6 | 0.0 | 4.8 | 19.0 |
| train gradient_search | 154.9 | 150.8 | 251.7 | 292.1 | 57.1 | 82.3 | 4.8 | 9.5 | 23.8 |
| train structure_raw | 203.1 | 208.6 | 324.4 | 388.9 | 89.3 | -39.3 | 0.0 | 9.5 | 14.3 |
| train selective_effective | 142.9 | 153.6 | 215.5 | 233.6 | 75.9 | 16.6 | 0.0 | 4.8 | 19.0 |
| val V5 | 147.7 | 146.2 | 209.1 | 237.4 | 74.4 | -37.0 | 0.0 | 0.0 | 0.0 |
| val gradient_search | 172.8 | 167.2 | 208.3 | 225.5 | -19.5 | 74.3 | 0.0 | 0.0 | 0.0 |
| val structure_raw | 253.8 | 250.5 | 322.8 | 343.4 | 28.8 | -20.3 | 0.0 | 0.0 | 0.0 |
| val selective_effective | 147.7 | 146.2 | 209.1 | 237.4 | 74.4 | -37.0 | 0.0 | 0.0 | 0.0 |

Right and left were ranked independently per image under one frozen mirrored-orientation algorithm. Bilateral context is reviewed in paired overlays and side-level tables only; it does not enter ranking, and one side never supplies its GT or endpoint to the other. The observed asymmetry supports side-specific QC.

## 8. ASL_L results

| Split/method | mean | median | p90 | max | mean dx | mean dy | %<25 | %<50 | %<75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train V5 | 538.2 | 529.4 | 685.3 | 813.8 | -490.1 | 185.7 | 0.0 | 0.0 | 0.0 |
| train gradient_search | 178.7 | 168.3 | 289.9 | 346.2 | -85.2 | 115.9 | 0.0 | 0.0 | 9.5 |
| train structure_raw | 93.5 | 60.1 | 185.1 | 387.1 | -13.6 | -32.7 | 23.8 | 38.1 | 57.1 |
| train selective_effective | 93.5 | 60.1 | 185.1 | 387.1 | -13.6 | -32.7 | 23.8 | 38.1 | 57.1 |
| val V5 | 471.7 | 441.5 | 604.0 | 704.0 | -451.3 | 120.7 | 0.0 | 0.0 | 0.0 |
| val gradient_search | 132.9 | 135.6 | 184.5 | 205.8 | -47.3 | 62.4 | 0.0 | 0.0 | 0.0 |
| val structure_raw | 98.7 | 81.5 | 178.8 | 222.2 | 36.5 | -70.9 | 20.0 | 20.0 | 40.0 |
| val selective_effective | 98.7 | 81.5 | 178.8 | 222.2 | 36.5 | -70.9 | 20.0 | 20.0 | 40.0 |

The ASL_L result is assessed independently because frozen V5 has a known medial-collapse failure. Frozen structure <75 px accuracy is 40.0% with mean dy -70.9 px; mean improvement alone is not structure-detectability or implementation evidence.

## 9. ASM/ASL confusion

Definition: ASL_L candidate is closer to GT ASM_L than to GT ASL_L.

| Split | V5 | gradient_search | structure raw | selective effective |
|---|---:|---:|---:|---:|
| TRAIN | 95.2% | 14.3% | 0.0% | 0.0% |
| VAL | 100.0% | 0.0% | 0.0% | 0.0% |

## 10. Extra-articular confounders

Possible visual confounders include AIIS contribution, lateral rim, osteophyte-like edges, pelvic cortical edges, and projected/overlapping bone. Geometry can reject some excessive or discontinuous extensions but these structures cannot be reliably named or separated from available pixels and landmarks. **AMBIGUOUS — DO NOT AUTOMATE.** No anatomical auto-labels were produced.

## 11. Fail-open analysis

Confidence combines frozen candidate quality and cross-method consensus. Thresholds were calibrated independently on TRAIN. A disabled side still reports its diagnostic threshold, but its effective threshold is infinity and its policy is static `KEEP_V5`.

| Side | policy | TRAIN threshold | split | coverage | precision-of-improvement | false replacements | replacements |
|---|---|---:|---|---:|---:|---:|---:|
| ASL_R | STATIC_KEEP_V5 | 0.5159 | TRAIN | 0.0% | 0.0% | 0 | 0 |
| ASL_R | STATIC_KEEP_V5 | 0.5159 | VAL | 0.0% | 0.0% | 0 | 0 |
| ASL_L | NONSELECTIVE_REPLACE | -1.0000 | TRAIN | 100.0% | 100.0% | 0 | 21 |
| ASL_L | NONSELECTIVE_REPLACE | -1.0000 | VAL | 100.0% | 100.0% | 0 | 5 |
| OVERALL | mixed | — | TRAIN | 50.0% | 100.0% | 0 | 21 |
| OVERALL | mixed | — | VAL | 50.0% | 100.0% | 0 | 5 |

Confidence-driven selectivity exists: **NO** (R=False, L=False). Static side gating is reported separately and is not counted as image-level fail-open selectivity. A train-fit threshold is not evidence by itself; partial coverage with separation of improving/regressing cases must persist on frozen validation.

## 12. Continuity validation

All parameters were frozen before the five validation labels were loaded. Critical original-pixel comparisons (GT coordinates are represented through errors; overlays mark GT, V5, gradient, raw/effective structure candidate, ASM, ROI, and several segments):

| Case | side | V5 err | gradient err | structure err | selective err |
|---|---|---:|---:|---:|---:|
| B26_10 | R | 166.8 | 225.5 | 243.1 | 166.8 |
| B26_10 | L | 454.0 | 90.6 | 61.7 | 61.7 |
| B26_13 | R | 94.2 | 121.8 | 343.4 | 94.2 |
| B26_13 | L | 412.4 | 152.4 | 222.2 | 222.2 |
| B26_17 | R | 237.4 | 182.7 | 250.5 | 237.4 |
| B26_17 | L | 346.6 | 79.9 | 81.5 | 81.5 |
| B26_20 | R | 94.1 | 167.1 | 291.8 | 94.1 |
| B26_20 | L | 704.0 | 205.8 | 14.6 | 14.6 |
| B26_26 | R | 146.2 | 167.2 | 140.0 | 146.2 |
| B26_26 | L | 441.5 | 135.6 | 113.6 | 113.6 |

**Required visual review:** B26_20 L shows a roof-aligned evidence run ending near GT rather than at the ROI boundary. B26_10 L is a shorter superior-roof run whose endpoint remains superolaterally displaced and could be cortical/rim overlap. B26_17 L is roof-aligned but still ends about 81.5 px from GT. Their magenta segments are bounded evidence runs, not full rays; however, the images do not establish that the runs are specifically sourcil rather than overlapping cortex/rim. Raw R paths are frequently unrelated cortical runs and remain disabled. Visual assessment: coarse left roof signal, not robust sourcil localization.

Twenty-six broad-context overlays were generated, including every validation case.

## 13. Failure cases

A failure below means raw or selective error regressed by >5 original pixels versus V5.

| Case | split | side | V5 | raw structure | selective |
|---|---|---|---:|---:|---:|
| B26_01 | train | R | 228.5 | 324.4 | 228.5 |
| B26_02 | train | R | 125.0 | 158.5 | 125.0 |
| B26_04 | train | R | 82.2 | 175.5 | 82.2 |
| B26_05 | train | R | 233.6 | 280.2 | 233.6 |
| B26_07 | train | R | 52.7 | 286.9 | 52.7 |
| B26_08 | train | R | 93.2 | 208.6 | 93.2 |
| B26_11 | train | R | 42.5 | 79.6 | 42.5 |
| B26_14 | train | R | 180.5 | 217.2 | 180.5 |
| B26_15 | train | R | 145.7 | 312.9 | 145.7 |
| B26_16 | train | R | 71.9 | 204.8 | 71.9 |
| B26_18 | train | R | 62.8 | 74.0 | 62.8 |
| B26_19 | train | R | 201.9 | 209.7 | 201.9 |
| B26_21 | train | R | 215.5 | 336.1 | 215.5 |
| B26_22 | train | R | 200.8 | 388.9 | 200.8 |
| B26_23 | train | R | 153.6 | 305.1 | 153.6 |
| B26_24 | train | R | 181.9 | 287.4 | 181.9 |
| B26_10 | val | R | 166.8 | 243.1 | 166.8 |
| B26_13 | val | R | 94.2 | 343.4 | 94.2 |
| B26_17 | val | R | 237.4 | 250.5 | 237.4 |
| B26_20 | val | R | 94.1 | 291.8 | 94.1 |

## 14. Best research candidate

Side-specific TRAIN outcome: `ASL_L:oriented_path+raw_lateral+geometry; ASL_R:NONE`. Each side's best raw structure trial remains reported even when its selective policy is `KEEP_V5`. Coarse lateral rescue is distinguished from actual structure localization using <75 px accuracy, vertical bias, tails, and visual path review. These are research candidates, not validated anatomical detectors. Candidate-level data, evidence-run metadata, and all endpoint variants are retained in `phase10f0_sourcil_structure_metrics.csv`.

## 15. Risks

- Five validation cases are continuity cases, not an independent test set.
- Two hips are not independent patients; patient count remains 26.
- Projection, sclerosis fade-out, and overlap can make the endpoint intrinsically ambiguous.
- Connected and Hough segments can follow a coherent but wrong cortical structure.
- Side asymmetry makes a universal always-on correction unsafe; side-specific QC remains necessary.
- GT is a point annotation for a potentially span-like radiographic structure.

## 16. Recommendation

Retain this as an isolated research audit only. Do not wire an adapter, alter labels, or train from these results. The absence of an independent test and the inability to distinguish extra-articular overlap conservatively force `SAFE_TO_IMPLEMENT: NO`, even if one side's mean improves.

PHASE_10F0_STATUS:
COMPLETE
SOURCIL_STRUCTURE_DETECTABLE:
PARTIAL
ASL_L_STRUCTURE_SIGNAL:
MODERATE
ASL_R_STRUCTURE_SIGNAL:
WEAK
SELECTIVE_FAIL_OPEN_POSSIBLE:
NO
BEST_METHOD:
ASL_L:oriented_path+raw_lateral+geometry; ASL_R:NONE
ASL_L_RESEARCH_PROMISING:
YES
ASL_R_RESEARCH_PROMISING:
NO
TRAINING_STARTED:
NO
PRODUCTION_MODIFIED:
NO
V5_MODIFIED:
NO
MVP_GEOMETRY_MODIFIED:
NO
LABELS_MODIFIED:
NO
SAFE_TO_IMPLEMENT:
NO
RECOMMENDATION:
Research signal only; ambiguous overlap and no independent test block implementation.
