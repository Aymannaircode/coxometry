#!/usr/bin/env python3
"""Analyse ASL/ASM (new_26) — rapport + galerie zoom, sans modifier les sources."""

from __future__ import annotations

import csv
import html
import json
import math
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
DATASET_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"
MAPPING_CSV = DATASET_ROOT / "meta" / "source_mapping.csv"
OUTPUT_ROOT = DATASET_ROOT / "visual_check" / "asl_asm_review"
OVERLAY_DIR = OUTPUT_ROOT / "overlays"
THUMB_DIR = OUTPUT_ROOT / "thumbs"

TARGET_NAMES = ("ASL_R", "ASM_R", "ASL_L", "ASM_L")
REFERENCE_NAMES = ("FHC_R", "FHC_L", "TD_R", "TD_L")

RIGHT_COLOR = (255, 120, 40)
LEFT_COLOR = (60, 180, 255)
LINE_COLOR_R = (255, 200, 80)
LINE_COLOR_L = (140, 220, 255)
REF_COLOR = (160, 160, 160)


@dataclass
class Point:
    name: str
    x: float
    y: float
    v: int


@dataclass
class SideMetrics:
    side: str
    asl: Point
    asm: Point
    fhc: Point
    td: Point
    asl_above_fhc_px: float
    asm_above_fhc_px: float
    asl_above_fhc_norm: float
    asm_above_fhc_norm: float
    sourcil_length_px: float
    sourcil_angle_deg: float
    lateral_medial_ok: bool
    flags: list[str] = field(default_factory=list)


@dataclass
class CaseRecord:
    pilot_id: str
    split: str
    image_path: Path
    source_json: Path
    width: int
    height: int
    points: dict[str, Point]
    right: SideMetrics
    left: SideMetrics
    suspect: bool
    suspect_reasons: list[str]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_case(json_path: Path, row: dict[str, str]) -> CaseRecord:
    data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    width = int(data["image_width"])
    height = int(data["image_height"])
    points = {
        lm["name"]: Point(lm["name"], float(lm["x"]), float(lm["y"]), int(lm["v"]))
        for lm in data["landmarks"]
        if lm.get("name")
    }

    def side_metrics(side: str) -> SideMetrics:
        suffix = "_R" if side == "right" else "_L"
        asl = points[f"ASL{suffix}"]
        asm = points[f"ASM{suffix}"]
        fhc = points[f"FHC{suffix}"]
        td = points[f"TD{suffix}"]
        dx = asl.x - asm.x
        dy = asl.y - asm.y
        # Inclinaison aiguë par rapport à l'horizontale (0° = sourcil horizontal)
        sourcil_tilt_deg = math.degrees(math.atan2(abs(dy), abs(dx))) if dx or dy else 0.0
        lateral_medial_ok = asl.x < asm.x if side == "right" else asl.x > asm.x
        return SideMetrics(
            side=side,
            asl=asl,
            asm=asm,
            fhc=fhc,
            td=td,
            asl_above_fhc_px=fhc.y - asl.y,
            asm_above_fhc_px=fhc.y - asm.y,
            asl_above_fhc_norm=(fhc.y - asl.y) / height,
            asm_above_fhc_norm=(fhc.y - asm.y) / height,
            sourcil_length_px=math.hypot(dx, dy),
            sourcil_angle_deg=sourcil_tilt_deg,
            lateral_medial_ok=lateral_medial_ok,
        )

    return CaseRecord(
        pilot_id=data["image_id"],
        split=row["split"],
        image_path=DATASET_ROOT / row["yolo_image"].replace("\\", "/"),
        source_json=json_path,
        width=width,
        height=height,
        points=points,
        right=side_metrics("right"),
        left=side_metrics("left"),
        suspect=False,
        suspect_reasons=[],
    )


def compute_cohort_thresholds(cases: list[CaseRecord]) -> dict[str, float]:
    asl_norm = [case.right.asl_above_fhc_norm for case in cases] + [
        case.left.asl_above_fhc_norm for case in cases
    ]
    asm_norm = [case.right.asm_above_fhc_norm for case in cases] + [
        case.left.asm_above_fhc_norm for case in cases
    ]
    return {
        "asl_above_fhc_norm_median": statistics.median(asl_norm),
        "asl_above_fhc_norm_mad": statistics.median(abs(v - statistics.median(asl_norm)) for v in asl_norm)
        or 0.01,
        "asm_above_fhc_norm_median": statistics.median(asm_norm),
        "asm_above_fhc_norm_mad": statistics.median(abs(v - statistics.median(asm_norm)) for v in asm_norm)
        or 0.01,
    }


def flag_cases(cases: list[CaseRecord], thresholds: dict[str, float]) -> None:
    """Heuristiques de présélection — ne remplace pas la revue manuelle."""
    mad_mult = 2.5
    asl_med = thresholds["asl_above_fhc_norm_median"]
    asl_mad = thresholds["asl_above_fhc_norm_mad"]
    asm_med = thresholds["asm_above_fhc_norm_median"]
    asm_mad = thresholds["asm_above_fhc_norm_mad"]

    for case in cases:
        reasons: list[str] = []
        for metrics, suffix in ((case.right, "R"), (case.left, "L")):
            prefix = suffix
            if not metrics.lateral_medial_ok:
                msg = f"{prefix}: ASL/ASM latéral-médial inversé (ASL_x={metrics.asl.x:.1f}, ASM_x={metrics.asm.x:.1f})"
                metrics.flags.append(msg)
                reasons.append(msg)

            if metrics.asl_above_fhc_px <= 0:
                msg = f"{prefix}: ASL sous le centre FHC (y_ASL={metrics.asl.y:.1f} ≥ y_FHC={metrics.fhc.y:.1f})"
                metrics.flags.append(msg)
                reasons.append(msg)

            if metrics.asm_above_fhc_px <= 0:
                msg = f"{prefix}: ASM sous le centre FHC (y_ASM={metrics.asm.y:.1f} ≥ y_FHC={metrics.fhc.y:.1f})"
                metrics.flags.append(msg)
                reasons.append(msg)

            if metrics.asl_above_fhc_norm > asl_med + mad_mult * asl_mad:
                msg = (
                    f"{prefix}: ASL anormalement haut vs FHC "
                    f"({metrics.asl_above_fhc_norm:.3f} norm, médiane {asl_med:.3f}) — possible ilium"
                )
                metrics.flags.append(msg)
                reasons.append(msg)

            if metrics.asm_above_fhc_norm > asm_med + mad_mult * asm_mad:
                msg = (
                    f"{prefix}: ASM anormalement haut vs FHC "
                    f"({metrics.asm_above_fhc_norm:.3f} norm, médiane {asm_med:.3f}) — possible ilium"
                )
                metrics.flags.append(msg)
                reasons.append(msg)

            asl_asm_dy = abs(metrics.asl.y - metrics.asm.y)
            if asl_asm_dy > case.height * 0.12:
                msg = (
                    f"{prefix}: écart vertical ASL/ASM important ({asl_asm_dy:.0f} px) — "
                    "ligne ne suit peut-être pas le sourcil"
                )
                metrics.flags.append(msg)
                reasons.append(msg)

            if metrics.sourcil_angle_deg > 50:
                msg = (
                    f"{prefix}: ligne ASL→ASM très inclinée ({metrics.sourcil_angle_deg:.1f}° vs horizontale) — "
                    "ne suit peut-être pas le sourcil"
                )
                metrics.flags.append(msg)
                reasons.append(msg)

            if metrics.sourcil_length_px < case.width * 0.04:
                msg = f"{prefix}: segment ASL→ASM très court ({metrics.sourcil_length_px:.1f} px)"
                metrics.flags.append(msg)
                reasons.append(msg)

        case.suspect_reasons = reasons
        case.suspect = bool(reasons)


def crop_zoom(
    image: Image.Image,
    center_points: list[Point],
    ref_points: list[Point],
    padding_ratio: float = 0.85,
    target_size: int = 900,
) -> Image.Image:
    all_pts = center_points + ref_points
    xs = [p.x for p in all_pts]
    ys = [p.y for p in all_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1.0)
    span_y = max(max_y - min_y, 1.0)
    pad_x = span_x * padding_ratio
    pad_y = span_y * padding_ratio
    left = int(max(0, min_x - pad_x))
    top = int(max(0, min_y - pad_y))
    right = int(min(image.width, max_x + pad_x))
    bottom = int(min(image.height, max_y + pad_y))
    crop = image.crop((left, top, right, bottom)).copy()
    scale = target_size / max(crop.width, crop.height)
    new_size = (max(1, int(crop.width * scale)), max(1, int(crop.height * scale)))
    crop = crop.resize(new_size, Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(crop)
    font = load_font(max(16, new_size[0] // 28))

    def to_crop(pt: Point) -> tuple[float, float]:
        return (pt.x - left) * scale, (pt.y - top) * scale

    for ref in ref_points:
        px, py = to_crop(ref)
        r = max(4, new_size[0] // 80)
        draw.ellipse((px - r, py - r, px + r, py + r), outline=REF_COLOR, width=2)
        draw.text((px + r + 2, py - r), ref.name, fill=REF_COLOR, font=font)

    asl, asm = center_points
    color = RIGHT_COLOR if asl.name.endswith("_R") else LEFT_COLOR
    line_color = LINE_COLOR_R if asl.name.endswith("_R") else LINE_COLOR_L
    ax, ay = to_crop(asl)
    mx, my = to_crop(asm)
    draw.line([(ax, ay), (mx, my)], fill=line_color, width=max(2, new_size[0] // 120))
    for pt in (asl, asm):
        px, py = to_crop(pt)
        r = max(7, new_size[0] // 55)
        draw.ellipse((px - r, py - r, px + r, py + r), fill=color, outline=(255, 255, 255), width=2)
        draw.text((px + r + 3, py - r - 2), pt.name, fill=color, font=font)
    return crop


def render_overlay(case: CaseRecord, output_path: Path, thumb_path: Path) -> None:
    with Image.open(case.image_path) as source:
        image = source.convert("RGB")

    right_panel = crop_zoom(
        image,
        [case.points["ASL_R"], case.points["ASM_R"]],
        [case.points["FHC_R"], case.points["TD_R"]],
    )
    left_panel = crop_zoom(
        image,
        [case.points["ASL_L"], case.points["ASM_L"]],
        [case.points["FHC_L"], case.points["TD_L"]],
    )
    gap = 16
    title_h = 56
    footer_h = 42
    canvas_w = right_panel.width + gap + left_panel.width
    canvas_h = title_h + max(right_panel.height, left_panel.height) + footer_h
    canvas = Image.new("RGB", (canvas_w, canvas_h), (18, 22, 30))
    canvas.paste(right_panel, (0, title_h))
    canvas.paste(left_panel, (right_panel.width + gap, title_h))

    draw = ImageDraw.Draw(canvas)
    title_font = load_font(22)
    footer_font = load_font(16)
    status = "SUSPECT (heuristique)" if case.suspect else "non signalé automatiquement"
    title = f"{case.pilot_id}  |  split={case.split}  |  {case.width}x{case.height}  |  {status}"
    draw.text((12, 14), title, fill=(240, 240, 240), font=title_font)
    legend = "Orange=RIGHT  Bleu=LEFT  Gris=FHC/TD (réf.)  Ligne=ASL→ASM"
    draw.text((12, canvas_h - footer_h + 10), legend, fill=(180, 190, 205), font=footer_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=True)
    thumb = canvas.copy()
    if thumb.width > 720:
        ratio = 720 / thumb.width
        thumb = thumb.resize((720, max(1, int(thumb.height * ratio))), Image.Resampling.LANCZOS)
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    thumb.save(thumb_path, format="PNG", optimize=True)


def write_csv_report(cases: list[CaseRecord], path: Path) -> None:
    fieldnames = [
        "pilot_id",
        "split",
        "image_file",
        "source_json",
        "image_width",
        "image_height",
        "ASL_R_x",
        "ASL_R_y",
        "ASM_R_x",
        "ASM_R_y",
        "ASL_L_x",
        "ASL_L_y",
        "ASM_L_x",
        "ASM_L_y",
        "ASL_R_above_FHC_norm",
        "ASM_R_above_FHC_norm",
        "ASL_L_above_FHC_norm",
        "ASM_L_above_FHC_norm",
        "sourcil_angle_R_deg",
        "sourcil_angle_L_deg",
        "lateral_medial_ok_R",
        "lateral_medial_ok_L",
        "auto_suspect",
        "auto_flags",
        "overlay_file",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for case in sorted(cases, key=lambda item: item.pilot_id):
            writer.writerow(
                {
                    "pilot_id": case.pilot_id,
                    "split": case.split,
                    "image_file": str(case.image_path.relative_to(DATASET_ROOT)),
                    "source_json": str(case.source_json.relative_to(PROJECT_ROOT)),
                    "image_width": case.width,
                    "image_height": case.height,
                    "ASL_R_x": f"{case.points['ASL_R'].x:.2f}",
                    "ASL_R_y": f"{case.points['ASL_R'].y:.2f}",
                    "ASM_R_x": f"{case.points['ASM_R'].x:.2f}",
                    "ASM_R_y": f"{case.points['ASM_R'].y:.2f}",
                    "ASL_L_x": f"{case.points['ASL_L'].x:.2f}",
                    "ASL_L_y": f"{case.points['ASL_L'].y:.2f}",
                    "ASM_L_x": f"{case.points['ASM_L'].x:.2f}",
                    "ASM_L_y": f"{case.points['ASM_L'].y:.2f}",
                    "ASL_R_above_FHC_norm": f"{case.right.asl_above_fhc_norm:.4f}",
                    "ASM_R_above_FHC_norm": f"{case.right.asm_above_fhc_norm:.4f}",
                    "ASL_L_above_FHC_norm": f"{case.left.asl_above_fhc_norm:.4f}",
                    "ASM_L_above_FHC_norm": f"{case.left.asm_above_fhc_norm:.4f}",
                    "sourcil_angle_R_deg": f"{case.right.sourcil_angle_deg:.2f}",
                    "sourcil_angle_L_deg": f"{case.left.sourcil_angle_deg:.2f}",
                    "lateral_medial_ok_R": case.right.lateral_medial_ok,
                    "lateral_medial_ok_L": case.left.lateral_medial_ok,
                    "auto_suspect": case.suspect,
                    "auto_flags": " | ".join(case.suspect_reasons),
                    "overlay_file": f"overlays/{case.pilot_id}_asl_asm.png",
                }
            )


def write_md_report(cases: list[CaseRecord], thresholds: dict[str, float], path: Path) -> None:
    suspect_cases = [case for case in cases if case.suspect]
    lines = [
        "# Rapport ASL / ASM — new_26",
        "",
        f"**Date :** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "**Sources :** JSON MVP (`annotation_pilot/annotations/new_26/`) — non modifiés",
        "",
        "## Résumé",
        "",
        f"- Cas analysés : **{len(cases)}**",
        f"- Cas signalés par heuristique automatique : **{len(suspect_cases)}**",
        "- ⚠️ Le flag *suspect* est une **aide à la revue**, pas un diagnostic définitif.",
        "",
        "## Coordonnées par image (pixels, origine haut-gauche)",
        "",
        "| ID | split | ASL_R (x,y) | ASM_R (x,y) | ASL_L (x,y) | ASM_L (x,y) | Suspect auto |",
        "|----|-------|-------------|-------------|-------------|-------------|--------------|",
    ]
    for case in sorted(cases, key=lambda item: item.pilot_id):
        p = case.points
        flag = "oui" if case.suspect else "non"
        lines.append(
            f"| {case.pilot_id} | {case.split} | "
            f"({p['ASL_R'].x:.1f}, {p['ASL_R'].y:.1f}) | "
            f"({p['ASM_R'].x:.1f}, {p['ASM_R'].y:.1f}) | "
            f"({p['ASL_L'].x:.1f}, {p['ASL_L'].y:.1f}) | "
            f"({p['ASM_L'].x:.1f}, {p['ASM_L'].y:.1f}) | {flag} |"
        )

    lines.extend(
        [
            "",
            "## Heuristiques automatiques (présélection)",
            "",
            f"- ASL au-dessus de FHC (normalisé) — médiane cohorte : {thresholds['asl_above_fhc_norm_median']:.4f}",
            f"- ASM au-dessus de FHC (normalisé) — médiane cohorte : {thresholds['asm_above_fhc_norm_median']:.4f}",
            "- Flag si valeur > médiane + 2.5×MAD, inversion latéral/médial, ASL/ASM sous FHC, "
            "écart vertical ASL/ASM > 12 % hauteur, inclinaison sourcil > 50°, ou segment très court.",
            "",
        ]
    )
    if suspect_cases:
        lines.append("## Détail des cas signalés")
        lines.append("")
        for case in sorted(suspect_cases, key=lambda item: item.pilot_id):
            lines.append(f"### {case.pilot_id}")
            for reason in case.suspect_reasons:
                lines.append(f"- {reason}")
            lines.append("")

    lines.extend(
        [
            "## Fichiers image associés",
            "",
            "| ID | PNG dataset | Overlay zoom |",
            "|----|-------------|--------------|",
        ]
    )
    for case in sorted(cases, key=lambda item: item.pilot_id):
        lines.append(
            f"| {case.pilot_id} | `{case.image_path.relative_to(DATASET_ROOT)}` | "
            f"`visual_check/asl_asm_review/overlays/{case.pilot_id}_asl_asm.png` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(suspect_count: int) -> None:
    text = f"""# Revue ASL / ASM — new_26

Galerie dédiée à la vérification manuelle des landmarks **ASL** et **ASM** (sourcil acétabulaire).

## Ouvrir la galerie

```
datasets/yolo_pose_new_26/visual_check/asl_asm_review/index.html
```

## Contenu

- **26 zooms** (acétabulum droit + gauche par cas)
- Points **ASL** / **ASM** colorés (orange=R, bleu=L)
- Ligne **ASL → ASM**
- Références grises **FHC** et **TD** (contexte anatomique, non modifiés)

## Rapports

- `asl_asm_report.csv` — coordonnées et métriques
- `asl_asm_report.md` — tableau lisible + cas signalés

## Heuristique « suspect »

**{suspect_count}** cas signalés automatiquement pour revue prioritaire.
Ce flag **ne remplace pas** votre validation manuelle et **ne modifie aucune annotation**.

## Checklist manuelle

- [ ] ASL est sur l'extrémité **latérale** du sourcil (pas sur l'aile iliaque)
- [ ] ASM est sur l'extrémité **médiale** du sourcil
- [ ] La ligne ASL→ASM suit le **toit acétabulaire porteur**
- [ ] Les points ne sont pas **trop hauts** sur l'ilium
- [ ] R/L non inversés (ASL latéral à ASM sur chaque côté)

## Regénérer

```bash
.venv\\\\Scripts\\\\python.exe annotation_pilot\\\\scripts\\\\analyze_asl_asm_new_26.py
```
"""
    (OUTPUT_ROOT / "README.md").write_text(text, encoding="utf-8")


def write_index(cases: list[CaseRecord]) -> None:
    cards = []
    for case in sorted(cases, key=lambda item: item.pilot_id):
        p = case.points
        badge = (
            "<span class='badge suspect'>suspect auto</span>"
            if case.suspect
            else "<span class='badge ok'>non signalé</span>"
        )
        flags_html = ""
        if case.suspect_reasons:
            items = "".join(f"<li>{html.escape(r)}</li>" for r in case.suspect_reasons)
            flags_html = f"<ul class='flags'>{items}</ul>"
        cards.append(
            f"""
<article class="card {'suspect' if case.suspect else ''}">
  <a href="overlays/{html.escape(case.pilot_id)}_asl_asm.png" target="_blank">
    <img src="thumbs/{html.escape(case.pilot_id)}_asl_asm_thumb.png" alt="{html.escape(case.pilot_id)}" loading="lazy">
  </a>
  <div class="meta">
    <h2>{html.escape(case.pilot_id)} {badge}</h2>
    <p>split: <strong>{html.escape(case.split)}</strong></p>
    <p><strong>R</strong> ASL ({p['ASL_R'].x:.1f}, {p['ASL_R'].y:.1f}) · ASM ({p['ASM_R'].x:.1f}, {p['ASM_R'].y:.1f})</p>
    <p><strong>L</strong> ASL ({p['ASL_L'].x:.1f}, {p['ASL_L'].y:.1f}) · ASM ({p['ASM_L'].x:.1f}, {p['ASM_L'].y:.1f})</p>
    {flags_html}
    <p><a href="overlays/{html.escape(case.pilot_id)}_asl_asm.png" target="_blank">Plein écran</a></p>
  </div>
</article>"""
        )

    suspect = sum(1 for case in cases if case.suspect)
    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Revue ASL/ASM — new_26</title>
  <style>
    :root {{ color-scheme: dark; --bg:#11151c; --panel:#1b2230; --text:#e8eef7; --muted:#9fb0c7; --warn:#ffb454; --ok:#5fd38d; }}
    body {{ margin:0; font-family:"Segoe UI",Arial,sans-serif; background:var(--bg); color:var(--text); }}
    header,main,footer {{ max-width:1400px; margin:0 auto; padding:1rem 1.25rem; }}
    header {{ border-bottom:1px solid #2a3447; }}
    .stats {{ display:flex; gap:.75rem; flex-wrap:wrap; margin-top:1rem; }}
    .stat {{ background:var(--panel); border:1px solid #2a3447; border-radius:10px; padding:.6rem .9rem; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:1rem; margin-top:1rem; }}
    .card {{ background:var(--panel); border:1px solid #2a3447; border-radius:12px; overflow:hidden; }}
    .card.suspect {{ border-color:#6a4b1f; }}
    .card img {{ width:100%; display:block; background:#000; }}
    .meta {{ padding:.85rem 1rem 1rem; }}
    .meta h2 {{ margin:0 0 .35rem; font-size:1.05rem; }}
    .meta p {{ margin:.15rem 0; color:var(--muted); font-size:.88rem; }}
    .badge {{ font-size:.72rem; padding:.12rem .45rem; border-radius:999px; margin-left:.35rem; }}
    .badge.suspect {{ background:#4a3314; color:var(--warn); }}
    .badge.ok {{ background:#163222; color:var(--ok); }}
    .flags {{ margin:.45rem 0 0; padding-left:1rem; color:var(--warn); font-size:.82rem; }}
    footer {{ color:var(--muted); font-size:.85rem; border-top:1px solid #2a3447; }}
  </style>
</head>
<body>
  <header>
    <h1>Revue ASL / ASM — sourcil acétabulaire</h1>
    <p>Zoom bilatéral · Ligne ASL→ASM · Références FHC/TD · Aucune annotation modifiée</p>
    <div class="stats">
      <div class="stat"><strong>{len(cases)}</strong><br>cas</div>
      <div class="stat"><strong>{suspect}</strong><br>suspects (heuristique)</div>
      <div class="stat"><strong>0</strong><br>annotations modifiées</div>
    </div>
  </header>
  <main><section class="grid">{''.join(cards)}</section></main>
  <footer>Généré le {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))} — validation manuelle requise</footer>
</body>
</html>"""
    (OUTPUT_ROOT / "index.html").write_text(page, encoding="utf-8")


def main() -> int:
    if not MAPPING_CSV.is_file():
        raise SystemExit(f"Mapping introuvable: {MAPPING_CSV}")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
    THUMB_DIR.mkdir(parents=True, exist_ok=True)

    cases: list[CaseRecord] = []
    errors: list[str] = []
    for row in csv.DictReader(MAPPING_CSV.open("r", encoding="utf-8-sig")):
        json_path = PROJECT_ROOT / row["source_json"].replace("\\", "/")
        try:
            cases.append(load_case(json_path, row))
        except Exception as exc:
            errors.append(f"{row['pilot_id']}: {exc}")

    thresholds = compute_cohort_thresholds(cases)
    flag_cases(cases, thresholds)

    for case in cases:
        overlay = OVERLAY_DIR / f"{case.pilot_id}_asl_asm.png"
        thumb = THUMB_DIR / f"{case.pilot_id}_asl_asm_thumb.png"
        try:
            render_overlay(case, overlay, thumb)
        except Exception as exc:
            errors.append(f"{case.pilot_id} overlay: {exc}")

    write_csv_report(cases, OUTPUT_ROOT / "asl_asm_report.csv")
    write_md_report(cases, thresholds, OUTPUT_ROOT / "asl_asm_report.md")
    write_readme(sum(1 for case in cases if case.suspect))
    write_index(cases)

    suspect_ids = [case.pilot_id for case in cases if case.suspect]
    print(f"CASES={len(cases)} SUSPECT={len(suspect_ids)} ERRORS={len(errors)}")
    print(f"INDEX={OUTPUT_ROOT / 'index.html'}")
    if suspect_ids:
        print("SUSPECT_IDS=" + ",".join(sorted(suspect_ids)))
    for err in errors:
        print(f"ERROR: {err}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
