import 'dart:convert';
import 'dart:typed_data';
import 'dart:ui' show Offset, Size;

import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/models/landmark.dart';
import 'package:coxometrie/models/landmark_correction_state.dart';
import 'package:coxometrie/screens/results_screen.dart';
import 'package:coxometrie/services/api_service.dart';
import 'package:coxometrie/services/radiograph_picker.dart';
import 'package:coxometrie/widgets/image_contain_layout.dart';
import 'package:coxometrie/widgets/landmark_hit_test.dart';
import 'package:coxometrie/widgets/landmark_overlay.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'fixtures/analysis_fixtures.dart';

Uint8List _tinyPng() {
  return Uint8List.fromList(
    base64Decode(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
    ),
  );
}

Widget _wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

class _FakeClient extends http.BaseClient {
  _FakeClient(this._handler);
  final Future<http.StreamedResponse> Function(http.BaseRequest request) _handler;
  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) => _handler(request);
}

http.StreamedResponse _jsonStreamed(Map<String, dynamic> body, {int status = 200}) {
  final bytes = utf8.encode(jsonEncode(body));
  return http.StreamedResponse(
    Stream<List<int>>.fromIterable([bytes]),
    status,
    headers: {'content-type': 'application/json'},
  );
}

Map<String, dynamic> _sideOut(String side, {required double vce}) => {
      'side': side,
      'vce': {
        'name': 'VCE',
        'side': side,
        'value_deg': vce,
        'available': true,
        'reason': null,
      },
      'tonnis': {
        'name': 'Tönnis',
        'side': side,
        'value_deg': 10.0,
        'available': true,
        'reason': null,
      },
      'ccd': {
        'name': 'CCD',
        'side': side,
        'value_deg': 130.0,
        'available': true,
        'reason': null,
      },
    };

ApiService _measurementsApi({
  double rightVce = 19.5,
  void Function(http.BaseRequest request)? onRequest,
}) {
  return ApiService(
    baseUrl: 'http://example.test',
    httpClient: _FakeClient((request) async {
      onRequest?.call(request);
      return _jsonStreamed({
        'status': 'ok',
        'mode': 'landmarks',
        'source': 'manual_landmarks',
        'sides': {
          'R': _sideOut('R', vce: rightVce),
          'L': _sideOut('L', vce: 28.0),
        },
      });
    }),
  );
}

List<Landmark> _correctableSet() {
  return const [
    Landmark(name: 'TD_R', x: 50, y: 50, confidence: 0.9),
    Landmark(name: 'ASL_L', x: 80, y: 40, confidence: 0.9),
    Landmark(name: 'ASL_R', x: 20, y: 40, confidence: 0.9),
    Landmark(name: 'FSP_L', x: 85, y: 70, confidence: 0.9),
    Landmark(name: 'FSP_R', x: 15, y: 70, confidence: 0.9),
    Landmark(name: 'FSD_L', x: 88, y: 90, confidence: 0.9),
    Landmark(name: 'FSD_R', x: 12, y: 90, confidence: 0.9),
  ];
}

Map<String, dynamic> _correctionReadyJson() {
  final json = v5FullyAvailableJson();
  final detection = json['detection'] as Map<String, dynamic>;
  detection['refined_landmarks'] = [
    for (final lm in _correctableSet())
      {
        'name': lm.name,
        'x': lm.x,
        'y': lm.y,
        'confidence': lm.confidence,
      },
  ];
  detection['coordinate_space'] = coordinateSpaceJson(
    imageWidth: 100,
    imageHeight: 100,
  );
  return json;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('landmark hit test helpers', () {
    test('selects correctable landmark and ignores non-editable', () {
      final layout = ImageContainLayout.compute(
        boxSize: const Size(200, 200),
        imageSize: const Size(100, 100),
      );
      final landmarks = _correctableSet();

      final aslDisplay = layout.toDisplay(80, 40);
      expect(
        findCorrectableLandmarkAt(
          localDisplay: aslDisplay,
          landmarks: landmarks,
          layout: layout,
        ),
        'ASL_L',
      );

      final tdDisplay = layout.toDisplay(50, 50);
      expect(
        findCorrectableLandmarkAt(
          localDisplay: tdDisplay,
          landmarks: landmarks,
          layout: layout,
        ),
        isNull,
      );
    });

    test('localDisplayToImage uses original_image_pixels', () {
      final layout = ImageContainLayout.compute(
        boxSize: const Size(200, 100),
        imageSize: const Size(100, 100),
      );
      final display = layout.toDisplay(80, 40);
      final image = localDisplayToImage(layout, display);
      expect(image.dx, closeTo(80, 1e-9));
      expect(image.dy, closeTo(40, 1e-9));
      expect(image.dx, isNot(closeTo(display.dx, 1e-6)));
    });
  });

  group('LandmarkOverlay correction mode', () {
    testWidgets('outside correction mode keeps InteractiveViewer pan/zoom',
        (tester) async {
      await tester.pumpWidget(
        _wrap(
          LandmarkOverlay(
            bytes: _tinyPng(),
            imageSize: const Size(100, 100),
            height: 200,
            landmarks: _correctableSet(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('landmark_correction_listener')), findsNothing);
      final viewer = tester.widget<InteractiveViewer>(
        find.byKey(const Key('landmark_interactive_viewer')),
      );
      expect(viewer.panEnabled, isTrue);
      expect(viewer.scaleEnabled, isTrue);
    });

    testWidgets('correction mode disables pan/zoom and enables listener',
        (tester) async {
      await tester.pumpWidget(
        _wrap(
          LandmarkOverlay(
            bytes: _tinyPng(),
            imageSize: const Size(100, 100),
            height: 200,
            landmarks: _correctableSet(),
            correctionMode: true,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('landmark_correction_listener')), findsOneWidget);
      final viewer = tester.widget<InteractiveViewer>(
        find.byKey(const Key('landmark_interactive_viewer')),
      );
      expect(viewer.panEnabled, isFalse);
      expect(viewer.scaleEnabled, isFalse);
    });

    testWidgets('drag updates current landmark via image coordinates',
        (tester) async {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_correctableSet());
      String? selected;
      final originalAsl = state.originalByName('ASL_L')!;

      await tester.pumpWidget(
        _wrap(
          StatefulBuilder(
            builder: (context, setLocal) {
              return LandmarkOverlay(
                key: const Key('correction_overlay'),
                bytes: _tinyPng(),
                imageSize: const Size(100, 100),
                height: 200,
                landmarks: state.currentLandmarks,
                correctionMode: true,
                landmarkStatuses: {
                  for (final lm in state.currentLandmarks)
                    lm.name: state.statusOf(lm.name),
                },
                selectedLandmarkName: selected,
                onSelectedLandmarkChanged: (name) {
                  selected = name;
                  setLocal(() {});
                },
                onLandmarkEditBegin: (name) {
                  state.beginLandmarkEdit(name);
                },
                onLandmarkDrag: (name, x, y) {
                  state.updateLandmarkPosition(name, x, y);
                  setLocal(() {});
                },
              );
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      final overlayState = tester.state<LandmarkOverlayState>(
        find.byKey(const Key('correction_overlay')),
      );
      final layout = overlayState.lastLayout!;
      expect(overlayState.hitTestLocal(layout.toDisplay(80, 40)), 'ASL_L');

      selected = 'ASL_L';
      state.beginLandmarkEdit('ASL_L');
      final targetDisplay = layout.toDisplay(70, 55);
      expect(
        overlayState.applyDragToLocalDisplay(targetDisplay, name: 'ASL_L'),
        isTrue,
      );
      await tester.pump();

      expect(state.currentByName('ASL_L')!.x, closeTo(70, 1e-6));
      expect(state.currentByName('ASL_L')!.y, closeTo(55, 1e-6));
      expect(state.statusOf('ASL_L'), LandmarkStatus.corrected);
      expect(state.originalByName('ASL_L')!.x, originalAsl.x);
      expect(state.originalByName('ASL_L')!.y, originalAsl.y);
      expect(state.originalByName('ASL_L')!.x, isNot(70));
    });

    testWidgets('pointer drag on ASL_L converts display to image coords',
        (tester) async {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_correctableSet());

      await tester.binding.setSurfaceSize(const Size(400, 600));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        _wrap(
          SizedBox(
            width: 200,
            height: 200,
            child: StatefulBuilder(
              builder: (context, setLocal) {
                return LandmarkOverlay(
                  key: const Key('pointer_drag_overlay'),
                  bytes: _tinyPng(),
                  imageSize: const Size(100, 100),
                  height: 200,
                  landmarks: state.currentLandmarks,
                  correctionMode: true,
                  landmarkStatuses: {
                    for (final lm in state.currentLandmarks)
                      lm.name: state.statusOf(lm.name),
                  },
                  onLandmarkEditBegin: state.beginLandmarkEdit,
                  onLandmarkDrag: (name, x, y) {
                    state.updateLandmarkPosition(name, x, y);
                    setLocal(() {});
                  },
                );
              },
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final overlayState = tester.state<LandmarkOverlayState>(
        find.byKey(const Key('pointer_drag_overlay')),
      );
      final layout = overlayState.lastLayout!;
      final start = layout.toDisplay(80, 40);
      final end = layout.toDisplay(65, 50);

      // Convert layout-local points to global for the gesture.
      final listener = find.byKey(const Key('landmark_correction_listener'));
      final topLeft = tester.getTopLeft(listener);
      final startGlobal = topLeft + start;
      final endGlobal = topLeft + end;

      final gesture = await tester.startGesture(startGlobal);
      await tester.pump();
      await gesture.moveTo(endGlobal);
      await tester.pump();
      await gesture.up();
      await tester.pump();

      expect(state.statusOf('ASL_L'), LandmarkStatus.corrected);
      expect(state.currentByName('ASL_L')!.x, closeTo(65, 1.5));
      expect(state.currentByName('ASL_L')!.y, closeTo(50, 1.5));
      expect(state.originalByName('ASL_L')!.x, 80);
      expect(state.originalByName('ASL_L')!.y, 40);
    });

    testWidgets('non-editable landmark cannot be selected for drag',
        (tester) async {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_correctableSet());

      await tester.pumpWidget(
        _wrap(
          LandmarkOverlay(
            key: const Key('correction_overlay_td'),
            bytes: _tinyPng(),
            imageSize: const Size(100, 100),
            height: 200,
            landmarks: state.currentLandmarks,
            correctionMode: true,
            onLandmarkDrag: (name, x, y) {
              state.updateLandmarkPosition(name, x, y);
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      final overlayState = tester.state<LandmarkOverlayState>(
        find.byKey(const Key('correction_overlay_td')),
      );
      final layout = overlayState.lastLayout!;
      final tdDisplay = layout.toDisplay(50, 50);
      expect(overlayState.hitTestLocal(tdDisplay), isNull);
      expect(state.moveLandmark('TD_R', 1, 1), isFalse);
      expect(state.currentByName('TD_R')!.x, 50);
      expect(state.statusOf('TD_R'), LandmarkStatus.ai);
    });
  });

  group('ResultsScreen correction UI', () {
    Future<void> pumpCorrectionScreen(WidgetTester tester) async {
      final result = AnalysisResult.fromJson(_correctionReadyJson());
      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 'test.png',
              width: 100,
              height: 100,
            ),
            result: result,
            apiService: _measurementsApi(),
          ),
        ),
      );
      await tester.pumpAndSettle();
    }

    Future<void> enterCorrectionMode(WidgetTester tester) async {
      await tester.tap(find.byKey(const Key('toggle_correction_mode_button')));
      await tester.pumpAndSettle();
    }

    Future<void> dragLandmarkOnResults(
      WidgetTester tester, {
      required double fromX,
      required double fromY,
      required double toX,
      required double toY,
    }) async {
      final overlayState = tester.state<LandmarkOverlayState>(
        find.byKey(const Key('results_landmark_overlay')),
      );
      final layout = overlayState.lastLayout!;
      final listener = find.byKey(const Key('landmark_correction_listener'));
      await tester.ensureVisible(listener);
      final topLeft = tester.getTopLeft(listener);
      final start = topLeft + layout.toDisplay(fromX, fromY);
      final end = topLeft + layout.toDisplay(toX, toY);
      final gesture = await tester.startGesture(start);
      await tester.pump();
      await gesture.moveTo(end);
      await tester.pump();
      await gesture.up();
      await tester.pumpAndSettle();
    }

    Landmark _painterLandmark(WidgetTester tester, String name) {
      final paint = tester.widget<CustomPaint>(
        find.byKey(const Key('landmark_painter')),
      );
      final painter = paint.painter! as LandmarkPainter;
      return painter.mvpLandmarks.firstWhere((l) => l.name == name);
    }

    testWidgets('activates and deactivates correction mode', (tester) async {
      await pumpCorrectionScreen(tester);

      expect(find.byKey(const Key('toggle_correction_mode_button')), findsOneWidget);
      expect(find.text('Corriger les landmarks'), findsOneWidget);
      expect(find.byKey(const Key('correction_status_bar')), findsNothing);
      expect(find.byKey(const Key('correction_mode_hint')), findsNothing);

      final viewerBefore = tester.widget<InteractiveViewer>(
        find.byKey(const Key('landmark_interactive_viewer')),
      );
      expect(viewerBefore.panEnabled, isTrue);

      await enterCorrectionMode(tester);

      expect(find.text('Terminer la correction'), findsOneWidget);
      expect(find.byKey(const Key('correction_status_bar')), findsOneWidget);
      expect(find.byKey(const Key('correction_mode_hint')), findsOneWidget);
      expect(find.byKey(const Key('landmark_correction_listener')), findsOneWidget);
      expect(find.byKey(const Key('undo_correction_button')), findsOneWidget);
      expect(find.byKey(const Key('reset_correction_button')), findsOneWidget);

      final undoBtn = tester.widget<OutlinedButton>(
        find.byKey(const Key('undo_correction_button')),
      );
      final resetBtn = tester.widget<OutlinedButton>(
        find.byKey(const Key('reset_correction_button')),
      );
      expect(undoBtn.onPressed, isNull);
      expect(resetBtn.onPressed, isNull);

      final viewerDuring = tester.widget<InteractiveViewer>(
        find.byKey(const Key('landmark_interactive_viewer')),
      );
      expect(viewerDuring.panEnabled, isFalse);
      expect(viewerDuring.scaleEnabled, isFalse);

      await tester.tap(find.byKey(const Key('toggle_correction_mode_button')));
      await tester.pumpAndSettle();

      expect(find.text('Corriger les landmarks'), findsOneWidget);
      expect(find.byKey(const Key('correction_status_bar')), findsNothing);
      expect(find.byKey(const Key('undo_correction_button')), findsNothing);
      final viewerAfter = tester.widget<InteractiveViewer>(
        find.byKey(const Key('landmark_interactive_viewer')),
      );
      expect(viewerAfter.panEnabled, isTrue);
      expect(viewerAfter.scaleEnabled, isTrue);
    });

    testWidgets('undo restores coordinates, status and global AI_ONLY',
        (tester) async {
      await pumpCorrectionScreen(tester);
      await enterCorrectionMode(tester);

      await dragLandmarkOnResults(
        tester,
        fromX: 80,
        fromY: 40,
        toX: 70,
        toY: 55,
      );

      expect(_painterLandmark(tester, 'ASL_L').x, closeTo(70, 1.5));
      expect(find.textContaining('Corrigés :'), findsOneWidget);
      expect(
        tester.widget<OutlinedButton>(
          find.byKey(const Key('undo_correction_button')),
        ).onPressed,
        isNotNull,
      );

      await tester.ensureVisible(find.byKey(const Key('undo_correction_button')));
      await tester.tap(find.byKey(const Key('undo_correction_button')));
      await tester.pumpAndSettle();

      expect(_painterLandmark(tester, 'ASL_L').x, closeTo(80, 1e-6));
      expect(_painterLandmark(tester, 'ASL_L').y, closeTo(40, 1e-6));
      expect(find.textContaining('IA uniquement'), findsOneWidget);
      expect(
        tester.widget<OutlinedButton>(
          find.byKey(const Key('undo_correction_button')),
        ).onPressed,
        isNull,
      );
    });

    testWidgets('multiple undo levels restore intermediate states',
        (tester) async {
      await pumpCorrectionScreen(tester);
      await enterCorrectionMode(tester);

      await dragLandmarkOnResults(
        tester,
        fromX: 80,
        fromY: 40,
        toX: 75,
        toY: 45,
      );
      await dragLandmarkOnResults(
        tester,
        fromX: 20,
        fromY: 40,
        toX: 25,
        toY: 48,
      );

      expect(_painterLandmark(tester, 'ASL_L').x, closeTo(75, 1.5));
      expect(_painterLandmark(tester, 'ASL_R').x, closeTo(25, 1.5));
      expect(find.textContaining('Corrigés : 2'), findsOneWidget);

      await tester.ensureVisible(find.byKey(const Key('undo_correction_button')));
      await tester.tap(find.byKey(const Key('undo_correction_button')));
      await tester.pumpAndSettle();

      expect(_painterLandmark(tester, 'ASL_R').x, closeTo(20, 1e-6));
      expect(_painterLandmark(tester, 'ASL_L').x, closeTo(75, 1.5));
      expect(find.textContaining('Corrigés : 1'), findsOneWidget);

      await tester.tap(find.byKey(const Key('undo_correction_button')));
      await tester.pumpAndSettle();

      expect(_painterLandmark(tester, 'ASL_L').x, closeTo(80, 1e-6));
      expect(find.textContaining('IA uniquement'), findsOneWidget);
    });

    testWidgets('empty undo history keeps Annuler disabled (no-op)',
        (tester) async {
      await pumpCorrectionScreen(tester);
      await enterCorrectionMode(tester);

      final undoFinder = find.byKey(const Key('undo_correction_button'));
      expect(tester.widget<OutlinedButton>(undoFinder).onPressed, isNull);
      expect(_painterLandmark(tester, 'ASL_L').x, 80);
      expect(find.textContaining('IA uniquement'), findsOneWidget);
    });

    testWidgets('reset restores AI originals, statuses, clears undo',
        (tester) async {
      await pumpCorrectionScreen(tester);
      await enterCorrectionMode(tester);

      await dragLandmarkOnResults(
        tester,
        fromX: 80,
        fromY: 40,
        toX: 60,
        toY: 50,
      );
      await dragLandmarkOnResults(
        tester,
        fromX: 85,
        fromY: 70,
        toX: 90,
        toY: 72,
      );

      expect(find.textContaining('Corrigés : 2'), findsOneWidget);
      expect(
        tester.widget<OutlinedButton>(
          find.byKey(const Key('reset_correction_button')),
        ).onPressed,
        isNotNull,
      );

      await tester.ensureVisible(find.byKey(const Key('reset_correction_button')));
      await tester.tap(find.byKey(const Key('reset_correction_button')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('reset_correction_dialog')), findsOneWidget);
      await tester.tap(find.byKey(const Key('reset_correction_confirm')));
      await tester.pumpAndSettle();

      expect(_painterLandmark(tester, 'ASL_L').x, closeTo(80, 1e-6));
      expect(_painterLandmark(tester, 'ASL_L').y, closeTo(40, 1e-6));
      expect(_painterLandmark(tester, 'FSP_L').x, closeTo(85, 1e-6));
      expect(find.textContaining('IA uniquement'), findsOneWidget);
      expect(
        tester.widget<OutlinedButton>(
          find.byKey(const Key('undo_correction_button')),
        ).onPressed,
        isNull,
      );
      expect(
        tester.widget<OutlinedButton>(
          find.byKey(const Key('reset_correction_button')),
        ).onPressed,
        isNull,
      );
      // Still on results — no inference / navigation.
      expect(find.byKey(const Key('results_screen')), findsOneWidget);
      expect(find.byKey(const Key('analysis_loading_message')), findsNothing);
    });

    testWidgets('reset dialog dismiss leaves corrections intact',
        (tester) async {
      await pumpCorrectionScreen(tester);
      await enterCorrectionMode(tester);
      await dragLandmarkOnResults(
        tester,
        fromX: 80,
        fromY: 40,
        toX: 66,
        toY: 52,
      );

      await tester.ensureVisible(find.byKey(const Key('reset_correction_button')));
      await tester.tap(find.byKey(const Key('reset_correction_button')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('reset_correction_dismiss')));
      await tester.pumpAndSettle();

      expect(_painterLandmark(tester, 'ASL_L').x, closeTo(66, 1.5));
      expect(find.textContaining('Corrigés : 1'), findsOneWidget);
      expect(find.byKey(const Key('reset_correction_dialog')), findsNothing);
    });

    testWidgets('without correctable landmarks hides correction button',
        (tester) async {
      // Default V5 fixture only has TD_R / TD_L — not in correctable set.
      final result = AnalysisResult.fromJson(v5FullyAvailableJson());
      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 'test.png',
              width: 1024,
              height: 768,
            ),
            result: result,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('toggle_correction_mode_button')), findsNothing);
      expect(find.byKey(const Key('landmark_interactive_viewer')), findsOneWidget);
      final viewer = tester.widget<InteractiveViewer>(
        find.byKey(const Key('landmark_interactive_viewer')),
      );
      expect(viewer.panEnabled, isTrue);
    });
  });
}

