#!/usr/bin/env python3
"""Contact sheet des 5 pires overlays V2 (lecture seule sur les sources)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OVERLAY_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "overlays"
OUTPUT_PATH = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_worst5_contact_sheet.jpg"

CASES = ("B26_01", "B26_21", "B26_10", "B26_13", "B26_05")
PANEL_HEIGHT = 720
LABEL_HEIGHT = 56
PADDING = 24
BACKGROUND = (18, 22, 30)
LABEL_COLOR = (255, 255, 255)
LABEL_BG = (12, 16, 24)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("arialbd.ttf", "Arial Bold.ttf", "arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_panel(path: Path, target_height: int) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGB")
    ratio = target_height / max(image.height, 1)
    new_width = max(1, int(image.width * ratio))
    return image.resize((new_width, target_height), Image.Resampling.LANCZOS)


def build_contact_sheet() -> Image.Image:
    panels: list[tuple[str, Image.Image]] = []
    for case_id in CASES:
        overlay_path = OVERLAY_DIR / f"{case_id}.jpg"
        if not overlay_path.is_file():
            raise FileNotFoundError(f"Overlay introuvable : {overlay_path}")
        panels.append((case_id, load_panel(overlay_path, PANEL_HEIGHT)))

    total_width = PADDING + sum(image.width for _, image in panels) + PADDING * (len(panels) - 1)
    total_height = PADDING * 2 + PANEL_HEIGHT + LABEL_HEIGHT
    canvas = Image.new("RGB", (total_width, total_height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    font = load_font(34)

    x = PADDING
    y = PADDING
    for case_id, image in panels:
        canvas.paste(image, (x, y))
        label = case_id
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        label_x = x + (image.width - text_w) // 2
        label_y = y + PANEL_HEIGHT + (LABEL_HEIGHT - text_h) // 2
        draw.rectangle(
            (x, y + PANEL_HEIGHT, x + image.width, y + PANEL_HEIGHT + LABEL_HEIGHT),
            fill=LABEL_BG,
        )
        draw.text((label_x, label_y), label, fill=LABEL_COLOR, font=font)
        x += image.width + PADDING

    return canvas


def main() -> int:
    print(f"OVERLAYS={OVERLAY_DIR}")
    print(f"CASES={','.join(CASES)}")
    sheet = build_contact_sheet()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT_PATH, format="JPEG", quality=92, optimize=True)
    print(f"OUTPUT={OUTPUT_PATH.resolve()}")
    print(f"SIZE={sheet.width}x{sheet.height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
