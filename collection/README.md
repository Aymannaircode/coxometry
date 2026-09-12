# Future collection staging — EMPTY INFRASTRUCTURE

**This directory is not a training dataset.**

It exists only so that **future** authorized adult AP-pelvis cases can be received
**outside** `datasets/yolo_pose_new_26/` and `datasets/yolo_pose_remediation_v1/`.

**Phase 11C-1 status**

- No real patient files are present.
- No Case IDs (`R27_*`, `R28_*`, …) are allocated.
- No B26 / R26 files were copied here.
- A file in any stage below is **not** train-ready.
- `08_VALIDATED` is **not** a frozen train/val/test split.

**Authoritative protocol**

`datasets/yolo_pose_new_26/phase11c1_collection_infrastructure.md`

Predecessor locks: Phase 11A / 11B / 11C-0. Do not reinterpret medical rules.

**Pipeline (empty)**

```
01_INBOX_RAW                 HIGHLY SENSITIVE — identifying source
        ↓
02_DEIDENTIFICATION_PENDING
        ↓
03_DEIDENTIFIED              not automatically eligible
        ↓
04_ELIGIBILITY_PENDING
        ↓
05_PHYSICIAN_REVIEW
        ↓
06_ANNOTATION_PENDING
        ↓
07_QC_PENDING
        ↓
08_VALIDATED                 not automatically train-ready
```

Terminal stages: `09_EXCLUDED`, `10_ARCHIVE`.

**Forbidden here**

- Dumping files into `datasets/yolo_pose_new_26/`
- Creating `datasets/yolo_pose_remediation_v2/`
- Using `bassin/` named folders as Case IDs
- Promoting R26
- Creating train/val/test
- Treating V5 / Flutter corrections / Phase 10F–10G candidates as ground truth
