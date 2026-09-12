import 'dart:typed_data';
import 'dart:ui' show Size;

import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

import '../../models/analysis_result.dart';
import '../../models/it_landmark.dart';
import '../../models/measurement.dart';
import '../../utils/overlay_image_size.dart';
import 'landmark_overlay_composer.dart';
import 'report_content.dart';
import 'report_display_snapshot.dart';
import 'report_pdf_fonts.dart';

/// Construit le PDF de rapport à partir de l'état d'affichage courant.
///
/// Consommateur uniquement : ne recalcule aucune mesure clinique et
/// n'exécute aucune inférence. Les landmarks viennent de [ReportDisplaySnapshot]
/// (`currentLandmarks` ou refined AI) — jamais de `raw_landmarks`.
class ReportPdfBuilder {
  ReportPdfBuilder({
    LandmarkOverlayComposer? composer,
  }) : _composer = composer ?? const LandmarkOverlayComposer();

  final LandmarkOverlayComposer _composer;

  static const String disclaimer =
      'Ce rapport présente des mesures coxométriques issues d\'une analyse '
      'assistée par IA. Les résultats doivent être vérifiés par un '
      'professionnel qualifié et ne constituent pas à eux seuls un diagnostic '
      'médical. Aucune certification de dispositif médical n\'est revendiquée.';

  /// Construit les octets PDF (A4).
  ///
  /// [display] = instantané Results (landmarks + mesures + statut correction).
  /// Si omis, retombe sur l'état IA de [result] (comportement historique).
  Future<Uint8List> buildPdfBytes({
    required Uint8List radiographBytes,
    required AnalysisResult result,
    Size? localImageSize,
    DateTime? generatedAt,
    ReportDisplaySnapshot? display,
  }) async {
    if (!result.isOk) {
      throw ArgumentError(
        'Seules les analyses status=ok peuvent générer un rapport.',
      );
    }

    final now = generatedAt ?? DateTime.now();
    final detection = result.detection;
    final snapshot = display ?? ReportDisplaySnapshot.fromAnalysisResult(result);

    final overlaySize = resolveOverlayImageSize(
      coordinateSpace: detection?.coordinateSpace,
      localSize: localImageSize,
    );

    OverlayComposeResult? overlay;
    if (radiographBytes.isNotEmpty) {
      overlay = await _composer.composePng(
        imageBytes: radiographBytes,
        imageSize: overlaySize.size,
        landmarks: snapshot.landmarks,
        itLandmarks: detection?.itLandmarks ?? const [],
      );
    }

    final content = ReportContent.fromAnalysis(
      result: result,
      generatedAt: now,
      hasImage: overlay != null,
      overlaySize: overlaySize,
      display: snapshot,
    );

    await ReportPdfFonts.ensureLoaded();

    final doc = pw.Document(
      title: content.title,
      author: 'Coxométrie',
      theme: ReportPdfFonts.theme(),
    );

    doc.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.fromLTRB(40, 36, 40, 40),
        build: (context) => [
          _buildHeader(content),
          pw.SizedBox(height: 14),
          if (overlay != null) ...[
            _buildImageSection(overlay),
            pw.SizedBox(height: 12),
          ],
          _buildStatusSection(content),
          pw.SizedBox(height: 14),
          if (content.rightMeasures.isNotEmpty) ...[
            _sectionTitle('Mesures'),
            pw.SizedBox(height: 6),
            _buildMeasurementsTable('Hanche droite', content.rightMeasures),
            pw.SizedBox(height: 10),
            _buildMeasurementsTable('Hanche gauche', content.leftMeasures),
            pw.SizedBox(height: 14),
          ],
          if (content.itRows.isNotEmpty) ...[
            _sectionTitle('Qualité des repères IT'),
            pw.SizedBox(height: 6),
            _buildItSection(content.itRows),
            pw.SizedBox(height: 14),
          ],
          if (content.warnings.isNotEmpty) ...[
            _sectionTitle('Avertissements'),
            pw.SizedBox(height: 6),
            for (final w in content.warnings)
              pw.Padding(
                padding: const pw.EdgeInsets.only(bottom: 4),
                child: pw.Text(
                  '• $w',
                  style: const pw.TextStyle(
                    fontSize: 9.5,
                    color: PdfColors.brown800,
                  ),
                ),
              ),
            pw.SizedBox(height: 14),
          ],
          _buildDisclaimer(content.disclaimer),
        ],
      ),
    );

    return doc.save();
  }

  /// Extrait les valeurs de mesures telles qu'écrites dans le PDF (tests).
  static Map<String, String> measurementDisplayMap(AnalysisMeasurements m) {
    return {
      'right.vce': measureDisplayValue(m.right.vce),
      'right.tonnis': measureDisplayValue(m.right.tonnis),
      'right.ccd': measureDisplayValue(m.right.ccd),
      'left.vce': measureDisplayValue(m.left.vce),
      'left.tonnis': measureDisplayValue(m.left.tonnis),
      'left.ccd': measureDisplayValue(m.left.ccd),
    };
  }

  static String measureDisplayValue(Measurement m) {
    if (!m.available || m.valueDeg == null) return 'Non disponible';
    return '${m.valueDeg!.toStringAsFixed(1)}°';
  }

  static String itQualityLabel(ITQuality? quality) {
    switch (quality) {
      case ITQuality.accept:
        return 'Accepté';
      case ITQuality.review:
        return 'À revoir';
      case ITQuality.unavailable:
      case null:
        return 'Indisponible';
    }
  }

  pw.Widget _buildHeader(ReportContent content) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          'Coxométrie',
          style: pw.TextStyle(
            fontSize: 18,
            fontWeight: pw.FontWeight.bold,
            color: PdfColor.fromInt(0xFF0B4F6C),
          ),
        ),
        pw.SizedBox(height: 2),
        pw.Text(
          content.title,
          style: pw.TextStyle(
            fontSize: 13,
            fontWeight: pw.FontWeight.bold,
            color: PdfColor.fromInt(0xFF1A2330),
          ),
        ),
        pw.SizedBox(height: 6),
        pw.Text(
          content.generatedAtLabel,
          style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey700),
        ),
        pw.Text(
          content.modelLabel,
          style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey700),
        ),
        pw.SizedBox(height: 8),
        pw.Container(height: 1, color: PdfColors.grey400),
      ],
    );
  }

  pw.Widget _buildImageSection(OverlayComposeResult overlay) {
    final image = pw.MemoryImage(overlay.pngBytes);
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        _sectionTitle('Radiographie et repères'),
        pw.SizedBox(height: 6),
        pw.Center(
          child: pw.Container(
            decoration: pw.BoxDecoration(
              border: pw.Border.all(color: PdfColors.grey400, width: 0.5),
            ),
            child: pw.Image(
              image,
              width: 480,
              fit: pw.BoxFit.contain,
            ),
          ),
        ),
        pw.SizedBox(height: 4),
        pw.Text(
          'Repères anatomiques (orange) · Repères IT (vert) · '
          'À revoir (ambre)',
          style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey600),
        ),
      ],
    );
  }

  pw.Widget _buildStatusSection(ReportContent content) {
    return pw.Container(
      width: double.infinity,
      padding: const pw.EdgeInsets.all(10),
      decoration: pw.BoxDecoration(
        border: pw.Border.all(color: PdfColors.grey400, width: 0.6),
        borderRadius: pw.BorderRadius.circular(3),
      ),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text(
            'Statut : ${content.statusTitle}',
            style: pw.TextStyle(
              fontSize: 11,
              fontWeight: pw.FontWeight.bold,
            ),
          ),
          pw.SizedBox(height: 4),
          pw.Text(
            content.analysisOriginLabel,
            style: const pw.TextStyle(fontSize: 9.5, color: PdfColors.grey800),
          ),
          if (content.statusDetail != null) ...[
            pw.SizedBox(height: 4),
            pw.Text(
              content.statusDetail!,
              style: const pw.TextStyle(fontSize: 9.5, color: PdfColors.grey800),
            ),
          ],
        ],
      ),
    );
  }

  pw.Widget _buildMeasurementsTable(
    String sideTitle,
    List<ReportMeasureLine> rows,
  ) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          sideTitle,
          style: pw.TextStyle(fontSize: 10.5, fontWeight: pw.FontWeight.bold),
        ),
        pw.SizedBox(height: 4),
        pw.Table(
          border: pw.TableBorder.all(color: PdfColors.grey400, width: 0.4),
          columnWidths: {
            0: const pw.FlexColumnWidth(3.2),
            1: const pw.FlexColumnWidth(1.4),
          },
          children: [
            pw.TableRow(
              decoration: const pw.BoxDecoration(color: PdfColors.grey200),
              children: [
                _cell('Mesure', bold: true),
                _cell('Valeur', bold: true),
              ],
            ),
            for (final row in rows)
              pw.TableRow(
                children: [
                  _cell(
                    row.reason == null
                        ? row.label
                        : '${row.label}\n(${row.reason})',
                  ),
                  _cell(row.value),
                ],
              ),
          ],
        ),
      ],
    );
  }

  pw.Widget _buildItSection(List<ReportItLine> rows) {
    return pw.Table(
      border: pw.TableBorder.all(color: PdfColors.grey400, width: 0.4),
      columnWidths: {
        0: const pw.FlexColumnWidth(1.2),
        1: const pw.FlexColumnWidth(1.4),
        2: const pw.FlexColumnWidth(3.2),
      },
      children: [
        pw.TableRow(
          decoration: const pw.BoxDecoration(color: PdfColors.grey200),
          children: [
            _cell('Repère', bold: true),
            _cell('Qualité', bold: true),
            _cell('Motif', bold: true),
          ],
        ),
        for (final row in rows)
          pw.TableRow(
            children: [
              _cell(row.name),
              _cell(row.qualityLabel),
              _cell(row.reason),
            ],
          ),
      ],
    );
  }

  pw.Widget _buildDisclaimer(String text) {
    return pw.Container(
      width: double.infinity,
      padding: const pw.EdgeInsets.all(10),
      decoration: pw.BoxDecoration(
        color: PdfColors.grey100,
        borderRadius: pw.BorderRadius.circular(3),
      ),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text(
            'Avertissement',
            style: pw.TextStyle(
              fontSize: 9,
              fontWeight: pw.FontWeight.bold,
              color: PdfColors.grey800,
            ),
          ),
          pw.SizedBox(height: 4),
          pw.Text(
            text,
            style: const pw.TextStyle(fontSize: 8.5, color: PdfColors.grey700),
          ),
        ],
      ),
    );
  }

  pw.Widget _sectionTitle(String text) {
    return pw.Text(
      text,
      style: pw.TextStyle(
        fontSize: 12,
        fontWeight: pw.FontWeight.bold,
        color: PdfColor.fromInt(0xFF0B4F6C),
      ),
    );
  }

  pw.Widget _cell(String text, {bool bold = false}) {
    return pw.Padding(
      padding: const pw.EdgeInsets.symmetric(horizontal: 6, vertical: 5),
      child: pw.Text(
        text,
        style: pw.TextStyle(
          fontSize: 9,
          fontWeight: bold ? pw.FontWeight.bold : pw.FontWeight.normal,
        ),
      ),
    );
  }
}
