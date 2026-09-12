"""Abstraction `LandmarkDetector` et types de sortie structurés.

Contrat du futur pipeline :

    PreprocessedImage
        ↓ LandmarkDetector.detect()
    landmarks (espace prétraité)
        ↓ reprojection
    landmarks (image originale)
        ↓ adaptateur → mvp_geometry
    VCE / Tönnis / CCD

Aucun modèle n'est chargé ici. Aucune coordonnée anatomique n'est générée.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Optional, Sequence, Tuple

from mvp_geometry.landmarks import MVP_LANDMARK_NAMES

from ..preprocessing import PreprocessedImage

DetectionStatus = Literal["ok", "not_implemented", "error"]


class LandmarkFormatError(ValueError):
    """Format ou nom de landmark invalide."""


@dataclass(frozen=True)
class DetectedLandmark:
    """Landmark détecté dans l'espace de l'image **prétraitée**.

    Coordonnées en pixels image : origine coin haut-gauche, `y` vers le bas.
    Les noms suivent `mvp_geometry.landmarks.MVP_LANDMARK_NAMES`.
    """

    name: str
    x: float
    y: float
    confidence: Optional[float] = None

    def __post_init__(self) -> None:
        validate_landmark_name(self.name)


@dataclass(frozen=True)
class DetectionBoundingBox:
    """Boîte englobante pelvis dans l'espace prétraité (pixels)."""

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float


@dataclass(frozen=True)
class LandmarkDetectionResult:
    """Résultat brut du détecteur (avant reprojection).

    ``landmarks`` contient les points **refined** prêts pour la reprojection /
    ``mvp_geometry`` lorsque le refinement ASL_L est actif.
    ``raw_landmarks`` conserve la sortie YOLO brute (avant refinement).
    """

    status: DetectionStatus
    message: Optional[str] = None
    landmarks: Tuple[DetectedLandmark, ...] = ()
    raw_landmarks: Tuple[DetectedLandmark, ...] = ()
    bounding_box: Optional[DetectionBoundingBox] = None
    coordinate_space: Literal["preprocessed"] = "preprocessed"
    detector_name: Optional[str] = None
    audit: Optional[dict] = None
    it_landmarks: Tuple[Any, ...] = ()


def validate_landmark_name(name: str) -> None:
    """Vérifie que `name` est l'un des 14 landmarks MVP."""
    if name not in MVP_LANDMARK_NAMES:
        raise LandmarkFormatError(
            f"Nom de landmark invalide : {name!r}. "
            f"Attendu l'un de : {', '.join(MVP_LANDMARK_NAMES)}."
        )


def validate_detected_landmarks(landmarks: Sequence[DetectedLandmark]) -> None:
    """Vérifie l'ensemble : noms valides, pas de doublons."""
    seen: set[str] = set()
    for item in landmarks:
        validate_landmark_name(item.name)
        if item.name in seen:
            raise LandmarkFormatError(f"Landmark en double : {item.name!r}.")
        seen.add(item.name)


class LandmarkDetector(ABC):
    """Interface pour un détecteur de landmarks sur image prétraitée."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Identifiant lisible du détecteur (ex. 'not_implemented', 'yolo_pose')."""

    @abstractmethod
    def detect(self, image: PreprocessedImage) -> LandmarkDetectionResult:
        """Détecte les landmarks dans l'espace de `image` (prétraitée).

        Ne doit jamais inventer de coordonnées anatomiques lorsque le
        détecteur n'est pas opérationnel : retourner `status=not_implemented`
        ou `status=error` avec `landmarks` vide.
        """


class NotImplementedLandmarkDetector(LandmarkDetector):
    """Détecteur par défaut tant qu'aucun modèle n'est entraîné."""

    @property
    def name(self) -> str:
        return "not_implemented"

    def detect(self, image: PreprocessedImage) -> LandmarkDetectionResult:
        _ = image  # signature homogène ; aucune inférence.
        return LandmarkDetectionResult(
            status="not_implemented",
            message=(
                "La détection IA des landmarks n'est pas encore implémentée. "
                "Aucune coordonnée n'est générée automatiquement. "
                "Utiliser mode=landmarks avec des points fournis manuellement."
            ),
            landmarks=(),
            detector_name=self.name,
        )


_default_detector: LandmarkDetector = NotImplementedLandmarkDetector()


def get_default_detector() -> LandmarkDetector:
    """Retourne le détecteur actif (stub tant qu'aucun modèle n'existe)."""
    return _default_detector
