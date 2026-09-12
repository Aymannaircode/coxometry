import '../../models/analysis_result.dart';
import '../../models/landmark.dart';
import '../../models/landmark_correction_state.dart';
import '../../models/measurement.dart';

/// Instantané de l'affichage Results — le PDF en est uniquement consommateur.
///
/// Ne recalcule aucune mesure et n'exécute aucune inférence.
class ReportDisplaySnapshot {
  const ReportDisplaySnapshot({
    required this.landmarks,
    this.measurements,
    this.correctionStatus = CorrectionSessionStatus.aiOnly,
    this.correctedLandmarkCount = 0,
  });

  /// Landmarks à dessiner (currentLandmarks ou refined AI).
  ///
  /// Jamais `raw_landmarks`.
  final List<Landmark> landmarks;

  /// Mesures actuellement affichées à l'écran.
  final AnalysisMeasurements? measurements;

  final CorrectionSessionStatus correctionStatus;
  final int correctedLandmarkCount;

  /// Libellé concis d'origine de l'analyse (PDF).
  String get analysisOriginLabel => formatAnalysisOriginLabel(
        correctionStatus: correctionStatus,
        correctedLandmarkCount: correctedLandmarkCount,
      );

  /// Cas A / défaut : état IA issu de `/analyze` uniquement.
  factory ReportDisplaySnapshot.fromAnalysisResult(AnalysisResult result) {
    return ReportDisplaySnapshot(
      landmarks: result.detection?.refinedLandmarks ?? const [],
      measurements: result.measurements,
      correctionStatus: CorrectionSessionStatus.aiOnly,
      correctedLandmarkCount: 0,
    );
  }

  /// Construit depuis l'état de correction + mesures affichées (ResultsScreen).
  factory ReportDisplaySnapshot.fromCorrectionState({
    required AnalysisResult result,
    LandmarkCorrectionState? correctionState,
    AnalysisMeasurements? displayedMeasurements,
  }) {
    final correction = correctionState;
    return ReportDisplaySnapshot(
      landmarks: correction?.currentLandmarks ??
          result.detection?.refinedLandmarks ??
          const [],
      measurements: displayedMeasurements ?? result.measurements,
      correctionStatus:
          correction?.globalStatus ?? CorrectionSessionStatus.aiOnly,
      correctedLandmarkCount: correction?.correctedCount ?? 0,
    );
  }

  /// Texte PDF : « Analyse : IA » ou « Analyse : IA + correction manuelle (N) ».
  ///
  /// [N] = nombre de landmarks au statut CORRECTED (source de vérité explicite).
  static String formatAnalysisOriginLabel({
    required CorrectionSessionStatus correctionStatus,
    required int correctedLandmarkCount,
  }) {
    if (correctionStatus == CorrectionSessionStatus.aiOnly ||
        correctedLandmarkCount <= 0) {
      return 'Analyse : IA';
    }
    return 'Analyse : IA + correction manuelle ($correctedLandmarkCount)';
  }
}
