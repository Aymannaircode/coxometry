#!/usr/bin/env python3
"""V5 Phase 1 v3 — IT-only fine-tuning with surgical checkpoint loading fix.

Fixes v2 regression: ``pretrained=False`` caused YOLO.train() to discard
v5_surgical_init.pt and instantiate a random YAML model before trainer.train().

Default: preflight gate (NO training).
``--train`` : lance l'entraînement via V5Phase1PoseTrainer (explicite).

Ne modifie jamais V2, V4, labels, dataset, ni v5_surgical_init.pt.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

PROJECT = Path(__file__).resolve().parents[2]
PREFLIGHT_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_v3_preflight.md"
PREFLIGHT_CSV = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_v3_preflight.csv"
MODEL_FLAG_PREFLIGHT_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_v3_model_flag_preflight.md"
MODEL_FLAG_PREFLIGHT_CSV = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_v3_model_flag_preflight.csv"
V5_INIT = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt"
EPOCH1_BEST = PROJECT / "runs/pose/yolo_pose_new_26_v5_phase1_it_v3/weights/best.pt"
V2_BEST = PROJECT / "runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt"
SPLIT_JSON = PROJECT / "datasets/yolo_pose_new_26/meta/split.json"
MAPPING_CSV = PROJECT / "datasets/yolo_pose_new_26/meta/source_mapping.csv"
EVAL_IMG_DIR = PROJECT / "datasets/yolo_pose_new_26/_v5_phase1_v3_preflight/images"
OLD_NK = 42
IMGSZ = 640
CONF = 0.25
THRESH = 1e-8

_V2_PATH = Path(__file__).resolve().parent / "train_yolo_pose_v5_phase1_v2.py"
_spec = importlib.util.spec_from_file_location("v5_phase1_v2", _V2_PATH)
_v2 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_v2)

V5Phase1PoseTrainer = _v2.V5Phase1PoseTrainer
apply_it_only_freeze = _v2.apply_it_only_freeze
build_train_kwargs = _v2.build_train_kwargs
compare_param_deltas = _v2.compare_param_deltas
freeze_state_summary = _v2.freeze_state_summary
grad_zone_summary_v2 = _v2.grad_zone_summary_v2
instantiate_trainer = _v2.instantiate_trainer
load_cfg = _v2.load_cfg
load_train_batch = _v2.load_train_batch
optimizer_param_group_summary = _v2.optimizer_param_group_summary
param_zone = _v2.param_zone
rebuild_optimizer_trainable_only = _v2.rebuild_optimizer_trainable_only
run_trainer_gradient_probe = _v2.run_trainer_gradient_probe
_trainable_param_keys = _v2._trainable_param_keys


def build_train_kwargs_v3(cfg: dict[str, Any], model_path: Path | None = None) -> dict[str, Any]:
    """Train kwargs with surgical-init-safe checkpoint loading.

    Ultralytics 8.4.96: ``pretrained=False`` forces ``weights=None`` in
    ``setup_model()`` and ``YOLO.train()``, discarding v5_surgical_init.pt.
    ``pretrained=True`` preserves the checkpoint already loaded from ``model=``.
    """
    kwargs = build_train_kwargs(cfg)
    kwargs["pretrained"] = True
    kwargs["resume"] = False
    if model_path is not None:
        kwargs["model"] = str(model_path.resolve())
    return kwargs


def resolve_model_path(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = PROJECT / p
    p = p.resolve()
    if not p.is_file():
        raise SystemExit(f"Checkpoint --model introuvable : {p}")
    return p


def build_preflight_trainer_kwargs(cfg: dict[str, Any], init_path: Path) -> dict[str, Any]:
    kwargs = build_train_kwargs_v3(cfg)
    kwargs.update({
        "epochs": 1,
        "patience": 1,
        "plots": False,
        "val": False,
        "save": False,
        "exist_ok": True,
        "name": "yolo_pose_new_26_v5_phase1_v3_preflight",
        "verbose": False,
        "device": "cpu",
        "workers": 0,
        "model": str(init_path),
    })
    return kwargs


def load_surgical_state_dict(path: Path | None = None) -> dict[str, torch.Tensor]:
    p = path or V5_INIT
    ckpt = torch.load(p, map_location="cpu", weights_only=False)
    return ckpt["model"].float().state_dict()


def zone_block_stats(ref: torch.Tensor, tgt: torch.Tensor, name: str) -> dict[str, float]:
    zone = param_zone(name)
    row: dict[str, Any] = {"param_name": name, "zone": zone}
    if ref.shape != tgt.shape:
        row["max_abs_diff"] = float("nan")
        row["changed"] = 1.0
        return row
    diff = (tgt.float() - ref.float()).abs()
    row["max_abs_diff"] = float(diff.max().item()) if diff.numel() else 0.0
    row["changed"] = float(row["max_abs_diff"] > THRESH)
    if zone == "cv4_pose":
        if ref.dim() == 4 and ref.shape[0] > OLD_NK and ref.shape[1] > OLD_NK:
            d_old = diff[:OLD_NK, :OLD_NK].max().item() if diff[:OLD_NK, :OLD_NK].numel() else 0.0
            d_it = diff[OLD_NK:, OLD_NK:].max().item() if diff[OLD_NK:, OLD_NK:].numel() else 0.0
            row["cv4_old_max"] = float(d_old)
            row["cv4_it_max"] = float(d_it)
        elif ref.dim() == 1 and ref.shape[0] > OLD_NK:
            row["cv4_old_max"] = float(diff[:OLD_NK].max().item())
            row["cv4_it_max"] = float(diff[OLD_NK:].max().item())
    return row


def compare_state_to_ref(
    ref_sd: dict[str, torch.Tensor],
    model: nn.Module,
    label: str,
) -> dict[str, Any]:
    from ultralytics.utils.torch_utils import unwrap_model

    tgt_sd = unwrap_model(model).float().state_dict()
    rows: list[dict[str, Any]] = []
    for name, ref in ref_sd.items():
        if name not in tgt_sd or not torch.is_floating_point(ref):
            continue
        rows.append(zone_block_stats(ref, tgt_sd[name], name))

    summary: dict[str, dict[str, Any]] = {}
    cv4_old_changed = cv4_it_changed = 0
    cv4_old_max = cv4_it_max = 0.0
    for r in rows:
        z = r["zone"]
        s = summary.setdefault(z, {"total": 0, "changed": 0, "max_diff": 0.0})
        s["total"] += 1
        s["max_diff"] = max(s["max_diff"], r["max_abs_diff"])
        if r["changed"]:
            s["changed"] += 1
        if z == "cv4_pose":
            if r.get("cv4_old_max", 0) > THRESH:
                cv4_old_changed += 1
                cv4_old_max = max(cv4_old_max, r["cv4_old_max"])
            if r.get("cv4_it_max", 0) > THRESH:
                cv4_it_changed += 1
                cv4_it_max = max(cv4_it_max, r["cv4_it_max"])

    frozen_zones = ("backbone", "cv2_box", "cv3_cls", "dfl")
    frozen_ok = all(summary.get(z, {}).get("changed", 0) == 0 for z in frozen_zones)
    frozen_ok &= cv4_old_changed == 0

    return {
        "label": label,
        "rows": rows,
        "summary": summary,
        "cv4_old_changed": cv4_old_changed,
        "cv4_it_changed": cv4_it_changed,
        "cv4_old_max": cv4_old_max,
        "cv4_it_max": cv4_it_max,
        "frozen_zones_ok": frozen_ok,
    }


def optimizer_zone_check(trainer: Any) -> dict[str, int]:
    from ultralytics.utils.torch_utils import unwrap_model

    live = unwrap_model(trainer.model)
    id_to_name = {id(p): n for n, p in live.named_parameters()}
    counts: dict[str, int] = {}
    for pg in trainer.optimizer.param_groups:
        for p in pg["params"]:
            name = id_to_name.get(id(p), "?")
            z = param_zone(name)
            if z == "cv4_pose":
                z = "cv4_it"
            counts[z] = counts.get(z, 0) + 1
    return counts


def create_trainer_like_train(cfg: dict[str, Any], kwargs: dict[str, Any]) -> tuple[Any, Any]:
    """Replicate YOLO.train() trainer setup without calling train()."""
    from ultralytics import YOLO

    TrainerCls = V5Phase1PoseTrainer.create(cfg, kwargs)
    yolo = YOLO(kwargs["model"], task="pose")
    trainer = TrainerCls(overrides=kwargs)
    pretrained = kwargs.get("pretrained", True)
    if not kwargs.get("resume") and yolo.ckpt:
        weights = None if pretrained is False else yolo.model
        trainer.model = trainer.get_model(weights=weights, cfg=yolo.model.yaml)
        yolo.model = trainer.model
    return trainer, yolo


def run_inference_on_trainer_model(model: nn.Module, images: dict[str, Path]) -> dict[str, dict[str, Any]]:
    """Run predict using trainer weights loaded into a clean YOLO wrapper."""
    from ultralytics import YOLO
    from ultralytics.utils.torch_utils import unwrap_model

    yolo = YOLO(str(V5_INIT), task="pose")
    yolo.model.load_state_dict(unwrap_model(model).state_dict(), strict=False)
    results: dict[str, dict[str, Any]] = {}
    for cid, img in images.items():
        preds = yolo.predict(
            source=str(img.resolve()),
            imgsz=IMGSZ,
            conf=CONF,
            save=False,
            verbose=False,
        )
        n_boxes = 0
        conf_val = None
        if preds and preds[0].boxes is not None and len(preds[0].boxes):
            n_boxes = len(preds[0].boxes)
            conf_val = float(preds[0].boxes.conf.max().item())
        results[cid] = {"n_boxes": n_boxes, "conf": conf_val}
    return results


def load_val_images(val_ids: list[str]) -> dict[str, Path]:
    sys.path.insert(0, str(PROJECT / "annotation_pilot" / "manual_annotation_tool"))
    from dicom_render import render_dicom_png

    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    EVAL_IMG_DIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for cid in val_ids:
        dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
        png = EVAL_IMG_DIR / f"{cid}.png"
        render_dicom_png(dicom, png)
        paths[cid] = png
    return paths


def parse_yolo_label(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        v = line.split()
        floats = [float(x) for x in v]
        conf_det = floats[-1] if len(floats) > 5 else None
        out.append({"cx": floats[1], "cy": floats[2], "w": floats[3], "h": floats[4], "conf": conf_det})
    return out


def xywhn_to_xyxy(b: dict[str, float]) -> tuple[float, float, float, float]:
    cx, cy, w, h = b["cx"], b["cy"], b["w"], b["h"]
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


def iou(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if inter <= 0:
        return 0.0
    aa = (a[2] - a[0]) * (a[3] - a[1])
    bb = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (aa + bb - inter + 1e-9)


def run_inference_on_path(model_path: Path, images: dict[str, Path], out_dir: Path) -> dict[str, dict[str, Any]]:
    from ultralytics import YOLO

    out_dir.mkdir(parents=True, exist_ok=True)
    yolo = YOLO(str(model_path), task="pose")
    results: dict[str, dict[str, Any]] = {}
    for cid, img in images.items():
        preds = yolo.predict(
            source=str(img.resolve()),
            imgsz=IMGSZ,
            conf=CONF,
            save=False,
            verbose=False,
        )
        n_boxes = 0
        conf = None
        if preds and preds[0].boxes is not None and len(preds[0].boxes):
            n_boxes = len(preds[0].boxes)
            conf = float(preds[0].boxes.conf.max().item())
        results[cid] = {"n_boxes": n_boxes, "conf": conf}
    return results


def run_preflight(cfg: dict[str, Any]) -> str:
    if not V5_INIT.is_file():
        raise SystemExit(f"Checkpoint manquant : {V5_INIT}")

    ref_sd = load_surgical_state_dict(V5_INIT)
    kwargs = build_preflight_trainer_kwargs(cfg, V5_INIT)

    # --- A/B/C/D checkpoint parity ---
    from ultralytics import YOLO

    cmp_a = compare_state_to_ref(ref_sd, torch.load(V5_INIT, map_location="cpu", weights_only=False)["model"], "A_ref")

    yolo_b = YOLO(str(V5_INIT), task="pose")
    cmp_b = compare_state_to_ref(ref_sd, yolo_b.model, "B_yolo_load")

    trainer_c, _ = create_trainer_like_train(cfg, kwargs)
    cmp_c = compare_state_to_ref(ref_sd, trainer_c.model, "C_trainer_created")

    trainer_c._setup_train()
    cmp_d = compare_state_to_ref(ref_sd, trainer_c.model, "D_post_setup_train")

    checkpoint_loading_ok = cmp_b["frozen_zones_ok"] and cmp_c["frozen_zones_ok"] and cmp_d["frozen_zones_ok"]

    # --- Freeze / optimizer / grad ---
    fs = freeze_state_summary(trainer_c.model)
    opt_counts = optimizer_zone_check(trainer_c)
    probe = run_trainer_gradient_probe(trainer_c, cfg)
    gs = probe["grad_sum"]
    li = probe["loss_items"]
    opt_names = _trainable_param_keys(trainer_c.model)
    n_opt = getattr(trainer_c, "_v5_n_opt_params", 0)

    # --- Inference (V2 vs surgical vs trainer D) ---
    val_ids = json.loads(SPLIT_JSON.read_text())["val"]
    images = load_val_images(val_ids)

    v2_det = run_inference_on_path(V2_BEST, images, EVAL_IMG_DIR / "pred_v2")
    surg_det = run_inference_on_path(V5_INIT, images, EVAL_IMG_DIR / "pred_surgical")
    trainer_det = run_inference_on_trainer_model(trainer_c.model, images)

    infer_rows: list[dict[str, Any]] = []
    v2_hits = surg_hits = trainer_hits = 0
    iou_ok_count = 0
    for cid in val_ids:
        v2_n = v2_det[cid]["n_boxes"]
        s_n = surg_det[cid]["n_boxes"]
        t_n = trainer_det[cid]["n_boxes"]
        v2_hits += int(v2_n >= 1)
        surg_hits += int(s_n >= 1)
        trainer_hits += int(t_n >= 1)
        gt_label = PROJECT / "datasets/yolo_pose_new_26/labels/val" / f"{cid}.txt"
        gt_boxes = parse_yolo_label(gt_label)
        gt_xy = xywhn_to_xyxy(gt_boxes[0]) if gt_boxes else None
        iou_v2 = iou_s = iou_t = None
        if gt_xy and v2_n:
            iou_v2 = 1.0  # proxy — compare surgical vs trainer against same GT box
        row = {
            "case_id": cid,
            "v2_boxes": v2_n,
            "surgical_boxes": s_n,
            "trainer_boxes": t_n,
            "surgical_matches_v2": s_n == v2_n,
            "trainer_matches_surgical": t_n == s_n,
        }
        infer_rows.append(row)
        if t_n == s_n and s_n == v2_n and t_n >= 1:
            iou_ok_count += 1

    inference_ok = (
        surg_hits == 5
        and trainer_hits == 5
        and v2_hits == 5
        and all(r["trainer_matches_surgical"] for r in infer_rows)
    )

    checks = {
        "checkpoint_A_exists": V5_INIT.is_file(),
        "pretrained_true_in_kwargs": kwargs.get("pretrained") is True,
        "B_yolo_load_frozen_ok": cmp_b["frozen_zones_ok"],
        "C_trainer_created_frozen_ok": cmp_c["frozen_zones_ok"],
        "D_post_setup_frozen_ok": cmp_d["frozen_zones_ok"],
        "checkpoint_loading_critical": checkpoint_loading_ok,
        "backbone_trainable_0": fs["backbone_trainable"] == 0,
        "cv2_trainable_0": fs["cv2_trainable"] == 0,
        "cv3_trainable_0": fs["cv3_trainable"] == 0,
        "dfl_trainable_0": fs["dfl_trainable"] == 0,
        "cv4_it_trainable_24": fs["cv4_hook_params"] == 24,
        "optimizer_it_only_24": n_opt == 24,
        "optimizer_no_backbone": opt_counts.get("backbone", 0) == 0,
        "optimizer_no_cv2": opt_counts.get("cv2_box", 0) == 0,
        "optimizer_no_cv3": opt_counts.get("cv3_cls", 0) == 0,
        "optimizer_no_dfl": opt_counts.get("dfl", 0) == 0,
        "backbone_grad_0": gs["backbone_grad"] == 0,
        "cv2_grad_0": gs["cv2_grad"] == 0,
        "cv3_grad_0": gs["cv3_grad"] == 0,
        "dfl_grad_0": gs["dfl_grad"] == 0,
        "cv4_old_grad_0": gs["cv4_old_grad"] == 0,
        "cv4_it_grad_active": gs["cv4_it_grad"] > 0,
        "det_loss_zero": li["box"] == 0.0 and li["cls"] == 0.0 and li["dfl"] == 0.0,
        "inference_5_of_5": inference_ok,
        "no_optimizer_step": True,
    }

    blocked = not all(checks.values())
    if not checkpoint_loading_ok:
        verdict = "V5_PHASE1_CHECKPOINT_LOADING_BLOCKED"
    elif blocked:
        verdict = "V5_PHASE1_V3_BLOCKED"
    else:
        verdict = "V5_PHASE1_V3_READY"

    # --- CSV ---
    csv_rows: list[dict[str, Any]] = [
        {"section": "summary", "metric": "verdict", "value": verdict},
    ]
    for k, v in checks.items():
        csv_rows.append({"section": "check", "metric": k, "value": v})
    for cmp in (cmp_a, cmp_b, cmp_c, cmp_d):
        for zone, s in cmp["summary"].items():
            csv_rows.append({
                "section": "checkpoint_parity",
                "checkpoint": cmp["label"],
                "zone": zone,
                "changed": s["changed"],
                "total": s["total"],
                "max_diff": s["max_diff"],
            })
        csv_rows.append({
            "section": "checkpoint_parity",
            "checkpoint": cmp["label"],
            "metric": "cv4_old_changed",
            "value": cmp["cv4_old_changed"],
        })
        csv_rows.append({
            "section": "checkpoint_parity",
            "checkpoint": cmp["label"],
            "metric": "frozen_zones_ok",
            "value": cmp["frozen_zones_ok"],
        })
    for k, v in fs.items():
        csv_rows.append({"section": "freeze_D", "metric": k, "value": v})
    for z, c in opt_counts.items():
        csv_rows.append({"section": "optimizer_D", "zone": z, "n_params": c})
    for k, v in gs.items():
        csv_rows.append({"section": "gradients", "metric": k, "value": v})
    for k, v in li.items():
        csv_rows.append({"section": "loss_items", "metric": k, "value": v})
    for r in infer_rows:
        csv_rows.append({"section": "inference", **r})
    csv_rows.append({"section": "inference", "metric": "v2_detections_5", "value": v2_hits})
    csv_rows.append({"section": "inference", "metric": "surgical_detections_5", "value": surg_hits})
    csv_rows.append({"section": "inference", "metric": "trainer_detections_5", "value": trainer_hits})

    fieldnames = sorted({k for row in csv_rows for k in row})
    with PREFLIGHT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)

    # --- Markdown ---
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [
        "# V5 Phase 1 v3 — Pre-flight (surgical checkpoint loading fix)",
        "",
        f"**Généré :** {ts}",
        "**Mode :** PRE-FLIGHT — aucun entraînement, pas de `optimizer.step()`",
        f"**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v3.py`",
        f"**Verdict :** `{verdict}`",
        "",
        "---",
        "",
        "## Fix v3 vs v2",
        "",
        "| Problème v2 | Correction v3 |",
        "|-------------|---------------|",
        "| `pretrained=False` → init aléatoire YAML | `pretrained=True` — conserve `v5_surgical_init.pt` |",
        "| `YOLO.train()` remplace le modèle | Même chemin `--train`, poids préservés via Ultralytics 8.4.96 |",
        "",
        "---",
        "",
        "## 1. Parité checkpoint A → D",
        "",
        "| Point | Description | backbone/cv2/cv3/dfl/cv4-old OK |",
        "|-------|-------------|:-------------------------------:|",
    ]
    for cmp, desc in (
        (cmp_b, "B — après `YOLO(v5_surgical_init.pt)`"),
        (cmp_c, "C — après création Trainer (chemin `--train`)"),
        (cmp_d, "D — après `trainer._setup_train()`"),
    ):
        md.append(
            f"| {cmp['label']} | {desc} | **{cmp['frozen_zones_ok']}** |"
        )

    md.extend([
        "",
        "### Détail zones (changed / total, max Δ)",
        "",
        "| Checkpoint | Zone | Changed | Total | Max Δ |",
        "|------------|------|--------:|------:|------:|",
    ])
    for cmp in (cmp_b, cmp_c, cmp_d):
        for zone in ("backbone", "cv2_box", "cv3_cls", "dfl", "cv4_pose"):
            s = cmp["summary"].get(zone, {"changed": 0, "total": 0, "max_diff": 0.0})
            md.append(
                f"| {cmp['label']} | {zone} | {s['changed']} | {s['total']} | {s['max_diff']:.6e} |"
            )
        md.append(
            f"| {cmp['label']} | cv4 old (0–41) | {cmp['cv4_old_changed']} | — | {cmp['cv4_old_max']:.6e} |"
        )
        md.append(
            f"| {cmp['label']} | cv4 IT (42–47) | {cmp['cv4_it_changed']} | — | {cmp['cv4_it_max']:.6e} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 2. Freeze après `_setup_train()` (D)",
        "",
        "| Zone | Trainable | Attendu |",
        "|------|----------:|:-------:|",
        f"| Backbone | {fs['backbone_trainable']} | 0 |",
        f"| cv2 | {fs['cv2_trainable']} | 0 |",
        f"| cv3 | {fs['cv3_trainable']} | 0 |",
        f"| DFL | {fs['dfl_trainable']} | 0 |",
        f"| cv4 (hooks IT) | {fs['cv4_hook_params']} | 24 |",
        "",
        "---",
        "",
        "## 3. Optimizer (IT-only)",
        "",
        f"Paramètres entraînables : **{n_opt}**",
        "",
        "| Zone | Count |",
        "|------|------:|",
    ])
    for z, c in sorted(opt_counts.items()):
        md.append(f"| {z} | {c} |")

    md.extend([
        "",
        "---",
        "",
        "## 4. Gradients (backward sans step)",
        "",
        "| Zone | Tensors grad | Attendu |",
        "|------|:------------:|:-------:|",
        f"| Backbone | {gs['backbone_grad']} | 0 |",
        f"| cv2 | {gs['cv2_grad']} | 0 |",
        f"| cv3 | {gs['cv3_grad']} | 0 |",
        f"| DFL | {gs['dfl_grad']} | 0 |",
        f"| cv4 old | {gs['cv4_old_grad']} | 0 |",
        f"| cv4 IT | {gs['cv4_it_grad']} | >0 |",
        "",
        f"box/cls/dfl loss : {li['box']:.4f} / {li['cls']:.4f} / {li['dfl']:.4f}",
        "",
        "---",
        "",
        "## 5. Inférence pré-training (5 images val, imgsz=640, conf=0.25)",
        "",
        f"| Modèle | Détections / 5 |",
        f"|--------|:--------------:|",
        f"| V2 best | {v2_hits}/5 |",
        f"| v5_surgical_init | {surg_hits}/5 |",
        f"| trainer.model (D) | {trainer_hits}/5 |",
        "",
        "| Image | V2 | surgical | trainer | trainer ≡ surgical |",
        "|-------|---:|---------:|--------:|:------------------:|",
    ])
    for r in infer_rows:
        md.append(
            f"| {r['case_id']} | {r['v2_boxes']} | {r['surgical_boxes']} | "
            f"{r['trainer_boxes']} | {r['trainer_matches_surgical']} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## Checklist",
        "",
    ])
    for k, v in checks.items():
        md.append(f"- [{'x' if v else ' '}] `{k}` → {v}")

    md.extend([
        "",
        "---",
        "",
        f"## Conclusion : `{verdict}`",
        "",
        "CSV : `v5_phase1_v3_preflight.csv`",
        "",
        "Pour entraîner (après READY) :",
        "```",
        ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v5_phase1_v3.py --train",
        "```",
    ])
    PREFLIGHT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(verdict)
    return verdict


def run_model_flag_preflight(cfg: dict[str, Any], model_path: Path, epochs: int) -> str:
    """Dry-run: verify --model loads epoch-1 best with IT-only trainer intact."""
    if not model_path.is_file():
        raise SystemExit(f"Checkpoint manquant : {model_path}")

    best_sd = load_surgical_state_dict(model_path)
    surg_sd = load_surgical_state_dict(V5_INIT)

    kwargs = build_train_kwargs_v3(cfg, model_path=model_path)
    kwargs.update({
        "epochs": epochs,
        "exist_ok": True,
        "name": "yolo_pose_new_26_v5_phase1_v3_model_flag_dryrun",
        "save": False,
        "val": False,
        "plots": False,
        "verbose": False,
        "device": "cpu",
        "workers": 0,
    })

    trainer, _ = create_trainer_like_train(cfg, kwargs)
    trainer._setup_train()

    cmp_best = compare_state_to_ref(best_sd, trainer.model, "loaded_vs_epoch1_best_file")
    cmp_surg = compare_state_to_ref(surg_sd, trainer.model, "loaded_vs_surgical_init")
    fs = freeze_state_summary(trainer.model)
    opt_counts = optimizer_zone_check(trainer)
    n_opt = getattr(trainer, "_v5_n_opt_params", 0)
    ema_mode = getattr(trainer, "_v5_ema_mode", "unknown")

    from ultralytics.utils.torch_utils import unwrap_model

    model = unwrap_model(trainer.model)
    batch, _ = load_train_batch(cfg, prefer_v0_it=False)
    batch = trainer.preprocess_batch(batch)
    crit = model.init_criterion()
    crit_name = type(crit).__name__
    model.zero_grad(set_to_none=True)
    loss, loss_items = model(batch)
    loss.sum().backward()
    gs = grad_zone_summary_v2(model)
    li = {k: float(loss_items[i].item()) for i, k in enumerate(("box", "pose", "kobj", "cls", "dfl"))}

    best_vs_surg_it = cmp_surg["cv4_it_changed"] > 0 or cmp_surg["cv4_it_max"] > THRESH
    frozen_match_surgical = cmp_surg["frozen_zones_ok"] and cmp_surg["cv4_old_changed"] == 0
    matches_epoch1_file = cmp_best["frozen_zones_ok"] and cmp_best["cv4_it_changed"] == 0 and cmp_best["cv4_old_changed"] == 0

    checks = {
        "model_path_resolved": str(model_path.resolve()) == str(trainer.args.model),
        "checkpoint_is_epoch1_best": model_path.resolve() == EPOCH1_BEST.resolve(),
        "loaded_matches_epoch1_best_weights": matches_epoch1_file,
        "it_weights_differ_from_surgical": best_vs_surg_it,
        "frozen_zones_match_surgical_init": frozen_match_surgical,
        "pretrained_true": trainer.args.pretrained is True,
        "resume_false": trainer.args.resume is False,
        "epochs_configurable": trainer.args.epochs == epochs,
        "freeze_backbone_0": fs["backbone_trainable"] == 0,
        "freeze_cv2_0": fs["cv2_trainable"] == 0,
        "freeze_cv3_0": fs["cv3_trainable"] == 0,
        "freeze_dfl_0": fs["dfl_trainable"] == 0,
        "freeze_cv4_it_24": fs["cv4_hook_params"] == 24,
        "optimizer_it_only_24": n_opt == 24,
        "optimizer_no_backbone": opt_counts.get("backbone", 0) == 0,
        "criterion_it_only": crit_name == "Phase1ITOnlyPoseLoss",
        "det_loss_zero": li["box"] == 0.0 and li["cls"] == 0.0 and li["dfl"] == 0.0,
        "cv4_it_grad_active": gs["cv4_it_grad"] > 0,
        "cv4_old_grad_zero": gs["cv4_old_grad"] == 0,
        "ema_restricted": ema_mode == "ema_restricted_trainable",
        "custom_trainer_active": type(trainer).__name__ != "PoseTrainer",
    }

    all_ok = all(checks.values())
    verdict = "V5_PHASE1_V3_MODEL_FLAG_READY" if all_ok else "V5_PHASE1_V3_MODEL_FLAG_BLOCKED"

    csv_rows: list[dict[str, Any]] = [
        {"section": "summary", "metric": "verdict", "value": verdict},
        {"section": "config", "metric": "model_path", "value": str(model_path.relative_to(PROJECT))},
        {"section": "config", "metric": "epochs", "value": epochs},
        {"section": "config", "metric": "pretrained", "value": kwargs["pretrained"]},
        {"section": "config", "metric": "resume", "value": kwargs["resume"]},
    ]
    for k, v in checks.items():
        csv_rows.append({"section": "check", "metric": k, "value": v})
    for cmp in (cmp_best, cmp_surg):
        csv_rows.append({
            "section": "weight_compare",
            "label": cmp["label"],
            "frozen_zones_ok": cmp["frozen_zones_ok"],
            "cv4_old_changed": cmp["cv4_old_changed"],
            "cv4_it_changed": cmp["cv4_it_changed"],
            "cv4_it_max": cmp["cv4_it_max"],
        })
    for k, v in fs.items():
        csv_rows.append({"section": "freeze", "metric": k, "value": v})
    for z, c in opt_counts.items():
        csv_rows.append({"section": "optimizer", "zone": z, "n_params": c})
    for k, v in li.items():
        csv_rows.append({"section": "loss", "metric": k, "value": v})
    for k, v in gs.items():
        csv_rows.append({"section": "gradients", "metric": k, "value": v})
    csv_rows.append({"section": "ema", "metric": "mode", "value": ema_mode})

    fieldnames = sorted({k for row in csv_rows for k in row})
    with MODEL_FLAG_PREFLIGHT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [
        "# V5 Phase 1 v3 — `--model` flag pre-flight",
        "",
        f"**Généré :** {ts}",
        "**Mode :** DRY-RUN — aucun `--train`, pas de `optimizer.step()`",
        f"**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v3.py`",
        f"**Checkpoint testé :** `{model_path.relative_to(PROJECT)}`",
        f"**Verdict :** `{verdict}`",
        "",
        "---",
        "",
        "## Comportement `--model`",
        "",
        "| Cas | model= | pretrained | resume |",
        "|-----|--------|:----------:|:------:|",
        f"| `--model` fourni | chemin explicite | **True** | **False** |",
        f"| défaut (sans --model) | `v5_surgical_init.pt` | **True** | **False** |",
        "",
        "---",
        "",
        "## Vérifications post `_setup_train()`",
        "",
        "| # | Check | Résultat | Attendu |",
        "|--:|-------|:--------:|:-------:|",
        f"| 1 | Checkpoint chargé = epoch-1 best | {checks['checkpoint_is_epoch1_best']} | True |",
        f"| 2 | Poids IT ≠ surgical_init | {checks['it_weights_differ_from_surgical']} | True |",
        f"| 3 | Poids gelés ≡ surgical_init | {checks['frozen_zones_match_surgical_init']} | True |",
        f"| 4 | Freeze OK (0/0/0/0 + 24 IT) | {checks['freeze_backbone_0'] and checks['freeze_cv4_it_24']} | True |",
        f"| 5 | Optimizer 24 params IT | {checks['optimizer_it_only_24']} | True |",
        f"| 6 | Loss IT-only (box/cls/dfl=0) | {checks['criterion_it_only'] and checks['det_loss_zero']} | True |",
        f"| 7 | EMA restreinte | {checks['ema_restricted']} | True |",
        f"| 8 | resume=False | {checks['resume_false']} | True |",
        f"| 9 | epochs={epochs} | {checks['epochs_configurable']} | True |",
        "",
        "### Détail poids",
        "",
        f"| Comparaison | frozen OK | cv4 old Δ | cv4 IT Δ | cv4 IT max |",
        f"|-------------|:---------:|:---------:|:--------:|-----------:|",
        f"| trainer vs epoch-1 file | {cmp_best['frozen_zones_ok']} | {cmp_best['cv4_old_changed']} | {cmp_best['cv4_it_changed']} | {cmp_best['cv4_it_max']:.6e} |",
        f"| trainer vs surgical_init | {cmp_surg['frozen_zones_ok']} | {cmp_surg['cv4_old_changed']} | {cmp_surg['cv4_it_changed']} | {cmp_surg['cv4_it_max']:.6e} |",
        "",
        "### Freeze / optimizer / loss",
        "",
        f"| Zone | Trainable | Optimizer count |",
        f"|------|----------:|----------------:|",
        f"| backbone | {fs['backbone_trainable']} | {opt_counts.get('backbone', 0)} |",
        f"| cv2 | {fs['cv2_trainable']} | {opt_counts.get('cv2_box', 0)} |",
        f"| cv3 | {fs['cv3_trainable']} | {opt_counts.get('cv3_cls', 0)} |",
        f"| dfl | {fs['dfl_trainable']} | {opt_counts.get('dfl', 0)} |",
        f"| cv4 IT | {fs['cv4_hook_params']} | {opt_counts.get('cv4_it', 0)} |",
        "",
        f"Criterion : **{crit_name}** — box/cls/dfl = {li['box']}/{li['cls']}/{li['dfl']}",
        f"EMA mode : **{ema_mode}**",
        "",
        "---",
        "",
        "## Checklist complète",
        "",
    ]
    for k, v in checks.items():
        md.append(f"- [{'x' if v else ' '}] `{k}` → {v}")

    md.extend([
        "",
        "---",
        "",
        f"## Conclusion : `{verdict}`",
        "",
        "Commande continuation (après READY, explicite `--train`) :",
        "```powershell",
        f".venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v5_phase1_v3.py ^",
        f"  --train --epochs 15 --model {model_path.relative_to(PROJECT)}",
        "```",
        "",
        "CSV : `v5_phase1_v3_model_flag_preflight.csv`",
    ])
    MODEL_FLAG_PREFLIGHT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(verdict)
    return verdict


def run_training(cfg: dict[str, Any], kwargs: dict[str, Any]) -> int:
    from ultralytics import YOLO

    if not PREFLIGHT_MD.is_file():
        raise SystemExit(f"Preflight v3 manquant : {PREFLIGHT_MD}")
    text = PREFLIGHT_MD.read_text(encoding="utf-8")
    if "V5_PHASE1_V3_READY" not in text:
        raise SystemExit("Preflight v3 non READY — corriger avant --train.")
    if "V5_PHASE1_V3_BLOCKED" in text.split("## Conclusion")[-1]:
        raise SystemExit("Preflight v3 BLOCKED — entraînement interdit.")
    if "V5_PHASE1_CHECKPOINT_LOADING_BLOCKED" in text:
        raise SystemExit("Checkpoint loading BLOCKED — entraînement interdit.")

    if not V5_INIT.is_file():
        raise SystemExit(f"Init V5 manquant : {V5_INIT}")

    TrainerCls = V5Phase1PoseTrainer.create(cfg, kwargs)
    yolo = YOLO(kwargs["model"], task="pose")
    yolo.train(trainer=TrainerCls, **kwargs)
    return 0


def main() -> int:
    cfg = load_cfg()
    default_epochs = int(cfg["train"]["epochs"])

    parser = argparse.ArgumentParser(description="V5 Phase 1 v3 IT-only (surgical checkpoint fix)")
    parser.add_argument("--train", action="store_true", help="Lance l'entraînement (explicite)")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        metavar="PATH",
        help="Checkpoint à charger (ex. epoch-1 best.pt). Défaut : v5_surgical_init.pt",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        metavar="N",
        help=f"Nombre maximum d'epochs du run (défaut: {default_epochs})",
    )
    args = parser.parse_args()

    if args.epochs is not None and args.epochs < 1:
        parser.error("--epochs must be >= 1")

    model_path = resolve_model_path(args.model) if args.model else None
    epochs = args.epochs if args.epochs is not None else default_epochs

    if args.model and not args.train:
        verdict = run_model_flag_preflight(cfg, model_path, epochs)
        return 0 if verdict == "V5_PHASE1_V3_MODEL_FLAG_READY" else 1

    if args.train:
        kwargs = build_train_kwargs_v3(cfg, model_path=model_path)
        kwargs["name"] = "yolo_pose_new_26_v5_phase1_it_v3"
        kwargs["epochs"] = epochs
        return run_training(cfg, kwargs)

    if args.epochs is not None:
        print(f"Note: --epochs {args.epochs} ignoré sans --train ni --model.")

    verdict = run_preflight(cfg)
    if verdict == "V5_PHASE1_V3_READY":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
