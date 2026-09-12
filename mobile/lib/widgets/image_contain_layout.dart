import 'dart:ui' show Size, Offset;

/// Géométrie d'affichage d'une image dans une boîte (équivalent `BoxFit.contain`).
///
/// Permet de convertir des pixels image → coordonnées widget sans déformer
/// l'image (letterbox / pillarbox).
class ImageContainLayout {
  const ImageContainLayout({
    required this.scale,
    required this.offset,
    required this.displayedSize,
    required this.boxSize,
    required this.imageSize,
  });

  /// Facteur uniforme image → widget.
  final double scale;

  /// Décalage du coin haut-gauche de l'image affichée dans la boîte.
  final Offset offset;

  /// Taille de la zone image réellement peinte.
  final Size displayedSize;

  final Size boxSize;
  final Size imageSize;

  /// Calcule le layout `contain` pour [boxSize] et [imageSize].
  ///
  /// Si une dimension image est nulle ou non finie, retourne un layout neutre
  /// (scale=1, offset=0) pour éviter tout crash.
  factory ImageContainLayout.compute({
    required Size boxSize,
    required Size imageSize,
  }) {
    final iw = imageSize.width;
    final ih = imageSize.height;
    final bw = boxSize.width;
    final bh = boxSize.height;

    if (!_positiveFinite(iw) ||
        !_positiveFinite(ih) ||
        !_positiveFinite(bw) ||
        !_positiveFinite(bh)) {
      return ImageContainLayout(
        scale: 1,
        offset: Offset.zero,
        displayedSize: Size.zero,
        boxSize: boxSize,
        imageSize: imageSize,
      );
    }

    final scale = (bw / iw < bh / ih) ? bw / iw : bh / ih;
    final dw = iw * scale;
    final dh = ih * scale;
    final ox = (bw - dw) / 2;
    final oy = (bh - dh) / 2;

    return ImageContainLayout(
      scale: scale,
      offset: Offset(ox, oy),
      displayedSize: Size(dw, dh),
      boxSize: boxSize,
      imageSize: imageSize,
    );
  }

  /// Convertit un point en pixels image vers la boîte widget.
  Offset toDisplay(double imageX, double imageY) {
    return Offset(
      offset.dx + imageX * scale,
      offset.dy + imageY * scale,
    );
  }

  /// Convertit un point de la boîte widget vers les pixels image originales.
  ///
  /// Inverse exacte de [toDisplay] lorsque [scale] est fini et non nul.
  /// Les coordonnées résultantes sont en `original_image_pixels` (origine
  /// haut-gauche), indépendantes du letterbox / pillarbox de l'affichage.
  ///
  /// Avec un zoom parent (`InteractiveViewer`), transformer d'abord le point
  /// pointeur vers l'espace local du canvas contain, puis appeler [toImage].
  Offset toImage(double displayX, double displayY) {
    if (!_positiveFinite(scale)) {
      return Offset.zero;
    }
    return Offset(
      (displayX - offset.dx) / scale,
      (displayY - offset.dy) / scale,
    );
  }

  static bool _positiveFinite(double v) => v.isFinite && v > 0;
}
