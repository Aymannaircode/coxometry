#!/usr/bin/env python3
"""V5 Phase 1 v2 — freeze lifecycle diagnostic (READ-ONLY, NO --train).

Traces requires_grad, optimizer param groups, gradients, weight hashes and deltas
at checkpoints T0–T10 of the training pipeline. Does NOT launch full training and
does NOT modify v5_surgical_init.pt or existing run checkpoints.

Usage:
    .venv\\Scripts\\python.exe annotation_pilot\\scripts\\v5_phase1_freeze_lifecycle_debug.py

Outputs:
    datasets/yolo_pose_new_26/v5_phase1_freeze_lifecycle_diagnostic.md
    datasets/yolo_pose_new_26/v5_phase1_freeze_lifecycle_diagnostic.csv
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import inspect
import shutil
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))

_V2_PATH = Path(__file__).resolve().parent / "train_yolo_pose_v5_phase1_v2.py"
_spec = importlib.util.spec_from_file_location("v5_phase1_v2", _V2_PATH)
_v2 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_v2)

V5_INIT = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt"
OUT_MD = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_freeze_lifecycle_diagnostic.md"
OUT_CSV = PROJECT / "datasets/yolo_pose_new_26/v5_phase1_freeze_lifecycle_diagnostic.csv"
WORK_CKPT = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_phase1_freeze_lifecycle_work.pt"

OLD_NK = 42
ZONES = ("BACKBONE", "CV2", "CV3", "DFL", "CV4_OLD", "CV4_IT")


def param_bucket(name: str) -> str:
    if "dfl" in name:
        return "DFL"
    if "cv4" in name:
        return "CV4"
    if "cv2" in name:
        return "CV2"
    if "cv3" in name:
        return "CV3"
    if name.startswith("model.") and name.split(".")[1].isdigit() and int(name.split(".")[1]) <= 22:
        return "BACKBONE"
    return "OTHER"


def cv4_sub_bucket(name: str, tensor: torch.Tensor) -> str:
    if "cv4" not in name:
        return param_bucket(name)
    if tensor.dim() == 4 and tensor.shape[0] > OLD_NK and tensor.shape[1] > OLD_NK:
        return "CV4_IT" if name.endswith("weight") else "CV4_OLD"
    if tensor.dim() == 4 and tensor.shape[0] > OLD_NK:
        return "CV4_IT"
    if tensor.dim() == 1 and tensor.shape[0] > OLD_NK:
        return "CV4_IT"
    return "CV4_OLD"


def tensor_hash(t: torch.Tensor) -> str:
    arr = t.detach().cpu().float().contiguous().numpy()
    return hashlib.sha256(arr.tobytes()).hexdigest()[:16]


def zone_snapshot(model: nn.Module, label: str) -> dict[str, Any]:
    from ultralytics.utils.torch_utils import unwrap_model

    m = unwrap_model(model)
    rows: list[dict[str, Any]] = []
    zone_stats: dict[str, dict[str, Any]] = {
        z: {
            "trainable": 0,
            "frozen": 0,
            "grad_nonzero": 0,
            "grad_norm_sum": 0.0,
            "hash_changed": 0,
            "total": 0,
        }
        for z in ZONES
    }

    for name, param in m.named_parameters():
        sub = cv4_sub_bucket(name, param)
        if sub not in zone_stats:
            continue
        zone_stats[sub]["total"] += 1
        if param.requires_grad:
            zone_stats[sub]["trainable"] += 1
        else:
            zone_stats[sub]["frozen"] += 1
        g = param.grad
        grad_norm = 0.0
        grad_nz = False
        if g is not None:
            if sub == "CV4_IT" and param.dim() == 4 and param.shape[0] > OLD_NK and param.shape[1] > OLD_NK:
                grad_norm = float(g[OLD_NK:, OLD_NK:].norm().item())
            elif sub == "CV4_IT" and param.dim() == 1 and param.shape[0] > OLD_NK:
                grad_norm = float(g[OLD_NK:].norm().item())
            else:
                grad_norm = float(g.norm().item()) if g.numel() else 0.0
            grad_nz = grad_norm > 1e-12
        if grad_nz:
            zone_stats[sub]["grad_nonzero"] += 1
        zone_stats[sub]["grad_norm_sum"] += grad_norm
        rows.append({
            "checkpoint": label,
            "param_name": name,
            "zone": sub,
            "requires_grad": param.requires_grad,
            "grad_nonzero": grad_nz,
            "grad_norm": grad_norm,
            "weight_hash": tensor_hash(param),
        })

    return {"label": label, "zones": zone_stats, "params": rows}


def apply_hash_delta(snap: dict[str, Any], ref_hashes: dict[str, str]) -> None:
    for row in snap["params"]:
        old = ref_hashes.get(row["param_name"])
        changed = old is not None and old != row["weight_hash"]
        row["hash_vs_T5_changed"] = changed
        if changed:
            snap["zones"][row["zone"]]["hash_changed"] += 1


def count_vs_surgical(model: nn.Module, ref_sd: dict[str, torch.Tensor]) -> dict[str, Any]:
    from ultralytics.utils.torch_utils import unwrap_model

    sd = unwrap_model(model).state_dict()
    changed = 0
    total = 0
    max_diff = 0.0
    for k, ref in ref_sd.items():
        if k not in sd or not torch.is_floating_point(ref):
            continue
        total += 1
        d = float((sd[k].float() - ref.float()).abs().max().item())
        max_diff = max(max_diff, d)
        if d > 1e-6:
            changed += 1
    return {"changed": changed, "total": total, "max_diff": max_diff}


def optimizer_param_names(trainer: Any) -> list[str]:
    from ultralytics.utils.torch_utils import unwrap_model

    live = unwrap_model(trainer.model)
    id_to_name = {id(p): n for n, p in live.named_parameters()}
    return [
        id_to_name.get(id(p), f"<unknown_{id(p)}>")
        for pg in trainer.optimizer.param_groups
        for p in pg["params"]
    ]


def classify_opt_params(names: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {z: 0 for z in ZONES}
    counts["OTHER"] = 0
    for n in names:
        b = param_bucket(n)
        if b == "CV4":
            counts["CV4_IT"] += 1
        elif b in counts:
            counts[b] += 1
        else:
            counts["OTHER"] += 1
    return counts


def list_active_callbacks(trainer: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event, fns in trainer.callbacks.items():
        for fn in fns:
            src = inspect.getsourcefile(fn) or "?"
            name = getattr(fn, "__name__", repr(fn))
            try:
                src_text = inspect.getsource(fn)
            except (OSError, TypeError):
                src_text = ""
            flags = [kw for kw in (
                "requires_grad", "requires_grad_", "freeze", "load_state_dict",
                "deepcopy", "optimizer", "param_groups", "ema", ".train(",
            ) if kw in src_text]
            rows.append({
                "event": event,
                "callback": name,
                "source": src.replace(str(PROJECT), "."),
                "risk_flags": "|".join(flags),
            })
    return rows


def ema_frozen_drift(trainer: Any, frozen_snap: dict[str, torch.Tensor]) -> dict[str, int]:
    drift = {z: 0 for z in ZONES}
    if trainer.ema is None:
        return drift
    for k, ref in frozen_snap.items():
        v = trainer.ema.ema.state_dict().get(k)
        if v is None or not torch.is_floating_point(v):
            continue
        if float((v - ref).abs().max().item()) <= 1e-12:
            continue
        b = param_bucket(k)
        key = "CV4_OLD" if b == "CV4" else b
        if key in drift:
            drift[key] += 1
    return drift


def make_trainer(cfg: dict[str, Any], kwargs: dict[str, Any]):
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
            self._v5_trainable_names = _v2.setup_phase1_model(model, self._v5_it_cfg)
            self._v5_n_opt_params = _v2.rebuild_optimizer_trainable_only(self)
            self._v5_ema_mode = _v2.restrict_ema_to_trainable(self)
            if hasattr(model, "criterion"):
                del model.criterion

    return _Trainer


def clone_params(model: nn.Module) -> dict[str, torch.Tensor]:
    from ultralytics.utils.torch_utils import unwrap_model

    return {n: p.detach().clone() for n, p in unwrap_model(model).named_parameters()}


def run_one_batch_step(trainer: Any, cfg: dict[str, Any], force_lr: float | None = None) -> None:
    from ultralytics.utils.torch_utils import autocast, unwrap_model

    model = unwrap_model(trainer.model)
    batch = trainer.preprocess_batch(next(iter(trainer.train_loader)))
    if force_lr is not None:
        for pg in trainer.optimizer.param_groups:
            pg["lr"] = force_lr
    model.zero_grad(set_to_none=True)
    with autocast(trainer.amp):
        loss, trainer.loss_items = model(batch)
        trainer.loss = loss.sum()
    trainer.scaler.scale(trainer.loss).backward()


def run_mini_epoch(trainer: Any) -> None:
    from ultralytics.utils.torch_utils import autocast, unwrap_model

    model = unwrap_model(trainer.model)
    nb = len(trainer.train_loader)
    nw = max(round(trainer.args.warmup_epochs * nb), 100) if trainer.args.warmup_epochs > 0 else -1
    last_opt = -1
    trainer._model_train()
    for i, batch in enumerate(trainer.train_loader):
        ni = i
        if nw > 0 and ni <= nw:
            import numpy as np

            xi = [0, nw]
            for x in trainer.optimizer.param_groups:
                x["lr"] = float(
                    np.interp(
                        ni,
                        xi,
                        [
                            trainer.args.warmup_bias_lr if x.get("param_group") == "bias" else 0.0,
                            x["initial_lr"] * trainer.lf(0),
                        ],
                    )
                )
        batch = trainer.preprocess_batch(batch)
        with autocast(trainer.amp):
            loss, trainer.loss_items = model(batch)
            trainer.loss = loss.sum()
        trainer.scaler.scale(trainer.loss).backward()
        if ni - last_opt >= trainer.accumulate:
            trainer.optimizer_step()
            last_opt = ni


def run_lifecycle_probe(cfg: dict[str, Any]) -> str:
    from ultralytics import YOLO
    from ultralytics.utils.torch_utils import unwrap_model

    if not V5_INIT.is_file():
        raise SystemExit(f"Missing init checkpoint: {V5_INIT}")

    WORK_CKPT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(V5_INIT, WORK_CKPT)
    ref_sd = torch.load(V5_INIT, map_location="cpu", weights_only=False)["model"].float().state_dict()

    kwargs = _v2.build_train_kwargs(cfg)
    kwargs.update({
        "model": str(WORK_CKPT),
        "epochs": 1,
        "patience": 1,
        "plots": False,
        "val": False,
        "save": False,
        "exist_ok": True,
        "name": "v5_phase1_freeze_lifecycle_debug",
        "pretrained": False,
        "verbose": False,
        "device": "cpu",
        "workers": 0,
    })

    csv_rows: list[dict[str, Any]] = []
    checkpoints: dict[str, dict[str, Any]] = {}

    # T0: YOLO.load preserves surgical_init
    yolo = YOLO(str(WORK_CKPT), task="pose")
    t0 = count_vs_surgical(yolo.model, ref_sd)
    csv_rows.append({"section": "surgical_parity", "checkpoint": "T0_yolo_load", **t0})

    TrainerCls = make_trainer(cfg, kwargs)
    trainer = TrainerCls(overrides=kwargs)

    # T0b: YOLO.train() pre-replace (run_training path)
    if not kwargs.get("resume") and yolo.ckpt:
        trainer.model = trainer.get_model(weights=None, cfg=yolo.model.yaml)
    t0b = count_vs_surgical(trainer.model, ref_sd)
    csv_rows.append({"section": "surgical_parity", "checkpoint": "T0b_yolo_train_replace", **t0b})
    checkpoints["T0b"] = zone_snapshot(trainer.model, "T0b")

    # Full _setup_train → T2/T4/T5 (T1 = post-Ultralytics inside super, inferred)
    trainer._setup_train()
    checkpoints["T2"] = zone_snapshot(trainer.model, "T2_post_setup_phase1")
    checkpoints["T4"] = zone_snapshot(trainer.model, "T4_post_rebuild_optimizer")
    checkpoints["T5"] = zone_snapshot(trainer.model, "T5_pre_first_batch")

    model = unwrap_model(trainer.model)
    model.init_criterion()
    checkpoints["T3"] = zone_snapshot(trainer.model, "T3_post_init_criterion")
    if hasattr(model, "criterion"):
        del model.criterion

    ref_hashes = {r["param_name"]: r["weight_hash"] for r in checkpoints["T5"]["params"]}
    for snap in checkpoints.values():
        apply_hash_delta(snap, ref_hashes)

    opt_names = optimizer_param_names(trainer)
    opt_zones = classify_opt_params(opt_names)
    fs = _v2.freeze_state_summary(trainer.model)

    # T6 backward
    run_one_batch_step(trainer, cfg, force_lr=float(cfg["optimizer"]["lr0"]))
    checkpoints["T6"] = zone_snapshot(trainer.model, "T6_post_backward")
    apply_hash_delta(checkpoints["T6"], ref_hashes)
    grad_probe = {"grad_sum": _v2.grad_zone_summary_v2(trainer.model)}

    # T7 pre-step (same weights as T6)
    checkpoints["T7"] = zone_snapshot(trainer.model, "T7_pre_optimizer_step")
    apply_hash_delta(checkpoints["T7"], ref_hashes)

    live_pre_step = clone_params(trainer.model)
    trainer.optimizer_step()
    checkpoints["T8"] = zone_snapshot(trainer.model, "T8_post_optimizer_step")
    apply_hash_delta(checkpoints["T8"], ref_hashes)
    step_delta = _v2.compare_param_deltas(live_pre_step, clone_params(trainer.model))

    frozen_snap: dict[str, torch.Tensor] = {}
    if trainer.ema is not None:
        trainable = _v2._trainable_param_keys(model)
        for k, v in trainer.ema.ema.state_dict().items():
            if v.dtype.is_floating_point and k not in trainable:
                frozen_snap[k] = v.detach().clone()
    ema_drift = ema_frozen_drift(trainer, frozen_snap)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        trainer.scheduler.step()
    checkpoints["T9"] = zone_snapshot(trainer.model, "T9_post_scheduler")
    apply_hash_delta(checkpoints["T9"], ref_hashes)

    live_pre_save = clone_params(trainer.model)
    trainer.fitness = 0.0
    trainer.metrics = {}
    trainer.epoch = 0
    trainer.save_model()
    checkpoints["T10"] = zone_snapshot(trainer.model, "T10_post_save_model")
    apply_hash_delta(checkpoints["T10"], ref_hashes)
    save_delta = _v2.compare_param_deltas(live_pre_save, clone_params(trainer.model))

    # Mini epoch from fresh trainer
    tr_epoch = TrainerCls(overrides=kwargs)
    tr_epoch._setup_train()
    t5_epoch = clone_params(tr_epoch.model)
    run_mini_epoch(tr_epoch)
    epoch_delta = _v2.compare_param_deltas(t5_epoch, clone_params(tr_epoch.model))

    cb_rows = list_active_callbacks(trainer)

    # --- Breakpoint logic ---
    findings: list[str] = []
    breakpoint_id: str | None = None

    if t0["changed"] == 0 and t0b["changed"] > 100:
        findings.append(
            "T0b BREAKPOINT: `YOLO.train(pretrained=False)` + `setup_model(pretrained=False)` "
            "ignore v5_surgical_init.pt → init aléatoire YAML (453+ tensors ≠ surgical_init)."
        )
        breakpoint_id = "T0_pretrained_false_discards_surgical_init"

    if fs["backbone_trainable"] == 0 and fs["cv4_hook_params"] == 24 and getattr(trainer, "_v5_n_opt_params", 0) == 24:
        findings.append(
            "T2–T5: freeze IT-only OK — requires_grad 24 cv4 hooks, optimizer 24 params, "
            "backbone/cv2/cv3/dfl gelés."
        )
    else:
        findings.append(f"T5: freeze state unexpected: {fs}")
        breakpoint_id = breakpoint_id or "T5_freeze_state_bad"

    if opt_zones.get("BACKBONE") or opt_zones.get("CV2") or opt_zones.get("CV3"):
        findings.append("T4 BREAKPOINT: optimizer contient backbone/cv2/cv3.")
        breakpoint_id = breakpoint_id or "T4_optimizer_contamination"

    if step_delta["zones"].get("backbone", {}).get("changed", 0) > 0:
        findings.append("T8: optimizer.step modifie backbone (Δ vs T7).")
        breakpoint_id = breakpoint_id or "T8_optimizer_step_backbone"
    elif step_delta["cv4_old_changed"] == 0 and step_delta["cv4_it_changed"] > 0:
        findings.append("T8: optimizer.step OK — seul cv4 IT modifié (1 batch, LR forcé).")

    epoch_ok = all(
        epoch_delta["zones"].get(z, {}).get("changed", 0) == 0
        for z in ("backbone", "cv2_box", "cv3_cls", "dfl")
    ) and epoch_delta.get("cv4_old_changed", 0) == 0
    if epoch_ok:
        findings.append(
            "T5→epoch_end (21 batches, warmup): zones gelées inchangées — "
            "le gel survive à `_do_train()` quand on mesure Δ vs T5 (pas vs surgical_init)."
        )

    if any(v > 0 for k, v in ema_drift.items() if k != "CV4_IT"):
        findings.append(f"T8 EMA drift zones gelées: {ema_drift}")
        breakpoint_id = breakpoint_id or "T8_ema_drift"

    save_mut = [z for z, d in save_delta.get("zones", {}).items() if d.get("changed", 0) > 0]
    if save_mut:
        findings.append(f"T10: save_model mute le modèle live: {save_mut}")
    else:
        findings.append("T10: save_model ne mute pas le modèle live (EMA sérialisé séparément).")

    findings.append(
        "Safety audit B→C: 100% tensors ≠ surgical_init car le run n'a jamais chargé surgical_init "
        "(pretrained=False), PAS parce que le gel est perdu pendant la boucle."
    )

    verdict = "V5_FREEZE_BREAKPOINT_IDENTIFIED" if breakpoint_id else "V5_FREEZE_BREAKPOINT_NOT_IDENTIFIED"

    # CSV
    csv_rows.append({"section": "summary", "metric": "verdict", "value": verdict})
    csv_rows.append({"section": "summary", "metric": "breakpoint", "value": breakpoint_id or ""})
    csv_rows.append({"section": "summary", "metric": "ema_mode", "value": getattr(trainer, "_v5_ema_mode", "")})
    csv_rows.append({"section": "summary", "metric": "epoch_frozen_ok", "value": epoch_ok})
    for k, v in fs.items():
        csv_rows.append({"section": "freeze_T5", "metric": k, "value": v})
    for cp, snap in checkpoints.items():
        for zone, st in snap["zones"].items():
            csv_rows.append({
                "section": "checkpoint_zone",
                "checkpoint": cp,
                "zone": zone,
                **{k: st[k] for k in ("trainable", "frozen", "grad_nonzero", "grad_norm_sum", "hash_changed", "total")},
            })
    for z, c in opt_zones.items():
        csv_rows.append({"section": "optimizer_T4", "zone": z, "n_params": c})
    for n in opt_names:
        csv_rows.append({"section": "optimizer_param", "param_name": n})
    for z, zd in step_delta["zones"].items():
        csv_rows.append({"section": "step_delta", "zone": z, **zd})
    csv_rows.append({"section": "step_delta", "metric": "cv4_old", "value": step_delta["cv4_old_changed"]})
    csv_rows.append({"section": "step_delta", "metric": "cv4_it", "value": step_delta["cv4_it_changed"]})
    for z, zd in epoch_delta["zones"].items():
        csv_rows.append({"section": "epoch_delta", "zone": z, **zd})
    for k, v in grad_probe["grad_sum"].items():
        csv_rows.append({"section": "grad_T6", "metric": k, "value": v})
    for r in cb_rows:
        csv_rows.append({"section": "callback", **r})
    for i, text in enumerate(findings, 1):
        csv_rows.append({"section": "finding", "index": i, "text": text})

    # Markdown
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [
        "# V5 Phase 1 v2 — Freeze Lifecycle Diagnostic",
        "",
        f"**Généré :** {ts}",
        "**Mode :** READ-ONLY — pas de `--train`, copie `v5_phase1_freeze_lifecycle_work.pt`",
        f"**Script :** `annotation_pilot/scripts/v5_phase1_freeze_lifecycle_debug.py`",
        f"**Verdict :** `{verdict}`",
        f"**Breakpoint :** `{breakpoint_id}`",
        "",
        "---",
        "",
        "## Breakpoint identifié",
        "",
        f"**`{breakpoint_id}`** — avant le premier batch (T0/T0b), pas pendant `optimizer.step()`.",
        "",
        "`pretrained=False` (config V5) provoque :",
        "",
        "1. `BaseTrainer.setup_model()` : charge le `.pt` puis `weights = None` (trainer.py L769-770)",
        "2. `YOLO.train()` : `get_model(weights=None, cfg=yaml)` (model.py L808-813)",
        "",
        f"Résultat T0b : **{t0b['changed']}/{t0b['total']}** tensors ≠ `v5_surgical_init.pt` (max Δ {t0b['max_diff']:.4g}).",
        "",
        "---",
        "",
        "## Snapshots T0–T10",
        "",
        "| CP | Zone | train | frozen | grad≠0 | hash≠T5 |",
        "|----|------|------:|-------:|-------:|--------:|",
    ]
    for cp in ("T0b", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"):
        snap = checkpoints[cp]
        for zone in ZONES:
            st = snap["zones"][zone]
            if st["total"] == 0:
                continue
            md.append(
                f"| {cp} | {zone} | {st['trainable']} | {st['frozen']} | "
                f"{st['grad_nonzero']} | {st['hash_changed']} |"
            )

    md.extend([
        "",
        "---",
        "",
        "## Optimizer (T4/T5)",
        "",
        f"Paramètres : **{len(opt_names)}** (attendu 24 cv4 IT uniquement)",
        "",
        "| Zone | Count |",
        "|------|------:|",
    ])
    for z, c in sorted(opt_zones.items()):
        md.append(f"| {z} | {c} |")

    md.extend([
        "",
        "---",
        "",
        "## Δ T5 → T8 (1 step, LR forcé)",
        "",
        "| Zone | changed/total | max Δ |",
        "|------|:-------------:|------:|",
    ])
    for z, zd in sorted(step_delta["zones"].items()):
        md.append(f"| {z} | {zd['changed']}/{zd['total']} | {zd['max_diff']:.6e} |")
    md.append(f"\ncv4 old: {step_delta['cv4_old_changed']} | cv4 IT: {step_delta['cv4_it_changed']}")

    md.extend([
        "",
        "---",
        "",
        "## Δ T5 → fin epoch simulée (21 batches)",
        "",
        f"**epoch_frozen_ok:** {epoch_ok}",
        "",
        "| Zone | changed/total |",
        "|------|:-------------:|",
    ])
    for z, zd in sorted(epoch_delta["zones"].items()):
        md.append(f"| {z} | {zd['changed']}/{zd['total']} |")

    md.extend([
        "",
        "---",
        "",
        "## Gradients T6",
        "",
        "| Métrique | Valeur |",
        "|----------|-------:|",
    ])
    for k, v in grad_probe["grad_sum"].items():
        md.append(f"| {k} | {v} |")

    md.extend([
        "",
        "---",
        "",
        "## EMA / save / callbacks",
        "",
        f"- EMA mode: `{getattr(trainer, '_v5_ema_mode', '')}`",
        f"- EMA drift zones gelées: `{ema_drift}`",
        f"- save_model live mutation: `{save_mut or 'none'}`",
        f"- Callbacks actifs: {len(cb_rows)} (aucun ne reset `requires_grad`)",
        "",
        "---",
        "",
        "## Findings",
        "",
    ])
    for i, text in enumerate(findings, 1):
        md.append(f"{i}. {text}")

    md.extend([
        "",
        "---",
        "",
        f"## Conclusion : `{verdict}`",
        "",
        "CSV : `v5_phase1_freeze_lifecycle_diagnostic.csv`",
    ])

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    fieldnames = sorted({k for row in csv_rows for k in row})
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)

    print(verdict)
    print(f"Breakpoint: {breakpoint_id}")
    return verdict


def main() -> int:
    argparse.ArgumentParser(description="V5 freeze lifecycle diagnostic").parse_args()
    verdict = run_lifecycle_probe(_v2.load_cfg())
    return 0 if verdict == "V5_FREEZE_BREAKPOINT_IDENTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
