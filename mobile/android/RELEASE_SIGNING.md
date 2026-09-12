# Android release signing (demo / development)

This project ships **without production signing credentials**. By default, `flutter build apk --release` uses the **debug keystore** unless you provide your own.

## Current status

| Build | Signing | Suitable for |
|-------|---------|--------------|
| `flutter build apk --debug` | Debug | Development, USB install |
| `flutter build apk --release` (no `key.properties`) | Debug (fallback) | Internal demo only — **not Play Store** |
| `flutter build apk --release` (with `key.properties`) | Your release keystore | Distribution / Play Store |

## Optional release keystore setup

### 1. Generate a keystore (once, on your machine)

```bash
keytool -genkey -v -keystore release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias coxometrie
```

Store `release.jks` **outside** the repository (e.g. `~/keystores/coxometrie/release.jks`).

### 2. Create `android/key.properties` (never commit)

Copy the example:

```bash
cp android/key.properties.example android/key.properties
```

Edit `android/key.properties`:

```properties
storePassword=YOUR_STORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=coxometrie
storeFile=C:/path/to/release.jks
```

`storeFile` may be absolute or relative to the `android/` directory.

### 3. Build release APK

```powershell
cd mobile
flutter build apk --release --dart-define=API_BASE_URL=http://<PC-IP>:8001
```

Gradle automatically picks up `key.properties` when present (`android/app/build.gradle.kts`).

## Security

- `key.properties`, `*.jks`, and `*.keystore` are listed in `android/.gitignore`.
- **Never** commit passwords or keystore files.
- CI/CD should inject secrets via environment variables or a secure vault, not the repo.

## Limitation

Until `android/key.properties` exists on the build machine, release builds are **demo-only** and must not be presented as production-signed.
