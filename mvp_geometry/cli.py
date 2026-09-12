"""Interface en ligne de commande (lecture seule) du module géométrique.

Exemples :

    # À partir d'un JSON pilote (aucune écriture) :
    python -m mvp_geometry.cli --json annotation_pilot/annotations/annotator_A/P01_a308.json

    # À partir de coordonnées saisies manuellement :
    python -m mvp_geometry.cli --manual "TD_R=300,500;TD_L=500,500;FHC_R=200,400;ASL_R=157.7,309.4"

    # Démonstration synthétique (hanche droite normale) :
    python -m mvp_geometry.cli --demo
"""

from __future__ import annotations

import argparse
import math
import sys
from typing import Dict

from .landmarks import Landmark, landmarks_by_name, load_pilot_schema
from .hip_measures import compute_all_sides


def _use_utf8_stdout() -> None:
    """Évite les caractères mal affichés (°, é) sur les consoles Windows."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def _parse_manual(text: str) -> Dict[str, Landmark]:
    """Convertit 'TD_R=300,500;FHC_R=200,400' en landmarks exploitables (v=2)."""
    landmarks: Dict[str, Landmark] = {}
    for chunk in text.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        name, _, coords = chunk.partition("=")
        name = name.strip()
        try:
            x_str, y_str = coords.split(",")
            x, y = float(x_str), float(y_str)
        except ValueError as error:
            raise SystemExit(f"Coordonnées invalides pour {name!r} : {coords!r} ({error})")
        side = "R" if name.endswith("_R") else "L" if name.endswith("_L") else "M"
        landmarks[name] = Landmark(id=name, name=name, side=side, x=x, y=y, v=2)
    return landmarks


def _demo_landmarks() -> Dict[str, Landmark]:
    """Jeu synthétique cohérent : hanche droite VCE=25°, Tönnis=10°, CCD=130°.

    Construit analytiquement pour que les trois mesures tombent sur des valeurs
    exactes, avec un FHC partagé par VCE et CCD et un ASL partagé par VCE et
    Tönnis (comme sur une vraie annotation).
    """
    td_r, td_l = (300.0, 500.0), (500.0, 500.0)
    fsp, fsd = (400.0, 600.0), (400.0, 900.0)
    fnm = (360.0, 560.0)

    # CCD = 130° : col FNM -> FHC à 130° de l'axe diaphysaire distal (0, +1).
    ccd = math.radians(130.0)
    fhc = (fnm[0] + 100.0 * math.sin(ccd), fnm[1] + 100.0 * math.cos(ccd))

    # VCE = 25° : ASL à 25° de la verticale crâniale (0, -1), côté latéral (-1, 0).
    vce = math.radians(25.0)
    asl = (fhc[0] - 100.0 * math.sin(vce), fhc[1] - 100.0 * math.cos(vce))

    # Tönnis = 10° : ASM tel que ASM -> ASL fasse 10° sous l'horizontale.
    tonnis = math.radians(10.0)
    sourcil = (-120.0 * math.cos(tonnis), 120.0 * math.sin(tonnis))
    asm = (asl[0] - sourcil[0], asl[1] - sourcil[1])

    raw = {
        "TD_R": td_r, "TD_L": td_l,
        "FHC_R": fhc, "ASL_R": asl, "ASM_R": asm,
        "FNM_R": fnm, "FSP_R": fsp, "FSD_R": fsd,
    }
    return {
        name: Landmark(id=name, name=name, side="R", x=round(x, 3), y=round(y, 3), v=2)
        for name, (x, y) in raw.items()
    }


def _print_results(landmarks: Dict[str, Landmark]) -> None:
    results = compute_all_sides(landmarks)
    for side in ("R", "L"):
        side_result = results[side]
        label = "DROITE patient" if side == "R" else "GAUCHE patient"
        print(f"\n=== Hanche {side} ({label}) ===")
        for measure in (side_result.vce, side_result.tonnis, side_result.ccd):
            print(f"  {measure}")


def main(argv=None) -> int:
    _use_utf8_stdout()
    parser = argparse.ArgumentParser(description="Calcul VCE / Tönnis / CCD (lecture seule).")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--json", help="Chemin d'un JSON pilote (schéma mvp-pilot-1.0).")
    source.add_argument("--manual", help="Coordonnées 'NAME=x,y;...' (v=2 implicite).")
    source.add_argument("--demo", action="store_true", help="Exemple synthétique.")
    args = parser.parse_args(argv)

    if args.demo:
        landmarks = _demo_landmarks()
        print("Démonstration synthétique (hanche droite construite analytiquement).")
    elif args.manual:
        landmarks = _parse_manual(args.manual)
    else:
        schema = load_pilot_schema(args.json)
        landmarks = landmarks_by_name(schema)
        print(f"Fichier : {args.json} (image_id={schema.get('image_id')})")

    _print_results(landmarks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
