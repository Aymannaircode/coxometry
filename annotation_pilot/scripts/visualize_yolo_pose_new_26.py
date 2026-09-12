#!/usr/bin/env python3
"""Génère des overlays visuels pour vérifier les labels YOLO Pose (new_26)."""

from __future__ import annotations

import csv
import html
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent
DATASET_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"
MAPPING_CSV = DATASET_ROOT / "meta" / "source_mapping.csv"
OUTPUT_ROOT = DATASET_ROOT / "visual_check"
OVERLAY_DIR = OUTPUT_ROOT / "overlays"
THUMB_DIR = OUTPUT_ROOT / "thumbs"

sys.path.insert(0, str(SCRIPTS_DIR.parent / "manual_annotation_tool"))
import server  # noqa: E402

KEYPOINT_NAMES = [name for _, name, _ in server.LANDMARKS]
NKPT = len(KEYPOINT_NAMES)
NDIM = 3
EXPECTED_LABEL_COLS = 5 + NKPT * NDIM
THUMB_MAX_WIDTH = 640

RIGHT_COLOR = (255, 120, 40)
LEFT_COLOR = (60, 180, 255)
BBOX_COLOR = (80, 255, 120)
SKELETON_COLOR_R = (255, 180, 80)
SKELETON_COLOR_L = (120, 200, 255)

# Chaînes anatomiques utiles à la vérification visuelle
FEMORAL_CHAIN_R = ["FHC_R", "FNM_R", "FSP_R", "FSD_R"]
FEMORAL_CHAIN_L = ["FHC_L", "FNM_L", "FSP_L", "FSD_L"]
ACETABULAR_CHAIN_R = ["ASL_R", "ASM_R"]
ACETABULAR_CHAIN_L = ["ASL_L", "ASM_L"]


@dataclass
class OverlayResult:
    pilot_id: str
    split: str
    overlay_path: Path
    thumb_path: Path
    width: int
    height: int
    visible_keypoints: int
    warnings: list[str]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def parse_label(label_path: Path) -> tuple[list[float], list[tuple[str, float, float, float]]]:
    values = [float(part) for part in label_path.read_text(encoding="utf-8").strip().split()]
    if len(values) != EXPECTED_LABEL_COLS:
        raise ValueError(f"{label_path.name}: {len(values)} colonnes, attendu {EXPECTED_LABEL_COLS}")

    keypoints: list[tuple[str, float, float, float]] = []
    offset = 5
    for index, name in enumerate(KEYPOINT_NAMES):
        base = offset + index * NDIM
        keypoints.append((name, values[base], values[base + 1], values[base + 2]))
    return values[:5], keypoints


def side_color(name: str) -> tuple[int, int, int]:
    return RIGHT_COLOR if name.endswith("_R") else LEFT_COLOR


def denorm_point(x_norm: float, y_norm: float, width: int, height: int) -> tuple[float, float]:
    return x_norm * width, y_norm * height


def draw_label_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    color: tuple[int, int, int],
    font: ImageFont.ImageFont,
) -> None:
    x, y = position
    bbox = draw.textbbox((x, y), text, font=font)
    pad = 2
    draw.rectangle(
        (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad),
        fill=(0, 0, 0),
    )
    draw.text((x, y), text, fill=color, font=font)


def draw_skeleton(
    draw: ImageDraw.ImageDraw,
    keypoint_map: dict[str, tuple[float, float, float]],
    chain: list[str],
    color: tuple[int, int, int],
    width: int,
    height: int,
) -> None:
    points: list[tuple[float, float]] = []
    for name in chain:
        x_norm, y_norm, visibility = keypoint_map[name]
        if visibility > 0:
            points.append(denorm_point(x_norm, y_norm, width, height))
    for start, end in zip(points, points[1:]):
        draw.line([start, end], fill=color, width=3)


def render_overlay(
    image_path: Path,
    label_path: Path,
    output_path: Path,
    thumb_path: Path,
) -> OverlayResult:
    pilot_id = image_path.stem
    split = "train" if "train" in image_path.parts else "val"
    warnings: list[str] = []

    with Image.open(image_path) as source:
        image = source.convert("RGB")
    width, height = image.size
    draw = ImageDraw.Draw(image)
    font_main = load_font(max(14, width // 180))
    font_title = load_font(max(18, width // 120))

    bbox_vals, keypoints = parse_label(label_path)
    _cls, cx, cy, bw, bh = bbox_vals
    keypoint_map = {name: (x, y, v) for name, x, y, v in keypoints}

    x1 = (cx - bw / 2) * width
    y1 = (cy - bh / 2) * height
    x2 = (cx + bw / 2) * width
    y2 = (cy + bh / 2) * height
    draw.rectangle((x1, y1, x2, y2), outline=BBOX_COLOR, width=max(2, width // 600))

    draw_skeleton(draw, keypoint_map, FEMORAL_CHAIN_R, SKELETON_COLOR_R, width, height)
    draw_skeleton(draw, keypoint_map, FEMORAL_CHAIN_L, SKELETON_COLOR_L, width, height)
    draw_skeleton(draw, keypoint_map, ACETABULAR_CHAIN_R, SKELETON_COLOR_R, width, height)
    draw_skeleton(draw, keypoint_map, ACETABULAR_CHAIN_L, SKELETON_COLOR_L, width, height)

    visible = 0
    for index, (name, x_norm, y_norm, visibility) in enumerate(keypoints):
        color = side_color(name)
        if visibility <= 0:
            warnings.append(f"{name}: keypoint invisible (v=0)")
            continue
        visible += 1
        px, py = denorm_point(x_norm, y_norm, width, height)
        if not (0 <= px <= width and 0 <= py <= height):
            warnings.append(f"{name}: hors image ({px:.1f}, {py:.1f})")

        radius = max(6, width // 220)
        draw.ellipse(
            (px - radius, py - radius, px + radius, py + radius),
            fill=color,
            outline=(255, 255, 255),
            width=2,
        )
        label = f"{index}:{name}"
        draw_label_text(draw, (px + radius + 4, py - radius - 2), label, color, font_main)

        if name.endswith("_R") and px > width / 2:
            warnings.append(f"{name}: côté droit mais x > milieu — vérifier inversion R/L")
        if name.endswith("_L") and px < width / 2:
            warnings.append(f"{name}: côté gauche mais x < milieu — vérifier inversion R/L")

    title = f"{pilot_id}  |  split={split}  |  {width}x{height}  |  {visible}/{NKPT} kpts"
    draw.rectangle((0, 0, width, font_title.size + 16), fill=(0, 0, 0))
    draw.text((12, 8), title, fill=(255, 255, 255), font=font_title)

    legend = "Orange=RIGHT (_R)   Bleu=LEFT (_L)   Vert=bbox   Lignes=axes fémoral/acétabulaire"
    draw.rectangle((0, height - font_main.size - 14, width, height), fill=(0, 0, 0))
    draw.text((12, height - font_main.size - 8), legend, fill=(220, 220, 220), font=font_main)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG", optimize=True)

    thumb = image.copy()
    if thumb.width > THUMB_MAX_WIDTH:
        ratio = THUMB_MAX_WIDTH / thumb.width
        thumb = thumb.resize(
            (THUMB_MAX_WIDTH, max(1, int(thumb.height * ratio))),
            Image.Resampling.LANCZOS,
        )
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    thumb.save(thumb_path, format="PNG", optimize=True)

    return OverlayResult(
        pilot_id=pilot_id,
        split=split,
        overlay_path=output_path,
        thumb_path=thumb_path,
        width=width,
        height=height,
        visible_keypoints=visible,
        warnings=warnings,
    )


def load_mapping_rows() -> list[dict[str, str]]:
    with MAPPING_CSV.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_readme() -> None:
    text = """# Vérification visuelle — YOLO Pose new_26

Ce dossier contient des **overlays générés automatiquement** pour contrôler les labels YOLO
sans modifier le dataset d'origine (`images/`, `labels/`, `dataset.yaml`).

## Ouvrir la galerie

1. Ouvrir `index.html` dans un navigateur (double-clic ou glisser-déposer).
2. Parcourir les 26 cas `B26_01` … `B26_26`.
3. Cliquer une vignette pour voir l'overlay pleine résolution.

Chemin complet :

```
datasets/yolo_pose_new_26/visual_check/index.html
```

## Légende des couleurs

| Élément | Couleur | Signification |
|---------|---------|---------------|
| Points `_R` | Orange | Landmarks côté **droit** (droite de l'image patient) |
| Points `_L` | Bleu | Landmarks côté **gauche** |
| Rectangle | Vert | Bounding box YOLO |
| Lignes orange | — | Chaîne fémorale / acétabulaire droite |
| Lignes bleues | — | Chaîne fémorale / acétabulaire gauche |

## Checklist de revue clinique

Pour **chaque** image, vérifier :

### Côté R / L
- [ ] Tous les points orange (`*_R`) sont à **droite** du milieu de l'image.
- [ ] Tous les points bleu (`*_L`) sont à **gauche** du milieu.
- [ ] Aucune paire R/L ne semble inversée.

### Teardrop (TD)
- [ ] `TD_R` / `TD_L` sont sur la gouttière acétabulaire (teardrop).

### Tête fémorale (FHC)
- [ ] `FHC_R` / `FHC_L` sont au **centre** de la tête fémorale.

### Acétabulum (ASL / ASM)
- [ ] `ASL_*` : sourcil acétabulaire latéral.
- [ ] `ASM_*` : bord supéro-médial / teardrop region cohérente.

### Col fémoral (FNM)
- [ ] `FNM_*` est sur l'**axe du col** (entre FHC et diaphyse).

### Diaphyse (FSP / FSD)
- [ ] `FSP_*` et `FSD_*` sont alignés sur l'**axe diaphysaire** distal.
- [ ] La ligne orange/bleue FHC→FNM→FSP→FSD suit le fémur.

### Normalisation
- [ ] Les points ne sont **pas décalés** (comparer mentalement avec l'anatomie).
- [ ] Pas de cluster anormal au coin (0,0) — signe d'erreur de conversion.

### Bounding box
- [ ] Le rectangle vert **englobe le bassin** ( deux hanches + part de diaphyse visible).
- [ ] La bbox n'est ni trop serrée ni démesurément large.

## Regénérer les overlays

```bash
.venv\\Scripts\\python.exe annotation_pilot\\scripts\\visualize_yolo_pose_new_26.py
```

Les fichiers source (JSON, DICOM, labels YOLO) ne sont **jamais modifiés**.
"""
    (OUTPUT_ROOT / "README.md").write_text(text, encoding="utf-8")


def write_index(results: list[OverlayResult], all_warnings: list[str]) -> None:
    ordered = sorted(results, key=lambda item: item.pilot_id)
    cards: list[str] = []
    for result in ordered:
        warning_html = ""
        if result.warnings:
            items = "".join(f"<li>{html.escape(w)}</li>" for w in result.warnings)
            warning_html = f"<ul class='warn'>{items}</ul>"
        cards.append(
            f"""
<article class="card">
  <a href="overlays/{html.escape(result.pilot_id)}_overlay.png" target="_blank">
    <img src="thumbs/{html.escape(result.pilot_id)}_thumb.png" alt="{html.escape(result.pilot_id)}" loading="lazy">
  </a>
  <div class="meta">
    <h2>{html.escape(result.pilot_id)}</h2>
    <p>split: <strong>{html.escape(result.split)}</strong></p>
    <p>{result.width} × {result.height} px</p>
    <p>{result.visible_keypoints}/{NKPT} keypoints visibles</p>
    {warning_html}
    <p><a href="overlays/{html.escape(result.pilot_id)}_overlay.png" target="_blank">Ouvrir pleine résolution</a></p>
  </div>
</article>"""
        )

    warning_section = ""
    if all_warnings:
        items = "".join(f"<li>{html.escape(w)}</li>" for w in all_warnings)
        warning_section = f"<section class='banner warn-banner'><h2>Avertissements automatiques ({len(all_warnings)})</h2><ul>{items}</ul></section>"

    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vérification visuelle YOLO Pose — new_26</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #11151c;
      --panel: #1b2230;
      --text: #e8eef7;
      --muted: #9fb0c7;
      --accent: #5fd38d;
      --warn: #ffb454;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    header, main, footer {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 1rem 1.25rem;
    }}
    header {{
      border-bottom: 1px solid #2a3447;
    }}
    h1 {{ margin: 0 0 .25rem; font-size: 1.6rem; }}
    .subtitle {{ color: var(--muted); margin: 0; }}
    .stats {{
      display: flex;
      flex-wrap: wrap;
      gap: .75rem;
      margin-top: 1rem;
    }}
    .stat {{
      background: var(--panel);
      border: 1px solid #2a3447;
      border-radius: 10px;
      padding: .6rem .9rem;
      min-width: 140px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1rem;
      margin-top: 1rem;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid #2a3447;
      border-radius: 12px;
      overflow: hidden;
    }}
    .card img {{
      width: 100%;
      display: block;
      background: #000;
    }}
    .meta {{ padding: .85rem 1rem 1rem; }}
    .meta h2 {{ margin: 0 0 .35rem; font-size: 1.1rem; color: var(--accent); }}
    .meta p {{ margin: .15rem 0; color: var(--muted); font-size: .92rem; }}
    .meta a {{ color: #8ec5ff; }}
    .warn {{ margin: .5rem 0 0; padding-left: 1rem; color: var(--warn); font-size: .85rem; }}
    .banner {{
      margin-top: 1rem;
      background: var(--panel);
      border: 1px solid #2a3447;
      border-radius: 12px;
      padding: .75rem 1rem;
    }}
    .warn-banner {{ border-color: #6a4b1f; }}
    footer {{ color: var(--muted); font-size: .85rem; border-top: 1px solid #2a3447; }}
  </style>
</head>
<body>
  <header>
    <h1>Vérification visuelle YOLO Pose — new_26</h1>
    <p class="subtitle">26 overlays · Orange = RIGHT (_R) · Bleu = LEFT (_L) · Vert = bbox</p>
    <div class="stats">
      <div class="stat"><strong>{len(results)}</strong><br>overlays</div>
      <div class="stat"><strong>{sum(1 for r in results if r.split == 'train')}</strong><br>train</div>
      <div class="stat"><strong>{sum(1 for r in results if r.split == 'val')}</strong><br>val</div>
      <div class="stat"><strong>{len(all_warnings)}</strong><br>avertissements auto</div>
    </div>
  </header>
  <main>
    {warning_section}
    <section class="grid">
      {''.join(cards)}
    </section>
  </main>
  <footer>
    Généré le {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))} —
    sources non modifiées — entraînement non lancé.
  </footer>
</body>
</html>
"""
    (OUTPUT_ROOT / "index.html").write_text(page, encoding="utf-8")


def main() -> int:
    if not MAPPING_CSV.is_file():
        raise SystemExit(f"Mapping introuvable: {MAPPING_CSV}")

    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
    THUMB_DIR.mkdir(parents=True, exist_ok=True)

    results: list[OverlayResult] = []
    errors: list[str] = []
    all_warnings: list[str] = []

    for row in load_mapping_rows():
        pilot_id = row["pilot_id"]
        image_path = DATASET_ROOT / row["yolo_image"].replace("\\", "/")
        label_path = DATASET_ROOT / row["yolo_label"].replace("\\", "/")
        overlay_path = OVERLAY_DIR / f"{pilot_id}_overlay.png"
        thumb_path = THUMB_DIR / f"{pilot_id}_thumb.png"

        try:
            if not image_path.is_file():
                raise FileNotFoundError(f"Image absente: {image_path}")
            if not label_path.is_file():
                raise FileNotFoundError(f"Label absent: {label_path}")
            result = render_overlay(image_path, label_path, overlay_path, thumb_path)
            results.append(result)
            for warning in result.warnings:
                all_warnings.append(f"{pilot_id}: {warning}")
        except Exception as exc:
            errors.append(f"{pilot_id}: {exc}")

    write_readme()
    write_index(results, all_warnings)

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "overlays_generated": len(results),
        "errors": errors,
        "auto_warnings": all_warnings,
    }
    (OUTPUT_ROOT / "generation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"OVERLAYS={len(results)} ERRORS={len(errors)} WARNINGS={len(all_warnings)}")
    print(f"INDEX={OUTPUT_ROOT / 'index.html'}")
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
