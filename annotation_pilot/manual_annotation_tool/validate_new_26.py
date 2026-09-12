#!/usr/bin/env python3
"""Validation en lecture seule du lot new_26 (26 annotations bassin)."""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

import server  # noqa: E402
from dicom_render import read_dicom_dimensions  # noqa: E402

EXPECTED_LANDMARKS = [name for _, name, _ in server.LANDMARKS]
ANNOT_DIR = TOOL_DIR.parent / "annotations" / "new_26"
DICOM_DIR = TOOL_DIR.parent.parent / "bassin" / "a_annoter"
REPORT_CSV = ANNOT_DIR / "validation_report.csv"
SUMMARY_MD = ANNOT_DIR / "validation_summary.md"


def classify_aberrant(
    landmarks_with_coords: list[dict], width: float, height: float
) -> list[str]:
    warnings: list[str] = []
    coords = [
        (str(lm["name"]), float(lm["x"]), float(lm["y"]))
        for lm in landmarks_with_coords
    ]

    for name, x, y in coords:
        if x == 0 and y == 0:
            warnings.append(f"{name}: coordonnées à l'origine (0, 0)")

    seen: dict[tuple[float, float], list[str]] = defaultdict(list)
    for name, x, y in coords:
        key = (round(x, 1), round(y, 1))
        seen[key].append(name)
    for key, names in seen.items():
        if len(names) > 1:
            joined = ", ".join(names)
            warnings.append(f"Doublon suspect aux coords {key}: {joined}")

    for name, x, y in coords:
        if x < 1 or y < 1 or x >= width - 1 or y >= height - 1:
            warnings.append(f"{name}: très proche du bord ({x:.1f}, {y:.1f})")

    mid = width / 2
    margin = width * 0.05
    for name, x, _y in coords:
        if name.endswith("_R") and x > mid + margin:
            warnings.append(
                f"{name}: côté droit mais x={x:.1f} > milieu+5% ({mid:.1f}) — à vérifier"
            )
        if name.endswith("_L") and x < mid - margin:
            warnings.append(
                f"{name}: côté gauche mais x={x:.1f} < milieu-5% ({mid:.1f}) — à vérifier"
            )

    return warnings


def main() -> int:
    config = server.build_dataset_config("new_26")
    expected_ids = [f"B26_{index:02d}" for index in range(1, 27)]

    rows: list[dict[str, str]] = []
    valid_count = 0
    review_count = 0
    global_stats = {
        "files_present": 0,
        "files_missing": [],
        "extra_files": [],
        "total_landmarks": 0,
        "visible_landmarks_v2": 0,
        "invisible_landmarks_v0": 0,
        "unset_landmarks_vnull": 0,
        "dicom_dimension_mismatches": 0,
    }

    found_files = sorted(path.name for path in ANNOT_DIR.glob("B26_*.json"))
    expected_file_names = {f"{pilot_id}.json" for pilot_id in expected_ids}
    for pilot_id in expected_ids:
        file_name = f"{pilot_id}.json"
        if file_name not in found_files:
            global_stats["files_missing"].append(file_name)
    for file_name in found_files:
        if file_name not in expected_file_names:
            global_stats["extra_files"].append(file_name)

    for case in config.cases:
        pilot_id = case["pilot_id"]
        annotation_path = ANNOT_DIR / case["annotation_name"]
        dicom_path = DICOM_DIR / case["dicom_name"]

        if not annotation_path.is_file():
            review_count += 1
            rows.append(
                {
                    "pilot_id": pilot_id,
                    "annotation_file": case["annotation_name"],
                    "dicom_file": case["dicom_name"],
                    "status": "MISSING",
                    "severity": "ERROR",
                    "category": "presence",
                    "landmark": "",
                    "message": "Fichier JSON absent",
                }
            )
            continue

        global_stats["files_present"] += 1

        try:
            data = json.loads(annotation_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            review_count += 1
            rows.append(
                {
                    "pilot_id": pilot_id,
                    "annotation_file": case["annotation_name"],
                    "dicom_file": case["dicom_name"],
                    "status": "INVALID",
                    "severity": "ERROR",
                    "category": "json_parse",
                    "landmark": "",
                    "message": str(exc),
                }
            )
            continue

        schema_errors = server.validate_annotation(data, case, config, finalize=True)
        for err in schema_errors:
            rows.append(
                {
                    "pilot_id": pilot_id,
                    "annotation_file": case["annotation_name"],
                    "dicom_file": case["dicom_name"],
                    "status": "TO_REVIEW",
                    "severity": "ERROR",
                    "category": "schema",
                    "landmark": err.split(":")[0].split()[0] if ":" in err else "",
                    "message": err,
                }
            )

        landmark_names: list[str] = []
        if isinstance(data.get("landmarks"), list):
            landmark_names = [
                str(lm.get("name"))
                for lm in data["landmarks"]
                if isinstance(lm, dict) and lm.get("name") is not None
            ]

        missing_landmarks = [name for name in EXPECTED_LANDMARKS if name not in landmark_names]
        extra_landmarks = [name for name in landmark_names if name not in EXPECTED_LANDMARKS]
        if missing_landmarks:
            message = "Landmarks manquants: " + ", ".join(missing_landmarks)
            rows.append(
                {
                    "pilot_id": pilot_id,
                    "annotation_file": case["annotation_name"],
                    "dicom_file": case["dicom_name"],
                    "status": "TO_REVIEW",
                    "severity": "ERROR",
                    "category": "landmark_presence",
                    "landmark": ", ".join(missing_landmarks),
                    "message": message,
                }
            )
        if extra_landmarks:
            message = "Landmarks inattendus: " + ", ".join(extra_landmarks)
            rows.append(
                {
                    "pilot_id": pilot_id,
                    "annotation_file": case["annotation_name"],
                    "dicom_file": case["dicom_name"],
                    "status": "TO_REVIEW",
                    "severity": "WARNING",
                    "category": "landmark_presence",
                    "landmark": ", ".join(extra_landmarks),
                    "message": message,
                }
            )

        width = data.get("image_width")
        height = data.get("image_height")
        visible_landmarks: list[dict] = []
        if isinstance(data.get("landmarks"), list):
            for landmark in data["landmarks"]:
                if not isinstance(landmark, dict):
                    continue
                name = str(landmark.get("name", "?"))
                global_stats["total_landmarks"] += 1
                visibility = landmark.get("v")
                x, y = landmark.get("x"), landmark.get("y")

                if visibility is None:
                    global_stats["unset_landmarks_vnull"] += 1
                elif visibility == 0:
                    global_stats["invisible_landmarks_v0"] += 1
                    if x is not None or y is not None:
                        message = f"{name}: v=0 mais coordonnées non nulles (x={x}, y={y})"
                        rows.append(
                            {
                                "pilot_id": pilot_id,
                                "annotation_file": case["annotation_name"],
                                "dicom_file": case["dicom_name"],
                                "status": "TO_REVIEW",
                                "severity": "ERROR",
                                "category": "visibility_v0",
                                "landmark": name,
                                "message": message,
                            }
                        )
                elif visibility == 2:
                    global_stats["visible_landmarks_v2"] += 1
                    visible_landmarks.append(landmark)
                    if x is None or y is None:
                        message = f"{name}: v=2 mais coordonnées manquantes (x={x}, y={y})"
                        rows.append(
                            {
                                "pilot_id": pilot_id,
                                "annotation_file": case["annotation_name"],
                                "dicom_file": case["dicom_name"],
                                "status": "TO_REVIEW",
                                "severity": "ERROR",
                                "category": "missing_coords",
                                "landmark": name,
                                "message": message,
                            }
                        )
                    elif x == 0 and y == 0:
                        message = f"{name}: coordonnées nulles (0, 0) avec v=2"
                        rows.append(
                            {
                                "pilot_id": pilot_id,
                                "annotation_file": case["annotation_name"],
                                "dicom_file": case["dicom_name"],
                                "status": "TO_REVIEW",
                                "severity": "WARNING",
                                "category": "null_coords",
                                "landmark": name,
                                "message": message,
                            }
                        )
                elif visibility == 1:
                    message = f"{name}: v=1 non autorisé"
                    rows.append(
                        {
                            "pilot_id": pilot_id,
                            "annotation_file": case["annotation_name"],
                            "dicom_file": case["dicom_name"],
                            "status": "TO_REVIEW",
                            "severity": "ERROR",
                            "category": "visibility",
                            "landmark": name,
                            "message": message,
                        }
                    )

        try:
            dicom_w, dicom_h = read_dicom_dimensions(dicom_path)
            ann_w, ann_h = data.get("image_width"), data.get("image_height")
            if ann_w != dicom_w or ann_h != dicom_h:
                global_stats["dicom_dimension_mismatches"] += 1
                message = f"Dimensions JSON ({ann_w}x{ann_h}) != DICOM ({dicom_w}x{dicom_h})"
                rows.append(
                    {
                        "pilot_id": pilot_id,
                        "annotation_file": case["annotation_name"],
                        "dicom_file": case["dicom_name"],
                        "status": "TO_REVIEW",
                        "severity": "ERROR",
                        "category": "dicom_dimensions",
                        "landmark": "",
                        "message": message,
                    }
                )
        except Exception as exc:
            message = f"Impossible de lire dimensions DICOM: {exc}"
            rows.append(
                {
                    "pilot_id": pilot_id,
                    "annotation_file": case["annotation_name"],
                    "dicom_file": case["dicom_name"],
                    "status": "TO_REVIEW",
                    "severity": "ERROR",
                    "category": "dicom_read",
                    "landmark": "",
                    "message": message,
                }
            )

        if data.get("image_id") != pilot_id:
            message = f"image_id={data.get('image_id')} != attendu {pilot_id}"
            rows.append(
                {
                    "pilot_id": pilot_id,
                    "annotation_file": case["annotation_name"],
                    "dicom_file": case["dicom_name"],
                    "status": "TO_REVIEW",
                    "severity": "ERROR",
                    "category": "identity",
                    "landmark": "",
                    "message": message,
                }
            )
        if data.get("source_file") != case["dicom_name"]:
            message = (
                f"source_file={data.get('source_file')} != DICOM worklist {case['dicom_name']}"
            )
            rows.append(
                {
                    "pilot_id": pilot_id,
                    "annotation_file": case["annotation_name"],
                    "dicom_file": case["dicom_name"],
                    "status": "TO_REVIEW",
                    "severity": "ERROR",
                    "category": "identity",
                    "landmark": "",
                    "message": message,
                }
            )

        if visible_landmarks and server.is_number(width) and server.is_number(height):
            for warning in classify_aberrant(visible_landmarks, float(width), float(height)):
                rows.append(
                    {
                        "pilot_id": pilot_id,
                        "annotation_file": case["annotation_name"],
                        "dicom_file": case["dicom_name"],
                        "status": "TO_REVIEW",
                        "severity": "WARNING",
                        "category": "aberrant_coords",
                        "landmark": warning.split(":")[0],
                        "message": warning,
                    }
                )

        has_errors = any(
            row["pilot_id"] == pilot_id and row["severity"] == "ERROR" for row in rows
        )
        has_warnings = any(
            row["pilot_id"] == pilot_id and row["severity"] == "WARNING" for row in rows
        )
        if has_errors or has_warnings:
            review_count += 1
        else:
            valid_count += 1
            rows.append(
                {
                    "pilot_id": pilot_id,
                    "annotation_file": case["annotation_name"],
                    "dicom_file": case["dicom_name"],
                    "status": "VALID",
                    "severity": "INFO",
                    "category": "summary",
                    "landmark": "all_14",
                    "message": (
                        "14 landmarks présents, coordonnées valides, correspondance DICOM OK"
                    ),
                }
            )

    for file_name in global_stats["files_missing"]:
        pilot_id = file_name.replace(".json", "")
        rows.append(
            {
                "pilot_id": pilot_id,
                "annotation_file": file_name,
                "dicom_file": "",
                "status": "MISSING",
                "severity": "ERROR",
                "category": "presence",
                "landmark": "",
                "message": "Fichier absent",
            }
        )

    fieldnames = [
        "pilot_id",
        "annotation_file",
        "dicom_file",
        "status",
        "severity",
        "category",
        "landmark",
        "message",
    ]
    with REPORT_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    by_pilot: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_pilot[row["pilot_id"]].append(row)

    error_pilots = sorted({row["pilot_id"] for row in rows if row["severity"] == "ERROR"})
    warning_pilots = sorted({row["pilot_id"] for row in rows if row["severity"] == "WARNING"})
    valid_pilots = sorted({row["pilot_id"] for row in rows if row["status"] == "VALID"})

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Rapport de validation — dataset new_26",
        "",
        f"**Date de génération :** {now}",
        f"**Répertoire :** `{ANNOT_DIR}`",
        "",
        "## Résumé exécutif",
        "",
        "| Métrique | Valeur |",
        "|----------|--------|",
        "| Annotations attendues | 26 |",
        f"| Fichiers JSON présents | {global_stats['files_present']} |",
        f"| Fichiers JSON manquants | {len(global_stats['files_missing'])} |",
        f"| **Annotations valides** | **{valid_count}** |",
        f"| **Annotations à vérifier** | **{review_count}** |",
        f"| Erreurs (ERROR) | {sum(1 for row in rows if row['severity'] == 'ERROR')} |",
        f"| Avertissements (WARNING) | {sum(1 for row in rows if row['severity'] == 'WARNING')} |",
        "",
        "## Statistiques landmarks",
        "",
        f"- Total landmarks vérifiés : {global_stats['total_landmarks']} (attendu : 364 = 26×14)",
        f"- Landmarks visibles (v=2) : {global_stats['visible_landmarks_v2']}",
        f"- Landmarks non visibles (v=0) : {global_stats['invisible_landmarks_v0']}",
        f"- Landmarks non renseignés (v=null) : {global_stats['unset_landmarks_vnull']}",
        f"- Incohérences dimensions JSON/DICOM : {global_stats['dicom_dimension_mismatches']}",
        "",
        "## Critères vérifiés",
        "",
        "1. Présence des 14 landmarks (TD, FHC, ASL, ASM, FNM, FSP, FSD — R/L)",
        "2. Champs x, y, v pour chaque landmark",
        "3. Coordonnées x/y dans les dimensions réelles de l'image (0 ≤ x < width, 0 ≤ y < height)",
        "4. Gestion v=0 : x=null et y=null obligatoires",
        "5. Détection coordonnées nulles ou manquantes",
        "6. Détection doublons et coordonnées aberrantes (bords, inversion R/L)",
        "7. Correspondance image_id / source_file ↔ B26_XX / DICOM worklist",
        "8. Présence des 26 fichiers B26_01.json à B26_26.json",
        "9. Cohérence dimensions annotation ↔ DICOM source",
        "",
    ]

    if global_stats["files_missing"]:
        lines.extend(["## Fichiers manquants", ""])
        for file_name in global_stats["files_missing"]:
            lines.append(f"- `{file_name}`")
        lines.append("")

    if error_pilots:
        lines.extend(["## Annotations avec erreurs", ""])
        for pilot_id in error_pilots:
            lines.append(f"### {pilot_id}")
            for row in by_pilot[pilot_id]:
                if row["severity"] == "ERROR":
                    suffix = f" [{row['landmark']}]" if row["landmark"] else ""
                    lines.append(f"- **{row['category']}**{suffix}: {row['message']}")
            lines.append("")

    if warning_pilots:
        lines.extend(["## Annotations avec avertissements (à vérifier visuellement)", ""])
        for pilot_id in warning_pilots:
            lines.append(f"### {pilot_id}")
            for row in by_pilot[pilot_id]:
                if row["severity"] == "WARNING":
                    suffix = f" [{row['landmark']}]" if row["landmark"] else ""
                    lines.append(f"- **{row['category']}**{suffix}: {row['message']}")
            lines.append("")

    if valid_pilots:
        lines.extend(["## Annotations valides", ""])
        lines.append(", ".join(f"`{pilot_id}`" for pilot_id in valid_pilots))
        lines.append("")

    lines.extend(
        [
            "## Fichiers générés",
            "",
            f"- Rapport détaillé CSV : `{REPORT_CSV}`",
            f"- Ce résumé : `{SUMMARY_MD}`",
            "",
            "---",
            "*Validation en lecture seule — aucune annotation modifiée.*",
        ]
    )

    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"VALID={valid_count} REVIEW={review_count}")
    print(f"ERRORS={sum(1 for row in rows if row['severity'] == 'ERROR')}")
    print(f"WARNINGS={sum(1 for row in rows if row['severity'] == 'WARNING')}")
    print(f"CSV={REPORT_CSV}")
    print(f"MD={SUMMARY_MD}")
    if error_pilots:
        print("ERROR_PILOTS=" + ",".join(error_pilots))
    if warning_pilots:
        print("WARNING_PILOTS=" + ",".join(warning_pilots))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
