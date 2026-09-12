#!/usr/bin/env python3
"""Analyse descriptive des mesures géométriques V2 (new_26).

Lit `v2_geometry_results.csv` produit par `test_v2_geometry_new_26.py`.
Aucun seuil clinique externe ; cohérence numérique du pipeline uniquement.
"""

from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_geometry_results.csv"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_geometry_analysis.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_geometry_analysis.md"

MEASURE_COLUMNS = ("VCE_R", "VCE_L", "Tonnis_R", "Tonnis_L", "CCD_R", "CCD_L")
BILATERAL_PAIRS = (
    ("VCE", "VCE_R", "VCE_L"),
    ("Tonnis", "Tonnis_R", "Tonnis_L"),
    ("CCD", "CCD_R", "CCD_L"),
)
TOP_N = 5
EXPECTED_CASES = 26
EXPECTED_MEASUREMENTS = 156


@dataclass
class MeasureStats:
    measure: str
    count: int = 0
    missing: int = 0
    mean: float | None = None
    median: float | None = None
    stdev: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    q1: float | None = None
    q3: float | None = None
    negative_count: int = 0
    above_180_count: int = 0
    values: list[tuple[str, float]] = field(default_factory=list)


@dataclass
class BilateralStats:
    measure: str
    diffs: list[tuple[str, float]] = field(default_factory=list)

    @property
    def values(self) -> list[float]:
        return [value for _, value in self.diffs]

    @property
    def mean(self) -> float | None:
        if not self.values:
            return None
        return statistics.mean(self.values)

    @property
    def maximum(self) -> float | None:
        if not self.values:
            return None
        return max(self.values)


def parse_measure(value: str) -> float | None:
    text = (value or "").strip()
    if not text:
        return None
    return float(text)


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def compute_measure_stats(rows: list[dict[str, str]], column: str) -> MeasureStats:
    stats = MeasureStats(measure=column)
    numeric_values: list[float] = []

    for row in rows:
        parsed = parse_measure(row.get(column, ""))
        if parsed is None:
            stats.missing += 1
            continue
        stats.count += 1
        numeric_values.append(parsed)
        stats.values.append((row["case_id"], parsed))
        if parsed < 0:
            stats.negative_count += 1
        if parsed > 180:
            stats.above_180_count += 1

    if numeric_values:
        stats.mean = statistics.mean(numeric_values)
        stats.median = statistics.median(numeric_values)
        stats.minimum = min(numeric_values)
        stats.maximum = max(numeric_values)
        if len(numeric_values) >= 2:
            stats.stdev = statistics.stdev(numeric_values)
        else:
            stats.stdev = 0.0
        if len(numeric_values) >= 4:
            q1, _, q3 = statistics.quantiles(numeric_values, n=4)
            stats.q1 = q1
            stats.q3 = q3
        elif len(numeric_values) == 1:
            stats.q1 = numeric_values[0]
            stats.q3 = numeric_values[0]

    return stats


def compute_bilateral_stats(rows: list[dict[str, str]], label: str, col_r: str, col_l: str) -> BilateralStats:
    stats = BilateralStats(measure=label)
    for row in rows:
        right = parse_measure(row.get(col_r, ""))
        left = parse_measure(row.get(col_l, ""))
        if right is None or left is None:
            continue
        stats.diffs.append((row["case_id"], abs(right - left)))
    stats.diffs.sort(key=lambda item: item[1], reverse=True)
    return stats


def format_num(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def top_extremes(stats: MeasureStats, n: int = TOP_N) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    ordered = sorted(stats.values, key=lambda item: item[1])
    lowest = ordered[:n]
    highest = list(reversed(ordered[-n:])) if len(ordered) >= n else list(reversed(ordered))
    return lowest, highest


def build_inspection_cases(
    rows: list[dict[str, str]],
    measure_stats: dict[str, MeasureStats],
    bilateral_stats: dict[str, BilateralStats],
) -> list[dict[str, str]]:
    """Cas à inspecter visuellement (cohérence pipeline, sans seuil clinique)."""
    flagged: dict[str, set[str]] = {}

    def add(case_id: str, reason: str) -> None:
        flagged.setdefault(case_id, set()).add(reason)

    for row in rows:
        case_id = row["case_id"]
        if row.get("status", "").strip().lower() != "ok":
            add(case_id, f"status={row.get('status', '')}")
        if (row.get("error") or "").strip():
            add(case_id, f"error={row['error'].strip()}")

    for column, stats in measure_stats.items():
        for case_id, value in stats.values:
            if value > 180:
                add(case_id, f"{column} > 180° ({value:.2f})")
        lowest, highest = top_extremes(stats)
        for case_id, value in lowest:
            add(case_id, f"{column} extrême bas ({value:.2f})")
        for case_id, value in highest:
            add(case_id, f"{column} extrême haut ({value:.2f})")

    for label, bstats in bilateral_stats.items():
        for case_id, diff in bstats.diffs[:TOP_N]:
            add(case_id, f"|{label}_R − {label}_L| élevé ({diff:.2f}°)")

    inspection: list[dict[str, str]] = []
    for case_id in sorted(flagged):
        inspection.append(
            {
                "case_id": case_id,
                "reasons": " | ".join(sorted(flagged[case_id])),
                "reason_count": str(len(flagged[case_id])),
            }
        )
    inspection.sort(key=lambda item: int(item["reason_count"]), reverse=True)
    return inspection


def write_csv(
    measure_stats: dict[str, MeasureStats],
    bilateral_stats: dict[str, BilateralStats],
    inspection_cases: list[dict[str, str]],
    total_missing: int,
) -> None:
    rows: list[dict[str, str]] = []

    rows.append(
        {
            "section": "summary",
            "metric": "cases",
            "value": str(EXPECTED_CASES),
            "case_id": "",
            "detail": "",
        }
    )
    rows.append(
        {
            "section": "summary",
            "metric": "measurements_expected",
            "value": str(EXPECTED_MEASUREMENTS),
            "case_id": "",
            "detail": "",
        }
    )
    rows.append(
        {
            "section": "summary",
            "metric": "measurements_missing",
            "value": str(total_missing),
            "case_id": "",
            "detail": "",
        }
    )

    for column in MEASURE_COLUMNS:
        stats = measure_stats[column]
        rows.append(
            {
                "section": "measure_stats",
                "metric": column,
                "value": str(stats.count),
                "case_id": "",
                "detail": "count",
            }
        )
        for label, attr in (
            ("mean", stats.mean),
            ("median", stats.median),
            ("stdev", stats.stdev),
            ("min", stats.minimum),
            ("max", stats.maximum),
            ("q1", stats.q1),
            ("q3", stats.q3),
            ("negative_count", stats.negative_count),
            ("above_180_count", stats.above_180_count),
            ("missing", stats.missing),
        ):
            rows.append(
                {
                    "section": "measure_stats",
                    "metric": column,
                    "value": format_num(float(attr)) if isinstance(attr, float) else str(attr),
                    "case_id": "",
                    "detail": label,
                }
            )

        lowest, highest = top_extremes(stats)
        for rank, (case_id, value) in enumerate(lowest, start=1):
            rows.append(
                {
                    "section": "extremes_low",
                    "metric": column,
                    "value": format_num(value),
                    "case_id": case_id,
                    "detail": f"rank_{rank}",
                }
            )
        for rank, (case_id, value) in enumerate(highest, start=1):
            rows.append(
                {
                    "section": "extremes_high",
                    "metric": column,
                    "value": format_num(value),
                    "case_id": case_id,
                    "detail": f"rank_{rank}",
                }
            )

    for label, bstats in bilateral_stats.items():
        rows.append(
            {
                "section": "bilateral",
                "metric": label,
                "value": format_num(bstats.mean),
                "case_id": "",
                "detail": "mean_abs_diff",
            }
        )
        rows.append(
            {
                "section": "bilateral",
                "metric": label,
                "value": format_num(bstats.maximum),
                "case_id": "",
                "detail": "max_abs_diff",
            }
        )
        for rank, (case_id, diff) in enumerate(bstats.diffs[:TOP_N], start=1):
            rows.append(
                {
                    "section": "bilateral_top",
                    "metric": label,
                    "value": format_num(diff),
                    "case_id": case_id,
                    "detail": f"rank_{rank}",
                }
            )

    for item in inspection_cases:
        rows.append(
            {
                "section": "visual_inspection",
                "metric": item["case_id"],
                "value": item["reason_count"],
                "case_id": item["case_id"],
                "detail": item["reasons"],
            }
        )

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["section", "metric", "value", "case_id", "detail"],
        )
        writer.writeheader()
        writer.writerows(rows)


def render_measure_section(stats: MeasureStats) -> list[str]:
    lowest, highest = top_extremes(stats)
    lines = [
        f"### {stats.measure}",
        "",
        "| Statistique | Valeur |",
        "|-------------|--------|",
        f"| N (disponibles) | {stats.count} |",
        f"| Manquantes | {stats.missing} |",
        f"| Moyenne | {format_num(stats.mean)}° |",
        f"| Médiane | {format_num(stats.median)}° |",
        f"| Écart-type | {format_num(stats.stdev)}° |",
        f"| Minimum | {format_num(stats.minimum)}° |",
        f"| Maximum | {format_num(stats.maximum)}° |",
        f"| Q1 | {format_num(stats.q1)}° |",
        f"| Q3 | {format_num(stats.q3)}° |",
        f"| Valeurs négatives | {stats.negative_count} |",
        f"| Valeurs > 180° | {stats.above_180_count} |",
        "",
        "**5 plus basses**",
        "",
        "| Rang | Radio | Valeur (°) |",
        "|------|-------|------------|",
    ]
    for rank, (case_id, value) in enumerate(lowest, start=1):
        lines.append(f"| {rank} | {case_id} | {format_num(value)} |")
    lines.extend(
        [
            "",
            "**5 plus élevées**",
            "",
            "| Rang | Radio | Valeur (°) |",
            "|------|-------|------------|",
        ]
    )
    for rank, (case_id, value) in enumerate(highest, start=1):
        lines.append(f"| {rank} | {case_id} | {format_num(value)} |")
    lines.append("")
    return lines


def write_markdown(
    rows: list[dict[str, str]],
    measure_stats: dict[str, MeasureStats],
    bilateral_stats: dict[str, BilateralStats],
    inspection_cases: list[dict[str, str]],
    total_missing: int,
) -> None:
    ok_count = sum(1 for row in rows if row.get("status", "").strip().lower() == "ok")
    lines = [
        "# Analyse descriptive géométrie V2 — new_26",
        "",
        f"**Généré :** {datetime.now(timezone.utc).isoformat()}",
        f"**Source :** `{INPUT_CSV.relative_to(PROJECT_ROOT).as_posix()}`",
        "",
        "> Analyse de cohérence numérique du pipeline. Aucun seuil clinique externe appliqué.",
        "",
        "## 1. Résumé global",
        "",
        f"- Radios dans le CSV : **{len(rows)}**",
        f"- Radios `status=ok` : **{ok_count}**",
        f"- Mesures attendues : **{EXPECTED_MEASUREMENTS}** (26 × 2 × 3)",
        f"- Mesures manquantes : **{total_missing}**",
        "",
    ]

    section_number = 2
    for group_name, columns in (
        ("VCE", ("VCE_R", "VCE_L")),
        ("Tönnis", ("Tonnis_R", "Tonnis_L")),
        ("CCD", ("CCD_R", "CCD_L")),
    ):
        lines.append(f"## {section_number}. Statistiques {group_name}")
        section_number += 1
        lines.append("")
        for column in columns:
            lines.extend(render_measure_section(measure_stats[column]))

    lines.extend(
        [
            "## 5. Analyse bilatérale (|R − L|)",
            "",
            "| Mesure | Moyenne |Δ| (°) | Maximum |Δ| (°) |",
            "|--------|----------------|----------------|",
        ]
    )
    for label, bstats in bilateral_stats.items():
        lines.append(
            f"| {label} | {format_num(bstats.mean)} | {format_num(bstats.maximum)} |"
        )

    for label, bstats in bilateral_stats.items():
        lines.extend(
            [
                "",
                f"### Top 5 asymétries — {label}",
                "",
                "| Rang | Radio | |R − L| (°) |",
                "|------|-------|------------|",
            ]
        )
        for rank, (case_id, diff) in enumerate(bstats.diffs[:TOP_N], start=1):
            lines.append(f"| {rank} | {case_id} | {format_num(diff)} |")

    lines.extend(["", "## 6. Valeurs extrêmes (synthèse)", ""])
    for column in MEASURE_COLUMNS:
        stats = measure_stats[column]
        lowest, highest = top_extremes(stats)
        low_text = ", ".join(f"{case_id} ({format_num(value)}°)" for case_id, value in lowest)
        high_text = ", ".join(f"{case_id} ({format_num(value)}°)" for case_id, value in highest)
        lines.append(f"- **{column}** — min : {low_text} ; max : {high_text}")

    lines.extend(["", "## 7. Cas nécessitant une inspection visuelle", ""])
    lines.append(
        "Critères : statut non ok, mesure > 180°, extrême (top/bottom 5), "
        "ou asymétrie bilatérale dans le top 5. **Sans interprétation clinique.**"
    )
    lines.append("")
    if not inspection_cases:
        lines.append("Aucun cas signalé.")
    else:
        lines.extend(["| Radio | Nb signaux | Motifs |", "|-------|------------|--------|"])
        for item in inspection_cases:
            lines.append(
                f"| {item['case_id']} | {item['reason_count']} | {item['reasons']} |"
            )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def count_total_missing(measure_stats: dict[str, MeasureStats]) -> int:
    return sum(stats.missing for stats in measure_stats.values())


def main() -> int:
    if not INPUT_CSV.is_file():
        raise FileNotFoundError(f"CSV source absent : {INPUT_CSV}")

    rows = load_rows(INPUT_CSV)
    measure_stats = {column: compute_measure_stats(rows, column) for column in MEASURE_COLUMNS}
    bilateral_stats = {
        label: compute_bilateral_stats(rows, label, col_r, col_l)
        for label, col_r, col_l in BILATERAL_PAIRS
    }
    total_missing = count_total_missing(measure_stats)
    inspection_cases = build_inspection_cases(rows, measure_stats, bilateral_stats)

    write_csv(measure_stats, bilateral_stats, inspection_cases, total_missing)
    write_markdown(rows, measure_stats, bilateral_stats, inspection_cases, total_missing)

    print("ANALYSIS COMPLETE")
    print(f"Cases: {len(rows)}")
    print(f"Measurements: {EXPECTED_MEASUREMENTS}")
    print(f"Missing: {total_missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
