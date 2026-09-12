# QA checklist — remediation_v1 seed (Step C)

Use after copy / before any Step D expansion.

| # | Check | Expected |
|---|-------|----------|
| 1 | 26 images present under `images/{train,val,test}` | 21 + 5 + 0 |
| 2 | 26 corresponding labels present | 21 + 5 + 0 |
| 3 | train/val/test file names correspond | Same `B26_*` stem in paired image/label |
| 4 | Image bytes identical to source | SHA256 match per `meta/copy_manifest.json` |
| 5 | Label bytes identical to source | SHA256 match |
| 6 | 16 keypoints preserved | Each label line: 5 + 16×3 = 53 floats; `kpt_shape [16,3]` |
| 7 | Keypoint order preserved | Per `meta/keypoint_order.md` (KP0–13 legacy, KP14 IT_R, KP15 IT_L) |
| 8 | Visibility values preserved | Unchanged vs source labels (no FOV policy applied) |
| 9 | No duplicate IDs | Exactly one file per B26_01…B26_26 |
| 10 | Source files not modified | Source SHA256 still equals precopy snapshot |
| 11 | No synthetic images | Only copied PNGs from `yolo_pose_new_26` |
| 12 | No DICOM re-rendering | Copy of existing PNG only |
| 13 | FOV_SHORT cases unchanged | 20 Step B flags; labels still byte-identical |
| 14 | Original dataset recoverable | `datasets/yolo_pose_new_26/` intact |
| 15 | `data.yaml` points only to remediation_v1 | No path to `yolo_pose_new_26` |
| 16 | Test set not claimed final | `test=[]`; seed incomplete for T1 gates |

Automated verification: see `datasets/yolo_pose_new_26/phase10c_stepC_dataset_copy_audit.md`.
