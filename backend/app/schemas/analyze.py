"""Schémas Pydantic pour POST /analyze."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeMeasureOut(BaseModel):
    value_deg: Optional[float] = None
    available: bool = False
    reason: Optional[str] = None
    landmarks_used: Optional[List[str]] = None


class AnalyzeSideOut(BaseModel):
    vce: AnalyzeMeasureOut
    tonnis: AnalyzeMeasureOut
    ccd: AnalyzeMeasureOut


class AnalyzeMeasurementsOut(BaseModel):
    right: AnalyzeSideOut
    left: AnalyzeSideOut


class AnalyzeITLandmarkOut(BaseModel):
    """Landmark IT V5 (index 14 = IT_R, 15 = IT_L).

    ``v=0`` : non identifiable (x/y absents). ``quality`` : fiabilité QC
    (accept / review / unavailable) — distincte de la prédiction brute.
    """

    name: Literal["IT_R", "IT_L"]
    kp_index: int = Field(description="Index keypoint : 14 (IT_R) ou 15 (IT_L).")
    v: int
    x: Optional[float] = None
    y: Optional[float] = None
    confidence: Optional[float] = None
    quality: Optional[Literal["accept", "review", "unavailable"]] = Field(
        default=None,
        description="État QC : accept, review ou unavailable (V5 uniquement).",
    )
    quality_reasons: Optional[List[str]] = Field(
        default=None,
        description="Codes techniques QC stables (présentation localisée côté client).",
    )


class AnalyzeCoordinateSpaceOut(BaseModel):
    """Métadonnées de reprojection ; landmarks exposés en pixels image originale."""

    image_width: int
    image_height: int
    preprocessed_width: int
    preprocessed_height: int
    scale: float
    pad_x: int
    pad_y: int
    landmark_coordinate_space: Literal["original_image_pixels"] = "original_image_pixels"


class AnalyzeDetectionOut(BaseModel):
    bounding_box: Optional[Dict[str, float]] = None
    raw_landmarks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Jusqu'à 14 landmarks MVP (espace image originale).",
    )
    refined_landmarks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Landmarks MVP après refinement éventuel (ASL_L).",
    )
    it_landmarks: List[AnalyzeITLandmarkOut] = Field(
        default_factory=list,
        description="IT_R / IT_L (V5 Phase 2) ; liste vide en V2.",
    )
    refinement_enabled: bool = False
    refinement_applied: bool = False
    coordinate_space: AnalyzeCoordinateSpaceOut


class AnalyzeErrorDetail(BaseModel):
    code: str
    message: str


class AnalyzeSuccessResponse(BaseModel):
    status: Literal["ok"] = "ok"
    model_version: Literal["v2", "v5_phase2"] = Field(
        default="v2",
        description="Modèle utilisé : v2 (14 KP) ou v5_phase2 (16 KP + QC IT).",
    )
    detection: AnalyzeDetectionOut
    measurements: AnalyzeMeasurementsOut
    audit: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    error: AnalyzeErrorDetail
