# Phase 10G-0 — ASL_L Success / Failure Analysis

## 1. Executive verdict

The success/failure pattern is **PARTIAL**, and confidence-gate feasibility is **UNCERTAIN**. This audit reproduces the frozen `oriented_path + raw_lateral + geometry` candidate and evaluates reliability separately from improvement. TRAIN contains 12/21 candidates below 75 px; frozen VAL contains 2/5. The five continuity cases are too few and already reused to justify implementation; all findings are feature-discovery evidence only.

Leakage control: frozen Phase 10F parameters were loaded first; image-derived candidates and features were generated without validation GT. Validation GT was then used only to compute retrospective errors, classifications, endpoint-variant errors, and visual marks. No parameter or threshold was selected on VAL.

## 2. Validation case summary

| Case | Class | V5 err | candidate err | dx | dy | conf | length | continuity | orientation | grad mean | grad SD | contrast | d ASM | d FHC | d TD | ROI x | ROI y | endpoint |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B26_10 | SUCCESS | 454.01 | 61.65 | -28.37 | -54.74 | 0.50 | 185.14 | 0.64 | -11.88 | 16.61 | 6.02 | 5.21 | 533.08 | 584.58 | 1216.03 | 0.72 | 0.20 | raw_lateral |
| B26_13 | FAILURE | 412.39 | 222.21 | 93.47 | -201.59 | 0.50 | 260.00 | 0.65 | -32.99 | 25.53 | 10.64 | 9.56 | 559.75 | 726.21 | 1391.78 | 0.64 | 0.04 | raw_lateral |
| B26_17 | FAILURE | 346.63 | 81.48 | 0.27 | -81.48 | 0.53 | 536.00 | 0.65 | -10.05 | 27.91 | 8.22 | 6.15 | 545.08 | 555.50 | 1164.89 | 0.78 | 0.18 | raw_lateral |
| B26_20 | STRONG SUCCESS | 704.01 | 14.59 | 3.60 | -14.14 | 0.57 | 525.75 | 0.63 | -19.57 | 33.17 | 14.71 | 11.50 | 531.13 | 590.62 | 1251.29 | 0.66 | 0.15 | raw_lateral |
| B26_26 | FAILURE | 441.55 | 113.63 | 113.60 | -2.74 | 0.57 | 516.19 | 0.65 | 5.47 | 38.69 | 13.40 | 11.32 | 522.18 | 466.81 | 1169.58 | 0.65 | 0.29 | raw_lateral |

Candidate coordinates and `dx/dy` are in original pixels; `dx/dy = candidate − GT`. ROI positions are fractions of the frozen ROI. `candidate_confidence` is the pre-existing Phase 10F score, not a validated reliability probability.

## 3. Successful cases

| Case | Class | error | dx | dy | endpoint spread | method spread | gradient | continuity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B26_10 | SUCCESS | 61.65 | -28.37 | -54.74 | 52.14 | 576.15 | 16.61 | 0.64 |
| B26_20 | STRONG SUCCESS | 14.59 | 3.60 | -14.14 | 291.87 | 304.00 | 33.17 | 0.63 |

B26_20 is the only strong success. B26_10 is a success by the fixed 75 px definition but remains visibly displaced; this distinction matters when interpreting confidence.

**Visual comparison.** B26_20 has a long oblique evidence run whose raw and fitted endpoints terminate at GT, although its continuity-trimmed endpoint retracts by about 284 px. B26_10 has a much shorter, low-gradient superior-roof run; its endpoint is still 55 px superior and 28 px medial to GT. Thus strong success and ordinary success do not share a single segment-length or image-strength signature.

## 4. Failed cases

| Case | error | dx | dy | endpoint spread | method spread | gradient | continuity | line residual |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B26_13 | 222.21 | 93.47 | -201.59 | 64.29 | 409.18 | 25.53 | 0.65 | 4.56 |
| B26_17 | 81.48 | 0.27 | -81.48 | 478.64 | 241.85 | 27.91 | 0.65 | 4.81 |
| B26_26 | 113.63 | 113.60 | -2.74 | 454.93 | 554.16 | 38.69 | 0.65 | 4.38 |

Failures are not one homogeneous mode: B26_13 is a large endpoint/location miss, while B26_17 and B26_26 are near-miss roof-aligned detections just beyond the 75 px boundary.

**Visual comparison.** B26_13 selects a steep superolateral iliac/cortical run near the top ROI boundary (`ROI y=0.04`) rather than the annotated roof endpoint; all endpoint variants remain tightly clustered around that wrong structure. B26_17 follows a shallow roof-aligned run but stays about 81 px superior to GT; its fitted endpoint falls just below the 75 px boundary while continuity trimming collapses medially. B26_26 follows a near-horizontal edge through the GT level but the raw endpoint overshoots laterally by 114 px; the robust endpoint is substantially better (62 px). These are respectively wrong-structure, vertical-offset, and lateral-overshoot failures.

## 5. Image-quality comparison

| Case | ROI range | grad mean | grad p90 | edge density | noise | Laplacian var | clip low | clip high | roof proxy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B26_10 | 109.000 | 7.695 | 16.000 | 0.000 | 1.771 | 61.188 | 0.000 | 0.000 | 2.158 |
| B26_13 | 162.000 | 11.437 | 24.207 | 0.002 | 1.619 | 35.633 | 0.000 | 0.000 | 2.232 |
| B26_17 | 145.000 | 14.615 | 27.019 | 0.001 | 5.049 | 516.022 | 0.000 | 0.000 | 1.910 |
| B26_20 | 183.000 | 13.323 | 28.636 | 0.002 | 3.849 | 291.090 | 0.018 | 0.000 | 2.490 |
| B26_26 | 130.000 | 20.247 | 36.688 | 0.005 | 6.517 | 880.024 | 0.001 | 0.000 | 1.911 |

Comparative medians: ROI gradient (success median 10.5; failure median 14.6); edge density (success median 0.0; failure median 0.0); noise (success median 2.8; failure median 5.0); Laplacian variance (success median 176.1; failure median 516.0). The roof-visibility value is an image proxy (selected-segment gradient / ROI mean gradient), not a clinical quality score or threshold.

## 6. Sourcil structure comparison

| Case | length | continuity | closed gap points | gradient | gradient CV | orientation consistency | line residual mean | line residual p90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B26_10 | 185.141 | 0.638 | 7 | 16.606 | 0.363 | 0.749 | 4.277 | 7.727 |
| B26_13 | 260.000 | 0.652 | 9 | 25.532 | 0.417 | 0.803 | 4.559 | 8.797 |
| B26_17 | 536.000 | 0.652 | 16 | 27.914 | 0.295 | 0.894 | 4.811 | 8.873 |
| B26_20 | 525.751 | 0.634 | 16 | 33.173 | 0.444 | 0.895 | 4.669 | 8.568 |
| B26_26 | 516.187 | 0.646 | 16 | 38.687 | 0.346 | 0.899 | 4.377 | 9.156 |

Successful-case medians versus failures: length (success median 355.4; failure median 516.2); gradient (success median 24.9; failure median 27.9); continuity (success median 0.6; failure median 0.7); line residual (success median 4.5; failure median 4.6). These comparisons determine whether the intuitive 'longer/stronger/cleaner' hypothesis is actually supported.

## 7. Endpoint stability

| Case | raw err | robust err | fit err | trim err | guard err | max spread | RMS spread |
|---|---:|---:|---:|---:|---:|---:|---:|
| B26_10 | 61.65 | 71.73 | 56.75 | 92.76 | 61.65 | 52.14 | 20.35 |
| B26_13 | 222.21 | 199.06 | 225.23 | 171.43 | 222.21 | 64.29 | 25.35 |
| B26_17 | 81.48 | 82.11 | 74.85 | 468.69 | 81.48 | 478.64 | 187.26 |
| B26_20 | 14.59 | 48.54 | 8.07 | 283.92 | 14.59 | 291.87 | 113.30 |
| B26_26 | 113.63 | 61.83 | 113.16 | 341.85 | 113.63 | 454.93 | 177.93 |

A. Partially. Successful cases have tighter endpoint variants in this sample. B. Failure-case divergence is therefore not consistently greater. C. Endpoint disagreement alone is not established as a confidence signal; it remains a continuous feature, with no threshold chosen.

## 8. Cross-method agreement

| Case | methods | similar endpoints | similarity radius | endpoint spread mean | endpoint spread max | orientation SD | location spread |
|---|---:|---:|---:|---:|---:|---:|---:|
| B26_10 | 5 | 1 | 53.09 | 576.15 | 961.68 | 35.45 | 502.71 |
| B26_13 | 5 | 3 | 53.09 | 409.18 | 695.56 | 29.54 | 374.66 |
| B26_17 | 5 | 1 | 53.09 | 241.85 | 555.18 | 17.47 | 233.39 |
| B26_20 | 5 | 3 | 53.09 | 304.00 | 507.42 | 37.04 | 307.46 |
| B26_26 | 5 | 1 | 53.09 | 554.16 | 918.69 | 42.76 | 502.72 |

Successful cases have **not higher** method agreement by median endpoint spread. The similar-endpoint count uses a predeclared scale-relative descriptive radius of 10% of TRAIN median ASM→ASL length; it is not a proposed gate.

## 9. V5-to-candidate displacement

| Case | V5→candidate | V5 err | candidate err | Class |
|---|---:|---:|---:|---:|
| B26_10 | 440.65 | 454.01 | 61.65 | SUCCESS |
| B26_13 | 602.79 | 412.39 | 222.21 | FAILURE |
| B26_17 | 372.48 | 346.63 | 81.48 | FAILURE |
| B26_20 | 712.27 | 704.01 | 14.59 | STRONG SUCCESS |
| B26_26 | 555.15 | 441.55 | 113.63 | FAILURE |

Displacement comparison: success median 576.5; failure median 555.2. Large movement is expected because V5 is medially collapsed, but movement magnitude is not treated as evidence of correctness.

## 10. ASM separation

| Case | candidate→ASM | normalized ASM separation | candidate err | Class |
|---|---:|---:|---:|---:|
| B26_10 | 533.08 | 1.47 | 61.65 | SUCCESS |
| B26_13 | 559.75 | 1.51 | 222.21 | FAILURE |
| B26_17 | 545.08 | 1.69 | 81.48 | FAILURE |
| B26_20 | 531.13 | 1.45 | 14.59 | STRONG SUCCESS |
| B26_26 | 522.18 | 1.32 | 113.63 | FAILURE |

ASM separation comparison: success median 532.1; failure median 545.1. No fixed 'too close' cutoff is selected.

## 11. Geometric consistency

| Case | segment length | length z | orientation | angle Δ TRAIN center | ASM ratio | FHC ratio | TD ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| B26_10 | 185.141 | -5.506 | -11.876 | 4.084 | 1.468 | 1.610 | 3.349 |
| B26_13 | 260.000 | -4.334 | -32.995 | 25.202 | 1.508 | 1.957 | 3.751 |
| B26_17 | 536.000 | -0.009 | -10.047 | 2.255 | 1.685 | 1.717 | 3.601 |
| B26_20 | 525.751 | -0.170 | -19.566 | 11.773 | 1.448 | 1.611 | 3.412 |
| B26_26 | 516.187 | -0.320 | 5.472 | 13.264 | 1.323 | 1.183 | 2.963 |

Length z-scores and angle deltas use only frozen TRAIN geometry. Anchor relationships use frozen FHC, TD, and ASM predictions. They are references for plausibility, not validation-tuned acceptance rules.

## 12. TRAIN feature analysis

TRAIN-only outcome is candidate error <75 px. AUC is direction-normalized (`max(AUC, 1−AUC)`) to express separation strength, not a deployable threshold.

| Feature | reliable median | poor median | Spearman vs error | TRAIN sep AUC | VAL directed AUC |
|---|---:|---:|---:|---:|---:|
| roof visibility proxy | 2.544 | 1.953 | -0.610 | 0.880 | 0.833 |
| cross-method similar endpoint count | 2.000 | 1.000 | -0.683 | 0.875 | 0.583 |
| ROI edge density | 0.001 | 0.003 | 0.490 | 0.815 | 0.833 |
| ROI gradient mean | 12.500 | 15.243 | 0.570 | 0.806 | 0.833 |
| FHC distance / FHC-ASM scale | 1.555 | 1.689 | 0.244 | 0.787 | 0.667 |
| TD distance / FHC-ASM scale | 3.376 | 3.624 | 0.261 | 0.787 | 0.667 |
| ROI gradient p90 | 25.767 | 29.967 | 0.488 | 0.759 | 0.667 |
| gradient coefficient of variation | 0.382 | 0.346 | -0.543 | 0.741 | 0.833 |

With 21 TRAIN cases, these are exploratory univariate associations. Correlated measurements and selection of the top entries inflate apparent evidence; no holdout or inferential claim is made.

## 13. Candidate confidence signals

| Case | TRAIN-directed score | candidate err | <75 |
|---|---:|---:|---:|
| B26_10 | 0.466 | 61.654 | 1 |
| B26_13 | 0.002 | 222.211 | 0 |
| B26_17 | -0.204 | 81.476 | 0 |
| B26_20 | 0.323 | 14.591 | 1 |
| B26_26 | -0.301 | 113.629 | 0 |

The displayed score is an analysis-only equal-weight summary of the six strongest TRAIN univariate directions, without a threshold and without VAL fitting. Its descriptive five-case direction-normalized AUC is 1.000. This perfect rank is not a validated gate: the six inputs were selected after examining TRAIN associations, several are strongly correlated, there is no frozen operating threshold, and the five continuity cases are reused rather than independent. A useful confidence mechanism must identify wrong candidates, not merely candidates that improve on V5; current evidence supports a hypothesis, not feasibility.

## 14. Failure modes

- Coherent wrong-structure selection: a long, continuous, high-gradient cortical/rim overlap can score well while ending far from ASL.
- False agreement: B26_13 has three similar method endpoints and tightly clustered endpoint variants, yet is the largest failure. Agreement can therefore be confidently wrong.
- Endpoint localization error: the selected run follows the roof but terminates before or beyond the annotated lateral endpoint.
- Near-boundary cases: B26_17 is close to the 75 px definition, so binary labels exaggerate separation from B26_10.
- Cross-method disagreement can reflect different valid-looking projected edges, but agreement can also occur on the same wrong structure.
- Global image quality does not guarantee local sourcil identity; strong gradients and sharpness can strengthen confounders.

## 15. Recommendation

Do not implement a confidence gate. Preserve ASL_R, FSP/FSD, V5, geometry, labels, and production exactly as frozen. The best exploratory features are: roof visibility proxy, ROI edge density, ROI gradient mean, FHC distance / FHC-ASM scale, TD distance / FHC-ASM scale. They require confirmation on a genuinely independent, prospectively frozen set and should be evaluated for rejection precision, not only error correlation. If confirmation is pursued, freeze the feature definitions and analysis protocol before collecting or opening new outcomes.

PHASE_10G0_STATUS:
COMPLETE
ASL_L_SUCCESS_FAILURE_PATTERN:
PARTIAL
ENDPOINT_STABILITY_SIGNAL:
NONE
METHOD_AGREEMENT_SIGNAL:
NONE
IMAGE_QUALITY_SIGNAL:
MODERATE
GEOMETRIC_SIGNAL:
WEAK
CONFIDENCE_GATE_FEASIBLE:
UNCERTAIN
BEST_CONFIDENCE_FEATURES:
roof visibility proxy, ROI edge density, ROI gradient mean, FHC distance / FHC-ASM scale, TD distance / FHC-ASM scale
ASL_R_MODIFIED:
NO
FSP_FSD_MODIFIED:
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
Promising multifeature ranking is unvalidated; freeze definitions and require independent confirmation before any gate design.
