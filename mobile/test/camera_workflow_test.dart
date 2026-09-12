import 'dart:convert';
import 'dart:typed_data';

import 'package:coxometrie/app.dart';
import 'package:coxometrie/screens/analysis_screen.dart';
import 'package:coxometrie/screens/camera_confirm_screen.dart';
import 'package:coxometrie/screens/camera_guidance_screen.dart';
import 'package:coxometrie/screens/home_screen.dart';
import 'package:coxometrie/screens/preview_screen.dart';
import 'package:coxometrie/services/radiograph_picker.dart';
import 'package:coxometrie/utils/camera_user_messages.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

Uint8List _tinyPng() {
  return Uint8List.fromList(
    base64Decode(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
    ),
  );
}

SelectedRadiograph _sample({String name = 'capture.jpg'}) {
  return SelectedRadiograph(
    bytes: _tinyPng(),
    filename: name,
    width: 1,
    height: 1,
  );
}

class _ScriptedPicker implements RadiographPicker {
  _ScriptedPicker({
    this.cameraResults = const [],
    this.cameraError,
    this.galleryResult,
  });

  /// Successive camera results (`null` = cancel).
  final List<SelectedRadiograph?> cameraResults;
  final Object? cameraError;
  final SelectedRadiograph? galleryResult;
  int cameraCalls = 0;
  int galleryCalls = 0;

  @override
  Future<SelectedRadiograph?> pickFromCamera() async {
    cameraCalls++;
    if (cameraError != null) {
      final err = cameraError!;
      if (err is Exception) throw err;
      throw Exception(err.toString());
    }
    if (cameraResults.isEmpty) return null;
    final index = (cameraCalls - 1).clamp(0, cameraResults.length - 1);
    return cameraResults[index];
  }

  @override
  Future<SelectedRadiograph?> pickFromGallery() async {
    galleryCalls++;
    return galleryResult;
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  Future<void> openGuidance(WidgetTester tester, RadiographPicker picker) async {
    await tester.pumpWidget(CoxometrieApp(picker: picker));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('import_camera_button')));
    await tester.pumpAndSettle();
  }

  Future<void> tapVisible(WidgetTester tester, Finder finder) async {
    await tester.ensureVisible(finder);
    await tester.pumpAndSettle();
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }

  group('Phase 7B camera entry', () {
    testWidgets('A. camera option opens guidance (French)', (tester) async {
      final picker = _ScriptedPicker();
      await openGuidance(tester, picker);

      expect(find.byType(CameraGuidanceScreen), findsOneWidget);
      expect(find.byKey(const Key('camera_framing_title')), findsOneWidget);
      expect(find.text('Cadrez la radiographie'), findsOneWidget);
      expect(find.byKey(const Key('camera_prototype_notice')), findsOneWidget);
      expect(find.textContaining('prototype'), findsOneWidget);
      expect(find.textContaining('Take a photo'), findsNothing);
      expect(find.text('Camera'), findsNothing);
    });

    testWidgets('D. cancel on guidance returns home', (tester) async {
      await openGuidance(tester, _ScriptedPicker());
      await tapVisible(
        tester,
        find.byKey(const Key('camera_guidance_cancel_button')),
      );

      expect(find.byType(HomeScreen), findsOneWidget);
      expect(find.byType(CameraGuidanceScreen), findsNothing);
    });

    testWidgets('D. capture cancel stays on guidance', (tester) async {
      final picker = _ScriptedPicker(cameraResults: const [null]);
      await openGuidance(tester, picker);
      await tapVisible(tester, find.byKey(const Key('camera_open_button')));

      expect(picker.cameraCalls, 1);
      expect(find.byType(CameraGuidanceScreen), findsOneWidget);
      expect(find.byType(CameraConfirmScreen), findsNothing);
    });
  });

  group('Phase 7B confirm / retake / use', () {
    testWidgets('C. use photo enters PreviewScreen analysis path',
        (tester) async {
      final sample = _sample();
      final picker = _ScriptedPicker(cameraResults: [sample]);

      await tester.pumpWidget(
        MaterialApp(
          home: CameraConfirmScreen(picker: picker, radiograph: sample),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Utiliser cette photo'), findsOneWidget);
      expect(find.text('Reprendre'), findsOneWidget);

      await tapVisible(tester, find.byKey(const Key('camera_use_photo_button')));

      expect(find.byType(PreviewScreen), findsOneWidget);
      expect(find.byKey(const Key('analyze_button')), findsOneWidget);
      expect(find.byType(AnalysisScreen), findsNothing);
    });

    testWidgets('B. retake replaces image without analyzing', (tester) async {
      final first = _sample(name: 'first.jpg');
      final second = SelectedRadiograph(
        bytes: _tinyPng(),
        filename: 'second.jpg',
        width: 2,
        height: 2,
      );
      final picker = _ScriptedPicker(cameraResults: [second]);

      await tester.pumpWidget(
        MaterialApp(
          home: CameraConfirmScreen(picker: picker, radiograph: first),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('1 × 1'), findsOneWidget);

      await tapVisible(tester, find.byKey(const Key('camera_retake_button')));

      expect(picker.cameraCalls, 1);
      expect(find.textContaining('2 × 2'), findsOneWidget);
      expect(find.byType(PreviewScreen), findsNothing);
      expect(find.byType(AnalysisScreen), findsNothing);
    });

    testWidgets('B. retake cancel keeps current photo', (tester) async {
      final first = _sample();
      final picker = _ScriptedPicker(cameraResults: const [null]);

      await tester.pumpWidget(
        MaterialApp(
          home: CameraConfirmScreen(picker: picker, radiograph: first),
        ),
      );
      await tester.pumpAndSettle();

      await tapVisible(tester, find.byKey(const Key('camera_retake_button')));

      expect(find.textContaining('1 × 1'), findsOneWidget);
      expect(find.byKey(const Key('camera_use_photo_button')), findsOneWidget);
    });
  });

  group('Phase 7B errors', () {
    testWidgets('E. permission error shows French recovery', (tester) async {
      final picker = _ScriptedPicker(
        cameraError: const RadiographPickerException(
          CameraUserMessages.permissionDenied,
        ),
      );

      await tester.pumpWidget(
        MaterialApp(home: CameraGuidanceScreen(picker: picker)),
      );
      await tester.pumpAndSettle();

      await tapVisible(tester, find.byKey(const Key('camera_open_button')));

      expect(find.text(CameraUserMessages.permissionDenied), findsOneWidget);
      expect(find.byKey(const Key('camera_error_retry_button')), findsOneWidget);
      expect(find.textContaining('PlatformException'), findsNothing);
    });

    test('E. platform permission maps to French', () {
      final mapped = mapCameraPlatformException(
        PlatformException(code: 'camera_access_denied', message: 'denied'),
      );
      expect(mapped, CameraUserMessages.permissionDenied);
      expect(mapped.contains('denied'), isFalse);
      expect(mapped, contains('Autorisation'));
    });
  });

  group('Phase 7B pipeline parity', () {
    testWidgets('G. gallery still opens PreviewScreen directly', (tester) async {
      final picker = _ScriptedPicker(galleryResult: _sample(name: 'g.png'));
      await tester.pumpWidget(CoxometrieApp(picker: picker));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('import_gallery_button')));
      await tester.pumpAndSettle();

      expect(picker.galleryCalls, 1);
      expect(find.byType(PreviewScreen), findsOneWidget);
      expect(find.byType(CameraGuidanceScreen), findsNothing);
    });

    test('F. disclaimer does not mention validated clinical camera use', () {
      expect(
        CameraUserMessages.prototypeDisclaimer.toLowerCase(),
        isNot(contains('validée cliniquement sur négatoscope')),
      );
      expect(
        CameraUserMessages.prototypeDisclaimer,
        contains('prototype'),
      );
      expect(
        CameraUserMessages.prototypeDisclaimer,
        contains('validation spécifique'),
      );
    });

    test('H. user-facing camera strings are French', () {
      const corpus = [
        CameraUserMessages.permissionDenied,
        CameraUserMessages.cameraUnavailable,
        CameraUserMessages.loadFailed,
        CameraUserMessages.captureFailed,
        CameraUserMessages.prototypeDisclaimer,
      ];
      for (final s in corpus) {
        expect(s.contains('Permission denied'), isFalse);
        expect(s.contains('Failed to'), isFalse);
        expect(s.contains('Try again'), isFalse);
      }
    });
  });
}
