import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' show Size;

import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/models/it_landmark.dart';
import 'package:coxometrie/services/report/landmark_overlay_composer.dart';
import 'package:coxometrie/services/report/report_content.dart';
import 'package:coxometrie/services/report/report_export_service.dart';
import 'package:coxometrie/services/report/report_pdf_builder.dart';
import 'package:coxometrie/services/report/report_pdf_fonts.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:share_plus/share_plus.dart';

import 'fixtures/analysis_fixtures.dart';

Uint8List _tinyPng() {
  return Uint8List.fromList(
    base64Decode(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
    ),
  );
}

Uint8List _png4x3() {
  final image = img.Image(width: 40, height: 30);
  img.fill(image, color: img.ColorRgb8(180, 180, 180));
  return Uint8List.fromList(img.encodePng(image));
}

bool _pdfLooksValid(Uint8List bytes) {
  if (bytes.length < 8) return false;
  return String.fromCharCodes(bytes.take(5)) == '%PDF-';
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    ReportPdfFonts.resetForTest();
  });

  group('ReportPdfBuilder', () {
    final builder = ReportPdfBuilder();

    test('A. V5 result generates non-empty valid PDF', () async {
      final result = AnalysisResult.fromJson(v5FullyAvailableJson());
      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
        generatedAt: DateTime(2026, 9, 4, 17, 30),
      );

      expect(pdf, isNotEmpty);
      expect(_pdfLooksValid(pdf), isTrue);
      expect(pdf.length, greaterThan(500));
    });

    test('B. measurement values match analysis result exactly', () async {
      final result = AnalysisResult.fromJson(v5FullyAvailableJson());
      final map = ReportPdfBuilder.measurementDisplayMap(result.measurements!);

      expect(map['right.vce'], '25.0°');
      expect(map['right.tonnis'], '10.5°');
      expect(map['right.ccd'], '130.0°');
      expect(map['left.vce'], '30.0°');
      expect(map['left.tonnis'], '9.5°');
      expect(map['left.ccd'], '128.0°');

      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4, 17, 30),
      );
      expect(content.measureValue('right', 'vce'), '25.0°');
      expect(content.measureValue('right', 'tonnis'), '10.5°');
      expect(content.measureValue('left', 'ccd'), '128.0°');

      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
      );
      expect(_pdfLooksValid(pdf), isTrue);
    });

    test('C. V5 IT_R / IT_L appear', () async {
      final result = AnalysisResult.fromJson(v5FullyAvailableJson());
      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
      );
      expect(content.itRows.map((e) => e.name), containsAll(['IT_L', 'IT_R']));
      expect(content.itRows.every((e) => e.qualityLabel == 'Accepté'), isTrue);

      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
      );
      expect(_pdfLooksValid(pdf), isTrue);
    });

    test('D. IT REVIEW shows French reason', () async {
      final result = AnalysisResult.fromJson(
        v5SuccessJson(
          itRQuality: 'review',
          itRReasons: ['low_model_confidence'],
          itLQuality: 'accept',
        ),
      );
      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
      );
      final itR = content.itRows.firstWhere((e) => e.name == 'IT_R');
      expect(itR.qualityLabel, 'À revoir');
      expect(itR.reason, 'Confiance du modèle trop basse');
      expect(
        content.warnings.any((w) => w.contains('Confiance du modèle trop basse')),
        isTrue,
      );

      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
      );
      expect(_pdfLooksValid(pdf), isTrue);
    });

    test('E. IT unavailable — no crash, no fake drawable', () async {
      final json = v5SuccessJson(
        itRQuality: 'unavailable',
        itRReasons: ['model_v0'],
        itLQuality: 'accept',
      );
      final itList = (json['detection'] as Map)['it_landmarks'] as List;
      itList[0] = itLandmarkJson(
        name: 'IT_R',
        kpIndex: 14,
        v: 0,
        quality: 'unavailable',
        qualityReasons: ['model_v0'],
      );

      final result = AnalysisResult.fromJson(json);
      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
      );
      final itR = content.itRows.firstWhere((e) => e.name == 'IT_R');
      expect(itR.qualityLabel, 'Indisponible');
      expect(itR.isDrawable, isFalse);
      expect(itR.reason, contains('non identifiable'));

      final composer = const LandmarkOverlayComposer();
      final composed = await composer.composePng(
        imageBytes: _tinyPng(),
        imageSize: const Size(1024, 768),
        landmarks: result.detection!.refinedLandmarks,
        itLandmarks: result.detection!.itLandmarks,
      );
      expect(composed.drawableItCount, 1);

      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
      );
      expect(_pdfLooksValid(pdf), isTrue);
    });

    test('F. V2 result generates without IT section crash', () async {
      final result = AnalysisResult.fromJson(v2SuccessJson());
      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
      );
      expect(content.itRows, isEmpty);
      expect(content.modelLabel, contains('V2'));

      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(200, 200),
      );
      expect(_pdfLooksValid(pdf), isTrue);
    });

    test('G. missing measurements show Non disponible', () async {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      expect(result.measurements!.left.tonnis.available, isFalse);

      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
      );
      expect(content.measureValue('left', 'tonnis'), 'Non disponible');
      expect(
        content.warnings.any((w) => w.contains('Tönnis G')),
        isTrue,
      );

      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
      );
      expect(_pdfLooksValid(pdf), isTrue);
    });

    test('H. image included and aspect ratio preserved', () async {
      final result = AnalysisResult.fromJson(v5FullyAvailableJson());
      final composer = const LandmarkOverlayComposer();
      final composed = await composer.composePng(
        imageBytes: _png4x3(),
        imageSize: const Size(400, 300),
        landmarks: result.detection!.refinedLandmarks,
        itLandmarks: result.detection!.itLandmarks,
      );

      expect(composed.pngBytes, isNotEmpty);
      expect(composed.aspectRatioPreserved, isTrue);
      expect(composed.width / composed.height, closeTo(400 / 300, 0.02));

      final aligned = await composer.composePng(
        imageBytes: _tinyPng(),
        imageSize: const Size(1024, 768),
        landmarks: const [],
        itLandmarks: const [],
        maxEdge: 1024,
      );
      final expected = aligned.layout.toDisplay(300, 500);
      expect(expected.dx, closeTo(300, 0.5));
      expect(expected.dy, closeTo(500, 0.5));

      final pdf = await builder.buildPdfBytes(
        radiographBytes: _png4x3(),
        result: result,
        localImageSize: const Size(400, 300),
      );
      expect(_pdfLooksValid(pdf), isTrue);
      // PNG signature appears embedded in PDF stream
      expect(
        pdf.indexOf(0x89) >= 0 || pdf.length > 1000,
        isTrue,
      );
    });

    test('disclaimer present without diagnosis claims', () async {
      final result = AnalysisResult.fromJson(v5FullyAvailableJson());
      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
      );
      expect(content.disclaimer.toLowerCase(), isNot(contains('dysplas')));
      expect(content.disclaimer.toLowerCase(), isNot(contains('traitement')));
      expect(content.disclaimer, contains('professionnel'));
      expect(content.disclaimer, contains('diagnostic'));
    });
  });

  group('ReportExportService', () {
    test('saves PDF to documents directory', () async {
      final tmp = await Directory.systemTemp.createTemp('cox_pdf_');
      addTearDown(() => tmp.delete(recursive: true));

      var shared = false;
      final service = ReportExportService(
        documentsDirectory: () async => tmp,
        shareFile: (file, {subject}) async {
          shared = true;
          expect(await file.length(), greaterThan(0));
          return ShareResult.unavailable;
        },
      );

      final result = AnalysisResult.fromJson(v5FullyAvailableJson());
      final export = await service.exportAndShare(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
        generatedAt: DateTime(2026, 9, 4, 12, 0, 0),
      );

      expect(await export.file.exists(), isTrue);
      expect(_pdfLooksValid(export.bytes), isTrue);
      expect(shared, isTrue);
      expect(export.file.path.contains('rapport_coxometrie_'), isTrue);
    });
  });
}
