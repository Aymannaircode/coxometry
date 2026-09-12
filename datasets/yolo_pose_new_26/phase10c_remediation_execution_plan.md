# Phase 10C — Legacy Landmark Remediation Program  
## Controlled Execution Plan (STOP AFTER THIS DOCUMENT)

**Date:** 2026-09-04  
**Mode:** PLAN ONLY — **no training, no dataset modification, no source-code modification**  
**Basis:** Phase 10B root-cause audit + live repository inspection  
**Preferred strategy:** OPTION F (QA → expand data → gated pose fine-tune → protect IT + good KP → manual bridge)

---

## Executive recommendation

Execute remediation as a **versioned, gated program** that never overwrites production assets.

| Decision | Choice |
|----------|--------|
| Dataset | New namespace `datasets/yolo_pose_remediation_v1/` — **copy** of original 26 + new cases; original `yolo_pose_new_26` untouched |
| Annotations | Locked definitions from `docs/landmark_specification.md` / `docs/annotation_guidelines.md`; QA checklist for ASL/FSP/FSD |
| Init weights | **Safer than naive V5 IT training:** copy of **V2** `best.pt` for legacy KP0–13 fine-tune (V3 pattern). V5 Phase 2 `best_it.pt` kept intact; IT weights reused unchanged at compose time |
| Why not train “on V5” first? | V5 Phase 2 script trains **IT only** with **cv4 frozen**. Improving ASL/FSP/FSD requires training the **legacy pose head**. Repo already designed this as V3 soft fine-tune from V2 |
| Production path | Unchanged until gates pass. Candidate = new remediation checkpoint + optional later compose with frozen V5 IT |
| Manual bridge | Backend `POST /measurements` `mode=landmarks` already exists; Flutter drag-edit is a **later** product phase — document only here |
| This phase | Produce plan → **STOP for approval** |

**Do not start a long training run until this plan is approved and Steps A–D below complete.**

---

## 1. Current baseline (frozen references)

### 1.1 Production checkpoints (DO NOT OVERWRITE)

| Role | Exact path |
|------|------------|
| **V2 production** | `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt` |
| V2 last | `…/yolo_pose_new_26_v2-3/weights/last.pt` |
| **V5 Phase 2 IT** | `runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756/weights/best_it.pt` |
| V5 last_it | `…/run_20260829_032756/weights/last_it.pt` |
| V5 surgical init (immutable) | `runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt` |

Backend loaders (must remain pointed at production until explicit promotion):

- V2: `backend/app/services/detection/yolo_pose.py` → `DEFAULT_V2_MODEL_PATH`
- V5: `backend/app/services/detection/v5_phase2_pose.py` → `best_it.pt` + `train_yolo_pose_v5_phase2.py` architecture

### 1.2 Original dataset (DO NOT MODIFY)

| Asset | Path |
|-------|------|
| Dataset root | `datasets/yolo_pose_new_26/` |
| Images/labels | `images/{train,val}/`, `labels/{train,val}/` |
| Split | `meta/split.json` (seed 42; 21 train / 5 val / **0 test**) |
| Mapping | `meta/source_mapping.csv` |
| Annotations JSON | `annotation_pilot/annotations/new_26/` |
| DICOM sources (26) | `bassin/a_annoter/` |

### 1.3 Phase 9B baseline metrics (val @640, V2≡V5 KP0–13)

| Landmark | Mean err | Notes |
|----------|---------:|-------|
| ASL_L | **104.9** | All 5 closer to ASM_L than ASL_L |
| FSP_L | 42.6 | Lateral+caudal bias |
| FSD_R | 39.0 | Lateral+cranial |
| FSD_L | 35.4 | Often cranial |
| ASL_R | 32.8 | Systematic shift |
| FSP_R | 28.8 | Caudal bias |
| Good KP (FHC/FNM/TD/ASM) | ~13.5–17.9 | Protect |
| IT_R/IT_L | ~25–28 | Protect; separate head |

Evidence files: `phase9b_landmark_errors.csv`, `phase9b_full_landmark_accuracy_audit.md`, `phase10b_legacy_landmark_root_cause_audit.md`.

---

## 2. Reproducible remediation tooling map (actual repo files)

Inspected — **do not assume new filenames until approved scripts are added in a later sub-phase.**

### 2.1 Dataset expansion / preparation

| Purpose | Existing artifact | Notes for 10C |
|---------|-------------------|---------------|
| Build YOLO images+labels from JSON | `annotation_pilot/scripts/prepare_yolo_pose_new_26.py` | Hard-codes `OUTPUT_ROOT=…/yolo_pose_new_26`. **Do not re-run against original.** After approval: clone pattern → new `prepare_yolo_pose_remediation_v1.py` writing to `datasets/yolo_pose_remediation_v1/` |
| DICOM→PNG | `annotation_pilot/manual_annotation_tool/dicom_render.py` | Used by prepare + inference scripts |
| Source inventory | `datasets/yolo_pose_new_26/meta/source_mapping.csv` | Template for remediation mapping |
| Extra DICOM pool | `bassin/<PATIENT_*>/` (~33 named dirs) + `bassin/a_annoter/` (26 used) | Hard-example candidates; **no fabrication** |
| Annotation UI | `annotation_pilot/manual_annotation_tool/server.py` | `LANDMARKS` currently lists **14** KP (no IT in tool list); IT annotated via B6 JSON path |

### 2.2 Annotation validation

| Purpose | Existing artifact |
|---------|-------------------|
| Spec | `docs/landmark_specification.md` |
| Annotator guide | `docs/annotation_guidelines.md` |
| Prior QA | `datasets/yolo_pose_new_26/landmark_annotation_quality_audit.md` |
| Flip audit | `annotation_pilot/scripts/audit_horizontal_flip_new_26.py` → `horizontal_flip_audit.md` |
| Keypoint mapping audit | `annotation_pilot/scripts/audit_keypoint_mapping_new_26.py` |
| B6 working JSON pattern | `datasets/yolo_pose_new_26/b6_working_annotations/` |
| Visual overlays | `annotation_pilot/scripts/visualize_yolo_pose_new_26.py` |

### 2.3 Train / val / test split

| Purpose | Existing artifact |
|---------|-------------------|
| Current split | `datasets/yolo_pose_new_26/meta/split.json` |
| Split logic | `prepare_yolo_pose_new_26.py` (`SPLIT_SEED=42`, `VAL_RATIO=5/26`) |
| Gap | **No test split today** — remediation dataset **must** introduce `images/test` + `labels/test` |

### 2.4 Pose fine-tuning (legacy KP)

| Purpose | Existing artifact | Fit for ASL/FSP/FSD |
|---------|-------------------|---------------------|
| Soft fine-tune from V2 | `annotation_pilot/scripts/train_yolo_pose_v3_new_26.py` + `datasets/yolo_pose_new_26/v3_train_config.yaml` | **Best template** (low LR, mild aug, copies init, `exist_ok:false`) |
| 16 KP attempt | `train_yolo_pose_v4_new_26.py` + `v4_training_config.yaml` | Historical failure mode — **do not reuse as-is** |
| V5 IT-only | `train_yolo_pose_v5_phase2.py` + `v5_phase2_training_config.yaml` | Improves IT only; **cv4 frozen** — wrong objective for this program |
| V5 Phase1 variants | `train_yolo_pose_v5_phase1*.py` | IT experiments — out of scope |

**Planned (after approval, not now):**  
`annotation_pilot/scripts/train_yolo_pose_remediation_v1.py` +  
`datasets/yolo_pose_remediation_v1/remediation_v1_train_config.yaml`  
modeled on **V3** script (SHA256 init copy, preflight, `--train` explicit).

### 2.5 Checkpoint saving

| Mechanism | Location pattern |
|-----------|------------------|
| Ultralytics runs | `runs/pose/<name>/weights/{best,last}.pt` |
| V3 safety pattern | Copy init to `runs/pose/.../init/` then train with `exist_ok: false` |
| V5 Phase2 | Timestamped `run_YYYYMMDD_HHMMSS/weights/best_it.pt` |

**Remediation naming (mandatory):** see §10.

### 2.6 Evaluation

| Purpose | Existing artifact |
|---------|-------------------|
| Per-landmark px errors | `analyze_landmark_errors_new_26.py`, `analyze_v2_errors_new_26.py`, `analyze_asl_l_error_new_26.py`, `analyze_asl_asm_new_26.py` |
| Train vs val | `analyze_v2_train_vs_val_new_26.py` |
| Phase 9B method | `datasets/yolo_pose_new_26/_phase9b_audit_temp/run_phase9b_audit.py` |
| Inference dump | `run_yolo_pose_inference_new_26.py` (V2); `run_yolo_pose_inference_v3_new_26.py`; `run_yolo_pose_inference_v4_new_26.py` |
| Anatomy validate | `validate_v2_anatomy_new_26.py` |
| V3 regression audit | `audit_v3_regression_new_26.py` |

### 2.7 Measurement / geometry evaluation

| Purpose | Existing artifact |
|---------|-------------------|
| VCE/Tönnis/CCD from preds | `test_v2_geometry_new_26.py`, `test_v3_geometry_new_26.py`, `test_v4_geometry_new_26.py` |
| Geometry engine | `mvp_geometry/` (**do not modify**) |
| YOLO→MVP adapter | `mvp_geometry/yolo_adapter.py` |

### 2.8 Regression testing (product)

| Purpose | Existing artifact |
|---------|-------------------|
| Backend suite | `backend/tests/` (incl. measurements landmarks mode) |
| Flutter suite | `mobile/` tests |
| Checkpoint parity history | `v5_phase2_checkpoint_integration_audit.md` / `.csv` |

---

## 3. Dataset plan

### 3.1 Versioned namespace

```
datasets/yolo_pose_remediation_v1/
  images/{train,val,test}/
  labels/{train,val,test}/
  meta/
    split.json
    source_mapping.csv
    keypoint_order.md          # copy of 16-KP order; do not reorder
    provenance.md              # SHA256 of sources, copy date
    qa_checklist.md            # this protocol excerpt
  data.yaml                    # path → remediation_v1 only
  README.md                    # “derived from new_26; original untouched”
```

**Original** `datasets/yolo_pose_new_26/` remains the recoverable production dataset.  
Remediation images/labels are **copies** (or new renders), never in-place edits of original files.

### 3.2 Content targets

| Stage | Total images | Composition |
|-------|-------------:|-------------|
| v1.0 seed | 26 | Bit-identical copies of current B26 PNGs + labels (16 KP) |
| v1.1+ expansion | **40–80** | Seed + **new** hard AP pelvis cases (DICOM-derived) |
| Aspiration | ≥60 with **≥15 test** | Prefer quality over rushing to 80 |

### 3.3 Split policy (new)

| Split | Share (guidance) | Rules |
|-------|------------------|-------|
| Train | ~65–70% | Learning only |
| Val | ~15–20% | Early stop / hyperparams |
| **Test** | **≥15 images or ≥20%** | **Never trained; never tuned on** |
| Continuity probe | Keep original 5 val IDs evaluable | Report Phase 9B continuity separately |

- New seed for remediation split (document in `meta/split.json`); **do not silently reshuffle** original IDs across train/val without logging.  
- Stratify when possible: shaft FOV length, ASL difficulty tag, image quality.

### 3.4 What is NOT allowed

- Fabricating or duplicating images (flip-as-new-case, copy-paste clones as extra IDs)  
- Editing original `yolo_pose_new_26` labels “in place”  
- Mixing phone-négatoscope photos into v1 without an explicit domain tag and separate analysis stratum

---

## 4. Annotation protocol (problem KP focus)

**Do not redefine landmarks.** Use locked project definitions.

### 4.1 ASL_R / ASL_L (locked)

| Item | Rule |
|------|------|
| Definition | Most **lateral** point of the **sclerotic acetabular sourcil** (weight-bearing roof) |
| Not ASL | Osteophyte/rim spur outside sourcil (= optional ALB, out of scope unless separately annotated) |
| Not ASL | ASM (medial sourcil), FHC, random roof point |
| L/R | Anatomical right/left; ASL_R x &lt; ASM_R; ASL_L x &gt; ASM_L |
| Visibility | If sourcil cannot be distinguished → `v=0`, coordinates `(0,0)` — **no invented point** |
| QA flag | Reject if ASL closer to ASM than expected lateral margin without documented short sourcil |

### 4.2 FSP_R / FSP_L (locked)

| Item | Rule |
|------|------|
| Definition | Point on **median proximal femoral shaft axis**, just **below lesser trochanter** (or first level with clear parallel cortices) |
| Not FSP | Neck axis, trochanter tip, FSD |
| L/R | Homolateral to femoral side |
| Visibility | If proximal shaft not clear → `v=0` |

### 4.3 FSD_R / FSD_L (locked)

| Item | Rule |
|------|------|
| Definition | Point on **median shaft axis**, **most distal still visible** with identifiable cortices |
| Not FSD | Extrapolate below FOV / invent below image border |
| FOV policy | If shaft too short for stable axis → prefer `v=0` for FSD (CCD unavailable) rather than guessing — **confirm with physician in Step A** |
| L/R | Homolateral; FSD distal to FSP (larger y on AP) |

### 4.4 Preserve other landmarks

TD, FHC, ASM, FNM, IT: existing guidelines unchanged. IT continues via B6 / 16-KP JSON policy (`bi_ischial_final_policy.md`).

### 4.5 Per-case annotation checklist (required fields)

For every new or QA’d case, annotator records:

1. Anatomical correctness (sourcil vs rim called out if ambiguous)  
2. Left/right correctness  
3. Visibility decision + `v` ∈ {0, 2} only  
4. No invented / extrapolated points  
5. Geometric self-check: ASL lateral to ASM; FSD distal to FSP; R left of L for paired lateral points  
6. Reviewer second pass on **all problem KP** for val+test; ≥30% of train  

### 4.6 Tools

- Primary: `annotation_pilot/manual_annotation_tool/`  
- Store remediation JSON under e.g. `annotation_pilot/annotations/remediation_v1/` (**new dir**, not overwriting `new_26`)  
- Promote to YOLO only via dedicated prepare script → `yolo_pose_remediation_v1`

---

## 5. Hard-example strategy

### 5.1 Goal

Enrich supervision where V2 fails: **left lateral sourcil**, **short/noisy shafts**, variable roofs — without synthetic duplicates.

### 5.2 Selection pool (real sources)

1. Unused `bassin/<PATIENT_*>/` DICOM folders (~33 named patient dirs observed)  
2. Any additional AP pelvis DICOMs obtained under the same clinical acquisition protocol  
3. **Exclude** intentional copies of B26_*; exclude rejected/`rejetees` unless physician re-qualifies

### 5.3 Triage rubric (before full 16-KP annotation)

Score each candidate PNG (render once for review):

| Tag | Prefer if… |
|-----|------------|
| `ASL_hard` | Low sourcil contrast, osteophyte near roof, short/irregular sourcil, left roof challenging |
| `SHAFT_hard` | Short FOV, faint cortices, mild rotation, overlapping bowel gas on shaft |
| `SIZE_var` | Unusually large/small pelvis scale in frame |
| `QUALITY_var` | Underexposure, noise, mild blur (still diagnostically readable) |
| `ROT_mild` | Mild pelvic/femoral rotation (not extreme non-AP) |
| `OVERLAP` | Soft-tissue / gas overlap near roof or shaft |

**Selection rule:** prioritize cases with ≥2 hard tags; ensure mix of easy gold cases too (avoid only-nightmare set).

### 5.4 Explicit non-methods

- No GAN/synth radiographs  
- No using horizontal flip of an existing labeled case as a “new” ID  
- No mosaic composites as GT images

---

## 6. Training strategy (gated fine-tune)

### 6.1 Architectural decision (repo evidence)

| Approach | Verdict |
|----------|---------|
| Train via current `train_yolo_pose_v5_phase2.py` | **Reject for legacy fix** — IT-only, cv4 frozen |
| Full V4-style 16 KP reinit | **Reject** — prior anatomical collapse |
| Soft fine-tune from **V2 best** (V3 pattern) on remediation dataset | **Accept as primary track** |
| Later compose: remediation KP0–13 + **unchanged** V5 IT weights | Preferred production assembly after gates |

This improves ASL/FSP/FSD while **not changing IT architecture**. IT head code and `best_it.pt` stay frozen.

### 6.2 Experiment identity

| Field | Value |
|-------|-------|
| Experiment ID | `remediation_v1` |
| Init source | Copy of V2 `…/yolo_pose_new_26_v2-3/weights/best.pt` |
| Init dest (example) | `runs/pose/yolo_pose_remediation_v1/init/v2_best_epoch80_COPY.pt` |
| Run name | `yolo_pose_remediation_v1` + timestamp suffix if re-run |
| `exist_ok` | **false** |
| Data YAML | `datasets/yolo_pose_remediation_v1/data.yaml` only |

### 6.3 Proposed hyperparameter envelope (proposal only — not launched)

Aligned with proven-safer `v3_train_config.yaml`, adjusted for remediation:

| Param | Proposed | Rationale vs V2 |
|-------|----------|-----------------|
| `epochs` | 40–60 | Early stop on gates |
| `patience` | 10–15 | |
| `imgsz` | **640** first (parity with Phase 9B); optional 960 pilot later | Avoid V3 1280 CPU shock unless approved |
| `batch` | 1–2 | CPU reality |
| `lr0` | **1e-4 → 3e-5** range | V2 used 0.01 (destructive for fine-tune) |
| `optimizer` | AdamW | |
| `seed` | 42 (document) | |
| `pose` loss | 12.0 (equal) initially; optional later upweight ASL/FSP/FSD **only if** script supports it without code hacks in geometry | |
| Freeze | Prefer freeze backbone early epochs if script supports; **never train IT in this run** | |
| Device | cpu (match project) unless GPU approved |

### 6.4 Phased training (after approval)

| Phase | Data | Goal |
|-------|------|------|
| **T0 smoke** | Current 26 copy only | Verify pipeline; expect limited ASL_L gain |
| **T1 main** | ≥40–60 remediation set | Meet engineering gates on **test** |
| **T2 optional** | ≥80 | Push ASL_L / shaft further |

**No T1 until annotation QA + expansion approved.**

### 6.5 IT protection procedure

1. Do not load `best_it.pt` as trainable Ultralytics pose weights for this experiment.  
2. After remediation KP0–13 acceptance, **compose** inference path: new legacy head OR new V2-like `best.pt` + existing V5 IT wrapper — exact compose script designed in Phase 10D, not now.  
3. IT regression gate: same decode metrics as Phase 9B / Phase 2 audit within tolerance.

---

## 7. Augmentation strategy

### 7.1 V2 production aug (harmful for these points)

From `runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/args.yaml`:

| Aug | V2 | Risk to ASL/shaft |
|-----|-----|-------------------|
| `mosaic` | 1.0 | **High** — fragments pelvic anatomy |
| `auto_augment` | randaugment | **High** — aggressive appearance distortion |
| `erasing` | 0.4 | **High** — can erase sourcil/shaft cues |
| `scale` | 0.5 | Medium–high |
| `translate` | 0.1 | Medium |
| `fliplr` | 0.5 | **Keep** if `flip_idx` correct (validated) |
| `hsv_*` | strong | Medium |

### 7.2 Conservative proposal (match V3/V4 lessons)

| Aug | Proposed remediation_v1 |
|-----|-------------------------|
| mosaic / mixup / cutmix / copy_paste | **0** |
| auto_augment | **null** |
| erasing | **0** |
| fliplr | **0.5** (flip_idx must match 14 or 16 KP YAML) |
| flipud | 0 |
| degrees / shear / perspective | 0 |
| translate | 0.03–0.05 |
| scale | 0.15–0.20 |
| hsv_h / s / v | 0.005–0.01 / 0.3–0.4 / 0.2–0.3 |

**Do not implement config file until approval** — then write `remediation_v1_train_config.yaml` only.

---

## 8. Gated acceptance criteria (define BEFORE training)

Coordinate space for KP gates: **letterbox 640×640** (Phase 9B method) + report original-px companion.

### 8.1 Per-landmark metrics (all 16 KP)

For each landmark compute on **test** (primary) and val (secondary):

- n, mean, median, p90, max  
- % &lt;25 / &lt;50 / &lt;75 px  
- mean Δx, mean Δy  
- For ASL_L: **% predictions closer to ASM_L GT than ASL_L GT** (must fall sharply)

### 8.2 Problem-group improvement gates (test set)

| Landmark | Engineering target (mean @640) | Hard fail |
|----------|--------------------------------:|-----------|
| ASL_L | ≤ **35** (stretch ≤25) | mean &gt;60 **or** ASM-collapse rate ≥20% |
| ASL_R | ≤ **25** | mean &gt;40 |
| FSP_R / FSP_L | ≤ **30** | mean &gt;45 |
| FSD_R / FSD_L | ≤ **30** | mean &gt;50 |

Must also beat V5/V2 Phase 9B means by a clear margin on ASL_L (e.g. ≥40% relative reduction).

### 8.3 Regression gates vs V5 Phase 2 (and V2 for KP0–13)

On the **same evaluation images** (continuity: original 5 val + remediation test):

| Protected | Max allowed mean degradation @640 vs V5/V2 baseline |
|-----------|-----------------------------------------------------|
| FHC_R/L, FNM_R/L, TD_R/L, ASM_R/L | **+5 px** mean (hard fail **+10 px**) |
| IT_R/IT_L | **+5 px** mean; QC path unbroken (hard fail +10 px or new systematic failure) |
| Detection | No collapse of pelvis detect rate |

Compare three columns always:

`V2 | V5 Phase 2 | remediation_v1_candidate`

### 8.4 Promotion rule

Promote **only if**:

1. Problem-group gates pass on **test**  
2. All regression gates pass  
3. Measurement gates (§9) show engineering improvement or non-worsening  
4. Manifest + SHA256 recorded  
5. Human visual review of ASL_L on ≥10 test cases  

Else: **reject checkpoint**; keep production V2/V5.

---

## 9. Clinical measurement gates (engineering only)

### 9.1 Method

1. Build GT angles from **verified** GT landmarks via `mvp_geometry.compute_all_sides` (unchanged).  
2. Build pred angles from model landmarks the same way (`test_v2_geometry_new_26.py` pattern).  
3. Absolute error `|pred − GT|` per side for **VCE, Tönnis, CCD**.

### 9.2 Report

| Measure | Stats |
|---------|-------|
| VCE_R, VCE_L | mean, median, p90, max abs error (°) |
| Tönnis_R/L | same |
| CCD_R/L | same |

Stratify: exclude sides where required KP `v=0`.

### 9.3 Engineering acceptance (not clinical validation)

- ASL_L-driven **VCE_L / Tönnis_L** mean abs error must **improve** vs V2/V5 baseline on test.  
- CCD errors must not worsen beyond agreed Δ when FSP/FSD improve.  
- **No invented degree thresholds claiming clinical adequacy.**

### 9.4 Explicit distinction

| Term | Meaning |
|------|---------|
| **Engineering acceptance** | Reproducible numeric gates vs GT labels / prior checkpoints |
| **Clinical validation** | Physician comparison study — **out of scope for automatic pass/fail here**; schedule separately |

---

## 10. Checkpoint safety & naming

### 10.1 Rules

- Every run → **new directory**; `exist_ok: false`  
- Never write into `yolo_pose_new_26_v2-3/` or `yolo_pose_new_26_v5_phase2/run_20260829_032756/`  
- Init = **copy** with SHA256 verify against source  

### 10.2 Proposed layout

```
runs/pose/yolo_pose_remediation_v1/
  init/
    v2_best_epoch80_COPY.pt
    init_manifest.json          # source path, SHA256, copy UTC time
  run_YYYYMMDD_HHMMSS/
    args.yaml / remediation_v1_train_config.snapshot.yaml
    weights/best.pt
    weights/last.pt
    results.csv
    metrics/
      landmark_errors_test.csv
      regression_vs_v5.csv
      geometry_errors_test.csv
    MANIFEST.json               # see fields below
```

### 10.3 `MANIFEST.json` required fields

- `experiment_id`, `created_utc`  
- `source_checkpoint` + `source_sha256`  
- `init_checkpoint` + `init_sha256`  
- `output_best` + `best_sha256`  
- `dataset_version` (`yolo_pose_remediation_v1@<tag>`)  
- `image_count` train/val/test  
- `split_path`  
- `train_config` snapshot  
- `augmentation` snapshot  
- `random_seed`  
- `metrics_summary` (problem KP + regression)  
- `gate_result`: `PASS` | `FAIL`  
- `operator_notes`

---

## 11. Manual correction safety bridge (architecture confirm — no implement)

### 11.1 Already available

| Layer | Status |
|-------|--------|
| Backend `POST /measurements` `mode=landmarks` | **Exists** — recomputes VCE/Tönnis/CCD from JSON (`backend/app/api/routes/measurements.py`, `pipeline.py`) |
| Schema | `backend/app/schemas/measurements.py` |
| Tests | `backend/tests/test_api.py`, `test_schemas.py` |
| Flutter drag-edit UX | **Missing** (Phase 10 R19) |
| PDF from corrected landmarks | Possible once Results holds edited landmarks → existing PDF builder path |

### 11.2 Target workflow (future phase)

```
AI predict (V5 / remediation)
  → physician adjusts landmark(s) in UI
  → POST measurements mode=landmarks OR local mvp_geometry
  → Results update
  → PDF uses corrected landmarks
```

### 11.3 This Phase 10C plan

**Do not implement Flutter editor now.**  
Minimal bridge if urgently needed later: documented API-only correction for lab/demo — still requires approval.

---

## 12. Exact execution steps (ordered) — STOP points

### Gate 0 — Approval of this document
- [ ] Stakeholders approve Option F plan, dataset name, gates, naming  
- **STOP here until approved**

### Step A — Definition / FOV policy lock (no code)
- [ ] Physician confirms FSD short-FOV → `v=0` vs keep-at-edge policy  
- [ ] Confirm A1 examples (sourcil vs rim) for annotator training  
- **No training**

### Step B — QA confirm on original 26 (read + optional new JSON dir)
- [ ] Double-read ASL/ASM/FSP/FSD on all 26; edit **only** into `annotations/remediation_v1/` if corrections needed  
- [ ] Never edit `annotations/new_26` or `labels/` of original dataset in place  
- **No training**

### Step C — Create dataset namespace (after approval)
- [ ] Create `datasets/yolo_pose_remediation_v1/`  
- [ ] Copy 26 images/labels; write provenance SHA256  
- [ ] Add `data.yaml`, `meta/*`  
- **No training**

### Step D — Hard-example triage + annotate expansion
- [ ] Triage `bassin/` pool with rubric §5  
- [ ] Annotate to 40–80 total with checklist §4  
- [ ] Build train/val/**test** split  
- **No training**

### Step E — Add training/eval scripts + config (new files only)
- [ ] `train_yolo_pose_remediation_v1.py` (V3-pattern)  
- [ ] `remediation_v1_train_config.yaml`  
- [ ] Eval harness adapting Phase 9B + geometry scripts → remediation paths  
- [ ] Preflight only (`python …` without `--train`)  
- **No long train yet**

### Step F — T0 smoke train (explicit `--train`, short)
- [ ] Verify losses, no overwrite of V2/V5, manifest written  
- [ ] Run regression pack  

### Step G — T1 main train on expanded set
- [ ] Full gates §8–§9 on **test**  
- [ ] PASS → candidate; FAIL → rollback (§14)

### Step H — Compose with V5 IT (separate sub-phase)
- [ ] Only after T1 PASS  
- [ ] Do not modify IT weights  

### Step I — Product promotion (separate approval)
- [ ] Backend path switch only with explicit go/no-go  
- [ ] Flutter manual edit scheduled independently  

**Phase 10C PLAN status:** Steps A–I are scheduled; **this deliverable ends at Gate 0 / plan publication.**

---

## 13. Risks

| Risk | Mitigation |
|------|------------|
| Fine-tune destroys good KP | Low LR; regression gates; reject on fail |
| Train on 26 only → no ASL_L fix | Require expansion before T1 success claims |
| Accidental overwrite of V2/V5 | Separate dirs; `exist_ok:false`; preflight path checks |
| Label drift / redefined ASL | Locked docs; checklist; physician exemplars |
| Domain mix (photo vs DICOM) | Tag domain; stratify metrics |
| Treating engineering pass as clinical validation | Explicit §9.4 language |
| Expanding hard-coded ASL offsets | Forbidden |
| Using V5 Phase2 trainer for legacy KP | Forbidden |

---

## 14. Rollback plan

If any remediation run fails gates or threatens production:

1. **Do not** change backend `MODEL_VERSION` / default paths  
2. Delete or quarantine failed `runs/pose/yolo_pose_remediation_v1/run_*` (optional); keep manifests for autopsy  
3. Production remains:
   - V2 `…/yolo_pose_new_26_v2-3/weights/best.pt`
   - V5 `…/run_20260829_032756/weights/best_it.pt`
4. Original `datasets/yolo_pose_new_26/` unchanged → full recoverability  
5. Revert any uncommitted script pointing at remediation weights  

---

## 15. Definition of success

### Engineering success (Phase 10C training outcome)

- New checkpoint under `yolo_pose_remediation_v1` with complete `MANIFEST.json`  
- Problem KP gates §8.2 PASS on **held-out test**  
- ASL_L ASM-collapse rate sharply reduced  
- Regression gates §8.3 PASS for good KP + IT  
- VCE/Tönnis/CCD engineering errors improve or non-worsen (§9)  
- V2 and V5 production files bit-identical to pre-experiment SHA256  

### Program success (Option F)

- Versioned dataset ≥40 (preferably ≥60) with test split  
- Annotation protocol followed  
- Manual-correction architecture understood; Flutter editor tracked as follow-on  
- No modifications to `mvp_geometry`, Flutter production code, PDF formulas, IT QC, or IT architecture in this program’s training track  

### Explicit non-success

- Higher Ultralytics mAP alone without landmark/angle gates  
- Offset hacks or formula changes  
- “Looks better on 2 images” without test metrics  

---

## 16. What this phase did / did not do

| Done | Not done |
|------|----------|
| Inspected real scripts, configs, checkpoints, pools | No training |
| Wrote this execution plan | No dataset creation/modification |
| Defined gates, naming, rollback | No source code changes |
| STOP for approval | No checkpoint writes |

---

## FINAL STOP

**Awaiting approval to proceed to Step A (definition/FOV lock) and Step B (QA).**  
Do **not** create `yolo_pose_remediation_v1/`, do **not** add training scripts, and do **not** launch `--train` until explicitly approved.

---

*End of Phase 10C controlled execution plan.*
