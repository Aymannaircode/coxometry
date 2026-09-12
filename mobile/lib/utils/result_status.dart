import '../models/analysis_result.dart';
import '../models/it_landmark.dart';
import '../models/measurement.dart';

/// État de présentation Results — dérivé uniquement des champs API existants.
enum ResultPresentationKind {
  /// Analyse OK, pas de REVIEW IT, mesures complètes (ou V2 sans IT).
  success,

  /// Au moins un landmark IT en qualité `review` (pas un échec).
  review,

  /// IT unavailable et/ou mesures indisponibles — informations partielles.
  incomplete,
}

/// Bannière Results : succès / à revoir / partiel (pas d'erreur API ici).
class ResultPresentationStatus {
  const ResultPresentationStatus({
    required this.kind,
    required this.title,
    this.detail,
  });

  final ResultPresentationKind kind;
  final String title;
  final String? detail;

  /// Classifie l'affichage à partir de [AnalysisResult] déjà validé (écran Results).
  ///
  /// Les erreurs API restent sur [AnalysisScreen] — cet helper ne les invente pas.
  factory ResultPresentationStatus.fromAnalysis(AnalysisResult result) {
    final itLandmarks = result.detection?.itLandmarks ?? const <ITLandmark>[];

    final reviewNames = itLandmarks
        .where((l) => l.isReview)
        .map((l) => l.name)
        .where((n) => n.isNotEmpty)
        .toList(growable: false);

    if (reviewNames.isNotEmpty) {
      return ResultPresentationStatus(
        kind: ResultPresentationKind.review,
        title: 'Vérification recommandée',
        detail: 'Repères à revoir : ${reviewNames.join(', ')}',
      );
    }

    final unavailableIt = itLandmarks
        .where((l) => l.isUnavailable)
        .map((l) => l.name)
        .where((n) => n.isNotEmpty)
        .toList(growable: false);

    final missingMeasures = _unavailableMeasureLabels(result.measurements);

    if (unavailableIt.isNotEmpty || missingMeasures.isNotEmpty) {
      final parts = <String>[];
      if (unavailableIt.isNotEmpty) {
        parts.add('Repères indisponibles : ${unavailableIt.join(', ')}');
      }
      if (missingMeasures.isNotEmpty) {
        parts.add('Mesures indisponibles : ${missingMeasures.join(', ')}');
      }
      return ResultPresentationStatus(
        kind: ResultPresentationKind.incomplete,
        title: 'Analyse terminée — informations partielles',
        detail: parts.join('\n'),
      );
    }

    return const ResultPresentationStatus(
      kind: ResultPresentationKind.success,
      title: 'Analyse terminée',
    );
  }
}

List<String> _unavailableMeasureLabels(AnalysisMeasurements? measurements) {
  if (measurements == null) return const [];

  final labels = <String>[];
  void addSide(String sideLabel, SideMeasurements side) {
    if (!side.vce.available) labels.add('VCE $sideLabel');
    if (!side.tonnis.available) labels.add('Tönnis $sideLabel');
    if (!side.ccd.available) labels.add('CCD $sideLabel');
  }

  addSide('D', measurements.right);
  addSide('G', measurements.left);
  return labels;
}
