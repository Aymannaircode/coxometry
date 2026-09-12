# Phase 6A — Professional Medical Report / PDF Implementation Plan

**Mode:** READ-ONLY AUDIT + PLAN ONLY  
**Date:** 2026-09-04  
**Scope:** Design the final coxometric analysis report/export.  
**Non-goals this phase:** No source code changes, no dependency installs, no PDF implementation, no model/dataset/backend/geometry/checkpoint/Flutter UX modifications.

**Validated baseline (pre-Phase 6):**
- Flutter: 74 tests passed
- Backend: 167 OK, 1 skipped
- Android debug APK: successful
- V5 demo: `.\backend\run_demo.ps1`
- Smoke: `model_version=v5_phase2`, IT_R / IT_L, QC, measurements, `coordinate_space`

---

## 1. Current export / PDF state

### Verdict

**No report/export/PDF functionality exists** in the shipped application path.

Confirmed by:
- Phase 5 final audit (`phase5_final_system_audit.md`): export/PDF **not present**; workflow ends at Results + “Nouvelle radiographie”
- Phase 5 P1 report: “No export/report feature”
- `mobile/pubspec.yaml`: no `pdf`, `printing`, `share_plus`, `path_provider`, or related packages
- `backend/requirements.txt`: no `reportlab`, WeasyPrint, fpdf, pdfkit, or similar
- Project-wide search of app sources: no Flutter PDF generation, no share/save report flow, no backend PDF endpoint

### Existing adjacent capabilities (not report export)

| Capability | Location | Relevance to PDF |
|---|---|---|
| Local image pick (gallery/camera) | `mobile/lib/services/radiograph_picker.dart` | Source radiograph bytes stay on device |
| EXIF / orientation normalize | `mobile/lib/utils/image_normalizer.dart` | Bytes already orientation-corrected before analyze |
| Image decode (`image` package) | `mobile/pubspec.yaml` → `image: ^4.5.4` | Useful later for raster compositing |
| Landmark overlay painter | `mobile/lib/widgets/landmark_overlay.dart` | Reusable geometry for report image |
| French IT QC labels | `mobile/lib/utils/it_quality_reason_label.dart` | Reuse for report warnings |
| Result presentation status | `mobile/lib/utils/result_status.dart` | Reuse status wording |
| File picker | `file_picker` | Save-as UX possible later; not used for PDF today |

### Current end-user workflow

```
Home → Preview → Analysis (POST /analyze) → Results
                                              └─ only CTA: “Nouvelle radiographie”
```

---

## 2. Existing data available

### 2.1 End-to-end data flow (exact)

```
Radiograph (SelectedRadiograph.bytes / filename / width / height)
    → EXIF bake / normalize (image_normalizer)
    → multipart POST /analyze (api_service)
    → FastAPI validate_upload_metadata
    → preprocessing
         • V2 : preprocess_image 512×512 grayscale letterbox
         • V5 : preprocess_image_v5 640×640 RGB letterbox
    → V5 (or V2) inference (model_factory / detectors)
         • V2 : 14 MVP landmarks
         • V5 : 14 MVP + IT_R (14) + IT_L (15)
    → reprojection to original_image_pixels + coordinate_space
    → IT QC (V5 only: accept / review / unavailable + quality_reasons)
    → mvp_geometry → VCE / Tönnis / CCD (right & left)
    → AnalyzeSuccessResponse JSON
    → AnalysisResult / DetectionInfo / Measurement models (Flutter)
    → ResultsScreen (overlay + measures + IT + technical details)
```

Errors (`status=error`) never reach Results; they stay on AnalysisScreen. A PDF should only be offered for validated `status=ok` results already on Results.

### 2.2 Field inventory (existing only — no invented fields)

#### A. Original image information

| Field | Source | Notes |
|---|---|---|
| `bytes` | `SelectedRadiograph.bytes` | Local only; **not** returned by API |
| `filename` | `SelectedRadiograph.filename` | Local only (picker name / capture name) |
| `width` / `height` | `SelectedRadiograph` and/or `coordinate_space.image_width/height` | Prefer backend `coordinate_space` for overlay |
| `orientationCorrected` | `SelectedRadiograph` | Local metadata |
| `sizeBytes` / `sizeLabel` | Derived from bytes | Local only |

**No patient name, ID, age, sex, Study UID, or clinical identifiers exist** in API or Flutter models.

#### B. Analysis status / version / space

| Field | Backend schema | Flutter model |
|---|---|---|
| `status` | `"ok"` \| `"error"` | `AnalysisResult.status` |
| `model_version` | `"v2"` \| `"v5_phase2"` | `AnalysisResult.modelVersion` (nullable → UI treats as V2) |
| `coordinate_space.image_width/height` | `AnalyzeCoordinateSpaceOut` | `CoordinateSpace` |
| `coordinate_space.preprocessed_width/height` | same | same |
| `coordinate_space.scale`, `pad_x`, `pad_y` | same | same |
| `landmark_coordinate_space` | always `"original_image_pixels"` | `CoordinateSpace.landmarkCoordinateSpace` |
| `error.code` / `error.message` | `AnalyzeErrorDetail` | `AnalysisError` (error path only) |
| `audit` | sanitized `Dict` | `Map<String, dynamic>?` (mostly hidden; expanded technical section uses detection fields, not raw audit dump) |

#### C. Landmarks (MVP 0–13)

From `detection.refined_landmarks` (display path) and `raw_landmarks` (API available, UI uses refined):

| Field | Present |
|---|---|
| `name` | yes |
| `x`, `y` | optional floats (original image pixels) |
| `confidence` | optional |
| `v` / visibility | optional (`0` absent, `1` occulted, `2` visible) |

Flutter `Landmark.isDrawable`: valid finite coords and `visibility != 0`.

#### D. IT_R / IT_L (V5)

| Field | Backend `AnalyzeITLandmarkOut` | Flutter `ITLandmark` |
|---|---|---|
| `name` | `"IT_R"` \| `"IT_L"` | same |
| `kp_index` | 14 / 15 | `kpIndex` |
| `v` | int | `v` |
| `x`, `y` | optional | optional |
| `confidence` | optional | optional |
| `quality` | `accept` \| `review` \| `unavailable` | `ITQuality` |
| `quality_reasons` | list of stable codes | `qualityReasons` |

Drawable rule: `v != 0`, quality ≠ unavailable, valid coordinates.

#### E. IT quality reason codes (existing)

Mapped to French UI strings in `formatItQualityReason`:

| Code | French label (UI) |
|---|---|
| `model_v0` | Repère non identifiable par le modèle |
| `out_of_image_bounds` | Position hors des limites de l'image |
| `midline_unreliable` | Ligne médiane pelvienne peu fiable |
| `wrong_patient_side` | Côté patient incohérent |
| `weak_lateral_placement` | Placement latéral peu marqué |
| `insufficient_caudal_vs_teardrop` | Position trop haute par rapport au teardrop |
| `insufficient_caudal_vs_fhc` | Position trop haute par rapport à la tête fémorale |
| `low_model_confidence` | Confiance du modèle trop basse |
| `high_confidence_marginal_it_fsd` | Confiance élevée mais position IT–diaphyse marginale |
| `bilateral_vertical_asymmetry` | Asymétrie verticale entre IT droit et gauche |
| `bilateral_horizontal_asymmetry` | Asymétrie horizontale entre IT droit et gauche |
| `bilateral_order_violation` | Ordre gauche/droite des IT incohérent |
| *(unknown)* | Contrôle de qualité non satisfait |

#### F. Measurements

Per side (`right` / `left`), each of `vce`, `tonnis`, `ccd`:

| Field | Meaning |
|---|---|
| `value_deg` | degrees if available |
| `available` | bool |
| `reason` | geometry / missing-landmark reason string when unavailable |
| `landmarks_used` | optional list of landmark names |

Display: `Measurement.displayValue` → `"25.0°"` or `"—"`. Unit is degrees (`°`).  
**No normal/abnormal threshold, no dysplasia flag, no clinical class** in API or UI.

#### G. Detection extras (API + collapsed UI)

| Field | Use |
|---|---|
| `bounding_box` | technical only |
| `refinement_enabled` / `refinement_applied` | technical (ASL_L) |
| MVP landmark count | derived |
| IT count | derived |

#### H. Presentation-only derived status (not a new API field)

`ResultPresentationStatus.fromAnalysis` derives:

| Kind | Title (FR) |
|---|---|
| success | Analyse terminée |
| review | Vérification recommandée |
| incomplete | Analyse terminée — informations partielles |

Details list review IT names and/or unavailable IT / missing measures. Safe to reuse in PDF.

#### I. Date / time

**No analysis timestamp field** exists in API or `AnalysisResult`.  
`DateTime.now()` appears only for API latency measurement in `api_service.dart`, not stored on the result.

For the report: either omit date, or use **client generation time** clearly labeled as “Date du rapport” (generation moment), **not** “date d’examen” (which does not exist).

---

## 3. Proposed report structure

Target audiences: surgeon demo, radiologist demo, university jury, academic presentation.  
Tone: concise, medically cautious, French primary.

### Recommended A4 layout

```
┌─────────────────────────────────────────────┐
│ HEADER                                      │
│  Coxométrie                                 │
│  Rapport d'analyse coxométrique             │
│  Date du rapport : <client generation time> │
│  Modèle : V5 Phase 2 | V2                   │
├─────────────────────────────────────────────┤
│ IMAGE                                       │
│  Radiographie + overlay landmarks           │
│  (aspect ratio preserved, BoxFit.contain)   │
│  Légende courte (MVP / IT / à revoir)       │
├─────────────────────────────────────────────┤
│ STATUT                                      │
│  Reuse ResultPresentationStatus title/detail│
├─────────────────────────────────────────────┤
│ MESURES                                     │
│  Hanche droite | Hanche gauche              │
│  VCE / Tönnis / CCD : value + ° + état      │
├─────────────────────────────────────────────┤
│ QUALITÉ DES REPÈRES (si V5 / IT présents)   │
│  IT_R / IT_L : Accepté | À revoir | Indispo.│
│  Motifs FR existants seulement              │
├─────────────────────────────────────────────┤
│ AVERTISSEMENTS (si présents)                │
│  IT review reasons + measure unavailability │
│  Dimension mismatch banner text if present  │
├─────────────────────────────────────────────┤
│ DISCLAIMER                                  │
│  Cautious wording (see §5 / §8)             │
└─────────────────────────────────────────────┘
```

### Section content rules

| Section | Include | Exclude |
|---|---|---|
| Header | App name, report title, model label (`formatModelVersion`), optional generation datetime | Fake patient block, study UID, clinician signature as certification |
| Image | Original radiograph + drawable landmarks (same rules as overlay) | Raw confidence heatmaps, bbox, developer debug marks |
| Measurements | Exact `value_deg` / `available` / `reason` as already shown | Normal ranges, dysplasia labels, treatment advice |
| Landmark / AI quality | Model version; IT quality + French reasons; note unavailable not drawn | YOLO jargon, checkpoint paths, preprocess pad/scale dump |
| Warnings | Existing review / unavailable / missing measure texts only | Invented clinical conclusions |
| Technical appendix | **Optional, off by default** (refinement, coordinate size) | Full `audit` dump, model paths, keypoint confidence tables for all 14 points |

### Patient line

**Do not invent patient data.**  
Identifiers are unavailable in the data model. Recommended approach:

- **Omit** a patient identity block entirely (preferred for privacy and honesty), **or**
- If a jury layout needs a placeholder row: **“Patient : non renseigné”** as a neutral statement of absence — **not** a fabricated identity. This is optional and must not imply a patient record system.

Do **not** put `filename` as a patient name (filenames can contain accidental identifiers).

---

## 4. Proposed image / landmark rendering

### Requirements (non-negotiable)

- Preserve original aspect ratio
- Use **original-image coordinate space** (`original_image_pixels`)
- Do not stretch the radiograph
- Do not change landmark coordinates
- Do not alter measurement calculations
- Prefer `coordinate_space.image_width/height` via existing `resolveOverlayImageSize`

### Safest approach

**Reuse the existing Flutter overlay geometry**, then rasterize for PDF:

1. Resolve image size with `resolveOverlayImageSize` (same as Results).
2. Compute layout with `ImageContainLayout.compute` (uniform scale + letterbox offset).
3. Draw:
   - radiograph bytes (`BoxFit.contain` equivalent)
   - MVP points via `Landmark.isDrawable`
   - IT points via `ITLandmark.isDrawable` (skip unavailable / v=0)
   - Review IT styling already in `LandmarkPainter` (warning ring)
4. Export a PNG/JPEG of that composed canvas at a fixed report width (e.g. ~170 mm printable width at 150–200 DPI), then embed in PDF **without further non-uniform scale**.

### Can `LandmarkPainter` be reused?

**Yes, for geometry and style rules** — with adaptation:

| Approach | Pros | Cons |
|---|---|---|
| **A. Offscreen Flutter canvas** using same `LandmarkPainter` + `ImageContainLayout` | Identical drawable rules; least coordinate risk | Needs widget/test binding or `PictureRecorder` path |
| **B. Pure Dart compositing** with `image` package + reimplemented dots | Easier headless unit tests | Must duplicate painter rules carefully |
| **C. Backend overlay PNG** | Server-side PDF easy | Needs original image upload again; duplicates Flutter coordinate logic; worse offline/demo story |

**Recommendation:** Approach **A** (Flutter-side raster of the validated overlay path), optionally extracting a small shared “compose overlay bitmap” helper used by UI tests and PDF. Do **not** invent a second coordinate pipeline on the backend for Phase 6B.

### What not to draw on the report image

- Landmarks with `v=0` or IT `unavailable`
- Bounding box
- Confidence percentages on every point (clutters; IT confidence already in text section)
- Developer terms (YOLO, imgsz, pad_x)

---

## 5. Clinical content rules (verified)

The current application **presents measurements, not diagnoses** (Phase 5 audit). The report must preserve that.

### Must NOT introduce

- Normal / abnormal classification
- Dysplasia diagnosis
- Treatment recommendations
- Clinical decision support claims
- Medical device certification claims
- Guaranteed accuracy claims
- Angle thresholds unless already present as validated product behavior (**they are not** in API/UI today)

### Allowed

- Numeric angles in degrees when `available == true`
- Em-dash / “indisponible” + existing `reason` when unavailable
- IT QC states Accepté / À revoir / Indisponible + mapped French reasons
- Presentation status titles already used on Results
- Disclaimer that analysis is assisted / non-diagnostic

### Suggested disclaimer (aligned with existing README tone)

Backend README already states: *« Aucune interprétation diagnostique. Aucune certification dispositif médical. Aucune coordonnée anatomique inventée. »*

Proposed report footer (French, cautious):

> Ce document présente des mesures coxométriques assistées par ordinateur (VCE, Tönnis, CCD) à partir de repères anatomiques détectés automatiquement. Il ne constitue pas un diagnostic, ni une décision clinique autonome, ni une certification de dispositif médical. Les résultats doivent être vérifiés par un professionnel de santé compétent. Certaines mesures ou repères peuvent être indisponibles ou soumis à revue.

Do not claim CE/FDA/MDR clearance.

---

## 6. Recommended implementation location

### Options evaluated

| Option | Fit |
|---|---|
| **A) Flutter-side PDF** | Best fit |
| **B) Backend-side PDF** | Weaker for demo/offline and image ownership |
| **C) Hybrid** | Possible later; not needed for first report |

### Recommendation: **A — Flutter-side PDF generation**

**Why:**

1. **Architecture:** Image bytes already live on device; Results already has `SelectedRadiograph` + `AnalysisResult`.
2. **Coordinate correctness:** Overlay / `ImageContainLayout` / `resolveOverlayImageSize` are already validated in Flutter tests.
3. **Offline / demo:** Demo often uses LAN backend; PDF should not require a second round-trip or keep the image server-side.
4. **Privacy:** Radiograph never needs re-upload for export.
5. **Cross-platform:** Same Dart code for Android (primary) and future iOS; Windows desktop demos also benefit.
6. **Maintainability:** One presentation layer for numbers (reuse measurement display + IT labels + status helpers).

**Backend PDF (B) rejected for Phase 6B** because:
- No PDF stack today
- Would need image retention or re-upload
- Risk of diverging overlay from Flutter
- Conflicts with “image stays local” privacy story

**Hybrid (C)** only if a future web client needs server export; out of scope now.

---

## 7. Dependencies already available

### Flutter (`mobile/pubspec.yaml`)

| Package | Version constraint | PDF relevance |
|---|---|---|
| `flutter` SDK | — | Canvas / UI |
| `http` / `http_parser` | existing | Analyze only |
| `file_picker` | ^12.1.2 | Future save dialog / file selection patterns |
| `image_picker` | ^1.1.2 | Capture path only |
| `image` | ^4.5.4 | Decode/encode/composite bitmaps |
| `path` | ^1.9.0 | Path joining |

**Not present:** `pdf`, `printing`, `share_plus`, `path_provider`, `open_filex`, etc.

### Backend (`backend/requirements.txt`)

`fastapi`, `uvicorn`, `pydantic`, `python-multipart`, `httpx`, `Pillow`, `numpy`, `ultralytics` — **no PDF library**.

Pillow could theoretically draw overlays server-side, but is **not recommended** as the Phase 6B path (see §6).

---

## 8. Dependencies that would be required (Phase 6B — do not install now)

For Flutter-side generation + share/save, typical minimal set:

| Package | Role | Notes |
|---|---|---|
| `pdf` | Build A4 PDF document | Widely used; pure Dart |
| `printing` *(optional)* | Preview / system print / PDF share helpers | Convenient preview on mobile |
| `share_plus` | Share sheet (Android/iOS) | Natural “Partager le rapport” |
| `path_provider` | Temporary/app documents directory | Write PDF bytes before share |

Alternatives:
- `pdf` alone + `file_picker` save / platform share — slightly more manual
- Skip `printing` if preview is done by opening the shared PDF in an external viewer

**Do not add backend reportlab** unless product later requires server-side batch export.

No dependency changes in Phase 6A.

---

## 9. Privacy considerations

| Topic | Finding | Report rule |
|---|---|---|
| Patient identifiers | **Absent** from API and Flutter models | Do not invent; omit identity block or “non renseigné” only |
| Radiograph content | Local bytes; may itself contain burned-in PHI | Warn demos to use de-identified images; do not strip pixels in Phase 6B unless separately specified |
| Filename | May leak names | Do **not** print filename as patient ID; optional tiny technical footnote only if needed for demo traceability |
| Audit secrets | Backend already strips `model_path`, checkpoint paths, etc. | Do not dump raw `audit` into PDF |
| Network | MVP uses cleartext LAN HTTP (README warning) | PDF generation should stay on-device |
| Storage | No persistent patient DB | Prefer share/temp file; avoid silent cloud upload |

**Conclusion:** Avoid unnecessary identifiers. The report is a **measurement + quality document**, not a medical record extract.

---

## 10. Cross-platform considerations

| Platform | Status | Report impact |
|---|---|---|
| Android | Primary (debug APK validated) | First target for Generate → Share |
| iOS | `ios/` not versioned; setup docs exist | Design Dart PDF code portable; verify later when iOS project exists |
| Windows desktop | Used for local Flutter demos | PDF generate + save-as useful for jury projection |
| Web | Camera limited; not primary | Out of scope unless requested |

### Share / save workflow (recommended, not implemented)

```
Results screen
  → action “Générer le rapport”
  → compose overlay bitmap (contain, original coords)
  → build A4 PDF in memory
  → optional preview (printing package or temp open)
  → Share sheet (share_plus) and/or Save to Downloads / Files
```

**Permissions / files:**
- Android: sharing via content URI / cache dir typically avoids legacy WRITE_EXTERNAL_STORAGE on modern targets; verify against current `targetSdk`
- iOS: share sheet; no special PDF entitlement; photo library access already for import only
- Prefer writing under app temp/cache then share, rather than requiring broad storage permission

**UI note:** Keep Results usable on small screens — add a secondary button/icon near “Nouvelle radiographie”, not a dense new section that crowds the scroll view.

---

## 11. Report design (A4 visual brief)

**Style:** professional, medical, restrained, readable, white space, clear hierarchy.  
**Avoid:** neon AI aesthetic, purple glow, dense debug tables, emoji, multi-color dashboards.

| Element | Guidance |
|---|---|
| Page | A4 portrait, ≥12–15 mm margins |
| Typography | Clean sans for body; slightly stronger weight for titles; no novelty fonts |
| Color | Near-black text, light gray rules; sparse accent (existing clinical teal/warning tones only for status) |
| Image | Full-width content column, letterboxed if needed, thin border optional |
| Tables | Simple 2-column measure tables (label \| value) |
| Hierarchy | Header → Image → Status → Measures → IT quality → Warnings → Disclaimer |
| Language | French clinical labels already used in UI (`VCE`, `Tönnis`, `CCD`, `Hanche droite/gauche`) |
| Developer terms | Hide YOLO, checkpoint, pad/scale, raw audit keys |

Target length: **1 page** when complete; **spill to page 2** only if many warnings + large image.

---

## 12. Detailed implementation steps (Phase 6B — future)

Ordered for low risk; **do not execute in 6A**.

1. **Confirm freeze** of API schemas and Flutter models (no new clinical fields).
2. **Add dependencies** (`pdf`, and likely `share_plus` + `path_provider`; optionally `printing`) — only when Phase 6B starts.
3. **Extract overlay composition helper**  
   Input: `Uint8List bytes`, `Size imageSize`, MVP + IT lists.  
   Output: raster image with contain layout + same drawable filters as `LandmarkOverlay`.  
   Keep `LandmarkPainter` rules as single source of truth.
4. **Create `ReportData` mapper** from `(SelectedRadiograph, AnalysisResult, DateTime generatedAt)` — maps only existing fields; formats measures with `displayValue`; formats IT reasons via `formatItQualityReason`.
5. **Implement `CoxometricReportPdfBuilder`**  
   Sections per §3; A4; embed composed image; disclaimer footer.
6. **Wire Results UI**  
   “Générer le rapport” → loading → preview/share. Disable if `!result.isOk` or measurements null (should not happen on Results).
7. **V2 path**  
   Omit IT section when `itLandmarks` empty; still show measures + overlay of MVP landmarks; model label V2.
8. **Incomplete / review states**  
   Mirror Results banners; still generate PDF (honest partial report).
9. **Share/save** via temp file + share sheet; Windows: save dialog if needed.
10. **Tests** per §13.
11. **Android build verification**; document iOS follow-up.
12. **Manual demo checklist** with V5 smoke radiograph + one IT review fixture + one V2 response.

**Explicit non-steps:** no model retraining, no QC threshold changes, no measurement formula changes, no new diagnostic fields.

---

## 13. Test plan

### Automated (Flutter)

| Test | Intent |
|---|---|
| PDF generation succeeds | Non-empty bytes / valid PDF header for fixture `v5SuccessJson` |
| Measurements match exactly | PDF text / builder data uses same `value_deg` / `displayValue` as API fixture (e.g. 25.0°, 10.5°, 130.0°) |
| No coordinate regression | Overlay composition uses `ImageContainLayout`; spot-check mapped point equals `layout.toDisplay(x,y)` |
| Aspect ratio preserved | Composed bitmap width/height ratio equals source image ratio within tolerance (letterbox padding allowed outside image) |
| 16 landmarks supported | MVP drawable + IT_R/IT_L drawable when accept/review |
| IT review represented | Quality “À revoir” + French primary reason present |
| IT unavailable represented | Text “Indisponible” + reasons; landmark **not** drawn |
| V2 compatibility | `v2SuccessJson` / empty `it_landmarks` → PDF without IT section; model V2 |
| Missing measurements | `available: false` → “—” + existing `reason` |
| Malformed / incomplete result | Builder refuses or no-ops safely; no crash (guard before navigate already exists) |
| Small-screen Results | Export control does not overflow / block “Nouvelle radiographie” |
| Reason label reuse | Unknown QC code → generic French fallback (existing) |

### Platform

| Check | Intent |
|---|---|
| Android debug/release build | Compiles with new plugins; share sheet opens |
| iOS considerations | Document plugin permissions; run when `ios/` generated |
| Windows desktop (optional demo) | Generate + save PDF for jury |

### Manual / demo

- V5 accept both IT
- V5 one IT review
- V5 one IT unavailable
- Partial measures
- Dimension mismatch banner case (if reproducible)
- Confirm disclaimer present; no diagnostic wording

### Backend

- **No new backend PDF tests required** if Flutter-only approach is chosen.
- Existing analyze contract tests remain the source of truth for field values.

---

## 14. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Duplicate coordinate math drifts from Results overlay | High | Reuse `LandmarkPainter` / `ImageContainLayout` / `resolveOverlayImageSize` |
| PDF looks like AI debug dump | Medium | Strict section allow-list; hide technical expansion by default |
| Accidental clinical over-claim in copy | High | Freeze disclaimer text; ban thresholds/diagnosis strings in review |
| Filename / burned-in PHI leakage | Medium | Omit filename; demo with de-identified images |
| Large radiograph → huge PDF / OOM | Medium | Downscale composed image for print DPI; keep aspect ratio |
| Plugin permission / share failures on Android versions | Medium | Write to cache + share_plus; test on target API level |
| iOS project absent | Low (demo) | Keep code portable; defer iOS CI |
| Treating generation time as exam date | Medium | Label “Date du rapport” only |
| V2 vs V5 layout inconsistency | Low | Conditional IT section |
| Scope creep into backend PDF | Medium | Stick to Flutter-side recommendation |

---

## 15. Acceptance criteria

Phase 6A (this document) is accepted when:

1. Export/PDF absence is documented with evidence from pubspec / requirements / UI.
2. Existing data fields are inventoried **without inventing** patient or clinical fields.
3. Results UI displayed vs hidden vs PDF-useful content is identified.
4. Report structure, clinical rules, privacy, and design brief are defined.
5. Flutter-side implementation is recommended with rationale.
6. Dependencies current vs future are listed (none installed).
7. Implementation steps and tests are specified for Phase 6B.
8. **No source, dependency, model, or UX code was modified** in Phase 6A.

Phase 6B (future implementation) will be accepted when:

1. User can generate a PDF from Results for a successful analysis.
2. Measurement values in the PDF match the on-screen / API values exactly.
3. Overlay image preserves aspect ratio and original-image landmark coordinates.
4. V5 IT accept / review / unavailable states are represented honestly.
5. V2 results produce a valid report without IT section.
6. Unavailable measures show “—” (or equivalent) with existing reasons — never fabricated angles.
7. Disclaimer present; no diagnosis / treatment / certification claims.
8. No patient identity invented.
9. Share or save works on Android demo path; small-screen Results remains usable.
10. Automated tests cover generation, V2/V5, IT states, and measurement fidelity.
11. Existing analyze / measurement / QC behavior unchanged.

---

## Appendix A — Flutter Results: displayed vs hidden vs PDF-useful

| Content | On Results today | Useful in PDF? | Notes |
|---|---|---|---|
| Radiograph + landmark overlay | Yes | **Yes** | Core visual |
| Landmark legend | Yes | Yes (short) | |
| Model version label | Yes | **Yes** | |
| Status banner (success/review/incomplete) | Yes | **Yes** | |
| VCE / Tönnis / CCD both sides | Yes | **Yes** | |
| Unavailable measure reasons | Yes | **Yes** | |
| IT quality + reasons | Yes (if IT present) | **Yes** | |
| Dimension mismatch banner | Conditional | Optional | Honesty if present |
| Detection technical expansion (bbox, refinement, px size) | Collapsed | **Default no** | Optional appendix |
| `raw_landmarks` | Available in model, not primary UI | No | Prefer refined |
| Per-landmark confidence (all MVP) | In model; not listed on cards | No (clutter) | IT confidence already shown for IT cards |
| `audit` map | Parsed, not fully shown | No | Sanitized but still technical |
| API errors | Not on Results | N/A | No PDF |
| Patient ID | N/A | No | Does not exist |
| Date/time of exam | N/A | Generation time only | Label carefully |

---

## Appendix B — Key file map

| Concern | Path |
|---|---|
| API success schema | `backend/app/schemas/analyze.py` |
| Analyze orchestration | `backend/app/services/analyze.py` |
| IT QC | `backend/app/services/detection/v5_it_qc.py` |
| Flutter result model | `mobile/lib/models/analysis_result.dart` |
| Landmark / IT / measure / space | `mobile/lib/models/*.dart` |
| Results UI | `mobile/lib/screens/results_screen.dart` |
| Overlay painter | `mobile/lib/widgets/landmark_overlay.dart` |
| Contain layout | `mobile/lib/widgets/image_contain_layout.dart` |
| Overlay size resolve | `mobile/lib/utils/overlay_image_size.dart` |
| IT reason FR | `mobile/lib/utils/it_quality_reason_label.dart` |
| Status presentation | `mobile/lib/utils/result_status.dart` |
| Local image | `mobile/lib/services/radiograph_picker.dart` |
| Fixtures | `mobile/test/fixtures/analysis_fixtures.dart` |

---

## Appendix C — Phase decision

| Item | Decision |
|---|---|
| Phase 6A deliverable | This plan only |
| Implementation | Deferred to Phase 6B |
| Location | Flutter-side PDF |
| Patient block | Omit (preferred) or “non renseigné” |
| Thresholds / diagnosis | Forbidden |
| Overlay reuse | Required for coordinate safety |
| New deps | Documented only; **not installed** |

---

**PHASE6A_PDF_PLAN_COMPLETE** — read-only audit finished; ready for Phase 6B implementation when authorized.
