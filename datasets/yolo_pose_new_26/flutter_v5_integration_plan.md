# Flutter V5 Integration Plan

**Phase:** 2B-0 — read-only inspection  
**Date:** 2026-09-02  
**Backend status:** `BACKEND_V5_PHASE2_INTEGRATION_READY`, `V5_IT_QC_READY` (167 tests OK, 1 skipped)  
**Scope:** Plan only — no Flutter or backend modifications in this phase.

---

## Current Flutter architecture

### Project layout (`mobile/`)

| Area | Path | Role |
|------|------|------|
| Entry point | `lib/main.dart` | `WidgetsFlutterBinding.ensureInitialized()` → `runApp(CoxometrieApp())` |
| App shell | `lib/app.dart` | `MaterialApp` with `AppTheme.light`, home = `HomeScreen` |
| Config | `lib/config/api_config.dart` | Base URL resolution (`API_BASE_URL` dart-define, platform defaults) |
| Services | `lib/services/api_service.dart`, `lib/services/radiograph_picker.dart` | HTTP client, image pick/normalize |
| Models | `lib/models/analysis_result.dart`, `landmark.dart`, `measurement.dart` | JSON parsing |
| Screens | `lib/screens/*.dart` | 5 screens (see below) |
| Widgets | `lib/widgets/*.dart` | Overlay, measurements, loading, image views |
| Utils | `lib/utils/image_size.dart`, `image_normalizer.dart` | Decode dimensions, EXIF bake |
| Theme | `lib/theme/app_theme.dart`, `app_colors.dart`, `app_spacing.dart` | Material 3 clinical design system |
| Tests | `test/*.dart` | 4 test files (see Tests section) |

### Dependencies (`pubspec.yaml`)

- `http`, `http_parser` — API calls
- `file_picker`, `image_picker` — gallery/camera import
- `image` — EXIF orientation normalization
- `path` — filename/extension handling

### Navigation pattern

Imperative `Navigator` only (no `go_router` / named routes):

```
HomeScreen
  → PreviewScreen          (push)
    → AnalysisScreen       (pushReplacement)
      → ResultsScreen      (pushReplacement on success)
HomeScreen / ResultsScreen
  → ServerConnectionScreen (push, optional debug)
ResultsScreen
  → HomeScreen             (popUntil first route)
```

### Loading and error handling

| Stage | Component | Behavior |
|-------|-----------|----------|
| Pick | `HomeScreen` | `_busy` flag, `_ErrorBanner` on picker failure |
| Analysis | `AnalysisScreen` | `PopScope(canPop: !_analyzing)`, `LoadingAnalysis`, `_ErrorView` with retry/back |
| API | `ApiService` | Typed `ApiException` + `ApiExceptionKind` (network, timeout, client/server, analysis error, etc.) |
| Results | `ResultsScreen` | Success banner only (no error path — errors stay on `AnalysisScreen`) |

---

## Current API client

### `ApiConfig` (`lib/config/api_config.dart`)

| Setting | Value |
|---------|-------|
| Env override | `--dart-define=API_BASE_URL=http://…` (highest priority) |
| Default port | `8001` |
| Endpoints | `$baseUrl/analyze`, `$baseUrl/health` |
| Android emulator default | `http://10.0.2.2:8001` |
| iOS simulator / desktop / web default | `http://127.0.0.1:8001` |
| Source label | `ApiConfig.sourceLabel` for debug UI |

### `ApiService` (`lib/services/api_service.dart`)

| Method | Endpoint | Timeout | Notes |
|--------|----------|---------|-------|
| `checkHealth()` | `GET /health` | 15 s | Parses `status`, `service`, `version` |
| `analyzeRadiograph()` | `POST /analyze` | 120 s | Multipart field **`file`**, PNG/JPG/JPEG |

Client-side limits aligned with backend:

- Max upload: **25 MiB** (`maxUploadBytes`)
- Empty file rejected before network call

Error handling layers:

1. Transport: `SocketException`, `TimeoutException`, `HttpException` → `ApiExceptionKind.network` / `timeout`
2. HTTP status: 422 → `clientError`; 4xx → `clientError`; 5xx → `serverError`
3. JSON body `status: "error"` → `ApiExceptionKind.analysisError` (throws even on HTTP 200)
4. Invalid JSON → `invalidJson`

### Platform connectivity (inspected, not modified)

| Environment | URL behavior | Notes |
|-------------|--------------|-------|
| Desktop / web dev | `127.0.0.1:8001` | Matches README `uvicorn --host 127.0.0.1` |
| Android emulator | `10.0.2.2:8001` | Host loopback alias |
| Physical Android | **Requires** `--dart-define=API_BASE_URL=http://<PC-IP>:8001` | Warning banner on `HomeScreen` when dart-define absent |
| Cleartext HTTP | Allowed | `android/.../network_security_config.xml` + manifest cleartext |
| Backend on device network | PC must use `--host 0.0.0.0` | Documented in `mobile/docs/TEST_MOBILE_E2E.md` |

`ServerConnectionScreen` provides manual `GET /health` diagnostic without uploading images.

---

## Current response models

### Actual FastAPI contract (`backend/app/schemas/analyze.py`)

#### Request — `POST /analyze`

```
Content-Type: multipart/form-data
Field: file  (alias image also accepted by backend; Flutter sends file only)
Formats: PNG, JPG, JPEG
Max size: 25 MiB
```

No JSON body. Model version is **server-side** (`MODEL_VERSION` env, default `v2`); the Flutter client does not select v2 vs v5.

#### Success — `status: "ok"`

```json
{
  "status": "ok",
  "model_version": "v2" | "v5_phase2",
  "detection": {
    "bounding_box": { "x1": float, "y1": float, "x2": float, "y2": float } | null,
    "raw_landmarks": [ { "name": str, "x": float, "y": float, "confidence": float? } ],
    "refined_landmarks": [ { "name": str, "x": float, "y": float, "confidence": float? } ],
    "it_landmarks": [
      {
        "name": "IT_R" | "IT_L",
        "kp_index": 14 | 15,
        "v": 0 | 1 | 2,
        "x": float | null,
        "y": float | null,
        "confidence": float | null,
        "quality": "accept" | "review" | "unavailable" | null,
        "quality_reasons": [ str ] | null
      }
    ],
    "refinement_enabled": bool,
    "refinement_applied": bool,
    "coordinate_space": {
      "image_width": int,
      "image_height": int,
      "preprocessed_width": int,
      "preprocessed_height": int,
      "scale": float,
      "pad_x": int,
      "pad_y": int,
      "landmark_coordinate_space": "original_image_pixels"
    }
  },
  "measurements": {
    "right": { "vce": MeasureOut, "tonnis": MeasureOut, "ccd": MeasureOut },
    "left":  { "vce": MeasureOut, "tonnis": MeasureOut, "ccd": MeasureOut }
  },
  "audit": { ... }
}
```

`MeasureOut` = `{ "value_deg": float|null, "available": bool, "reason": str|null, "landmarks_used": [str]|null }`

**Landmark counts (validated backend):**

- `refined_landmarks` / `raw_landmarks`: **14** MVP landmarks (`MVP_LANDMARK_NAMES` in `mvp_geometry/landmarks.py`)
- `it_landmarks`: **empty `[]` for v2**; **2 entries (`IT_R`, `IT_L`) for v5_phase2**
- IT indices: `IT_R` → `kp_index` 14, `IT_L` → `kp_index` 15
- When `v == 0`: `x` and `y` are `null` (no invented coordinates)
- `quality` / `quality_reasons` present only when V5 QC runs; absent for v2

**14 MVP landmark names (order):**

`TD_R`, `TD_L`, `FHC_R`, `FHC_L`, `ASL_R`, `ASL_L`, `ASM_R`, `ASM_L`, `FNM_R`, `FNM_L`, `FSP_R`, `FSP_L`, `FSD_R`, `FSD_L`

#### Error — `status: "error"` (HTTP 200)

```json
{
  "status": "error",
  "error": {
    "code": "<string>",
    "message": "<string>"
  }
}
```

Known `error.code` values (from backend tests):

| Code | Typical cause |
|------|---------------|
| `invalid_image` | Empty, corrupt, unreadable |
| `file_too_large` | > 25 MiB |
| `unsupported_format` | Wrong extension/MIME |
| `model_not_found` | Checkpoint missing |
| `no_detection` | No pelvis detection |
| `low_bbox_confidence` | Bbox below threshold |
| `insufficient_landmarks` | Too few keypoints |
| `geometry_error` | Pelvis geometry indeterminate (VCE/Tönnis both sides) |
| `detection_failed` | Generic detection failure |
| `internal_error` | Unexpected pipeline error |

#### HTTP errors (non-200)

- **422**: missing/invalid multipart (no `file` field) — FastAPI `detail` string or validation list
- **4xx / 5xx**: handled by `ApiService` before `AnalysisResult` parsing

### Flutter model coverage vs contract

| Backend field | Flutter model | Status |
|---------------|---------------|--------|
| `status` | `AnalysisResult.status` | OK |
| `model_version` | — | **Missing** |
| `detection.refined_landmarks` | `DetectionInfo.refinedLandmarks` → `Landmark` | OK (14 MVP) |
| `detection.raw_landmarks` | `DetectionInfo.rawLandmarks` | OK (parsed, not displayed) |
| `detection.it_landmarks` | — | **Missing** |
| `detection.coordinate_space` | — | **Missing** |
| `detection.bounding_box` | `DetectionInfo.boundingBox` | OK |
| `measurements` | `AnalysisMeasurements` | OK (VCE, Tönnis, CCD only) |
| `audit` | `AnalysisResult.audit` | OK (opaque map, not shown in UI) |
| `error` | `AnalysisError` | OK |

`Landmark` supports optional `v` / `visibility` but MVP refined landmarks from backend currently expose `name`, `x`, `y`, `confidence` only (no `v` in serialized dict).

---

## Current image coordinate mapping

### Backend coordinate system

- All exposed landmark coordinates: **`original_image_pixels`**
- Origin: **top-left**; **y increases downward**
- Backend pipeline: detect in letterboxed preprocessed space → `reproject_point()` → original pixels
- `detection.coordinate_space` documents transform metadata (`image_width`, `image_height`, `scale`, `pad_x`, `pad_y`) for debugging/validation; overlay math on Flutter side does **not** need preprocessed dimensions if landmarks are already in original space

### Flutter mapping pipeline

1. **Image dimensions for layout**
   - Primary: `SelectedRadiograph.width/height` from `normalizeRadiographBytes()` (post-EXIF)
   - Fallback: `decodeImageSize(bytes)` in `ResultsScreen`
   - **Not used today:** `detection.coordinate_space.image_width/height`

2. **Display widget** — `LandmarkOverlay` / `RadiographImageView`
   - Fixed-height container (`height: 320` on results, `260` default)
   - `Image.memory(bytes, fit: BoxFit.contain)` — **letterbox/pillarbox**
   - **No zoom, no pan, no `InteractiveViewer`**

3. **Transform math** — `ImageContainLayout` (`lib/widgets/image_contain_layout.dart`)

```
scale = min(boxWidth / imageWidth, boxHeight / imageHeight)
displayedWidth  = imageWidth  * scale
displayedHeight = imageHeight * scale
offsetX = (boxWidth  - displayedWidth)  / 2
offsetY = (boxHeight - displayedHeight) / 2

displayX = offsetX + imageX * scale
displayY = offsetY + imageY * scale
```

4. **Drawable filter** — `Landmark.isDrawable`
   - Requires finite `x`, `y`
   - Excludes `visibility == 0` (or `v == 0` if parsed)

5. **EXIF alignment** — `image_normalizer.dart` bakes EXIF orientation **before upload** so backend landmarks match displayed pixels. Comment explicitly states backend does not fix EXIF.

### Coordinate risks identified

| Risk | Detail |
|------|--------|
| Dimension mismatch | If decoded local size ≠ `coordinate_space.image_width/height` (re-encode after normalize), overlay may drift |
| IT landmarks excluded | Overlay only renders `detection.refinedLandmarks` (14 MVP); `it_landmarks` never painted |
| No zoom | Acceptable for MVP; future pinch-zoom would require inverse transform on pan/zoom state |
| `BoxFit` locked to `contain` | `LandmarkOverlay` asserts `fit == BoxFit.contain` |

---

## Current screens

### Actual user flow

```
SCREEN 1 — Home / Import          HomeScreen
    ↓ gallery or camera
SCREEN 1b — Preview (extra step)    PreviewScreen
    ↓ "Analyser"
SCREEN 2 — Analysis loading       AnalysisScreen + LoadingAnalysis
    ↓ POST /analyze success
SCREEN 3 — Results                  ResultsScreen
```

Auxiliary: **ServerConnectionScreen** (health check, URL display, physical-device instructions).

### Screen responsibilities

| Screen | Key UI | Data shown |
|--------|--------|------------|
| `HomeScreen` | Import buttons, backend URL, Android physical-device warning | `ApiConfig.baseUrl` |
| `PreviewScreen` | `RadiographImageView`, dimensions, Analyze / Back | Local image only |
| `AnalysisScreen` | Spinner over image, error + retry | — |
| `ResultsScreen` | `LandmarkOverlay`, measurement sections, detection info, success banner | VCE/Tönnis/CCD R+L, landmark count, bbox, ASL_L refinement status |
| `ServerConnectionScreen` | Health test, config card | Latency, HTTP status, service version |

### Medical terminology audit

Current UI uses neutral terms: **Measurement**, **Détection**, **Landmarks**, unavailable shown as **"—"**, reasons as plain text. No **"normal"**, **"abnormal"**, or **"diagnosis"** labels found. V5 work must preserve this (use **Quality**, **Confidence**, **Review required**).

---

## Reusable components

| Component | Reuse for V5 |
|-----------|--------------|
| `ApiService` / `ApiConfig` | Extend parsing only; transport unchanged |
| `FileRadiographPicker` + `image_normalizer` | Fully reusable |
| `ImageContainLayout` | Core of overlay plan; unit-tested |
| `LandmarkOverlay` + `LandmarkPainter` | Extend to accept IT landmarks + quality styling |
| `RadiographImageView` | Preview / loading |
| `LoadingAnalysis` | Unchanged |
| `MeasurementCard` / `SideMeasurementsSection` | VCE/Tönnis/CCD display — no backend change |
| `AppTheme` / `AppColors` / `AppSpacing` | Add IT quality colors (accept/review/unavailable) |
| `ServerConnectionScreen` | Unchanged; optional: show backend `model_version` from health if added later |
| Screen flow (Home → Preview → Analysis → Results) | Keep; enhance Results only |

---

## Required changes

### Models (`lib/models/`)

1. **`AnalysisResult`** — add `modelVersion` (`String?`, values `v2` | `v5_phase2`)
2. **`DetectionInfo`** — add:
   - `itLandmarks: List<ITLandmark>`
   - `coordinateSpace: CoordinateSpace?`
3. **New `ITLandmark` model** — fields: `name`, `kpIndex`, `v`, `x`, `y`, `confidence`, `quality`, `qualityReasons`
   - Helpers: `isDrawable`, `qualityLabel`, `isAccept` / `isReview` / `isUnavailable`
4. **New `CoordinateSpace` model** — mirror `AnalyzeCoordinateSpaceOut`
5. **`Landmark`** — optional: alias `v` from JSON consistently for MVP if backend adds visibility later

### Services

- `ApiService._parseResponse` — no protocol change; richer `AnalysisResult` from same JSON
- Consider logging / dev assertion when `coordinate_space.image_width` ≠ local decoded width

### UI — `ResultsScreen`

- Show **`model_version`** (e.g. footer or detection section)
- New **IT status section**: `IT_R` / `IT_L` with quality badge, confidence, review reasons
- Pass **16 drawable landmarks** to overlay (14 refined + IT with `v != 0` and valid coords)
- Differentiate IT visual style (color/shape) vs MVP landmarks
- Optional **landmark legend / toggle** (MVP vs IT visibility)
- When `quality == review`: show **"Review required"** + `quality_reasons` (human-readable mapping TBD)
- When `quality == unavailable` or `v == 0`: no point on image; status card shows **Unavailable** + reasons
- Do **not** add Alpha angle or new measurements

### UI — overlay

- Extend `LandmarkOverlay` to accept `List<ITLandmark>` or unified `OverlayLandmark` type
- Quality-based styling:
  - `accept` → solid point (e.g. existing orange or new green-teal)
  - `review` → warning outline / dashed ring
  - `unavailable` → no marker; legend shows status only
- Prefer `coordinate_space.image_width/height` for `imageSize` when present (fallback to local decode)

### Tests (fixtures)

- Update `_okBody()` / `_sampleSuccessJson()` to include `model_version`, `coordinate_space`, `it_landmarks` for V5 scenarios
- Keep V2 fixture path (empty `it_landmarks`, `model_version: v2`)

---

## New components

| Component | Purpose |
|-----------|---------|
| `ITLandmark` model | Parse V5 IT QC payload |
| `CoordinateSpace` model | Parse `detection.coordinate_space` |
| `ITStatusCard` (widget) | Per-side IT quality, confidence, reasons |
| `ModelVersionBadge` (widget) | Display `model_version` on results |
| `LandmarkLegend` (widget) | Toggle/show MVP vs IT, quality color key |
| `quality_reason_labels.dart` (optional util) | Map backend reason codes → user-facing French strings (non-diagnostic) |

---

## API integration plan

### Phase 2B-1 — Models & parsing (no UI)

1. Add Dart models matching `backend/app/schemas/analyze.py` exactly
2. Extend `AnalysisResult.fromJson` / `DetectionInfo.fromJson`
3. Unit tests: V2 response (backward compatible), V5 full response, partial IT (`v=0`), each quality state
4. Verify `ApiService` integration tests pass with updated fixtures

### Phase 2B-2 — Results UI

1. Display `model_version`
2. Render IT status cards (no new measurements)
3. Wire overlay with 16 landmarks
4. Manual E2E on v5 backend (`MODEL_VERSION=v5_phase2`)

### Phase 2B-3 — Polish

1. Legend / landmark selector
2. Reason code localization table
3. Dimension consistency check (`coordinate_space` vs local)
4. Update `TEST_MOBILE_E2E.md` checklist for IT + model version

### Version detection strategy

Flutter **does not** choose model version. It displays whatever the server returns in `model_version`. Backend operator sets `MODEL_VERSION=v5_phase2` on server for V5 deployment.

---

## Landmark overlay plan

### Data sources for painting

| Landmark set | Source | Count |
|--------------|--------|------:|
| MVP | `detection.refined_landmarks` | 14 |
| IT | `detection.it_landmarks` where `v != 0` and `x`,`y` finite | 0–2 |

**Do not** merge IT into `refined_landmarks` on the client; backend keeps them separate.

### Transform (unchanged algorithm)

Continue using `ImageContainLayout.compute` + `toDisplay()` with `imageSize` from:

1. `detection.coordinate_space.image_width/height` (preferred when present)
2. Else `SelectedRadiograph` / `decodeImageSize`

### Visual encoding proposal

| Type | Marker | Label |
|------|--------|-------|
| MVP | Filled circle, `AppColors.landmark` | `name` |
| IT accept | Filled circle, distinct color (e.g. teal) | `IT_R` / `IT_L` |
| IT review | Same position, warning ring + badge in legend | + "Review required" |
| IT unavailable | Hidden on image | Legend only |

### BoxFit / interaction

- Keep **`BoxFit.contain`** only (existing assert)
- No zoom/pan in first V5 release; document as future enhancement requiring transform stack update

---

## IT QC display

### Fields to surface (per `IT_R` / `IT_L`)

| Field | Display |
|-------|---------|
| `name` | IT_R / IT_L header |
| `kp_index` | Optional debug/subtitle |
| `v` | Drives coord availability |
| `x`, `y` | Overlay when drawable |
| `confidence` | Show as percentage or 0.00–1.00 (consistent with MVP if shown) |
| `quality` | Badge: **Accept** / **Review required** / **Unavailable** |
| `quality_reasons` | Bulleted list when `review` or `unavailable` |

### Reason codes (from `v5_it_qc.py` — display only, not diagnostic)

`model_v0`, `out_of_image_bounds`, `wrong_patient_side`, `weak_lateral_placement`, `insufficient_caudal_vs_teardrop`, `insufficient_caudal_vs_fhc`, `bilateral_vertical_asymmetry`, `bilateral_horizontal_asymmetry`, `bilateral_order_violation`, `low_model_confidence`, `high_confidence_marginal_it_fsd`

### UX rules

- Never imply clinical diagnosis from quality state
- `review` still shows coordinates (backend exposes them); UI must warn **Review required**
- `unavailable` / `v=0`: no fabricated position; show **Unavailable**
- V2 responses (`it_landmarks: []`): hide IT section or show "Not available (model v2)"

### Measurements unchanged

VCE, Tönnis, CCD remain computed from **14 MVP landmarks only** (backend unchanged). IT QC is informational for future measures, not current angles.

---

## Tests

### Existing Flutter tests (4 files)

| File | Coverage |
|------|----------|
| `test/api_service_test.dart` | Multipart upload, error/422/500/invalid JSON, file size |
| `test/models_test.dart` | `Measurement`, `Landmark`, `AnalysisResult` (V2-shaped JSON) |
| `test/landmark_overlay_test.dart` | `ImageContainLayout` math, overlay paint, invalid coords |
| `test/health_check_test.dart` | `GET /health` success/failure |

**Gaps:** No `model_version`, `coordinate_space`, `it_landmarks`, IT quality, or 16-landmark overlay tests. Fixtures omit required backend field `coordinate_space` (would fail strict schema validation if enforced client-side).

### Tests to add (Phase 2B — not written yet)

#### Model parsing

- [ ] V5 success JSON with `model_version: v5_phase2`
- [ ] `it_landmarks` length 2, names `IT_R`/`IT_L`, `kp_index` 14/15
- [ ] `quality: accept` — full coords
- [ ] `quality: review` — coords present + `quality_reasons` non-empty
- [ ] `quality: unavailable` / `v: 0` — `x`/`y` null, not drawable
- [ ] V2 regression: empty `it_landmarks`, default `model_version`
- [ ] `coordinate_space` parsed; `landmark_coordinate_space == original_image_pixels`

#### Overlay

- [ ] 14 MVP + 2 IT markers when all drawable
- [ ] IT `unavailable` excluded from painter list
- [ ] IT `review` still painted (with distinct delegate if styling split)
- [ ] Layout uses `coordinate_space` dimensions when provided
- [ ] Aspect-ratio letterbox: corner landmark maps correctly (extend existing `ImageContainLayout` tests)

#### API service

- [ ] V5 body parses without throw
- [ ] `status: error` with V5 server still throws `ApiException`
- [ ] HTTP 422 / 500 unchanged

#### Widget (optional integration)

- [ ] `ResultsScreen` shows IT section when `it_landmarks` non-empty
- [ ] `ModelVersionBadge` shows `v5_phase2`

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Local image size ≠ `coordinate_space` | Overlay drift | Prefer backend dimensions; assert/warn in debug |
| EXIF not normalized (camera bypass) | Systematic offset | Keep `normalizeRadiographBytes` mandatory path |
| V5 backend not deployed | Empty IT, `model_version: v2` | UI degrades gracefully |
| `review` coords misleading | User over-trusts IT position | Prominent **Review required** + reasons |
| Reason codes opaque | Poor UX | French label map; link to legend |
| 120 s timeout on slow CPU | Failed analyses on device | Keep timeout; show retry (existing) |
| Physical device wrong URL | Connection failures | Existing banners + `ServerConnectionScreen` |
| Tests fixtures out of sync | False green tests | Align fixtures with `test_analyze_api.py` structure |
| Adding zoom later | Breaks overlay math | Encapsulate transform in `ImageContainLayout` |

---

## Recommended implementation order

1. **Models & JSON parsing** — `ITLandmark`, `CoordinateSpace`, `modelVersion`; V2/V5 fixtures  
2. **Unit tests for parsing** — all quality states, 16 landmarks data layer  
3. **`ImageContainLayout` + overlay** — unified landmark input, IT styling, `coordinate_space` dimensions  
4. **Overlay tests** — 14+2 painting, unavailable exclusion  
5. **`ITStatusCard` + `ModelVersionBadge`** — Results screen sections  
6. **`LandmarkLegend`** — toggle MVP/IT visibility  
7. **Reason code labels** — non-diagnostic French strings  
8. **Update E2E checklist** — `TEST_MOBILE_E2E.md` IT criteria  
9. **Manual QA** — v2 backend regression, v5_phase2 with B26_26 review case, physical Android  

---

## Appendix — Proposed Results screen layout (UX target)

```
┌─────────────────────────────────────┐
│  AppBar: Résultats                  │
├─────────────────────────────────────┤
│  [Radiograph + 16 landmark overlay] │
│  [Landmark legend / toggles]        │
│  model_version: v5_phase2           │
├─────────────────────────────────────┤
│  Hanche droite — VCE / Tönnis / CCD │
│  Hanche gauche  — VCE / Tönnis / CCD │
├─────────────────────────────────────┤
│  IT_R — Quality: Review required    │
│         Confidence: 0.82            │
│         Reasons: …                  │
│  IT_L — Quality: Accept             │
│         Confidence: 0.84            │
├─────────────────────────────────────┤
│  Détection (landmark count, bbox)   │
├─────────────────────────────────────┤
│  [ Nouvelle radiographie ]          │
└─────────────────────────────────────┘
```

This matches Phase 2B objectives while reusing the existing navigation shell and measurement components.
