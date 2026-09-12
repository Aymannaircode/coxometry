# Phase 10E-COURSE — Coxometry Domain Knowledge Audit

**Date:** 2026-09-04  
**Mode:** DOMAIN KNOWLEDGE AUDIT ONLY — no training, no production / V5 / labels / `mvp_geometry` / Flutter / PDF changes  
**Project sources (definitions):** `docs/landmark_specification.md`, `docs/annotation_guidelines.md`, `datasets/yolo_pose_new_26/phase10c_stepA_definition_fov_lock.md`  
**Literature sources studied:**

1. Clohisy et al. — *A Systematic Approach to the Plain Radiographic Evaluation of the Young Adult Hip* (JBJS 2008; PDF / ANCHOR)
2. *Assessment of the young adult hip joint using plain radiographs* (Musculoskelet Surg / Springer summary of young-adult hip plain-film assessment)
3. Mittal et al. — *Defining the lateral edge of the femoroacetabular articulation: correlation analysis between radiographs and computed tomography* (J Child Orthop 2016)
4. Rivas et al. — *Radiographically Apparent Acetabular Sourcil Landmarks Are Created by Comparable Regions of the Pelvis With Extraarticular Bone Variably Confounding Estimates of Joint Coverage* (CORR 2024)
5. Radiology / hip-preservation secondary references: Radiopaedia LCEA & acetabular index; Hanson et al. JHPS 2015 (bone-edge vs sourcil-edge); Ogata et al. (refined LCEA); Radsource DDH review; NSA/CCD radiographic construction papers

**Evidence tags used throughout:**

| Tag | Meaning |
|-----|---------|
| **LITERATURE FACT** | Stated in cited radiographic literature |
| **PROJECT DEFINITION** | Explicit project/doc definition |
| **INFERENCE** | Reasoned link between literature and project (not a source quote) |
| **UNRESOLVED** | Not settled by sources or requires physician confirmation |

**Index note:** The user query listed KP indices starting at `0 FHC_R`. The **YOLO / Phase 9B order** used in this repo is:

`0 TD_R, 1 TD_L, 2 FHC_R, 3 FHC_L, 4 ASL_R, 5 ASL_L, 6 ASM_R, 7 ASM_L, 8 FNM_R, 9 FNM_L, 10 FSP_R, 11 FSP_L, 12 FSD_R, 13 FSD_L, 14 IT_R, 15 IT_L`

This audit refers to landmarks **by name**, not by the query’s alternate index list.

---

## 1. Executive summary

| Question | Short answer |
|----------|--------------|
| Do project KPs correspond to standard coxometry? | **Mostly yes** for FHC, TD, ASM/ASL (sourcil), VCE/Tönnis geometry; **partially** for FSP/FSD (project convention approximating NSA shaft axis); IT is an extension |
| What is “correct” ASL? | Project ASL = **lateral edge of the sclerotic sourcil** (weight-bearing densification), **not** the most lateral bony rim |
| Is that identical to “lateral acetabular rim”? | **No** — LITERATURE FACT: sourcil-edge vs bone-edge LCEA differ by ~4–10° on average |
| Is ASL a unique anatomical point? | **No** — LITERATURE FACT (CORR 2024): radiographically apparent lateral sourcil arises from a **span** of laterosuperior bone; AIIS can contribute |
| Why ASL_L AI failure may be definitional | Sourcil lateral endpoint is **projection-dependent**, often subtle, and easily confused with medial sourcil / rim / AIIS — model collapse toward ASM is anatomically plausible |
| Implement / train now? | **No** — audit only |

---

## 2. Distinctions that must not be conflated

These are **not** identical concepts.

| Label | What it means | Typical radiographic cue |
|-------|---------------|--------------------------|
| **A. Lateral acetabular rim** | Lateral margin of the acetabular wall / labral bony base | Most lateral ossified rim contour |
| **B. Lateral bony acetabular edge** | Often used synonymously with A in LCEA-E literature | “Lateral-most ossification” (Mittal) |
| **C. Lateral edge of the sourcil** | Lateral end of the sclerotic subchondral roof densification | End of dense “eyebrow” of the roof |
| **D. Most lateral point of sclerotic weight-bearing zone** | Operational synonym of C in Clohisy / Ogata-style measurement | Same dense roof band |
| **E. Superolateral point of weight-bearing acetabular roof** | Clohisy LCEA wording: “most superolateral point of the sclerotic weight-bearing zone” | Same family as C/D; **not** necessarily the absolute lateral rim |

**LITERATURE FACT (Mittal 2016):**  
- LCEA-S (sourcil): “most lateral end of the sclerotic subchondral bone”  
- LCEA-E (acetabulum): “lateral most ossification”  
- Mean difference large (~16.5° vs ~26.0° in their dysplasia cohort); LCEA-S correlates best with **central** 3D weight-bearing coverage; LCEA-E with **anterior** acetabular edge.

**LITERATURE FACT (Hanson 2015):** bone-edge LCEA ≈ **+4°** (limits −2 to +10°) vs sourcil-edge in adults; classification of coverage often changes.

**LITERATURE FACT (Clohisy 2008):** LCEA line goes to “the most superolateral point of the **sclerotic weight-bearing zone** of the acetabulum” — i.e. sourcil family, not unspecified “any rim bone.”

**PROJECT DEFINITION (`ASL`):** most lateral point of the **sclerotic sourcil**, **excluding** rim osteophyte / spur when distinguishable → optional `ALB` for bone-edge variant.

**INFERENCE:** Project ASL ≈ **C / D / E (sourcil / Ogata–Clohisy family)**, deliberately **not** A/B. That is the correct choice for Tönnis + sourcil-LCEA consistency.

**UNRESOLVED:** Exact pixel choice when sclerosis fades gradually, or when AIIS / rim overlays the sourcil (CORR 2024).

---

## 3. What the sourcil actually is (critical for AI)

### 3.1 Appearance on AP pelvis

**LITERATURE FACT:**  
- French *sourcil* = “eyebrow.”  
- Dense/sclerotic band along the acetabular roof representing the **weight-bearing subchondral condensation**.  
- Normal sourcil is typically concave and congruent with the femoral head; in dysplasia it may be short, flattened, or upsloping (Radsource / young-adult hip reviews).

### 3.2 Why it appears sclerotic

**LITERATURE FACT / standard radiographic interpretation:** chronic compressive load produces subchondral osseous condensation along the weight-bearing roof — a **projection of a loaded zone**, not a single discrete bone tip.

### 3.3 What determines the lateral endpoint

**LITERATURE FACT (Clohisy; Mittal; Ogata tradition):** lateral margin of that sclerotic band.

**LITERATURE FACT (CORR Rivas 2024):**  
- 3D anatomy contributing to the **lateral sourcil** is a **variable-length span** (~27 mm IQR 15–34 mm) of laterosuperior acetabular edges.  
- **Anterior inferior iliac spine (AIIS)** contributed in **35% (7/20)** of hips.  
- Extra-articular bone can **variably confound** coverage estimates.  
- Interobserver LCEA ICC good (~0.82), but agreement on the underlying **3D sourcil location** varies widely (ICC 0.32–0.95).

### 3.4 Projection / positioning dependence

**LITERATURE FACT:** pelvic tilt/rotation alters acetabular index / coverage angles (classic Siebenrock / Tannast literature; Clohisy stresses standardized AP technique).  
**INFERENCE:** The apparent ASL can move when tilt/rotation changes even if 3D anatomy is fixed.

### 3.5 Annotation ambiguity

**INFERENCE:** Asking annotators (or a 2D network) for “the” ASL assumes a unique 2D point exists. Literature shows the radiographic sourcil edge is a **projection of a region**, sometimes contaminated by extra-articular bone → **intrinsic ambiguity**.

---

## 4. ASL vs ASM

| Item | Content | Tag |
|------|---------|-----|
| **ASM** | Medial / inferior end of the sclerotic sourcil (start of weight-bearing densification) | PROJECT DEFINITION; LITERATURE FACT (Clohisy “point I” = most inferior point of sclerotic sourcil) |
| **ASL** | Lateral end of the same sclerotic sourcil | PROJECT DEFINITION; LITERATURE FACT (Clohisy “point L”) |
| Visual structure between them | Continuous (or interrupted) dense roof band — the sourcil “eyebrow” | LITERATURE FACT |
| Can they be close? | Yes — short / upsloping / dysplastic sourcil; poor sclerosis; severe dysplasia | LITERATURE FACT + PROJECT DEFINITION (Tönnis undefined if ASM≈ASL) |
| Annotator look-for | Trace the **dense roof band** from medial condensation to its **last lateral dense point**; do **not** jump to a more lateral non-sclerotic rim spur | PROJECT DEFINITION |

**LITERATURE FACT:** Medial sourcil edge is often **ill-defined** → modified Tönnis angle was proposed when ASM is unclear (Zhang / modified Tönnis literature). Project already documents this as ambiguity A3 (`v=0` if not visible).

**INFERENCE for ASL_L model failure:** If the network learns “dense acetabular roof near the head,” ASM and medial sourcil are stronger / more consistent cues than the distant lateral fade-out → collapse of ASL toward ASM is consistent with **definitional difficulty**, not only random error.

---

## 5. VCE / LCEA construction

### 5.1 Standard construction (literature)

**LITERATURE FACT (Clohisy / Radiopaedia summary):**

1. Best-fit circle → **femoral head center**  
2. Transverse pelvic reference (commonly **teardrop–teardrop**; alternatives: bicenters of heads, ischial line)  
3. Vertical through FHC ⟂ transverse axis  
4. Line FHC → **lateral landmark**  
5. LCEA = angle between vertical and FHC→lateral landmark

### 5.2 Wiberg bone-edge vs Ogata sourcil-edge

| Method | Lateral landmark | Notes |
|--------|------------------|-------|
| **Wiberg / bone-edge (LCEA-E)** | Lateral acetabular bony rim / “lateral-most ossification” | Often **larger** angle; includes non–weight-bearing rim / labral base bone |
| **Ogata / sourcil-edge (LCEA-S)** | Lateral end of sclerotic sourcil | Closer to **central weight-bearing** coverage (Mittal) |

Historical note (**LITERATURE FACT / Hanson commentary**): Wiberg’s original wording is debated (some read it as sourcil “dense shadow”; many modern papers measure bone-edge). Ogata explicitly refined to sourcil condensation.

### 5.3 Project mapping

| Element | Project | Match |
|---------|---------|-------|
| FHC | Best-fit head center | Match |
| Transverse | `TD_R`–`TD_L` | Match to Clohisy teardrop preference |
| Vertical | ⟂ ITH through FHC | Match |
| Lateral | `ASL` = sourcil lateral | **Ogata / Clohisy sourcil method** |
| Optional bone-edge | `ALB` (optional, not in 16KP production set) | Explicitly separated |

**PROJECT DEFINITION:** VCE uses **sourcil** ASL.  
**ASL_PROJECT_LITERATURE_MATCH:** **PARTIAL** — matches the **sourcil-edge / Clohisy–Ogata** school; does **not** match protocols that still use bone-edge LCEA without saying so.

**Do not modify geometry code** (per phase rules) — this section is audit only.

---

## 6. Tönnis angle

### 6.1 Literature landmarks

**LITERATURE FACT (Clohisy 2008; Assessment of young adult hip; Radiopaedia acetabular index):**

1. Horizontal: teardrop base line (transverse pelvic axis)  
2. Horizontal parallel through **most inferior point of sclerotic sourcil** (medial/inferior sourcil = Clohisy “point I”)  
3. Line from that point to **lateral margin of sourcil** (“point L”)  
4. Tönnis = angle between (2) and (3)

Normal often cited ~0–10° (Clohisy); thresholds vary (**UNRESOLVED** clinical cutoffs — out of scope).

### 6.2 Project mapping

| Literature | Project KP |
|------------|------------|
| Medial/inferior sourcil (I) | `ASM` |
| Lateral sourcil (L) | `ASL` |
| Teardrop line | `TD_R`, `TD_L` |
| Horizontal ∥ teardrops through ASM | `mvp_geometry` Tönnis construction |

**Match:** Strong for ASM/ASL/TD roles.  
**Caveat:** Some papers say “lateral edge of the acetabulum” when describing Tönnis in passing — that language can blur sourcil vs rim (**UNRESOLVED** terminology drift in secondary sources). Project docs correctly lock **sourcil** for both ends.

---

## 7. FSP / FSD and CCD / NSA

### 7.1 Project definitions

| KP | PROJECT DEFINITION (locked) |
|----|-----------------------------|
| **FSP** | Median proximal shaft axis, **just below lesser trochanter**, or first clear parallel diaphyseal cortex level |
| **FSD** | Median shaft axis at **most distal still-visible stable** cortical level **inside FOV**; **no extrapolation** outside image; short FOV → prefer `v=0` |

### 7.2 Literature shaft-axis practice

**LITERATURE FACT:** Neck-shaft / CCD angle = angle between neck axis and shaft axis. Exact FSA construction varies:

- Midpoints of shaft width at two levels (e.g. below intertrochanteric / LT region + more distal)  
- Midpoint ~1 cm under LT + mid-shaft / 1/3 femur / distal end  
- Some automated methods avoid near-LT curvature

**NOT SPECIFIED BY SOURCE:** Named landmarks “FSP” / “FSD” as project codes.  
**NOT SPECIFIED BY SOURCE:** “Most distal pixel in FOV of an AP pelvis” as a universal NSA rule.  
**NOT SPECIFIED BY SOURCE:** Numeric 0.5× head-diameter short-FOV cutoff (project provisional).

**INFERENCE:** Project FSP≈ common “proximal shaft below LT midpoint” practice. Project FSD≈ pragmatic FOV-limited distal midpoint — **reasonable engineering convention**, not a single authoritative coxometry named point.

**Extrapolation:** Project **forbids** inventing FSD outside FOV — aligns with “don’t invent anatomy”; literature rarely endorses extrapolating a shaft point off-film for clinical NSA on pelvis-only films.

### 7.3 CCD appropriateness

| Axis | Project | Literature fit |
|------|---------|----------------|
| Neck | `FHC`–`FNM` | Common (head center + neck midline) |
| Shaft | `FSP`–`FSD` | Common 2-point mid-cortical idea |
| Overall | Suitable **2D estimate** of CCD/NSA | Sensitive to femoral rotation (PROJECT + LITERATURE) |

**FSP_DEFINITION_CONFIDENCE:** **MEDIUM**  
**FSD_DEFINITION_CONFIDENCE:** **LOW–MEDIUM** (FOV convention dominates; literature prefers longer shaft when available)

---

## 8. IT_R / IT_L

**PROJECT DEFINITION:** Ischial tuberosity landmarks for bi-ischial / alternate pelvic horizontal (added in 16KP V5-IT path).  
**LITERATURE FACT:** Transverse pelvic references include teardrops, ischial tuberosities, or femoral head centers (Radiopaedia / LCEA horizon variants).  
**Match:** Conceptually valid alternate horizon; not required for Clohisy teardrop-preferred Tönnis/LCEA.  
**Project VCE/Tönnis geometry** currently prioritizes **teardrops** per `landmark_specification.md`.

---

## 9. Definitions table

| KP | Project definition | Literature definition | Match | Ambiguity | Recommendation (audit only) |
|----|--------------------|----------------------|-------|-----------|------------------------------|
| **FHC_R/L** | Best-fit circle center of femoral head | Same (Mose / best-fit) for LCEA/NSA | **Yes** | Aspherical heads, osteophytes | Keep; document aspheric protocol |
| **FNM_R/L** | Mid-neck axis point (between cortices) | Neck axis via head+neck midpoints (variants exist) | **Partial** | Cam, short neck, method variants | Keep; illustrate mid-neck level |
| **TD_R/L** | Inferior tip of radiographic teardrop | Teardrop base / inferior teardrop for transverse axis (Clohisy) | **Yes** | Teardrop vs ischia vs bicenters | Keep as primary horizon |
| **ASM_R/L** | Medial end of sclerotic sourcil | Clohisy “point I” / medial sourcil for Tönnis | **Yes** | Often poorly defined | Keep; allow `v=0`; modified Tönnis is literature escape hatch (not implemented) |
| **ASL_R/L** | Lateral end of sclerotic sourcil (not rim spur) | Clohisy/Ogata sourcil lateral; **≠** bone-edge LCEA | **Partial** (sourcil school yes; bone-edge school no) | **High** (projection, AIIS, fade-out, rim confusion) | Keep sourcil definition; strengthen annotator exemplars; optional `ALB` if bone-edge needed |
| **FSP_R/L** | Shaft mid-axis just below LT | Common NSA proximal shaft midpoint practice | **Partial** | Exact height not universal | Keep verbal lock; need illustrated exemplars |
| **FSD_R/L** | Most distal visible mid-shaft in FOV; no extrapolate | NSA distal point often mid-shaft / % length — **not** FOV endpoint by name | **Partial / project convention** | Short FOV instability | Keep FOV policy; mark short shafts `v=0` |
| **IT_R/L** | Ischial tuberosity | Valid alternate pelvic horizontal landmark | **Partial** (role differs by protocol) | Which horizon is canonical | Keep as optional / IT head; don’t silently replace TD |

---

## 10. WHY ASL_L MAY BE HARD FOR A 2D AI MODEL

### Factors

1. **Projection ambiguity** — lateral sourcil is a 2D projection of a 3D span (CORR 2024).  
2. **Sourcil morphology** — short/upsloping/faint sclerosis in dysplasia.  
3. **Sclerosis gradient** — lateral “end” is often a fade, not a corner.  
4. **Lateral-edge ambiguity** — sourcil vs rim vs osteophyte vs AIIS overlay.  
5. **Overlap** — iliac wing, AIIS, rim lines can mimic or extend the dense band.  
6. **Anatomical vs radiographic edge** — true articular coverage ≠ most lateral bone.  
7. **Pelvic positioning** — tilt/rotation changes apparent endpoint.  
8. **Annotation variability** — humans agree better on angle than on exact 3D bone contributing to the point (CORR).  
9. **ASM proximity cue** — medial sourcil / ASM is a stronger local feature; network may regress ASL→ASM (observed 25/26).  

### Classification of current ASL definition

| Layer | Rating |
|-------|--------|
| Written project definition (sourcil lateral ≠ rim) | **CLEAR** as intent |
| Radiographic localization as a unique 2D point | **HIGHLY AMBIGUOUS** |
| Overall for AI purposes (this audit’s `ASL_DEFINITION`) | **HIGHLY_AMBIGUOUS** |

**INFERENCE:** Ambiguous definition **contributes** to ASL_L failure risk, but does **not** alone prove GT is wrong or that V5 is “correct.” It means single-point ASL is an intrinsically hard target.

---

## 11. Implications for AI representation (conceptual only)

| Option | Idea | Advantages | Risks |
|--------|------|------------|-------|
| **A. Single point** | Current KP | Simple; matches present geometry | High variance; ASM collapse; understates region nature |
| **B. Endpoint of detected line/curve** | Fit sourcil curve ASM→lateral | Encodes continuity of eyebrow | Curve fit can latch wrong edge (rim/AIIS) |
| **C. Endpoint of segmented sourcil region** | Segment dense roof; take lateral extreme of mask | Matches “zone” biology better | Needs labels/masks; FOV/exposure sensitive |
| **D. Point from radiographic edge candidates** | Multi-candidate + anatomical ranking | Fail-open possible | Ranking still ambiguous; Phase 10E-0 showed coarse residuals |
| **E. Dual points ASL + ALB** | Explicit sourcil vs bone-edge | Matches literature split; reduces silent confusion | Extra annotation cost; geometry must choose which for VCE |

**INFERENCE (no implementation):** Conceptually, **C or B** better match literature’s zone/span nature; **E** matches the documented A1 split. **A** remains acceptable for MVP geometry **only if** annotation exemplars strictly enforce sourcil≠rim and accept high irreducible noise.

**Do not train. Do not implement.**

---

## 12. Explicit separation checklist

| Statement | Tag |
|-----------|-----|
| Sourcil-edge and bone-edge LCEA are different | LITERATURE FACT |
| Project ASL is sourcil lateral | PROJECT DEFINITION |
| Project ASL matches Clohisy/Ogata lateral landmark family | INFERENCE |
| Project ASL matches all published “Wiberg” usages | **False** — PARTIAL only |
| Sourcil lateral is a unique 3D point | Contradicted by LITERATURE FACT (CORR) |
| FSP/FSD names are standard coxometry codes | **NOT SPECIFIED BY SOURCE** |
| Never extrapolate FSD off FOV | PROJECT DEFINITION |
| ASL_L V5→ASM collapse is partly definitional difficulty | INFERENCE |
| Clinical dysplasia thresholds | Not used here (audit forbids inventing clinical cutoffs) |

---

## 13. Recommendation (no implementation)

1. **Keep** ASL = lateral **sourcil** (not rim) — consistent with Tönnis + preferred LCEA-S.  
2. Treat ASL as **HIGHLY AMBIGUOUS** for AI; expect irreducible localization noise and ASM confusion risk.  
3. Do **not** silently redefine ASL as bone-edge; if bone-edge is needed, that is **`ALB`**, not ASL.  
4. Strengthen human exemplars (sourcil vs rim vs AIIS) before any future labeling expansion.  
5. FSP remains a **reasonable** NSA proximal convention (**MEDIUM** confidence); FSD FOV rule is **project policy** (**LOW–MEDIUM**).  
6. **No training, no production change** from this course audit.

---

## Final status block

PHASE_10E_COURSE_AUDIT:
COMPLETE

ASL_DEFINITION:
HIGHLY_AMBIGUOUS

ASL_PROJECT_LITERATURE_MATCH:
PARTIAL

FSP_DEFINITION_CONFIDENCE:
MEDIUM

FSD_DEFINITION_CONFIDENCE:
LOW

TRAINING_STARTED:
NO

PRODUCTION_MODIFIED:
NO

V5_MODIFIED:
NO

MVP_GEOMETRY_MODIFIED:
NO

RECOMMENDATION:
ASL correctly targets sourcil-edge (Ogata/Clohisy), not bone rim, but as a unique 2D point it remains highly ambiguous because the radiographic sourcil is a projection of a bone span often confounded by extra-articular structures; keep definitions, do not train or implement from this audit alone.
