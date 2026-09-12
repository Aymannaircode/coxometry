import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' show Size;

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../../models/analysis_result.dart';
import 'report_display_snapshot.dart';
import 'report_pdf_builder.dart';

/// Orchestration export : génération PDF → enregistrement → partage.
///
/// Couche présentation uniquement — pas d'inférence ni de calcul clinique.
class ReportExportService {
  ReportExportService({
    ReportPdfBuilder? builder,
    Future<Directory> Function()? documentsDirectory,
    Future<ShareResult> Function(XFile file, {String? subject})? shareFile,
    Future<ReportExportResult> Function({
      required Uint8List radiographBytes,
      required AnalysisResult result,
      Size? localImageSize,
      DateTime? generatedAt,
      ReportDisplaySnapshot? display,
    })? exportHandler,
  })  : _builder = builder ?? ReportPdfBuilder(),
        _documentsDirectory =
            documentsDirectory ?? getApplicationDocumentsDirectory,
        _shareFile = shareFile ?? _defaultShare,
        _exportHandler = exportHandler;

  final ReportPdfBuilder _builder;
  final Future<Directory> Function() _documentsDirectory;
  final Future<ShareResult> Function(XFile file, {String? subject}) _shareFile;
  final Future<ReportExportResult> Function({
    required Uint8List radiographBytes,
    required AnalysisResult result,
    Size? localImageSize,
    DateTime? generatedAt,
    ReportDisplaySnapshot? display,
  })? _exportHandler;

  static Future<ShareResult> _defaultShare(
    XFile file, {
    String? subject,
  }) {
    return SharePlus.instance.share(
      ShareParams(
        files: [file],
        subject: subject,
        title: subject,
      ),
    );
  }

  /// Génère le PDF et l'enregistre sous le répertoire documents de l'app.
  Future<ReportExportResult> generateAndSave({
    required Uint8List radiographBytes,
    required AnalysisResult result,
    Size? localImageSize,
    DateTime? generatedAt,
    ReportDisplaySnapshot? display,
  }) async {
    final bytes = await _builder.buildPdfBytes(
      radiographBytes: radiographBytes,
      result: result,
      localImageSize: localImageSize,
      generatedAt: generatedAt,
      display: display,
    );

    if (bytes.isEmpty) {
      throw StateError('Le PDF généré est vide.');
    }

    final dir = await _documentsDirectory();
    final stamp = generatedAt ?? DateTime.now();
    final name =
        'rapport_coxometrie_${stamp.year}'
        '${stamp.month.toString().padLeft(2, '0')}'
        '${stamp.day.toString().padLeft(2, '0')}_'
        '${stamp.hour.toString().padLeft(2, '0')}'
        '${stamp.minute.toString().padLeft(2, '0')}'
        '${stamp.second.toString().padLeft(2, '0')}.pdf';
    final file = File(p.join(dir.path, name));
    await file.writeAsBytes(bytes, flush: true);

    return ReportExportResult(file: file, bytes: bytes);
  }

  /// Propose le partage système du fichier PDF déjà généré.
  Future<ShareResult> share(ReportExportResult export) {
    return _shareFile(
      XFile(
        export.file.path,
        mimeType: 'application/pdf',
        name: p.basename(export.file.path),
      ),
      subject: 'Rapport d\'analyse coxométrique',
    );
  }

  /// Génération + enregistrement + partage.
  Future<ReportExportResult> exportAndShare({
    required Uint8List radiographBytes,
    required AnalysisResult result,
    Size? localImageSize,
    DateTime? generatedAt,
    ReportDisplaySnapshot? display,
  }) async {
    final handler = _exportHandler;
    if (handler != null) {
      return handler(
        radiographBytes: radiographBytes,
        result: result,
        localImageSize: localImageSize,
        generatedAt: generatedAt,
        display: display,
      );
    }

    final export = await generateAndSave(
      radiographBytes: radiographBytes,
      result: result,
      localImageSize: localImageSize,
      generatedAt: generatedAt,
      display: display,
    );
    await share(export);
    return export;
  }
}

class ReportExportResult {
  const ReportExportResult({
    required this.file,
    required this.bytes,
  });

  final File file;
  final Uint8List bytes;

  int get byteLength => bytes.length;
}
