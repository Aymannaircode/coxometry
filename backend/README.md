# Backend Coxométrie — Pipeline analyse radiographique

API FastAPI pour l'application Flutter : upload d'une radiographie du bassin,
détection assistée par IA des repères anatomiques, puis calcul des angles
**VCE**, **Tönnis** et **CCD** via `mvp_geometry`.

Aucune interprétation diagnostique. Aucune certification dispositif médical.
Aucune coordonnée anatomique inventée.

## Pipeline (`POST /analyze`)

```
Image (PNG / JPG / JPEG)
        ↓
Validation upload (≤ 25 Mo)
        ↓
Prétraitement
  • V2  : 512×512 grayscale letterbox
  • V5  : 640×640 RGB letterbox
        ↓
Détection landmarks (MODEL_VERSION)
  • v2         → 14 landmarks MVP
  • v5_phase2  → 14 landmarks + IT_R (14) + IT_L (15)
        ↓
Reprojection → pixels image originale (coordinate_space)
        ↓
QC IT (V5 uniquement) : accept / review / unavailable
        ↓
mvp_geometry → VCE / Tönnis / CCD (R et L)
        ↓
Réponse JSON (Flutter)
```

## État actuel

| Étape | Statut |
|-------|--------|
| `POST /analyze` (upload image) | **Opérationnel** |
| Prétraitement V2 / V5 | **Opérationnel** |
| Détection YOLO Pose V2 (14 KP) | **Opérationnel** |
| Détection V5 Phase 2 (16 KP + IT) | **Opérationnel** |
| Contrôle qualité IT (`v5_it_qc`) | **Opérationnel** |
| Reprojection + `coordinate_space` | **Opérationnel** |
| Mesures VCE / Tönnis / CCD | **Opérationnel** |
| `POST /measurements` (landmarks manuels) | **Opérationnel** (lab / compatibilité) |
| Flutter mobile | Consomme `POST /analyze` |

## Sélection de modèle (`MODEL_VERSION`)

| Valeur | Comportement |
|--------|----------------|
| *(absent)* ou `v2` | **V2** — 14 landmarks (défaut code / compatibilité) |
| `v5`, `v5_phase2`, `phase2` | **V5 Phase 2** — 16 landmarks + QC IT |

`GET /health` renvoie `model_version` actif : vérifier **`v5_phase2`** avant une démo V5.

### Démo (recommandé) — force V5

```powershell
# Depuis la racine du dépôt — méthode officielle pour jury / démo
.\backend\run_demo.ps1
# équivalent : port 8001, MODEL_VERSION=v5_phase2, --host 0.0.0.0
```

Vérification :

```powershell
curl.exe http://127.0.0.1:8001/health
# → "model_version": "v5_phase2"
```

Dans l’app Flutter : **Connexion serveur** → **Tester GET /health** → **Modèle : V5 Phase 2**.

### Manuel V5 (développement)

Si `run_demo.ps1` ne peut pas être utilisé, définir explicitement le modèle :

```powershell
$env:MODEL_VERSION = "v5_phase2"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

### Compatibilité V2

```powershell
# Sans MODEL_VERSION → V2
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001

# Explicite
$env:MODEL_VERSION = "v2"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

> **Attention démo :** un `uvicorn` nu (sans `run_demo.ps1` ni `MODEL_VERSION=v5_phase2`)
> démarre en **V2** — pas d'IT_R / IT_L. Ne pas l’utiliser comme commande de démo V5.

## Structure

```
backend/
├── README.md
├── run_demo.ps1            # lancement démo V5 Phase 2
├── requirements.txt
├── main.py                 # FastAPI (uvicorn backend.main:app)
├── app/
│   ├── api/routes/
│   │   ├── analyze.py      # POST /analyze
│   │   └── measurements.py # POST /measurements
│   ├── schemas/
│   │   ├── analyze.py
│   │   ├── landmarks.py
│   │   └── measurements.py
│   └── services/
│       ├── analyze.py
│       ├── measurement_service.py
│       ├── preprocessing.py / preprocessing_v5.py
│       └── detection/
│           ├── model_factory.py
│           ├── yolo_pose.py          # V2
│           ├── v5_phase2_pose.py     # V5
│           ├── v5_it_qc.py
│           └── reprojection.py
└── tests/
```

## Installation

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Lancer depuis la **racine du dépôt** pour que `mvp_geometry/` et les checkpoints
sous `runs/pose/` soient accessibles.

## Endpoints

| Méthode | Chemin | Rôle |
|---------|--------|------|
| `GET` | `/health` | Santé + `model_version` |
| `POST` | `/analyze` | Analyse image → landmarks + mesures |
| `POST` | `/measurements` | Géométrie depuis landmarks JSON (manuel) |
| — | `/docs` | OpenAPI interactif |

### `POST /analyze`

- Multipart champ `file` (ou `image`), PNG/JPG/JPEG
- Réponse OK : `model_version`, `detection` (landmarks, `it_landmarks` en V5,
  `coordinate_space`), `measurements` (VCE / Tönnis / CCD)
- En V5, chaque IT expose `quality` et `quality_reasons` (codes techniques stables)

### `POST /measurements`

Mode landmarks manuels pour tests géométriques. Mode `image` JSON reste
`not_implemented` (utiliser `/analyze` pour l'IA).

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
```

Couvre schémas, prétraitement, reprojection, géométrie, détecteurs V2/V5,
QC IT et API (cas réels + mocks). Compte typique : ~167 OK, 1 skip conditionnel.

## Limites

1. Formats : JPG/JPEG/PNG uniquement (pas de DICOM).
2. Pas d'authentification, CORS durci, ni persistance des images.
3. Pas de seuils cliniques (normal / dysplasie) dans la réponse.
4. HTTP clair recommandé uniquement en LAN de développement / démo.
5. V5 dépend des checkpoints et scripts d'architecture validés sous `runs/`
   et `annotation_pilot/` (chargement inference only).

## Ce que ce dossier ne fait pas

- Ne modifie aucun dataset / label.
- Ne lance aucun entraînement.
- Ne génère aucune coordonnée anatomique fictive.
- N'émet aucun diagnostic clinique.
