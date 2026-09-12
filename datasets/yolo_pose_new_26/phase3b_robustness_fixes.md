# Phase 3B — Cross-Platform Robustness Fixes

**Date:** 2026-09-02  
**Environment:** Windows 10 (no macOS, no physical Android device attached)  
**Phase 3A verdict addressed:** `CROSS_PLATFORM_BLOCKED`

---

## Issues addressed

| Issue | Phase 3A ID | Status |
|-------|-------------|--------|
| Physical Android API configuration | P0 / P1 | **FIXED** (docs + `ApiConfig` helpers + in-app hints) |
| Malformed `status: ok` responses | P1 | **FIXED** (defensive validation + tests) |
| Release signing (debug keys) | P1 | **DOCUMENTED** + optional `key.properties` wiring |
| API configuration clarity | P1 | **DOCUMENTED** (`docs/API_CONFIGURATION.md`) |
| README `/measurements` outdated | P1 | **FIXED** |
| iOS project missing | P0 | **DOCUMENTED** (`docs/IOS_SETUP.md`) — not generated on Windows |
| Large image memory | P2 | **DOCUMENTED** (comment in `image_normalizer.dart`) |
| HTTP cleartext | P2 | **DOCUMENTED** (README, API_CONFIGURATION, network_security_config comment) |
| Landscape / narrow screen | P2 | **FIXED** (flexible `_InfoRow` + widget test) |
| Physical Android E2E execution | P0 | **NOT VERIFIED** (no device available in audit environment) |

---

## Files modified

| File | Change |
|------|--------|
| `mobile/lib/config/api_config.dart` | Added `androidEmulatorUrl`, `localhostUrl`, `physicalDeviceRunCommand()`, `physicalDeviceHint` |
| `mobile/lib/models/analysis_result.dart` | `AnalysisMeasurements.isValidJson`, `AnalysisResponseValidator` |
| `mobile/lib/services/api_service.dart` | `invalidResponse` kind; validate `status: ok` before return |
| `mobile/lib/screens/analysis_screen.dart` | Friendly `invalidResponse` + generic unexpected error (no raw exception) |
| `mobile/lib/screens/home_screen.dart` | Cross-platform physical-device hint banner (Android + iOS) |
| `mobile/lib/screens/server_connection_screen.dart` | Updated physical-device instructions |
| `mobile/lib/screens/results_screen.dart` | Flexible `_InfoRow` for narrow widths |
| `mobile/lib/utils/image_normalizer.dart` | Memory-risk documentation comment |
| `mobile/android/app/build.gradle.kts` | Optional release signing via `key.properties` |
| `mobile/android/app/src/main/res/xml/network_security_config.xml` | Clarified dev/LAN scope comment |
| `mobile/README.md` | Updated endpoint, API table, doc links |
| `mobile/test/api_service_test.dart` | +5 tests (valid/missing/malformed ok, timeout) |
| `mobile/test/models_test.dart` | +4 tests (validator + isValidJson) |
| `mobile/test/v5_integration_test.dart` | +1 narrow-width layout test |

## Files created

| File | Purpose |
|------|---------|
| `mobile/docs/API_CONFIGURATION.md` | Platform-by-platform API URL guide |
| `mobile/docs/IOS_SETUP.md` | macOS `flutter create --platforms=ios` procedure |
| `mobile/android/RELEASE_SIGNING.md` | Release keystore setup (no secrets) |
| `mobile/android/key.properties.example` | Placeholder signing properties |
| `mobile/test/api_config_test.dart` | ApiConfig helper tests |

---

## Android configuration

### BEFORE
- Emulator default `10.0.2.2:8001` worked; physical device required dart-define with minimal in-app guidance.
- Release builds always used debug signing with a TODO comment.

### AFTER
- **FIXED:** `ApiConfig.physicalDeviceRunCommand()` and `physicalDeviceHint` centralize the documented run command.
- Home + server screens show emulator vs physical instructions.
- **DOCUMENTED:** `android/RELEASE_SIGNING.md` + `key.properties.example`.
- **FIXED:** `build.gradle.kts` uses release keystore when `android/key.properties` exists; otherwise debug fallback (demo only).

### Physical device command (documented, not hardcoded)

```powershell
cd mobile
flutter run -d <device-id> --dart-define=API_BASE_URL=http://<PC-IP>:8001
```

Backend:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

**Physical E2E:** NOT VERIFIED in this session (no device attached).

---

## API configuration

### BEFORE
- `--dart-define=API_BASE_URL` only; scattered comments.

### AFTER
- **FIXED:** Single mechanism preserved; `docs/API_CONFIGURATION.md` documents:

| Platform | Default | Physical device |
|----------|---------|-----------------|
| Android emulator | `http://10.0.2.2:8001` | `--dart-define=API_BASE_URL=http://<PC-IP>:8001` |
| Android physical | — | same dart-define |
| iOS Simulator | `http://127.0.0.1:8001` | — |
| iPhone physical | — | same dart-define (macOS) |

No IP addresses hardcoded in source.

---

## Error handling

### BEFORE
- `status: ok` with missing/malformed `measurements` could throw `TypeError` → raw `'Erreur inattendue : $e'` in UI.

### AFTER
- **FIXED:** `AnalysisResponseValidator.validateOkResponse()` runs before navigation.
- **FIXED:** `ApiExceptionKind.invalidResponse` with user message:
  - `'Réponse serveur incomplète : mesures absentes ou invalides.'`
  - `'Réponse serveur incomplète : format de données invalide.'`
- **FIXED:** Generic catch shows friendly message without exception text.
- Valid V2/V5 responses unchanged.
- `status: error` from backend still surfaces `error.message` (measurement/analysis errors not hidden).

### Tests added

1. status ok + valid measurements — PASS  
2. status ok + missing measurements — PASS (`invalidResponse`)  
3. status ok + malformed measurements — PASS (`invalidResponse`)  
4. malformed JSON — PASS (existing)  
5. HTTP error — PASS (existing 422/500)  
6. timeout — PASS (new)

---

## Release signing status

| Item | Status |
|------|--------|
| Production keystore committed | **No** (by design) |
| `key.properties` gitignored | **Yes** (pre-existing) |
| Release build without `key.properties` | Debug signing — **demo only** |
| Developer instructions | **DOCUMENTED** in `android/RELEASE_SIGNING.md` |

**NOT FIXED:** Production signing (requires developer-provided keystore).

---

## README status

### BEFORE
- Referenced `POST /measurements` and minimal platform notes.

### AFTER
- **FIXED:** `POST /analyze`, API configuration table, links to E2E / iOS / release docs, HTTP security notice.

---

## iOS status

### BEFORE
- `mobile/ios/` absent; no setup guide.

### AFTER
- **DOCUMENTED:** `docs/IOS_SETUP.md` with exact Mac command:
  ```bash
  cd mobile && flutter create . --platforms=ios
  ```
  Plus Info.plist permissions, ATS note, physical iPhone dart-define.
- **BLOCKED:** iOS project not generated on Windows (per instructions).
- **iOS build requires macOS + Xcode for final verification.**

---

## Memory status

### BEFORE
- Full-image decode + re-encode in RAM; risk noted in Phase 3A.

### AFTER
- **DOCUMENTED:** Comment in `image_normalizer.dart` describing RAM use up to 25 MB upload limit.
- **NOT FIXED:** No downscale/pre-upload optimization (would risk coordinate semantics).

---

## HTTP status

### BEFORE
- Cleartext enabled for Android MVP.

### AFTER
- **DOCUMENTED:** LAN/development-only notice in README, `API_CONFIGURATION.md`, and `network_security_config.xml` comment.
- **NOT FIXED:** No TLS infrastructure added (out of scope).

---

## Layout status

### BEFORE
- `_InfoRow` used fixed 160 px label width — potential tight layout on narrow screens.

### AFTER
- **FIXED:** `Flexible` + `Expanded` flex ratio for label/value.
- **FIXED:** Widget test at 320 px width — no overflow exception.

---

## Tests

### Flutter

```powershell
cd mobile
C:\Users\g\flutter\bin\flutter.bat test
```

**Result:** `61 passed, 0 failed` (was 47 — +14 new tests)

### Backend

```powershell
python -m unittest discover -s backend\tests -v
```

**Result:** `Ran 167 tests — OK (skipped=1)`

### Android debug build

```powershell
C:\Users\g\flutter\bin\flutter.bat build apk --debug
```

**Result:** `√ Built build\app\outputs\flutter-apk\app-debug.apk`

### Regression

| Area | Status |
|------|--------|
| V5 integration tests | PASS |
| V2 backward compatibility | PASS |
| Backend unchanged | PASS |

---

## Remaining blockers

| Blocker | Status | Next action |
|---------|--------|-------------|
| iOS project absent | **BLOCKED** | Run `flutter create . --platforms=ios` on macOS |
| Physical Android E2E | **NOT VERIFIED** | Execute `docs/TEST_MOBILE_E2E.md` with real device |
| Production release signing | **DOCUMENTED** | Provide local `key.properties` + keystore |
| Large radiograph RAM | **DOCUMENTED** | Profile on device; optimize only if needed |
| HTTPS for non-LAN | **DOCUMENTED** | Future infrastructure |

---

## Final verdict

### `CROSS_PLATFORM_ROBUSTNESS_READY`

All Phase 3B fixable items on Windows are complete: defensive API parsing, Android API documentation, release signing template, README correction, layout hardening, and full test/build regression.

Cross-platform **demo execution** remains blocked on **iOS project generation (macOS)** and **unverified physical Android E2E** — documented, not claimed as passed.

**Stopped** — no UI redesign, model changes, or dependency upgrades performed.
