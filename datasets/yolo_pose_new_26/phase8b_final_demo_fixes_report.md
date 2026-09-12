# Phase 8B — Final Demo Reliability Fixes Report

**Date:** 2026-09-04  
**Reference:** `datasets/yolo_pose_new_26/phase8a_final_pre_demo_audit.md`  
**Scope:** P1-1, P1-2, P1-3 only  

---

## Final verdict

# **PHASE8B_FINAL_DEMO_FIXES_COMPLETE**

---

## 1. Files modified

| Path | Change |
|------|--------|
| `mobile/lib/services/api_service.dart` | Parse `model_version` from `GET /health` into `HealthCheckResult.modelVersion` |
| `mobile/lib/screens/server_connection_screen.dart` | Display Modèle from health; prioritize `run_demo.ps1`; no-device demo guidance |
| `mobile/test/health_check_test.dart` | Assert `model_version` parsing (V5 + V2) |
| `mobile/test/server_connection_test.dart` | **Created** — UI shows V5/V2 from `/health`; no bare uvicorn tip |
| `mobile/README.md` | Validated no-device demo path; `run_demo.ps1` primary; camera caveat |
| `mobile/docs/API_CONFIGURATION.md` | Demo launcher priority; health model display; no-device note |
| `mobile/docs/CAMERA_CAPTURE.md` | Emulator ≠ physical validation; point to digital demo path |
| `mobile/docs/TEST_MOBILE_E2E.md` | Replace bare uvicorn with `run_demo.ps1`; health model checklist |
| `mobile/docs/IOS_SETUP.md` | Physical iPhone backend via `run_demo.ps1` / explicit V5 |
| `backend/README.md` | Official demo launcher + manual V5 section; warn bare uvicorn |

**Not modified:** models, checkpoints, dataset, labels, training, `mvp_geometry`, IT QC, inference, coordinate mapping, PDF measure content logic.

---

## 2. V2 launch ambiguity resolution (P1-1)

| Before | After |
|--------|-------|
| In-app Connexion serveur listed bare `uvicorn …` as step 2 | Recommends `.\backend\run_demo.ps1` and explains V2 risk without it |
| E2E / iOS docs used bare uvicorn as primary | Demo launcher first; manual V5 only with `$env:MODEL_VERSION = "v5_phase2"` |
| Developer could follow UI and get silent V2 | Following demo instructions forces V5 |

**Code default remains V2** when `MODEL_VERSION` is unset (compatibility unchanged).

---

## 3. Health model-version display (P1-2)

- `ApiService.checkHealth` reads `body['model_version']`.
- On success, UI shows discreetly: **`Modèle : V5 Phase 2`** or **`Modèle : V2`** via `formatModelVersion` (same helper as Results).
- Value comes from the live `/health` response — **not hardcoded**.
- No YOLO internals, checkpoint paths, or raw JSON dumps.

Widget keys: `health_model_version`, existing `health_check_result`.

---

## 4. No-device demo workflow (P1-3)

Documented **VALIDATED DEMO PATH**:

1. `.\backend\run_demo.ps1`
2. Confirm `/health` → `v5_phase2` (curl and/or Connexion serveur)
3. `flutter run -d windows` **or** Android emulator
4. **Importer une image** → known DICOM→PNG from `datasets/yolo_pose_new_26/images/…`
5. Analyse → résultats → PDF

**IMPLEMENTED BUT NOT PHYSICALLY VALIDATED:** camera UI/workflow. Emulator camera ≠ physical device. No clinical claim for négatoscope photos. Prototype disclaimer retained.

---

## 5. Documentation changes

Updated only docs needed to remove ambiguity:

- Mobile README (primary demo path)
- Backend README (launcher + manual V5)
- API configuration, camera, E2E, iOS setup
- In-app Connexion serveur copy

Distinction is explicit: digital import validated for demo; camera UI only.

---

## 6. Flutter tests

```
flutter test
→ All tests passed!
→ 102 passed (was 98; + health model_version + ServerConnectionScreen suite)
```

---

## 7. Backend tests

```
python -m unittest discover -s backend\tests -v
→ Ran 167 tests in ~157 s
→ OK (skipped=1)
```

No backend inference/code changes beyond README.

---

## 8. APK build

```
flutter build apk --debug
→ √ Built build\app\outputs\flutter-apk\app-debug.apk
```

---

## 9. V5 demo verification

```
.\backend\run_demo.ps1
GET http://127.0.0.1:8001/health
→ {"status":"ok","service":"coxometrie-backend","version":"0.2.0","model_version":"v5_phase2"}
```

Flutter unit/widget tests confirm Connexion serveur renders **Modèle : V5 Phase 2** / **Modèle : V2** from mocked `/health` bodies.

---

## 10. Safety confirmation

| Asset | Status |
|-------|--------|
| V2 / V5 models | **Unchanged** |
| Checkpoints | **Unchanged** |
| Dataset / labels | **Unchanged** |
| Training | **Unchanged** |
| `mvp_geometry` / VCE / Tönnis / CCD | **Unchanged** |
| IT QC rules | **Unchanged** |
| Inference architecture | **Unchanged** |
| Coordinate mapping | **Unchanged** |
| PDF calculation/content logic | **Unchanged** |

---

## 11. Remaining limitations

1. Physical Android camera still not validated (no device).  
2. Négatoscope photo accuracy still not clinically validated.  
3. Code default remains V2 if someone ignores demo docs (by design).  
4. Phase 8A P2 items (Landmarks MVP jargon, zoom/scroll, etc.) untouched.  
5. iOS project still not versioned.

---

**PHASE8B_FINAL_DEMO_FIXES_COMPLETE**
