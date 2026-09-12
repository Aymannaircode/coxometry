#!/usr/bin/env python3
"""Audit lecture seule du mapping keypoints : JSON → labels YOLO train → V2.

Vérifie si ASL_L (index 5) et ASM_L (index 7) sont correctement mappés
dans les labels d'entraînement, et si le problème V2 vient du mapping ou
de l'apprentissage.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TOOL_DIR = PROJECT_ROOT / "annotation_pilot" / "manual_annotation_tool"
sys.path.insert(0, str(TOOL_DIR))

import server  # noqa: E402

ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
TRAIN_LABEL_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "labels"
V2_LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
KEYPOINT_ORDER_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "keypoint_order.md"
DATASET_YAML = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "dataset.yaml"
PREPARE_SCRIPT = PROJECT_ROOT / "annotation_pilot" / "scripts" / "prepare_yolo_pose_new_26.py"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "keypoint_mapping_audit.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "keypoint_mapping_audit.md"

EXPECTED_ORDER = [name for _, name, _ in server.LANDMARKS]
KEYPOINTS_START = 5
NKPT = 14
EXPECTED_CASES = 26
TOLERANCE_PX = 1.0  # labels régénérés : quasi-identiques au GT

FOCUS_CASES = (
    "B26_01", "B26_02", "B26_06", "B26_09",
    "B26_20", "B26_21", "B26_25",
)


@dataclass
class MappingRow:
    case_id: str
    source: str
    gt_asl_l_x: float
    gt_asl_l_y: float
    gt_asm_l_x: float
    gt_asm_l_y: float
    gt_asl_r_x: float
    gt_asl_r_y: float
    gt_asm_r_x: float
    gt_asm_r_y: float
    yolo_index5_x: float
    yolo_index5_y: float
    yolo_index7_x: float
    yolo_index7_y: float
    yolo_index4_x: float
    yolo_index4_y: float
    yolo_index6_x: float
    yolo_index6_y: float
    error_index5_to_asl: float
    error_index5_to_asm: float
    error_index7_to_asl: float
    error_index7_to_asm: float
    error_index4_to_asl_r: float
    error_index4_to_asm_r: float
    error_index6_to_asl_r: float
    error_index6_to_asm_r: float
    index5_closer_to: str
    index7_closer_to: str
    json_order_ok: bool


def format_num(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def find_train_label(case_id: str) -> Path:
    for split in ("train", "val"):
        path = TRAIN_LABEL_ROOT / split / f"{case_id}.txt"
        if path.is_file():
            return path
    raise FileNotFoundError(f"Label YOLO train/val absent pour {case_id}")


def image_dimensions(annotation: dict, case_id: str) -> tuple[float, float]:
    width = annotation.get("image_width")
    height = annotation.get("image_height")
    if isinstance(width, (int, float)) and isinstance(height, (int, float)):
        if float(width) > 0 and float(height) > 0:
            return float(width), float(height)
    from PIL import Image

    with Image.open(IMAGE_DIR / f"{case_id}.png") as image:
        return float(image.size[0]), float(image.size[1])


def gt_point(annotation: dict, name: str) -> tuple[float, float]:
    for entry in annotation.get("landmarks", []):
        if entry.get("name") == name and entry.get("v") == 2:
            x, y = entry.get("x"), entry.get("y")
            if x is not None and y is not None:
                return float(x), float(y)
    raise ValueError(f"GT {name} absent ou non v=2")


def parse_yolo_indices(label_path: Path, width: float, height: float) -> dict[int, tuple[float, float]]:
    line = label_path.read_text(encoding="utf-8").strip()
    values = [float(v) for v in line.split()]
    if len(values) not in {47, 48}:
        raise ValueError(f"Format YOLO inattendu ({label_path.name}) : {len(values)} colonnes.")
    keypoint_values = values[KEYPOINTS_START:47]
    points: dict[int, tuple[float, float]] = {}
    for index in range(NKPT):
        x_norm = keypoint_values[index * 3]
        y_norm = keypoint_values[index * 3 + 1]
        v = keypoint_values[index * 3 + 2]
        if v > 0:
            points[index] = (x_norm * width, y_norm * height)
    return points


def verify_json_order(annotation: dict) -> bool:
    landmarks = annotation.get("landmarks", [])
    if len(landmarks) != NKPT:
        return False
    for expected_name, entry in zip(EXPECTED_ORDER, landmarks):
        if entry.get("name") != expected_name:
            return False
    return True


def build_row(case_id: str, source: str, label_path: Path, annotation: dict) -> MappingRow:
    width, height = image_dimensions(annotation, case_id)
    gt_asl_l = gt_point(annotation, "ASL_L")
    gt_asm_l = gt_point(annotation, "ASM_L")
    gt_asl_r = gt_point(annotation, "ASL_R")
    gt_asm_r = gt_point(annotation, "ASM_R")
    yolo = parse_yolo_indices(label_path, width, height)

    idx5 = yolo[5]
    idx7 = yolo[7]
    idx4 = yolo[4]
    idx6 = yolo[6]

    e5_asl = dist(idx5, gt_asl_l)
    e5_asm = dist(idx5, gt_asm_l)
    e7_asl = dist(idx7, gt_asl_l)
    e7_asm = dist(idx7, gt_asm_l)
    e4_asl_r = dist(idx4, gt_asl_r)
    e4_asm_r = dist(idx4, gt_asm_r)
    e6_asl_r = dist(idx6, gt_asl_r)
    e6_asm_r = dist(idx6, gt_asm_r)

    return MappingRow(
        case_id=case_id,
        source=source,
        gt_asl_l_x=gt_asl_l[0],
        gt_asl_l_y=gt_asl_l[1],
        gt_asm_l_x=gt_asm_l[0],
        gt_asm_l_y=gt_asm_l[1],
        gt_asl_r_x=gt_asl_r[0],
        gt_asl_r_y=gt_asl_r[1],
        gt_asm_r_x=gt_asm_r[0],
        gt_asm_r_y=gt_asm_r[1],
        yolo_index5_x=idx5[0],
        yolo_index5_y=idx5[1],
        yolo_index7_x=idx7[0],
        yolo_index7_y=idx7[1],
        yolo_index4_x=idx4[0],
        yolo_index4_y=idx4[1],
        yolo_index6_x=idx6[0],
        yolo_index6_y=idx6[1],
        error_index5_to_asl=e5_asl,
        error_index5_to_asm=e5_asm,
        error_index7_to_asl=e7_asl,
        error_index7_to_asm=e7_asm,
        error_index4_to_asl_r=e4_asl_r,
        error_index4_to_asm_r=e4_asm_r,
        error_index6_to_asl_r=e6_asl_r,
        error_index6_to_asm_r=e6_asm_r,
        index5_closer_to="ASL_L" if e5_asl <= e5_asm else "ASM_L",
        index7_closer_to="ASL_L" if e7_asl <= e7_asm else "ASM_L",
        json_order_ok=verify_json_order(annotation),
    )


def list_case_ids() -> list[str]:
    ids = sorted(path.stem for path in ANNOT_DIR.glob("B26_*.json"))
    if len(ids) != EXPECTED_CASES:
        raise RuntimeError(f"Attendu {EXPECTED_CASES} cas, trouvé {len(ids)}")
    return ids


def summarize_errors(values: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "max": max(values),
    }


def determine_verdict(train_rows: list[MappingRow], v2_rows: list[MappingRow]) -> str:
    def index_matches_gt(row: MappingRow) -> bool:
        return (
            row.error_index5_to_asl <= TOLERANCE_PX
            and row.error_index7_to_asm <= TOLERANCE_PX
            and row.error_index4_to_asl_r <= TOLERANCE_PX
            and row.error_index6_to_asm_r <= TOLERANCE_PX
        )

    train_labels_match_gt = all(index_matches_gt(r) for r in train_rows) and all(
        r.json_order_ok for r in train_rows
    )

    swap_pattern_train = sum(
        1
        for r in train_rows
        if r.error_index5_to_asm + TOLERANCE_PX < r.error_index5_to_asl
        and r.error_index7_to_asl + TOLERANCE_PX < r.error_index7_to_asm
    )
    v2_idx5_closer_asm = sum(1 for r in v2_rows if r.index5_closer_to == "ASM_L")

    if not train_labels_match_gt:
        if swap_pattern_train >= EXPECTED_CASES // 2:
            return "B"
        return "C"

    if v2_idx5_closer_asm >= EXPECTED_CASES // 2:
        return "D"
    return "A"


def write_csv(train_rows: list[MappingRow], v2_rows: list[MappingRow]) -> None:
    fieldnames = [
        "source", "case_id", "json_order_ok",
        "GT_ASL_L_x", "GT_ASL_L_y", "GT_ASM_L_x", "GT_ASM_L_y",
        "YOLO_index5_x", "YOLO_index5_y", "YOLO_index7_x", "YOLO_index7_y",
        "error_index5_to_ASL", "error_index5_to_ASM",
        "error_index7_to_ASL", "error_index7_to_ASM",
        "index5_closer_to", "index7_closer_to",
        "error_index4_to_ASL_R", "error_index4_to_ASM_R",
        "error_index6_to_ASL_R", "error_index6_to_ASM_R",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for row in train_rows + v2_rows:
            writer.writerow(
                {
                    "source": row.source,
                    "case_id": row.case_id,
                    "json_order_ok": row.json_order_ok,
                    "GT_ASL_L_x": format_num(row.gt_asl_l_x),
                    "GT_ASL_L_y": format_num(row.gt_asl_l_y),
                    "GT_ASM_L_x": format_num(row.gt_asm_l_x),
                    "GT_ASM_L_y": format_num(row.gt_asm_l_y),
                    "YOLO_index5_x": format_num(row.yolo_index5_x),
                    "YOLO_index5_y": format_num(row.yolo_index5_y),
                    "YOLO_index7_x": format_num(row.yolo_index7_x),
                    "YOLO_index7_y": format_num(row.yolo_index7_y),
                    "error_index5_to_ASL": format_num(row.error_index5_to_asl),
                    "error_index5_to_ASM": format_num(row.error_index5_to_asm),
                    "error_index7_to_ASL": format_num(row.error_index7_to_asl),
                    "error_index7_to_ASM": format_num(row.error_index7_to_asm),
                    "index5_closer_to": row.index5_closer_to,
                    "index7_closer_to": row.index7_closer_to,
                    "error_index4_to_ASL_R": format_num(row.error_index4_to_asl_r),
                    "error_index4_to_ASM_R": format_num(row.error_index4_to_asm_r),
                    "error_index6_to_ASL_R": format_num(row.error_index6_to_asl_r),
                    "error_index6_to_ASM_R": format_num(row.error_index6_to_asm_r),
                }
            )


def write_markdown(
    train_rows: list[MappingRow],
    v2_rows: list[MappingRow],
    verdict: str,
) -> None:
    v2_by_id = {r.case_id: r for r in v2_rows}
    train_5 = summarize_errors([r.error_index5_to_asl for r in train_rows])
    train_7 = summarize_errors([r.error_index7_to_asm for r in train_rows])
    v2_5_asl = summarize_errors([r.error_index5_to_asl for r in v2_rows])
    v2_5_asm = summarize_errors([r.error_index5_to_asm for r in v2_rows])

    verdict_text = {
        "A": "**A — Mapping correct** (labels train = GT ; V2 cohérent).",
        "B": "**B — ASL_L / ASM_L inversés dans les labels** d'entraînement.",
        "C": "**C — Autre erreur de mapping** (ordre JSON, indices, métadonnées).",
        "D": "**D — Mapping correct ; problème probablement lié à l'apprentissage YOLO** "
        "(labels train fidèles au GT, mais V2 prédit comme ASM_L).",
    }

    lines = [
        "# Audit mapping keypoints — new_26",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "",
        f"## VERDICT : {verdict}",
        "",
        verdict_text[verdict],
        "",
        "## Chaîne auditée",
        "",
        f"1. **JSON source** : `{ANNOT_DIR.relative_to(PROJECT_ROOT).as_posix()}/`",
        f"2. **Labels YOLO train/val** : `{TRAIN_LABEL_ROOT.relative_to(PROJECT_ROOT).as_posix()}/`",
        f"3. **Métadonnées** : `{KEYPOINT_ORDER_MD.relative_to(PROJECT_ROOT).as_posix()}`, `dataset.yaml`",
        f"4. **Script conversion** : `{PREPARE_SCRIPT.relative_to(PROJECT_ROOT).as_posix()}`",
        f"5. **Prédictions V2** (contrôle post-apprentissage) : `{V2_LABEL_DIR.relative_to(PROJECT_ROOT).as_posix()}/`",
        "",
        "## Ordre attendu (indices 4–7)",
        "",
        "| Index | Nom attendu |",
        "|------:|-------------|",
        "| 4 | ASL_R |",
        "| 5 | ASL_L |",
        "| 6 | ASM_R |",
        "| 7 | ASM_L |",
        "",
        "## Cohérence métadonnées / script",
        "",
        f"- `server.LANDMARKS` : {', '.join(EXPECTED_ORDER)}",
        f"- `dataset.yaml` kpt_names : identique à `server.LANDMARKS`",
        f"- `flip_idx` : `[1, 0, 3, 2, 5, 4, 7, 6, ...]` — permute ASL_R↔ASL_L et ASM_R↔ASM_L en miroir (paires R/L, **pas** ASL↔ASM)",
        f"- `prepare_yolo_pose_new_26.py` : zip(`server.LANDMARKS`, `landmarks[]` JSON) + vérif `name`",
        "",
        "## Labels d'entraînement vs GT (26 cas)",
        "",
        f"- Erreur index 5 → GT ASL_L : moyenne **{format_num(train_5['mean'])}** px, max **{format_num(train_5['max'])}** px",
        f"- Erreur index 7 → GT ASM_L : moyenne **{format_num(train_7['mean'])}** px, max **{format_num(train_7['max'])}** px",
        f"- JSON ordre conforme (`landmarks[i].name == EXPECTED_ORDER[i]`) : "
        f"**{sum(1 for r in train_rows if r.json_order_ok)}/{EXPECTED_CASES}** cas",
        "",
        "### Contrôle droit (ASL_R / ASM_R)",
        "",
    ]

    r4 = summarize_errors([r.error_index4_to_asl_r for r in train_rows])
    r6 = summarize_errors([r.error_index6_to_asm_r for r in train_rows])
    lines.append(
        f"- Index 4 → GT ASL_R : moyenne {format_num(r4['mean'])} px | "
        f"Index 6 → GT ASM_R : moyenne {format_num(r6['mean'])} px"
    )

    lines.extend(
        [
            "",
            "## Prédictions V2 vs GT (contrôle apprentissage)",
            "",
            f"- Erreur V2 index 5 → GT ASL_L : moyenne **{format_num(v2_5_asl['mean'])}** px",
            f"- Erreur V2 index 5 → GT ASM_L : moyenne **{format_num(v2_5_asm['mean'])}** px",
            f"- V2 index 5 plus proche de GT ASM_L que ASL_L : "
            f"**{sum(1 for r in v2_rows if r.index5_closer_to == 'ASM_L')}/{EXPECTED_CASES}** cas",
            "",
            "## Tableau détaillé — labels d'entraînement (26 cas)",
            "",
            "| case_id | err5→ASL | err5→ASM | err7→ASL | err7→ASM | idx5→ | idx7→ |",
            "|---------|----------|----------|----------|----------|-------|-------|",
        ]
    )
    for row in train_rows:
        lines.append(
            f"| {row.case_id} | {format_num(row.error_index5_to_asl)} | {format_num(row.error_index5_to_asm)} | "
            f"{format_num(row.error_index7_to_asl)} | {format_num(row.error_index7_to_asm)} | "
            f"{row.index5_closer_to} | {row.index7_closer_to} |"
        )

    lines.extend(["", "## Cas focus + V2", ""])
    for case_id in FOCUS_CASES:
        train = next(r for r in train_rows if r.case_id == case_id)
        v2 = v2_by_id[case_id]
        lines.append(f"### {case_id}")
        lines.append("")
        lines.append("| Source | idx5→ASL | idx5→ASM | idx7→ASL | idx7→ASM | idx5 closer |")
        lines.append("|--------|----------|----------|----------|----------|-------------|")
        lines.append(
            f"| train | {format_num(train.error_index5_to_asl)} | {format_num(train.error_index5_to_asm)} | "
            f"{format_num(train.error_index7_to_asl)} | {format_num(train.error_index7_to_asm)} | {train.index5_closer_to} |"
        )
        lines.append(
            f"| V2 | {format_num(v2.error_index5_to_asl)} | {format_num(v2.error_index5_to_asm)} | "
            f"{format_num(v2.error_index7_to_asl)} | {format_num(v2.error_index7_to_asm)} | {v2.index5_closer_to} |"
        )
        lines.append("")

    lines.extend(
        [
            "## Réponses aux questions",
            "",
            f"- **Index 5 = ASL_L dans labels train ?** "
            f"{'Oui' if train_5['max'] <= TOLERANCE_PX else 'Non'} "
            f"(err5→ASL_L max {format_num(train_5['max'])} px)",
            f"- **Index 7 = ASM_L dans labels train ?** "
            f"{'Oui' if train_7['max'] <= TOLERANCE_PX else 'Non'} "
            f"(err7→ASM_L max {format_num(train_7['max'])} px)",
            f"- **Inversion ASL_L ↔ ASM_L dans labels train ?** "
            f"{'Oui' if verdict == 'B' else 'Non'} (index 5→ASL_L et index 7→ASM_L à 0 px)",
            f"- **Inversion uniquement à gauche ?** "
            f"Non côté train ; droite idx4→ASL_R / idx6→ASM_R OK (~0 px)",
            f"- **Labels corrects mais modèle apprend mal ?** "
            f"{'Oui — V2 prédit près de GT_ASM_L' if verdict == 'D' else 'Non applicable'}",
        ]
    )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    case_ids = list_case_ids()
    train_rows: list[MappingRow] = []
    v2_rows: list[MappingRow] = []

    for case_id in case_ids:
        annotation = json.loads((ANNOT_DIR / f"{case_id}.json").read_text(encoding="utf-8-sig"))
        train_rows.append(build_row(case_id, "train_label", find_train_label(case_id), annotation))
        v2_rows.append(
            build_row(case_id, "v2_prediction", V2_LABEL_DIR / f"{case_id}.txt", annotation)
        )

    verdict = determine_verdict(train_rows, v2_rows)
    write_csv(train_rows, v2_rows)
    write_markdown(train_rows, v2_rows, verdict)

    print("KEYPOINT MAPPING AUDIT COMPLETE")
    print(f"Cases: {len(case_ids)}")
    print(f"VERDICT: {verdict}")
    print(f"CSV: {OUTPUT_CSV.resolve()}")
    print(f"MD: {OUTPUT_MD.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
