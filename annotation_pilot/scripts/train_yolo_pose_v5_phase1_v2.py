#!/usr/bin/env python3
"""V5 Phase 1 v2 — IT-only fine-tuning with trainer-integrated freeze/loss.

Corrects the v1 pipeline: freeze, gradient hooks, and ITOnlyPoseLoss are applied
inside a custom PoseTrainer AFTER Ultralytics _setup_train() resets requires_grad.

Default: preflight gate (NO training).
``--train`` : lance l'entraînement via V5Phase1PoseTrainer (explicite).

Ne modifie jamais V2, V4, labels, dataset, ni v5_surgical_init.pt.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import shutil
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import yaml

PROJECT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_training_config.yaml"
PREFLIGHT_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_v2_preflight.md"
PREFLIGHT_CSV = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_v2_preflight.csv"
V5_INIT = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt"
INITIAL_LR_FIX_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_v2_initial_lr_fix.md"
INITIAL_LR_FIX_CSV = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_v2_initial_lr_fix.csv"
V5_WORK = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_phase1_v2_work.pt"

OLD_NK = 42
DEFAULT_IT_KP = (14, 15)

# Reuse v1 probe utilities without modifying v1.
_V1_PATH = Path(__file__).resolve().parent / "train_yolo_pose_v5_phase1.py"
_spec = importlib.util.spec_from_file_location("v5_phase1_v1", _V1_PATH)
_v1 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_v1)

ITOnlyPoseLoss = _v1.ITOnlyPoseLoss
apply_it_only_freeze = _v1.apply_it_only_freeze
grad_zone_summary = _v1.grad_zone_summary
load_train_batch = _v1.load_train_batch
per_kp_contributions = _v1.per_kp_contributions
_extract_pose_tensors = _v1._extract_pose_tensors
_it_only_bool_mask = _v1._it_only_bool_mask
LANDMARKS_16 = _v1.LANDMARKS_16
build_train_kwargs = _v1.build_train_kwargs
resolve = _v1.resolve
it_kp_indices = _v1.it_kp_indices
load_cfg = _v1.load_cfg


class Phase1ITOnlyPoseLoss(ITOnlyPoseLoss):
    """IT-only pose loss with box/cls/dfl zeroed for Phase 1."""

    _DET_LOSS_IDX = (0, 3, 4)  # box, cls, dfl

    def __call__(
        self,
        preds: dict[str, torch.Tensor] | tuple[torch.Tensor, dict[str, torch.Tensor]],
        batch: dict[str, torch.Tensor],
    ) -> tuple[torch.Tensor, torch.Tensor]:
        return self.loss(self._base.parse_output(preds), batch)

    def loss(
        self, preds: dict[str, torch.Tensor], batch: dict[str, torch.Tensor]
    ) -> tuple[torch.Tensor, torch.Tensor]:
        loss_vec, loss_detach = self._base.loss(preds, batch)
        loss_vec = loss_vec.clone()
        loss_detach = loss_detach.clone()
        for idx in self._DET_LOSS_IDX:
            loss_vec[idx] = 0.0
            loss_detach[idx] = 0.0
        return loss_vec, loss_detach


def apply_phase1_loss_patch(model: nn.Module, train_kp_indices: tuple[int, ...] = DEFAULT_IT_KP) -> None:
    """Replace model criterion init with Phase1 IT-only loss."""

    def patched_init_criterion():
        crit = Phase1ITOnlyPoseLoss(model, train_kp_indices=train_kp_indices)
        base = crit._base

        def masked_calc(*args: Any, **kwargs: Any) -> tuple[torch.Tensor, torch.Tensor]:
            return crit.calculate_keypoints_loss(*args, **kwargs)

        base.calculate_keypoints_loss = masked_calc  # type: ignore[method-assign]
        return crit

    model.init_criterion = patched_init_criterion  # type: ignore[method-assign]
    if hasattr(model, "criterion"):
        del model.criterion


def setup_phase1_model(model: nn.Module, cfg: dict[str, Any]) -> list[str]:
    """Apply freeze + loss patch on the live trainer model."""
    trainable = apply_it_only_freeze(model)
    apply_phase1_loss_patch(model, train_kp_indices=it_kp_indices(cfg))
    if hasattr(model, "criterion"):
        del model.criterion
    return trainable


def _trainable_param_keys(model: nn.Module) -> set[str]:
    from ultralytics.utils.torch_utils import unwrap_model

    return {n for n, p in unwrap_model(model).named_parameters() if p.requires_grad}


def rebuild_optimizer_trainable_only(trainer: Any) -> int:
    """Rebuild optimizer with only IT trainable parameters (post-freeze).

    Ultralytics _do_train() warmup reads param_group['initial_lr'], set by
    LambdaLR in _setup_scheduler(). Rebuilding the optimizer must therefore
    recreate param groups like build_optimizer() and call _setup_scheduler().
    """
    from torch import optim
    from ultralytics.utils.torch_utils import unwrap_model

    model = unwrap_model(trainer.model)
    trainable_count = sum(1 for p in model.parameters() if p.requires_grad)
    if trainable_count == 0:
        raise RuntimeError("No trainable parameters after Phase 1 freeze.")

    g: list[dict[str, nn.Parameter]] = [{}, {}, {}]
    bn = tuple(v for k, v in nn.__dict__.items() if "Norm" in k)
    for module_name, module in model.named_modules():
        for param_name, param in module.named_parameters(recurse=False):
            if not param.requires_grad:
                continue
            fullname = f"{module_name}.{param_name}" if module_name else param_name
            if "bias" in fullname:
                g[2][fullname] = param
            elif isinstance(module, bn) or "logit_scale" in fullname:
                g[1][fullname] = param
            else:
                g[0][fullname] = param

    lr = trainer.args.lr0
    momentum = trainer.args.momentum
    decay = trainer.args.weight_decay * trainer.batch_size * trainer.accumulate / trainer.args.nbs
    name = {x.lower(): x for x in ("Adam", "Adamax", "AdamW", "NAdam", "RAdam", "RMSProp", "SGD")}.get(
        str(trainer.args.optimizer).lower(), str(trainer.args.optimizer)
    )

    if name in {"Adam", "Adamax", "AdamW", "NAdam", "RAdam"}:
        optim_args = dict(lr=lr, betas=(momentum, 0.999), weight_decay=0.0)
    elif name == "RMSProp":
        optim_args = dict(lr=lr, momentum=momentum)
    elif name == "SGD":
        optim_args = dict(lr=lr, momentum=momentum, nesterov=True)
    else:
        raise NotImplementedError(f"Optimizer '{name}' not supported for Phase 1 IT-only rebuild.")

    param_groups: list[dict[str, Any]] = [
        {"params": list(g[0].values()), **optim_args, "weight_decay": decay, "param_group": "weight"},
        {"params": list(g[1].values()), **optim_args, "weight_decay": 0.0, "param_group": "bn"},
        {"params": list(g[2].values()), **optim_args, "param_group": "bias"},
    ]
    param_groups = [pg for pg in param_groups if pg["params"]]

    trainer.optimizer = getattr(optim, name)(params=param_groups)
    trainer._setup_scheduler()
    return trainable_count


def optimizer_param_group_summary(trainer: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, pg in enumerate(trainer.optimizer.param_groups):
        rows.append({
            "group_index": i,
            "param_group": pg.get("param_group"),
            "n_params": len(pg["params"]),
            "lr": float(pg["lr"]),
            "initial_lr": float(pg["initial_lr"]) if "initial_lr" in pg else None,
            "has_initial_lr": "initial_lr" in pg,
            "weight_decay": float(pg.get("weight_decay", 0.0)),
        })
    return rows


def simulate_warmup_lr_access(trainer: Any) -> dict[str, Any]:
    """Exercise the _do_train warmup LR path without forward/backward/step."""
    nb = len(trainer.train_loader)
    nw = max(round(trainer.args.warmup_epochs * nb), 100) if trainer.args.warmup_epochs > 0 else -1
    epoch = trainer.start_epoch
    ni = 0
    warmup_lrs: list[float] = []
    if trainer.args.warmup_epochs > 0 and ni <= nw:
        xi = [0, nw]
        import numpy as np

        for x in trainer.optimizer.param_groups:
            warmup_lrs.append(
                float(
                    np.interp(
                        ni,
                        xi,
                        [
                            trainer.args.warmup_bias_lr if x.get("param_group") == "bias" else 0.0,
                            x["initial_lr"] * trainer.lf(epoch),
                        ],
                    )
                )
            )
    return {"nb": nb, "nw": nw, "warmup_lrs": warmup_lrs, "warmup_ok": True}


def restrict_ema_to_trainable(trainer: Any) -> str:
    """Restrict EMA updates to IT trainable parameters only.

    Justification: disabling EMA would break Ultralytics checkpoint semantics (best.pt
    uses EMA weights). Restricting updates prevents frozen zones from drifting in the
    EMA shadow model while preserving EMA smoothing for IT channels.
    """
    from ultralytics.utils.torch_utils import unwrap_model

    ema_obj = trainer.ema
    if ema_obj is None:
        return "ema_none"

    model = unwrap_model(trainer.model)
    trainable = _trainable_param_keys(model)
    frozen_snap: dict[str, torch.Tensor] = {}
    for k, v in ema_obj.ema.state_dict().items():
        if v.dtype.is_floating_point and k not in trainable:
            frozen_snap[k] = v.detach().clone()

    def restricted_update(model_in: nn.Module) -> None:
        if not ema_obj.enabled:
            return
        ema_obj.updates += 1
        d = ema_obj.decay(ema_obj.updates)
        msd = unwrap_model(model_in).state_dict()
        for k, v in ema_obj.ema.state_dict().items():
            if not v.dtype.is_floating_point:
                continue
            if k in frozen_snap:
                v.copy_(frozen_snap[k])
                continue
            if k not in trainable or k not in msd:
                continue
            v.mul_(d).add_(msd[k].detach(), alpha=1 - d)

    ema_obj.update = restricted_update  # type: ignore[method-assign]
    return "ema_restricted_trainable"


def freeze_state_summary(model: nn.Module) -> dict[str, Any]:
    from ultralytics.utils.torch_utils import unwrap_model

    m = unwrap_model(model)
    summary: dict[str, Any] = {
        "backbone_trainable": 0,
        "cv2_trainable": 0,
        "cv3_trainable": 0,
        "dfl_trainable": 0,
        "cv4_hook_params": 0,
        "total_trainable": 0,
        "total_frozen": 0,
        "gradient_hooks": 0,
    }
    for name, param in m.named_parameters():
        if param.requires_grad:
            summary["total_trainable"] += 1
            if "dfl" in name:
                summary["dfl_trainable"] += 1
            elif "cv4" in name:
                summary["cv4_hook_params"] += 1
            elif "cv2" in name:
                summary["cv2_trainable"] += 1
            elif "cv3" in name:
                summary["cv3_trainable"] += 1
            elif name.startswith("model.") and name.split(".")[1].isdigit():
                layer = int(name.split(".")[1])
                if layer <= 22:
                    summary["backbone_trainable"] += 1
        else:
            summary["total_frozen"] += 1
        if getattr(param, "_backward_hooks", None):
            summary["gradient_hooks"] += len(param._backward_hooks)
    return summary


def grad_zone_summary_v2(model: nn.Module) -> dict[str, Any]:
    summary = grad_zone_summary(model)
    from ultralytics.utils.torch_utils import unwrap_model

    summary["dfl_grad"] = 0
    for name, param in unwrap_model(model).named_parameters():
        if "dfl" not in name:
            continue
        g = param.grad
        if g is not None and g.abs().max().item() > 1e-12:
            summary["dfl_grad"] += 1
    return summary


def param_zone(name: str) -> str:
    if "dfl" in name:
        return "dfl"
    if "cv4" in name:
        return "cv4_pose"
    if "cv2" in name:
        return "cv2_box"
    if "cv3" in name:
        return "cv3_cls"
    if name.startswith("model.") and name.split(".")[1].isdigit():
        if int(name.split(".")[1]) <= 22:
            return "backbone"
    return "other"


def compare_param_deltas(
    before: dict[str, torch.Tensor], after: dict[str, torch.Tensor], old_nk: int = OLD_NK
) -> dict[str, Any]:
    """Compare named_parameters only (excludes BN running buffers updated in train mode)."""
    zones: dict[str, dict[str, Any]] = {}
    cv4_old_changed = 0
    cv4_it_changed = 0
    for key in before:
        if key not in after:
            continue
        b, a = before[key], after[key]
        if not (torch.is_floating_point(b) and torch.is_floating_point(a)):
            continue
        diff = (a - b).abs()
        max_diff = float(diff.max().item()) if diff.numel() else 0.0
        changed = max_diff > 1e-12
        zone = param_zone(key)
        z = zones.setdefault(zone, {"changed": 0, "total": 0, "max_diff": 0.0})
        z["total"] += 1
        z["max_diff"] = max(z["max_diff"], max_diff)
        if changed:
            z["changed"] += 1
        if zone == "cv4_pose" and changed:
            if b.dim() == 4 and b.shape[0] > old_nk and b.shape[1] > old_nk:
                if diff[:old_nk, :old_nk].max().item() > 1e-12:
                    cv4_old_changed += 1
                if diff[old_nk:, old_nk:].max().item() > 1e-12:
                    cv4_it_changed += 1
            elif b.dim() == 1 and b.shape[0] > old_nk:
                if diff[:old_nk].max().item() > 1e-12:
                    cv4_old_changed += 1
                if diff[old_nk:].max().item() > 1e-12:
                    cv4_it_changed += 1
            elif b.dim() == 4 and b.shape[0] > old_nk:
                if diff[:old_nk].max().item() > 1e-12:
                    cv4_old_changed += 1
                if diff[old_nk:].max().item() > 1e-12:
                    cv4_it_changed += 1
    return {"zones": zones, "cv4_old_changed": cv4_old_changed, "cv4_it_changed": cv4_it_changed}


def make_work_checkpoint() -> Path:
    V5_WORK.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(V5_INIT, V5_WORK)
    return V5_WORK


class V5Phase1PoseTrainer:
    """Factory wrapper — actual class built lazily to avoid import cost in probes."""

    @staticmethod
    def create(cfg: dict[str, Any], overrides: dict[str, Any]):
        from ultralytics.models.yolo.pose import PoseTrainer
        from ultralytics.utils import DEFAULT_CFG
        from ultralytics.utils.torch_utils import unwrap_model

        it_cfg = cfg

        class _Trainer(PoseTrainer):
            def __init__(self, cfg=DEFAULT_CFG, overrides=None, _callbacks=None):
                self._v5_it_cfg = it_cfg
                super().__init__(cfg, overrides, _callbacks)

            def _setup_train(self):
                super()._setup_train()
                model = unwrap_model(self.model)
                trainable = setup_phase1_model(model, self._v5_it_cfg)
                self._v5_trainable_names = trainable
                self._v5_n_opt_params = rebuild_optimizer_trainable_only(self)
                self._v5_ema_mode = restrict_ema_to_trainable(self)
                if hasattr(model, "criterion"):
                    del model.criterion

            def get_model(self, cfg=None, weights=None, verbose=True):
                model = super().get_model(cfg=cfg, weights=weights, verbose=verbose)
                return model

        return _Trainer


def build_preflight_trainer_kwargs(cfg: dict[str, Any], init_path: Path) -> dict[str, Any]:
    kwargs = build_train_kwargs(cfg)
    kwargs.update({
        "model": str(init_path),
        "epochs": 1,
        "patience": 1,
        "plots": False,
        "val": False,
        "save": False,
        "exist_ok": True,
        "name": "yolo_pose_new_26_v5_phase1_v2_preflight",
        "pretrained": False,
        "verbose": False,
    })
    return kwargs


def run_trainer_gradient_probe(trainer: Any, cfg: dict[str, Any]) -> dict[str, Any]:
    from ultralytics.utils.torch_utils import unwrap_model

    model = unwrap_model(trainer.model)
    batch, _ = load_train_batch(cfg, prefer_v0_it=False)
    batch = trainer.preprocess_batch(batch)

    freeze_after = freeze_state_summary(model)
    crit = model.init_criterion()
    assert isinstance(crit, Phase1ITOnlyPoseLoss), type(crit)

    with torch.no_grad():
        stock_items = None
    model.zero_grad(set_to_none=True)
    loss, loss_items = model(batch)
    total = loss.sum()
    total.backward()
    grad_sum = grad_zone_summary_v2(model)

    pose_gain = float(cfg["loss"]["pose"])
    kobj_gain = float(cfg["loss"]["kobj"])
    tensors = _extract_pose_tensors(model, batch, crit)
    kp_rows: list[dict[str, Any]] = []
    if tensors["gt_kpt"] is not None:
        kp_rows = per_kp_contributions(
            tensors["base"],
            tensors["gt_kpt"],
            tensors["pred_kpt"],
            tensors["area"],
            tensors["vis_mask"],
            pose_gain,
            kobj_gain,
            it_only_loss_fn=crit._it_keypoint_loss,
        )

    v0_batch, _ = load_train_batch(cfg, prefer_v0_it=True)
    v0_batch = trainer.preprocess_batch(v0_batch)
    v0_tensors = _extract_pose_tensors(model, v0_batch, crit)
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
            it_only_loss_fn=crit._it_keypoint_loss,
        )
    v0_rows = [r for r in v0_kp_rows if r["landmark"] in ("IT_R", "IT_L") and not r["gt_visible"]]

    box_l, pose_l, kobj_l, cls_l, dfl_l = [float(x.item()) for x in loss_items]
    old_pos = sum(r["position_loss_weighted"] for r in kp_rows if r["zone"] == "old_14kp")
    old_vis = sum(r["visibility_loss_weighted"] for r in kp_rows if r["zone"] == "old_14kp")

    return {
        "freeze_after_setup": freeze_after,
        "criterion_type": type(crit).__name__,
        "loss_items": {"box": box_l, "pose": pose_l, "kobj": kobj_l, "cls": cls_l, "dfl": dfl_l},
        "total_loss": float(total.item()),
        "kp_rows": kp_rows,
        "v0_rows": v0_rows,
        "old_kp_position_weighted": old_pos,
        "old_kp_visibility_weighted": old_vis,
        "grad_sum": grad_sum,
        "ema_mode": getattr(trainer, "_v5_ema_mode", "unknown"),
        "trainable_cv4": getattr(trainer, "_v5_trainable_names", []),
    }


def run_simulated_optimizer_step(trainer: Any, batch: dict[str, Any]) -> dict[str, Any]:
    from ultralytics.utils.torch_utils import unwrap_model

    model = unwrap_model(trainer.model)
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    after: dict[str, torch.Tensor]

    model.zero_grad(set_to_none=True)
    loss, _ = model(batch)
    trainer.scaler.scale(loss.sum()).backward()
    trainer.optimizer_step()

    after = {n: p.detach().clone() for n, p in model.named_parameters()}
    return compare_param_deltas(before, after)


def instantiate_trainer(
    cfg: dict[str, Any],
    init_path: Path,
    kwargs: dict[str, Any] | None = None,
) -> Any:
    if kwargs is None:
        kwargs = build_preflight_trainer_kwargs(cfg, init_path)
    trainer_cls = V5Phase1PoseTrainer.create(cfg, kwargs)
    trainer = trainer_cls(overrides=kwargs)
    trainer._setup_train()
    return trainer


def run_preflight(cfg: dict[str, Any]) -> str:
    if not V5_INIT.is_file():
        raise SystemExit(f"Checkpoint manquant : {V5_INIT}")

    work_ckpt = make_work_checkpoint()

    # --- Phase A: trainer init probe (work copy, no optimizer step on init) ---
    trainer = instantiate_trainer(cfg, work_ckpt)
    probe = run_trainer_gradient_probe(trainer, cfg)
    fs = probe["freeze_after_setup"]
    gs = probe["grad_sum"]
    li = probe["loss_items"]

    checks = {
        "checkpoint_exists": V5_INIT.is_file(),
        "work_checkpoint_separate": work_ckpt.resolve() != V5_INIT.resolve(),
        "trainer_custom_subclass": True,
        "freeze_applied_after_setup": (
            fs["backbone_trainable"] == 0
            and fs["cv2_trainable"] == 0
            and fs["cv3_trainable"] == 0
            and fs["dfl_trainable"] == 0
            and fs["cv4_hook_params"] == 24
        ),
        "gradient_hooks_installed": fs["gradient_hooks"] >= 24,
        "criterion_it_only": probe["criterion_type"] == "Phase1ITOnlyPoseLoss",
        "old_kp_position_zero": probe["old_kp_position_weighted"] == 0.0,
        "old_kp_visibility_zero": probe["old_kp_visibility_weighted"] == 0.0,
        "det_loss_zero_in_total": li["box"] == 0.0 and li["cls"] == 0.0 and li["dfl"] == 0.0,
        "v0_it_no_position": all(r["position_loss_raw"] == 0.0 for r in probe["v0_rows"]),
        "backbone_no_grad": gs["backbone_grad"] == 0,
        "cv2_no_grad": gs["cv2_grad"] == 0,
        "cv3_no_grad": gs["cv3_grad"] == 0,
        "dfl_no_grad": gs["dfl_grad"] == 0,
        "cv4_old_blocked": gs["cv4_old_grad"] == 0,
        "cv4_it_active": gs["cv4_it_grad"] > 0,
        "ema_restricted": probe["ema_mode"] == "ema_restricted_trainable",
        "optimizer_trainable_only": getattr(trainer, "_v5_n_opt_params", 0) == 24,
        "no_optimizer_step_in_probe": True,
    }

    # --- Phase B: simulated optimizer.step on fresh work copy ---
    work_ckpt2 = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_phase1_v2_work_step.pt"
    shutil.copy2(V5_INIT, work_ckpt2)
    trainer_step = instantiate_trainer(cfg, work_ckpt2)
    batch, _ = load_train_batch(cfg, prefer_v0_it=False)
    batch = trainer_step.preprocess_batch(batch)
    step_result = run_simulated_optimizer_step(trainer_step, batch)
    zones = step_result["zones"]

    only_it_changed = (
        zones.get("backbone", {}).get("changed", 0) == 0
        and zones.get("cv2_box", {}).get("changed", 0) == 0
        and zones.get("cv3_cls", {}).get("changed", 0) == 0
        and zones.get("dfl", {}).get("changed", 0) == 0
        and step_result["cv4_old_changed"] == 0
        and step_result["cv4_it_changed"] > 0
    )
    checks["simulated_step_only_it_changes"] = only_it_changed

    blocked = not all(checks.values())
    verdict = "V5_PHASE1_V2_BLOCKED" if blocked else "V5_PHASE1_V2_READY"

    # --- CSV ---
    csv_rows: list[dict[str, Any]] = [
        {"section": "summary", "metric": "verdict", "value": verdict},
    ]
    for k, v in checks.items():
        csv_rows.append({"section": "check", "metric": k, "value": v})
    for k, v in fs.items():
        csv_rows.append({"section": "freeze_after_setup", "metric": k, "value": v})
    for k, v in li.items():
        csv_rows.append({"section": "loss_items_weighted", "metric": k, "value": v})
    csv_rows.append({"section": "loss", "metric": "old_kp_position_weighted", "value": probe["old_kp_position_weighted"]})
    csv_rows.append({"section": "loss", "metric": "old_kp_visibility_weighted", "value": probe["old_kp_visibility_weighted"]})
    csv_rows.append({"section": "loss", "metric": "total_loss", "value": probe["total_loss"]})
    for r in probe["kp_rows"]:
        csv_rows.append({"section": "per_kp", **r})
    for r in probe["v0_rows"]:
        csv_rows.append({"section": "v0_it", **r})
    for k, v in gs.items():
        csv_rows.append({"section": "gradients", "metric": k, "value": v})
    csv_rows.append({"section": "ema", "metric": "mode", "value": probe["ema_mode"]})
    for zone, zd in zones.items():
        csv_rows.append({
            "section": "simulated_step",
            "zone": zone,
            "changed": zd["changed"],
            "total": zd["total"],
            "max_diff": zd["max_diff"],
        })
    csv_rows.append({"section": "simulated_step", "metric": "cv4_old_changed_tensors", "value": step_result["cv4_old_changed"]})
    csv_rows.append({"section": "simulated_step", "metric": "cv4_it_changed_tensors", "value": step_result["cv4_it_changed"]})

    fieldnames = sorted({k for row in csv_rows for k in row})
    with PREFLIGHT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)

    # --- Markdown ---
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [
        "# V5 Phase 1 v2 — Pre-flight IT-only (trainer-integrated)",
        "",
        f"**Généré :** {ts}",
        "**Mode :** PRE-FLIGHT — aucun entraînement complet, `optimizer.step()` simulé sur copie",
        f"**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v2.py`",
        f"**Verdict :** `{verdict}`",
        "",
        "---",
        "",
        "## Correction v2 vs v1",
        "",
        "| Problème v1 | Correction v2 |",
        "|-------------|---------------|",
        "| Gel/hooks appliqués avant `yolo.train()` | `V5Phase1PoseTrainer._setup_train()` ré-applique après Ultralytics |",
        "| `requires_grad` reset par trainer L321-326 | `setup_phase1_model()` post-setup |",
        "| `ITOnlyPoseLoss` perdu | `init_criterion` patché dans le trainer |",
        "| EMA met à jour tous les poids | EMA restreint aux paramètres IT entraînables |",
        "| box/cls/dfl actifs | `Phase1ITOnlyPoseLoss` zero box/cls/dfl |",
        "",
        "---",
        "",
        "## 1. État freeze APRÈS `_setup_train()`",
        "",
        "| Zone | Paramètres trainables | Attendu |",
        "|------|:---------------------:|:-------:|",
        f"| Backbone | {fs['backbone_trainable']} | 0 |",
        f"| cv2 | {fs['cv2_trainable']} | 0 |",
        f"| cv3 | {fs['cv3_trainable']} | 0 |",
        f"| DFL | {fs['dfl_trainable']} | 0 |",
        f"| cv4 (hooks IT) | {fs['cv4_hook_params']} | 24 |",
        f"| Hooks gradient | {fs['gradient_hooks']} | ≥24 |",
        "",
        "---",
        "",
        "## 2. Loss IT-only (batch réel, post-trainer-init)",
        "",
        "| Composante | Weighted loss | Attendu Phase 1 |",
        "|------------|-------------:|:---------------:|",
        f"| box | {li['box']:.6f} | 0 |",
        f"| pose | {li['pose']:.6f} | >0 |",
        f"| kobj | {li['kobj']:.6f} | ≥0 |",
        f"| cls | {li['cls']:.6f} | 0 |",
        f"| dfl | {li['dfl']:.6f} | 0 |",
        "",
        f"KP 0–13 position (effective) : **{probe['old_kp_position_weighted']:.6f}**",
        f"KP 0–13 visibility (effective) : **{probe['old_kp_visibility_weighted']:.6f}**",
        "",
        "---",
        "",
        "## 3. v=0 IT (position loss = 0)",
        "",
    ]
    if probe["v0_rows"]:
        md.append("| Landmark | gt_visible | position_loss_raw |")
        md.append("|----------|:----------:|------------------:|")
        for r in probe["v0_rows"]:
            md.append(f"| {r['landmark']} | {r['gt_visible']} | {r['position_loss_raw']:.6f} |")
    else:
        md.append("Aucun IT v=0 dans le batch v0 — comportement attendu via masque `gt_v != 0`.")

    md.extend([
        "",
        "---",
        "",
        "## 4. Gradients (forward → loss → backward, sans step)",
        "",
        "| Zone | Tensors avec grad | Attendu |",
        "|------|:-----------------:|:-------:|",
        f"| Backbone | {gs['backbone_grad']} | 0 |",
        f"| cv2 | {gs['cv2_grad']} | 0 |",
        f"| cv3 | {gs['cv3_grad']} | 0 |",
        f"| DFL | {gs['dfl_grad']} | 0 |",
        f"| cv4 canaux 0–41 | {gs['cv4_old_grad']} | 0 |",
        f"| cv4 canaux 42–47 | {gs['cv4_it_grad']} | >0 |",
        "",
        "---",
        "",
        "## 5. EMA",
        "",
        f"**Mode :** `{probe['ema_mode']}`",
        "",
        "EMA restreint aux paramètres IT entraînables — les zones gelées conservent leur snapshot",
        "initial dans le modèle EMA (pas de dérive sur backbone/cv2/cv3/cv4-old).",
        "",
        "---",
        "",
        "## 6. Simulated `optimizer.step()` (copie `v5_phase1_v2_work_step.pt`)",
        "",
        "| Zone | Changed / Total | Max abs diff |",
        "|------|:---------------:|-------------:|",
    ])
    for zone, zd in sorted(zones.items()):
        md.append(f"| {zone} | {zd['changed']}/{zd['total']} | {zd['max_diff']:.6e} |")
    md.extend([
        "",
        f"cv4 ancien bloc modifié : **{step_result['cv4_old_changed']}** tensors (attendu 0)",
        f"cv4 IT bloc modifié : **{step_result['cv4_it_changed']}** tensors (attendu >0)",
        "",
        "---",
        "",
        "## 7. Checkpoints",
        "",
        f"| Fichier | Rôle |",
        f"|---------|------|",
        f"| `{V5_INIT.relative_to(PROJECT)}` | Init Phase 0 — **intact** |",
        f"| `{work_ckpt.relative_to(PROJECT)}` | Copie travail preflight |",
        f"| `{work_ckpt2.relative_to(PROJECT)}` | Copie step simulé |",
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
        "CSV : `v5_phase1_v2_preflight.csv`",
        "",
        "Pour entraîner (après READY) :",
        "```",
        ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\train_yolo_pose_v5_phase1_v2.py --train",
        "```",
    ])
    PREFLIGHT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(verdict)
    return verdict


def build_dry_run_trainer_kwargs(cfg: dict[str, Any], init_path: Path, epochs: int = 1) -> dict[str, Any]:
    """Train-like kwargs for dry-run (matches --train --epochs N setup)."""
    kwargs = build_train_kwargs(cfg)
    kwargs.update({
        "model": str(init_path),
        "epochs": epochs,
        "patience": 1,
        "plots": False,
        "val": True,
        "save": False,
        "exist_ok": True,
        "name": "yolo_pose_new_26_v5_phase1_v2_initial_lr_dryrun",
        "pretrained": False,
        "verbose": False,
    })
    return kwargs


def run_initial_lr_dry_run(cfg: dict[str, Any], epochs: int = 1) -> str:
    """Dry-run train setup until just before the first training iteration."""
    if not V5_INIT.is_file():
        raise SystemExit(f"Checkpoint manquant : {V5_INIT}")

    work_ckpt = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_phase1_v2_initial_lr_dryrun.pt"
    work_ckpt.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(V5_INIT, work_ckpt)

    kwargs = build_dry_run_trainer_kwargs(cfg, work_ckpt, epochs=epochs)
    trainer = instantiate_trainer(cfg, work_ckpt, kwargs=kwargs)

    pg_rows = optimizer_param_group_summary(trainer)
    warmup = simulate_warmup_lr_access(trainer)
    probe = run_trainer_gradient_probe(trainer, cfg)
    fs = probe["freeze_after_setup"]
    gs = probe["grad_sum"]
    li = probe["loss_items"]

    checks = {
        "trainer_created": True,
        "setup_train_completed": True,
        "all_param_groups_have_initial_lr": all(r["has_initial_lr"] for r in pg_rows),
        "initial_lr_matches_lr0": all(abs(r["initial_lr"] - float(cfg["optimizer"]["lr0"])) < 1e-15 for r in pg_rows if r["initial_lr"] is not None),
        "warmup_lr_path_ok": warmup["warmup_ok"],
        "optimizer_trainable_param_count": getattr(trainer, "_v5_n_opt_params", 0) == 24,
        "freeze_applied": fs["backbone_trainable"] == 0 and fs["cv4_hook_params"] == 24,
        "cv4_it_grad_active": gs["cv4_it_grad"] > 0,
        "cv4_old_grad_zero": gs["cv4_old_grad"] == 0,
        "backbone_grad_zero": gs["backbone_grad"] == 0,
        "det_loss_zero": li["box"] == 0.0 and li["cls"] == 0.0 and li["dfl"] == 0.0,
        "old_kp_loss_zero": probe["old_kp_position_weighted"] == 0.0 and probe["old_kp_visibility_weighted"] == 0.0,
        "no_optimizer_step": True,
        "no_epoch_started": True,
    }
    blocked = not all(checks.values())
    verdict = "V5_PHASE1_V2_INITIAL_LR_BLOCKED" if blocked else "V5_PHASE1_V2_INITIAL_LR_FIXED"

    csv_rows: list[dict[str, Any]] = [{"section": "summary", "metric": "verdict", "value": verdict}]
    for k, v in checks.items():
        csv_rows.append({"section": "check", "metric": k, "value": v})
    for r in pg_rows:
        csv_rows.append({"section": "optimizer_param_group", **r})
    csv_rows.append({"section": "warmup", "metric": "nb", "value": warmup["nb"]})
    csv_rows.append({"section": "warmup", "metric": "nw", "value": warmup["nw"]})
    for i, lr in enumerate(warmup["warmup_lrs"]):
        csv_rows.append({"section": "warmup", "metric": f"lr_group_{i}", "value": lr})
    for k, v in fs.items():
        csv_rows.append({"section": "freeze", "metric": k, "value": v})
    for k, v in gs.items():
        csv_rows.append({"section": "gradients", "metric": k, "value": v})
    for k, v in li.items():
        csv_rows.append({"section": "loss_items", "metric": k, "value": v})

    fieldnames = sorted({k for row in csv_rows for k in row})
    with INITIAL_LR_FIX_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [
        "# V5 Phase 1 v2 — Fix `initial_lr` (dry-run train setup)",
        "",
        f"**Généré :** {ts}",
        "**Mode :** DRY-RUN — `_setup_train()` + gradient probe, pas d'epoch, pas de `optimizer.step()`",
        f"**Script :** `annotation_pilot/scripts/train_yolo_pose_v5_phase1_v2.py`",
        f"**Verdict :** `{verdict}`",
        "",
        "---",
        "",
        "## Cause",
        "",
        "`rebuild_optimizer_trainable_only()` remplaçait l'optimizer sans recréer le scheduler.",
        "Ultralytics `_do_train()` warmup lit `param_group['initial_lr']`, défini par `LambdaLR`",
        "dans `_setup_scheduler()` — d'où le `KeyError: 'initial_lr'`.",
        "",
        "## Correction",
        "",
        "1. Param groups reconstruits comme `build_optimizer()` (weight / bn / bias, clé `param_group`)",
        "2. Appel `trainer._setup_scheduler()` après rebuild → `initial_lr` injecté par PyTorch `LambdaLR`",
        "",
        "---",
        "",
        "## Optimizer param groups (post `_setup_train`)",
        "",
        "| Index | param_group | n_params | lr | initial_lr | weight_decay |",
        "|------:|:-----------:|---------:|---:|-----------:|-------------:|",
    ]
    for r in pg_rows:
        md.append(
            f"| {r['group_index']} | {r['param_group']} | {r['n_params']} | {r['lr']:.2e} | "
            f"{r['initial_lr']:.2e} | {r['weight_decay']:.2e} |"
        )
    md.extend([
        "",
        "---",
        "",
        "## Warmup LR path (simulation `_do_train`, ni=0)",
        "",
        f"- nb batches : {warmup['nb']}",
        f"- nw warmup iters : {warmup['nw']}",
        f"- LR calculés : {[f'{x:.2e}' for x in warmup['warmup_lrs']]}",
        "",
        "---",
        "",
        "## IT-only / freeze (backward sans step)",
        "",
        f"| IT trainable params | {getattr(trainer, '_v5_n_opt_params', 0)} |",
        f"| cv4 IT grad tensors | {gs['cv4_it_grad']} |",
        f"| cv4 old grad tensors | {gs['cv4_old_grad']} |",
        f"| box / cls / dfl loss | {li['box']:.4f} / {li['cls']:.4f} / {li['dfl']:.4f} |",
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
        "CSV : `v5_phase1_v2_initial_lr_fix.csv`",
    ])
    INITIAL_LR_FIX_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(verdict)
    return verdict


def run_training(cfg: dict[str, Any], kwargs: dict[str, Any]) -> int:
    from ultralytics import YOLO

    if not PREFLIGHT_MD.is_file():
        raise SystemExit(f"Preflight v2 manquant : {PREFLIGHT_MD}")
    text = PREFLIGHT_MD.read_text(encoding="utf-8")
    if "V5_PHASE1_V2_READY" not in text:
        raise SystemExit("Preflight v2 non READY — corriger avant --train.")
    if "V5_PHASE1_V2_BLOCKED" in text.split("## Conclusion")[-1]:
        raise SystemExit("Preflight v2 BLOCKED — entraînement interdit.")

    if not V5_INIT.is_file():
        raise SystemExit(f"Init V5 manquant : {V5_INIT}")

    TrainerCls = V5Phase1PoseTrainer.create(cfg, kwargs)
    yolo = YOLO(kwargs["model"], task="pose")
    yolo.train(trainer=TrainerCls, **kwargs)
    return 0


def main() -> int:
    cfg = load_cfg()
    default_epochs = int(cfg["train"]["epochs"])

    parser = argparse.ArgumentParser(description="V5 Phase 1 v2 IT-only (trainer-integrated)")
    parser.add_argument("--train", action="store_true", help="Lance l'entraînement (explicite)")
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        metavar="N",
        help=f"Nombre maximum d'epochs du run (défaut sans option: {default_epochs}, config)",
    )
    parser.add_argument(
        "--verify-initial-lr",
        action="store_true",
        help="Dry-run train setup (initial_lr fix verification, NO training)",
    )
    args = parser.parse_args()

    if args.epochs is not None and args.epochs < 1:
        parser.error("--epochs must be >= 1")

    if args.verify_initial_lr:
        ep = args.epochs if args.epochs is not None else 1
        return 0 if run_initial_lr_dry_run(cfg, epochs=ep) == "V5_PHASE1_V2_INITIAL_LR_FIXED" else 1

    if args.train:
        kwargs = build_train_kwargs(cfg)
        kwargs["name"] = "yolo_pose_new_26_v5_phase1_it_v2"
        if args.epochs is not None:
            kwargs["epochs"] = args.epochs
        return run_training(cfg, kwargs)

    if args.epochs is not None:
        print(f"Note: --epochs {args.epochs} ignoré sans --train (preflight utilise epochs=1 interne).")

    verdict = run_preflight(cfg)
    return 0 if verdict == "V5_PHASE1_V2_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
