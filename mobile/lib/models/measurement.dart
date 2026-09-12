/// Mesure coxométrique (VCE, Tönnis ou CCD) pour un côté.
///
/// Aligné sur `AnalyzeMeasureOut` du backend.
class Measurement {
  const Measurement({
    this.valueDeg,
    required this.available,
    this.reason,
    this.landmarksUsed,
  });

  final double? valueDeg;
  final bool available;
  final String? reason;
  final List<String>? landmarksUsed;

  /// Texte affiché — jamais `0°` si la mesure est indisponible.
  String get displayValue {
    if (!available || valueDeg == null) return '—';
    return '${valueDeg!.toStringAsFixed(1)}°';
  }

  factory Measurement.fromJson(Map<String, dynamic> json) {
    final landmarksRaw = json['landmarks_used'];
    List<String>? landmarksUsed;
    if (landmarksRaw is List) {
      landmarksUsed = landmarksRaw.map((e) => e.toString()).toList();
    }

    return Measurement(
      valueDeg: (json['value_deg'] as num?)?.toDouble(),
      available: json['available'] as bool? ?? false,
      reason: json['reason'] as String?,
      landmarksUsed: landmarksUsed,
    );
  }
}

/// Mesures VCE / Tönnis / CCD pour une hanche (droite ou gauche).
class SideMeasurements {
  const SideMeasurements({
    required this.vce,
    required this.tonnis,
    required this.ccd,
  });

  final Measurement vce;
  final Measurement tonnis;
  final Measurement ccd;

  factory SideMeasurements.fromJson(Map<String, dynamic> json) {
    return SideMeasurements(
      vce: Measurement.fromJson(json['vce'] as Map<String, dynamic>),
      tonnis: Measurement.fromJson(json['tonnis'] as Map<String, dynamic>),
      ccd: Measurement.fromJson(json['ccd'] as Map<String, dynamic>),
    );
  }
}
