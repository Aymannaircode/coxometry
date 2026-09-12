"""Module de calcul géométrique des mesures coxométriques MVP.

Trois mesures, définies dans docs/landmark_specification.md (section 3) :

- VCE / Wiberg (LCEA) : angle entre la verticale pelvienne (perpendiculaire à
  la droite inter-teardrop ITH, passant par FHC) et la droite FHC -> ASL.
- Tönnis : angle entre l'horizontale pelvienne (parallèle à ITH, passant par
  ASM) et la droite du sourcil ASM -> ASL.
- CCD : angle médial entre l'axe du col FHC -> FNM et l'axe diaphysaire
  FSP -> FSD.

Le module ne contient aucune IA, aucune inférence, aucun apprentissage. Les
coordonnées proviennent exclusivement de saisies manuelles ou de tests
synthétiques ; le module ne lit ni ne modifie Dataset1/.
"""

from .measurements import (
    GeometryError,
    angle_between_vectors,
    ccd_angle,
    tonnis_angle,
    vce_angle,
)
from .landmarks import (
    Landmark,
    landmarks_by_name,
    load_pilot_schema,
)
from .hip_measures import (
    MeasurementResult,
    compute_all_sides,
    compute_side,
)
from .yolo_adapter import (
    landmarks_from_yolo_label,
    landmarks_from_yolo_label_with_refinement,
    parse_yolo_pose_line,
)
from .refinement import (
    ASL_L_REFINEMENT_ENABLED,
    AslLCalibration,
    AslLRefinementResult,
    RefinementStatus,
    TRAIN_ASM_OFFSET_CALIBRATION,
    refine_asl_l,
    refine_asl_l_landmarks,
)

__all__ = [
    "GeometryError",
    "angle_between_vectors",
    "vce_angle",
    "tonnis_angle",
    "ccd_angle",
    "Landmark",
    "load_pilot_schema",
    "landmarks_by_name",
    "MeasurementResult",
    "compute_side",
    "compute_all_sides",
    "landmarks_from_yolo_label",
    "landmarks_from_yolo_label_with_refinement",
    "parse_yolo_pose_line",
    "ASL_L_REFINEMENT_ENABLED",
    "AslLCalibration",
    "AslLRefinementResult",
    "RefinementStatus",
    "TRAIN_ASM_OFFSET_CALIBRATION",
    "refine_asl_l",
    "refine_asl_l_landmarks",
]
