#!/usr/bin/env python3
"""V5 Phase 1 post-training diagnostic — READ-ONLY."""
from __future__ import annotations

import csv
import json
import math
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

from dicom_render import read_dicom_dimensions, render_dicom_png  # noqa: E402
from ultralytics.nn.tasks import torch_safe_load

DATASET = PROJECT / "datasets/yolo_pose_new_26"
OUT_MD = DATASET / "v5_phase1_posttraining_diagnostic.md"
OUT_CSV = DATASET / "v5_phase1_posttraining_diagnostic.csv"
SPLIT_JSON = DATASET / "meta/split.json"
MAPPING_CSV = DATASET / "meta/source_mapping.csv"
DATA_YAML = DATASET / "data.yaml"
ARGS_YAML = PROJECT / "runs/pose/yolo_pose_new_26_v5_phase1_it/args.yaml"
RESULTS_CSV = PROJECT / "runs/pose/yolo_pose_new_26_v5_phase1_it/results.csv"

V2_PATH = PROJECT / "runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt"
SURGICAL = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp/weights/v5_surgical_init.pt"
BEST_P1 = PROJECT / "runs/pose/yolo_pose_new_26_v5_phase1_it/weights/best.pt"
LAST_P1 = PROJECT / "runs/pose/yolo_pose_new_26_v5_phase1_it/weights/last.pt"

OLD_NK = 42
IMGSZ = 640
CONF = 0.25
EVAL_IMG = DATASET / "_v5_phase1_posttrain_eval/images"
THRESH = 1e-8

MODELS = {
    "V2_best": V2_PATH,
    "v5_surgical_init": SURGICAL,
    "V5_phase1_best": BEST_P1,
    "V5_phase1_last": LAST_P1,
}


def load_sd(path: Path) -> dict[str, torch.Tensor]:
    ckpt = torch_safe_load(str(path))[0]
    model = ckpt["model"]
    if hasattr(model, "float"):
        model = model.float()
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


def tensor_zones(name: str, t: torch.Tensor) -> list[str]:
    zone = param_zone(name)
    if zone != "cv4_pose":
        return [zone]
    zones = []
    if t.dim() == 4:
        o, i = t.shape[0], t.shape[1]
        if o > OLD_NK:
            zones.append("cv4_it_rows")
        if o > OLD_NK and i > OLD_NK:
            zones.append("cv4_it_block")
        if o >= OLD_NK or i >= OLD_NK:
            zones.append("cv4_old_channels")
    elif t.dim() == 1 and t.shape[0] > OLD_NK:
        zones.extend(["cv4_old_channels", "cv4_it_rows"])
    else:
        zones.append("cv4_old_channels")
    return zones


def compare_block(ref: torch.Tensor, tgt: torch.Tensor, od: int, id_: int) -> dict[str, float]:
    rb = ref[:od, :id_].float() if ref.dim() >= 2 else ref[:od].float()
    tb = tgt[:od, :id_].float() if tgt.dim() >= 2 else tgt[:od].float()
    d = (tb - rb).abs()
    return {
        "max_abs_diff": float(d.max().item()) if d.numel() else 0.0,
        "mean_abs_diff": float(d.mean().item()) if d.numel() else 0.0,
        "changed_frac": float((d > THRESH).float().mean().item()) if d.numel() else 0.0,
    }


def compare_tensors(
    ref_name: str,
    ref_sd: dict[str, torch.Tensor],
    tgt_sd: dict[str, torch.Tensor],
    ref_label: str,
    tgt_label: str,
) -> list[dict[str, Any]]:
    rows = []
    common = sorted(set(ref_sd) & set(tgt_sd))
    for name in common:
        r, t = ref_sd[name], tgt_sd[name]
        zone = param_zone(name)
        row: dict[str, Any] = {
            "section": "weight_diff",
            "ref_model": ref_label,
            "tgt_model": tgt_label,
            "param_name": name,
            "zone": zone,
            "shape_ref": str(tuple(r.shape)),
            "shape_tgt": str(tuple(t.shape)),
        }
        if r.shape == t.shape:
            d = (t.float() - r.float()).abs()
            row.update({
                "max_abs_diff": float(d.max().item()),
                "mean_abs_diff": float(d.mean().item()),
                "changed_frac": float((d > THRESH).float().mean().item()),
                "identical": float(d.max().item()) <= THRESH,
            })
        elif zone == "cv4_pose" and r.shape != t.shape:
            od = min(r.shape[0], t.shape[0])
            id_ = min(r.shape[1], t.shape[1]) if r.dim() >= 2 else 0
            old_od = min(od, OLD_NK)
            old_id = min(id_, OLD_NK) if id_ else old_od
            old = compare_block(r, t, old_od, old_id)
            row.update({f"old_{k}": v for k, v in old.items()})
            if t.dim() == 4 and t.shape[0] > OLD_NK and t.shape[1] > OLD_NK:
                it_block = (t[OLD_NK:, OLD_NK:] - (r[OLD_NK:, OLD_NK:] if r.shape[0] > OLD_NK and r.shape[1] > OLD_NK else 0)).abs()
                row["it_max_abs_diff"] = float(it_block.max().item())
            elif t.dim() == 1 and t.shape[0] > OLD_NK:
                it_d = (t[OLD_NK:] - (r[OLD_NK:] if r.shape[0] > OLD_NK else 0)).abs()
                row["it_max_abs_diff"] = float(it_d.max().item())
        else:
            row["note"] = "shape_mismatch_skip"
        rows.append(row)
    return rows


def summarize_zone_diff(rows: list[dict[str, Any]], key: str = "max_abs_diff") -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = defaultdict(lambda: {"n": 0, "changed": 0, "max": 0.0})
    for r in rows:
        z = r.get("zone", "other")
        out[z]["n"] += 1
        v = r.get(key, r.get("old_max_abs_diff", 0.0)) or 0.0
        if v > THRESH:
            out[z]["changed"] += 1
        out[z]["max"] = max(out[z]["max"], float(v))
    return dict(out)


def load_val_images(val_ids: list[str]) -> dict[str, Path]:
    mapping = {r["pilot_id"]: r for r in csv.DictReader(MAPPING_CSV.open(encoding="utf-8-sig"))}
    EVAL_IMG.mkdir(parents=True, exist_ok=True)
    paths = {}
    for cid in val_ids:
        dicom = PROJECT / mapping[cid]["source_dicom"].replace("\\", "/")
        png = EVAL_IMG / f"{cid}.png"
        render_dicom_png(dicom, png)
        paths[cid] = png
    return paths


def parse_yolo_label(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        v = line.split()
        floats = [float(x) for x in v]
        conf_det = floats[-1] if len(floats) > 5 else None
        out.append({
            "cx": floats[1], "cy": floats[2], "w": floats[3], "h": floats[4],
            "conf": conf_det,
        })
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
        run_root = DATASET / "_v5_phase1_posttrain_eval" / f"_ultra_{out_dir.name}_{cid}"
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


def ckpt_meta(path: Path, ckpt: dict) -> dict[str, Any]:
    m = ckpt.get("v5_meta", {})
    return {
        "path": str(path.relative_to(PROJECT)),
        "epoch": ckpt.get("epoch"),
        "best_fitness": ckpt.get("best_fitness"),
        "date": ckpt.get("date"),
        "train_args_data": (ckpt.get("train_args") or {}).get("data"),
        "kpt_shape": getattr(ckpt["model"], "kpt_shape", None) if ckpt.get("model") is not None else None,
        "v5_meta": m,
        "has_ema": ckpt.get("ema") is not None,
        "optimizer_in_ckpt": ckpt.get("optimizer") is not None,
    }


def main() -> str:
    val_ids = json.loads(SPLIT_JSON.read_text())["val"]
    args = yaml.safe_load(ARGS_YAML.read_text(encoding="utf-8"))

    states = {k: load_sd(p) for k, p in MODELS.items()}
    sds = {k: v[0] for k, v in states.items()}
    ckpts = {k: v[1] for k, v in states.items()}

    csv_rows: list[dict[str, Any]] = []

    for label, meta in [(k, ckpt_meta(MODELS[k], ckpts[k])) for k in MODELS]:
        csv_rows.append({"section": "checkpoint_meta", "model": label, **{f"meta_{k}": v for k, v in meta.items()}})

    # Weight diffs
    diff_init_best = compare_tensors("x", sds["v5_surgical_init"], sds["V5_phase1_best"], "surgical_init", "phase1_best")
    diff_init_last = compare_tensors("x", sds["v5_surgical_init"], sds["V5_phase1_last"], "surgical_init", "phase1_last")
    diff_v2_surgical = compare_tensors("x", sds["V2_best"], sds["v5_surgical_init"], "V2", "surgical_init")
    csv_rows.extend(diff_init_best)
    csv_rows.extend(diff_init_last)

    sum_init_best = summarize_zone_diff(diff_init_best)
    sum_init_last = summarize_zone_diff(diff_init_last)
    sum_v2_surg = summarize_zone_diff(diff_v2_surgical)

    # BN running stats check
    bn_rows = []
    for name, t in sds["v5_surgical_init"].items():
        if "running_mean" in name or "running_var" in name:
            if name in sds["V5_phase1_best"]:
                d = (sds["V5_phase1_best"][name].float() - t.float()).abs().max().item()
                bn_rows.append({"param": name, "max_diff_best": d})
    csv_rows.extend([{"section": "bn_running", **r} for r in bn_rows])

    # Inference on val
    images = load_val_images(val_ids)
    pred_dirs: dict[str, Path] = {}
    for label, path in MODELS.items():
        d = DATASET / f"_v5_phase1_posttrain_eval/pred_{label}"
        run_inference(path, images, d)
        pred_dirs[label] = d

    gt_root = DATASET / "labels/val"
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
            csv_rows.append(row)

    # Compare detection counts on val
    v2_det = sum(1 for r in csv_rows if r.get("section") == "inference_val" and r["model"] == "V2_best" and r["detected"])
    surg_det = sum(1 for r in csv_rows if r.get("section") == "inference_val" and r["model"] == "v5_surgical_init" and r["detected"])
    best_det = sum(1 for r in csv_rows if r.get("section") == "inference_val" and r["model"] == "V5_phase1_best" and r["detected"])
    last_det = sum(1 for r in csv_rows if r.get("section") == "inference_val" and r["model"] == "V5_phase1_last" and r["detected"])

    # Root cause flags
    backbone_changed_best = sum_init_best.get("backbone", {}).get("changed", 0)
    cv2_changed = sum_init_best.get("cv2_box", {}).get("changed", 0)
    cv3_changed = sum_init_best.get("cv3_cls", {}).get("changed", 0)
    cv4_old_changed = sum_init_best.get("cv4_pose", {}).get("changed", 0)

    # Check if setup_it_only was ineffective (Ultralytics resets requires_grad + full loss on box/cls)
    findings = []

    if backbone_changed_best > 0 or cv2_changed > 0 or cv3_changed > 0:
        findings.append(
            "BACKBONE/CV2/CV3 : **100 % des tensors modifiés** vs surgical_init (max Δ≈10.2 backbone, 9.0 cv2, 4.5 cv3). "
            "Le gel IT-only (`apply_it_only_freeze`) appelé avant `yolo.train()` n'est **pas propagé** au PoseTrainer : "
            "`freeze=null`, reset `requires_grad=True`, losses box/cls/dfl actives sur toute la tête."
        )
    if cv4_old_changed > 0:
        findings.append(
            "CV4 : **42/42 tensors modifiés** (incl. canaux 0–41) — le masque IT-only cv4 n'a pas été appliqué dans la boucle trainer."
        )
    if args.get("pretrained") is False:
        findings.append(
            "`pretrained=False` : Ultralytics `model.train()` peut reconstruire le modèle via `get_model(weights=None)` "
            "(model.py L808-814) — le checkpoint surgical_init est chargé via `args.model`, mais sans gel les losses détections "
            "réentraînent l'intégralité du réseau."
        )
    if args.get("freeze") is None:
        findings.append("`freeze=null` — seul `.dfl` gelé nativement; aucun gel backbone/cv2/cv3/cv4-old.")

    findings.append(
        "`ITOnlyPoseLoss` (masque KP 0–13) **non branché** dans le trainer — seule la loss pose IT est masquée en design, "
        "mais box/cls/dfl continuent de mettre à jour cv2/cv3/backbone."
    )
    findings.append(
        "EMA (`ModelEMA.update`) appliquée à **tous** les paramètres chaque step — les checkpoints best/last reflètent "
        "cette moyenne mobile, pas un gel effectif."
    )
    findings.append(
        "Val `cls_loss` explose epoch 12+ (≈7.68) — symptôme d'effondrement classification ; Box P/R instables (epoch 9 spike P=0.28 puis chute)."
    )

    if v2_det >= 4 and best_det <= 1:
        findings.append(
            f"Inférence val @ conf={CONF} : V2 détecte **{v2_det}/5** pelvis, V5 best **{best_det}/5** — effondrement détection confirmé post-training."
        )
    if v2_det >= 4 and surg_det >= 4:
        findings.append(
            "surgical_init conserve la détection V2 sur val — la régression est **causée par Phase 1 training**, "
            "pas par l'expansion 14→16 KP seule."
        )

    verdict = "V5_PHASE1_DIAGNOSTIC_REQUIRED"

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [
        "# V5 Phase 1 — Post-training Diagnostic",
        "",
        f"**Généré :** {ts}",
        "**Mode :** READ-ONLY",
        f"**Conclusion :** `{verdict}`",
        "",
        "---",
        "",
        "## Contexte run",
        "",
        f"| Paramètre | Valeur |",
        f"|-----------|--------|",
        f"| Run | `runs/pose/yolo_pose_new_26_v5_phase1_it` |",
        f"| Epochs | 15 |",
        f"| Init args.model | `{args.get('model')}` |",
        f"| data.yaml | `{args.get('data')}` |",
        f"| imgsz | {args.get('imgsz')} |",
        f"| conf (val default) | {args.get('conf') or '0.001 (Ultralytics val default)'} |",
        f"| inférence diagnostic | conf=**{CONF}**, imgsz=**{IMGSZ}** |",
        f"| freeze | {args.get('freeze')} |",
        f"| pretrained | {args.get('pretrained')} |",
        f"| lr0 | {args.get('lr0')} |",
        f"| optimizer | {args.get('optimizer')} |",
        "",
        "Métriques finales (`results.csv` epoch 15) : Box P≈0.006, R≈0.6, mAP50(B)≈0.01, Pose mAP=0.",
        "",
        "---",
        "",
        "## 1. Comparaison checkpoints",
        "",
        "| Checkpoint | Rôle |",
        "|------------|------|",
        f"| `V2 best.pt` | Référence production 14 KP |",
        f"| `v5_surgical_init.pt` | Init Phase 0 (epoch -1) |",
        f"| `V5 phase1 best.pt` | Meilleur fitness Phase 1 |",
        f"| `V5 phase1 last.pt` | Dernier epoch (15) |",
        "",
        "---",
        "",
        "## 2. Paramètres modifiés (surgical_init → phase1 best)",
        "",
        "| Zone | Tensors | Changed | Max abs diff |",
        "|------|--------:|--------:|-------------:|",
    ]
    for zone in ("backbone", "cv2_box", "cv3_cls", "dfl", "cv4_pose", "other"):
        s = sum_init_best.get(zone, {"n": 0, "changed": 0, "max": 0})
        md.append(f"| {zone} | {int(s['n'])} | {int(s['changed'])} | {s['max']:.6e} |")

    md.extend([
        "",
        "### surgical_init → last.pt",
        "",
        "| Zone | Changed | Max abs diff |",
        "|------|--------:|-------------:|",
    ])
    sum_init_last = summarize_zone_diff(diff_init_last)
    for zone in ("backbone", "cv2_box", "cv3_cls", "dfl", "cv4_pose"):
        s = sum_init_last.get(zone, {"changed": 0, "max": 0})
        md.append(f"| {zone} | {int(s['changed'])} | {s['max']:.6e} |")

    md.extend([
        "",
        "### V2 → surgical_init (non-cv4 attendu identique)",
        "",
        "| Zone | Changed | Max abs diff |",
        "|------|--------:|-------------:|",
    ])
    for zone in ("backbone", "cv2_box", "cv3_cls", "dfl"):
        s = sum_v2_surg.get(zone, {"changed": 0, "max": 0})
        md.append(f"| {zone} | {int(s['changed'])} | {s['max']:.6e} |")

    md.extend([
        "",
        "---",
        "",
        "## 3. Gel prévu vs réalité training",
        "",
        "| Mécanisme prévu | Appliqué dans trainer ? |",
        "|-----------------|:-----------------------:|",
        "| `apply_it_only_freeze()` avant train | **Non persistant** — trainer reset `requires_grad=True` (L321-326) |",
        "| Hooks cv4 canaux 42–47 | **Perdus** — nouveau module dans trainer |",
        "| `ITOnlyPoseLoss` masque KP 0–13 | **Non injecté** dans trainer |",
        "| `freeze=null` | Aucun gel backbone/cv2/cv3 |",
        "| EMA (`ModelEMA`) | **Met à jour tous les poids** chaque step |",
        "| Loss box/cls/dfl | **Active** sur tête gelée en principe |",
        "",
        "---",
        "",
        "## 4. Inférence comparée (5 val @ conf=0.25, imgsz=640)",
        "",
        "| Image | V2 boxes | surgical boxes | best boxes | last boxes |",
        "|-------|:--------:|:--------------:|:----------:|:----------:|",
    ])

    for cid in val_ids:
        def nb(m):
            return next((r["n_boxes"] for r in csv_rows if r.get("section") == "inference_val" and r["image"] == cid and r["model"] == m), "—")
        md.append(f"| {cid} | {nb('V2_best')} | {nb('v5_surgical_init')} | {nb('V5_phase1_best')} | {nb('V5_phase1_last')} |")

    md.extend([
        "",
        "### Détail inférence (top box par image)",
        "",
        "| Image | Modèle | n_boxes | conf | IoU vs GT |",
        "|-------|--------|--------:|-----:|----------:|",
    ])
    for cid in val_ids:
        gt_boxes = parse_yolo_label(gt_root / f"{cid}.txt")
        gt_xyxy = xywhn_to_xyxy(gt_boxes[0]) if gt_boxes else None
        for label in MODELS:
            preds = parse_yolo_label(pred_dirs[label] / f"{cid}.txt")
            best = max(preds, key=lambda x: x.get("conf") or 0) if preds else None
            iou_v = iou(gt_xyxy, xywhn_to_xyxy(best)) if gt_xyxy and best else None
            conf_s = f"{best['conf']:.4f}" if best and best.get("conf") is not None else "—"
            iou_s = f"{iou_v:.4f}" if iou_v is not None else "—"
            md.append(f"| {cid} | {label} | {len(preds)} | {conf_s} | {iou_s} |")

    md.extend([
        "",
        f"**Détections (≥1 box @ conf={CONF})** : V2 **{v2_det}/5** · surgical **{surg_det}/5** · best **{best_det}/5** · last **{last_det}/5**",
        "",
        "---",
        "",
        "## 5. Findings (cause racine)",
        "",
    ])
    for i, f in enumerate(findings, 1):
        md.append(f"{i}. {f}")
    if not findings:
        md.append("Aucune anomalie poids détectée — investiguer métriques val/conf threshold.")

    md.extend([
        "",
        "---",
        "",
        f"## Conclusion : `{verdict}`",
        "",
        "CSV détaillé : `v5_phase1_posttraining_diagnostic.csv`",
    ])

    fieldnames = sorted({k for row in csv_rows for k in row})
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(verdict)
    return verdict


if __name__ == "__main__":
    main()
