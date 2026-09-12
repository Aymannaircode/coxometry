# Phase 7B — Camera Capture + Négatoscope MVP Implementation Report

**Date:** 2026-09-04  
**Scope:** Option B only (guidance + capture + preview/retake + existing pipeline)  
**Reference:** `datasets/yolo_pose_new_26/phase7b_camera_technical_audit.md`

---

## Final verdict

# **PHASE7B_CAMERA_MVP_IMPLEMENTED**

---

## 1. Files modified

| Path | Change |
|------|--------|
| `mobile/lib/screens/home_screen.dart` | Camera opens guidance flow; gallery label « Importer une image »; Semantics |
| `mobile/lib/services/radiograph_picker.dart` | French camera errors; PlatformException mapping; shared `_normalize` preserved |
| `mobile/README.md` | Link to camera docs + validation caveat |

## 2. Files created

| Path | Role |
|------|------|
| `mobile/lib/screens/camera_guidance_screen.dart` | Guidage FR + cadre + disclaimer + ouverture caméra |
| `mobile/lib/screens/camera_confirm_screen.dart` | Aperçu capturé · Utiliser / Reprendre |
| `mobile/lib/widgets/camera_framing_guide.dart` | Cadre visuel + overlay décoratif (sans crop) |
| `mobile/lib/utils/camera_user_messages.dart` | Messages FR + mapping erreurs plateforme |
| `mobile/test/camera_workflow_test.dart` | Tests Option B (A–H) |
| `mobile/docs/CAMERA_CAPTURE.md` | Workflow, limites, tests appareil |
| `datasets/yolo_pose_new_26/phase7b_camera_implementation_report.md` | Ce rapport |

**Not modified:** backend, `mvp_geometry`, models/checkpoints/dataset/labels/training, IT QC, VCE/Tönnis/CCD formulas, coordinate mapping.

**Dependencies:** none added (`image_picker` already present).

---

## 3. Camera workflow

```
Home « Prendre une photo »
  → CameraGuidanceScreen (cadre + consignes + notice prototype)
  → image_picker ImageSource.camera (caméra système)
  → EXIF bake (normalizeRadiographBytes) — inchangé
  → CameraConfirmScreen
       ├─ Utiliser cette photo → PreviewScreen (même chemin galerie)
       │                         → AnalysisScreen → POST /analyze → Results / PDF
       └─ Reprendre → nouvelle capture (remplace l’image, pas d’analyse)
```

Galerie : **Importer une image** → PreviewScreen (inchangé).

---

## 4. Framing guidance

- Cadre à coins sur fond sombre (écran de guidage)
- Overlay décoratif sur l’aperçu capturé (`IgnorePointer`)
- **Ne croppe pas**, ne warpe pas, ne corrige pas la perspective
- Ce n’est **pas** une limite de mesure clinique
- Pas d’overlay live sur la caméra système (hors scope Option B / pas de package `camera`)

---

## 5. Capture / retake flow

| Action | Comportement |
|--------|----------------|
| Annuler (guidage) | Retour Home |
| Annuler capture OS | Reste sur guidage |
| Reprendre | Reouvre caméra ; remplace `SelectedRadiograph` ; pas d’API |
| Annuler retake | Conserve la photo courante |
| Utiliser | `pushAndRemoveUntil` → `PreviewScreen` (pile propre jusqu’à Home) |

Pas d’analyse automatique à la capture.

---

## 6. Existing pipeline reuse

Après « Utiliser », octets = même `SelectedRadiograph` / EXIF / Preview / multipart `file` / backend preprocess / V5 (ou V2) / reprojection / IT QC / géométrie / Results / PDF que la galerie.

Aucun second pipeline d’inférence.

---

## 7. Disclaimer

Texte FR (guidage + rappel court sur confirm) :

> Les photos de radiographies prises avec un téléphone peuvent être influencées par l'éclairage, les reflets et la perspective. Cette fonctionnalité est destinée au prototype et nécessite une validation spécifique avant toute utilisation clinique.

Pas de claim de validation clinique négatoscope.

---

## 8. Error handling (FR)

| Cas | Message |
|-----|---------|
| Permission refusée | Autorisation de la caméra refusée. |
| Caméra indisponible | Impossible d'accéder à la caméra. |
| Chargement / décode | Impossible de charger la photo. |
| Échec capture | Échec de la capture. Réessayez. |
| Annulation | Silencieuse (pas d’erreur) |

Récupération : bouton **Réessayer** sur le guidage.

---

## 9. Tests

`mobile/test/camera_workflow_test.dart` :

| ID | Couverture |
|----|------------|
| A | Entrée caméra → guidage FR |
| B | Retake remplace / annulation retake |
| C | Utiliser → PreviewScreen (`analyze_button`) |
| D | Annuler guidage / annuler capture OS |
| E | Erreurs permission FR |
| F | Disclaimer prototype |
| G | Galerie → Preview (parity) |
| H | Chaînes FR (pas d’anglais technique) |

Les tests unitaires **ne valident pas** le matériel caméra.

---

## 10. Flutter result

```
flutter pub get → OK
flutter test    → 98 passed, 0 failed
```

---

## 11. Backend result

```
python -m unittest discover -s backend\tests -v
→ Ran 167 tests in ~157 s
→ OK (skipped=1)
```

Aucun changement backend.

---

## 12. Android APK result

```
flutter build apk --debug
→ √ Built build\app\outputs\flutter-apk\app-debug.apk
```

---

## 13. V5 demo verification

```
MODEL_VERSION=v5_phase2
GET http://127.0.0.1:8001/health
→ {"status":"ok",...,"model_version":"v5_phase2"}
```

Aligné avec `.\backend\run_demo.ps1`.

---

## 14. Physical-device tests NOT performed

Non exécutés dans cette phase (APK ≠ validation caméra) :

- permission caméra réelle
- ouverture / preview / capture OS
- retake / orientation / netteté / reflets
- cadrage radiographie complète sur négatoscope
- upload + analyse + résultats + PDF sur téléphone

Voir `mobile/docs/CAMERA_CAPTURE.md`.

---

## 15. Clinical validation limitations

| Validé | Pas encore validé |
|--------|-------------------|
| Dataset DICOM→PNG (`new_26`) | Photos téléphone |
| Pipeline V5 + VCE / Tönnis / CCD | Photos de négatoscope |
| Import numérique | Glare / perspective / usage clinique photo |

---

## 16. Safety confirmation

| Asset | Status |
|-------|--------|
| V2 / V5 models | **Unchanged** |
| Checkpoints | **Unchanged** |
| Dataset / labels | **Unchanged** |
| Training | **Unchanged** |
| `mvp_geometry` / VCE / Tönnis / CCD | **Unchanged** |
| IT QC rules | **Unchanged** |
| Backend inference | **Unchanged** |
| Coordinate mapping math | **Unchanged** |
| New CV / OpenCV / perspective | **Not added** |

---

## 17. Remaining limitations

1. Cadre = aide visuelle seulement (pas de correction géométrique)
2. Caméra système : pas d’overlay live in-app
3. Domaine photo non représenté dans `new_26`
4. Validation physique Android encore requise
5. Pas de claim clinique pour le flux photo

---

**PHASE7B_CAMERA_MVP_IMPLEMENTED**
