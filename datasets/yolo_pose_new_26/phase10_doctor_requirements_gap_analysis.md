# Phase 10 — Complete Doctor Requirements Gap Analysis

**Date:** 2026-09-04  
**Mode:** READ-ONLY — no source, model, dataset, label, `mvp_geometry`, Flutter, PDF, or training changes except this report and the companion CSV  
**Basis:** Live repository code + Phase 9B landmark audit + Phases 7A/7B/8A/8B + specs (`docs/landmark_specification.md`, `missing_measurements_spec.md`, `femoral_offset_spec.md`, `bi_ischial_spec.md`)  
**Companion matrix:** `datasets/yolo_pose_new_26/phase10_requirements_matrix.csv`

**Status legend (exactly one per requirement):**

| Code | Meaning |
|------|---------|
| **A** | FULLY IMPLEMENTED AND VERIFIED |
| **B** | IMPLEMENTED BUT PARTIAL / NOT FULLY VALIDATED |
| **C** | PRESENT IN CODE/UI BUT NOT FUNCTIONALLY COMPLETE |
| **D** | ABSENT |
| **E** | IMPLEMENTED BUT CURRENTLY UNRELIABLE / ACCURACY PROBLEM |

**Problem-type tags used below:** engineering · AI/data · mathematical/geometry · clinical-definition · validation · UI/product

---

## 1. Executive summary

The product is a **working digital coxometry MVP**: Android/Flutter + FastAPI backend + V5 Phase 2 (16 landmarks) + `mvp_geometry` (VCE / Tönnis / CCD) + IT QC + PDF report. The **validated demo path** is **DICOM→PNG gallery import**, not the phone-négatoscope path the physician originally requested.

**Phase 9B verdict (`MODEL_ACCURACY`):** legacy KP0–13 errors are **pre-existing V2** problems; V5 did **not** regress them. Mean legacy error **29.7 px** @640; IT **25.7 px** (9/9 GT v=2 &lt;75 px). Worst: **ASL_L** mean **104.9 px**, systematically too medial. Secondary bias group: **ASL_R, FSP_R/L, FSD_R/L**. Errors exist **before** Flutter/PDF. Therefore **do not** “fix” by Flutter/PDF, hard-coded UI offsets, IT-head retrain, or silent `mvp_geometry` formula changes.

**Gap vs doctor brief:**

| Bucket | Verdict |
|--------|---------|
| Core named angles (VCE / Tönnis / CCD) | Implemented in code + unit tests; **clinically unreliable** on sides/landmarks hit by ASL / FSP–FSD bias (**E**) |
| Automatic landmarks (16) | Detected; IT QC exists; **legacy accuracy insufficient** for ASL / shaft group (**E**/mixed) |
| Automatic PDF report | **A** for current measurement scope (engineering verified) |
| Digital import demo | **A**/B — PNG/JPG path solid; native DICOM/PACS **D** |
| Phone + négatoscope | UX Option B exists (guidance/confirm); **no** perspective/glare/scale pipeline; **no** physical Android validation (**B**/C) |
| Femoral offset, alpha, head-neck offset, crossover, FAI suite, limb length, THA planning | Mostly **D**; several need **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** |
| Dysplasia “assessment support” | Indirect via VCE/Tönnis only; no diagnostic module (**B**/C) |

**Bottom line:** The stack can evolve into the physician’s coxometry assistant, but **complete** is not “more UI.” Completeness requires (1) legacy landmark remediation with real data/AI work, (2) clinical definitions for every new measure, (3) scale/calibration for length metrics, (4) honest camera-domain handling + validation, (5) physician comparison studies. Engineering validation ≠ clinical validation.

---

## 2. Doctor requirements matrix

| # | Requirement | Status | Priority | Primary problem type(s) | One-line gap |
|---|-------------|:------:|:--------:|-------------------------|--------------|
| R1 | Smartphone camera photo of pelvic XR on négatoscope | **B** | P0 | UI/product + validation + engineering | Capture UX exists; photo domain unvalidated; no geometric restore |
| R2 | Automatic anatomical landmark detection | **E** | P0 | AI/data + validation | 16 KP detected; ASL/FSP/FSD clinically unusable as-is |
| R3 | VCE / Wiberg / CEA | **E** | P0 | AI/data (ASL) + validation | Formula OK; L (and often R) degraded by ASL error |
| R4 | Tönnis / HTE | **E** | P0 | AI/data (ASL) + validation | Formula OK; depends on ASL (+ ASM/TD) |
| R5 | CCD | **E** | P0 | AI/data (FSP/FSD) + validation | Formula OK; shaft landmarks biased |
| R6 | Femoral offset | **D** | P2 | clinical-definition + math + engineering + scale | Spec only; no `femoral_offset()`; mm/px undefined |
| R7 | Alpha angle | **D** | P3 | clinical-definition + AI/data + view protocol | No formula locked; AP≠Dunn; no α-point |
| R8 | Head-neck offset | **D** | P3 | clinical-definition + AI/data | Classic points not in 16-KP set |
| R9 | Cross-over sign | **D** | P3 | clinical-definition + AI/data | No wall landmarks / sign logic |
| R10 | Acetabular index | **C** | P2 | clinical-definition | Tönnis/HTE present; separate “AI” output absent — **DEFINITION TO BE CONFIRMED** |
| R11 | FAI-related parameters | **D** | P3 | clinical-definition + AI/data | Depends on alpha/crossover/etc. |
| R12 | Limb-length measurements | **D** | P3 | clinical-definition + AI/data + FOV | Pelvis FOV; no distal landmarks; needs long-leg protocol |
| R13 | Dysplasia-related assessment support | **B** | P1 | UI/product + clinical-definition + validation | VCE/Tönnis support assessment; no thresholds/diagnosis (correctly avoided) |
| R14 | THA / arthroplasty planning support | **D** | P3 | clinical-definition + product | No templating, sizing, cup/stem planning |
| R15 | Automatic report generation | **A** | P1 | — | PDF with image, overlay, VCE/Tönnis/CCD, IT QC, disclaimer |
| R16a | Landmark: femoral head center | **B** | P1 | validation | FHC mean ~14–18 px640 — usable engineering-wise; not physician-validated |
| R16b | Landmark: lateral acetabular roof (ASL) | **E** | P0 | AI/data | ASL_L catastrophic; ASL_R systematic bias |
| R16c | Landmark / line: bi-ischial | **B** / measure **D** | P2 | clinical-definition + math | IT_R/IT_L detected+QC; no bi-ischial *measurement* output |
| R16d | Landmark / line: teardrop (ITH) | **B** | P1 | validation | TD usable (~17 px); ITH used in VCE/Tönnis |
| R16e | Landmark / axis: femoral neck | **B** | P1 | validation | FHC+FNM relatively good; CCD still hurt by shaft |
| R16f | Landmark / axis: femoral shaft | **E** | P0 | AI/data | FSP/FSD systematic bias group |
| R17 | Parity with mediCAD / TraumaCad / etc. | **D** | P3 | product scope | Reference tools only — not a compliance target for MVP |
| R18 | Digital DICOM→PNG import (demo path) | **B** | P0 | engineering | Gallery PNG/JPG is validated demo; in-app DICOM/PACS **D** |
| R19 | Semi-automatic landmark correction | **D** | P1 | UI/product + engineering | Display/zoom only; no drag-edit |
| R20 | Physical scale / mm calibration | **D** | P2 | clinical-definition + engineering | Required for lengths; absent (angles-only MVP) |

---

## 3. Current implemented functionality

### 3.1 End-to-end (code-verified)

```
HomeScreen
  ├─ Gallery: FilePicker → JPG/JPEG/PNG  (demo: DICOM→PNG from new_26)
  └─ Camera Option B: guidance → ImagePicker(camera) → confirm/retake
       → EXIF bake (image_normalizer)
       → PreviewScreen → AnalysisScreen
       → POST /analyze
Backend:
  validate → preprocess (V5: 640 RGB letterbox)
  → V5 Phase 2 pose (KP0–13 frozen + IT head)
  → optional ASL_L refinement (mvp_geometry.refinement; env-gated)
  → IT QC (accept/review/unavailable)
  → mvp_geometry: VCE, Tönnis, CCD bilaterally
  → landmarks in original_image_pixels
Flutter Results: overlay, zoom/pan, measures, IT status, model label
PDF: ReportExportService / ReportPdfBuilder
```

### 3.2 Delivered capabilities

| Capability | Evidence |
|------------|----------|
| V5 Phase 2 integrated; `/health` model version | Demo launcher; backend detection factory; mobile model label |
| 16 landmarks | `data.yaml`, `meta/keypoint_order.md`, V5 detector |
| IT QC | `backend/app/services/detection/v5_it_qc.py`; Flutter `it_status_section.dart` |
| VCE / Tönnis / CCD | `mvp_geometry/measurements.py`, `hip_measures.py`; API + UI + PDF |
| PDF report | `mobile/lib/services/report/*` |
| Camera UX Option B | `camera_guidance_screen.dart`, `camera_confirm_screen.dart`, `camera_framing_guide.dart` |
| Engineering tests | Flutter **102** passed; backend **167** passed, **1** skipped (project state) |
| Android debug APK builds | Phase 8A/8B |
| iOS | Out of scope (no macOS/Xcode) |

### 3.3 What exists but is not a clinical measure

- **IT_R / IT_L:** detection + QC + overlay/PDF — **not** inputs to VCE/Tönnis/CCD (`hip_measures._REQUIRED` excludes IT).
- **ASL_L refinement:** post-YOLO `refine_asl_l` with TRAIN `C_asm_offset` (`mvp_geometry/refinement/`). Phase 9B measured **raw** pose predictions; do **not** expand hard-coded offsets as the remediation strategy for the legacy group (per Phase 9B / project constraints).
- **Manual landmarks API mode:** `POST` measurements with JSON landmarks exists for geometry testing — not an in-app edit UX.

---

## 4. Missing functionality

| Missing item | What is required to implement correctly | Problem types |
|--------------|----------------------------------------|---------------|
| Reliable ASL / FSP / FSD | Targeted legacy remediation (label QA ± limited pose-head work ± validated refinement) — **not** IT retrain, Flutter offsets, or formula hacks | AI/data, validation |
| Femoral offset | Physician-locked metric (F1–F7) + mm/px method + `femoral_offset()` + API/UI + FOV rule A7 + tests | clinical-definition, geometry, engineering, scale |
| Alpha angle | Lock view (A1), neck axis (A2), circle fit (A3), sphericity-loss point (A4), thresholds (A5); usually Dunn/lateral data — AP `new_26` insufficient | clinical-definition, AI/data, validation |
| Head-neck offset | Define cortical/junction points; annotate; detect or derive; formula; validate | clinical-definition, AI/data |
| Cross-over sign | Define anterior/posterior wall representation; annotate walls/curves; qualitative or quantitative rule | clinical-definition, AI/data |
| Acetabular index (if ≠ Tönnis) | Confirm with physician whether Tönnis/HTE **is** the requested AI; if not, define pediatric/other formula | clinical-definition |
| FAI suite | Union of alpha, crossover, related; product packaging | clinical-definition, product |
| Limb length | Long-leg / full-limb protocol, distal landmarks, scale | clinical-definition, AI/data, FOV |
| THA planning | Templating, implant libraries, planning UI — out of current architecture intent | product |
| Bi-ischial *measurement* | Confirm output (angle vs distance vs pelvic tilt proxy); if distance → mm/px; geometry on IT_R–IT_L | clinical-definition, geometry |
| In-app DICOM / PACS | Parser, PixelSpacing, series selection, network — separate product track | engineering |
| Landmark drag-edit | Flutter editor → re-POST landmarks or local recompute → PDF refresh | UI/product, engineering |
| Camera geometric restore | Optional crop/homography **only** if corrected bytes become the single original for detect+overlay; plus photo-domain validation | engineering, validation |
| Clinical thresholds / diagnosis | Explicitly **out** of safe MVP unless physician + regulatory path — keep disclaimer | clinical-definition, product |

---

## 5. Current technical problems

| Problem | Evidence | Must not “fix” by |
|---------|----------|-------------------|
| ASL_L mean 104.9 px, always too medial | Phase 9B | Flutter/PDF offsets; IT retrain |
| ASL_R / FSP_* / FSD_* systematic bias | Phase 9B means ~29–43 px | Hard-coded coordinate offsets |
| VCE_L / Tönnis_L numerically computable but anatomically wrong when ASL_L wrong | Geometry consumes bad ASL | Changing `vce_angle` / `tonnis_angle` formulas |
| CCD sensitive to FSP–FSD | Spec A7/A8 + Phase 9B | Changing `ccd_angle` without clinical lock |
| Camera path domain shift | Training = DICOM→PNG; photos unvalidated | Claiming clinical photo accuracy |
| No mm/px | Length measures blocked | Inventing PixelSpacing from pixels alone |
| Small val set (n=5 official val images in Phase 9B) | Phase 9B | Over-claiming population accuracy |
| No physician angle comparison study | Docs/audits | Calling results “clinically validated” |
| ASL_L refinement is TRAIN ASM-offset | `calibration.py` | Treating it as Phase 9B-approved cure for all legacy KP; expanding offset hacks |

---

## 6. Landmark accuracy problems

**Source:** Phase 9B — V5 Phase 2, letterbox 640×640, val B26_10/13/17/20/26.  
**Legacy accuracy problem group (explicit):** **ASL_L, ASL_R, FSP_R, FSP_L, FSD_R, FSD_L**.

### 6.1 Complete 16-landmark table

| Landmark | KP | Status | Mean err (px640) | Main observed problem | Usable for clinical measurement? | What must be improved | Priority |
|----------|---:|--------|-----------------:|------------------------|----------------------------------|------------------------|:--------:|
| TD_R | 0 | Better legacy | 16.8 | Mild shift | Conditionally yes (engineering) | Keep; enlarge clinical check | P2 |
| TD_L | 1 | Better legacy | 17.3 | Mild shift | Conditionally yes | Same | P2 |
| FHC_R | 2 | Better legacy | 13.9 | Small error | Conditionally yes | Clinical angle compare | P1 |
| FHC_L | 3 | Better legacy | 17.8 | Small error | Conditionally yes | Clinical angle compare | P1 |
| **ASL_R** | 4 | **Legacy problem group** | **32.8** | Systematic bias (Δx=+16.5) | **No (borderline)** | Pose accuracy / label QA — not UI offset | **P0** |
| **ASL_L** | 5 | **Legacy problem group** | **104.9** | Systematically too medial (Δx=−100.5); MISPLACED all 5 | **No** | Highest priority remediation | **P0** |
| ASM_R | 6 | Better legacy | 17.9 | Mild | Conditionally yes | Monitor | P2 |
| ASM_L | 7 | Better legacy | 17.9 | Mild | Conditionally yes | Monitor | P2 |
| FNM_R | 8 | Best legacy | 13.5 | Small | Conditionally yes | Keep | P2 |
| FNM_L | 9 | Better legacy | 17.8 | Mild caudal bias | Conditionally yes | Monitor | P2 |
| **FSP_R** | 10 | **Legacy problem group** | **28.8** | Systematic shift (Δy=+25.6) | **No / limited** | Shaft axis accuracy | **P0** |
| **FSP_L** | 11 | **Legacy problem group** | **42.6** | Lateral+caudal bias | **No** | Shaft axis accuracy | **P0** |
| **FSD_R** | 12 | **Legacy problem group** | **39.0** | Lateral+cranial bias | **No** | Shaft axis accuracy | **P0** |
| **FSD_L** | 13 | **Legacy problem group** | **35.4** | Often too cranial | **No / limited** | Shaft axis accuracy | **P0** |
| IT_R | 14 | IT (separate head) | 27.9 (n=4) | Acceptable vs legacy ASL | Conditionally yes for QC/display; measure TBD | Keep IT QC; clinical bi-ischial definition | P2 |
| IT_L | 15 | IT | 24.0 | Acceptable | Conditionally yes for QC/display | Same | P2 |

**Aggregates (Phase 9B):** KP0–13 mean **29.7** px; IT mean **25.7** px; V2≈V5 KP0–13 identical.

**Clinical usability rule used here:** mean error ≫ ~25–30 px @640 and/or systematic anatomical misplacement → **not** usable for clinical measurement without remediation or mandatory human correction.

---

## 7. Measurement dependency matrix

| Measurement | Required landmarks | Required geometric construction | Current availability | Current reliability | Missing prerequisites | Validation needed |
|-------------|-------------------|---------------------------------|----------------------|---------------------|----------------------|-------------------|
| **VCE / Wiberg / CEA** | TD_R, TD_L, FHC_side, ASL_side | ITH; VERT ⟂ ITH through FHC; angle FHC→ASL (`vce_angle`) | Code **yes** | **Unreliable** especially L (ASL_L) | ASL accuracy; clinical naming CEA vs VCE polish | Engineering: unit tests exist. Clinical: physician vs auto angles |
| **Tönnis / HTE** | TD_R, TD_L, ASM_side, ASL_side | ITH; sourcil ASM→ASL vs ∥ ITH (`tonnis_angle`) | Code **yes** | **Unreliable** when ASL wrong | ASL accuracy; sign/threshold A4 clinical lock optional | Same |
| **CCD** | FHC, FNM, FSP, FSD (side) | NECK FHC–FNM vs SHAFT FSP–FSD (`ccd_angle`) | Code **yes** | **Degraded** by FSP/FSD bias; rotation sensitivity A8 | Shaft accuracy; pose protocol QC | Same + femoral rotation QC |
| **Femoral offset** | Typically FHC + SHAFT (FSP–FSD) | **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** (perp vs horizontal vs other) + mm/px | Landmarks mostly present; **function absent** | N/A | F1–F7 clinical lock; calibration; FOV A7; API/UI | After definition: analytic tests + physician mm compare |
| **Alpha angle** | FHC + neck axis + sphericity-loss point; often non-AP view | Nötzli-style; **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** (view A1–A7) | **Absent** | N/A | View protocol, α-point (not in 16 KP), data | Dunn/lateral dataset + clinical |
| **Head-neck offset** | Head center + neck cortex / junction refs | **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** | Incomplete (FNM ≠ classic offset points) | N/A | New points or contour method; formula; scale if mm | Clinical + engineering |
| **Cross-over sign** | Anterior + posterior acetabular walls | Qualitative overlap rule — **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** | **Absent** | N/A | Wall landmarks/curves; sign logic | Clinical reader study |
| **Acetabular index** | If = adult HTE/Tönnis: same as Tönnis. If pediatric AI: Hilgenreiner + acetabular roof — **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** | Depends on definition | Tönnis only | Tied to ASL | Physician confirmation | Clinical |
| **FAI parameters** | Union (alpha, crossover, …) | Suite packaging — **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** | **Absent** | N/A | Sub-measures first | Clinical |
| **Limb length** | Proximal + distal limb points (ankle/knee) outside pelvis FOV | Length along axis + mm/px — **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** | **Absent** | N/A | Acquisition protocol; landmarks; scale | Clinical |
| **Dysplasia-related** | Typically VCE + Tönnis (+ optional others) | Interpretive layer — **do not invent diagnosis** | Angles present | Unreliable until ASL fixed | Optional thresholds only with physician; no auto-diagnosis | Clinical |
| **THA planning** | Implant templates, cup/stem axes, offset, LL, etc. | Planning toolkit — **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** | **Absent** | N/A | Entire planning module | Clinical + regulatory |

**IT note:** IT supports future bi-ischial line `BI_ISCHIAL = IT_R–IT_L`; output metric still **DEFINITION / CLINICAL METHOD TO BE CONFIRMED**.

---

## 8. Camera / négatoscope gap analysis

### 8.1 Two acquisition worlds

| Aspect | Digital radiograph (DICOM→PNG/JPG) | Phone photograph on négatoscope |
|--------|-----------------------------------|----------------------------------|
| Domain vs training | **Matched** (`new_26` from DICOM) | **Mismatched** — no photo training domain |
| Product path | Gallery import — **validated demo** | Option B UX — **unvalidated** |
| Perspective distortion | Negligible (native digital) | Common if phone not parallel |
| Glare / reflections | Rare | Common (glass/lightbox) |
| Rotation | EXIF bake handled | EXIF + possible in-plane tilt of film |
| Cropping | User/file crop | Partial film / background clutter |
| Non-uniform scaling | No | Possible (perspective → affine shear) |
| Resolution | High DICOM renders | Phone sensor + distance dependent |
| Exposure / contrast | Windowed digital | Ambient light + auto-exposure |
| Radiograph borders | Usually full FOV | Need framing; guide is **visual only** |
| Calibration / physical scale | DICOM PixelSpacing possible later; **not used** | Harder; ruler/marker needed |
| Patient marker orientation | Usually in DICOM | May be illegible in photo |
| Quality control | Implicit digital QC | Needed: sharpness, full pelvis, glare, tilt warnings |

### 8.2 Implemented vs missing

| Item | Status |
|------|--------|
| Open camera + capture | Implemented (`radiograph_picker.pickFromCamera`) |
| Guidance + confirm/retake | Implemented (Phase 7B) |
| Honest prototype warning | Implemented (`CAMERA_CAPTURE.md`, UI copy) |
| EXIF orientation bake | Implemented |
| Perspective / keystone correction | **Missing** |
| Glare / reflection handling | **Missing** |
| Film-edge crop / deskew | **Missing** (guide does not alter pixels) |
| Photo-domain model / fine-tune | **Missing** |
| Physical Android + réel négatoscope validation | **Missing** |
| Emulator camera as validation | Explicitly **not** sufficient (`CAMERA_CAPTURE.md`) |

**Angles** remain valid under uniform scale; **perspective/shear** can corrupt angles. Lengths need scale regardless.

---

## 9. Validation gap analysis

### 9.1 Engineering validation (exists)

| Area | Evidence | Sufficient for shipping claims? |
|------|----------|----------------------------------|
| Landmark decode / V2↔V5 parity | Phase 9B, checkpoint audits | Yes for “no V5 regression” |
| Geometry unit tests | `mvp_geometry/tests/` | Yes for formula correctness given good points |
| API /analyze | Backend tests | Yes for plumbing |
| Flutter UI/PDF | 102 tests | Yes for UI contracts |
| IT QC thresholds | Derived from 26-image GT | Engineering-only; small-N |
| Digital demo path | Phase 8A/8B | Yes for jury/demo on known PNG |

### 9.2 Clinical validation (does **not** exist as evidence)

| Claim | Evidence in repo? |
|-------|-------------------|
| Auto landmarks agree with physician clicks beyond GT labels | No dedicated physician study |
| Auto VCE/Tönnis/CCD agree with physician measurements | **No** |
| Phone-négatoscope path clinically reliable | **No** |
| Thresholds for dysplasia/FAI | Explicitly avoided (correct) |
| Device certification | Explicitly disclaimed |

**Do not claim clinical validation.** Current state = **engineering / research prototype validation** on a small digital set.

### 9.3 Sufficiency verdict

| Target | Sufficient today? |
|--------|-------------------|
| Landmark detection (engineering) | Partial — IT OK-ish; legacy ASL/shaft **no** |
| Each measurement (clinical) | **No** until ASL/shaft remediated + physician compare |
| Phone-camera workflow | **No** |
| Clinical reliability | **No** |
| Comparison vs physician | **Missing** (must be designed) |

---

## 10. Architecture gap analysis

Can the stack evolve from VCE/Tönnis/CCD MVP → full coxometry assistant?

| Layer | Fit for evolution? | Gap |
|-------|--------------------|-----|
| **Backend** FastAPI `/analyze` | **Yes** | Add measure fields carefully; keep unavailable semantics |
| **Flutter** | **Yes** | Needs edit UX, camera preprocess hooks, length units UI |
| **Model** V5 Phase 2 (frozen KP0–13 + IT head) | **Partially** | Legacy head accuracy ceiling; new KP/views need new data |
| **Landmark representation** 16 KP named schema | **Yes** as core; extensible | New measures need new KP or contours — don’t overload IT |
| **Geometry engine** `mvp_geometry` | **Yes** | Add functions only after clinical lock; keep no-invented-coords |
| **QC layer** | **Good pattern** (IT) | Extend QC to ASL/shaft / measure-level confidence |
| **Manual correction** | **Missing** | Critical bridge until AI accurate |
| **PDF/report** | **Reusable** | Extend sections; keep disclaimer |
| **Camera preprocessing** | **Stub** | Optional warp must own the byte identity |
| **Calibration** | **Missing** for mm | Need PixelSpacing / marker / physician scale |
| **Future measurements** | Spec docs exist | Blocked on clinical definitions + data |

**Verdict:** Architecture is **adequate to evolve** without a rewrite. Gaps are **accuracy, definitions, validation, and product modules** — not framework choice.

---

## 11. P0 blockers

1. **ASL_L (and ASL_R) accuracy** — blocks trustworthy VCE/Tönnis (especially left).  
2. **FSP/FSD accuracy** — blocks trustworthy CCD (and future femoral offset).  
3. **No clinical angle comparison protocol** — cannot claim physician-grade measures.  
4. **Négatoscope photograph path** — core to original wording; UX only, domain unvalidated.  
5. **Honesty constraint** — any demo must state digital-validated vs photo-unvalidated.

*Not P0 for “MVP angles exist in code” — they do — but P0 for “complete physician application.”*

---

## 12. P1 priorities

1. Phase 9C-style **legacy remediation plan** (label QA vs limited pose finetune vs validated refinement) — **without** IT-head misuse or Flutter offsets.  
2. **Landmark QC** for ASL/shaft analogous to IT QC (accept/review/unavailable → suppress or flag measures).  
3. **Semi-automatic landmark correction** in Flutter + recompute geometry/PDF.  
4. **Physician measurement comparison** study design on digital set (VCE/Tönnis/CCD).  
5. On-device **Android camera** checklist execution (engineering validation of Option B).  
6. Dysplasia **support** UX: present VCE/Tönnis clearly as assistance, still no auto-diagnosis.  
7. Confirm with physician: **acetabular index ≡ Tönnis/HTE?** and **CEA naming**.

---

## 13. P2 priorities

1. Femoral offset after F1–F7 clinical lock + mm/px method.  
2. Bi-ischial **measurement** output using existing IT (after metric lock).  
3. Optional DICOM file→PNG in-app (still not PACS).  
4. Capture aids: sharpness/glare soft checks; optional four-corner crop **if** identity-preserving.  
5. Enlarge validation set beyond 5 val images.  
6. Physical scale pipeline (PixelSpacing or marker).

---

## 14. P3 future improvements

1. Alpha angle (Dunn/lateral data + A1–A7).  
2. Head-neck offset.  
3. Cross-over sign / FAI suite.  
4. Limb-length (long-leg protocol).  
5. THA planning / templating (mediCAD-class).  
6. PACS / full DICOM workflow.  
7. iOS when macOS/Xcode available.  
8. Feature parity chase with commercial suites — **explicitly deprioritized**.

---

## 15. Recommended target architecture

Keep the current **layered** design; extend, don’t replace:

```
Acquisition
  ├─ Digital: PNG/JPG (+ optional DICOM→PNG)
  └─ Camera: guidance → (optional rectify) → EXIF bake
       ↓
Detection (YOLO pose 16 KP; future KP append-only)
       ↓
QC (per-landmark + per-measure confidence)
       ↓
Optional human correction (edit → same Landmark schema)
       ↓
Geometry engine (angles now; lengths when calibrated)
       ↓
Results + PDF + audit trail (model version, QC, disclaimer)
```

**Principles:** single coordinate identity; no invented points; clinical definitions before code; measure unavailable when QC fails; angles vs lengths separated by calibration.

---

## 16. Recommended development order

1. **Lock clinical priorities** with physician (what “complete” means for v1 vs v2).  
2. **Remediate ASL then FSP/FSD** (AI/data) + measure-level QC.  
3. **Manual correction UX** (product bridge).  
4. **Physician vs auto angle study** on digital path.  
5. **Camera engineering validation** on device; then decide photo-domain ML vs assisted capture.  
6. **Femoral offset** (definitions + scale) once shaft reliable.  
7. **Bi-ischial metric** if physician wants it (IT already present).  
8. **Extended FAI / alpha / crossover / LL / THA** only after definitions + data.  

---

## 17. What must NOT be changed

Per Phase 9B and this gap analysis (until a dedicated approved phase):

- Do **not** change `mvp_geometry` VCE/Tönnis/CCD formulas to “compensate” bad landmarks.  
- Do **not** retrain the **IT head** to fix KP0–13.  
- Do **not** hard-code Flutter/PDF coordinate offsets.  
- Do **not** alter official labels without a B6-style annotation phase.  
- Do **not** invent clinical formulas (offset, alpha, AI, FAI, LL, THA).  
- Do **not** claim clinical validation or device certification.  
- Do **not** treat emulator camera as négatoscope validation.  
- Do **not** expand TRAIN ASM-offset hacks as the general fix for FSP/FSD/ASL_R.

---

## 18. What can safely be reused

- FastAPI analyze pipeline + schemas (`available=false` pattern)  
- V5 Phase 2 IT head + IT QC pattern (extend, don’t scrap)  
- Flutter Results / overlay / PDF composer  
- Camera Option B UX shell  
- `mvp_geometry` angle primitives (given good landmarks)  
- Named 16-KP schema and flip_idx  
- Demo launcher / digital DICOM→PNG path  
- Disclaimer / non-diagnosis product stance  
- Spec documents for missing measures (as requirements input)

---

## 19. What requires new data

| Need | Data required |
|------|----------------|
| Fix ASL / FSP / FSD | More/better AP pelvis annotations; possible hard-example mining; optional limited pose finetune set |
| Photo path | Phone photos of négatoscope ± paired digital GT |
| Alpha / cam FAI | Dunn/lateral (or locked view) with sphericity-loss annotation |
| Cross-over | Wall silhouette annotations |
| Limb length | Full-limb radiographs + landmarks |
| THA | Planning cases / templates (product data, not just KP) |
| Clinical study | Physician-measured angles on same images |
| Scale | DICOM PixelSpacing corpus or physical markers |

---

## 20. What requires clinical input from the physician

| ID | Decision |
|----|----------|
| C1 | Is **acetabular index** identical to **Tönnis/HTE** in this practice? |
| C2 | Accept VCE ≡ Wiberg ≡ CEA naming in UI/PDF? |
| C3 | Femoral offset definition (F1–F7) and mm/px method |
| C4 | Bi-ischial output metric (B2) and IT point definition finalization |
| C5 | Alpha view/protocol (A1–A7) — in or out of AP-only app |
| C6 | Head-neck offset operational definition |
| C7 | Cross-over / FAI suite inclusion criteria |
| C8 | Limb-length protocol and landmarks |
| C9 | THA planning scope (yes/no for this product generation) |
| C10 | Acceptable landmark/angle error tolerances for clinical use |
| C11 | Whether auto thresholds for dysplasia are desired (regulatory impact) |
| C12 | Camera path: required for v1 or digital-only acceptable interim |

Mark any unlocked formula: **DEFINITION / CLINICAL METHOD TO BE CONFIRMED**.

---

## 21. Final definition of “complete” for this project

**Complete** for *this* physician-facing coxometry assistant means **all** of the following — not merely feature checkboxes:

1. **Acquisition:** Reliable path for the agreed primary input (digital and/or validated négatoscope photo), with explicit QC for pose, glare, framing, and scale when needed.  
2. **Landmarks:** All landmarks required by the agreed measurement set are detected **or** human-correctable, with QC that prevents silent bad measures — including remediation of the **ASL / FSP / FSD legacy problem group**.  
3. **Measurements:** Every measure in the agreed clinical set has a physician-locked definition, correct geometry, and (for lengths) calibration.  
4. **Report:** Automatic report includes image, landmarks, measures, QC, model version, and non-diagnostic disclaimer.  
5. **Validation:** Engineering tests **plus** a documented **physician comparison** study on the target domain(s).  
6. **Scope honesty:** Items outside the agreed set (full THA planner, PACS, mediCAD parity) are either scheduled or explicitly out of scope — not silently claimed.

**Current project vs that bar:** Digital MVP demo **engineering-complete** for VCE/Tönnis/CCD + PDF; **not clinically complete**; camera path **not complete**; extended coxometry suite **mostly absent / undefined**.

---

## Appendix A — Per-requirement detail sheets

### R1 — Smartphone camera / négatoscope

| Field | Content |
|-------|---------|
| Status | **B** |
| Current implementation | Option B: guidance → system camera → confirm → same `/analyze` path |
| Files | `mobile/lib/screens/camera_guidance_screen.dart`, `camera_confirm_screen.dart`, `radiograph_picker.dart`, `camera_framing_guide.dart`, `image_normalizer.dart`, `mobile/docs/CAMERA_CAPTURE.md` |
| Validation | Widget/unit tests; **no** physical Android/négatoscope evidence |
| Problems | Domain shift; no perspective/glare restore; guide non-destructive |
| Missing | Device validation; optional rectify; photo QC |
| Landmark deps | Indirect (all measures) |
| Image quality deps | **High** |
| Recommended solution | Execute device checklist; then decide rectify vs photo-domain data; keep warnings |
| Priority | **P0** |

### R2 — Automatic landmark detection

| Field | Content |
|-------|---------|
| Status | **E** |
| Current implementation | V5 Phase 2 16 KP + optional ASL_L refine |
| Files | `v5_phase2_pose.py`, `yolo_pose.py`, `data.yaml`, refinement package |
| Validation | Phase 9B positional audit (engineering) |
| Problems | ASL/FSP/FSD legacy group |
| Missing | Remediation + stronger measure QC |
| Recommended solution | Phase 9C remediation plan; manual edit bridge |
| Priority | **P0** |

### R3 — VCE / Wiberg / CEA

| Field | Content |
|-------|---------|
| Status | **E** |
| Current implementation | `vce_angle` + UI/PDF |
| Files | `mvp_geometry/measurements.py`, `hip_measures.py`, Flutter measurement cards, PDF builder |
| Validation | Unit tests; **no** physician angle study |
| Problems | ASL accuracy dominates error |
| Missing | ASL fix; clinical compare; naming consistency |
| Landmark deps | TD_R, TD_L, FHC, ASL |
| Scale deps | Angles — low (similarity); perspective — high |
| Recommended solution | Fix ASL; flag VCE when ASL QC fails; physician study |
| Priority | **P0** |

### R4 — Tönnis / HTE

| Field | Content |
|-------|---------|
| Status | **E** |
| Same pattern as VCE | Depends on ASL (+ ASM, TD) |
| Priority | **P0** |

### R5 — CCD

| Field | Content |
|-------|---------|
| Status | **E** |
| Files | `ccd_angle` in `measurements.py` |
| Landmark deps | FHC, FNM, FSP, FSD |
| Problems | FSP/FSD bias; femoral rotation A8 |
| Priority | **P0** |

### R6 — Femoral offset

| Field | Content |
|-------|---------|
| Status | **D** |
| Spec | `femoral_offset_spec.md`, `missing_measurements_spec.md` |
| Formula | **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** |
| Landmarks present | FHC, FSP, FSD |
| Missing | Metric, mm/px, code, API, UI, tests |
| Priority | **P2** |

### R7 — Alpha angle

| Field | Content |
|-------|---------|
| Status | **D** |
| Formula / view | **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** |
| Priority | **P3** |

### R8 — Head-neck offset

| Field | Content |
|-------|---------|
| Status | **D** |
| Formula | **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** |
| Priority | **P3** |

### R9 — Cross-over sign

| Field | Content |
|-------|---------|
| Status | **D** |
| Formula | **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** |
| Priority | **P3** |

### R10 — Acetabular index

| Field | Content |
|-------|---------|
| Status | **C** (via Tönnis only) |
| Definition | **DEFINITION / CLINICAL METHOD TO BE CONFIRMED** if ≠ Tönnis |
| Priority | **P2** |

### R11–R14 — FAI / limb length / dysplasia module / THA

| Item | Status | Priority |
|------|:------:|:--------:|
| FAI suite | **D** | P3 |
| Limb length | **D** | P3 |
| Dysplasia support | **B** (angles only) | P1 |
| THA planning | **D** | P3 |

### R15 — Automatic report

| Field | Content |
|-------|---------|
| Status | **A** (for implemented measures) |
| Files | `report_pdf_builder.dart`, `report_export_service.dart`, `landmark_overlay_composer.dart` |
| Validation | PDF tests |
| Missing for “complete” | Extended measures; clinical trust in underlying angles |
| Priority | Keep; extend later |

---

## Appendix B — Evidence index

| Artifact | Role |
|----------|------|
| `phase9b_full_landmark_accuracy_audit.md` | Landmark errors, V2≈V5, MODEL_ACCURACY |
| `phase9b_landmark_errors.csv` | Numeric detail |
| `phase7a_doctor_requirements_audit.md` | Earlier requirements map (superseded where Phase 7B–9B advanced camera/IT) |
| `phase7b_camera_*` | Camera Option B |
| `phase8a_final_pre_demo_audit.md` | Demo readiness |
| `mvp_geometry/measurements.py` | VCE/Tönnis/CCD definitions |
| `missing_measurements_spec.md` | Offset/alpha/bi-ischial open decisions |
| `mobile/docs/CAMERA_CAPTURE.md` | Photo limitations |

---

*End of Phase 10 gap analysis — documentation only; no application code modified.*
