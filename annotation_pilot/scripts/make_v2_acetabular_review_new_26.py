#!/usr/bin/env python3
"""Contact sheet de revue acétabulaire — prédictions YOLO V2 vs annotations humaines.

Génère des overlays focalisés sur TD, FHC, ASL, ASM avec lignes VCE (FHC→ASL)
et sourcil (ASM→ASL). Lecture seule sur images, labels, JSON et poids.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mvp_geometry.yolo_adapter import KEYPOINTS_START, NKPT, landmarks_from_yolo_label  # noqa: E402

ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
GEOMETRY_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_geometry_results.csv"
OUTPUT_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_acetabular_review"
INDIVIDUAL_DIR = OUTPUT_ROOT / "individual"
CONTACT_SHEET_PATH = OUTPUT_ROOT / "contact_sheet_asl_asm.jpg"

FOCUS_LANDMARKS = (
    "TD_R", "TD_L",
    "FHC_R", "FHC_L",
    "ASL_R", "ASL_L",
    "ASM_R", "ASM_L",
)

V2_LINE_VCE_R = (255, 220, 60)
V2_LINE_VCE_L = (255, 80, 220)
V2_LINE_SOURCIL_R = (255, 160, 80)
V2_LINE_SOURCIL_L = (100, 200, 255)
V2_POINT_R = (255, 120, 40)
V2_POINT_L = (60, 180, 255)

GT_POINT = (80, 255, 120)
GT_LINE_VCE = (120, 255, 160)
GT_LINE_SOURCIL = (60, 220, 100)

BACKGROUND = (18, 22, 30)
HEADER_COLOR = (240, 240, 240)
SUBHEADER_COLOR = (180, 200, 220)

THUMB_MAX_WIDTH = 720
GRID_COLS = 3
PANEL_PAD = 16
HEADER_HEIGHT = 48
LEGEND_HEIGHT = 72


@dataclass
class PointRecord:
    x: float
    y: float
    confidence: float | None = None
    visible: bool = True


@dataclass
class CaseReview:
    case_id: str
    groups: list[str] = field(default_factory=list)
    vce_l: float | None = None
    tonnis_l: float | None = None
    asl_l_medial: bool = False


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["arialbd.ttf", "Arial Bold.ttf"] if bold else []
    ) + ["arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_geometry_table() -> dict[str, dict[str, str]]:
    with GEOMETRY_CSV.open("r", encoding="utf-8-sig", newline="") as stream:
        return {row["case_id"]: row for row in csv.DictReader(stream)}


def parse_v2_label_with_conf(label_path: Path) -> dict[str, PointRecord]:
    line = label_path.read_text(encoding="utf-8").strip()
    values = line.split()
    if len(values) not in {47, 48}:
        raise ValueError(f"Format YOLO inattendu ({label_path.name}) : {len(values)} colonnes.")

    from mvp_geometry.landmarks import MVP_LANDMARK_NAMES

    keypoint_values = [float(v) for v in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    if len(keypoint_values) != NKPT * 3:
        raise ValueError(f"Keypoints invalides ({label_path.name}).")

    records: dict[str, PointRecord] = {}
    for index, name in enumerate(MVP_LANDMARK_NAMES):
        x_norm = keypoint_values[index * 3]
        y_norm = keypoint_values[index * 3 + 1]
        conf = keypoint_values[index * 3 + 2]
        records[name] = PointRecord(x_norm, y_norm, conf, conf >= 0.25)
    return records


def load_gt_landmarks(case_id: str, width: int, height: int) -> dict[str, PointRecord]:
    path = ANNOT_DIR / f"{case_id}.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    records: dict[str, PointRecord] = {}
    for entry in data.get("landmarks", []):
        name = entry.get("name")
        if name not in FOCUS_LANDMARKS:
            continue
        v = entry.get("v")
        x, y = entry.get("x"), entry.get("y")
        visible = v == 2 and x is not None and y is not None
        if visible:
            records[name] = PointRecord(float(x), float(y), visible=True)
        else:
            records[name] = PointRecord(0.0, 0.0, visible=False)
    return records


def denorm_v2(record: PointRecord, width: int, height: int) -> tuple[float, float]:
    return record.x * width, record.y * height


def asl_l_is_medial(v2_px: dict[str, tuple[float, float]]) -> bool:
    if "FHC_L" not in v2_px or "ASL_L" not in v2_px:
        return False
    return v2_px["ASL_L"][0] < v2_px["FHC_L"][0]


def compute_groups(geometry: dict[str, dict[str, str]]) -> tuple[list[str], list[str], list[str]]:
    group1: list[str] = []
    vce_l_values: list[tuple[str, float]] = []
    tonnis_l_values: list[tuple[str, float]] = []

    for case_id in sorted(geometry):
        label_path = LABEL_DIR / f"{case_id}.txt"
        image_path = IMAGE_DIR / f"{case_id}.png"
        if not label_path.is_file() or not image_path.is_file():
            continue
        with Image.open(image_path) as img:
            width, height = img.size
        landmarks = landmarks_from_yolo_label(label_path, width, height)
        v2_px = {
            name: lm.point
            for name, lm in landmarks.items()
            if name in FOCUS_LANDMARKS and lm.point is not None
        }
        if asl_l_is_medial(v2_px):
            group1.append(case_id)

        row = geometry[case_id]
        if row.get("VCE_L"):
            vce_l_values.append((case_id, float(row["VCE_L"])))
        if row.get("Tonnis_L"):
            tonnis_l_values.append((case_id, float(row["Tonnis_L"])))

    group2 = [case_id for case_id, _ in sorted(vce_l_values, key=lambda item: item[1])[:5]]
    group3 = [
        case_id
        for case_id, _ in sorted(tonnis_l_values, key=lambda item: abs(item[1]), reverse=True)[:5]
    ]
    return group1, group2, group3


def ordered_unique_cases(
    group1: list[str], group2: list[str], group3: list[str]
) -> list[CaseReview]:
    tags: dict[str, set[str]] = {}
    for case_id in group1:
        tags.setdefault(case_id, set()).add("G1")
    for case_id in group2:
        tags.setdefault(case_id, set()).add("G2")
    for case_id in group3:
        tags.setdefault(case_id, set()).add("G3")

    geometry = load_geometry_table()
    reviews: list[CaseReview] = []
    for case_id in sorted(tags):
        row = geometry.get(case_id, {})
        v2_px = {}
        label_path = LABEL_DIR / f"{case_id}.txt"
        image_path = IMAGE_DIR / f"{case_id}.png"
        if label_path.is_file() and image_path.is_file():
            with Image.open(image_path) as img:
                w, h = img.size
            landmarks = landmarks_from_yolo_label(label_path, w, h)
            v2_px = {
                n: lm.point
                for n, lm in landmarks.items()
                if lm.point is not None
            }
        reviews.append(
            CaseReview(
                case_id=case_id,
                groups=sorted(tags[case_id], key=lambda g: (g[1], g)),
                vce_l=float(row["VCE_L"]) if row.get("VCE_L") else None,
                tonnis_l=float(row["Tonnis_L"]) if row.get("Tonnis_L") else None,
                asl_l_medial=asl_l_is_medial(v2_px),
            )
        )
    return reviews


def draw_text_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    *,
    color: tuple[int, int, int],
    font: ImageFont.ImageFont,
    bg: tuple[int, int, int] = (0, 0, 0),
) -> None:
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    pad = 2
    draw.rectangle(
        (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad),
        fill=bg,
    )
    draw.text((x, y), text, fill=color, font=font)


def draw_landmark(
    draw: ImageDraw.ImageDraw,
    point: tuple[float, float],
    name: str,
    *,
    color: tuple[int, int, int],
    font: ImageFont.ImageFont,
    prefix: str,
    confidence: float | None = None,
    radius: int = 8,
    dashed: bool = False,
) -> None:
    x, y = point
    if dashed:
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            outline=color,
            width=3,
        )
    else:
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=color,
            outline=(255, 255, 255),
            width=2,
        )
    conf_text = f" c={confidence:.2f}" if confidence is not None else ""
    label = f"{prefix}{name} ({x:.0f},{y:.0f}){conf_text}"
    draw_text_box(draw, (x + radius + 4, y - radius - 2), label, color=color, font=font)


def draw_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    color: tuple[int, int, int],
    width: int,
) -> None:
    draw.line([start, end], fill=color, width=width)


def render_case_panel(review: CaseReview, *, thumb_width: int | None = None) -> Image.Image:
    case_id = review.case_id
    image_path = IMAGE_DIR / f"{case_id}.png"
    label_path = LABEL_DIR / f"{case_id}.txt"

    with Image.open(image_path) as source:
        image = source.convert("RGB")
    width, height = image.size
    draw = ImageDraw.Draw(image)

    font_main = load_font(max(13, width // 200))
    font_title = load_font(max(18, width // 140), bold=True)

    v2_norm = parse_v2_label_with_conf(label_path)
    gt = load_gt_landmarks(case_id, width, height)

    v2_px: dict[str, tuple[float, float]] = {}
    v2_conf: dict[str, float] = {}
    for name in FOCUS_LANDMARKS:
        rec = v2_norm.get(name)
        if rec and rec.visible:
            v2_px[name] = denorm_v2(rec, width, height)
            v2_conf[name] = rec.confidence or 0.0

    gt_px: dict[str, tuple[float, float]] = {
        name: (rec.x, rec.y) for name, rec in gt.items() if rec.visible
    }

    line_w = max(3, width // 500)
    radius = max(7, width // 280)

    # GT lines (underneath)
    for side, vce_color, sour_color in (
        ("R", GT_LINE_VCE, GT_LINE_SOURCIL),
        ("L", GT_LINE_VCE, GT_LINE_SOURCIL),
    ):
        fhc, asl, asm = f"FHC_{side}", f"ASL_{side}", f"ASM_{side}"
        if fhc in gt_px and asl in gt_px:
            draw_line(draw, gt_px[fhc], gt_px[asl], vce_color, max(2, line_w - 1))
        if asm in gt_px and asl in gt_px:
            draw_line(draw, gt_px[asm], gt_px[asl], sour_color, max(2, line_w - 1))

    # V2 lines
    if "FHC_R" in v2_px and "ASL_R" in v2_px:
        draw_line(draw, v2_px["FHC_R"], v2_px["ASL_R"], V2_LINE_VCE_R, line_w)
    if "FHC_L" in v2_px and "ASL_L" in v2_px:
        draw_line(draw, v2_px["FHC_L"], v2_px["ASL_L"], V2_LINE_VCE_L, line_w)
    if "ASM_R" in v2_px and "ASL_R" in v2_px:
        draw_line(draw, v2_px["ASM_R"], v2_px["ASL_R"], V2_LINE_SOURCIL_R, line_w)
    if "ASM_L" in v2_px and "ASL_L" in v2_px:
        draw_line(draw, v2_px["ASM_L"], v2_px["ASL_L"], V2_LINE_SOURCIL_L, line_w)

    # TD line (reference ITH)
    if "TD_R" in v2_px and "TD_L" in v2_px:
        draw_line(draw, v2_px["TD_R"], v2_px["TD_L"], (180, 180, 180), max(2, line_w - 1))

    # GT landmarks
    for name, point in gt_px.items():
        color = GT_POINT
        draw_landmark(
            draw, point, name, color=color, font=font_main,
            prefix="GT ", radius=radius, dashed=True,
        )

    # V2 landmarks
    for name, point in v2_px.items():
        color = V2_POINT_R if name.endswith("_R") else V2_POINT_L
        draw_landmark(
            draw, point, name, color=color, font=font_main,
            prefix="V2 ", confidence=v2_conf.get(name), radius=radius,
        )

    groups_text = ",".join(review.groups)
    medial_flag = " ASL_L medial" if review.asl_l_medial else ""
    metrics = []
    if review.vce_l is not None:
        metrics.append(f"VCE_L={review.vce_l:.1f}")
    if review.tonnis_l is not None:
        metrics.append(f"Tonnis_L={review.tonnis_l:.1f}")
    title = f"{case_id}  [{groups_text}]  {' | '.join(metrics)}{medial_flag}"
    draw.rectangle((0, 0, width, font_title.size + 20), fill=(0, 0, 0))
    draw.text((10, 8), title, fill=(255, 255, 255), font=font_title)

    legend_lines = [
        "GT = annotation humaine (cercle creux vert)   |   V2 = prédiction YOLO V2 (plein orange R / bleu L)",
        "Jaune/rose V2 = FHC→ASL (VCE)   |   Sourcil V2 = ASM→ASL   |   Gris = TD_R→TD_L",
    ]
    lh = font_main.size + 6
    draw.rectangle((0, height - lh * 2 - 8, width, height), fill=(0, 0, 0))
    draw.text((10, height - lh * 2 - 2), legend_lines[0], fill=(220, 220, 220), font=font_main)
    draw.text((10, height - lh - 2), legend_lines[1], fill=(200, 200, 200), font=font_main)

    if thumb_width and image.width > thumb_width:
        ratio = thumb_width / image.width
        new_h = max(1, int(image.height * ratio))
        image = image.resize((thumb_width, new_h), Image.Resampling.LANCZOS)

    return image


def build_contact_sheet(panels: list[tuple[str, Image.Image]]) -> Image.Image:
    if not panels:
        raise RuntimeError("Aucun panneau à assembler.")

    font_header = load_font(28, bold=True)
    font_legend = load_font(20)

    col_width = max(img.width for _, img in panels) + PANEL_PAD
    row_height = max(img.height for _, img in panels) + PANEL_PAD + HEADER_HEIGHT

    rows = math.ceil(len(panels) / GRID_COLS)
    sheet_w = PANEL_PAD + GRID_COLS * col_width
    sheet_h = LEGEND_HEIGHT + PANEL_PAD + rows * row_height + PANEL_PAD

    canvas = Image.new("RGB", (sheet_w, sheet_h), BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    draw.text(
        (PANEL_PAD, 12),
        "Revues acétabulaires V2 — ASL / ASM / FHC / TD",
        fill=HEADER_COLOR,
        font=font_header,
    )
    draw.text(
        (PANEL_PAD, 42),
        "GT = annotation humaine   |   V2 = prédiction YOLO V2   |   G1=ASL_L médial   G2=pire VCE_L   G3=Tönnis_L extrême",
        fill=SUBHEADER_COLOR,
        font=font_legend,
    )

    y0 = LEGEND_HEIGHT + PANEL_PAD
    for index, (case_id, panel) in enumerate(panels):
        col = index % GRID_COLS
        row = index // GRID_COLS
        x = PANEL_PAD + col * col_width
        y = y0 + row * row_height
        draw.text((x, y), case_id, fill=HEADER_COLOR, font=font_legend)
        canvas.paste(panel, (x, y + HEADER_HEIGHT))
    return canvas


def main() -> int:
    geometry = load_geometry_table()
    group1, group2, group3 = compute_groups(geometry)
    reviews = ordered_unique_cases(group1, group2, group3)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    INDIVIDUAL_DIR.mkdir(parents=True, exist_ok=True)

    thumb_panels: list[tuple[str, Image.Image]] = []
    for review in reviews:
        full = render_case_panel(review, thumb_width=None)
        full_path = INDIVIDUAL_DIR / f"{review.case_id}_acetabular_review.png"
        full.save(full_path, format="PNG", optimize=True)

        thumb = render_case_panel(review, thumb_width=THUMB_MAX_WIDTH)
        thumb_panels.append((review.case_id, thumb))

    sheet = build_contact_sheet(thumb_panels)
    sheet.save(CONTACT_SHEET_PATH, format="JPEG", quality=90, optimize=True)

    print(f"OUTPUT_DIR={OUTPUT_ROOT.resolve()}")
    print(f"CONTACT_SHEET={CONTACT_SHEET_PATH.resolve()}")
    print(f"INDIVIDUAL={INDIVIDUAL_DIR.resolve()} ({len(reviews)} PNG)")
    print(f"GROUP1 = {len(group1)} cases")
    print(f"GROUP2 = {len(group2)} cases")
    print(f"GROUP3 = {len(group3)} cases")
    print(f"TOTAL UNIQUE = {len(reviews)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
