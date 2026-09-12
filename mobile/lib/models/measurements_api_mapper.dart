import 'analysis_result.dart';
import 'landmark.dart';
import 'measurement.dart';

/// Noms MVP acceptés par `POST /measurements` (`LandmarkIn`).
const Set<String> kMvpMeasurementLandmarkNames = {
  'TD_R',
  'TD_L',
  'FHC_R',
  'FHC_L',
  'ASL_R',
  'ASL_L',
  'ASM_R',
  'ASM_L',
  'FNM_R',
  'FNM_L',
  'FSP_R',
  'FSP_L',
  'FSD_R',
  'FSD_L',
};

/// Adaptateurs `/measurements` ↔ modèles Flutter existants (Phase 10H).
abstract final class MeasurementsApiMapper {
  /// Corps JSON `mode=landmarks` — coordonnées en `original_image_pixels`.
  static Map<String, dynamic> requestBody(List<Landmark> landmarks) {
    final payload = <Map<String, dynamic>>[];
    for (final landmark in landmarks) {
      if (!kMvpMeasurementLandmarkNames.contains(landmark.name)) continue;
      if (!landmark.hasValidCoordinates) continue;
      payload.add({
        'name': landmark.name,
        'x': landmark.x,
        'y': landmark.y,
        'v': landmark.visibility ?? 2,
      });
    }
    return {
      'mode': 'landmarks',
      'landmarks': payload,
    };
  }

  /// Mappe `sides.R` / `sides.L` → [AnalysisMeasurements].
  static AnalysisMeasurements fromResponseJson(Map<String, dynamic> json) {
    final status = json['status'];
    if (status != 'ok') {
      throw FormatException(
        'Réponse /measurements inattendue : status=$status',
      );
    }
    final sidesRaw = json['sides'];
    if (sidesRaw is! Map) {
      throw const FormatException(
        'Réponse /measurements invalide : sides absent.',
      );
    }
    final sides = Map<String, dynamic>.from(sidesRaw);
    final right = sides['R'] ?? sides['right'];
    final left = sides['L'] ?? sides['left'];
    if (right is! Map || left is! Map) {
      throw const FormatException(
        'Réponse /measurements invalide : côtés R/L absents.',
      );
    }
    return AnalysisMeasurements(
      right: SideMeasurements.fromJson(Map<String, dynamic>.from(right)),
      left: SideMeasurements.fromJson(Map<String, dynamic>.from(left)),
    );
  }
}
