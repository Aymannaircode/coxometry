import 'coordinate_space.dart';
import 'it_landmark.dart';
import 'landmark.dart';
import 'measurement.dart';

/// Erreur structurée renvoyée par `POST /analyze` (`status: error`).
class AnalysisError {
  const AnalysisError({
    required this.code,
    required this.message,
  });

  final String code;
  final String message;

  factory AnalysisError.fromJson(Map<String, dynamic> json) {
    return AnalysisError(
      code: json['code'] as String? ?? 'unknown',
      message: json['message'] as String? ?? 'Erreur inconnue.',
    );
  }
}

/// Informations de détection YOLO + refinement ASL_L.
class DetectionInfo {
  const DetectionInfo({
    this.boundingBox,
    this.rawLandmarks = const [],
    this.refinedLandmarks = const [],
    this.itLandmarks = const [],
    this.coordinateSpace,
    this.refinementEnabled = false,
    this.refinementApplied = false,
  });

  final Map<String, double>? boundingBox;
  final List<Landmark> rawLandmarks;
  final List<Landmark> refinedLandmarks;
  final List<ITLandmark> itLandmarks;
  final CoordinateSpace? coordinateSpace;
  final bool refinementEnabled;
  final bool refinementApplied;

  int get landmarkCount => refinedLandmarks.length;

  bool get hasItLandmarks => itLandmarks.isNotEmpty;

  factory DetectionInfo.fromJson(Map<String, dynamic> json) {
    final bboxRaw = json['bounding_box'];
    Map<String, double>? bbox;
    if (bboxRaw is Map<String, dynamic>) {
      bbox = bboxRaw.map(
        (key, value) => MapEntry(key, (value as num).toDouble()),
      );
    }

    List<Landmark> parseLandmarks(dynamic raw) {
      if (raw is! List) return const [];
      return raw
          .whereType<Map<String, dynamic>>()
          .map(Landmark.fromJson)
          .toList();
    }

    List<ITLandmark> parseItLandmarks(dynamic raw) {
      if (raw is! List) return const [];
      return raw
          .whereType<Map<String, dynamic>>()
          .map(ITLandmark.fromJson)
          .toList();
    }

    final csRaw = json['coordinate_space'];
    CoordinateSpace? coordinateSpace;
    if (csRaw is Map<String, dynamic>) {
      try {
        coordinateSpace = CoordinateSpace.fromJson(csRaw);
      } on Object {
        coordinateSpace = null;
      }
    }

    return DetectionInfo(
      boundingBox: bbox,
      rawLandmarks: parseLandmarks(json['raw_landmarks']),
      refinedLandmarks: parseLandmarks(json['refined_landmarks']),
      itLandmarks: parseItLandmarks(json['it_landmarks']),
      coordinateSpace: coordinateSpace,
      refinementEnabled: json['refinement_enabled'] as bool? ?? false,
      refinementApplied: json['refinement_applied'] as bool? ?? false,
    );
  }
}

/// Réponse complète de `POST /analyze`.
class AnalysisResult {
  const AnalysisResult({
    required this.status,
    this.modelVersion,
    this.detection,
    this.measurements,
    this.audit,
    this.error,
  });

  final String status;
  final String? modelVersion;
  final DetectionInfo? detection;
  final AnalysisMeasurements? measurements;
  final Map<String, dynamic>? audit;
  final AnalysisError? error;

  bool get isOk => status == 'ok';
  bool get isError => status == 'error';
  bool get isV5Phase2 => modelVersion == 'v5_phase2';

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    final measurementsRaw = json['measurements'];
    final detectionRaw = json['detection'];
    final errorRaw = json['error'];

    return AnalysisResult(
      status: json['status'] as String,
      modelVersion: json['model_version'] as String?,
      detection: detectionRaw is Map<String, dynamic>
          ? DetectionInfo.fromJson(detectionRaw)
          : null,
      measurements: measurementsRaw is Map<String, dynamic>
          ? AnalysisMeasurements.fromJson(measurementsRaw)
          : null,
      audit: json['audit'] is Map<String, dynamic>
          ? Map<String, dynamic>.from(json['audit'] as Map)
          : null,
      error: errorRaw is Map<String, dynamic>
          ? AnalysisError.fromJson(errorRaw)
          : null,
    );
  }
}

/// Mesures bilatérales (hanche droite et gauche).
class AnalysisMeasurements {
  const AnalysisMeasurements({
    required this.right,
    required this.left,
  });

  final SideMeasurements right;
  final SideMeasurements left;

  factory AnalysisMeasurements.fromJson(Map<String, dynamic> json) {
    return AnalysisMeasurements(
      right: SideMeasurements.fromJson(json['right'] as Map<String, dynamic>),
      left: SideMeasurements.fromJson(json['left'] as Map<String, dynamic>),
    );
  }

  /// Vérifie que [raw] contient un bloc `measurements` parseable.
  static bool isValidJson(dynamic raw) {
    if (raw is! Map<String, dynamic>) return false;
    try {
      AnalysisMeasurements.fromJson(raw);
      return true;
    } on Object {
      return false;
    }
  }
}

/// Valide une réponse `status: ok` avant navigation vers les résultats.
abstract final class AnalysisResponseValidator {
  /// Message utilisateur si la réponse `ok` est incomplète ou invalide ; sinon `null`.
  static String? validateOkResponse(Map<String, dynamic> json) {
    if (json['status'] != 'ok') return null;

    if (!AnalysisMeasurements.isValidJson(json['measurements'])) {
      return 'Réponse serveur incomplète : mesures absentes ou invalides.';
    }

    try {
      AnalysisResult.fromJson(json);
      return null;
    } on Object {
      return 'Réponse serveur incomplète : format de données invalide.';
    }
  }
}
