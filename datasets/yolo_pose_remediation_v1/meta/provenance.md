# Provenance — yolo_pose_remediation_v1 seed

| Field | Value |
|-------|-------|
| **Source dataset path** | `datasets/yolo_pose_new_26/` |
| **Target dataset path** | `datasets/yolo_pose_remediation_v1/` |
| **Copy UTC** | 2026-09-04T18:19:12Z |
| **Operation** | Byte-identical file copy (`shutil.copyfile`) — no DICOM re-render, no recompress, no resize, no label edit |
| **Source images** | 26 |
| **Copied images** | 26 |
| **Source labels** | 26 |
| **Copied labels** | 26 |
| **Identical image SHA256** | 26/26 |
| **Identical label SHA256** | 26/26 |
| **Source files modified during copy?** | NO |
| **Source split** | train=21, val=5, test=0 (seed 42) |
| **Target split** | train=21, val=5 (continuity probe), test=0 (empty dirs present) |
| **Continuity probe IDs** | B26_10, B26_13, B26_17, B26_20, B26_26 |
| **FOV_SHORT labels changed?** | NO (Step B documentation only) |
| **Machine-readable manifest** | `meta/copy_manifest.json` |

## Confirmation

- Original `datasets/yolo_pose_new_26/` remains the recoverable production dataset.
- This namespace is derived **only** by copying existing PNG/TXT assets.
- No synthetic cases, no duplicates-as-new-IDs, no phone-negatoscope images.
- No training performed as part of this copy.


## Step D addendum (2026-09-04T18:28:17Z)

- Inventoried `bassin/` pools + empty PATIENT_* dirs
- Rendered 10 triage PNGs (8 a_verifier + 2 rejetees) via project `dicom_render.py` (DICOM originals untouched)
- No new cases promoted into `images/{train,val,test}` or `labels/{train,val,test}`
- No synthetic / flip / phone-photo cases added
- Annotation stubs created only under `annotation_pilot/annotations/remediation_v1/`
