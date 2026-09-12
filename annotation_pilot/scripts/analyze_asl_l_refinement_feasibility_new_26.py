#!/usr/bin/env python3
"""Faisabilité d'un refinement ASL_L post-V2 (new_26) — lecture seule.

Analyse si l'erreur ASL_L V2 est suffisamment structurée pour un correctif
géométrique ou un module spécialisé, sans toucher labels, JSON, poids ni prédictions.
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
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "asl_l_refinement_feasibility.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "asl_l_refinement_feasibility.md"

LANDMARKS = [
    "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASL_L",
    "ASM_R", "ASM_L", "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L",
]
KEYPOINTS_START = 5
MIN_KEYPOINT_CONF = 0.25
EXPECTED_CASES = 26

# Seuils verdict
FEASIBLE_MEAN_REDUCTION = 0.50
FEASIBLE_MEDIAN_REDUCTION = 0.40
FEASIBLE_ORACLE_MEDIAN_PX = 80.0
PARTIAL_MEAN_REDUCTION = 0.25
PARTIAL_MEDIAN_REDUCTION = 0.20
STRUCTURED_CV_THRESHOLD = 0.35  # coef variation dx/W, dy/H


@dataclass
class CaseRecord:
    case_id: str
    width: float
    height: float
    gt: dict[str, tuple[float, float]]
    v2: dict[str, tuple[float, float]]
    dx: float
    dy: float
    dx_norm: float
    dy_norm: float
    error_px: float
    dist_v2_to_gt_asm_l: float
    dist_v2_to_gt_asl_l: float
    dist_gt_asm_to_gt_asl: float
    dist_v2_asm_to_v2_asl: float
    angle_gt_asm_asl_deg: float
    angle_v2_asm_asl_deg: float
    angle_error_deg: float
    pelvis_width_px: float
    v2_errors: dict[str, float] = field(default_factory=dict)


@dataclass
class BaselineResult:
    name: str
    description: str
    errors: list[float]
    mean: float
    median: float
    oracle: bool = False

    @classmethod
    def from_errors(cls, name: str, description: str, errors: list[float], oracle: bool = False) -> BaselineResult:
        return cls(
            name=name,
            description=description,
            errors=errors,
            mean=statistics.mean(errors),
            median=statistics.median(errors),
            oracle=oracle,
        )


def format_num(v: float | None, d: int = 2) -> str:
    return "NA" if v is None else f"{v:.{d}f}"


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def angle_deg(origin: tuple[float, float], target: tuple[float, float]) -> float:
    return math.degrees(math.atan2(target[1] - origin[1], target[0] - origin[0]))


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return None
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den_x = math.sqrt(sum((a - mx) ** 2 for a in x))
    den_y = math.sqrt(sum((b - my) ** 2 for b in y))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def circular_std_deg(angles: list[float]) -> float:
    if not angles:
        return float("nan")
    rads = [math.radians(a) for a in angles]
    sin_m = statistics.mean(math.sin(r) for r in rads)
    cos_m = statistics.mean(math.cos(r) for r in rads)
    R = math.hypot(sin_m, cos_m)
    if R <= 1e-9:
        return 180.0
    return math.degrees(math.sqrt(-2 * math.log(R)))


def coef_variation(values: list[float]) -> float:
    if not values:
        return float("nan")
    m = abs(statistics.mean(values))
    if m < 1e-9:
        return statistics.stdev(values) if len(values) >= 2 else 0.0
    return statistics.stdev(values) / m if len(values) >= 2 else 0.0


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


def build_records() -> list[CaseRecord]:
    records: list[CaseRecord] = []
    for json_path in sorted(ANNOT_DIR.glob("B26_*.json")):
        case_id = json_path.stem
        ann = json.loads(json_path.read_text(encoding="utf-8-sig"))
        w, h = image_dimensions(ann, case_id)
        gt = gt_points(ann)
        v2 = parse_v2(LABEL_DIR / f"{case_id}.txt", w, h)
        required = ("ASL_L", "ASM_L", "ASL_R", "FHC_L", "FHC_R", "FNM_L")
        for name in required:
            if name not in gt or name not in v2:
                raise ValueError(f"{case_id} : GT ou V2 manquant pour {name}")

        gt_asl, v2_asl = gt["ASL_L"], v2["ASL_L"]
        dx = v2_asl[0] - gt_asl[0]
        dy = v2_asl[1] - gt_asl[1]
        err = math.hypot(dx, dy)

        gt_asm, v2_asm = gt["ASM_L"], v2["ASM_L"]
        ang_gt = angle_deg(gt_asm, gt_asl)
        ang_v2 = angle_deg(v2_asm, v2_asl)

        v2_errors: dict[str, float] = {}
        for lm in ("ASL_R", "ASM_L", "FHC_L", "FNM_L"):
            if lm in gt and lm in v2:
                v2_errors[lm] = dist(v2[lm], gt[lm])

        records.append(
            CaseRecord(
                case_id=case_id,
                width=w,
                height=h,
                gt=gt,
                v2=v2,
                dx=dx,
                dy=dy,
                dx_norm=dx / w,
                dy_norm=dy / h,
                error_px=err,
                dist_v2_to_gt_asm_l=dist(v2_asl, gt_asm),
                dist_v2_to_gt_asl_l=err,
                dist_gt_asm_to_gt_asl=dist(gt_asm, gt_asl),
                dist_v2_asm_to_v2_asl=dist(v2_asm, v2_asl),
                angle_gt_asm_asl_deg=ang_gt,
                angle_v2_asm_asl_deg=ang_v2,
                angle_error_deg=ang_v2 - ang_gt,
                pelvis_width_px=dist(gt["FHC_R"], gt["FHC_L"]),
                v2_errors=v2_errors,
            )
        )
    if len(records) != EXPECTED_CASES:
        raise RuntimeError(f"Attendu {EXPECTED_CASES} cas, trouvé {len(records)}")
    return records


def apply_baselines(records: list[CaseRecord]) -> list[BaselineResult]:
    mean_dx = statistics.mean(r.dx for r in records)
    mean_dy = statistics.mean(r.dy for r in records)
    median_dx = statistics.median(r.dx for r in records)
    median_dy = statistics.median(r.dy for r in records)

    gt_offsets = [(r.gt["ASL_L"][0] - r.gt["ASM_L"][0], r.gt["ASL_L"][1] - r.gt["ASM_L"][1]) for r in records]
    mean_off_x = statistics.mean(o[0] for o in gt_offsets)
    mean_off_y = statistics.mean(o[1] for o in gt_offsets)

    results: list[BaselineResult] = []

    # 0 — V2 brut
    results.append(
        BaselineResult.from_errors(
            "v2_raw",
            "V2 ASL_L sans correction",
            [r.error_px for r in records],
        )
    )

    # 1 — translation moyenne
    trans_mean_err = [
        dist((r.v2["ASL_L"][0] - mean_dx, r.v2["ASL_L"][1] - mean_dy), r.gt["ASL_L"]) for r in records
    ]
    results.append(
        BaselineResult.from_errors(
            "translation_mean",
            f"Soustraire dx/dy moyens ({format_num(mean_dx)}, {format_num(mean_dy)}) px",
            trans_mean_err,
        )
    )

    # 1b — translation médiane
    trans_med_err = [
        dist((r.v2["ASL_L"][0] - median_dx, r.v2["ASL_L"][1] - median_dy), r.gt["ASL_L"]) for r in records
    ]
    results.append(
        BaselineResult.from_errors(
            "translation_median",
            f"Soustraire dx/dy médians ({format_num(median_dx)}, {format_num(median_dy)}) px",
            trans_med_err,
        )
    )

    # 2 — correction relative ASM_L (vecteur GT moyen depuis V2_ASM_L)
    asm_global_err = [
        dist((r.v2["ASM_L"][0] + mean_off_x, r.v2["ASM_L"][1] + mean_off_y), r.gt["ASL_L"]) for r in records
    ]
    results.append(
        BaselineResult.from_errors(
            "asm_global_offset",
            "V2_ASM_L + vecteur moyen (GT_ASL_L − GT_ASM_L) sur 26 cas",
            asm_global_err,
        )
    )

    # 3 — oracle ASM_L par cas (borne supérieure géométrie locale)
    asm_oracle_err = [
        dist(
            (r.v2["ASM_L"][0] + (r.gt["ASL_L"][0] - r.gt["ASM_L"][0]),
             r.v2["ASM_L"][1] + (r.gt["ASL_L"][1] - r.gt["ASM_L"][1])),
            r.gt["ASL_L"],
        )
        for r in records
    ]
    results.append(
        BaselineResult.from_errors(
            "asm_oracle_per_case",
            "V2_ASM_L + (GT_ASL_L − GT_ASM_L) par cas [oracle]",
            asm_oracle_err,
            oracle=True,
        )
    )

    # 4 — miroir ASL_R via midline FHC
    mirror_err: list[float] = []
    for r in records:
        mid_x = (r.gt["FHC_R"][0] + r.gt["FHC_L"][0]) / 2.0
        v2_asl_r = r.v2["ASL_R"]
        mirrored = (2 * mid_x - v2_asl_r[0], v2_asl_r[1])
        mirror_err.append(dist(mirrored, r.gt["ASL_L"]))
    results.append(
        BaselineResult.from_errors(
            "mirror_asl_r_fhc",
            "Réflexion V2_ASL_R par rapport à la midline FHC_R/FHC_L",
            mirror_err,
        )
    )

    # 4b — miroir + translation résiduelle moyenne
    mirror_res_err: list[float] = []
    mirror_pts = []
    for r in records:
        mid_x = (r.gt["FHC_R"][0] + r.gt["FHC_L"][0]) / 2.0
        mirrored = (2 * mid_x - r.v2["ASL_R"][0], r.v2["ASL_R"][1])
        mirror_pts.append(mirrored)
    res_dx = [p[0] - r.gt["ASL_L"][0] for p, r in zip(mirror_pts, records)]
    res_dy = [p[1] - r.gt["ASL_L"][1] for p, r in zip(mirror_pts, records)]
    mrdx, mrdy = statistics.mean(res_dx), statistics.mean(res_dy)
    for p, r in zip(mirror_pts, records):
        corrected = (p[0] - mrdx, p[1] - mrdy)
        mirror_res_err.append(dist(corrected, r.gt["ASL_L"]))
    results.append(
        BaselineResult.from_errors(
            "mirror_asl_r_calibrated",
            "Miroir ASL_R + calibration translation résiduelle moyenne",
            mirror_res_err,
        )
    )

    # 5 — géométrie sourcil : prolonger depuis V2_ASM_L avec longueur/angle GT moyens
    gt_lengths = [r.dist_gt_asm_to_gt_asl for r in records]
    gt_angles = [r.angle_gt_asm_asl_deg for r in records]
    mean_len = statistics.mean(gt_lengths)
    mean_ang = statistics.mean(gt_angles)
    sourcil_mean_err = []
    for r in records:
        rad = math.radians(mean_ang)
        corrected = (
            r.v2["ASM_L"][0] + mean_len * math.cos(rad),
            r.v2["ASM_L"][1] + mean_len * math.sin(rad),
        )
        sourcil_mean_err.append(dist(corrected, r.gt["ASL_L"]))
    results.append(
        BaselineResult.from_errors(
            "eyebrow_global_polar",
            "V2_ASM_L + longueur/angle moyens GT (ASM_L→ASL_L)",
            sourcil_mean_err,
        )
    )

    # 5b — sourcil oracle angle+length par cas depuis V2_ASM
    sourcil_oracle_err = []
    for r in records:
        corrected = (
            r.v2["ASM_L"][0] + r.dist_gt_asm_to_gt_asl * math.cos(math.radians(r.angle_gt_asm_asl_deg)),
            r.v2["ASM_L"][1] + r.dist_gt_asm_to_gt_asl * math.sin(math.radians(r.angle_gt_asm_asl_deg)),
        )
        sourcil_oracle_err.append(dist(corrected, r.gt["ASL_L"]))
    results.append(
        BaselineResult.from_errors(
            "eyebrow_oracle_polar",
            "V2_ASM_L + longueur/angle GT par cas [oracle]",
            sourcil_oracle_err,
            oracle=True,
        )
    )

    # 6 — blend V2_ASL_L vers V2_ASM_L + offset global (50% correction)
    blend_err = []
    for r in records:
        target = (r.v2["ASM_L"][0] + mean_off_x, r.v2["ASM_L"][1] + mean_off_y)
        corrected = (
            0.5 * r.v2["ASL_L"][0] + 0.5 * target[0],
            0.5 * r.v2["ASL_L"][1] + 0.5 * target[1],
        )
        blend_err.append(dist(corrected, r.gt["ASL_L"]))
    results.append(
        BaselineResult.from_errors(
            "blend50_asm_global",
            "50% V2_ASL_L + 50% (V2_ASM_L + offset GT moyen)",
            blend_err,
        )
    )

    return results


def assess_verdict(
    records: list[CaseRecord],
    baselines: list[BaselineResult],
) -> tuple[str, list[str]]:
    raw = next(b for b in baselines if b.name == "v2_raw")
    learnable = [b for b in baselines if not b.oracle]
    best_learnable = min(learnable, key=lambda b: b.mean)
    asm_oracle = next(b for b in baselines if b.name == "asm_oracle_per_case")
    eyebrow_oracle = next(b for b in baselines if b.name == "eyebrow_oracle_polar")

    mean_red = 1 - best_learnable.mean / raw.mean
    med_red = 1 - best_learnable.median / raw.median

    dx_cv = coef_variation([r.dx_norm for r in records])
    dy_cv = coef_variation([r.dy_norm for r in records])
    ang_std = circular_std_deg([r.angle_error_deg for r in records])

    closer_asm = sum(1 for r in records if r.dist_v2_to_gt_asm_l < r.dist_v2_to_gt_asl_l)
    dx_same_sign = max(
        sum(1 for r in records if r.dx < 0),
        sum(1 for r in records if r.dx > 0),
    )

    lines = [
        f"Erreur V2 brute : mean={format_num(raw.mean)} px, median={format_num(raw.median)} px",
        f"Meilleure baseline learnable : **{best_learnable.name}** "
        f"(mean={format_num(best_learnable.mean)}, median={format_num(best_learnable.median)})",
        f"Réduction vs V2 : mean **{mean_red*100:.1f}%**, median **{med_red*100:.1f}%**",
        f"Oracle ASM-relative : median={format_num(asm_oracle.median)} px",
        f"Oracle sourcil polaire : median={format_num(eyebrow_oracle.median)} px",
        f"V2_ASL_L plus proche GT_ASM_L que GT_ASL_L : **{closer_asm}/{len(records)}** cas",
        f"Biais dx cohérent (même signe) : **{dx_same_sign}/{len(records)}** cas",
        f"CV dx/W={format_num(dx_cv, 3)}, CV dy/H={format_num(dy_cv, 3)}, écart angular ASM→ASL={format_num(ang_std, 1)}°",
    ]

    structured = (
        dx_cv <= STRUCTURED_CV_THRESHOLD
        or dy_cv <= STRUCTURED_CV_THRESHOLD
        or dx_same_sign >= len(records) * 0.75
        or closer_asm >= len(records) * 0.5
    )

    if (
        mean_red >= FEASIBLE_MEAN_REDUCTION
        and med_red >= FEASIBLE_MEDIAN_REDUCTION
        and best_learnable.median < 150
    ):
        verdict = "FEASIBLE"
        lines.append(
            "Une correction simple (translation ou offset ASM global) réduit fortement l'erreur "
            "avec un biais structuré — refinement post-V2 recommandable."
        )
    elif (
        asm_oracle.median <= FEASIBLE_ORACLE_MEDIAN_PX
        or eyebrow_oracle.median <= FEASIBLE_ORACLE_MEDIAN_PX
    ) and structured:
        if mean_red >= PARTIAL_MEAN_REDUCTION or med_red >= PARTIAL_MEDIAN_REDUCTION:
            verdict = "PARTIALLY FEASIBLE"
            lines.append(
                "La géométrie locale (ASM_L → ASL_L) explique une grande partie de l'erreur (oracle bas), "
                "mais les baselines learnables globales n'atteignent pas un gain suffisant seules — "
                "envisager un refinement conditionnel (résolution, erreurs voisins, ASM_L V2)."
            )
        else:
            verdict = "PARTIALLY FEASIBLE"
            lines.append(
                "Erreur fortement liée à la géométrie ASM/ASL (oracle bas) mais corrections globales faibles — "
                "refinement nécessiterait un modèle contextuel par cas."
            )
    elif mean_red >= PARTIAL_MEAN_REDUCTION or med_red >= PARTIAL_MEDIAN_REDUCTION:
        verdict = "PARTIALLY FEASIBLE"
        lines.append(
            "Amélioration partielle par correction simple ; variance résiduelle élevée — "
            "refinement limité ou hybride V2+heuristique."
        )
    else:
        verdict = "NOT FEASIBLE"
        lines.append(
            "Aucune baseline simple ne réduit suffisamment l'erreur ; biais peu structuré pour un post-traitement fiable."
        )

    return verdict, lines


def write_csv(records: list[CaseRecord], baselines: list[BaselineResult], correlations: list[dict]) -> None:
    rows: list[dict[str, str | float]] = []

    for r in records:
        rows.append(
            {
                "section": "case",
                "case_id": r.case_id,
                "width": r.width,
                "height": r.height,
                "dx": r.dx,
                "dy": r.dy,
                "dx_norm": r.dx_norm,
                "dy_norm": r.dy_norm,
                "error_px": r.error_px,
                "dist_v2_to_gt_asm_l": r.dist_v2_to_gt_asm_l,
                "dist_v2_to_gt_asl_l": r.dist_v2_to_gt_asl_l,
                "dist_gt_asm_to_gt_asl": r.dist_gt_asm_to_gt_asl,
                "dist_v2_asm_to_v2_asl": r.dist_v2_asm_to_v2_asl,
                "angle_gt_asm_asl_deg": r.angle_gt_asm_asl_deg,
                "angle_v2_asm_asl_deg": r.angle_v2_asm_asl_deg,
                "angle_error_deg": r.angle_error_deg,
                "pelvis_width_px": r.pelvis_width_px,
                "v2_err_asl_r": r.v2_errors.get("ASL_R"),
                "v2_err_asm_l": r.v2_errors.get("ASM_L"),
                "v2_err_fhc_l": r.v2_errors.get("FHC_L"),
                "v2_err_fnm_l": r.v2_errors.get("FNM_L"),
            }
        )

    for b in baselines:
        rows.append(
            {
                "section": "baseline_summary",
                "baseline": b.name,
                "description": b.description,
                "mean_error_px": b.mean,
                "median_error_px": b.median,
                "oracle": b.oracle,
            }
        )
        for r, err in zip(records, b.errors):
            rows.append(
                {
                    "section": "baseline_per_case",
                    "baseline": b.name,
                    "case_id": r.case_id,
                    "error_px": err,
                }
            )

    for c in correlations:
        rows.append({"section": "correlation", **c})

    fieldnames = sorted({k for row in rows for k in row.keys()})
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def compute_correlations(records: list[CaseRecord]) -> list[dict]:
    err = [r.error_px for r in records]
    out: list[dict] = []
    for key, label in (
        ("ASL_R", "v2_err_asl_r"),
        ("ASM_L", "v2_err_asm_l"),
        ("FHC_L", "v2_err_fhc_l"),
        ("FNM_L", "v2_err_fnm_l"),
    ):
        vals = [r.v2_errors[key] for r in records if key in r.v2_errors]
        if len(vals) == len(records):
            out.append({"variable": label, "pearson_vs_asl_l_error": pearson(err, vals)})

    for label, xs in (
        ("image_width", [r.width for r in records]),
        ("image_height", [r.height for r in records]),
        ("pelvis_width_px", [r.pelvis_width_px for r in records]),
        ("dist_gt_asm_to_gt_asl", [r.dist_gt_asm_to_gt_asl for r in records]),
        ("dist_v2_asm_to_v2_asl", [r.dist_v2_asm_to_v2_asl for r in records]),
    ):
        out.append({"variable": label, "pearson_vs_asl_l_error": pearson(err, xs)})

    return out


def write_md(
    records: list[CaseRecord],
    baselines: list[BaselineResult],
    correlations: list[dict],
    verdict: str,
    verdict_lines: list[str],
) -> None:
    raw = next(b for b in baselines if b.name == "v2_raw")
    dx_vals = [r.dx for r in records]
    dy_vals = [r.dy for r in records]

    lines = [
        "# Faisabilité refinement ASL_L post-V2 (new_26)",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        "**Mode :** lecture seule — V2 intact, aucun entraînement",
        "",
        f"## Verdict : **{verdict}**",
        "",
    ]
    lines.extend(f"- {line}" for line in verdict_lines)

    lines.extend(
        [
            "",
            "## 1. Erreur vectorielle ASL_L (V2 − GT)",
            "",
            f"| Métrique | dx (px) | dy (px) | dx/W | dy/H | error_px |",
            f"|----------|---------|---------|------|------|----------|",
            f"| Moyenne | {format_num(statistics.mean(dx_vals))} | {format_num(statistics.mean(dy_vals))} | "
            f"{format_num(statistics.mean(r.dx_norm for r in records), 4)} | "
            f"{format_num(statistics.mean(r.dy_norm for r in records), 4)} | {format_num(raw.mean)} |",
            f"| Médiane | {format_num(statistics.median(dx_vals))} | {format_num(statistics.median(dy_vals))} | "
            f"{format_num(statistics.median(r.dx_norm for r in records), 4)} | "
            f"{format_num(statistics.median(r.dy_norm for r in records), 4)} | {format_num(raw.median)} |",
            "",
            "## 2. Relations spatiales",
            "",
            f"- V2_ASL_L plus proche **GT_ASM_L** que GT_ASL_L : "
            f"**{sum(1 for r in records if r.dist_v2_to_gt_asm_l < r.error_px)}/{len(records)}** cas",
            f"- Distance moyenne V2_ASL_L → GT_ASM_L : "
            f"**{format_num(statistics.mean(r.dist_v2_to_gt_asm_l for r in records))}** px",
            f"- Distance moyenne V2_ASL_L → GT_ASL_L : **{format_num(raw.mean)}** px",
            f"- Longueur moyenne GT ASM_L→ASL_L : "
            f"**{format_num(statistics.mean(r.dist_gt_asm_to_gt_asl for r in records))}** px",
            f"- Longueur moyenne V2 ASM_L→ASL_L : "
            f"**{format_num(statistics.mean(r.dist_v2_asm_to_v2_asl for r in records))}** px",
            f"- Écart angular moyen vecteur ASM→ASL (V2 vs GT) : "
            f"**{format_num(statistics.mean(abs(r.angle_error_deg) for r in records))}**°",
            "",
            "## 3. Corrélations (Pearson vs error_px ASL_L)",
            "",
            "| Variable | r |",
            "|----------|---|",
        ]
    )
    for c in correlations:
        r_val = c.get("pearson_vs_asl_l_error")
        lines.append(f"| {c['variable']} | {format_num(r_val, 3) if r_val is not None else 'NA'} |")

    lines.extend(
        [
            "",
            "## 4. Baselines de correction simple",
            "",
            "| Baseline | Mean px | Median px | Δ mean vs V2 | Oracle |",
            "|----------|---------|-----------|--------------|--------|",
        ]
    )
    for b in baselines:
        delta = (1 - b.mean / raw.mean) * 100
        lines.append(
            f"| {b.name} | {format_num(b.mean)} | {format_num(b.median)} | "
            f"{format_num(delta, 1)}% | {'oui' if b.oracle else 'non'} |"
        )

    lines.extend(
        [
            "",
            "## 5. Détail par cas (V2 brut)",
            "",
            "| Cas | error | dx | dy | dist→GT_ASM | angle_err ASM→ASL | pelvis_w |",
            "|-----|-------|----|----|-------------|-------------------|----------|",
        ]
    )
    for r in sorted(records, key=lambda x: x.error_px, reverse=True):
        lines.append(
            f"| {r.case_id} | {format_num(r.error_px)} | {format_num(r.dx)} | {format_num(r.dy)} | "
            f"{format_num(r.dist_v2_to_gt_asm_l)} | {format_num(r.angle_error_deg, 1)} | "
            f"{format_num(r.pelvis_width_px)} |"
        )

    lines.extend(
        [
            "",
            "## 6. Recommandation stratégique",
            "",
            "- **Conserver V2** comme détecteur principal (26/26, conf box ~0.89).",
            "- Envisager un **refinement ASL_L uniquement** si verdict FEASIBLE ou PARTIALLY FEASIBLE.",
            "- V4 est **NO-GO** — ne pas remplacer V2 par fine-tuning global.",
            "",
            f"CSV : `{OUTPUT_CSV.name}`",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    records = build_records()
    baselines = apply_baselines(records)
    correlations = compute_correlations(records)
    verdict, verdict_lines = assess_verdict(records, baselines)
    write_csv(records, baselines, correlations)
    write_md(records, baselines, correlations, verdict, verdict_lines)

    raw = next(b for b in baselines if b.name == "v2_raw")
    best = min((b for b in baselines if not b.oracle), key=lambda b: b.mean)

    print("ASL_L REFINEMENT FEASIBILITY COMPLETE")
    print(f"VERDICT={verdict}")
    print(f"V2 mean error: {raw.mean:.2f} px")
    print(f"Best learnable baseline: {best.name} mean={best.mean:.2f} px median={best.median:.2f} px")
    print(f"REPORT={OUTPUT_MD.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
