# Phase 4B — UX Perfection Audit

**Date:** 2026-09-04  
**Scope:** Flutter app `mobile/` — UX / UI / medical presentation (read-only)  
**Validated upstream:** CHECKPOINT_INFERENCE_READY · BACKEND_V5_PHASE2_INTEGRATION_READY · V5_IT_QC_READY · FLUTTER_V5_INTEGRATION_READY · CROSS_PLATFORM_ROBUSTNESS_READY  
**Tests cited by requester:** Flutter 61 passed · Backend 167 OK / 1 skipped · Android debug APK builds  

**Method:** Static review of all user-facing screens and widgets (`home_screen`, `preview_screen`, `analysis_screen`, `results_screen`, `server_connection_screen`, `landmark_overlay`, `measurement_card`, `it_status_section`, `loading_analysis`, theme). No files modified except this audit document. No implementation started.

---

## Executive Summary

The application **already communicates its clinical purpose** (AP pelvis → automatic landmarks → VCE / Tönnis / CCD) and follows a clean linear workflow. Measurement presentation is medically cautious: values in degrees, unavailable shown as `—`, no diagnostic interpretation. The clinical color palette is sober and appropriate.

What prevents a **professional, jury-ready medical AI demo** is not missing features such as Alpha angle — it is **presentation hierarchy and demo surface**:

1. **Results screen hierarchy is inverted** for a doctor: a generic green “success” banner and a developer **Détection** dump compete with the radiograph and the three angles.
2. **Landmark review on the image is underpowered**: fixed ~320 px height, no zoom, no legend, labels can collide/clip.
3. **Home and Analysis still look partly like a developer console**: always-visible backend URL, duplicate server entry points, physical-device `flutter run` hints, English loading copy + “YOLO”, mixed FR/EN on Results (Model / Confidence / ACCEPT / REVIEW).
4. **IT REVIEW quality is under-signaled at the top of Results** while the status banner always claims success — a trust issue for surgeons and radiologists.

**Verdict:** Functionally demo-capable for a technical audience; **not yet presentation-perfect** for orthopedic / radiology / jury scrutiny. No P0 crash/usability blockers found in UI code review. Priority work is **Results medical hierarchy + demo declutter + FR consistency + overlay inspectability**.

**5-second doctor test (Home):** **Mostly yes** — title “Coxométrie”, subtitle naming VCE / Tönnis / CCD and landmarks is clear. Residual friction: backend URL and server/debug chrome dilute first impression.

---

## Home

**Sources:** `mobile/lib/screens/home_screen.dart`

| Aspect | Assessment |
|--------|------------|
| Visual hierarchy | Title + icon + body copy → primary Import → secondary Camera → tertiary Server. Spacers push CTAs down; readable on phone. |
| Title / subtitle | AppBar “Coxométrie”; body “Analyse coxométrique” + clear FR explanation of workflow. Strong. |
| Primary action | “Importer une radiographie” — correct primary. |
| Import workflow | Gallery / camera with busy guard — sound. |
| Server configuration | **Too visible for demo:** AppBar ethernet icon + TextButton “Connexion serveur” + footer `Backend : ${ApiConfig.baseUrl}` + optional physical-device banner with `flutter run --dart-define=…`. |
| Unnecessary elements | Duplicate server access; raw URL footer; developer hint banner on physical Android/iOS without dart-define. |
| Spacing / typography / consistency | Theme tokens used; FR consistent on this screen. Icon `monitor_heart_outlined` is weakly related to pelvis radiography. |

**Questions**

- Can a doctor understand within 5 seconds? **Yes**, if they read the subtitle.
- Does it look like a medical product or a lab tool? **Mixed** — clinical copy, but server/debug chrome reads as engineering.

**Findings**

| ID | Pri | Finding |
|----|-----|---------|
| H1 | P1 | Always-visible backend URL and dual “Connexion serveur” harm demo trust. |
| H2 | P1 | Physical-device warning exposes CLI/`dart-define` to clinical audience. |
| H3 | P2 | Redundant server entry (AppBar + button). |
| H4 | P3 | Heart-monitor icon is a weak brand/clinical cue for coxometry. |

---

## Preview

**Sources:** `mobile/lib/screens/preview_screen.dart`, `radiograph_image_view.dart`

| Aspect | Assessment |
|--------|------------|
| Radiograph presentation | Dark clinical background, `BoxFit.contain`, clipped radius — appropriate. |
| Proportions | Fixed height **360** — larger than Results overlay (320); inconsistent and still not full-bleed inspectable. |
| Clarity | Workflow obvious: see image → Analyser / Retour. |
| Buttons | Primary Analyze with biotech icon; Outlined Retour duplicates AppBar back. |
| Metadata | `W × H px · size · orientation corrigée` — slightly technical but useful for QC. |
| Error / loading | Relies on `Image.memory` error icon; no dedicated empty state beyond picker errors on Home. |

**Findings**

| ID | Pri | Finding |
|----|-----|---------|
| P1-prev | P2 | Fixed 360 px preview; not adaptive to small phones / landscape / tablet. |
| P2-prev | P3 | Explicit “Retour” duplicates system back; low harm. |
| P3-prev | P3 | Pixel/size line is fine for engineers; optional hide in “demo mode”. |

**Workflow obvious?** Yes.

---

## Analysis

**Sources:** `mobile/lib/screens/analysis_screen.dart`, `loading_analysis.dart`

| Aspect | Assessment |
|--------|------------|
| Loading state | Thumbnail + indeterminate `CircularProgressIndicator` — honest, **no fake progress**. Good. |
| Wording | Default message **English:** `Analyzing radiograph…` while rest of UI is French. Subtitle: “Détection **YOLO** et calcul des mesures en cours.” |
| Perceived responsiveness | Up to 120 s timeout with only spinner; acceptable medically if copy is calm FR; feels unfinished with EN + YOLO. |
| Double submit | `_requestStarted` + `PopScope(canPop: !_analyzing)` + `pushReplacement` — solid. |
| Error handling | Friendly FR messages, Retry + back to preview — good. |

**French localization:** **Should be restored** for the primary loading string (and preferably demote “YOLO” to non-demo or replace with “détection automatique des landmarks”).

**Findings**

| ID | Pri | Finding |
|----|-----|---------|
| A1 | P1 | Mixed language: English primary loading string in a French clinical app. |
| A2 | P2 | “YOLO” in user-facing copy is research jargon for a jury/doctor demo. |
| A3 | P3 | Optional elapsed-time hint for long analyses (not fake %). |

---

## Results

**Sources:** `mobile/lib/screens/results_screen.dart` (+ measurement / IT / overlay widgets)

This is the **most important screen**. Current vertical order:

1. Landmark overlay (or bare image) — height **320**  
2. Dimension mismatch banner (conditional)  
3. Model version  
4. Green **“Analyse terminée avec succès”** (always, ignoring IT REVIEW)  
5. Hanche droite / gauche measurements  
6. Landmarks IT QC  
7. **Détection** debug block (counts, BBox, refinement ASL_L, coordinate space)  
8. Sticky **Nouvelle radiographie**

### What the user should understand immediately

| Need | Current state |
|------|----------------|
| 1. What image was analyzed | Yes — same bytes shown; size limited. |
| 2. What landmarks were detected | Partially — markers + labels; no legend; dense labels. |
| 3. What measurements were calculated | Yes — VCE / Tönnis / CCD by side; `—` when unavailable. |
| 4. Whether any landmark requires review | Partially — IT REVIEW badge + ring on overlay; **contradicted** by always-green success banner; MVP landmark confidence never surfaced. |

**Findings**

| ID | Pri | Finding |
|----|-----|---------|
| R1 | P1 | Overlay height 320 px is too small for credible landmark review on AP pelvis. |
| R2 | P1 | No pinch-zoom / pan (`InteractiveViewer` absent) — doctor cannot inspect markers. |
| R3 | P1 | Always-green success banner ignores REVIEW / unavailable IT and unavailable measures. |
| R4 | P1 | `_DetectionSection` (BBox, Refinement ASL_L, Espace coordonnées, “Landmarks MVP”) looks like a debug panel in a clinical demo. |
| R5 | P1 | No overlay legend (MVP vs IT accept vs IT review). |
| R6 | P2 | Information order: success + model before measurements; measurements should follow the image more tightly. |
| R7 | P2 | Model line uses English “Model:”. |
| R8 | P2 | Sticky “Nouvelle radiographie” is good; AppBar lacks equivalent shortcut only as minor polish. |
| R9 | P3 | Dimension-mismatch banner text is accurate but verbose/technical. |

**Medical honesty (positive):** Measurement cards do **not** invent diagnoses; unavailable reasons shown in warning tone. Keep this.

---

## Landmark Overlay

**Sources:** `mobile/lib/widgets/landmark_overlay.dart`

| Aspect | Assessment |
|--------|------------|
| Marker size | Default radius **4.5** + white stroke — readable at 320 px height but small when image is downscaled. |
| IT_R vs IT_L | Same accept color; distinction mainly by label text — acceptable if labels readable. |
| REVIEW | Warning fill + outer ring + `⚠` in label — good visual language. |
| Unavailable | Not drawn (`isDrawable` false) — correct. |
| Legend | **None.** |
| Label positioning | Fixed offset to the right; **no collision avoidance / edge clamping** → risk of clip near right/top borders and overlap between nearby KP. |
| Overlap with image | Dark label chips help contrast on radiograph; many simultaneous labels can obscure anatomy. |
| Zoom | None. |

**Findings**

| ID | Pri | Finding |
|----|-----|---------|
| L1 | P1 | Missing legend; REVIEW meaning not explained without scrolling to IT section. |
| L2 | P1 | No zoom/pan for overlay inspection. |
| L3 | P2 | Label placement can clip or overlap; no density toggle. |
| L4 | P2 | Marker size not density-aware (small phones vs tablets). |
| L5 | P3 | Optional: dim MVP labels when focusing IT, or tap-to-identify. |

---

## Measurements

**Sources:** `mobile/lib/widgets/measurement_card.dart`, `measurement.dart`

| Aspect | Assessment |
|--------|------------|
| Hierarchy | Side sections “Hanche droite / gauche” then VCE → Tönnis → CCD — clinically familiar order. |
| Presentation | Large-ish degree values with tabular figures; unavailable `—`. |
| Diagnostic language | **None** — appropriate. Prefer keeping labels as measurement names, not “dysplasia / dysplasia grade”. |
| Confidence | Not shown per angle (backend may not expose per-measure confidence) — OK; do not invent. |
| Unavailable reasons | Shown under the side block — good; ensure reasons stay short/clinical if raw codes appear. |

**Recommendation (presentation only, no new clinical claims):** A quiet section title such as **“Mesures”** (or “Measurements”) above the sides would clarify that these are quantitative outputs, not diagnoses. Quality/review language belongs with landmarks/IT, not with inventing disease labels.

**Findings**

| ID | Pri | Finding |
|----|-----|---------|
| M1 | P2 | No explicit “Mesures” heading — sides appear abruptly after status banner. |
| M2 | P3 | Full names once (e.g. “VCE (angle de couverture)” ) could help non-orthopedists on a jury — optional, keep values primary. |

---

## IT QC

**Sources:** `mobile/lib/widgets/it_status_section.dart`

| Aspect | Assessment |
|--------|------------|
| Structure | Per-landmark cards IT_R / IT_L with quality badge. |
| Labels | Badges **ACCEPT / REVIEW / UNAVAILABLE** (English); fields “Confidence”, “Reason”, pixel “Position”. |
| Trust | REVIEW is visible here, but easy to miss if user stops at green banner + angles. |
| Medical tone | Prefer humanized FR: “À revoir” / “Accepté” / “Indisponible”; keep technical reason secondary. |
| Pixel coordinates | Useful for engineers; noise for surgeon demo. |

**Findings**

| ID | Pri | Finding |
|----|-----|---------|
| I1 | P1 | IT REVIEW not reflected in Results top-level status. |
| I2 | P2 | FR/EN mix (Confidence / Reason / ACCEPT). |
| I3 | P2 | Raw pixel positions and engine `quality_reasons` strings feel debug-like. |
| I4 | P3 | Section title “Landmarks IT” may need one-line plain-language subtitle (ischial tuberosity) for jury — without clinical interpretation. |

---

## Responsive Design

| Context | Risk |
|---------|------|
| Small Android | Home with warning banner + Spacers may squeeze; Results long scroll OK. Fixed overlay heights waste vertical space poorly (too small for clinical review, not too large). |
| Standard phone | Usable; Results scroll-heavy. |
| Large phone | Extra whitespace on Home; overlay still capped at 320. |
| Tablet (`contentMaxWidth` 720) | Layout centers well; radiograph still short — **underuses tablet**. |
| Portrait | Primary assumed path — OK. |
| Landscape | No dedicated layout; fixed-height image + bottom button bar likely awkward; overlay not wider-aware beyond width stretch. |

**Overflow / clip:** No obvious unbounded Column overflow in code paths reviewed; landmark **labels** can paint outside visible usefulness near edges. Image uses contain — no aspect distortion of the radiograph itself.

**Findings**

| ID | Pri | Finding |
|----|-----|---------|
| RD1 | P1 | Fixed radiograph heights (260 / 320 / 360) ignore screen size — weak on small and tablet. |
| RD2 | P2 | No landscape layout strategy. |
| RD3 | P3 | Double `SafeArea` on Results footer is slightly padded but not broken. |

---

## Accessibility

**Observed:** Almost no `Semantics` / `semanticLabel` usage (only server IconButton `tooltip`). Overlay is pure `CustomPaint` (invisible to screen readers). Buttons generally have visible text. Theme contrast for primary text is good; `textMuted` on light gray is weaker.

| Pri | Improvement |
|-----|-------------|
| **P1** | Meaningful semantics for primary CTAs (Import, Analyze, Nouvelle radiographie) and for IT quality badges (announce REVIEW). |
| **P1** | Do not rely on color alone for REVIEW — keep text/badge (already present in IT section; ensure overlay has accessible summary). |
| **P2** | Minimum touch targets audit on IconButtons; increase if needed. |
| **P2** | Contrast check for muted footer URL / model label. |
| **P3** | Screen-reader summary of six angle values after analysis. |
| **P3** | Font: `Segoe UI` is Windows-biased; ensure Android fallback remains legible (usually does). |

---

## Error UX

| Scenario | Behavior | Assessment |
|----------|----------|------------|
| Server unavailable | FR message with base URL | Clear; slightly technical. |
| Timeout | FR timeout message | Good. |
| Invalid / empty image | ApiException / picker messages | Good. |
| Malformed JSON / incomplete ok | Validator messages in FR | Good. |
| HTTP 4xx/5xx | Status code + short message | Acceptable for prototype; avoid dumping `detail` stacks (currently message-oriented). |
| Coordinate mismatch | Warning banner under image | Actionable for engineers; verbose for doctors. |
| Home picker catch-all | `'Échec de la sélection : $e'` | **Risk of raw exception text** (P2). |

**Positive:** Analysis errors do not show stack traces. Retry path exists.

**Findings**

| ID | Pri | Finding |
|----|-----|---------|
| E1 | P2 | Sanitize Home catch-all to avoid exposing exception `toString()`. |
| E2 | P2 | Network copy mentioning `dart-define` is for developers, not clinicians. |
| E3 | P3 | Soften dimension-mismatch wording for demo. |

---

## Performance

| Area | Notes |
|------|-------|
| Image loading | `Image.memory` with `gaplessPlayback` — fine for MVP sizes. |
| Analysis wait | Indeterminate spinner — correct; no fake %. |
| Results / overlay | `CustomPaint` + `shouldRepaint` gated — sound. |
| Rebuilds | Local `setState` for overlay size decode — acceptable. |

**No performance optimization recommended without profiling evidence.** UX of long wait is a **copy/hierarchy** issue, not a rebuild issue.

---

## Doctor Workflow

Scenario: receive AP pelvis → import → analyze → see landmarks → inspect VCE / Tönnis / CCD → identify uncertain landmarks.

| Step | Friction |
|------|----------|
| Import | Low — gallery primary. |
| Analyze | Low — one confirm on Preview. |
| See landmarks | **Medium–high** — small image, no zoom, label clutter, no legend. |
| Inspect angles | **Low** — clear R/L cards. |
| Uncertain landmarks | **Medium** — IT REVIEW exists but success banner + scroll distance + English badges reduce salience; MVP KP confidence unused. |
| Another image | Low — sticky Nouvelle radiographie. |

**Conclusion:** Measurement inspection is quick; **landmark confidence review is not yet surgeon-grade**.

---

## Demo Readiness

Elements that look unfinished or debug-like for an academic live demo:

| Element | Why it hurts |
|---------|----------------|
| Footer `Backend : http://…` | Lab console aesthetic. |
| Home server button + AppBar + Connection screen with uvicorn/`flutter run` | Developer playbook on stage. |
| Loading “Analyzing…” + YOLO | Language/jargon break immersion. |
| Results Détection block (BBox, refinement flags, coordinate space) | Looks like API inspector. |
| Always-green success | Overconfident when REVIEW present. |
| Mixed FR/EN (Model, Confidence, ACCEPT) | Unfinished localization. |
| Small non-zoomable overlay | Jury cannot “see the AI working” on anatomy. |

**Target look:** Coherent medical imaging prototype — radiograph + landmarks + six angles + honest QC — not a FastAPI client debugger.

**What already works for demo:** Clinical palette, FR measurement naming, unavailable `—`, IT quality model, single-flight analysis, sticky re-import.

---

## P0

*None identified in this read-only UI audit.*

No crash paths, blocked navigation, or unusable primary flow found in reviewed Flutter UI code. (Runtime device issues such as wrong API URL remain operational, not P0 UI defects.)

---

## P1

1. **Results hierarchy for clinical demo** — demote/hide Détection debug block; elevate radiograph + measures + review signals.  
2. **Status honesty** — replace always-green success when any IT is REVIEW/UNAVAILABLE or critical measures missing.  
3. **Overlay inspectability** — larger adaptive image area + pinch-zoom/pan.  
4. **Overlay legend** — MVP / IT / À revoir.  
5. **Home demo declutter** — hide backend URL and CLI hints from default Home; keep server tools one tap away (or behind long-press / settings only).  
6. **French loading string** — restore FR for Analysis primary message; remove or demote “YOLO” in user copy.  
7. **IT REVIEW salience** — top-of-Results summary when review required.  
8. **Accessibility P1** — semantics for primary actions and REVIEW state.

---

## P2

1. Unify FR labels (Model → Modèle; Confidence → Confiance; quality badges).  
2. Adaptive radiograph heights; basic landscape behavior.  
3. Measurement section title “Mesures”; tighten vertical order.  
4. Soften/hide pixel positions and raw QC reason codes in demo presentation.  
5. Label collision / edge clamping; optional label density control.  
6. Sanitize Home exception strings; clinician-friendly network errors.  
7. Remove duplicate server CTA; keep a single discreet entry.  
8. Accessibility P2 (contrast, targets).

---

## P3

1. Richer coxometry icon / brand mark.  
2. Optional full measurement names for non-specialist jury.  
3. Elapsed-time text during long analysis.  
4. Re-analyze same image without re-import.  
5. Demo mode flag (hide all debug surfaces in one switch) — presentation-only.  
6. Screen-reader summary of angles.  
7. IT plain-language subtitle without diagnostic claims.

---

## Recommended Implementation Order

1. **Demo surface cleanup (Home + Analysis copy)** — highest jury impact, lowest clinical risk.  
2. **Results status + hide/collapse Détection debug** — trust and professionalism.  
3. **IT REVIEW summary + FR QC labels** — medical honesty.  
4. **Larger overlay + zoom + legend** — core doctor workflow.  
5. **Responsive radiograph sizing** — small phone + tablet.  
6. **Accessibility semantics** — P1 items.  
7. **P2 polish** (label collision, error copy, landscape).  
8. **P3 optional** (demo mode toggle, brand icon).

Do **not** in that order: retrain models, change geometry, add Alpha angle, change API contracts, or redesign the visual language from scratch.

---

## Five-Day Final Plan

Assumes implementation **after** this audit gate; this document does not start coding.

| Day | Focus | Exit criteria |
|-----|--------|----------------|
| **Day 1** | Demo declutter + FR consistency | Home without raw URL/CLI by default; Analysis message in French; no user-facing “YOLO”; single discreet server entry. |
| **Day 2** | Results medical hierarchy | Success/review banner reflects QC; Détection block collapsed or demo-hidden; “Mesures” heading; FR model/QC labels. |
| **Day 3** | Landmark inspection | Adaptive taller overlay; pinch-zoom/pan; legend; REVIEW still visible on image. |
| **Day 4** | Responsive + error polish | Small/large phone checks; landscape sanity; sanitized errors; IT cards less debug-like. |
| **Day 5** | Accessibility + dry-run demo | Semantics P1; full Home→Results rehearsal as surgeon + jury; checklist sign-off; **no** model/API/geometry changes. |

**Demo dry-run checklist (Day 5)**

- [ ] Doctor understands purpose in ≤5 s on Home  
- [ ] No backend URL or `flutter run` visible on projector  
- [ ] Loading copy fully French, calm, non-jargon  
- [ ] Results: image → landmarks understood → six angles → review state if any  
- [ ] No always-green success when REVIEW present  
- [ ] Zoom can show a landmark to the jury  
- [ ] Nouvelle radiographie works without stack confusion  

---

## Appendix — Screen inventory (read-only)

| Screen | Role |
|--------|------|
| `HomeScreen` | Import + server access |
| `PreviewScreen` | Confirm radiograph |
| `AnalysisScreen` | POST `/analyze` + loading/error |
| `ResultsScreen` | Overlay, measures, IT QC, detection dump |
| `ServerConnectionScreen` | GET `/health` diagnostic (explicitly debug-oriented in code comments) |

**Theme:** `AppTheme.light` / `AppColors` — clinical teal primary, orange MVP landmarks, teal IT, amber review — **keep**; recommend changes only where contrast/REVIEW salience needs reinforcement, not a palette rewrite.

---

*End of Phase 4B audit. No implementation performed.*
