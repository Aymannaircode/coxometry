# Phase 9B — Full Landmark Accuracy Audit

**Date:** 2026-09-04
**Mode:** READ-ONLY — no code / model / label / Flutter / PDF / geometry changes
**Validation set:** B26_10, B26_13, B26_17, B26_20, B26_26 (official `labels/val`)
**Sources:** GT `labels/val`; V2 & V5 Phase2 KP0–13 from `_v5_phase2_checkpoint_audit_temp`; IT_R/IT_L from validated `v5_phase2_checkpoint_integration_audit.csv` decode (YOLO shell `.txt` IT slots are placeholders — not used).
**Coordinate space:** letterbox 640×640 (Ultralytics-style pad), unless noted.

---

## 1. Executive verdict

**Primary root cause: `MODEL_ACCURACY` (pre-existing in V2 for KP0–13; IT is separate and relatively accurate).**

Observed PDF/overlay problems are **not** explained by a new V5 Phase 2 regression on legacy landmarks, nor by a Flutter/PDF-only drawing bug as the main driver. KP0–13 V2 vs V5 Phase 2 predictions are **identical / near-identical** (69/70 pairs Δ&lt;1e-5 px; one float micro-diff 6.4e-4 px on B26_26 FNM_R; mean errors identical).

On this 5-image set, legacy KP0–13 mean error is **29.7 px** (640), IT mean error **25.7 px** (9/9 GT v=2). The dominant failure is **ASL_L** (mean **104.9 px**, always too medial). Secondary: FSP_L / FSD_R / FSD_L / ASL_R (means ~33–43 px). These errors exist in **decoded 640 / original coordinates before Flutter or PDF**.

| Question | Answer |
|----------|--------|
| A. V5 ≈ V2 for KP0–13? | **YES — identical / near-identical** |
| B. V5 changed legacy landmarks? | **NO** (frozen cv4; parity confirmed) |
| C. Problem already in V2? | **YES** for KP0–13 visual/anatomical errors |
| IT_R / IT_L wrong like legacy? | **NO** — IT mean ~25–26 px, all &lt;75 px |
| Flutter/PDF invent wrong anatomy? | **Unlikely as primary cause** — same original-px coords feed Results + PDF composer via `BoxFit.contain` |

---

## 2. Per-landmark accuracy table (V5 Phase 2, px640)

| Rank | KP | Name | Group | n | Mean | Median | Max | p90 | &lt;25px | &lt;50px | &lt;75px | &lt;100px |
|-----:|---:|------|-------|--:|-----:|-------:|----:|----:|-------:|-------:|-------:|--------:|
| 1 | 8 | FNM_R | legacy_0_13 | 5 | 13.50 | 12.66 | 23.84 | 21.67 | 100% | 100% | 100% | 100% |
| 2 | 2 | FHC_R | legacy_0_13 | 5 | 13.85 | 9.38 | 30.18 | 24.35 | 80% | 100% | 100% | 100% |
| 3 | 0 | TD_R | legacy_0_13 | 5 | 16.77 | 12.97 | 26.72 | 26.37 | 60% | 100% | 100% | 100% |
| 4 | 1 | TD_L | legacy_0_13 | 5 | 17.32 | 16.77 | 26.95 | 24.24 | 80% | 100% | 100% | 100% |
| 5 | 9 | FNM_L | legacy_0_13 | 5 | 17.79 | 16.21 | 26.40 | 24.51 | 80% | 100% | 100% | 100% |
| 6 | 3 | FHC_L | legacy_0_13 | 5 | 17.80 | 17.75 | 22.39 | 21.36 | 100% | 100% | 100% | 100% |
| 7 | 6 | ASM_R | legacy_0_13 | 5 | 17.91 | 17.30 | 25.47 | 23.65 | 80% | 100% | 100% | 100% |
| 8 | 7 | ASM_L | legacy_0_13 | 5 | 17.92 | 20.33 | 27.26 | 27.06 | 60% | 100% | 100% | 100% |
| 9 | 15 | IT_L | IT | 5 | 23.99 | 24.22 | 29.41 | 28.34 | 60% | 100% | 100% | 100% |
| 10 | 14 | IT_R | IT | 4 | 27.87 | 27.56 | 39.90 | 37.10 | 50% | 100% | 100% | 100% |
| 11 | 10 | FSP_R | legacy_0_13 | 5 | 28.75 | 30.64 | 66.73 | 53.03 | 40% | 80% | 100% | 100% |
| 12 | 4 | ASL_R | legacy_0_13 | 5 | 32.84 | 33.16 | 54.98 | 47.04 | 40% | 80% | 100% | 100% |
| 13 | 13 | FSD_L | legacy_0_13 | 5 | 35.36 | 23.28 | 79.42 | 65.61 | 60% | 80% | 80% | 100% |
| 14 | 12 | FSD_R | legacy_0_13 | 5 | 39.02 | 48.45 | 54.97 | 53.49 | 40% | 60% | 100% | 100% |
| 15 | 11 | FSP_L | legacy_0_13 | 5 | 42.63 | 36.46 | 66.54 | 60.32 | 0% | 60% | 100% | 100% |
| 16 | 5 | ASL_L | legacy_0_13 | 5 | 104.89 | 95.61 | 166.82 | 140.14 | 0% | 0% | 0% | 60% |

### Aggregate

| Pool | n | Mean | Median | Max | p90 | &lt;25 | &lt;50 | &lt;75 | &lt;100 |
|------|--:|-----:|-------:|----:|----:|-----:|-----:|-----:|------:|
| KP0–13 legacy | 70 | 29.74 | 21.55 | 166.82 | 66.56 | 59% | 83% | 91% | 97% |
| KP14–15 IT (v=2) | 9 | 25.71 | 24.55 | 39.90 | 32.43 | 56% | 100% | 100% | 100% |
| All scored | 79 | 29.28 | 22.29 | 166.82 | 57.29 | 58% | 85% | 92% | 97% |

B26_26 `IT_R` GT v=0 → excluded from IT positional stats (model may still emit a point + QC `review`).

---

## 3. Worst landmarks

| Rank | Landmark | Mean err | Median | Max | &lt;75px | Notes |
|-----:|----------|---------:|-------:|----:|-------:|-------|
| 1 | **ASL_L** (KP5) | 104.9 | 95.6 | 166.8 | 0% | bias Δx=-100.5, Δy=26.6 |
| 2 | **FSP_L** (KP11) | 42.6 | 36.5 | 66.5 | 100% | bias Δx=26.1, Δy=32.7 |
| 3 | **FSD_R** (KP12) | 39.0 | 48.5 | 55.0 | 100% | bias Δx=24.1, Δy=-24.1 |
| 4 | **FSD_L** (KP13) | 35.4 | 23.3 | 79.4 | 80% | bias Δx=0.5, Δy=-25.2 |
| 5 | **ASL_R** (KP4) | 32.8 | 33.2 | 55.0 | 100% | bias Δx=16.5, Δy=-7.7 |
| 6 | **FSP_R** (KP10) | 28.8 | 30.6 | 66.7 | 100% | bias Δx=-12.4, Δy=25.6 |

Highest single-case errors:

| Case | Landmark | Err px640 | Placement | Plausible | Conf |
|------|----------|----------:|-----------|-----------|-----:|
| B26_20 | ASL_L | 166.816 | MISPLACED | YES | 0.3065 |
| B26_26 | ASL_L | 100.138 | MISPLACED | YES | 0.3948 |
| B26_10 | ASL_L | 95.612 | LARGE_SHIFT | YES | 0.5286 |
| B26_13 | ASL_L | 81.61 | LARGE_SHIFT | YES | 0.4982 |
| B26_17 | ASL_L | 80.29 | LARGE_SHIFT | YES | 0.6246 |
| B26_13 | FSD_L | 79.424 | LARGE_SHIFT | YES | 0.5145 |
| B26_26 | FSP_R | 66.725 | SYSTEMATIC_SHIFT | YES | 0.6633 |
| B26_26 | FSP_L | 66.539 | SYSTEMATIC_SHIFT | YES | 0.6096 |
| B26_17 | ASL_R | 54.98 | SYSTEMATIC_SHIFT | YES | 0.4624 |
| B26_13 | FSD_R | 54.969 | SYSTEMATIC_SHIFT | YES | 0.5382 |
| B26_10 | FSD_R | 51.264 | SYSTEMATIC_SHIFT | YES | 0.5366 |
| B26_10 | FSP_L | 50.997 | SYSTEMATIC_SHIFT | YES | 0.5834 |

---

## 4. Best landmarks

| Rank | Landmark | Mean err | Median | Max | &lt;25px | &lt;50px |
|-----:|----------|---------:|-------:|----:|-------:|-------:|
| 1 | **FNM_R** (KP8) | 13.5 | 12.7 | 23.8 | 100% | 100% |
| 2 | **FHC_R** (KP2) | 13.9 | 9.4 | 30.2 | 80% | 100% |
| 3 | **TD_R** (KP0) | 16.8 | 13.0 | 26.7 | 60% | 100% |
| 4 | **TD_L** (KP1) | 17.3 | 16.8 | 27.0 | 80% | 100% |
| 5 | **FNM_L** (KP9) | 17.8 | 16.2 | 26.4 | 80% | 100% |
| 6 | **FHC_L** (KP3) | 17.8 | 17.7 | 22.4 | 100% | 100% |

Lowest single-case errors (sample):

| Case | Landmark | Err px640 | Placement | Conf |
|------|----------|----------:|-----------|-----:|
| B26_13 | FSP_R | 0.401 | ACCURATE | 0.5745 |
| B26_10 | ASM_L | 3.72 | ACCURATE | 0.6163 |
| B26_13 | FNM_R | 4.216 | ACCURATE | 0.7063 |
| B26_17 | FHC_R | 4.913 | ACCURATE | 0.6321 |
| B26_17 | FSD_L | 6.075 | ACCURATE | 0.5091 |
| B26_10 | FNM_R | 8.374 | ACCURATE | 0.6857 |
| B26_10 | TD_R | 8.377 | ACCURATE | 0.733 |
| B26_10 | ASM_R | 9.092 | ACCURATE | 0.7087 |

---

## 5. V2 vs V5 comparison (KP0–13)

- Pairwise coordinate Δ (V5 Phase2 txt vs V2 txt, same 5 images × 14 KP): **max=6.400e-04 px**, mean=9.143e-06 px
- Identical within 1e-5: **69/70**; within 0.01 px: 70/70
- Prior checkpoint audit: detection boxes/conf/IoU identical; `kp14_parity` all True; architecture freeze backbone/neck/cv4 confirmed.

| Landmark | V2 mean err | V5 mean err | \|Δmean\| |
|----------|------------:|------------:|--------:|
| TD_R | 16.77 | 16.77 | 0.00e+00 |
| TD_L | 17.32 | 17.32 | 0.00e+00 |
| FHC_R | 13.85 | 13.85 | 0.00e+00 |
| FHC_L | 17.80 | 17.80 | 0.00e+00 |
| ASL_R | 32.84 | 32.84 | 0.00e+00 |
| ASL_L | 104.89 | 104.89 | 0.00e+00 |
| ASM_R | 17.91 | 17.91 | 0.00e+00 |
| ASM_L | 17.92 | 17.92 | 0.00e+00 |
| FNM_R | 13.50 | 13.50 | 2.29e-05 |
| FNM_L | 17.79 | 17.79 | 0.00e+00 |
| FSP_R | 28.75 | 28.75 | 0.00e+00 |
| FSP_L | 42.63 | 42.63 | 0.00e+00 |
| FSD_R | 39.02 | 39.02 | 0.00e+00 |
| FSD_L | 35.36 | 35.36 | 0.00e+00 |

**Verdict:** **A** — V5 and V2 are identical/near-identical for KP0–13. Visual PDF issues on legacy landmarks therefore **already existed in V2** (option C), not introduced by Phase 2 IT training.

---

## 6. Examples of anatomically wrong / high-error landmarks

Heuristic coarse side/order flags alone found 0 side-flip cases; after clinical medial-bias review, **ASL_L is marked anatomically wrong on all 5 images** (CSV `plausibility_flags=systematic_medial_bias_vs_sourcil`). Remaining high-error points are mostly **systematic shifts** (FSP/FSD/ASL_R).

**Important:** coarse side/order checks can still say `YES` while the point is **clinically / anatomically wrong**. The clearest case is **ASL_L**.

### ASL_L — genuine anatomical misplacement (not a uniform overlay shift)

On all 5 validation images, ASL_L is predicted **~73–157 px too medial** (mean Δx = **−100.5** px640) with moderate caudal bias (mean Δy = +26.6). That moves the point off the expected lateral acetabular sourcil toward the joint/center — i.e. **wrong anatomy**, not a small display offset.

| Case | Landmark | GT 640 | Pred 640 | Err | Δx | Conf | Placement | Clinical read |
|------|----------|--------|----------|----:|---:|-----:|-----------|---------------|
| B26_20 | ASL_L | (541.8,205.8) | (384.7,261.9) | 166.8 | −157.1 | 0.31 | MISPLACED | Far too medial |
| B26_26 | ASL_L | (512.6,218.4) | (412.6,223.1) | 100.1 | −100.0 | 0.39 | MISPLACED | Far too medial |
| B26_10 | ASL_L | (531.9,229.9) | (438.0,248.2) | 95.6 | −93.8 | 0.53 | LARGE_SHIFT | Systematic medial |
| B26_13 | ASL_L | (482.7,188.8) | (409.9,225.7) | 81.6 | −72.8 | 0.50 | LARGE_SHIFT | Systematic medial |
| B26_17 | ASL_L | (532.8,266.7) | (454.2,283.5) | 80.3 | −78.5 | 0.62 | LARGE_SHIFT | Systematic medial |
| B26_13 | FSD_L | (504.0,578.9) | (508.1,499.5) | 79.4 | +4.1 | 0.51 | LARGE_SHIFT | Too cranial vs GT |

Confidence for ASL_L is also low (0.31–0.62), consistent with an unreliable head output rather than a remapping artefact.

### Systematic bias (mean pred−GT, px640)

| Landmark | mean Δx | mean Δy | mean \|Δx\| | mean \|Δy\| |
|----------|--------:|--------:|----------:|----------:|
| FNM_R | 0.4 | 7.6 | 9.0 | 7.7 |
| FHC_R | 4.4 | 0.4 | 9.5 | 9.6 |
| TD_R | 4.8 | 4.2 | 13.4 | 8.5 |
| TD_L | 3.6 | 6.4 | 14.5 | 6.4 |
| FNM_L | 9.6 | 14.8 | 9.6 | 14.8 |
| FHC_L | 10.4 | 12.0 | 10.4 | 12.8 |
| ASM_R | 12.8 | -9.6 | 12.8 | 10.1 |
| ASM_L | -1.4 | 0.9 | 10.5 | 12.0 |
| IT_L | 7.2 | -3.7 | 15.7 | 14.7 |
| IT_R | -14.8 | 7.6 | 19.5 | 16.7 |
| FSP_R | -12.4 | 25.6 | 12.5 | 25.6 |
| ASL_R | 16.5 | -7.7 | 27.0 | 14.5 |
| FSD_L | 0.5 | -25.2 | 6.3 | 34.3 |
| FSD_R | 24.1 | -24.1 | 24.1 | 25.3 |
| FSP_L | 26.1 | 32.7 | 26.1 | 32.7 |
| ASL_L | -100.5 | 26.6 | 100.5 | 26.6 |

Large mean \|Δ\| with **consistent sign** ⇒ systematic model bias (ASL_L medial; FSP_L lateral+caudal; FSD_* often cranial).  
ASL_L’s −100 px mean Δx is large enough to count as **genuine misplacement** even when coarse side checks still pass.

---

## 7. Overlay / mapping diagnosis

### Pipeline

```
GT label (norm × original W×H)
  → letterbox to px640  (r, pad_left, pad_top)
V5 raw (KP0–13 via YOLO pose head; IT via ITHead + kpts_decode)
  → decoded px640 = grid × stride   [IT: single stride, validated]
  → original px = (px640 - pad) / scale
API /analyze exposes original-image pixels
Flutter LandmarkOverlay / PDF LandmarkOverlayComposer
  → BoxFit.contain / ImageContainLayout.toDisplay(x,y)
```

### Letterbox params (this audit)

| Case | Orig W×H | r | pad_left | pad_top |
|------|----------|--:|---------:|--------:|
| B26_10 | 3039×2625 | 0.210596 | 0 | 43 |
| B26_13 | 3234×2961 | 0.197897 | 0 | 27 |
| B26_17 | 2763×2442 | 0.231632 | 0 | 37 |
| B26_20 | 2701×2514 | 0.236949 | 0 | 22 |
| B26_26 | 2822×2426 | 0.226790 | 0 | 45 |

GT letterbox vs prior checkpoint GT for IT: max Δ=0.334 px (mean 0.207) — conversion consistent.

### Numerical evidence — wrong **before** Flutter/PDF

For high-error landmarks below, Euclidean error is already large in **decoded 640** and scales consistently into **original** space. Flutter/PDF only apply contain-fit display mapping; they do not invent a different anatomical location.

| Case | LM | Err640 | GT640 | Pred640 | GT orig | Pred orig | Err orig | Class |
|------|----|-------:|-------|---------|---------|-----------|---------:|-------|
| B26_20 | ASL_L | 166.816 | (541.815, 205.763) | (384.735, 261.919) | (2286.6, 775.5) | (1623.7, 1012.5) | 704.0 | MISPLACED |
| B26_26 | ASL_L | 100.138 | (512.579, 218.444) | (412.55, 223.139) | (2260.2, 764.8) | (1819.1, 785.5) | 441.6 | MISPLACED |
| B26_10 | ASL_L | 95.612 | (531.864, 229.889) | (438.027, 248.226) | (2525.5, 887.4) | (2079.9, 974.5) | 454.0 | LARGE_SHIFT |
| B26_13 | ASL_L | 81.61 | (482.684, 188.848) | (409.885, 225.734) | (2439.1, 817.8) | (2071.2, 1004.2) | 412.4 | LARGE_SHIFT |
| B26_17 | ASL_L | 80.29 | (532.752, 266.717) | (454.225, 283.451) | (2300.0, 991.7) | (1961.0, 1064.0) | 346.6 | LARGE_SHIFT |
| B26_13 | FSD_L | 79.424 | (503.991, 578.856) | (508.055, 499.536) | (2546.7, 2788.6) | (2567.3, 2387.8) | 401.3 | LARGE_SHIFT |
| B26_26 | FSP_R | 66.725 | (114.388, 373.151) | (84.125, 432.619) | (504.4, 1446.9) | (370.9, 1709.2) | 294.2 | SYSTEMATIC_SHIFT |

IT example decode chain (B26_10 IT_R from checkpoint audit): raw grid≈(4.64,16.19) × stride 32 → px640≈(148.6,518.0) vs GT≈(173.1,518.7) → **err 24.6 px** already at decode — not a PDF shift.

### Classification of observed visual issues

| Symptom | Likely class | Evidence |
|---------|--------------|----------|
| Landmark near correct bone but offset | **MODEL_ACCURACY** (systematic shift) | Non-zero mean Δx/Δy; still plausible side/order |
| Landmark on wrong anatomy / far | **MODEL_ACCURACY** (misplaced) | Err≫75–100 px640; sometimes plausibility flags |
| Uniform global shift of all points | **COORDINATE_REPROJECTION** (if present) | **Not observed** as dominant pattern; per-KP errors highly heterogeneous |
| Overlay wrong only on screen, API coords OK | **FLUTTER_OVERLAY** | Results uses same original-px + contain layout; not supported as primary |
| Wrong only in PDF export | **PDF_RENDERING** | PDF composer reuses same painter path as Results; secondary risk only |
| Mix of real model error + display | **MIXED** | Possible minor marker-size perception; **does not explain** 100–300 px model errors |

---

## 8. Root cause

1. **KP0–13:** Frozen V2 pose head accuracy limits. Worst families: **ASL**, **FSP**, **FSD** (and variable FNM/TD). Errors are present in offline YOLO predictions vs GT in 640 space.
2. **V5 Phase 2 did not change KP0–13** — IT-only head; parity with V2 is exact on this set.
3. **IT_R / IT_L:** Separate head; **acceptable** positional accuracy (~26 px mean, 100% &lt;75 on scored IT). Not the main “anatomically wrong” PDF complaint for legacy points.
4. **Coordinate / Flutter / PDF pipeline:** Prior E2E bug (API returning preprocess space) was addressed; current design reprojects to original pixels. Heterogeneous per-landmark errors argue against a single global remap bug.
5. Therefore the two visual symptoms map mainly to **model error modes**: (offset = shift) and (wrong bone = misplacement), both **MODEL_ACCURACY**, pre-render.

**Overall problem class:** `MODEL_ACCURACY` (with optional secondary `MIXED` only for marker readability).

---

## 9. Recommended next phase

**Phase 9C — Targeted legacy landmark remediation plan (still no blind retrain):**

1. Prioritize clinical impact: **ASL_*** (VCE), then **FSP/FSD** (CCD), then TD/FNM outliers.
2. Case-level visual QC overlays (GT vs V2/V5) on the same 5 images + a few train failures — confirm shift vs misplacement per KP.
3. Decide remediation path separately: label QA vs refinement post-process vs limited unfreeze/finetune of cv4 — **do not** retrain IT head to “fix” legacy points.
4. Keep IT QC path; optionally tighten display of `review`/`unavailable` so PDF does not over-assert IT.
5. Only if a new uniform offset appears on a specific export path, open a dedicated **COORDINATE_REPROJECTION** ticket with before/after numeric diffs.

---

## 10. What MUST NOT be changed yet

- Do **not** modify `mvp_geometry`, Flutter overlay, or PDF composer based on this audit alone.
- Do **not** retrain V5 Phase 2 IT head / change IT labels to fix KP0–13.
- Do **not** alter official dataset labels without a dedicated B6-style annotation phase.
- Do **not** “fix” coordinates by hard-coded offsets in the app.
- Do **not** swap model checkpoints without a new parity+accuracy gate.

---

## Appendix A — Per image × landmark detail

Full numeric table: `datasets/yolo_pose_new_26/phase9b_landmark_errors.csv`

### B26_10

| KP | Name | GT640 | V5 640 | Err | Conf | V2=V5 Δ | Plausible | Placement |
|---:|------|-------|--------|----:|-----:|--------:|-----------|-----------|
| 0 | TD_R | (267.8,426.3) | (261.4,431.6) | 8.38 | 0.733 | 0.000000 | YES | ACCURATE |
| 1 | TD_L | (363.3,428.1) | (389.3,435.0) | 26.95 | 0.8291 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 2 | FHC_R | (203.9,304.0) | (191.2,295.0) | 15.62 | 0.6701 | 0.000000 | YES | ACCURATE |
| 3 | FHC_L | (430.0,301.2) | (443.9,310.2) | 16.58 | 0.7643 | 0.000000 | YES | ACCURATE |
| 4 | ASL_R | (98.3,223.4) | (133.2,219.3) | 35.12 | 0.5034 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 5 | ASL_L | (531.9,229.9) | (438.0,248.2) | 95.61 | 0.5286 | 0.000000 | YES | LARGE_SHIFT |
| 6 | ASM_R | (224.3,233.6) | (233.4,233.6) | 9.09 | 0.7087 | 0.000000 | YES | ACCURATE |
| 7 | ASM_L | (416.1,242.9) | (415.6,239.2) | 3.72 | 0.6163 | 0.000000 | YES | ACCURATE |
| 8 | FNM_R | (157.6,338.3) | (164.9,342.4) | 8.37 | 0.6857 | 0.000000 | YES | ACCURATE |
| 9 | FNM_L | (468.9,345.7) | (475.6,352.9) | 9.84 | 0.7171 | 0.000000 | YES | ACCURATE |
| 10 | FSP_R | (141.9,401.4) | (131.7,432.3) | 32.48 | 0.5678 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 11 | FSP_L | (485.1,400.0) | (518.4,438.5) | 51.00 | 0.5834 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 12 | FSD_R | (129.8,572.6) | (161.9,532.6) | 51.26 | 0.5366 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 13 | FSD_L | (493.0,579.1) | (501.7,535.1) | 44.90 | 0.5169 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 14 | IT_R | (173.1,518.5) | (148.6,518.0) | 24.55 | 0.713 | — | YES | ACCURATE |
| 15 | IT_L | (415.9,508.4) | (436.8,491.7) | 26.73 | 0.829 | — | YES | SYSTEMATIC_SHIFT |

### B26_13

| KP | Name | GT640 | V5 640 | Err | Conf | V2=V5 Δ | Plausible | Placement |
|---:|------|-------|--------|----:|-----:|--------:|-----------|-----------|
| 0 | TD_R | (263.1,386.2) | (255.5,392.6) | 9.95 | 0.8175 | 0.000000 | YES | ACCURATE |
| 1 | TD_L | (378.9,388.0) | (381.7,397.1) | 9.54 | 0.8582 | 0.000000 | YES | ACCURATE |
| 2 | FHC_R | (189.9,267.6) | (195.7,260.4) | 9.18 | 0.679 | 0.000000 | YES | ACCURATE |
| 3 | FHC_L | (435.4,261.1) | (439.0,278.5) | 17.75 | 0.753 | 0.000000 | YES | ACCURATE |
| 4 | ASL_R | (130.7,206.4) | (136.6,188.8) | 18.65 | 0.4935 | 0.000000 | YES | ACCURATE |
| 5 | ASL_L | (482.7,188.8) | (409.9,225.7) | 81.61 | 0.4982 | 0.000000 | YES | LARGE_SHIFT |
| 6 | ASM_R | (226.1,212.9) | (243.1,200.8) | 20.93 | 0.6951 | 0.000000 | YES | ACCURATE |
| 7 | ASM_L | (390.0,205.5) | (409.6,211.2) | 20.33 | 0.5624 | 0.000000 | YES | ACCURATE |
| 8 | FNM_R | (163.1,309.3) | (167.3,309.1) | 4.22 | 0.7063 | 0.000000 | YES | ACCURATE |
| 9 | FNM_L | (464.2,302.8) | (472.4,322.8) | 21.68 | 0.6891 | 0.000000 | YES | ACCURATE |
| 10 | FSP_R | (133.2,393.3) | (133.6,393.4) | 0.40 | 0.5745 | 0.000000 | YES | ACCURATE |
| 11 | FSP_L | (498.1,384.6) | (516.9,402.4) | 25.86 | 0.6147 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 12 | FSD_R | (139.9,555.7) | (154.9,502.8) | 54.97 | 0.5382 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 13 | FSD_L | (504.0,578.9) | (508.1,499.5) | 79.42 | 0.5145 | 0.000000 | YES | LARGE_SHIFT |
| 14 | IT_R | (176.5,490.5) | (151.5,472.9) | 30.57 | 0.748 | — | YES | SYSTEMATIC_SHIFT |
| 15 | IT_L | (429.1,480.6) | (430.2,451.2) | 29.41 | 0.771 | — | YES | SYSTEMATIC_SHIFT |

### B26_17

| KP | Name | GT640 | V5 640 | Err | Conf | V2=V5 Δ | Plausible | Placement |
|---:|------|-------|--------|----:|-----:|--------:|-----------|-----------|
| 0 | TD_R | (220.1,448.2) | (239.0,465.8) | 25.84 | 0.7669 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 1 | TD_L | (388.5,460.2) | (381.3,471.1) | 13.13 | 0.8619 | 0.000000 | YES | ACCURATE |
| 2 | FHC_R | (159.5,325.3) | (163.7,322.7) | 4.91 | 0.6321 | 0.000000 | YES | ACCURATE |
| 3 | FHC_L | (429.2,340.5) | (441.6,338.6) | 12.48 | 0.7957 | 0.000000 | YES | ACCURATE |
| 4 | ASL_R | (45.8,253.1) | (99.1,239.8) | 54.98 | 0.4624 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 5 | ASL_L | (532.8,266.7) | (454.2,283.5) | 80.29 | 0.6246 | 0.000000 | YES | LARGE_SHIFT |
| 6 | ASM_R | (196.8,253.1) | (213.5,254.4) | 16.76 | 0.6985 | 0.000000 | YES | ACCURATE |
| 7 | ASM_L | (405.5,244.7) | (408.7,271.2) | 26.76 | 0.6524 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 8 | FNM_R | (123.8,372.8) | (135.8,376.8) | 12.66 | 0.6925 | 0.000000 | YES | ACCURATE |
| 9 | FNM_L | (464.0,377.0) | (473.8,390.0) | 16.21 | 0.7477 | 0.000000 | YES | ACCURATE |
| 10 | FSP_R | (111.5,454.0) | (108.1,467.1) | 13.52 | 0.4842 | 0.000000 | YES | ACCURATE |
| 11 | FSP_L | (489.4,458.3) | (516.1,478.2) | 33.29 | 0.5934 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 12 | FSD_R | (93.3,590.8) | (140.1,578.4) | 48.45 | 0.5128 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 13 | FSD_L | (506.5,585.7) | (510.8,581.5) | 6.08 | 0.5091 | 0.000000 | YES | ACCURATE |
| 14 | IT_R | (120.0,544.3) | (129.4,557.8) | 16.44 | 0.709 | — | YES | ACCURATE |
| 15 | IT_L | (421.6,536.2) | (439.5,548.6) | 21.85 | 0.626 | — | YES | ACCURATE |

### B26_20

| KP | Name | GT640 | V5 640 | Err | Conf | V2=V5 Δ | Plausible | Placement |
|---:|------|-------|--------|----:|-----:|--------:|-----------|-----------|
| 0 | TD_R | (266.0,475.9) | (258.8,465.1) | 12.97 | 0.853 | 0.000000 | YES | ACCURATE |
| 1 | TD_L | (384.0,459.8) | (400.5,462.6) | 16.77 | 0.8119 | 0.000000 | YES | ACCURATE |
| 2 | FHC_R | (190.5,315.5) | (198.8,311.2) | 9.38 | 0.8068 | 0.000000 | YES | ACCURATE |
| 3 | FHC_L | (452.7,303.7) | (465.3,319.0) | 19.82 | 0.7142 | 0.000000 | YES | ACCURATE |
| 4 | ASL_R | (94.1,213.6) | (108.6,230.6) | 22.29 | 0.518 | 0.000000 | YES | ACCURATE |
| 5 | ASL_L | (541.8,205.8) | (384.7,261.9) | 166.82 | 0.3065 | 0.000000 | YES | MISPLACED |
| 6 | ASM_R | (213.1,259.6) | (223.4,245.8) | 17.30 | 0.7666 | 0.000000 | YES | ACCURATE |
| 7 | ASM_L | (434.1,247.3) | (423.5,242.8) | 11.52 | 0.5816 | 0.000000 | YES | ACCURATE |
| 8 | FNM_R | (152.5,364.0) | (135.2,370.4) | 18.42 | 0.7255 | 0.000000 | YES | ACCURATE |
| 9 | FNM_L | (505.9,359.5) | (512.3,372.9) | 14.84 | 0.6055 | 0.000000 | YES | ACCURATE |
| 10 | FSP_R | (123.1,436.6) | (104.6,461.0) | 30.64 | 0.7146 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 11 | FSP_L | (524.2,425.0) | (535.2,459.8) | 36.46 | 0.5938 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 12 | FSD_R | (104.2,606.3) | (109.6,588.1) | 18.98 | 0.6127 | 0.000000 | YES | ACCURATE |
| 13 | FSD_L | (546.3,603.0) | (537.0,581.8) | 23.13 | 0.5959 | 0.000000 | YES | ACCURATE |
| 14 | IT_R | (163.0,545.2) | (144.0,580.2) | 39.90 | 0.726 | — | YES | SYSTEMATIC_SHIFT |
| 15 | IT_L | (447.4,540.4) | (464.7,544.2) | 17.75 | 0.684 | — | YES | ACCURATE |

### B26_26

| KP | Name | GT640 | V5 640 | Err | Conf | V2=V5 Δ | Plausible | Placement |
|---:|------|-------|--------|----:|-----:|--------:|-----------|-----------|
| 0 | TD_R | (217.2,436.9) | (243.8,439.1) | 26.72 | 0.7973 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 1 | TD_L | (410.3,435.7) | (390.3,437.9) | 20.18 | 0.7905 | 0.000000 | YES | ACCURATE |
| 2 | FHC_R | (158.7,257.6) | (175.4,282.8) | 30.18 | 0.7849 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 3 | FHC_L | (452.9,271.8) | (462.7,291.9) | 22.39 | 0.7602 | 0.000000 | YES | ACCURATE |
| 4 | ASL_R | (114.4,222.8) | (88.3,202.3) | 33.16 | 0.5618 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 5 | ASL_L | (512.6,218.4) | (412.6,223.1) | 100.14 | 0.3948 | 0.000000 | YES | MISPLACED |
| 6 | ASM_R | (194.8,237.0) | (205.8,214.0) | 25.47 | 0.7805 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 7 | ASM_L | (438.7,233.1) | (420.0,213.3) | 27.26 | 0.6209 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 8 | FNM_R | (126.5,318.3) | (122.2,341.7) | 23.84 | 0.7118 | 0.000640 | YES | ACCURATE |
| 9 | FNM_L | (495.5,326.0) | (512.3,346.4) | 26.40 | 0.6512 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 10 | FSP_R | (114.4,373.2) | (84.1,432.6) | 66.72 | 0.6633 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 11 | FSP_L | (505.3,383.3) | (546.2,435.8) | 66.54 | 0.6096 | 0.000000 | YES | SYSTEMATIC_SHIFT |
| 12 | FSD_R | (78.7,549.2) | (99.9,552.2) | 21.42 | 0.5892 | 0.000000 | YES | ACCURATE |
| 13 | FSD_L | (526.5,537.6) | (521.4,560.4) | 23.28 | 0.5211 | 0.000000 | YES | ACCURATE |
| 14 | IT_R | (—,—) | (—,—) | — | 0.818 | — | N/A | EXCLUDED_GT_V0 |
| 15 | IT_L | (453.1,498.1) | (431.7,509.5) | 24.22 | 0.837 | — | YES | ACCURATE |

---

## Appendix B — Method notes

- Errors use GT v=2 only.
- KP0–13 confidence = YOLO keypoint confidence from prediction txt.
- IT confidence = API values from Phase 2A QC audit (`v5_phase2_landmark_qc_audit.md`).
- Anatomical plausibility is a **conservative heuristic** for triage, not a clinical gold standard.
- Placement thresholds (640): ACCURATE &lt;25; SYSTEMATIC_SHIFT &lt;75; LARGE_SHIFT &lt;100; else MISPLACED (or any failed plausibility with large error).
