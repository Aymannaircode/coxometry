"""Chargement en lecture seule des landmarks au format `mvp-pilot-1.0`.

Ce module lit les gabarits / annotations JSON du pilote sans jamais les
modifier. Il n'écrit aucun fichier et n'accède pas à Dataset1/.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

Point = Tuple[float, float]

SCHEMA_VERSION = "mvp-pilot-1.0"

# Les 14 landmarks obligatoires, dans l'ordre de la spécification.
MVP_LANDMARK_NAMES = (
    "TD_R", "TD_L",
    "FHC_R", "FHC_L",
    "ASL_R", "ASL_L",
    "ASM_R", "ASM_L",
    "FNM_R", "FNM_L",
    "FSP_R", "FSP_L",
    "FSD_R", "FSD_L",
)


@dataclass(frozen=True)
class Landmark:
    """Un landmark tel que stocké dans le schéma pilote."""

    id: str
    name: str
    side: str
    x: Optional[float]
    y: Optional[float]
    v: Optional[int]

    @property
    def point(self) -> Optional[Point]:
        if self.x is None or self.y is None:
            return None
        return (float(self.x), float(self.y))

    @property
    def usable(self) -> bool:
        """Vrai si le point est exploitable pour un calcul.

        Conformément au protocole pilote, seul `v=2` (point net, posé par clic
        humain) est exploité. `v=1` est désactivé et `v=0`/`None` signifient
        « non annoté / non fiable ».
        """
        return self.v == 2 and self.point is not None


def load_pilot_schema(path: str | Path) -> dict:
    """Charge un fichier JSON au format pilote (lecture seule)."""
    file_path = Path(path)
    data = json.loads(file_path.read_text(encoding="utf-8-sig"))
    version = data.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ValueError(
            f"Version de schéma inattendue : {version!r} (attendu {SCHEMA_VERSION!r})."
        )
    return data


def landmarks_by_name(schema: dict) -> Dict[str, Landmark]:
    """Indexe les landmarks d'un schéma par nom (`TD_R`, `FHC_L`, ...)."""
    result: Dict[str, Landmark] = {}
    for entry in schema.get("landmarks", []):
        landmark = Landmark(
            id=entry.get("id"),
            name=entry.get("name"),
            side=entry.get("side"),
            x=entry.get("x"),
            y=entry.get("y"),
            v=entry.get("v"),
        )
        result[landmark.name] = landmark
    return result
