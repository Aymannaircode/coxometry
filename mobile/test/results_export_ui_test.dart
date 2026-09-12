import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/screens/results_screen.dart';
import 'package:coxometrie/services/radiograph_picker.dart';
import 'package:coxometrie/services/report/report_display_snapshot.dart';
import 'package:coxometrie/services/report/report_export_service.dart';
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
  TestWidgetsFlutterBinding.ensureInitialized();

  SelectedRadiograph radiograph() => SelectedRadiograph(
        bytes: _tinyPng(),
        filename: 'test.png',
        width: 1024,
        height: 768,
      );

  ReportExportService fakeExport({
    required Future<ReportExportResult> Function() run,
  }) {
    return ReportExportService(
      exportHandler: ({
        required radiographBytes,
        required result,
        localImageSize,
        generatedAt,
        display,
      }) =>
          run(),
    );
  }

  testWidgets('export button visible on Results', (tester) async {
    final result = AnalysisResult.fromJson(v5FullyAvailableJson());
    await tester.pumpWidget(
      MaterialApp(
        home: ResultsScreen(
          radiograph: radiograph(),
          result: result,
          exportService: fakeExport(
            run: () async => throw StateError('not used'),
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.byKey(const Key('export_report_button')), findsOneWidget);
    expect(find.text('Exporter le rapport'), findsOneWidget);
    expect(find.byKey(const Key('new_import_button')), findsOneWidget);
  });

  testWidgets('I. export failure shows French error snackbar', (tester) async {
    final result = AnalysisResult.fromJson(v5FullyAvailableJson());
    await tester.pumpWidget(
      MaterialApp(
        home: ResultsScreen(
          radiograph: radiograph(),
          result: result,
          exportService: fakeExport(
            run: () async => throw StateError('export failed'),
          ),
        ),
      ),
    );
    await tester.pump();

    await tester.tap(find.byKey(const Key('export_report_button')));
    await tester.pump(); // microtask: catch + snackbar

    expect(
      find.textContaining('Impossible de générer ou partager le rapport'),
      findsOneWidget,
    );

    // Annule le Timer du SnackBar pour ne pas bloquer la fin du test.
    final messenger = ScaffoldMessenger.of(
      tester.element(find.byType(ResultsScreen)),
    );
    messenger.clearSnackBars();
    await tester.pump();
  });

  testWidgets('export passes current display snapshot to PDF service',
      (tester) async {
    final result = AnalysisResult.fromJson(v5FullyAvailableJson());
    ReportDisplaySnapshot? captured;

    final exportService = ReportExportService(
      exportHandler: ({
        required radiographBytes,
        required result,
        localImageSize,
        generatedAt,
        display,
      }) async {
        captured = display;
        return ReportExportResult(
          file: File('dummy.pdf'),
          bytes: Uint8List.fromList([0x25, 0x50, 0x44, 0x46]),
        );
      },
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ResultsScreen(
          radiograph: radiograph(),
          result: result,
          exportService: exportService,
        ),
      ),
    );
    await tester.pump();

    await tester.tap(find.byKey(const Key('export_report_button')));
    await tester.pump();

    expect(captured, isNotNull);
    expect(captured!.analysisOriginLabel, 'Analyse : IA');
    expect(
      captured!.landmarks.map((l) => l.name),
      result.detection!.refinedLandmarks.map((l) => l.name),
    );
    expect(captured!.measurements!.right.vce.valueDeg, 25.0);

    final messenger = ScaffoldMessenger.of(
      tester.element(find.byType(ResultsScreen)),
    );
    messenger.clearSnackBars();
    await tester.pump();
  });
}
