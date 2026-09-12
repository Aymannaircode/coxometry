import 'dart:convert';

import 'package:coxometrie/screens/server_connection_screen.dart';
import 'package:coxometrie/services/api_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('ServerConnectionScreen model version', () {
    testWidgets('affiche Modèle V5 Phase 2 depuis /health', (tester) async {
      final api = ApiService(
        httpClient: _FakeClient((_) async => _jsonStreamed({
              'status': 'ok',
              'service': 'coxometrie-backend',
              'version': '0.2.0',
              'model_version': 'v5_phase2',
            })),
        baseUrl: 'http://127.0.0.1:8001',
      );

      await tester.pumpWidget(
        MaterialApp(home: ServerConnectionScreen(api: api)),
      );

      await tester.tap(find.byKey(const Key('health_check_button')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('health_check_result')), findsOneWidget);
      expect(find.text('Serveur accessible'), findsOneWidget);
      expect(find.byKey(const Key('health_model_version')), findsOneWidget);
      expect(find.text('Modèle : V5 Phase 2'), findsOneWidget);
      expect(find.textContaining('YOLO'), findsNothing);
    });

    testWidgets('affiche Modèle V2 quand /health renvoie v2', (tester) async {
      final api = ApiService(
        httpClient: _FakeClient((_) async => _jsonStreamed({
              'status': 'ok',
              'service': 'coxometrie-backend',
              'version': '0.2.0',
              'model_version': 'v2',
            })),
        baseUrl: 'http://127.0.0.1:8001',
      );

      await tester.pumpWidget(
        MaterialApp(home: ServerConnectionScreen(api: api)),
      );

      await tester.tap(find.byKey(const Key('health_check_button')));
      await tester.pumpAndSettle();

      expect(find.text('Modèle : V2'), findsOneWidget);
      expect(find.textContaining('V5 Phase 2'), findsNothing);
    });

    testWidgets('instructions démo priorisent run_demo.ps1', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ServerConnectionScreen()),
      );

      expect(find.textContaining('run_demo.ps1'), findsWidgets);
      expect(
        find.textContaining('uvicorn backend.main:app --host 0.0.0.0'),
        findsNothing,
      );
    });
  });
}

class _FakeClient extends http.BaseClient {
  _FakeClient(this._handler);
  final Future<http.StreamedResponse> Function(http.BaseRequest request)
      _handler;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) =>
      _handler(request);
}

http.StreamedResponse _jsonStreamed(
  Map<String, dynamic> body, {
  int status = 200,
}) {
  return http.StreamedResponse(
    Stream<List<int>>.fromIterable([utf8.encode(jsonEncode(body))]),
    status,
    headers: {'content-type': 'application/json'},
  );
}
