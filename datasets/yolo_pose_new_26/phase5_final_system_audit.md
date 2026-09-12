# Phase 5 — Final System Audit / Pre-Demo Audit

**Date:** 2026-09-04  
**Mode:** READ-ONLY — no source, model, dataset, checkpoint, dependency, UI, backend, Flutter, or documentation modifications except this report  
**Scope:** End-to-end coxometry application (image → inference → QC → geometry → API → Flutter → UX)  
**Prior validated state cited:** V2 production baseline · V5 16-landmark · V5 Phase 2 IT head · independent validation · checkpoint + FastAPI + IT QC + Flutter V5 · Phase 3 robustness · Phase 4B UX  

---

## 1. Executive summary

The production pipeline is **intact and coherent**. V2 remains the default production detector; V5 Phase 2 remains an explicit opt-in via `MODEL_VERSION`. Clinical geometry (VCE / Tönnis / CCD) is unchanged. IT QC states `accept` / `review` / `unavailable` propagate correctly and REVIEW is **not** mapped to API failure or UI “success-as-error”. Phase 4B decluttered the demo surface (French loading, honest status, collapsed technical details, larger overlay + shared InteractiveViewer, legend).

**Live regression this audit:**

| Suite | Result |
|-------|--------|
| Flutter `flutter test` | **70 passed**, 0 failed |
| Backend `python -m unittest discover -s backend\tests -v` | **167 OK**, **1 skipped** (~155.5 s) |
| Android `flutter build apk --debug` | **Success** → `mobile/build/app/outputs/flutter-apk/app-debug.apk` |

**No P0 blockers** for an Android + local-backend demo.

**Final verdict:** **`DEMO_READY_WITH_P1_ITEMS`**

P1 items are documentation/ops/clarity gaps (not model or geometry regressions). See §15–§16.

---

## 2. Architecture map

### 2.1 End-to-end pipeline

```
Flutter Home (gallery/camera)
  → EXIF bake / normalize (image_normalizer.dart)
  → Preview
  → AnalysisScreen → ApiService POST /analyze (multipart field `file`)
       ↓
FastAPI backend.main:app
  → validate_upload_metadata (size ≤ 25 Mo, PNG/JPG/JPEG)
  → MODEL_VERSION → preprocess_image (V2 512² gray) | preprocess_image_v5 (640² RGB)
  → get_landmark_detector()
       ├─ v2: YoloPoseLandmarkDetector (Ultralytics best.pt)
       └─ v5_phase2: V5Phase2LandmarkDetector
            ├─ YOLO V2 subdetector → 14 KP + bbox @640
            └─ V5 forward_head_preds → IT_R(14) / IT_L(15)
  → run_measurement_pipeline
       → detect()
       → reproject landmarks + IT → original_image_pixels
       → assess_it_landmarks_qc (V5 only, when IT present)
       → compute_all_sides (mvp_geometry) on preprocessed 14 KP
  → AnalyzeSuccessResponse | AnalyzeErrorResponse
       ↓
Flutter parse (AnalysisResult) → ResultsScreen
  → LandmarkOverlay (BoxFit.contain + InteractiveViewer on shared tree)
  → ResultPresentationStatus (success | review | incomplete)
  → measurements + IT status + collapsed technical details
```

**Export / PDF report:** **not present** (by design). Workflow ends at Results + “Nouvelle radiographie”.

### 2.2 Entry points

| Layer | Entry |
|-------|--------|
| Backend process | `uvicorn backend.main:app --host 0.0.0.0 --port 8001` |
| HTTP clinical path | `POST /analyze` (`backend/app/api/routes/analyze.py` → `run_analyze_from_bytes`) |
| HTTP legacy / lab | `POST /measurements` (manual landmarks / image + geometry only) |
| Health | `GET /health` |
| Flutter | `mobile/lib/main.dart` → `HomeScreen` |
| Model selection | env `MODEL_VERSION` ∈ {`v2` (default), `v5` / `v5_phase2` / `phase2`} via `model_factory.py` |

### 2.3 Important files

| Role | Path |
|------|------|
| FastAPI app | `backend/main.py` |
| Analyze orchestration | `backend/app/services/analyze.py` |
| Measurement + QC hook | `backend/app/services/measurement_service.py` |
| V2 detector | `backend/app/services/detection/yolo_pose.py` |
| V5 detector | `backend/app/services/detection/v5_phase2_pose.py` |
| IT QC | `backend/app/services/detection/v5_it_qc.py` |
| Reprojection | `backend/app/services/detection/reprojection.py` |
| Factory | `backend/app/services/detection/model_factory.py` |
| Schemas | `backend/app/schemas/analyze.py` |
| Geometry | `mvp_geometry/hip_measures.py`, `measurements.py`, `landmarks.py` |
| Dataset YAML | `datasets/yolo_pose_new_26/data.yaml`, `dataset.yaml` |
| Flutter API / models / UI | `mobile/lib/services/api_service.dart`, `models/*`, `screens/*`, `widgets/landmark_overlay.dart`, `utils/result_status.dart` |

### 2.4 Service boundaries

- **API** = HTTP only.  
- **Detection** = landmarks (+ optional IT); no clinical angles.  
- **QC** = reliability labels only; does not rewrite `v`/`x`/`y`.  
- **Geometry** = pure functions on usable landmarks; no diagnosis.  
- **Flutter** = presentation; presentation status derived from API fields only.

### 2.5 V2 / V5 compatibility

| Aspect | Mechanism |
|--------|-----------|
| Default | V2 (`MODEL_VERSION` unset) |
| V5 | Explicit env; V5 preprocess 640 RGB; hybrid V2@640 + IT head |
| API | `model_version`: `v2` \| `v5_phase2`; V2 → `it_landmarks=[]` |
| Flutter | Empty IT hides IT section; parses optional quality fields |
| Geometry | Always uses 14 MVP landmarks only (IT never enters VCE/Tönnis/CCD) |

### 2.6 Error path

Upload validation → preprocess errors → detector structured errors (`ModelNotFound`, `NoDetection`, …) mapped to French client messages → geometry pelvis failure → Flutter `ApiException` on Analysis screen (retry). Results screen never invents API errors.

### 2.7 Dead / duplicated critical paths

| Path | Assessment |
|------|------------|
| `POST /analyze` | **Canonical** clinical path |
| `POST /measurements` | **Legacy / lab** still registered — not dead; not used by Flutter |
| `pipeline.py` / `geometry.py` / `landmark_detection.py` | Support `/measurements` and older services; not the Flutter path |
| Dual preprocess | Intentional V2 vs V5; not duplication of geometry |
| V5 imports `train_yolo_pose_v5_phase2.py` for `build_model` | Coupling to training script for architecture load only; **no training** invoked at inference |

**No competing Flutter analyze clients.** Single `ApiService.analyzeRadiograph`.

---

## 3. Model / AI audit

### 3.1 Checkpoints (intact on disk)

| Model | Path | Size | mtime | SHA256 |
|-------|------|------|-------|--------|
| **V2** | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` | 5 947 464 | 2026-08-23 18:12:41 | `1F92D0867B4CD86EB6A4E3EC6111F812824B1B0D4D8DCD1D1EBE6C00EF2C48B8` |
| **V5 Phase 2** | `runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/weights/best_it.pt` | 24 963 226 | 2026-08-29 03:36:09 | `2E3D3E48C800C1583D427844AF84835EF0115E6456EC1F6096A4ACECEDB257F6` |

Matches `DEFAULT_V2_MODEL_PATH` and `DEFAULT_V5_CHECKPOINT` in code. Checkpoint mtimes predate Phase 4B (2026-09-04 Flutter-only edits).

### 3.2 Keypoint contract

| Check | Status |
|-------|--------|
| V5 `kpt_shape` / 16×3 | Confirmed in YAML + detector audit (`n_keypoints_total: 16`) |
| IT_R index **14** | `IT_KP_INDICES = (14, 15)` |
| IT_L index **15** | Confirmed |
| V2 keypoints 0–13 | YOLO V2 + `MVP_LANDMARK_NAMES` (14 names); adapter parses 14 KP |
| V5 base / frozen zone | Prior checkpoint audit: backbone/neck/cv4 frozen; IT head only |
| UX phase model edits | **None** — Phase 4B touched Flutter presentation only |
| Training in production path | `build_model` / `load_state_dict` / `eval` / `forward_head_preds` only — no `--train` |
| Fresh-process load | Validated historically (`CHECKPOINT_INFERENCE_READY`); tests load with `load_on_init=True` |
| Decoder single-stride | `decode_keypoints_px640` + `verify_single_stride` in detector |
| Reprojection | Letterbox inverse: `(x_prep - pad) / scale` → `original_image_pixels` |

### 3.3 Comparison to validated V5 architecture

Aligned with prior audits (`v5_phase2_checkpoint_integration_audit.md`, `v5_phase2_backend_integration_audit.md`): hybrid V2 bbox/14 KP + V5 IT at max-IoU anchor; confidence threshold 0.25; v=0 ⇒ no fabricated coordinates.

**No retrain performed in this audit.**

---

## 4. Dataset audit

| Check | Evidence | Status |
|-------|----------|--------|
| 26 images | 21 train + 5 val images & labels | **OK** |
| Split 21 / 5 | Directory counts | **OK** |
| 16 keypoints | `kpt_shape: [16, 3]` in `data.yaml` & `dataset.yaml` | **OK** |
| Label columns | All 26 labels = **53** cols (`1 + 4 + 16×3`) | **OK** (`BAD=0`) |
| `flip_idx` | `[1,0,3,2,5,4,7,6,9,8,11,10,13,12,15,14]` | **OK** |
| First 14 names | TD_R…FSD_L then IT_R, IT_L | **OK** |
| IT definitions | Documented in B5/B6 reports + YAML `kpt_names` | **OK** |
| v=0 policy | Conservative; coords `(0,0,0)` when non-identifiable; no FOV extrapolation (B5 QC) | **OK** (docs + prior QC) |
| Fabricated coords | Policy forbids; inference mirrors with v=0 | **OK** |

**Labels not modified this audit.**

---

## 5. Clinical geometry audit

**Sources:** `mvp_geometry/hip_measures.py` `_REQUIRED`, `measurements.py`  
**File mtimes:** `measurements.py` / `hip_measures.py` = **2026-09-02 00:58** (unchanged during Phase 4B Flutter work).

| Measure | Required landmarks | Status |
|---------|-------------------|--------|
| **VCE / Wiberg** | TD_R, TD_L, FHC_{side}, ASL_{side} | **Unchanged** |
| **Tönnis** | TD_R, TD_L, ASM_{side}, ASL_{side} | **Unchanged** |
| **CCD** | FHC, FNM, FSP, FSD (per side) | **Unchanged** |

| Aspect | Finding |
|--------|---------|
| Landmark indices / names | Via MVP names; IT never in `_REQUIRED` |
| Side handling | `_resolve` / `_lateral_direction` R/L; CCD side-independent vectors |
| Coordinate space | Angles from preprocessed detections (scale-invariant); API exposes original-space landmarks for overlay |
| Missing landmarks | `available=false` + reason; no invented points |
| Diagnostic interpretation | **None** in API or Flutter measurement cards (degrees / `—` only). Docstrings mention clinical meaning of signs; UI does not classify normal/pathologic |

---

## 6. IT QC audit

**Module:** `backend/app/services/detection/v5_it_qc.py`  
**Integration:** `measurement_service._build_detection_out` after IT reprojection.

| Status | Meaning | Propagation |
|--------|---------|-------------|
| `accept` | Passes conservative checks | API `quality` + Flutter green “Accepté”; drawable |
| `review` | Exposed coords, uncertain reliability | API + warning banner “Vérification recommandée”; orange IT marker + ring; **not** analysis failure |
| `unavailable` | v=0 / hard fail | API + “Indisponible”; **not drawn**; incomplete presentation if measures also missing |

| Rule family | Codes (examples) | Severity |
|-------------|------------------|----------|
| Visibility | `model_v0` | unavailable |
| Bounds | `out_of_image_bounds` | unavailable |
| Patient side | `wrong_patient_side` | unavailable |
| Lateral / caudal | `weak_lateral_placement`, `insufficient_caudal_vs_*` | review |
| Bilateral | asymmetry → review; `bilateral_order_violation` → unavailable |
| Confidence | `low_model_confidence`, `high_confidence_marginal_it_fsd` | review |

**Frontend:** French badges; REVIEW prioritized over success; incomplete separate from review.  
**Gap (P1):** `Motif` still shows **raw English reason codes** (e.g. `high_confidence_marginal_it_fsd`).

**Confirm:** REVIEW is **not** converted into HTTP error or Results “failure”.

---

## 7. Backend API audit

### 7.1 `POST /analyze`

| Step | Status |
|------|--------|
| Multipart `file` / `image` | OK |
| Preprocess V2/V5 | OK |
| Detector via factory + DI | OK |
| Reprojection + QC + geometry | OK |
| JSON schema | `AnalyzeSuccessResponse` / `AnalyzeErrorResponse` |
| `coordinate_space` | widths/heights, scale, pads, `landmark_coordinate_space=original_image_pixels` |
| Errors | French sanitized codes/messages |
| Malformed client handling | Flutter validates ok payloads; backend Pydantic schemas |
| V2 compatibility | Empty `it_landmarks`, `model_version=v2` |

### 7.2 Documentation drift (P1)

| Artifact | Issue |
|----------|--------|
| `backend/README.md` | Still claims YOLO stub / AI **not implemented** / upload not exposed — **false** vs current code |
| `backend/main.py` OpenAPI description | Emphasizes MVP + V2; understates V5 |
| Route docstring `/analyze` | Still “YOLO Pose V2” only |
| `POST /measurements` | Still valid legacy endpoint — Flutter unused; OK if documented as such |

No API contract change found from Phase 4B.

---

## 8. Flutter audit

| Area | Status |
|------|--------|
| Home | Decluttered; AppBar server diagnostics only; FR copy |
| Preview | Radiograph + Analyse |
| Loading | FR: “Analyse de la radiographie…” / anatomical subtitle — **no YOLO** |
| Results | Status banner + measures + IT + legend + mismatch banner |
| Overlay | `BoxFit.contain` only; `ImageContainLayout`; **InteractiveViewer wraps shared image + CustomPaint** |
| Status | `ResultPresentationStatus` — review ≠ fail |
| IT quality | Accepté / À revoir / Indisponible |
| Detection details | Collapsed “Détails techniques” |
| API service | 120 s analyze / 15 s health; malformed/empty/422/5xx handled |
| Models | 16-aware IT; V2 empty IT OK |
| Coordinate mapping | Prefer backend `coordinate_space`; mismatch warning |
| Responsive | Overlay height ~45% clamped 280–520; narrow-width test |
| Accessibility | Semantics on overlay, legend, status, IT badges |
| User-facing EN/YOLO | Removed from normal path (Phase 4B) |
| Residual jargon | Expandable “Landmarks MVP”; English QC codes in Motif |
| Export | Absent |

`ITQuality.label` English (`ACCEPT`/`REVIEW`) exists on the enum but **UI badges use French**, not `.label`.

---

## 9. UX / medical demo audit

Evaluated post–Phase 4B (no redesign).

### A) Orthopedic surgeon

| Pri | Finding |
|-----|---------|
| P1 | REVIEW Motif codes in English snake_case hurt trust/clarity |
| P1 | Demo must run backend with `MODEL_VERSION=v5_phase2` or IT never appears (default V2) |
| P2 | Nested scroll vs pinch-zoom friction |
| P2 | Landmark labels can collide on dense overlays |
| P3 | Heart-monitor home icon weakly related to pelvis |

Clarity of VCE/Tönnis/CCD: **good**. Uncertainty: **good** at banner/badge level.

### B) Radiologist

| Pri | Finding |
|-----|---------|
| P1 | Same English Motif codes |
| P2 | No DICOM path (JPEG/PNG only) — expected for MVP demo |
| P2 | Preview metadata (px/size) slightly technical |
| P3 | No structured report export |

Landmark visualization + REVIEW ring: **adequate** after Phase 4B.

### C) University jury

| Pri | Finding |
|-----|---------|
| P1 | `backend/README.md` contradiction vs live system — credibility risk if opened |
| P1 | OpenAPI/title still “MVP” / V2-centric |
| P2 | Residual “MVP” label in technical expander |
| P3 | iOS absent (documented; Android demo viable) |

Workflow friction: **low** on Android emulator with documented API URL.

### D) Developer / software quality

| Pri | Finding |
|-----|---------|
| P2 | V5 detector depends on training script import for `build_model` |
| P2 | Dual `/analyze` + `/measurements` needs clear “supported product path” docs |
| P3 | Large radiograph RAM (decode full image ≤ 25 Mo) — documented, not optimized |

---

## 10. Edge-case audit

| Case | Expected / observed behavior | Risk |
|------|------------------------------|------|
| Invalid / corrupt image | Preprocess → `invalid_image`; Flutter error + retry | Low |
| Very large (>25 Mo) | Client + server reject `file_too_large` | Low |
| Very small | Preprocess/detect may fail → structured error | Low |
| Portrait / landscape | Letterbox contain; overlay contain | Low |
| Malformed JSON / empty body | Flutter `invalidJson` / `invalidResponse` | Low |
| API unavailable / timeout | Network / timeout messages (120 s) | Low |
| Missing measurement | Card `—` + incomplete status | Low |
| Missing landmark | Geometry unavailable reason | Low |
| IT v=0 | `unavailable`, not drawn | Low |
| IT REVIEW | Warning status; still drawable | Low |
| Low confidence | QC review reason | Low |
| Coordinate mismatch | Banner; mapping uses backend dims | Low |
| Unexpected `model_version` | Backend clamps unknown → `v2` display path; Flutter shows raw string if non-null unknown | Low–Med |
| Crash / silent success on REVIEW | **Not observed** in code paths | — |

**No unsafe silent success** for IT REVIEW found.

---

## 11. Performance audit

*(Recorded from prior validated runs + this suite; no optimization.)*

| Metric | Source / value |
|--------|----------------|
| V5 IT infer_ms (val, prior audit) | ~123–176 ms per image (CPU path in checkpoint audit) |
| Model load | Cold load of V2 + V5 (~25 Mo state) — first request slower; not re-timed this audit |
| Full `/analyze` | Dominated by YOLO predict + optional V5; Flutter timeout **120 s** |
| Backend test wall | **155.5 s** for 167 tests (includes real model cases) |
| Flutter tests | **~32.5 s**, 70 tests |
| Debug APK build | **~27 s** this run |
| Flutter loading UX | Indeterminate spinner — honest; no fake progress |
| Image memory | Full decode/re-encode in RAM up to upload cap 25 Mo — risk on low-end devices (documented Phase 3B) |

---

## 12. Android / iOS audit

### Android

| Item | State |
|------|--------|
| Debug APK | **Builds successfully** this audit |
| Permissions | `INTERNET`, `CAMERA`, `READ_MEDIA_IMAGES`, legacy storage |
| Cleartext HTTP | `usesCleartextTraffic=true` (LAN demo) |
| API config | `--dart-define=API_BASE_URL=...`; emulator default `http://10.0.2.2:8001` |
| Docs | `mobile/docs/API_CONFIGURATION.md`, `TEST_MOBILE_E2E.md`, README |
| Release signing | `android/RELEASE_SIGNING.md`; no production keystore in repo; release falls back to debug without `key.properties` |

### iOS

| Item | State |
|------|--------|
| `mobile/ios/` | **Absent** (`Test-Path` → False) |
| Generation | Documented Mac-only: `flutter create . --platforms=ios` in `docs/IOS_SETUP.md` |
| Requirements | macOS + Xcode + pods; camera/photo plist keys; ATS local networking for HTTP |
| This audit | **Did not generate** iOS project |

**Android is the demo platform on this Windows workspace.**

---

## 13. Test results (exact, this audit)

### Flutter

```
cd mobile
C:\Users\g\flutter\bin\flutter.bat test
→ 00:04 +70: All tests passed!
exit_code: 0
elapsed ~32.5 s
```

### Backend

```
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
→ Ran 167 tests in 155.507s
→ OK (skipped=1)
exit_code: 0
```

Skip: same historical asset-gated case (B26_01 real-model when asset absent) — consistent with Phase 4B report.

### Android

```
flutter build apk --debug
→ √ Built build\app\outputs\flutter-apk\app-debug.apk
exit_code: 0
elapsed ~26.7 s
```

**No tests added or modified.**

---

## 14. Regression findings (Phases 4A / 4B)

| Area | Regression? |
|------|-------------|
| V2 detection / default factory | **No** |
| V5 hybrid + indices 14/15 | **No** |
| VCE / Tönnis / CCD formulas | **No** (mtime 2026-09-02) |
| Coordinate mapping math | **No** (InteractiveViewer shared transform only) |
| IT QC states | **No** |
| API response schema | **No** |
| Flutter parsing V2/V5 | **No** (tests green) |
| Overlay contain + mismatch | **No** |
| Status honesty (REVIEW) | **Improved** in 4B (was always-success) |
| Responsive overlay height | **Improved** in 4B |
| Checkpoints / labels | **Untouched** |

**Conclusion:** Phase 4B did not regress model/geometry/API; it fixed presentation issues identified in Phase 4B audit.

---

## 15. P0 / P1 / P2 / P3 table

| ID | Pri | Area | Finding |
|----|-----|------|---------|
| — | **P0** | — | **None identified** |
| P1-1 | P1 | Demo ops | Backend default is **V2**; demo of 16 KP / IT requires `MODEL_VERSION=v5_phase2` |
| P1-2 | P1 | UX / trust | IT `Motif` shows raw English `quality_reasons` codes |
| P1-3 | P1 | Docs / jury | `backend/README.md` still describes stub / no AI / no upload — contradicts live system |
| P1-4 | P1 | Docs / API | FastAPI title/description & `/analyze` summary still V2/MVP-centric |
| P2-1 | P2 | UX | Pinch-zoom vs vertical scroll competition |
| P2-2 | P2 | UX | Dense landmark label collisions / edge clamp |
| P2-3 | P2 | Architecture | Production V5 loads architecture via training script import |
| P2-4 | P2 | Docs | Expandable “Landmarks MVP” jargon |
| P2-5 | P2 | Ops | Physical-device E2E not re-executed in this read-only session |
| P3-1 | P3 | Platform | No `ios/` until Mac generation |
| P3-2 | P3 | Product | No export/report |
| P3-3 | P3 | Perf | No pre-upload downscale (RAM risk ≤ 25 Mo) |
| P3-4 | P3 | UX | Home icon weakly pelvic |

---

## 16. Final demo verdict

# **DEMO_READY_WITH_P1_ITEMS**

**Not `DEMO_BLOCKED`:** core pipeline, tests, APK, geometry, IT QC, and Phase 4B UX are sound for an Android + LAN backend demonstration.

**Not full `DEMO_READY`:** the following **P1** items should be closed (or explicitly scripted around) before calling the demo presentation-perfect:

1. **P1-1** — Launch checklist: set `MODEL_VERSION=v5_phase2` (and document it on the demo run sheet).  
2. **P1-2** — French (or clinician-readable) mapping for IT QC Motif reasons.  
3. **P1-3** — Refresh `backend/README.md` to match the live `/analyze` + V2/V5 system (docs-only; out of scope for this audit to edit).  
4. **P1-4** — Align FastAPI OpenAPI title/description with V5 capability (docs/metadata only).

Until P1-1 is on the run sheet, a demo can **accidentally show V2-only** (no IT) — operational, not a code defect.

---

## 17. Recommended next steps

1. **Demo run sheet (immediate):**  
   - `MODEL_VERSION=v5_phase2`  
   - `uvicorn backend.main:app --host 0.0.0.0 --port 8001`  
   - Flutter: emulator default URL or `--dart-define=API_BASE_URL=http://<PC-IP>:8001`  
   - Walkthrough: import → analyse → show REVIEW case (e.g. known B26_26 behavior) → show VCE/Tönnis/CCD  
2. **Docs sync (short):** update `backend/README.md` + OpenAPI blurbs so jury docs match reality.  
3. **UX polish (optional before jury):** localize IT Motif strings; rename “Landmarks MVP” in expander.  
4. **Do not** retrain, change geometry, or alter checkpoints before demo.  
5. **iOS:** only if required — generate on Mac per `IOS_SETUP.md` (not needed for Windows Android demo).  
6. **Post-demo:** consider decoupling V5 `build_model` from the training script path (engineering debt).

---

## Audit integrity statement

- **Only deliverable written:** `datasets/yolo_pose_new_26/phase5_final_system_audit.md`  
- **No** source, model, dataset, checkpoint, dependency, test, UI, or config modifications  
- **Tests run only** as specified; results recorded above  

**End of Phase 5 final system audit.**
