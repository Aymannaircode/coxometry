#!/usr/bin/env python3
"""Analyse lecture seule des keypoints d'entraînement YOLO V2 (new_26).

Parcourt les labels YOLO dans datasets/yolo_pose_new_26/labels/{train,val}.
Ne modifie aucun label, JSON, poids ou prédiction.
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent
DATASET_ROOT = PROJECT_ROOT / "datasets" / "yolo_pose_new_26"
LABEL_ROOT = DATASET_ROOT / "labels"
OUTPUT_CSV = DATASET_ROOT / "training_keypoint_analysis.csv"
OUTPUT_MD = DATASET_ROOT / "training_keypoint_analysis.md"
OUTPUT_PNG = DATASET_ROOT / "training_keypoint_distribution.png"

sys.path.insert(0, str(SCRIPTS_DIR.parent / "manual_annotation_tool"))
import server  # noqa: E402

KEYPOINT_NAMES = [name for _, name, _ in server.LANDMARKS]
NKPT = len(KEYPOINT_NAMES)
NDIM = 3
EXPECTED_LABEL_COLS = 5 + NKPT * NDIM
EDGE_MARGIN = 0.05
FOCUS_KEYPOINTS = ("ASL_R", "ASL_L", "ASM_R", "ASM_L")


@dataclass
class KeypointStats:
    name: str
    split: str
    total_annotations: int = 0
    present_count: int = 0
    absent_count: int = 0
    xs: list[float] = field(default_factory=list)
    ys: list[float] = field(default_factory=list)
    near_edge_count: int = 0
    side: str = ""

    @property
    def presence_pct(self) -> float:
        if self.total_annotations == 0:
            return 0.0
        return 100.0 * self.present_count / self.total_annotations

    @property
    def mean_x(self) -> float | None:
        return statistics.mean(self.xs) if self.xs else None

    @property
    def mean_y(self) -> float | None:
        return statistics.mean(self.ys) if self.ys else None

    @property
    def std_x(self) -> float | None:
        return statistics.stdev(self.xs) if len(self.xs) >= 2 else (0.0 if self.xs else None)

    @property
    def std_y(self) -> float | None:
        return statistics.stdev(self.ys) if len(self.ys) >= 2 else (0.0 if self.ys else None)

    @property
    def dispersion(self) -> float:
        sx = self.std_x or 0.0
        sy = self.std_y or 0.0
        return math.hypot(sx, sy)

    def quantiles(self, axis: str) -> tuple[float | None, float | None, float | None]:
        values = self.xs if axis == "x" else self.ys
        if not values:
            return None, None, None
        if len(values) == 1:
            v = values[0]
            return v, v, v
        q1, _, q3 = statistics.quantiles(values, n=4)
        return q1, statistics.median(values), q3


@dataclass
class DistanceRecord:
    case_id: str
    split: str
    dist_norm: float


def format_num(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def parse_label(label_path: Path) -> list[tuple[str, float, float, float]]:
    values = [float(part) for part in label_path.read_text(encoding="utf-8").strip().split()]
    if len(values) != EXPECTED_LABEL_COLS:
        raise ValueError(f"{label_path.name}: {len(values)} colonnes, attendu {EXPECTED_LABEL_COLS}")
    keypoints: list[tuple[str, float, float, float]] = []
    offset = 5
    for index, name in enumerate(KEYPOINT_NAMES):
        base = offset + index * NDIM
        keypoints.append((name, values[base], values[base + 1], values[base + 2]))
    return keypoints


def is_near_edge(x: float, y: float, margin: float = EDGE_MARGIN) -> bool:
    return x <= margin or x >= 1.0 - margin or y <= margin or y >= 1.0 - margin


def collect_split_stats(split: str) -> tuple[dict[str, KeypointStats], list[DistanceRecord], list[str]]:
    label_dir = LABEL_ROOT / split
    if not label_dir.is_dir():
        raise FileNotFoundError(f"Dossier labels absent: {label_dir}")

    stats = {
        name: KeypointStats(name=name, split=split, side="R" if name.endswith("_R") else "L")
        for name in KEYPOINT_NAMES
    }
    distances: list[DistanceRecord] = []
    case_ids: list[str] = []

    for label_path in sorted(label_dir.glob("*.txt")):
        case_ids.append(label_path.stem)
        keypoints = parse_label(label_path)
        by_name = {name: (x, y, v) for name, x, y, v in keypoints}

        for name in KEYPOINT_NAMES:
            kp = stats[name]
            kp.total_annotations += 1
            x, y, v = by_name[name]
            if v > 0:
                kp.present_count += 1
                kp.xs.append(x)
                kp.ys.append(y)
                if is_near_edge(x, y):
                    kp.near_edge_count += 1
            else:
                kp.absent_count += 1

        asl = by_name["ASL_L"]
        asm = by_name["ASM_L"]
        if asl[2] > 0 and asm[2] > 0:
            dist_norm = math.hypot(asl[0] - asm[0], asl[1] - asm[1])
            distances.append(DistanceRecord(label_path.stem, split, dist_norm))

    return stats, distances, case_ids


def rank_keypoints(all_stats: dict[str, KeypointStats], key: str) -> list[tuple[str, float]]:
    if key == "frequency":
        scored = [(name, s.presence_pct) for name, s in all_stats.items()]
        return sorted(scored, key=lambda item: item[1], reverse=True)
    if key == "dispersion":
        scored = [(name, s.dispersion) for name, s in all_stats.items() if s.present_count >= 2]
        return sorted(scored, key=lambda item: item[1], reverse=True)
    if key == "edge":
        scored = [
            (name, s.near_edge_count / s.present_count if s.present_count else 0.0)
            for name, s in all_stats.items()
        ]
        return sorted(scored, key=lambda item: item[1], reverse=True)
    raise ValueError(f"Clé de classement inconnue: {key}")


def write_csv(
    train_stats: dict[str, KeypointStats],
    val_stats: dict[str, KeypointStats],
    train_dist: list[DistanceRecord],
    val_dist: list[DistanceRecord],
) -> None:
    fieldnames = [
        "section",
        "split",
        "keypoint",
        "side",
        "total_annotations",
        "present_count",
        "absent_count",
        "presence_pct",
        "mean_x_norm",
        "mean_y_norm",
        "std_x",
        "std_y",
        "dispersion",
        "q1_x",
        "median_x",
        "q3_x",
        "q1_y",
        "median_y",
        "q3_y",
        "near_edge_count",
        "near_edge_pct_of_present",
    ]
    rows: list[dict[str, str | float | int]] = []

    for split_name, split_stats in (("TRAIN", train_stats), ("VAL", val_stats)):
        for name in KEYPOINT_NAMES:
            kp = split_stats[name]
            q1x, medx, q3x = kp.quantiles("x")
            q1y, medy, q3y = kp.quantiles("y")
            near_pct = (100.0 * kp.near_edge_count / kp.present_count) if kp.present_count else 0.0
            rows.append(
                {
                    "section": "keypoint",
                    "split": split_name,
                    "keypoint": name,
                    "side": kp.side,
                    "total_annotations": kp.total_annotations,
                    "present_count": kp.present_count,
                    "absent_count": kp.absent_count,
                    "presence_pct": round(kp.presence_pct, 2),
                    "mean_x_norm": format_num(kp.mean_x),
                    "mean_y_norm": format_num(kp.mean_y),
                    "std_x": format_num(kp.std_x),
                    "std_y": format_num(kp.std_y),
                    "dispersion": format_num(kp.dispersion),
                    "q1_x": format_num(q1x),
                    "median_x": format_num(medx),
                    "q3_x": format_num(q3x),
                    "q1_y": format_num(q1y),
                    "median_y": format_num(medy),
                    "q3_y": format_num(q3y),
                    "near_edge_count": kp.near_edge_count,
                    "near_edge_pct_of_present": round(near_pct, 2),
                }
            )

    for split_name, dist_list in (("TRAIN", train_dist), ("VAL", val_dist)):
        values = [record.dist_norm for record in dist_list]
        if values:
            q1, med, q3 = (
                statistics.quantiles(values, n=4)[0],
                statistics.median(values),
                statistics.quantiles(values, n=4)[2],
            ) if len(values) >= 2 else (values[0], values[0], values[0])
            rows.append(
                {
                    "section": "distance_ASL_L_ASM_L",
                    "split": split_name,
                    "keypoint": "ASL_L-ASM_L",
                    "side": "L",
                    "total_annotations": len(dist_list),
                    "present_count": len(dist_list),
                    "absent_count": 0,
                    "presence_pct": 100.0 if dist_list else 0.0,
                    "mean_x_norm": format_num(statistics.mean(values)),
                    "mean_y_norm": "NA",
                    "std_x": format_num(statistics.stdev(values) if len(values) >= 2 else 0.0),
                    "std_y": "NA",
                    "dispersion": format_num(statistics.stdev(values) if len(values) >= 2 else 0.0),
                    "q1_x": format_num(q1),
                    "median_x": format_num(med),
                    "q3_x": format_num(q3),
                    "q1_y": "NA",
                    "median_y": "NA",
                    "q3_y": "NA",
                    "near_edge_count": 0,
                    "near_edge_pct_of_present": 0.0,
                }
            )
        for record in dist_list:
            rows.append(
                {
                    "section": "distance_case",
                    "split": split_name,
                    "keypoint": record.case_id,
                    "side": "L",
                    "total_annotations": 1,
                    "present_count": 1,
                    "absent_count": 0,
                    "presence_pct": 100.0,
                    "mean_x_norm": format_num(record.dist_norm),
                    "mean_y_norm": "NA",
                    "std_x": "NA",
                    "std_y": "NA",
                    "dispersion": "NA",
                    "q1_x": "NA",
                    "median_x": "NA",
                    "q3_x": "NA",
                    "q1_y": "NA",
                    "median_y": "NA",
                    "q3_y": "NA",
                    "near_edge_count": 0,
                    "near_edge_pct_of_present": 0.0,
                }
            )

    for split_name, split_stats in (("TRAIN", train_stats), ("VAL", val_stats)):
        for rank_key in ("frequency", "dispersion", "edge"):
            ranked = rank_keypoints(split_stats, rank_key)
            for rank, (name, score) in enumerate(ranked, start=1):
                rows.append(
                    {
                        "section": f"rank_{rank_key}",
                        "split": split_name,
                        "keypoint": name,
                        "side": split_stats[name].side,
                        "total_annotations": rank,
                        "present_count": int(round(score * 100)) if rank_key == "frequency" else 0,
                        "absent_count": 0,
                        "presence_pct": round(score, 4) if rank_key == "frequency" else round(score, 4),
                        "mean_x_norm": "NA",
                        "mean_y_norm": "NA",
                        "std_x": "NA",
                        "std_y": "NA",
                        "dispersion": "NA",
                        "q1_x": "NA",
                        "median_x": "NA",
                        "q3_x": "NA",
                        "q1_y": "NA",
                        "median_y": "NA",
                        "q3_y": "NA",
                        "near_edge_count": 0,
                        "near_edge_pct_of_present": 0.0,
                    }
                )

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def side_distribution_md(stats: dict[str, KeypointStats]) -> str:
    r_present = sum(s.present_count for name, s in stats.items() if name.endswith("_R"))
    l_present = sum(s.present_count for name, s in stats.items() if name.endswith("_L"))
    r_total = sum(s.total_annotations for name, s in stats.items() if name.endswith("_R"))
    l_total = sum(s.total_annotations for name, s in stats.items() if name.endswith("_L"))
    return (
        f"- Présence globale côté **R** : {r_present}/{r_total} "
        f"({100.0 * r_present / r_total:.1f} %)\n"
        f"- Présence globale côté **L** : {l_present}/{l_total} "
        f"({100.0 * l_present / l_total:.1f} %)"
    )


def comparison_block(
    train_stats: dict[str, KeypointStats],
    val_stats: dict[str, KeypointStats],
    left_name: str,
    right_name: str,
) -> list[str]:
    tr_l, tr_r = train_stats[left_name], train_stats[right_name]
    va_l, va_r = val_stats[left_name], val_stats[right_name]
    return [
        f"### {left_name} vs {right_name}",
        "",
        "| Métrique | TRAIN L | TRAIN R | VAL L | VAL R |",
        "|----------|---------|---------|-------|-------|",
        f"| Présence % | {tr_l.presence_pct:.1f} | {tr_r.presence_pct:.1f} | "
        f"{va_l.presence_pct:.1f} | {va_r.presence_pct:.1f} |",
        f"| mean_x | {format_num(tr_l.mean_x, 3)} | {format_num(tr_r.mean_x, 3)} | "
        f"{format_num(va_l.mean_x, 3)} | {format_num(va_r.mean_x, 3)} |",
        f"| mean_y | {format_num(tr_l.mean_y, 3)} | {format_num(tr_r.mean_y, 3)} | "
        f"{format_num(va_l.mean_y, 3)} | {format_num(va_r.mean_y, 3)} |",
        f"| std_x | {format_num(tr_l.std_x, 3)} | {format_num(tr_r.std_x, 3)} | "
        f"{format_num(va_l.std_x, 3)} | {format_num(va_r.std_x, 3)} |",
        f"| std_y | {format_num(tr_l.std_y, 3)} | {format_num(tr_r.std_y, 3)} | "
        f"{format_num(va_l.std_y, 3)} | {format_num(va_r.std_y, 3)} |",
        f"| dispersion | {format_num(tr_l.dispersion, 3)} | {format_num(tr_r.dispersion, 3)} | "
        f"{format_num(va_l.dispersion, 3)} | {format_num(va_r.dispersion, 3)} |",
        f"| proche bord | {tr_l.near_edge_count} | {tr_r.near_edge_count} | "
        f"{va_l.near_edge_count} | {va_r.near_edge_count} |",
        "",
    ]


def write_md(
    train_stats: dict[str, KeypointStats],
    val_stats: dict[str, KeypointStats],
    train_dist: list[DistanceRecord],
    val_dist: list[DistanceRecord],
    train_images: int,
    val_images: int,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    train_dist_vals = [r.dist_norm for r in train_dist]
    val_dist_vals = [r.dist_norm for r in val_dist]

    lines = [
        "# Analyse des keypoints d'entraînement — YOLO V2 (new_26)",
        "",
        f"**Date :** {now}",
        "**Source :** `datasets/yolo_pose_new_26/labels/{train,val}/` — lecture seule",
        "**Verdict mapping audit :** D — mapping JSON→YOLO correct, problème probablement lié à l'apprentissage",
        "",
        "## Résumé",
        "",
        f"- Images **train** : **{train_images}**",
        f"- Images **val** : **{val_images}**",
        f"- Keypoints : **{NKPT}** par image (1 instance pelvis)",
        f"- Marge « proche bord » : **{EDGE_MARGIN:.0%}** (normalisé)",
        "",
        "## Présence ASL / ASM (focus audit)",
        "",
        "| Keypoint | TRAIN présence | VAL présence | TRAIN dispersion | VAL dispersion |",
        "|----------|----------------|--------------|------------------|----------------|",
    ]
    for name in FOCUS_KEYPOINTS:
        tr, va = train_stats[name], val_stats[name]
        lines.append(
            f"| {name} | {tr.presence_pct:.1f} % ({tr.present_count}/{tr.total_annotations}) | "
            f"{va.presence_pct:.1f} % ({va.present_count}/{va.total_annotations}) | "
            f"{format_num(tr.dispersion, 3)} | {format_num(va.dispersion, 3)} |"
        )

    lines.extend(
        [
            "",
            "## Comparaisons bilatérales",
            "",
        ]
    )
    lines.extend(comparison_block(train_stats, val_stats, "ASL_L", "ASL_R"))
    lines.extend(comparison_block(train_stats, val_stats, "ASM_L", "ASM_R"))

    lines.extend(
        [
            "## Distance ASL_L ↔ ASM_L (labels d'entraînement)",
            "",
        ]
    )
    if train_dist_vals:
        lines.append(
            f"- **TRAIN** : n={len(train_dist_vals)}, "
            f"moyenne={format_num(statistics.mean(train_dist_vals), 3)}, "
            f"médiane={format_num(statistics.median(train_dist_vals), 3)}, "
            f"écart-type={format_num(statistics.stdev(train_dist_vals) if len(train_dist_vals) >= 2 else 0.0, 3)}"
        )
    else:
        lines.append("- **TRAIN** : aucune paire visible")
    if val_dist_vals:
        lines.append(
            f"- **VAL** : n={len(val_dist_vals)}, "
            f"moyenne={format_num(statistics.mean(val_dist_vals), 3)}, "
            f"médiane={format_num(statistics.median(val_dist_vals), 3)}, "
            f"écart-type={format_num(statistics.stdev(val_dist_vals) if len(val_dist_vals) >= 2 else 0.0, 3)}"
        )
    else:
        lines.append("- **VAL** : aucune paire visible")

    asl_l_train = train_stats["ASL_L"]
    asl_r_train = train_stats["ASL_R"]
    asl_l_disp = asl_l_train.dispersion
    asl_r_disp = asl_r_train.dispersion
    asl_l_presence_gap = asl_r_train.presence_pct - asl_l_train.presence_pct

    lines.extend(
        [
            "",
            "### Interprétation ciblée (audit ASL_L)",
            "",
            f"- ASL_L systématiquement proche de ASM_L ? "
            f"{'Non — distance médiane significative' if train_dist_vals and statistics.median(train_dist_vals) > 0.03 else 'Possible — distances faibles'} "
            f"(médiane train={format_num(statistics.median(train_dist_vals) if train_dist_vals else None, 3)} norm)",
            f"- ASL_L forte dispersion ? "
            f"{'Oui' if asl_l_disp > asl_r_disp * 1.25 else 'Non'} "
            f"(dispersion ASL_L={format_num(asl_l_disp, 3)} vs ASL_R={format_num(asl_r_disp, 3)})",
            f"- ASL_L moins présent que ASL_R ? "
            f"{'Oui' if asl_l_presence_gap > 1 else 'Non'} "
            f"(écart {asl_l_presence_gap:.1f} pts)",
            f"- Écart train/val ASL_L présence ? "
            f"{abs(train_stats['ASL_L'].presence_pct - val_stats['ASL_L'].presence_pct):.1f} pts",
            "",
        ]
    )

    for split_title, split_stats in (("TRAIN", train_stats), ("VAL", val_stats)):
        lines.extend(
            [
                f"## Statistiques détaillées — {split_title}",
                "",
                side_distribution_md(split_stats),
                "",
                "| Keypoint | Présents | Absents | % | mean_x | mean_y | std_x | std_y | Q1_x | med_x | Q3_x | Q1_y | med_y | Q3_y | bord |",
                "|----------|----------|---------|---|--------|--------|-------|-------|------|-------|------|------|-------|------|------|",
            ]
        )
        for name in KEYPOINT_NAMES:
            kp = split_stats[name]
            q1x, medx, q3x = kp.quantiles("x")
            q1y, medy, q3y = kp.quantiles("y")
            lines.append(
                f"| {name} | {kp.present_count} | {kp.absent_count} | {kp.presence_pct:.1f} | "
                f"{format_num(kp.mean_x, 3)} | {format_num(kp.mean_y, 3)} | "
                f"{format_num(kp.std_x, 3)} | {format_num(kp.std_y, 3)} | "
                f"{format_num(q1x, 3)} | {format_num(medx, 3)} | {format_num(q3x, 3)} | "
                f"{format_num(q1y, 3)} | {format_num(medy, 3)} | {format_num(q3y, 3)} | "
                f"{kp.near_edge_count} |"
            )
        lines.append("")

    for split_title, split_stats in (("TRAIN", train_stats), ("VAL", val_stats)):
        lines.append(f"## Classements — {split_title}")
        lines.append("")
        for rank_key, label in (
            ("frequency", "Fréquence (présence % décroissante)"),
            ("dispersion", "Dispersion (écart-type combiné décroissant)"),
            ("edge", "Proximité bords (ratio proche bord / présents)"),
        ):
            lines.append(f"### {label}")
            lines.append("")
            for rank, (name, score) in enumerate(rank_keypoints(split_stats, rank_key), start=1):
                unit = "%" if rank_key == "frequency" else ""
                lines.append(f"{rank}. **{name}** — {score:.4f}{unit}")
            lines.append("")

    lines.extend(
        [
            "## Fichiers générés",
            "",
            f"- `{OUTPUT_CSV.relative_to(PROJECT_ROOT).as_posix()}`",
            f"- `{OUTPUT_MD.relative_to(PROJECT_ROOT).as_posix()}`",
            f"- `{OUTPUT_PNG.relative_to(PROJECT_ROOT).as_posix()}`",
            "",
            "## Regénérer",
            "",
            "```bash",
            ".venv\\Scripts\\python.exe annotation_pilot\\scripts\\analyze_training_keypoints_new_26.py",
            "```",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_contact_sheet(train_stats: dict[str, KeypointStats]) -> None:
    """Figure : nuages de points + mini-grille d'exemples train pour ASL/ASM."""
    colors = {
        "ASL_R": "#ff7828",
        "ASM_R": "#ffb454",
        "ASL_L": "#3cb4ff",
        "ASM_L": "#78c8ff",
    }

    fig = plt.figure(figsize=(16, 10), facecolor="#11151c")
    gs = fig.add_gridspec(2, 4, height_ratios=[1.2, 1.0], hspace=0.28, wspace=0.25)

    for idx, name in enumerate(FOCUS_KEYPOINTS):
        ax = fig.add_subplot(gs[0, idx])
        kp = train_stats[name]
        ax.set_facecolor("#1b2230")
        if kp.xs:
            ax.scatter(kp.xs, kp.ys, c=colors[name], s=55, alpha=0.85, edgecolors="white", linewidths=0.4)
            ax.scatter([kp.mean_x], [kp.mean_y], c="white", s=120, marker="x", linewidths=2, label="moyenne")
        ax.set_xlim(0, 1)
        ax.set_ylim(1, 0)
        ax.set_title(f"{name} (n={kp.present_count})", color="white", fontsize=11)
        ax.set_xlabel("x norm", color="#9fb0c7", fontsize=9)
        ax.set_ylabel("y norm", color="#9fb0c7", fontsize=9)
        ax.tick_params(colors="#9fb0c7", labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#2a3447")
        ax.axvline(EDGE_MARGIN, color="#444", linestyle="--", linewidth=0.8)
        ax.axvline(1 - EDGE_MARGIN, color="#444", linestyle="--", linewidth=0.8)
        ax.axhline(EDGE_MARGIN, color="#444", linestyle="--", linewidth=0.8)
        ax.axhline(1 - EDGE_MARGIN, color="#444", linestyle="--", linewidth=0.8)

    overlay_ax = fig.add_subplot(gs[1, :2])
    overlay_ax.set_facecolor("#1b2230")
    for name in FOCUS_KEYPOINTS:
        kp = train_stats[name]
        if kp.xs:
            overlay_ax.scatter(kp.xs, kp.ys, c=colors[name], s=40, alpha=0.7, label=name)
    overlay_ax.set_xlim(0, 1)
    overlay_ax.set_ylim(1, 0)
    overlay_ax.set_title("Superposition TRAIN — ASL/ASM R/L", color="white")
    overlay_ax.legend(loc="upper right", fontsize=8, facecolor="#1b2230", edgecolor="#2a3447", labelcolor="white")
    overlay_ax.tick_params(colors="#9fb0c7")
    for spine in overlay_ax.spines.values():
        spine.set_color("#2a3447")

    dist_ax = fig.add_subplot(gs[1, 2:])
    dist_ax.set_facecolor("#1b2230")
    train_dist = []
    label_dir = LABEL_ROOT / "train"
    for label_path in sorted(label_dir.glob("*.txt")):
        kps = parse_label(label_path)
        by_name = {n: (x, y, v) for n, x, y, v in kps}
        asl = by_name["ASL_L"]
        asm = by_name["ASM_L"]
        if asl[2] > 0 and asm[2] > 0:
            train_dist.append(math.hypot(asl[0] - asm[0], asl[1] - asm[1]))
    if train_dist:
        dist_ax.hist(train_dist, bins=min(10, max(3, len(train_dist) // 2)), color="#3cb4ff", edgecolor="#11151c")
        dist_ax.axvline(statistics.median(train_dist), color="#ffb454", linestyle="--", label=f"médiane={statistics.median(train_dist):.3f}")
        dist_ax.legend(facecolor="#1b2230", edgecolor="#2a3447", labelcolor="white", fontsize=8)
    dist_ax.set_title("Distance ASL_L ↔ ASM_L (train, norm)", color="white")
    dist_ax.set_xlabel("distance", color="#9fb0c7")
    dist_ax.tick_params(colors="#9fb0c7")
    for spine in dist_ax.spines.values():
        spine.set_color("#2a3447")

    fig.suptitle(
        "Distribution des keypoints d'entraînement — focus ASL/ASM",
        color="white",
        fontsize=14,
        y=0.98,
    )
    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    train_stats, train_dist, train_cases = collect_split_stats("train")
    val_stats, val_dist, val_cases = collect_split_stats("val")

    write_csv(train_stats, val_stats, train_dist, val_dist)
    write_md(train_stats, val_stats, train_dist, val_dist, len(train_cases), len(val_cases))
    render_contact_sheet(train_stats)

    print("TRAINING KEYPOINT ANALYSIS COMPLETE")
    print(f"Train images: {len(train_cases)}")
    print(f"Val images: {len(val_cases)}")
    print(f"ASL_R presence: {train_stats['ASL_R'].presence_pct:.1f}%")
    print(f"ASL_L presence: {train_stats['ASL_L'].presence_pct:.1f}%")
    print(f"ASM_R presence: {train_stats['ASM_R'].presence_pct:.1f}%")
    print(f"ASM_L presence: {train_stats['ASM_L'].presence_pct:.1f}%")
    print(f"CSV={OUTPUT_CSV}")
    print(f"MD={OUTPUT_MD}")
    print(f"PNG={OUTPUT_PNG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
