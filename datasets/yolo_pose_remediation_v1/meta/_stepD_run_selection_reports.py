"""Phase 10C Step D — selection, annotation prep, reports (STOP before Step E)."""
from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\g\OneDrive\Desktop\Projet-Ayman")
REM = ROOT / "datasets" / "yolo_pose_remediation_v1"
META = REM / "meta"
SRC26 = ROOT / "datasets" / "yolo_pose_new_26"
ANN = ROOT / "annotation_pilot" / "annotations" / "remediation_v1"

CONTINUITY = ["B26_10", "B26_13", "B26_17", "B26_20", "B26_26"]

# Hard tags from visual triage of a_verifier / rejetees thumbnails
TAGS = {
    "1.2.840.113564.192168100150.202312191448193835.1203801020003": {
        "hard_tags": "OVERLAP;ROT_mild;SHAFT_hard;ASL_hard;QUALITY_var",
        "difficulty": "moderate_hard",
        "fov_policy_review": "YES",
        "n_hard": 5,
        "note": "DARI FATIMA view A; bowel gas; short shaft FOV; mild rotation",
    },
    "1.2.840.113564.192168100150.202312191451251017.1203801020003": {
        "hard_tags": "OVERLAP;SHAFT_hard;ASL_hard;QUALITY_var",
        "difficulty": "moderate_hard",
        "fov_policy_review": "YES",
        "n_hard": 4,
        "note": "DARI FATIMA view B (same PatientID 54321); prefer A or B after physician pick-one",
    },
    "1.3.12.2.1107.5.3.63.40605.12.202607200851078206": {
        "hard_tags": "OVERLAP;SHAFT_hard;ASL_hard",
        "difficulty": "moderate_hard",
        "fov_policy_review": "YES",
        "n_hard": 3,
        "note": "MOUNTASER AICHA 016Y; very short shaft FOV; good centering",
    },
    "1.3.12.2.1107.5.3.63.40605.12.202607231823530408": {
        "hard_tags": "OVERLAP;ROT_mild;SHAFT_hard;ASL_hard",
        "difficulty": "moderate_hard",
        "fov_policy_review": "YES",
        "n_hard": 4,
        "note": "ACHLAFY ABIR 016Y; left sourcil gas overlap; short R shaft",
    },
    "1.3.12.2.1107.5.3.63.40605.12.202608051210254689": {
        "hard_tags": "OVERLAP;ROT_mild;SHAFT_hard;ASL_hard",
        "difficulty": "hard",
        "fov_policy_review": "YES",
        "n_hard": 4,
        "note": "HADDOURI MANAL 017Y view A; IUD metal; short shafts; duplicate patient",
    },
    "1.3.12.2.1107.5.3.63.40605.12.202608051215434223": {
        "hard_tags": "OVERLAP;ROT_mild;ASL_hard",
        "difficulty": "moderate",
        "fov_policy_review": "YES",
        "n_hard": 3,
        "note": "HADDOURI MANAL 017Y view B (better of pair per CSV); still age-uncertain",
    },
    "1.3.12.2.1107.5.3.63.40605.12.202608111126260582": {
        "hard_tags": "ASL_hard;ROT_mild;OVERLAP",
        "difficulty": "moderate",
        "fov_policy_review": "MAYBE",
        "n_hard": 3,
        "note": "GOURID ABDELAADIM 016Y; left degenerative ASL ambiguity; shafts more usable",
    },
    "1.3.12.2.1107.5.3.63.40605.12.202608162110024587": {
        "hard_tags": "ASL_hard;SHAFT_hard;OVERLAP;ROT_mild;QUALITY_var",
        "difficulty": "hard",
        "fov_policy_review": "YES",
        "n_hard": 5,
        "note": "KABBAJ GHITA 094Y; left hip pathology/deformation; adult but annotation-hard",
    },
    "1.3.12.2.1107.5.3.63.40605.12.202608031038074414": {
        "hard_tags": "ASL_hard;SHAFT_hard;OVERLAP;ROT_mild;QUALITY_var",
        "difficulty": "reject_quality",
        "fov_policy_review": "N/A",
        "n_hard": 5,
        "note": "REJECTED: horizontal seam + truncated proximal femurs; not re-qualified",
    },
    "1.3.12.2.1107.5.3.63.40605.12.202608161539116335": {
        "hard_tags": "N/A_NOT_AP_PELVIS",
        "difficulty": "reject_view",
        "fov_policy_review": "N/A",
        "n_hard": 0,
        "note": "REJECTED: unilateral hip AP; same patient as B26_25 ZAFFOU; not bilateral pelvis",
    },
}

# One image per new patient for annotation queue (pending physician adult/eligibility)
SELECTED_NEW = [
    # (provisional_id, dicom_name, patient_id, patient_name, reason)
    (
        "R26_01",
        "1.2.840.113564.192168100150.202312191448193835.1203801020003",
        "54321",
        "DARI FATIMA",
        "Hard AP pelvis (>=2 tags); pick one of two same-patient views; age absent — PENDING physician adult confirm",
    ),
    (
        "R26_02",
        "1.3.12.2.1107.5.3.63.40605.12.202607200851078206",
        "202607200845491",
        "MOUNTASER AICHA",
        "SHAFT_hard short FOV + OVERLAP; age 016Y — PENDING physician adult confirm",
    ),
    (
        "R26_03",
        "1.3.12.2.1107.5.3.63.40605.12.202607231823530408",
        "202607231822531",
        "ACHLAFY ABIR",
        "ASL_hard left + SHAFT_hard; age 016Y — PENDING physician adult confirm",
    ),
    (
        "R26_04",
        "1.3.12.2.1107.5.3.63.40605.12.202608051215434223",
        "202608051209231",
        "HADDOURI MANAL",
        "Better of patient duplicate pair (CSV); age 017Y — PENDING physician adult confirm",
    ),
    (
        "R26_05",
        "1.3.12.2.1107.5.3.63.40605.12.202608111126260582",
        "202608111125311",
        "GOURID ABDELAADIM",
        "ASL_hard degenerative left; age 016Y — PENDING physician adult confirm",
    ),
    (
        "R26_06",
        "1.3.12.2.1107.5.3.63.40605.12.202608162110024587",
        "202608162107121",
        "KABBAJ GHITA",
        "Adult 094Y hard ASL_L pathology case; annotation difficulty high — PENDING physician annotation feasibility",
    ),
]


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state = json.loads((META / "_stepD_state.json").read_text(encoding="utf-8"))
    renders = {r["dicom_file"]: r for r in state["render_manifest"]}
    inv = load_csv(META / "candidate_inventory.csv")
    b26_map = load_csv(SRC26 / "meta" / "source_mapping.csv")
    rem_map = load_csv(META / "source_mapping.csv")

    # --- selected_cases.csv ---
    sel_fields = [
        "case_id",
        "role",
        "source_patient_id",
        "source_patient_name",
        "source_dicom",
        "source_folder",
        "render_path",
        "hard_tags",
        "n_hard_tags",
        "difficulty",
        "selection_reason",
        "duplicate_check",
        "eligible_for_annotation",
        "annotation_status",
        "fov_policy_review_required",
        "promoted_to_yolo_split",
        "patient_level_ok",
    ]
    selected = []

    # Seed B26
    for row in rem_map:
        case = row["pilot_id"]
        selected.append(
            {
                "case_id": case,
                "role": "seed_b26",
                "source_patient_id": "",  # filled below from inventory
                "source_patient_name": "",
                "source_dicom": row["source_dicom"],
                "source_folder": "bassin/a_annoter",
                "render_path": row["yolo_image"],
                "hard_tags": "SEED_EXISTING",
                "n_hard_tags": "",
                "difficulty": "seed",
                "selection_reason": "Byte-identical seed from yolo_pose_new_26 (Step C)",
                "duplicate_check": "PASS_unique_in_seed",
                "eligible_for_annotation": "ALREADY_ANNOTATED",
                "annotation_status": "COMPLETE_SEED_QA_STEP_B",
                "fov_policy_review_required": "YES" if row.get("fov_short_stepB_flag") == "YES" else "NO",
                "promoted_to_yolo_split": row["split"],
                "patient_level_ok": "YES",
            }
        )

    # Fill patient ids for B26 from inventory
    inv_by_dicom = {r["dicom_file"]: r for r in inv if r.get("dicom_file")}
    for s in selected:
        if s["role"] != "seed_b26":
            continue
        dname = Path(s["source_dicom"].replace("\\", "/")).name
        ir = inv_by_dicom.get(dname, {})
        s["source_patient_id"] = ir.get("patient_id", "")
        s["source_patient_name"] = ir.get("patient_name", "")

    # New provisional selections
    for case_id, dicom, pid, pname, reason in SELECTED_NEW:
        tag = TAGS[dicom]
        rend = renders[dicom]
        selected.append(
            {
                "case_id": case_id,
                "role": "expansion_candidate",
                "source_patient_id": pid,
                "source_patient_name": pname,
                "source_dicom": f"bassin/a_verifier/{dicom}",
                "source_folder": "bassin/a_verifier",
                "render_path": rend["render_path"],
                "hard_tags": tag["hard_tags"],
                "n_hard_tags": tag["n_hard"],
                "difficulty": tag["difficulty"],
                "selection_reason": reason,
                "duplicate_check": "PASS_not_B26;unique_patient_among_selected_new",
                "eligible_for_annotation": "PENDING_PHYSICIAN",
                "annotation_status": "NOT_STARTED",
                "fov_policy_review_required": tag["fov_policy_review"],
                "promoted_to_yolo_split": "NONE",
                "patient_level_ok": "YES",
            }
        )

    # Explicitly document not-selected siblings / rejects
    not_selected_notes = [
        {
            "case_id": "NOT_SELECTED",
            "role": "excluded_sibling",
            "source_patient_id": "54321",
            "source_patient_name": "DARI FATIMA",
            "source_dicom": "bassin/a_verifier/1.2.840.113564.192168100150.202312191451251017.1203801020003",
            "source_folder": "bassin/a_verifier",
            "render_path": renders["1.2.840.113564.192168100150.202312191451251017.1203801020003"]["render_path"],
            "hard_tags": TAGS["1.2.840.113564.192168100150.202312191451251017.1203801020003"]["hard_tags"],
            "n_hard_tags": 4,
            "difficulty": "moderate_hard",
            "selection_reason": "Same patient as R26_01 — hold as alternate view; do not put in different split",
            "duplicate_check": "SAME_PATIENT_AS_R26_01",
            "eligible_for_annotation": "NO_SIBLING_HELD",
            "annotation_status": "N/A",
            "fov_policy_review_required": "YES",
            "promoted_to_yolo_split": "NONE",
            "patient_level_ok": "YES",
        },
        {
            "case_id": "NOT_SELECTED",
            "role": "excluded_sibling",
            "source_patient_id": "202608051209231",
            "source_patient_name": "HADDOURI MANAL",
            "source_dicom": "bassin/a_verifier/1.3.12.2.1107.5.3.63.40605.12.202608051210254689",
            "source_folder": "bassin/a_verifier",
            "render_path": renders["1.3.12.2.1107.5.3.63.40605.12.202608051210254689"]["render_path"],
            "hard_tags": TAGS["1.3.12.2.1107.5.3.63.40605.12.202608051210254689"]["hard_tags"],
            "n_hard_tags": 4,
            "difficulty": "hard",
            "selection_reason": "Same patient as R26_04 — held out; CSV preferred other view",
            "duplicate_check": "SAME_PATIENT_AS_R26_04",
            "eligible_for_annotation": "NO_SIBLING_HELD",
            "annotation_status": "N/A",
            "fov_policy_review_required": "YES",
            "promoted_to_yolo_split": "NONE",
            "patient_level_ok": "YES",
        },
        {
            "case_id": "NOT_SELECTED",
            "role": "rejected",
            "source_patient_id": "202608031034111",
            "source_patient_name": "bennani asmae",
            "source_dicom": "bassin/rejetees/1.3.12.2.1107.5.3.63.40605.12.202608031038074414",
            "source_folder": "bassin/rejetees",
            "render_path": renders["1.3.12.2.1107.5.3.63.40605.12.202608031038074414"]["render_path"],
            "hard_tags": TAGS["1.3.12.2.1107.5.3.63.40605.12.202608031038074414"]["hard_tags"],
            "n_hard_tags": 5,
            "difficulty": "reject_quality",
            "selection_reason": "Rejected: seam artifact + truncated femurs; not re-qualified",
            "duplicate_check": "REJECTED_POOL",
            "eligible_for_annotation": "NO",
            "annotation_status": "N/A",
            "fov_policy_review_required": "N/A",
            "promoted_to_yolo_split": "NONE",
            "patient_level_ok": "YES",
        },
        {
            "case_id": "NOT_SELECTED",
            "role": "rejected",
            "source_patient_id": "202608161537561",
            "source_patient_name": "ZAFFOU ABOUCH",
            "source_dicom": "bassin/rejetees/1.3.12.2.1107.5.3.63.40605.12.202608161539116335",
            "source_folder": "bassin/rejetees",
            "render_path": renders["1.3.12.2.1107.5.3.63.40605.12.202608161539116335"]["render_path"],
            "hard_tags": "N/A_NOT_AP_PELVIS",
            "n_hard_tags": 0,
            "difficulty": "reject_view",
            "selection_reason": "Rejected unilateral hip; same PatientID as seed B26_25",
            "duplicate_check": "SAME_PATIENT_AS_B26_25",
            "eligible_for_annotation": "NO",
            "annotation_status": "N/A",
            "fov_policy_review_required": "N/A",
            "promoted_to_yolo_split": "NONE",
            "patient_level_ok": "YES",
        },
    ]
    selected.extend(not_selected_notes)

    with (META / "selected_cases.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sel_fields)
        w.writeheader()
        w.writerows(selected)

    # --- Update split.json: keep seed; document expansion BLOCKED ---
    split = {
        "dataset": "yolo_pose_remediation_v1",
        "seed_version": "v1.0_seed_26",
        "updated_utc": utc,
        "source_dataset": "datasets/yolo_pose_new_26",
        "source_split_seed": 42,
        "policy": {
            "preserve_original_val_as_continuity_probe": True,
            "no_silent_reshuffle": True,
            "no_fabricated_test_cases": True,
            "patient_level_split_required": True,
            "patient_identity_available": True,
            "patient_identity_source": "DICOM PatientID (+ PatientName cross-check)",
            "test_set_status": "EMPTY_AT_SEED",
            "final_evaluation_ready": False,
            "expansion_status": "BLOCKED_INSUFFICIENT_REAL_DICOM_POOL",
            "note": (
                "Step D inventory found 33 empty PATIENT_* dirs, 26 already-used a_annoter DICOMs, "
                "8 a_verifier DICOMs (all PENDING_PHYSICIAN), 2 rejetees (excluded). "
                "Max unique new patients after de-dup = 6 → total would be 32 << 40–80 target and "
                "cannot form >=15 held-out test cases. Final train/val/test redesign DEFERRED. "
                "Seed assignment unchanged. Continuity probe preserved."
            ),
        },
        "train": [
            "B26_01",
            "B26_02",
            "B26_03",
            "B26_04",
            "B26_05",
            "B26_06",
            "B26_07",
            "B26_08",
            "B26_09",
            "B26_11",
            "B26_12",
            "B26_14",
            "B26_15",
            "B26_16",
            "B26_18",
            "B26_19",
            "B26_21",
            "B26_22",
            "B26_23",
            "B26_24",
            "B26_25",
        ],
        "val": CONTINUITY,
        "test": [],
        "continuity_probe_ids": CONTINUITY,
        "counts": {"train": 21, "val": 5, "test": 0, "total": 26},
        "expansion_candidates_pending_physician": [x[0] for x in SELECTED_NEW],
        "expansion_candidates_not_promoted_to_yolo": True,
    }
    (META / "split.json").write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")

    # --- Annotation directory for NEW cases only ---
    ANN.mkdir(parents=True, exist_ok=True)
    worklist_fields = [
        "case_id",
        "source_dicom",
        "render_path",
        "patient_id",
        "patient_name",
        "guidelines",
        "status",
        "fov_policy_review_required",
        "hard_tags",
    ]
    work_rows = []
    for case_id, dicom, pid, pname, reason in SELECTED_NEW:
        tag = TAGS[dicom]
        rend = renders[dicom]
        work_rows.append(
            {
                "case_id": case_id,
                "source_dicom": f"bassin/a_verifier/{dicom}",
                "render_path": rend["render_path"],
                "patient_id": pid,
                "patient_name": pname,
                "guidelines": "docs/annotation_guidelines.md + phase10c_stepA_definition_fov_lock.md + bi_ischial_final_policy.md",
                "status": "PENDING_PHYSICIAN_THEN_ANNOTATE",
                "fov_policy_review_required": tag["fov_policy_review"],
                "hard_tags": tag["hard_tags"],
            }
        )
        # Minimal schema stub — landmarks empty / not invented
        stub = {
            "schema_version": "mvp-pilot-1.0",
            "image_id": case_id,
            "source_file": dicom,
            "source_dataset": "bassin_a_verifier",
            "view": "AP_pelvis",
            "population_note": "PENDING_PHYSICIAN_ADULT_CONFIRM",
            "annotator_id": None,
            "annotation_date": None,
            "guidelines_version": "annotation_guidelines.md + phase10c_stepA_definition_fov_lock.md",
            "image_width": rend["width"],
            "image_height": rend["height"],
            "landmarks": [],
            "status": "NOT_ANNOTATED",
            "notes": reason,
            "fov_policy_review_required": tag["fov_policy_review"],
            "hard_tags": tag["hard_tags"],
            "do_not_invent_coordinates": True,
            "do_not_apply_0_5_head_diameter_cutoff": True,
        }
        (ANN / f"{case_id}.json").write_text(json.dumps(stub, indent=2) + "\n", encoding="utf-8")

    with (ANN / "worklist.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=worklist_fields)
        w.writeheader()
        w.writerows(work_rows)

    (ANN / "README.md").write_text(
        f"""# remediation_v1 annotations (NEW cases only)

**Created UTC:** {utc}  
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
""",
        encoding="utf-8",
    )

    # --- Update remediation README + provenance lightly ---
    readme = (REM / "README.md").read_text(encoding="utf-8")
    if "Step D" not in readme:
        readme += f"""

## Step D expansion status ({utc})

- Candidate inventory: `meta/candidate_inventory.csv`
- Selected / deferred cases: `meta/selected_cases.csv`
- Triage renders (not YOLO-promoted): `triage_renders/`
- Expansion **BLOCKED** for target 40–80 / ≥15 test: insufficient unused real AP pelvis DICOMs in repo
- 6 provisional new candidates (R26_01…06) queued under `annotation_pilot/annotations/remediation_v1/` pending physician clearance
- Seed 26 cases unchanged; FOV_SHORT labels still unchanged
- Final patient-safe train/val/test redesign deferred
"""
        (REM / "README.md").write_text(readme, encoding="utf-8")

    prov = (META / "provenance.md").read_text(encoding="utf-8")
    if "Step D" not in prov:
        prov += f"""

## Step D addendum ({utc})

- Inventoried `bassin/` pools + empty PATIENT_* dirs
- Rendered 10 triage PNGs (8 a_verifier + 2 rejetees) via project `dicom_render.py` (DICOM originals untouched)
- No new cases promoted into `images/{{train,val,test}}` or `labels/{{train,val,test}}`
- No synthetic / flip / phone-photo cases added
- Annotation stubs created only under `annotation_pilot/annotations/remediation_v1/`
"""
        (META / "provenance.md").write_text(prov, encoding="utf-8")

    # Hard tag distribution among selected NEW only
    tag_counts = {}
    for case_id, dicom, *_ in SELECTED_NEW:
        for t in TAGS[dicom]["hard_tags"].split(";"):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    summary = {
        "created_utc": utc,
        "candidates_inventoried": state["n_inventory_rows"],
        "empty_patient_dirs": state["n_empty_patient_dirs"],
        "dicoms_a_annoter_used": 26,
        "dicoms_a_verifier": 8,
        "dicoms_rejetees": 2,
        "eligible_yes": 0,
        "eligible_pending_physician": 8,
        "selected_new_unique_patients": 6,
        "total_remediation_cases_in_yolo": 26,
        "new_cases_yolo_promoted": 0,
        "test_cases": 0,
        "hard_tag_distribution_selected_new": tag_counts,
        "annotation_qa_complete": False,
        "final_evaluation_ready": False,
        "safe_to_proceed_step_e": False,
        "blockers": [
            "Insufficient real unused AP pelvis DICOMs to reach 40–80 total",
            "Cannot form >=15 held-out test cases without fabricating or reshuffling",
            "All unused a_verifier cases require physician adult/eligibility confirmation",
            "New cases not annotated; YOLO promotion withheld",
        ],
    }
    (META / "stepD_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("SELECTED_CSV", META / "selected_cases.csv")
    print("ANN_DIR", ANN)
    print("SUMMARY", summary)


if __name__ == "__main__":
    main()
