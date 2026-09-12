# Phase 10H — Real End-to-End Validation Report

**Date:** 2026-09-04  
**Scope:** Validation only. No new functionality. No training.  
**Images:** existing `datasets/yolo_pose_new_26/images/{train,val}` PNGs — not modified.

---

## 17. Final verdict

# **PHASE_10H_VALIDATION: PASS_WITH_MINOR_ISSUES**

Integration of import → V5 `/analyze` → AI baseline → `/measurements` recalculation → correction state → PDF consumer is **functionally consistent**. No P0/P1 defects found. No forbidden production/model/dataset/geometry files were modified in this phase.

Minor issues are **environment / residual-visual** (native Flutter picker, live InteractiveViewer zoom, and share-sheet PDF were not physically clicked) plus one **pre-existing V5 landmark-out-of-bounds observation** unrelated to Phase 10H.

---

## 1. Test environment

| Item | Value |
|------|--------|
| Host | Windows 10 (10.0.26200) |
| Backend | Live demo already running: `GET http://127.0.0.1:8001/health` |
| Health | `status=ok`, `version=0.2.0`, **`model_version=v5_phase2`** |
| Python | `.venv\Scripts\python.exe` |
| Flutter | `C:\Users\g\flutter\bin\flutter.bat` |
| App path under test | `mobile/` (ResultsScreen + PDF consumer from Steps A–F) |
| Git | **No `.git` repository** at project / mobile / backend / datasets roots — integrity via timestamps |
| This phase code changes | **None** except this report |

Real radiographs were sent to the **same** `POST /analyze` multipart field (`file`) the Flutter app uses. Native `file_picker` / Windows share sheet cannot be driven from this agent session.

---

## 2–3. Images tested and resolutions

Eight existing B26 AP pelvis PNGs. Mix of train/val, square vs landscape, ~2.1–4.3 MB.

| ID | Split | Resolution | Aspect | Bytes | Why selected |
|----|-------|------------|--------|------:|--------------|
| B26_01 | train | 2730×2665 | 1.024 | 2 105 428 | typical near-square |
| B26_05 | train | 3008×3008 | 1.000 | 4 293 526 | square / larger |
| B26_19 | train | 2825×2228 | 1.268 | 2 357 869 | wider landscape |
| B26_10 | val | 3039×2625 | 1.158 | 2 547 724 | ASL_L Phase 10G SUCCESS but visibly displaced |
| B26_13 | val | 3234×2961 | 1.092 | 2 574 437 | ASL_L FAILURE (problematic) |
| B26_17 | val | 2763×2442 | 1.131 | 3 547 234 | ASL_L FAILURE near-miss |
| B26_20 | val | 2701×2514 | 1.074 | 3 308 566 | ASL_L STRONG SUCCESS |
| B26_26 | val | 2822×2426 | 1.163 | 4 041 400 | ASL_L FAILURE; FSP/FSD candidate |

`coordinate_space.image_width/height` matched the PNG size on every case. `landmark_coordinate_space` = `original_image_pixels`.

---

## 4. TEST A / B — Import + AI baseline

All 8: HTTP 200, `status=ok`, `model_version=v5_phase2`, **14 refined + 14 raw** landmarks, overlay payload present.

| ID | Infer (s) | Overlay | Right VCE / Tönnis / CCD | Left VCE / Tönnis / CCD | IT QC |
|----|----------:|---------|--------------------------|-------------------------|-------|
| B26_01 | 1.79 | OK | 41.70 / −5.13 / 135.20 | 44.39 / −10.68 / 163.10 | IT_R accept; IT_L **review** (`insufficient_caudal_vs_fhc`) |
| B26_05 | 1.11 | OK | 40.66 / −7.33 / 136.83 | 39.85 / −8.96 / 146.16 | IT_R accept; IT_L **review** (`high_confidence_marginal_it_fsd`) |
| B26_19 | 1.36 | OK | 40.48 / −4.14 / 135.15 | 43.48 / −10.44 / 138.19 | both accept |
| B26_10 | 1.30 | OK | 38.68 / −6.58 / 133.55 | 39.96 / −11.61 / 132.32 | both accept |
| B26_13 | 5.36 | OK | 44.37 / −5.50 / 135.69 | 39.87 / −10.68 / 143.32 | both accept |
| B26_17 | 4.77 | OK | 41.26 / −4.40 / 135.76 | 41.87 / −12.01 / 147.13 | both accept |
| B26_20 | 2.73 | OK | 47.96 / −10.75 / 136.37 | 40.19 / −7.74 / 145.52 | both accept |
| B26_26 | 1.25 | OK | 47.25 / −5.82 / 130.71 | 36.81 / −9.57 / 125.15 | IT_R **review** (`high_confidence_marginal_it_fsd`); IT_L accept |

**AI-only confirmations**

- `/measurements` with the **same** refined 14 MVP landmarks reproduced `/analyze` angles to machine precision (AI round-trip). That is the integration equivalent of “measurements correspond to the AI state”.
- Opening ResultsScreen does **not** call `/measurements` — covered by `landmark_recompute_test` **D**.
- Correction status starts **AI_ONLY** (`correctedCount=0`) — covered by `landmark_correction_state_test` + PDF snapshot tests.
- Source landmarks for display/PDF/correction are `refined_landmarks`, never `raw_landmarks`.
- Images were **read-only**; PNG files and labels were not rewritten.

Displayed priority landmarks (AI, `original_image_pixels`):

| ID | ASL_L (x,y) | FSP_L (x,y) | FSD_L (x,y) |
|----|-------------|-------------|-------------|
| B26_01 | 2240.43, 1098.57 | 2177.00, 2059.53 | 2218.68, 2533.27 |
| B26_10 | 2489.51, 832.83 | 2467.95, 1882.04 | 2384.38, 2342.55 |
| B26_13 | 2579.77, 833.77 | 2614.49, 1879.26 | 2591.19, 2401.14 |
| B26_26 | 2373.57, 630.89 | 2413.12, 1718.86 | 2311.22, 2269.24 |

This is an **integration** record, not a clinical accuracy study.

---

## 5. TEST C — Landmark correction (3 images)

Programmatic moves of current refined coordinates, then `POST /measurements` with the 14-point payload (same contract as `MeasurementsApiMapper`).

| Case | Landmark | Before (x,y) | After (x,y) | Status expected |
|------|----------|--------------|-------------|-----------------|
| B26_13 | ASL_L (difficult) | 2579.77, 833.77 | 2604.77, 851.77 | AI → CORRECTED, N=1 |
| B26_10 | ASL_L | 2489.51, 832.83 | 2469.51, 847.83 | AI → CORRECTED, N=1 |
| B26_26 | FSP_L | 2413.12, 1718.86 | 2431.12, 1696.86 | AI → CORRECTED, N=1 |

Flutter widget tests (`landmark_correction_ui_test`, `landmark_recompute_test`) additionally verify:

- selection of correctable names only (ASL/FSP/FSD L/R)
- drag follows `localDisplayToImage` (no hardcoded offset)
- `originalAiLandmarks` stay frozen
- `LandmarkStatus.corrected` + `PARTIALLY_CORRECTED`

---

## 6. TEST D — Zoom / coordinate mapping

**Live InteractiveViewer zoom on real B26 PNGs was not physically performed** (no desktop UI automation).

Automated evidence (no systematic offset found):

- `image_contain_layout_test`: `toImage` is the exact inverse of `toDisplay` under letterbox, pillarbox, extreme aspects, different box sizes; **composes with an external zoom transform** (InteractiveViewer-like); saved coords stay in `original_image_pixels`.
- `landmark_correction_ui_test`: `localDisplayToImage uses original_image_pixels`.
- All 8 live `/analyze` responses: `coordinate_space` dimensions = PNG size.

No inverted axes, no hardcoded offsets, no formula compensation applied.

**Remaining visual checklist** (Windows or Android, optional 5 minutes):

1. Import B26_13 and B26_19 (different aspects).
2. Corriger les landmarks — move ASL_L with **no zoom**.
3. Zoom in — move FSP_L — zoom out; confirm the point stays on the intended anatomy.
4. If any systematic offset appears: **STOP**. Do not add offsets. File as P0.

---

## 7. TEST E — Recalculation

After each move: `POST /measurements` HTTP 200, 14 landmarks, coordinates = AI + explicit delta (image pixels).

**B26_10 — ASL_L (−20, +15)**

| | Right VCE / Tönnis / CCD | Left VCE / Tönnis / CCD |
|--|--------------------------|-------------------------|
| Before | 38.68 / −6.58 / 133.55 | 39.96 / −11.61 / 132.32 |
| After | 38.68 / −6.58 / 133.55 **unchanged** | **39.43 / −10.32** / 132.32 |

**B26_13 — ASL_L (+25, +18)**

| | Right VCE / Tönnis / CCD | Left VCE / Tönnis / CCD |
|--|--------------------------|-------------------------|
| Before | 44.37 / −5.50 / 135.69 | 39.87 / −10.68 / 143.32 |
| After | 44.37 / −5.50 / 135.69 **unchanged** | **43.02 / −8.33** / 143.32 |

**B26_26 — FSP_L (+18, −22)**

| | Right VCE / Tönnis / CCD | Left VCE / Tönnis / CCD |
|--|--------------------------|-------------------------|
| Before | 47.25 / −5.82 / 130.71 | 36.81 / −9.57 / 125.15 |
| After | 47.25 / −5.82 / 130.71 **unchanged** | 36.81 / −9.57 / **123.81** |

Observation (no formula change): contralateral side unchanged; ASL_L moved **left VCE + Tönnis** only; FSP_L moved **left CCD** only. Matches geometric dependence. Flutter test **E/A/B** confirms one `/measurements` call after drag with corrected image coords.

---

## 8. TEST F — Undo

Covered by:

- `landmark_correction_state_test` — single- and multi-level undo restores positions/status
- `landmark_correction_ui_test` — UI undo
- `landmark_recompute_test` **H** — undo to AI restores original `/analyze` measurements **without** a new `/analyze` or stale overwrite

Not re-driven on the live HTTP session (undo is client-side).

---

## 9. TEST G — Reset

Covered by:

- `landmark_correction_state_test` — restore AI coords, statuses AI, undo cleared
- `landmark_correction_ui_test` — confirmation dialog; dismiss leaves corrections
- `landmark_recompute_test` **I** — original `/analyze` measurements restored, no `/analyze`

---

## 10. TEST H — PDF

Consumer architecture confirmed (Step F). No PDF redesign. Disclaimer unchanged:

> Ce rapport présente des mesures coxométriques issues d'une analyse assistée par IA. Les résultats doivent être vérifiés par un professionnel qualifié et ne constituent pas à eux seuls un diagnostic médical. Aucune certification de dispositif médical n'est revendiquée.

| Case | Evidence | Result |
|------|----------|--------|
| 1 AI_ONLY | `report_pdf_correction_test` 1, 4, 9, 10 + `results_export_ui_test` snapshot | landmarks = refined; measures = `/analyze`; label **Analyse : IA** |
| 2 corrected | tests 2, 3, 5, 8 | `currentLandmarks` + displayed measures; **Analyse : IA + correction manuelle (N)**; N = `correctedCount` |
| 3 undo → AI | test 7 | PDF state returns to AI |
| 4 reset → AI | test 6 | PDF state returns to AI |

Native share-sheet visual inspection of a generated file was **not** performed in this session.

---

## 11. TEST I — Error behavior

Live `/measurements` failure was **not** injected against production. Existing automated coverage:

- `landmark_recompute_test` **J/K**: API failure keeps previous valid measurements **and** corrected landmarks; snackbar + retry; no inference.

---

## 12. TEST J — Stale response

Manual A-then-B race was **not** reproduced on the live server. Covered by `landmark_recompute_test` **L** (`_recomputeGeneration` ignores the older response).

---

## 13. Automated test totals

### Flutter — required Phase 10H list

`landmark_correction_state_test`, `landmark_correction_ui_test`, `landmark_recompute_test`, `measurements_api_mapper_test`, `api_service_test`, `landmark_overlay_test`, `image_contain_layout_test`, `results_export_ui_test`, `report_pdf_correction_test`, `report_pdf_test`, `v5_integration_test`

**115 passed, 0 failed**

### Flutter — complete suite (`flutter test` in `mobile/`)

**163 passed, 0 failed**

### Backend — `/measurements`, geometry, schemas, analyze

```
pytest backend/tests/test_api.py
       backend/tests/test_measurement_service.py
       backend/tests/test_geometry_service.py
       backend/tests/test_schemas.py
       backend/tests/test_analyze_api.py
       backend/tests/test_analyze_api_v5.py
       backend/tests/test_analyze_coordinate_reprojection.py
```

**71 passed, 1 skipped, 0 failed**  
(skip: V2 checkpoint / optional integration gate — not a Phase 10H regression)

---

## 14. Git / integrity check

```
git status / git diff : unavailable (no .git at repo root, mobile, backend, or datasets)
```

Timestamp inspection (validation window ~2026-09-04 22:37 local). **None of these were written during this validation:**

| Path | LastWriteTime | Note |
|------|---------------|------|
| `mvp_geometry/` | 2026-08-24 | unchanged |
| `backend/app/api/routes/analyze.py` | 2026-09-04 16:55 | earlier today, **before** this phase |
| `backend/app/api/routes/measurements.py` | 2026-09-02 | unchanged |
| `backend/app/services/geometry.py` | 2026-09-02 | unchanged |
| `datasets/yolo_pose_new_26/images/` | 2026-08-23 | unchanged |
| `datasets/yolo_pose_new_26/labels/` | 2026-08-29 | unchanged |
| `yolo11n-pose.pt` | 2026-08-23 | unchanged |
| V5 Phase 2 checkpoint copies under `datasets/yolo_pose_new_26/_v5_*` | 2026-08-29 / 2026-09-02 | unchanged |

**This phase created only:** `datasets/yolo_pose_new_26/phase10h_validation_report.md`  
Helper script lived outside the repo (`%TEMP%\phase10h_validate.py`) and did not alter images.

---

## 15–16. Bugs found and severity

| ID | Severity | Description | Action |
|----|----------|-------------|--------|
| — | — | No P0 (coordinate corruption / wrong measurement state) | — |
| — | — | No P1 (workflow broken) | — |
| OBS-1 | P3 / pre-existing | B26_19 `FSD_L.y` ≈ 2352 while image height is 2228 (V5 prediction slightly outside canvas). Not introduced by 10H; no offset added. | Observe only |
| LIM-1 | P3 / validation gap | Native Flutter import picker, live zoom-drag on B26 PNGs, and OS PDF share sheet were not physically clicked | Optional visual pass below |

No heuristic, offset, or formula change was applied.

---

## 14b. Acceptance criteria

| Criterion | Result |
|-----------|--------|
| Real image import works | **PASS** (same `/analyze` multipart the app uses; 8/8) |
| V5 inference works | **PASS** (`v5_phase2`, 8/8) |
| AI landmarks display correctly | **PASS** (14 refined, `original_image_pixels`; widget overlay tests) |
| AI measurements display correctly | **PASS** (round-trip `/measurements` matches `/analyze`) |
| Correction mode works | **PASS** (automated UI) |
| ASL/FSP/FSD drag works | **PASS** (automated + live coord updates) |
| Coordinates correct, normal display | **PASS** (contain inverse + live space) |
| Coordinates correct with zoom | **PASS automated**; live B26 zoom not physically clicked |
| No systematic coordinate offset | **PASS** (no defect found) |
| Correction status works | **PASS** |
| `/measurements` gets corrected image coords | **PASS** |
| Recalculated measurements appear | **PASS** (side- and measure-selective) |
| Undo works | **PASS** (automated) |
| Reset works | **PASS** (automated) |
| AI measures restored at AI_ONLY | **PASS** |
| PDF AI / corrected / undo / reset | **PASS** (Step F tests) |
| Automated regression | **PASS** (163 Flutter + 71 backend) |
| No forbidden modifications | **PASS** |

---

## 18. Recommendation for next phase

1. **Review this report before Phase 11 / any retraining.** Do not start ASL/FSP/FSD training or dataset expansion from this validation.
2. Optional **5-minute visual demo** on Windows (`flutter run -d windows`) or Android using B26_13 and B26_19: import → correct → zoom → undo/reset → export PDF. If a systematic overlay offset appears, treat as **P0** and stop.
3. Phase 10H client bridge (correction state, `/measurements` consumer, PDF snapshot) is **ready to keep**. Clinical landmark accuracy remains a **model** topic, not a 10H client defect.

---

## Manual visual procedure (remaining only)

```
.\backend\run_demo.ps1          # already v5_phase2 on :8001
cd mobile
flutter run -d windows
```

For B26_13.png then B26_19.png:

1. Importer une image → Analyser  
2. Record AI VCE / Tönnis / CCD (should match the tables above within rounding)  
3. Corriger les landmarks → drag ASL_L → confirm left VCE/Tönnis update  
4. Zoom in / move / zoom out  
5. Undo → AI measures  
6. Correct again → Reset (dialog) → AI measures  
7. Export PDF AI_ONLY then after one correction  

**STOP after this report.** No Phase 11, no retraining, no heuristics.
