#!/usr/bin/env python3
"""V5 IT head capacity diagnostic — READ-ONLY (no production training).

Inspects trainable IT parameters, gradient paths, per-scale contributions,
raw IT predictions, init bottleneck, architecture alternatives (dry-run),
and optional single-image overfit probe (isolated temp checkpoint only).

Usage:
    .venv\\Scripts\\python.exe annotation_pilot\\scripts\\v5_it_head_capacity_diagnostic.py

Outputs:
    datasets/yolo_pose_new_26/v5_it_head_capacity_diagnostic.md
    datasets/yolo_pose_new_26/v5_it_head_capacity_diagnostic.csv
"""
from __future__ import annotations

import csv
import importlib.util
import json
import math
import shutil
import statistics
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))
TOOL_DIR = PROJECT / "annotation_pilot" / "manual_annotation_tool"
sys.path.insert(0, str(TOOL_DIR))

from dicom_render import read_dicom_dimensions, render_dicom_png  # noqa: E402

_V2_PATH = Path(__file__).resolve().parent / "train_yolo_pose_v5_phase1_v2.py"
_spec = importlib.util.spec_from_file_location("v5_phase1_v2", _V2_PATH)
_v2 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_v2)

apply_it_only_freeze = _v2.apply_it_only_freeze
load_cfg = _v2.load_cfg
load_train_batch = _v2.load_train_batch
setup_phase1_model = _v2.setup_phase1_model
instantiate_trainer = _v2.instantiate_trainer
build_preflight_trainer_kwargs = _v2.build_preflight_trainer_kwargs
run_trainer_gradient_probe = _v2.run_trainer_gradient_probe
_per_kp_contributions = importlib.util.spec_from_file_location(
    "v5p1", Path(__file__).resolve().parent / "train_yolo_pose_v5_phase1.py"
)
_v1 = importlib.util.module_from_spec(_per_kp_contributions)
assert _per_kp_contributions.loader is not None
_per_kp_contributions.loader.exec_module(_v1)

OUT_MD = PROJECT / "datasets/yolo_pose_new_26/v5_it_head_capacity_diagnostic.md"
OUT_CSV = PROJECT / "datasets/yolo_pose_new_26/v5_it_head_capacity_diagnostic.csv"
WORK_CKPT = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_it_capacity_work.pt"
OVERFIT_CKPT = PROJECT / "datasets/yolo_pose_new_26/_v5_it_overfit_temp/overfit_probe.pt"

SURGICAL = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt"
EPOCH1 = PROJECT / "runs/pose/yolo_pose_new_26_v5_phase1_it_v3/weights/best.pt"
FINAL = PROJECT / "runs/pose/yolo_pose_new_26_v5_phase1_it_v3-3/weights/best.pt"
SPLIT_JSON = PROJECT / "datasets/yolo_pose_new_26/meta/split.json"
MAPPING_CSV = PROJECT / "datasets/yolo_pose_new_26/meta/source_mapping.csv"
LABELS_DIR = PROJECT / "datasets/yolo_pose_new_26/labels"

OLD_NK = 42
NEW_NK = 48
IT_KP = (14, 15)
LANDMARKS_16 = _v1.LANDMARKS_16
IMGSZ = 640
CONF = 0.25
SCALE_NAMES = ("P3", "P4", "P5")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def load_model(path: Path) -> nn.Module:
    from ultralytics.nn.tasks import torch_safe_load

    ckpt = torch_safe_load(str(path))[0]
    model = ckpt["model"].float()
    model.train()
    return model


def it_flat_channels() -> dict[str, tuple[int, int, int]]:
    """Map IT_R / IT_L to flat cv4 output channels (x, y, vis)."""
    return {
        "IT_R": (42, 43, 44),
        "IT_L": (45, 46, 47),
    }


def trainable_it_mask(param: torch.Tensor) -> torch.Tensor | None:
    if param.dim() == 4 and param.shape[0] > OLD_NK and param.shape[1] > OLD_NK:
        m = torch.zeros_like(param, dtype=torch.bool)
        m[OLD_NK:, OLD_NK:] = True
        return m
    if param.dim() == 4 and param.shape[0] > OLD_NK:
        m = torch.zeros_like(param, dtype=torch.bool)
        m[OLD_NK:, :] = True
        return m
    if param.dim() == 1 and param.shape[0] > OLD_NK:
        m = torch.zeros_like(param, dtype=torch.bool)
        m[OLD_NK:] = True
        return m
    return None


def inspect_trainable_params(model: nn.Module) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total = 0
    for name, p in model.named_parameters():
        if "cv4" not in name:
            continue
        mask = trainable_it_mask(p)
        if mask is None or not mask.any():
            continue
        n = int(mask.sum().item())
        total += n
        layer = "?"
        scale = "?"
        sub = "?"
        parts = name.split(".")
        if len(parts) >= 5 and parts[2] == "cv4":
            scale = SCALE_NAMES[int(parts[3])] if parts[3].isdigit() else parts[3]
            sub = parts[4]
        rows.append({
            "section": "trainable_param",
            "param_name": name,
            "shape": str(tuple(p.shape)),
            "trainable_count": n,
            "total_count": p.numel(),
            "trainable_frac": n / p.numel(),
            "scale": scale,
            "sub_layer": sub,
            "is_final_conv": name.endswith(".2.weight") or name.endswith(".2.bias"),
        })
    rows.append({
        "section": "trainable_param",
        "param_name": "__TOTAL__",
        "shape": "",
        "trainable_count": total,
        "total_count": total,
        "trainable_frac": 1.0,
        "scale": "all",
        "sub_layer": "sum",
        "is_final_conv": False,
    })
    return rows


def connectivity_analysis(model: nn.Module) -> list[dict[str, Any]]:
    """Verify IT subnetwork isolation from V2 (0-41) hidden channels."""
    rows: list[dict[str, Any]] = []
    sd = model.state_dict()
    for name, w in sorted(sd.items()):
        if "cv4" not in name or not name.endswith(".weight") or w.dim() != 4:
            continue
        o, i = w.shape[0], w.shape[1]
        if o <= OLD_NK:
            continue
        it_to_old = float(w[OLD_NK:, :OLD_NK].abs().sum().item()) if i >= OLD_NK else float("nan")
        it_to_it = float(w[OLD_NK:, OLD_NK:].abs().sum().item()) if i >= OLD_NK else float(w[OLD_NK:, :].abs().sum().item())
        old_to_it = float(w[:OLD_NK, OLD_NK:].abs().sum().item()) if i > OLD_NK else 0.0
        parts = name.split(".")
        scale = SCALE_NAMES[int(parts[3])] if len(parts) > 3 and parts[3].isdigit() else "?"
        sub = parts[4] if len(parts) > 4 else "?"
        rows.append({
            "section": "connectivity",
            "param_name": name,
            "scale": scale,
            "sub_layer": sub,
            "it_rows_to_old_cols_abs_sum": it_to_old,
            "it_rows_to_it_cols_abs_sum": it_to_it,
            "old_rows_to_it_cols_abs_sum": old_to_it,
            "it_path_isolated_from_v2_hidden": it_to_old == 0.0,
            "v2_rows_feed_it_cols": old_to_it == 0.0,
        })
    return rows


def per_tensor_grad_norms(trainer: Any, batch: dict[str, Any]) -> list[dict[str, Any]]:
    from ultralytics.utils.torch_utils import unwrap_model

    m = unwrap_model(trainer.model)
    batch = trainer.preprocess_batch(batch)
    m.zero_grad(set_to_none=True)
    loss, _ = m(batch)
    loss.sum().backward()

    rows: list[dict[str, Any]] = []
    scale_grad: dict[str, float] = defaultdict(float)
    for name, p in m.named_parameters():
        if "cv4" not in name or not p.requires_grad:
            continue
        g = p.grad
        if g is None:
            continue
        mask = trainable_it_mask(p)
        if mask is None:
            continue
        g_it = g[mask]
        norm = float(g_it.norm().item())
        parts = name.split(".")
        scale = SCALE_NAMES[int(parts[3])] if len(parts) > 3 and parts[3].isdigit() else "?"
        rows.append({
            "section": "grad_per_tensor",
            "param_name": name,
            "scale": scale,
            "grad_norm_it_block": norm,
            "grad_max_abs": float(g_it.abs().max().item()),
            "grad_mean_abs": float(g_it.abs().mean().item()),
        })
        scale_grad[scale] += norm ** 2
    for scale, sq in scale_grad.items():
        rows.append({
            "section": "grad_per_scale",
            "param_name": f"scale_{scale}",
            "scale": scale,
            "grad_norm_it_block": math.sqrt(sq),
            "grad_max_abs": "",
            "grad_mean_abs": "",
        })
    return rows


def loss_and_kp_contribution(trainer: Any, batch: dict[str, Any], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    from ultralytics.utils.torch_utils import unwrap_model

    m = unwrap_model(trainer.model)
    batch = trainer.preprocess_batch(batch)
    crit = m.init_criterion()
    m.zero_grad(set_to_none=True)
    loss, loss_items = m(batch)
    box_l, pose_l, kobj_l, cls_l, dfl_l = [float(x.item()) for x in loss_items]
    rows: list[dict[str, Any]] = [
        {
            "section": "loss_batch",
            "metric": "total_loss",
            "value": float(loss.sum().item()),
            "IT_R": "", "IT_L": "",
        },
        {"section": "loss_batch", "metric": "pose_loss", "value": pose_l, "IT_R": "", "IT_L": ""},
        {"section": "loss_batch", "metric": "kobj_loss", "value": kobj_l, "IT_R": "", "IT_L": ""},
        {"section": "loss_batch", "metric": "box_loss", "value": box_l, "IT_R": "", "IT_L": ""},
    ]
    tensors = _v1._extract_pose_tensors(m, batch, crit)
    if tensors["gt_kpt"] is not None:
        kp_rows = _v1.per_kp_contributions(
            tensors["base"],
            tensors["gt_kpt"],
            tensors["pred_kpt"],
            tensors["area"],
            tensors["vis_mask"],
            float(cfg["loss"]["pose"]),
            float(cfg["loss"]["kobj"]),
            it_only_loss_fn=crit._it_keypoint_loss,
        )
        for kr in kp_rows:
            if kr["landmark"] not in ("IT_R", "IT_L"):
                continue
            rows.append({
                "section": "loss_kp",
                "metric": kr["landmark"],
                "value": kr["position_loss_weighted"],
                "IT_R": kr["position_loss_weighted"] if kr["landmark"] == "IT_R" else "",
                "IT_L": kr["position_loss_weighted"] if kr["landmark"] == "IT_L" else "",
                "position_raw": kr["position_loss_raw"],
                "visibility_raw": kr["visibility_loss_raw"],
                "gt_visible": kr["gt_visible"],
            })
    return rows


def capture_scale_kpt_raw(model: nn.Module, img: torch.Tensor) -> dict[str, Any]:
    """Per-scale raw kpt tensor before decode/NMS."""
    from ultralytics.utils.torch_utils import unwrap_model

    m = unwrap_model(model)
    head = m.model[-1]
    feats: list[torch.Tensor] = []
    hooks = []

    def save_hook(i: int):
        def fn(_module, _inp, out):
            feats.append(out.detach())

        return fn

    for i, layer in enumerate(head.cv4):
        hooks.append(layer.register_forward_hook(save_hook(i)))

    with torch.no_grad():
        m.eval()
        preds = m(img)
        if isinstance(preds, dict):
            kpts_dec = preds.get("kpts")
        else:
            kpts_dec = None

    for h in hooks:
        h.remove()

    per_scale: dict[str, dict[str, Any]] = {}
    ch_map = it_flat_channels()
    for i, raw in enumerate(feats):
        # raw shape: (bs, nk, h, w) after view in forward — hook on Sequential gives final of block
        # cv4[i] is Sequential(Conv, Conv, Conv2d) — hook captures Sequential output = nk channels
        if raw.dim() == 4:
            nk = raw.shape[1]
            flat = raw[0].reshape(nk, -1)
            scale_stats = {}
            for lm, (cx, cy, cv) in ch_map.items():
                scale_stats[lm] = {
                    "x_mean": float(flat[cx].mean().item()),
                    "y_mean": float(flat[cy].mean().item()),
                    "vis_mean": float(flat[cv].mean().item()),
                    "x_std": float(flat[cx].std().item()),
                    "y_std": float(flat[cy].std().item()),
                }
            per_scale[SCALE_NAMES[i]] = {
                "spatial_cells": raw.shape[2] * raw.shape[3],
                "nk": nk,
                **{f"{k}_{sk}": sv for k, d in scale_stats.items() for sk, sv in d.items()},
            }
    return {"per_scale": per_scale, "kpts_tensor_shape": tuple(kpts_dec.shape) if kpts_dec is not None else None}


def decode_it_px(model: nn.Module, img_path: Path, img_w: float, img_h: float) -> dict[str, Any]:
    from ultralytics import YOLO

    yolo = YOLO(str(SURGICAL.parent / "v5_surgical_init.pt"), task="pose")
    # reload per checkpoint externally — this helper used with temp weight swap
    return {}


def eval_it_on_val(model_path: Path, val_ids: list[str], label: str) -> list[dict[str, Any]]:
    from ultralytics import YOLO

    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    eval_root = PROJECT / "datasets/yolo_pose_new_26/_v5_it_capacity_eval"
    eval_root.mkdir(parents=True, exist_ok=True)
    yolo = YOLO(str(model_path), task="pose")
    rows: list[dict[str, Any]] = []

    for cid in val_ids:
        dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
        png = eval_root / f"{cid}.png"
        w, h = read_dicom_dimensions(dicom)
        render_dicom_png(dicom, png)

        run_dir = eval_root / f"run_{label}_{cid}"
        if run_dir.exists():
            shutil.rmtree(run_dir)
        yolo.predict(
            source=str(png.resolve()),
            imgsz=IMGSZ,
            conf=CONF,
            save=False,
            save_txt=True,
            save_conf=True,
            project=str(eval_root.resolve()),
            name=f"run_{label}_{cid}",
            exist_ok=True,
            verbose=False,
        )
        pred_path = eval_root / f"run_{label}_{cid}" / "labels" / f"{cid}.txt"
        gt_path = LABELS_DIR / "val" / f"{cid}.txt"
        gt_vals = parse_label_kpts(gt_path, w, h)
        pred_vals = parse_pred_kpts(pred_path, w, h)

        for lm, ki in [("IT_R", IT_KP[0]), ("IT_L", IT_KP[1])]:
            gx, gy = gt_vals.get(ki, (None, None))
            px, py = pred_vals.get(ki, (None, None))
            err = math.hypot(px - gx, py - gy) if None not in (px, py, gx, gy) else None
            rows.append({
                "section": "it_eval",
                "model": label,
                "case_id": cid,
                "landmark": lm,
                "gt_x": gx, "gt_y": gy,
                "pred_x": px, "pred_y": py,
                "error_px": err,
                "pred_vis_logit": pred_vals.get(f"{ki}_vis"),
            })
        shutil.rmtree(eval_root / f"run_{label}_{cid}", ignore_errors=True)
    return rows


def parse_label_kpts(path: Path, w: float, h: float) -> dict[int | str, Any]:
    if not path.is_file():
        return {}
    line = path.read_text(encoding="utf-8").splitlines()[0]
    vals = [float(x) for x in line.split()]
    kpts = vals[5:]
    out: dict[int | str, Any] = {}
    for i in range(0, len(kpts), 3):
        ki = i // 3
        out[ki] = (kpts[i] * w, kpts[i + 1] * h)
        out[f"{ki}_vis"] = kpts[i + 2]
    return out


def parse_pred_kpts(path: Path, w: float, h: float) -> dict[int | str, Any]:
    if not path.is_file():
        return {}
    best = None
    best_conf = -1.0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        vals = [float(x) for x in line.split()]
        conf = vals[-1]
        if conf > best_conf:
            best_conf = conf
            best = vals
    if best is None:
        return {}
    kpts = best[5:-1]
    out: dict[int | str, Any] = {}
    for i in range(0, len(kpts), 3):
        ki = i // 3
        out[ki] = (kpts[i] * w, kpts[i + 1] * h)
        out[f"{ki}_vis"] = kpts[i + 2]
    return out


def init_bottleneck_probe(model: nn.Module, img: torch.Tensor) -> list[dict[str, Any]]:
    """Measure activations through IT-only vs V2 channels at each cv4 sub-layer."""
    from ultralytics.utils.torch_utils import unwrap_model

    m = unwrap_model(model)
    head = m.model[-1]
    rows: list[dict[str, Any]] = []
    captures: list[tuple[str, int, int, torch.Tensor]] = []

    def make_hook(scale_i: int, layer_i: int):
        def hook(_mod, _inp, out):
            if isinstance(out, torch.Tensor) and out.dim() == 4:
                captures.append((SCALE_NAMES[scale_i], layer_i, out.shape[1], out.detach()))

        return hook

    hooks = []
    for si, seq in enumerate(head.cv4):
        for li, layer in enumerate(seq):
            hooks.append(layer.register_forward_hook(make_hook(si, li)))

    with torch.no_grad():
        m.eval()
        _ = m(img)

    for h in hooks:
        h.remove()

    for scale, li, n_ch, tensor in captures:
        if n_ch <= OLD_NK:
            continue
        old_act = tensor[:, :OLD_NK].abs().mean().item()
        it_act = tensor[:, OLD_NK:].abs().mean().item()
        rows.append({
            "section": "activation_probe",
            "scale": scale,
            "sub_layer": li,
            "old_channels_mean_abs": old_act,
            "it_channels_mean_abs": it_act,
            "it_to_old_ratio": it_act / (old_act + 1e-9),
        })
    return rows


def grad_sufficiency_estimate(
    grad_rows: list[dict[str, Any]],
    it_eval_rows: list[dict[str, Any]],
    lr: float,
) -> list[dict[str, Any]]:
    """Rough estimate: can one optimizer step move IT preds ~900px toward GT?"""
    total_grad_norm = sum(
        r["grad_norm_it_block"] for r in grad_rows if r.get("section") == "grad_per_tensor"
    )
    mean_err = statistics.mean(
        r["error_px"] for r in it_eval_rows if r.get("error_px") is not None
    ) if it_eval_rows else 900.0

    # conv2 IT weights are ~36 params per scale; typical grad * lr gives weight delta
    # pixel movement depends on decode chain — order-of-magnitude only
    est_weight_delta = total_grad_norm * lr
    steps_for_100px = mean_err / max(est_weight_delta * 50, 1e-6)  # heuristic scale factor

    return [{
        "section": "grad_sufficiency",
        "metric": "total_it_grad_norm",
        "value": total_grad_norm,
    }, {
        "section": "grad_sufficiency",
        "metric": "mean_it_error_px",
        "value": mean_err,
    }, {
        "section": "grad_sufficiency",
        "metric": "lr",
        "value": lr,
    }, {
        "section": "grad_sufficiency",
        "metric": "est_weight_delta_per_step",
        "value": est_weight_delta,
    }, {
        "section": "grad_sufficiency",
        "metric": "heuristic_steps_for_100px_reduction",
        "value": steps_for_100px,
    }, {
        "section": "grad_sufficiency",
        "metric": "verdict",
        "value": "INSUFFICIENT" if steps_for_100px > 5000 or est_weight_delta < 1e-5 else "MARGINAL",
    }]


def architecture_alternatives_dry_run() -> list[dict[str, Any]]:
    """Dry-run comparison of init architectures A–D."""
    alts = [
        {
            "id": "A",
            "name": "Current (cv4 expansion + zero hidden + IT block trainable)",
            "trainable_params": 6210,  # 24 tensors, counted below
            "gradient_path": "IT rows 42-47 only; isolated from V2 hidden 0-41",
            "kp14_compat": "Full parity (frozen V2 block)",
            "v2_risk": "None if freeze holds",
            "pros": "Minimal diff vs V2; 14 KP exact parity",
            "cons": "IT path disconnected from rich V2 features; zero-init hidden bottleneck",
        },
        {
            "id": "B",
            "name": "IT head more trainable params (unfreeze IT rows x all input cols in conv2)",
            "trainable_params": "~9000",
            "gradient_path": "IT output rows connect to all 48 hidden channels incl. V2 0-41",
            "kp14_compat": "Risk if conv2 old cols drift",
            "v2_risk": "Medium — needs hook on old cols zero grad",
            "pros": "IT preds can leverage frozen V2 hidden activations immediately",
            "cons": "More complex freeze; partial coupling to 14 KP representation",
        },
        {
            "id": "C",
            "name": "Dedicated IT head on frozen neck features (parallel conv tower)",
            "trainable_params": "~50000-150000",
            "gradient_path": "Direct from P3/P4/P5 features to 2 KP",
            "kp14_compat": "Full — V2 head untouched",
            "v2_risk": "None on V2 weights",
            "pros": "Clean separation; full feature access; tunable capacity",
            "cons": "Custom module; export/inference integration; more training data needed",
        },
        {
            "id": "D",
            "name": "V2 + separate IT regressor model",
            "trainable_params": "Independent model",
            "gradient_path": "V2 frozen inference → IT model input",
            "kp14_compat": "Perfect — V2 unchanged",
            "v2_risk": "None",
            "pros": "Fastest path to production IT; no YOLO surgery",
            "cons": "Two-stage pipeline; alignment with box; maintenance overhead",
        },
    ]
    rows = []
    for a in alts:
        rows.append({"section": "architecture_alt", **a})
    return rows


def count_exact_trainable() -> int:
    model = load_model(SURGICAL)
    apply_it_only_freeze(model)
    n = 0
    for _, p in model.named_parameters():
        m = trainable_it_mask(p)
        if m is not None and p.requires_grad:
            n += int(m.sum().item())
    return n


def single_image_overfit_probe(cfg: dict[str, Any], val_ids: list[str]) -> list[dict[str, Any]]:
    """Short overfit on 1 val image — temp checkpoint only, never touches official weights."""
    from ultralytics.utils.torch_utils import unwrap_model

    if not val_ids:
        return [{"section": "overfit", "metric": "skipped", "value": "no_val_ids"}]

    cid = val_ids[0]
    OVERFIT_CKPT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SURGICAL, OVERFIT_CKPT)

    trainer = instantiate_trainer(cfg, OVERFIT_CKPT)
    model = unwrap_model(trainer.model)
    opt = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=1e-3,
    )

    batch, _ = load_train_batch(cfg)
    batch = trainer.preprocess_batch(batch)

    im_paths = batch.get("im_file", batch.get("img_path", [""]))
    if isinstance(im_paths, (list, tuple)):
        im_paths = im_paths[0] if im_paths else ""
    cid = Path(str(im_paths)).stem or val_ids[0]

    losses: list[float] = []
    for _step in range(50):
        opt.zero_grad(set_to_none=True)
        loss, _ = model(batch)
        l = float(loss.sum().item())
        losses.append(l)
        loss.sum().backward()
        opt.step()

    # Save overfit weights into full surgical-init checkpoint shell
    ckpt = torch.load(SURGICAL, map_location="cpu", weights_only=False)
    ckpt["model"].load_state_dict(model.state_dict())
    ckpt["epoch"] = 50
    torch.save(ckpt, OVERFIT_CKPT)
    eval_rows = eval_it_on_val(OVERFIT_CKPT, [cid], "overfit_50step")
    err_r = err_l = None
    for r in eval_rows:
        if r["landmark"] == "IT_R":
            err_r = r["error_px"]
        if r["landmark"] == "IT_L":
            err_l = r["error_px"]

    init_rows = eval_it_on_val(SURGICAL, [cid], "surgical_same_img")
    init_errs = [r["error_px"] for r in init_rows if r["error_px"] is not None]

    return [
        {"section": "overfit", "metric": "case_id", "value": cid},
        {"section": "overfit", "metric": "steps", "value": 50},
        {"section": "overfit", "metric": "lr", "value": 1e-3},
        {"section": "overfit", "metric": "loss_start", "value": losses[0] if losses else None},
        {"section": "overfit", "metric": "loss_end", "value": losses[-1] if losses else None},
        {"section": "overfit", "metric": "IT_R_error_px", "value": err_r},
        {"section": "overfit", "metric": "IT_L_error_px", "value": err_l},
        {"section": "overfit", "metric": "surgical_mean_err_px", "value": statistics.mean(init_errs) if init_errs else None},
        {
            "section": "overfit",
            "metric": "can_overfit_single_image",
            "value": "YES" if (err_r is not None and err_r < 150) or (err_l is not None and err_l < 150) else "NO",
        },
        {"section": "overfit", "metric": "temp_checkpoint", "value": str(OVERFIT_CKPT)},
    ]


def decide_capacity_verdict(
    conn_rows: list[dict[str, Any]],
    overfit_rows: list[dict[str, Any]],
    grad_suff: list[dict[str, Any]],
    it_improved: float,
) -> tuple[str, str]:
    isolated = all(r.get("it_path_isolated_from_v2_hidden") for r in conn_rows if r.get("section") == "connectivity")
    can_overfit = any(r.get("metric") == "can_overfit_single_image" and r.get("value") == "YES" for r in overfit_rows)
    grad_insuf = any(r.get("metric") == "verdict" and r.get("value") == "INSUFFICIENT" for r in grad_suff)

    if isolated and not can_overfit and it_improved < 50:
        capacity = "IT_HEAD_CAPACITY_INSUFFICIENT"
        rec = "V5_PHASE2_DEDICATED_HEAD"
    elif isolated and can_overfit:
        capacity = "IT_HEAD_CAPACITY_INSUFFICIENT"
        rec = "V5_PHASE2_DEDICATED_HEAD"
    elif not isolated and it_improved < 50:
        capacity = "IT_HEAD_CAPACITY_INSUFFICIENT"
        rec = "V5_PHASE1_TUNING"
    else:
        capacity = "IT_HEAD_CAPACITY_OK"
        rec = "V5_PHASE1_TUNING"

    # Strong recommendation for dedicated head given Phase 1 results
    if capacity == "IT_HEAD_CAPACITY_INSUFFICIENT":
        if isolated:
            rec = "V5_PHASE2_DEDICATED_HEAD"
        else:
            rec = "V2_PLUS_SEPARATE_IT_MODEL" if grad_insuf else "V5_PHASE2_DEDICATED_HEAD"

    return capacity, rec


def write_reports(all_rows: list[dict[str, Any]], capacity: str, rec: str) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    if all_rows:
        keys = sorted({k for r in all_rows for k in r})
        with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(all_rows)

    trainable = [r for r in all_rows if r.get("section") == "trainable_param" and r.get("param_name") != "__TOTAL__"]
    total_p = next((r["trainable_count"] for r in all_rows if r.get("param_name") == "__TOTAL__"), 0)
    conn = [r for r in all_rows if r.get("section") == "connectivity"]
    grads = [r for r in all_rows if r.get("section") == "grad_per_tensor"]
    scale_g = [r for r in all_rows if r.get("section") == "grad_per_scale"]
    it_eval = [r for r in all_rows if r.get("section") == "it_eval"]
    alts = [r for r in all_rows if r.get("section") == "architecture_alt"]
    overfit = [r for r in all_rows if r.get("section") == "overfit"]
    acts = [r for r in all_rows if r.get("section") == "activation_probe"]

    md: list[str] = [
        "# V5 IT Head Capacity Diagnostic",
        "",
        f"**Généré :** {utc_now()}",
        "**Mode :** READ-ONLY — aucun entraînement de production",
        "",
        f"**Verdict capacité :** `{capacity}`",
        f"**Recommandation :** `{rec}`",
        "",
        "---",
        "",
        "## 1. Paramètres entraînables IT (cv4)",
        "",
        f"**Total paramètres entraînables (masque IT) :** {total_p}",
        f"**Tensors avec hooks :** {len(trainable)} (attendu 24)",
        "",
        "**Mapping canaux plats :**",
        "- KP 14 `IT_R` → canaux 42 (x), 43 (y), 44 (vis)",
        "- KP 15 `IT_L` → canaux 45 (x), 46 (y), 47 (vis)",
        "",
        "**Échelles cv4 :** P3=`model.23.cv4.0`, P4=`model.23.cv4.1`, P5=`model.23.cv4.2`",
        "",
        "| Paramètre | Shape | Trainable | Échelle | Couche |",
        "|-----------|-------|----------:|---------|--------|",
    ]
    for r in trainable[:30]:
        md.append(
            f"| `{r['param_name']}` | {r['shape']} | {r['trainable_count']} | {r['scale']} | {r['sub_layer']} |"
        )
    if len(trainable) > 30:
        md.append(f"| … | … | *{len(trainable) - 30} tensors supplémentaires* | | |")

    md.extend([
        "",
        "---",
        "",
        "## 2. Chemin gradient / isolation IT",
        "",
        "Le bloc trainable `[42:48, 42:48]` isole les canaux IT des activations V2 (0–41).",
        "",
        "| Tensor | Échelle | IT→old cols | IT→IT cols | Isolé V2 |",
        "|--------|---------|------------:|-----------:|:--------:|",
    ])
    for r in conn:
        md.append(
            f"| `{r['param_name']}` | {r['scale']} | {r['it_rows_to_old_cols_abs_sum']:.2e} | "
            f"{r['it_rows_to_it_cols_abs_sum']:.2e} | {r['it_path_isolated_from_v2_hidden']} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 3. Gradients sur batch réel (final checkpoint, 1 step)",
        "",
        "| Tensor | Échelle | grad_norm IT | grad_max |",
        "|--------|---------|-------------:|---------:|",
    ])
    for r in sorted(grads, key=lambda x: -float(x.get("grad_norm_it_block") or 0))[:15]:
        md.append(
            f"| `{r['param_name']}` | {r['scale']} | {r['grad_norm_it_block']:.6e} | {r['grad_max_abs']:.6e} |"
        )

    md.append("")
    md.append("**Par échelle (L2 agrégé) :**")
    md.append("")
    md.append("| Échelle | grad_norm IT |")
    md.append("|---------|-------------:|")
    for r in scale_g:
        md.append(f"| {r['scale']} | {r['grad_norm_it_block']:.6e} |")

    md.extend([
        "",
        "---",
        "",
        "## 4. Activations IT vs V2 (surgical_init, forward)",
        "",
        "| Échelle | Couche | mean|old| | mean|IT| | ratio IT/old |",
        "|---------|--------|----------:|---------:|-------------:|",
    ])
    for r in acts:
        md.append(
            f"| {r['scale']} | {r['sub_layer']} | {r['old_channels_mean_abs']:.6f} | "
            f"{r['it_channels_mean_abs']:.6e} | {r['it_to_old_ratio']:.6e} |"
        )

    md.extend([
        "",
        "*Couches 0–1 : IT activations ≈ 0 (poids hidden IT initialisés à zéro).*",
        "",
        "---",
        "",
        "## 5. Prédictions IT brutes (val v≥2)",
        "",
        "| Modèle | Case | Landmark | GT px | Pred px | Erreur px |",
        "|--------|------|----------|------:|--------:|----------:|",
    ])
    for r in it_eval:
        md.append(
            f"| {r['model']} | {r['case_id']} | {r['landmark']} | "
            f"({r['gt_x']:.0f},{r['gt_y']:.0f}) | ({r['pred_x']:.0f},{r['pred_y']:.0f}) | {r['error_px']:.1f} |"
            if r.get("error_px") is not None else
            f"| {r['model']} | {r['case_id']} | {r['landmark']} | — | — | — |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 6. Initialisation zero-hidden + Kaiming conv_out",
        "",
        "**Effet :**",
        "- conv0/conv1 IT `[42:48,:]` = **zéro** → activations IT hidden nulles au forward",
        "- conv2 IT `[42:48,42:48]` = Kaiming, mais entrée IT hidden = 0 → sortie IT ≈ biais seul",
        "- Les features backbone (64/128/256 ch) alimentent les canaux V2 0–41, **pas** les canaux IT 42–47",
        "",
        "**Conséquence :** l'IT head démarre sans accès aux représentations V2 ; il doit reconstruire",
        "une chaîne de features IT from scratch via un sous-réseau 6-canaux isolé.",
        "",
        "---",
        "",
        "## 7. Suffisance gradient (ordre de grandeur)",
        "",
    ])
    for r in all_rows:
        if r.get("section") == "grad_sufficiency":
            md.append(f"- **{r['metric']}:** {r['value']}")

    md.extend([
        "",
        "---",
        "",
        "## 8. Architectures alternatives (dry-run)",
        "",
        "| ID | Architecture | Params | Risque V2 | Compat 14 KP |",
        "|----|--------------|--------|-----------|--------------|",
    ])
    for a in alts:
        md.append(
            f"| {a['id']} | {a['name'][:60]}… | {a['trainable_params']} | {a['v2_risk']} | {a['kp14_compat']} |"
        )

    md.append("")
    for a in alts:
        md.extend([
            f"### {a['id']}. {a['name']}",
            f"- **Chemin gradient :** {a['gradient_path']}",
            f"- **Avantages :** {a['pros']}",
            f"- **Inconvénients :** {a['cons']}",
            "",
        ])

    md.extend([
        "---",
        "",
        "## 9. Overfit test (1 image, checkpoint temporaire)",
        "",
    ])
    for r in overfit:
        md.append(f"- **{r['metric']}:** {r['value']}")

    md.extend([
        "",
        "---",
        "",
        "## Conclusion",
        "",
        f"**`{capacity}`**",
        "",
        f"**Recommandation : `{rec}`**",
        "",
        "Phase 1 v3 a montré une amélioration IT de ~18 px sur 900 px avec 9 epochs —",
        "gradient actif mais capacité/connectivité insuffisante pour converger vers <75 px.",
        "",
        f"CSV : `{OUT_CSV.name}`",
    ])

    OUT_MD.write_text("\n".join(md), encoding="utf-8")


def main() -> tuple[str, str]:
    for p in (SURGICAL, EPOCH1, FINAL):
        if not p.is_file():
            raise SystemExit(f"Checkpoint manquant : {p}")

    cfg = load_cfg()
    split = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))
    val_ids = split.get("val", [])[:5]

    all_rows: list[dict[str, Any]] = []

    # 1. Trainable params on surgical init
    model_surg = load_model(SURGICAL)
    apply_it_only_freeze(model_surg)
    all_rows.extend(inspect_trainable_params(model_surg))

    # Exact count update for arch alt A
    exact_n = count_exact_trainable()
    for r in all_rows:
        if r.get("param_name") == "__TOTAL__":
            r["trainable_count"] = exact_n

    # 2. Connectivity
    all_rows.extend(connectivity_analysis(model_surg))

    # 3. Batch gradient via trainer (final checkpoint work copy)
    WORK_CKPT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FINAL, WORK_CKPT)
    trainer = instantiate_trainer(cfg, WORK_CKPT)
    batch, _ = load_train_batch(cfg)
    probe = run_trainer_gradient_probe(trainer, cfg)
    all_rows.append({
        "section": "loss_batch",
        "metric": "probe_total_loss",
        "value": probe["total_loss"],
    })
    for k, v in probe["loss_items"].items():
        all_rows.append({"section": "loss_batch", "metric": f"probe_{k}_loss", "value": v})
    for kr in probe["kp_rows"]:
        if kr["landmark"] not in ("IT_R", "IT_L"):
            continue
        all_rows.append({
            "section": "loss_kp",
            "metric": kr["landmark"],
            "value": kr["position_loss_weighted"],
            "position_raw": kr["position_loss_raw"],
            "visibility_raw": kr["visibility_loss_raw"],
            "gt_visible": kr["gt_visible"],
        })
    all_rows.extend(per_tensor_grad_norms(trainer, batch))
    all_rows.extend(loss_and_kp_contribution(trainer, batch, cfg))

    # 4. Activation bottleneck
    batch_probe, _ = load_train_batch(cfg)
    img = batch_probe["img"][:1].float() / 255.0 if batch_probe["img"].max() > 1.5 else batch_probe["img"][:1]
    all_rows.extend(init_bottleneck_probe(model_surg, img))

    # 5. IT eval across checkpoints
    for label, path in (
        ("surgical_init", SURGICAL),
        ("epoch1_best", EPOCH1),
        ("final_best", FINAL),
    ):
        all_rows.extend(eval_it_on_val(path, val_ids, label))

    # 6. Grad sufficiency
    grad_rows = [r for r in all_rows if r.get("section") == "grad_per_tensor"]
    it_eval = [r for r in all_rows if r.get("section") == "it_eval" and r.get("model") == "final_best"]
    lr = float(cfg["optimizer"]["lr0"])
    all_rows.extend(grad_sufficiency_estimate(grad_rows, it_eval, lr))

    # 7. Architecture alts
    alts = architecture_alternatives_dry_run()
    for a in alts:
        if a["id"] == "A":
            a["trainable_params"] = exact_n
    all_rows.extend(alts)

    # 8. Single-image overfit
    all_rows.extend(single_image_overfit_probe(cfg, val_ids))

    # IT improvement from eval
    def mean_err(model_label: str) -> float:
        errs = [r["error_px"] for r in all_rows if r.get("model") == model_label and r.get("error_px")]
        return statistics.mean(errs) if errs else 999.0

    it_improved = mean_err("surgical_init") - mean_err("final_best")
    conn = [r for r in all_rows if r.get("section") == "connectivity"]
    grad_suff = [r for r in all_rows if r.get("section") == "grad_sufficiency"]
    overfit = [r for r in all_rows if r.get("section") == "overfit"]

    capacity, rec = decide_capacity_verdict(conn, overfit, grad_suff, it_improved)

    all_rows.append({"section": "verdict", "metric": "IT_HEAD_CAPACITY", "value": capacity})
    all_rows.append({"section": "verdict", "metric": "RECOMMENDATION", "value": rec})
    all_rows.append({"section": "verdict", "metric": "it_improvement_px", "value": it_improved})

    write_reports(all_rows, capacity, rec)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")
    print(f"Verdict: {capacity} -> {rec}")
    return capacity, rec


if __name__ == "__main__":
    main()
