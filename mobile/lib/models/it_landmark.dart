/// Qualité QC d'un landmark IT (V5 Phase 2).
enum ITQuality {
  accept,
  review,
  unavailable;

  static ITQuality? fromString(String? raw) {
    switch (raw) {
      case 'accept':
        return ITQuality.accept;
      case 'review':
        return ITQuality.review;
      case 'unavailable':
        return ITQuality.unavailable;
      default:
        return null;
    }
  }

  String get label {
    switch (this) {
      case ITQuality.accept:
        return 'ACCEPT';
      case ITQuality.review:
        return 'REVIEW';
      case ITQuality.unavailable:
        return 'UNAVAILABLE';
    }
  }
}

/// Landmark IT (index 14 = IT_R, 15 = IT_L) avec QC V5.
class ITLandmark {
  const ITLandmark({
    required this.name,
    required this.kpIndex,
    required this.v,
    this.x,
    this.y,
    this.confidence,
    this.quality,
    this.qualityReasons = const [],
  });

  final String name;
  final int kpIndex;
  final int v;
  final double? x;
  final double? y;
  final double? confidence;
  final ITQuality? quality;
  final List<String> qualityReasons;

  bool get isAccept => quality == ITQuality.accept;
  bool get isReview => quality == ITQuality.review;
  bool get isUnavailable => quality == ITQuality.unavailable;

  bool get hasValidCoordinates {
    final px = x;
    final py = y;
    if (px == null || py == null) return false;
    return px.isFinite && py.isFinite;
  }

  /// Affichable sur l'overlay : coordonnées valides, v≠0, qualité ≠ unavailable.
  bool get isDrawable {
    if (v == 0) return false;
    if (isUnavailable) return false;
    return hasValidCoordinates;
  }

  String? get primaryQualityReason =>
      qualityReasons.isNotEmpty ? qualityReasons.first : null;

  factory ITLandmark.fromJson(Map<String, dynamic> json) {
    final reasonsRaw = json['quality_reasons'];
    final reasons = reasonsRaw is List
        ? reasonsRaw.map((e) => e.toString()).toList(growable: false)
        : const <String>[];

    return ITLandmark(
      name: json['name'] as String? ?? '',
      kpIndex: (json['kp_index'] as num?)?.toInt() ?? -1,
      v: (json['v'] as num?)?.toInt() ?? 0,
      x: (json['x'] as num?)?.toDouble(),
      y: (json['y'] as num?)?.toDouble(),
      confidence: (json['confidence'] as num?)?.toDouble(),
      quality: ITQuality.fromString(json['quality'] as String?),
      qualityReasons: reasons,
    );
  }
}
