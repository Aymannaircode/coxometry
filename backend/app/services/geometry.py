"""Adaptation des schémas API vers `mvp_geometry` et calcul des mesures.

Réutilise exclusivement `mvp_geometry.compute_side` / `Landmark`.
Aucune formule géométrique n'est recopiée ici.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from mvp_geometry import Landmark, compute_side
from mvp_geometry.hip_measures import MeasurementResult, SideResult

from ..schemas.landmarks import LandmarkIn
from ..schemas.measurements import MeasureOut, SideOut


def landmarks_to_geometry(landmarks: Sequence[LandmarkIn]) -> Dict[str, Landmark]:
    """Convertit les landmarks Pydantic en `Landmark` mvp_geometry indexés par nom."""
    result: Dict[str, Landmark] = {}
    for item in landmarks:
        name = item.name.value
        side = "R" if name.endswith("_R") else "L" if name.endswith("_L") else "?"
        result[name] = Landmark(
            id=name.lower(),
            name=name,
            side=side,
            x=item.x,
            y=item.y,
            v=item.v,
        )
    return result


def _measure_out(result: MeasurementResult) -> MeasureOut:
    return MeasureOut(
        name=result.name,
        side=result.side,  # type: ignore[arg-type]
        value_deg=result.value_deg,
        available=result.available,
        reason=result.reason,
    )


def side_result_to_out(side_result: SideResult) -> SideOut:
    return SideOut(
        side=side_result.side,  # type: ignore[arg-type]
        vce=_measure_out(side_result.vce),
        tonnis=_measure_out(side_result.tonnis),
        ccd=_measure_out(side_result.ccd),
    )


def compute_measurements(
    landmarks: Sequence[LandmarkIn],
    sides: Iterable[str] | None = None,
) -> Dict[str, SideOut]:
    """Calcule VCE / Tönnis / CCD via `mvp_geometry` pour les côtés demandés."""
    indexed = landmarks_to_geometry(landmarks)
    target_sides: List[str] = list(sides) if sides is not None else ["R", "L"]
    output: Dict[str, SideOut] = {}
    for side in target_sides:
        output[side] = side_result_to_out(compute_side(indexed, side))
    return output
