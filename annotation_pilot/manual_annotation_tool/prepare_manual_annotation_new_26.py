#!/usr/bin/env python3
"""Prépare et vérifie la session d'annotation manuelle new_26 (sans import YOLO)."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

import server  # noqa: E402
from dicom_render import read_dicom_dimensions  # noqa: E402
from verification_radios import DICOM_DIR, selected_dicom_names, verification_by_dicom  # noqa: E402

OUTPUT_DIR = TOOL_DIR.parent / "annotations" / "new_26"
EXPECTED_COUNT = 26


def empty_annotation(pilot_id: str, dicom_name: str) -> dict:
    return {
        "schema_version": "mvp-pilot-1.0",
        "image_id": pilot_id,
        "source_file": dicom_name,
        "source_dataset": "bassin_a_annoter",
        "view": "AP_pelvis",
        "population_note": "adult_pelvis_AP_selected",
        "annotator_id": "annotator_A",
        "annotation_date": None,
        "guidelines_version": "annotation_guidelines.md_2026-07-17",
        "image_width": None,
        "image_height": None,
        "landmarks": [
            {
                "id": landmark_id,
                "name": name,
                "side": side,
                "x": None,
                "y": None,
                "v": None,
                "notes": "",
            }
            for landmark_id, name, side in server.LANDMARKS
        ],
        "image_level": {
            "pelvic_rotation_suspected": None,
            "fov_diaphysis_insufficient_R": None,
            "fov_diaphysis_insufficient_L": None,
            "overall_annotation_feasible": None,
        },
        "ambiguity_flags": [],
    }


def ensure_worklist_and_json(selected: list[str]) -> list[dict[str, str]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = verification_by_dicom()
    rows: list[dict[str, str]] = []

    for index, dicom_name in enumerate(selected, start=1):
        pilot_id = f"B26_{index:02d}"
        annotation_name = f"{pilot_id}.json"
        annotation_path = OUTPUT_DIR / annotation_name
        if not annotation_path.exists():
            annotation_path.write_text(
                json.dumps(empty_annotation(pilot_id, dicom_name), ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
        rows.append(
            {
                "order": str(index),
                "pilot_id": pilot_id,
                "image_file": f"{pilot_id}.png",
                "annotation_file": annotation_name,
                "dicom_file": dicom_name,
                "status": "pending",
                "verification_remarque": meta.get(dicom_name, {}).get("remarque", ""),
            }
        )

    worklist_path = OUTPUT_DIR / "worklist.csv"
    with worklist_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "order",
                "pilot_id",
                "image_file",
                "annotation_file",
                "dicom_file",
                "status",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in writer.fieldnames})

    return rows


def validate_accessibility() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    config = server.build_dataset_config("new_26")

    for case in config.cases:
        pilot_id = case["pilot_id"]
        dicom_path = DICOM_DIR / str(case["dicom_name"])
        json_path = OUTPUT_DIR / str(case["annotation_name"])

        if not dicom_path.is_file():
            errors.append(f"{pilot_id}: DICOM absent ({case['dicom_name']})")
            continue
        if not json_path.is_file():
            errors.append(f"{pilot_id}: JSON absent")
            continue

        try:
            read_dicom_dimensions(dicom_path)
        except Exception as exc:
            errors.append(f"{pilot_id}: DICOM illisible ({exc})")

        try:
            data = json.loads(json_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            errors.append(f"{pilot_id}: JSON illisible ({exc})")
            continue

        landmarks = data.get("landmarks")
        if not isinstance(landmarks, list) or len(landmarks) != 14:
            errors.append(f"{pilot_id}: attendu 14 landmarks, trouvé {len(landmarks) if isinstance(landmarks, list) else '?'}")

        remarque = verification_by_dicom().get(str(case["dicom_name"]), {}).get("remarque", "")
        if remarque and ("FSD" in remarque or "cadrage bas" in remarque.lower() or "serre" in remarque.lower()):
            warnings.append(f"{pilot_id}: FOV diaphyse possiblement court — vérifier FSD (v=0 si non fiable)")

    return errors, warnings


def main() -> int:
    selected = selected_dicom_names()
    if len(selected) != EXPECTED_COUNT:
        print(f"ERROR: verification_radios.csv — attendu {EXPECTED_COUNT} utilisable=oui, trouvé {len(selected)}")
        return 1

    on_disk = sorted(path.name for path in DICOM_DIR.iterdir() if path.is_file())
    missing = sorted(set(selected) - set(on_disk))
    extra = sorted(set(on_disk) - set(selected))
    if missing:
        print("ERROR: DICOM manquants dans a_annoter:")
        for name in missing:
            print(f"  - {name}")
        return 1
    if extra:
        print(f"WARN: {len(extra)} fichier(s) dans a_annoter hors sélection CSV (ignorés)")

    rows = ensure_worklist_and_json(selected)
    errors, warnings = validate_accessibility()

    print(f"READY cases={len(rows)} worklist={OUTPUT_DIR / 'worklist.csv'}")
    print("Launch: .\\annotation_pilot\\manual_annotation_tool\\launch_new_26.ps1")
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
