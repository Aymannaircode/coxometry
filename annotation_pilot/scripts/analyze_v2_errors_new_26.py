#!/usr/bin/env python3
"""Analyse des erreurs V2 par radio — identification des cas les moins précis."""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "comparison_v1_v2.csv"
OUTPUT_CSV = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_error_analysis.csv"
OUTPUT_MD = PROJECT_ROOT / "datasets" / "yolo_pose_new_26" / "v2_error_analysis.md"

FSP_FSD_LANDMARKS = ("FSP_R", "FSP_L", "FSD_R", "FSD_L")
TOP_N = 5


def parse_error(value: str) -> float | None:
    text = (value or "").strip()
    if not text or text.lower() == "missing" or text.lower() == "na":
        return None
    return float(text)


def load_detail_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return [row for row in csv.DictReader(stream) if row.get("section") == "detail"]


def build_case_stats(detail_rows: list[dict[str, str]]) -> dict[str, dict]:
    by_case: dict[str, list[dict[str, float | str | None]]] = defaultdict(list)
    for row in detail_rows:
        pilot_id = row["pilot_id"]
        v1 = parse_error(row.get("v1_error_px", ""))
        v2 = parse_error(row.get("v2_error_px", ""))
        by_case[pilot_id].append(
            {
                "landmark": row["landmark"],
                "group": row["group"],
                "v1_error_px": v1,
                "v2_error_px": v2,
            }
        )

    case_stats: dict[str, dict] = {}
    for pilot_id, items in by_case.items():
        v2_values = [item["v2_error_px"] for item in items if item["v2_error_px"] is not None]
        v1_values = [item["v1_error_px"] for item in items if item["v1_error_px"] is not None]
        worst = max(
            (item for item in items if item["v2_error_px"] is not None),
            key=lambda item: float(item["v2_error_px"]),
            default=None,
        )
        case_stats[pilot_id] = {
            "pilot_id": pilot_id,
            "v2_mean_px": statistics.mean(v2_values) if v2_values else float("nan"),
            "v2_max_px": max(v2_values) if v2_values else float("nan"),
            "v2_median_px": statistics.median(v2_values) if v2_values else float("nan"),
            "v1_mean_px": statistics.mean(v1_values) if v1_values else float("nan"),
            "v1_max_px": max(v1_values) if v1_values else float("nan"),
            "evaluated_landmarks": len(v2_values),
            "worst_landmark": worst["landmark"] if worst else "",
            "worst_landmark_v2_px": float(worst["v2_error_px"]) if worst else float("nan"),
            "worst_landmark_v1_px": float(worst["v1_error_px"])
            if worst and worst["v1_error_px"] is not None
            else float("nan"),
            "items": items,
        }
    return case_stats


def landmark_ranking(
    case_stats: dict[str, dict], landmark: str
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for pilot_id, stats in case_stats.items():
        item = next((entry for entry in stats["items"] if entry["landmark"] == landmark), None)
        if item is None or item["v2_error_px"] is None:
            continue
        v2 = float(item["v2_error_px"])
        v1 = float(item["v1_error_px"]) if item["v1_error_px"] is not None else float("nan")
        rows.append(
            {
                "pilot_id": pilot_id,
                "landmark": landmark,
                "v2_error_px": v2,
                "v1_error_px": v1,
                "v1_minus_v2_px": v1 - v2 if not (v1 != v1) else float("nan"),
                "best_model": "V2" if v2 < v1 else ("V1" if v1 < v2 else "egal"),
            }
        )
    rows.sort(key=lambda row: float(row["v2_error_px"]), reverse=True)
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return rows


def fsp_fsd_case_score(stats: dict) -> float:
    values: list[float] = []
    for landmark in FSP_FSD_LANDMARKS:
        item = next((entry for entry in stats["items"] if entry["landmark"] == landmark), None)
        if item and item["v2_error_px"] is not None:
            values.append(float(item["v2_error_px"]))
    return statistics.mean(values) if values else float("nan")


def format_num(value: float, digits: int = 2) -> str:
    if value != value:
        return "NA"
    return f"{value:.{digits}f}"


def write_csv(
    ranked_cases: list[dict],
    landmark_rankings: dict[str, list[dict]],
    top_fsp_fsd: list[dict],
) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "section",
                "rank",
                "pilot_id",
                "landmark",
                "v2_mean_px",
                "v2_max_px",
                "v2_median_px",
                "v1_mean_px",
                "v1_max_px",
                "worst_landmark",
                "worst_landmark_v2_px",
                "worst_landmark_v1_px",
                "v2_error_px",
                "v1_error_px",
                "v1_minus_v2_px",
                "fsp_fsd_mean_v2_px",
                "best_model",
            ],
        )
        writer.writeheader()

        for index, case in enumerate(ranked_cases, start=1):
            writer.writerow(
                {
                    "section": "case_ranking",
                    "rank": index,
                    "pilot_id": case["pilot_id"],
                    "landmark": "",
                    "v2_mean_px": format_num(case["v2_mean_px"]),
                    "v2_max_px": format_num(case["v2_max_px"]),
                    "v2_median_px": format_num(case["v2_median_px"]),
                    "v1_mean_px": format_num(case["v1_mean_px"]),
                    "v1_max_px": format_num(case["v1_max_px"]),
                    "worst_landmark": case["worst_landmark"],
                    "worst_landmark_v2_px": format_num(case["worst_landmark_v2_px"]),
                    "worst_landmark_v1_px": format_num(case["worst_landmark_v1_px"]),
                    "v2_error_px": "",
                    "v1_error_px": "",
                    "v1_minus_v2_px": "",
                    "fsp_fsd_mean_v2_px": format_num(case["fsp_fsd_mean_v2_px"]),
                    "best_model": "",
                }
            )

        for landmark in FSP_FSD_LANDMARKS:
            for row in landmark_rankings[landmark]:
                writer.writerow(
                    {
                        "section": f"landmark_{landmark}",
                        "rank": row["rank"],
                        "pilot_id": row["pilot_id"],
                        "landmark": landmark,
                        "v2_mean_px": "",
                        "v2_max_px": "",
                        "v2_median_px": "",
                        "v1_mean_px": "",
                        "v1_max_px": "",
                        "worst_landmark": "",
                        "worst_landmark_v2_px": "",
                        "worst_landmark_v1_px": "",
                        "v2_error_px": format_num(float(row["v2_error_px"])),
                        "v1_error_px": format_num(float(row["v1_error_px"])),
                        "v1_minus_v2_px": format_num(float(row["v1_minus_v2_px"])),
                        "fsp_fsd_mean_v2_px": "",
                        "best_model": row["best_model"],
                    }
                )

        for index, case in enumerate(top_fsp_fsd, start=1):
            writer.writerow(
                {
                    "section": "top5_fsp_fsd",
                    "rank": index,
                    "pilot_id": case["pilot_id"],
                    "landmark": "",
                    "v2_mean_px": format_num(case["v2_mean_px"]),
                    "v2_max_px": format_num(case["v2_max_px"]),
                    "v2_median_px": format_num(case["v2_median_px"]),
                    "v1_mean_px": format_num(case["v1_mean_px"]),
                    "v1_max_px": format_num(case["v1_max_px"]),
                    "worst_landmark": case["worst_landmark"],
                    "worst_landmark_v2_px": format_num(case["worst_landmark_v2_px"]),
                    "worst_landmark_v1_px": format_num(case["worst_landmark_v1_px"]),
                    "v2_error_px": "",
                    "v1_error_px": "",
                    "v1_minus_v2_px": format_num(case["v1_mean_px"] - case["v2_mean_px"]),
                    "fsp_fsd_mean_v2_px": format_num(case["fsp_fsd_mean_v2_px"]),
                    "best_model": "V2" if case["v2_mean_px"] < case["v1_mean_px"] else "V1",
                }
            )


def write_markdown(
    ranked_cases: list[dict],
    landmark_rankings: dict[str, list[dict]],
    top_fsp_fsd: list[dict],
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Analyse des erreurs V2 — new_26",
        "",
        f"**Généré le :** {now}",
        f"**Source :** `{INPUT_CSV.relative_to(PROJECT_ROOT)}`",
        "",
        "## Classement des 26 radios (erreur moyenne V2 décroissante)",
        "",
        "| Rang | Radio | V2 mean px | V2 max px | Pire landmark | V2 px (pire) | V1 px (pire) | FSP/FSD mean V2 |",
        "|------|-------|------------|-----------|---------------|--------------|--------------|-----------------|",
    ]

    for index, case in enumerate(ranked_cases, start=1):
        lines.append(
            f"| {index} | {case['pilot_id']} | {format_num(case['v2_mean_px'])} | "
            f"{format_num(case['v2_max_px'])} | {case['worst_landmark']} | "
            f"{format_num(case['worst_landmark_v2_px'])} | "
            f"{format_num(case['worst_landmark_v1_px'])} | "
            f"{format_num(case['fsp_fsd_mean_v2_px'])} |"
        )

    for landmark in FSP_FSD_LANDMARKS:
        lines.extend(
            [
                "",
                f"## Classement V2 — {landmark}",
                "",
                "| Rang | Radio | V2 px | V1 px | Δ V1−V2 | Meilleur |",
                "|------|-------|-------|-------|---------|----------|",
            ]
        )
        for row in landmark_rankings[landmark][:10]:
            lines.append(
                f"| {row['rank']} | {row['pilot_id']} | {format_num(float(row['v2_error_px']))} | "
                f"{format_num(float(row['v1_error_px']))} | "
                f"{format_num(float(row['v1_minus_v2_px']))} | {row['best_model']} |"
            )

    lines.extend(
        [
            "",
            "## 5 pires radios pour FSP/FSD (moyenne V2 sur FSP_R, FSP_L, FSD_R, FSD_L)",
            "",
            "| Rang | Radio | FSP/FSD mean V2 | V2 mean global | V1 mean global | Δ V1−V2 global | Meilleur global |",
            "|------|-------|-----------------|----------------|----------------|----------------|-----------------|",
        ]
    )
    for index, case in enumerate(top_fsp_fsd, start=1):
        delta = case["v1_mean_px"] - case["v2_mean_px"]
        best = "V2" if case["v2_mean_px"] < case["v1_mean_px"] else "V1"
        lines.append(
            f"| {index} | {case['pilot_id']} | {format_num(case['fsp_fsd_mean_v2_px'])} | "
            f"{format_num(case['v2_mean_px'])} | {format_num(case['v1_mean_px'])} | "
            f"{format_num(delta)} | {best} |"
        )

    lines.extend(
        [
            "",
            "## Comparaison V1 vs V2 sur les 5 pires cas FSP/FSD",
            "",
        ]
    )
    for index, case in enumerate(top_fsp_fsd, start=1):
        lines.append(f"### {index}. {case['pilot_id']}")
        lines.append("")
        lines.append("| Landmark | V1 px | V2 px | Meilleur |")
        lines.append("|----------|-------|-------|----------|")
        for landmark in FSP_FSD_LANDMARKS:
            item = next(
                (entry for entry in case["items"] if entry["landmark"] == landmark),
                None,
            )
            if not item or item["v2_error_px"] is None:
                lines.append(f"| {landmark} | NA | NA | NA |")
                continue
            v1 = float(item["v1_error_px"]) if item["v1_error_px"] is not None else float("nan")
            v2 = float(item["v2_error_px"])
            best = "V2" if v2 < v1 else ("V1" if v1 < v2 else "egal")
            lines.append(
                f"| {landmark} | {format_num(v1)} | {format_num(v2)} | {best} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Lecture",
            "",
            "- Un rang élevé = erreur V2 plus forte (moins précis).",
            "- Δ V1−V2 positif = V2 meilleur que V1 sur ce cas/landmark.",
            "- Les cas listés ici sont les priorités de relecture manuelle.",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_CSV.is_file():
        print(f"ERROR: fichier introuvable : {INPUT_CSV}")
        return 1

    detail_rows = load_detail_rows(INPUT_CSV)
    case_stats = build_case_stats(detail_rows)
    if len(case_stats) != 26:
        print(f"WARN: {len(case_stats)} cas trouvés dans les lignes detail (attendu 26)")

    ranked_cases = sorted(
        (
            {
                **stats,
                "fsp_fsd_mean_v2_px": fsp_fsd_case_score(stats),
            }
            for stats in case_stats.values()
        ),
        key=lambda row: row["v2_mean_px"],
        reverse=True,
    )

    landmark_rankings = {
        landmark: landmark_ranking(case_stats, landmark) for landmark in FSP_FSD_LANDMARKS
    }

    top_fsp_fsd = sorted(
        ranked_cases,
        key=lambda row: row["fsp_fsd_mean_v2_px"],
        reverse=True,
    )[:TOP_N]

    write_csv(ranked_cases, landmark_rankings, top_fsp_fsd)
    write_markdown(ranked_cases, landmark_rankings, top_fsp_fsd)

    print(f"INPUT={INPUT_CSV}")
    print(f"CASES={len(ranked_cases)}")
    print(f"WORST_V2={ranked_cases[0]['pilot_id']} mean={format_num(ranked_cases[0]['v2_mean_px'])} px")
    print(f"TOP5_FSP_FSD={','.join(case['pilot_id'] for case in top_fsp_fsd)}")
    print(f"CSV={OUTPUT_CSV}")
    print(f"MD={OUTPUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
