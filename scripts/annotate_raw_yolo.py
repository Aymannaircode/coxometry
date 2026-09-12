"""Draw annotated image from real raw YOLO detections only."""
import json
from pathlib import Path

from PIL import Image, ImageDraw

raw = json.loads(Path("docs/artifacts/retuve_inference_raw.json").read_text(encoding="utf-8"))
img = Image.open("docs/artifacts/retuve_xray_input.jpg").convert("RGB")
draw = ImageDraw.Draw(img)
colors = {0: (0, 255, 0), 1: (255, 80, 80)}
class_names = {0: "hip_pelvis", 1: "hip_femour"}

for det in raw["raw_yolo"]["detections"]:
    c = colors.get(det["class_id"], (255, 255, 0))
    x1, y1, x2, y2 = det["box_xyxy"]
    draw.rectangle([x1, y1, x2, y2], outline=c, width=2)
    draw.text(
        (x1, max(0, y1 - 12)),
        f"{class_names.get(det['class_id'], det['class_id'])} {det['box_confidence']:.3f}",
        fill=c,
    )
    if det["keypoints_xy"]:
        for i, (x, y) in enumerate(det["keypoints_xy"]):
            r = 3
            draw.ellipse([x - r, y - r, x + r, y + r], fill=c)
            conf = det["keypoints_conf"][i] if det.get("keypoints_conf") else None
            label = f"k{i}"
            if conf is not None:
                label += f" {conf:.2f}"
            draw.text((x + 4, y - 8), label, fill=c)

out = Path("docs/artifacts/retuve_xray_annotated_raw_yolo.jpg")
img.save(out)
print(f"saved {out}")
print("NOTE: annotated from raw YOLO detections only; Retuve analyse_hip_xray_2D failed")
