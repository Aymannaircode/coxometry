# TEST MOBILE E2E — Coxométrie MVP

Test manuel sur **téléphone Android réel** connecté au backend FastAPI sur le PC.

## Prérequis

| Élément | Valeur |
|---------|--------|
| **Device** | Android réel (USB ou Wi‑Fi debug) |
| **Backend** | `http://<PC-IP>:8001` |
| **Test image** | Une radiographie pelvienne de test connue (PNG/JPG) |

### 1. Démarrer le backend (PC) — démo V5

```powershell
cd C:\Users\g\OneDrive\Desktop\Projet-Ayman
.\backend\run_demo.ps1
```

> **`run_demo.ps1` est obligatoire pour une démo V5** : il force `MODEL_VERSION=v5_phase2`
> et `--host 0.0.0.0` (accès téléphone / émulateur).  
> Un `uvicorn` nu démarre en **V2** (pas d’IT).

Manuel V5 (développement uniquement) :

```powershell
$env:MODEL_VERSION = "v5_phase2"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

### 2. Trouver l'IP du PC

```powershell
ipconfig
```

Noter l'**Adresse IPv4** du Wi‑Fi (ex. `192.168.1.42`).

### 3. Vérifier depuis le PC

```powershell
curl http://127.0.0.1:8001/health
```

Réponse attendue : `"status":"ok"` et **`"model_version":"v5_phase2"`**.

### 4. Pare-feu Windows

Autoriser le port **8001** entrant (réseau privé) si la connexion échoue.

### 5. Lancer l'app Flutter sur le téléphone

```powershell
cd mobile
flutter devices
flutter run --dart-define=API_BASE_URL=http://192.168.1.42:8001
```

Remplacer `192.168.1.42` par l'IP réelle du PC.

---

## Procédure de test

### Phase A — Connexion serveur (sans analyse)

1. Ouvrir l'app → icône **Connexion serveur** (ou bouton sur l'accueil).
2. Vérifier que l'URL affichée = `http://<PC-IP>:8001`.
3. Appuyer sur **Tester GET /health**.
4. Résultat attendu : « Serveur accessible », **« Modèle : V5 Phase 2 »**, latence < 2000 ms, `status: ok`.

| Critère | PASS | FAIL | Notes |
|---------|------|------|-------|
| Configuration `API_BASE_URL` | ☐ | ☐ | Source = `dart-define` |
| GET /health | ☐ | ☐ | |
| `model_version` affiché (V5 Phase 2) | ☐ | ☐ | Depuis la réponse /health |
| Message si backend arrêté | ☐ | ☐ | Arrêter le backend, retester |

### Phase B — Analyse complète

1. **Importer une radiographie** (galerie) ou prendre une photo.
2. Vérifier l'**aperçu** : image visible, dimensions affichées.
3. Appuyer sur **Analyser** — une seule requête (pas de double spinner).
4. Attendre la fin (timeout max ~120 s).
5. Consulter l'écran **Résultats**.

| Critère | PASS | FAIL | Notes |
|---------|------|------|-------|
| Image sélectionnée | ☐ | ☐ | |
| Upload multipart (`file`) | ☐ | ☐ | |
| Analyse terminée | ☐ | ☐ | |
| **VCE** hanche droite | ☐ | ☐ | Valeur en ° ou « — » |
| **VCE** hanche gauche | ☐ | ☐ | |
| **Tönnis** hanche droite | ☐ | ☐ | |
| **Tönnis** hanche gauche | ☐ | ☐ | |
| **CCD** hanche droite | ☐ | ☐ | |
| **CCD** hanche gauche | ☐ | ☐ | |
| Landmarks (14 attendus) | ☐ | ☐ | Section Détection |
| **ASL_L refinement** | ☐ | ☐ | Activé / Désactivé affiché |
| Overlay landmarks | ☐ | ☐ | Points alignés sur l'image |
| Mesure indisponible ≠ 0° | ☐ | ☐ | Affiche « — » |

### Phase C — Cas limites

| Critère | PASS | FAIL | Notes |
|---------|------|------|-------|
| Image haute résolution (> 2 Mo) | ☐ | ☐ | Galerie, pas de crash |
| Orientation EXIF (photo caméra) | ☐ | ☐ | Overlay aligné |
| Timeout (backend lent) | ☐ | ☐ | Message explicite après 120 s |
| Erreur réseau | ☐ | ☐ | Mode avion ou mauvaise IP |
| Pas de double requête | ☐ | ☐ | Un seul POST /analyze par analyse |

---

## Grille de synthèse

```
TEST MOBILE E2E

Device:     Android réel — ___________________
Backend:    http://_______________:8001
Test image: ___________________
Date:       ___________________

Résultats:
  image sélectionnée     : PASS / FAIL
  upload                 : PASS / FAIL
  analyse                : PASS / FAIL
  VCE R/L                : PASS / FAIL
  Tönnis R/L             : PASS / FAIL
  CCD R/L                : PASS / FAIL
  landmarks              : PASS / FAIL
  ASL_L refinement       : PASS / FAIL
  overlay                : PASS / FAIL
  erreur réseau          : PASS / FAIL
```

---

## Dépannage

| Symptôme | Cause probable | Action |
|----------|----------------|--------|
| Serveur inaccessible | IP incorrecte ou pare-feu | Vérifier IP, pare-feu, même Wi‑Fi |
| URL = 10.0.2.2 | dart-define absent | Relancer avec `--dart-define=API_BASE_URL=...` |
| HTTP cleartext blocked | Rare sur MVP | `usesCleartextTraffic` déjà activé |
| Timeout analyse | YOLO lent sur CPU | Attendre ou tester image plus petite |
| Overlay décalé | EXIF non corrigé | Vérifier « orientation corrigée » à l'aperçu |

---

## Commandes utiles

```powershell
# Build APK debug pour installation manuelle
flutter build apk --debug --dart-define=API_BASE_URL=http://192.168.1.42:8001

# Tests automatisés Flutter (PC)
flutter test
```
