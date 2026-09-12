#!/usr/bin/env python3
"""Overlays visuels — validation refinement ASL_L C_asm_offset (new_26).

Génère contact sheets et images individuelles. Lecture seule sur toutes les sources.
Offset calibré sur 21 TRAIN GT — appliqué identiquement aux 26 cas.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mvp_geometry.landmarks import landmarks_by_name, load_pilot_schema  # noqa: E402
from mvp_geometry.yolo_adapter import KEYPOINTS_START, NKPT, MVP_LANDMARK_NAMES  # noqa: E402

ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
SPLIT_JSON = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "split.json"
LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
OUTPUT_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "asl_l_refinement_review"
INDIVIDUAL_DIR = OUTPUT_ROOT / "individual"
CONTACT_ALL = OUTPUT_ROOT / "contact_sheet_all_26.jpg"
CONTACT_VAL = OUTPUT_ROOT / "contact_sheet_val_5.jpg"
REVIEW_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "asl_l_refinement_visual_review.csv"

MIN_CONF = 0.25
CROP_RADIUS = 420
PANEL_SIZE = 520
HEADER_H = 72
LEGEND_H = 56

COLOR_GT_ASL = (80, 255, 120)
COLOR_V2_ASL = (255, 60, 60)
COLOR_REF_ASL = (60, 140, 255)
COLOR_ASM = (255, 160, 40)
COLOR_FHC = (200, 80, 255)
COLOR_GT_LINE = (100, 220, 140)
COLOR_REF_LINE = (80, 160, 255)
COLOR_TEXT = (235, 235, 235)
COLOR_VAL_BADGE = (255, 200, 80)
COLOR_TRAIN_BADGE = (140, 200, 255)
BG_CANVAS = (16, 20, 28)


@dataclass
class CaseOverlay:
    case_id: str
    split: str
    width: int
    height: int
    gt_asm: tuple[float, float]
    gt_asl: tuple[float, float]
    gt_fhc: tuple[float, float]
    v2_asm: tuple[float, float]
    v2_asl: tuple[float, float]
    v2_fhc: tuple[float, float]
    v2_asm_conf: float
    v2_asl_conf: float
    ref_asl: tuple[float, float]
    v2_error_px: float
    ref_error_px: float
    improvement_pct: float
    panel: Image.Image


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (["arialbd.ttf", "Arial Bold.ttf"] if bold else []) + [
        "arial.ttf", "Arial.ttf", "DejaVuSans.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def load_split() -> tuple[set[str], set[str]]:
    data = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))
    return set(data["train"]), set(data["val"])


def calibrate_train_offset(train_ids: list[str]) -> tuple[float, float]:
    offsets = []
    for case_id in train_ids:
        gt = landmarks_by_name(load_pilot_schema(ANNOT_DIR / f"{case_id}.json"))
        asm, asl = gt["ASM_L"], gt["ASL_L"]
        if not asm.usable or not asl.usable:
            raise ValueError(f"{case_id} : GT ASM_L/ASL_L manquant.")
        offsets.append((float(asl.x) - float(asm.x), float(asl.y) - float(asm.y)))
    return statistics.mean(o[0] for o in offsets), statistics.mean(o[1] for o in offsets)


def parse_v2_kpts(label_path: Path) -> dict[str, tuple[float, float, float]]:
    values = label_path.read_text(encoding="utf-8").strip().split()
    kpts = [float(v) for v in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    out: dict[str, tuple[float, float, float]] = {}
    for i, name in enumerate(MVP_LANDMARK_NAMES):
        out[name] = (kpts[i * 3], kpts[i * 3 + 1], kpts[i * 3 + 2])
    return out


def gt_xy(case_id: str, name: str) -> tuple[float, float]:
    gt = landmarks_by_name(load_pilot_schema(ANNOT_DIR / f"{case_id}.json"))
    lm = gt[name]
    if not lm.usable or lm.x is None or lm.y is None:
        raise ValueError(f"{case_id} GT {name} absent.")
    return float(lm.x), float(lm.y)


def draw_marker(draw: ImageDraw.ImageDraw, pt: tuple[float, float], color: tuple[int, int, int], *, circle: bool = False, r: int = 7) -> None:
    x, y = pt
    if circle:
        draw.ellipse((x - r, y - r, x + r, y + r), outline=color, width=3)
    else:
        draw.rectangle((x - r, y - r, x + r, y + r), fill=color, outline=(255, 255, 255), width=1)


def render_panel(case: CaseOverlay) -> Image.Image:
    with Image.open(IMAGE_DIR / f"{case.case_id}.png") as src:
        img = src.convert("RGB")

    cx = (case.gt_asl[0] + case.v2_asl[0] + case.ref_asl[0]) / 3
    cy = (case.gt_asl[1] + case.v2_asl[1] + case.ref_asl[1]) / 3
    left = max(0, int(cx - CROP_RADIUS))
    top = max(0, int(cy - CROP_RADIUS))
    right = min(img.width, int(cx + CROP_RADIUS))
    bottom = min(img.height, int(cy + CROP_RADIUS))
    crop = img.crop((left, top, right, bottom))

    scale = PANEL_SIZE / max(crop.width, crop.height, 1)
    new_w = max(1, int(crop.width * scale))
    new_h = max(1, int(crop.height * scale))
    crop = crop.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (PANEL_SIZE, PANEL_SIZE + HEADER_H), BG_CANVAS)
    ox = (PANEL_SIZE - new_w) // 2
    oy = HEADER_H + (PANEL_SIZE - new_h) // 2
    canvas.paste(crop, (ox, oy))

    def to_panel(pt: tuple[float, float]) -> tuple[float, float]:
        return (ox + (pt[0] - left) * scale, oy + (pt[1] - top) * scale)

    draw = ImageDraw.Draw(canvas)
    font = load_font(13)
    font_sm = load_font(11)
    font_b = load_font(14, bold=True)

    gt_asm_p = to_panel(case.gt_asm)
    gt_asl_p = to_panel(case.gt_asl)
    v2_asm_p = to_panel(case.v2_asm)
    v2_asl_p = to_panel(case.v2_asl)
    ref_asl_p = to_panel(case.ref_asl)
    fhc_p = to_panel(case.v2_fhc)

    draw.line([gt_asm_p, gt_asl_p], fill=COLOR_GT_LINE, width=2)
    draw.line([v2_asm_p, ref_asl_p], fill=COLOR_REF_LINE, width=2)

    draw_marker(draw, fhc_p, COLOR_FHC, r=6)
    draw_marker(draw, v2_asm_p, COLOR_ASM, r=6)
    draw_marker(draw, gt_asl_p, COLOR_GT_ASL, circle=True, r=9)
    draw_marker(draw, v2_asl_p, COLOR_V2_ASL, r=7)
    draw_marker(draw, ref_asl_p, COLOR_REF_ASL, r=7)

    badge_color = COLOR_VAL_BADGE if case.split == "val" else COLOR_TRAIN_BADGE
    draw.rectangle((8, 8, 88, 28), fill=badge_color)
    draw.text((14, 10), case.split.upper(), fill=(20, 20, 20), font=font_b)
    draw.text((96, 10), case.case_id, fill=COLOR_TEXT, font=font_b)
    draw.text(
        (8, 32),
        f"V2 err={case.v2_error_px:.0f}px  Ref={case.ref_error_px:.0f}px  "
        f"Δ={case.improvement_pct:.1f}%",
        fill=COLOR_TEXT,
        font=font,
    )

    info_y = PANEL_SIZE + HEADER_H - 52
    draw.text(
        (8, info_y),
        f"GT_ASL ({case.gt_asl[0]:.0f},{case.gt_asl[1]:.0f})  "
        f"V2_ASL ({case.v2_asl[0]:.0f},{case.v2_asl[1]:.0f}) c={case.v2_asl_conf:.2f}",
        fill=COLOR_TEXT,
        font=font_sm,
    )
    draw.text(
        (8, info_y + 14),
        f"Ref_ASL ({case.ref_asl[0]:.0f},{case.ref_asl[1]:.0f})  "
        f"ASM ({case.v2_asm[0]:.0f},{case.v2_asm[1]:.0f}) c={case.v2_asm_conf:.2f}  "
        f"FHC ({case.v2_fhc[0]:.0f},{case.v2_fhc[1]:.0f})",
        fill=COLOR_TEXT,
        font=font_sm,
    )

    legend = "vert=GT_ASL  rouge=V2  bleu=refined  orange=ASM  violet=FHC"
    draw.text((8, PANEL_SIZE + HEADER_H - 18), legend, fill=(160, 170, 180), font=font_sm)
    return canvas


def build_case(case_id: str, split: str, off_x: float, off_y: float) -> CaseOverlay:
    with Image.open(IMAGE_DIR / f"{case_id}.png") as img:
        w, h = img.size

    kpts = parse_v2_kpts(LABEL_DIR / f"{case_id}.txt")
    for name in ("ASM_L", "ASL_L", "FHC_L"):
        if kpts[name][2] < MIN_CONF:
            raise ValueError(f"{case_id} : V2 {name} conf insuffisante.")

    v2_asm = (kpts["ASM_L"][0] * w, kpts["ASM_L"][1] * h)
    v2_asl = (kpts["ASL_L"][0] * w, kpts["ASL_L"][1] * h)
    v2_fhc = (kpts["FHC_L"][0] * w, kpts["FHC_L"][1] * h)
    ref_asl = (v2_asm[0] + off_x, v2_asm[1] + off_y)

    gt_asm = gt_xy(case_id, "ASM_L")
    gt_asl = gt_xy(case_id, "ASL_L")
    gt_fhc = gt_xy(case_id, "FHC_L")

    v2_err = dist(v2_asl, gt_asl)
    ref_err = dist(ref_asl, gt_asl)
    imp_pct = (1 - ref_err / v2_err) * 100 if v2_err > 0 else 0.0

    case = CaseOverlay(
        case_id=case_id,
        split=split,
        width=w,
        height=h,
        gt_asm=gt_asm,
        gt_asl=gt_asl,
        gt_fhc=gt_fhc,
        v2_asm=v2_asm,
        v2_asl=v2_asl,
        v2_fhc=v2_fhc,
        v2_asm_conf=kpts["ASM_L"][2],
        v2_asl_conf=kpts["ASL_L"][2],
        ref_asl=ref_asl,
        v2_error_px=v2_err,
        ref_error_px=ref_err,
        improvement_pct=imp_pct,
        panel=Image.new("RGB", (1, 1)),
    )
    case.panel = render_panel(case)
    return case


def compose_contact_sheet(cases: list[CaseOverlay], cols: int, out_path: Path, title: str) -> None:
    if not cases:
        return
    panel_w = cases[0].panel.width
    panel_h = cases[0].panel.height
    rows = math.ceil(len(cases) / cols)
    pad = 12
    title_h = 36
    canvas_w = pad + cols * (panel_w + pad)
    canvas_h = pad + title_h + rows * (panel_h + pad) + LEGEND_H
    canvas = Image.new("RGB", (canvas_w, canvas_h), BG_CANVAS)
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, pad), title, fill=COLOR_TEXT, font=load_font(18, bold=True))

    for idx, case in enumerate(sorted(cases, key=lambda c: c.case_id)):
        col = idx % cols
        row = idx // cols
        x = pad + col * (panel_w + pad)
        y = pad + title_h + row * (panel_h + pad)
        canvas.paste(case.panel, (x, y))

    draw.text(
        (pad, canvas_h - LEGEND_H + 8),
        "Offset C_asm_offset calibré sur 21 TRAIN — identique pour TRAIN et VAL | "
        "ligne verte=GT sourcil | ligne bleue=refined sourcil",
        fill=(170, 180, 190),
        font=load_font(12),
    )
    canvas.save(out_path, format="JPEG", quality=92, optimize=True)


def write_csv(cases: list[CaseOverlay]) -> None:
    fieldnames = [
        "case_id", "split",
        "v2_asl_l_x", "v2_asl_l_y",
        "refined_asl_l_x", "refined_asl_l_y",
        "gt_asl_l_x", "gt_asl_l_y",
        "v2_error_px", "refined_error_px", "improvement_pct",
    ]
    with REVIEW_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for c in sorted(cases, key=lambda x: x.case_id):
            writer.writerow(
                {
                    "case_id": c.case_id,
                    "split": c.split,
                    "v2_asl_l_x": f"{c.v2_asl[0]:.2f}",
                    "v2_asl_l_y": f"{c.v2_asl[1]:.2f}",
                    "refined_asl_l_x": f"{c.ref_asl[0]:.2f}",
                    "refined_asl_l_y": f"{c.ref_asl[1]:.2f}",
                    "gt_asl_l_x": f"{c.gt_asl[0]:.2f}",
                    "gt_asl_l_y": f"{c.gt_asl[1]:.2f}",
                    "v2_error_px": f"{c.v2_error_px:.2f}",
                    "refined_error_px": f"{c.ref_error_px:.2f}",
                    "improvement_pct": f"{c.improvement_pct:.2f}",
                }
            )


def main() -> int:
    train_ids_set, val_ids_set = load_split()
    train_ids = sorted(train_ids_set)
    val_ids = sorted(val_ids_set)
    all_ids = sorted(train_ids + val_ids)

    off_x, off_y = calibrate_train_offset(train_ids)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    INDIVIDUAL_DIR.mkdir(parents=True, exist_ok=True)

    cases: list[CaseOverlay] = []
    for case_id in all_ids:
        split = "val" if case_id in val_ids_set else "train"
        case = build_case(case_id, split, off_x, off_y)
        cases.append(case)
        case.panel.save(INDIVIDUAL_DIR / f"{case_id}.jpg", format="JPEG", quality=92, optimize=True)

    compose_contact_sheet(cases, cols=4, out_path=CONTACT_ALL, title="ASL_L refinement review — 26 cas (offset TRAIN)")
    val_cases = [c for c in cases if c.split == "val"]
    compose_contact_sheet(val_cases, cols=3, out_path=CONTACT_VAL, title="ASL_L refinement review — 5 VAL (offset TRAIN)")

    write_csv(cases)

    print("ASL_L REFINEMENT VISUAL REVIEW COMPLETE")
    print(f"Cases: {len(cases)}")
    print(f"Validation cases: {len(val_cases)}")
    print(f"Offset TRAIN: ({off_x:.2f}, {off_y:.2f}) px")
    print(f"OUTPUT={OUTPUT_ROOT.resolve()}")
    print(f"CSV={REVIEW_CSV.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
