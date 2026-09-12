#!/usr/bin/env python3
"""Diagnostic lecture seule — V4 produit 0/26 détections (new_26).

Compare V2 best.pt et V4 best.pt sur les mêmes 26 images avec les mêmes
paramètres d'inférence, en balayant plusieurs seuils de confiance.

Ne modifie aucun poids, label, annotation ni run V2/V3.
"""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGES_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
V2_BEST = (
    PROJECT_ROOT
    / "runs"
    / "pose"
    / "runs"
    / "pose"
    / "runs"
    / "yolo_pose_new_26_v2-3"
    / "weights"
    / "best.pt"
)
V4_BEST = PROJECT_ROOT / "runs" / "pose" / "yolo_pose_new_26_v4" / "weights" / "best.pt"
V4_LAST = PROJECT_ROOT / "runs" / "pose" / "yolo_pose_new_26_v4" / "weights" / "last.pt"
V4_INIT = PROJECT_ROOT / "runs" / "pose" / "yolo_pose_new_26_v4" / "init" / "v2_best_mAP_epoch80.pt"
V4_RESULTS = PROJECT_ROOT / "runs" / "pose" / "yolo_pose_new_26_v4" / "results.csv"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v4_zero_detection_diagnosis.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v4_zero_detection_diagnosis.md"

CONF_THRESHOLDS = (0.001, 0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5)
INFERENCE_IMGSZ = 640
INFERENCE_IOU = 0.7
INFERENCE_MAX_DET = 300


@dataclass
class CheckpointSummary:
    label: str
    path: Path
    exists: bool
    size_bytes: int = 0
    sha256: str = ""
    epoch: object = None
    best_fitness: object = None
    nc: object = None
    kpt_shape: object = None
    train_lr0: object = None
    train_mosaic: object = None


@dataclass
class ConfSweepRow:
    model: str
    conf: float
    detections: int
    total: int
    mean_max_box_conf: float | None
    median_max_box_conf: float | None
    min_max_box_conf: float | None
    max_max_box_conf: float | None


@dataclass
class ImageDetail:
    case_id: str
    model: str
    conf_threshold: float
    n_boxes: int
    max_box_conf: float | None
    max_kpt_conf: float | None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_checkpoint_summary(label: str, path: Path) -> CheckpointSummary:
    if not path.is_file():
        return CheckpointSummary(label=label, path=path, exists=False)
    import torch

    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    model = ckpt.get("model")
    yaml_meta = getattr(model, "yaml", {}) if model is not None else {}
    train_args = ckpt.get("train_args", {})
    ta = dict(train_args) if hasattr(train_args, "items") else {}
    return CheckpointSummary(
        label=label,
        path=path,
        exists=True,
        size_bytes=path.stat().st_size,
        sha256=sha256_file(path),
        epoch=ckpt.get("epoch"),
        best_fitness=ckpt.get("best_fitness"),
        nc=yaml_meta.get("nc"),
        kpt_shape=yaml_meta.get("kpt_shape"),
        train_lr0=ta.get("lr0"),
        train_mosaic=ta.get("mosaic"),
    )


def list_images() -> list[Path]:
    images = sorted(IMAGES_DIR.glob("B26_*.png"))
    if len(images) != 26:
        raise SystemExit(f"Attendu 26 images dans {IMAGES_DIR}, trouvé {len(images)}")
    return images


def predict_all(model_path: Path, conf: float) -> list[tuple[str, object]]:
    from ultralytics import YOLO

    model = YOLO(str(model_path))
    images = list_images()
    results = model.predict(
        source=[str(p) for p in images],
        imgsz=INFERENCE_IMGSZ,
        conf=conf,
        iou=INFERENCE_IOU,
        max_det=INFERENCE_MAX_DET,
        verbose=False,
    )
    return [(images[i].stem, results[i]) for i in range(len(results))]


def extract_detection_stats(result) -> tuple[int, float | None, float | None]:
    boxes = result.boxes
    if boxes is None or len(boxes) == 0:
        return 0, None, None
    box_confs = boxes.conf.cpu().tolist()
    max_box = max(box_confs)
    max_kpt = None
    if result.keypoints is not None and result.keypoints.data is not None:
        kpt_data = result.keypoints.data
        if len(kpt_data) > 0:
            # shape: (n_det, n_kpt, 3) — x, y, conf
            max_kpt = float(kpt_data[..., 2].max().cpu())
    return len(box_confs), float(max_box), max_kpt


def sweep_confidence(model_label: str, model_path: Path) -> tuple[list[ConfSweepRow], list[ImageDetail]]:
    sweep_rows: list[ConfSweepRow] = []
    details: list[ImageDetail] = []
    for conf in CONF_THRESHOLDS:
        per_image = predict_all(model_path, conf)
        max_confs: list[float] = []
        det_count = 0
        for case_id, result in per_image:
            n_boxes, max_box, max_kpt = extract_detection_stats(result)
            if n_boxes > 0:
                det_count += 1
                if max_box is not None:
                    max_confs.append(max_box)
            details.append(
                ImageDetail(
                    case_id=case_id,
                    model=model_label,
                    conf_threshold=conf,
                    n_boxes=n_boxes,
                    max_box_conf=max_box,
                    max_kpt_conf=max_kpt,
                )
            )
        sweep_rows.append(
            ConfSweepRow(
                model=model_label,
                conf=conf,
                detections=det_count,
                total=26,
                mean_max_box_conf=statistics.mean(max_confs) if max_confs else None,
                median_max_box_conf=statistics.median(max_confs) if max_confs else None,
                min_max_box_conf=min(max_confs) if max_confs else None,
                max_max_box_conf=max(max_confs) if max_confs else None,
            )
        )
    return sweep_rows, details


def read_v4_training_pose_map() -> tuple[float | None, float | None]:
    if not V4_RESULTS.is_file():
        return None, None
    with V4_RESULTS.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        return None, None
    maps = [float(r["metrics/mAP50-95(P)"]) for r in rows if r.get("metrics/mAP50-95(P)")]
    epochs = [int(float(r["epoch"])) for r in rows if r.get("epoch")]
    if not maps:
        return None, None
    best_idx = max(range(len(maps)), key=lambda i: maps[i])
    return maps[best_idx], maps[-1]


def infer_verdict(
    v2_sweep: list[ConfSweepRow],
    v4_sweep: list[ConfSweepRow],
    v4_init_sweep: list[ConfSweepRow] | None,
    ckpts: dict[str, CheckpointSummary],
) -> tuple[str, list[str]]:
    lines: list[str] = []
    v2_at_025 = next(r for r in v2_sweep if r.conf == 0.25)
    v4_at_025 = next(r for r in v4_sweep if r.conf == 0.25)
    v4_at_0001 = next(r for r in v4_sweep if r.conf == 0.001)

    lines.append(
        f"V2 @ conf=0.25 : **{v2_at_025.detections}/26** détections "
        f"(médiane max box conf = {v2_at_025.median_max_box_conf})"
    )
    lines.append(
        f"V4 best @ conf=0.25 : **{v4_at_025.detections}/26** détections "
        f"(médiane max box conf = {v4_at_025.median_max_box_conf})"
    )
    lines.append(
        f"V4 best @ conf=0.001 : **{v4_at_0001.detections}/26** détections "
        f"(médiane max box conf = {v4_at_0001.median_max_box_conf})"
    )

    if v4_init_sweep:
        init_at_025 = next(r for r in v4_init_sweep if r.conf == 0.25)
        lines.append(f"V4 init (copie V2) @ conf=0.25 : **{init_at_025.detections}/26**")

    v2_ckpt = ckpts["V2 best"]
    v4_ckpt = ckpts["V4 best"]
    init_ckpt = ckpts.get("V4 init")

    if init_ckpt and init_ckpt.exists and v2_ckpt.sha256 == init_ckpt.sha256:
        lines.append("V4 init est bit-identique à V2 best (init OK).")
    elif init_ckpt and init_ckpt.exists:
        lines.append("V4 init **diffère** de V2 best (SHA256 différent).")

    best_map, final_map = read_v4_training_pose_map()
    if best_map is not None:
        lines.append(f"Entraînement V4 : mAP50-95(P) best={best_map:.4f}, final={final_map:.4f}")
        if best_map == 0.0 and final_map == 0.0:
            lines.append("Courbe V4 : mAP pose **nul sur tous les epochs** — tête pose / confiance effondrée.")

    if v4_at_0001.detections == 0:
        code = "A"
        lines.append(
            "**Verdict A** : aucune détection même à conf=0.001 — effondrement complet de la tête de détection "
            "(pas un simple seuil conf trop élevé)."
        )
    elif v4_at_025.detections == 0 and v4_at_0001.detections > 0:
        code = "B"
        lines.append(
            "**Verdict B** : détections présentes à conf basse mais filtrées à conf=0.25 — "
            "confiance box post-entraînement très faible."
        )
    else:
        code = "C"
        lines.append("**Verdict C** : comportement atypique — analyser le détail par image.")

    if v4_init_sweep:
        init_at_025 = next(r for r in v4_init_sweep if r.conf == 0.25)
        v4_best_at_025 = v4_at_025
        if init_at_025.detections == 26 and v4_best_at_025.detections == 0:
            lines.append(
                "V4 init détecte 26/26 mais V4 best 0/26 → la dégradation est survenue **pendant** le fine-tuning."
            )

    if v2_ckpt.kpt_shape != v4_ckpt.kpt_shape:
        lines.append(f"ATTENTION kpt_shape diffère : V2={v2_ckpt.kpt_shape}, V4={v4_ckpt.kpt_shape}")

    return code, lines


def write_outputs(
    ckpts: dict[str, CheckpointSummary],
    sweeps: list[ConfSweepRow],
    details: list[ImageDetail],
    verdict_code: str,
    verdict_lines: list[str],
) -> None:
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "section",
                "model",
                "conf",
                "case_id",
                "detections",
                "total",
                "n_boxes",
                "max_box_conf",
                "max_kpt_conf",
                "mean_max_box_conf",
                "median_max_box_conf",
                "min_max_box_conf",
                "checkpoint_epoch",
                "checkpoint_sha256",
                "kpt_shape",
            ],
        )
        writer.writeheader()
        for label, ckpt in ckpts.items():
            writer.writerow(
                {
                    "section": "checkpoint",
                    "model": label,
                    "checkpoint_epoch": ckpt.epoch,
                    "checkpoint_sha256": ckpt.sha256[:16] if ckpt.sha256 else "",
                    "kpt_shape": str(ckpt.kpt_shape),
                }
            )
        for row in sweeps:
            writer.writerow(
                {
                    "section": "conf_sweep",
                    "model": row.model,
                    "conf": row.conf,
                    "detections": row.detections,
                    "total": row.total,
                    "mean_max_box_conf": row.mean_max_box_conf,
                    "median_max_box_conf": row.median_max_box_conf,
                    "min_max_box_conf": row.min_max_box_conf,
                    "max_box_conf": row.max_max_box_conf,
                }
            )
        for d in details:
            writer.writerow(
                {
                    "section": "per_image",
                    "model": d.model,
                    "conf": d.conf_threshold,
                    "case_id": d.case_id,
                    "n_boxes": d.n_boxes,
                    "max_box_conf": d.max_box_conf,
                    "max_kpt_conf": d.max_kpt_conf,
                }
            )

    md_lines = [
        "# Diagnostic V4 — 0/26 détections",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "**Mode :** lecture seule — aucun poids modifié",
        "",
        "## Contexte",
        "",
        "- V2 inference : **26/26**",
        "- V3 inference : **25/26**",
        "- V4 inference : **0/26** (0 label saved)",
        "",
        f"Images : `{IMAGES_DIR.relative_to(PROJECT_ROOT).as_posix()}` (26 PNG identiques V2/V3/V4)",
        "",
        f"Paramètres inférence communs : imgsz={INFERENCE_IMGSZ}, iou={INFERENCE_IOU}, max_det={INFERENCE_MAX_DET}",
        "",
        "## Checkpoints",
        "",
        "| Modèle | Existe | Epoch | kpt_shape | SHA256 (16) | Taille |",
        "|--------|--------|-------|-----------|-------------|--------|",
    ]
    for label, ckpt in ckpts.items():
        md_lines.append(
            f"| {label} | {'oui' if ckpt.exists else 'non'} | {ckpt.epoch} | {ckpt.kpt_shape} | "
            f"{ckpt.sha256[:16] if ckpt.sha256 else 'NA'} | {ckpt.size_bytes} |"
        )

    md_lines.extend(
        [
            "",
            "## Balayage confiance (détections / 26)",
            "",
            "| Modèle | conf | détections | médiane max box conf | min | max |",
            "|--------|------|------------|----------------------|-----|-----|",
        ]
    )
    for row in sweeps:
        md_lines.append(
            f"| {row.model} | {row.conf} | {row.detections}/26 | "
            f"{row.median_max_box_conf} | {row.min_max_box_conf} | {row.max_max_box_conf} |"
        )

    md_lines.extend(["", f"## Verdict : **{verdict_code}**", ""] + [f"- {line}" for line in verdict_lines])
    md_lines.extend(["", f"CSV : `{OUTPUT_CSV.name}`", ""])
    OUTPUT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def main() -> int:
    for path in (V2_BEST, V4_BEST):
        if not path.is_file():
            raise SystemExit(f"Checkpoint introuvable : {path}")
    if not IMAGES_DIR.is_dir():
        raise SystemExit(f"Images introuvables : {IMAGES_DIR}")

    ckpts = {
        "V2 best": load_checkpoint_summary("V2 best", V2_BEST),
        "V4 best": load_checkpoint_summary("V4 best", V4_BEST),
        "V4 last": load_checkpoint_summary("V4 last", V4_LAST),
        "V4 init": load_checkpoint_summary("V4 init", V4_INIT),
    }

    all_sweeps: list[ConfSweepRow] = []
    all_details: list[ImageDetail] = []

    models_to_test = [
        ("V2 best", V2_BEST),
        ("V4 best", V4_BEST),
    ]
    if V4_INIT.is_file():
        models_to_test.append(("V4 init", V4_INIT))
    if V4_LAST.is_file() and V4_LAST.resolve() != V4_BEST.resolve():
        models_to_test.append(("V4 last", V4_LAST))

    v4_init_sweep: list[ConfSweepRow] | None = None
    v2_sweep: list[ConfSweepRow] = []
    v4_sweep: list[ConfSweepRow] = []

    for label, path in models_to_test:
        print(f"SWEEP {label} ...")
        sweep, details = sweep_confidence(label, path)
        all_sweeps.extend(sweep)
        all_details.extend(details)
        if label == "V2 best":
            v2_sweep = sweep
        elif label == "V4 best":
            v4_sweep = sweep
        elif label == "V4 init":
            v4_init_sweep = sweep

    verdict_code, verdict_lines = infer_verdict(v2_sweep, v4_sweep, v4_init_sweep, ckpts)
    write_outputs(ckpts, all_sweeps, all_details, verdict_code, verdict_lines)

    v2_025 = next(r for r in v2_sweep if r.conf == 0.25)
    v4_025 = next(r for r in v4_sweep if r.conf == 0.25)
    v4_001 = next(r for r in v4_sweep if r.conf == 0.001)

    print("V4 ZERO DETECTION DIAGNOSIS COMPLETE")
    print(f"VERDICT={verdict_code}")
    print(f"V2 detections @ conf=0.25: {v2_025.detections}/26")
    print(f"V4 detections @ conf=0.25: {v4_025.detections}/26")
    print(f"V4 detections @ conf=0.001: {v4_001.detections}/26")
    print(f"REPORT={OUTPUT_MD.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
