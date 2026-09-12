import '../../models/analysis_result.dart';
import '../../models/it_landmark.dart';
import '../../models/measurement.dart';
import '../../utils/it_quality_reason_label.dart';
import '../../utils/model_version_label.dart';
import '../../utils/overlay_image_size.dart';
import '../../utils/result_status.dart';
import 'report_display_snapshot.dart';
import 'report_pdf_builder.dart';

/// Contenu textuel du rapport — miroir exact de ce qui est rendu dans le PDF.
///
/// Permet de tester les valeurs sans dépendre de l'encodage glyphe TTF.
class ReportContent {
  const ReportContent({
    required this.title,
    required this.generatedAtLabel,
    required this.modelLabel,
    required this.statusTitle,
    this.statusDetail,
    required this.analysisOriginLabel,
    required this.rightMeasures,
    required this.leftMeasures,
    required this.itRows,
    required this.warnings,
    required this.disclaimer,
    required this.hasImage,
  });

  final String title;
  final String generatedAtLabel;
  final String modelLabel;
  final String statusTitle;
  final String? statusDetail;

  /// Origine de l'analyse affichée (IA seule ou IA + corrections).
  final String analysisOriginLabel;
  final List<ReportMeasureLine> rightMeasures;
  final List<ReportMeasureLine> leftMeasures;
  final List<ReportItLine> itRows;
  final List<String> warnings;
  final String disclaimer;
  final bool hasImage;

  /// Construit le contenu à partir du résultat d'analyse (sans image).
  ///
  /// Si [display] est fourni, les mesures et le libellé d'origine viennent
  /// de l'instantané courant (pas de recalcul).
  factory ReportContent.fromAnalysis({
    required AnalysisResult result,
    required DateTime generatedAt,
    bool hasImage = true,
    OverlayImageSizeResult? overlaySize,
    ReportDisplaySnapshot? display,
  }) {
    final snapshot = display ?? ReportDisplaySnapshot.fromAnalysisResult(result);
    final measurements = snapshot.measurements;
    final status = ResultPresentationStatus.fromAnalysis(result);
    final itLandmarks = result.detection?.itLandmarks ?? const <ITLandmark>[];

    final dateLabel =
        '${generatedAt.day.toString().padLeft(2, '0')}/'
        '${generatedAt.month.toString().padLeft(2, '0')}/'
        '${generatedAt.year} '
        '${generatedAt.hour.toString().padLeft(2, '0')}:'
        '${generatedAt.minute.toString().padLeft(2, '0')}';

    return ReportContent(
      title: 'Rapport d\'analyse coxométrique',
      generatedAtLabel: 'Date du rapport : $dateLabel',
      modelLabel: 'Modèle : ${formatModelVersion(result.modelVersion)}',
      statusTitle: status.title,
      statusDetail: status.detail,
      analysisOriginLabel: snapshot.analysisOriginLabel,
      rightMeasures: measurements == null
          ? const []
          : _sideLines(measurements.right),
      leftMeasures: measurements == null
          ? const []
          : _sideLines(measurements.left),
      itRows: _itLines(itLandmarks),
      warnings: _warnings(
        result,
        overlaySize,
        measurementsOverride: measurements,
      ),
      disclaimer: ReportPdfBuilder.disclaimer,
      hasImage: hasImage,
    );
  }

  String measureValue(String side, String key) {
    final list = side == 'right' ? rightMeasures : leftMeasures;
    return list.firstWhere((l) => l.key == key).value;
  }

  static List<ReportMeasureLine> _sideLines(SideMeasurements side) {
    return [
      ReportMeasureLine(
        key: 'vce',
        label: 'Angle VCE / Wiberg',
        value: ReportPdfBuilder.measureDisplayValue(side.vce),
        reason: side.vce.available ? null : side.vce.reason,
      ),
      ReportMeasureLine(
        key: 'tonnis',
        label: 'Angle de Tönnis',
        value: ReportPdfBuilder.measureDisplayValue(side.tonnis),
        reason: side.tonnis.available ? null : side.tonnis.reason,
      ),
      ReportMeasureLine(
        key: 'ccd',
        label: 'Angle cervico-diaphysaire (CCD)',
        value: ReportPdfBuilder.measureDisplayValue(side.ccd),
        reason: side.ccd.available ? null : side.ccd.reason,
      ),
    ];
  }

  static List<ReportItLine> _itLines(List<ITLandmark> itLandmarks) {
    final sorted = List<ITLandmark>.from(itLandmarks)
      ..sort((a, b) => a.name.compareTo(b.name));
    return [
      for (final it in sorted)
        ReportItLine(
          name: it.name,
          qualityLabel: ReportPdfBuilder.itQualityLabel(it.quality),
          reason: _itReason(it),
          isDrawable: it.isDrawable,
        ),
    ];
  }

  static String _itReason(ITLandmark it) {
    if (it.quality == ITQuality.accept) return '—';
    if (it.qualityReasons.isEmpty) return '—';
    if (it.quality == ITQuality.review && it.primaryQualityReason != null) {
      return formatItQualityReason(it.primaryQualityReason!);
    }
    return formatItQualityReasons(it.qualityReasons);
  }

  static List<String> _warnings(
    AnalysisResult result,
    OverlayImageSizeResult? overlaySize, {
    AnalysisMeasurements? measurementsOverride,
  }) {
    final warnings = <String>[];

    for (final it in result.detection?.itLandmarks ?? const <ITLandmark>[]) {
      if (it.isReview) {
        final reason = it.primaryQualityReason != null
            ? formatItQualityReason(it.primaryQualityReason!)
            : null;
        warnings.add(
          reason == null
              ? '${it.name} : vérification recommandée'
              : '${it.name} : $reason',
        );
      } else if (it.isUnavailable) {
        final reason = it.qualityReasons.isNotEmpty
            ? formatItQualityReasons(it.qualityReasons)
            : null;
        warnings.add(
          reason == null
              ? '${it.name} : non disponible'
              : '${it.name} : $reason',
        );
      }
    }

    final measurements = measurementsOverride ?? result.measurements;
    if (measurements != null) {
      void addMissing(String side, SideMeasurements s) {
        void one(String name, Measurement m) {
          if (!m.available) {
            final r = (m.reason != null && m.reason!.isNotEmpty)
                ? ' (${m.reason})'
                : '';
            warnings.add('$name $side : non disponible$r');
          }
        }

        one('VCE', s.vce);
        one('Tönnis', s.tonnis);
        one('CCD', s.ccd);
      }

      addMissing('D', measurements.right);
      addMissing('G', measurements.left);
    }

    if (overlaySize?.dimensionMismatch == true &&
        overlaySize?.mismatchDetail != null) {
      warnings.add(overlaySize!.mismatchDetail!);
    }

    final seen = <String>{};
    return warnings.where((w) => seen.add(w)).toList(growable: false);
  }
}

class ReportMeasureLine {
  const ReportMeasureLine({
    required this.key,
    required this.label,
    required this.value,
    this.reason,
  });

  final String key;
  final String label;
  final String value;
  final String? reason;
}

class ReportItLine {
  const ReportItLine({
    required this.name,
    required this.qualityLabel,
    required this.reason,
    required this.isDrawable,
  });

  final String name;
  final String qualityLabel;
  final String reason;
  final bool isDrawable;
}
