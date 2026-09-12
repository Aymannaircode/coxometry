"""
Real Retuve YOLO X-ray inference test (no simulated results).
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

os.environ["RETUVE_DISABLE_WARNING"] = "True"

from PIL import Image
from ultralytics import YOLO

from retuve.defaults.hip_configs import default_xray
from retuve.funcs import analyse_hip_xray_2D
from retuve.testdata import Cases, download_case
from retuve_yolo_plugin.xray_pose import WEIGHTS, yolo_predict_xray

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "artifacts"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESULT_JSON = OUT_DIR / "retuve_inference_raw.json"
ANNOTATED_PATH = OUT_DIR / "retuve_xray_annotated.jpg"
RAW_IMG_COPY = OUT_DIR / "retuve_xray_input.jpg"


def main() -> int:
    report: dict = {
        "status": "started",
        "error": None,
        "python": sys.version,
        "weights": WEIGHTS,
        "weights_exists": os.path.exists(WEIGHTS),
        "image_source": None,
        "image_path": None,
        "image_size": None,
        "raw_yolo": {},
        "retuve_landmarks": {},
        "retuve_metrics": None,
        "annotated_image": None,
    }

    try:
        print("=== Download official Retuve XRAY_JPG ===")
        img_file, labels_json = download_case(Cases.XRAY_JPG)
        report["image_source"] = "Cases.XRAY_JPG (radoss-creative-commons / Retuve testdata)"
        report["image_path"] = str(img_file)
        report["labels_json_path"] = str(labels_json)
        report["image_size_bytes"] = os.path.getsize(img_file)

        img_raw = Image.open(img_file).convert("RGB")
        report["image_size"] = {"width": img_raw.width, "height": img_raw.height}
        img_raw.save(RAW_IMG_COPY)
        print(f"Image: {img_file} ({img_raw.width}x{img_raw.height})")

        print("=== Load YOLO X-ray pose model ===")
        print(f"Weights: {WEIGHTS}")
        if not os.path.exists(WEIGHTS):
            raise FileNotFoundError(f"Weights not found: {WEIGHTS}")

        model = YOLO(WEIGHTS)
        model.to("cpu")
        default_xray.device = "cpu"

        print("=== Raw YOLO predict (for confidence scores) ===")
        raw_results = model.predict(
            [img_raw],
            imgsz=800,
            conf=0.5,
            verbose=True,
            device="cpu",
        )
        raw_detections = []
        for result in raw_results:
            boxes = result.boxes
            kpts = result.keypoints
            n = len(boxes) if boxes is not None else 0
            print(f"Raw detections: {n}")
            if boxes is None or n == 0:
                continue
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            clss = boxes.cls.cpu().numpy()
            kxy = kpts.xy.cpu().numpy() if kpts is not None else None
            kconf = None
            if kpts is not None and getattr(kpts, "conf", None) is not None:
                kconf = kpts.conf.cpu().numpy()
            for i in range(n):
                det = {
                    "class_id": int(clss[i]),
                    "box_confidence": float(confs[i]),
                    "box_xyxy": [float(x) for x in xyxy[i].tolist()],
                    "keypoints_xy": (
                        kxy[i].tolist() if kxy is not None else None
                    ),
                    "keypoints_conf": (
                        kconf[i].tolist() if kconf is not None else None
                    ),
                }
                raw_detections.append(det)
                print(
                    f"  det[{i}] class={det['class_id']} "
                    f"box_conf={det['box_confidence']:.4f} "
                    f"kpts={det['keypoints_xy']}"
                )
        report["raw_yolo"] = {
            "num_detections": len(raw_detections),
            "detections": raw_detections,
        }

        print("=== Retuve analyse_hip_xray_2D with yolo_predict_xray ===")
        hip_data, annotated_img, dev_metrics = analyse_hip_xray_2D(
            img_raw,
            keyphrase=default_xray,
            modes_func=yolo_predict_xray,
            modes_func_kwargs_dict={},
        )

        landmarks = hip_data.landmarks
        lm_dict = {}
        if landmarks is not None:
            for name, value in landmarks.items():
                lm_dict[name] = list(value) if value is not None else None
                print(f"  landmark {name}: {lm_dict[name]}")
        else:
            print("  landmarks object is None")
        report["retuve_landmarks"] = lm_dict

        metrics = hip_data.json_dump(default_xray, dev_metrics)
        report["retuve_metrics"] = metrics
        print("Metrics:")
        print(json.dumps(metrics, indent=2))

        if hasattr(hip_data, "recorded_error") and hip_data.recorded_error:
            report["recorded_error"] = str(hip_data.recorded_error)
            print(f"Recorded error: {hip_data.recorded_error}")

        annotated_img.save(ANNOTATED_PATH)
        report["annotated_image"] = str(ANNOTATED_PATH)
        print(f"Annotated image saved: {ANNOTATED_PATH}")

        report["status"] = "success"

    except Exception as e:
        report["status"] = "error"
        report["error"] = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        print("ERROR:", e)
        print(traceback.format_exc())

    RESULT_JSON.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Raw report JSON: {RESULT_JSON}")
    return 0 if report["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
