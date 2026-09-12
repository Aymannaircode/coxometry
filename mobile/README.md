# Prototype Flutter — Coxométrie MVP

Application mobile : import radiographie → `POST /analyze` → mesures VCE, Tönnis, CCD et overlay landmarks (V2 / V5).

## Chemin de démo recommandé (sans téléphone Android)

**VALIDATED DEMO PATH** — à utiliser pour jury / présentation :

1. Backend V5 : `.\backend\run_demo.ps1` (depuis la racine du dépôt)
2. Vérifier : `GET http://127.0.0.1:8001/health` → `"model_version":"v5_phase2"`
3. App : Windows desktop **ou** émulateur Android
4. Accueil → **Importer une image** → PNG DICOM→PNG du dataset validé  
   (ex. `datasets/yolo_pose_new_26/images/train/B26_01.png`)
5. Analyser → Résultats (16 landmarks, IT, mesures) → **Exporter le rapport**

| Validé pour la démo | Non validé physiquement / cliniquement |
|---------------------|----------------------------------------|
| Import image numérique (DICOM→PNG) | Caméra téléphone réelle |
| Pipeline V5 + VCE / Tönnis / CCD + PDF | Photos de négatoscope |
| UI/workflow caméra (écrans) | Exactitude photo négatoscope |

L’émulateur **ne valide pas** le matériel caméra d’un téléphone réel.

## Prérequis

- Flutter SDK (stable)
- Backend FastAPI en **mode démo V5** (16 landmarks + IT) :

```powershell
cd C:\Users\g\OneDrive\Desktop\Projet-Ayman
.\backend\run_demo.ps1
```

> **`run_demo.ps1` est la méthode de lancement démo recommandée.**  
> Il force `MODEL_VERSION=v5_phase2` et `--host 0.0.0.0`.

Vérifier avant la démo :

- `GET http://127.0.0.1:8001/health` → `"model_version":"v5_phase2"`
- Dans l’app : **Connexion serveur** → **Tester GET /health** → **Modèle : V5 Phase 2**

> Ne pas lancer un `uvicorn` nu pour une démo V5 : sans `MODEL_VERSION=v5_phase2`
> le backend reste en **V2** (14 landmarks, pas d'IT).

Manuel V5 (développement, si le script n’est pas utilisé) :

```powershell
$env:MODEL_VERSION = "v5_phase2"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

## Lancer (desktop — démo sans téléphone)

```powershell
cd mobile
flutter pub get
flutter run -d windows
```

Émulateur Android (après `run_demo.ps1` sur le PC) :

```powershell
cd mobile
flutter run -d <emulator-id>
```

URL API défaut émulateur : `http://10.0.2.2:8001`.

## Configuration API

Voir **[docs/API_CONFIGURATION.md](docs/API_CONFIGURATION.md)** pour le détail par plateforme.

| Plateforme | URL par défaut | Appareil physique |
|------------|----------------|-------------------|
| Android émulateur | `http://10.0.2.2:8001` | `--dart-define=API_BASE_URL=http://<IP-PC>:8001` |
| iOS simulateur | `http://127.0.0.1:8001` | idem (macOS + projet iOS) |
| Windows | `http://127.0.0.1:8001` | — |

Exemple téléphone Android réel (quand un appareil est disponible) :

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.1.42:8001
```

## Tests

```powershell
cd mobile
flutter test
```

## Capture caméra (prototype)

**IMPLEMENTED BUT NOT PHYSICALLY VALIDATED**

Accueil → **Prendre une photo** → guidage → caméra système → confirmer / reprendre → même analyse que l’import image.

Détails, limites et tests appareil : **[docs/CAMERA_CAPTURE.md](docs/CAMERA_CAPTURE.md)**  
Les photos de négatoscope **ne sont pas** cliniquement validées (dataset actuel = DICOM→PNG).  
Sans téléphone réel, ne pas présenter le flux caméra comme validé matériellement.

## Rapport PDF

Sur l'écran **Résultats** : **Exporter le rapport**.  
Détails : **[docs/PDF_REPORT.md](docs/PDF_REPORT.md)**

## Test E2E appareil réel

Procédure complète (quand un téléphone est disponible) : **[docs/TEST_MOBILE_E2E.md](docs/TEST_MOBILE_E2E.md)**

## iOS

Le dossier `ios/` n'est pas versionné. Génération sur Mac : **[docs/IOS_SETUP.md](docs/IOS_SETUP.md)**

## Release Android

Configuration optionnelle du keystore : **[android/RELEASE_SIGNING.md](android/RELEASE_SIGNING.md)**

Sans `android/key.properties`, les builds release utilisent les clés debug (démo uniquement).

## Sécurité (développement)

Le MVP utilise **HTTP en clair** sur le réseau local (LAN). Ne pas utiliser tel quel pour des données médicales en production.
