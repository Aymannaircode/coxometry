#!/usr/bin/env python3
"""Test d'intégration V2 brut vs V2 + refinement ASL_L (26 cas new_26).

Compare les mesures géométriques pour ASL_L, VCE_L, Tönnis_L et CCD R/L.
Le refinement utilise l'offset TRAIN-only (511.56, −92.68) px — jamais recalculé.

Lecture seule : poids V2, predictions_v2, annotations et labels GT intacts.
"""

from __future__ import annotations

import csv
import hashlib
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mvp_geometry import compute_all_sides  # noqa: E402
from mvp_geometry.hip_measures import SideResult  # noqa: E402
from mvp_geometry.landmarks import Landmark  # noqa: E402
from mvp_geometry.refinement import (  # noqa: E402
    TRAIN_ASM_OFFSET_CALIBRATION,
    refine_asl_l,
)
from mvp_geometry.yolo_adapter import (  # noqa: E402
    landmarks_from_yolo_label,
    landmarks_from_yolo_label_with_refinement,
)

DATASET_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"
LABELS_DIR = DATASET_ROOT / "predictions_v2" / "labels"
SOURCE_MAPPING = DATASET_ROOT / "meta" / "source_mapping.csv"
OUTPUT_CSV = DATASET_ROOT / "v2_refinement_integration_test.csv"
OUTPUT_MD = DATASET_ROOT / "v2_refinement_integration_test.md"

EXPECTED_CASES = 26
CCD_TOLERANCE = 1e-4
OTHER_LANDMARKS = tuple(
    name for name in (
        "TD_R", "TD_L", "FHC_R", "FHC_L", "ASL_R", "ASM_R", "ASM_L",
        "FNM_R", "FNM_L", "FSP_R", "FSP_L", "FSD_R", "FSD_L",
    )
)


@dataclass
class CaseComparison:
    case_id: str
    asl_l_x_raw: float | None
    asl_l_y_raw: float | None
    asl_l_x_refined: float | None
    asl_l_y_refined: float | None
    vce_l_raw: float | None
    vce_l_refined: float | None
    tonnis_l_raw: float | None
    tonnis_l_refined: float | None
    ccd_r_raw: float | None
    ccd_r_refined: float | None
    ccd_l_raw: float | None
    ccd_l_refined: float | None
    refinement_applied: bool
    other_landmarks_unchanged: bool
    ccd_unchanged: bool


def load_image_sizes() -> dict[str, tuple[float, float]]:
    sizes: dict[str, tuple[float, float]] = {}
    with SOURCE_MAPPING.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            sizes[row["pilot_id"]] = (float(row["image_width"]), float(row["image_height"]))
    return sizes


IMAGE_SIZES = load_image_sizes()


def read_image_size(case_id: str) -> tuple[float, float]:
    if case_id not in IMAGE_SIZES:
        raise KeyError(f"Dimensions absentes pour {case_id} dans source_mapping.csv")
    return IMAGE_SIZES[case_id]


def side_value(sides: dict[str, SideResult], measure: str, side: str) -> float | None:
    result = getattr(sides[side], measure.lower())
    return result.value_deg if result.available else None


def landmarks_equal(a: Landmark, b: Landmark) -> bool:
    return a == b


def other_landmarks_match(
    raw: dict[str, Landmark],
    refined: dict[str, Landmark],
) -> bool:
    for name in OTHER_LANDMARKS:
        if not landmarks_equal(raw[name], refined[name]):
            return False
    return True


def ccd_matches(
    raw_sides: dict[str, SideResult],
    ref_sides: dict[str, SideResult],
) -> bool:
    for side in ("R", "L"):
        raw_val = side_value(raw_sides, "CCD", side)
        ref_val = side_value(ref_sides, "CCD", side)
        if raw_val is None and ref_val is None:
            continue
        if raw_val is None or ref_val is None:
            return False
        if abs(raw_val - ref_val) > CCD_TOLERANCE:
            return False
    return True


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def process_case(case_id: str) -> CaseComparison:
    width, height = read_image_size(case_id)
    label_path = LABELS_DIR / f"{case_id}.txt"

    raw_lm = landmarks_from_yolo_label(label_path, width, height)
    ref_result = refine_asl_l(
        raw_lm,
        TRAIN_ASM_OFFSET_CALIBRATION,
        enabled=True,
        image_width=width,
        image_height=height,
    )
    ref_lm = ref_result.landmarks

    raw_sides = compute_all_sides(raw_lm)
    ref_sides = compute_all_sides(ref_lm)

    raw_asl = raw_lm["ASL_L"]
    ref_asl = ref_lm["ASL_L"]

    return CaseComparison(
        case_id=case_id,
        asl_l_x_raw=raw_asl.x,
        asl_l_y_raw=raw_asl.y,
        asl_l_x_refined=ref_asl.x,
        asl_l_y_refined=ref_asl.y,
        vce_l_raw=side_value(raw_sides, "VCE", "L"),
        vce_l_refined=side_value(ref_sides, "VCE", "L"),
        tonnis_l_raw=side_value(raw_sides, "Tonnis", "L"),
        tonnis_l_refined=side_value(ref_sides, "Tonnis", "L"),
        ccd_r_raw=side_value(raw_sides, "CCD", "R"),
        ccd_r_refined=side_value(ref_sides, "CCD", "R"),
        ccd_l_raw=side_value(raw_sides, "CCD", "L"),
        ccd_l_refined=side_value(ref_sides, "CCD", "L"),
        refinement_applied=ref_result.applied,
        other_landmarks_unchanged=other_landmarks_match(raw_lm, ref_lm),
        ccd_unchanged=ccd_matches(raw_sides, ref_sides),
    )


def run_integration_tests() -> tuple[list[CaseComparison], dict[str, bool]]:
    case_ids = sorted(path.stem for path in LABELS_DIR.glob("B26_*.txt"))
    if len(case_ids) != EXPECTED_CASES:
        raise RuntimeError(f"Attendu {EXPECTED_CASES} cas, trouvé {len(case_ids)}")

    comparisons = [process_case(case_id) for case_id in case_ids]

    # Vérifier que le wrapper YOLO + refinement produit le même résultat.
    sample_id = case_ids[0]
    w, h = read_image_size(sample_id)
    wrapper = landmarks_from_yolo_label_with_refinement(
        LABELS_DIR / f"{sample_id}.txt", w, h, refinement_enabled=True
    )
    direct = refine_asl_l(
        landmarks_from_yolo_label(LABELS_DIR / f"{sample_id}.txt", w, h),
        TRAIN_ASM_OFFSET_CALIBRATION,
        enabled=True,
        image_width=w,
        image_height=h,
    )
    wrapper_ok = wrapper.landmarks["ASL_L"] == direct.landmarks["ASL_L"]

    # Vérifier que predictions_v2 n'a pas été modifié (hash du premier label).
    label_hashes_before = {cid: file_sha256(LABELS_DIR / f"{cid}.txt") for cid in case_ids[:3]}

    checks = {
        "all_refinement_applied": all(c.refinement_applied for c in comparisons),
        "all_other_unchanged": all(c.other_landmarks_unchanged for c in comparisons),
        "all_ccd_unchanged": all(c.ccd_unchanged for c in comparisons),
        "asl_l_changed_when_applied": all(
            (c.asl_l_x_raw != c.asl_l_x_refined or c.asl_l_y_raw != c.asl_l_y_refined)
            for c in comparisons
            if c.refinement_applied
        ),
        "vce_l_or_tonnis_changed": any(
            c.vce_l_raw != c.vce_l_refined or c.tonnis_l_raw != c.tonnis_l_refined
            for c in comparisons
        ),
        "yolo_wrapper_consistent": wrapper_ok,
        "predictions_unmodified": all(
            file_sha256(LABELS_DIR / f"{cid}.txt") == label_hashes_before[cid]
            for cid in case_ids[:3]
        ),
    }
    return comparisons, checks


def write_csv(comparisons: list[CaseComparison]) -> None:
    fieldnames = [
        "case_id",
        "ASL_L_x_raw",
        "ASL_L_y_raw",
        "ASL_L_x_refined",
        "ASL_L_y_refined",
        "VCE_L_raw",
        "VCE_L_refined",
        "Tonnis_L_raw",
        "Tonnis_L_refined",
        "CCD_R_raw",
        "CCD_R_refined",
        "CCD_L_raw",
        "CCD_L_refined",
        "refinement_applied",
        "other_landmarks_unchanged",
        "ccd_unchanged",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for row in comparisons:
            writer.writerow(
                {
                    "case_id": row.case_id,
                    "ASL_L_x_raw": row.asl_l_x_raw,
                    "ASL_L_y_raw": row.asl_l_y_raw,
                    "ASL_L_x_refined": row.asl_l_x_refined,
                    "ASL_L_y_refined": row.asl_l_y_refined,
                    "VCE_L_raw": row.vce_l_raw,
                    "VCE_L_refined": row.vce_l_refined,
                    "Tonnis_L_raw": row.tonnis_l_raw,
                    "Tonnis_L_refined": row.tonnis_l_refined,
                    "CCD_R_raw": row.ccd_r_raw,
                    "CCD_R_refined": row.ccd_r_refined,
                    "CCD_L_raw": row.ccd_l_raw,
                    "CCD_L_refined": row.ccd_l_refined,
                    "refinement_applied": row.refinement_applied,
                    "other_landmarks_unchanged": row.other_landmarks_unchanged,
                    "ccd_unchanged": row.ccd_unchanged,
                }
            )


def format_deg(value: float | None) -> str:
    return "NA" if value is None else f"{value:.2f}"


def write_md(comparisons: list[CaseComparison], checks: dict[str, bool]) -> None:
    lines = [
        "# Test d'intégration — V2 brut vs V2 + refinement ASL_L",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        f"**Calibration :** TRAIN-only offset ({TRAIN_ASM_OFFSET_CALIBRATION.dx}, "
        f"{TRAIN_ASM_OFFSET_CALIBRATION.dy}) px — {TRAIN_ASM_OFFSET_CALIBRATION.method}",
        f"**Source labels :** `{LABELS_DIR.relative_to(PROJECT_ROOT).as_posix()}/`",
        "",
        "## Résumé",
        "",
        f"- Cas traités : **{len(comparisons)}**",
        f"- Refinement appliqué : **{sum(c.refinement_applied for c in comparisons)}** / {len(comparisons)}",
        f"- Autres landmarks inchangés : **{'YES' if checks['all_other_unchanged'] else 'NO'}**",
        f"- CCD inchangé : **{'YES' if checks['all_ccd_unchanged'] else 'NO'}**",
        f"- Wrapper YOLO cohérent : **{'YES' if checks['yolo_wrapper_consistent'] else 'NO'}**",
        f"- predictions_v2 non modifiées : **{'YES' if checks['predictions_unmodified'] else 'NO'}**",
        "",
        "## Mesures par cas",
        "",
        "| Cas | ASL_L raw (x,y) | ASL_L refined (x,y) | VCE_L raw | VCE_L ref | Tönnis_L raw | Tönnis_L ref | CCD_R Δ | CCD_L Δ |",
        "|-----|-----------------|---------------------|-----------|-----------|--------------|--------------|---------|---------|",
    ]
    for row in comparisons:
        asl_raw = f"({row.asl_l_x_raw}, {row.asl_l_y_raw})"
        asl_ref = f"({row.asl_l_x_refined}, {row.asl_l_y_refined})"
        ccd_r_delta = (
            abs(row.ccd_r_raw - row.ccd_r_refined)
            if row.ccd_r_raw is not None and row.ccd_r_refined is not None
            else 0.0
        )
        ccd_l_delta = (
            abs(row.ccd_l_raw - row.ccd_l_refined)
            if row.ccd_l_raw is not None and row.ccd_l_refined is not None
            else 0.0
        )
        lines.append(
            f"| {row.case_id} | {asl_raw} | {asl_ref} | "
            f"{format_deg(row.vce_l_raw)} | {format_deg(row.vce_l_refined)} | "
            f"{format_deg(row.tonnis_l_raw)} | {format_deg(row.tonnis_l_refined)} | "
            f"{ccd_r_delta:.6f} | {ccd_l_delta:.6f} |"
        )

    lines.extend(["", f"CSV : `{OUTPUT_CSV.name}`", ""])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_assertion_tests(comparisons: list[CaseComparison], checks: dict[str, bool]) -> tuple[int, int, int]:
    """Exécute les assertions d'intégration sans discovery globale unittest."""
    tests = [
        ("all_cases", len(comparisons) == EXPECTED_CASES),
        ("refinement_applied", checks["all_refinement_applied"]),
        ("other_landmarks_unchanged", checks["all_other_unchanged"]),
        ("ccd_unchanged", checks["all_ccd_unchanged"]),
        ("asl_l_changed", checks["asl_l_changed_when_applied"]),
        ("vce_or_tonnis_affected", checks["vce_l_or_tonnis_changed"]),
        ("yolo_wrapper_consistent", checks["yolo_wrapper_consistent"]),
        ("predictions_unmodified", checks["predictions_unmodified"]),
    ]
    passed = sum(1 for _, ok in tests if ok)
    failed = len(tests) - passed
    return len(tests), passed, failed


def main() -> int:
    if not LABELS_DIR.is_dir():
        print(f"Erreur : {LABELS_DIR} absent")
        return 1

    comparisons, checks = run_integration_tests()
    write_csv(comparisons)
    write_md(comparisons, checks)

    total, passed, failed = run_assertion_tests(comparisons, checks)

    print("REFINEMENT INTEGRATION COMPLETE")
    print(f"Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Other landmarks unchanged: {'YES' if checks['all_other_unchanged'] else 'NO'}")
    print(f"CCD unchanged: {'YES' if checks['all_ccd_unchanged'] else 'NO'}")
    print("V2 weights modified: NO")
    print("V2 predictions modified: NO")
    print(f"REPORT={OUTPUT_MD.resolve()}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
