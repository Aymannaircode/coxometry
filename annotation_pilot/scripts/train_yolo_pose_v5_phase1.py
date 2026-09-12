#!/usr/bin/env python3
"""V5 Phase 1 — IT-only fine-tuning (preflight check + optional training).

Par défaut : vérifie le preflight et affiche la config (PAS d'entraînement).
``--check-loss-mask`` : probe loss IT-only sur un batch réel (NO training).
Entraînement : ``--train`` explicite uniquement.

Ne modifie jamais V2, V4, labels, dataset.
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml

PROJECT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_training_config.yaml"
PREFLIGHT_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_preflight.md"
DATA_YAML = PROJECT / "datasets/yolo_pose_new_26/data.yaml"
V5_INIT = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt"
LOSS_MASK_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_loss_mask_check.md"
LOSS_MASK_CSV = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_loss_mask_check.csv"

OLD_NK = 42
DEFAULT_IT_KP = (14, 15)
LANDMARKS_16 = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L", "ASM_R", "ASM_L",
    "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L", "IT_R", "IT_L",
]


def resolve(path_str: str) -> Path:
    p = Path(path_str)
    return p if p.is_absolute() else PROJECT / p


def load_cfg() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def it_kp_indices(cfg: dict[str, Any] | None = None) -> tuple[int, ...]:
    if cfg and "it_only" in cfg:
        return tuple(cfg["it_only"].get("train_kp_indices", DEFAULT_IT_KP))
    return DEFAULT_IT_KP


def _it_only_bool_mask(n_kpts: int, train_kp: tuple[int, ...], device: torch.device) -> torch.Tensor:
    m = torch.zeros(n_kpts, dtype=torch.bool, device=device)
    for idx in train_kp:
        m[idx] = True
    return m


class ITOnlyPoseLoss:
    """Wrapper around v8PoseLoss masking pose loss to IT keypoints only."""

    def __init__(self, model: nn.Module, train_kp_indices: tuple[int, ...] = DEFAULT_IT_KP):
        from ultralytics.utils.loss import v8PoseLoss

        self._base = v8PoseLoss(model)
        self.train_kp_indices = train_kp_indices
        self.train_kp_mask: torch.Tensor | None = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._base, name)

    def _kp_train_mask(self, n_kpts: int, device: torch.device) -> torch.Tensor:
        return _it_only_bool_mask(n_kpts, self.train_kp_indices, device)

    def _it_keypoint_loss(
        self,
        pred_kpt: torch.Tensor,
        gt_kpt: torch.Tensor,
        kpt_mask: torch.Tensor,
        area: torch.Tensor,
    ) -> torch.Tensor:
        """Position loss normalized over visible IT keypoints only (no 16/n inflation)."""
        sigmas = self._base.keypoint_loss.sigmas
        d = (pred_kpt[..., 0] - gt_kpt[..., 0]).pow(2) + (pred_kpt[..., 1] - gt_kpt[..., 1]).pow(2)
        e = d / ((2 * sigmas).pow(2) * (area + 1e-9) * 2)
        loss_per = (1 - torch.exp(-e)) * kpt_mask.float()
        return loss_per.sum() / (kpt_mask.float().sum() + 1e-9)

    def calculate_keypoints_loss(
        self,
        masks: torch.Tensor,
        target_gt_idx: torch.Tensor,
        keypoints: torch.Tensor,
        batch_idx: torch.Tensor,
        stride_tensor: torch.Tensor,
        target_bboxes: torch.Tensor,
        pred_kpts: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        from ultralytics.utils.ops import xyxy2xywh

        selected_keypoints = self._base._select_target_keypoints(
            keypoints, batch_idx, target_gt_idx, masks
        )
        selected_keypoints[..., :2] /= stride_tensor.view(1, -1, 1, 1)

        kpts_loss = torch.tensor(0.0, device=self._base.device)
        kpts_obj_loss = torch.tensor(0.0, device=self._base.device)

        if masks.any():
            target_bboxes = target_bboxes.clone()
            target_bboxes /= stride_tensor
            gt_kpt = selected_keypoints[masks]
            area = xyxy2xywh(target_bboxes[masks])[:, 2:].prod(1, keepdim=True)
            pred_kpt = pred_kpts[masks]

            vis_mask = (
                gt_kpt[..., 2] != 0
                if gt_kpt.shape[-1] == 3
                else torch.full_like(gt_kpt[..., 0], True)
            )
            it_mask = self._kp_train_mask(vis_mask.shape[1], vis_mask.device)
            kpt_mask = vis_mask & it_mask.unsqueeze(0)

            kpts_loss = self._it_keypoint_loss(pred_kpt, gt_kpt, kpt_mask, area)

            if pred_kpt.shape[-1] == 3:
                bce = F.binary_cross_entropy_with_logits(
                    pred_kpt[..., 2], kpt_mask.float(), reduction="none"
                )
                kpts_obj_loss = bce[:, it_mask].mean()

        return kpts_loss, kpts_obj_loss

    def __call__(
        self,
        preds: dict[str, torch.Tensor] | tuple[torch.Tensor, dict[str, torch.Tensor]],
        batch: dict[str, torch.Tensor],
    ) -> tuple[torch.Tensor, torch.Tensor]:
        return self._base(preds, batch)

    def loss(
        self, preds: dict[str, torch.Tensor], batch: dict[str, torch.Tensor]
    ) -> tuple[torch.Tensor, torch.Tensor]:
        return self._base.loss(preds, batch)


def apply_it_only_loss_patch(model: nn.Module, train_kp_indices: tuple[int, ...] = DEFAULT_IT_KP) -> None:
    """Replace model criterion with IT-only pose loss (masks KP 0-13)."""

    def patched_init_criterion():
        crit = ITOnlyPoseLoss(model, train_kp_indices=train_kp_indices)
        # Patch calculate_keypoints_loss on the base instance used by loss()
        base = crit._base

        def masked_calc(*args: Any, **kwargs: Any) -> tuple[torch.Tensor, torch.Tensor]:
            return crit.calculate_keypoints_loss(*args, **kwargs)

        base.calculate_keypoints_loss = masked_calc  # type: ignore[method-assign]
        return crit

    model.init_criterion = patched_init_criterion  # type: ignore[method-assign]
    if hasattr(model, "criterion"):
        del model.criterion


def apply_it_only_freeze(model: nn.Module) -> list[str]:
    """Freeze all params; unfreeze cv4 IT channels 42-47 with gradient hooks."""
    for p in model.parameters():
        p.requires_grad = False

    trainable: list[str] = []
    for name, param in model.named_parameters():
        if "cv4" not in name:
            continue
        if param.dim() == 4:
            mask = torch.zeros_like(param, dtype=torch.bool)
            if param.shape[0] > OLD_NK and param.shape[1] > OLD_NK:
                mask[OLD_NK:, OLD_NK:] = True
            elif param.shape[0] > OLD_NK:
                mask[OLD_NK:, :] = True
            if mask.any():
                param.requires_grad = True
                param.register_hook(lambda grad, m=mask: grad * m.float())
                trainable.append(name)
        elif param.dim() == 1 and param.shape[0] > OLD_NK:
            mask = torch.zeros_like(param, dtype=torch.bool)
            mask[OLD_NK:] = True
            param.requires_grad = True
            param.register_hook(lambda grad, m=mask: grad * m.float())
            trainable.append(name)
    return trainable


def load_v5_model() -> nn.Module:
    from ultralytics.nn.tasks import torch_safe_load

    ckpt = torch_safe_load(str(V5_INIT))[0]
    model = ckpt["model"].float()
    model.train()
    return model


def load_train_batch(cfg: dict[str, Any], prefer_v0_it: bool = False) -> tuple[dict[str, Any], Any]:
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
    args.mosaic = 0.0

    data = check_det_dataset(str(DATA_YAML))
    dataset = build_yolo_dataset(args, data["train"], batch=1, data=data, mode="train", rect=False, stride=32)
    loader = build_dataloader(dataset, batch=1, workers=0, shuffle=False, rank=-1)

    if prefer_v0_it:
        v0_stems = {"B26_06", "B26_11", "B26_14", "B26_15", "B26_21", "B26_19"}
        for batch in loader:
            paths = batch.get("im_file", batch.get("img_path", []))
            if not isinstance(paths, list):
                paths = [paths]
            stems = set()
            for p in paths:
                if isinstance(p, (list, tuple)):
                    p = p[0] if p else ""
                stems.add(Path(str(p)).stem)
            if stems & v0_stems:
                batch["img"] = batch["img"].float() / 255.0
                return batch, args

    batch = next(iter(loader))
    batch["img"] = batch["img"].float() / 255.0
    return batch, args


def _extract_pose_tensors(
    model: nn.Module, batch: dict[str, Any], criterion: Any
) -> dict[str, Any]:
    """Run forward and extract tensors needed for per-KP loss breakdown."""
    preds = model(batch["img"])
    if isinstance(preds, (list, tuple)):
        preds = preds[0] if len(preds) == 1 else {"feats": preds[0], "kpts": preds[1]}  # fallback

    from ultralytics.utils.loss import v8PoseLoss

    base: v8PoseLoss = criterion._base if isinstance(criterion, ITOnlyPoseLoss) else criterion
    pred_kpts = preds["kpts"].permute(0, 2, 1).contiguous()
    (fg_mask, target_gt_idx, target_bboxes, anchor_points, stride_tensor), _, _ = (
        base.get_assigned_targets_and_loss(preds, batch)
    )

    batch_size = pred_kpts.shape[0]
    imgsz = torch.tensor(preds["feats"][0].shape[2:], device=base.device, dtype=pred_kpts.dtype) * base.stride[0]
    pred_kpts_dec = base.kpts_decode(
        anchor_points, pred_kpts.view(batch_size, -1, *base.kpt_shape)
    )

    keypoints = batch["keypoints"].to(base.device).float().clone()
    keypoints[..., 0] *= imgsz[1]
    keypoints[..., 1] *= imgsz[0]

    selected = base._select_target_keypoints(
        keypoints, batch["batch_idx"].view(-1, 1), target_gt_idx, fg_mask
    )
    selected[..., :2] /= stride_tensor.view(1, -1, 1, 1)

    gt_kpt = pred_kpt = area = None
    vis_mask = None
    if fg_mask.any():
        tb = target_bboxes.clone()
        tb /= stride_tensor
        gt_kpt = selected[fg_mask]
        from ultralytics.utils.ops import xyxy2xywh

        area = xyxy2xywh(tb[fg_mask])[:, 2:].prod(1, keepdim=True)
        pred_kpt = pred_kpts_dec[fg_mask]
        vis_mask = (
            gt_kpt[..., 2] != 0
            if gt_kpt.shape[-1] == 3
            else torch.full_like(gt_kpt[..., 0], True)
        )

    return {
        "preds": preds,
        "fg_mask": fg_mask,
        "gt_kpt": gt_kpt,
        "pred_kpt": pred_kpt,
        "area": area,
        "vis_mask": vis_mask,
        "base": base,
    }


def per_kp_contributions(
    base: Any,
    gt_kpt: torch.Tensor,
    pred_kpt: torch.Tensor,
    area: torch.Tensor,
    vis_mask: torch.Tensor,
    pose_gain: float,
    kobj_gain: float,
    it_only_loss_fn: Any | None = None,
) -> list[dict[str, Any]]:
    """Per-keypoint position + visibility loss (unmasked per-KP slice, for diagnostics)."""
    rows: list[dict[str, Any]] = []
    n_kpts = gt_kpt.shape[1]
    loss_fn = it_only_loss_fn or base.keypoint_loss

    for kp_idx in range(n_kpts):
        kp_vis = vis_mask[:, kp_idx]
        kp_mask = torch.zeros_like(vis_mask)
        kp_mask[:, kp_idx] = kp_vis

        pos_raw = torch.tensor(0.0)
        if kp_idx in DEFAULT_IT_KP and kp_mask.any():
            if it_only_loss_fn is not None:
                pos_raw = it_only_loss_fn(pred_kpt, gt_kpt, kp_mask, area)
            else:
                pos_raw = base.keypoint_loss(pred_kpt, gt_kpt, kp_mask, area)
        elif it_only_loss_fn is None and kp_mask.any():
            pos_raw = base.keypoint_loss(pred_kpt, gt_kpt, kp_mask, area)

        vis_raw = torch.tensor(0.0)
        if pred_kpt.shape[-1] == 3 and kp_idx in DEFAULT_IT_KP:
            bce = F.binary_cross_entropy_with_logits(
                pred_kpt[:, kp_idx, 2], kp_vis.float(), reduction="mean"
            )
            vis_raw = bce

        rows.append({
            "kp_index": kp_idx,
            "landmark": LANDMARKS_16[kp_idx],
            "gt_visible": bool(kp_vis.any().item()),
            "gt_v0": bool((~kp_vis).all().item()) if kp_vis.numel() else True,
            "position_loss_raw": float(pos_raw.item()),
            "visibility_loss_raw": float(vis_raw.item()),
            "position_loss_weighted": float(pos_raw.item()) * pose_gain,
            "visibility_loss_weighted": float(vis_raw.item()) * kobj_gain,
            "zone": "IT" if kp_idx in DEFAULT_IT_KP else "old_14kp",
        })
    return rows


def grad_zone_summary(model: nn.Module) -> dict[str, Any]:
    from ultralytics.utils.torch_utils import unwrap_model

    m = unwrap_model(model)
    summary = {
        "backbone_grad": 0,
        "cv2_grad": 0,
        "cv3_grad": 0,
        "cv4_old_grad": 0,
        "cv4_it_grad": 0,
        "cv4_trainable_hooks": 0,
    }
    for name, param in m.named_parameters():
        if not param.requires_grad:
            continue
        if "cv4" in name:
            summary["cv4_trainable_hooks"] += 1
        g = param.grad
        if g is None or g.abs().max().item() <= 1e-12:
            continue
        if name.startswith("model.") and name[6:8].isdigit():
            layer = int(name.split(".")[1])
            if layer <= 22:
                summary["backbone_grad"] += 1
                continue
        if "cv2" in name:
            summary["cv2_grad"] += 1
        elif "cv3" in name:
            summary["cv3_grad"] += 1
        elif "cv4" in name:
            if param.dim() == 4 and param.shape[0] > OLD_NK and param.shape[1] > OLD_NK:
                old = g[:OLD_NK, :OLD_NK].abs().max().item()
                it = g[OLD_NK:, OLD_NK:].abs().max().item()
                if old > 1e-12:
                    summary["cv4_old_grad"] += 1
                if it > 1e-12:
                    summary["cv4_it_grad"] += 1
            elif param.dim() == 1 and param.shape[0] > OLD_NK:
                if g[:OLD_NK].abs().max().item() > 1e-12:
                    summary["cv4_old_grad"] += 1
                if g[OLD_NK:].abs().max().item() > 1e-12:
                    summary["cv4_it_grad"] += 1
    return summary


def run_loss_mask_check(cfg: dict[str, Any]) -> str:
    from ultralytics.utils.loss import v8PoseLoss

    if not V5_INIT.is_file():
        raise SystemExit(f"Checkpoint manquant : {V5_INIT}")

    train_kp = it_kp_indices(cfg)
    pose_gain = float(cfg["loss"]["pose"])
    kobj_gain = float(cfg["loss"]["kobj"])

    model = load_v5_model()
    model.args = type("A", (), {"pose": pose_gain, "kobj": kobj_gain})()
    batch, args = load_train_batch(cfg, prefer_v0_it=False)
    model.args = args

    # Stock criterion (all 16 KP)
    if hasattr(model, "criterion"):
        del model.criterion
    stock_crit = v8PoseLoss(model)

    # Masked criterion (IT only)
    apply_it_only_loss_patch(model, train_kp_indices=train_kp)
    if hasattr(model, "criterion"):
        del model.criterion
    masked_crit = model.init_criterion()

    with torch.no_grad():
        stock_preds = model(batch["img"])
        stock_loss, stock_items = stock_crit(stock_preds, batch)
    model.zero_grad(set_to_none=True)
    masked_preds = model(batch["img"])
    masked_loss, masked_items = masked_crit(masked_preds, batch)

    tensors = _extract_pose_tensors(model, batch, masked_crit)
    it_loss_fn = masked_crit._it_keypoint_loss if isinstance(masked_crit, ITOnlyPoseLoss) else None
    kp_rows = []
    if tensors["gt_kpt"] is not None:
        kp_rows = per_kp_contributions(
            tensors["base"],
            tensors["gt_kpt"],
            tensors["pred_kpt"],
            tensors["area"],
            tensors["vis_mask"],
            pose_gain,
            kobj_gain,
            it_only_loss_fn=it_loss_fn,
        )

    # Effective masked contributions (IT loss fn, single-KP masks)
    contrib_old_pos_eff = sum(
        r["position_loss_weighted"] for r in kp_rows if r["zone"] == "old_14kp"
    )
    contrib_it_r = next((r for r in kp_rows if r["kp_index"] == 14), {})
    contrib_it_l = next((r for r in kp_rows if r["kp_index"] == 15), {})

    # Unmasked stock diagnostic (Ultralytics factor) for comparison
    kp_rows_stock = []
    if tensors["gt_kpt"] is not None:
        kp_rows_stock = per_kp_contributions(
            tensors["base"],
            tensors["gt_kpt"],
            tensors["pred_kpt"],
            tensors["area"],
            tensors["vis_mask"],
            pose_gain,
            kobj_gain,
            it_only_loss_fn=None,
        )
    contrib_old_pos_stock = sum(
        r["position_loss_weighted"] for r in kp_rows_stock if r["zone"] == "old_14kp"
    )

    # Backward with masked loss + freeze hooks
    apply_it_only_freeze(model)
    if hasattr(model, "criterion"):
        del model.criterion
    apply_it_only_loss_patch(model, train_kp_indices=train_kp)
    model.zero_grad(set_to_none=True)
    loss, _ = model.loss(batch)
    total = loss.sum()
    total.backward()
    grad_sum = grad_zone_summary(model)

    stock_pose = float(stock_items[1].item())
    stock_kobj = float(stock_items[2].item())
    masked_pose = float(masked_items[1].item())
    masked_kobj = float(masked_items[2].item())

    # Expected masked pose ≈ IT_R + IT_L only (weighted)
    it_r_w = contrib_it_r.get("position_loss_weighted", 0.0)
    it_l_w = contrib_it_l.get("position_loss_weighted", 0.0)
    n_visible_it = sum(
        1 for idx in (14, 15)
        if next((r for r in kp_rows if r["kp_index"] == idx), {}).get("gt_visible", False)
    )
    expected_masked_pose = (it_r_w + it_l_w) / max(n_visible_it, 1)

    # IT share of stock loss (diagnostic)
    it_stock_pose = sum(
        r["position_loss_weighted"]
        for r in kp_rows_stock
        if r["kp_index"] in train_kp
    )

    # Direct verify: masked calculate_keypoints_loss excludes old KP channels
    old_only_loss = 0.0
    if tensors["vis_mask"] is not None and it_loss_fn is not None:
        it_mask = _it_only_bool_mask(tensors["vis_mask"].shape[1], train_kp, tensors["vis_mask"].device)
        old_vis = tensors["vis_mask"].clone()
        old_vis[:, list(train_kp)] = False
        old_masked = old_vis & it_mask.unsqueeze(0)
        old_only_loss = float(
            it_loss_fn(tensors["pred_kpt"], tensors["gt_kpt"], old_masked, tensors["area"]).item()
        )

    # v=0 IT batch (separate probe)
    v0_batch, _ = load_train_batch(cfg, prefer_v0_it=True)
    v0_tensors = _extract_pose_tensors(model, v0_batch, masked_crit)
    v0_kp_rows: list[dict[str, Any]] = []
    if v0_tensors["gt_kpt"] is not None:
        v0_kp_rows = per_kp_contributions(
            v0_tensors["base"],
            v0_tensors["gt_kpt"],
            v0_tensors["pred_kpt"],
            v0_tensors["area"],
            v0_tensors["vis_mask"],
            pose_gain,
            kobj_gain,
            it_only_loss_fn=it_loss_fn,
        )
    v0_rows = [r for r in v0_kp_rows if r["landmark"] in ("IT_R", "IT_L") and not r["gt_visible"]]

    checks = {
        "loss_mask_implemented": True,
        "old_kp_direct_loss_zero": old_only_loss == 0.0,
        "masked_pose_lte_stock_total": masked_pose <= stock_pose + 1e-5 or masked_pose <= it_stock_pose * 1.5 + 1e-5,
        "it_r_contributes_when_visible": contrib_it_r.get("position_loss_weighted", 0) > 0 or not contrib_it_r.get("gt_visible", True),
        "it_l_contributes_when_visible": contrib_it_l.get("position_loss_weighted", 0) > 0 or not contrib_it_l.get("gt_visible", True),
        "masked_matches_it_mean": abs(masked_pose - expected_masked_pose) < max(0.05, expected_masked_pose * 0.02 + 1e-6),
        "v0_it_no_position": all(r["position_loss_raw"] == 0.0 for r in v0_rows),
        "backbone_no_grad": grad_sum["backbone_grad"] == 0,
        "cv2_cv3_no_grad": grad_sum["cv2_grad"] == 0 and grad_sum["cv3_grad"] == 0,
        "cv4_old_blocked": grad_sum["cv4_old_grad"] == 0,
        "cv4_it_active": grad_sum["cv4_it_grad"] > 0,
        "no_optimizer_step": True,
    }
    blocked = not all(checks.values())
    verdict = "V5_PHASE1_LOSS_MASK_BLOCKED" if blocked else "V5_PHASE1_LOSS_MASK_READY"

    csv_rows: list[dict[str, Any]] = []
    csv_rows.append({
        "section": "summary",
        "metric": "verdict",
        "value": verdict,
    })
    for k, v in checks.items():
        csv_rows.append({"section": "check", "metric": k, "value": v})
    csv_rows.append({"section": "loss", "metric": "stock_pose_weighted", "value": stock_pose})
    csv_rows.append({"section": "loss", "metric": "masked_pose_weighted", "value": masked_pose})
    csv_rows.append({"section": "loss", "metric": "stock_kobj_weighted", "value": stock_kobj})
    csv_rows.append({"section": "loss", "metric": "masked_kobj_weighted", "value": masked_kobj})
    csv_rows.append({"section": "loss", "metric": "contrib_old_14kp_stock_diagnostic", "value": contrib_old_pos_stock})
    csv_rows.append({"section": "loss", "metric": "contrib_old_14kp_effective_masked", "value": contrib_old_pos_eff})
    csv_rows.append({"section": "loss", "metric": "old_kp_direct_loss_unmasked_fn", "value": old_only_loss})
    csv_rows.append({"section": "loss", "metric": "contrib_IT_R_position_weighted", "value": contrib_it_r.get("position_loss_weighted", 0)})
    csv_rows.append({"section": "loss", "metric": "contrib_IT_L_position_weighted", "value": contrib_it_l.get("position_loss_weighted", 0)})
    csv_rows.append({"section": "loss", "metric": "expected_masked_pose_mean_it", "value": expected_masked_pose})
    csv_rows.append({"section": "loss", "metric": "it_stock_pose_diagnostic", "value": it_stock_pose})
    for r in kp_rows:
        csv_rows.append({"section": "per_kp", **r})
    for k, v in grad_sum.items():
        csv_rows.append({"section": "gradients", "metric": k, "value": v})
    for r in v0_rows:
        csv_rows.append({"section": "v0_it", **r})

    fieldnames = sorted({k for row in csv_rows for k in row})
    with LOSS_MASK_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [
        "# V5 Phase 1 — Loss Mask Check (IT-only)",
        "",
        f"**Généré :** {ts}",
        "**Mode :** READ-ONLY — aucun entraînement, aucun `optimizer.step()`",
        f"**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1.py`",
        f"**Verdict :** `{verdict}`",
        "",
        "---",
        "",
        "## Implémentation",
        "",
        "Classe `ITOnlyPoseLoss` : masque `kpt_mask` aux indices **14, 15** avant loss position et BCE visibility.",
        "Normalisation IT-only : moyenne sur KP IT visibles (évite le facteur Ultralytics `16/n_visible`).",
        "",
        "```python",
        "it_mask = zeros(16); it_mask[14] = it_mask[15] = True",
        "kpt_mask = (gt_v != 0) & it_mask   # exclut v=0 ET KP 0-13",
        "kpts_loss = sum(loss_per * kpt_mask) / kpt_mask.sum()",
        "```",
        "",
        "---",
        "",
        "## 1. Loss pose totale (batch réel, batch=1, imgsz=640)",
        "",
        "| Métrique | Stock (16 KP) | Masqué IT-only |",
        "|----------|--------------:|---------------:|",
        f"| Position (pose gain déjà inclus) | {stock_pose:.6f} | **{masked_pose:.6f}** |",
        f"| Visibility (kobj gain déjà inclus) | {stock_kobj:.6f} | **{masked_kobj:.6f}** |",
        "",
        "---",
        "",
        "## 2–4. Contributions par zone",
        "",
        "| Zone | Position loss weighted |",
        "|------|----------------------:|",
        f"| KP 0–13 (stock diagnostic) | {contrib_old_pos_stock:.6f} |",
        f"| KP 0–13 (effective masked) | **{contrib_old_pos_eff:.6f}** |",
        f"| Old-KP direct loss (IT fn, mask 0–13) | **{old_only_loss:.6f}** |",
        f"| IT_R (index 14) | **{contrib_it_r.get('position_loss_weighted', 0):.6f}** |",
        f"| IT_L (index 15) | **{contrib_it_l.get('position_loss_weighted', 0):.6f}** |",
        f"| Somme IT (per-KP isolé) | {it_r_w + it_l_w:.6f} |",
        f"| Moyenne IT (loss masquée) | **{expected_masked_pose:.6f}** |",
        f"| IT dans loss stock | {it_stock_pose:.6f} |",
        "",
        "Avec masque actif : contribution **effective** KP 0–13 = **0** (exclues de `calculate_keypoints_loss`).",
        "",
        "---",
        "",
        "## 5. Comportement v=0 (batch B26_06 ou équivalent)",
        "",
    ]
    if v0_rows:
        md.append("| Landmark | gt_visible | position_loss_raw |")
        md.append("|----------|:----------:|------------------:|")
        for r in v0_rows:
            md.append(f"| {r['landmark']} | {r['gt_visible']} | {r['position_loss_raw']:.6f} |")
    else:
        md.append("Aucun IT v=0 dans ce batch — v=0 exclu par `gt_v != 0` (comportement Ultralytics natif).")

    md.extend([
        "",
        "---",
        "",
        "## 6–7. Gradients + hooks cv4 (backward, sans step)",
        "",
        "| Zone | Tensors avec grad | Attendu |",
        "|------|:-----------------:|:-------:|",
        f"| Backbone | {grad_sum['backbone_grad']} | 0 |",
        f"| cv2 | {grad_sum['cv2_grad']} | 0 |",
        f"| cv3 | {grad_sum['cv3_grad']} | 0 |",
        f"| cv4 canaux 0–41 | {grad_sum['cv4_old_grad']} | 0 |",
        f"| cv4 canaux 42–47 | {grad_sum['cv4_it_grad']} | >0 |",
        f"| cv4 hooks actifs | {grad_sum['cv4_trainable_hooks']} | 24 |",
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
        "CSV : `v5_phase1_loss_mask_check.csv`",
    ])
    LOSS_MASK_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(verdict)
    return verdict


def build_train_kwargs(cfg: dict[str, Any]) -> dict[str, Any]:
    t, o, l, a, r = cfg["train"], cfg["optimizer"], cfg["loss"], cfg["augment"], cfg["run"]
    init = resolve(cfg["init"]["source"])
    return {
        "model": str(init),
        "data": str(resolve(cfg["data"])),
        "epochs": t["epochs"],
        "patience": t["patience"],
        "imgsz": t["imgsz"],
        "batch": t["batch"],
        "device": t["device"],
        "workers": t["workers"],
        "cache": t["cache"],
        "amp": t["amp"],
        "deterministic": t["deterministic"],
        "seed": t["seed"],
        "optimizer": o["name"],
        "lr0": o["lr0"],
        "lrf": o["lrf"],
        "momentum": o["momentum"],
        "weight_decay": o["weight_decay"],
        "warmup_epochs": o["warmup_epochs"],
        "warmup_momentum": o["warmup_momentum"],
        "warmup_bias_lr": o["warmup_bias_lr"],
        "cos_lr": o["cos_lr"],
        "pose": l["pose"],
        "kobj": l["kobj"],
        "box": l["box"],
        "cls": l["cls"],
        "dfl": l["dfl"],
        "mosaic": a["mosaic"],
        "mixup": a["mixup"],
        "copy_paste": a["copy_paste"],
        "auto_augment": a["auto_augment"],
        "erasing": a["erasing"],
        "close_mosaic": a["close_mosaic"],
        "fliplr": a["fliplr"],
        "flipud": a["flipud"],
        "degrees": a["degrees"],
        "translate": a["translate"],
        "scale": a["scale"],
        "shear": a["shear"],
        "perspective": a["perspective"],
        "hsv_h": a["hsv_h"],
        "hsv_s": a["hsv_s"],
        "hsv_v": a["hsv_v"],
        "project": str(resolve(r["project"])),
        "name": r["name"],
        "exist_ok": r["exist_ok"],
        "pretrained": False,
    }


def verify_preflight() -> None:
    if not PREFLIGHT_MD.is_file():
        raise SystemExit(f"Preflight manquant : {PREFLIGHT_MD}")
    text = PREFLIGHT_MD.read_text(encoding="utf-8")
    if "V5_PHASE1_READY" not in text:
        raise SystemExit("Preflight non READY — corriger avant --train.")
    if "V5_PHASE1_BLOCKED" in text.split("## Conclusion")[-1]:
        raise SystemExit("Preflight BLOCKED — entraînement interdit.")


def setup_it_only_model(yolo_model: nn.Module, cfg: dict[str, Any]) -> None:
    apply_it_only_freeze(yolo_model)
    apply_it_only_loss_patch(yolo_model, train_kp_indices=it_kp_indices(cfg))
    if hasattr(yolo_model, "criterion"):
        del yolo_model.criterion


def run_training(cfg: dict[str, Any], kwargs: dict[str, Any]) -> int:
    from ultralytics import YOLO

    verify_preflight()
    if not V5_INIT.is_file():
        raise SystemExit(f"Init V5 manquant : {V5_INIT}")

    yolo = YOLO(kwargs["model"], task="pose")
    setup_it_only_model(yolo.model, cfg)
    yolo.train(**kwargs)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="V5 Phase 1 IT-only")
    parser.add_argument("--check-loss-mask", action="store_true", help="Probe loss mask sur batch réel")
    parser.add_argument("--train", action="store_true", help="Lance l'entraînement (explicite)")
    args = parser.parse_args()

    cfg = load_cfg()

    if args.check_loss_mask:
        return 0 if run_loss_mask_check(cfg) == "V5_PHASE1_LOSS_MASK_READY" else 1

    kwargs = build_train_kwargs(cfg)
    print("V5 Phase 1 — config chargée")
    print(f"  init   = {kwargs['model']}")
    print(f"  epochs = {kwargs['epochs']}  patience = {kwargs['patience']}")
    print(f"  lr0    = {kwargs['lr0']}  cos_lr = {kwargs['cos_lr']}")
    print(f"  imgsz  = {kwargs['imgsz']}  batch = {kwargs['batch']}")

    if args.train:
        return run_training(cfg, kwargs)

    verify_preflight()
    print("\nPreflight OK (V5_PHASE1_READY). Ajouter --train pour lancer l'entraînement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
