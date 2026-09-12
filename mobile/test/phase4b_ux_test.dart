import 'dart:convert';
import 'dart:typed_data';

import 'package:coxometrie/services/radiograph_picker.dart';
import 'package:coxometrie/screens/home_screen.dart';
import 'package:coxometrie/widgets/loading_analysis.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakePicker implements RadiographPicker {
  @override
  Future<SelectedRadiograph?> pickFromCamera() async => null;

  @override
  Future<SelectedRadiograph?> pickFromGallery() async => null;
}

Uint8List _tinyPng() {
  return Uint8List.fromList(
    base64Decode(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
    ),
  );
}

void main() {
  group('Phase 4B Home declutter', () {
    testWidgets('hides backend URL and CLI chrome; keeps server entry',
        (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: HomeScreen(picker: _FakePicker()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('server_connection_button')), findsOneWidget);
      expect(find.byKey(const Key('import_gallery_button')), findsOneWidget);
      expect(find.textContaining('Backend :'), findsNothing);
      expect(find.textContaining('dart-define'), findsNothing);
      expect(find.textContaining('flutter run'), findsNothing);
      expect(find.text('Connexion serveur'), findsNothing);
    });
  });

  group('Phase 4B French loading', () {
    testWidgets('uses French loading copy without YOLO', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: LoadingAnalysis(imageBytes: _tinyPng()),
          ),
        ),
      );
      // CircularProgressIndicator animates indefinitely — do not pumpAndSettle.
      await tester.pump();

      expect(find.byKey(const Key('analysis_loading_message')), findsOneWidget);
      expect(find.text('Analyse de la radiographie…'), findsOneWidget);
      expect(
        find.textContaining('Détection des repères anatomiques'),
        findsOneWidget,
      );
      expect(find.textContaining('YOLO'), findsNothing);
      expect(find.textContaining('Analyzing'), findsNothing);
    });
  });
}
