# V5 Phase 2 Backend Integration Audit

**Généré :** 2026-09-02  
**Mode :** Intégration Phase 1 — aucun training, aucun checkpoint modifié  
**Verdict :** `BACKEND_V5_PHASE2_INTEGRATION_READY`

---

## Phase 1 Implementation

Intégration conservative de V5 Phase 2 dans le backend FastAPI existant :
- V2 reste le **défaut** (`MODEL_VERSION` absent ou `v2`)
- V5 activable via `MODEL_VERSION=v5_phase2`
- 14 KP via sous-détecteur YOLO V2 (régression nulle @640)
- IT_R / IT_L via `forward_head_preds` V5 à l'anchor aligné bbox YOLO

---

## Files modified

| Fichier | Changement |
|---------|------------|
| `backend/app/services/detection/base.py` | Champ `it_landmarks` sur `LandmarkDetectionResult` |
| `backend/app/services/detection/__init__.py` | Exports V5 + factory |
| `backend/app/services/measurement_service.py` | `it_landmarks` reprojetés, `model_version` audit |
| `backend/app/services/analyze.py` | Preprocessing V5, `model_version` réponse |
| `backend/app/api/routes/analyze.py` | Factory `get_landmark_detector_dep` |
| `backend/app/schemas/analyze.py` | `model_version`, `AnalyzeITLandmarkOut`, `it_landmarks` |
| `backend/tests/test_analyze_api.py` | Renommage dependency inject |

## Files created

| Fichier | Rôle |
|---------|------|
| `backend/app/services/preprocessing_v5.py` | Preprocessing 640×640 RGB |
| `backend/app/services/detection/v5_phase2_pose.py` | Wrapper V5 Phase 2 |
| `backend/app/services/detection/model_factory.py` | Factory v2 / v5_phase2 |
| `backend/tests/test_v5_phase2_detector.py` | Tests 16 KP + decoder |
| `backend/tests/test_v5_v2_regression.py` | Non-régression @640 |
| `backend/tests/test_analyze_api_v5.py` | Test HTTP V2 + V5 |

## Files untouched

- `backend/app/services/preprocessing.py` (V2 512×512 inchangé)
- `mvp_geometry/measurements.py`, `mvp_geometry/hip_measures.py`
- `mobile/**`, labels, dataset YAML, checkpoints
- Scripts d'entraînement V5 (`train_yolo_pose_v5_phase2.py`, etc.)

---

## V5 preprocessing 640

```python
DEFAULT_V5_PREPROCESS = PreprocessConfig(
    target_size=(640, 640),
    color_mode="rgb",
    normalize=True,
)
```

Aligné sur l'audit checkpoint (`imgsz=640`, letterbox, RGB).  
V2 conserve `target_size=(512, 512)` grayscale via `DEFAULT_ANALYZE_PREPROCESS`.

---

## V5 wrapper

Chargement validé :
```python
model = build_model(cfg)  # via import dynamique train_yolo_pose_v5_phase2.py
model.load_state_dict(ckpt["v5_phase2"]["wrapper_state"])
attach_hyp(model.base)
preds, _, _ = model.forward_head_preds(img_tensor)
```

Pipeline hybride production :
1. YOLO V2 sur image 640 → 14 KP + bbox (identique audit détection)
2. V5 `forward_head_preds` → IT à l'anchor max IoU avec bbox YOLO (sans GT)

---

## Decoder

```
raw logits → kpts_decode → grid → grid × stride → px640 → reprojection → original
```

- `verify_single_stride()` + test `test_v5_decoder_single_stride`
- `decoder_single_stride_ok` dans audit V5

---

## Reprojection

Réutilise `reprojection.py` existant. IT avec `v=2` reprojetés ; `v=0` → `x/y=null`.

---

## 16 KP mapping

| Index | Nom | Source backend |
|------:|-----|----------------|
| 0–13 | MVP landmarks | YOLO V2 (sous-détecteur) |
| 14 | IT_R | V5 `forward_head_preds` |
| 15 | IT_L | V5 `forward_head_preds` |

---

## V2/V5 comparison (@640)

Sur preprocessing 640 identique (5 images val) :
- **bbox/conf** : identiques (V5 délègue 14 KP à V2)
- **KP 0–13** : identiques (tolérance 2 px original)
- **VCE/Tönnis/CCD** : identiques (tolérance 0.01°)
- **IT** : présents uniquement en V5

Note : V2 défaut (512) vs V5 (640) produisent des coords originales différentes — comportement attendu.

---

## B26_26 v=0

- **GT** : IT_R v=0, IT_L v=2
- **Production** : modèle prédit IT_R avec confiance > seuil (v=2) — limitation modèle, pas backend
- **Backend** : si conf < 0.25 → v=0, pas de coordonnées (test unitaire `test_v0_parsing_no_invented_coords`)
- **IT_L** : v=2, coordonnées valides

---

## API test

```
POST /analyze + MODEL_VERSION=v2  → model_version=v2, it_landmarks=[]
POST /analyze + MODEL_VERSION=v5_phase2 → model_version=v5_phase2, it_landmarks=[IT_R, IT_L]
```

JSON sérialisable confirmé (`test_analyze_api_v5`).

---

## Existing tests

```
python -m unittest discover -s backend/tests -v
→ 153 tests OK (1 skipped)
```

Tous les tests V2 existants restent verts.

---

## Performance (B26_10, CPU)

| Métrique | V2 | V5 |
|----------|---:|---:|
| Chargement modèle | 531 ms | 168 ms |
| Pipeline measurement | 760 ms | 405 ms |
| POST /analyze total | 359 ms | 780 ms |

V5 plus lent sur `/analyze` car charge V2 + V5 ; optimisable ultérieurement.

---

## Known limitations

1. `best_it.pt` ne se charge pas via `YOLO(path)` seul — wrapper Python requis
2. V5 nécessite preprocessing 640 (pas 512)
3. B26_26 IT_R : GT v=0 mais modèle prédit v=2 (confiance élevée) — pas de GT en production
4. `MODEL_VERSION` via variable d'environnement (pas encore header HTTP)
5. Flutter non modifié — affichage IT à faire en Phase 2

---

## Verdict

### `BACKEND_V5_PHASE2_INTEGRATION_READY`
