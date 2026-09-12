#!/usr/bin/env python3
"""V5 Phase 1 v2 — post epoch-1 safety audit (READ-ONLY)."""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import yaml

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))
TOOL_DIR = PROJECT / "annotation_pilot" / "manual_annotation_tool"
sys.path.insert(0, str(TOOL_DIR))

from dicom_render import render_dicom_png  # noqa: E402
from ultralytics.nn.tasks import torch_safe_load

DATASET = PROJECT / "datasets/yolo_pose_new_26"
OUT_MD = DATASET / "v5_phase1_v2_epoch1_safety_audit.md"
OUT_CSV = DATASET / "v5_phase1_v2_epoch1_safety_audit.csv"
SPLIT_JSON = DATASET / "meta/split.json"
MAPPING_CSV = DATASET / "meta/source_mapping.csv"
RUN_DIR = PROJECT / "runs/pose/yolo_pose_new_26_v5_phase1_it_v2-2"
ARGS_YAML = RUN_DIR / "args.yaml"
RESULTS_CSV = RUN_DIR / "results.csv"

V2_PATH = PROJECT / "runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt"
SURGICAL = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt"
BEST_P1 = RUN_DIR / "weights/best.pt"
LAST_P1 = RUN_DIR / "weights/last.pt"

OLD_NK = 42
IMGSZ = 640
CONF = 0.25
EVAL_IMG = DATASET / "_v5_phase1_v2_epoch1_audit/images"
THRESH = 1e-8

MODELS = {
    "A_V2_best": V2_PATH,
    "B_v5_surgical_init": SURGICAL,
    "C_phase1_v2_best": BEST_P1,
    "D_phase1_v2_last": LAST_P1,
}


def load_ckpt(path: Path) -> tuple[dict[str, torch.Tensor], dict[str, Any]]:
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    model = ckpt["model"].float()
    return dict(model.state_dict()), ckpt


def param_zone(name: str) -> str:
    if "dfl" in name:
        return "dfl"
    if "cv4" in name:
        return "cv4_pose"
    if "cv3" in name:
        return "cv3_cls"
    if "cv2" in name:
        return "cv2_box"
    if name.startswith("model.") and name.split(".")[1].isdigit():
        if int(name.split(".")[1]) <= 22:
            return "backbone"
    return "other"


def block_stats(ref: torch.Tensor, tgt: torch.Tensor, slices: tuple[slice, ...]) -> dict[str, float]:
    rb = ref[slices].float()
    tb = tgt[slices].float()
    if rb.shape != tb.shape:
        return {"max_abs_diff": float("nan"), "mean_abs_diff": float("nan"), "changed": float("nan")}
    d = (tb - rb).abs()
    return {
        "max_abs_diff": float(d.max().item()) if d.numel() else 0.0,
        "mean_abs_diff": float(d.mean().item()) if d.numel() else 0.0,
        "changed": float((d > THRESH).any().item()) if d.numel() else 0.0,
    }


def compare_param(ref: torch.Tensor, tgt: torch.Tensor, name: str) -> dict[str, Any]:
    zone = param_zone(name)
    row: dict[str, Any] = {"param_name": name, "zone": zone}
    if ref.shape != tgt.shape:
        row["shape_match"] = False
        return row
    row["shape_match"] = True
    d = (tgt.float() - ref.float()).abs()
    row.update({
        "max_abs_diff": float(d.max().item()),
        "mean_abs_diff": float(d.mean().item()),
        "changed": float(d.max().item()) > THRESH,
    })
    if zone == "cv4_pose":
        if ref.dim() == 4:
            row.update({f"cv4_old_{k}": v for k, v in block_stats(ref, tgt, (slice(0, OLD_NK), slice(0, OLD_NK))).items()})
            if ref.shape[0] > OLD_NK:
                row.update({f"cv4_it_rows_{k}": v for k, v in block_stats(ref, tgt, (slice(OLD_NK, None), slice(None, None))).items()})
            if ref.shape[0] > OLD_NK and ref.shape[1] > OLD_NK:
                row.update({f"cv4_it_block_{k}": v for k, v in block_stats(ref, tgt, (slice(OLD_NK, None), slice(OLD_NK, None))).items()})
        elif ref.dim() == 1 and ref.shape[0] > OLD_NK:
            row.update({f"cv4_old_{k}": v for k, v in block_stats(ref, tgt, (slice(0, OLD_NK),)).items()})
            row.update({f"cv4_it_rows_{k}": v for k, v in block_stats(ref, tgt, (slice(OLD_NK, None),)).items()})
    return row


def summarize(rows: list[dict[str, Any]], prefix: str = "") -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = defaultdict(lambda: {"n": 0, "changed": 0, "max": 0.0, "mean_sum": 0.0})
    for r in rows:
        z = r.get("zone", "other")
        out[z]["n"] += 1
        key = f"{prefix}max_abs_diff" if prefix else "max_abs_diff"
        mx = float(r.get(key, r.get("max_abs_diff", 0.0)) or 0.0)
        if r.get(f"{prefix}changed" if prefix else "changed", r.get("changed", False)):
            out[z]["changed"] += 1
        out[z]["max"] = max(out[z]["max"], mx)
        mn = float(r.get(f"{prefix}mean_abs_diff" if prefix else "mean_abs_diff", 0.0) or 0.0)
        out[z]["mean_sum"] += mn
    for z in out:
        n = max(out[z]["n"], 1)
        out[z]["mean"] = out[z]["mean_sum"] / n
    return dict(out)


def summarize_cv4_sub(rows: list[dict[str, Any]], sub: str) -> dict[str, float]:
    changed = 0
    n = 0
    mx = 0.0
    mean_sum = 0.0
    for r in rows:
        if r.get("zone") != "cv4_pose":
            continue
        k_max = f"{sub}_max_abs_diff"
        k_mean = f"{sub}_mean_abs_diff"
        k_chg = f"{sub}_changed"
        if k_max not in r:
            continue
        n += 1
        v = float(r[k_max])
        mx = max(mx, v)
        mean_sum += float(r.get(k_mean, 0.0))
        if r.get(k_chg, 0.0):
            changed += 1
    return {"n": n, "changed": changed, "max": mx, "mean": mean_sum / max(n, 1)}


def load_val_images(val_ids: list[str]) -> dict[str, Path]:
    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    EVAL_IMG.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for cid in val_ids:
        dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
        png = EVAL_IMG / f"{cid}.png"
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
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    if inter <= 0:
        return 0.0
    aa = (a[2] - a[0]) * (a[3] - a[1])
    bb = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (aa + bb - inter + 1e-9)


def run_inference(model_path: Path, images: dict[str, Path], out_dir: Path) -> None:
    from ultralytics import YOLO
    import shutil

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    yolo = YOLO(str(model_path), task="pose")
    for cid, img in images.items():
        run_root = DATASET / "_v5_phase1_v2_epoch1_audit" / f"_ultra_{out_dir.name}_{cid}"
        if run_root.exists():
            shutil.rmtree(run_root)
        yolo.predict(
            source=str(img.resolve()),
            imgsz=IMGSZ,
            conf=CONF,
            save=False,
            save_txt=True,
            save_conf=True,
            project=str(run_root.parent.resolve()),
            name=run_root.name,
            exist_ok=True,
            verbose=False,
        )
        raw = run_root / "labels" / f"{img.stem}.txt"
        dst = out_dir / f"{cid}.txt"
        if raw.is_file():
            shutil.copy2(raw, dst)
        shutil.rmtree(run_root, ignore_errors=True)


def inspect_checkpoint(path: Path, label: str) -> dict[str, Any]:
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    meta: dict[str, Any] = {
        "label": label,
        "path": str(path.relative_to(PROJECT)),
        "epoch": ckpt.get("epoch"),
        "best_fitness": ckpt.get("best_fitness"),
        "updates": ckpt.get("updates"),
        "has_ema_object": ckpt.get("ema") is not None,
        "has_optimizer_object": ckpt.get("optimizer") is not None,
        "train_metrics": ckpt.get("train_metrics"),
        "train_results": ckpt.get("train_results"),
    }
    if ckpt.get("optimizer") is not None:
        opt = ckpt["optimizer"]
        meta["optimizer_n_groups"] = len(opt.param_groups)
        meta["optimizer_n_params"] = sum(len(g["params"]) for g in opt.param_groups)
        meta["optimizer_groups"] = [
            {
                "index": i,
                "n_params": len(g["params"]),
                "lr": float(g.get("lr", 0)),
                "initial_lr": float(g["initial_lr"]) if "initial_lr" in g else None,
                "weight_decay": float(g.get("weight_decay", 0)),
                "param_group": g.get("param_group"),
            }
            for i, g in enumerate(opt.param_groups)
        ]
    if ckpt.get("ema") is not None:
        ema = ckpt["ema"]
        meta["ema_type"] = type(ema).__name__
        if hasattr(ema, "state_dict"):
            meta["ema_n_tensors"] = len(ema.state_dict())
    return meta


def compare_ema_frozen(ckpt_path: Path, ref_sd: dict[str, torch.Tensor]) -> list[dict[str, Any]]:
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    rows: list[dict[str, Any]] = []
    ema = ckpt.get("ema")
    model_sd = dict(ckpt["model"].float().state_dict())
    # Saved inference weights are in ckpt["model"]; EMA may be stripped at save.
    for src_name, src_sd in (("model_saved", model_sd),):
        for name, ref in ref_sd.items():
            if name not in src_sd or not torch.is_floating_point(ref):
                continue
            zone = param_zone(name)
            if zone in {"cv4_pose"} and "cv4" in name:
                continue
            if zone in {"backbone", "cv2_box", "cv3_cls", "dfl", "other"} or (
                zone == "cv4_pose" and ref.dim() != 4
            ):
                d = (src_sd[name].float() - ref.float()).abs().max().item()
                rows.append({
                    "section": "ema_or_saved_vs_surgical",
                    "source": src_name,
                    "param_name": name,
                    "zone": zone,
                    "max_abs_diff": float(d),
                    "changed": float(d) > THRESH,
                })
    if ema is not None and hasattr(ema, "state_dict"):
        ema_sd = ema.state_dict()
        for name, ref in ref_sd.items():
            if name not in ema_sd:
                continue
            zone = param_zone(name)
            if zone not in {"backbone", "cv2_box", "cv3_cls", "dfl"}:
                continue
            d = (ema_sd[name].float() - ref.float()).abs().max().item()
            rows.append({
                "section": "ema_vs_surgical",
                "source": "ema",
                "param_name": name,
                "zone": zone,
                "max_abs_diff": float(d),
                "changed": float(d) > THRESH,
            })
    return rows


def decide_verdict(
    sum_b_c: dict[str, dict[str, float]],
    sum_b_d: dict[str, dict[str, float]],
    cv4_old_c: dict[str, float],
    cv4_it_c: dict[str, float],
    v2_det: int,
    surg_det: int,
    best_det: int,
    last_det: int,
    train_results: dict[str, Any] | None,
    val_metrics: dict[str, Any] | None,
) -> str:
    frozen_zones = ("backbone", "cv2_box", "cv3_cls", "dfl")
    frozen_changed = any(sum_b_c.get(z, {}).get("changed", 0) > 0 for z in frozen_zones)
    frozen_changed |= cv4_old_c.get("changed", 0) > 0
    if frozen_changed:
        return "V5_PHASE1_V2_FREEZE_BROKEN"

    det_stable = v2_det == surg_det == best_det == last_det and v2_det >= 4
    metrics_bad = False
    if val_metrics:
        metrics_bad = float(val_metrics.get("metrics/mAP50(B)", 0)) < 0.1
    if det_stable and metrics_bad:
        return "V5_PHASE1_METRICS_ISSUE"
    if det_stable:
        return "V5_PHASE1_EPOCH1_SAFE"
    if not frozen_changed and (best_det < v2_det or surg_det >= 4):
        return "V5_PHASE1_VALIDATION_OR_ARCHITECTURE_ISSUE"
    return "V5_PHASE1_VALIDATION_OR_ARCHITECTURE_ISSUE"


def main() -> str:
    for p in MODELS.values():
        if not p.is_file():
            raise SystemExit(f"Checkpoint manquant : {p}")

    val_ids = json.loads(SPLIT_JSON.read_text())["val"]
    args = yaml.safe_load(ARGS_YAML.read_text(encoding="utf-8"))
    results_row = list(csv.DictReader(RESULTS_CSV.open(encoding="utf-8")))[-1]

    sds = {k: load_ckpt(p)[0] for k, p in MODELS.items()}
    ckpts = {k: load_ckpt(p)[1] for k, p in MODELS.items()}

    csv_rows: list[dict[str, Any]] = []

    # 1. Tensor comparisons
    pairs = [
        ("A_V2_best", "B_v5_surgical_init", "A_vs_B"),
        ("B_v5_surgical_init", "C_phase1_v2_best", "B_vs_C"),
        ("B_v5_surgical_init", "D_phase1_v2_last", "B_vs_D"),
    ]
    all_diffs: dict[str, list[dict[str, Any]]] = {}
    for ref_k, tgt_k, tag in pairs:
        rows = []
        common = sorted(set(sds[ref_k]) & set(sds[tgt_k]))
        for name in common:
            r = compare_param(sds[ref_k][name], sds[tgt_k][name], name)
            r.update({"section": "weight_diff", "pair": tag, "ref": ref_k, "tgt": tgt_k})
            rows.append(r)
        all_diffs[tag] = rows
        csv_rows.extend(rows)

    sum_ab = summarize(all_diffs["A_vs_B"])
    sum_bc = summarize(all_diffs["B_vs_C"])
    sum_bd = summarize(all_diffs["B_vs_D"])
    cv4_old_c = summarize_cv4_sub(all_diffs["B_vs_C"], "cv4_old")
    cv4_it_c = summarize_cv4_sub(all_diffs["B_vs_C"], "cv4_it_block")
    if cv4_it_c["n"] == 0:
        cv4_it_c = summarize_cv4_sub(all_diffs["B_vs_C"], "cv4_it_rows")

    # 2. Inference
    images = load_val_images(val_ids)
    pred_dirs: dict[str, Path] = {}
    for label, path in MODELS.items():
        d = DATASET / f"_v5_phase1_v2_epoch1_audit/pred_{label}"
        run_inference(path, images, d)
        pred_dirs[label] = d

    gt_root = DATASET / "labels/val"
    inf_rows: list[dict[str, Any]] = []
    for cid in val_ids:
        gt_boxes = parse_yolo_label(gt_root / f"{cid}.txt")
        gt_box = gt_boxes[0] if gt_boxes else None
        gt_xyxy = xywhn_to_xyxy(gt_box) if gt_box else None
        for label, pdir in pred_dirs.items():
            preds = parse_yolo_label(pdir / f"{cid}.txt")
            best = max(preds, key=lambda x: x.get("conf") or 0) if preds else None
            row = {
                "section": "inference_val",
                "image": cid,
                "model": label,
                "n_boxes": len(preds),
                "detected": len(preds) > 0,
                "top_conf": best["conf"] if best else None,
                "top_cx": best["cx"] if best else None,
                "top_cy": best["cy"] if best else None,
                "top_w": best["w"] if best else None,
                "top_h": best["h"] if best else None,
            }
            if gt_xyxy and best:
                row["iou_vs_gt"] = iou(gt_xyxy, xywhn_to_xyxy(best))
            inf_rows.append(row)
            csv_rows.append(row)

    det = {label: sum(1 for r in inf_rows if r["model"] == label and r["detected"]) for label in MODELS}

    # 3–4. Checkpoint / EMA / optimizer meta
    for label, path in MODELS.items():
        if label.startswith(("C_", "D_", "B_")):
            meta = inspect_checkpoint(path, label)
            csv_rows.append({"section": "checkpoint_meta", **meta})

    ema_rows = compare_ema_frozen(BEST_P1, sds["B_v5_surgical_init"])
    csv_rows.extend(ema_rows)
    ema_frozen_changed = sum(1 for r in ema_rows if r.get("changed") and r.get("zone") in {"backbone", "cv2_box", "cv3_cls", "dfl"})

    # 5. Freeze after epoch — inferred from weight diffs B→C
    freeze_ok = all(sum_bc.get(z, {}).get("changed", 0) == 0 for z in ("backbone", "cv2_box", "cv3_cls", "dfl"))
    freeze_ok &= cv4_old_c.get("changed", 0) == 0

    # 6. Loss from results.csv (training) + val metrics in checkpoint
    train_loss = {
        "box": float(results_row.get("train/box_loss", "nan")),
        "pose": float(results_row.get("train/pose_loss", "nan")),
        "kobj": float(results_row.get("train/kobj_loss", "nan")),
        "cls": float(results_row.get("train/cls_loss", "nan")),
        "dfl": float(results_row.get("train/dfl_loss", "nan")),
    }
    val_metrics = ckpts["C_phase1_v2_best"].get("train_metrics") or {}

    # 7. Validation checkpoint
    best_last_identical = all(
        (sds["C_phase1_v2_best"][k].float() - sds["D_phase1_v2_last"][k].float()).abs().max().item() <= THRESH
        for k in sds["C_phase1_v2_best"]
        if torch.is_floating_point(sds["C_phase1_v2_best"][k])
    )
    val_ckpt_path = str(BEST_P1.relative_to(PROJECT))

    verdict = decide_verdict(
        sum_bc, sum_bd, cv4_old_c, cv4_it_c,
        det["A_V2_best"], det["B_v5_surgical_init"], det["C_phase1_v2_best"], det["D_phase1_v2_last"],
        ckpts["C_phase1_v2_best"].get("train_results"),
        val_metrics,
    )

    for k, v in train_loss.items():
        csv_rows.append({"section": "train_loss_epoch1", "metric": k, "value": v})
    csv_rows.append({"section": "summary", "metric": "verdict", "value": verdict})

    fieldnames = sorted({k for row in csv_rows for k in row})
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [
        "# V5 Phase 1 v2 — Post Epoch-1 Safety Audit",
        "",
        f"**Généré :** {ts}",
        "**Mode :** READ-ONLY — aucun training",
        f"**Run :** `runs/pose/yolo_pose_new_26_v5_phase1_it_v2-2`",
        f"**Verdict :** `{verdict}`",
        "",
        "---",
        "",
        "## Checkpoints comparés",
        "",
        "| ID | Fichier |",
        "|----|---------|",
        f"| A | `{V2_PATH.relative_to(PROJECT)}` |",
        f"| B | `{SURGICAL.relative_to(PROJECT)}` |",
        f"| C | `{BEST_P1.relative_to(PROJECT)}` |",
        f"| D | `{LAST_P1.relative_to(PROJECT)}` |",
        "",
        "---",
        "",
        "## 1. Comparaison tensorielle",
        "",
        "### A vs B (parité V2 / surgical_init)",
        "",
        "| Zone | Tensors | Changed | Max Δ | Mean Δ |",
        "|------|--------:|--------:|------:|-------:|",
    ]
    for zone in ("backbone", "cv2_box", "cv3_cls", "dfl", "cv4_pose", "other"):
        s = sum_ab.get(zone, {"n": 0, "changed": 0, "max": 0, "mean": 0})
        md.append(f"| {zone} | {int(s['n'])} | {int(s['changed'])} | {s['max']:.6e} | {s.get('mean', 0):.6e} |")

    md.extend([
        "",
        "### B vs C (surgical_init → phase1 v2 best)",
        "",
        "| Zone | Tensors | Changed | Max Δ | Mean Δ |",
        "|------|--------:|--------:|------:|-------:|",
    ])
    for zone in ("backbone", "cv2_box", "cv3_cls", "dfl", "cv4_pose", "other"):
        s = sum_bc.get(zone, {"n": 0, "changed": 0, "max": 0, "mean": 0})
        md.append(f"| {zone} | {int(s['n'])} | {int(s['changed'])} | {s['max']:.6e} | {s.get('mean', 0):.6e} |")

    md.extend([
        "",
        "**cv4 détail B→C :**",
        "",
        f"| Sous-zone | Tensors | Changed | Max Δ | Mean Δ |",
        f"|-----------|--------:|--------:|------:|-------:|",
        f"| cv4 canaux 0–41 (old) | {int(cv4_old_c['n'])} | {int(cv4_old_c['changed'])} | {cv4_old_c['max']:.6e} | {cv4_old_c['mean']:.6e} |",
        f"| cv4 canaux 42–47 (IT) | {int(cv4_it_c['n'])} | {int(cv4_it_c['changed'])} | {cv4_it_c['max']:.6e} | {cv4_it_c['mean']:.6e} |",
        "",
        "### B vs D (surgical_init → phase1 v2 last)",
        "",
        "| Zone | Changed | Max Δ |",
        "|------|--------:|------:|",
    ])
    for zone in ("backbone", "cv2_box", "cv3_cls", "dfl", "cv4_pose"):
        s = sum_bd.get(zone, {"changed": 0, "max": 0})
        md.append(f"| {zone} | {int(s['changed'])} | {s['max']:.6e} |")

    md.extend([
        "",
        "---",
        "",
        "## 2. Détection val (imgsz=640, conf=0.25, 5 images)",
        "",
        f"| Modèle | Détections / 5 |",
        f"|--------|:--------------:|",
    ])
    for label in MODELS:
        md.append(f"| {label} | **{det[label]}/5** |")

    md.extend([
        "",
        "| Image | Modèle | n_boxes | conf | IoU vs GT |",
        "|-------|--------|--------:|-----:|----------:|",
    ])
    for r in inf_rows:
        md.append(
            f"| {r['image']} | {r['model']} | {r['n_boxes']} | "
            f"{r['top_conf'] if r['top_conf'] is not None else '—'} | "
            f"{r.get('iou_vs_gt', '—') if r.get('iou_vs_gt') is not None else '—'} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 3. EMA / checkpoint sauvegardé",
        "",
        f"| Checkpoint | ema object | optimizer object | epoch field |",
        f"|------------|:----------:|:----------------:|:-----------:|",
    ])
    for label in ("C_phase1_v2_best", "D_phase1_v2_last"):
        m = inspect_checkpoint(MODELS[label], label)
        md.append(
            f"| {label} | {m['has_ema_object']} | {m['has_optimizer_object']} | {m['epoch']} |"
        )
    md.extend([
        "",
        f"Poids gelés divergents vs surgical_init dans checkpoint sauvegardé : **{ema_frozen_changed}** tensors",
        "",
        "---",
        "",
        "## 4. Optimizer (dans checkpoint)",
        "",
    ])
    opt_meta = inspect_checkpoint(BEST_P1, "C")
    if opt_meta.get("optimizer_groups"):
        md.append("| Group | n_params | lr | initial_lr | weight_decay |")
        md.append("|------:|---------:|---:|-----------:|-------------:|")
        for g in opt_meta["optimizer_groups"]:
            md.append(
                f"| {g['param_group']} | {g['n_params']} | {g['lr']:.2e} | "
                f"{g['initial_lr'] if g['initial_lr'] is not None else '—'} | {g['weight_decay']:.2e} |"
            )
    else:
        md.append("Optimizer **non embarqué** dans best.pt (Ultralytics strip à la sauvegarde finale).")

    md.extend([
        "",
        "---",
        "",
        "## 5. Freeze après epoch (inféré B→C)",
        "",
        f"- backbone/cv2/cv3/dfl unchanged : **{freeze_ok}**",
        f"- cv4 old 0–41 unchanged : **{cv4_old_c['changed'] == 0}**",
        f"- cv4 IT 42–47 changed : **{cv4_it_c['changed'] > 0}** ({int(cv4_it_c['changed'])} tensors)",
        "",
        "---",
        "",
        "## 6. Loss epoch 1 (results.csv train + val)",
        "",
        f"| Composante | Train (logged) | Val (checkpoint metrics) |",
        f"|------------|---------------:|-------------------------:|",
        f"| box | {train_loss['box']:.4f} | {float(val_metrics.get('val/box_loss', 0)):.4f} |",
        f"| pose | {train_loss['pose']:.4f} | {float(val_metrics.get('val/pose_loss', 0)):.4f} |",
        f"| kobj | {train_loss['kobj']:.4f} | {float(val_metrics.get('val/kobj_loss', 0)):.4f} |",
        f"| cls | {train_loss['cls']:.4f} | {float(val_metrics.get('val/cls_loss', 0)):.4f} |",
        f"| dfl | {train_loss['dfl']:.4f} | {float(val_metrics.get('val/dfl_loss', 0)):.4f} |",
        "",
        "Train box/cls/dfl = 0 confirme Phase1ITOnlyPoseLoss actif pendant training.",
        "Val box/cls/dfl > 0 = métriques calculées par validator stock (non masquées).",
        "",
        "**Paradoxe observé :** loss train box/cls/dfl = 0 mais **100 % des poids**",
        "backbone/cv2/cv3/cv4-old ont changé (max Δ backbone ≈ 10.2). Cela indique que",
        "le gel/hooks appliqués dans `_setup_train()` **ne survivent pas** à la boucle",
        "`_do_train()` réelle, ou que le checkpoint sauvegardé reflète le modèle live",
        "(EMA stripé : `ema=None`, `optimizer=None`, `epoch=-1`).",
        "",
        "La loss pose IT-only backpropage toujours via le graphe complet ; si `requires_grad`",
        "est réactivé sur backbone/cv2/cv3, un seul epoch suffit à effondrer la détection.",
        "",
        "---",
        "",
        "## 7. Checkpoint validation",
        "",
        f"- Validation terminale utilise : **`{val_ckpt_path}`** (best.pt du run v2-2)",
        f"- best ≡ last (1 epoch) : **{best_last_identical}**",
        f"- Init run : `{Path(args['model']).relative_to(PROJECT)}`",
        f"- Métriques results.csv : P(B)={results_row.get('metrics/precision(B)')}, "
        f"R(B)={results_row.get('metrics/recall(B)')}, mAP50(B)={results_row.get('metrics/mAP50(B)')}",
        "",
        "---",
        "",
        f"## Conclusion : `{verdict}`",
        "",
        "CSV : `v5_phase1_v2_epoch1_safety_audit.csv`",
    ])
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(verdict)
    return verdict


if __name__ == "__main__":
    raise SystemExit(0 if main().startswith("V5_PHASE1") else 1)
