# remediation_v1 annotations (NEW cases only)

**Created UTC:** 2026-09-04T18:28:17Z  
**Purpose:** Annotation workspace for Phase 10C Step D expansion candidates.

## Rules

- Do **not** modify `annotation_pilot/annotations/new_26/`.
- Do **not** modify `datasets/yolo_pose_new_26/`.
- Do **not** invent landmark coordinates.
- Use locked Step A definitions for ASL/FSP/FSD + existing TD/FHC/ASM/FNM/IT policies.
- `v=2` only when clearly identifiable; `v=0` otherwise.
- Never extrapolate FSD beyond visible FOV.
- Do **not** apply provisional 0.5× head-diameter cutoff until physician confirms.
- If FSD ambiguous → mark `FOV_POLICY_REVIEW_REQUIRED`.

## Status

All listed cases are **PENDING_PHYSICIAN** (adult/eligibility) before annotation is training-ready.  
JSON stubs have **empty landmarks** on purpose — not training-ready, not YOLO-promoted.

## Cases

See `worklist.csv` (R26_01…R26_06).
