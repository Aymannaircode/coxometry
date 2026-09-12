import 'dart:convert';

import 'package:coxometrie/services/api_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('ApiService.checkHealth', () {
    test('success parses GET /health', () async {
      final client = _FakeClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, '/health');
        return _jsonStreamed({
          'status': 'ok',
          'service': 'mvp-backend',
          'version': '0.2.0',
          'model_version': 'v5_phase2',
        });
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://192.168.1.10:8001',
      );

      final result = await api.checkHealth();
      expect(result.ok, isTrue);
      expect(result.status, 'ok');
      expect(result.service, 'mvp-backend');
      expect(result.version, '0.2.0');
      expect(result.modelVersion, 'v5_phase2');
      expect(result.latency.inMilliseconds, greaterThanOrEqualTo(0));
    });

    test('success parses model_version v2', () async {
      final client = _FakeClient((request) async {
        return _jsonStreamed({
          'status': 'ok',
          'service': 'coxometrie-backend',
          'version': '0.2.0',
          'model_version': 'v2',
        });
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
      );

      final result = await api.checkHealth();
      expect(result.ok, isTrue);
      expect(result.modelVersion, 'v2');
    });

    test('failure on HTTP 503', () async {
      final client = _FakeClient((request) async {
        return _jsonStreamed({'detail': 'unavailable'}, status: 503);
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
      );

      final result = await api.checkHealth();
      expect(result.ok, isFalse);
      expect(result.statusCode, 503);
    });

    test('failure on invalid JSON', () async {
      final client = _FakeClient((request) async {
        return http.StreamedResponse(
          Stream<List<int>>.fromIterable([utf8.encode('not-json')]),
          200,
        );
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
      );

      final result = await api.checkHealth();
      expect(result.ok, isFalse);
      expect(result.message, contains('non JSON'));
    });
  });
}

class _FakeClient extends http.BaseClient {
  _FakeClient(this._handler);
  final Future<http.StreamedResponse> Function(http.BaseRequest request) _handler;
  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) => _handler(request);
}

http.StreamedResponse _jsonStreamed(Map<String, dynamic> body, {int status = 200}) {
  return http.StreamedResponse(
    Stream<List<int>>.fromIterable([utf8.encode(jsonEncode(body))]),
    status,
    headers: {'content-type': 'application/json'},
  );
}
