#!/usr/bin/env python3
"""Validation leave-one-out des corrections ASL_L post-V2 (new_26).

Pour chaque cas i : calibrer sur les 25 autres, appliquer sans GT du cas i,
évaluer vs GT ASL_L. Lecture seule — aucune modification des sources.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ANNOT_DIR = PROJECT_ROOT / "annotation_pilot" / "annotations" / "new_26"
LABEL_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "labels"
IMAGE_DIR = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "predictions_v2" / "images"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "asl_l_refinement_loo.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "asl_l_refinement_loo.md"

LANDMARKS = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L",
    "ASM_R", "ASM_L", "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L",
]
KEYPOINTS_START = 5
MIN_KEYPOINT_CONF = 0.25
EXPECTED_CASES = 26
HIGH_ERROR_PX = 200.0

FEASIBLE_MEAN_REDUCTION = 0.45
FEASIBLE_MEDIAN_PX = 160.0
FEASIBLE_OVER200_MAX = 6
PARTIAL_MEAN_REDUCTION = 0.25
PARTIAL_MEDIAN_PX = 250.0


@dataclass
class CaseData:
    case_id: str
    width: float
    height: float
    gt: dict[str, tuple[float, float]]
    v2: dict[str, tuple[float, float]]

    @property
    def v2_raw_error(self) -> float:
        return dist(self.v2["ASL_L"], self.gt["ASL_L"])


@dataclass
class MethodResult:
    method_id: str
    label: str
    errors: dict[str, float] = field(default_factory=dict)

    def stats(self, raw_errors: dict[str, float]) -> dict[str, float | int]:
        vals = list(self.errors.values())
        raw_vals = [raw_errors[c] for c in self.errors]
        improved = sum(1 for c in self.errors if self.errors[c] < raw_errors[c] - 1e-6)
        degraded = sum(1 for c in self.errors if self.errors[c] > raw_errors[c] + 1e-6)
        raw_mean = statistics.mean(raw_vals)
        return {
            "mean": statistics.mean(vals),
            "median": statistics.median(vals),
            "stdev": statistics.stdev(vals) if len(vals) >= 2 else 0.0,
            "min": min(vals),
            "max": max(vals),
            "improvement_pct": (1 - statistics.mean(vals) / raw_mean) * 100 if raw_mean else 0.0,
            "improved": improved,
            "degraded": degraded,
            "unchanged": len(vals) - improved - degraded,
            "over_200": sum(1 for v in vals if v > HIGH_ERROR_PX),
        }

    def worst_cases(self, n: int = 5) -> list[tuple[str, float]]:
        return sorted(self.errors.items(), key=lambda x: x[1], reverse=True)[:n]


def format_num(v: float | None, d: int = 2) -> str:
    return "NA" if v is None else f"{v:.{d}f}"


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def angle_deg(origin: tuple[float, float], target: tuple[float, float]) -> float:
    return math.degrees(math.atan2(target[1] - origin[1], target[0] - origin[0]))


def circular_mean_deg(angles: list[float]) -> float:
    rads = [math.radians(a) for a in angles]
    sin_m = statistics.mean(math.sin(r) for r in rads)
    cos_m = statistics.mean(math.cos(r) for r in rads)
    return math.degrees(math.atan2(sin_m, cos_m))


def image_dimensions(annotation: dict, case_id: str) -> tuple[float, float]:
    w, h = annotation.get("image_width"), annotation.get("image_height")
    if w and h:
        return float(w), float(h)
    from PIL import Image

    with Image.open(IMAGE_DIR / f"{case_id}.png") as img:
        return float(img.size[0]), float(img.size[1])


def gt_points(annotation: dict) -> dict[str, tuple[float, float]]:
    pts: dict[str, tuple[float, float]] = {}
    for lm in annotation.get("landmarks", []):
        if lm.get("v") == 2 and lm.get("name") in LANDMARKS:
            pts[lm["name"]] = (float(lm["x"]), float(lm["y"]))
    return pts


def parse_v2(path: Path, width: float, height: float) -> dict[str, tuple[float, float]]:
    values = path.read_text(encoding="utf-8").strip().split()
    kpts = [float(v) for v in values[KEYPOINTS_START:-1 if len(values) == 48 else None]]
    out: dict[str, tuple[float, float]] = {}
    for i, name in enumerate(LANDMARKS):
        x, y, c = kpts[i * 3], kpts[i * 3 + 1], kpts[i * 3 + 2]
        if c >= MIN_KEYPOINT_CONF:
            out[name] = (x * width, y * height)
    return out


def load_cases() -> list[CaseData]:
    cases: list[CaseData] = []
    required = ("ASL_L", "ASM_L", "ASL_R", "FHC_L", "FHC_R")
    for json_path in sorted(ANNOT_DIR.glob("B26_*.json")):
        case_id = json_path.stem
        ann = json.loads(json_path.read_text(encoding="utf-8-sig"))
        w, h = image_dimensions(ann, case_id)
        gt = gt_points(ann)
        v2 = parse_v2(LABEL_DIR / f"{case_id}.txt", w, h)
        for name in required:
            if name not in gt or name not in v2:
                raise ValueError(f"{case_id} : GT ou V2 manquant pour {name}")
        cases.append(CaseData(case_id=case_id, width=w, height=h, gt=gt, v2=v2))
    if len(cases) != EXPECTED_CASES:
        raise RuntimeError(f"Attendu {EXPECTED_CASES} cas, trouvé {len(cases)}")
    return cases


def mirror_asl_r(v2: dict[str, tuple[float, float]]) -> tuple[float, float]:
    mid_x = (v2["FHC_R"][0] + v2["FHC_L"][0]) / 2.0
    asl_r = v2["ASL_R"]
    return (2 * mid_x - asl_r[0], asl_r[1])


def calibrate_translation(train: list[CaseData]) -> tuple[float, float]:
    dxs = [c.v2["ASL_L"][0] - c.gt["ASL_L"][0] for c in train]
    dys = [c.v2["ASL_L"][1] - c.gt["ASL_L"][1] for c in train]
    return statistics.mean(dxs), statistics.mean(dys)


def apply_translation(case: CaseData, mean_dx: float, mean_dy: float) -> tuple[float, float]:
    p = case.v2["ASL_L"]
    return (p[0] - mean_dx, p[1] - mean_dy)


def calibrate_asm_offset(train: list[CaseData]) -> tuple[float, float]:
    ox = [c.gt["ASL_L"][0] - c.gt["ASM_L"][0] for c in train]
    oy = [c.gt["ASL_L"][1] - c.gt["ASM_L"][1] for c in train]
    return statistics.mean(ox), statistics.mean(oy)


def apply_asm_offset(case: CaseData, off_x: float, off_y: float) -> tuple[float, float]:
    asm = case.v2["ASM_L"]
    return (asm[0] + off_x, asm[1] + off_y)


def calibrate_mirror_residual(train: list[CaseData]) -> tuple[float, float]:
    res_x, res_y = [], []
    for c in train:
        m = mirror_asl_r(c.v2)
        res_x.append(m[0] - c.gt["ASL_L"][0])
        res_y.append(m[1] - c.gt["ASL_L"][1])
    return statistics.mean(res_x), statistics.mean(res_y)


def apply_mirror_calibrated(case: CaseData, res_x: float, res_y: float) -> tuple[float, float]:
    m = mirror_asl_r(case.v2)
    return (m[0] - res_x, m[1] - res_y)


def calibrate_brow_polar(train: list[CaseData]) -> tuple[float, float]:
    lengths = [dist(c.gt["ASM_L"], c.gt["ASL_L"]) for c in train]
    angles = [angle_deg(c.gt["ASM_L"], c.gt["ASL_L"]) for c in train]
    return statistics.mean(lengths), circular_mean_deg(angles)


def apply_brow_geometry(case: CaseData, length: float, ang_deg: float) -> tuple[float, float]:
    asm = case.v2["ASM_L"]
    rad = math.radians(ang_deg)
    return (asm[0] + length * math.cos(rad), asm[1] + length * math.sin(rad))


def run_loo(cases: list[CaseData]) -> dict[str, MethodResult]:
    methods = {
        "A_v2_raw": MethodResult("A_v2_raw", "V2 brut"),
        "B_translation": MethodResult("B_translation", "Translation globale dx/dy"),
        "C_asm_offset": MethodResult("C_asm_offset", "Offset ASM_L global"),
        "D_mirror_calibrated": MethodResult("D_mirror_calibrated", "Miroir ASL_R calibré"),
        "E_brow_geometry": MethodResult("E_brow_geometry", "Géométrie sourcil (V2_ASM_L + polaire)"),
    }

    for i, test in enumerate(cases):
        train = [c for c in cases if c.case_id != test.case_id]
        gt_asl = test.gt["ASL_L"]

        # A — V2 brut
        methods["A_v2_raw"].errors[test.case_id] = dist(test.v2["ASL_L"], gt_asl)

        # B — translation
        mdx, mdy = calibrate_translation(train)
        corr_b = apply_translation(test, mdx, mdy)
        methods["B_translation"].errors[test.case_id] = dist(corr_b, gt_asl)

        # C — ASM offset
        ox, oy = calibrate_asm_offset(train)
        corr_c = apply_asm_offset(test, ox, oy)
        methods["C_asm_offset"].errors[test.case_id] = dist(corr_c, gt_asl)

        # D — mirror calibrated (inférence : V2 FHC + ASL_R uniquement)
        rx, ry = calibrate_mirror_residual(train)
        corr_d = apply_mirror_calibrated(test, rx, ry)
        methods["D_mirror_calibrated"].errors[test.case_id] = dist(corr_d, gt_asl)

        # E — brow geometry (inférence : V2_ASM_L uniquement)
        length, ang = calibrate_brow_polar(train)
        corr_e = apply_brow_geometry(test, length, ang)
        methods["E_brow_geometry"].errors[test.case_id] = dist(corr_e, gt_asl)

    return methods


def assess_verdict(
    methods: dict[str, MethodResult],
    raw: MethodResult,
) -> tuple[str, str, list[str]]:
    learnable = [m for m in methods.values() if m.method_id != "A_v2_raw"]
    best = min(learnable, key=lambda m: m.stats(raw.errors)["mean"])
    best_stats = best.stats(raw.errors)
    raw_stats = raw.stats(raw.errors)

    lines = [
        f"Meilleure méthode LOO : **{best.label}** ({best.method_id})",
        f"Mean LOO : {format_num(best_stats['mean'])} px (V2 brut : {format_num(raw_stats['mean'])} px)",
        f"Median LOO : {format_num(best_stats['median'])} px (V2 brut : {format_num(raw_stats['median'])} px)",
        f"Amélioration mean : {format_num(best_stats['improvement_pct'], 1)}%",
        f"Cas >200 px : {best_stats['over_200']}/26 (V2 : {raw_stats['over_200']}/26)",
        f"Cas améliorés / dégradés : {best_stats['improved']}/{best_stats['degraded']}",
    ]

    mean_red = best_stats["improvement_pct"] / 100
    if (
        mean_red >= FEASIBLE_MEAN_REDUCTION
        and best_stats["median"] <= FEASIBLE_MEDIAN_PX
        and best_stats["over_200"] <= FEASIBLE_OVER200_MAX
        and best_stats["improved"] >= best_stats["degraded"]
    ):
        verdict = "FEASIBLE"
        lines.append(
            "La correction reste efficace hors échantillon avec une marge suffisante "
            "pour un post-traitement déterministe."
        )
    elif mean_red >= PARTIAL_MEAN_REDUCTION and best_stats["median"] <= PARTIAL_MEDIAN_PX:
        verdict = "PARTIALLY FEASIBLE"
        lines.append(
            "Amélioration LOO significative mais résidus élevés sur certains cas — "
            "post-traitement possible avec garde-fous ou revue manuelle."
        )
    else:
        verdict = "NOT FEASIBLE"
        lines.append("La validation LOO n'confirme pas un post-traitement fiable sans sur-apprentissage.")

    return verdict, best.method_id, lines


def write_csv(methods: dict[str, MethodResult], raw: MethodResult) -> None:
    rows: list[dict] = []
    for method in methods.values():
        st = method.stats(raw.errors)
        rows.append(
            {
                "section": "summary",
                "method_id": method.method_id,
                "method_label": method.label,
                "mean_px": st["mean"],
                "median_px": st["median"],
                "stdev_px": st["stdev"],
                "min_px": st["min"],
                "max_px": st["max"],
                "improvement_pct_vs_v2": st["improvement_pct"],
                "cases_improved": st["improved"],
                "cases_degraded": st["degraded"],
                "cases_unchanged": st["unchanged"],
                "cases_over_200px": st["over_200"],
            }
        )
        for case_id, err in sorted(method.errors.items()):
            raw_err = raw.errors[case_id]
            rows.append(
                {
                    "section": "per_case",
                    "method_id": method.method_id,
                    "case_id": case_id,
                    "error_px": err,
                    "v2_error_px": raw_err,
                    "delta_px": err - raw_err,
                    "improved": err < raw_err - 1e-6,
                }
            )

    fieldnames = sorted({k for row in rows for k in row})
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_md(
    methods: dict[str, MethodResult],
    raw: MethodResult,
    verdict: str,
    best_id: str,
    verdict_lines: list[str],
) -> None:
    learnable = [m for m in methods.values() if m.method_id != "A_v2_raw"]
    best = methods[best_id]
    best_st = best.stats(raw.errors)
    raw_st = raw.stats(raw.errors)

    degraded_cases: list[tuple[str, str, float, float]] = []
    for case_id in raw.errors:
        worst_delta = 0.0
        worst_method = ""
        for m in learnable:
            delta = m.errors[case_id] - raw.errors[case_id]
            if delta > worst_delta:
                worst_delta = delta
                worst_method = m.method_id
        if worst_delta > 50:
            degraded_cases.append((case_id, worst_method, raw.errors[case_id], worst_delta))

    lines = [
        "# Validation LOO — refinement ASL_L post-V2 (new_26)",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "**Protocole :** leave-one-out sur 26 cas — calibrage sur 25, test sans GT ASL_L du cas exclu",
        "**Mode :** lecture seule",
        "",
        f"## Verdict LOO : **{verdict}**",
        "",
    ]
    lines.extend(f"- {line}" for line in verdict_lines)

    lines.extend(
        [
            "",
            "## Synthèse par méthode",
            "",
            "| Méthode | Mean | Median | Std | Min | Max | Δ vs V2 | Améliorés | Dégradés | >200 px |",
            "|---------|------|--------|-----|-----|-----|---------|-----------|----------|---------|",
        ]
    )
    for m in methods.values():
        st = m.stats(raw.errors)
        lines.append(
            f"| {m.label} | {format_num(st['mean'])} | {format_num(st['median'])} | "
            f"{format_num(st['stdev'])} | {format_num(st['min'])} | {format_num(st['max'])} | "
            f"{format_num(st['improvement_pct'], 1)}% | {st['improved']} | {st['degraded']} | {st['over_200']} |"
        )

    lines.extend(["", "## Pires 5 cas par méthode", ""])
    for m in methods.values():
        lines.append(f"### {m.label}")
        lines.append("")
        lines.append("| Cas | Error LOO px | V2 brut px | Δ |")
        lines.append("|-----|--------------|------------|---|")
        for case_id, err in m.worst_cases(5):
            r = raw.errors[case_id]
            lines.append(f"| {case_id} | {format_num(err)} | {format_num(r)} | {format_num(err - r)} |")
        lines.append("")

    lines.extend(
        [
            "## Réponses aux questions clés",
            "",
            "### 1. La correction reste-t-elle efficace hors échantillon ?",
            "",
        ]
    )
    if verdict == "FEASIBLE":
        lines.append(
            f"**Oui.** La meilleure méthode ({best.label}) réduit l'erreur médiane LOO "
            f"de {format_num(raw_st['median'])} px à {format_num(best_st['median'])} px "
            f"({format_num(best_st['improvement_pct'], 1)}% sur la moyenne)."
        )
    elif verdict == "PARTIALLY FEASIBLE":
        lines.append(
            f"**Partiellement.** Gain LOO mean {format_num(best_st['improvement_pct'], 1)}% "
            f"mais {best_st['over_200']} cas restent >200 px."
        )
    else:
        lines.append("**Non** — le gain LOO est insuffisant pour généraliser.")

    lines.extend(
        [
            "",
            "### 2. Quelle méthode est la plus robuste ?",
            "",
            f"**{best.label}** ({best_id}) — plus faible erreur moyenne LOO "
            f"({format_num(best_st['mean'])} px) avec {best_st['improved']} cas améliorés vs "
            f"{best_st['degraded']} dégradés.",
            "",
            "### 3. Quelle erreur moyenne/médiane obtient-elle ?",
            "",
            f"- Mean : **{format_num(best_st['mean'])} px**",
            f"- Median : **{format_num(best_st['median'])} px**",
            f"- Std : {format_num(best_st['stdev'])} px",
            "",
            "### 4. Combien de cas restent >200 px ?",
            "",
            f"- V2 brut : **{raw_st['over_200']}/26**",
        ]
    )
    for m in learnable:
        st = m.stats(raw.errors)
        lines.append(f"- {m.label} : **{st['over_200']}/26**")

    lines.extend(
        [
            "",
            "### 5. Peut-on intégrer la correction comme post-traitement déterministe ?",
            "",
        ]
    )
    if verdict in ("FEASIBLE", "PARTIALLY FEASIBLE"):
        lines.append(
            f"**Oui{' (avec prudence)' if verdict == 'PARTIALLY FEASIBLE' else ''}.** "
            f"Paramètres calibrés sur N−1 cas, inférence basée uniquement sur landmarks V2 "
            f"(ASM_L, ASL_R, FHC_R/L). Pipeline déterministe sans ré-entraînement YOLO."
        )
    else:
        lines.append("**Non recommandé** sans stratégie adaptative ou garde-fous supplémentaires.")

    lines.extend(
        [
            "",
            "### 6. Existe-t-il des cas où la correction dégrade fortement ASL_L ?",
            "",
        ]
    )
    if degraded_cases:
        lines.append("**Oui** — cas avec dégradation >50 px vs V2 brut (pire méthode learnable) :")
        lines.append("")
        lines.append("| Cas | Méthode | V2 px | Δ dégradation |")
        lines.append("|-----|---------|-------|---------------|")
        for case_id, meth, r_err, delta in sorted(degraded_cases, key=lambda x: -x[3])[:10]:
            lines.append(f"| {case_id} | {meth} | {format_num(r_err)} | +{format_num(delta)} |")
    else:
        lines.append("**Non** — aucune dégradation >50 px détectée sur les méthodes learnables.")

    lines.extend(["", f"CSV : `{OUTPUT_CSV.name}`", ""])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    cases = load_cases()
    methods = run_loo(cases)
    raw = methods["A_v2_raw"]
    verdict, best_id, verdict_lines = assess_verdict(methods, raw)
    write_csv(methods, raw)
    write_md(methods, raw, verdict, best_id, verdict_lines)

    best = methods[best_id]
    best_st = best.stats(raw.errors)

    print("ASL_L REFINEMENT LOO COMPLETE")
    print(f"VERDICT: {verdict}")
    print(f"BEST_METHOD: {best_id} ({best.label})")
    print(f"LOO mean={best_st['mean']:.2f} px median={best_st['median']:.2f} px")
    print(f"REPORT={OUTPUT_MD.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
