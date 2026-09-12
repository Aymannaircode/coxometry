# Annotation pilot (MVP — 14 landmarks)

**Purpose:** protocol test of the annotation guidelines on a small pilot set.  
**Not** a training set. **Not** adult coxometry validation.

## Rules

- Do **not** annotate inside `Dataset1/`.
- Do **not** copy Dataset 1 DDH keypoints (`re`/`ry`/`rc`/`rh`/…) into MVP landmarks.
- Do **not** invent or auto-generate coordinates.
- Leave `x`/`y` as `null` until a human annotator clicks.
- Prefer `v=0` or `v=2`; avoid `v=1` unless clinically validated.

## Population note

Source images come from Dataset 1 (MTDDH, pediatric DDH). They are used **only** to test the annotation protocol and tooling.

## Layout

- `images/` — JPEG copies P01–P16
- `templates/` — empty JSON templates (14 landmarks, null coordinates)
- `annotations/annotator_A|B/` — future manual annotations
- `logs/` — visibility, difficulty, ambiguity, guideline feedback CSVs
- `reviews/` — clinical synthesis (Phase 4)

See `docs/annotation_pilot_protocol.md`.
