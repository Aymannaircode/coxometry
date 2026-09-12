#!/usr/bin/env python3
"""V5 Phase 2 — Post-training final QA (READ-ONLY)."""
from __future__ import annotations

import csv
import importlib.util
import json
import math
import shutil
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import yaml

PROJECT = Path(__file__).resolve().parents[2]
DATASET = PROJECT / "datasets/yolo_pose_new_26"
OUT_MD = DATASET / "v5_phase2_final_QA.md"
OUT_CSV = DATASET / "v5_phase2_final_QA.csv"
RUN_DIR = PROJECT / "runs/pose/yolo_pose_new_26_v5_phase2/run_20260829_032756"
TRAINING_REPORT = RUN_DIR / "training_report.json"
BEST_PT = RUN_DIR / "weights/best_it.pt"
LAST_PT = RUN_DIR / "weights/last_it.pt"
SURGICAL = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt"
V2_PATH = PROJECT / "runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt"
SPLIT_JSON = DATASET / "meta/split.json"
MAPPING_CSV = DATASET / "meta/source_mapping.csv"
LABELS_VAL = DATASET / "labels/val"
CONFIG_PATH = DATASET / "v5_phase2_training_config.yaml"
EVAL_ROOT = DATASET / "_v5_phase2_final_QA"
IMGSZ = 640
CONF = 0.25
OLD_NK = 42
THRESH = 1e-8
LANDMARKS_16 = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L", "ASM_R", "ASM_L",
    "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L", "IT_R", "IT_L",
]

sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "annotation_pilot/manual_annotation_tool"))
from dicom_render import read_dicom_dimensions, render_dicom_png  # noqa: E402

_TRAIN_PATH = Path(__file__).resolve().parent / "train_yolo_pose_v5_phase2.py"
_spec = importlib.util.spec_from_file_location("p2train", _TRAIN_PATH)
_p2 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_p2)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def verdict_px(err: float | None) -> str:
    if err is None:
        return "NA"
    if err <= 75:
        return "CORRECT"
    if err <= 149:
        return "INCERTAIN"
    return "INCORRECT"


def tier_counts(errs: list[float]) -> dict[str, int]:
    c = {"CORRECT": 0, "INCERTAIN": 0, "INCORRECT": 0}
    for e in errs:
        c[verdict_px(e)] += 1
    return c


def load_sd_from_ckpt(path: Path) -> tuple[dict[str, torch.Tensor], dict[str, Any]]:
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    model = ckpt["model"]
    if hasattr(model, "float"):
        model = model.float()
    return dict(model.state_dict()), ckpt


def phase2_zone(name: str) -> str:
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


def compare_cv4_old(ref: torch.Tensor, tgt: torch.Tensor) -> float:
    if ref.dim() == 4 and ref.shape[0] > OLD_NK and ref.shape[1] > OLD_NK:
        d = (tgt[:OLD_NK, :OLD_NK].float() - ref[:OLD_NK, :OLD_NK].float()).abs()
        return float(d.max().item()) if d.numel() else 0.0
    if ref.dim() == 1 and ref.shape[0] > OLD_NK:
        d = (tgt[:OLD_NK].float() - ref[:OLD_NK].float()).abs()
        return float(d.max().item()) if d.numel() else 0.0
    return 0.0


def freeze_audit(ref_sd: dict[str, torch.Tensor], tgt_sd: dict[str, torch.Tensor], it_head_ref: dict | None, it_head_tgt: dict | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    zones: dict[str, dict[str, Any]] = defaultdict(lambda: {"total": 0, "changed": 0, "max_diff": 0.0})

    for name, ref in ref_sd.items():
        if name not in tgt_sd or not torch.is_floating_point(ref):
            continue
        tgt = tgt_sd[name].float()
        ref_f = ref.float()
        diff = (tgt - ref_f).abs()
        max_diff = float(diff.max().item()) if diff.numel() else 0.0
        zone = phase2_zone(name)
        if zone == "cv4_pose":
            max_diff = max(max_diff, compare_cv4_old(ref_f, tgt))
        z = zones[zone]
        z["total"] += 1
        z["max_diff"] = max(z["max_diff"], max_diff)
        if max_diff > THRESH:
            z["changed"] += 1
        rows.append({
            "section": "freeze_tensor",
            "param_name": name,
            "zone": zone,
            "max_abs_diff": max_diff,
            "changed": int(max_diff > THRESH),
            "cv4_old_max": compare_cv4_old(ref_f, tgt) if "cv4" in name else None,
        })

    if it_head_ref is not None and it_head_tgt is not None:
        it_max = 0.0
        it_changed = 0
        for k, ref in it_head_ref.items():
            if k not in it_head_tgt:
                continue
            d = (it_head_tgt[k].float() - ref.float()).abs().max().item()
            it_max = max(it_max, float(d))
            if d > THRESH:
                it_changed += 1
            rows.append({
                "section": "freeze_it_head_tensor",
                "param_name": k,
                "zone": "it_head",
                "max_abs_diff": float(d),
                "changed": int(d > THRESH),
            })
        zones["it_head"] = {"total": len(it_head_ref), "changed": it_changed, "max_diff": it_max}

    for zone, z in zones.items():
        rows.append({"section": "freeze_zone_summary", "zone": zone, **z})
    return rows


def parse_yolo_label(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        vals = [float(x) for x in line.split()]
        conf = vals[-1] if len(vals) > 5 else None
        kpts = vals[5:-1] if conf is not None else vals[5:]
        out.append({"cx": vals[1], "cy": vals[2], "w": vals[3], "h": vals[4], "conf": conf, "kpts": kpts})
    return out


def xywhn_to_xyxy(b: dict[str, float]) -> tuple[float, float, float, float]:
    cx, cy, w, h = b["cx"], b["cy"], b["w"], b["h"]
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


def iou(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if inter <= 0:
        return 0.0
    aa = (a[2] - a[0]) * (a[3] - a[1])
    bb = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (aa + bb - inter + 1e-9)


def kp_err_norm(pred_kpts: list[float], gt_kpts: list[float], w: float, h: float, ki: int, min_vis: int = 2) -> float | None:
    if len(pred_kpts) < (ki + 1) * 3 or len(gt_kpts) < (ki + 1) * 3:
        return None
    gv = gt_kpts[ki * 3 + 2]
    if gv != min_vis:
        return None
    gx, gy = gt_kpts[ki * 3] * w, gt_kpts[ki * 3 + 1] * h
    px, py = pred_kpts[ki * 3] * w, pred_kpts[ki * 3 + 1] * h
    return math.hypot(px - gx, py - gy)


def run_yolo_predict(model_path: Path, val_ids: list[str], label: str) -> Path:
    from ultralytics import YOLO

    out_dir = EVAL_ROOT / f"pred_{label}"
    out_dir.mkdir(parents=True, exist_ok=True)
    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    yolo = YOLO(str(model_path), task="pose")
    for cid in val_ids:
        dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
        png = EVAL_ROOT / "images" / f"{cid}.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        render_dicom_png(dicom, png)
        run_name = f"{label}_{cid}"
        yolo.predict(
            source=str(png.resolve()),
            imgsz=IMGSZ,
            conf=CONF,
            save_txt=True,
            save_conf=True,
            project=str(EVAL_ROOT.resolve()),
            name=run_name,
            exist_ok=True,
            verbose=False,
        )
        src = EVAL_ROOT / run_name / "labels" / f"{cid}.txt"
        if src.is_file():
            shutil.copy2(src, out_dir / f"{cid}.txt")
        shutil.rmtree(EVAL_ROOT / run_name, ignore_errors=True)
    return out_dir


def load_phase2_model(ckpt_path: Path) -> tuple[Any, dict[str, Any]]:
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = _p2.build_model(cfg)
    model.load_state_dict(ckpt["v5_phase2"]["wrapper_state"])
    _p2.attach_hyp(model.base)
    return model, ckpt


def eval_it_inmemory(model: Any, val_ids: list[str], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    from ultralytics.cfg import DEFAULT_CFG, get_cfg
    from ultralytics.data.build import build_dataloader, build_yolo_dataset
    from ultralytics.data.utils import check_det_dataset

    device = torch.device("cpu")
    model = model.to(device).eval()
    t = cfg["train"]
    args = get_cfg(cfg=DEFAULT_CFG)
    args.task = "pose"
    args.data = str(PROJECT / cfg["data"])
    args.imgsz = t["imgsz"]
    args.batch = 1
    args.workers = 0
    args.mosaic = 0.0
    data = check_det_dataset(str(PROJECT / cfg["data"]))
    dataset = build_yolo_dataset(args, data["val"], batch=1, data=data, mode="val", rect=False, stride=32)
    loader = build_dataloader(dataset, batch=1, workers=0, shuffle=False, rank=-1)

    rows: list[dict[str, Any]] = []
    min_vis = int(cfg.get("it_only", {}).get("position_loss_min_visibility", 2))
    crit = model.init_criterion()
    base = crit._base

    for batch in loader:
        batch = _p2.batch_to_device(batch, device)
        paths = batch.get("im_file", batch.get("img_path", []))
        if isinstance(paths, list):
            path = paths[0] if paths else ""
        else:
            path = paths
        cid = Path(str(path)).stem
        if cid not in val_ids:
            continue

        preds, _, _ = model.forward_head_preds(batch["img"])
        pred_kpts = preds["kpts"].permute(0, 2, 1).contiguous()
        (fg_mask, target_gt_idx, _, anchor_points, _), _, _ = base.get_assigned_targets_and_loss(preds, batch)
        if not fg_mask.any():
            rows.append({"section": "it_per_image", "case_id": cid, "note": "no_fg_anchor"})
            continue

        bs = pred_kpts.shape[0]
        imgsz = torch.tensor(preds["feats"][0].shape[2:], device=base.device, dtype=pred_kpts.dtype) * base.stride[0]
        pred_dec = base.kpts_decode(anchor_points, pred_kpts.view(bs, -1, *base.kpt_shape))
        gk = batch["keypoints"].float().clone()
        gk[..., 0] *= imgsz[1]
        gk[..., 1] *= imgsz[0]
        sel = base._select_target_keypoints(gk, batch["batch_idx"].view(-1, 1), target_gt_idx, fg_mask)
        pk = pred_dec[fg_mask][0]
        gt = sel[fg_mask][0]

        for ki, name in ((14, "IT_R"), (15, "IT_L")):
            if gt.shape[-1] == 3 and (gt[ki, 2] == min_vis).item():
                err = float(((pk[ki, :2] - gt[ki, :2]) ** 2).sum().sqrt().detach().item())
                rows.append({
                    "section": "it_landmark",
                    "case_id": cid,
                    "landmark": name,
                    "kp_index": ki,
                    "error_px": err,
                    "tier": verdict_px(err),
                    "gt_v": 2,
                })
    return rows


def summarize_it(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def bucket(name: str | None = None) -> list[float]:
        return [
            float(r["error_px"])
            for r in rows
            if r.get("section") == "it_landmark" and (name is None or r.get("landmark") == name)
        ]

    all_e = bucket()
    r_e = bucket("IT_R")
    l_e = bucket("IT_L")
    if not all_e:
        return {}

    def p90(xs: list[float]) -> float:
        s = sorted(xs)
        return s[min(len(s) - 1, math.ceil(0.9 * len(s)) - 1)]

    return {
        "IT_R_mean_px": statistics.mean(r_e) if r_e else None,
        "IT_L_mean_px": statistics.mean(l_e) if l_e else None,
        "IT_mean_px": statistics.mean(all_e),
        "IT_median_px": statistics.median(all_e),
        "IT_p90_px": p90(all_e),
        "IT_correct_rate_75": sum(1 for e in all_e if e < 75) / len(all_e),
        "IT_correct_rate_150": sum(1 for e in all_e if e < 150) / len(all_e),
        "IT_n_evaluated": len(all_e),
    }


def eval_14kp_from_preds(pred_dir: Path, val_ids: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    for cid in val_ids:
        dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
        w, h = read_dicom_dimensions(dicom)
        gt_line = (LABELS_VAL / f"{cid}.txt").read_text(encoding="utf-8").splitlines()[0]
        gt_vals = [float(x) for x in gt_line.split()]
        gt_kpts = gt_vals[5:]
        preds = parse_yolo_label(pred_dir / f"{cid}.txt")
        best = max(preds, key=lambda x: x.get("conf") or 0) if preds else None
        if not best:
            continue
        for ki in range(14):
            e = kp_err_norm(best["kpts"], gt_kpts, w, h, ki)
            if e is not None:
                rows.append({
                    "section": "kp14_landmark",
                    "case_id": cid,
                    "kp_index": ki,
                    "landmark": LANDMARKS_16[ki],
                    "error_px": e,
                    "tier": verdict_px(e),
                })
    return rows


def summarize_kp14(rows: list[dict[str, Any]], model: str) -> dict[str, Any]:
    errs = [float(r["error_px"]) for r in rows if r.get("section") == "kp14_landmark" and r.get("model") == model]
    if not errs:
        return {"model": model}
    s = sorted(errs)
    tiers = tier_counts(errs)
    return {
        "model": model,
        "mean_px": statistics.mean(errs),
        "median_px": statistics.median(errs),
        "p90_px": s[min(len(s) - 1, math.ceil(0.9 * len(s)) - 1)],
        **tiers,
        "n": len(errs),
    }


def main() -> str:
    val_ids = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))["val"]
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    report = json.loads(TRAINING_REPORT.read_text(encoding="utf-8"))
    history = report["history"]
    best_metric = report["best_IT_mean_px"]
    best_epoch = min(history, key=lambda r: r["IT_mean_px"] if r["IT_mean_px"] is not None else float("inf"))["epoch"]
    last_epoch = history[-1]["epoch"]
    patience = int(cfg["train"]["patience"])

    rows: list[dict[str, Any]] = []

    # 1. Training summary
    rows.append({"section": "training", "metric": "run_dir", "value": str(RUN_DIR.relative_to(PROJECT))})
    rows.append({"section": "training", "metric": "epochs_executed", "value": last_epoch})
    rows.append({"section": "training", "metric": "best_epoch", "value": best_epoch})
    rows.append({"section": "training", "metric": "best_IT_mean_px", "value": best_metric})
    rows.append({"section": "training", "metric": "best_it_pt", "value": str(BEST_PT.relative_to(PROJECT))})
    rows.append({"section": "training", "metric": "last_it_pt", "value": str(LAST_PT.relative_to(PROJECT))})
    rows.append({
        "section": "training",
        "metric": "stop_reason",
        "value": f"early_stopping patience={patience} on IT_mean_px; best epoch {best_epoch} ({best_metric:.4f} px); "
                 f"no improvement for {patience} epochs after best → stopped at epoch {last_epoch}",
    })
    for h in history:
        rows.append({
            "section": "epoch_curve",
            "epoch": h["epoch"],
            "train_loss": h["train_loss"],
            "IT_mean_px": h["IT_mean_px"],
            "IT_R_mean_px": h["IT_R_mean_px"],
            "IT_L_mean_px": h["IT_L_mean_px"],
            "frozen_ok": h["frozen_ok"],
            "det_ok": h["det_ok"],
        })

    # Freeze audit surgical → best
    surg_sd, surg_ckpt = load_sd_from_ckpt(SURGICAL)
    best_sd, best_ckpt = load_sd_from_ckpt(BEST_PT)
    init_model = _p2.build_model(cfg)
    init_it = {k: v.clone() for k, v in init_model.it_head.state_dict().items()}
    best_it = best_ckpt["v5_phase2"]["it_head_state"]
    freeze_rows = freeze_audit(surg_sd, best_sd, init_it, best_it)
    rows.extend(freeze_rows)
    zone_summ = {r["zone"]: r for r in freeze_rows if r.get("section") == "freeze_zone_summary"}
    frozen_zones = ("backbone", "neck", "cv2_box", "cv3_cls", "dfl", "cv4_pose")
    freeze_ok = all(zone_summ.get(z, {}).get("changed", 1) == 0 for z in frozen_zones)
    it_head_ok = zone_summ.get("it_head", {}).get("changed", 0) > 0

    # Inference dirs
    pred_v2 = run_yolo_predict(V2_PATH, val_ids, "V2")
    pred_surg = run_yolo_predict(SURGICAL, val_ids, "surgical")
    pred_p2 = run_yolo_predict(BEST_PT, val_ids, "phase2_best")

    # Detection comparison
    for label, pdir in (("V2", pred_v2), ("surgical_init", pred_surg), ("phase2_best", pred_p2)):
        for cid in val_ids:
            gt_boxes = parse_yolo_label(LABELS_VAL / f"{cid}.txt")
            gt_xy = xywhn_to_xyxy(gt_boxes[0]) if gt_boxes else None
            preds = parse_yolo_label(pdir / f"{cid}.txt")
            best = max(preds, key=lambda x: x.get("conf") or 0) if preds else None
            row = {
                "section": "detection",
                "model": label,
                "case_id": cid,
                "n_boxes": len(preds),
                "top_conf": best["conf"] if best else None,
            }
            if gt_xy and best:
                row["iou_vs_gt"] = iou(gt_xy, xywhn_to_xyxy(best))
            rows.append(row)

    # 14 KP from YOLO preds
    kp14_all: list[dict[str, Any]] = []
    for label, pdir in (("V2", pred_v2), ("surgical_init", pred_surg), ("phase2_best", pred_p2)):
        kp_rows = eval_14kp_from_preds(pdir, val_ids)
        for r in kp_rows:
            r["model"] = label
        kp14_all.extend(kp_rows)
    rows.extend(kp14_all)

    # IT in-memory phase2 best
    p2_model, _ = load_phase2_model(BEST_PT)
    it_rows = eval_it_inmemory(p2_model, val_ids, cfg)
    rows.extend(it_rows)
    it_summary = summarize_it(it_rows)

    # IT from YOLO for V2/surgical (cv4 channels) — reference only
    for label, pdir in (("V2", pred_v2), ("surgical_init", pred_surg)):
        mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
        for cid in val_ids:
            dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
            w, h = read_dicom_dimensions(dicom)
            gt_line = (LABELS_VAL / f"{cid}.txt").read_text(encoding="utf-8").splitlines()[0]
            gt_kpts = [float(x) for x in gt_line.split()][5:]
            preds = parse_yolo_label(pdir / f"{cid}.txt")
            best = max(preds, key=lambda x: x.get("conf") or 0) if preds else None
            if not best:
                continue
            for ki, name in ((14, "IT_R"), (15, "IT_L")):
                e = kp_err_norm(best["kpts"], gt_kpts, w, h, ki)
                if e is not None:
                    rows.append({
                        "section": "it_yolo_ref",
                        "model": label,
                        "case_id": cid,
                        "landmark": name,
                        "error_px": e,
                        "tier": verdict_px(e),
                    })

    # Per-image IT summary
    for cid in val_ids:
        sub = [r for r in it_rows if r.get("case_id") == cid and r.get("section") == "it_landmark"]
        if not sub:
            continue
        errs = [float(r["error_px"]) for r in sub]
        rows.append({
            "section": "it_per_image_summary",
            "case_id": cid,
            "IT_mean_px": statistics.mean(errs),
            "IT_n": len(errs),
            "IT_R_px": next((r["error_px"] for r in sub if r["landmark"] == "IT_R"), None),
            "IT_L_px": next((r["error_px"] for r in sub if r["landmark"] == "IT_L"), None),
        })

    # Verdict logic
    det_rows = [r for r in rows if r.get("section") == "detection"]
    v2_det = sum(1 for r in det_rows if r["model"] == "V2" and r["n_boxes"] >= 1)
    p2_det = sum(1 for r in det_rows if r["model"] == "phase2_best" and r["n_boxes"] >= 1)
    det_regression = p2_det < v2_det or any(
        r["model"] == "phase2_best" and r["n_boxes"] != next(x["n_boxes"] for x in det_rows if x["case_id"] == r["case_id"] and x["model"] == "V2")
        for r in det_rows if r["model"] == "phase2_best"
    )

    kp14_v2 = summarize_kp14([{**r, "model": r["model"]} for r in kp14_all], "V2")
    kp14_p2 = summarize_kp14(kp14_all, "phase2_best")
    kp14_regression = abs(kp14_p2.get("mean_px", 0) - kp14_v2.get("mean_px", 0)) > 1.0

    init_it_mean = history[0]["IT_mean_px"]
    final_best_it = it_summary.get("IT_mean_px", best_metric)
    it_improved = final_best_it < init_it_mean - 1.0
    it_sufficient = final_best_it <= 150.0 and it_summary.get("IT_correct_rate_150", 0) > 0.5

    if not freeze_ok:
        verdict = "V5_PHASE2_FREEZE_VIOLATION"
    elif det_regression:
        verdict = "V5_PHASE2_DETECTION_REGRESSION"
    elif it_sufficient:
        verdict = "V5_PHASE2_SUCCESS"
    elif it_improved:
        verdict = "V5_PHASE2_IT_IMPROVED_BUT_INSUFFICIENT"
    else:
        verdict = "V5_PHASE2_IT_IMPROVED_BUT_INSUFFICIENT"

    rows.append({"section": "verdict", "metric": "status", "value": verdict})
    rows.append({"section": "verdict", "metric": "freeze_ok", "value": freeze_ok})
    rows.append({"section": "verdict", "metric": "it_head_changed", "value": it_head_ok})
    rows.append({"section": "verdict", "metric": "det_regression", "value": det_regression})
    rows.append({"section": "verdict", "metric": "it_improved_vs_epoch1", "value": it_improved})

    # CSV
    keys = sorted({k for r in rows for k in r})
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # Markdown
    md = [
        "# V5 Phase 2 — Final QA (Post-Training)",
        "",
        f"**Généré :** {utc_now()}",
        "**Mode :** READ-ONLY",
        f"**Run :** `{RUN_DIR.relative_to(PROJECT)}`",
        f"**Verdict :** `{verdict}`",
        "",
        "---",
        "",
        "## 1. Training",
        "",
        f"| Métrique | Valeur |",
        f"|----------|--------|",
        f"| Epochs exécutés | {last_epoch} |",
        f"| Meilleur epoch | **{best_epoch}** |",
        f"| Meilleur IT_mean_px | **{best_metric:.2f} px** |",
        f"| best_it.pt | `{BEST_PT.relative_to(PROJECT)}` |",
        f"| last_it.pt | `{LAST_PT.relative_to(PROJECT)}` |",
        f"| Arrêt | early stopping patience={patience} sur IT_mean_px — meilleur epoch {best_epoch}, arrêt epoch {last_epoch} |",
        "",
        "### Évolution IT_mean_px",
        "",
        "| Epoch | train_loss | IT_mean_px | IT_R | IT_L | frozen_ok |",
        "|------:|-----------:|-----------:|-----:|-----:|:---------:|",
    ]
    for h in history:
        md.append(
            f"| {h['epoch']} | {h['train_loss']:.4f} | {h['IT_mean_px']:.2f} | "
            f"{h['IT_R_mean_px']:.2f} | {h['IT_L_mean_px']:.2f} | {h['frozen_ok']} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 2. IT Performance (val, v=2 uniquement) — Phase2 best in-memory",
        "",
        f"| Métrique | Valeur |",
        f"|----------|-------:|",
        f"| IT_R_mean_px | {it_summary.get('IT_R_mean_px', '—')} |",
        f"| IT_L_mean_px | {it_summary.get('IT_L_mean_px', '—')} |",
        f"| IT_mean_px | {it_summary.get('IT_mean_px', '—')} |",
        f"| IT_median_px | {it_summary.get('IT_median_px', '—')} |",
        f"| IT_p90_px | {it_summary.get('IT_p90_px', '—')} |",
        f"| IT_correct_rate <75 px | {it_summary.get('IT_correct_rate_75', 0):.1%} |",
        f"| IT_correct_rate <150 px | {it_summary.get('IT_correct_rate_150', 0):.1%} |",
        f"| N évalué | {it_summary.get('IT_n_evaluated', 0)} |",
        "",
        "### Par image",
        "",
        "| Image | IT_R px | IT_L px | IT_mean px |",
        "|-------|--------:|--------:|-----------:|",
    ])
    for cid in val_ids:
        s = next((r for r in rows if r.get("section") == "it_per_image_summary" and r.get("case_id") == cid), None)
        if s:
            md.append(f"| {cid} | {s.get('IT_R_px', '—')} | {s.get('IT_L_px', '—')} | {s.get('IT_mean_px', '—'):.2f} |")

    md.extend([
        "",
        "---",
        "",
        "## 3. Comparaison V2 / surgical_init / Phase2 best",
        "",
        "### Détection (conf=0.25)",
        "",
        "| Image | V2 n | V2 conf | V2 IoU | surgical n | phase2 n | phase2 conf | phase2 IoU |",
        "|-------|-----:|--------:|-------:|-----------:|---------:|------------:|-----------:|",
    ])
    for cid in val_ids:
        def g(m, k):
            r = next((x for x in det_rows if x["case_id"] == cid and x["model"] == m), {})
            return r.get(k)
        md.append(
            f"| {cid} | {g('V2','n_boxes')} | {g('V2','top_conf')} | {g('V2','iou_vs_gt')} | "
            f"{g('surgical_init','n_boxes')} | {g('phase2_best','n_boxes')} | {g('phase2_best','top_conf')} | {g('phase2_best','iou_vs_gt')} |"
        )

    md.extend([
        "",
        "### 14 KP — agrégat",
        "",
        "| Modèle | Mean px | Median | P90 | CORRECT | INCERTAIN | INCORRECT |",
        "|--------|--------:|-------:|----:|--------:|----------:|----------:|",
    ])
    for label in ("V2", "surgical_init", "phase2_best"):
        s = summarize_kp14(kp14_all, label)
        md.append(
            f"| {label} | {s.get('mean_px', '—'):.2f} | {s.get('median_px', '—'):.2f} | {s.get('p90_px', '—'):.2f} | "
            f"{s.get('CORRECT', 0)} | {s.get('INCERTAIN', 0)} | {s.get('INCORRECT', 0)} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 4. Safety / Freeze (surgical_init → best_it.pt)",
        "",
        f"**Freeze zones OK :** {freeze_ok}",
        f"**IT head changed :** {it_head_ok}",
        "",
        "| Zone | Tensors | Changed | Max Δ |",
        "|------|--------:|--------:|------:|",
    ])
    for z in ("backbone", "neck", "cv2_box", "cv3_cls", "dfl", "cv4_pose", "it_head"):
        s = zone_summ.get(z, {})
        md.append(f"| {z} | {int(s.get('total', 0))} | {int(s.get('changed', 0))} | {s.get('max_diff', 0):.6e} |")

    md.extend([
        "",
        "---",
        "",
        "## 5. Détection — régression",
        "",
        f"- V2 détections /5 : **{v2_det}/5**",
        f"- Phase2 best détections /5 : **{p2_det}/5**",
        f"- Régression détection : **{det_regression}**",
        "",
        "---",
        "",
        "## 6. 14 KP vs V2",
        "",
        f"- Mean V2 : {kp14_v2.get('mean_px', 0):.2f} px",
        f"- Mean Phase2 : {kp14_p2.get('mean_px', 0):.2f} px",
        f"- Régression significative : **{kp14_regression}**",
        "",
        "---",
        "",
        f"## 7. Conclusion : `{verdict}`",
        "",
        f"- Gel respecté : {freeze_ok}",
        f"- IT head entraîné (Δ>0) : {it_head_ok}",
        f"- IT amélioré vs epoch 1 ({init_it_mean:.2f} → {final_best_it:.2f} px) : {it_improved}",
        f"- IT suffisant (<150 px, >50% correct) : {it_sufficient}",
        f"- Détection stable vs V2 : {not det_regression}",
        "",
        f"CSV : `{OUT_CSV.name}`",
    ])
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(verdict)
    return verdict


if __name__ == "__main__":
    main()
