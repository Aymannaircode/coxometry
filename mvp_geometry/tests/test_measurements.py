"""Tests analytiques des mesures VCE, Tönnis et CCD.

Chaque cas nominal est construit à partir d'un angle cible connu, de sorte que
la valeur attendue est exacte (aux erreurs d'arrondi flottant près). On teste
aussi l'invariance par translation, mise à l'échelle et rotation modérée, ainsi
que les cas dégénérés. Aucune donnée réelle n'est utilisée.
"""

from __future__ import annotations

import math
import unittest

from mvp_geometry.landmarks import Landmark
from mvp_geometry.hip_measures import compute_side
from mvp_geometry.measurements import (
    GeometryError,
    angle_between_vectors,
    ccd_angle,
    tonnis_angle,
    vce_angle,
)

Point = tuple


def rotate(point, degrees, origin=(0.0, 0.0)):
    angle = math.radians(degrees)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    dx, dy = point[0] - origin[0], point[1] - origin[1]
    return (
        origin[0] + dx * cos_a - dy * sin_a,
        origin[1] + dx * sin_a + dy * cos_a,
    )


def scale(point, factor, origin=(0.0, 0.0)):
    return (origin[0] + (point[0] - origin[0]) * factor,
            origin[1] + (point[1] - origin[1]) * factor)


def translate(point, dx, dy):
    return (point[0] + dx, point[1] + dy)


def build_vce_case(target_deg, side, fhc=(200.0, 400.0), radius=100.0):
    """Construit (td_r, td_l, fhc, asl) donnant un VCE = target_deg exact.

    ITH est horizontale ; la verticale crâniale est (0, -1). Le latéral vaut
    (-1, 0) à droite et (1, 0) à gauche.
    """
    td_r, td_l = (300.0, 500.0), (500.0, 500.0)
    lateral = (-1.0, 0.0) if side == "R" else (1.0, 0.0)
    cranial = (0.0, -1.0)
    theta = math.radians(target_deg)
    coverage = (
        radius * (math.sin(theta) * lateral[0] + math.cos(theta) * cranial[0]),
        radius * (math.sin(theta) * lateral[1] + math.cos(theta) * cranial[1]),
    )
    asl = (fhc[0] + coverage[0], fhc[1] + coverage[1])
    return td_r, td_l, fhc, asl


def build_tonnis_case(target_deg, side, asm=(250.0, 300.0), radius=120.0):
    """Construit (td_r, td_l, asm, asl) donnant un Tönnis = target_deg exact."""
    td_r, td_l = (300.0, 500.0), (500.0, 500.0)
    lateral = (-1.0, 0.0) if side == "R" else (1.0, 0.0)
    caudal = (0.0, 1.0)
    t = math.radians(target_deg)
    sourcil = (
        radius * (math.cos(t) * lateral[0] + math.sin(t) * caudal[0]),
        radius * (math.cos(t) * lateral[1] + math.sin(t) * caudal[1]),
    )
    asl = (asm[0] + sourcil[0], asm[1] + sourcil[1])
    return td_r, td_l, asm, asl


def build_ccd_case(target_deg, side, fnm=(360.0, 560.0), neck_len=100.0):
    """Construit (fhc, fnm, fsp, fsd) donnant un CCD = target_deg exact.

    Diaphyse verticale (FSP au-dessus de FSD). Le col part de FNM vers la tête
    (médial + crânial), à l'angle voulu par rapport à l'axe diaphysaire distal.
    """
    fsp, fsd = (400.0, 600.0), (400.0, 900.0)
    medial_sign = 1.0 if side == "R" else -1.0  # médial droit = +x
    angle = math.radians(target_deg)
    neck_to_head = (
        neck_len * medial_sign * math.sin(angle),
        neck_len * math.cos(angle),  # cos(130°)<0 => vers le haut (crânial)
    )
    fhc = (fnm[0] + neck_to_head[0], fnm[1] + neck_to_head[1])
    return fhc, fnm, fsp, fsd


class TestAngleBetween(unittest.TestCase):
    def test_orthogonal(self):
        self.assertAlmostEqual(angle_between_vectors((1, 0), (0, 1)), 90.0, places=9)

    def test_opposite(self):
        self.assertAlmostEqual(angle_between_vectors((1, 0), (-1, 0)), 180.0, places=9)

    def test_parallel(self):
        self.assertAlmostEqual(angle_between_vectors((2, 0), (5, 0)), 0.0, places=9)

    def test_zero_vector_raises(self):
        with self.assertRaises(GeometryError):
            angle_between_vectors((0, 0), (1, 0))


class TestVce(unittest.TestCase):
    def test_right_nominal(self):
        for target in (0.0, 12.5, 25.0, 40.0, 55.0):
            td_r, td_l, fhc, asl = build_vce_case(target, "R")
            self.assertAlmostEqual(vce_angle(td_r, td_l, fhc, asl, "R"), target, places=6)

    def test_left_nominal(self):
        for target in (0.0, 15.0, 30.0, 45.0):
            td_r, td_l, fhc, asl = build_vce_case(target, "L")
            self.assertAlmostEqual(vce_angle(td_r, td_l, fhc, asl, "L"), target, places=6)

    def test_negative_when_edge_medial(self):
        # ASL médial à la verticale => sous-couverture => VCE négatif.
        td_r, td_l, fhc, asl = build_vce_case(-15.0, "R")
        self.assertAlmostEqual(vce_angle(td_r, td_l, fhc, asl, "R"), -15.0, places=6)

    def test_invariance_translation_scale(self):
        td_r, td_l, fhc, asl = build_vce_case(25.0, "R")
        pts = [td_r, td_l, fhc, asl]
        moved = [translate(p, 123.4, -56.7) for p in pts]
        scaled = [scale(p, 3.5) for p in moved]
        self.assertAlmostEqual(vce_angle(*scaled, "R"), 25.0, places=6)

    def test_invariance_moderate_tilt(self):
        # La verticale étant définie perpendiculairement à ITH, une inclinaison
        # pelvienne modérée (< 90°) ne doit pas changer le VCE.
        td_r, td_l, fhc, asl = build_vce_case(30.0, "R")
        for tilt in (-25.0, -10.0, 10.0, 25.0):
            pts = [rotate(p, tilt) for p in (td_r, td_l, fhc, asl)]
            self.assertAlmostEqual(vce_angle(*pts, "R"), 30.0, places=6)


class TestTonnis(unittest.TestCase):
    def test_right_nominal(self):
        for target in (0.0, 5.0, 10.0, 20.0, 35.0):
            td_r, td_l, asm, asl = build_tonnis_case(target, "R")
            self.assertAlmostEqual(tonnis_angle(td_r, td_l, asm, asl, "R"), target, places=6)

    def test_left_nominal(self):
        for target in (0.0, 8.0, 18.0):
            td_r, td_l, asm, asl = build_tonnis_case(target, "L")
            self.assertAlmostEqual(tonnis_angle(td_r, td_l, asm, asl, "L"), target, places=6)

    def test_negative_when_roof_upslopes(self):
        td_r, td_l, asm, asl = build_tonnis_case(-6.0, "R")
        self.assertAlmostEqual(tonnis_angle(td_r, td_l, asm, asl, "R"), -6.0, places=6)

    def test_invariance_moderate_tilt(self):
        td_r, td_l, asm, asl = build_tonnis_case(12.0, "R")
        for tilt in (-25.0, -10.0, 10.0, 25.0):
            pts = [rotate(p, tilt) for p in (td_r, td_l, asm, asl)]
            self.assertAlmostEqual(tonnis_angle(*pts, "R"), 12.0, places=6)


class TestCcd(unittest.TestCase):
    def test_right_nominal(self):
        for target in (110.0, 125.0, 130.0, 140.0):
            fhc, fnm, fsp, fsd = build_ccd_case(target, "R")
            self.assertAlmostEqual(ccd_angle(fhc, fnm, fsp, fsd), target, places=6)

    def test_left_nominal(self):
        for target in (118.0, 128.0, 135.0):
            fhc, fnm, fsp, fsd = build_ccd_case(target, "L")
            self.assertAlmostEqual(ccd_angle(fhc, fnm, fsp, fsd), target, places=6)

    def test_full_rotation_invariance(self):
        # Le CCD ne dépend d'aucune référence externe : invariant sous toute
        # rotation, translation et mise à l'échelle.
        fhc, fnm, fsp, fsd = build_ccd_case(127.0, "R")
        for angle in (-140.0, -35.0, 47.0, 190.0):
            pts = [rotate(p, angle, origin=(500.0, 500.0)) for p in (fhc, fnm, fsp, fsd)]
            pts = [scale(p, 2.0) for p in pts]
            self.assertAlmostEqual(ccd_angle(*pts), 127.0, places=6)


class TestDegenerate(unittest.TestCase):
    def test_vce_coincident_teardrops(self):
        with self.assertRaises(GeometryError):
            vce_angle((300, 500), (300, 500), (200, 400), (157, 309), "R")

    def test_vce_fhc_equals_asl(self):
        with self.assertRaises(GeometryError):
            vce_angle((300, 500), (500, 500), (200, 400), (200, 400), "R")

    def test_tonnis_asm_equals_asl(self):
        with self.assertRaises(GeometryError):
            tonnis_angle((300, 500), (500, 500), (250, 300), (250, 300), "R")

    def test_ccd_fhc_equals_fnm(self):
        with self.assertRaises(GeometryError):
            ccd_angle((200, 400), (200, 400), (110, 400), (110, 700))

    def test_ccd_fsp_equals_fsd(self):
        with self.assertRaises(GeometryError):
            ccd_angle((200, 400), (140, 360), (110, 400), (110, 400))

    def test_unknown_side(self):
        with self.assertRaises(GeometryError):
            vce_angle((300, 500), (500, 500), (200, 400), (157, 309), "X")


class TestHighLevelApi(unittest.TestCase):
    def _landmarks_for_full_right_hip(self):
        # FHC est partagé par VCE et CCD : on le fixe via la construction CCD,
        # puis on bâtit le VCE autour de ce même centre de tête.
        fhc, fnm, fsp, fsd = build_ccd_case(130.0, "R")
        td_r, td_l, _fhc, asl = build_vce_case(25.0, "R", fhc=fhc)
        _, _, asm, _asl_t = build_tonnis_case(10.0, "R")
        raw = {
            "TD_R": td_r, "TD_L": td_l,
            "FHC_R": fhc, "ASL_R": asl,
            "ASM_R": asm,
            "FNM_R": fnm, "FSP_R": fsp, "FSD_R": fsd,
        }
        return {
            name: Landmark(id=name, name=name, side="R", x=x, y=y, v=2)
            for name, (x, y) in raw.items()
        }

    def test_compute_side_right(self):
        landmarks = self._landmarks_for_full_right_hip()
        result = compute_side(landmarks, "R")
        self.assertTrue(result.vce.available)
        self.assertTrue(result.ccd.available)
        self.assertTrue(result.tonnis.available)
        self.assertAlmostEqual(result.vce.value_deg, 25.0, places=5)
        self.assertAlmostEqual(result.ccd.value_deg, 130.0, places=5)

    def test_missing_landmark_reported(self):
        landmarks = self._landmarks_for_full_right_hip()
        del landmarks["FNM_R"]
        result = compute_side(landmarks, "R")
        self.assertFalse(result.ccd.available)
        self.assertIn("FNM_R", result.ccd.reason)
        # Les autres mesures restent disponibles.
        self.assertTrue(result.vce.available)

    def test_v0_landmark_not_usable(self):
        landmarks = self._landmarks_for_full_right_hip()
        old = landmarks["ASL_R"]
        landmarks["ASL_R"] = Landmark(old.id, old.name, old.side, None, None, 0)
        result = compute_side(landmarks, "R")
        self.assertFalse(result.vce.available)
        self.assertFalse(result.tonnis.available)
        # CCD n'utilise pas ASL et reste disponible.
        self.assertTrue(result.ccd.available)


if __name__ == "__main__":
    unittest.main()
