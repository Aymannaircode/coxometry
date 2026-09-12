#!/usr/bin/env python3
"""Audit lecture seule du flip horizontal — compatibilité R/L (new_26).

Simule le flip Ultralytics sur les labels train et vérifie flip_idx,
dataset.yaml et args V2. Ne modifie aucun fichier.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent
DATASET_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"
DATASET_YAML = DATASET_ROOT / "dataset.yaml"
KEYPOINT_ORDER_MD = DATASET_ROOT / "meta" / "keypoint_order.md"
PREPARE_SCRIPT = SCRIPTS_DIR / "prepare_yolo_pose_new_26.py"
V2_ARGS_YAML = (
    PROJECT_ROOT / "runs" / "pose" / "runs" / "pose" / "runs" / "yolo_pose_new_26_v2-3" / "args.yaml"
)
TRAIN_LABEL_DIR = DATASET_ROOT / "labels" / "train"
OUTPUT_CSV = DATASET_ROOT / "horizontal_flip_audit.csv"
OUTPUT_MD = DATASET_ROOT / "horizontal_flip_audit.md"

sys.path.insert(0, str(SCRIPTS_DIR.parent / "manual_annotation_tool"))
import server  # noqa: E402

KEYPOINT_NAMES = [name for _, name, _ in server.LANDMARKS]
NKPT = len(KEYPOINT_NAMES)
NDIM = 3
EXPECTED_LABEL_COLS = 5 + NKPT * NDIM
KEYPOINTS_START = 5
COORD_TOLERANCE = 1e-5

# Paires R/L attendues (nom R, nom L, index R, index L)
RL_PAIRS = [
    ("TD_R", "TD_L", 0, 1),
    ("FHC_R", "FHC_L", 2, 3),
    ("ASL_R", "ASL_L", 4, 5),
    ("ASM_R", "ASM_L", 6, 7),
    ("FNM_R", "FNM_L", 8, 9),
    ("FSP_R", "FSP_L", 10, 11),
    ("FSD_R", "FSD_L", 12, 13),
]
PREPARE_FLIP_IDX = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12]
# Erreur typique : permuter ASL↔ASM au lieu de R↔L sur le côté gauche
WRONG_ASL_ASM_FLIP_IDX = [1, 0, 3, 2, 7, 6, 5, 4, 9, 8, 11, 10, 13, 12]


@dataclass
class Keypoint:
    name: str
    x: float
    y: float
    v: float


@dataclass
class PairCheck:
    case_id: str
    pair_name: str
    r_index: int
    l_index: int
    r_to_l_x_error: float
    r_to_l_y_error: float
    l_to_r_x_error: float
    l_to_r_y_error: float
    max_error: float
    ok: bool


@dataclass
class CaseFlipResult:
    case_id: str
    pair_checks: list[PairCheck] = field(default_factory=list)
    bbox_cx_error: float = 0.0
    all_ok: bool = True


def format_num(value: float | None, digits: int = 6) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def load_dataset_yaml() -> dict:
    return yaml.safe_load(DATASET_YAML.read_text(encoding="utf-8"))


def load_v2_args() -> dict:
    if not V2_ARGS_YAML.is_file():
        return {}
    return yaml.safe_load(V2_ARGS_YAML.read_text(encoding="utf-8"))


def expected_flip_idx_from_pairs() -> list[int]:
    mapping = list(range(NKPT))
    for _, _, r_idx, l_idx in RL_PAIRS:
        mapping[r_idx] = l_idx
        mapping[l_idx] = r_idx
    return mapping


def parse_label(path: Path) -> tuple[list[float], list[Keypoint]]:
    values = [float(part) for part in path.read_text(encoding="utf-8").strip().split()]
    if len(values) != EXPECTED_LABEL_COLS:
        raise ValueError(f"{path.name}: {len(values)} colonnes, attendu {EXPECTED_LABEL_COLS}")
    keypoints: list[Keypoint] = []
    for index, name in enumerate(KEYPOINT_NAMES):
        base = KEYPOINTS_START + index * NDIM
        keypoints.append(Keypoint(name, values[base], values[base + 1], values[base + 2]))
    return values[:5], keypoints


def simulate_ultralytics_fliplr(keypoints: list[Keypoint], flip_idx: list[int]) -> list[Keypoint]:
    """Reproduit RandomFlip Ultralytics : miroir x puis permutation flip_idx."""
    mirrored = [
        Keypoint(kp.name, 1.0 - kp.x, kp.y, kp.v)
        for kp in keypoints
    ]
    flipped: list[Keypoint] = []
    for target_index, name in enumerate(KEYPOINT_NAMES):
        source_index = flip_idx[target_index]
        src = mirrored[source_index]
        flipped.append(Keypoint(name, src.x, src.y, src.v))
    return flipped


def check_pair(case_id: str, original: list[Keypoint], flipped: list[Keypoint], pair: tuple[str, str, int, int]) -> PairCheck:
    r_name, l_name, r_idx, l_idx = pair
    orig_r, orig_l = original[r_idx], original[l_idx]
    flip_r, flip_l = flipped[r_idx], flipped[l_idx]

    # Après flip : slot R reçoit miroir de L ; slot L reçoit miroir de R
    expected_r_x, expected_r_y = 1.0 - orig_l.x, orig_l.y
    expected_l_x, expected_l_y = 1.0 - orig_r.x, orig_r.y

    r_x_err = abs(flip_r.x - expected_r_x)
    r_y_err = abs(flip_r.y - expected_r_y)
    l_x_err = abs(flip_l.x - expected_l_x)
    l_y_err = abs(flip_l.y - expected_l_y)
    max_err = max(r_x_err, r_y_err, l_x_err, l_y_err)

    return PairCheck(
        case_id=case_id,
        pair_name=f"{r_name}/{l_name}",
        r_index=r_idx,
        l_index=l_idx,
        r_to_l_x_error=r_x_err,
        r_to_l_y_error=r_y_err,
        l_to_r_x_error=l_x_err,
        l_to_r_y_error=l_y_err,
        max_error=max_err,
        ok=max_err <= COORD_TOLERANCE,
    )


def audit_case(label_path: Path, flip_idx: list[int]) -> CaseFlipResult:
    case_id = label_path.stem
    bbox, keypoints = parse_label(label_path)
    flipped = simulate_ultralytics_fliplr(keypoints, flip_idx)
    result = CaseFlipResult(case_id=case_id)

    for pair in RL_PAIRS:
        check = check_pair(case_id, keypoints, flipped, pair)
        result.pair_checks.append(check)
        if not check.ok:
            result.all_ok = False

    cx = bbox[1]
    result.bbox_cx_error = abs((1.0 - cx) - (1.0 - cx))  # miroir bbox : cx' = 1 - cx
    return result


def flip_idx_pair_errors(flip_idx: list[int]) -> list[tuple[str, int, int, int]]:
    """Retourne les paires mal mappées vs anatomie attendue."""
    errors: list[tuple[str, int, int, int]] = []
    expected = expected_flip_idx_from_pairs()
    for i, (exp, got) in enumerate(zip(expected, flip_idx)):
        if exp != got:
            errors.append((KEYPOINT_NAMES[i], i, exp, got))
    return errors


def determine_verdict(
    dataset: dict,
    v2_args: dict,
    flip_idx: list[int],
    simulation_ok: bool,
    idx_errors: list[tuple[str, int, int, int]],
) -> tuple[str, str]:
    kpt_shape = dataset.get("kpt_shape", [])
    fliplr = float(v2_args.get("fliplr", 0.0) or 0.0)
    flipud = float(v2_args.get("flipud", 0.0) or 0.0)

    if not flip_idx or len(flip_idx) != NKPT:
        return "C", "flip_idx absent ou longueur incorrecte — flip horizontal ambigu ou désactivé."

    if fliplr > 0 and len(flip_idx) == 0:
        return "C", "fliplr > 0 sans flip_idx — Ultralytics désactiverait le flip (comportement ambigu)."

    if flip_idx == WRONG_ASL_ASM_FLIP_IDX:
        return "B", "flip_idx permute ASL↔ASM au lieu de ASL_R↔ASL_L — configuration R/L incorrecte."

    if idx_errors or not simulation_ok:
        detail = ", ".join(f"{name}[{i}] attendu→{exp} obtenu→{got}" for name, i, exp, got in idx_errors[:4])
        return "B", f"flip_idx ou simulation incompatible avec les paires R/L ({detail or 'erreurs numériques'})."

    if kpt_shape != [NKPT, 3]:
        return "C", f"kpt_shape inattendu {kpt_shape}."

    return (
        "D",
        "Flip horizontal correctement configuré (flip_idx, paires R/L, simulation x'=1-x). "
        "Compte tenu du diagnostic V2 (ASL_L ~538 px sur TRAIN, ASL_R/ASM_L corrects, mapping validé), "
        "le flip n'est probablement pas la cause principale de l'échec ASL_L.",
    )


def write_csv(
    flip_idx: list[int],
    case_results: list[CaseFlipResult],
    idx_errors: list[tuple[str, int, int, int]],
    verdict: str,
) -> None:
    rows: list[dict[str, str]] = []

    rows.append({"section": "summary", "case_id": "", "pair": "verdict", "field": "value", "value": verdict})
    rows.append({"section": "summary", "case_id": "", "pair": "flip_idx", "field": "value", "value": str(flip_idx)})
    rows.append(
        {
            "section": "summary",
            "case_id": "",
            "pair": "rl_pairs_checked",
            "field": "count",
            "value": str(len(RL_PAIRS)),
        }
    )

    for name, i, exp, got in idx_errors:
        rows.append(
            {
                "section": "flip_idx_error",
                "case_id": "",
                "pair": name,
                "field": f"index_{i}",
                "value": f"expected={exp} got={got}",
            }
        )

    for pair in RL_PAIRS:
        r_name, l_name, r_idx, l_idx = pair
        rows.append(
            {
                "section": "pair_mapping",
                "case_id": "",
                "pair": f"{r_name}/{l_name}",
                "field": "flip_idx_R",
                "value": str(flip_idx[r_idx]),
            }
        )
        rows.append(
            {
                "section": "pair_mapping",
                "case_id": "",
                "pair": f"{r_name}/{l_name}",
                "field": "flip_idx_L",
                "value": str(flip_idx[l_idx]),
            }
        )
        rows.append(
            {
                "section": "pair_mapping",
                "case_id": "",
                "pair": f"{r_name}/{l_name}",
                "field": "expected_swap",
                "value": f"{r_idx}<->{l_idx}",
            }
        )

    for case in case_results:
        for check in case.pair_checks:
            rows.append(
                {
                    "section": "simulation",
                    "case_id": case.case_id,
                    "pair": check.pair_name,
                    "field": "max_error",
                    "value": format_num(check.max_error),
                }
            )
            rows.append(
                {
                    "section": "simulation",
                    "case_id": case.case_id,
                    "pair": check.pair_name,
                    "field": "ok",
                    "value": str(check.ok),
                }
            )

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["section", "case_id", "pair", "field", "value"])
        writer.writeheader()
        writer.writerows(rows)


def write_md(
    dataset: dict,
    v2_args: dict,
    flip_idx: list[int],
    case_results: list[CaseFlipResult],
    idx_errors: list[tuple[str, int, int, int]],
    verdict: str,
    verdict_detail: str,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    simulation_ok = all(c.all_ok for c in case_results)
    kpt_names = dataset.get("kpt_names", {}).get(0, KEYPOINT_NAMES)

    lines = [
        "# Audit flip horizontal — new_26",
        "",
        f"**Généré :** {now}",
        "**Mode :** lecture seule",
        "",
        f"## Verdict : **{verdict}**",
        "",
        verdict_detail,
        "",
        "## Configuration Ultralytics V2",
        "",
        "| Paramètre | Valeur | Source |",
        "|-----------|--------|--------|",
        f"| fliplr | **{v2_args.get('fliplr', 'NA')}** | `{V2_ARGS_YAML.relative_to(PROJECT_ROOT).as_posix()}` |",
        f"| flipud | **{v2_args.get('flipud', 'NA')}** | args.yaml |",
        f"| mosaic | **{v2_args.get('mosaic', 'NA')}** | args.yaml |",
        f"| auto_augment | **{v2_args.get('auto_augment', 'NA')}** | args.yaml |",
        f"| erasing | **{v2_args.get('erasing', 'NA')}** | args.yaml |",
        f"| data | `{v2_args.get('data', 'NA')}` | args.yaml |",
        "",
        "## Dataset pose (`dataset.yaml`)",
        "",
        f"- **kpt_shape :** `{dataset.get('kpt_shape')}`",
        f"- **flip_idx :** `{flip_idx}`",
        f"- **prepare_yolo FLIP_IDX :** `{PREPARE_FLIP_IDX}`",
        f"- **flip_idx == prepare :** {'Oui' if flip_idx == PREPARE_FLIP_IDX else 'Non'}",
        "",
        "### kpt_names",
        "",
        "| Index | Nom |",
        "|------:|-----|",
    ]
    for i, name in enumerate(kpt_names):
        lines.append(f"| {i} | {name} |")

    lines.extend(
        [
            "",
            "## Mapping flip_idx attendu (7 paires R/L)",
            "",
            "Ultralytics applique : `x' = w - x` puis `kpt[i] = kpt_mirrored[flip_idx[i]]`.",
            "",
            "| Paire | Index R | Index L | flip_idx[R]→ | flip_idx[L]→ | Attendu |",
            "|-------|--------:|--------:|-------------:|-------------:|---------|",
        ]
    )
    for r_name, l_name, r_idx, l_idx in RL_PAIRS:
        ok = flip_idx[r_idx] == l_idx and flip_idx[l_idx] == r_idx
        lines.append(
            f"| {r_name}↔{l_name} | {r_idx} | {l_idx} | {flip_idx[r_idx]} | {flip_idx[l_idx]} | "
            f"{'OK' if ok else 'ERREUR'} |"
        )

    lines.extend(
        [
            "",
            "### Vérification ASL / ASM (confusion potentielle)",
            "",
            f"- flip_idx[4] (ASL_R) = **{flip_idx[4]}** — attendu **5** (ASL_L), pas 7 (ASM_L)",
            f"- flip_idx[5] (ASL_L) = **{flip_idx[5]}** — attendu **4** (ASL_R), pas 6 (ASM_R)",
            f"- flip_idx[6] (ASM_R) = **{flip_idx[6]}** — attendu **7** (ASM_L)",
            f"- flip_idx[7] (ASM_L) = **{flip_idx[7]}** — attendu **6** (ASM_R)",
            "",
            f"- Pattern ASL↔ASM inversé ? **{'Oui' if flip_idx == WRONG_ASL_ASM_FLIP_IDX else 'Non'}**",
            "",
            "## Simulation sur labels TRAIN",
            "",
            f"- Cas audités : **{len(case_results)}**",
            f"- Paires R/L par cas : **{len(RL_PAIRS)}**",
            f"- Simulation conforme (tolérance {COORD_TOLERANCE}) : **{'Oui' if simulation_ok else 'Non'}**",
            "",
            "### Détail par paire (erreur max sur tous les cas train)",
            "",
            "| Paire | Max error | Tous OK |",
            "|-------|-----------|---------|",
        ]
    )

    for pair in RL_PAIRS:
        r_name, l_name, _, _ = pair
        pair_name = f"{r_name}/{l_name}"
        checks = [c for case in case_results for c in case.pair_checks if c.pair_name == pair_name]
        max_err = max(c.max_error for c in checks) if checks else 0.0
        all_ok = all(c.ok for c in checks)
        lines.append(f"| {pair_name} | {format_num(max_err)} | {'Oui' if all_ok else 'Non'} |")

    lines.extend(
        [
            "",
            "### Exemple ASL (premier cas train)",
            "",
        ]
    )
    if case_results:
        case = case_results[0]
        bbox, kps = parse_label(TRAIN_LABEL_DIR / f"{case.case_id}.txt")
        flipped = simulate_ultralytics_fliplr(kps, flip_idx)
        lines.extend(
            [
                f"**Cas :** {case.case_id}",
                "",
                "| Keypoint | x orig | y orig | x après flip | y après flip | Attendu si miroir R/L |",
                "|----------|--------|--------|--------------|--------------|------------------------|",
            ]
        )
        for r_name, l_name, r_idx, l_idx in [RL_PAIRS[2]]:  # ASL pair
            orig_r, orig_l = kps[r_idx], kps[l_idx]
            flip_r, flip_l = flipped[r_idx], flipped[l_idx]
            lines.append(
                f"| {r_name} | {format_num(orig_r.x, 4)} | {format_num(orig_r.y, 4)} | "
                f"{format_num(flip_r.x, 4)} | {format_num(flip_r.y, 4)} | "
                f"x=1-x({l_name})={format_num(1-orig_l.x, 4)} |"
            )
            lines.append(
                f"| {l_name} | {format_num(orig_l.x, 4)} | {format_num(orig_l.y, 4)} | "
                f"{format_num(flip_l.x, 4)} | {format_num(flip_l.y, 4)} | "
                f"x=1-x({r_name})={format_num(1-orig_r.x, 4)} |"
            )

    lines.extend(
        [
            "",
            "## Comportement Ultralytics (référence code)",
            "",
            "- `ultralytics/data/augment.py` : `RandomFlip` miroir horizontal + `keypoints[:, flip_idx, :]`.",
            "- Si `flip_idx` absent et `fliplr > 0` → flip **désactivé** avec warning.",
            "- Si `len(flip_idx) != kpt_shape[0]` → **ValueError** au build des augmentations.",
            "",
            "## Interprétation des verdicts",
            "",
            "| Verdict | Signification |",
            "|---------|---------------|",
            "| **A** | Flip parfaitement configuré |",
            "| **B** | Flip R/L mal configuré |",
            "| **C** | Flip non configuré / ambigu |",
            "| **D** | Flip correct mais probablement pas la cause ASL_L |",
            "",
            "## Regénérer",
            "",
            "```bash",
            ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\audit_horizontal_flip_new_26.py",
            "```",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    dataset = load_dataset_yaml()
    v2_args = load_v2_args()
    flip_idx = list(dataset.get("flip_idx", []))
    expected_idx = expected_flip_idx_from_pairs()
    idx_errors = flip_idx_pair_errors(flip_idx)

    label_paths = sorted(TRAIN_LABEL_DIR.glob("*.txt"))
    if not label_paths:
        raise SystemExit(f"Aucun label train dans {TRAIN_LABEL_DIR}")

    case_results = [audit_case(path, flip_idx) for path in label_paths]
    simulation_ok = all(c.all_ok for c in case_results)
    verdict, verdict_detail = determine_verdict(dataset, v2_args, flip_idx, simulation_ok, idx_errors)

    write_csv(flip_idx, case_results, idx_errors, verdict)
    write_md(dataset, v2_args, flip_idx, case_results, idx_errors, verdict, verdict_detail)

    print("HORIZONTAL FLIP AUDIT COMPLETE")
    print(f"VERDICT: {verdict}")
    print(f"flip_idx: {flip_idx}")
    print(f"R/L pairs checked: {len(RL_PAIRS)}")
    print(f"Train cases simulated: {len(case_results)}")
    print(f"Simulation OK: {simulation_ok}")
    print(f"MD={OUTPUT_MD}")
    print(f"CSV={OUTPUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
