import 'package:flutter/services.dart';

/// Messages utilisateur français — flux caméra / négatoscope (Option B).
abstract final class CameraUserMessages {
  static const String permissionDenied =
      'Autorisation de la caméra refusée.';

  static const String cameraUnavailable =
      'Impossible d\'accéder à la caméra.';

  static const String loadFailed =
      'Impossible de charger la photo.';

  static const String captureFailed =
      'Échec de la capture. Réessayez.';

  static const String emptyCapture =
      'La photo capturée est vide.';

  /// Notice prototype — validation négatoscope non effectuée.
  static const String prototypeDisclaimer =
      'Les photos de radiographies prises avec un téléphone peuvent être '
      'influencées par l\'éclairage, les reflets et la perspective. Cette '
      'fonctionnalité est destinée au prototype et nécessite une validation '
      'spécifique avant toute utilisation clinique.';

  static const String prototypeDisclaimerShort =
      'Prototype : les photos téléphone ne sont pas encore validées '
      'cliniquement (éclairage, reflets, perspective).';
}

/// Mappe les erreurs plateforme caméra vers un message FR contrôlé.
String mapCameraPlatformException(PlatformException e) {
  final code = e.code.toLowerCase();
  final message = (e.message ?? '').toLowerCase();

  if (code.contains('photo_access_denied') ||
      code.contains('camera_access_denied') ||
      code.contains('access_denied') ||
      message.contains('permission') ||
      message.contains('denied') ||
      message.contains('autorisation')) {
    return CameraUserMessages.permissionDenied;
  }

  if (code.contains('camera_access_restricted') ||
      code.contains('unavailable') ||
      message.contains('no available camera') ||
      message.contains('camera not available')) {
    return CameraUserMessages.cameraUnavailable;
  }

  return CameraUserMessages.captureFailed;
}
