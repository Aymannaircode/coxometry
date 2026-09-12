# iOS platform setup (macOS required)

The `mobile/ios/` directory is **not present** in this repository. iOS builds require **macOS + Xcode**.

> **Do not run these steps on Windows.** Generate the iOS project on a Mac only.

## 1. Generate the iOS platform

```bash
cd mobile
flutter create . --platforms=ios
```

This adds `ios/Runner`, `Podfile`, and Xcode project files without overwriting existing `lib/` code.

## 2. Info.plist permissions

Add usage descriptions in `ios/Runner/Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Capture radiographs for coxometry analysis.</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Select radiographs from the photo library.</string>
```

## 3. App Transport Security (HTTP / LAN backend)

For development against `http://<PC-IP>:8001`, add a LAN exception (development only):

```xml
<key>NSAppTransportSecurity</key>
<dict>
  <key>NSAllowsLocalNetworking</key>
  <true/>
</dict>
```

For production, use HTTPS instead of broad cleartext exceptions.

## 4. Install pods and run simulator

```bash
cd ios
pod install
cd ..
flutter run -d ios
```

Default API URL (simulator): `http://127.0.0.1:8001` (see `lib/config/api_config.dart`).

## 5. Physical iPhone

1. PC and iPhone on the same Wi‑Fi.
2. Backend (recommended demo launcher): `.\backend\run_demo.ps1`  
   Manual V5: `$env:MODEL_VERSION="v5_phase2"` then  
   `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001`  
   (Bare uvicorn without `MODEL_VERSION` starts **V2** — not for a V5 demo.)
3. Run:

```bash
flutter run -d <device-id> --dart-define=API_BASE_URL=http://<PC-IP>:8001
```

4. Configure signing in Xcode (Team, Bundle ID, provisioning profile).

## 5. Verify build

```bash
flutter build ios --debug --no-codesign
```

Full device/release builds require valid Apple Developer signing.

## Status

| Check | Windows | macOS + Xcode |
|-------|---------|---------------|
| Generate `ios/` | Not possible | Required first step |
| Simulator build | Not possible | After setup |
| Physical iPhone | Not possible | After signing + dart-define |
