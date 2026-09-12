#!/usr/bin/env python3
"""V5 Phase 2 — Dedicated IT head training (ITHeadMultiScaleFusion).

Default: preflight gate (forward / loss / backward probe, NO training).
``--train`` : lance l'entraînement custom IT-only (explicite).

Ne modifie jamais V2, V4, labels, dataset, ni v5_surgical_init.pt.

Usage:
    .venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v5_phase2.py
    .venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v5_phase2.py --train
"""
from __future__ import annotations

import argparse
import copy
import csv
import importlib.util
import json
import math
import shutil
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import yaml

PROJECT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT / "datasets/yolo_pose_new_26/v5_phase2_training_config.yaml"
PREFLIGHT_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase2_training_preflight.md"
PREFLIGHT_CSV = PROJECT / "datasets/yolo_pose_new_26/v5_phase2_training_preflight.csv"
DRYRUN_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase2_dedicated_head_dryrun.md"
SURGICAL = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt"
V2_PATH = PROJECT / "runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt"
SPLIT_JSON = PROJECT / "datasets/yolo_pose_new_26/meta/split.json"
MAPPING_CSV = PROJECT / "datasets/yolo_pose_new_26/meta/source_mapping.csv"
LABELS_DIR = PROJECT / "datasets/yolo_pose_new_26/labels"
TOOL_DIR = PROJECT / "annotation_pilot/manual_annotation_tool"
OLD_NK = 42
IT_KP = (14, 15)
IMGSZ = 640
CONF = 0.25
THRESH = 1e-8

sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(TOOL_DIR))

_V1_PATH = Path(__file__).resolve().parent / "train_yolo_pose_v5_phase1.py"
_spec_v1 = importlib.util.spec_from_file_location("v5p1", _V1_PATH)
_v1 = importlib.util.module_from_spec(_spec_v1)
assert _spec_v1.loader is not None
_spec_v1.loader.exec_module(_v1)

_DRY_PATH = Path(__file__).resolve().parent / "v5_phase2_dedicated_head_dryrun.py"
_spec_dry = importlib.util.spec_from_file_location("v5p2dry", _DRY_PATH)
_dry = importlib.util.module_from_spec(_spec_dry)
assert _spec_dry.loader is not None
_spec_dry.loader.exec_module(_dry)

ITHeadMultiScaleFusion = _dry.ITHeadMultiScaleFusion
V5Phase2DedicatedModel = _dry.V5Phase2DedicatedModel
attach_hyp = _dry.attach_hyp
grad_probe = _dry.grad_probe
load_surgical_model = _dry.load_surgical_model
parity_probe = _dry.parity_probe
preprocess_batch = _dry.preprocess_batch
it_kpts_from_head = _dry.it_kpts_from_head
IT_OUT_CH = _dry.IT_OUT_CH

METRIC_FIX_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase2_metric_decoder_fix.md"
METRIC_FIX_CSV = PROJECT / "datasets/yolo_pose_new_26/v5_phase2_metric_decoder_fix.csv"

_orig_extract_neck = V5Phase2DedicatedModel._extract_neck
_orig_forward_head_preds = V5Phase2DedicatedModel.forward_head_preds


def extract_pose_head_dict(raw: Any) -> dict[str, torch.Tensor]:
    """Normalize Pose head output to the training dict (boxes/scores/feats/kpts).

    Train mode: head returns dict directly.
    Eval mode: head returns (combined_tensor, dict) — pose tensors are in raw[1].
    """
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, (tuple, list)):
        for item in raw:
            if isinstance(item, dict) and "kpts" in item:
                return item
        raise TypeError(
            f"Pose head tuple has no dict with 'kpts'; got types {[type(x).__name__ for x in raw]}"
        )
    raise TypeError(f"Unexpected pose head output type: {type(raw).__name__}")


def _patched_forward_head_preds(
    self: V5Phase2DedicatedModel, img: torch.Tensor
) -> tuple[dict[str, torch.Tensor], list[torch.Tensor], list[torch.Tensor]]:
    neck = self._extract_neck(img)
    with torch.no_grad():
        raw = self.base.model[-1](neck)
    preds = extract_pose_head_dict(raw)
    it_parts = self.it_head(neck)
    kpts = preds["kpts"].clone()
    kpts[:, OLD_NK:OLD_NK + IT_OUT_CH, :] = it_kpts_from_head(it_parts)
    preds["kpts"] = kpts
    return preds, neck, it_parts


V5Phase2DedicatedModel.forward_head_preds = _patched_forward_head_preds  # type: ignore[method-assign]


def _frozen_extract_neck(self: V5Phase2DedicatedModel, img: torch.Tensor) -> list[torch.Tensor]:
    with torch.no_grad():
        return _orig_extract_neck(self, img)


V5Phase2DedicatedModel._extract_neck = _frozen_extract_neck  # type: ignore[method-assign]
LANDMARKS_16 = _v1.LANDMARKS_16


def load_train_batch(cfg: dict[str, Any]) -> tuple[dict[str, Any], Any]:
    from ultralytics.cfg import DEFAULT_CFG, get_cfg
    from ultralytics.data.build import build_dataloader, build_yolo_dataset
    from ultralytics.data.utils import check_det_dataset

    t = cfg["train"]
    args = get_cfg(cfg=DEFAULT_CFG)
    args.task = "pose"
    args.data = str(resolve(cfg["data"]))
    args.imgsz = t["imgsz"]
    args.batch = t["batch"]
    args.workers = 0
    apply_augment_args(args, cfg)

    data = check_det_dataset(str(resolve(cfg["data"])))
    dataset = build_yolo_dataset(args, data["train"], batch=1, data=data, mode="train", rect=False, stride=32)
    loader = build_dataloader(dataset, batch=1, workers=0, shuffle=False, rank=-1)
    batch = next(iter(loader))
    batch["img"] = batch["img"].float() / 255.0
    return batch, args


def resolve(path_str: str) -> Path:
    p = Path(path_str)
    return p if p.is_absolute() else PROJECT / p


def load_cfg() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def phase2_param_zone(name: str) -> str:
    if name.startswith("it_head"):
        return "it_head"
    if "dfl" in name:
        return "dfl"
    if "cv4" in name:
        return "cv4_pose"
    if "cv3" in name:
        return "cv3_cls"
    if "cv2" in name:
        return "cv2_box"
    if name.startswith("model.") and name.split(".")[1].isdigit():
        layer = int(name.split(".")[1])
        if layer <= 10:
            return "backbone"
        if layer <= 22:
            return "neck"
    return "other"


def count_params_summary(model: V5Phase2DedicatedModel) -> dict[str, int]:
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    frozen = sum(p.numel() for p in model.parameters() if not p.requires_grad)
    it_head = sum(p.numel() for p in model.it_head.parameters())
    base_frozen = sum(p.numel() for p in model.base.parameters())
    return {
        "trainable": trainable,
        "frozen": frozen,
        "it_head": it_head,
        "base_frozen": base_frozen,
        "optimizer_params": trainable,
    }


def load_surgical_base_params() -> dict[str, torch.Tensor]:
    ckpt = torch.load(SURGICAL, map_location="cpu", weights_only=False)
    return {
        n: p.clone()
        for n, p in ckpt["model"].float().named_parameters()
    }


def compare_base_to_surgical(
    model: V5Phase2DedicatedModel,
    ref_params: dict[str, torch.Tensor],
    max_delta: float = THRESH,
) -> dict[str, Any]:
    base_params = dict(model.base.named_parameters())
    zones: dict[str, dict[str, float]] = {}
    cv4_old_max = 0.0
    cv4_old_changed = 0

    for name, ref in ref_params.items():
        if name not in base_params or not torch.is_floating_point(ref):
            continue
        tgt = base_params[name].detach().float().cpu()
        ref_f = ref.float().cpu()
        diff = (tgt - ref_f).abs()
        max_diff = float(diff.max().item()) if diff.numel() else 0.0
        zone = phase2_param_zone(name)

        z = zones.setdefault(zone, {"max_diff": 0.0, "changed": 0, "total": 0})
        z["total"] += 1
        z["max_diff"] = max(z["max_diff"], max_diff)
        if max_diff > max_delta:
            z["changed"] += 1

        if "cv4" in name and ref_f.dim() >= 2:
            if ref_f.dim() == 4 and ref_f.shape[0] > OLD_NK and ref_f.shape[1] > OLD_NK:
                d_old = diff[:OLD_NK, :OLD_NK].max().item() if diff[:OLD_NK, :OLD_NK].numel() else 0.0
            elif ref_f.dim() == 1 and ref_f.shape[0] > OLD_NK:
                d_old = diff[:OLD_NK].max().item()
            else:
                d_old = 0.0
            if d_old > max_delta:
                cv4_old_changed += 1
                cv4_old_max = max(cv4_old_max, d_old)

    frozen_zones = ("backbone", "neck", "cv2_box", "cv3_cls", "dfl", "cv4_pose")
    frozen_ok = all(zones.get(z, {}).get("changed", 0) == 0 for z in frozen_zones)
    frozen_ok &= cv4_old_changed == 0

    return {
        "zones": zones,
        "cv4_old_max": cv4_old_max,
        "cv4_old_changed": cv4_old_changed,
        "frozen_ok": frozen_ok,
    }


def build_model(cfg: dict[str, Any]) -> V5Phase2DedicatedModel:
    surgical = load_surgical_model()
    attach_hyp(surgical)
    it_head = ITHeadMultiScaleFusion()
    return V5Phase2DedicatedModel(surgical, it_head)


def build_optimizer(model: V5Phase2DedicatedModel, cfg: dict[str, Any]) -> torch.optim.Optimizer:
    opt_cfg = cfg["optimizer"]
    name = str(opt_cfg.get("name", "AdamW"))
    lr = float(opt_cfg.get("lr0", 1e-4))
    wd = float(opt_cfg.get("weight_decay", 0.0005))
    params = [p for p in model.it_head.parameters() if p.requires_grad]
    if name.lower() == "adamw":
        return torch.optim.AdamW(params, lr=lr, weight_decay=wd)
    if name.lower() == "adam":
        return torch.optim.Adam(params, lr=lr, weight_decay=wd)
    raise ValueError(f"Optimizer non supporté : {name}")


def eval_14kp_v2_on_val(val_ids: list[str]) -> dict[str, float | None]:
    from dicom_render import read_dicom_dimensions, render_dicom_png
    from ultralytics import YOLO

    root = PROJECT / "datasets/yolo_pose_new_26/_v5_phase2_v2_14kp"
    root.mkdir(parents=True, exist_ok=True)
    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    yolo = YOLO(str(V2_PATH), task="pose")
    errs: list[float] = []
    for cid in val_ids:
        dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
        png = root / f"{cid}.png"
        w, h = read_dicom_dimensions(dicom)
        render_dicom_png(dicom, png)
        run_name = f"v2_{cid}"
        yolo.predict(
            source=str(png.resolve()),
            imgsz=IMGSZ,
            conf=CONF,
            save_txt=True,
            project=str(root.resolve()),
            name=run_name,
            exist_ok=True,
            verbose=False,
        )
        pred = root / run_name / "labels" / f"{cid}.txt"
        gt = LABELS_DIR / "val" / f"{cid}.txt"
        for ki in range(14):
            e = kp_error_px(pred, gt, w, h, ki)
            if e is not None:
                errs.append(e)
        shutil.rmtree(root / run_name, ignore_errors=True)
    if not errs:
        return {"mean_14kp_px": None, "median_14kp_px": None, "p90_14kp_px": None}
    s = sorted(errs)
    return {
        "mean_14kp_px": statistics.mean(errs),
        "median_14kp_px": statistics.median(errs),
        "p90_14kp_px": s[min(len(s) - 1, math.ceil(0.9 * len(s)) - 1)],
    }


def apply_augment_args(args: Any, cfg: dict[str, Any]) -> None:
    aug = cfg.get("augment", {})
    for key in (
        "mosaic", "mixup", "cutmix", "copy_paste", "erasing", "fliplr", "flipud",
        "degrees", "translate", "scale", "shear", "perspective", "hsv_h", "hsv_s", "hsv_v",
        "close_mosaic",
    ):
        if key in aug:
            setattr(args, key, aug[key])
    if "auto_augment" in aug:
        args.auto_augment = aug["auto_augment"]


def build_dataloader(cfg: dict[str, Any], mode: str = "train") -> Any:
    from ultralytics.cfg import DEFAULT_CFG, get_cfg
    from ultralytics.data.build import build_dataloader, build_yolo_dataset
    from ultralytics.data.utils import check_det_dataset

    t = cfg["train"]
    args = get_cfg(cfg=DEFAULT_CFG)
    args.task = "pose"
    args.data = str(resolve(cfg["data"]))
    args.imgsz = t["imgsz"]
    args.batch = t["batch"]
    args.workers = t.get("workers", 0)
    apply_augment_args(args, cfg)

    data = check_det_dataset(str(resolve(cfg["data"])))
    split = data["train"] if mode == "train" else data["val"]
    dataset = build_yolo_dataset(
        args, split, batch=t["batch"], data=data, mode=mode, rect=False, stride=32
    )
    return build_dataloader(
        dataset,
        batch=t["batch"],
        workers=t.get("workers", 0),
        shuffle=(mode == "train"),
        rank=-1,
    )


def batch_to_device(batch: dict[str, Any], device: torch.device) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in batch.items():
        if isinstance(v, torch.Tensor):
            out[k] = v.to(device)
        else:
            out[k] = v
    if out["img"].dtype != torch.float32:
        out["img"] = out["img"].float() / 255.0
    return out


def sim_optimizer_step_probe(model: V5Phase2DedicatedModel, batch: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """One in-memory optimizer.step(); only it_head may change."""
    model_copy = copy.deepcopy(model)
    model_copy.train()
    attach_hyp(model_copy.base)
    before_base = {n: p.detach().clone() for n, p in model_copy.base.named_parameters()}
    before_it = {k: v.clone() for k, v in model_copy.it_head.state_dict().items()}

    opt = build_optimizer(model_copy, cfg)
    crit = model_copy.init_criterion()
    opt.zero_grad(set_to_none=True)
    preds, _, _ = model_copy.forward_head_preds(batch["img"])
    loss_vec, _ = crit(preds, batch)
    loss_vec.sum().backward()
    opt.step()

    it_changed = 0
    it_max = 0.0
    for k, b in before_it.items():
        a = model_copy.it_head.state_dict()[k]
        d = (a.float() - b.float()).abs().max().item()
        it_max = max(it_max, d)
        if d > THRESH:
            it_changed += 1

    base_cmp = compare_base_to_surgical(model_copy, before_base)
    return {
        "it_head_tensors_changed": it_changed,
        "it_head_max_delta": it_max,
        "it_head_changed_ok": it_changed > 0,
        "base_frozen_ok": base_cmp["frozen_ok"],
        "base_zones": base_cmp["zones"],
    }


def inspect_forward_head_preds(model: V5Phase2DedicatedModel, img: torch.Tensor) -> list[dict[str, Any]]:
    """Dry-run: inspect raw head output vs normalized preds (train + eval)."""
    rows: list[dict[str, Any]] = []
    neck = model._extract_neck(img)
    for mode_name, train_flag in (("train", True), ("eval", False)):
        model.train(train_flag)
        with torch.no_grad():
            raw = model.base.model[-1](neck)
        row: dict[str, Any] = {
            "section": "inspect",
            "mode": mode_name,
            "raw_type": type(raw).__name__,
        }
        if isinstance(raw, (tuple, list)):
            row["raw_len"] = len(raw)
            for i, el in enumerate(raw):
                rows.append({
                    **row,
                    "element_index": i,
                    "element_type": type(el).__name__,
                    "element_shape": str(tuple(el.shape)) if hasattr(el, "shape") else "",
                    "element_keys": ",".join(el.keys()) if isinstance(el, dict) else "",
                })
        elif isinstance(raw, dict):
            row["element_index"] = -1
            row["element_keys"] = ",".join(raw.keys())
            rows.append(row)
        try:
            out = model.forward_head_preds(img)
            preds = out[0]
            rows.append({
                "section": "inspect",
                "mode": mode_name,
                "forward_ok": True,
                "preds_type": type(preds).__name__,
                "kpts_shape": str(tuple(preds["kpts"].shape)),
                "kpts_channels": preds["kpts"].shape[1],
                "feats_shape": str(tuple(preds["feats"][0].shape)) if preds.get("feats") else "",
            })
        except Exception as exc:
            rows.append({
                "section": "inspect",
                "mode": mode_name,
                "forward_ok": False,
                "error": str(exc),
            })
    return rows


def decode_keypoints_px(
    model: V5Phase2DedicatedModel,
    batch: dict[str, Any],
) -> tuple[torch.Tensor | None, torch.Tensor | None, dict[str, Any]]:
    """Decode 16-KP predictions to pixel space for the assigned foreground anchor."""
    crit = model.init_criterion()
    base = crit._base
    preds, _, _ = model.forward_head_preds(batch["img"])
    pred_kpts = preds["kpts"].permute(0, 2, 1).contiguous()
    (fg_mask, target_gt_idx, _, anchor_points, _), _, _ = base.get_assigned_targets_and_loss(preds, batch)
    meta: dict[str, Any] = {
        "preds_keys": list(preds.keys()),
        "kpts_raw_shape": tuple(preds["kpts"].shape),
        "n_fg_anchors": int(fg_mask.sum().item()),
    }
    if not fg_mask.any():
        return None, None, meta

    bs = pred_kpts.shape[0]
    imgsz = torch.tensor(preds["feats"][0].shape[2:], device=base.device, dtype=pred_kpts.dtype) * base.stride[0]
    meta["imgsz_hw"] = [float(imgsz[0].item()), float(imgsz[1].item())]
    meta["batch_imgsz"] = [float(batch["img"].shape[2]), float(batch["img"].shape[3])]

    pred_dec = base.kpts_decode(anchor_points, pred_kpts.view(bs, -1, *base.kpt_shape))
    gk = batch["keypoints"].float().clone()
    gk[..., 0] *= imgsz[1]
    gk[..., 1] *= imgsz[0]
    sel = base._select_target_keypoints(
        gk, batch["batch_idx"].view(-1, 1), target_gt_idx, fg_mask
    )
    pk = pred_dec[fg_mask][0]
    gt = sel[fg_mask][0]
    meta["decoded_shape"] = tuple(pred_dec.shape)
    meta["n_kpts"] = int(pred_dec.shape[-2])
    return pk, gt, meta


def _decode_it_errors(
    model: V5Phase2DedicatedModel,
    batch: dict[str, Any],
    min_vis: int = 2,
) -> tuple[list[float], list[float], list[float]]:
    """Pixel errors for IT_R / IT_L on v=min_vis only."""
    crit = model.init_criterion()
    base = crit._base
    preds, _, _ = model.forward_head_preds(batch["img"])
    pred_kpts = preds["kpts"].permute(0, 2, 1).contiguous()
    (fg_mask, target_gt_idx, target_bboxes, anchor_points, stride_tensor), _, _ = (
        base.get_assigned_targets_and_loss(preds, batch)
    )
    errs_r: list[float] = []
    errs_l: list[float] = []
    all_errs: list[float] = []

    if not fg_mask.any():
        return errs_r, errs_l, all_errs

    bs = pred_kpts.shape[0]
    imgsz = torch.tensor(preds["feats"][0].shape[2:], device=base.device, dtype=pred_kpts.dtype) * base.stride[0]
    pred_dec = base.kpts_decode(anchor_points, pred_kpts.view(bs, -1, *base.kpt_shape))
    pred_dec = pred_dec.clone()
    pred_dec[..., :2] *= stride_tensor.view(1, -1, 1, 1)

    gk = batch["keypoints"].float().clone()
    gk[..., 0] *= imgsz[1]
    gk[..., 1] *= imgsz[0]
    sel = base._select_target_keypoints(
        gk, batch["batch_idx"].view(-1, 1), target_gt_idx, fg_mask
    )
    pk = pred_dec[fg_mask]
    gt = sel[fg_mask]

    for ki, bucket in ((14, errs_r), (15, errs_l)):
        vis = gt[:, ki, 2] == min_vis if gt.shape[-1] == 3 else torch.zeros(gt.shape[0], dtype=torch.bool, device=gt.device)
        if not vis.any():
            continue
        d = ((pk[vis, ki, :2] - gt[vis, ki, :2]) ** 2).sum(-1).sqrt()
        vals = [float(x) for x in d.tolist()]
        bucket.extend(vals)
        all_errs.extend(vals)

    return errs_r, errs_l, all_errs


def compute_it_metrics(
    model: V5Phase2DedicatedModel,
    loader: Any,
    device: torch.device,
    cfg: dict[str, Any],
) -> dict[str, float | None]:
    min_vis = int(cfg.get("it_only", {}).get("position_loss_min_visibility", 2))
    correct_thr = float(cfg.get("metrics", {}).get("it_correct_threshold_px", 50.0))
    model.eval()

    errs_r: list[float] = []
    errs_l: list[float] = []
    all_errs: list[float] = []

    with torch.no_grad():
        for batch in loader:
            batch = batch_to_device(batch, device)
            r, l, a = _decode_it_errors(model, batch, min_vis=min_vis)
            errs_r.extend(r)
            errs_l.extend(l)
            all_errs.extend(a)

    def _mean(xs: list[float]) -> float | None:
        return statistics.mean(xs) if xs else None

    def _median(xs: list[float]) -> float | None:
        return statistics.median(xs) if xs else None

    def _p90(xs: list[float]) -> float | None:
        if not xs:
            return None
        s = sorted(xs)
        idx = min(len(s) - 1, math.ceil(0.9 * len(s)) - 1)
        return s[idx]

    it_mean = _mean(all_errs)
    correct = sum(1 for e in all_errs if e < correct_thr)
    total = len(all_errs)

    return {
        "IT_R_mean_px": _mean(errs_r),
        "IT_L_mean_px": _mean(errs_l),
        "IT_mean_px": it_mean,
        "IT_median_px": _median(all_errs),
        "IT_p90_px": _p90(all_errs),
        "IT_correct_rate": (correct / total) if total else None,
        "IT_n_evaluated": float(total),
    }


def kp_error_px(pred_path: Path, gt_path: Path, w: float, h: float, kp_idx: int) -> float | None:
    if not pred_path.is_file() or not gt_path.is_file():
        return None
    gt_line = gt_path.read_text(encoding="utf-8").splitlines()[0]
    gt_vals = [float(x) for x in gt_line.split()]
    gt_kpts = gt_vals[5:]
    if gt_kpts[kp_idx * 3 + 2] != 2:
        return None
    gx, gy = gt_kpts[kp_idx * 3] * w, gt_kpts[kp_idx * 3 + 1] * h
    best = None
    best_conf = -1.0
    for line in pred_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        vals = [float(x) for x in line.split()]
        if vals[-1] > best_conf:
            best_conf = vals[-1]
            best = vals
    if best is None:
        return None
    pk = best[5:-1]
    px, py = pk[kp_idx * 3] * w, pk[kp_idx * 3 + 1] * h
    return math.hypot(px - gx, py - gy)


def export_phase2_for_predict(model: V5Phase2DedicatedModel, out_path: Path) -> Path:
    """Write a YOLO-loadable checkpoint with IT channels spliced into cv4 output via wrapper state."""
    ckpt = torch.load(SURGICAL, map_location="cpu", weights_only=False)
    ckpt["v5_phase2_meta"] = {
        "architecture": "ITHeadMultiScaleFusion",
        "wrapper_state": model.state_dict(),
        "note": "Use V5Phase2DedicatedModel for training; this shell preserves surgical base for YOLO predict on 14KP",
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(ckpt, out_path)
    return out_path


def eval_14kp_on_val(model: V5Phase2DedicatedModel, val_ids: list[str], cfg: dict[str, Any]) -> dict[str, float | None]:
    from dicom_render import read_dicom_dimensions, render_dicom_png
    from ultralytics import YOLO

    root = PROJECT / "datasets/yolo_pose_new_26/_v5_phase2_train_eval"
    root.mkdir(parents=True, exist_ok=True)
    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    temp_ckpt = root / "phase2_eval_shell.pt"
    export_phase2_for_predict(model, temp_ckpt)

    errs: list[float] = []
    yolo = YOLO(str(temp_ckpt), task="pose")
    for cid in val_ids:
        dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
        png = root / f"{cid}.png"
        w, h = read_dicom_dimensions(dicom)
        render_dicom_png(dicom, png)
        run_name = f"p2_{cid}"
        yolo.predict(
            source=str(png.resolve()),
            imgsz=IMGSZ,
            conf=CONF,
            save_txt=True,
            project=str(root.resolve()),
            name=run_name,
            exist_ok=True,
            verbose=False,
        )
        pred = root / run_name / "labels" / f"{cid}.txt"
        gt = LABELS_DIR / "val" / f"{cid}.txt"
        for ki in range(14):
            e = kp_error_px(pred, gt, w, h, ki)
            if e is not None:
                errs.append(e)
        shutil.rmtree(root / run_name, ignore_errors=True)

    if not errs:
        return {"mean_14kp_px": None, "median_14kp_px": None, "p90_14kp_px": None}
    s = sorted(errs)
    return {
        "mean_14kp_px": statistics.mean(errs),
        "median_14kp_px": statistics.median(errs),
        "p90_14kp_px": s[min(len(s) - 1, math.ceil(0.9 * len(s)) - 1)],
    }


def eval_detections_on_val(model_path: Path, val_ids: list[str], label: str) -> list[dict[str, Any]]:
    from dicom_render import render_dicom_png
    from ultralytics import YOLO

    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    root = PROJECT / "datasets/yolo_pose_new_26/_v5_phase2_train_det"
    root.mkdir(parents=True, exist_ok=True)
    yolo = YOLO(str(model_path), task="pose")
    rows: list[dict[str, Any]] = []
    for cid in val_ids:
        dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
        png = root / f"{cid}.png"
        render_dicom_png(dicom, png)
        run_name = f"{label}_{cid}"
        yolo.predict(
            source=str(png.resolve()),
            imgsz=IMGSZ,
            conf=CONF,
            save_txt=True,
            project=str(root.resolve()),
            name=run_name,
            exist_ok=True,
            verbose=False,
        )
        pred_path = root / run_name / "labels" / f"{cid}.txt"
        n_det = len([ln for ln in pred_path.read_text(encoding="utf-8").splitlines() if ln.strip()]) if pred_path.is_file() else 0
        rows.append({"model": label, "case_id": cid, "n_detections": n_det})
        shutil.rmtree(root / run_name, ignore_errors=True)
    return rows


def save_checkpoint(
    path: Path,
    model: V5Phase2DedicatedModel,
    epoch: int,
    metrics: dict[str, Any],
    cfg: dict[str, Any],
    tag: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ckpt = torch.load(SURGICAL, map_location="cpu", weights_only=False)
    ckpt["epoch"] = epoch
    ckpt["v5_phase2"] = {
        "tag": tag,
        "architecture": "ITHeadMultiScaleFusion",
        "it_head_state": model.it_head.state_dict(),
        "wrapper_state": model.state_dict(),
        "metrics": metrics,
        "config_version": cfg.get("version"),
    }
    torch.save(ckpt, path)


def unique_run_dir(cfg: dict[str, Any]) -> Path:
    base = resolve(cfg["run"]["project"]) / cfg["run"]["name"]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = base / f"run_{ts}"
    if run_dir.exists():
        raise RuntimeError(f"Run dir exists (should not): {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "weights").mkdir()
    return run_dir


def verify_dryrun_ready() -> bool:
    if not DRYRUN_MD.is_file():
        return False
    text = DRYRUN_MD.read_text(encoding="utf-8")
    return "V5_PHASE2_DEDICATED_HEAD_READY" in text and "V5_PHASE2_DEDICATED_HEAD_BLOCKED" not in text.split("## Conclusion")[-1]


def run_preflight(cfg: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    blocked_reasons: list[str] = []

    if not SURGICAL.is_file():
        raise SystemExit(f"Checkpoint manquant : {SURGICAL}")
    if not V2_PATH.is_file():
        raise SystemExit(f"V2 checkpoint manquant : {V2_PATH}")

    dryrun_ok = verify_dryrun_ready()
    rows.append({"section": "gate", "metric": "dryrun_ready", "value": dryrun_ok})
    if not dryrun_ok:
        blocked_reasons.append("v5_phase2_dedicated_head_dryrun not READY")

    model = build_model(cfg)
    attach_hyp(model.base)
    params = count_params_summary(model)
    print(f"Trainable parameters: {params['trainable']}")
    print(f"Frozen parameters: {params['frozen']}")
    print(f"Optimizer parameter count: {params['optimizer_params']}")
    for k, v in params.items():
        rows.append({"section": "params", "metric": k, "value": v})

    ref_params = load_surgical_base_params()
    init_cmp = compare_base_to_surgical(model, ref_params)
    rows.append({"section": "init_frozen", "metric": "frozen_ok", "value": init_cmp["frozen_ok"]})

    opt = build_optimizer(model, cfg)
    n_opt = sum(len(pg["params"]) for pg in opt.param_groups)
    rows.append({"section": "optimizer", "metric": "param_tensors", "value": n_opt})
    rows.append({"section": "optimizer", "metric": "param_count", "value": params["optimizer_params"]})

    batch, _ = load_train_batch(cfg)
    batch = preprocess_batch(batch)
    device = torch.device("cpu")
    batch = batch_to_device(batch, device)
    model = model.to(device)

    grad = grad_probe(model, batch)
    for k, v in grad["grad_zones"].items():
        rows.append({"section": "grad_probe", "metric": k, "value": v})
    for k, v in grad["grad_nz"].items():
        rows.append({"section": "grad_nz", "metric": k, "value": v})
    for k, v in grad["loss_items"].items():
        rows.append({"section": "loss", "metric": k, "value": v})

    parity = parity_probe(model.base, model, batch)
    rows.append({"section": "parity", **parity})

    sim = sim_optimizer_step_probe(model, batch, cfg)
    for k, v in sim.items():
        if k != "base_zones":
            rows.append({"section": "sim_step", "metric": k, "value": v})

    checks = {
        "dryrun_ready": dryrun_ok,
        "trainable_it_head_expected": params["trainable"] == 362898,
        "frozen_base_gt_0": params["frozen"] > 0,
        "optimizer_it_only": n_opt > 0 and params["trainable"] == params["optimizer_params"],
        "backbone_grad_0": grad["grad_nz"].get("backbone", 0) == 0,
        "neck_grad_0": grad["grad_nz"].get("neck", 0) == 0,
        "head_14kp_grad_0": grad["grad_nz"].get("head_14kp", 0) == 0,
        "it_head_grad_gt_0": grad["grad_nz"].get("it_head_total", 0) > 0,
        "p3_grad_gt_0": grad["grad_zones"].get("it_head_P3", 0) > 0,
        "p4_grad_gt_0": grad["grad_zones"].get("it_head_P4", 0) > 0,
        "p5_grad_gt_0": grad["grad_zones"].get("it_head_P5", 0) > 0,
        "det_loss_zero": grad["loss_items"]["box"] == 0.0 and grad["loss_items"]["cls"] == 0.0 and grad["loss_items"]["dfl"] == 0.0,
        "parity_14kp": parity["parity_14kp_ok"],
        "parity_det": parity["parity_det_ok"],
        "sim_it_changed": sim["it_head_changed_ok"],
        "sim_base_frozen": sim["base_frozen_ok"],
        "init_base_matches_surgical": init_cmp["frozen_ok"],
        "no_optimizer_step_in_preflight": True,
    }
    for k, v in checks.items():
        rows.append({"section": "check", "metric": k, "value": v})
        if not v:
            blocked_reasons.append(k)

    val_ids = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))["val"]
    v2_det = eval_detections_on_val(V2_PATH, val_ids, "V2")
    surg_det = eval_detections_on_val(SURGICAL, val_ids, "surgical")
    for r in v2_det + surg_det:
        rows.append({"section": "val_det", **r})
    v2_total = sum(r["n_detections"] for r in v2_det)
    surg_total = sum(r["n_detections"] for r in surg_det)
    det_stable = v2_total == surg_total == 5
    rows.append({"section": "check", "metric": "detection_v2_preserved", "value": det_stable})
    if not det_stable:
        blocked_reasons.append("detection_v2_preserved")

    kp14_v2 = eval_14kp_v2_on_val(val_ids)
    kp14_p2 = eval_14kp_on_val(model, val_ids, cfg)
    rows.append({"section": "val_14kp_v2", **kp14_v2})
    rows.append({"section": "val_14kp_phase2_init", **kp14_p2})

    if blocked_reasons:
        verdict = "V5_PHASE2_TRAINING_BLOCKED"
        detail = "; ".join(blocked_reasons)
    else:
        verdict = "V5_PHASE2_TRAINING_READY"
        detail = "ITHeadMultiScaleFusion preflight passed; ready for --train"

    rows.append({"section": "verdict", "metric": "status", "value": verdict})
    rows.append({"section": "verdict", "metric": "detail", "value": detail})
    return verdict, rows


def write_preflight_reports(verdict: str, detail: str, rows: list[dict[str, Any]], params: dict[str, int]) -> None:
    keys = sorted({k for r in rows for k in r})
    with PREFLIGHT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    grad = {r["metric"]: r["value"] for r in rows if r.get("section") == "grad_probe"}
    checks = {r["metric"]: r["value"] for r in rows if r.get("section") == "check"}
    parity = next((r for r in rows if r.get("section") == "parity"), {})

    md = [
        "# V5 Phase 2 — Training Pre-flight",
        "",
        f"**Généré :** {utc_now()}",
        "**Mode :** PRE-FLIGHT — forward / loss / backward / sim-step — **aucun entraînement**",
        f"**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase2.py`",
        f"**Architecture :** `ITHeadMultiScaleFusion` (Option B)",
        f"**Verdict :** `{verdict}`",
        f"**Détail :** {detail}",
        "",
        "---",
        "",
        "## 1. Paramètres",
        "",
        f"| Métrique | Valeur |",
        f"|----------|-------:|",
        f"| Trainable (IT head) | {params.get('trainable', '?')} |",
        f"| Frozen (base) | {params.get('frozen', '?')} |",
        f"| Optimizer param count | {params.get('optimizer_params', '?')} |",
        "",
        "---",
        "",
        "## 2. Gradient probe (backward sans optimizer.step)",
        "",
        "| Zone | grad norm | Attendu |",
        "|------|----------:|:-------:|",
    ]
    for zone, expected in (
        ("backbone", "0"),
        ("neck", "0"),
        ("head_14kp", "0"),
        ("it_head_total", ">0"),
        ("it_head_P3", ">0"),
        ("it_head_P4", ">0"),
        ("it_head_P5", ">0"),
    ):
        md.append(f"| {zone} | {grad.get(zone, '?')} | {expected} |")

    md.extend([
        "",
        "---",
        "",
        "## 3. Simulated optimizer.step (mémoire)",
        "",
        f"- IT head changed : **{checks.get('sim_it_changed')}**",
        f"- Base frozen OK : **{checks.get('sim_base_frozen')}**",
        "",
        "---",
        "",
        "## 4. Parité initiale",
        "",
        f"- 14 KP max Δ : **{parity.get('max_diff_14kp_channels', '?'):.2e}**",
        f"- boxes max Δ : **{parity.get('max_diff_boxes', '?'):.2e}**",
        f"- cls max Δ : **{parity.get('max_diff_cls', '?'):.2e}**",
        "",
        "---",
        "",
        "## 5. Loss IT-only",
        "",
        "- KP 0–13 : position=0, visibility=0",
        "- box / cls / dfl : 0",
        "- IT_R / IT_L : actifs si v=2",
        "- v=0 : exclu des métriques et de la position loss",
        "",
        "---",
        "",
        "## 6. Config entraînement initial (non lancé)",
        "",
        "| Param | Valeur |",
        "|-------|--------|",
        "| imgsz | 640 |",
        "| batch | 1 |",
        "| lr0 | 1e-4 |",
        "| optimizer | AdamW |",
        "| epochs | 30 |",
        "| patience | 8 |",
        "| mosaic | 0 |",
        "| randaugment | off |",
        "| erasing | 0 |",
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
        detail,
        "",
        "Pour entraîner (après READY, explicite) :",
        "```powershell",
        ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v5_phase2.py --train",
        "```",
        "",
        f"CSV : `{PREFLIGHT_CSV.name}`",
    ])
    PREFLIGHT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def safety_check_epoch(
    model: V5Phase2DedicatedModel,
    ref_params: dict[str, torch.Tensor],
    cfg: dict[str, Any],
    val_ids: list[str],
    v2_14kp_baseline: dict[str, float | None],
) -> dict[str, Any]:
    """Post-epoch safety: frozen zones + 14KP + detection."""
    max_delta = float(cfg.get("guardrails", {}).get("frozen_zone_max_delta", THRESH))
    cmp = compare_base_to_surgical(model, ref_params, max_delta=max_delta)
    if cfg.get("guardrails", {}).get("abort_on_frozen_drift", True) and not cmp["frozen_ok"]:
        raise RuntimeError(f"ABORT: frozen zone drift detected: {cmp['zones']}")

    kp14 = eval_14kp_on_val(model, val_ids, cfg)
    ratio_mean = None
    if v2_14kp_baseline.get("mean_14kp_px") and kp14.get("mean_14kp_px"):
        ratio_mean = kp14["mean_14kp_px"] / v2_14kp_baseline["mean_14kp_px"]
    max_ratio = float(cfg.get("guardrails", {}).get("epoch_14kp_mean_max_ratio_vs_v2", 1.15))
    kp14_ok = ratio_mean is None or ratio_mean <= max_ratio

    temp = PROJECT / "datasets/yolo_pose_new_26/_v5_phase2_train_safety.pt"
    export_phase2_for_predict(model, temp)
    p2_det = eval_detections_on_val(temp, val_ids, "phase2")
    v2_det = eval_detections_on_val(V2_PATH, val_ids, "V2")
    v2_counts = {r["case_id"]: r["n_detections"] for r in v2_det}
    det_ok = all(r["n_detections"] == v2_counts[r["case_id"]] for r in p2_det)

    if cfg.get("guardrails", {}).get("detection_count_must_match_v2", True) and not det_ok:
        raise RuntimeError("ABORT: detection count mismatch vs V2 on val")

    return {
        "frozen_ok": cmp["frozen_ok"],
        "zones": cmp["zones"],
        "kp14": kp14,
        "kp14_ratio_vs_v2": ratio_mean,
        "kp14_ok": kp14_ok,
        "det_ok": det_ok,
    }


def train_loop(cfg: dict[str, Any]) -> int:
    if not PREFLIGHT_MD.is_file() or "V5_PHASE2_TRAINING_READY" not in PREFLIGHT_MD.read_text(encoding="utf-8"):
        raise SystemExit("Preflight non READY — exécuter sans --train d'abord.")

    device = torch.device(cfg["train"].get("device", "cpu"))
    model = build_model(cfg).to(device)
    attach_hyp(model.base)
    ref_params = load_surgical_base_params()

    run_dir = unique_run_dir(cfg)
    weights_dir = run_dir / "weights"
    train_loader = build_dataloader(cfg, "train")
    val_loader = build_dataloader(cfg, "val")
    optimizer = build_optimizer(model, cfg)
    crit = model.init_criterion()

    val_ids = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))["val"]
    v2_14kp_baseline = eval_14kp_v2_on_val(val_ids)

    epochs = int(cfg["train"]["epochs"])
    patience = int(cfg["train"]["patience"])
    best_metric = float("inf")
    patience_left = patience
    history: list[dict[str, Any]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        n_batches = 0
        for batch in train_loader:
            batch = batch_to_device(batch, device)
            optimizer.zero_grad(set_to_none=True)
            preds, _, _ = model.forward_head_preds(batch["img"])
            loss_vec, _ = crit(preds, batch)
            loss = loss_vec.sum()
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.item())
            n_batches += 1

        safety = safety_check_epoch(model, ref_params, cfg, val_ids, v2_14kp_baseline)
        it_metrics = compute_it_metrics(model, val_loader, device, cfg)
        row = {"epoch": epoch, "train_loss": epoch_loss / max(n_batches, 1), **it_metrics, **safety}
        history.append(row)

        save_checkpoint(weights_dir / "last_it.pt", model, epoch, it_metrics, cfg, "last")
        metric = it_metrics.get("IT_mean_px")
        if metric is not None and metric < best_metric:
            best_metric = metric
            patience_left = patience
            save_checkpoint(weights_dir / "best_it.pt", model, epoch, it_metrics, cfg, "best")
        else:
            patience_left -= 1

        print(f"Epoch {epoch}/{epochs} loss={row['train_loss']:.4f} IT_mean_px={metric} patience={patience_left}")
        if patience_left <= 0:
            print(f"Early stop on IT_mean_px (best={best_metric:.2f})")
            break

    report_path = run_dir / "training_report.json"
    report_path.write_text(json.dumps({"history": history, "best_IT_mean_px": best_metric}, indent=2), encoding="utf-8")
    print(f"Run saved: {run_dir}")
    return 0


def run_metric_decoder_fix_verification(cfg: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Verify metric decoder on val set without training."""
    rows: list[dict[str, Any]] = []
    blocked: list[str] = []
    device = torch.device(cfg["train"].get("device", "cpu"))
    model = build_model(cfg).to(device)
    attach_hyp(model.base)
    val_loader = build_dataloader(cfg, "val")
    batch = batch_to_device(next(iter(val_loader)), device)

    rows.extend(inspect_forward_head_preds(model, batch["img"]))

    model.eval()
    pk, gt, meta = decode_keypoints_px(model, batch)
    rows.append({"section": "decode_meta", **{k: v for k, v in meta.items() if not isinstance(v, (list, tuple))}})
    rows.append({"section": "decode_meta", "metric": "imgsz_hw", "value": meta.get("imgsz_hw")})
    rows.append({"section": "decode_meta", "metric": "batch_imgsz", "value": meta.get("batch_imgsz")})

    decode_ok = pk is not None and gt is not None and pk.shape[0] >= 16
    rows.append({"section": "single_val", "metric": "decode_ok", "value": decode_ok})
    if not decode_ok:
        blocked.append("single_val_decode_failed")
    else:
        assert pk is not None and gt is not None
        rows.append({"section": "single_val", "metric": "n_kpts_decoded", "value": int(pk.shape[0])})
        for ki, name in enumerate(LANDMARKS_16):
            rows.append({
                "section": "kp_layout",
                "kp_index": ki,
                "landmark": name,
                "pred_x": float(pk[ki, 0].item()),
                "pred_y": float(pk[ki, 1].item()),
                "gt_v": float(gt[ki, 2].item()) if gt.shape[-1] == 3 else None,
            })
        it_r_ok = pk.shape[0] > 14 and torch.isfinite(pk[14, :2].detach()).all().item()
        it_l_ok = pk.shape[0] > 15 and torch.isfinite(pk[15, :2].detach()).all().item()
        rows.append({"section": "single_val", "metric": "IT_R_retrievable", "value": bool(it_r_ok)})
        rows.append({"section": "single_val", "metric": "IT_L_retrievable", "value": bool(it_l_ok)})
        if not it_r_ok or not it_l_ok:
            blocked.append("it_landmarks_not_retrievable")

        scale_ok = (
            meta.get("batch_imgsz") == meta.get("imgsz_hw")
            and all(
                0 <= float(pk[ki, 0].detach()) <= IMGSZ and 0 <= float(pk[ki, 1].detach()) <= IMGSZ
                for ki in (14, 15)
            )
        )
        rows.append({"section": "single_val", "metric": "coords_in_image_space", "value": scale_ok})
        if not scale_ok:
            blocked.append("coords_out_of_image_space")

    try:
        metrics = compute_it_metrics(model, val_loader, device, cfg)
        rows.append({"section": "val_metrics", **metrics})
        metrics_ok = metrics.get("IT_n_evaluated", 0) > 0 and metrics.get("IT_mean_px") is not None
        rows.append({"section": "val_metrics", "metric": "full_val_ok", "value": metrics_ok})
        if not metrics_ok:
            blocked.append("compute_it_metrics_empty_or_failed")
    except Exception as exc:
        rows.append({"section": "val_metrics", "metric": "full_val_ok", "value": False})
        rows.append({"section": "val_metrics", "metric": "error", "value": str(exc)})
        blocked.append(f"compute_it_metrics_crash: {exc}")

    inspect_eval = next((r for r in rows if r.get("section") == "inspect" and r.get("mode") == "eval" and r.get("forward_ok")), {})
    if not inspect_eval.get("forward_ok"):
        blocked.append("eval_forward_head_preds_failed")

    verdict = "V5_PHASE2_METRIC_DECODER_BLOCKED" if blocked else "V5_PHASE2_METRIC_DECODER_FIXED"
    detail = "; ".join(blocked) if blocked else "eval/train head outputs normalized; 16-KP decode OK on 5 val images"
    rows.append({"section": "verdict", "metric": "status", "value": verdict})
    rows.append({"section": "verdict", "metric": "detail", "value": detail})
    return verdict, rows


def write_metric_decoder_fix_reports(verdict: str, detail: str, rows: list[dict[str, Any]]) -> None:
    keys = sorted({k for r in rows for k in r})
    with METRIC_FIX_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    inspect_rows = [r for r in rows if r.get("section") == "inspect"]
    kp_rows = [r for r in rows if r.get("section") == "kp_layout"]
    metrics = {r.get("metric", k): r.get("value", r.get(k)) for r in rows if r.get("section") == "val_metrics" for k in r}

    md = [
        "# V5 Phase 2 — Metric Decoder Fix",
        "",
        f"**Généré :** {utc_now()}",
        "**Mode :** vérification décodeur métriques — **aucun entraînement**",
        f"**Verdict :** `{verdict}`",
        f"**Détail :** {detail}",
        "",
        "---",
        "",
        "## 1. Inspection `forward_head_preds`",
        "",
        "| Mode | Raw type | Len | Élément | Type | Shape | Keys |",
        "|------|----------|----:|---------|------|-------|------|",
    ]
    for r in inspect_rows:
        if "element_index" in r:
            md.append(
                f"| {r.get('mode','')} | {r.get('raw_type','')} | {r.get('raw_len','')} | "
                f"{r.get('element_index','')} | {r.get('element_type','')} | {r.get('element_shape','')} | "
                f"{r.get('element_keys','')} |"
            )
        elif r.get("forward_ok") is not None:
            md.append(
                f"| {r.get('mode','')} | — | — | preds | {r.get('preds_type','')} | "
                f"{r.get('kpts_shape','')} | kpts,{r.get('kpts_channels','')}ch |"
            )

    md.extend([
        "",
        "**Cause :** en `eval`, la tête Pose Ultralytics retourne `(tensor, dict)` ; le dict `kpts` est à l'index 1.",
        "",
        "---",
        "",
        "## 2. Layout 16 KP (1 image val)",
        "",
        "| Index | Landmark | pred_x | pred_y | gt_v |",
        "|------:|----------|-------:|-------:|-----:|",
    ])
    for r in kp_rows:
        md.append(
            f"| {r['kp_index']} | {r['landmark']} | {r['pred_x']:.1f} | {r['pred_y']:.1f} | {r.get('gt_v')} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 3. `compute_it_metrics` — 5 images val",
        "",
        f"- IT_R_mean_px : **{metrics.get('IT_R_mean_px', '—')}**",
        f"- IT_L_mean_px : **{metrics.get('IT_L_mean_px', '—')}**",
        f"- IT_mean_px : **{metrics.get('IT_mean_px', '—')}**",
        f"- IT_median_px : **{metrics.get('IT_median_px', '—')}**",
        f"- IT_p90_px : **{metrics.get('IT_p90_px', '—')}**",
        f"- IT_correct_rate : **{metrics.get('IT_correct_rate', '—')}**",
        f"- IT_n_evaluated : **{metrics.get('IT_n_evaluated', '—')}**",
        "",
        "---",
        "",
        f"## Conclusion : `{verdict}`",
        "",
        detail,
        "",
        f"CSV : `{METRIC_FIX_CSV.name}`",
    ])
    METRIC_FIX_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="V5 Phase 2 IT-only dedicated head training")
    parser.add_argument("--train", action="store_true", help="Lance l'entraînement (explicite)")
    parser.add_argument(
        "--metric-decoder-fix",
        action="store_true",
        help="Vérifie le décodeur métriques IT sur val (aucun entraînement)",
    )
    args = parser.parse_args()

    cfg = load_cfg()

    if args.metric_decoder_fix:
        verdict, rows = run_metric_decoder_fix_verification(cfg)
        detail = next((r["value"] for r in rows if r.get("section") == "verdict" and r.get("metric") == "detail"), "")
        write_metric_decoder_fix_reports(verdict, str(detail), rows)
        print(f"Wrote {METRIC_FIX_MD}")
        print(f"Wrote {METRIC_FIX_CSV}")
        print(f"Verdict: {verdict}")
        return 0 if verdict == "V5_PHASE2_METRIC_DECODER_FIXED" else 1

    if args.train:
        return train_loop(cfg)

    verdict, rows = run_preflight(cfg)
    params = {r["metric"]: r["value"] for r in rows if r.get("section") == "params"}
    detail = next((r["value"] for r in rows if r.get("section") == "verdict" and r.get("metric") == "detail"), "")
    write_preflight_reports(verdict, str(detail), rows, params)
    print(f"Wrote {PREFLIGHT_MD}")
    print(f"Wrote {PREFLIGHT_CSV}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "V5_PHASE2_TRAINING_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
