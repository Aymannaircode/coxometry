import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';

/// Configuration de l'URL du backend FastAPI.
///
/// Priorité :
/// 1. `--dart-define=API_BASE_URL=http://192.168.x.x:8001`
/// 2. Plateforme par défaut (émulateur / simulateur / desktop)
abstract final class ApiConfig {
  static const String _envBaseUrl = String.fromEnvironment('API_BASE_URL');

  static const int defaultPort = 8001;

  /// `true` si l'URL provient de `--dart-define=API_BASE_URL=...`.
  static bool get isFromDartDefine => _envBaseUrl.isNotEmpty;

  /// URL de base sans slash final.
  static String get baseUrl {
    if (_envBaseUrl.isNotEmpty) {
      return _stripTrailingSlash(_envBaseUrl);
    }
    return _stripTrailingSlash(_defaultForPlatform());
  }

  static Uri get analyzeUri => Uri.parse('$baseUrl/analyze');

  static Uri get healthUri => Uri.parse('$baseUrl/health');

  /// Défaut émulateur Android (loopback hôte).
  static String get androidEmulatorUrl => 'http://10.0.2.2:$defaultPort';

  /// Défaut simulateur iOS / desktop / web.
  static String get localhostUrl => 'http://127.0.0.1:$defaultPort';

  /// Commande `flutter run` documentée pour appareil physique (remplacer `<PC-IP>`).
  static String physicalDeviceRunCommand({String deviceId = ''}) {
    final devicePart = deviceId.isNotEmpty ? ' -d $deviceId' : '';
    return 'flutter run$devicePart '
        '--dart-define=API_BASE_URL=http://<PC-IP>:$defaultPort';
  }

  /// Rappel affiché sur l'écran d'accueil quand aucune URL n'est fournie.
  static String get physicalDeviceHint {
    if (kIsWeb) return '';
    if (Platform.isAndroid) {
      return 'Émulateur Android : défaut $androidEmulatorUrl.\n'
          'Téléphone réel : $physicalDeviceRunCommand()';
    }
    if (Platform.isIOS) {
      return 'Simulateur iOS : défaut $localhostUrl.\n'
          'iPhone réel : $physicalDeviceRunCommand()';
    }
    return 'Backend local : $localhostUrl';
  }

  /// Libellé pour l'écran debug / accueil.
  static String get sourceLabel {
    if (isFromDartDefine) return 'dart-define (API_BASE_URL)';
    if (kIsWeb) return 'défaut web';
    if (Platform.isAndroid) return 'défaut Android (émulateur 10.0.2.2)';
    if (Platform.isIOS) return 'défaut iOS (127.0.0.1)';
    return 'défaut desktop';
  }

  static String _defaultForPlatform() {
    if (kIsWeb) {
      return localhostUrl;
    }

    if (Platform.isAndroid) {
      return androidEmulatorUrl;
    }

    if (Platform.isIOS) {
      return localhostUrl;
    }

    return localhostUrl;
  }

  static String _stripTrailingSlash(String url) {
    if (url.endsWith('/')) {
      return url.substring(0, url.length - 1);
    }
    return url;
  }
}
