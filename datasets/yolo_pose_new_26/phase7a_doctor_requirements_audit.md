# Phase 7A — Doctor Requirements Compliance Audit

**Date:** 2026-09-04  
**Mode:** READ-ONLY — no source, model, dataset, checkpoint, geometry, Flutter, backend, or dependency modifications except this report  
**Evidence basis:** Actual application source (`mobile/`, `backend/`, `mvp_geometry/`), dataset metadata (`datasets/yolo_pose_new_26/`), and prior phase reports cited only when cross-checked against code  
**Prior state cited:** Phase 5 system audit · Phase 6A PDF implementation  

---

## 1. Original doctor objective

**Core objective (verbatim intent):**

> Développer une application que le médecin peut utiliser sur son téléphone et prendre avec sa caméra une photo de la radiographie du bassin sur le négatoscope, puis avoir automatiquement les angles.

**Interpreted MVP requirements from that statement:**

| Element | Meaning |
|---------|---------|
| Mobile phone app | Doctor-facing Android (primary) workflow |
| Phone camera | Capture a **photograph** of a pelvic radiograph displayed on a **négatoscope** |
| Automatic angles | Auto landmark detection → coxometry angles without manual tracing |
| Digital pelvic radiographs | Also referenced in the broader brief (import of existing images) |

**Broader brief (referenced commercial / research tools):** mediCAD, TraumaCad, Surgimap, EOSviewer, ImageJ, Horos, RadiAnt, AI imaging solutions — used here only to separate **CORE MVP** from **EXTENDED / FUTURE** scope.

**Core parameters explicitly named:** VCE / Wiberg / CEA · Tönnis / HTE · CCD  

**Additional parameters mentioned:** femoral offset · alpha angle · head-neck offset · cross-over sign · acetabular index · FAI-related parameters · lower-limb length  

**Other capabilities mentioned:** auto/semi-auto landmarks · automatic measurement · automatic report · PACS / clinical imaging workflow compatibility  

---

## 2. Current implementation summary

### 2.1 End-to-end pipeline (code-verified)

```
HomeScreen
  ├─ Gallery: FilePicker → JPG/JPEG/PNG
  └─ Camera:  ImagePicker(ImageSource.camera) → photo bytes
       ↓
  normalizeRadiographBytes (EXIF bake only)
       ↓
  PreviewScreen → AnalysisScreen
       ↓
  ApiService POST /analyze (multipart field `file`, ≤ 25 Mo, PNG/JPG/JPEG)
       ↓
  Backend analyze:
    validate upload → preprocess (V2: 512² gray | V5: 640² RGB letterbox)
    → landmark detection (V2 14 KP | V5 Phase 2: 14 KP + IT_R/IT_L)
    → IT QC (V5 only: accept / review / unavailable)
    → mvp_geometry: VCE, Tönnis, CCD (R/L)
    → landmarks reprojected to original_image_pixels
       ↓
  ResultsScreen: overlay + zoom/pan + measures + IT status + model label
       ↓
  ReportExportService: PDF (image+overlay, measures, QC, disclaimer) → share
```

### 2.2 What is actually implemented

| Layer | Implemented today | Evidence |
|-------|-------------------|----------|
| Mobile Android app | Flutter `coxometrie` MVP | `mobile/pubspec.yaml`, `mobile/lib/` |
| Gallery import | JPG/JPEG/PNG via `file_picker` | `radiograph_picker.dart` |
| Camera capture API | `ImageSource.camera`, rear camera, quality 100 | `radiograph_picker.dart` `pickFromCamera` |
| Camera permission | `CAMERA` in AndroidManifest | `mobile/android/app/src/main/AndroidManifest.xml` |
| EXIF orientation | Bake pixels before upload | `image_normalizer.dart` |
| AI landmarks | V2 14 KP; V5 + IT_R(14)/IT_L(15) | detectors + `data.yaml` |
| Core angles | VCE, Tönnis, CCD bilaterally | `mvp_geometry/hip_measures.py` |
| QC | IT quality states (V5) | `v5_it_qc.py`, Flutter IT section |
| Results UX | Overlay, InteractiveViewer zoom/pan, REVIEW banner | `results_screen.dart`, `landmark_overlay.dart` |
| Automatic PDF report | A4 PDF + share | Phase 6A report modules under `mobile/lib/services/report/` |
| Formats | PNG/JPG/JPEG only | `analyze.py` `ALLOWED_EXTENSIONS` |

### 2.3 What is not implemented (high level)

- Négatoscope-specific capture guidance / framing / validation  
- Perspective / keystone correction for phone photos  
- Lighting / glare / background / film-edge handling for photographed radiographs  
- Femoral offset, alpha, head-neck offset, cross-over, separate acetabular index, FAI suite, limb lengths  
- DICOM import/export, PACS connection  
- Automatic diagnosis or clinical thresholding  
- Evidence of on-device validation that camera→négatoscope photos produce reliable angles (APK build ≠ workflow validation)

### 2.4 Training / inference domain note (relevant to camera)

Dataset `new_26` images are derived from **digital DICOM** sources (`meta/source_mapping.csv` → `bassin\a_annoter\…`), rendered to PNG for training/eval. There is **no** phone-photograph / négatoscope training domain in the current dataset metadata. Inference preprocessing is generic letterbox resize — not photo-radiograph restoration.

---

## 3. Complete requirement matrix

| Requirement | Status | Evidence / file | Priority | Gap | Recommendation |
|-------------|--------|-----------------|----------|-----|----------------|
| Mobile app for physician | ✅ IMPLEMENTED | `mobile/` Flutter Android | P0 | iOS not versioned | Keep Android as demo path |
| Phone camera open + capture | 🟡 PARTIALLY IMPLEMENTED | `radiograph_picker.dart` `pickFromCamera`; Home button « Prendre une photo » | P0 | Wired, but not a validated négatoscope workflow | Phase 7B camera workflow |
| Photo of radiograph on négatoscope | 🔴 NOT IMPLEMENTED | No négatoscope UX, crop, deskew, or validation code | P0 | Domain gap vs doctor wording | Phase 7B |
| Feed image into analysis pipeline | ✅ IMPLEMENTED | Preview → `/analyze` (gallery **and** camera bytes share path) | P0 | Same pipeline for any JPG/PNG | Keep |
| Automatic landmark detection | ✅ IMPLEMENTED | V2/V5 detectors via `POST /analyze` | P0 | Trained on digital XR, not phone photos | Validate on photo domain later |
| VCE / Wiberg / CEA | ✅ IMPLEMENTED | `measurements.py` `vce_angle`; `hip_measures.py` | P0 | — | Keep |
| Tönnis / HTE | ✅ IMPLEMENTED | `tonnis_angle`; UI/PDF « Tönnis » | P0 | — | Keep |
| CCD | ✅ IMPLEMENTED | `ccd_angle` | P0 | — | Keep |
| Femoral offset | 🔴 NOT IMPLEMENTED | No function/API field | P2 | Landmarks FHC+FSP+FSD exist; no formula | Future if requested |
| Alpha angle | 🔴 NOT IMPLEMENTED | No landmarks / geometry | P2–P3 | Missing alpha-point / contour | Future |
| Head-neck offset | 🔴 NOT IMPLEMENTED | No dedicated measure | P2–P3 | Classic points not in 16-KP set | Future |
| Cross-over sign | 🔴 NOT IMPLEMENTED | No wall landmarks / sign logic | P3 | Qualitative acetabular walls absent | Future |
| Acetabular index (separate) | 🟡 PARTIALLY IMPLEMENTED | Tönnis/HTE present; no separate « index acétabulaire » output | P2 | Naming/product gap vs Tonnis | Clarify with doctor; do not invent |
| FAI parameter suite | 🔴 NOT IMPLEMENTED | — | P3 | Depends on alpha/crossover/etc. | Future |
| Lower-limb length | 🔴 NOT IMPLEMENTED | No ankle/knee landmarks; FOV is pelvis | P3 | Out of current image domain | Future |
| Automatic measurements | ✅ IMPLEMENTED | Geometry after detection | P0 | Unavailable → `available=false` | Keep |
| Automatic report / PDF | ✅ IMPLEMENTED | `report_pdf_builder.dart`, Results export | P1 | No in-app PDF viewer | Keep / minor polish later |
| Gallery / digital image import | ✅ IMPLEMENTED | FilePicker JPG/PNG | P0 | Distinct from camera B | Keep as fallback |
| PACS connection | 🔴 NOT IMPLEMENTED | No PACS client | P3 | — | Out of MVP |
| DICOM import | 🔴 NOT IMPLEMENTED | API rejects non PNG/JPG; README | P2–P3 | Offline DICOM→PNG only in **tests** | Out of MVP |
| DICOM metadata / export | 🔴 NOT IMPLEMENTED | — | P3 | — | Out of MVP |
| Semi-automatic landmark edit | 🔴 NOT IMPLEMENTED | Display only; no drag-edit | P1–P2 | Useful for REVIEW cases | Future after camera |
| Clinical diagnosis | ⚪ NOT APPLICABLE / FUTURE SCOPE | Explicitly avoided | — | Correct for safety | Do not add |
| mediCAD-class full suite | ⚪ NOT APPLICABLE / FUTURE SCOPE | Far beyond MVP | — | Scope control | Do not chase |

---

## 4. Camera requirement analysis

**Priority:** HIGH (central to the doctor’s original wording).

### 4.1 Checklist

| # | Capability | Verdict | Evidence |
|---|------------|---------|----------|
| 1 | Open phone camera | 🟡 Code present | `ImagePicker.pickImage(source: ImageSource.camera)` |
| 2 | Capture a photograph | 🟡 Code present | Same; returns bytes → normalize |
| 3 | Acquire négatoscope radiograph photo | 🔴 Not productized | No guidance, framing aids, film crop, or demo validation artifacts |
| 4 | Send image into analysis pipeline | ✅ Yes | Camera and gallery both → `PreviewScreen` → `/analyze` |
| 5 | Preprocessing for photographed radiograph | 🔴 No | Only EXIF bake (`image_normalizer.dart`) + generic letterbox (`preprocessing*.py`) |
| 6 | Perspective correction if needed | 🔴 No | No homography / deskew / corner detection in app or backend |
| 7 | Lighting / reflection / background handling | 🔴 No | No glare mask, contrast normalize for ambient light, BG removal |
| 8 | Preserve anatomical geometry for measurement | ⚪ Unknown / unvalidated | Model trained on digital DICOM-rendered PNG; phone photo fidelity not evidenced |

### 4.2 Critical distinction

| Path | Status |
|------|--------|
| **A) Selecting an existing digital image** | ✅ Implemented and aligned with training domain |
| **B) Taking a photograph with the phone camera** | 🟡 Entry point exists; **does not** satisfy the doctor’s négatoscope photograph requirement by itself |

**Gallery import must not be counted as satisfying camera capture.**

### 4.3 Validation gap

- Unit/widget tests stub or avoid real camera (`phase4b_ux_test.dart` mock `pickFromCamera → null`).  
- Phase 5/6A success criteria include APK build and Flutter/backend tests — **not** on-device négatoscope capture trials.  
- **APK builds successfully ≠ camera workflow validated.**

### 4.4 Camera status summary

**🟡 PARTIALLY IMPLEMENTED** at the OS integration layer; **🔴 NOT IMPLEMENTED** as a clinically credible négatoscope photograph workflow.

---

## 5. Coxometry parameter matrix

| Parameter | Calculated? | Required landmarks (clinical / geometric) | Landmarks exist in V5 set? | Geometry support today? | Status |
|-----------|-------------|---------------------------------------------|----------------------------|-------------------------|--------|
| **VCE / Wiberg / CEA** | Yes | TD_R, TD_L, FHC_{side}, ASL_{side} | Yes (0–5) | `vce_angle` | ✅ IMPLEMENTED |
| **Tönnis / HTE** | Yes | TD_R, TD_L, ASM_{side}, ASL_{side} | Yes | `tonnis_angle` | ✅ IMPLEMENTED |
| **CCD** | Yes | FHC, FNM, FSP, FSD ({side}) | Yes (8–13) | `ccd_angle` | ✅ IMPLEMENTED |
| **Femoral offset** | No | Typically FHC + femoral shaft axis (FSP–FSD) | Yes (partial: FHC, FSP, FSD) | No dedicated function | 🔴 NOT IMPLEMENTED |
| **Alpha angle** | No | Head center + α point on head–neck contour (often Dunn/frog) | No α-point | No | 🔴 NOT IMPLEMENTED |
| **Head-neck offset** | No | Head center + anterior neck cortex / junction points | Incomplete (FNM ≠ classic offset points) | No | 🔴 NOT IMPLEMENTED |
| **Cross-over sign** | No | Anterior + posterior acetabular wall silhouettes | No | No | 🔴 NOT IMPLEMENTED |
| **Acetabular index** | No separate output | Often pediatric AI or adult HTE-related | ASL/ASM/TD exist for Tonnis | Tonnis only | 🟡 PARTIAL (via Tönnis only) |
| **FAI parameters** | No | Alpha, crossover, etc. | Insufficient | No | 🔴 NOT IMPLEMENTED |
| **Lower-limb length** | No | Proximal + distal limb landmarks (outside pelvic FOV) | No | No | 🔴 NOT IMPLEMENTED |

**IT_R / IT_L:** Detected and QC’d in V5; **not** inputs to VCE / Tönnis / CCD (`hip_measures.py` `_REQUIRED` excludes IT). Used for reliability presentation / overlay / PDF QC, not angle computation.

**Unavailable landmarks:** Geometry returns `available=false` + reason; UI/PDF show « Non disponible » — no invented coordinates.

---

## 6. Landmark coverage matrix

**Current validated V5 model:** 16 landmarks (`data.yaml` / `meta/keypoint_order.md`).  
**IT_R = keypoint 14 · IT_L = keypoint 15.**

| Measurement | Required landmarks | Currently available | Missing landmarks |
|-------------|--------------------|---------------------|-------------------|
| VCE / Wiberg | TD_R, TD_L, FHC_{side}, ASL_{side} | All | — |
| Tönnis / HTE | TD_R, TD_L, ASM_{side}, ASL_{side} | All | — |
| CCD | FHC_{side}, FNM_{side}, FSP_{side}, FSD_{side} | All | — |
| Femoral offset (if defined as FHC⊥shaft) | FHC_{side}, FSP_{side}, FSD_{side} | All three present | Formula/API only (not landmarks) |
| Alpha angle | FHC_{side} + alpha contour point(s) | FHC only | Alpha / head–neck junction contour points (not in set) |
| Head-neck offset | Head center + neck cortical / junction refs | FHC, FNM only (insufficient for classic offset) | Dedicated head–neck offset points |
| Cross-over sign | Anterior & posterior acetabular walls | None | Wall landmarks / curves |
| Acetabular index (if ≠ Tonnis) | Depends on definition | ASL/ASM/TD support Tonnis | Any extra AI-specific points if doctor requires distinct measure |
| FAI suite | Union of alpha / crossover / related | Insufficient | Multiple missing |
| Lower-limb length | Extra-pelvic landmarks | None in 16-KP pelvis set | Distal tibial / ankle / etc. |
| IT QC / display | IT_R, IT_L (+ TD/FHC/FSD for QC rules) | Present in V5 | — (V2: IT empty by design) |

**Do not invent landmark names:** Only the 16 names above exist in the validated schema.

---

## 7. Automatic report assessment

| Feature | Present? | Evidence |
|---------|----------|----------|
| Automatic report generation | ✅ | Results → « Exporter le rapport » |
| PDF | ✅ | `package:pdf` via `ReportPdfBuilder` |
| Measurements | ✅ | VCE / Tönnis / CCD D+G |
| Image | ✅ | Radiograph embedded |
| Landmark overlay | ✅ | `LandmarkOverlayComposer` reuses painter layout |
| QC information | ✅ | IT Accepté / À revoir / Indisponible + warnings |
| Review status | ✅ | `ResultPresentationStatus` mirrored in PDF |
| V2 / V5 model information | ✅ | `formatModelVersion` → « Modèle : … » |
| Disclaimer / non-diagnosis | ✅ | Explicit PDF disclaimer string |

**Does this satisfy the doctor’s “automatic report” requirement for MVP?**  
**Yes, for the current measurement scope** (angles + image + QC + model + caution). It is not a mediCAD-style operative planning report.

---

## 8. Mobile assessment

### 8.1 Android functionality (excluding camera depth)

| Feature | Status | Evidence |
|---------|--------|----------|
| Image import (gallery/files) | ✅ | `pickFromGallery` |
| Analysis | ✅ | `ApiService.analyzeRadiograph` → `/analyze` |
| Results | ✅ | `ResultsScreen` |
| Zoom / pan | ✅ | `InteractiveViewer` on overlay |
| PDF export | ✅ | `ReportExportService` |
| Share | ✅ | `share_plus` |
| V5 model | ✅ | Parses `model_version`, IT landmarks, QC |
| IT QC UI | ✅ | `it_status_section.dart`, REVIEW banner |

### 8.2 Camera functionality (separate)

| Feature | Status |
|---------|--------|
| UI button + `ImageSource.camera` | 🟡 Present |
| Android `CAMERA` permission | ✅ Declared |
| Négatoscope photograph workflow | 🔴 Absent |
| Device validation of photo→angles | 🔴 Not evidenced |
| Photo-specific preprocessing | 🔴 Absent |

**Verdict:** Mobile digital workflow is demo-capable. Camera remains the **main open gap** relative to the original objective.

---

## 9. PACS / DICOM assessment

| Capability | Status | Evidence |
|------------|--------|----------|
| DICOM import in app/API | 🔴 NOT IMPLEMENTED | `ALLOWED_EXTENSIONS = {png,jpg,jpeg}`; backend README « pas de DICOM » |
| DICOM metadata in product path | 🔴 NOT IMPLEMENTED | Analyze schemas expose image geometry, not DICOM tags |
| PACS connection | 🔴 NOT IMPLEMENTED | No DICOM network / C-STORE / Q/R client |
| DICOM export | 🔴 NOT IMPLEMENTED | PDF share only |

**Note:** Test helpers may render DICOM→PNG for regression (`dicom_render` in backend tests). That is **lab infrastructure**, not product PACS compatibility.

---

## 10. Core MVP vs future scope

### CORE MVP (aligned with doctor wording + current product)

1. Phone-usable application (Android)  
2. Acquire pelvic radiograph image (digital import **and** intended camera photo of négatoscope)  
3. Automatic landmark detection  
4. Automatic **VCE, Tönnis, CCD**  
5. Display results with caution / REVIEW  
6. Automatic report (PDF) for those measures  

### EXTENDED / FUTURE SCOPE (mentioned tools / extras — not required to claim MVP)

- Femoral offset, alpha, head-neck offset, crossover, FAI suite, limb length  
- Full PACS / DICOM workflow parity with Horos / RadiAnt / mediCAD  
- Planning / templating / 3D EOS-class features  
- Semi-automatic landmark editing, multi-user EMR integration, device certification  

**Scope discipline:** Do not expand toward mediCAD/TraumaCad/EOS feature parity for the next phase. Close the **camera + négatoscope photograph** gap first.

---

## 11. Clinical safety assessment

| Behavior | Observed? | Evidence |
|----------|-----------|----------|
| Reports measurements (degrees / unavailable) | ✅ | API + UI + PDF |
| Communicates REVIEW | ✅ | IT `review` → « Vérification recommandée »; PDF QC |
| Handles unavailable landmarks | ✅ | `available=false`, no fabricated coords; IT `v=0` not drawn |
| Avoids automatic diagnosis | ✅ | No dysplasia/normal labels in UI/PDF |
| Avoids unsupported clinical conclusions | ✅ | Disclaimer; README « Pas de seuils cliniques » |
| Device certification claim | ✅ Avoided | PDF: « Aucune certification de dispositif médical n'est revendiquée » |

**Conclusion:** The application remains appropriately cautious for a research/prototype assisted-measurement tool. Do not add diagnostic interpretation.

---

## 12. P0 / P1 / P2 / P3 priorities

Classification of **missing or incomplete** items relative to the doctor’s original objective:

### P0 — must exist before calling this a solution to the original objective

1. **Camera capture of négatoscope radiograph as a real, demoable workflow** (not merely `ImageSource.camera` plumbing)  
2. Path from that photograph into analysis with **honest handling** of geometry risk (at minimum: capture guidance + known limitations; ideally basic perspective/crop aids)  
3. Core angles already exist — **retain** VCE / Tönnis / CCD as P0 delivered  

### P1 — important for a convincing prototype / demo

1. On-device validation set: phone photos of négatoscope vs digital ground truth (process/validation, not model retrain in this audit)  
2. Capture UX: framing hints, confirm sharpness, reject useless frames  
3. Semi-automatic landmark correction for REVIEW cases (optional but strong for demo trust)  

### P2 — useful extension

1. Femoral offset (landmarks largely present)  
2. Clarify acetabular index vs Tönnis with the doctor  
3. Optional DICOM file→PNG import (still not PACS)  

### P3 — future / optional

1. Alpha, head-neck offset, crossover, FAI suite  
2. Lower-limb length  
3. PACS connectivity / DICOM export  
4. mediCAD-class planning  

**Attention ranking (as requested):**  
1. Camera capture — **P0 gap**  
2. Core coxometry — **delivered**  
3. Automatic landmark detection — **delivered** (digital domain)  
4. Automatic report — **delivered**  
5. Mobile workflow — **delivered** for digital; camera incomplete  

---

## 13. Scope decision

### Decision: **B) Current application satisfies the core objective but needs camera workflow**

**Why B (not A):**  
The doctor’s objective explicitly requires photographing a radiograph **on a négatoscope with the phone camera**. That workflow is not complete or validated. Declaring A would be overly optimistic.

**Why B (not C):**  
The three core named angles (VCE, Tönnis, CCD) **are** implemented with matching landmarks. Missing extras (offset, alpha, FAI, limb length) are **extended** scope, not blockers for the stated core angles.

**Why B (not D):**  
On the digital-import path, the product already delivers: mobile use → automatic landmarks → automatic angles → results → PDF report, with clinical caution. The **primary** remaining blocker to matching the original wording is the **camera / négatoscope photograph workflow**, not absence of the whole solution.

**Strict caveat:** If stakeholders treat “reliable angles from a négatoscope phone photo” as binary and refuse any digital-import substitute, operational readiness is closer to **incomplete** until Phase 7B is done. Status remains **B** because the measurement/AI/report core exists and camera is the named gap.

---

## 14. Recommended next phase

# **PHASE 7B — CAMERA CAPTURE + RADIOGRAPH PHOTOGRAPH WORKFLOW**

**Do not implement in this audit.** Recommended focus only:

1. Treat camera as a first-class clinical acquisition path (not a secondary button).  
2. Négatoscope photograph UX: framing, orientation, distance, glare awareness.  
3. Minimal geometric safeguards appropriate for phone photos (e.g. crop-to-film / perspective assist) — design only in 7B planning; implement later as agreed.  
4. Feed corrected/captured image into the **existing** `/analyze` pipeline without changing model weights or coxometry formulas unless a separate validated need appears.  
5. On-device demo protocol: digital import vs phone photo of same film; document failure modes honestly.  
6. Explicitly **exclude** from 7B: new coxometry parameters, PACS/DICOM productization, model retrain, diagnosis features.

**Rationale:** Camera/négatoscope is the P0 gap against the doctor’s original sentence. Core angles, landmarks, QC, mobile results, and PDF already exist for the digital path.

---

## Appendix A — Key evidence index

| Topic | Path |
|-------|------|
| Camera / gallery picker | `mobile/lib/services/radiograph_picker.dart` |
| Home CTAs | `mobile/lib/screens/home_screen.dart` |
| EXIF normalize | `mobile/lib/utils/image_normalizer.dart` |
| Android CAMERA permission | `mobile/android/app/src/main/AndroidManifest.xml` |
| Analyze API limits | `backend/app/services/analyze.py` |
| Preprocess V2/V5 | `backend/app/services/preprocessing.py`, `preprocessing_v5.py` |
| Geometry measures | `mvp_geometry/hip_measures.py`, `measurements.py` |
| Landmark names | `mvp_geometry/landmarks.py`, `datasets/yolo_pose_new_26/data.yaml` |
| IT QC | `backend/app/services/detection/v5_it_qc.py` |
| PDF report | `mobile/lib/services/report/*` |
| Safety disclaimer | `report_pdf_builder.dart` `disclaimer` |
| DICOM absence | `backend/README.md` Limites |
| Dataset DICOM sources | `datasets/yolo_pose_new_26/meta/source_mapping.csv` |
| Phase 6A PDF complete | `datasets/yolo_pose_new_26/phase6a_pdf_implementation_report.md` |

---

## Appendix B — Status legend (as required)

| Symbol | Meaning |
|--------|---------|
| ✅ IMPLEMENTED | Present in source and usable on the intended path |
| 🟡 PARTIALLY IMPLEMENTED | Some code/UX exists; does not fully meet the requirement |
| 🔴 NOT IMPLEMENTED | Absent from product path |
| ⚪ NOT APPLICABLE / FUTURE SCOPE | Out of MVP or intentionally excluded |

---

**PHASE7A_AUDIT_COMPLETE — READ-ONLY — NO IMPLEMENTATION PERFORMED**
