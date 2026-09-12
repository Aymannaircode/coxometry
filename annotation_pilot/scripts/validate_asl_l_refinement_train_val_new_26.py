#!/usr/bin/env python3
"""Validation stricte TRAIN→VAL du refinement C_asm_offset ASL_L (new_26).

Calibrage : vecteur GT ASM_L→ASL_L moyen sur 21 TRAIN uniquement.
Application : 5 VAL sans aucune fuite (GT VAL sert uniquement à l'évaluation).

Lecture seule — ne modifie ni poids, labels, annotations, prédictions V2, ni mvp_geometry.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mvp_geometry import compute_all_sides  # noqa: E402
from mvp_geometry.hip_measures import SideResult  # noqa: E402
from mvp_geometry.landmarks import Landmark, landmarks_by_name, load_pilot_schema  # noqa: E402
from mvp_geometry.yolo_adapter import landmarks_from_yolo_label  # noqa: E402

ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
SPLIT_JSON = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "meta" / "split.json"
LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "asl_l_refinement_train_val.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "asl_l_refinement_train_val.md"

TONNIS_EXTREME_ABS = 150.0
CCD_TOLERANCE = 1e-4


@dataclass
class ValCaseResult:
    case_id: str
    asl_l_error_v2: float
    asl_l_error_refined: float
    vce_l_v2: float | None
    vce_l_refined: float | None
    vce_l_gt: float | None
    tonnis_l_v2: float | None
    tonnis_l_refined: float | None
    tonnis_l_gt: float | None
    vce_r_v2: float | None
    vce_r_refined: float | None
    tonnis_r_v2: float | None
    tonnis_r_refined: float | None
    ccd_r_v2: float | None
    ccd_r_refined: float | None
    ccd_l_v2: float | None
    ccd_l_refined: float | None


def format_num(v: float | None, d: int = 2) -> str:
    return "NA" if v is None else f"{v:.{d}f}"


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def load_split() -> tuple[list[str], list[str]]:
    data = json.loads(SPLIT_JSON.read_text(encoding="utf-8"))
    train_ids = sorted(data["train"])
    val_ids = sorted(data["val"])
    if len(train_ids) != 21 or len(val_ids) != 5:
        raise RuntimeError(f"Split inattendu : train={len(train_ids)}, val={len(val_ids)}")
    return train_ids, val_ids


def read_image_size(case_id: str) -> tuple[float, float]:
    from PIL import Image

    with Image.open(IMAGE_DIR / f"{case_id}.png") as img:
        return float(img.size[0]), float(img.size[1])


def gt_asm_asl_offset(case_id: str) -> tuple[float, float]:
    """Offset GT ASM_L→ASL_L — utilisé UNIQUEMENT pour calibrage TRAIN."""
    gt = landmarks_by_name(load_pilot_schema(ANNOT_DIR / f"{case_id}.json"))
    asm, asl = gt["ASM_L"], gt["ASL_L"]
    if not asm.usable or not asl.usable:
        raise ValueError(f"{case_id} : GT ASM_L ou ASL_L non exploitable.")
    return float(asl.x) - float(asm.x), float(asl.y) - float(asm.y)


def calibrate_from_train(train_ids: list[str]) -> tuple[float, float, dict]:
    offsets = [gt_asm_asl_offset(cid) for cid in train_ids]
    off_x = statistics.mean(o[0] for o in offsets)
    off_y = statistics.mean(o[1] for o in offsets)
    meta = {
        "train_cases": train_ids,
        "n_train": len(train_ids),
        "offset_x_mean": off_x,
        "offset_y_mean": off_y,
        "offset_x_stdev": statistics.stdev(o[0] for o in offsets) if len(offsets) >= 2 else 0.0,
        "offset_y_stdev": statistics.stdev(o[1] for o in offsets) if len(offsets) >= 2 else 0.0,
    }
    return off_x, off_y, meta


def apply_refinement(v2_landmarks: dict[str, Landmark], off_x: float, off_y: float) -> dict[str, Landmark]:
    asm = v2_landmarks["ASM_L"]
    if not asm.usable or asm.x is None or asm.y is None:
        raise ValueError("V2 ASM_L non exploitable.")
    refined = dict(v2_landmarks)
    asl = v2_landmarks["ASL_L"]
    refined["ASL_L"] = replace(asl, x=round(asm.x + off_x, 2), y=round(asm.y + off_y, 2), v=2)
    return refined


def side_value(sides: dict[str, SideResult], measure: str, side: str) -> float | None:
    m = getattr(sides[side], measure.lower())
    return m.value_deg if m.available else None


def is_tonnis_extreme(v: float | None) -> bool:
    if v is None:
        return False
    return abs(v) > TONNIS_EXTREME_ABS or v < -15 or v > 165


def abs_err(pred: float | None, gt: float | None) -> float | None:
    if pred is None or gt is None:
        return None
    return abs(pred - gt)


def evaluate_val_case(case_id: str, off_x: float, off_y: float) -> ValCaseResult:
    w, h = read_image_size(case_id)
    gt_lm = landmarks_by_name(load_pilot_schema(ANNOT_DIR / f"{case_id}.json"))
    v2_lm = landmarks_from_yolo_label(LABEL_DIR / f"{case_id}.txt", w, h)
    ref_lm = apply_refinement(v2_lm, off_x, off_y)

    gt_s = compute_all_sides(gt_lm)
    v2_s = compute_all_sides(v2_lm)
    ref_s = compute_all_sides(ref_lm)

    gt_asl = gt_lm["ASL_L"]
    assert gt_asl.usable and gt_asl.x is not None and gt_asl.y is not None
    gt_pt = (float(gt_asl.x), float(gt_asl.y))
    v2_pt = v2_lm["ASL_L"].point
    ref_pt = ref_lm["ASL_L"].point
    assert v2_pt is not None and ref_pt is not None

    return ValCaseResult(
        case_id=case_id,
        asl_l_error_v2=dist(v2_pt, gt_pt),
        asl_l_error_refined=dist(ref_pt, gt_pt),
        vce_l_v2=side_value(v2_s, "vce", "L"),
        vce_l_refined=side_value(ref_s, "vce", "L"),
        vce_l_gt=side_value(gt_s, "vce", "L"),
        tonnis_l_v2=side_value(v2_s, "tonnis", "L"),
        tonnis_l_refined=side_value(ref_s, "tonnis", "L"),
        tonnis_l_gt=side_value(gt_s, "tonnis", "L"),
        vce_r_v2=side_value(v2_s, "vce", "R"),
        vce_r_refined=side_value(ref_s, "vce", "R"),
        tonnis_r_v2=side_value(v2_s, "tonnis", "R"),
        tonnis_r_refined=side_value(ref_s, "tonnis", "R"),
        ccd_r_v2=side_value(v2_s, "ccd", "R"),
        ccd_r_refined=side_value(ref_s, "ccd", "R"),
        ccd_l_v2=side_value(v2_s, "ccd", "L"),
        ccd_l_refined=side_value(ref_s, "ccd", "L"),
    )


def ccd_unchanged(results: list[ValCaseResult]) -> bool:
    for r in results:
        for side in ("r", "l"):
            v2 = getattr(r, f"ccd_{side}_v2")
            ref = getattr(r, f"ccd_{side}_refined")
            if v2 is None and ref is None:
                continue
            if v2 is None or ref is None or abs(v2 - ref) > CCD_TOLERANCE:
                return False
    return True


def mean_of(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None]
    return statistics.mean(nums) if nums else None


def median_of(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None]
    return statistics.median(nums) if nums else None


def asymmetry_mean(results: list[ValCaseResult], measure: str, version: str) -> float | None:
    diffs = []
    for r in results:
        left = getattr(r, f"{measure.lower()}_l_{version}")
        right = getattr(r, f"{measure.lower()}_r_{version}")
        if left is not None and right is not None:
            diffs.append(abs(right - left))
    return statistics.mean(diffs) if diffs else None


def assess_verdict(
    results: list[ValCaseResult],
    ccd_ok: bool,
    asl_improvement_pct: float,
    improved: int,
    degraded: int,
    vce_err_v2: float | None,
    vce_err_ref: float | None,
    ton_err_v2: float | None,
    ton_err_ref: float | None,
) -> str:
    if not ccd_ok:
        return "FAILED"
    geom_better = (
        vce_err_ref is not None
        and vce_err_v2 is not None
        and ton_err_ref is not None
        and ton_err_v2 is not None
        and vce_err_ref < vce_err_v2
        and ton_err_ref < ton_err_v2
    )
    if improved == len(results) and degraded == 0 and asl_improvement_pct >= 40 and geom_better:
        return "ROBUST"
    if improved >= 3 and degraded == 0 and asl_improvement_pct > 0 and geom_better:
        return "PROMISING"
    if improved > degraded and asl_improvement_pct > 0:
        return "PROMISING"
    return "FAILED"


def write_csv(results: list[ValCaseResult], calib_meta: dict) -> None:
    rows: list[dict] = [
        {
            "section": "calibration",
            "train_n": calib_meta["n_train"],
            "offset_x_mean": calib_meta["offset_x_mean"],
            "offset_y_mean": calib_meta["offset_y_mean"],
            "offset_x_stdev": calib_meta["offset_x_stdev"],
            "offset_y_stdev": calib_meta["offset_y_stdev"],
        }
    ]
    for r in results:
        rows.append(
            {
                "section": "val_case",
                "case_id": r.case_id,
                "asl_l_error_v2_px": r.asl_l_error_v2,
                "asl_l_error_refined_px": r.asl_l_error_refined,
                "asl_l_improved": r.asl_l_error_refined < r.asl_l_error_v2,
                "vce_l_v2": r.vce_l_v2,
                "vce_l_refined": r.vce_l_refined,
                "vce_l_gt": r.vce_l_gt,
                "vce_l_abs_err_v2": abs_err(r.vce_l_v2, r.vce_l_gt),
                "vce_l_abs_err_refined": abs_err(r.vce_l_refined, r.vce_l_gt),
                "tonnis_l_v2": r.tonnis_l_v2,
                "tonnis_l_refined": r.tonnis_l_refined,
                "tonnis_l_gt": r.tonnis_l_gt,
                "tonnis_l_abs_err_v2": abs_err(r.tonnis_l_v2, r.tonnis_l_gt),
                "tonnis_l_abs_err_refined": abs_err(r.tonnis_l_refined, r.tonnis_l_gt),
                "ccd_r_v2": r.ccd_r_v2,
                "ccd_r_refined": r.ccd_r_refined,
                "ccd_l_v2": r.ccd_l_v2,
                "ccd_l_refined": r.ccd_l_refined,
            }
        )

    fieldnames = sorted({k for row in rows for k in row})
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_md(
    results: list[ValCaseResult],
    calib_meta: dict,
    verdict: str,
    ccd_ok: bool,
    summary: dict,
) -> None:
    lines = [
        "# Validation stricte TRAIN → VAL — refinement C_asm_offset ASL_L",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "**Protocole :** calibrage GT sur 21 TRAIN ; application sur 5 VAL sans fuite",
        f"**Verdict :** **{verdict}**",
        "",
        "## Calibrage (TRAIN uniquement)",
        "",
        f"- Cas TRAIN : {calib_meta['n_train']}",
        f"- Offset moyen GT ASM_L→ASL_L : **({format_num(calib_meta['offset_x_mean'])}, "
        f"{format_num(calib_meta['offset_y_mean'])})** px",
        f"- Écart-type offset : ({format_num(calib_meta['offset_x_stdev'])}, "
        f"{format_num(calib_meta['offset_y_stdev'])}) px",
        f"- Cas VAL (jamais utilisés pour calibrage) : {', '.join(r.case_id for r in results)}",
        "",
        "## 1. Résultat pixel-level (VAL, n=5)",
        "",
        "| Métrique | V2 brut | Refined |",
        "|----------|---------|---------|",
        f"| ASL_L error mean px | {format_num(summary['asl_v2_mean'])} | {format_num(summary['asl_ref_mean'])} |",
        f"| ASL_L error median px | {format_num(summary['asl_v2_median'])} | {format_num(summary['asl_ref_median'])} |",
        f"| Amélioration mean | — | {format_num(summary['asl_improvement_pct'], 1)}% |",
        f"| Cas améliorés | — | {summary['asl_improved']}/5 |",
        f"| Cas dégradés | — | {summary['asl_degraded']}/5 |",
        "",
        "### Détail par cas VAL",
        "",
        "| Cas | V2 px | Refined px | Δ |",
        "|-----|-------|------------|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.case_id} | {format_num(r.asl_l_error_v2)} | {format_num(r.asl_l_error_refined)} | "
            f"{format_num(r.asl_l_error_refined - r.asl_l_error_v2)} |"
        )

    lines.extend(
        [
            "",
            "## 2. Résultat géométrique (VAL vs GT annotations)",
            "",
            "### VCE_L",
            "",
            "| Métrique | V2 | Refined |",
            "|----------|----|---------|",
            f"| \\|pred−GT\\| mean ° | {format_num(summary['vce_err_v2_mean'])} | {format_num(summary['vce_err_ref_mean'])} |",
            f"| \\|pred−GT\\| median ° | {format_num(summary['vce_err_v2_median'])} | {format_num(summary['vce_err_ref_median'])} |",
            f"| négatifs | {summary['vce_neg_v2']} | {summary['vce_neg_ref']} |",
            f"| asymétrie \\|R−L\\| mean ° | {format_num(summary['vce_asym_v2'])} | {format_num(summary['vce_asym_ref'])} |",
            "",
            "### Tönnis_L",
            "",
            "| Métrique | V2 | Refined |",
            "|----------|----|---------|",
            f"| \\|pred−GT\\| mean ° | {format_num(summary['ton_err_v2_mean'])} | {format_num(summary['ton_err_ref_mean'])} |",
            f"| \\|pred−GT\\| median ° | {format_num(summary['ton_err_v2_median'])} | {format_num(summary['ton_err_ref_median'])} |",
            f"| extrêmes | {summary['ton_ext_v2']} | {summary['ton_ext_ref']} |",
            f"| asymétrie \\|R−L\\| mean ° | {format_num(summary['ton_asym_v2'])} | {format_num(summary['ton_asym_ref'])} |",
            "",
            "### CCD (contrôle)",
            "",
            f"- **CCD changed : {'NO' if ccd_ok else 'YES'}**",
            "",
            "## 3. Comparaison aux annotations GT",
            "",
            "GT VAL utilisé **exclusivement** pour mesurer l'erreur finale (pixel + angles). "
            "Aucune annotation VAL n'a participé au calcul de l'offset TRAIN→VAL.",
            "",
            "## 4. Interprétation clinique",
            "",
            "- n=5 VAL limité statistiquement — prudence sur la généralisation.",
            "- Amélioration géométrique vs GT ne remplace pas une validation clinique experte.",
            "- CCD stable confirme que seul ASL_L est déplacé (landmarks fémoraux intacts).",
            "",
            f"CSV : `{OUTPUT_CSV.name}`",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    train_ids, val_ids = load_split()
    off_x, off_y, calib_meta = calibrate_from_train(train_ids)

    results = [evaluate_val_case(cid, off_x, off_y) for cid in val_ids]

    asl_v2 = [r.asl_l_error_v2 for r in results]
    asl_ref = [r.asl_l_error_refined for r in results]
    asl_v2_mean = statistics.mean(asl_v2)
    asl_ref_mean = statistics.mean(asl_ref)
    asl_v2_median = statistics.median(asl_v2)
    asl_ref_median = statistics.median(asl_ref)
    improved = sum(1 for r in results if r.asl_l_error_refined < r.asl_l_error_v2 - 1e-6)
    degraded = sum(1 for r in results if r.asl_l_error_refined > r.asl_l_error_v2 + 1e-6)
    asl_improvement_pct = (1 - asl_ref_mean / asl_v2_mean) * 100 if asl_v2_mean else 0.0

    vce_err_v2 = [abs_err(r.vce_l_v2, r.vce_l_gt) for r in results]
    vce_err_ref = [abs_err(r.vce_l_refined, r.vce_l_gt) for r in results]
    ton_err_v2 = [abs_err(r.tonnis_l_v2, r.tonnis_l_gt) for r in results]
    ton_err_ref = [abs_err(r.tonnis_l_refined, r.tonnis_l_gt) for r in results]

    vce_neg_v2 = sum(1 for r in results if r.vce_l_v2 is not None and r.vce_l_v2 < 0)
    vce_neg_ref = sum(1 for r in results if r.vce_l_refined is not None and r.vce_l_refined < 0)
    ton_ext_v2 = sum(1 for r in results if is_tonnis_extreme(r.tonnis_l_v2))
    ton_ext_ref = sum(1 for r in results if is_tonnis_extreme(r.tonnis_l_refined))

    ccd_ok = ccd_unchanged(results)

    summary = {
        "asl_v2_mean": asl_v2_mean,
        "asl_ref_mean": asl_ref_mean,
        "asl_v2_median": asl_v2_median,
        "asl_ref_median": asl_ref_median,
        "asl_improvement_pct": asl_improvement_pct,
        "asl_improved": improved,
        "asl_degraded": degraded,
        "vce_err_v2_mean": mean_of(vce_err_v2),
        "vce_err_ref_mean": mean_of(vce_err_ref),
        "vce_err_v2_median": median_of(vce_err_v2),
        "vce_err_ref_median": median_of(vce_err_ref),
        "vce_neg_v2": vce_neg_v2,
        "vce_neg_ref": vce_neg_ref,
        "vce_asym_v2": asymmetry_mean(results, "vce", "v2"),
        "vce_asym_ref": asymmetry_mean(results, "vce", "refined"),
        "ton_err_v2_mean": mean_of(ton_err_v2),
        "ton_err_ref_mean": mean_of(ton_err_ref),
        "ton_err_v2_median": median_of(ton_err_v2),
        "ton_err_ref_median": median_of(ton_err_ref),
        "ton_ext_v2": ton_ext_v2,
        "ton_ext_ref": ton_ext_ref,
        "ton_asym_v2": asymmetry_mean(results, "tonnis", "v2"),
        "ton_asym_ref": asymmetry_mean(results, "tonnis", "refined"),
    }

    verdict = assess_verdict(
        results,
        ccd_ok,
        asl_improvement_pct,
        improved,
        degraded,
        summary["vce_err_v2_mean"],
        summary["vce_err_ref_mean"],
        summary["ton_err_v2_mean"],
        summary["ton_err_ref_mean"],
    )

    write_csv(results, calib_meta)
    write_md(results, calib_meta, verdict, ccd_ok, summary)

    print("STRICT TRAIN-VAL REFINEMENT COMPLETE")
    print(f"Train calibration cases: {len(train_ids)}")
    print(f"Validation cases: {len(val_ids)}")
    print("")
    print("ASL_L:")
    print(f"V2 = {asl_v2_mean:.2f} px (median {asl_v2_median:.2f})")
    print(f"Refined = {asl_ref_mean:.2f} px (median {asl_ref_median:.2f})")
    print(f"Improvement = {asl_improvement_pct:.1f}% ({improved}/5 improved, {degraded}/5 degraded)")
    print("")
    print("VCE_L:")
    print(f"negative V2 = {vce_neg_v2}")
    print(f"negative refined = {vce_neg_ref}")
    print(f"error V2 = {summary['vce_err_v2_mean']:.2f}°")
    print(f"error refined = {summary['vce_err_ref_mean']:.2f}°")
    print("")
    print("TONNIS_L:")
    print(f"extreme V2 = {ton_ext_v2}")
    print(f"extreme refined = {ton_ext_ref}")
    print(f"error V2 = {summary['ton_err_v2_mean']:.2f}°")
    print(f"error refined = {summary['ton_err_ref_mean']:.2f}°")
    print("")
    print(f"CCD changed: {'NO' if ccd_ok else 'YES'}")
    print("")
    print(f"VERDICT: {verdict}")
    print(f"REPORT={OUTPUT_MD.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
