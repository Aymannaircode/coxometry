# Phase 10D-0 — Small-Data Landmark Refinement Audit

**Date:** 2026-09-04  
**Mode:** READ-ONLY technical audit — no training, no production/code/label/checkpoint changes  
**Corpus:** 26 verified cases in `datasets/yolo_pose_new_26/` (21 train / 5 continuity val)  
**Predictions used for ROI inference-path tests:** `predictions_v2/labels/*.txt` (V2 ≡ V5 Phase 2 for KP0–13 per Phase 9B)  
**Companion CSV:** `datasets/yolo_pose_new_26/phase10d_roi_feasibility.csv`  
**Isolated analysis script (non-production):** `_phase10d0_audit_temp/run_roi_audit.py`

**Context:** Phase 10C Step D is **BLOCKED** (insufficient unused real AP pelvis DICOMs for 40–80 case expansion). This audit does **not** wait for new clinical data. It asks whether a *technically safe* small-data refinement path exists on the existing 26 cases **without** replacing V5/V5-IT.

---

## 1. Executive verdict

| Field | Value |
|-------|-------|
| **FINAL VERDICT** | **REFINEMENT_NOT_SAFE_WITH_CURRENT_DATA** |
| Primary blocker | Learned specialists on **n_source=21** train patients are not safe: V2 already failed ASL_L on the same train set; ROI built from V5/V2 **ASL init systematically excludes true ASL_L**; safe fallback ROIs must be ~29% of the image (weak “zoom”); project docs already require ≥100–200 images for heatmap-class models and ≥60–100 for legacy remediation claims |
| What *is* technically feasible | Offline **evaluation harness** vs frozen V2/V5; **adapter-layer fusion design** (replace only ASL/FSP/FSD); **fallback acetabular ROI** from TD+FHC+ASM + lateral sourcil expansion (containment 52/52 at margin 300 px); shaft ROI mostly feasible with large margins |
| What is *not* safe now | Training any ROI YOLO / heatmap / full fine-tune / axis-only FSP–FSD solver as a remediation claiming improvement on 26 cases alone |
| SAFE_TO_PROCEED_TO_10D1 | **NO** (no training / no specialist checkpoint / no production adapter change) |

**Counting rule (mandatory):** ROI crops are **derived samples from the same source case**. They are **not** independent patients. Effective diversity remains **21 train + 5 val source images**, not 42/52/104 “new” samples.

---

## 2. Current landmark error problem

### 2.1 Phase 9B (letterbox 640, continuity val n=5)

| Landmark | Mean err | Median | Max | Pattern |
|----------|---------:|-------:|----:|---------|
| **ASL_L** | **104.9** | 95.6 | 166.8 | Medial collapse toward ASM (anatomical misplacement) |
| FSP_L | 42.6 | 36.5 | 66.5 | Lateral + caudal systematic |
| FSD_R | 39.0 | 48.5 | 55.0 | Lateral + cranial |
| FSD_L | 35.4 | 23.3 | 79.4 | Often cranial; B26_13 outlier |
| ASL_R | 32.8 | 33.2 | 55.0 | Systematic translation |
| FSP_R | 28.8 | 30.6 | 66.7 | Caudal (+ medial) |
| FHC / FNM / TD / ASM | ~13.5–17.9 | — | — | Comparatively good |
| IT_R/L | ~24–28 | — | — | Separate head; not the legacy failure |

V5 Phase 2 **did not regress KP0–13** vs V2 (69/70 pairs Δ&lt;1e-5). Problem is inherited V2 underlearning, not IT training.

### 2.2 All 26 cases, V2 preds, original pixels (this audit)

| Landmark | Mean err (orig px) | Mean Δx | Mean Δy | Pred closer to ASM than ASL |
|----------|-------------------:|--------:|--------:|----------------------------:|
| ASL_L | **525.4** | −482.7 | +173.2 | **25/26** (train 20/21, val 5/5) |
| FSP_L | 170.0 | +103.6 | +128.5 | — |
| FSD_R | 159.4 | +112.8 | −36.7 | — |
| FSP_R | 150.9 | −67.3 | +123.5 | — |
| ASL_R | 143.8 | +75.6 | +6.3 | **0/26** |
| FSD_L | 108.0 | +2.7 | −28.3 | — |
| Protected (TD/FHC/ASM/FNM) | ~58–94 | smaller | smaller | — |

**ASL_L failure mode for ROI design:** on 25/26 images the V2/V5 ASL_L prediction is **closer to GT ASM_L than to GT ASL_L**. Any ROI that tightly wraps TD+FHC+ASM+**ASL_pred** is anchored near the **medial** sourcil and **misses** the true lateral endpoint.

### 2.3 Existing non-learned adapter (context only — not modified)

`mvp_geometry.refinement` already implements **C_asm_offset** ASL_L post-process (TRAIN-calibrated ASM→ASL offset, adapter between YOLO and geometry). Phase 10B does **not** endorse formula offsets as primary remediation; it remains evidence that **selective KP replacement without touching V5 weights** is already an established pattern in this repo.

---

## 3. ROI feasibility

### 3.1 Image dimensions

| Metric | Value |
|--------|------:|
| n images | 26 (26 unique WxH) |
| Mean W×H | **2894 × 2513** |
| Range W | 2548–3234 |
| Range H | 1975–3008 |
| Inference letterbox | 640×640 (Ultralytics) |

Native resolution is high enough that a **local crop resized to 320–640** can preserve acetabular / shaft detail **if** the crop actually contains the target.

### 3.2 Anatomical segment lengths (GT, original px, 52 hips)

| Segment | Mean | Std | Min | Max |
|---------|-----:|----:|----:|----:|
| Sourcil ASM→ASL | **530.3** | 71.9 | 332 | 673 |
| Shaft FSP→FSD | **637.1** | 112.9 | 453 | 982 |

### 3.3 Derived vs independent samples

| Concept | Count | May train as independent? |
|---------|------:|---------------------------|
| Source cases (patients/images) | **26** | Split unit of account |
| Train source cases | **21** | Yes (with patient leak rules) |
| Val continuity cases | **5** | Eval only |
| Acetabular ROI crops (R+L) | ≤52 | **No** — derived from source case |
| Shaft ROI crops (R+L) | ≤52 | **No** — derived from source case |
| Independent new patients | **0** (Phase 10C Step D blocked) | — |

---

## 4. ASL ROI analysis

### 4.1 Candidate constructions tested

| ID | Construction (inference path uses V2 preds) | Target |
|----|-----------------------------------------------|--------|
| A_pred | bbox(TD, FHC, ASM, **ASL_pred**) | GT ASL |
| A_gt | bbox(TD, FHC, ASM, ASL_GT) oracle | GT ASL |
| A_rel | bbox(TD, FHC, ASM) only | GT ASL |
| A_lat | bbox(TD, FHC, ASM, **lateral proxy** = ASM ± 1.25×mean sourcil) | GT ASL |
| A_exp | A_rel expanded laterally by 1.0×mean sourcil | GT ASL |

### 4.2 Containment of GT ASL (52 hips)

| Construction | m=0 | m=100 | m=150 | m=200 | m=300 | Mean crop @ success margin |
|--------------|----:|------:|------:|------:|------:|----------------------------|
| A_pred | 1/52 | 11/52 | 18/52 | 25/52 | 34/52 | **Never 100%** even at m=400 (45/52) |
| A_rel | 0/52 | 0/52 | 0/52 | 0/52 | 12/52 | Fails without lateral expand |
| A_lat | 8/52 | 27/52 | 38/52 | 44/52 | **52/52** | ~1357×1522 (~**28.7%** image area) |
| A_exp | 10/52 | 27/52 | 38/52 | 44/52 | **52/52** | ~1382×1522 (~**29.2%**) |
| A_gt oracle | **52/52** | — | — | — | — | ~649×1011 (~9%) |

**Critical ASL_L result:** with A_pred and **m=200, GT ASL_L is inside ROI on 0/26 left hips**. Mean lateral shortfall outside zero-margin A_pred for ASL_L ≈ **335 px** (max ≈ 461 px).

### 4.3 Can an ROI derived from V2/V5 still contain true ASL_L?

| Method | Contains true ASL_L safely? |
|--------|-----------------------------|
| Tight ROI around V5 ASL_L (+ TD/FHC/ASM) | **NO** — ASL_pred ≈ ASM; true ASL is far lateral |
| Reliable TD+FHC+ASM without lateral expand | **NO** at practical margins |
| **Fallback:** TD+FHC+ASM + lateral expansion ≥ mean sourcil + **~300 px** pad | **YES** (52/52) |
| Bilateral TD + FHC + ASM + fixed lateral band from laterality rules | Same family as fallback — recommended if any future experiment proceeds |

**Fallback ROI construction (design only — not implemented):**

```
anchors = {TD_side_pred, FHC_side_pred, ASM_side_pred}   # do NOT require ASL_pred
lateral = mean_train_sourcil_length × k   # k≈1.0–1.25; calibrated on TRAIN only
if side == R: expand bbox leftward by lateral
if side == L: expand bbox rightward by lateral
pad ≈ 250–300 px (original) until TRAIN containment ≥ target; freeze pad before VAL look
```

QC gate: if expanded ROI would exceed image bounds or area fraction &gt; threshold, **skip specialist** and keep V5 ASL (fail-open).

### 4.4 Left/right symmetry

Acetabular A_lat crops at m=100: R mean ≈ 972×1140, L mean ≈ 984×1105 — **symmetric enough** for shared architecture with flip / side channel. Error severity is **not** symmetric (ASL_L ≫ ASL_R).

### 4.5 Anatomical context

At A_lat m=100, GT anchors remain inside crop for FHC 52/52, TD 49/52, ASM 49/52. After m=300 expansion needed for full ASL coverage, context is preserved but **zoom factor vs full pelvis drops to ~2×**, limiting specialist benefit.

### 4.6 ASL ROI feasibility verdict

**ASL_ROI_FEASIBLE: YES** — but **only** with **fallback lateral expansion from reliable landmarks**, not with ASL_pred-init ROIs. Feasibility ≠ training safety.

---

## 5. Shaft ROI analysis

### 5.1 Constructions

| ID | Construction | Target |
|----|--------------|--------|
| S_pred | bbox(FHC, FNM, FSP_pred, FSD_pred) | both GT FSP & FSD |
| S_gt | oracle GT anchors | both |
| S_ext | FHC+FNM extended distally by 1.1×mean shaft (vertical) | both |

### 5.2 Containment (both FSP and FSD inside)

| Construction | m=0 | m=100 | m=150 | m=200 | m=300 | 100%? |
|--------------|----:|------:|------:|------:|------:|------:|
| S_pred | 11/52 | 40/52 | 46/52 | 49/52 | 51/52 | **NO** (51/52 best) |
| S_ext | 0/52 | 1/52 | 9/52 | 22/52 | 41/52 | NO |
| S_gt | **52/52** | — | — | — | — | YES at m=0 |

Misses at m=150 include val cases **B26_10 R/L**, **B26_13 R/L**, plus train B26_09/14 R — often large FSD cranial/lateral errors so GT FSD sits outside the pred-anchored box.

### 5.3 Crop shape / context

S_pred at m=100: mean ~533×1266, aspect ~0.42 (**tall**). Enough shaft context if containment holds; failures when FSD_pred is far cranial of GT.

### 5.4 Shaft ROI feasibility verdict

**SHAFT_ROI_FEASIBLE: YES** for a *majority* of hips with S_pred + ≥150–200 px margin, with **fail-open** when GT would be out (or when pred FSP–FSD length/angle fails QC). Not universally safe without large pads or axis-aware boxes.

---

## 6. Heatmap feasibility

| Question | Finding |
|----------|---------|
| Compatible framework already in project deps? | **No.** `backend/requirements.txt` = FastAPI + **ultralytics** + Pillow/numpy. No MMPose / HRNet / soft-argmax training stack |
| Ultralytics “heatmap” module? | Tracking visualization only — **not** keypoint heatmap regression |
| Prior design docs? | `docs/model_architecture_comparison.md` discusses heatmaps as Phase-2 alternative; states **~100–200** images minimum with pretrain for usable medical KP models |
| Integration path | Would need new `LandmarkDetector` subclass + train pipeline + deps — **major architecture addition**, not a small adapter |
| Data vs doc floor | **26 ≪ 100–200** |

**HEATMAP_FEASIBLE: NO** under current dependencies and data volume (without installing new stacks / claiming readiness). Introducing heatmaps later remains conceptually compatible with `LandmarkDetector`, but is **out of scope** for safe 26-case remediation.

---

## 7. Axis-based feasibility

### 7.1 What annotations support

| Property (GT, 52 hips) | Result |
|------------------------|--------|
| Shaft angle atan2(FSD−FSP) from +x | mean **90.5°**, std **8.6°** (near vertical) |
| \|Δx\| FSP−FSD | mean **77 px**, std **45** (mild bow / obliquity) |
| FSP y-fraction below FHC → image bottom | mean **0.41**, std **0.06** |
| FSD y-fraction | mean **0.92**, std **0.07** (FOV-sensitive) |

Axis **direction** is consistent enough to define a diaphyseal line once two reliable shaft points exist.

### 7.2 Can FSP/FSD be derived geometrically without learning levels?

**No.** CCD needs the shaft **axis** (FSP→FSD) and neck (FNM→FHC). Annotations do **not** encode a unique geometric rule that places FSP height (A7: “just below lesser trochanter”) or FSD (FOV edge policy) from FHC+FNM alone. S_ext containment fails badly. Pure axis geometry is **underdetermined** for the two endpoints.

A hybrid “detect axis + project levels” still needs a learned or heuristic level model → collapses to small-data learning risk.

**Do not modify `mvp_geometry/`.** Geometry already consumes FSP/FSD as points; refinement would supply better points, not change formulas.

**AXIS_REFINEMENT_FEASIBLE: NO** as a standalone replacement for FSP/FSD.

---

## 8. Leakage / split analysis

### 8.1 Official split (`meta/split.json`, seed=42)

| Split | Cases | Role |
|-------|------:|------|
| train | 21 | B26_01–09,11,12,14–16,18,19,21–25 |
| val (continuity) | 5 | **B26_10, B26_13, B26_17, B26_20, B26_26** |
| test | 0 | None (Phase 10C: `final_evaluation_ready=false`) |

### 8.2 Specialist train on 21 / eval on 5 — possible?

**Operationally yes, scientifically weak:**

- Same continuity probe as V2/V5 — enables **like-for-like** comparison tables.
- **n_val=5** cannot support promotion thresholds; only smoke / continuity.
- **No held-out test** → cannot claim remediation (Phase 10B: need test ≥15).
- ROI crops from a train image must stay in **train**; crops from a val image must stay in **val**. Treating L/R crops or multi-ROI as independent patients = **leakage / N inflation**.

### 8.3 Correct future split strategy

1. **Unit of split = source image / PatientID**, never ROI crop.  
2. Keep continuity five **frozen** for trend vs V2/V5 until a true test set exists.  
3. Do not reshuffle val into train to “gain” data for a specialist.  
4. When expansion unblocks: patient-safe train / val / **test≥15**; calibrate ROI margins and any offsets on **train only**.  
5. Report metrics with explicit denominator: `n_source_cases`, not `n_crops`.

---

## 9. Small-data risk analysis

| Risk | Assessment |
|------|------------|
| Overfitting | **Very high** — V2 nano already saw these 21 labels and still collapses ASL_L (25/26 pred≈ASM). Specialist capacity on 21 sources can memorize crop textures |
| Train/val leakage | Controlled **if** split by source ID; broken if crops counted as new cases or if VAL used to pick margins/architecture |
| ROI bias | A_pred ROIs **systematically exclude** hard ASL_L → training would never see true lateral sourcil if crops built that way |
| L/R imbalance | ASL_L catastrophic, ASL_R moderate; shared weights + flip may help but can also wash side-specific failure |
| Hard-example concentration | Failures concentrated on thin sourcil edge + short-FOV shafts — few diverse hard patterns in 21 |
| Insufficient diversity | 26 unique sizes but one acquisition domain; Phase 10C found only 6 unused candidates, not promoted |
| Dependence on V5 init | Pred-init ROI **fails** for ASL_L; specialist that assumes “target near init” is invalid |
| Failure when V5 very wrong | Documented; requires fallback ROI + fail-open to V5 |
| Domain shift | Any new site/FOV without expansion will shift shaft levels and sourcil appearance |
| False N | **More crops ≠ more data** |

**Conclusion:** small-data *learned* refinement is **not** a safe substitute for the blocked expansion program.

---

## 10. V2 / V5 preservation strategy

### 10.1 Frozen baselines (do not modify)

| Artifact | Use |
|----------|-----|
| V2 `best.pt` + `predictions_v2/` | Legacy KP0–13 baseline |
| V5 Phase 2 checkpoint | Production IT + frozen cv4 KP0–13 |
| Continuity labels `labels/val` | GT for five cases |
| Phase 9B CSV / audit temps | Reproducible 640-space scores |

### 10.2 Preferred offline comparison (future experiment)

For each continuity case, compare in **letterbox 640** and **original** px:

`GT | V2 | V5 | candidate_refined`

**Metrics** (per KP and pooled): mean, median, p90, max, mean Δx, mean Δy, %&lt;25, %&lt;50, %&lt;75.

**Target KPs:** ASL_R, ASL_L, FSP_R, FSP_L, FSD_R, FSD_L  

**Protected KPs (must not worsen beyond agreed Δ, e.g. +5 px @640 mean):** TD, FHC, ASM, FNM, IT_R, IT_L  

**Confusion metric:** fraction of ASL_L preds closer to ASM_L than ASL_L → must move toward 0.

Run candidate inference in an **isolated eval script**; never overwrite production checkpoints or `MODEL_VERSION`.

### 10.3 Adapter fusion (design — not implemented)

```
V5 Phase 2 detect (unchanged weights)
    → QC / confidence / ROI-containment checks
    → optional specialist(s) on acetabular / shaft ROIs
    → replace ONLY {ASL_R, ASL_L, FSP_R, FSP_L, FSD_R, FSD_L} when gates pass
    → keep all other V5 landmarks (incl. IT)
    → existing mvp_geometry measures
```

This matches the existing `_apply_adapter_and_refinement` seam in `backend/app/services/detection/yolo_pose.py` / V5 detector: **adapter layer, checkpoint untouched**.

---

## 11. Geometry dependency analysis

**Do not modify `mvp_geometry/`.** Dependencies from `hip_measures._REQUIRED` / `measurements.py`:

| Measure | Required landmarks | Effect of target errors |
|---------|-------------------|-------------------------|
| **VCE** | TD_R, TD_L, FHC, **ASL** | ASL medial (ASL_L) → coverage vector FHC→ASL swings medial → **VCE bias** (under-coverage direction per signed construction) |
| **Tönnis** | TD_R, TD_L, ASM, **ASL** | ASL medial shortens/rotates sourcil ASM→ASL → **Tönnis bias**; if ASL≈ASM, measure becomes unstable / undefined |
| **CCD** | FHC, FNM, **FSP**, **FSD** | FSP/FSD errors tilt or shorten diaphyseal axis → **CCD bias**; coincident FSP/FSD → GeometryError |

Protected landmarks:

- Improving ASL without touching FHC/TD/ASM preserves VCE/Tönnis inputs except ASL.  
- Improving FSP/FSD without touching FHC/FNM preserves neck axis; CCD changes only via shaft axis.  
- IT unused by VCE/Tönnis/CCD in current engine.

**No clinical angle thresholds invented here** — only dependency direction from code.

---

## 12. Architecture comparison

| Option | Expected benefit | Impl. complexity | Data need | Overfit risk | Compat. w/ V5/IT | Isolate ASL/FSP/FSD | Recommendation |
|--------|------------------|------------------|-----------|--------------|------------------|---------------------|----------------|
| **A. ROI YOLO Pose specialist** | Moderate *if* fallback ROI + zoom; low if A_pred | Medium (Ultralytics already present) | ≫21 sources ideally | **High** @26 | Good as adapter | Yes | **Not now** |
| **B. ROI heatmap specialist** | Highest localization *in theory* | **High** (new stack) | Docs: **100–200+** | Extreme @26 | Needs new detector class | Yes | **Not recommended** |
| **C. Axis/geometry shaft refine** | Direction OK; levels unresolved | Low–med | N/A for pure geo | Heuristic bias | Good | FSP/FSD only | **Not recommended** standalone |
| **D. Full soft fine-tune from V2** | Could help problem KPs | Medium | ≥60–100 to claim; smoke on 26 | High; **risk to good KP + IT path if misconfigured** | Conflicts with freeze/IT story | Weak isolation | **Not recommended** now |
| **E. Hybrid V5 + specialized refine** | Best *architecture* for preservation | Medium (adapter exists) | Same as A/B for learned head | High if learned on 26 | **Best** — V5 frozen | Yes | **Architecture preferred later**; **not safe to train now** |

---

## 13. Recommended architecture (when data exists)

**Future (post-expansion):** **E — Hybrid V5 + ROI specialists**, with:

1. V5/IT checkpoint **frozen**.  
2. Acetabular specialist ROI = **fallback lateral expand** (never ASL_pred-tight).  
3. Shaft specialist ROI = FHC+FNM+FSP+FSD pred box + margin + fail-open.  
4. Replace only targeted KPs after QC.  
5. Optional tiny YOLO-pose or heatmap **only after** n_source meets Phase 10B floors.

**Now:** do **not** train A–D. Keep expansion / QA / manual-correction bridge (Phase 10B Option F) as the primary remediation path. Existing offset ASL_L adapter is out of scope for change in this audit.

---

## 14. Recommended experiment sequence (gated; no execution in 10D-0)

| Step | Action | Exit |
|-----:|--------|------|
| 0 | This audit | Done |
| 1 | **STOP training** until more real cases **or** explicit research-only waiver | — |
| 2 | Unblock Phase 10C data (≥40–80, test≥15) + QA | Expansion ready |
| 3 | Offline eval harness: GT/V2/V5 tables for target+protected KPs | Script in isolated temp only |
| 4 | Freeze ROI recipes on **train** containment study (no val tuning loop) | Written ROI spec |
| 5 | Prototype adapter in **non-production** branch replacing KP dict only | Parity: protected KP identical to V5 |
| 6 | Train specialist **only** on expanded set | Meet Phase 10B gates on **test** |
| 7 | Compare candidate vs V2/V5; promote only if gates pass | Checkpoint outside production until signed |

**Phase 10D-1 should not start training under current N.**

---

## 15. What must NOT be changed

- Production source / Flutter / PDF  
- `mvp_geometry/` formulas and (in this phase) refinement calibration  
- V2 checkpoint / V5 Phase 2 checkpoint / IT architecture / IT training  
- Existing labels / `yolo_pose_new_26` images / `yolo_pose_remediation_v1` seed labels  
- `MODEL_VERSION` / backend inference wiring for production  
- No `--train`, no new production checkpoint, no composed production model  

Allowed in this phase: **audit docs + isolated temp analysis** (done).

---

## 16. Exact prerequisites before any training

1. **Source-case count** meeting Phase 10B remediation floor (**≥60–100** preferred; absolute minimum policy to be signed — **26 alone is insufficient** for a learned specialist claim).  
2. True **held-out test ≥15** patient-safe; continuity 5 retained as trend probe.  
3. ROI construction locked: **fallback acetabular** (no ASL_pred-tight); shaft margins + fail-open.  
4. Explicit statement in experiment card: **crops ≠ patients**.  
5. Eval harness ready: GT/V2/V5/candidate metrics for target + protected KPs + ASL↔ASM confusion rate.  
6. Adapter design reviewed: replace only targeted KPs; IT and good KP bit-identical when specialist skipped.  
7. No dependency install for heatmap stacks unless separately approved.  
8. Physician A1/A7 exemplars still recommended before label edits (Phase 10B).  
9. Written go/no-go from this audit: **NO-GO for training on 26 alone**.

---

## FINAL STATUS BLOCK

```
PHASE_10D0_STATUS: COMPLETE_AUDIT_ONLY
RECOMMENDED_APPROACH: REFINEMENT_NOT_SAFE_WITH_CURRENT_DATA
ASL_ROI_FEASIBLE: YES
SHAFT_ROI_FEASIBLE: YES
HEATMAP_FEASIBLE: NO
AXIS_REFINEMENT_FEASIBLE: NO
TRAINING_STARTED: NO
PRODUCTION_MODIFIED: NO
SAFE_TO_PROCEED_TO_10D1: NO
```

**Notes on YES/NO flags:**  
- ASL/SHAFT ROI **YES** = geometrically constructible with annotations/dimensions under **fallback / padded** recipes.  
- Heatmap **NO** = no in-repo framework + data below documented floor.  
- Axis **NO** = cannot uniquely derive FSP/FSD from current geometry without learning levels.  
- Overall approach **REFINEMENT_NOT_SAFE_WITH_CURRENT_DATA** overrides “ROI feasible” for go/no-go.

---

*End of Phase 10D-0. STOP — do not implement, train, or modify production.*
