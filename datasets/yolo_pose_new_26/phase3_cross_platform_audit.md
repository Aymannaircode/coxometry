# Phase 3 — Cross-Platform End-to-End Audit

**Date:** 2026-09-02  
**Audit environment:** Windows 10 (no macOS/Xcode available)  
**Scope:** `mobile/` Flutter app — Android + iOS readiness (read-only)  
**Validated upstream state:** V5 Phase 2 CHECKPOINT_INFERENCE_READY, BACKEND_V5_PHASE2_INTEGRATION_READY, FLUTTER_V5_INTEGRATION_READY

---

## Executive Summary

The Coxometry Flutter application (`mobile/`) is **architecturally sound for V5 integration** on the Dart/UI layer: navigation (Home → Preview → Analysis → Results), multipart `POST /analyze`, coordinate-space-aware landmark overlay, IT QC display, and 47 automated widget/unit tests all pass. Android **debug build was verified** on this machine (`app-debug.apk` built successfully).

**Critical gap:** the repository contains **no `mobile/ios/` directory**. iOS cannot be built, simulated, or device-tested until the platform is generated on macOS (`flutter create --platforms=ios`) and Info.plist permissions are added. `.metadata` lists only `android`, `web`, and `windows`.

**Android status:** `ANDROID_BUILD_READY` — source and debug APK verified. Physical-device API access requires compile-time `--dart-define=API_BASE_URL=http://<LAN-IP>:8001` (documented in-app; no runtime URL editor).

**iOS status:** `SOURCE-LEVEL READY` (Dart code has `Platform.isIOS` defaults) but **`ACTUAL macOS/Xcode BUILD VERIFIED` = NOT POSSIBLE** on this audit host because the iOS project is absent.

**Final verdict:** `CROSS_PLATFORM_BLOCKED` (iOS platform missing; Android needs physical-device E2E validation and release signing before production).

---

## Current Flutter Architecture

| Area | Implementation |
|------|----------------|
| **Flutter / Dart** | Flutter 3.44.6 stable, Dart SDK `^3.12.2` (resolved 3.12.2) |
| **Entry** | `lib/main.dart` → `CoxometrieApp` (`lib/app.dart`) |
| **Navigation** | Imperative `MaterialPageRoute`; no router package |
| **State management** | `StatefulWidget` local state only (no Provider/Bloc/Riverpod) |
| **Screens** | `HomeScreen` → `PreviewScreen` → `AnalysisScreen` → `ResultsScreen`; `ServerConnectionScreen` for health check |
| **Services** | `ApiService` (HTTP), `FileRadiographPicker` (gallery + camera) |
| **Models** | `AnalysisResult`, `DetectionInfo`, `Landmark`, `ITLandmark`, `CoordinateSpace`, `Measurement` |
| **Overlay** | `LandmarkOverlay` + `ImageContainLayout` (`BoxFit.contain` only) |
| **Image pipeline** | `normalizeRadiographBytes` (EXIF bake + re-encode) before upload |
| **API config** | `ApiConfig` — `--dart-define=API_BASE_URL` or platform defaults |
| **Theme** | Material 3, `AppTheme.light`, clinical palette (`app_colors.dart`) |
| **Tests** | 5 test files, 47 tests (API, models, overlay, V5 integration, health) |
| **Platforms in repo** | `android/`, `windows/`, `web/` — **no `ios/`** |
| **Assets** | None declared in `pubspec.yaml` (no bundled images/fonts beyond system) |

---

## Android Audit

### Build configuration

| Setting | Value |
|---------|-------|
| `compileSdk` | 36 |
| `targetSdk` | 36 (via `flutter.targetSdkVersion`) |
| `minSdk` | 24 |
| Kotlin | 2.3.20 |
| Android Gradle Plugin | 9.0.1 |
| Gradle wrapper | 9.1.0 |
| Java compatibility | 17 |
| Namespace / applicationId | `com.coxometrie.coxometrie` |

### Manifest & permissions (`android/app/src/main/AndroidManifest.xml`)

- `INTERNET` — required for API
- `CAMERA` — camera capture via `image_picker`
- `READ_MEDIA_IMAGES` — gallery on API 33+
- `READ_EXTERNAL_STORAGE` (`maxSdkVersion="32"`) — legacy gallery access
- `android:usesCleartextTraffic="true"` + `@xml/network_security_config` — HTTP to local backend permitted

### Release configuration

- `release` build type uses **debug signing keys** (`signingConfig = signingConfigs.getByName("debug")`) — acceptable for demo, **not production-ready**.

### Build verification (this audit)

```
flutter build apk --debug
→ √ Built build\app\outputs\flutter-apk\app-debug.apk  (exit 0, ~435 s)
```

### Android verdict

**`ANDROID_BUILD_READY`**

No structural blockers found. Release signing and Play Store packaging remain unfinished (expected for MVP).

---

## iOS Audit

### Structural finding

**`mobile/ios/` does not exist.** `.metadata` platform list: `android`, `web`, `windows` only. The project was never scaffolded for iOS in this repository.

### Source-level readiness (Dart)

- `ApiConfig` defaults iOS simulator to `http://127.0.0.1:8001`
- `image_picker` (^1.2.3) and `file_picker` (^12.1.2) include iOS implementations transitively (`image_picker_ios`, `file_picker_darwin` in lockfile)
- No `dart:io` usage in UI layer except `Platform.isAndroid` / `Platform.isIOS` in `api_config.dart` and `home_screen.dart`
- **No iOS-specific warning banner** on `HomeScreen` (only Android shows LAN IP reminder)

### Required but absent (must be created on macOS)

| Item | Status |
|------|--------|
| `ios/Runner.xcodeproj` | **Missing** |
| `ios/Podfile` | **Missing** |
| `ios/Runner/Info.plist` | **Missing** |
| Camera usage description | **Not present** (would crash/deny without `NSCameraUsageDescription`) |
| Photo library usage | **Not present** (would need `NSPhotoLibraryUsageDescription` for gallery) |
| ATS (App Transport Security) | **Not configured** — HTTP to LAN backend will require `NSAppTransportSecurity` exception or HTTPS |
| Signing / provisioning | **Not configured** |

### iOS verdict

| Check | Result |
|-------|--------|
| Source-level ready | **Partial** — shared Dart code is platform-aware |
| Simulator ready | **BLOCKED** — no iOS project |
| Physical device ready | **BLOCKED** |
| Release build ready | **BLOCKED** |

**iOS build requires macOS + Xcode for final verification.**

---

## Networking Audit

### `ApiConfig` (`lib/config/api_config.dart`)

| Priority | URL |
|----------|-----|
| 1 | `--dart-define=API_BASE_URL=<url>` (compile-time) |
| 2 Android emulator | `http://10.0.2.2:8001` |
| 2 iOS simulator (if built) | `http://127.0.0.1:8001` |
| 2 Desktop / Web | `http://127.0.0.1:8001` |

Default port: **8001**. No trailing-slash normalization applied.

### `ApiService` (`lib/services/api_service.dart`)

| Feature | Behavior |
|---------|----------|
| Endpoints | `GET /health`, `POST /analyze` |
| Multipart | Field name `file`; content-type from extension (jpeg/png/octet-stream) |
| Max upload | 25 MiB (client-side, aligned with backend) |
| Health timeout | 15 s |
| Analyze timeout | 120 s (send + response read) |
| HTTP vs HTTPS | **HTTP cleartext** (MVP local network) |
| Error taxonomy | `ApiExceptionKind`: network, timeout, clientError, serverError, invalidJson, fileTooLarge, analysisError |
| Response parsing | JSON → `AnalysisResult.fromJson`; `status: error` → `ApiException` |
| Platform differences | None in client code; cleartext policy is per-platform manifest (Android configured; iOS ATS not yet present) |

### Physical Android device

- Default `10.0.2.2` **does not work** on real hardware.
- App shows warning banner when `Platform.isAndroid && !ApiConfig.isFromDartDefine`.
- `ServerConnectionScreen` documents: `flutter run --dart-define=API_BASE_URL=http://<PC-IP>:8001`.
- **No in-app runtime URL configuration** — must rebuild/relaunch with dart-define.

---

## Image Handling Audit

### Supported formats

| Format | Gallery (`file_picker`) | Camera (`image_picker`) | Upload content-type |
|--------|-------------------------|-------------------------|---------------------|
| JPG/JPEG | Yes | Yes (default) | `image/jpeg` |
| PNG | Yes | Possible | `image/png` |

### Pipeline

1. User picks image → bytes read into memory (`Uint8List`)
2. `normalizeRadiographBytes` decodes with `image` package, applies `bakeOrientation` (EXIF)
3. Re-encodes: PNG stays PNG; others → JPEG quality **95**
4. Dimensions stored on `SelectedRadiograph` (`width`, `height`)
5. Full byte array held in memory through Preview → Analysis → Results
6. Upload via multipart; no local persistence by app code

### Large images

- Client rejects > 25 MiB before upload
- High-resolution radiographs (multi-MB) decoded multiple times (normalizer + `Image.memory` + optional `decodeImageSize`) — **memory pressure risk** on low-RAM devices
- No downscaling before upload

### EXIF / orientation

- EXIF correction applied **before** upload so backend `original_image_pixels` align with displayed pixels
- Preview shows "orientation corrigée" when applicable

---

## Coordinate Mapping Audit

### Chain

```
Backend landmarks (original_image_pixels)
  → resolveOverlayImageSize (prefers coordinate_space.image_width/height)
  → ImageContainLayout.compute (BoxFit.contain math)
  → LandmarkPainter.toDisplay(x, y)
  → CustomPaint on Stack over Image.memory(fit: contain)
```

### Key behaviors

- `coordinate_space` from V5 response is **preferred** over locally decoded size
- If local ≠ backend (> 1 px tolerance): overlay uses **backend dimensions** + `_DimensionMismatchBanner` shown
- `ImageContainLayout` handles letterbox/pillarbox with uniform scale + offset
- Only `BoxFit.contain` supported (assert in `LandmarkOverlay`)
- Invalid/non-finite coordinates skipped in painter (no crash)
- Tests cover center mapping, scale-down, mismatch banner

### Gaps (not tested on device)

- Portrait vs landscape **device orientation** with real radiographs
- Very wide/tall aspect ratios on small phones (layout uses fixed overlay height 320 px + scroll)

---

## V5 Landmark Audit

### MVP landmarks (KP 0–13)

- Parsed from `detection.refined_landmarks`
- `Landmark.isDrawable`: requires valid x/y and `visibility != 0` (field `v` in JSON)
- Painted orange (`AppColors.landmark`) with white stroke + optional label

### IT landmarks (IT_R = index 14, IT_L = index 15)

| Condition | Overlay | IT status card |
|-----------|---------|----------------|
| `v=2`, quality `accept` | Green-teal marker | ACCEPT badge |
| `v=2`, quality `review` | Amber marker + warning ring + `⚠` label | REVIEW badge + reason |
| `v=0` or quality `unavailable` | **No marker** (`isDrawable=false`) | UNAVAILABLE badge |
| Invalid coords | Skipped in painter | Card still shown if in JSON |

### Visual distinction REVIEW vs ACCEPT

- **Overlay:** `itLandmarkReview` color, thicker stroke, outer warning ring
- **Card:** amber `REVIEW` badge + `Reason : …` in warning color
- **Tests:** `v5_integration_test.dart` verifies REVIEW badge and overlay exclusion for v=0

---

## Results Screen Audit

### Displayed data

- Radiograph + landmark overlay (or plain image if no landmarks)
- Model version label (`V5 Phase 2` / `V2`)
- Success banner (always green on arrival — assumes `status: ok`)
- Per-side measurements: **VCE**, **Tönnis**, **CCD** (right + left)
- IT section (V5 only): IT_R, IT_L with quality, confidence, reasons, position
- Detection section: MVP count, IT count, bbox, ASL_L refinement, coordinate space dims

### Layout / responsiveness

- `SingleChildScrollView` + `ConstrainedBox(maxWidth: 720)` — reasonable for phones and tablets
- Fixed overlay height 320 px
- `_InfoRow` label column width 160 px — may be tight on very narrow landscape screens
- No explicit `Semantics` labels for accessibility
- Unavailable measurements show `—` (never `0°`) — tested

### Not shown

- `audit` JSON (parsed but not rendered — good for privacy)
- Raw landmark lists (only overlay + counts)

---

## Error Handling Audit

| Scenario | Expected behavior | Verified |
|----------|-------------------|----------|
| Server unavailable | `ApiException` network message; retry UI on Analysis screen | Unit test (mock); device NOT VERIFIED |
| Timeout (120 s) | Timeout message | Unit test (mock) |
| Invalid image (client) | `RadiographPickerException` on home | Code review |
| HTTP 400/422 | `ApiException` clientError with detail | Unit test |
| HTTP 500 | Generic server message | Unit test |
| Malformed JSON | `invalidJson` exception | Unit test |
| `status: error` in 200 body | `analysisError` exception | Unit test |
| Missing `measurements` on `status: ok` | **`AnalysisMeasurements.fromJson` throws** → caught as unexpected error string | **Risk — not tested** |
| Missing `coordinate_space` | Falls back to local decoded size | Unit test |
| Invalid landmark coordinate | Ignored in painter | Widget test |
| IT `v=0` | No overlay marker | Unit + widget test |
| IT `review` | Drawable + distinct styling | Widget test |
| Empty HTTP body | `invalidJson` / empty response error | Code review |
| Non-`ApiException` throw | Raw `'Erreur inattendue : $e'` shown | Code review — may leak internals |

**UI crash risk:** Low for normal API contracts; **medium** if backend returns `status: ok` with malformed/partial `measurements` block.

---

## Performance Audit

| Risk | Severity | Notes |
|------|----------|-------|
| Full-image `Uint8List` in memory end-to-end | **Medium** | Up to 25 MB + decode buffers |
| Double/triple decode (normalize, display, size probe) | **Medium** | Noticeable on 3000×3000+ radiographs |
| JPEG re-encode at q=95 | **Low–Medium** | May increase upload size vs original |
| 120 s blocking analyze | **Low** | Appropriate for YOLO; UI shows spinner |
| Overlay `CustomPaint` rebuild | **Low** | `shouldRepaint` compares landmark lists |
| Results screen nested scroll + fixed image | **Low** | Acceptable for MVP |

No premature optimization recommended; **device profiling with real radiographs** is the next step.

---

## Dependency Audit

| Package | Resolved version | Purpose | Android | iOS | Notes |
|---------|------------------|---------|---------|-----|-------|
| `flutter` (SDK) | 3.44.6 | Framework | Yes | Yes* | *iOS project missing |
| `http` | 1.6.0 | REST client | Yes | Yes | Cleartext depends on manifest |
| `http_parser` | 4.1.2 | Multipart MediaType | Yes | Yes | |
| `file_picker` | 12.1.2 | Gallery file pick | Yes | Yes* | Uses platform pickers |
| `image_picker` | 1.2.3 | Camera capture | Yes | Yes* | Runtime permissions via plugin |
| `image` | 4.9.2 | EXIF normalize / encode | Pure Dart | Pure Dart | |
| `path` | 1.9.1 | Extension helpers | Pure Dart | Pure Dart | |
| `flutter_lints` | 6.0.0 | Static analysis | Dev only | Dev only | |

**Transitive (notable):** `image_picker_android` 0.8.13+19, `image_picker_ios` 0.8.13+6, `android_file_picker` 1.0.3.

**Compatibility:** 16 packages have newer incompatible versions per `flutter pub get` warning — **no upgrade performed** (per audit rules).

---

## Security Audit

| Topic | Finding |
|-------|---------|
| Transport | **HTTP cleartext** to local/LAN backend — images traverse Wi‑Fi unencrypted |
| HTTPS | Not implemented; acceptable for controlled demo LAN, not for public networks |
| Local storage | Images kept **in memory only**; app does not write radiographs to disk |
| Temp files | `image_picker` / OS may create cache temps — standard plugin behavior, not explicitly cleaned |
| API error exposure | User-facing messages are sanitized; generic catch may show exception `toString()` |
| Logging | `avoid_print: true` in lints; **no `print`/`debugPrint` in `lib/`** |
| Audit field | Parsed but **not displayed** — reduces accidental internal detail leak |
| Patient identifiers | App does not collect names/IDs; only radiograph bytes |
| Regulatory compliance | **Not assessed** (out of scope) |

---

## Test Results

### Flutter (`mobile/`)

**Command:**
```powershell
Set-Location C:\Users\g\OneDrive\Desktop\Projet-Ayman\mobile
C:\Users\g\flutter\bin\flutter.bat test
```

**Result:** `00:02 +47: All tests passed!` (exit 0)

### Backend

**Command:**
```powershell
Set-Location C:\Users\g\OneDrive\Desktop\Projet-Ayman
python -m unittest discover -s backend\tests -v
```

**Result:** `Ran 167 tests in 153.331s — OK (skipped=1)`

### Android build (verification only)

**Command:**
```powershell
C:\Users\g\flutter\bin\flutter.bat build apk --debug
```

**Result:** `√ Built build\app\outputs\flutter-apk\app-debug.apk` (exit 0)

---

## Android/iOS Test Matrix

| Feature | Android | iOS |
|---------|---------|-----|
| App starts | NOT VERIFIED (device) | BLOCKED (no project) |
| Image picker | NOT VERIFIED | BLOCKED |
| Camera | NOT VERIFIED | BLOCKED |
| JPG | NOT VERIFIED | BLOCKED |
| JPEG | NOT VERIFIED | BLOCKED |
| PNG | NOT VERIFIED | BLOCKED |
| Upload | NOT VERIFIED | BLOCKED |
| API connection | NOT VERIFIED | BLOCKED |
| V5 response | PASS (unit/widget tests) | PASS (unit tests only) |
| 16 KP overlay | PASS (widget tests) | PASS (unit tests only) |
| IT ACCEPT | PASS (widget tests) | PASS (unit tests only) |
| IT REVIEW | PASS (widget tests) | PASS (unit tests only) |
| IT UNAVAILABLE | PASS (unit tests) | PASS (unit tests only) |
| VCE | PASS (widget tests) | PASS (unit tests only) |
| Tönnis | PASS (widget tests) | PASS (unit tests only) |
| CCD | PASS (widget tests) | PASS (unit tests only) |
| Error handling | PASS (unit tests) | PASS (unit tests only) |

*Android debug APK builds on Windows; no emulator or physical device was attached during this audit.*

---

## P0 Issues

| ID | Issue | Platform |
|----|-------|----------|
| P0-1 | **`mobile/ios/` directory absent** — cannot build, sign, or test on iOS Simulator or iPhone | iOS |
| P0-2 | **No physical Android E2E validation** in this audit — real-device upload/API/overlay alignment unconfirmed | Android |

---

## P1 Issues

| ID | Issue | Platform |
|----|-------|----------|
| P1-1 | API URL only via `--dart-define` at compile time — no runtime configuration; easy misconfiguration on physical devices | Both |
| P1-2 | Release APK uses **debug signing** | Android |
| P1-3 | iOS Info.plist permission strings and ATS cleartext exception not created | iOS |
| P1-4 | `AnalysisMeasurements.fromJson` throws if `measurements` block missing/malformed on `status: ok` — shows raw unexpected error | Both |
| P1-5 | README outdated (`POST /measurements` vs current `POST /analyze`) | Docs |
| P1-6 | No iOS LAN IP warning (Android has banner; iOS physical device would need same guidance) | iOS |

---

## P2 Issues

| ID | Issue | Platform |
|----|-------|----------|
| P2-1 | Large radiograph memory pressure (full bytes + multiple decodes, no downscale) | Both |
| P2-2 | HTTP cleartext only — no HTTPS path for non-LAN deployment | Both |
| P2-3 | Fixed overlay height (320 px) may reduce landmark visibility on small screens | Both |
| P2-4 | Landscape layout / narrow-width `_InfoRow` not validated on devices | Both |
| P2-5 | `Segoe UI` font family — falls back on Android/iOS (cosmetic) | Both |
| P2-6 | Camera permission declared but no explicit pre-request UX (relies on plugin) | Android |

---

## P3 Issues

| ID | Issue | Platform |
|----|-------|----------|
| P3-1 | No accessibility `Semantics` on measurement cards / overlay | Both |
| P3-2 | `ServerConnectionScreen` is debug-oriented — could expose internal URL in screenshots | Both |
| P3-3 | 16 transitive packages have newer versions available | Both |
| P3-4 | `web/` and `windows/` platforms present but out of clinical demo scope | Desktop |

---

## Recommended Fix Order

1. **Generate iOS project on macOS** (`flutter create . --platforms=ios`), add Info.plist camera/photo/ATS entries, verify simulator build
2. **Android physical E2E** per `mobile/docs/TEST_MOBILE_E2E.md` with `--dart-define=API_BASE_URL`
3. **Harden JSON parsing** for partial `measurements` / missing `coordinate_space` (graceful degradation)
4. **Runtime or persisted API URL** (optional settings screen) for demo reliability
5. **Release signing** (Android keystore; iOS provisioning)
6. **Device coordinate validation** with known radiographs (portrait/landscape, EXIF)
7. **Memory profiling** with ≥10 MB images on mid-range Android
8. UX polish (accessibility, landscape, font fallbacks)
9. HTTPS / secure transport if leaving LAN demo context

**Alpha angle:** Not recommended in remaining 5 days — requires additional imaging view/landmarks not in current V5 MVP scope.

---

## Remaining 5-Day Plan

| Day | Focus |
|-----|-------|
| **Day 1** | macOS: `flutter create --platforms=ios`, Info.plist permissions + ATS, iOS simulator build; Android physical E2E checklist (health + one full analyze) |
| **Day 2** | Cross-device coordinate audit (3+ radiographs, portrait/landscape); fix overlay mismatches if found |
| **Day 3** | Error-path hardening (malformed JSON edge cases, missing measurements); API URL UX for physical devices |
| **Day 4** | Release builds (signed APK, iOS ad-hoc/TestFlight if certs available); performance pass on large images |
| **Day 5** | Final demo rehearsal, documentation update, regression (`flutter test` + backend tests), go/no-go |

---

## Final Verdict

### `CROSS_PLATFORM_BLOCKED`

**Rationale:** Android is build-ready and well-tested at the unit/widget level, but **iOS cannot be compiled** because the platform project is missing from the repository. Cross-platform demo readiness requires iOS scaffolding on macOS plus confirmed physical-device E2E on at least one Android phone.

| Platform | Source ready | Debug build | Release build | Physical device |
|----------|--------------|-------------|---------------|-----------------|
| **Android** | Yes | **Verified** | Not ready (debug signing) | Not verified |
| **iOS** | Partial (Dart only) | **Blocked** | **Blocked** | **Blocked** |

**iOS build requires macOS + Xcode for final verification.**

---

## Appendix — Files Inspected

### Configuration
- `mobile/pubspec.yaml`, `mobile/pubspec.lock`, `mobile/analysis_options.yaml`, `mobile/.metadata`, `mobile/README.md`
- `mobile/android/app/build.gradle.kts`, `mobile/android/build.gradle.kts`, `mobile/android/settings.gradle.kts`
- `mobile/android/gradle/wrapper/gradle-wrapper.properties`, `mobile/android/gradle.properties`
- `mobile/android/app/src/main/AndroidManifest.xml`, `debug/`, `profile/`
- `mobile/android/app/src/main/res/xml/network_security_config.xml`

### Application source (`mobile/lib/`)
- `main.dart`, `app.dart`, `config/api_config.dart`
- `services/api_service.dart`, `services/radiograph_picker.dart`
- `screens/home_screen.dart`, `preview_screen.dart`, `analysis_screen.dart`, `results_screen.dart`, `server_connection_screen.dart`
- `models/analysis_result.dart`, `landmark.dart`, `it_landmark.dart`, `coordinate_space.dart`, `measurement.dart`
- `widgets/landmark_overlay.dart`, `image_contain_layout.dart`, `radiograph_image_view.dart`, `measurement_card.dart`, `it_status_section.dart`, `loading_analysis.dart`, `model_version_label.dart`
- `utils/image_normalizer.dart`, `image_size.dart`, `overlay_image_size.dart`, `model_version_label.dart`
- `theme/app_theme.dart`, `app_colors.dart`, `app_spacing.dart`

### Tests & docs
- `mobile/test/*.dart`, `mobile/test/fixtures/analysis_fixtures.dart`
- `mobile/docs/TEST_MOBILE_E2E.md`

### Build artifacts (read-only verification)
- `mobile/build/app/outputs/flutter-apk/app-debug.apk` (produced during audit)

---

## Appendix — Commands Executed

```powershell
# Backend tests
Set-Location C:\Users\g\OneDrive\Desktop\Projet-Ayman
python -m unittest discover -s backend\tests -v

# Flutter tests
Set-Location C:\Users\g\OneDrive\Desktop\Projet-Ayman\mobile
C:\Users\g\flutter\bin\flutter.bat test

# Flutter / Android debug build
C:\Users\g\flutter\bin\flutter.bat --version
C:\Users\g\flutter\bin\flutter.bat build apk --debug
```

**No source files were modified during this audit.** Only this report file was created.
