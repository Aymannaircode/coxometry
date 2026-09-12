import 'dart:ui' show Size;

/// Métadonnées de l'espace de coordonnées renvoyées par le backend V5.
///
/// Les landmarks sont exprimés en `original_image_pixels` (origine haut-gauche).
class CoordinateSpace {
  const CoordinateSpace({
    required this.imageWidth,
    required this.imageHeight,
    required this.preprocessedWidth,
    required this.preprocessedHeight,
    required this.scale,
    required this.padX,
    required this.padY,
    this.landmarkCoordinateSpace = 'original_image_pixels',
  });

  final int imageWidth;
  final int imageHeight;
  final int preprocessedWidth;
  final int preprocessedHeight;
  final double scale;
  final int padX;
  final int padY;
  final String landmarkCoordinateSpace;

  Size get imageSize =>
      Size(imageWidth.toDouble(), imageHeight.toDouble());

  bool get isOriginalImagePixels =>
      landmarkCoordinateSpace == 'original_image_pixels';

  factory CoordinateSpace.fromJson(Map<String, dynamic> json) {
    return CoordinateSpace(
      imageWidth: (json['image_width'] as num).toInt(),
      imageHeight: (json['image_height'] as num).toInt(),
      preprocessedWidth: (json['preprocessed_width'] as num).toInt(),
      preprocessedHeight: (json['preprocessed_height'] as num).toInt(),
      scale: (json['scale'] as num).toDouble(),
      padX: (json['pad_x'] as num).toInt(),
      padY: (json['pad_y'] as num).toInt(),
      landmarkCoordinateSpace:
          json['landmark_coordinate_space'] as String? ??
              'original_image_pixels',
    );
  }
}
