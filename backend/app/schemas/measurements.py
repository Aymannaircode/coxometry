"""Requêtes et réponses de l'endpoint POST /measurements."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from .landmarks import LandmarkIn


class InputMode(str, Enum):
    """Mode d'entrée du pipeline.

    - `landmarks` : coordonnées fournies manuellement → calcul géométrique.
    - `image` : radiographie (JSON sans fichier, ou multipart avec upload).
    """

    landmarks = "landmarks"
    image = "image"


class MeasureOut(BaseModel):
    """Une mesure (VCE, Tönnis ou CCD) pour un côté."""

    name: str
    side: Literal["R", "L"]
    value_deg: Optional[float] = None
    available: bool = False
    reason: Optional[str] = None


class SideOut(BaseModel):
    """Mesures VCE / Tönnis / CCD pour une hanche."""

    side: Literal["R", "L"]
    vce: MeasureOut
    tonnis: MeasureOut
    ccd: MeasureOut


class MeasurementsRequest(BaseModel):
    """Corps de `POST /measurements`.

    Mode `landmarks` : fournir une liste de landmarks manuels.
    Mode `image` (JSON sans octets) : `not_implemented` sans inventer de points.
    Pour un upload réel, utiliser `multipart/form-data` avec un fichier image.
    """

    mode: InputMode = Field(
        default=InputMode.landmarks,
        description="Source des landmarks : manuelle ou image.",
    )
    landmarks: Optional[List[LandmarkIn]] = Field(
        default=None,
        description="Landmarks manuels (requis si mode=landmarks).",
    )
    sides: Optional[List[Literal["R", "L"]]] = Field(
        default=None,
        description="Côtés à calculer (défaut : R et L).",
    )

    @model_validator(mode="after")
    def validate_mode_payload(self) -> MeasurementsRequest:
        if self.mode == InputMode.landmarks:
            if not self.landmarks:
                raise ValueError(
                    "mode=landmarks exige une liste non vide de landmarks fournis manuellement."
                )
        if self.sides is not None:
            if len(self.sides) == 0:
                raise ValueError("sides ne peut pas être une liste vide.")
            if len(set(self.sides)) != len(self.sides):
                raise ValueError("sides ne doit pas contenir de doublons.")
        return self


class MeasurementsResponse(BaseModel):
    """Réponse structurée pour l'application Flutter (future)."""

    status: Literal["ok", "not_implemented", "error"]
    mode: InputMode
    source: Literal["manual_landmarks", "image"]
    message: Optional[str] = None
    sides: Optional[Dict[str, SideOut]] = None
