# Phase 10B — Legacy Landmark Root-Cause & Remediation Audit

**Date:** 2026-09-04  
**Mode:** READ-ONLY — no code / dataset / labels / checkpoints / Flutter / PDF / `mvp_geometry` / offsets / training changes  
**Scope:** Root cause of legacy problem group (ASL_R/L, FSP_R/L, FSD_R/L) and safest remediation strategy **before** any code or training changes  
**Primary evidence:** Phase 9B (`phase9b_landmark_errors.csv`, `phase9b_full_landmark_accuracy_audit.md`), Phase 10 gap analysis, live `labels/{train,val}`, `docs/landmark_specification.md`, `docs/annotation_guidelines.md`, V2 `args.yaml`, V5 freeze audits, prior annotation/flip/training audits  
**Companion CSV:** `datasets/yolo_pose_new_26/phase10b_remediation_options.csv`

---

## 0. Executive verdict

| Question | Answer |
|----------|--------|
| Are GT labels the primary cause? | **No** — geometric QA on all 26 images: 0 R/L inversions; 52/52 ASL lateral to ASM; 52/52 FSD distal to FSP; YOLO↔JSON historically 0 px |
| Is ASL definition ambiguous enough to call DEFINITION_PROBLEM? | **No as primary** — MVP locks ASL = **lateral end of acetabular sourcil**; A1 (sourcil vs bony rim) is documented residual risk, not the observed medial failure mode |
| Why is ASL_L catastrophic? | Model systematically places ASL_L **too medial**, closer to **ASM_L GT than ASL_L GT on all 5 val cases** (anatomical confusion lateral↔medial sourcil on left) |
| Flip / side / label order? | **Ruled out** — `flip_idx` correct; prior horizontal-flip audit verdict D |
| Did V5 create this? | **No** — V2≈V5 KP0–13; V5 froze cv4; IT-only training |
| Primary drivers | **DATA_VOLUME** (21 train) + **MODEL_CAPACITY / underlearning** (nano + equal pose loss) + **structure difficulty** (sourcil edge / short-FOV shaft) + **TRAINING_CONFIGURATION** (aggressive mosaic/erasing) |
| Preferred remediation | **OPTION F (combination)** — QA confirm → expand data → limited pose-head fine-tune with regression gates → manual correction bridge; **no** formula hacks / Flutter offsets / IT retrain |

**Problem is structure-specific:** FHC / FNM / TD / ASM remain comparatively good (~14–18 px @640). Failures concentrate on **lateral sourcil (esp. left)** and **femoral shaft axis points**.

---

## 1. Dataset / label audit

### 1.1 Corpus

| Item | Value |
|------|------:|
| Images | 26 (B26_01…B26_26) |
| Train / val / test | 21 / 5 / **0** |
| Val cases | B26_10, B26_13, B26_17, B26_20, B26_26 |
| Label schema on disk | 16 KP × 3 (`kpt_shape: [16,3]`) |
| Legacy KP visibility (0–13) | **v=2 on 26/26** for all ASL/FSP/FSD and better landmarks |
| Annotator | Single primary annotator historically (`annotator_A`); B6 IT work separate |

### 1.2 Geometric consistency (live labels, this audit)

Automated checks on all 26 images (original-pixel geometry from normalized YOLO labels):

| Check | Pass |
|-------|-----:|
| ASL_R lateral to ASM_R (x_ASL &lt; x_ASM) | **26/26** |
| ASL_L lateral to ASM_L (x_ASL &gt; x_ASM) | **26/26** |
| ASL above FHC (y) both sides | **26/26** |
| ASL_R left of ASL_L | **26/26** |
| FSD distal to FSP both sides | **26/26** |
| Blocking fails | **0** |

Sourcil / shaft length stability (original px):

| Segment | Mean | Std | Min | Max |
|---------|-----:|----:|----:|----:|
| Sourcil_R (ASM→ASL) | 535.7 | 77.6 | 360 | 673 |
| Sourcil_L | 524.9 | 65.4 | 332 | 629 |
| Shaft_R (FSP→FSD) | 640.8 | 101.6 | 482 | 846 |
| Shaft_L | 633.5 | 123.2 | 453 | 982 |
| ASL–ASM lateral margin R | 515.8 | 82.1 | 323 | 652 |
| ASL–ASM lateral margin L | 503.5 | 71.1 | 326 | 603 |

Normalized coordinate clouds are tight and anatomically ordered (ASL_R ~x=0.16, ASL_L ~x=0.83; FSD near bottom y≈0.96). **No evidence of systematic left/right label swap or medial-ASL mislabeling.**

### 1.3 Per problematic landmark — annotation read

| Landmark | Consistency | L/R | Anatomical definition adherence | Placement variability | Visibility / occlusion | Difficult cases | Ambiguous target? | Systematic GT bias? | Suspicious outliers? |
|----------|-------------|-----|----------------------------------|----------------------|------------------------|-----------------|-------------------|---------------------|----------------------|
| **ASL_R** | High | OK | Lateral sourcil end | Moderate (margin std ~82 px) | All v=2 | A1 rim vs sourcil on some hips | Mild (A1) | No | None geometric |
| **ASL_L** | High | OK | Same as R; margins mirror R | Similar to R | All v=2 | Same A1 | Mild (A1) | No — GT stays lateral | None; model fails, not GT |
| **FSP_R** | High | OK | Proximal shaft under lesser trochanter | Moderate | All v=2 | A7 height; rotation | Moderate (A7) | No | None |
| **FSP_L** | High | OK | Same | Moderate | All v=2 | Same | Moderate (A7) | No | None |
| **FSD_R** | High | OK | Distalmost reliable shaft in FOV | Higher (FOV edge) | All v=2 | Short FOV ~70% corpus | Moderate–high (FOV) | Policy: keep v=2 at FOV edge | Prior QA: REVIEW_FOV not INVALID |
| **FSD_L** | High | OK | Same | Higher | All v=2 | Same | Moderate–high | Same | Same |

Prior `landmark_annotation_quality_audit.md` (2026-08-28): **0 CRITICAL** GT errors on priority landmarks; ASL 52/52 VALID; FSP 52/52 VALID; FSD mostly VALID with FOV review flags. Visual B26_01 confirmed GT on sourcil/shaft.

### 1.4 Comparison with better landmarks

| Group | Landmarks | Phase 9B mean err @640 | GT geometry | Model behavior |
|-------|-----------|------------------------|-------------|----------------|
| Better | FHC_R/L, FNM_R/L, TD_R/L, ASM_R/L | ~13.5–17.9 px | Equally consistent | Learned adequately |
| Problem | ASL_R, FSP_*, FSD_* | ~28.8–42.6 | Equally consistent | Systematic bias |
| Catastrophic | ASL_L | **104.9** | Equally consistent | Anatomical misplacement toward ASM |

**Conclusion:** Failure is **not** “whole pelvis labeling broken.” It is **specific to:**

1. **Lateral acetabular sourcil endpoint**, especially **left** (model collapses toward medial sourcil / joint).  
2. **Femoral diaphyseal axis endpoints** (level ambiguity + short FOV + lower visual contrast than head/neck centers).

Structures with strong circular/contrast cues (head center, neck midline, teardrop, medial sourcil) generalize; thin-edge / axis-level points do not.

---

## 2. Anatomical definition audit

Sources: `docs/landmark_specification.md` §4; `docs/annotation_guidelines.md` §2.3–2.7. **No new definitions invented.**

### 2.1 ASL — what ASL means in this project

| Field | Project definition (locked) |
|-------|-----------------------------|
| Full name | Acetabular **sourcil lateral** (extrémité latérale du sourcil) |
| Exact location | Most **lateral** point of the **sclerotic weight-bearing acetabular roof (sourcil)** |
| Explicit exclusion | Osteophyte / rim spur **outside** the dense sourcil → that would be optional **ALB**, not ASL |
| Annotator instruction | Follow roof medial→lateral; place where sourcil densification **ends laterally**; if sourcil≠rim inseparable → `v=0` |
| Measures | VCE (FHC→ASL) and Tönnis (ASM→ASL) |
| Literature ambiguity A1 | Sourcil lateral vs most-lateral bony acetabulum — **MVP chooses sourcil for ASL** |

**Unambiguous enough for MVP?** **Yes for operational annotation** (guide is explicit).  
**Visually reproducible?** **Moderately** — requires recognizing sclerotic band end; hard when osteophyte/arthritis/underexposure.  
**Is observed ASL_L failure a DEFINITION_PROBLEM?** **No.** Predictions are **too medial** (toward ASM / joint), not “ALB vs ASL” (which would bias **more lateral**). Primary class = **MODEL_PROBLEM** (with data/training contributors), not DEFINITION_PROBLEM.

### 2.2 Problematic landmarks — definition cards

| Landmark | Intended location | Annotator instruction summary | Unambiguous? | Visually reproducible point? |
|----------|-------------------|-------------------------------|--------------|------------------------------|
| ASL_R | Lateral sourcil end, right | Same as ASL_L | Sufficient (A1 residual) | Moderate |
| ASL_L | Lateral sourcil end, left | Same | Sufficient (A1 residual) | Moderate |
| FSP_R | Mid-shaft proximal, just below lesser trochanter (or first clear parallel cortices) | Place on median diaphyseal axis under lesser trochanter | **Partial** — A7 height not universal | Moderate |
| FSP_L | Same, left | Same | Partial (A7) | Moderate |
| FSD_R | Mid-shaft, most distal still visible with identifiable cortices | Follow shaft down; stop at last reliable level in FOV | **Partial** — FOV-dependent | Moderate–low when FOV short |
| FSD_L | Same, left | Same | Partial | Moderate–low |

FSP/FSD: definition is **internally consistent** and labels follow it; residual **A7** means exact pixel height can vary between conscientious annotators even when “correct.” That raises noise floors for shaft KP but does **not** explain ASL_L’s ~100 px medial collapse.

---

## 3. Left/right / flip audit

### 3.1 Configuration (read-only)

| Item | Value | Status |
|------|-------|--------|
| `data.yaml` `kpt_shape` | `[16, 3]` | OK |
| `flip_idx` | `[1,0, 3,2, 5,4, 7,6, 9,8, 11,10, 13,12, 15,14]` | Correct R↔L pairs |
| ASL pair | 4↔5 | Not crossed with ASM 6↔7 |
| V2 train-time shape | `[14,3]` + 14-length `flip_idx` | Consistent for V2 era |
| `fliplr` V2 | 0.5 | Enabled with matching `flip_idx` |
| Patient-side convention | Image left = patient right (standard AP); KP `*_R` = anatomical right | Consistent in labels |
| Label generation | `prepare_yolo_pose_new_26.py` | Order matches `meta/keypoint_order.md` |

Prior `horizontal_flip_audit.md` **verdict D**: flip configured correctly; **not** primary ASL_L cause. Train-label flip simulation: 0 error on all 7 pairs.

### 3.2 Could flip explain ASL_L medial bias?

| Hypothesis | Evidence | Verdict |
|------------|----------|---------|
| flip_idx swaps ASL↔ASM | flip_idx[4]=5, [5]=4; ASM is 6/7 | **Rejected** |
| Left/right label confusion in GT | 26/26 geometric laterality | **Rejected** |
| Asymmetric anatomy only on left | GT margins R≈L; model error highly asymmetric | Anatomy not the GT asymmetry source |
| Coordinate convention (norm vs px) | Phase 9B errors already in letterbox 640 | **Rejected as primary** |
| Augmentation amplifies hard left sourcil | Possible **contributor** (fliplr mixes sides) but cannot be root alone — **train set ASL_L also catastrophic** (~538 px original in prior V2 analysis) | Secondary at most |

**ASL_L medial pattern is side-specific model failure, not a flip bug.**

---

## 4. Error pattern analysis (Phase 9B CSV)

Coordinate space: letterbox **640×640**. Pred = V5 Phase2 = V2 for KP0–13.

### 4.1 Summary bias (pred − GT)

| Landmark | Mean err | Mean Δx | Mean Δy | Std Δx | Std Δy | Mean conf | Pattern class |
|----------|---------:|--------:|--------:|-------:|-------:|----------:|---------------|
| **ASL_L** | **104.9** | **−100.5** | +26.6 | 30.0 | 18.0 | 0.47 | **C + D** systematic anatomical misplacement, left-specific |
| ASL_R | 32.8 | +16.5 | −7.7 | 26.9 | 13.5 | 0.51 | **B** systematic translation (often lateral) |
| FSP_R | 28.8 | −12.4 | +25.6 | 11.0 | 19.9 | 0.60 | **B** caudal (+ medial) |
| FSP_L | 42.6 | +26.1 | +32.7 | 10.5 | 12.8 | 0.60 | **B + D** lateral+caudal, worse left |
| FSD_R | 39.0 | +24.1 | −24.1 | 14.3 | 19.9 | 0.56 | **B** lateral+cranial |
| FSD_L | 35.4 | +0.5 | −25.2 | 6.7 | 34.7 | 0.53 | **B + E** often cranial; B26_13 outlier |

Better landmarks (contrast): mean errs 13.5–17.9; smaller biases; higher confidence (~0.68–0.83).

### 4.2 Taxonomy (A–G)

| Code | Meaning | Applies to |
|------|---------|------------|
| A random | Unstructured scatter | Not dominant for problem group |
| B systematic translation | Consistent sign Δx/Δy | ASL_R, FSP_*, FSD_* |
| C systematic anatomical misplacement | Wrong structure | **ASL_L** |
| D side-specific | L≠R severity | **ASL_L ≫ ASL_R**; FSP_L &gt; FSP_R |
| E image-specific | Single-case spikes | FSD_L on B26_13 (79 px); FSP_* on B26_26 |
| F annotation-driven | GT wrong | **Not supported** by geometric/visual QA |
| G model-capacity / data-volume | Underfitting even on train | **Yes** — V2 ASL_L bad on train+val; n=21 |

### 4.3 Why all 5 val ASL_L predictions are systematically medial

Per-case Δx all negative (−73 to −157). Distance of **ASL_L prediction** to GT landmarks:

| Case | d(pred, ASL_L GT) | d(pred, ASM_L GT) | Closer to |
|------|------------------:|------------------:|-----------|
| B26_10 | 95.6 | **22.6** | **ASM** |
| B26_13 | 81.6 | **28.3** | **ASM** |
| B26_17 | 80.3 | **62.3** | **ASM** |
| B26_20 | 166.8 | **51.5** | **ASM** |
| B26_26 | 100.1 | **28.0** | **ASM** |

**5/5 predictions closer to ASM_L than to ASL_L.** This is a **learned confusion** between left lateral and left medial sourcil endpoints — consistent with prior note that raw V2 ASL_L ≈ ASM_L on ~25/26 cases (original-px analysis). Low confidence (0.31–0.62) matches uncertain / wrong mode.

Not explained by: random noise, global overlay shift, Flutter/PDF, IT head, or GT medial labeling.

---

## 5. Prediction vs ground truth visual audit (val)

No new visualization files were created. Existing artifacts inspected conceptually / numerically:

- Phase 9B appendix tables (GT640 vs V5/V2)  
- `_v5_phase2_checkpoint_audit_temp/{V2,phase2}/B26_{10,13,17,20,26}.txt`  
- `predictions_v2/labels/*.txt`  
- `asl_l_refinement_visual_review.csv` (shows raw→offset-refine gains; **not** endorsed as primary remediation)

### 5.1 Conceptual comparison table (six problem KP)

V2 and V5 columns are **identical** within float noise (Phase 9B: 69/70 pairs Δ&lt;1e-5).

#### B26_10

| LM | GT 640 | V2 640 | V5 640 | Err | Read |
|----|--------|--------|--------|----:|------|
| ASL_R | (98.3,223.4) | (133.2,219.3) | same | 35.1 | Too lateral |
| ASL_L | (531.9,229.9) | (438.0,248.2) | same | 95.6 | Far medial → near ASM |
| FSP_R | (141.9,401.4) | (131.7,432.3) | same | 32.5 | Too caudal |
| FSP_L | (485.1,400.0) | (518.4,438.5) | same | 51.0 | Lateral+caudal |
| FSD_R | (129.8,572.6) | (161.9,532.6) | same | 51.3 | Lateral+cranial |
| FSD_L | (493.0,579.1) | (501.7,535.1) | same | 44.9 | Cranial |

#### B26_13

| LM | GT 640 | V2/V5 | Err | Read |
|----|--------|-------|----:|------|
| ASL_R | (130.7,206.4) | (136.6,188.8) | 18.7 | Near OK |
| ASL_L | (482.7,188.8) | (409.9,225.7) | 81.6 | Medial misplacement |
| FSP_R | (133.2,393.3) | (133.6,393.4) | **0.4** | Accurate |
| FSP_L | (498.1,384.6) | (516.9,402.4) | 25.9 | Mild systematic |
| FSD_R | (139.9,555.7) | (154.9,502.8) | 55.0 | Too cranial |
| FSD_L | (504.0,578.9) | (508.1,499.5) | **79.4** | Large cranial (FOV/axis) |

#### B26_17

| LM | GT 640 | V2/V5 | Err | Read |
|----|--------|-------|----:|------|
| ASL_R | (45.8,253.1) | (99.1,239.8) | 55.0 | Large lateral shift |
| ASL_L | (532.8,266.7) | (454.2,283.5) | 80.3 | Medial |
| FSP_R | (111.5,454.0) | (108.1,467.1) | 13.5 | Mild |
| FSP_L | (489.4,458.3) | (516.1,478.2) | 33.3 | Lateral+caudal |
| FSD_R | (93.3,590.8) | (140.1,578.4) | 48.5 | Lateral |
| FSD_L | (506.5,585.7) | (510.8,581.5) | **6.1** | Accurate |

#### B26_20

| LM | GT 640 | V2/V5 | Err | Read |
|----|--------|-------|----:|------|
| ASL_R | (94.1,213.6) | (108.6,230.6) | 22.3 | Mild |
| ASL_L | (541.8,205.8) | (384.7,261.9) | **166.8** | Worst medial (conf 0.31) |
| FSP_R | (123.1,436.6) | (104.6,461.0) | 30.6 | Caudal+medial |
| FSP_L | (524.2,425.0) | (535.2,459.8) | 36.5 | Caudal |
| FSD_R | (104.2,606.3) | (109.6,588.1) | 19.0 | Mild |
| FSD_L | (546.3,603.0) | (537.0,581.8) | 23.1 | Mild |

#### B26_26

| LM | GT 640 | V2/V5 | Err | Read |
|----|--------|-------|----:|------|
| ASL_R | (114.4,222.8) | (88.3,202.3) | 33.2 | Medial+cranial (opposite ASL_R usual) |
| ASL_L | (512.6,218.4) | (412.6,223.1) | 100.1 | Medial |
| FSP_R | (114.4,373.2) | (84.1,432.6) | 66.7 | Large caudal+medial |
| FSP_L | (505.3,383.3) | (546.2,435.8) | 66.5 | Large lateral+caudal |
| FSD_R | (78.7,549.2) | (99.9,552.2) | 21.4 | Mild |
| FSD_L | (526.5,537.6) | (521.4,560.4) | 23.3 | Mild caudal |

**Visual audit conclusion:** Errors are **per-landmark anatomical**, heterogeneous across KP on the same image — incompatible with a single remapping bug.

---

## 6. Training audit (V2 + V5 init)

### 6.1 V2 (source of legacy KP0–13)

| Parameter | Value |
|-----------|-------|
| Init chain | COCO `yolo11n-pose.pt` → V1 best → **V2 best** (`yolo_pose_new_26_v2-3`) |
| Architecture | YOLO11n-pose, ~nano, `nc=1`, **14 KP** at train time |
| Dataset size | **21 train / 5 val / 0 test** |
| Class/KP imbalance | 1 class; **equal pose loss across KP** (`pose=12.0`); no ASL/FSP upweight |
| `imgsz` | 640 (~4.5× downscale from ~2900 px natives) |
| Epochs | 100; best @ **80** (mAP50-95(P)=0.692) |
| Batch / device | 2 / CPU |
| LR | `lr0=0.01`, `lrf=0.01`, optimizer auto→AdamW effective ~0.002 |
| Freeze | **`freeze: null`** — full fine-tune |
| Augmentations | **Aggressive:** mosaic=1.0, randaugment, erasing=0.4, fliplr=0.5, scale=0.5, translate=0.1 |
| Pretrained | true (from V1) |
| Legacy head fine-tuned? | **Yes in V2** — and **still failed ASL_L on train** |

Implication: V2 was **not** “never trained on these points”; it was trained and **underlearned / confused** ASL_L despite seeing labels. High aggregate mAP **masked** landmark-level failure.

### 6.2 V5 Phase 2

| Parameter | Value |
|-----------|-------|
| Goal | Add IT_R/IT_L |
| cv4 (legacy 14 KP) | **Frozen** (changed=0) |
| Legacy fine-tune in V5? | **No** |
| Parity | V2≡V5 KP0–13 on val |

V5 **preserved** V2 legacy errors by design.

### 6.3 Was V2 undertrained for these points?

**Yes, in the clinical sense:**

- ASL_L mean ~525 px (original) / ~105 px @640 val — unusable  
- Failure on **train** images ⇒ not pure generalization gap  
- Nano capacity + 21 images + heavy mosaic/erasing + equal KP loss + subtle sourcil target ⇒ under-capacity / under-supervision for hard KP  
- Good KP prove the head *can* learn some anatomy; problem KP need more data and/or targeted training

---

## 7. Root-cause classification

| Landmark | Primary class | Secondary | Evidence |
|----------|---------------|-----------|----------|
| **ASL_L** | **MIXED** (MODEL_CAPACITY + DATA_VOLUME + anatomical confusion) | TRAINING_CONFIGURATION; not SIDE/FLIP; not LABEL_QUALITY | 5/5 pred closer to ASM_L; train+val failure; GT lateral OK; flip OK; def locked |
| **ASL_R** | **MIXED** (DATA_VOLUME + TRAINING_CONFIGURATION) | MODEL_CAPACITY; mild ANATOMICAL_DEFINITION (A1) | Systematic ~33 px bias; conf ~0.5; GT OK |
| **FSP_R** | **MIXED** (DATA_VOLUME + ANATOMICAL_DEFINITION A7 + TRAINING) | IMAGE_DOMAIN (rotation/FOV); MODEL_CAPACITY | Caudal bias; 1/5 near-perfect (B26_13) shows learnability |
| **FSP_L** | **MIXED** (same + SIDE-specific severity) | MODEL_CAPACITY | Larger lateral+caudal bias than R |
| **FSD_R** | **MIXED** (DATA_VOLUME + IMAGE_DOMAIN FOV + A7) | TRAINING_CONFIGURATION | Cranial/lateral bias; FOV-edge GT |
| **FSD_L** | **MIXED** (same + IMAGE-SPECIFIC spikes) | MODEL_CAPACITY | B26_13 79 px cranial; others milder |

**Not selected as primary for any of the six:** LABEL_QUALITY, SIDE/FLIP, pure ANATOMICAL_DEFINITION (DEFINITION_PROBLEM), UNKNOWN.

**Global legacy-group root cause statement:**  
Pre-existing **V2 pose-head underlearning** of hard, low-contrast, definition-edge landmarks on a **tiny dataset**, with **ASL_L collapsing to ASM_L**; **V5 did not remediate** because legacy head stayed frozen.

---

## 8. Remediation options (evaluation only — not executed)

Full scored table: `phase10b_remediation_options.csv`.

| Option | One-line | Suitability |
|--------|----------|-------------|
| **A** QA + relabel + targeted retrain | Needed as **gate**; insufficient alone if GT already correct | Necessary step, not sufficient |
| **B** Expand dataset + relabel + retrain | Attacks true data bottleneck | Core of durable fix |
| **C** Limited pose-head fine-tune | Possible after data/QA; high regress risk if naive | Conditional |
| **D** Dedicated refinement model | OK later as **learned** gated refiner; **not** offset expansion | Secondary |
| **E** Manual correction bridge | Safety now; does not fix AI | Mandatory parallel |
| **F** Combination | Aligns priorities 1–8 below | **Preferred** |

### Brief option notes

- **A expected benefit:** Confirm A1/A7; catch rare mistakes. **Risk:** Relabeling “correct” points wastes time.  
- **B:** Highest expected ASL_L benefit. **Risk:** Domain shift; schedule. **Data:** +40–80 AP pelvis recommended.  
- **C:** Low LR, freeze IT (+ preferably backbone), monitor good KP. **Risk:** V3/V4-style collapse if `lr0=0.01` full unfreeze.  
- **D:** Existing `refine_asl_l` + TRAIN `C_asm_offset` improves numbers but is an **offset family** — forbidden as primary strategy. Learned anatomical refiner with QC could be Phase 10D+.  
- **E:** Backend landmarks mode exists; Flutter editor missing (Phase 10 R19).  
- **F:** Sequence A→(E parallel)→B→C→optional D; regression gates throughout.

---

## 9. Recommended strategy

### Preferred: **OPTION F — Combination**

**Program shape:**

1. **Physician / senior annotator QA** on ASL/ASM/FSP/FSD (confirm, don’t blindly rewrite). Lock A1 examples (sourcil vs rim). Optional FOV policy for FSD (`v=2` vs `v=0`).  
2. **Expand AP-pelvis dataset** with the same locked protocol; stratified FOV / contrast / dysplasia-like roofs if available.  
3. **Limited legacy pose-head fine-tune** (or controlled V2→V6 pose run) with: low LR, freeze IT head, strong **good-landmark regression gates**, milder mosaic/erasing than V2 defaults, optional higher loss weight on ASL/FSP/FSD.  
4. **Manual correction UX** as safety bridge until gates pass.  
5. **Defer** dedicated learned refiner until after pose improvement; **never** expand hard-coded coordinate offsets; **never** change `mvp_geometry` formulas to absorb bias.

### Why preferred (priority order)

1. **Anatomical correctness** — fixes wrong structure (ASL_L→ASM) via learning correct target, not shifting pixels blindly.  
2. **Reproducibility** — locked definitions + expanded multi-case evidence.  
3. **Preserve good landmarks** — explicit regression gates + freeze IT.  
4. **No hard-coded offsets.**  
5. **No formula hacks.**  
6. **No IT regression** — IT stays frozen / separately gated.  
7. **Measurable validation** — per-KP + angle + side metrics (§10).  
8. **Extensibility** — cleaner ASL/FSP/FSD unlock VCE/Tönnis/CCD credibility and future offset/FAI work that depends on shaft/roof quality.

---

## 10. Validation plan (after remediation — engineering, not clinical claim)

### 10.1 Splits

| Split | Minimum recommendation | Role |
|-------|------------------------|------|
| Train | ≥50–80 labeled AP pelvis (after expansion) | Learning |
| Val | ≥10–15 | Early stop / hyperparams |
| **Test** | ≥15 **held-out, never trained** | Final report (currently **0** — must create) |
| Current 5 val | Keep as continuity probe vs Phase 9B | Regression vs V2/V5 numbers |

Do **not** tune on the final test set.

### 10.2 Dataset size

- **Floor to attempt pose fine-tune with regression gates:** current 26 + confirmed QA (pilot only).  
- **Minimum for claiming legacy remediation:** **≥60–100** total images with locked protocol; **≥15** clean test.  
- Prefer diversity (FOV length, exposure, mild osteophytes) over duplicates.

### 10.3 Metrics

| Layer | Metrics |
|-------|---------|
| Per-landmark | mean / median / max / p90 err @640 and @original; % &lt;25 / &lt;50 / &lt;75 px @640 |
| Side-specific | ASL_L vs ASL_R, FSP_L vs FSP_R, etc. **separately** |
| Bias | mean Δx, Δy (detect residual medial ASL_L) |
| Confusion check | fraction of ASL_L preds closer to ASM_L than ASL_L — must → ~0 |
| Anatomical plausibility | ASL lateral to ASM; FSD distal to FSP; side order |
| Angles | VCE / Tönnis / CCD absolute error vs GT geometry (engineering) |
| IT regression | IT mean err & QC status unchanged within tolerance; cv4/IT freeze parity if applicable |
| Good-KP regression | FHC/FNM/TD/ASM mean err must not worsen beyond agreed Δ (e.g. +5 px @640) |
| Confidence | calibration / REVIEW rates when err high |
| Physician comparison | **Separate study** — pairwise landmark/angle vs physician; **do not claim clinical validation** from engineering gates alone |

### 10.4 Suggested engineering thresholds (@640, test set)

| Landmark | Target mean | Hard fail |
|----------|-------------|-----------|
| ASL_L | ≤25 px | &gt;50 px mean or any systematic medial ASM-collapse |
| ASL_R | ≤25 px | &gt;40 px mean |
| FSP_*/FSD_* | ≤25–30 px | &gt;50 px mean |
| Good KP | ≤ current V2/V5 ±5 px | Any &gt;10 px mean regression |
| IT | ≤ current ±5 px | Any QC path break |

### 10.5 Explicit non-claims

This plan validates **engineering reproducibility and regression safety**. It does **not** constitute clinical validation, regulatory clearance, or physician sign-off.

---

## 11. Development order (do not implement in this phase)

| Step | Action | Exit criterion |
|-----:|--------|----------------|
| **1** | Freeze scope: no Flutter/PDF/`mvp_geometry`/IT/offset “fixes” | Written constraint checklist signed in Phase 10C kickoff |
| **2** | Physician A1/A7 micro-calibration session on 5–10 exemplar images (ASL sourcil vs rim; FSP height; FSD FOV policy) | Written locked examples; no silent definition drift |
| **3** | Annotation QA pass on all 26 ASL/ASM/FSP/FSD (double-read sample ≥30% + all val) | Disagreement report; only edit if physician confirms error |
| **4** | Implement / prioritize **manual landmark correction UX** (bridge) | REVIEW cases editable → recompute measures/PDF |
| **5** | QC gates in product: flag VCE/Tönnis when ASL fails; CCD when FSP/FSD fail | No silent bad angles |
| **6** | Acquire + annotate expanded AP pelvis set under locked protocol | ≥40–80 new; train/val/test split documented |
| **7** | Design training run: freeze IT; low LR; reduced mosaic/erasing; optional KP loss weights; good-KP early-stop | Written `args` plan reviewed |
| **8** | Pilot fine-tune on QA’d current set (optional smoke) | No IT/good-KP regression; ASL_L confusion metric improves |
| **9** | Full train on expanded data | Meet §10 thresholds on **test** |
| **10** | Parity + regression pack vs V2/V5 (KP tables, IT, angles) | Promote candidate checkpoint only if gates pass |
| **11** | Only if residual ASL_L errors remain: evaluate **learned** gated refiner (not offset table) | Separate acceptance test |
| **12** | Update Phase 10 requirements status; plan physician comparison study | Engineering done ≠ clinical done |

**Exact next phase name:** **Phase 10C — Legacy Landmark Remediation Program (execute Option F plan; still no formula/offset/IT misuse).**

---

## FINAL RECOMMENDATION

### Root cause
**MIXED — primarily DATA_VOLUME + MODEL_CAPACITY/underlearning of hard landmarks in V2**, with **ASL_L systematically confused with ASM_L** (anatomical misplacement). Labels and `flip_idx` are not the primary cause. Definitions are locked and adequate (residual A1/A7 only). V5 froze the legacy head and therefore **inherited** the failure. Flutter/PDF/`mvp_geometry` are not the root.

### Preferred remediation
**OPTION F (Combination):** annotation QA confirm → expand dataset → limited pose-head fine-tune with regression gates → manual correction as safety bridge → optional learned refiner later.

### Data required
- QA double-read on current 26 (problem KP)  
- **≥40–80 new** AP pelvis annotations under locked ASL/FSP/FSD protocol  
- True **held-out test ≥15**  
- Physician exemplars for A1/A7

### Code required
- **Later (Phase 10C+):** training script/config for gated fine-tune; Flutter manual edit UX; QC gating for measures  
- **Not now:** no production code changes in this audit phase

### Training required
- Yes — **targeted legacy pose remediation** after data/QA  
- Freeze / protect **IT** and monitor **good KP**  
- Do **not** retrain IT to “fix” ASL/FSP/FSD

### Validation required
- Per-landmark + side-specific + bias + ASL↔ASM confusion metric  
- VCE/Tönnis/CCD engineering errors vs GT  
- IT + good-KP regression gates  
- Physician comparison as **separate** study (not claimed here)

### What must NOT be changed
- Official labels/dataset **until** dedicated QA phase authorizes edits  
- `mvp_geometry` formulas  
- Flutter/PDF coordinate mapping as a “fix”  
- Hard-coded coordinate offsets / expanding TRAIN ASM-offset as strategy  
- IT head / IT labels to compensate legacy KP  
- Blind full retrain without regression gates

### Exact next phase
**Phase 10C — Legacy Landmark Remediation Program (Option F execution plan)**  
Start with Steps 1–5 (constraints, definition lock, QA, manual bridge, QC gates), then data expansion and gated training.

---

*End of Phase 10B read-only audit. Deliverables: this file + `phase10b_remediation_options.csv`. No source, data, model, or checkpoint modifications were made.*
