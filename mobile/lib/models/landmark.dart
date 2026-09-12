/// Landmark anatomique en coordonnées pixels de l'image originale.
///
/// Aligné sur la réponse `POST /analyze` (`detection.refined_landmarks`).
/// Origine coin haut-gauche, `y` vers le bas.
class Landmark {
  const Landmark({
    required this.name,
    this.x,
    this.y,
    this.confidence,
    this.visibility,
  });

  final String name;
  final double? x;
  final double? y;
  final double? confidence;

  /// Visibilité COCO / MVP : 0=absent, 1=occulté, 2=visible.
  final int? visibility;

  bool get hasValidCoordinates {
    final px = x;
    final py = y;
    if (px == null || py == null) return false;
    return px.isFinite && py.isFinite;
  }

  bool get isDrawable {
    if (!hasValidCoordinates) return false;
    if (visibility == 0) return false;
    return true;
  }

  factory Landmark.fromJson(Map<String, dynamic> json) {
    return Landmark(
      name: json['name'] as String? ?? '',
      x: (json['x'] as num?)?.toDouble(),
      y: (json['y'] as num?)?.toDouble(),
      confidence: (json['confidence'] as num?)?.toDouble(),
      visibility: json['v'] as int? ?? json['visibility'] as int?,
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'x': x,
        'y': y,
        if (confidence != null) 'confidence': confidence,
        if (visibility != null) 'visibility': visibility,
      };
}
