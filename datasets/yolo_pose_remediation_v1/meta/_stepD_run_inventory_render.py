"""Phase 10C Step D — inventory, triage render, selection (no training)."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\g\OneDrive\Desktop\Projet-Ayman")
sys.path.insert(0, str(ROOT / "annotation_pilot" / "manual_annotation_tool"))
from dicom_render import render_dicom_png  # noqa: E402

import pydicom  # noqa: E402

BASSIN = ROOT / "bassin"
SRC26 = ROOT / "datasets" / "yolo_pose_new_26"
REM = ROOT / "datasets" / "yolo_pose_remediation_v1"
TRIAGE = REM / "triage_renders"
META = REM / "meta"

CONTINUITY = ["B26_10", "B26_13", "B26_17", "B26_20", "B26_26"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_verification() -> dict[str, dict]:
    path = BASSIN / "verification_radios.csv"
    out = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out[row["nom_fichier"]] = row
    return out


def load_b26_mapping() -> dict[str, dict]:
    path = SRC26 / "meta" / "source_mapping.csv"
    out = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            # source_dicom like bassin\a_annoter\<uid>
            dicom_name = Path(row["source_dicom"].replace("\\", "/")).name
            out[dicom_name] = row
    return out


def normalize_name(name: str) -> str:
    s = re.sub(r"\s+", " ", name.replace("^", " ").replace("_", " ")).strip().upper()
    return s


def dicom_meta(path: Path) -> dict:
    ds = pydicom.dcmread(str(path), stop_before_pixels=True, force=True)
    def g(a, default=""):
        v = getattr(ds, a, default)
        return "" if v is None else str(v)
    rows = int(getattr(ds, "Rows", 0) or 0)
    cols = int(getattr(ds, "Columns", 0) or 0)
    return {
        "patient_id": g("PatientID"),
        "patient_name": g("PatientName"),
        "patient_age": g("PatientAge"),
        "patient_sex": g("PatientSex"),
        "study_date": g("StudyDate"),
        "modality": g("Modality"),
        "body_part": g("BodyPartExamined"),
        "study_desc": g("StudyDescription"),
        "series_desc": g("SeriesDescription"),
        "view_position": g("ViewPosition"),
        "rows": rows,
        "columns": cols,
        "sop_uid": g("SOPInstanceUID"),
    }


def list_dicoms(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted([p for p in folder.iterdir() if p.is_file()])


def main() -> None:
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ver = load_verification()
    b26 = load_b26_mapping()
    META.mkdir(parents=True, exist_ok=True)
    TRIAGE.mkdir(parents=True, exist_ok=True)

    inventory_rows = []
    # Empty PATIENT_* folders
    for p in sorted(BASSIN.iterdir()):
        if not p.is_dir():
            continue
        if p.name in {"a_annoter", "a_verifier", "rejetees"}:
            continue
        n_files = sum(1 for f in p.rglob("*") if f.is_file())
        inventory_rows.append(
            {
                "candidate_id": f"EMPTY_DIR::{p.name}",
                "source_folder": f"bassin/{p.name}",
                "dicom_file": "",
                "patient_id": "",
                "patient_name": p.name.rsplit("_", 1)[0] if "_" in p.name else p.name,
                "patient_age": "",
                "study_desc": "",
                "series_desc": "",
                "view_info": "",
                "ap_pelvis_likely": "UNKNOWN",
                "already_used_as_b26": "NO",
                "b26_id": "",
                "duplicate_or_rejected": "EMPTY_FOLDER",
                "image_width": "",
                "image_height": "",
                "n_files_in_folder": n_files,
                "verification_status": "",
                "eligible": "NO",
                "exclusion_reason": "Patient directory present but contains 0 DICOM files",
                "notes": "Placeholder folder; DICOM consolidated elsewhere",
            }
        )

    # Real DICOM pools
    pools = {
        "a_annoter": BASSIN / "a_annoter",
        "a_verifier": BASSIN / "a_verifier",
        "rejetees": BASSIN / "rejetees",
    }

    all_dicom_meta = []
    for pool_name, folder in pools.items():
        for dicom_path in list_dicoms(folder):
            m = dicom_meta(dicom_path)
            vrow = ver.get(dicom_path.name, {})
            used = dicom_path.name in b26
            b26_id = b26[dicom_path.name]["pilot_id"] if used else ""
            utilisable = (vrow.get("utilisable_annotation") or "").strip().lower()
            bassin_ok = (vrow.get("bassin") or "").strip().lower()
            ap_ok = (vrow.get("AP") or "").strip().lower()
            adulte = (vrow.get("adulte") or "").strip().lower()
            rejet = (vrow.get("raison_rejet") or "").strip()

            # eligibility for NEW remediation expansion (not already B26)
            eligible = "NO"
            exclusion = ""
            if used:
                eligible = "NO"
                exclusion = f"Already used as {b26_id}"
            elif pool_name == "rejetees" or utilisable == "non":
                eligible = "NO"
                exclusion = rejet or "Rejected in verification_radios.csv; not re-qualified"
            elif utilisable == "incertain" or adulte == "incertain":
                eligible = "PENDING_PHYSICIAN"
                exclusion = (
                    vrow.get("remarque")
                    or "Adult/annotation eligibility uncertain; physician confirmation required"
                )
            elif utilisable == "oui" and bassin_ok == "oui" and ap_ok == "oui" and adulte == "oui":
                eligible = "YES"
                exclusion = ""
            else:
                eligible = "NO"
                exclusion = f"verification flags: utilisable={utilisable} bassin={bassin_ok} AP={ap_ok} adulte={adulte}"

            ap_likely = "YES" if ap_ok == "oui" and bassin_ok == "oui" else (
                "NO" if bassin_ok == "non" or ap_ok in {"non", "incertain"} and bassin_ok != "oui" else "UNCERTAIN"
            )
            if ap_ok == "oui" and bassin_ok == "oui":
                ap_likely = "YES"
            elif bassin_ok == "non":
                ap_likely = "NO"
            else:
                ap_likely = "UNCERTAIN"

            dup_rej = ""
            if pool_name == "rejetees":
                dup_rej = "REJECTED"
            if utilisable == "incertain":
                dup_rej = (dup_rej + ";UNCERTAIN").strip(";")

            row = {
                "candidate_id": f"{pool_name}::{dicom_path.name}",
                "source_folder": f"bassin/{pool_name}",
                "dicom_file": dicom_path.name,
                "patient_id": m["patient_id"],
                "patient_name": m["patient_name"],
                "patient_age": m["patient_age"],
                "study_desc": m["study_desc"],
                "series_desc": m["series_desc"],
                "view_info": f"{m['view_position']}|{m['series_desc']}|{m['study_desc']}",
                "ap_pelvis_likely": ap_likely,
                "already_used_as_b26": "YES" if used else "NO",
                "b26_id": b26_id,
                "duplicate_or_rejected": dup_rej or "NO",
                "image_width": m["columns"],
                "image_height": m["rows"],
                "n_files_in_folder": "",
                "verification_status": utilisable or "missing_from_csv",
                "eligible": eligible,
                "exclusion_reason": exclusion,
                "notes": (vrow.get("remarque") or "").strip(),
                "dicom_sha256": sha256_file(dicom_path),
                "pool": pool_name,
            }
            inventory_rows.append(row)
            all_dicom_meta.append(row)

    # Detect same-patient multi-image
    by_pid: dict[str, list[str]] = {}
    for r in all_dicom_meta:
        by_pid.setdefault(r["patient_id"], []).append(r["dicom_file"])
    multi = {k: v for k, v in by_pid.items() if len(v) > 1}

    # Mark cross-pool same patient (e.g. ZAFFOU in a_annoter + rejetees)
    for r in inventory_rows:
        if not r.get("patient_id"):
            continue
        siblings = by_pid.get(r["patient_id"], [])
        if len(siblings) > 1:
            note = f"Same PatientID appears in {len(siblings)} DICOM(s): " + ";".join(siblings)
            if r.get("notes"):
                if note not in r["notes"]:
                    r["notes"] = r["notes"] + " | " + note
            else:
                r["notes"] = note
            if r["duplicate_or_rejected"] in {"", "NO"}:
                r["duplicate_or_rejected"] = "MULTI_IMAGE_SAME_PATIENT"
            elif "MULTI_IMAGE" not in r["duplicate_or_rejected"]:
                r["duplicate_or_rejected"] += ";MULTI_IMAGE_SAME_PATIENT"

    # Write candidate_inventory.csv
    inv_fields = [
        "candidate_id",
        "source_folder",
        "dicom_file",
        "patient_id",
        "patient_name",
        "patient_age",
        "study_desc",
        "series_desc",
        "view_info",
        "ap_pelvis_likely",
        "already_used_as_b26",
        "b26_id",
        "duplicate_or_rejected",
        "image_width",
        "image_height",
        "n_files_in_folder",
        "verification_status",
        "eligible",
        "exclusion_reason",
        "notes",
        "dicom_sha256",
        "pool",
    ]
    inv_path = META / "candidate_inventory.csv"
    with inv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=inv_fields, extrasaction="ignore")
        w.writeheader()
        for r in inventory_rows:
            w.writerow(r)

    # D2: render triage for a_verifier + rejetees (not B26; B26 already have PNGs)
    render_manifest = []
    triage_targets = [r for r in all_dicom_meta if r["pool"] in {"a_verifier", "rejetees"}]
    for r in triage_targets:
        dicom_path = BASSIN / r["pool"] / r["dicom_file"]
        safe = r["dicom_file"].replace(".", "_")[-80:]
        out_png = TRIAGE / r["pool"] / f"{safe}.png"
        w, h = render_dicom_png(dicom_path, out_png)
        render_manifest.append(
            {
                "candidate_id": r["candidate_id"],
                "dicom_file": r["dicom_file"],
                "pool": r["pool"],
                "patient_id": r["patient_id"],
                "patient_name": r["patient_name"],
                "render_path": str(out_png.relative_to(ROOT)).replace("\\", "/"),
                "render_sha256": sha256_file(out_png),
                "width": w,
                "height": h,
                "eligible": r["eligible"],
            }
        )
    (META / "triage_render_manifest.json").write_text(
        json.dumps({"created_utc": utc, "renders": render_manifest}, indent=2) + "\n",
        encoding="utf-8",
    )

    # Save state for tagging / reports
    state = {
        "created_utc": utc,
        "n_inventory_rows": len(inventory_rows),
        "n_empty_patient_dirs": sum(1 for r in inventory_rows if r["candidate_id"].startswith("EMPTY")),
        "n_dicoms_a_annoter": sum(1 for r in all_dicom_meta if r["pool"] == "a_annoter"),
        "n_dicoms_a_verifier": sum(1 for r in all_dicom_meta if r["pool"] == "a_verifier"),
        "n_dicoms_rejetees": sum(1 for r in all_dicom_meta if r["pool"] == "rejetees"),
        "eligible_yes": [r["candidate_id"] for r in all_dicom_meta if r["eligible"] == "YES"],
        "eligible_pending": [r for r in all_dicom_meta if r["eligible"] == "PENDING_PHYSICIAN"],
        "multi_patient_images": multi,
        "render_manifest": render_manifest,
        "b26_patient_ids": sorted({r["patient_id"] for r in all_dicom_meta if r["pool"] == "a_annoter"}),
        "continuity_probe": CONTINUITY,
    }
    (META / "_stepD_state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print("INVENTORY_OK", inv_path)
    print("EMPTY_DIRS", state["n_empty_patient_dirs"])
    print("A_ANNOTER", state["n_dicoms_a_annoter"])
    print("A_VERIFIER", state["n_dicoms_a_verifier"])
    print("REJETEES", state["n_dicoms_rejetees"])
    print("ELIGIBLE_YES", state["eligible_yes"])
    print("ELIGIBLE_PENDING", len(state["eligible_pending"]))
    print("RENDERS", len(render_manifest))
    print("MULTI_PID", {k: len(v) for k, v in multi.items()})


if __name__ == "__main__":
    main()
