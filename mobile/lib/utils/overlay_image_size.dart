import 'dart:ui' show Size;

import '../models/coordinate_space.dart';

/// Résultat de la résolution des dimensions pour l'overlay landmarks.
class OverlayImageSizeResult {
  const OverlayImageSizeResult({
    required this.size,
    this.dimensionMismatch = false,
    this.mismatchDetail,
  });

  /// Dimensions utilisées pour le mapping pixel → widget.
  final Size size;

  /// Vrai si les dimensions locales diffèrent de [CoordinateSpace] backend.
  final bool dimensionMismatch;

  /// Détail du décalage (affichage discret à l'utilisateur).
  final String? mismatchDetail;
}

/// Résout la taille image pour [ImageContainLayout].
///
/// Priorité : `coordinate_space.image_width/height` du backend.
/// Repli : dimensions locales décodées.
///
/// Si backend et local divergent de plus de 1 px, [dimensionMismatch] est vrai
/// et un message est fourni — les coordonnées backend ne sont pas étirées
/// arbitrairement sur une autre taille locale.
Size _sizeFromCoordinateSpace(CoordinateSpace cs) => cs.imageSize;

bool _sizesMatch(Size a, Size b, {double tolerance = 1.0}) {
  return (a.width - b.width).abs() <= tolerance &&
      (a.height - b.height).abs() <= tolerance;
}

OverlayImageSizeResult resolveOverlayImageSize({
  CoordinateSpace? coordinateSpace,
  Size? localSize,
}) {
  if (coordinateSpace != null) {
    final backendSize = _sizeFromCoordinateSpace(coordinateSpace);
    if (localSize != null &&
        localSize.width > 0 &&
        localSize.height > 0 &&
        !_sizesMatch(backendSize, localSize)) {
      return OverlayImageSizeResult(
        size: backendSize,
        dimensionMismatch: true,
        mismatchDetail:
            'Dimensions image locale (${localSize.width.toInt()}×'
            '${localSize.height.toInt()}) ≠ backend '
            '(${backendSize.width.toInt()}×${backendSize.height.toInt()}). '
            'Overlay basé sur les dimensions backend.',
      );
    }
    return OverlayImageSizeResult(size: backendSize);
  }

  if (localSize != null && localSize.width > 0 && localSize.height > 0) {
    return OverlayImageSizeResult(size: localSize);
  }

  return const OverlayImageSizeResult(size: Size(1, 1));
}
