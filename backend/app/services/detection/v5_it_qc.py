"""Contrôle qualité anatomique conservateur pour IT_R / IT_L (V5 Phase 2).

Sépare explicitement la prédiction brute du modèle (``v``, coordonnées, confiance)
de l'évaluation de fiabilité (``quality``, ``quality_reasons``).

Les seuils numériques proviennent des 26 labels officiels 16 kp
(``datasets/yolo_pose_new_26/labels/{train,val}``) et des dimensions image
``b6_working_annotations`` — voir ``v5_phase2_landmark_qc_audit.md``.
Aucun accès aux labels en production.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Optional, Sequence

ITQualityStatus = Literal["accept", "review", "unavailable"]

# --- Seuils dérivés empiriquement (26 images, IT v=2 uniquement) ---
# dy_td_frac = (IT.y - TD_same_side.y) / image_height  — IT caudal au teardrop
# p10 train+val GT = 0.0939 ; marge conservative → 0.05
MIN_DY_TD_FRAC = 0.05

# dy_fhc_frac = (IT.y - FHC_same_side.y) / image_height
# p10 GT = 0.3144 ; marge → 0.28
MIN_DY_FHC_FRAC = 0.28

# dx_mid_frac : distance positive vers le côté patient attendu
# p10 GT = 0.1678 ; marge → 0.12
MIN_DX_MID_FRAC = 0.12

# Écart vertical bilatéral |IT_R.y - IT_L.y| / height — p90 GT ≈ 0.050
MAX_BILATERAL_Y_DIFF_FRAC = 0.06

# Ratio max(dx_R, dx_L) / min(dx_R, dx_L) depuis la ligne médiane TD — p90 GT ≈ 1.55
MAX_BILATERAL_DX_RATIO = 1.70

# Confiance modèle : complément au seuil inférence 0.25, pas critère unique
LOW_CONFIDENCE_REVIEW = 0.40

# Au-dessus de ce seuil, appliquer une marge IT–FSD plus stricte (sur-confiance connue)
HIGH_CONFIDENCE_REVIEW = 0.78
# it_fsd_frac = (IT.y - FSD_same_side.y) / height (négatif = IT crânial au FSD)
# Seuils calibrés sur prédictions val + distribution GT (audit Phase 2A)
HIGH_CONF_MAX_IT_FSD_FRAC_R = -0.025
HIGH_CONF_MAX_IT_FSD_FRAC_L = -0.048

# Tolérance pixels pour bornes image
BOUNDS_MARGIN_PX = 1.0


@dataclass(frozen=True)
class ITQCResult:
    """Résultat QC pour un landmark IT."""

    name: str
    quality: ITQualityStatus
    quality_reasons: tuple[str, ...]


def _pelvic_midline_x(mvp_landmarks: Mapping[str, Mapping[str, float]]) -> Optional[float]:
    """Ligne médiane pelvienne via TD_R / TD_L (paire bilatérale existante)."""
    try:
        td_r = mvp_landmarks["TD_R"]
        td_l = mvp_landmarks["TD_L"]
    except KeyError:
        return None
    return (float(td_r["x"]) + float(td_l["x"])) / 2.0


def _mvp_point(
    mvp_landmarks: Mapping[str, Mapping[str, float]],
    name: str,
) -> Optional[tuple[float, float]]:
    if name not in mvp_landmarks:
        return None
    item = mvp_landmarks[name]
    return float(item["x"]), float(item["y"])


def _assess_single_it(
    *,
    name: str,
    v: int,
    x: Optional[float],
    y: Optional[float],
    confidence: Optional[float],
    image_width: int,
    image_height: int,
    mvp_landmarks: Mapping[str, Mapping[str, float]],
    bilateral_context: Optional[Mapping[str, Any]] = None,
) -> ITQCResult:
    """Évalue la fiabilité d'un IT sans modifier la prédiction brute."""
    reasons: list[str] = []

    if v != 2 or x is None or y is None:
        return ITQCResult(name=name, quality="unavailable", quality_reasons=("model_v0",))

    h = float(image_height)
    w = float(image_width)

    # A. Bornes image
    if (
        x < -BOUNDS_MARGIN_PX
        or y < -BOUNDS_MARGIN_PX
        or x > w + BOUNDS_MARGIN_PX
        or y > h + BOUNDS_MARGIN_PX
    ):
        return ITQCResult(
            name=name,
            quality="unavailable",
            quality_reasons=("out_of_image_bounds",),
        )

    side = "R" if name == "IT_R" else "L"
    td_name = f"TD_{side}"
    fhc_name = f"FHC_{side}"
    fsd_name = f"FSD_{side}"

    midline_x = _pelvic_midline_x(mvp_landmarks)
    td = _mvp_point(mvp_landmarks, td_name)
    fhc = _mvp_point(mvp_landmarks, fhc_name)
    fsd = _mvp_point(mvp_landmarks, fsd_name)

    if midline_x is None or td is None:
        reasons.append("midline_unreliable")
    else:
        # B. Cohérence latérale (R = côté patient droit = moitié gauche de l'image)
        dx_mid = (x - midline_x) * (-1.0 if side == "R" else 1.0)
        dx_mid_frac = dx_mid / w
        if dx_mid_frac < 0.0:
            return ITQCResult(
                name=name,
                quality="unavailable",
                quality_reasons=("wrong_patient_side",),
            )
        if dx_mid_frac < MIN_DX_MID_FRAC:
            reasons.append("weak_lateral_placement")

    # C. Position caudale relative aux repères pelviens
    if td is not None:
        dy_td_frac = (y - td[1]) / h
        if dy_td_frac < MIN_DY_TD_FRAC:
            reasons.append("insufficient_caudal_vs_teardrop")
    if fhc is not None:
        dy_fhc_frac = (y - fhc[1]) / h
        if dy_fhc_frac < MIN_DY_FHC_FRAC:
            reasons.append("insufficient_caudal_vs_fhc")

    # E. Confiance (complémentaire)
    if confidence is not None and confidence < LOW_CONFIDENCE_REVIEW:
        reasons.append("low_model_confidence")

    # Sur-confiance : confiance élevée ne suffit pas si anatomie marginale
    if (
        confidence is not None
        and confidence >= HIGH_CONFIDENCE_REVIEW
        and fsd is not None
    ):
        it_fsd_frac = (y - fsd[1]) / h
        max_frac = (
            HIGH_CONF_MAX_IT_FSD_FRAC_R if side == "R" else HIGH_CONF_MAX_IT_FSD_FRAC_L
        )
        if it_fsd_frac > max_frac:
            reasons.append("high_confidence_marginal_it_fsd")

    # D. Plausibilité bilatérale (contexte partagé)
    if bilateral_context is not None:
        if bilateral_context.get("y_diff_review"):
            reasons.append("bilateral_vertical_asymmetry")
        if bilateral_context.get("dx_ratio_review"):
            reasons.append("bilateral_horizontal_asymmetry")
        if bilateral_context.get("order_violation"):
            return ITQCResult(
                name=name,
                quality="unavailable",
                quality_reasons=("bilateral_order_violation",),
            )

    if reasons:
        # Dédupliquer en conservant l'ordre
        seen: set[str] = set()
        unique = tuple(r for r in reasons if not (r in seen or seen.add(r)))  # type: ignore[func-returns-value]
        return ITQCResult(name=name, quality="review", quality_reasons=unique)

    return ITQCResult(name=name, quality="accept", quality_reasons=())


def _bilateral_context(
    it_items: Sequence[Mapping[str, Any]],
    image_width: int,
    image_height: int,
    midline_x: Optional[float],
) -> dict[str, dict[str, Any]]:
    """Calcule signaux bilatéraux partagés pour IT_R et IT_L."""
    by_name = {str(item["name"]): item for item in it_items}
    ctx: dict[str, dict[str, Any]] = {
        "IT_R": {"y_diff_review": False, "dx_ratio_review": False, "order_violation": False},
        "IT_L": {"y_diff_review": False, "dx_ratio_review": False, "order_violation": False},
    }
    it_r = by_name.get("IT_R")
    it_l = by_name.get("IT_L")
    if (
        it_r is None
        or it_l is None
        or it_r.get("v") != 2
        or it_l.get("v") != 2
        or it_r.get("x") is None
        or it_l.get("x") is None
        or it_r.get("y") is None
        or it_l.get("y") is None
    ):
        return ctx

    h = float(image_height)
    w = float(image_width)
    y_diff = abs(float(it_r["y"]) - float(it_l["y"])) / h
    y_review = y_diff > MAX_BILATERAL_Y_DIFF_FRAC

    order_violation = float(it_r["x"]) >= float(it_l["x"])

    dx_ratio_review = False
    if midline_x is not None:
        dx_r = (float(it_r["x"]) - midline_x) * -1.0
        dx_l = (float(it_l["x"]) - midline_x)
        if dx_r > 0 and dx_l > 0:
            ratio = max(dx_r, dx_l) / min(dx_r, dx_l)
            dx_ratio_review = ratio > MAX_BILATERAL_DX_RATIO

    for name in ("IT_R", "IT_L"):
        ctx[name] = {
            "y_diff_review": y_review,
            "dx_ratio_review": dx_ratio_review,
            "order_violation": order_violation,
        }
    return ctx


def assess_it_landmarks_qc(
    it_landmarks: Sequence[Mapping[str, Any]],
    *,
    image_width: int,
    image_height: int,
    mvp_landmarks: Sequence[Mapping[str, Any]],
) -> dict[str, ITQCResult]:
    """Évalue la qualité de tous les IT reprojetés (espace image originale)."""
    mvp_by_name = {str(item["name"]): item for item in mvp_landmarks}
    midline_x = _pelvic_midline_x(mvp_by_name)
    bilateral = _bilateral_context(
        it_landmarks,
        image_width,
        image_height,
        midline_x,
    )

    results: dict[str, ITQCResult] = {}
    for item in it_landmarks:
        name = str(item["name"])
        results[name] = _assess_single_it(
            name=name,
            v=int(item.get("v", 0)),
            x=item.get("x"),
            y=item.get("y"),
            confidence=item.get("confidence"),
            image_width=image_width,
            image_height=image_height,
            mvp_landmarks=mvp_by_name,
            bilateral_context=bilateral.get(name),
        )
    return results


def apply_qc_to_it_dicts(
    it_landmarks: list[dict[str, Any]],
    qc_results: Mapping[str, ITQCResult],
) -> list[dict[str, Any]]:
    """Enrichit les dicts IT reprojetés avec quality / quality_reasons (prédiction brute intacte)."""
    enriched: list[dict[str, Any]] = []
    for item in it_landmarks:
        name = str(item["name"])
        qc = qc_results.get(name)
        payload = dict(item)
        if qc is not None:
            payload["quality"] = qc.quality
            payload["quality_reasons"] = list(qc.quality_reasons)
        enriched.append(payload)
    return enriched
