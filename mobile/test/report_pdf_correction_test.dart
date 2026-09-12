import 'dart:convert';
import 'dart:typed_data';
import 'dart:ui' show Size;

import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/models/it_landmark.dart';
import 'package:coxometrie/models/landmark.dart';
import 'package:coxometrie/models/landmark_correction_state.dart';
import 'package:coxometrie/models/measurement.dart';
import 'package:coxometrie/services/report/landmark_overlay_composer.dart';
import 'package:coxometrie/services/report/report_content.dart';
import 'package:coxometrie/services/report/report_display_snapshot.dart';
import 'package:coxometrie/services/report/report_pdf_builder.dart';
import 'package:coxometrie/services/report/report_pdf_fonts.dart';
import 'package:flutter_test/flutter_test.dart';

import 'fixtures/analysis_fixtures.dart';

Uint8List _tinyPng() {
  return Uint8List.fromList(
    base64Decode(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
    ),
  );
}

bool _pdfLooksValid(Uint8List bytes) {
  if (bytes.length < 8) return false;
  return String.fromCharCodes(bytes.take(5)) == '%PDF-';
}

Measurement _m(double deg) => Measurement(valueDeg: deg, available: true);

AnalysisMeasurements _measures({
  required double rightVce,
  required double leftVce,
}) {
  return AnalysisMeasurements(
    right: SideMeasurements(
      vce: _m(rightVce),
      tonnis: _m(10.5),
      ccd: _m(130.0),
    ),
    left: SideMeasurements(
      vce: _m(leftVce),
      tonnis: _m(9.5),
      ccd: _m(128.0),
    ),
  );
}

Landmark? _byName(List<Landmark> list, String name) {
  for (final lm in list) {
    if (lm.name == name) return lm;
  }
  return null;
}

List<Landmark> _correctableSample() => const [
      Landmark(name: 'TD_R', x: 300.0, y: 500.0, confidence: 0.9),
      Landmark(name: 'TD_L', x: 700.0, y: 510.0, confidence: 0.91),
      Landmark(name: 'ASL_R', x: 250.0, y: 320.0, confidence: 0.88),
      Landmark(name: 'ASL_L', x: 750.0, y: 330.0, confidence: 0.87),
      Landmark(name: 'FSP_R', x: 220.0, y: 480.0, confidence: 0.85),
      Landmark(name: 'FSP_L', x: 780.0, y: 490.0, confidence: 0.84),
      Landmark(name: 'FSD_R', x: 210.0, y: 560.0, confidence: 0.83),
      Landmark(name: 'FSD_L', x: 790.0, y: 570.0, confidence: 0.82),
    ];

AnalysisResult _resultWithCorrectableLandmarks() {
  final json = v5FullyAvailableJson();
  final detection = json['detection'] as Map<String, dynamic>;
  detection['raw_landmarks'] = [
    {'name': 'ASL_L', 'x': 1.0, 'y': 2.0, 'confidence': 0.5},
    {'name': 'TD_R', 'x': 300.0, 'y': 500.0, 'confidence': 0.9},
  ];
  detection['refined_landmarks'] = [
    for (final lm in _correctableSample())
      {
        'name': lm.name,
        'x': lm.x,
        'y': lm.y,
        'confidence': lm.confidence,
      },
  ];
  return AnalysisResult.fromJson(json);
}

class _RecordingComposer extends LandmarkOverlayComposer {
  List<Landmark>? lastLandmarks;

  @override
  Future<OverlayComposeResult> composePng({
    required Uint8List imageBytes,
    required Size imageSize,
    List<Landmark> landmarks = const [],
    List<ITLandmark> itLandmarks = const [],
    double maxEdge = 1600,
    bool showLabels = true,
    double pointRadius = 4.5,
  }) async {
    lastLandmarks = List<Landmark>.from(landmarks);
    return super.composePng(
      imageBytes: imageBytes,
      imageSize: imageSize,
      landmarks: landmarks,
      itLandmarks: itLandmarks,
      maxEdge: maxEdge,
      showLabels: showLabels,
      pointRadius: pointRadius,
    );
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    ReportPdfFonts.resetForTest();
  });

  group('ReportDisplaySnapshot / analysis origin label', () {
    test('5. correction count uses CORRECTED status, not pixel tolerance', () {
      final result = _resultWithCorrectableLandmarks();
      final refined = result.detection!.refinedLandmarks;
      final state = LandmarkCorrectionState.fromRefinedLandmarks(refined);

      expect(state.correctedCount, 0);
      expect(
        ReportDisplaySnapshot.formatAnalysisOriginLabel(
          correctionStatus: state.globalStatus,
          correctedLandmarkCount: state.correctedCount,
        ),
        'Analyse : IA',
      );

      expect(state.moveLandmark('ASL_L', 111.0, 222.0), isTrue);
      expect(state.moveLandmark('FSP_R', 333.0, 444.0), isTrue);
      expect(state.correctedCount, 2);
      expect(state.statusOf('ASL_L'), LandmarkStatus.corrected);
      expect(state.statusOf('FSP_R'), LandmarkStatus.corrected);

      expect(
        ReportDisplaySnapshot.formatAnalysisOriginLabel(
          correctionStatus: state.globalStatus,
          correctedLandmarkCount: state.correctedCount,
        ),
        'Analyse : IA + correction manuelle (2)',
      );
    });
  });

  group('STEP F — PDF consumes current display state', () {
    test('1. AI-only PDF uses refinedLandmarks', () async {
      final result = _resultWithCorrectableLandmarks();
      final refined = result.detection!.refinedLandmarks;
      final recorder = _RecordingComposer();
      final builder = ReportPdfBuilder(composer: recorder);

      final display = ReportDisplaySnapshot.fromAnalysisResult(result);
      expect(
        display.landmarks.map((l) => '${l.name}:${l.x},${l.y}'),
        refined.map((l) => '${l.name}:${l.x},${l.y}'),
      );
      expect(display.analysisOriginLabel, 'Analyse : IA');

      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
        display: display,
      );
      expect(_pdfLooksValid(pdf), isTrue);
      expect(recorder.lastLandmarks, isNotNull);
      expect(
        recorder.lastLandmarks!.map((l) => '${l.name}:${l.x},${l.y}'),
        refined.map((l) => '${l.name}:${l.x},${l.y}'),
      );

      // Never raw_landmarks
      final rawAsl = _byName(result.detection!.rawLandmarks, 'ASL_L')!;
      final refinedAsl = _byName(refined, 'ASL_L')!;
      final usedAsl = _byName(recorder.lastLandmarks!, 'ASL_L')!;
      expect(usedAsl.x, refinedAsl.x);
      expect(usedAsl.y, refinedAsl.y);
      expect(usedAsl.x, isNot(rawAsl.x));
      expect(usedAsl.y, isNot(rawAsl.y));
    });

    test('2+8. Corrected PDF uses currentLandmarks, not AI coordinates',
        () async {
      final result = _resultWithCorrectableLandmarks();
      final refined = result.detection!.refinedLandmarks;
      final state = LandmarkCorrectionState.fromRefinedLandmarks(refined);
      final aiAsl = state.originalByName('ASL_L')!;
      expect(state.moveLandmark('ASL_L', 501.5, 602.5), isTrue);

      final corrected = state.currentByName('ASL_L')!;
      expect(corrected.x, 501.5);
      expect(corrected.y, 602.5);
      expect(corrected.x, isNot(aiAsl.x));
      expect(corrected.y, isNot(aiAsl.y));

      final display = ReportDisplaySnapshot.fromCorrectionState(
        result: result,
        correctionState: state,
        displayedMeasurements: result.measurements,
      );
      expect(
        display.landmarks.firstWhere((l) => l.name == 'ASL_L').x,
        501.5,
      );
      expect(
        display.landmarks.firstWhere((l) => l.name == 'ASL_L').y,
        602.5,
      );

      final recorder = _RecordingComposer();
      final builder = ReportPdfBuilder(composer: recorder);
      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
        display: display,
      );
      expect(_pdfLooksValid(pdf), isTrue);

      final overlayAsl =
          recorder.lastLandmarks!.firstWhere((l) => l.name == 'ASL_L');
      expect(overlayAsl.x, 501.5);
      expect(overlayAsl.y, 602.5);
      expect(overlayAsl.x, isNot(aiAsl.x));
      expect(overlayAsl.y, isNot(aiAsl.y));
    });

    test('3. Corrected measurements are passed to PDF', () {
      final result = _resultWithCorrectableLandmarks();
      final original = result.measurements!;
      final updated = _measures(rightVce: 41.2, leftVce: 38.7);
      expect(updated.right.vce.valueDeg, isNot(original.right.vce.valueDeg));

      final state = LandmarkCorrectionState.fromRefinedLandmarks(
        result.detection!.refinedLandmarks,
      );
      expect(state.moveLandmark('ASL_R', 10, 20), isTrue);

      final display = ReportDisplaySnapshot.fromCorrectionState(
        result: result,
        correctionState: state,
        displayedMeasurements: updated,
      );
      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4, 18, 0),
        display: display,
      );

      expect(content.measureValue('right', 'vce'), '41.2°');
      expect(content.measureValue('left', 'vce'), '38.7°');
      expect(content.analysisOriginLabel, 'Analyse : IA + correction manuelle (1)');

      final map = ReportPdfBuilder.measurementDisplayMap(updated);
      expect(map['right.vce'], '41.2°');
      expect(map['left.vce'], '38.7°');
    });

    test('4. AI-only measurements remain unchanged', () {
      final result = _resultWithCorrectableLandmarks();
      final display = ReportDisplaySnapshot.fromAnalysisResult(result);
      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
        display: display,
      );

      expect(content.measureValue('right', 'vce'), '25.0°');
      expect(content.measureValue('right', 'tonnis'), '10.5°');
      expect(content.measureValue('left', 'ccd'), '128.0°');
      expect(content.analysisOriginLabel, 'Analyse : IA');
      expect(display.measurements, same(result.measurements));
    });

    test('6. Reset returns PDF state to AI', () {
      final result = _resultWithCorrectableLandmarks();
      final state = LandmarkCorrectionState.fromRefinedLandmarks(
        result.detection!.refinedLandmarks,
      );
      final original = result.measurements!;
      final updated = _measures(rightVce: 50.0, leftVce: 49.0);

      expect(state.moveLandmark('FSD_L', 1, 2), isTrue);
      expect(state.hasCorrections, isTrue);

      var display = ReportDisplaySnapshot.fromCorrectionState(
        result: result,
        correctionState: state,
        displayedMeasurements: updated,
      );
      expect(display.analysisOriginLabel, contains('correction manuelle'));

      state.reset();
      display = ReportDisplaySnapshot.fromCorrectionState(
        result: result,
        correctionState: state,
        displayedMeasurements: original,
      );

      expect(state.globalStatus, CorrectionSessionStatus.aiOnly);
      expect(state.correctedCount, 0);
      expect(display.analysisOriginLabel, 'Analyse : IA');
      expect(display.measurements!.right.vce.valueDeg, original.right.vce.valueDeg);

      final aiAsl = state.originalByName('ASL_L')!;
      final curAsl = display.landmarks.firstWhere((l) => l.name == 'ASL_L');
      expect(curAsl.x, aiAsl.x);
      expect(curAsl.y, aiAsl.y);

      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
        display: display,
      );
      expect(content.measureValue('right', 'vce'), '25.0°');
      expect(content.analysisOriginLabel, 'Analyse : IA');
    });

    test('7. Undo to AI returns PDF state to AI', () {
      final result = _resultWithCorrectableLandmarks();
      final state = LandmarkCorrectionState.fromRefinedLandmarks(
        result.detection!.refinedLandmarks,
      );
      final original = result.measurements!;
      final updated = _measures(rightVce: 55.0, leftVce: 54.0);

      expect(state.moveLandmark('ASL_L', 900, 901), isTrue);
      expect(state.correctedCount, 1);

      var display = ReportDisplaySnapshot.fromCorrectionState(
        result: result,
        correctionState: state,
        displayedMeasurements: updated,
      );
      expect(display.analysisOriginLabel, 'Analyse : IA + correction manuelle (1)');

      expect(state.undo(), isTrue);
      display = ReportDisplaySnapshot.fromCorrectionState(
        result: result,
        correctionState: state,
        displayedMeasurements: original,
      );

      expect(state.globalStatus, CorrectionSessionStatus.aiOnly);
      expect(display.analysisOriginLabel, 'Analyse : IA');
      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
        display: display,
      );
      expect(content.measureValue('right', 'vce'), '25.0°');
      expect(
        display.landmarks.firstWhere((l) => l.name == 'ASL_L').x,
        state.originalByName('ASL_L')!.x,
      );
    });

    test('9. Existing disclaimer remains unchanged', () {
      const expected =
          'Ce rapport présente des mesures coxométriques issues d\'une analyse '
          'assistée par IA. Les résultats doivent être vérifiés par un '
          'professionnel qualifié et ne constituent pas à eux seuls un diagnostic '
          'médical. Aucune certification de dispositif médical n\'est revendiquée.';
      expect(ReportPdfBuilder.disclaimer, expected);

      final result = _resultWithCorrectableLandmarks();
      final state = LandmarkCorrectionState.fromRefinedLandmarks(
        result.detection!.refinedLandmarks,
      );
      expect(state.moveLandmark('ASL_L', 1, 2), isTrue);
      final content = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4),
        display: ReportDisplaySnapshot.fromCorrectionState(
          result: result,
          correctionState: state,
          displayedMeasurements: result.measurements,
        ),
      );
      expect(content.disclaimer, expected);
      expect(content.disclaimer.toLowerCase(), isNot(contains('dysplas')));
    });

    test('10. Existing PDF layout/content remains compatible', () async {
      final result = _resultWithCorrectableLandmarks();
      final contentAi = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4, 17, 30),
      );
      expect(contentAi.title, 'Rapport d\'analyse coxométrique');
      expect(contentAi.statusTitle, isNotEmpty);
      expect(contentAi.analysisOriginLabel, 'Analyse : IA');
      expect(contentAi.rightMeasures.length, 3);
      expect(contentAi.leftMeasures.length, 3);
      expect(contentAi.itRows, isNotEmpty);
      expect(contentAi.disclaimer, ReportPdfBuilder.disclaimer);

      final builder = ReportPdfBuilder();
      final pdf = await builder.buildPdfBytes(
        radiographBytes: _tinyPng(),
        result: result,
        localImageSize: const Size(1024, 768),
        generatedAt: DateTime(2026, 9, 4, 17, 30),
      );
      expect(_pdfLooksValid(pdf), isTrue);
      expect(pdf.length, greaterThan(500));

      // Corrected path keeps same structure
      final state = LandmarkCorrectionState.fromRefinedLandmarks(
        result.detection!.refinedLandmarks,
      );
      expect(state.moveLandmark('FSP_L', 12, 34), isTrue);
      final contentCorr = ReportContent.fromAnalysis(
        result: result,
        generatedAt: DateTime(2026, 9, 4, 17, 30),
        display: ReportDisplaySnapshot.fromCorrectionState(
          result: result,
          correctionState: state,
          displayedMeasurements: _measures(rightVce: 26.0, leftVce: 31.0),
        ),
      );
      expect(contentCorr.title, contentAi.title);
      expect(contentCorr.statusTitle, contentAi.statusTitle);
      expect(contentCorr.rightMeasures.map((e) => e.key).toList(),
          contentAi.rightMeasures.map((e) => e.key).toList());
      expect(contentCorr.disclaimer, contentAi.disclaimer);
      expect(contentCorr.analysisOriginLabel,
          'Analyse : IA + correction manuelle (1)');
    });
  });
}
