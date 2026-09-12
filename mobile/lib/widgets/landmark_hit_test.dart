import 'package:flutter/painting.dart';

import '../models/landmark.dart';
import '../models/landmark_correction_state.dart';
import 'image_contain_layout.dart';

/// Rayon de sélection (espace display / widget contain), adapté doigt + souris.
const double kLandmarkHitRadiusDisplay = 28.0;

/// Retourne le landmark corrigible le plus proche de [localDisplay], ou `null`.
///
/// [localDisplay] est dans l'espace du canvas contain (enfant de
/// [InteractiveViewer]) — le zoom parent est déjà appliqué via les
/// coordonnées locales du geste.
String? findCorrectableLandmarkAt({
  required Offset localDisplay,
  required List<Landmark> landmarks,
  required ImageContainLayout layout,
  double hitRadiusDisplay = kLandmarkHitRadiusDisplay,
}) {
  String? bestName;
  var bestDistSq = hitRadiusDisplay * hitRadiusDisplay;

  for (final landmark in landmarks) {
    if (!LandmarkCorrectionState.correctableNames.contains(landmark.name)) {
      continue;
    }
    if (!landmark.isDrawable) continue;
    final x = landmark.x;
    final y = landmark.y;
    if (x == null || y == null) continue;

    final display = layout.toDisplay(x, y);
    final dx = display.dx - localDisplay.dx;
    final dy = display.dy - localDisplay.dy;
    final distSq = dx * dx + dy * dy;
    if (distSq <= bestDistSq) {
      bestDistSq = distSq;
      bestName = landmark.name;
    }
  }
  return bestName;
}

/// Convertit un point local du canvas contain → pixels image originales.
Offset localDisplayToImage(
  ImageContainLayout layout,
  Offset localDisplay,
) {
  return layout.toImage(localDisplay.dx, localDisplay.dy);
}
