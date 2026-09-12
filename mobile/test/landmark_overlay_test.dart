import 'dart:convert';
import 'dart:typed_data';
import 'dart:ui' show Size, Offset;

import 'package:coxometrie/models/it_landmark.dart';
import 'package:coxometrie/models/landmark.dart';
import 'package:coxometrie/widgets/image_contain_layout.dart';
import 'package:coxometrie/widgets/landmark_overlay.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

Uint8List _tinyPng() {
  return Uint8List.fromList(
    base64Decode(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
    ),
  );
}

Widget _wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  group('Landmark coordinate mapping', () {
    test('ImageContainLayout maps image center to widget center', () {
      final layout = ImageContainLayout.compute(
        boxSize: const Size(200, 100),
        imageSize: const Size(100, 100),
      );
      expect(layout.scale, 1.0);
      expect(layout.offset, const Offset(50, 0));
      expect(layout.toDisplay(50, 50), const Offset(100, 50));
    });

    test('scales uniformly when box is smaller than image', () {
      final layout = ImageContainLayout.compute(
        boxSize: const Size(100, 50),
        imageSize: const Size(200, 200),
      );
      expect(layout.scale, 0.25);
      expect(layout.toDisplay(200, 200), const Offset(75, 50));
    });
  });

  group('LandmarkOverlay widget', () {
    testWidgets('image with landmarks paints overlay', (tester) async {
      await tester.pumpWidget(
        _wrap(
          LandmarkOverlay(
            bytes: _tinyPng(),
            imageSize: const Size(100, 100),
            landmarks: const [
              Landmark(name: 'TD_R', x: 50, y: 50),
            ],
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('landmark_painter')), findsOneWidget);
      final paint = tester.widget<CustomPaint>(
        find.byKey(const Key('landmark_painter')),
      );
      final painter = paint.painter! as LandmarkPainter;
      expect(painter.mvpLandmarks.single.name, 'TD_R');
    });

    testWidgets('coordinates adapted to contain layout', (tester) async {
      await tester.binding.setSurfaceSize(const Size(200, 400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        _wrap(
          SizedBox(
            width: 200,
            height: 100,
            child: LandmarkOverlay(
              bytes: _tinyPng(),
              imageSize: const Size(100, 100),
              height: 100,
              landmarks: const [
                Landmark(name: 'C', x: 50, y: 50),
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
      final display = painter.layout.toDisplay(50, 50);
      expect(display.dx, closeTo(100, 0.01));
      expect(display.dy, closeTo(50, 0.01));
    });

    testWidgets('invalid coordinates ignored without crash', (tester) async {
      await tester.pumpWidget(
        _wrap(
          LandmarkOverlay(
            bytes: _tinyPng(),
            imageSize: const Size(100, 100),
            landmarks: const [
              Landmark(name: 'bad', x: null, y: null),
              Landmark(name: 'hidden', x: 5, y: 5, visibility: 0),
              Landmark(name: 'ok', x: 10, y: 10),
            ],
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      final paint = tester.widget<CustomPaint>(
        find.byKey(const Key('landmark_painter')),
      );
      expect((paint.painter! as LandmarkPainter).mvpLandmarks, hasLength(1));
    });

    testWidgets('16 landmarks: 14 MVP + 2 IT painted', (tester) async {
      final mvp = List.generate(
        14,
        (i) => Landmark(name: 'KP_$i', x: 10.0 + i, y: 20.0 + i),
      );
      const itLandmarks = [
        ITLandmark(
          name: 'IT_R',
          kpIndex: 14,
          v: 2,
          x: 50,
          y: 50,
          quality: ITQuality.accept,
        ),
        ITLandmark(
          name: 'IT_L',
          kpIndex: 15,
          v: 2,
          x: 60,
          y: 60,
          quality: ITQuality.review,
        ),
      ];

      await tester.pumpWidget(
        _wrap(
          LandmarkOverlay(
            bytes: _tinyPng(),
            imageSize: const Size(100, 100),
            landmarks: mvp,
            itLandmarks: itLandmarks,
          ),
        ),
      );
      await tester.pumpAndSettle();

      final paint = tester.widget<CustomPaint>(
        find.byKey(const Key('landmark_painter')),
      );
      final painter = paint.painter! as LandmarkPainter;
      expect(painter.mvpLandmarks, hasLength(14));
      expect(painter.itLandmarks, hasLength(2));
    });

    testWidgets('IT unavailable excluded from painter', (tester) async {
      await tester.pumpWidget(
        _wrap(
          LandmarkOverlay(
            bytes: _tinyPng(),
            imageSize: const Size(100, 100),
            itLandmarks: const [
              ITLandmark(
                name: 'IT_R',
                kpIndex: 14,
                v: 2,
                x: 50,
                y: 50,
                quality: ITQuality.unavailable,
              ),
            ],
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('landmark_painter')), findsNothing);
    });

    testWidgets('InteractiveViewer wraps image and painter together',
        (tester) async {
      await tester.pumpWidget(
        _wrap(
          LandmarkOverlay(
            bytes: _tinyPng(),
            imageSize: const Size(100, 100),
            landmarks: const [
              Landmark(name: 'TD_R', x: 50, y: 50),
            ],
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('landmark_interactive_viewer')), findsOneWidget);
      expect(find.byKey(const Key('landmark_painter')), findsOneWidget);
      expect(find.byType(InteractiveViewer), findsOneWidget);
    });
  });
}
