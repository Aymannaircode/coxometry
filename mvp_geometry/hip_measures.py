"""Couche haut niveau : calcule VCE, Tönnis et CCD par hanche.

Prend en entrée un dictionnaire de `Landmark` indexé par nom (voir
`landmarks.landmarks_by_name`) ou des points bruts, et applique les fonctions
géométriques. Lorsqu'un landmark requis est absent ou non exploitable, la
mesure correspondante est rapportée comme indisponible avec une raison, sans
inventer de coordonnée.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .landmarks import Landmark
from .measurements import GeometryError, ccd_angle, tonnis_angle, vce_angle

# Landmarks nécessaires à chaque mesure, par côté.
_REQUIRED = {
    "vce": ("TD_R", "TD_L", "FHC", "ASL"),
    "tonnis": ("TD_R", "TD_L", "ASM", "ASL"),
    "ccd": ("FHC", "FNM", "FSP", "FSD"),
}


@dataclass
class MeasurementResult:
    """Résultat d'une mesure : valeur en degrés ou raison d'indisponibilité."""

    name: str
    side: str
    value_deg: Optional[float] = None
    available: bool = False
    reason: Optional[str] = None

    def __str__(self) -> str:
        if self.available:
            return f"{self.name}_{self.side} = {self.value_deg:.2f}°"
        return f"{self.name}_{self.side} = indisponible ({self.reason})"


@dataclass
class SideResult:
    side: str
    vce: MeasurementResult
    tonnis: MeasurementResult
    ccd: MeasurementResult

    def as_dict(self) -> Dict[str, Optional[float]]:
        return {
            "vce": self.vce.value_deg,
            "tonnis": self.tonnis.value_deg,
            "ccd": self.ccd.value_deg,
        }


def _resolve(landmarks: Dict[str, Landmark], base_name: str, side: str):
    """Retourne (point, raison). `base_name` sans suffixe reçoit le côté."""
    full_name = base_name if base_name.endswith(("_R", "_L")) else f"{base_name}_{side}"
    landmark = landmarks.get(full_name)
    if landmark is None:
        return None, f"{full_name} absent du schéma"
    if not landmark.usable:
        return None, f"{full_name} non exploitable (v={landmark.v})"
    return landmark.point, None


def _gather(landmarks: Dict[str, Landmark], measure: str, side: str):
    """Résout tous les points requis pour une mesure. Retourne (points, reason)."""
    points = {}
    for base_name in _REQUIRED[measure]:
        point, reason = _resolve(landmarks, base_name, side)
        if point is None:
            return None, reason
        # Clé stable : "td_r"/"td_l" pour les teardrops, "fhc"/"asl"/... sinon.
        points[base_name.lower()] = point
    return points, None


def compute_side(landmarks: Dict[str, Landmark], side: str) -> SideResult:
    """Calcule les trois mesures pour un côté ('R' ou 'L')."""
    side = side.upper()

    vce_result = MeasurementResult("VCE", side)
    points, reason = _gather(landmarks, "vce", side)
    if points is None:
        vce_result.reason = reason
    else:
        try:
            vce_result.value_deg = vce_angle(
                points["td_r"], points["td_l"], points["fhc"], points["asl"], side
            )
            vce_result.available = True
        except GeometryError as error:
            vce_result.reason = str(error)

    tonnis_result = MeasurementResult("Tonnis", side)
    points, reason = _gather(landmarks, "tonnis", side)
    if points is None:
        tonnis_result.reason = reason
    else:
        try:
            tonnis_result.value_deg = tonnis_angle(
                points["td_r"], points["td_l"], points["asm"], points["asl"], side
            )
            tonnis_result.available = True
        except GeometryError as error:
            tonnis_result.reason = str(error)

    ccd_result = MeasurementResult("CCD", side)
    points, reason = _gather(landmarks, "ccd", side)
    if points is None:
        ccd_result.reason = reason
    else:
        try:
            ccd_result.value_deg = ccd_angle(
                points["fhc"], points["fnm"], points["fsp"], points["fsd"]
            )
            ccd_result.available = True
        except GeometryError as error:
            ccd_result.reason = str(error)

    return SideResult(side=side, vce=vce_result, tonnis=tonnis_result, ccd=ccd_result)


def compute_all_sides(landmarks: Dict[str, Landmark]) -> Dict[str, SideResult]:
    """Calcule les mesures pour les deux hanches."""
    return {"R": compute_side(landmarks, "R"), "L": compute_side(landmarks, "L")}
