# Phase 7B-0 — Camera / Négatoscope Technical Audit

**Date:** 2026-09-04  
**Mode:** READ-ONLY — no source, model, dataset, checkpoint, geometry, Flutter, backend, or dependency modifications except this report  
**Reference:** `datasets/yolo_pose_new_26/phase7a_doctor_requirements_audit.md` (Verdict B)  
**Evidence:** `mobile/lib/services/radiograph_picker.dart`, `image_normalizer.dart`, preview/analysis/results/report modules, `backend/app/services/{analyze,preprocessing*,measurement_service}.py`, `reprojection.py`, `mvp_geometry/*`, `datasets/yolo_pose_new_26/meta/source_mapping.csv`, AndroidManifest  

---

## Final verdict

# **CAMERA_MVP_READY_TO_IMPLEMENT**

**Meaning:** Engineering may proceed with a **narrow Option B** camera UX (framing guidance + preview/retake + honest unvalidated-photo warning) that reuses the existing `/analyze` path **without** changing V5 weights or `mvp_geometry`.

**Not implied:**

- V5 performance on négatoscope photographs is validated — **it is not**.  
- Perspective correction / glare algorithms are ready — **they are not**.  
- Clinical claims for photo-derived angles are allowed — **they are not** until a dedicated camera validation set exists.

---

## 1. Current camera implementation

### 1.1 Where `ImageSource.camera` is used

| Item | Detail |
|------|--------|
| Only call site | `FileRadiographPicker.pickFromCamera()` in `mobile/lib/services/radiograph_picker.dart` |
| API | `ImagePicker.pickImage(source: ImageSource.camera, imageQuality: 100, preferredCameraDevice: CameraDevice.rear)` |
| UI entry | `HomeScreen` OutlinedButton « Prendre une photo » → `_pick(RadiographSource.camera)` |
| Package | `image_picker: ^1.1.2` — **no** `camera` plugin custom preview |
| Web | Explicitly throws: camera unavailable on web |

**Not set:** `maxWidth`, `maxHeight` — full camera resolution (subject to OS / plugin defaults).

### 1.2 How the captured image is returned and stored

```
XFile (image_picker temporary path)
  → photo.readAsBytes()
  → normalizeRadiographBytes (decode → bakeOrientation → re-encode JPG@95 or PNG)
  → SelectedRadiograph { bytes, filename, width, height, orientationCorrected }
  → held in memory through Preview → Analysis → Results
```

| Aspect | Behavior |
|--------|----------|
| App-owned radiograph file | **Not written** by picker (bytes in RAM) |
| Source tag camera vs gallery | **Not stored** on `SelectedRadiograph` — paths merge after pick |
| Filename | `photo.name` or `'capture.jpg'` |
| Gallery path | `FilePicker` → bytes → **same** `_normalize` |

### 1.3 Decode / resize before preview

| Step | What happens |
|------|----------------|
| Decode | `package:image` `decodeImage` |
| Transform | `bakeOrientation` only (EXIF) |
| Resize | **None** on client before upload |
| Re-encode | JPG quality 95 (typical camera) or PNG |

Comment in `image_normalizer.dart`: full decode/re-encode in RAM; large images may stress memory; pre-upload resize noted as future optimization.

### 1.4 Preview → `/analyze`

| Step | File | Behavior |
|------|------|----------|
| Preview | `preview_screen.dart` | Shows bytes; « Analyser » → `AnalysisScreen` |
| Upload | `api_service.dart` | Multipart field `file`, ≤ 25 Mo, PNG/JPG/JPEG |
| Backend | `POST /analyze` | In-memory only (« Les images ne sont pas persistées ») |

### 1.5 EXIF and shared preprocessing

| Question | Answer |
|----------|--------|
| EXIF normalization on camera? | **Yes** — same `_normalize` as gallery |
| Backend EXIF? | **No** — client must bake (documented) |
| Backend preprocess on camera images? | **Yes, identical** — letterbox 512² gray (V2) or 640² RGB (V5) |
| Gallery and camera share code? | **Yes** after bytes exist (`_normalize` → `SelectedRadiograph` → same screens) |

### 1.6 Android permissions (declared, not device-validated)

`mobile/android/app/src/main/AndroidManifest.xml`:

- `CAMERA`  
- `INTERNET`  
- `READ_MEDIA_IMAGES` / legacy `READ_EXTERNAL_STORAGE` (gallery)  

No custom in-app camera preview screen exists today — system camera UI via `image_picker`.

---

## 2. End-to-end camera pipeline

```
[1] Home « Prendre une photo »
[2] OS camera UI (image_picker)
[3] XFile → bytes
[4] EXIF bake + re-encode          ← CLIENT (existing)
[5] ★ INSERT POINT (proposed)      ← CLIENT négatoscope prep (isolated)
[6] PreviewScreen
[7] AnalysisScreen → POST /analyze
[8] validate_upload_metadata
[9] preprocess_image / preprocess_image_v5   ← letterbox only
[10] V5 (or V2) inference
[11] reproject → original_image_pixels
[12] IT QC (V5)
[13] mvp_geometry VCE / Tönnis / CCD
[14] Results + optional PDF
```

### 2.1 Safe insertion point for négatoscope-specific preprocessing

**Preferred:** Flutter (or a dedicated client module) **after EXIF bake ([4]) and before Preview ([6])**, producing the final `SelectedRadiograph.bytes` that:

1. Are displayed in Preview / Results / PDF overlay  
2. Are uploaded as the multipart file  
3. Become the backend’s **original image** for letterbox + reprojection  

**Why here:**

- Keeps **V5 checkpoint and `mvp_geometry` untouched**  
- Preserves one coordinate space: whatever pixels are uploaded = overlay space  
- Avoids dual transforms fighting `reprojection.py` (letterbox inverse only)  

**Avoid:**

- Changing letterbox / detector / geometry formulas  
- Applying perspective warp **after** landmarks are computed  
- Sending an uncorrected photo for inference while overlaying a corrected preview (coordinate desync)

**Optional later:** a backend “photo_prep” stage **before** `preprocess_image_v5`, still emitting a single canonical image + identity metadata — only if client-side prep is insufficient. Not required for Option B MVP.

---

## 3. Négatoscope technical challenges

| Problem | Priority | Why | Current project support |
|---------|----------|-----|-------------------------|
| Perspective / keystone distortion | **P0** | Non-similarity warp changes angles between anatomical vectors | None |
| Oblique camera angle | **P0** | Same as perspective | None |
| Partial radiograph / missing anatomy | **P0** | Missing landmarks → wrong/incomplete measures | Soft: `available=false`; no FOV completeness gate |
| Severe rotation of film in frame | **P0–P1** | `_perp_cranial` uses image **y** to pick cranial — upright assumption | EXIF phone orient only; not film-in-frame |
| Motion blur | **P1** | Landmark detection failure / drift | None |
| Soft focus | **P1** | Same | None |
| Glare / specular reflections | **P1** | False edges / landmark confusion | None |
| Uneven illumination / exposure | **P1** | Contrast collapse vs training domain | None (pixel [0,1] normalize only) |
| Low contrast | **P1** | Detection degradation | None |
| Négatoscope / screen borders in FOV | **P1** | Background distractors; bbox may include frame | None |
| Surrounding dark/bright areas | **P1–P2** | Domain shift vs cropped digital XR | None |
| Crop too tight / asymmetric | **P1** | May clip landmarks | None |
| Phone auto-exposure / HDR | **P2** | Appearance shift | None |
| Simple rectangular crop of upright orthographic photo | **P2** if already near-frontal | Crop alone does not fix keystone | N/A |
| Cosmetic framing polish | **P3** | Presentation | None |

**Rule:** Do not claim an algorithm solves a problem unless this repo already implements or clearly can host it without new unverified medical thresholds. Today: **no** perspective, glare, blur, or completeness detectors exist.

---

## 4. Geometric integrity analysis

Core outputs today are **angles in degrees** (VCE, Tönnis, CCD), computed in the **same pixel space** as the landmarks after letterbox inference + inverse letterbox to “original” upload pixels. Overlay uses that original space.

| Transform | Coordinates | Angles (VCE/Tönnis/CCD) | Lengths (if ever) | Reprojection / overlay valid? |
|-----------|-------------|-------------------------|-------------------|-------------------------------|
| **Crop** (axis-aligned) | Shifted; must use cropped image as original | Preserved for points that remain | Preserved in px within crop | Yes **if** crop done **before** upload and overlay uses cropped bytes |
| **Uniform scale** | Scaled | Preserved | Scaled | Yes (letterbox already scales uniformly) |
| **Resize + letterbox** (existing backend) | Mapped via `scale`, `pad_*` | Preserved (similarity on content) | Scaled | Yes — `reprojection.py` |
| **Rotation 90°/180°/EXIF bake** | Remapped | **Pelvic-relative** constructions use ITH; **cranial choice** uses image `y` — large in-frame film rotation can flip sign conventions | Preserved magnitudes | Valid only if baked image is what is uploaded/displayed |
| **Perspective correction** (homography to film plane) | Non-linear map | Can **restore** angles toward film plane if corners correct; **wrong** corners **corrupt** angles | Distort unless ortho | Valid **only if** corrected image is the unique original for detect+overlay |
| **General affine** (anisotropic scale, shear) | Remapped | **Can change angles** | Distorted | Dangerous unless carefully constrained |
| **Contrast / brightness** | Unchanged geometry | Unchanged if detections stable | Unchanged | Yes geometrically; detection may change |
| **Non-uniform stretch** | Remapped | **Invalidates angles** | Distorted | Must not occur |

### Design constraints (must preserve)

1. One canonical image after any client prep.  
2. That image = upload = Results overlay = PDF raster.  
3. Backend continues: letterbox → detect → inverse letterbox only.  
4. **Do not modify `mvp_geometry`.**  
5. Prefer **no** anisotropic stretch. Perspective only if implemented as a proper planar rectification with user-confirmed corners, and only after validation — **out of Option B MVP**.

**Important:** A simple on-screen rectangular guide **does not** guarantee geometric preservation if the phone is not parallel to the film. Guidance reduces risk; it does not equal correction.

---

## 5. Proposed camera UX (design only — not implemented)

### 5.1 Clinician flow (evaluated)

```
« Prendre une photo »
  → Camera (system UI today / optional custom later)
  → Guidance (text ± frame overlay if custom preview)
  → Capture
  → Preview (existing PreviewScreen enhanced)
  → « Utiliser cette photo » | « Reprendre »
  → Optional soft quality warning (non-blocking)
  → Analyse (existing)
```

### 5.2 What is necessary for MVP

| Element | MVP? | Rationale |
|---------|------|-----------|
| Keep `image_picker` system camera | **Yes** | Already wired; no new plugin; lowest complexity |
| Preview + Utiliser / Reprendre | **Yes** | Retake is high value, low risk |
| Short FR guidance copy before/on preview | **Yes** | « Cadrez toute la radiographie, téléphone parallèle au négatoscope, évitez les reflets » |
| Custom live camera preview + overlay frame | **Optional P1** | Needs `camera` package + more UX; not required to start |
| Fancy focus/exposure controls | **No** | Unnecessary complexity |
| Auto perspective / ML crop | **No** for MVP | See §6–7 |
| Hard quality block | **No** | Unvalidated thresholds |

### 5.3 Minimal MVP UX recommendation

1. Before opening camera: 3–5 line guidance dialog.  
2. Capture via existing `pickFromCamera`.  
3. Enhanced Preview: guidance reminder + Utiliser / Reprendre (Retour already exists; make Retake explicit).  
4. Soft banner: photo path **not clinically validated** on négatoscope photos (research/demo).  
5. Then existing Analyze → Results → PDF.

---

## 6. Radiograph alignment (framing)

| Topic | Assessment |
|-------|------------|
| Portrait / landscape | Pelvic XR often landscape; phones often portrait — user must rotate phone or accept letterboxing in preview |
| Aspect ratio | Digital training images vary (~1:1 to ~1.5:1); no single film AR — frame should be **loose** (“fill most of the view”), not a fixed medical template |
| Safe area | Keep film interior away from screen edges; include both hips + teardrop region |
| Camera preview overlay | Only with custom `camera` preview; system camera cannot host in-app frame |
| Capture resolution | Currently full res; consider later `maxWidth`/`maxHeight` (e.g. 2048–3000 long side) to protect RAM/25 Mo — **uniform** only |
| Crop behavior | Optional post-capture crop of film rectangle: OK for geometry **if** phone≈parallel; **not** a substitute for perspective fix |

**Do not assume** a simple rectangular crop fixes keystone. Framing asks the user to **approximate** orthographic capture.

---

## 7. Perspective correction assessment

| Option | Description | Fit for this project now |
|--------|-------------|---------------------------|
| **A** Manual four-corner | User drags film corners → homography | Medium complexity; needs UI + warp lib; user error risk |
| **B** Automatic boundary detection | Document scanner / edge ML | Needs new deps + tuning; high false-positive risk on XR |
| **C** No correction in MVP | Rely on guidance + parallel phone | **Recommended for Phase 7B** |
| **D** Other | e.g. gyroscope “level” hint only | Possible lightweight add-on later |

### Recommendation: **C for Phase 7B MVP**

**Reasons:**

- No OpenCV / ML kit / document scanner in `pubspec.yaml` today  
- Adding CV deps expands scope and validation surface  
- Wrong automatic warp is **worse** than an honest uncorrected photo + warning  
- Core angles already work on **digital** import for demos  

**If later (post-MVP) A is chosen:**

- Possible libraries (identify only — **do not install now**): OpenCV (e.g. `opencv_dart`), `image` package limited warps, Android ML Kit document scanner, platform channels  
- Workflow: warp → **replace** `SelectedRadiograph.bytes` → upload that image → V5 sees rectified pixels → landmarks/reprojection/overlay stay consistent  

---

## 8. Image quality assessment (glare / QC)

| Signal | Detect now? | Gate type if added later |
|--------|-------------|---------------------------|
| Glare | Not implemented | Prefer **WARNING** |
| Blur | Not implemented | Prefer **WARNING** |
| Insufficient contrast | Not implemented | Prefer **WARNING** |
| Incomplete radiograph | Not implemented | Prefer **WARNING** (blocking only if zero landmarks — already API error) |
| Severe perspective | Not implemented | Prefer **WARNING** |

**Principles:**

- No unsupported medical quality thresholds  
- Prefer **conservative warnings** over hard blocks  
- Existing API failures (`no_detection`, etc.) remain the only hard stops  
- Phase 7B: static educational warning for camera path is enough  

---

## 9. Camera vs digital image comparison

| Factor | A) Native digital radiograph | B) Phone photo of négatoscope |
|--------|------------------------------|--------------------------------|
| Resolution | DICOM-native / rendered PNG (often 2–3k px) | Phone sensor; may be larger but optically resampled film |
| Noise | Detector / compression noise | Sensor noise + ambient + JPEG |
| Geometry | Near-orthographic digital projection | Perspective + possible keystone |
| Lighting | Controlled windowing | Ambient + backlight + glare |
| Perspective | Negligible for AP digital | Often non-negligible |
| Metadata | May have DICOM (not used in app) | EXIF orientation/GPS possible; app bakes orient, does not strip PHI burned in image |
| Calibration | Pixel spacing in DICOM (unused; angles only) | None |
| Reproducibility | High for same file | Low (pose, distance, tilt, lighting) |

### V5 validation on camera photographs?

**No.** Dataset `new_26` (26/26) maps to `source_dicom` under `bassin\a_annoter\…` (`meta/source_mapping.csv`). No metadata entries for phone / négatoscope / photograph sources.

**Validation gap (explicit):** V5 (and V2) performance on négatoscope phone photographs is **not validated**. Do not claim otherwise.

---

## 10. V5 validation gap (dataset composition)

| Content type in `new_26` | Present? | Evidence |
|--------------------------|----------|----------|
| Native digital radiographs (DICOM→PNG) | **Yes** | `source_mapping.csv` → DICOM UIDs |
| Photographed radiographs | **No evidence** | No matching meta |
| Négatoscope photographs | **No evidence** | No matching meta |

**Statement:** Camera workflow requires a **future validation dataset** (paired digital vs photo, and/or annotated photo cases) before any clinical performance claim. **Do not retrain in Phase 7B.** Implementation of acquisition UX may proceed with disclaimers; acceptance of photo-derived clinical use waits on validation.

---

## 11. Android / device requirements

| Topic | Status |
|-------|--------|
| Debug APK builds | Reported successful in prior phases — **not** camera validation |
| Physical Android camera test | **Not completed** (per Phase 7A / this audit scope) |
| Manifest `CAMERA` | Declared |
| Runtime permission | Handled by `image_picker` / Android OS — must be verified on device |
| Emulator camera | Often fake/black/unavailable — **insufficient** for négatoscope validation |
| Flutter behavior | System intent camera; cancel → `null`; deny permission → plugin error path |
| Windows / web | Camera not a clinical target (web throws; Windows camera limited) |

**Rule:** Do not claim camera functionality validated until **real-device** tests pass (§15).

---

## 12. Privacy assessment

| Question | Finding |
|----------|---------|
| Radiograph stored locally by picker? | **No durable app file** — bytes in memory (`SelectedRadiograph`) |
| Uploaded to backend? | **Yes** — multipart to `/analyze` |
| Backend persistence? | **No** — processed in memory (route docstring) |
| Temporary OS camera file? | Possible under OS/`image_picker` cache — **not controlled** by app code; treat as OS-managed |
| PDF contains image? | **Yes** — overlay raster embedded |
| PDF saved where? | App documents dir `rapport_coxometrie_*.pdf` + share sheet |
| Patient identifiers captured? | **No** app fields for name/ID/MRN; burned-in film text may remain in pixels/PDF |
| Cleartext HTTP? | Dev demo may use cleartext (`usesCleartextTraffic`) — LAN risk |

**Do not introduce new patient identifiers in Phase 7B.**

---

## 13. Implementation options

| Option | Scope | Complexity | Clinical risk | Demo value | Validation need | Priority |
|--------|-------|------------|---------------|------------|-----------------|----------|
| **A** Simple camera → existing pipeline | Already mostly true | Low | High if presented as validated | Low–medium | High before claims | Baseline only |
| **B** + framing guidance + retake + disclaimer | UX + copy | Low–medium | Medium (honest limits) | **High** | Still required for claims | **Recommended now** |
| **C** + perspective correction | Homography + UI/deps | High | High if wrong warp | High if correct | **Mandatory** paired tests | Later |
| **D** + perspective + quality checks | C + heuristics | Very high | Threshold risk | High | **Mandatory** | Future |

---

## 14. Recommended Phase 7B scope

### Implement now (Phase 7B)

1. **Option B** clinician UX: guidance dialog, explicit Retake, clearer Preview confirm.  
2. Keep **system camera** via existing `image_picker` (no new dependency required for B).  
3. Soft, non-blocking warning that camera/négatoscope path is **prototype / unvalidated**.  
4. Ensure camera and gallery still share EXIF normalize → Preview → `/analyze` → Results → PDF.  
5. Optional: uniform downscale long-edge cap if large captures approach 25 Mo / RAM issues (preserve aspect).  
6. Physical Android test protocol (§15).  
7. Unit/widget tests for cancel, retake navigation, large bytes, permission error messaging.

### Do **not** implement now

1. Automatic or manual perspective correction (Options C/D).  
2. New CV / OpenCV / ML Kit dependencies.  
3. V5 retrain or checkpoint changes.  
4. Dataset changes / photo labels.  
5. `mvp_geometry` changes.  
6. Hard quality gates with invented medical thresholds.  
7. PACS/DICOM, new coxometry parameters.  
8. Custom live viewfinder **unless** framing overlay is explicitly prioritized after B ships.

### Requires validation before clinical claims

1. Paired or annotated **négatoscope phone-photo** set.  
2. Agreement of VCE/Tönnis/CCD vs digital reference within predefined study protocol.  
3. Documented failure modes (glare, tilt, partial FOV).  

### Preserve existing V5 pipeline

- No model / geometry / letterbox / IT QC rule changes.  
- Any future prep must finish **before** upload so one image feeds detect + overlay.  
- Insertion point: §2.1 ★ after EXIF, before Preview.

---

## 15. Test plan

### 15.1 Automated / widget / integration (simulable)

| Test | Intent |
|------|--------|
| Camera source wiring | `pickFromCamera` invoked; mock `ImagePicker` returns bytes |
| Permission denial | Plugin/OS error → French error banner, no crash |
| Capture cancellation | `null` → stay on Home, no navigation |
| Successful capture | Bytes → Preview with dimensions |
| Preview | Image visible; metadata line |
| Retake | Back / Reprendre returns without analyze |
| Orientation | EXIF-oriented fixture → `orientationCorrected` / upright pixels |
| Large camera image | Near 25 Mo reject client-side; slightly under accepted |
| Upload | Multipart `file` field, correct content-type |
| API failure | AnalysisScreen error + retry |
| Preprocessing failure | Unsupported/corrupt bytes → friendly error |
| Coordinate consistency | Overlay coords match uploaded dimensions (`coordinate_space`) |
| V5 inference | Mock/real backend `model_version` + IT QC parse |
| Results | Measures + REVIEW banner |
| PDF | Export uses same radiograph bytes |

### 15.2 Physical Android tests (cannot be replaced by unit tests)

| Test | Pass criteria |
|------|----------------|
| Real rear camera open | System camera launches |
| Permission grant/deny | Expected UX |
| Photo of **printed or lightbox / négatoscope** film | Capture returns; Preview shows film |
| Parallel vs tilted phone | Observe detection/measure stability **qualitatively**; record issues |
| Glare angle | Document failure/warning need |
| End-to-end analyze on LAN | Results + PDF on device |
| Emulator vs device | Confirm emulator is **not** sufficient sign-off |

---

## 16. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Users trust photo angles as clinically validated | High | Explicit disclaimer; no diagnostic language |
| Perspective tilt silently biases angles | High | Guidance; defer correction; validation study |
| Domain shift → missed landmarks | High | Retake UX; existing incomplete/REVIEW states |
| Large photos OOM / slow EXIF bake | Medium | Optional max dimension; monitor on device |
| OS temp files / shared PDF PHI | Medium | Process hygiene; user education; no new IDs |
| Scope creep into OpenCV perspective | Medium | Stick to Option B |
| Emulator false confidence | Medium | Require physical device sign-off |

---

## 17. Acceptance criteria (Phase 7B engineering)

Phase 7B **engineering** is accepted when:

1. Doctor can open camera from Home, capture, preview, retake, and analyze on a **physical Android device**.  
2. Guidance + unvalidated-photo warning are visible on the camera path.  
3. Camera-captured bytes still pass EXIF bake → `/analyze` → V5 (or configured model) → Results → PDF without model/geometry changes.  
4. Gallery path remains intact.  
5. Automated tests cover cancel / error / happy path mocks.  
6. Written note states: **photo-derived measurements are not clinically validated** pending a camera validation dataset.

Phase 7B does **not** accept:

- Claims of validated négatoscope accuracy  
- Perspective/glare auto-correction as complete  
- APK build alone as camera validation  

---

## Appendix — Evidence index

| Topic | Path |
|-------|------|
| Camera pick | `mobile/lib/services/radiograph_picker.dart` |
| EXIF | `mobile/lib/utils/image_normalizer.dart` |
| Home CTA | `mobile/lib/screens/home_screen.dart` |
| Preview / Analyze | `preview_screen.dart`, `analysis_screen.dart` |
| Upload limits | `mobile/lib/services/api_service.dart`, `backend/.../analyze.py` |
| No backend persist | `backend/app/api/routes/analyze.py` |
| Letterbox + meta | `preprocessing.py`, `reprojection.py` |
| PDF persistence | `report_export_service.dart` |
| Manifest | `mobile/android/app/src/main/AndroidManifest.xml` |
| Digital-only dataset | `datasets/yolo_pose_new_26/meta/source_mapping.csv` |
| Phase 7A | `phase7a_doctor_requirements_audit.md` |

---

**PHASE7B0_CAMERA_TECHNICAL_AUDIT_COMPLETE — READ-ONLY — NO IMPLEMENTATION**
