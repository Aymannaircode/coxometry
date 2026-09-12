#!/usr/bin/env python3
"""Impact géométrique du refinement LOO C_asm_offset sur ASL_L (new_26).

Couche post-traitement indépendante — ne modifie ni V2, ni labels, ni prédictions.
Calibration LOO : vecteur ASM_L→ASL_L appris sur 25 cas, jamais le GT du cas testé.
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
LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_asl_refined_geometry_results.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_asl_refined_geometry_analysis.md"

EXPECTED_CASES = 26
TONNIS_EXTREME_ABS = 150.0
CCD_TOLERANCE = 1e-4


@dataclass
class CaseBundle:
    case_id: str
    width: float
    height: float
    gt_landmarks: dict[str, Landmark]
    v2_landmarks: dict[str, Landmark]
    refined_landmarks: dict[str, Landmark]


@dataclass
class CaseMeasures:
    case_id: str
    vce_r: float | None
    vce_l: float | None
    tonnis_r: float | None
    tonnis_l: float | None
    ccd_r: float | None
    ccd_l: float | None

    def get(self, measure: str, side: str) -> float | None:
        return getattr(self, f"{measure.lower()}_{side.lower()}")


def format_num(v: float | None, d: int = 2) -> str:
    return "NA" if v is None else f"{v:.{d}f}"


def read_image_size(case_id: str) -> tuple[float, float]:
    from PIL import Image

    with Image.open(IMAGE_DIR / f"{case_id}.png") as img:
        return float(img.size[0]), float(img.size[1])


def gt_point_dict(gt_landmarks: dict[str, Landmark]) -> dict[str, tuple[float, float]]:
    return {
        name: (lm.x, lm.y)
        for name, lm in gt_landmarks.items()
        if lm.usable and lm.x is not None and lm.y is not None
    }


def calibrate_asm_offset_loo(
    train_gt: list[dict[str, tuple[float, float]]],
) -> tuple[float, float]:
    ox = [g["ASL_L"][0] - g["ASM_L"][0] for g in train_gt]
    oy = [g["ASL_L"][1] - g["ASM_L"][1] for g in train_gt]
    return statistics.mean(ox), statistics.mean(oy)


def apply_asm_offset_refinement(
    v2_landmarks: dict[str, Landmark],
    off_x: float,
    off_y: float,
) -> dict[str, Landmark]:
    refined = dict(v2_landmarks)
    asm = v2_landmarks["ASM_L"]
    if not asm.usable or asm.x is None or asm.y is None:
        raise ValueError("V2 ASM_L non exploitable pour refinement.")
    new_x = round(asm.x + off_x, 2)
    new_y = round(asm.y + off_y, 2)
    asl = v2_landmarks["ASL_L"]
    refined["ASL_L"] = replace(asl, x=new_x, y=new_y, v=2)
    return refined


def extract_measures(case_id: str, sides: dict[str, SideResult]) -> CaseMeasures:
    def val(side: SideResult, attr: str) -> float | None:
        m = getattr(side, attr)
        return m.value_deg if m.available else None

    return CaseMeasures(
        case_id=case_id,
        vce_r=val(sides["R"], "vce"),
        vce_l=val(sides["L"], "vce"),
        tonnis_r=val(sides["R"], "tonnis"),
        tonnis_l=val(sides["L"], "tonnis"),
        ccd_r=val(sides["R"], "ccd"),
        ccd_l=val(sides["L"], "ccd"),
    )


def is_tonnis_extreme(v: float | None) -> bool:
    if v is None:
        return False
    return abs(v) > TONNIS_EXTREME_ABS or v < -15 or v > 165


def measure_stats(values: list[float | None]) -> dict[str, float | int | None]:
    nums = [v for v in values if v is not None]
    if not nums:
        return {"mean": None, "median": None, "min": None, "max": None, "n": 0}
    return {
        "mean": statistics.mean(nums),
        "median": statistics.median(nums),
        "min": min(nums),
        "max": max(nums),
        "n": len(nums),
    }


def asymmetry_stats(measures: list[CaseMeasures], measure: str) -> dict[str, float | None]:
    diffs = []
    for m in measures:
        r, l = m.get(measure, "R"), m.get(measure, "L")
        if r is not None and l is not None:
            diffs.append(abs(r - l))
    if not diffs:
        return {"mean": None, "median": None}
    return {"mean": statistics.mean(diffs), "median": statistics.median(diffs)}


def gt_distance(case: CaseMeasures, gt: CaseMeasures, measure: str, side: str) -> float | None:
    v, g = case.get(measure, side), gt.get(measure, side)
    if v is None or g is None:
        return None
    return abs(v - g)


def build_cases() -> list[CaseBundle]:
    case_ids = sorted(p.stem for p in ANNOT_DIR.glob("B26_*.json"))
    if len(case_ids) != EXPECTED_CASES:
        raise RuntimeError(f"Attendu {EXPECTED_CASES} cas, trouvé {len(case_ids)}")

    gt_dicts: dict[str, dict[str, tuple[float, float]]] = {}
    bundles: list[CaseBundle] = []

    for case_id in case_ids:
        w, h = read_image_size(case_id)
        gt_lm = landmarks_by_name(load_pilot_schema(ANNOT_DIR / f"{case_id}.json"))
        v2_lm = landmarks_from_yolo_label(LABEL_DIR / f"{case_id}.txt", w, h)
        gt_dicts[case_id] = gt_point_dict(gt_lm)
        bundles.append(
            CaseBundle(
                case_id=case_id,
                width=w,
                height=h,
                gt_landmarks=gt_lm,
                v2_landmarks=v2_lm,
                refined_landmarks=v2_lm,
            )
        )

    for i, test in enumerate(bundles):
        train_gt = [gt_dicts[c.case_id] for c in bundles if c.case_id != test.case_id]
        off_x, off_y = calibrate_asm_offset_loo(train_gt)
        test.refined_landmarks = apply_asm_offset_refinement(test.v2_landmarks, off_x, off_y)

    return bundles


def ccd_unchanged(raw: list[CaseMeasures], refined: list[CaseMeasures]) -> bool:
    for r, f in zip(raw, refined):
        for side in ("r", "l"):
            rv = getattr(r, f"ccd_{side}")
            fv = getattr(f, f"ccd_{side}")
            if rv is None and fv is None:
                continue
            if rv is None or fv is None:
                return False
            if abs(rv - fv) > CCD_TOLERANCE:
                return False
    return True


def assess_verdict(
    raw: list[CaseMeasures],
    refined: list[CaseMeasures],
    gt: list[CaseMeasures],
    ccd_ok: bool,
) -> tuple[str, list[str]]:
    lines: list[str] = []

    vce_neg_raw = sum(1 for m in raw if m.vce_l is not None and m.vce_l < 0)
    vce_neg_ref = sum(1 for m in refined if m.vce_l is not None and m.vce_l < 0)
    ton_ext_raw = sum(1 for m in raw if is_tonnis_extreme(m.tonnis_l))
    ton_ext_ref = sum(1 for m in refined if is_tonnis_extreme(m.tonnis_l))

    vce_gt_raw = [gt_distance(r, g, "VCE", "L") for r, g in zip(raw, gt)]
    vce_gt_ref = [gt_distance(r, g, "VCE", "L") for r, g in zip(refined, gt)]
    ton_gt_raw = [gt_distance(r, g, "Tonnis", "L") for r, g in zip(raw, gt)]
    ton_gt_ref = [gt_distance(r, g, "Tonnis", "L") for r, g in zip(refined, gt)]

    vce_gt_raw_n = [v for v in vce_gt_raw if v is not None]
    vce_gt_ref_n = [v for v in vce_gt_ref if v is not None]
    ton_gt_raw_n = [v for v in ton_gt_raw if v is not None]
    ton_gt_ref_n = [v for v in ton_gt_ref if v is not None]

    vce_closer = statistics.mean(vce_gt_ref_n) < statistics.mean(vce_gt_raw_n) if vce_gt_ref_n else False
    ton_closer = statistics.mean(ton_gt_ref_n) < statistics.mean(ton_gt_raw_n) if ton_gt_ref_n else False

    asym_vce_raw = asymmetry_stats(raw, "VCE")
    asym_vce_ref = asymmetry_stats(refined, "VCE")
    asym_ton_raw = asymmetry_stats(raw, "Tonnis")
    asym_ton_ref = asymmetry_stats(refined, "Tonnis")

    coherence_better = (
        (asym_vce_ref["mean"] or 999) <= (asym_vce_raw["mean"] or 999)
        and (asym_ton_ref["mean"] or 999) <= (asym_ton_raw["mean"] or 999)
        and vce_neg_ref <= vce_neg_raw
        and ton_ext_ref <= ton_ext_raw
    )

    gt_better = vce_closer and ton_closer
    gt_partial = (vce_closer or ton_closer) and not (not vce_closer and not ton_closer)

    lines.append(
        f"Distance moyenne |VCE_L − GT| : {format_num(statistics.mean(vce_gt_raw_n))}° → "
        f"{format_num(statistics.mean(vce_gt_ref_n))}°"
    )
    lines.append(
        f"Distance moyenne |Tönnis_L − GT| : {format_num(statistics.mean(ton_gt_raw_n))}° → "
        f"{format_num(statistics.mean(ton_gt_ref_n))}°"
    )
    lines.append(
        f"Asymétrie |R−L| VCE mean : {format_num(asym_vce_raw['mean'])}° → "
        f"{format_num(asym_vce_ref['mean'])}°"
    )
    lines.append(
        f"Asymétrie |R−L| Tönnis mean : {format_num(asym_ton_raw['mean'])}° → "
        f"{format_num(asym_ton_ref['mean'])}°"
    )

    if not ccd_ok:
        verdict = "DEGRADING"
        lines.append("CCD modifié — non conforme au cahier des charges (landmarks fémoraux intacts).")
    elif gt_better and coherence_better:
        verdict = "IMPROVED"
        lines.append("Amélioration vs GT et cohérence interne (asymétrie / comptages).")
    elif gt_partial or coherence_better:
        verdict = "IMPROVED" if gt_partial and vce_neg_ref <= vce_neg_raw else "NEUTRAL"
        if verdict == "IMPROVED":
            lines.append("Amélioration partielle vs GT avec cohérence stable ou améliorée.")
        else:
            lines.append("Effet mixte — certains indicateurs s'améliorent, d'autres stagnent.")
    elif vce_neg_ref > vce_neg_raw or ton_ext_ref > ton_ext_raw:
        verdict = "DEGRADING"
        lines.append("Dégradation de cohérence (négatifs VCE ou Tönnis extrêmes en hausse).")
    else:
        verdict = "NEUTRAL"
        lines.append("Pas d'amélioration nette mesurable vs GT ni en cohérence globale.")

    return verdict, lines


def write_csv(
    raw: list[CaseMeasures],
    refined: list[CaseMeasures],
    gt: list[CaseMeasures],
) -> None:
    rows: list[dict] = []
    for r, f, g in zip(raw, refined, gt):
        row = {
            "case_id": r.case_id,
            "VCE_L_raw": r.vce_l,
            "VCE_L_refined": f.vce_l,
            "VCE_L_gt": g.vce_l,
            "VCE_R_raw": r.vce_r,
            "VCE_R_refined": f.vce_r,
            "Tonnis_L_raw": r.tonnis_l,
            "Tonnis_L_refined": f.tonnis_l,
            "Tonnis_L_gt": g.tonnis_l,
            "Tonnis_R_raw": r.tonnis_r,
            "Tonnis_R_refined": f.tonnis_r,
            "CCD_R_raw": r.ccd_r,
            "CCD_R_refined": f.ccd_r,
            "CCD_L_raw": r.ccd_l,
            "CCD_L_refined": f.ccd_l,
            "delta_VCE_L_abs": abs(f.vce_l - r.vce_l) if f.vce_l is not None and r.vce_l is not None else None,
            "delta_Tonnis_L_abs": abs(f.tonnis_l - r.tonnis_l)
            if f.tonnis_l is not None and r.tonnis_l is not None
            else None,
            "delta_VCE_L_vs_gt_raw": gt_distance(r, g, "VCE", "L"),
            "delta_VCE_L_vs_gt_refined": gt_distance(f, g, "VCE", "L"),
            "delta_Tonnis_L_vs_gt_raw": gt_distance(r, g, "Tonnis", "L"),
            "delta_Tonnis_L_vs_gt_refined": gt_distance(f, g, "Tonnis", "L"),
        }
        rows.append(row)

    fieldnames = list(rows[0].keys()) if rows else []
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(
    raw: list[CaseMeasures],
    refined: list[CaseMeasures],
    gt: list[CaseMeasures],
    verdict: str,
    verdict_lines: list[str],
    ccd_ok: bool,
) -> None:
    vce_neg_raw = sum(1 for m in raw if m.vce_l is not None and m.vce_l < 0)
    vce_neg_ref = sum(1 for m in refined if m.vce_l is not None and m.vce_l < 0)
    ton_ext_raw = sum(1 for m in raw if is_tonnis_extreme(m.tonnis_l))
    ton_ext_ref = sum(1 for m in refined if is_tonnis_extreme(m.tonnis_l))

    def block(measures: list[CaseMeasures], measure: str, side: str) -> dict:
        return measure_stats([m.get(measure, side) for m in measures])

    improvements: list[tuple[str, float]] = []
    degradations: list[tuple[str, float]] = []
    for r, f, g in zip(raw, refined, gt):
        raw_d = (gt_distance(r, g, "VCE", "L") or 0) + (gt_distance(r, g, "Tonnis", "L") or 0)
        ref_d = (gt_distance(f, g, "VCE", "L") or 0) + (gt_distance(f, g, "Tonnis", "L") or 0)
        delta = raw_d - ref_d
        if delta > 0.5:
            improvements.append((r.case_id, delta))
        elif delta < -0.5:
            degradations.append((r.case_id, -delta))

    improvements.sort(key=lambda x: -x[1])
    degradations.sort(key=lambda x: -x[1])

    lines = [
        "# Analyse géométrique — refinement LOO C_asm_offset sur ASL_L",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "**Méthode :** C_asm_offset LOO (calibrage 25 cas, test sans GT ASL_L du cas exclu)",
        "**Post-traitement :** couche indépendante — V2 prédictions non modifiées sur disque",
        "",
        f"## Verdict : **{verdict}**",
        "",
    ]
    lines.extend(f"- {line}" for line in verdict_lines)

    lines.extend(
        [
            "",
            "## 1. Cohérence mathématique (prédictions V2 brutes vs refined)",
            "",
            "### VCE_L",
            "",
            "| Stat | Brut | Refined |",
            "|------|------|---------|",
        ]
    )
    for stat in ("mean", "median", "min", "max"):
        b = block(raw, "VCE", "L")
        f = block(refined, "VCE", "L")
        lines.append(f"| {stat} | {format_num(b[stat])} | {format_num(f[stat])} |")
    asym_vce_r = asymmetry_stats(raw, "VCE")
    asym_vce_f = asymmetry_stats(refined, "VCE")
    lines.extend(
        [
            f"| négatifs | {vce_neg_raw} | {vce_neg_ref} |",
            f"| asymétrie \\|R−L\\| mean | {format_num(asym_vce_r['mean'])} | {format_num(asym_vce_f['mean'])} |",
            "",
            "### Tönnis_L",
            "",
            "| Stat | Brut | Refined |",
            "|------|------|---------|",
        ]
    )
    for stat in ("mean", "median", "min", "max"):
        b = block(raw, "Tonnis", "L")
        f = block(refined, "Tonnis", "L")
        lines.append(f"| {stat} | {format_num(b[stat])} | {format_num(f[stat])} |")
    asym_ton_r = asymmetry_stats(raw, "Tonnis")
    asym_ton_f = asymmetry_stats(refined, "Tonnis")
    lines.extend(
        [
            f"| négatifs | {sum(1 for m in raw if m.tonnis_l is not None and m.tonnis_l < 0)} | "
            f"{sum(1 for m in refined if m.tonnis_l is not None and m.tonnis_l < 0)} |",
            f"| extrêmes | {ton_ext_raw} | {ton_ext_ref} |",
            f"| asymétrie \\|R−L\\| mean | {format_num(asym_ton_r['mean'])} | {format_num(asym_ton_f['mean'])} |",
            "",
            "### CCD (contrôle — landmarks fémoraux non modifiés)",
            "",
            "| Stat | CCD_R brut | CCD_R refined | CCD_L brut | CCD_L refined | Δ R−L brut | Δ R−L refined |",
            "|------|------------|---------------|------------|---------------|------------|-----------------|",
        ]
    )
    ccd_r_b = block(raw, "CCD", "R")
    ccd_r_f = block(refined, "CCD", "R")
    ccd_l_b = block(raw, "CCD", "L")
    ccd_l_f = block(refined, "CCD", "L")
    rl_b = [
        abs(m.ccd_r - m.ccd_l)
        for m in raw
        if m.ccd_r is not None and m.ccd_l is not None
    ]
    rl_f = [
        abs(m.ccd_r - m.ccd_l)
        for m in refined
        if m.ccd_r is not None and m.ccd_l is not None
    ]
    lines.append(
        f"| mean | {format_num(ccd_r_b['mean'])} | {format_num(ccd_r_f['mean'])} | "
        f"{format_num(ccd_l_b['mean'])} | {format_num(ccd_l_f['mean'])} | "
        f"{format_num(statistics.mean(rl_b) if rl_b else None)} | "
        f"{format_num(statistics.mean(rl_f) if rl_f else None)} |"
    )
    lines.append(f"| **CCD changed** | — | — | — | — | — | **{'NO' if ccd_ok else 'YES'}** |")

    lines.extend(
        [
            "",
            "## 2. Proximité aux annotations GT (référence manuelle)",
            "",
            "| Mesure | Mean \\|pred−GT\\| brut | Mean \\|pred−GT\\| refined |",
            "|--------|---------------------|------------------------|",
        ]
    )
    for measure, side in (("VCE", "L"), ("Tonnis", "L")):
        raw_d = [gt_distance(r, g, measure, side) for r, g in zip(raw, gt)]
        ref_d = [gt_distance(r, g, measure, side) for r, g in zip(refined, gt)]
        raw_n = [v for v in raw_d if v is not None]
        ref_n = [v for v in ref_d if v is not None]
        lines.append(
            f"| {measure}_{side} | {format_num(statistics.mean(raw_n) if raw_n else None)} | "
            f"{format_num(statistics.mean(ref_n) if ref_n else None)} |"
        )

    lines.extend(
        [
            "",
            "## 3. Interprétation clinique (descriptive, sans seuil arbitraire imposé)",
            "",
            "- **VCE_L** et **Tönnis_L** dépendent directement de ASL_L ; le refinement déplace ces angles.",
            "- **CCD** ne dépend pas de ASL_L — toute variation signalerait un bug de pipeline.",
            "- Les comptages « négatif » et « extrême » Tönnis sont des indicateurs de cohérence interne, "
            "pas des diagnostics cliniques autonomes.",
            "- La validation clinique finale requiert une revue expert indépendante des cas individuels.",
            "",
            "## 4. Variation par cas",
            "",
            "### Top 5 améliorations (réduction \\|VCE_L−GT\\| + \\|Tönnis_L−GT\\|)",
            "",
            "| Cas | Gain composite ° |",
            "|-----|------------------|",
        ]
    )
    for case_id, gain in improvements[:5]:
        lines.append(f"| {case_id} | {format_num(gain)} |")
    if not improvements:
        lines.append("| — | aucune |")

    lines.extend(
        [
            "",
            "### Top 5 dégradations éventuelles",
            "",
            "| Cas | Perte composite ° |",
            "|-----|-------------------|",
        ]
    )
    for case_id, loss in degradations[:5]:
        lines.append(f"| {case_id} | {format_num(loss)} |")
    if not degradations:
        lines.append("| — | aucune |")

    lines.extend(["", f"CSV : `{OUTPUT_CSV.name}`", ""])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    bundles = build_cases()
    raw: list[CaseMeasures] = []
    refined: list[CaseMeasures] = []
    gt: list[CaseMeasures] = []

    for b in bundles:
        raw.append(extract_measures(b.case_id, compute_all_sides(b.v2_landmarks)))
        refined.append(extract_measures(b.case_id, compute_all_sides(b.refined_landmarks)))
        gt.append(extract_measures(b.case_id, compute_all_sides(b.gt_landmarks)))

    ccd_ok = ccd_unchanged(raw, refined)
    verdict, verdict_lines = assess_verdict(raw, refined, gt, ccd_ok)
    write_csv(raw, refined, gt)
    write_md(raw, refined, gt, verdict, verdict_lines, ccd_ok)

    vce_neg_raw = sum(1 for m in raw if m.vce_l is not None and m.vce_l < 0)
    vce_neg_ref = sum(1 for m in refined if m.vce_l is not None and m.vce_l < 0)
    ton_ext_raw = sum(1 for m in raw if is_tonnis_extreme(m.tonnis_l))
    ton_ext_ref = sum(1 for m in refined if is_tonnis_extreme(m.tonnis_l))

    print("ASL_L REFINEMENT GEOMETRY COMPLETE")
    print(f"Cases: {len(bundles)}")
    print(f"VCE_L negative: {vce_neg_raw} -> {vce_neg_ref}")
    print(f"Tonnis_L extreme: {ton_ext_raw} -> {ton_ext_ref}")
    print(f"CCD changed: {'NO' if ccd_ok else 'YES'}")
    print(f"VERDICT: {verdict}")
    print(f"REPORT={OUTPUT_MD.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
