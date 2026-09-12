# Phase 5 — P1 Demo Readiness Fixes

**Date:** 2026-09-04  
**Reference:** `datasets/yolo_pose_new_26/phase5_final_system_audit.md`  
**Verdict:** **`PHASE5_P1_FIXES_COMPLETE`**

---

## 1. Files modified

| File | Change |
|------|--------|
| `backend/run_demo.ps1` | **Created** — demo launcher forcing `MODEL_VERSION=v5_phase2` |
| `backend/main.py` | OpenAPI title/description; `/health` exposes `model_version` |
| `backend/app/api/routes/analyze.py` | OpenAPI route summary/docs (V2/V5 accurate) |
| `backend/app/schemas/analyze.py` | Field/schema descriptions for OpenAPI |
| `backend/app/services/detection/model_factory.py` | Docstrings clarifying V2 default vs demo |
| `backend/README.md` | Rewritten to match live implementation |
| `backend/tests/test_api.py` | Health asserts `model_version` present |
| `mobile/lib/utils/it_quality_reason_label.dart` | **Created** — FR mapping of QC reason codes |
| `mobile/lib/widgets/it_status_section.dart` | Shows French Motif (not raw codes) |
| `mobile/test/it_quality_reason_label_test.dart` | **Created** — mapping unit tests |
| `mobile/test/v5_integration_test.dart` | Expects French Motif, not English code |
| `mobile/README.md` | Demo launch via `run_demo.ps1` |
| `mobile/docs/API_CONFIGURATION.md` | Demo V5 backend instructions |

**Unchanged:** model weights, labels, `mvp_geometry`, `v5_it_qc.py` rules, detector inference logic, Flutter layout/hierarchy beyond IT Motif text.

---

## 2. P1 items addressed

| ID | Item | Resolution |
|----|------|------------|
| P1-1 | V5 demo default | Explicit demo path (`run_demo.ps1` + docs + health); **code default remains V2** |
| P1-2 | French IT Motif | Frontend mapping; API codes unchanged |
| P1-3 | `backend/README.md` | Updated to current pipeline |
| P1-4 | FastAPI OpenAPI | Title, description, `/analyze`, schemas updated |

---

## 3. V5 demo configuration

**Code default (compatibility):** `MODEL_VERSION` unset → **`v2`** (preserves intentional V2 mode and existing tests).

**Demo launch (required for V5 presentation):**

```powershell
.\backend\run_demo.ps1
```

Sets `MODEL_VERSION=v5_phase2`, binds `0.0.0.0:8001`.

**Verification:**

```text
GET /health → "model_version": "v5_phase2"
```

Documented in `backend/README.md`, `mobile/README.md`, `mobile/docs/API_CONFIGURATION.md`.

Bare `uvicorn` without the env var still starts V2 — intentionally, so demos must use `run_demo.ps1`.

---

## 4. French IT reason-code mapping

Module: `mobile/lib/utils/it_quality_reason_label.dart`

| Internal code (API unchanged) | French UI |
|-------------------------------|-----------|
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

UI copy:

- Review: **`Motif de vérification : …`**
- Unavailable: **`Motif : …`**
- Accept / v=0 / quality badges: unchanged behavior

---

## 5. README changes

`backend/README.md` now documents:

- `POST /analyze` with image upload
- Preprocessing V2/V5
- Model selection via `MODEL_VERSION`
- V5 16 landmarks + IT_R / IT_L + IT QC
- Measurements + `coordinate_space`
- Demo vs V2 compatibility launch
- Tests (~167 OK / 1 skip)
- Explicit non-claims (no diagnosis / no medical-device certification)

Removed obsolete claims that AI/upload were unimplemented.

---

## 6. OpenAPI changes

- App title: **Coxométrie — Backend**
- Description: `/analyze`, V2/V5, IT QC, no diagnostic claims
- `/health`: returns `model_version`
- `/analyze` summary/response_description/docstring: V2/V5 accurate
- Schema Field descriptions for IT quality, landmarks, `model_version`

**API JSON contract unchanged** (same fields/enums; docs only + health additive field).

---

## 7. Flutter test result

```text
flutter test
→ 00:05 +74: All tests passed!
exit_code: 0
```

(Includes new `it_quality_reason_label_test.dart` and updated REVIEW Motif assertion.)

---

## 8. Backend test result

```text
python -m unittest discover -s backend\tests -v
→ Ran 167 tests in 152.786s
→ OK (skipped=1)
exit_code: 0
```

V2-default expectations intentionally preserved.

---

## 9. Android build result

```text
flutter build apk --debug
→ √ Built build\app\outputs\flutter-apk\app-debug.apk
exit_code: 0
```

---

## 10. V5 smoke-test result

Launched with `MODEL_VERSION=v5_phase2` on `127.0.0.1:8011`.

**Health:**

```json
{"status":"ok","service":"coxometrie-backend","version":"0.2.0","model_version":"v5_phase2"}
```

**POST /analyze** (`B26_10.png`):

| Check | Result |
|-------|--------|
| `status` | `ok` |
| `model_version` | `v5_phase2` |
| Refined MVP landmarks | **14** |
| `it_landmarks` | **2** (IT_R kp=14, IT_L kp=15) |
| IT quality | both `accept` |
| `coordinate_space` | `original_image_pixels` 3039×2625 |
| Measurements | VCE / Tönnis / CCD available R+L |

---

## 11. Confirmation — frozen assets

| Asset / behavior | Modified? |
|------------------|-----------|
| Model architecture | **No** |
| Checkpoints | **No** |
| Dataset / labels | **No** |
| `mvp_geometry` / VCE / Tönnis / CCD | **No** |
| IT QC rules (`v5_it_qc.py`) | **No** |
| Backend QC reason **codes** | **No** (presentation only) |

---

## 12. Remaining limitations

- Code default remains V2 if someone ignores `run_demo.ps1` (by design).
- Unknown future QC codes fall back to a generic French string.
- iOS project still absent (unchanged).
- No export/report feature.
- OpenAPI `service` name changed from `mvp-backend` to `coxometrie-backend` in `/health` (additive clarity).

---

## 13. Final verdict

# **PHASE5_P1_FIXES_COMPLETE**

All four P1 items implemented; Flutter 74/74; backend 167 OK (1 skipped); debug APK builds; V5 smoke confirms `model_version=v5_phase2` with IT + QC + measurements + `coordinate_space`.
