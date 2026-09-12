# Phase 4B — Implementation Plan

**Date:** 2026-09-04  
**Audit reference:** `datasets/yolo_pose_new_26/phase4b_ux_perfection_audit.md`  
**Scope:** Flutter UX / medical presentation only (`mobile/`)  
**Status:** Plan only — **no application source code modified yet**

---

## Safety constraints (non-negotiable)

| Must NOT change | Must preserve |
|-----------------|---------------|
| V5 / V2 models, checkpoints, training, labels | Cautious measurement display (`—` when unavailable) |
| `mvp_geometry` / VCE / Tönnis / CCD formulas | IT quality: `accept` / `review` / `unavailable` |
| API request/response contracts | `coordinate_space` + dimension mismatch banner |
| Landmark coordinates / measurement values | V2 compatibility (empty IT, no coordinate_space) |
| Diagnostic claims | Existing Flutter + backend test intent |

This phase is **perception-of-quality**: copy, hierarchy, overlay inspectability, status honesty derived from **existing** backend QC fields.

---

## Current test inventory (baseline)

| Suite | Path | Relevance |
|-------|------|-----------|
| Overlay / mapping | `mobile/test/landmark_overlay_test.dart` | `ImageContainLayout`, painter, IT review ring, unavailable not drawn |
| V5 UI + parsing | `mobile/test/v5_integration_test.dart` | Results keys, IT badges, `Model: …` text, mismatch banner, narrow width |
| Models | `mobile/test/models_test.dart` | Parsing; must stay green |
| API | `mobile/test/api_service_test.dart` | No API contract change |
| API config | `mobile/test/api_config_test.dart` | Home may stop displaying URL; config API unchanged |
| Health | `mobile/test/health_check_test.dart` | Server screen remains |
| Fixtures | `mobile/test/fixtures/analysis_fixtures.dart` | Reuse for status / REVIEW cases |

**After each implementation group:** run focused Flutter tests.  
**End of phase:** full `flutter test`, backend tests, Android debug APK.

---

## Implementation order (incremental)

1. P1-1 Home declutter  
2. P1-2 French loading copy (+ demote YOLO)  
3. P1-3 Honest Results status + P1-8 Review salience (same Results status surface)  
4. P1-4 Collapse Détection block  
5. P1-5 Larger overlay area  
6. P1-6 Zoom / pan  
7. P1-7 Landmark legend  

Related FR polish on Results (`Model:` → `Modèle :`, IT badge wording) may ship with P1-3/P1-8 if it avoids breaking demo consistency; update `v5_integration_test` string expectations in the same PR group.

---

## Issue map

### P1-1 — Home screen declutter

| Field | Detail |
|-------|--------|
| **Audit refs** | H1, H2, H3 |
| **Current files** | `mobile/lib/screens/home_screen.dart` (`_WarningBanner`, footer `Backend : …`, duplicate `TextButton` + AppBar `server_connection_button`); `mobile/lib/config/api_config.dart` (`physicalDeviceHint` — keep for diagnostics); `mobile/lib/screens/server_connection_screen.dart` (already holds URL / health / setup) |
| **Proposed change** | On Home: remove always-visible backend URL footer; remove physical-device CLI/`dart-define` banner from default Home; remove duplicate body “Connexion serveur” `TextButton`; **keep** a single discreet AppBar action (`server_connection_button`) so connection/errors remain reachable. Ensure `ServerConnectionScreen` continues to show URL, health, and physical-device guidance. Keep Home clinical title/subtitle + Import / Camera CTAs and picker `_ErrorBanner`. |
| **Risk** | Low. Operators who relied on Home URL must open Connexion serveur once. No API/model impact. |
| **Tests** | Add lightweight widget test (or extend existing) that Home does **not** show `Backend :` / `flutter run` / `dart-define` text, still finds `server_connection_button` and import keys. Run `api_config_test.dart` unchanged. |

---

### P1-2 — French localization (loading)

| Field | Detail |
|-------|--------|
| **Audit refs** | A1, A2 |
| **Current files** | `mobile/lib/widgets/loading_analysis.dart` (default `message = 'Analyzing radiograph…'`; subtitle `Détection YOLO et calcul des mesures en cours.`); consumed by `mobile/lib/screens/analysis_screen.dart` |
| **Proposed change** | Default message → `Analyse de la radiographie…` (key `analysis_loading_message` preserved). Replace YOLO subtitle with non-diagnostic clinical wording, e.g. `Détection des repères anatomiques et calcul des mesures en cours.` (or shorter `Analyse IA des repères anatomiques en cours.` — prefer first: no diagnosis claim). Do **not** change code comments in models/services that mention YOLO. |
| **Risk** | Very low. Any test asserting English loading string (none found today) would need update. |
| **Tests** | New/updated widget test pumping `LoadingAnalysis` / `AnalysisScreen` loading state: expect FR message; assert no `YOLO` / `Analyzing radiograph` in UI. Run full Flutter suite after group. |

---

### P1-3 — Honest Results status

| Field | Detail |
|-------|--------|
| **Audit refs** | R3, I1 |
| **Current files** | `mobile/lib/screens/results_screen.dart` — `_StatusBanner` takes `AnalysisResult` but **ignores** it and always paints green “Analyse terminée avec succès”. IT QC already on `ITLandmark.quality` (`mobile/lib/models/it_landmark.dart`). Measurements availability on `Measurement.available` (`measurement.dart`). Analysis/API failures never reach Results (`AnalysisScreen` error path). |
| **Proposed change** | Introduce a small **presentation-only** helper (e.g. `lib/utils/result_status.dart` or private in results screen) that classifies UI status from existing fields only: (1) any IT `review` → warning / “Vérification recommandée” (or equivalent FR) listing affected names; (2) IT `unavailable` and/or measurements unavailable → neutral/info, not green “perfect success”; (3) all IT accept (or no IT / V2) and analysis ok → success “Analyse terminée” (keep cautious wording). **Do not** invent thresholds or convert REVIEW→FAIL. Do not change parsing. Optional: soft FR `Model:` → `Modèle :` in `model_version_label.dart` in same group. |
| **Risk** | Medium-low. Existing Results tests do not assert the green banner text today, but will need new assertions. Avoid implying diagnosis. |
| **Tests** | Extend `v5_integration_test.dart`: accept-all → success-style banner key; IT REVIEW → review banner key + not unconditional success copy; V2 (no IT) → success/usable path; unavailable IT fixture → non-green honest state. Keep parsing tests intact. |

---

### P1-4 — Détection developer block

| Field | Detail |
|-------|--------|
| **Audit refs** | R4 |
| **Current files** | `mobile/lib/screens/results_screen.dart` — `_DetectionSection` (BBox, Landmarks MVP, refinement ASL_L, coordinate space) always expanded below IT |
| **Proposed change** | Keep data model/API untouched. Wrap section in `ExpansionTile` / equivalent, **collapsed by default**, title e.g. `Détails techniques` or `Détection (avancé)`. Keys for expand test. Primary scroll order remains: overlay → status → measures → IT → collapsible detection. |
| **Risk** | Low. E2E docs mentioning open Détection become “expand once”; no product docs change required in this plan step. |
| **Tests** | Widget test: section content (e.g. `BBox` / `Landmarks MVP`) not visible until expand; after tap, visible. Narrow-width Results test still no overflow. |

---

### P1-5 — Larger landmark overlay

| Field | Detail |
|-------|--------|
| **Audit refs** | R1, RD1 |
| **Current files** | `results_screen.dart` hardcodes `height: 320` for `LandmarkOverlay` and fallback `Image.memory`; `AppSpacing.radiographHeight = 260`; `preview_screen.dart` uses 360; `LandmarkOverlay.height` param |
| **Proposed change** | Compute overlay height from `MediaQuery` (e.g. ~42–50% of screen height, clamped min/max such as 280–520) while keeping `BoxFit.contain` via existing `ImageContainLayout`. Still pass `overlaySize` from `resolveOverlayImageSize` — **do not** alter coordinates or mismatch logic. Align preview height similarly if trivial (optional same pass). Prefer changing Results first. |
| **Risk** | Low–medium. Narrow 320×640 test may need surface size / scroll pump; avoid overflow with sticky footer. |
| **Tests** | Existing overlay mapping tests unchanged. Results narrow-width test still passes. Optional: assert overlay `SizedBox` height ≥ previous 320 on a tall surface. |

---

### P1-6 — Zoom and pan

| Field | Detail |
|-------|--------|
| **Audit refs** | R2, L2 |
| **Current files** | `mobile/lib/widgets/landmark_overlay.dart` (Stack: `Image.memory` + `CustomPaint`/`LandmarkPainter`); layout via `ImageContainLayout` |
| **Proposed change** | Wrap the **inner** image+paint stack (same child tree) in Flutter **`InteractiveViewer`** (`minScale`/`maxScale` constrained, e.g. 1–4). Because image and markers share one transformed subtree, **registration stays correct** without changing `toDisplay`. No new packages. Clip to rounded radiograph container. Consider `clipBehavior` so zoom stays inside the dark frame. Do not apply separate transforms to paint vs image. |
| **Risk** | Medium. Gesture competition with parent `SingleChildScrollView` (vertical drag vs pan). Mitigations: `InteractiveViewer` with bounded pan; optional `PanAxis`; document that zoom gestures take priority inside overlay. Tests must not flake on settle. |
| **Tests** | Widget test: find `InteractiveViewer`; optionally drive `TransformationController` to scale > 1 and assert `landmark_painter` still present and layout mapping unit tests unchanged. Keep `landmark_overlay_test` coordinate tests as ground truth. |

---

### P1-7 — Landmark legend

| Field | Detail |
|-------|--------|
| **Audit refs** | L1, R5 |
| **Current files** | Colors in `app_colors.dart` (`landmark`, `itLandmark`, `itLandmarkReview`); painting in `landmark_overlay.dart`; Results hosts overlay |
| **Proposed change** | New compact widget e.g. `mobile/lib/widgets/landmark_legend.dart` under/above overlay on Results: short FR rows — anatomical landmarks (MVP color), IT landmarks (IT color), “À revoir” (review color + icon/text), note that unavailable landmarks are not shown. No diagnostic claims; no listing all 16 names. Show IT/review rows only when relevant (has IT / has review) to avoid clutter on V2. |
| **Risk** | Low. Slight vertical space; keep compact. |
| **Tests** | Keys for legend; V5 accept shows MVP+IT entries; REVIEW shows review entry; V2 hides IT-specific rows; unavailable does not show fake marker (existing overlay tests). |

---

### P1-8 — Review salience

| Field | Detail |
|-------|--------|
| **Audit refs** | I1, L1 (partial), accessibility note on not color-alone |
| **Current files** | Overlay already: review fill + ring + `⚠` (`landmark_overlay.dart`); IT section badges (`it_status_section.dart`); weak top status (`_StatusBanner`) |
| **Proposed change** | Couple with P1-3: top banner/chip must surface REVIEW with **icon + text** (not color only). Optionally FR badges `ACCEPT`→`Accepté`, `REVIEW`→`À revoir`, `UNAVAILABLE`→`Indisponible` in `it_status_section.dart` while **keeping** existing keys `it_quality_review` etc. Do not draw markers for unavailable/`v=0` (already `isDrawable`). Do not map REVIEW to FAIL. |
| **Risk** | Low–medium if FR badge text changes; update any `find.text('REVIEW')` (currently tests use keys). |
| **Tests** | REVIEW fixture: top status key + IT badge key both present; accept-all: no review banner; overlay review paint tests remain. |

---

## Files expected to change (when implementation starts)

| File | P1 items |
|------|----------|
| `mobile/lib/screens/home_screen.dart` | P1-1 |
| `mobile/lib/widgets/loading_analysis.dart` | P1-2 |
| `mobile/lib/screens/results_screen.dart` | P1-3, P1-4, P1-5, P1-8 (wiring) |
| `mobile/lib/utils/result_status.dart` *(new, optional)* | P1-3 |
| `mobile/lib/widgets/landmark_overlay.dart` | P1-5/6 (height caller + InteractiveViewer) |
| `mobile/lib/widgets/landmark_legend.dart` *(new)* | P1-7 |
| `mobile/lib/widgets/it_status_section.dart` | P1-8 (FR labels) |
| `mobile/lib/widgets/model_version_label.dart` | optional FR with P1-3 |
| `mobile/lib/theme/app_spacing.dart` | optional constants for overlay min/max |
| `mobile/test/v5_integration_test.dart` | P1-3–8 expectations |
| `mobile/test/landmark_overlay_test.dart` | P1-6/7 additions |
| New small tests for Home / LoadingAnalysis | P1-1, P1-2 |

**Explicitly out of scope for code changes:** backend, training, geometry, models weights, dataset, API schemas, `ServerConnectionScreen` diagnostic depth (keep as the debug home).

---

## Risk summary

| Area | Level | Notes |
|------|-------|-------|
| Clinical/geometry/API | None if constraints followed | Presentation-only |
| Overlay registration under zoom | Contained | Single `InteractiveViewer` child tree |
| Scroll vs pan gestures | Medium | Manual device check Day 3–4 |
| Test string churn | Low | Update `Model:` / badge text assertions together |
| Home ops discoverability | Low | Single AppBar server entry remains |

---

## Verification gate (end of implementation — future)

1. Focused tests after each group  
2. `flutter test` (full mobile suite)  
3. Backend test suite (regression only — no intentional backend edits)  
4. `flutter build apk --debug`  
5. Manual demo dry-run: Home clean → Analyze FR → Results honest status → zoom landmark → legend → expand technical details  

---

## Stop condition

This document is the **only** deliverable of the planning step.  
**Do not modify application source code until an explicit implementation go-ahead.**

*End of Phase 4B implementation plan.*
