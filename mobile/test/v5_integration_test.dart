import 'dart:convert';
import 'dart:typed_data';

import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/models/coordinate_space.dart';
import 'package:coxometrie/models/it_landmark.dart';
import 'package:coxometrie/models/landmark.dart';
import 'package:coxometrie/screens/results_screen.dart';
import 'package:coxometrie/services/radiograph_picker.dart';
import 'package:coxometrie/utils/model_version_label.dart';
import 'package:coxometrie/utils/overlay_image_size.dart';
import 'package:coxometrie/widgets/landmark_overlay.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'fixtures/analysis_fixtures.dart';

Uint8List _tinyPng() {
  return Uint8List.fromList(
    base64Decode(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
    ),
  );
}

void main() {
  group('V2 response parsing', () {
    test('parses V2 with empty it_landmarks', () {
      final result = AnalysisResult.fromJson(v2SuccessJson());
      expect(result.isOk, isTrue);
      expect(result.modelVersion, 'v2');
      expect(result.detection!.itLandmarks, isEmpty);
      expect(result.detection!.coordinateSpace, isNull);
    });

    test('V2 backward compatible without model_version', () {
      final json = v2SuccessJson();
      json.remove('model_version');
      final result = AnalysisResult.fromJson(json);
      expect(result.modelVersion, isNull);
      expect(result.detection!.itLandmarks, isEmpty);
    });
  });

  group('V5 response parsing', () {
    test('parses model_version v5_phase2', () {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      expect(result.modelVersion, 'v5_phase2');
      expect(result.isV5Phase2, isTrue);
    });

    test('parses coordinate_space', () {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      final cs = result.detection!.coordinateSpace!;
      expect(cs.imageWidth, 1024);
      expect(cs.imageHeight, 768);
      expect(cs.isOriginalImagePixels, isTrue);
    });

    test('parses IT_R', () {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      final itR = result.detection!.itLandmarks
          .firstWhere((l) => l.name == 'IT_R');
      expect(itR.kpIndex, 14);
      expect(itR.x, 320.0);
      expect(itR.y, 480.0);
      expect(itR.confidence, 0.82);
      expect(itR.isAccept, isTrue);
      expect(itR.isDrawable, isTrue);
    });

    test('parses IT_L', () {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      final itL = result.detection!.itLandmarks
          .firstWhere((l) => l.name == 'IT_L');
      expect(itL.kpIndex, 15);
      expect(itL.x, 680.0);
      expect(itL.isAccept, isTrue);
    });

    test('parses ACCEPT quality', () {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      for (final it in result.detection!.itLandmarks) {
        expect(it.quality, ITQuality.accept);
        expect(it.isAccept, isTrue);
      }
    });

    test('parses REVIEW quality with reasons', () {
      final result = AnalysisResult.fromJson(v5SuccessJson(
        itRQuality: 'review',
        itRReasons: ['high_confidence_marginal_it_fsd'],
      ));
      final itR = result.detection!.itLandmarks
          .firstWhere((l) => l.name == 'IT_R');
      expect(itR.isReview, isTrue);
      expect(itR.primaryQualityReason, 'high_confidence_marginal_it_fsd');
      expect(itR.isDrawable, isTrue);
    });

    test('parses UNAVAILABLE quality', () {
      final json = v5SuccessJson(
        itRQuality: 'unavailable',
        itRReasons: ['low_model_confidence'],
      );
      final itList = (json['detection'] as Map)['it_landmarks'] as List;
      final itRMap = itList[0] as Map<String, dynamic>;
      itRMap['v'] = 0;
      itRMap['x'] = null;
      itRMap['y'] = null;

      final result = AnalysisResult.fromJson(json);
      final itR = result.detection!.itLandmarks
          .firstWhere((l) => l.name == 'IT_R');
      expect(itR.isUnavailable, isTrue);
      expect(itR.isDrawable, isFalse);
    });
  });

  group('coordinate mapping', () {
    test('resolveOverlayImageSize prefers coordinate_space', () {
      final cs = CoordinateSpace.fromJson(coordinateSpaceJson());
      final resolved = resolveOverlayImageSize(
        coordinateSpace: cs,
        localSize: const Size(1024, 768),
      );
      expect(resolved.size.width, 1024);
      expect(resolved.size.height, 768);
      expect(resolved.dimensionMismatch, isFalse);
    });

    test('coordinate_space mismatch detected', () {
      final cs = CoordinateSpace.fromJson(coordinateSpaceJson());
      final resolved = resolveOverlayImageSize(
        coordinateSpace: cs,
        localSize: const Size(800, 600),
      );
      expect(resolved.dimensionMismatch, isTrue);
      expect(resolved.mismatchDetail, isNotNull);
      expect(resolved.size.width, 1024);
    });

    test('falls back to local size without coordinate_space', () {
      final resolved = resolveOverlayImageSize(
        localSize: const Size(640, 480),
      );
      expect(resolved.size, const Size(640, 480));
      expect(resolved.dimensionMismatch, isFalse);
    });
  });

  group('v=0 does not display marker', () {
    test('ITLandmark v=0 is not drawable', () {
      const it = ITLandmark(
        name: 'IT_R',
        kpIndex: 14,
        v: 0,
        x: null,
        y: null,
        quality: ITQuality.unavailable,
      );
      expect(it.isDrawable, isFalse);
    });

    testWidgets('overlay excludes v=0 IT landmarks', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: LandmarkOverlay(
              bytes: _tinyPng(),
              imageSize: const Size(100, 100),
              itLandmarks: const [
                ITLandmark(
                  name: 'IT_R',
                  kpIndex: 14,
                  v: 0,
                  quality: ITQuality.unavailable,
                ),
                ITLandmark(
                  name: 'IT_L',
                  kpIndex: 15,
                  v: 2,
                  x: 50,
                  y: 50,
                  quality: ITQuality.accept,
                ),
              ],
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final paint = tester.widget<CustomPaint>(
        find.byKey(const Key('landmark_painter')),
      );
      final painter = paint.painter! as LandmarkPainter;
      expect(painter.itLandmarks, hasLength(1));
      expect(painter.itLandmarks.single.name, 'IT_L');
    });
  });

  group('model version label', () {
    test('formatModelVersion maps v5_phase2', () {
      expect(formatModelVersion('v5_phase2'), 'V5 Phase 2');
    });

    test('formatModelVersion maps v2', () {
      expect(formatModelVersion('v2'), 'V2');
    });
  });

  group('Results screen renders V5 data', () {
    testWidgets('shows model version, IT section, and overlay', (tester) async {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      final radiograph = SelectedRadiograph(
        bytes: _tinyPng(),
        filename: 'test.png',
        width: 1024,
        height: 768,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: radiograph,
            result: result,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('results_screen')), findsOneWidget);
      expect(find.byKey(const Key('model_version_label')), findsOneWidget);
      expect(find.text('Modèle : V5 Phase 2'), findsOneWidget);
      expect(find.byKey(const Key('it_status_IT_L')), findsOneWidget);
      expect(find.byKey(const Key('it_status_IT_R')), findsOneWidget);
      expect(find.byKey(const Key('it_quality_accept')), findsNWidgets(2));
      expect(find.byKey(const Key('landmark_painter')), findsOneWidget);
      expect(find.byKey(const Key('landmark_interactive_viewer')), findsOneWidget);
      expect(find.byKey(const Key('landmark_legend')), findsOneWidget);
      // Fixture has unavailable left Tönnis → honest partial status.
      expect(find.byKey(const Key('results_status_incomplete')), findsOneWidget);
      expect(find.byKey(const Key('detection_section')), findsOneWidget);
      expect(find.text('BBox'), findsNothing);
    });

    testWidgets('shows success status when all measures available', (tester) async {
      final result = AnalysisResult.fromJson(v5FullyAvailableJson());
      final radiograph = SelectedRadiograph(
        bytes: _tinyPng(),
        filename: 'test.png',
        width: 1024,
        height: 768,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: radiograph,
            result: result,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('results_status_success')), findsOneWidget);
      expect(find.text('Analyse terminée'), findsOneWidget);
    });

    testWidgets('shows REVIEW badge for IT_R', (tester) async {
      final result = AnalysisResult.fromJson(v5SuccessJson(
        itRQuality: 'review',
        itRReasons: ['high_confidence_marginal_it_fsd'],
      ));
      final radiograph = SelectedRadiograph(
        bytes: _tinyPng(),
        filename: 'test.png',
        width: 1024,
        height: 768,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: radiograph,
            result: result,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('it_quality_review')), findsOneWidget);
      expect(find.byKey(const Key('results_status_review')), findsOneWidget);
      expect(find.text('Vérification recommandée'), findsOneWidget);
      expect(
        find.textContaining('Motif de vérification'),
        findsOneWidget,
      );
      expect(
        find.textContaining(
          'Confiance élevée mais position IT–diaphyse marginale',
        ),
        findsOneWidget,
      );
      expect(
        find.textContaining('high_confidence_marginal_it_fsd'),
        findsNothing,
      );
    });

    testWidgets('expands technical detection details on demand', (tester) async {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      final radiograph = SelectedRadiograph(
        bytes: _tinyPng(),
        filename: 'test.png',
        width: 1024,
        height: 768,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: radiograph,
            result: result,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('BBox'), findsNothing);
      await tester.scrollUntilVisible(
        find.byKey(const Key('detection_expansion_tile')),
        200,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.tap(find.byKey(const Key('detection_expansion_tile')));
      await tester.pumpAndSettle();
      expect(find.text('BBox'), findsOneWidget);
    });

    testWidgets('V2 hides IT section', (tester) async {
      final result = AnalysisResult.fromJson(v2SuccessJson());
      final radiograph = SelectedRadiograph(
        bytes: _tinyPng(),
        filename: 'test.png',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: radiograph,
            result: result,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Modèle : V2'), findsOneWidget);
      expect(find.byKey(const Key('it_status_IT_R')), findsNothing);
      expect(find.byKey(const Key('results_status_incomplete')), findsOneWidget);
    });

    testWidgets('shows dimension mismatch banner', (tester) async {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      final radiograph = SelectedRadiograph(
        bytes: _tinyPng(),
        filename: 'test.png',
        width: 800,
        height: 600,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: radiograph,
            result: result,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('dimension_mismatch_banner')), findsOneWidget);
    });

    testWidgets('renders without overflow on narrow width', (tester) async {
      await tester.binding.setSurfaceSize(const Size(320, 640));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      final result = AnalysisResult.fromJson(v5SuccessJson());
      final radiograph = SelectedRadiograph(
        bytes: _tinyPng(),
        filename: 'test.png',
        width: 1024,
        height: 768,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: radiograph,
            result: result,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.byKey(const Key('results_screen')), findsOneWidget);
    });
  });
}
