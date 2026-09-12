"""Modèles Pydantic pour les landmarks fournis manuellement.

Les noms suivent `mvp_geometry.landmarks.MVP_LANDMARK_NAMES` et la
spécification `docs/landmark_specification.md`. Aucune coordonnée n'est
générée ici : l'appelant doit fournir explicitement `x`, `y` et `v`.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class LandmarkName(str, Enum):
    """Les 14 landmarks obligatoires du schéma pilote MVP."""

    TD_R = "TD_R"
    TD_L = "TD_L"
    FHC_R = "FHC_R"
    FHC_L = "FHC_L"
    ASL_R = "ASL_R"
    ASL_L = "ASL_L"
    ASM_R = "ASM_R"
    ASM_L = "ASM_L"
    FNM_R = "FNM_R"
    FNM_L = "FNM_L"
    FSP_R = "FSP_R"
    FSP_L = "FSP_L"
    FSD_R = "FSD_R"
    FSD_L = "FSD_L"


class LandmarkIn(BaseModel):
    """Landmark saisi manuellement (pas de détection IA).

    Convention pixels image : origine coin haut-gauche, `y` vers le bas.
    Seul `v=2` est exploitable pour le calcul (protocole pilote).
    """

    name: LandmarkName
    x: Optional[float] = Field(default=None, description="Abscisse en pixels image")
    y: Optional[float] = Field(default=None, description="Ordonnée en pixels image")
    v: Optional[int] = Field(
        default=None,
        description="Visibilité : 2=exploitable, 0/1/null=non exploitable",
    )

    @model_validator(mode="after")
    def coordinates_consistency(self) -> LandmarkIn:
        has_x = self.x is not None
        has_y = self.y is not None
        if has_x != has_y:
            raise ValueError(
                f"{self.name.value}: x et y doivent être fournis ensemble ou tous deux absents."
            )
        if self.v is not None and self.v not in (0, 1, 2):
            raise ValueError(f"{self.name.value}: v doit être 0, 1, 2 ou null.")
        return self
