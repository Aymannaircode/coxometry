"""Point d'entrée FastAPI du backend coxométrie.

Démo V5 (recommandé) — depuis la racine du dépôt :

    .\\backend\\run_demo.ps1

Compatibilité V2 (défaut code si MODEL_VERSION absent) :

    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
"""

from __future__ import annotations

from fastapi import FastAPI

from .app.api.routes.analyze import router as analyze_router
from .app.api.routes.measurements import router as measurements_router
from .app.services.detection.model_factory import get_model_version

app = FastAPI(
    title="Coxométrie — Backend",
    description=(
        "API d'analyse coxométrique pour radiographies du bassin (AP).\n\n"
        "**POST /analyze** — upload d'image (PNG/JPG) : prétraitement → "
        "détection assistée par IA des repères anatomiques → reprojection → "
        "mesures géométriques VCE / Tönnis / CCD.\n\n"
        "**Versions de modèle** (variable d'environnement `MODEL_VERSION`) :\n"
        "- `v2` — 14 landmarks (référence de compatibilité ; défaut si non défini)\n"
        "- `v5_phase2` — 16 landmarks (14 + IT_R / IT_L) avec contrôle qualité IT "
        "(`accept` / `review` / `unavailable`)\n\n"
        "**Démo** : lancer via `backend/run_demo.ps1` pour forcer `v5_phase2`.\n\n"
        "**POST /measurements** — calcul géométrique à partir de landmarks "
        "fournis manuellement (outil lab / compatibilité).\n\n"
        "Aucune coordonnée inventée. Aucune interprétation diagnostique."
    ),
    version="0.2.0",
)

app.include_router(measurements_router)
app.include_router(analyze_router)


@app.get("/health", tags=["system"])
def health() -> dict:
    """Santé du service — inclut le modèle actif (`MODEL_VERSION`)."""
    return {
        "status": "ok",
        "service": "coxometrie-backend",
        "version": "0.2.0",
        "model_version": get_model_version(),
    }