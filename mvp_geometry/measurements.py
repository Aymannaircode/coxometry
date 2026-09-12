"""Primitives géométriques et les trois mesures coxométriques du MVP.

Toutes les fonctions travaillent sur des points 2D `(x, y)` en pixels image,
origine au coin supérieur haut-gauche, axe `y` orienté vers le bas (convention
image). La convention radiographique AP est : droite patient à gauche de
l'image. Aucune coordonnée n'est générée ici ; les fonctions consomment
uniquement des points fournis par l'appelant.
"""

from __future__ import annotations

import math
from typing import Tuple

Point = Tuple[float, float]
Vector = Tuple[float, float]

# Seuil de longueur en dessous duquel deux points sont considérés confondus
# (vecteur nul non orientable). En pixels, 1e-6 est très en dessous du bruit
# d'annotation réel tout en évitant les divisions par ~0.
_MIN_LENGTH = 1e-6


class GeometryError(ValueError):
    """Erreur levée lorsqu'une construction géométrique est indéterminée."""


def _subtract(a: Point, b: Point) -> Vector:
    """Vecteur allant de `a` vers `b`."""
    return (b[0] - a[0], b[1] - a[1])


def _norm(v: Vector) -> float:
    return math.hypot(v[0], v[1])


def _unit(v: Vector, *, what: str = "vecteur") -> Vector:
    length = _norm(v)
    if length < _MIN_LENGTH:
        raise GeometryError(f"{what} de longueur quasi nulle : direction indéterminée.")
    return (v[0] / length, v[1] / length)


def _dot(a: Vector, b: Vector) -> float:
    return a[0] * b[0] + a[1] * b[1]


def _cross(a: Vector, b: Vector) -> float:
    return a[0] * b[1] - a[1] * b[0]


def angle_between_vectors(u: Vector, v: Vector) -> float:
    """Angle non signé (degrés, 0..180) entre deux vecteurs non nuls."""
    unit_u = _unit(u, what="premier vecteur")
    unit_v = _unit(v, what="second vecteur")
    # atan2(|cross|, dot) est numériquement stable près de 0° et 180°,
    # contrairement à acos(dot).
    return math.degrees(math.atan2(abs(_cross(unit_u, unit_v)), _dot(unit_u, unit_v)))


def _perp_cranial(ith: Vector) -> Vector:
    """Perpendiculaire unitaire à `ith`, orientée en crânial (y négatif).

    Les deux perpendiculaires à la droite inter-teardrop représentent les
    directions « verticales » pelviennes. Sur un cliché AP orthograde (ou
    faiblement incliné, < 90°), la direction crâniale est celle dont la
    composante `y` est négative (vers le haut de l'image).
    """
    perpendicular = (-ith[1], ith[0])
    if perpendicular[1] > 0:
        perpendicular = (-perpendicular[0], -perpendicular[1])
    return _unit(perpendicular, what="perpendiculaire à ITH")


def _lateral_direction(ith_r_to_l: Vector, side: str) -> Vector:
    """Direction unitaire latérale (vers l'extérieur) pour la hanche donnée.

    `ith_r_to_l` va de `TD_R` vers `TD_L`. Le latéral du côté droit patient
    pointe vers `TD_R` (sens opposé), le latéral du côté gauche vers `TD_L`.
    """
    normalized_side = side.upper()
    if normalized_side == "R":
        return _unit((-ith_r_to_l[0], -ith_r_to_l[1]), what="ITH")
    if normalized_side == "L":
        return _unit(ith_r_to_l, what="ITH")
    raise GeometryError(f"Côté inconnu : {side!r} (attendu 'R' ou 'L').")


def vce_angle(td_r: Point, td_l: Point, fhc: Point, asl: Point, side: str) -> float:
    """Angle VCE / LCEA de Wiberg (degrés) pour la hanche `side`.

    Construction (spec §3.1) : verticale = perpendiculaire à ITH passant par
    FHC ; mesure = angle entre cette verticale et FHC -> ASL. Le signe est
    positif lorsque ASL est latéral à la verticale (couverture normale) et
    négatif lorsque ASL est médial (sous-couverture / dysplasie).
    """
    ith = _subtract(td_r, td_l)
    if _norm(ith) < _MIN_LENGTH:
        raise GeometryError("TD_R et TD_L confondus : ITH indéterminée.")

    coverage = _subtract(fhc, asl)
    if _norm(coverage) < _MIN_LENGTH:
        raise GeometryError("FHC et ASL confondus : direction de couverture indéterminée.")

    lateral = _lateral_direction(ith, side)
    cranial = _perp_cranial(ith)

    lateral_component = _dot(coverage, lateral)
    cranial_component = _dot(coverage, cranial)
    return math.degrees(math.atan2(lateral_component, cranial_component))


def tonnis_angle(td_r: Point, td_l: Point, asm: Point, asl: Point, side: str) -> float:
    """Angle de Tönnis (degrés) pour la hanche `side`.

    Construction (spec §3.2) : horizontale = parallèle à ITH passant par ASM ;
    mesure = angle entre cette horizontale et ASM -> ASL. Le signe est positif
    lorsque le sourcil s'incline vers le bas en latéral (dysplasie typique).
    """
    ith = _subtract(td_r, td_l)
    if _norm(ith) < _MIN_LENGTH:
        raise GeometryError("TD_R et TD_L confondus : ITH indéterminée.")

    sourcil = _subtract(asm, asl)
    if _norm(sourcil) < _MIN_LENGTH:
        raise GeometryError("ASM et ASL confondus : sourcil indéterminé (Tönnis non défini).")

    lateral = _lateral_direction(ith, side)
    # Caudal = perpendiculaire à ITH orientée vers le bas de l'image.
    cranial = _perp_cranial(ith)
    caudal = (-cranial[0], -cranial[1])

    lateral_component = _dot(sourcil, lateral)
    caudal_component = _dot(sourcil, caudal)
    return math.degrees(math.atan2(caudal_component, lateral_component))


def ccd_angle(fhc: Point, fnm: Point, fsp: Point, fsd: Point) -> float:
    """Angle CCD / neck-shaft (degrés, 0..180).

    Construction (spec §3.3) : angle médial entre l'axe du col FHC -> FNM et
    l'axe diaphysaire FSP -> FSD. On mesure entre le rayon col orienté vers la
    tête (FNM -> FHC) et le rayon diaphysaire orienté distalement (FSP -> FSD),
    ce qui fournit intrinsèquement l'angle médial (typiquement obtus ~120-135°).
    Ne dépend ni des teardrops ni du côté.
    """
    neck_to_head = _subtract(fnm, fhc)
    if _norm(neck_to_head) < _MIN_LENGTH:
        raise GeometryError("FHC et FNM confondus : axe du col indéterminé.")

    shaft_distal = _subtract(fsp, fsd)
    if _norm(shaft_distal) < _MIN_LENGTH:
        raise GeometryError("FSP et FSD confondus : axe diaphysaire indéterminé.")

    return angle_between_vectors(neck_to_head, shaft_distal)
