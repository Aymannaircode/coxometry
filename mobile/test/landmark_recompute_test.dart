import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/models/landmark.dart';
import 'package:coxometrie/screens/results_screen.dart';
import 'package:coxometrie/services/api_service.dart';
import 'package:coxometrie/services/radiograph_picker.dart';
import 'package:coxometrie/widgets/landmark_overlay.dart';
import 'package:coxometrie/widgets/measurement_card.dart';
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

Map<String, dynamic> _side(String side, {required double vce}) => {
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

List<Landmark> _landmarks() => const [
      Landmark(name: 'TD_R', x: 50, y: 50),
      Landmark(name: 'TD_L', x: 90, y: 50),
      Landmark(name: 'FHC_R', x: 40, y: 60),
      Landmark(name: 'FHC_L', x: 80, y: 60),
      Landmark(name: 'ASL_L', x: 80, y: 40),
      Landmark(name: 'ASL_R', x: 20, y: 40),
      Landmark(name: 'ASM_R', x: 30, y: 45),
      Landmark(name: 'ASM_L', x: 70, y: 45),
      Landmark(name: 'FNM_R', x: 35, y: 65),
      Landmark(name: 'FNM_L', x: 75, y: 65),
      Landmark(name: 'FSP_L', x: 85, y: 70),
      Landmark(name: 'FSP_R', x: 15, y: 70),
      Landmark(name: 'FSD_L', x: 88, y: 90),
      Landmark(name: 'FSD_R', x: 12, y: 90),
    ];

Map<String, dynamic> _readyJson() {
  final json = v5FullyAvailableJson();
  final detection = json['detection'] as Map<String, dynamic>;
  detection['refined_landmarks'] = [
    for (final lm in _landmarks())
      {'name': lm.name, 'x': lm.x, 'y': lm.y, 'confidence': 0.9},
  ];
  detection['coordinate_space'] = coordinateSpaceJson(
    imageWidth: 100,
    imageHeight: 100,
  );
  return json;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('ResultsScreen measurement recompute', () {
    Future<void> dragAsl(
      WidgetTester tester, {
      double fromX = 80,
      double fromY = 40,
      double toX = 70,
      double toY = 55,
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
      // Avoid pumpAndSettle: recompute may leave an indeterminate progress ticker.
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 50));
    }

    testWidgets('D. no /measurements call on initial display', (tester) async {
      var calls = 0;
      final api = ApiService(
        baseUrl: 'http://example.test',
        httpClient: _FakeClient((request) async {
          calls++;
          fail('unexpected request ${request.url}');
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 't.png',
              width: 100,
              height: 100,
            ),
            result: AnalysisResult.fromJson(_readyJson()),
            apiService: api,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(calls, 0);
      expect(find.text('25.0°'), findsWidgets); // original analyze VCE
    });

    testWidgets('E/A/B one call after drag with corrected image coords',
        (tester) async {
      final bodies = <Map<String, dynamic>>[];
      final api = ApiService(
        baseUrl: 'http://example.test',
        httpClient: _FakeClient((request) async {
          expect(request.url.path, '/measurements');
          expect(request, isA<http.Request>());
          bodies.add(
            jsonDecode((request as http.Request).body) as Map<String, dynamic>,
          );
          return _jsonStreamed({
            'status': 'ok',
            'mode': 'landmarks',
            'source': 'manual_landmarks',
            'sides': {
              'R': _side('R', vce: 18.0),
              'L': _side('L', vce: 27.0),
            },
          });
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 't.png',
              width: 100,
              height: 100,
            ),
            result: AnalysisResult.fromJson(_readyJson()),
            apiService: api,
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(bodies, isEmpty);

      await tester.tap(find.byKey(const Key('toggle_correction_mode_button')));
      await tester.pumpAndSettle();
      await dragAsl(tester, toX: 70, toY: 55);

      expect(bodies, hasLength(1));
      expect(bodies.single['mode'], 'landmarks');
      final landmarks = bodies.single['landmarks'] as List;
      final asl = landmarks.cast<Map>().firstWhere((e) => e['name'] == 'ASL_L');
      expect(asl['x'], closeTo(70, 1.5));
      expect(asl['y'], closeTo(55, 1.5));
      // Display coords for this layout would be different when scale/offset ≠ identity.
      expect(find.text('18.0°'), findsOneWidget);
      expect(find.text('27.0°'), findsOneWidget);
    });

    testWidgets('F. multiple corrections trigger recalculation', (tester) async {
      var calls = 0;
      final api = ApiService(
        baseUrl: 'http://example.test',
        httpClient: _FakeClient((request) async {
          calls++;
          return _jsonStreamed({
            'status': 'ok',
            'mode': 'landmarks',
            'source': 'manual_landmarks',
            'sides': {
              'R': _side('R', vce: 10.0 + calls),
              'L': _side('L', vce: 20.0 + calls),
            },
          });
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 't.png',
              width: 100,
              height: 100,
            ),
            result: AnalysisResult.fromJson(_readyJson()),
            apiService: api,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('toggle_correction_mode_button')));
      await tester.pumpAndSettle();

      await dragAsl(tester, toX: 72, toY: 50);
      expect(calls, 1);
      await dragAsl(tester, fromX: 72, fromY: 50, toX: 68, toY: 52);
      expect(calls, 2);
    });

    testWidgets('H. undo to AI restores original measurements without API',
        (tester) async {
      var calls = 0;
      final api = ApiService(
        baseUrl: 'http://example.test',
        httpClient: _FakeClient((request) async {
          calls++;
          return _jsonStreamed({
            'status': 'ok',
            'mode': 'landmarks',
            'source': 'manual_landmarks',
            'sides': {
              'R': _side('R', vce: 11.0),
              'L': _side('L', vce: 12.0),
            },
          });
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 't.png',
              width: 100,
              height: 100,
            ),
            result: AnalysisResult.fromJson(_readyJson()),
            apiService: api,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('toggle_correction_mode_button')));
      await tester.pumpAndSettle();
      await dragAsl(tester);
      expect(calls, 1);
      expect(find.text('11.0°'), findsOneWidget);

      await tester.ensureVisible(find.byKey(const Key('undo_correction_button')));
      await tester.tap(find.byKey(const Key('undo_correction_button')));
      await tester.pumpAndSettle();

      expect(calls, 1); // no extra API call
      expect(find.text('25.0°'), findsWidgets); // original analyze
      expect(find.text('11.0°'), findsNothing);
    });

    testWidgets('I. reset restores original measurements without /analyze',
        (tester) async {
      var calls = 0;
      final api = ApiService(
        baseUrl: 'http://example.test',
        httpClient: _FakeClient((request) async {
          expect(request.url.path, isNot('/analyze'));
          calls++;
          return _jsonStreamed({
            'status': 'ok',
            'mode': 'landmarks',
            'source': 'manual_landmarks',
            'sides': {
              'R': _side('R', vce: 14.0),
              'L': _side('L', vce: 15.0),
            },
          });
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 't.png',
              width: 100,
              height: 100,
            ),
            result: AnalysisResult.fromJson(_readyJson()),
            apiService: api,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('toggle_correction_mode_button')));
      await tester.pumpAndSettle();
      await dragAsl(tester);
      expect(calls, 1);

      await tester.ensureVisible(find.byKey(const Key('reset_correction_button')));
      await tester.tap(find.byKey(const Key('reset_correction_button')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('reset_correction_confirm')));
      await tester.pumpAndSettle();

      expect(calls, 1);
      expect(find.text('25.0°'), findsWidgets);
      expect(find.text('14.0°'), findsNothing);
    });

    testWidgets('J/K API failure keeps previous measures and landmarks',
        (tester) async {
      var calls = 0;
      final api = ApiService(
        baseUrl: 'http://example.test',
        httpClient: _FakeClient((request) async {
          calls++;
          return _jsonStreamed({'detail': 'boom'}, status: 500);
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 't.png',
              width: 100,
              height: 100,
            ),
            result: AnalysisResult.fromJson(_readyJson()),
            apiService: api,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('toggle_correction_mode_button')));
      await tester.pumpAndSettle();
      await dragAsl(tester, toX: 66, toY: 52);

      expect(calls, 1);
      expect(find.text('25.0°'), findsWidgets); // previous valid
      expect(find.textContaining('Corrigés :'), findsOneWidget);
      final paint = tester.widget<CustomPaint>(
        find.byKey(const Key('landmark_painter')),
      );
      final asl = (paint.painter! as LandmarkPainter)
          .mvpLandmarks
          .firstWhere((l) => l.name == 'ASL_L');
      expect(asl.x, closeTo(66, 1.5));

      final messenger = ScaffoldMessenger.of(
        tester.element(find.byType(ResultsScreen)),
      );
      messenger.clearSnackBars();
      await tester.pump();
    });

    testWidgets('L. stale older response cannot overwrite newer correction',
        (tester) async {
      final first = Completer<http.StreamedResponse>();
      final second = Completer<http.StreamedResponse>();
      var call = 0;

      final api = ApiService(
        baseUrl: 'http://example.test',
        httpClient: _FakeClient((request) async {
          call++;
          if (call == 1) return first.future;
          if (call == 2) return second.future;
          fail('unexpected call $call');
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 't.png',
              width: 100,
              height: 100,
            ),
            result: AnalysisResult.fromJson(_readyJson()),
            apiService: api,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('toggle_correction_mode_button')));
      await tester.pumpAndSettle();

      await dragAsl(tester, toX: 71, toY: 51);
      expect(call, 1);
      await dragAsl(tester, fromX: 71, fromY: 51, toX: 69, toY: 53);
      expect(call, 2);

      // Complete newer request first.
      second.complete(
        _jsonStreamed({
          'status': 'ok',
          'mode': 'landmarks',
          'source': 'manual_landmarks',
          'sides': {
            'R': _side('R', vce: 33.0),
            'L': _side('L', vce: 34.0),
          },
        }),
      );
      await tester.pumpAndSettle();
      expect(find.text('33.0°'), findsOneWidget);

      // Late older response must be ignored.
      first.complete(
        _jsonStreamed({
          'status': 'ok',
          'mode': 'landmarks',
          'source': 'manual_landmarks',
          'sides': {
            'R': _side('R', vce: 1.0),
            'L': _side('L', vce: 2.0),
          },
        }),
      );
      await tester.pumpAndSettle();
      expect(find.text('33.0°'), findsOneWidget);
      expect(find.text('1.0°'), findsNothing);
    });

    testWidgets('M. AI-only measurements unchanged without correction',
        (tester) async {
      var calls = 0;
      final api = ApiService(
        baseUrl: 'http://example.test',
        httpClient: _FakeClient((request) async {
          calls++;
          return _jsonStreamed({
            'status': 'ok',
            'mode': 'landmarks',
            'source': 'manual_landmarks',
            'sides': {
              'R': _side('R', vce: 1),
              'L': _side('L', vce: 2),
            },
          });
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: ResultsScreen(
            radiograph: SelectedRadiograph(
              bytes: _tinyPng(),
              filename: 't.png',
              width: 100,
              height: 100,
            ),
            result: AnalysisResult.fromJson(_readyJson()),
            apiService: api,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('toggle_correction_mode_button')));
      await tester.pumpAndSettle();

      expect(calls, 0);
      expect(find.byType(SideMeasurementsSection), findsNWidgets(2));
      expect(find.text('25.0°'), findsWidgets);
    });
  });
}
