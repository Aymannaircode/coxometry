#!/usr/bin/env python3
"""Diagnostic ciblé ASL_L — biais systématique et confusion landmark (new_26).

Compare GT vs prédiction V2 pour ASL_L sur 26 cas. Lecture seule.
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

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
OUTPUT_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"
OUTPUT_CSV = OUTPUT_DIR / "asl_l_error_analysis.csv"
OUTPUT_MD = OUTPUT_DIR / "asl_l_error_analysis.md"
SCATTER_DX_DY = OUTPUT_DIR / "asl_l_scatter_dx_dy.png"
SCATTER_GT_PRED = OUTPUT_DIR / "asl_l_scatter_gt_vs_pred_norm.png"
CONTACT_SHEET = OUTPUT_DIR / "asl_l_contact_sheet.jpg"

LANDMARK_NAMES = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L",
    "ASM_R", "ASM_L", "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L",
]
ASL_L_INDEX = LANDMARK_NAMES.index("ASL_L")
KEYPOINTS_START = 5
MIN_KEYPOINT_CONF = 0.25
EXPECTED_CASES = 26

GT_COLOR = (80, 255, 120)
V2_COLOR = (255, 100, 180)
ERROR_COLOR = (255, 220, 80)
REF_COLORS = {
    "GT_ASM_L": (100, 200, 255),
    "GT_FHC_L": (255, 180, 80),
    "GT_ASL_R": (200, 200, 200),
}


@dataclass
class AslLCase:
    case_id: str
    image_width: float
    image_height: float
    gt_x: float
    gt_y: float
    pred_x: float
    pred_y: float
    confidence: float
    gt_x_norm: float
    gt_y_norm: float
    pred_x_norm: float
    pred_y_norm: float
    dx: float
    dy: float
    error_px: float
    dist_to_gt_asm_l: float
    dist_to_gt_fhc_l: float
    dist_to_gt_asl_r: float
    dist_v2_to_v2_asm_l: float | None
    dist_v2_to_v2_fhc_l: float | None
    dist_v2_to_v2_asl_r: float | None
    nearest_gt_reference: str
    pred_closer_to_gt_asm_than_gt_asl: bool
    pred_medial_to_gt_fhc: bool
    edge_margin_px: float


def format_num(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def image_dimensions(annotation: dict, case_id: str) -> tuple[float, float]:
    width = annotation.get("image_width")
    height = annotation.get("image_height")
    if isinstance(width, (int, float)) and isinstance(height, (int, float)):
        if float(width) > 0 and float(height) > 0:
            return float(width), float(height)
    with Image.open(IMAGE_DIR / f"{case_id}.png") as image:
        return float(image.size[0]), float(image.size[1])


def gt_point(annotation: dict, name: str) -> tuple[float, float] | None:
    for entry in annotation.get("landmarks", []):
        if entry.get("name") != name or entry.get("v") != 2:
            continue
        x, y = entry.get("x"), entry.get("y")
        if x is None or y is None:
            return None
        return float(x), float(y)
    return None


def parse_asl_l_v2(label_path: Path, width: float, height: float) -> tuple[float, float, float] | None:
    line = label_path.read_text(encoding="utf-8").strip()
    values = line.split()
    if len(values) not in {47, 48}:
        raise ValueError(f"Format YOLO inattendu ({label_path.name}).")
    keypoint_values = [float(v) for v in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    base = ASL_L_INDEX * 3
    x_norm, y_norm, conf = keypoint_values[base], keypoint_values[base + 1], keypoint_values[base + 2]
    if conf < MIN_KEYPOINT_CONF:
        return None
    return x_norm * width, y_norm * height, conf


def parse_v2_all(label_path: Path, width: float, height: float) -> dict[str, tuple[float, float] | None]:
    line = label_path.read_text(encoding="utf-8").strip()
    values = line.split()
    keypoint_values = [float(v) for v in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    points: dict[str, tuple[float, float] | None] = {}
    for index, name in enumerate(LANDMARK_NAMES):
        x_norm = keypoint_values[index * 3]
        y_norm = keypoint_values[index * 3 + 1]
        conf = keypoint_values[index * 3 + 2]
        points[name] = (x_norm * width, y_norm * height) if conf >= MIN_KEYPOINT_CONF else None
    return points


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def edge_margin(x: float, y: float, width: float, height: float) -> float:
    return min(x, y, width - x, height - y)


def build_cases(case_ids: list[str]) -> list[AslLCase]:
    rows: list[AslLCase] = []
    for case_id in case_ids:
        annotation = json.loads((ANNOT_DIR / f"{case_id}.json").read_text(encoding="utf-8-sig"))
        width, height = image_dimensions(annotation, case_id)
        gt = gt_point(annotation, "ASL_L")
        if gt is None:
            raise ValueError(f"GT ASL_L absent pour {case_id}")
        parsed = parse_asl_l_v2(LABEL_DIR / f"{case_id}.txt", width, height)
        if parsed is None:
            raise ValueError(f"Prédiction V2 ASL_L absente pour {case_id}")
        pred_x, pred_y, conf = parsed
        gt_x, gt_y = gt
        v2_all = parse_v2_all(LABEL_DIR / f"{case_id}.txt", width, height)
        pred_pt = (pred_x, pred_y)

        gt_asm = gt_point(annotation, "ASM_L")
        gt_fhc = gt_point(annotation, "FHC_L")
        gt_asl_r = gt_point(annotation, "ASL_R")
        if gt_asm is None or gt_fhc is None or gt_asl_r is None:
            raise ValueError(f"GT de référence manquant pour {case_id}")

        ref_dists = {
            "GT_ASM_L": dist(pred_pt, gt_asm),
            "GT_FHC_L": dist(pred_pt, gt_fhc),
            "GT_ASL_R": dist(pred_pt, gt_asl_r),
        }
        nearest_ref = min(ref_dists, key=ref_dists.get)

        dx = pred_x - gt_x
        dy = pred_y - gt_y
        error_px = math.hypot(dx, dy)

        rows.append(
            AslLCase(
                case_id=case_id,
                image_width=width,
                image_height=height,
                gt_x=gt_x,
                gt_y=gt_y,
                pred_x=pred_x,
                pred_y=pred_y,
                confidence=conf,
                gt_x_norm=gt_x / width,
                gt_y_norm=gt_y / height,
                pred_x_norm=pred_x / width,
                pred_y_norm=pred_y / height,
                dx=dx,
                dy=dy,
                error_px=error_px,
                dist_to_gt_asm_l=ref_dists["GT_ASM_L"],
                dist_to_gt_fhc_l=ref_dists["GT_FHC_L"],
                dist_to_gt_asl_r=ref_dists["GT_ASL_R"],
                dist_v2_to_v2_asm_l=dist(pred_pt, v2_all["ASM_L"]) if v2_all.get("ASM_L") else None,
                dist_v2_to_v2_fhc_l=dist(pred_pt, v2_all["FHC_L"]) if v2_all.get("FHC_L") else None,
                dist_v2_to_v2_asl_r=dist(pred_pt, v2_all["ASL_R"]) if v2_all.get("ASL_R") else None,
                nearest_gt_reference=nearest_ref,
                pred_closer_to_gt_asm_than_gt_asl=ref_dists["GT_ASM_L"] < error_px,
                pred_medial_to_gt_fhc=pred_x < gt_fhc[0],
                edge_margin_px=edge_margin(pred_x, pred_y, width, height),
            )
        )
    return rows


def summarize(values: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values) if len(values) >= 2 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def write_csv(cases: list[AslLCase]) -> None:
    fieldnames = [
        "case_id", "image_width", "image_height",
        "gt_x", "gt_y", "pred_x", "pred_y", "confidence",
        "gt_x_norm", "gt_y_norm", "pred_x_norm", "pred_y_norm",
        "dx", "dy", "error_px",
        "dist_to_gt_asm_l", "dist_to_gt_fhc_l", "dist_to_gt_asl_r",
        "dist_v2_asl_l_to_v2_asm_l", "dist_v2_asl_l_to_v2_fhc_l", "dist_v2_asl_l_to_v2_asl_r",
        "nearest_gt_reference", "pred_closer_to_gt_asm_than_gt_asl", "pred_medial_to_gt_fhc",
        "edge_margin_px",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for row in cases:
            writer.writerow(
                {
                    "case_id": row.case_id,
                    "image_width": format_num(row.image_width),
                    "image_height": format_num(row.image_height),
                    "gt_x": format_num(row.gt_x),
                    "gt_y": format_num(row.gt_y),
                    "pred_x": format_num(row.pred_x),
                    "pred_y": format_num(row.pred_y),
                    "confidence": format_num(row.confidence, 4),
                    "gt_x_norm": format_num(row.gt_x_norm, 4),
                    "gt_y_norm": format_num(row.gt_y_norm, 4),
                    "pred_x_norm": format_num(row.pred_x_norm, 4),
                    "pred_y_norm": format_num(row.pred_y_norm, 4),
                    "dx": format_num(row.dx),
                    "dy": format_num(row.dy),
                    "error_px": format_num(row.error_px),
                    "dist_to_gt_asm_l": format_num(row.dist_to_gt_asm_l),
                    "dist_to_gt_fhc_l": format_num(row.dist_to_gt_fhc_l),
                    "dist_to_gt_asl_r": format_num(row.dist_to_gt_asl_r),
                    "dist_v2_asl_l_to_v2_asm_l": format_num(row.dist_v2_to_v2_asm_l),
                    "dist_v2_asl_l_to_v2_fhc_l": format_num(row.dist_v2_to_v2_fhc_l),
                    "dist_v2_asl_l_to_v2_asl_r": format_num(row.dist_v2_to_v2_asl_r),
                    "nearest_gt_reference": row.nearest_gt_reference,
                    "pred_closer_to_gt_asm_than_gt_asl": row.pred_closer_to_gt_asm_than_gt_asl,
                    "pred_medial_to_gt_fhc": row.pred_medial_to_gt_fhc,
                    "edge_margin_px": format_num(row.edge_margin_px),
                }
            )


def bias_diagnosis(cases: list[AslLCase], dx_s: dict, dy_s: dict) -> list[str]:
    lines: list[str] = []
    n = len(cases)

    dx_neg = sum(1 for c in cases if c.dx < 0)
    dx_pos = sum(1 for c in cases if c.dx > 0)
    dy_neg = sum(1 for c in cases if c.dy < 0)
    dy_pos = sum(1 for c in cases if c.dy > 0)

    lines.append(
        f"- **Décalage horizontal (dx = pred − GT)** : moyenne {format_num(dx_s['mean'])} px, "
        f"médiane {format_num(dx_s['median'])} px. "
        f"dx < 0 (prédiction à **gauche** de GT / plus médial) : **{dx_neg}/{n}** cas ; "
        f"dx > 0 : **{dx_pos}/{n}** cas."
    )
    lines.append(
        f"- **Décalage vertical (dy = pred − GT)** : moyenne {format_num(dy_s['mean'])} px, "
        f"médiane {format_num(dy_s['median'])} px. "
        f"dy < 0 (prédiction **au-dessus** de GT) : **{dy_neg}/{n}** cas ; "
        f"dy > 0 (en dessous) : **{dy_pos}/{n}** cas."
    )

    nearest_counts: dict[str, int] = {}
    for case in cases:
        nearest_counts[case.nearest_gt_reference] = nearest_counts.get(case.nearest_gt_reference, 0) + 1
    lines.append("- **Landmark GT le plus proche de V2 ASL_L** :")
    for name, count in sorted(nearest_counts.items(), key=lambda item: -item[1]):
        lines.append(f"  - {name} : **{count}/{n}** cas")

    closer_asm = sum(1 for c in cases if c.pred_closer_to_gt_asm_than_gt_asl)
    medial_fhc = sum(1 for c in cases if c.pred_medial_to_gt_fhc)
    lines.append(
        f"- **V2 ASL_L plus proche de GT_ASM_L que de GT_ASL_L** (confusion ASM) : **{closer_asm}/{n}** cas."
    )
    lines.append(
        f"- **V2 ASL_L médial à GT_FHC_L** (x_pred < x_fhc) : **{medial_fhc}/{n}** cas."
    )

    mean_asm = statistics.mean(c.dist_to_gt_asm_l for c in cases)
    mean_err = statistics.mean(c.error_px for c in cases)
    lines.append(
        f"- Distance moyenne V2_ASL_L → GT_ASM_L : **{format_num(mean_asm)}** px "
        f"(erreur moyenne ASL_L : {format_num(mean_err)} px)."
    )

    mean_edge = statistics.mean(c.edge_margin_px for c in cases)
    lines.append(f"- Marge moyenne au bord d'image (min des 4 bords) : **{format_num(mean_edge)}** px.")

    if dx_s["mean"] < -50:
        lines.append(
            "- **Interprétation** : biais systématique vers la **gauche image** (médial pour hanche gauche)."
        )
    if closer_asm >= n // 2:
        lines.append(
            "- **Interprétation** : dans la majorité des cas, la prédiction ressemble davantage à **ASM_L** qu'à **ASL_L**."
        )
    return lines


def write_markdown(cases: list[AslLCase]) -> None:
    dx_vals = [c.dx for c in cases]
    dy_vals = [c.dy for c in cases]
    err_vals = [c.error_px for c in cases]
    dx_s = summarize(dx_vals)
    dy_s = summarize(dy_vals)
    err_s = summarize(err_vals)

    lines = [
        "# Diagnostic ASL_L — erreurs V2 vs GT (new_26)",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Statistiques globales",
        "",
        "| Métrique | Moyenne | Médiane | Écart-type | Min | Max |",
        "|----------|---------|---------|------------|-----|-----|",
        f"| error_px | {format_num(err_s['mean'])} | {format_num(err_s['median'])} | {format_num(err_s['stdev'])} | {format_num(err_s['min'])} | {format_num(err_s['max'])} |",
        f"| dx | {format_num(dx_s['mean'])} | {format_num(dx_s['median'])} | {format_num(dx_s['stdev'])} | {format_num(dx_s['min'])} | {format_num(dx_s['max'])} |",
        f"| dy | {format_num(dy_s['mean'])} | {format_num(dy_s['median'])} | {format_num(dy_s['stdev'])} | {format_num(dy_s['min'])} | {format_num(dy_s['max'])} |",
        "",
        "## Diagnostic de biais",
        "",
    ]
    lines.extend(bias_diagnosis(cases, dx_s, dy_s))

    lines.extend(
        [
            "",
            "## Détail par cas (trié par error_px décroissant)",
            "",
            "| Radio | error_px | dx | dy | conf | nearest_GT | dist→ASM_L | dist→FHC_L | dist→ASL_R | médial FHC |",
            "|-------|----------|----|----|------|------------|------------|------------|------------|------------|",
        ]
    )
    for case in sorted(cases, key=lambda c: c.error_px, reverse=True):
        lines.append(
            f"| {case.case_id} | {format_num(case.error_px)} | {format_num(case.dx)} | {format_num(case.dy)} | "
            f"{format_num(case.confidence, 3)} | {case.nearest_gt_reference} | "
            f"{format_num(case.dist_to_gt_asm_l)} | {format_num(case.dist_to_gt_fhc_l)} | "
            f"{format_num(case.dist_to_gt_asl_r)} | {case.pred_medial_to_gt_fhc} |"
        )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_scatter_plots(cases: list[AslLCase]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    dx = [c.dx for c in cases]
    dy = [c.dy for c in cases]
    errors = [c.error_px for c in cases]
    labels = [c.case_id for c in cases]

    sc = axes[0].scatter(dx, dy, c=errors, cmap="plasma", s=80, edgecolors="k", linewidths=0.5)
    axes[0].axhline(0, color="gray", linestyle="--", linewidth=0.8)
    axes[0].axvline(0, color="gray", linestyle="--", linewidth=0.8)
    axes[0].set_xlabel("dx = pred_x - gt_x (px)  [<0 = gauche / médial]")
    axes[0].set_ylabel("dy = pred_y - gt_y (px)  [<0 = haut]")
    axes[0].set_title("Biais vectoriel ASL_L (couleur = error_px)")
    plt.colorbar(sc, ax=axes[0], label="error_px")
    for case in sorted(cases, key=lambda c: c.error_px, reverse=True)[:5]:
        axes[0].annotate(case.case_id, (case.dx, case.dy), fontsize=7, alpha=0.9)

    gt_xn = [c.gt_x_norm for c in cases]
    pred_xn = [c.pred_x_norm for c in cases]
    gt_yn = [c.gt_y_norm for c in cases]
    pred_yn = [c.pred_y_norm for c in cases]
    lims = [0, 1]
    axes[1].plot(lims, lims, "k--", linewidth=0.8, label="y = x")
    axes[1].scatter(gt_xn, pred_xn, c="tab:blue", label="x_norm", s=50, alpha=0.8)
    axes[1].scatter(gt_yn, pred_yn, c="tab:orange", label="y_norm", s=50, alpha=0.8)
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    axes[1].set_xlabel("GT normalisé")
    axes[1].set_ylabel("V2 prédit normalisé")
    axes[1].set_title("GT vs V2 (coords normalisées)")
    axes[1].legend(loc="upper left", fontsize=8)
    axes[1].set_aspect("equal")

    fig.tight_layout()
    fig.savefig(SCATTER_DX_DY, dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig2, ax2 = plt.subplots(figsize=(7, 7))
    ax2.scatter(gt_xn, gt_yn, c="green", marker="o", s=70, label="GT ASL_L", alpha=0.85)
    ax2.scatter(pred_xn, pred_yn, c="red", marker="x", s=70, label="V2 ASL_L", alpha=0.85)
    for case in cases:
        ax2.plot(
            [case.gt_x_norm, case.pred_x_norm],
            [case.gt_y_norm, case.pred_y_norm],
            color="gray",
            linewidth=0.6,
            alpha=0.5,
        )
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.invert_yaxis()
    ax2.set_xlabel("x_norm")
    ax2.set_ylabel("y_norm (origine haut)")
    ax2.set_title("Position spatiale GT vs V2 ASL_L (26 cas)")
    ax2.legend()
    ax2.set_aspect("equal")
    fig2.tight_layout()
    fig2.savefig(SCATTER_GT_PRED, dpi=150, bbox_inches="tight")
    plt.close(fig2)


def render_contact_sheet(cases: list[AslLCase]) -> None:
    font = load_font(16)
    font_small = load_font(12)
    panel_size = 480
    cols = 4
    rows = math.ceil(len(cases) / cols)
    pad = 12
    header = 36
    canvas_w = pad + cols * (panel_size + pad)
    canvas_h = pad + rows * (panel_size + header + pad)
    canvas = Image.new("RGB", (canvas_w, canvas_h), (20, 24, 32))
    draw = ImageDraw.Draw(canvas)

    for index, case in enumerate(sorted(cases, key=lambda c: c.case_id)):
        col = index % cols
        row = index // cols
        ox = pad + col * (panel_size + pad)
        oy = pad + row * (panel_size + header + pad)

        with Image.open(IMAGE_DIR / f"{case.case_id}.png") as source:
            img = source.convert("RGB")

        annotation = json.loads((ANNOT_DIR / f"{case.case_id}.json").read_text(encoding="utf-8-sig"))
        gt_asm = gt_point(annotation, "ASM_L")
        gt_fhc = gt_point(annotation, "FHC_L")
        gt_asl_r = gt_point(annotation, "ASL_R")
        assert gt_asm and gt_fhc and gt_asl_r

        cx = (case.gt_x + case.pred_x) / 2
        cy = (case.gt_y + case.pred_y) / 2
        crop_r = 350
        left = max(0, int(cx - crop_r))
        top = max(0, int(cy - crop_r))
        right = min(img.width, int(cx + crop_r))
        bottom = min(img.height, int(cy + crop_r))
        crop = img.crop((left, top, right, bottom))
        crop = crop.resize((panel_size, panel_size), Image.Resampling.LANCZOS)
        panel_draw = ImageDraw.Draw(crop)

        def to_crop(pt: tuple[float, float]) -> tuple[float, float]:
            return (
                (pt[0] - left) / max(right - left, 1) * panel_size,
                (pt[1] - top) / max(bottom - top, 1) * panel_size,
            )

        gt_pt = to_crop((case.gt_x, case.gt_y))
        pred_pt = to_crop((case.pred_x, case.pred_y))
        for ref_pt, color in (
            (gt_asm, REF_COLORS["GT_ASM_L"]),
            (gt_fhc, REF_COLORS["GT_FHC_L"]),
            (gt_asl_r, REF_COLORS["GT_ASL_R"]),
        ):
            p = to_crop(ref_pt)
            panel_draw.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), outline=color, width=2)

        panel_draw.line([gt_pt, pred_pt], fill=ERROR_COLOR, width=2)
        panel_draw.ellipse((gt_pt[0] - 8, gt_pt[1] - 8, gt_pt[0] + 8, gt_pt[1] + 8), outline=GT_COLOR, width=3)
        panel_draw.ellipse((pred_pt[0] - 6, pred_pt[1] - 6, pred_pt[0] + 6, pred_pt[1] + 6), fill=V2_COLOR)

        title = f"{case.case_id}  err={case.error_px:.0f}px  dx={case.dx:.0f}"
        draw.text((ox, oy), title, fill=(230, 230, 230), font=font_small)
        canvas.paste(crop, (ox, oy + header))

    legend = "GT ASL_L=cercle vert | V2 ASL_L=rose | trait=erreur | bleu=GT_ASM_L orange=GT_FHC_L gris=GT_ASL_R"
    draw.text((pad, canvas_h - 28), legend, fill=(180, 180, 180), font=font_small)
    canvas.save(CONTACT_SHEET, format="JPEG", quality=90, optimize=True)


def list_case_ids() -> list[str]:
    ids = sorted(path.stem for path in ANNOT_DIR.glob("B26_*.json"))
    if len(ids) != EXPECTED_CASES:
        raise RuntimeError(f"Attendu {EXPECTED_CASES} cas, trouvé {len(ids)}")
    return ids


def main() -> int:
    cases = build_cases(list_case_ids())
    write_csv(cases)
    write_markdown(cases)
    render_scatter_plots(cases)
    render_contact_sheet(cases)

    err_s = summarize([c.error_px for c in cases])
    dx_s = summarize([c.dx for c in cases])
    dy_s = summarize([c.dy for c in cases])

    print("ASL_L ERROR ANALYSIS COMPLETE")
    print(f"Cases: {len(cases)}")
    print(f"Mean error: {err_s['mean']:.2f} px")
    print(f"Median error: {err_s['median']:.2f} px")
    print(f"Mean dx: {dx_s['mean']:.2f} px")
    print(f"Mean dy: {dy_s['mean']:.2f} px")
    print(f"CSV: {OUTPUT_CSV.resolve()}")
    print(f"MD: {OUTPUT_MD.resolve()}")
    print(f"Scatter: {SCATTER_DX_DY.resolve()}, {SCATTER_GT_PRED.resolve()}")
    print(f"Contact sheet: {CONTACT_SHEET.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
