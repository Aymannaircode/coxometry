# Phase 8A — Final Pre-Demo Audit

**Date:** 2026-09-04  
**Mode:** READ-ONLY — no source, model, dataset, checkpoint, geometry, dependency, or test modifications except this report  
**Evidence:** Current `mobile/`, `backend/`, `mvp_geometry/`, docs under `mobile/docs/`, and prior phase reports cross-checked against code  
**Validation cited by project:** Flutter 98 tests passed · Backend 167 OK / 1 skipped · Android debug APK builds · V5 via `.\backend\run_demo.ps1`  
**Explicit limitation:** No physical Android device available — camera hardware and négatoscope photo accuracy are **not** clinically or device-validated (APK build ≠ physical validation)

---

## 1. Executive summary

The product supports a **complete, demonstrable digital coxometry workflow** on Windows desktop (or Android emulator): import a known DICOM→PNG radiograph → V5 Phase 2 analysis (16 landmarks + IT QC) → results with overlay / zoom / measurements → A4 PDF export/share.

The **camera MVP (Phase 7B Option B)** is implemented end-to-end in UI (guidance → system camera → Utiliser/Reprendre → same `/analyze` path) with honest prototype disclaimers. It is **not** a substitute for physical-device or négatoscope clinical validation.

**No P0 blockers** for a jury demo that uses the **digital import** path and `run_demo.ps1`. Remaining risks are operational (accidental V2 if bare `uvicorn` is used; in-app health UI omits `model_version`) and presentation polish.

**Verdict: `DEMO_READY_WITH_P1`**

---

## 2. Complete user journey

### 2.1 Camera path (implemented UI)

| Step | Status | Notes |
|------|--------|-------|
| Home | OK | Title « Coxométrie », purpose, two CTAs |
| Prendre une photo | OK | Opens `CameraGuidanceScreen` (not raw picker) |
| Camera guidance | OK | Framing guide, bullets, prototype notice, FR |
| Capture | OK | System `image_picker` camera; no live in-app overlay |
| Utiliser / Reprendre | OK | Confirm screen; retake replaces bytes; cancel keeps photo |
| Preview | OK | Same `PreviewScreen` as gallery |
| Analyse | OK | `AnalysisScreen` → `POST /analyze` |
| Loading | OK | FR copy, no YOLO |
| Results | OK | Overlay, legend, zoom/pan, measures, IT, status |
| PDF → share/save | OK | Generate → app documents → system share sheet |

**Journey integrity:** Intact. After « Utiliser », `pushAndRemoveUntil` clears guidance/confirm so Back does not re-enter a stale camera stack.

### 2.2 Import path (recommended demo)

| Step | Status | Notes |
|------|--------|-------|
| Home → Importer une image | OK | Primary filled button |
| Preview → Analyser | OK | |
| Loading → Results → PDF | OK | Same pipeline as camera after bytes exist |

### 2.3 Broken / confusing / unfinished

| Finding | Severity | Detail |
|---------|----------|--------|
| Camera live framing | By design | System camera has no in-app overlay; guide is pre-capture + post-capture only |
| Physical camera | Validation gap | Not exercised on real Android |
| Home purpose copy | Minor | Mentions import only; camera is secondary CTA (acceptable for honesty) |
| Double preview (camera) | Minor | Confirm then Preview before Analyse — slightly long but clear |
| Server connection tip | Ops risk | In-app text still shows bare `uvicorn` without `MODEL_VERSION` (see §3, §13) |

No unfinished screen that blocks the digital demo.

---

## 3. Demo startup audit

### 3.1 `backend/run_demo.ps1`

Verified behavior:

- Sets `$env:MODEL_VERSION = "v5_phase2"` **before** uvicorn
- Default port **8001**, host **0.0.0.0**
- Prints expected health URL and warns against bare uvicorn
- Uses repo `.venv\Scripts\python.exe` when present
- Runs `uvicorn backend.main:app` from repo root

### 3.2 Model selection

| Path | Result |
|------|--------|
| `.\backend\run_demo.ps1` | Forces **V5 Phase 2** |
| Bare `uvicorn` / unset `MODEL_VERSION` | Code default **V2** (14 KP, no IT) — intentional compatibility |
| `GET /health` | Returns `model_version` via `get_model_version()` |
| `POST /analyze` under V5 | 16 KP + `it_landmarks` IT_R/IT_L + QC |

### 3.3 Can a developer accidentally run V2?

**Yes**, if they:

1. Ignore `run_demo.ps1` / README and launch bare uvicorn, **or**
2. Follow the in-app **Connexion serveur** checklist step 2 (`uvicorn …` without `MODEL_VERSION`)

Documented demos in `mobile/README.md`, `backend/README.md`, and `API_CONFIGURATION.md` correctly push `run_demo.ps1`. Following **those** docs → V5. Following **only** the Server Connection screen’s bare uvicorn line → V2 risk.

**Mitigation for live demo (ops, no code change required):** always start with `.\backend\run_demo.ps1` and confirm `curl http://127.0.0.1:8001/health` shows `"model_version":"v5_phase2"` before opening the app.

---

## 4. Home audit (jury first impression)

| Criterion | Assessment |
|-----------|------------|
| Title | « Coxométrie » — clear brand |
| Purpose | « Analyse coxométrique » + VCE / Tönnis / CCD + landmarks — understandable |
| Main actions | Import (primary) + Photo (secondary) — good hierarchy for safest demo |
| Server connection | Ethernet icon → dedicated screen; not cluttering Home body |
| Debug chrome | `debugShowCheckedModeBanner: false`; no YOLO / env dumps on Home |
| French | Consistent |
| Visual hierarchy | Icon → headline → body → CTAs; medical teal theme |
| Professional impression | Adequate student/research prototype; not “toy” |

**Remaining issues (actual):**

1. Purpose text emphasizes import; camera is present but secondary (appropriate given validation limits).  
2. Icon is generic `monitor_heart_outlined` (weak pelvic cue) — polish only.  
3. No explicit “assistée par IA / à vérifier” on Home (disclaimer lives in PDF and camera notice) — optional P2.

---

## 5. Camera audit

### IMPLEMENTED (camera UI / workflow)

- Entry: Home « Prendre une photo » → guidance  
- Guidance: framing corners, FR bullets (parallèle au négatoscope, reflets, bassin entier)  
- Prototype notice: lighting / glare / perspective; prototype; validation before clinical use  
- Capture: rear camera, quality 100, EXIF bake shared with gallery  
- Confirm: preview + decorative overlay (no crop) + Utiliser / Reprendre  
- Cancellation: silent on OS cancel; Annuler returns Home  
- Permission / unavailable errors: French messages + Réessayer  

### NOT VALIDATED

- Physical Android camera open / permission / EXIF on device  
- Real négatoscope photograph quality, glare, perspective, measurement fidelity  
- Emulator camera as proxy for négatoscope  

### Wording / clinical validation

Copy does **not** claim clinical validation of phone photos. Tests assert absence of “validée cliniquement sur négatoscope”. Safe for demo if narrator does not oversell the photo path.

---

## 6. Digital image demo audit

**Recommended demo path given no physical phone: digital import.**

| Check | Status |
|-------|--------|
| Dataset domain | `new_26` = DICOM→PNG (`meta/source_mapping.csv`) |
| Suggested sample | e.g. `datasets/yolo_pose_new_26/images/train/B26_01.png` (or a rehearsed val case); for IT REVIEW storytelling, prior audits cite **B26_26** |
| Preview | Shows image + dimensions |
| V5 analysis | Requires `run_demo.ps1` |
| 16 landmarks | 14 MVP + IT_R / IT_L when drawable |
| IT QC | accept / review / unavailable + FR reasons |
| Measurements | VCE, Tönnis, CCD R/L from API |
| Results + PDF | Full path |

This is the **safest, most reliable** jury path. Camera can be shown as a short UI walkthrough (“acquisition prototype”) without requiring live négatoscope success.

---

## 7. Loading audit

| Item | Status |
|------|--------|
| French | « Analyse de la radiographie… » + anatomical landmarks subtitle |
| No “YOLO” | User-facing loading has none (code comments only) |
| Progress | Indeterminate spinner — honest, no fake % |
| Misleading success | None on loading screen |
| Errors | Friendly FR; Réessayer / Retour à l’aperçu; back blocked while analyzing |

Acceptable for student demo. Cold model load may make first analysis slower (see §15).

---

## 8. Results audit

| Element | Status |
|---------|--------|
| Image + overlay | `LandmarkOverlay` + contain layout |
| 16 landmarks | MVP + IT when drawable |
| Legend | Anatomical / IT / À revoir / Indisponible note |
| Zoom/pan | `InteractiveViewer` 1×–4× |
| Measurements | Side sections VCE / Tönnis / CCD |
| Status | Success / Vérification recommandée / Informations partielles |
| REVIEW | Warning banner + amber IT styling |
| IT quality | Dedicated section |
| Technical details | Collapsed by default (« Détails techniques ») |
| V2/V5 | « Modèle : V5 Phase 2 » / « V2 » |
| Responsive | Overlay height ~45% screen, clamped 280–520 |

**Surgeon without developer?** Yes for core: image, angles in degrees, IT quality, review banner.  
**Jury in &lt;30 s?** Yes if scripted: import → results → point to measures + IT + PDF.

**Caveats:** Expanding technical details shows « Landmarks MVP », bbox coords, « ASL_L » — developer jargon (P2). Pinch-zoom vs vertical scroll can compete (known P2).

---

## 9. Measurement audit (presentation only)

| Check | Status |
|-------|--------|
| VCE / Wiberg | UI label « VCE »; PDF « Angle VCE / Wiberg » — same API field |
| Tönnis | Displayed both sides |
| CCD | Displayed both sides |
| Values = API | `Measurement.displayValue` from `value_deg` / `available` — no client recalculation |
| Units | Degrees with one decimal (`25.0°`) |
| Unavailable | `—` (UI) / « Non disponible » (PDF); reasons from API (FR geometry strings) |
| Diagnostic interpretation | None; no dysplasia/normal thresholds |

Presentation is honest and non-diagnostic. UI/PDF synonym labeling for VCE/Wiberg is a minor consistency polish (P2).

---

## 10. IT QC audit

| State | Overlay | UI / PDF | Notes |
|-------|---------|----------|-------|
| accept | Drawn (if coords) | Accepté (green) | Not a global “diagnosis OK” |
| review | Drawn + review color | À revoir + FR motif; top banner | Salient |
| unavailable / v=0 | **Not drawn** (`isDrawable`) | Indisponible + FR reasons | No fake markers |
| Success banner | Only if no review and no missing measures/IT | Incomplete banner if partial | Avoids misleading green when IT review present |

French reason mapping via `formatItQualityReason` (Phase 5 P1 closed). Unknown codes → generic FR fallback.

---

## 11. PDF audit

| Check | Status |
|-------|--------|
| Flow | Résultats → Exporter le rapport → generate → save → share |
| A4 | `PdfPageFormat.a4` |
| French | Header, measures, QC, disclaimer |
| Image + overlay | Composer reuses painter geometry |
| Measurements / QC / status | From same presentation helpers as UI |
| Disclaimer | Assisted IA; verify; not sole diagnosis; no device certification |
| No raw JSON / debug dump | Confirmed in builder structure |
| V2 | No IT section; label V2 |
| V5 / 16 KP | Overlay + IT quality table |
| Embarrassing demo risks | Share sheet depends on OS apps; no in-app PDF preview; first export may feel slow on large images; Unicode depends on system fonts |

Pre-generated samples exist under `datasets/yolo_pose_new_26/phase6a_pdf_samples/` for offline backup if live share fails.

---

## 12. Error-state audit

| Scenario | Behavior | Recoverable | Misleading? |
|----------|----------|-------------|-------------|
| API unavailable | FR network message | Retry / back | No |
| Timeout (120 s analyze) | FR timeout | Retry | No |
| Malformed response | invalid JSON / response | Retry | No |
| Invalid / empty image | Client or analysis error | Retry / re-import | No |
| File &gt; 25 Mo | Explicit too large | Choose smaller | No |
| Camera unavailable | FR | Réessayer / import | No |
| Permission denied | FR | Réessayer | No |
| Cancelled capture | Silent stay on guidance/confirm | Yes | No |
| Unavailable measurement | `—` + incomplete status | N/A | No |
| IT unavailable / review | Honest QC + banners | N/A | No |
| Coordinate mismatch | Warning banner | N/A | No |

Errors are French, non-crashing in reviewed paths, and recoverable where applicable.

---

## 13. Responsive / presentation audit

| Target | Risk |
|--------|------|
| 320 px narrow | Home spacers OK; Results scroll + sticky footer OK; **Camera confirm / Preview** use fixed Column without scroll → possible overflow on very short heights (P2) |
| Android portrait | Primary design target; overlay height clamps |
| Windows desktop | Content max width 720; works for digital demo |

Buttons and PDF export remain reachable on Results via bottom bar. Status banners wrap text.

---

## 14. Technical reliability audit

| Risk | Likelihood in live demo | Mitigation |
|------|-------------------------|------------|
| Backend not started | High if forgotten | Checklist: `run_demo.ps1` first |
| Accidental V2 | Medium | Health curl; avoid bare uvicorn |
| Wrong API URL (physical) | High on phone | N/A without device; Windows uses `127.0.0.1:8001` |
| Emulator networking | Low if `10.0.2.2:8001` | Documented |
| Firewall / Wi‑Fi | Medium for phone | Desktop demo avoids |
| Cold start latency | Medium first analyze | Warm up with one practice analyze |
| Large PNG RAM | Low–Med | Prefer rehearsed mid-size sample |
| PDF share OS quirks | Low–Med | Keep sample PDFs ready |
| Windows camera | May be unavailable | Do not depend on it for primary script |

**In-app gap:** Server Connection health result shows `status` / `service` / `version` (API `0.2.0`) but **does not surface `model_version`** from the health JSON — easy to miss V2 vs V5 without curl or Results label after analyze.

---

## 15. Performance audit

(From prior audits + current timeouts; **no new benchmarking**.)

| Item | Expectation |
|------|-------------|
| V5 IT infer (prior) | ~123–176 ms/image (CPU path cited previously) |
| Full `/analyze` | Dominated by YOLO + geometry; Flutter timeout **120 s** |
| First request | Slower (model cold load) |
| Loading UX | Indeterminate — acceptable |
| Memory | Full image in RAM up to 25 Mo — low-end risk |
| PDF compose | Extra raster of overlay — acceptable for demo |
| Test suites | Flutter ~98; backend ~167 — confidence in regressions |

**Student demo:** Acceptable if first analysis is warmed and image is a known dataset PNG.

---

## 16. Documentation audit

| Document | Consistency |
|----------|-------------|
| `mobile/README.md` | Aligns with `run_demo.ps1`, V5 health check, camera caveat, PDF |
| `backend/README.md` | Updated (no longer stub); documents V2 default vs demo V5 |
| `API_CONFIGURATION.md` | Correct defaults + dart-define; demo V5 |
| `CAMERA_CAPTURE.md` | Honest validation limits |
| `PDF_REPORT.md` | Matches implementation |
| `RELEASE_SIGNING.md` | Debug signing for demo — clear |
| **Connexion serveur (in-app)** | Step 2 still bare uvicorn → **contradicts** demo docs (P1 ops) |
| Phase 7A report | Historical: camera was P0 gap; **superseded for UI** by Phase 7B (validation gap remains) |
| Root README | Absent — demos rely on `mobile/` + `backend/` READMEs |

Obsolete “YOLO stub / AI not implemented” claims from early Phase 5 audit appear **fixed** in current `backend/README.md`.

---

## 17. Clinical / scientific claims audit

Searched user-facing UI and primary docs.

| Claim type | Finding |
|------------|---------|
| Diagnosis | Explicitly avoided; PDF disclaims |
| Guaranteed accuracy | Not claimed |
| Clinical validation of négatoscope photos | Explicitly **denied** in camera UI/docs |
| Autonomous medical decision | Not claimed |
| Certification | PDF: no device certification claimed |
| Unsupported thresholds | None in UI/PDF |

**Positioning match:** Consistent with « application de coxométrie assistée par IA » with review/QC and cautious measurement presentation.

**Narrator risk (not code):** Overstating phone-photo accuracy or skipping the prototype notice would be the main claim failure mode.

---

## 18. Surgeon perspective

**Strengths:** Bilateral VCE / Tönnis / CCD; overlay inspection; IT review salience; no false diagnosis labels; PDF for discussion.  
**Weaknesses:** No landmark edit; phone path unvalidated; VCE synonym “Wiberg” only in PDF; technical expander jargon.  
**Likely questions:** How accurate vs manual? What about photo of film? Can I correct a wrong IT? Where is CEA naming?  
**P1 before demo:** Script digital import; rehearse REVIEW case language (“vérification recommandée”, not failure).  
**P2:** Landmark correction UX later.

---

## 19. Radiologist perspective

**Strengths:** Domain-honest DICOM→PNG training story; QC states; coordinate-space awareness; no fabricated IT markers.  
**Weaknesses:** Not a PACS/DICOM viewer; no DICOM metadata; photo domain gap.  
**Likely questions:** Dataset size/domain? Inter-observer vs model? IT QC rules?  
**P1:** Keep claims to assisted measurement on digital XR.  
**P2:** DICOM import later.

---

## 20. Jury perspective

**Strengths:** End-to-end story; V5 + IT; professional FR UI; PDF; tests + APK; clear demo launcher.  
**Weaknesses:** Camera story incomplete without device; risk of V2 if startup wrong; academic prototype (HTTP LAN).  
**Likely questions:** Why not live camera? Is it certified? How do you start V5?  
**P1:** Startup checklist + digital path script.  
**P2:** Show camera screenshots/UI only as “prototype acquisition”.

---

## 21. Software / AI evaluator perspective

**Strengths:** Clean architecture (shared gallery/camera pipeline); model factory env switch; IT QC separation; reprojection + geometry separation; strong automated tests.  
**Weaknesses:** V5 architecture load via training-script path (known debt); code default V2; health UI omits `model_version`; no physical E2E.  
**Likely questions:** Failure modes? Latency? Train/val leakage? Coordinate mapping tests?  
**P1:** Prove V5 with `/health` live.  
**P2:** Decouple V5 build from training import; surface `model_version` in health UI.

---

## 22. 2–3 minute demo script (existing features only)

1. **(15 s)** Start backend: `.\backend\run_demo.ps1` → show `/health` → `model_version: v5_phase2`.  
2. **(10 s)** Launch Flutter Windows (or emulator): Home « Coxométrie ».  
3. **(20 s)** Optional 10 s: open « Prendre une photo » guidance → show framing + prototype notice → **Annuler** (do not depend on live capture).  
4. **(25 s)** « Importer une image » → select rehearsed `B26_*.png` from `datasets/yolo_pose_new_26/images/...` → Aperçu → **Analyser**.  
5. **(40 s)** Results: zoom landmarks → Mesures VCE/Tönnis/CCD → IT quality (or REVIEW banner if using B26_26-class case) → « Modèle : V5 Phase 2 ».  
6. **(30 s)** **Exporter le rapport** → open/share PDF → point disclaimer + measures.  
7. **(10 s)** Close: assisted coxometry, human verification, digital path validated; camera acquisition is prototype pending device/photo validation.

Total ≈ 2.5 minutes. Do **not** invent live négatoscope success.

---

## 23. P0 / P1 / P2 / P3 table

| ID | Pri | Area | Finding |
|----|-----|------|---------|
| — | **P0** | — | **None** for digital-import + `run_demo.ps1` demo |
| P1-1 | P1 | Ops | In-app Connexion serveur still instructs bare `uvicorn` → accidental **V2** |
| P1-2 | P1 | Ops | Health UI does not display `model_version` (easy to miss V2) |
| P1-3 | P1 | Demo prep | Must rehearse with known PNG + warm backend; script must not depend on physical camera |
| — | **Limitation** | Validation | Physical Android camera / négatoscope accuracy **not validated** (not classified P0 solely for absence) |
| P2-1 | P2 | UX | « Landmarks MVP » / ASL_L / bbox in technical expander |
| P2-2 | P2 | UX | Pinch-zoom vs scroll competition |
| P2-3 | P2 | UX | Camera confirm / Preview may overflow on very short 320px heights |
| P2-4 | P2 | Copy | Results « VCE » vs PDF « VCE / Wiberg » |
| P2-5 | P2 | UX | Home icon weakly pelvic |
| P3-1 | P3 | Platform | No versioned `ios/` |
| P3-2 | P3 | Product | Landmark correction / semi-auto edit |
| P3-3 | P3 | Clinical | Phone-photo validation dataset + perspective aids |
| P3-4 | P3 | Eng | Decouple V5 `build_model` from training script import |
| P3-5 | P3 | Perf | Optional pre-upload downscale for huge images |

---

## 24. Final verdict

# **DEMO_READY_WITH_P1**

**Not `DEMO_BLOCKED`:** Digital end-to-end path, V5 demo launcher, IT QC, measurements, PDF, FR UX, and automated tests support a credible 2–3 minute jury demonstration.

**Not full `DEMO_READY`:** Operational P1 items (accidental V2 via in-app bare uvicorn tip; health UI omitting `model_version`; demo must be scripted around lack of physical camera) should be closed or strictly checklist-mitigated before calling the presentation polished.

**Validation limitation (explicit):** Physical Android camera and real-world négatoscope photo accuracy remain **unvalidated**. APK build success does not close that gap.

---

## 25. Recommended next actions

1. **Demo run sheet (immediate, no code required):**  
   - `.\backend\run_demo.ps1`  
   - Confirm `/health` → `v5_phase2`  
   - `flutter run -d windows` (or emulator)  
   - Import rehearsed `B26_*.png` → analyse → PDF  
2. **Before polished jury (P1):** Fix or verbally override Connexion serveur uvicorn line; verify model via curl or Results label every time.  
3. **Optional short camera UI glance** only — do not stake the demo on live capture.  
4. **Do not** retrain, change geometry, thresholds, or claim négatoscope clinical validation.  
5. **Post-demo / P3:** Physical Android E2E when a device is available; photo-domain validation set.

---

## Audit integrity statement

- **Only deliverable written:** `datasets/yolo_pose_new_26/phase8a_final_pre_demo_audit.md`  
- **No** source, model, dataset, checkpoint, geometry, dependency, or test modifications  
- Read-only inspection of implementation and documentation as of 2026-09-04  

**End of Phase 8A final pre-demo audit.**
