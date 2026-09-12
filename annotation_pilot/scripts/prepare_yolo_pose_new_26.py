#!/usr/bin/env python3
"""Prépare le dataset YOLO Pose à partir des annotations new_26 (lecture seule sur les sources)."""

from __future__ import annotations

import csv
import json
import random
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

TOOL_DIR = Path(__file__).resolve().parent.parent / "manual_annotation_tool"
sys.path.insert(0, str(TOOL_DIR))

import server  # noqa: E402
from dicom_render import render_dicom_png  # noqa: E402

PROJECT_ROOT = TOOL_DIR.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
DICOM_DIR = PROJECT_ROOT / "bassin" / "a_annoter"
OUTPUT_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"

SPLIT_SEED = 42
VAL_RATIO = 5 / 26  # ~19 % → 5 val, 21 train (reproductible)
CLASS_NAME = "pelvis"
CLASS_ID = 0
BBOX_PADDING_RATIO = 0.02

KEYPOINT_NAMES = [name for _, name, _ in server.LANDMARKS]
FLIP_IDX = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]
NKPT = len(KEYPOINT_NAMES)
NDIM = 3
EXPECTED_LABEL_COLS = 5 + NKPT * NDIM


@dataclass
class ConversionResult:
    pilot_id: str
    split: str
    image_path: Path
    label_path: Path
    width: int
    height: int
    visible_keypoints: int
    bbox: tuple[float, float, float, float]
    issues: list[str]


def map_visibility(v: Any, x: Any, y: Any) -> tuple[float, float, float]:
    """Convertit la visibilité MVP vers YOLO Pose (x, y, v normalisés plus tard pour x/y)."""
    if v == 0 or v is None:
        return 0.0, 0.0, 0.0
    if v == 2:
        if x is None or y is None:
            raise ValueError(f"Landmark v=2 sans coordonnées (x={x}, y={y})")
        return float(x), float(y), 2.0
    raise ValueError(f"Valeur de visibilité non supportée: v={v}")


def compute_bbox(
    keypoints_px: list[tuple[float, float, float]], width: int, height: int
) -> tuple[float, float, float, float]:
    """BBox englobante sur les keypoints visibles, avec marge, normalisée YOLO."""
    visible = [(x, y) for x, y, v in keypoints_px if v > 0]
    if not visible:
        raise ValueError("Aucun keypoint visible pour calculer la bbox")

    xs = [point[0] for point in visible]
    ys = [point[1] for point in visible]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    pad_x = max((x_max - x_min) * BBOX_PADDING_RATIO, width * BBOX_PADDING_RATIO)
    pad_y = max((y_max - y_min) * BBOX_PADDING_RATIO, height * BBOX_PADDING_RATIO)

    x_min = max(0.0, x_min - pad_x)
    y_min = max(0.0, y_min - pad_y)
    x_max = min(float(width), x_max + pad_x)
    y_max = min(float(height), y_max + pad_y)

    box_w = x_max - x_min
    box_h = y_max - y_min
    cx = (x_min + x_max) / 2.0 / width
    cy = (y_min + y_max) / 2.0 / height
    nw = box_w / width
    nh = box_h / height
    return cx, cy, nw, nh


def build_yolo_label(
    keypoints_px: list[tuple[float, float, float]], width: int, height: int
) -> str:
    cx, cy, bw, bh = compute_bbox(keypoints_px, width, height)
    parts: list[str] = [
        str(CLASS_ID),
        f"{cx:.6f}",
        f"{cy:.6f}",
        f"{bw:.6f}",
        f"{bh:.6f}",
    ]
    for x_px, y_px, v in keypoints_px:
        if v > 0:
            parts.extend([f"{x_px / width:.6f}", f"{y_px / height:.6f}", f"{v:.0f}"])
        else:
            parts.extend(["0.000000", "0.000000", "0"])
    return " ".join(parts)


def verify_label_line(line: str, width: int, height: int) -> list[str]:
    issues: list[str] = []
    values = line.split()
    if len(values) != EXPECTED_LABEL_COLS:
        issues.append(f"Nombre de colonnes {len(values)} != {EXPECTED_LABEL_COLS}")
        return issues

    nums = [float(value) for value in values]
    cls_id = int(nums[0])
    if cls_id != CLASS_ID:
        issues.append(f"class_id={cls_id} != {CLASS_ID}")

    bbox = nums[1:5]
    if any(value < -0.01 or value > 1.01 for value in bbox):
        issues.append(f"bbox hors [0,1]: {bbox}")

    kpts = nums[5:]
    for index in range(NKPT):
        kx = kpts[index * NDIM]
        ky = kpts[index * NDIM + 1]
        kv = kpts[index * NDIM + 2]
        name = KEYPOINT_NAMES[index]
        if kv == 0:
            if kx != 0 or ky != 0:
                issues.append(f"{name}: v=0 mais x/y non nuls ({kx}, {ky})")
        elif kv == 2:
            if not (0 <= kx <= 1.01 and 0 <= ky <= 1.01):
                issues.append(f"{name}: coordonnées normalisées hors bornes ({kx}, {ky})")
        else:
            issues.append(f"{name}: visibilité YOLO invalide v={kv}")
    return issues


def load_cases() -> list[dict[str, Any]]:
    config = server.build_dataset_config("new_26")
    return list(config.cases)


def choose_split(pilot_ids: list[str]) -> dict[str, str]:
    rng = random.Random(SPLIT_SEED)
    shuffled = pilot_ids[:]
    rng.shuffle(shuffled)
    val_count = max(1, round(len(shuffled) * VAL_RATIO))
    val_ids = set(shuffled[:val_count])
    return {pilot_id: ("val" if pilot_id in val_ids else "train") for pilot_id in pilot_ids}


def write_dataset_yaml() -> None:
    yaml_text = f"""# YOLO Pose — bassin adulte AP (lot new_26, 26 images)
# Généré automatiquement — ne pas éditer manuellement sans regénérer.
# Usage futur : yolo train data=dataset.yaml model=yolo11n-pose.pt

path: {OUTPUT_ROOT.as_posix()}
train: images/train
val: images/val

kpt_shape: [{NKPT}, {NDIM}]
flip_idx: {FLIP_IDX}

names:
  {CLASS_ID}: {CLASS_NAME}

kpt_names:
  {CLASS_ID}:
"""
    for name in KEYPOINT_NAMES:
        yaml_text += f"    - {name}\n"
    (OUTPUT_ROOT / "dataset.yaml").write_text(yaml_text, encoding="utf-8")


def write_keypoint_order_doc() -> None:
    lines = [
        "# Ordre fixe des 14 keypoints YOLO Pose (new_26)",
        "",
        "Une seule instance `pelvis` par image, 14 keypoints bilatéraux.",
        "",
        "| Index | Nom | Côté | ID source |",
        "|------:|-----|------|-----------|",
    ]
    for index, (landmark_id, name, side) in enumerate(server.LANDMARKS):
        lines.append(f"| {index} | {name} | {side} | {landmark_id} |")
    lines.extend(
        [
            "",
            "## Mapping visibilité MVP → YOLO",
            "",
            "| MVP `v` | YOLO `v` | Coordonnées |",
            "|---------|----------|-------------|",
            "| `null` | `0` | `0, 0` |",
            "| `0` | `0` | `0, 0` |",
            "| `2` | `2` | `x/W`, `y/H` normalisés |",
            "",
            "## flip_idx (augmentation miroir horizontal)",
            "",
            f"`{FLIP_IDX}` — permutation R↔L par paire.",
            "",
            "## Format label (.txt)",
            "",
            f"`class cx cy w h " + " ".join(f"kpt{{i}}_x kpt{{i}}_y kpt{{i}}_v" for i in range(NKPT)) + "`",
            "",
            f"Total colonnes : **{EXPECTED_LABEL_COLS}** (5 + {NKPT}×{NDIM}).",
        ]
    )
    (OUTPUT_ROOT / "meta" / "keypoint_order.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    cases = load_cases()
    pilot_ids = [case["pilot_id"] for case in cases]
    split_map = choose_split(pilot_ids)

    for sub in ("images/train", "images/val", "labels/train", "labels/val", "meta"):
        (OUTPUT_ROOT / sub).mkdir(parents=True, exist_ok=True)

    results: list[ConversionResult] = []
    mapping_rows: list[dict[str, str]] = []
    all_label_issues: list[str] = []

    for case in cases:
        pilot_id = case["pilot_id"]
        split = split_map[pilot_id]
        annotation_path = ANNOT_DIR / case["annotation_name"]
        dicom_path = DICOM_DIR / case["dicom_name"]
        image_name = f"{pilot_id}.png"
        label_name = f"{pilot_id}.txt"
        image_out = OUTPUT_ROOT / "images" / split / image_name
        label_out = OUTPUT_ROOT / "labels" / split / label_name
        issues: list[str] = []

        data = json.loads(annotation_path.read_text(encoding="utf-8-sig"))
        width = int(data["image_width"])
        height = int(data["image_height"])

        if data.get("image_id") != pilot_id:
            issues.append("image_id incohérent")
        if data.get("source_file") != case["dicom_name"]:
            issues.append("source_file incohérent")

        landmarks = data.get("landmarks", [])
        if len(landmarks) != NKPT:
            issues.append(f"{len(landmarks)} landmarks au lieu de {NKPT}")

        keypoints_px: list[tuple[float, float, float]] = []
        for expected, landmark in zip(server.LANDMARKS, landmarks):
            landmark_id, name, side = expected
            if landmark.get("name") != name:
                issues.append(f"Ordre/nom landmark incorrect: attendu {name}")
            try:
                x_px, y_px, v = map_visibility(landmark.get("v"), landmark.get("x"), landmark.get("y"))
            except ValueError as exc:
                issues.append(f"{name}: {exc}")
                x_px, y_px, v = 0.0, 0.0, 0.0
            keypoints_px.append((x_px, y_px, v))

        if not image_out.exists():
            render_dicom_png(dicom_path, image_out)
        else:
            # Régénère uniquement si le cache local est absent ou plus ancien que le DICOM
            if image_out.stat().st_mtime < dicom_path.stat().st_mtime:
                render_dicom_png(dicom_path, image_out)

        label_line = build_yolo_label(keypoints_px, width, height)
        label_out.write_text(label_line + "\n", encoding="utf-8")

        label_issues = verify_label_line(label_line, width, height)
        issues.extend(label_issues)
        all_label_issues.extend(f"{pilot_id}: {issue}" for issue in label_issues)

        visible = sum(1 for _x, _y, v in keypoints_px if v > 0)
        bbox = compute_bbox(keypoints_px, width, height)
        results.append(
            ConversionResult(
                pilot_id=pilot_id,
                split=split,
                image_path=image_out,
                label_path=label_out,
                width=width,
                height=height,
                visible_keypoints=visible,
                bbox=bbox,
                issues=issues,
            )
        )
        mapping_rows.append(
            {
                "pilot_id": pilot_id,
                "split": split,
                "yolo_image": str(image_out.relative_to(OUTPUT_ROOT)),
                "yolo_label": str(label_out.relative_to(OUTPUT_ROOT)),
                "source_json": str(annotation_path.relative_to(PROJECT_ROOT)),
                "source_dicom": str(dicom_path.relative_to(PROJECT_ROOT)),
                "image_width": str(width),
                "image_height": str(height),
                "visible_keypoints": str(visible),
            }
        )

    split_manifest = {
        "seed": SPLIT_SEED,
        "val_ratio_target": VAL_RATIO,
        "train": sorted(pilot_id for pilot_id, split in split_map.items() if split == "train"),
        "val": sorted(pilot_id for pilot_id, split in split_map.items() if split == "val"),
    }
    (OUTPUT_ROOT / "meta" / "split.json").write_text(
        json.dumps(split_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    mapping_path = OUTPUT_ROOT / "meta" / "source_mapping.csv"
    with mapping_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(mapping_rows[0].keys()))
        writer.writeheader()
        writer.writerows(mapping_rows)

    write_dataset_yaml()
    write_keypoint_order_doc()

    train_count = sum(1 for result in results if result.split == "train")
    val_count = sum(1 for result in results if result.split == "val")
    anomaly_results = [result for result in results if result.issues]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines = [
        "# Rapport de préparation YOLO Pose — new_26",
        "",
        f"**Date :** {now}",
        f"**Sources (non modifiées) :** `{ANNOT_DIR.relative_to(PROJECT_ROOT)}`",
        f"**Dataset YOLO :** `{OUTPUT_ROOT.relative_to(PROJECT_ROOT)}`",
        "",
        "## Résumé",
        "",
        "| Métrique | Valeur |",
        "|----------|--------|",
        f"| Images train | {train_count} |",
        f"| Images val | {val_count} |",
        f"| Labels train | {train_count} |",
        f"| Labels val | {val_count} |",
        f"| Keypoints par image | {NKPT} |",
        f"| Keypoints total (train+val) | {(train_count + val_count) * NKPT} |",
        f"| Classe | `{CLASS_NAME}` (id={CLASS_ID}) |",
        f"| kpt_shape | [{NKPT}, {NDIM}] |",
        f"| Colonnes par label | {EXPECTED_LABEL_COLS} |",
        f"| Split seed | {SPLIT_SEED} |",
        f"| Anomalies | {len(anomaly_results)} |",
        "",
        "## Split reproductible",
        "",
        f"- **Train ({train_count}) :** {', '.join(f'`{pid}`' for pid in split_manifest['train'])}",
        f"- **Val ({val_count}) :** {', '.join(f'`{pid}`' for pid in split_manifest['val'])}",
        "",
        "## Dimensions des images",
        "",
        "| pilot_id | split | width | height | keypoints visibles |",
        "|----------|-------|------:|-------:|-------------------:|",
    ]
    for result in results:
        report_lines.append(
            f"| {result.pilot_id} | {result.split} | {result.width} | {result.height} | {result.visible_keypoints} |"
        )

    report_lines.extend(
        [
            "",
            "## Conversion appliquée",
            "",
            "1. Lecture JSON MVP (`landmarks[].x/y/v` en pixels).",
            "2. Ordre des 14 keypoints conservé : TD_R, TD_L, FHC_R, FHC_L, …, FSD_R, FSD_L.",
            "3. Normalisation YOLO : `x_norm = x / image_width`, `y_norm = y / image_height`.",
            "4. Visibilité : v=2 → visible ; v=0/null → (0, 0, 0).",
            "5. Bbox instance dérivée de l'enveloppe des keypoints visibles (+2 % marge).",
            "6. PNG 1:1 générées depuis DICOM (sources DICOM intactes).",
            "",
            "## Vérification des labels",
            "",
        ]
    )
    if all_label_issues:
        report_lines.append("**Problèmes détectés :**")
        report_lines.extend(f"- {issue}" for issue in all_label_issues)
    else:
        report_lines.append("- Tous les labels passent les contrôles de format, bornes et visibilité.")

    if anomaly_results:
        report_lines.extend(["", "## Anomalies par image", ""])
        for result in anomaly_results:
            report_lines.append(f"### {result.pilot_id}")
            for issue in result.issues:
                report_lines.append(f"- {issue}")

    report_lines.extend(
        [
            "",
            "## Fichiers produits",
            "",
            "- `dataset.yaml`",
            "- `images/train/`, `images/val/`",
            "- `labels/train/`, `labels/val/`",
            "- `meta/split.json`",
            "- `meta/source_mapping.csv`",
            "- `meta/keypoint_order.md`",
            "- `preparation_report.md`",
            "",
            "---",
            "*Aucune annotation source, DICOM ou schéma JSON modifié. Entraînement non lancé.*",
        ]
    )
    (OUTPUT_ROOT / "preparation_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"TRAIN={train_count} VAL={val_count} LABELS={len(results)}")
    print(f"OUTPUT={OUTPUT_ROOT}")
    print(f"ANOMALIES={len(anomaly_results)}")
    return 1 if anomaly_results else 0


if __name__ == "__main__":
    raise SystemExit(main())
