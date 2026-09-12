#!/usr/bin/env python3
"""V5 Phase 0 — surgical initialization + epoch-0 parity test (NO training)."""
from __future__ import annotations

import csv
import hashlib
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
import torch.nn as nn

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))
TOOL_DIR = PROJECT / "annotation_pilot" / "manual_annotation_tool"
sys.path.insert(0, str(TOOL_DIR))

from dicom_render import read_dicom_dimensions, render_dicom_png  # noqa: E402

from ultralytics.data.utils import check_det_dataset
from ultralytics.nn.tasks import PoseModel, torch_safe_load

V2_PATH = PROJECT / "runs/pose/runs/pose/runs/yolo_pose_new_26_v2-3/weights/best.pt"
DATA_YAML = PROJECT / "datasets/yolo_pose_new_26/data.yaml"
DATASET = PROJECT / "datasets/yolo_pose_new_26"
V5_RUN = PROJECT / "runs/pose/yolo_pose_new_26_v5_16kp"
V5_WEIGHTS = V5_RUN / "weights" / "v5_surgical_init.pt"
OUT_MD = DATASET / "v5_surgical_init_report.md"
OUT_CSV = DATASET / "v5_surgical_init_report.csv"

MAPPING_CSV = DATASET / "meta" / "source_mapping.csv"
SPLIT_JSON = DATASET / "meta" / "split.json"
LABELS_GT = DATASET / "labels"
EVAL_ROOT = DATASET / "_v5_phase0_eval_temp"
IMAGES_DIR = EVAL_ROOT / "images"
V2_PRED = EVAL_ROOT / "pred_v2" / "labels"
V5_PRED = EVAL_ROOT / "pred_v5" / "labels"

LANDMARKS_16 = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L", "ASM_R", "ASM_L",
    "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L", "IT_R", "IT_L",
]
LANDMARKS_14 = LANDMARKS_16[:14]
OLD_NK = 42
NEW_NK = 48
OLD_KP = 14
CONF_THRESHOLD = 0.25
IMGSZ = 640
KEYPOINTS_START = 5
GO_MEAN_PX = 150.0
CATASTROPHIC_RATIO = 3.0


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmt(v: Any, d: int = 2) -> str:
    if v is None or v == "":
        return ""
    if isinstance(v, float):
        return f"{v:.{d}f}"
    return str(v)


def verdict_px(err: float | None) -> str:
    if err is None:
        return "NA"
    if err <= 75:
        return "CORRECT"
    if err <= 149:
        return "INCERTAIN"
    return "INCORRECT"


def load_v2_model() -> tuple[Any, dict[str, torch.Tensor]]:
    ckpt = torch_safe_load(str(V2_PATH))[0]
    model = ckpt["model"].float()
    return model, model.state_dict()


def build_v5_model() -> tuple[PoseModel, dict[str, Any]]:
    ds = check_det_dataset(str(DATA_YAML))
    model = PoseModel(
        "yolo11n-pose.yaml",
        nc=ds["nc"],
        ch=ds.get("channels", 3),
        data_kpt_shape=ds["kpt_shape"],
        verbose=False,
    )
    return model, ds


def inspect_cv4_params(v2_sd: dict[str, torch.Tensor], v5_sd: dict[str, torch.Tensor]) -> list[dict]:
    rows = []
    for name in sorted(v5_sd):
        if "cv4" not in name:
            continue
        s2 = tuple(v2_sd[name].shape) if name in v2_sd else None
        s5 = tuple(v5_sd[name].shape)
        zone = ""
        if s2 and s2 != s5:
            if len(s5) == 4 and s5[0] > (s2[0] if s2 else 0):
                zone = f"rows 0:{s2[0]} <- V2; rows {s2[0]}:{s5[0]} <- IT init"
            elif len(s5) == 4 and s5[1] > (s2[1] if s2 else 0):
                zone = f"cols 0:{s2[1]} <- V2; cols {s2[1]}:{s5[1]} <- zero/IT"
            elif len(s5) == 2 and s5[0] > (s2[0] if s2 else 0):
                zone = f"rows 0:{s2[0]} <- V2; rows {s2[0]}:{s5[0]} <- IT init"
            elif len(s5) == 1 and s5[0] > (s2[0] if s2 else 0):
                zone = f"[0:{s2[0]}] <- V2; [{s2[0]}:{s5[0]}] <- IT init"
            else:
                zone = "shape mismatch"
        elif s2 == s5:
            zone = "full copy"
        rows.append({
            "param_name": name,
            "shape_v2": str(s2) if s2 else "MISSING",
            "shape_v5": str(s5),
            "kp_zone_old": "flat 0-41 (14 KP)",
            "kp_zone_it": "flat 42-47 (IT_R/IT_L)",
            "copy_zone": zone,
        })
    return rows


def surgical_copy_cv4(v2_sd: dict[str, torch.Tensor], v5_model: PoseModel) -> list[dict]:
    """Copy V2 cv4 weights into V5 16-KP tensors; IT channels zero in hidden, kaiming on final out only."""
    v5_sd = v5_model.state_dict()
    log: list[dict] = []

    for name, dst in v5_sd.items():
        if "cv4" not in name or name not in v2_sd:
            continue
        src = v2_sd[name]
        is_final_out = name.endswith(".2.weight") or (name.endswith(".2.bias") and "cv4" in name)

        if src.shape == dst.shape:
            dst.copy_(src)
            log.append({
                "v2_tensor": name, "v5_tensor": name,
                "shape_source": str(tuple(src.shape)),
                "shape_dest": str(tuple(dst.shape)),
                "zone_copied": "full tensor",
                "values_copied": src.numel(),
            })
            continue

        od = min(src.shape[0], dst.shape[0])
        id_ = min(src.shape[1], dst.shape[1]) if src.dim() >= 2 else 0
        dst.zero_()

        if src.dim() == 4:
            dst[:od, :id_].copy_(src[:od, :id_])
            if is_final_out and dst.shape[0] > od and dst.shape[1] > od:
                nn.init.kaiming_uniform_(dst[od:, od:], a=math.sqrt(5))
            zone = f"block [:,{od},:,{id_}] <- V2; hidden expansion ZERO; IT kaiming on final only"
        elif src.dim() == 2:
            dst[:od, :id_].copy_(src[:od, :id_])
            if is_final_out and dst.shape[0] > od and dst.shape[1] > od:
                nn.init.kaiming_uniform_(dst[od:, od:], a=math.sqrt(5))
            zone = f"block [:,{od},:,{id_}] <- V2; hidden expansion ZERO; IT kaiming on final only"
        elif src.dim() == 1:
            dst[:od].copy_(src[:od])
            zone = f"[:{od}] <- V2; [{od}:] <- zero"
        else:
            continue

        log.append({
            "v2_tensor": name, "v5_tensor": name,
            "shape_source": str(tuple(src.shape)),
            "shape_dest": str(tuple(dst.shape)),
            "zone_copied": zone,
            "values_copied": int(src[:od].numel() if src.dim() == 1 else src[:od, :id_].numel()),
        })

    v5_model.load_state_dict(v5_sd)
    return log


def copy_non_cv4(v2_model: Any, v5_model: PoseModel) -> int:
    """Copy all matching non-cv4 weights from V2."""
    v5_model.load(v2_model)
    matched = 0
    v2_sd = v2_model.state_dict()
    v5_sd = v5_model.state_dict()
    for k in v5_sd:
        if "cv4" in k:
            continue
        if k in v2_sd and v2_sd[k].shape == v5_sd[k].shape:
            matched += 1
    return matched


def verify_surgery(v2_sd: dict[str, torch.Tensor], v5_sd: dict[str, torch.Tensor]) -> dict:
    copied_vals = 0
    diff_vals = 0
    max_diff = 0.0
    diffs: list[float] = []

    for name, src in v2_sd.items():
        if "cv4" not in name or name not in v5_sd:
            continue
        dst = v5_sd[name]
        if src.shape == dst.shape:
            d = (dst - src).abs()
            copied_vals += d.numel()
            nz = (d > 0).sum().item()
            diff_vals += nz
            max_diff = max(max_diff, d.max().item())
            diffs.extend(d.flatten().tolist())
        else:
            od = min(src.shape[0], dst.shape[0])
            id_ = min(src.shape[1], dst.shape[1]) if src.dim() >= 2 else 0
            if src.dim() == 4:
                block = dst[:od, :id_]
                ref = src[:od, :id_]
            elif src.dim() == 2:
                block = dst[:od, :id_]
                ref = src[:od, :id_]
            elif src.dim() == 1:
                block = dst[:od]
                ref = src[:od]
            else:
                continue
            d = (block - ref).abs()
            copied_vals += d.numel()
            nz = (d > 1e-8).sum().item()
            diff_vals += nz
            max_diff = max(max_diff, d.max().item())
            diffs.extend(d.flatten().tolist())

    mean_diff = statistics.mean(diffs) if diffs else 0.0
    return {
        "values_copied": copied_vals,
        "values_different": diff_vals,
        "max_abs_diff": max_diff,
        "mean_abs_diff": mean_diff,
        "identical_zones": diff_vals == 0,
    }


def finalize_v5_model(v5_model: PoseModel, v2_model: Any, ds: dict[str, Any]) -> None:
    """Attach Ultralytics metadata required for inference (names, yaml, kpt_shape)."""
    kpt_shape = list(ds["kpt_shape"])
    v5_model.names = dict(getattr(v2_model, "names", {0: "pelvis"}))
    v5_model.kpt_shape = kpt_shape
    v5_model.kpt_names = {0: list(LANDMARKS_16)}
    yaml_cfg = dict(getattr(v2_model, "yaml", {}) or {})
    yaml_cfg["nc"] = ds["nc"]
    yaml_cfg["kpt_shape"] = kpt_shape
    v5_model.yaml = yaml_cfg
    v5_model.model[-1].kpt_shape = tuple(kpt_shape)
    v5_model.model[-1].nk = kpt_shape[0] * kpt_shape[1]


def save_v5_checkpoint(
    v5_model: PoseModel,
    v2_model: Any,
    v2_ckpt: dict,
    ds: dict[str, Any],
    copy_log: list[dict],
    verify: dict,
) -> None:
    V5_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
    finalize_v5_model(v5_model, v2_model, ds)
    meta = {
        "description": "V5 Phase 0 surgical init — 16 KP from V2 14 KP",
        "source_v2": str(V2_PATH.relative_to(PROJECT)),
        "source_sha256": sha256_file(V2_PATH),
        "surgery": "cv4 block copy 42->48; hidden IT channels ZERO; final conv IT kaiming",
        "training": "NONE — phase 0 only",
        "verify": verify,
        "copy_ops": len(copy_log),
    }
    ckpt = dict(v2_ckpt)
    ckpt["model"] = v5_model
    ckpt["ema"] = None
    ckpt["epoch"] = -1
    ckpt["best_fitness"] = None
    ckpt["date"] = datetime.now(timezone.utc).isoformat()
    ckpt["v5_meta"] = meta
    train_args = dict(ckpt.get("train_args") or {})
    train_args["data"] = str(DATA_YAML)
    ckpt["train_args"] = train_args
    torch.save(ckpt, V5_WEIGHTS)


def load_predict_model(model_path: Path):
    from ultralytics import YOLO

    return YOLO(str(model_path))


def run_predict(model_path: Path, out_labels: Path) -> None:
    out_labels.mkdir(parents=True, exist_ok=True)
    run_dir = out_labels.parent / "_ultra_run"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    model = load_predict_model(model_path)
    model.predict(
        source=str(IMAGES_DIR),
        imgsz=IMGSZ,
        conf=CONF_THRESHOLD,
        save=False,
        save_txt=True,
        save_conf=True,
        project=str(out_labels.parent),
        name="_ultra_run",
        exist_ok=True,
        verbose=False,
    )
    raw = run_dir / "labels"
    for src in raw.glob("*.txt"):
        shutil.copy2(src, out_labels / src.name)
    shutil.rmtree(run_dir, ignore_errors=True)


def load_cases() -> list[dict[str, str]]:
    with MAPPING_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: r["pilot_id"])
    return rows


def gt_label_path(case_id: str, train_ids: set[str]) -> Path:
    split = "train" if case_id in train_ids else "val"
    return LABELS_GT / split / f"{case_id}.txt"


def parse_gt(path: Path, w: float, h: float) -> dict[str, dict]:
    vals = [float(x) for x in path.read_text(encoding="utf-8").split()]
    kpts = vals[KEYPOINTS_START:]
    out = {}
    for i, name in enumerate(LANDMARKS_16):
        x_n, y_n, v = kpts[i * 3], kpts[i * 3 + 1], kpts[i * 3 + 2]
        visible = v >= 2 and not (x_n == 0 and y_n == 0)
        out[name] = {
            "x": x_n * w if visible else None,
            "y": y_n * h if visible else None,
            "v": int(v),
            "evaluable": visible,
        }
    return out


def parse_pred(path: Path | None, w: float, h: float, n_kpt: int) -> dict | None:
    if path is None or not path.is_file():
        return None
    line = path.read_text(encoding="utf-8").strip()
    if not line:
        return None
    vals = line.split()
    expected_kpt_cols = n_kpt * 3
    has_det_conf = len(vals) == KEYPOINTS_START + expected_kpt_cols + 1
    kpt_end = -1 if has_det_conf else None
    det_conf = float(vals[-1]) if has_det_conf else None
    kpts = [float(v) for v in vals[KEYPOINTS_START:kpt_end]]
    names = LANDMARKS_16 if n_kpt == 16 else LANDMARKS_14
    lm = {}
    for i, name in enumerate(names):
        x_n, y_n, c = kpts[i * 3], kpts[i * 3 + 1], kpts[i * 3 + 2]
        usable = c >= CONF_THRESHOLD
        lm[name] = {"x": x_n * w if usable else None, "y": y_n * h if usable else None, "conf": c}
    return {"landmarks": lm, "det_conf": det_conf}


def pixel_error(gt: dict, pred: dict | None, name: str) -> float | None:
    if not gt.get("evaluable") or pred is None:
        return None
    pl = pred["landmarks"].get(name)
    if pl is None or pl["x"] is None:
        return None
    return math.hypot(pl["x"] - gt["x"], pl["y"] - gt["y"])


def stats(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "mean": None, "median": None, "p90": None, "min": None, "max": None}
    s = sorted(values)
    n = len(s)
    p90_i = min(n - 1, math.ceil(0.9 * n) - 1)
    return {
        "n": n,
        "mean": statistics.mean(s),
        "median": statistics.median(s),
        "p90": s[p90_i],
        "min": s[0],
        "max": s[-1],
    }


def tier_counts(values: list[float]) -> dict[str, int]:
    c = {"CORRECT": 0, "INCERTAIN": 0, "INCORRECT": 0}
    for v in values:
        c[verdict_px(v)] += 1
    return c


def run_parity_test() -> dict:
    split = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))
    train_ids = set(split["train"])
    cases = load_cases()

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    dims: dict[str, tuple[float, float]] = {}
    for row in cases:
        cid = row["pilot_id"]
        dicom = PROJECT / row["source_dicom"].replace("\\", "/")
        png = IMAGES_DIR / f"{cid}.png"
        w, h = read_dicom_dimensions(dicom)
        render_dicom_png(dicom, png)
        dims[cid] = (w, h)

    print(f"V2 inference imgsz={IMGSZ} conf={CONF_THRESHOLD}...")
    run_predict(V2_PATH, V2_PRED)
    print(f"V5 inference imgsz={IMGSZ} conf={CONF_THRESHOLD}...")
    run_predict(V5_WEIGHTS, V5_PRED)

    errors_v2: dict[str, list[float]] = defaultdict(list)
    errors_v5: dict[str, list[float]] = defaultdict(list)
    csv_rows: list[dict] = []
    det_v2 = det_v5 = 0

    for row in cases:
        cid = row["pilot_id"]
        w, h = dims[cid]
        gt = parse_gt(gt_label_path(cid, train_ids), w, h)
        p2 = parse_pred(V2_PRED / f"{cid}.txt", w, h, 14)
        p5 = parse_pred(V5_PRED / f"{cid}.txt", w, h, 16)
        det_v2 += int(p2 is not None)
        det_v5 += int(p5 is not None)

        for name in LANDMARKS_16:
            e2 = pixel_error(gt[name], p2, name) if name in LANDMARKS_14 else None
            e5 = pixel_error(gt[name], p5, name)
            if e2 is not None:
                errors_v2[name].append(e2)
            if e5 is not None and name in LANDMARKS_14:
                errors_v5[name].append(e5)
            if name in ("IT_R", "IT_L") and e5 is not None:
                errors_v5[name].append(e5)

            pl2 = p2["landmarks"].get(name) if p2 and name in LANDMARKS_14 else None
            pl5 = p5["landmarks"].get(name) if p5 else None
            csv_rows.append({
                "section": "landmark",
                "image": cid,
                "landmark": name,
                "GT_v": str(gt[name]["v"]),
                "error_V2": fmt(e2),
                "error_V5": fmt(e5 if name in LANDMARKS_14 else e5),
                "verdict_V2": verdict_px(e2),
                "verdict_V5_14kp": verdict_px(e5 if name in LANDMARKS_14 else None),
                "verdict_V5_it": verdict_px(e5) if name in ("IT_R", "IT_L") else "",
                "delta_V5_minus_V2": fmt(e5 - e2) if e2 is not None and e5 is not None and name in LANDMARKS_14 else "",
            })

    all_v2 = [e for lm in LANDMARKS_14 for e in errors_v2[lm]]
    all_v5_14 = [e for lm in LANDMARKS_14 for e in errors_v5[lm]]
    st_v2 = stats(all_v2)
    st_v5 = stats(all_v5_14)
    t2, t5 = tier_counts(all_v2), tier_counts(all_v5_14)

    per_lm = {}
    for lm in LANDMARKS_14:
        m2 = statistics.mean(errors_v2[lm]) if errors_v2[lm] else None
        m5 = statistics.mean(errors_v5[lm]) if errors_v5[lm] else None
        per_lm[lm] = {"v2_mean": m2, "v5_mean": m5, "delta": (m5 - m2) if m2 and m5 else None}

    catastrophic = [
        lm for lm, v in per_lm.items()
        if v["v2_mean"] and v["v5_mean"] and v["v5_mean"] > v["v2_mean"] * CATASTROPHIC_RATIO
    ]

    go = (
        st_v5["mean"] is not None
        and st_v5["mean"] <= GO_MEAN_PX
        and len(catastrophic) == 0
        and det_v5 >= det_v2
    )

    it_errors = errors_v5["IT_R"] + errors_v5["IT_L"]
    it_st = stats(it_errors)

    return {
        "csv_rows": csv_rows,
        "st_v2": st_v2,
        "st_v5_14": st_v5,
        "tiers_v2": t2,
        "tiers_v5": t5,
        "per_lm": per_lm,
        "catastrophic": catastrophic,
        "det_v2": det_v2,
        "det_v5": det_v5,
        "go": go,
        "it_st": it_st,
        "it_errors": it_errors,
        "it_tiers": tier_counts(it_errors),
    }


def main() -> int:
    if not V2_PATH.is_file():
        raise SystemExit(f"V2 checkpoint missing: {V2_PATH}")

    v2_ckpt_raw = torch.load(V2_PATH, map_location="cpu", weights_only=False)
    v2_model, v2_sd = load_v2_model()
    v5_model, ds = build_v5_model()
    v5_sd_before = {k: v.clone() for k, v in v5_model.state_dict().items()}

    arch_rows = inspect_cv4_params(v2_sd, v5_model.state_dict())
    non_cv4_matched = copy_non_cv4(v2_model, v5_model)
    copy_log = surgical_copy_cv4(v2_sd, v5_model)
    verify = verify_surgery(v2_sd, v5_model.state_dict())

    save_v5_checkpoint(v5_model, v2_model, v2_ckpt_raw, ds, copy_log, verify)
    parity = run_parity_test()

    verdict = "V5_PHASE0_GO" if parity["go"] else "V5_PHASE0_NO_GO"
    now = datetime.now(timezone.utc).isoformat()

    # CSV report
    csv_out: list[dict] = []
    for r in arch_rows:
        csv_out.append({"section": "architecture", **r})
    for r in copy_log:
        csv_out.append({"section": "surgical_copy", **r})
    csv_out.append({"section": "verification", "metric": "values_copied", "value": verify["values_copied"]})
    csv_out.append({"section": "verification", "metric": "values_different", "value": verify["values_different"]})
    csv_out.append({"section": "verification", "metric": "max_abs_diff", "value": verify["max_abs_diff"]})
    csv_out.append({"section": "verification", "metric": "mean_abs_diff", "value": verify["mean_abs_diff"]})
    csv_out.append({"section": "verification", "metric": "identical_zones", "value": verify["identical_zones"]})
    csv_out.append({
        "section": "it_init",
        "metric": "method",
        "value": "Hidden cv4 expansion ZERO; final conv2 IT rows 42-47 Kaiming; bias IT=0",
    })
    for lm in LANDMARKS_14:
        p = parity["per_lm"][lm]
        csv_out.append({
            "section": "parity_14kp",
            "landmark": lm,
            "v2_mean_px": fmt(p["v2_mean"]),
            "v5_mean_px": fmt(p["v5_mean"]),
            "delta_px": fmt(p["delta"]),
        })
    csv_out.append({"section": "parity_global", "metric": "v2_mean_px", "value": fmt(parity["st_v2"]["mean"])})
    csv_out.append({"section": "parity_global", "metric": "v5_mean_px", "value": fmt(parity["st_v5_14"]["mean"])})
    csv_out.append({"section": "parity_global", "metric": "v5_median_px", "value": fmt(parity["st_v5_14"]["median"])})
    csv_out.append({"section": "parity_global", "metric": "v5_p90_px", "value": fmt(parity["st_v5_14"]["p90"])})
    csv_out.append({"section": "parity_global", "metric": "go_threshold_px", "value": GO_MEAN_PX})
    csv_out.append({"section": "parity_global", "metric": "verdict", "value": verdict})
    for r in parity["csv_rows"]:
        csv_out.append({"section": "parity_detail", **r})

    fieldnames = sorted({k for row in csv_out for k in row})
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(csv_out)

    md = [
        "# V5 Phase 0 — Surgical Initialization + Epoch-0 Parity Test",
        "",
        f"**Généré :** {now}",
        "**Mode :** inference / validation ONLY — **aucun entraînement** (`model.train()` non appelé)",
        "",
        f"**V2 source :** `{V2_PATH.relative_to(PROJECT)}`",
        f"**SHA256 V2 :** `{sha256_file(V2_PATH)}`",
        f"**V5 checkpoint :** `{V5_WEIGHTS.relative_to(PROJECT)}`",
        "",
        "---",
        "",
        "## 1. Inspection architecture",
        "",
        f"| Paramètre | V2 | V5 |",
        f"|-----------|----|----|",
        f"| kpt_shape | `{list(v2_model.model[-1].kpt_shape)}` | `{list(v5_model.state_dict() and ds['kpt_shape'])}` |",
        f"| nk (canaux plats) | **{OLD_NK}** | **{NEW_NK}** |",
        f"| KP 0–13 (V2) | flat **0–41** | flat **0–41** (identique) |",
        f"| IT_R / IT_L | N/A | flat **42–47** (indices KP 14–15) |",
        f"| cv4 tensors | 36 | 36 |",
        f"| non-cv4 matched | — | **{non_cv4_matched}** |",
        "",
        "### Tensors cv4 (échantillon)",
        "",
        "| Paramètre | Shape V2 | Shape V5 | Zone copiée |",
        "|-----------|----------|----------|-------------|",
    ]
    for r in arch_rows[:12]:
        md.append(f"| `{r['param_name']}` | {r['shape_v2']} | {r['shape_v5']} | {r['copy_zone']} |")
    if len(arch_rows) > 12:
        md.append(f"| … | … | … | *{len(arch_rows) - 12} tensors cv4 supplémentaires* |")

    md.extend([
        "",
        "---",
        "",
        "## 2. Surgical copy",
        "",
        f"**Opérations documentées :** {len(copy_log)}",
        "",
        "Stratégie :",
        "- Backbone + cv2 + cv3 : copie Ultralytics `intersect_dicts` (shapes identiques)",
        "- cv4 : bloc supérieur/gauche V2 (42×42) copié ; expansion IT initialisée séparément",
        "",
        "| V2 tensor | V5 tensor | Shape source → dest | Zone copiée |",
        "|-----------|-----------|---------------------|-------------|",
    ])
    for r in copy_log[:15]:
        md.append(
            f"| `{r['v2_tensor']}` | `{r['v5_tensor']}` | {r['shape_source']} → {r['shape_dest']} | {r['zone_copied']} |"
        )
    if len(copy_log) > 15:
        md.append(f"| … | … | … | *{len(copy_log)-15} ops supplémentaires — voir CSV* |")

    md.extend([
        "",
        "---",
        "",
        "## 3. Vérification numérique (zones V2 copiées)",
        "",
        f"| Métrique | Valeur |",
        f"|----------|-------:|",
        f"| Valeurs copiées (zones V2) | {verify['values_copied']} |",
        f"| Valeurs différentes | {verify['values_different']} |",
        f"| Max abs diff | {verify['max_abs_diff']:.2e} |",
        f"| Mean abs diff | {verify['mean_abs_diff']:.2e} |",
        f"| Zones identiques (tol 0) | {'Oui' if verify['identical_zones'] else 'Non'} |",
        "",
        "---",
        "",
        "## 4. Initialisation IT_R / IT_L",
        "",
        "| Canal | Init | Justification |",
        "|-------|------|---------------|",
        "| cv4 expansion rows 42–47 (conv0/conv1) | **Zéro** | Pas de signal caché IT → preserve 14 KP |",
        "| cv4 final conv rows 42–47 | **Kaiming uniform** | Init IT output uniquement |",
        "| bias IT | **Zéro** | Neutre à epoch 0 |",
        "",
        "**Aucune valeur des 14 KP V2 réutilisée pour IT.**",
        "",
        "---",
        "",
        "## 5. Epoch-0 parity test (14 KP)",
        "",
        f"Protocole identique à `v4_vs_v2_anatomical_evaluation` : imgsz={IMGSZ}, conf={CONF_THRESHOLD}, 26 DICOM, GT v≥2.",
        "",
        "### Global 14 KP",
        "",
        "| Métrique | V2 | V5 (14 KP) |",
        "|----------|---:|----------:|",
    ])
    for k in ("n", "mean", "median", "p90", "min", "max"):
        md.append(
            f"| {k} | {fmt(parity['st_v2'][k]) if k != 'n' else parity['st_v2']['n']} | "
            f"{fmt(parity['st_v5_14'][k]) if k != 'n' else parity['st_v5_14']['n']} |"
        )
    md.extend([
        "",
        f"**Tiers V2 :** CORRECT={parity['tiers_v2']['CORRECT']} INCERTAIN={parity['tiers_v2']['INCERTAIN']} INCORRECT={parity['tiers_v2']['INCORRECT']}",
        f"**Tiers V5 (14 KP) :** CORRECT={parity['tiers_v5']['CORRECT']} INCERTAIN={parity['tiers_v5']['INCERTAIN']} INCORRECT={parity['tiers_v5']['INCORRECT']}",
        "",
        "### Par landmark (mean px)",
        "",
        "| Landmark | V2 | V5 | Δ |",
        "|----------|---:|---:|--:|",
    ])
    for lm in LANDMARKS_14:
        p = parity["per_lm"][lm]
        md.append(f"| {lm} | {fmt(p['v2_mean'])} | {fmt(p['v5_mean'])} | {fmt(p['delta'])} |")

    md.extend([
        "",
        f"**Détection :** V2={parity['det_v2']}/26 · V5={parity['det_v5']}/26",
        "",
        "---",
        "",
        "## 6. Critère GO / NO-GO",
        "",
        f"| Critère | Seuil | Résultat | Pass |",
        f"|---------|-------|----------|:----:|",
        f"| Mean error 14 KP V5 | ≤ {GO_MEAN_PX} px | {fmt(parity['st_v5_14']['mean'])} px | {'✓' if parity['st_v5_14']['mean'] and parity['st_v5_14']['mean'] <= GO_MEAN_PX else '✗'} |",
        f"| Dégradation catastrophique | aucune (>×{CATASTROPHIC_RATIO} V2) | {', '.join(parity['catastrophic']) or 'aucune'} | {'✓' if not parity['catastrophic'] else '✗'} |",
        f"| Détection | V5 ≥ V2 | {parity['det_v5']} ≥ {parity['det_v2']} | {'✓' if parity['det_v5'] >= parity['det_v2'] else '✗'} |",
        "",
        "---",
        "",
        "## 7. IT (informatif — hors critère parité)",
        "",
        f"| Métrique | IT pooled (n={len(parity['it_errors'])}) |",
        f"|----------|------:|",
        f"| mean px | {fmt(parity['it_st']['mean'])} |",
        f"| median px | {fmt(parity['it_st']['median'])} |",
        f"| % CORRECT | {100 * parity['it_tiers']['CORRECT'] / max(1, len(parity['it_errors'])):.1f}% |",
        "",
        "*IT non évalué pour GO/NO-GO — canaux non issus de V2.*",
        "",
        "---",
        "",
        "## 8. Intégrité",
        "",
        "| Zone | Modifié |",
        "|------|:-------:|",
        "| V2 best.pt | **Non** |",
        "| V4 | **Non** |",
        "| Labels / dataset | **Non** |",
        "| Entraînement | **Non** |",
        "",
        "---",
        "",
        "## Conclusion",
        "",
        f"**`{verdict}`**",
        "",
    ])
    if verdict == "V5_PHASE0_GO":
        md.append("Parité epoch-0 validée. **Phase 1 non lancée** — validation humaine requise avant IT-only fine-tuning.")
    else:
        md.append("Parité epoch-0 **non validée**. Ne pas préparer Phase 1. Corriger la chirurgie cv4 ou investiguer cross-talk.")
    md.append("")
    md.append(f"CSV : `{OUT_CSV.name}`")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"VERDICT={verdict}")
    print(f"V2 mean={parity['st_v2']['mean']:.2f}px V5 mean={parity['st_v5_14']['mean']:.2f}px")
    print(f"MD={OUT_MD}")
    print(f"CSV={OUT_CSV}")
    print(f"CKPT={V5_WEIGHTS}")
    return 0 if parity["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
