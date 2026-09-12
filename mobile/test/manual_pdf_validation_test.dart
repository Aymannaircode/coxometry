/// Script manuel — génère des PDF de validation Phase 6A.
///
/// Usage:
///   flutter test test/manual_pdf_validation_test.dart
///
/// Les fichiers sont écrits dans le répertoire temporaire système
/// (chemin imprimé en sortie).
library;

import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' show Size;

import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/services/report/report_pdf_builder.dart';
import 'package:coxometrie/services/report/report_pdf_fonts.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;

import 'fixtures/analysis_fixtures.dart';

Uint8List _sampleRadiograph() {
  final image = img.Image(width: 640, height: 480);
  img.fill(image, color: img.ColorRgb8(40, 40, 40));
  // Zones claires simulées (bassin)
  img.fillRect(
    image,
    x1: 80,
    y1: 60,
    x2: 560,
    y2: 420,
    color: img.ColorRgb8(200, 200, 200),
  );
  return Uint8List.fromList(img.encodePng(image));
}

Future<File> _writePdf(String name, Uint8List bytes) async {
  final dir = await Directory.systemTemp.createTemp('cox_phase6a_pdf_');
  final file = File('${dir.path}/$name');
  await file.writeAsBytes(bytes, flush: true);
  // ignore: avoid_print
  print('WROTE ${file.path} (${bytes.length} bytes)');
  return file;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => ReportPdfFonts.resetForTest());

  test('manual: generate V5 / review / unavailable / V2 PDFs', () async {
    final builder = ReportPdfBuilder();
    final bytes = _sampleRadiograph();
    final outDir = await Directory.systemTemp.createTemp('cox_phase6a_manual_');
    // ignore: avoid_print
    print('OUT_DIR ${outDir.path}');

    Future<void> gen(String name, Map<String, dynamic> json) async {
      final result = AnalysisResult.fromJson(json);
      final pdf = await builder.buildPdfBytes(
        radiographBytes: bytes,
        result: result,
        localImageSize: const Size(640, 480),
        generatedAt: DateTime(2026, 9, 4, 17, 45),
      );
      expect(pdf.length, greaterThan(500));
      expect(utf8.decode(pdf.take(5).toList(), allowMalformed: true), '%PDF-');
      final file = File('${outDir.path}/$name');
      await file.writeAsBytes(pdf, flush: true);
      // ignore: avoid_print
      print('WROTE ${file.path} (${pdf.length} bytes)');
    }

    await gen('01_v5_accept.pdf', v5FullyAvailableJson());
    await gen(
      '02_v5_it_review.pdf',
      v5SuccessJson(
        itRQuality: 'review',
        itRReasons: ['low_model_confidence'],
        itLQuality: 'accept',
      ),
    );

    final unavailable = v5SuccessJson(
      itRQuality: 'unavailable',
      itRReasons: ['model_v0'],
      itLQuality: 'accept',
    );
    final itList = (unavailable['detection'] as Map)['it_landmarks'] as List;
    itList[0] = itLandmarkJson(
      name: 'IT_R',
      kpIndex: 14,
      v: 0,
      quality: 'unavailable',
      qualityReasons: ['model_v0'],
    );
    await gen('03_v5_it_unavailable.pdf', unavailable);
    await gen('04_v2_compatible.pdf', v2SuccessJson());

    // Copie aussi via helper pour smoke path write
    final smoke = await builder.buildPdfBytes(
      radiographBytes: bytes,
      result: AnalysisResult.fromJson(v5FullyAvailableJson()),
      localImageSize: const Size(640, 480),
    );
    await _writePdf('smoke_v5.pdf', smoke);
  });
}
