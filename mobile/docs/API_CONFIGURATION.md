# API configuration — Coxométrie mobile

Single configuration mechanism: **`--dart-define=API_BASE_URL=...`** at build/run time.

No IP addresses are hardcoded in source code.

## Priority

1. `--dart-define=API_BASE_URL=<url>` (if set)
2. Platform default (see below)

Default port: **8001**

## Platform defaults (no dart-define)

| Platform | Default URL | Notes |
|----------|-------------|--------|
| Android emulator | `http://10.0.2.2:8001` | Maps to host `127.0.0.1` |
| iOS Simulator | `http://127.0.0.1:8001` | Backend on same Mac |
| Windows / Linux desktop | `http://127.0.0.1:8001` | |
| Web | `http://127.0.0.1:8001` | |

## Physical devices (Android / iPhone)

The host loopback defaults **do not work** on real hardware. Use the PC's LAN IPv4.

**No physical device available?** Use the validated demo path in [README.md](../README.md): Windows / Android emulator + digital DICOM→PNG import. Do not treat emulator camera as physical validation.

```powershell
# Find PC IP (Windows)
ipconfig

# Demo / V5 (recommended) — forces MODEL_VERSION=v5_phase2
.\backend\run_demo.ps1

# Manual V5 only if run_demo.ps1 cannot be used:
# $env:MODEL_VERSION = "v5_phase2"
# .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001

# Compatibility V2 only (not for V5 demo):
# $env:MODEL_VERSION = "v2"
# .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

Confirm before demo: `GET http://127.0.0.1:8001/health` → `model_version` is `v5_phase2`.

### Android physical device

```powershell
cd mobile
flutter devices
flutter run -d <device-id> --dart-define=API_BASE_URL=http://<PC-IP>:8001
```

Debug APK:

```powershell
flutter build apk --debug --dart-define=API_BASE_URL=http://<PC-IP>:8001
```

### iOS physical iPhone (macOS only)

```bash
flutter run -d <device-id> --dart-define=API_BASE_URL=http://<PC-IP>:8001
```

See [IOS_SETUP.md](IOS_SETUP.md) for generating the iOS project.

## Health check

In-app: **Connexion serveur** → **Tester GET /health** (does not upload images).

On success the UI shows the active model from `/health`, e.g. **Modèle : V5 Phase 2** or **Modèle : V2** (not hardcoded).

## HTTP / security notice

Development and LAN demos use **unencrypted HTTP**. Radiographs are transmitted over the local network. This is **not** suitable for production medical data over public networks. Use HTTPS and proper infrastructure for any non-LAN deployment.

## Android cleartext

`android:usesCleartextTraffic` and `network_security_config.xml` allow HTTP for local backend access during development. Scope is documented in `android/app/src/main/res/xml/network_security_config.xml`.
