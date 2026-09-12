# Flutter V5 Phase 2 Integration Audit

**Phase:** 2B-1 — implementation  
**Date:** 2026-09-02  
**Backend status (unchanged):** `BACKEND_V5_PHASE2_INTEGRATION_READY`, `V5_IT_QC_READY`

---

## Files modified

| File | Change |
|------|--------|
| `mobile/lib/models/analysis_result.dart` | Added `modelVersion`, `itLandmarks`, `coordinateSpace` |
| `mobile/lib/theme/app_colors.dart` | Added `itLandmark`, `itLandmarkReview` colors |
| `mobile/lib/widgets/landmark_overlay.dart` | 16-landmark overlay (MVP + IT), review ring styling |
| `mobile/lib/screens/results_screen.dart` | Model version, IT section, coordinate resolution, mismatch banner |
| `mobile/lib/widgets/loading_analysis.dart` | Loading message text update |
| `mobile/test/models_test.dart` | V2 fixture via shared fixtures, `model_version` assertions |
| `mobile/test/landmark_overlay_test.dart` | 16-landmark + IT unavailable tests |
| `mobile/test/api_service_test.dart` | V5 response parsing test, V2 `it_landmarks: []` in fixture |

## Files created

| File | Purpose |
|------|---------|
| `mobile/lib/models/coordinate_space.dart` | `CoordinateSpace` model |
| `mobile/lib/models/it_landmark.dart` | `ITLandmark`, `ITQuality` enum |
| `mobile/lib/utils/overlay_image_size.dart` | Backend/local dimension resolution + mismatch detection |
| `mobile/lib/utils/model_version_label.dart` | `formatModelVersion()` helper |
| `mobile/lib/widgets/it_status_section.dart` | IT_R / IT_L quality UI |
| `mobile/lib/widgets/model_version_label.dart` | Discreet model version display |
| `mobile/test/fixtures/analysis_fixtures.dart` | Shared V2/V5 JSON fixtures |
| `mobile/test/v5_integration_test.dart` | V5 parsing, coordinate mapping, Results screen widget tests |

---

## API changes

No protocol changes. `ApiService` continues:

- `POST /analyze` with multipart field `file`
- Same timeouts, health check, error handling
- Parses extended `AnalysisResult` from same JSON envelope

New fields consumed (optional for V2 backward compatibility):

| Field | V2 | V5 Phase 2 |
|-------|----|------------|
| `model_version` | `"v2"` or absent | `"v5_phase2"` |
| `detection.it_landmarks` | `[]` | 2 entries (`IT_R`, `IT_L`) |
| `detection.coordinate_space` | absent or present | present with `original_image_pixels` |

---

## V5 models

### `ITLandmark`

Fields: `name`, `kpIndex`, `v`, `x`, `y`, `confidence`, `quality`, `qualityReasons`

Quality states: `accept`, `review`, `unavailable`

`isDrawable`: `v != 0`, valid finite coordinates, `quality != unavailable`

### `CoordinateSpace`

Mirrors `AnalyzeCoordinateSpaceOut`: `image_width`, `image_height`, preprocessed dims, `scale`, `pad_x`, `pad_y`, `landmark_coordinate_space`

### `AnalysisResult`

Added `modelVersion`, `isV5Phase2` getter

---

## Coordinate mapping

Algorithm unchanged (`ImageContainLayout`):

```
scale = min(boxW / imageW, boxH / imageH)
displayX = offsetX + imageX * scale
displayY = offsetY + imageY * scale
```

Dimension resolution (`resolveOverlayImageSize`):

1. Prefer `coordinate_space.image_width/height` when present
2. Fallback to locally decoded radiograph dimensions
3. If backend and local differ by >1 px: `dimensionMismatch = true`, warning banner shown, mapping uses **backend** dimensions (landmarks are in backend pixel space — no silent stretch to local size)

---

## 16 landmark overlay

| Source | Count | Display |
|--------|------:|---------|
| `detection.refined_landmarks` | 14 MVP | Orange filled circle + label |
| `detection.it_landmarks` (drawable) | 0–2 | Teal circle; review = warning ring + `⚠` label suffix |

Excluded from overlay: `v=0`, `quality=unavailable`, null/invalid coordinates

---

## IT quality UI

`ITStatusSection` on Results screen when `it_landmarks` non-empty:

- **ACCEPT** — green dot + confidence
- **REVIEW** — warning icon + confidence + primary reason
- **UNAVAILABLE** — `— UNAVAILABLE` + reasons if present

Explicit naming: `IT_R`, `IT_L` headers. Position shown in details when drawable.

---

## V2 compatibility

- `it_landmarks: []` parses to empty list; IT section hidden
- `model_version` absent → label shows `V2`
- Existing measurement cards (VCE, Tönnis, CCD) unchanged
- `ApiService` transport and error paths unchanged
- All prior test files retained and updated (not deleted)

---

## Tests

### Added (`mobile/test/v5_integration_test.dart`)

1. V2 response parsing  
2. V5 response parsing  
3. IT_R parsing  
4. IT_L parsing  
5. ACCEPT quality  
6. REVIEW quality  
7. UNAVAILABLE quality  
8. Coordinate mapping  
9. `coordinate_space` mismatch detection  
10. `v=0` does not display marker  
11. Results screen renders V5 data  

### Extended

- `landmark_overlay_test.dart` — 16 landmarks, IT unavailable exclusion  
- `api_service_test.dart` — V5 body parse  
- `models_test.dart` — V2 `model_version` + empty `it_landmarks`

### Execution

| Suite | Result | Notes |
|-------|--------|-------|
| Flutter (`flutter test`) | **47 passed, 0 failed** | Full suite green |
| Backend (`python -m unittest discover -s backend/tests -v`) | **167 OK, 1 skipped** | No backend files modified; DICOM deps required in environment |

---

## Screens verified

| Screen | Status |
|--------|--------|
| `HomeScreen` | Unchanged |
| `PreviewScreen` | Unchanged |
| `AnalysisScreen` | Loading message updated |
| `ResultsScreen` | Overlay 16 LM, measurements, IT QC, model version, mismatch banner |
| `ServerConnectionScreen` | Unchanged |

---

## Known limitations

1. No zoom/pan on radiograph (by design — `BoxFit.contain` only)
2. No Alpha angle or new clinical interpretation (out of scope)
3. Dimension mismatch uses backend size with user warning — if local bytes truly differ in resolution, overlay accuracy depends on EXIF normalization path
4. Backend regression suite requires DICOM decompression dependencies (`pylibjpeg`) in test environment

---

## Verdict

**FLUTTER_V5_INTEGRATION_READY**

Implementation complete per Phase 2B-1 spec. Flutter: 47/47 tests passed. Backend: 167 OK, 1 skipped (unchanged).
