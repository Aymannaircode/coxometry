"""Contrôles anatomiques — avertissements uniquement, sans correction automatique."""

from __future__ import annotations

from typing import Any

SIDE_MARGIN_RATIO = 0.05


def _point(landmarks: dict[str, dict[str, Any]], name: str) -> tuple[float, float] | None:
    landmark = landmarks.get(name)
    if not landmark or landmark.get("v") != 2:
        return None
    x, y = landmark.get("x"), landmark.get("y")
    if x is None or y is None:
        return None
    return float(x), float(y)


def _landmarks_by_name(landmarks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("name")): item for item in landmarks if isinstance(item, dict)}


def run_anatomical_checks(
    landmarks: list[dict[str, Any]], width: float, height: float
) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    if width <= 0 or height <= 0:
        return warnings

    by_name = _landmarks_by_name(landmarks)
    mid = width / 2
    margin = width * SIDE_MARGIN_RATIO

    for name, landmark in by_name.items():
        if landmark.get("v") != 2:
            continue
        x, y = landmark.get("x"), landmark.get("y")
        if x is None or y is None:
            continue
        xf, yf = float(x), float(y)
        if not (0 <= xf < width and 0 <= yf < height):
            warnings.append(
                {
                    "category": "out_of_bounds",
                    "landmark": name,
                    "message": f"{name} : coordonnées hors image ({xf:.1f}, {yf:.1f}).",
                }
            )
        if name.endswith("_R") and xf > mid + margin:
            warnings.append(
                {
                    "category": "side_rl",
                    "landmark": name,
                    "message": (
                        f"{name} : côté droit patient mais x={xf:.1f} "
                        f"> milieu+5% ({mid:.1f}) — vérifier R/L."
                    ),
                }
            )
        if name.endswith("_L") and xf < mid - margin:
            warnings.append(
                {
                    "category": "side_rl",
                    "landmark": name,
                    "message": (
                        f"{name} : côté gauche patient mais x={xf:.1f} "
                        f"< milieu-5% ({mid:.1f}) — vérifier R/L."
                    ),
                }
            )

    for suffix, asl_name, asm_name in (
        ("R", "ASL_R", "ASM_R"),
        ("L", "ASL_L", "ASM_L"),
    ):
        asl = _point(by_name, asl_name)
        asm = _point(by_name, asm_name)
        if asl and asm:
            if suffix == "R" and asl[0] > asm[0]:
                warnings.append(
                    {
                        "category": "asl_asm",
                        "landmark": asl_name,
                        "message": (
                            f"{asl_name}/{asm_name} : ASL devrait être latéral à ASM "
                            f"(ASL_x={asl[0]:.1f}, ASM_x={asm[0]:.1f})."
                        ),
                    }
                )
            if suffix == "L" and asl[0] < asm[0]:
                warnings.append(
                    {
                        "category": "asl_asm",
                        "landmark": asl_name,
                        "message": (
                            f"{asl_name}/{asm_name} : ASL devrait être latéral à ASM "
                            f"(ASL_x={asl[0]:.1f}, ASM_x={asm[0]:.1f})."
                        ),
                    }
                )

    for suffix in ("R", "L"):
        chain = [f"FHC_{suffix}", f"FNM_{suffix}", f"FSP_{suffix}", f"FSD_{suffix}"]
        coords = [_point(by_name, name) for name in chain]
        present = [(name, coord) for name, coord in zip(chain, coords) if coord]
        for index in range(len(present) - 1):
            upper_name, (upper_x, upper_y) = present[index]
            lower_name, (lower_x, lower_y) = present[index + 1]
            if upper_y >= lower_y:
                warnings.append(
                    {
                        "category": "femoral_chain",
                        "landmark": lower_name,
                        "message": (
                            f"Chaîne fémorale {suffix} : {upper_name} devrait être au-dessus de "
                            f"{lower_name} (y {upper_name}={upper_y:.1f}, "
                            f"y {lower_name}={lower_y:.1f})."
                        ),
                    }
                )

    return warnings
