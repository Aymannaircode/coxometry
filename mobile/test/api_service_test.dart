import 'dart:convert';
import 'dart:typed_data';

import 'package:coxometrie/models/landmark.dart';
import 'package:coxometrie/services/api_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

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

Map<String, dynamic> _okBody() => {
      'status': 'ok',
      'model_version': 'v2',
      'detection': {
        'bounding_box': {'x1': 1, 'y1': 2, 'x2': 3, 'y2': 4},
        'raw_landmarks': [],
        'refined_landmarks': [],
        'it_landmarks': [],
        'refinement_enabled': true,
        'refinement_applied': true,
      },
      'measurements': {
        'right': {
          'vce': {'value_deg': 25, 'available': true, 'reason': null},
          'tonnis': {'value_deg': 10, 'available': true, 'reason': null},
          'ccd': {'value_deg': 130, 'available': true, 'reason': null},
        },
        'left': {
          'vce': {'value_deg': 30, 'available': true, 'reason': null},
          'tonnis': {'value_deg': 10, 'available': true, 'reason': null},
          'ccd': {'value_deg': 128, 'available': true, 'reason': null},
        },
      },
      'audit': {},
    };

void main() {
  group('ApiService', () {
    test('API success — multipart field file on /analyze', () async {
      http.MultipartRequest? captured;

      final client = _FakeClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, '/analyze');
        expect(request, isA<http.MultipartRequest>());
        captured = request as http.MultipartRequest;
        expect(captured!.files.single.field, 'file');
        expect(captured!.files.single.filename, 'radio.png');
        return _jsonStreamed(_okBody());
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
      );

      final result = await api.analyzeRadiograph(
        bytes: Uint8List.fromList([1, 2, 3, 4]),
        filename: 'radio.png',
      );

      expect(result.isOk, isTrue);
      expect(result.measurements!.right.vce.valueDeg, 25);
    });

    test('V5 response parses without throw', () async {
      final client = _FakeClient((request) async {
        return _jsonStreamed({
          'status': 'ok',
          'model_version': 'v5_phase2',
          'detection': {
            'bounding_box': {'x1': 1, 'y1': 2, 'x2': 3, 'y2': 4},
            'raw_landmarks': [],
            'refined_landmarks': [
              {'name': 'TD_R', 'x': 100, 'y': 200, 'confidence': 0.9},
            ],
            'it_landmarks': [
              {
                'name': 'IT_R',
                'kp_index': 14,
                'v': 2,
                'x': 110.0,
                'y': 210.0,
                'confidence': 0.82,
                'quality': 'accept',
                'quality_reasons': null,
              },
              {
                'name': 'IT_L',
                'kp_index': 15,
                'v': 2,
                'x': 120.0,
                'y': 220.0,
                'confidence': 0.83,
                'quality': 'accept',
                'quality_reasons': null,
              },
            ],
            'refinement_enabled': true,
            'refinement_applied': true,
            'coordinate_space': {
              'image_width': 1024,
              'image_height': 768,
              'preprocessed_width': 640,
              'preprocessed_height': 640,
              'scale': 0.625,
              'pad_x': 0,
              'pad_y': 80,
              'landmark_coordinate_space': 'original_image_pixels',
            },
          },
          'measurements': _okBody()['measurements'],
          'audit': {},
        });
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
      );

      final result = await api.analyzeRadiograph(
        bytes: Uint8List.fromList([1, 2, 3, 4]),
        filename: 'radio.png',
      );

      expect(result.isOk, isTrue);
      expect(result.modelVersion, 'v5_phase2');
      expect(result.detection!.itLandmarks, hasLength(2));
      expect(result.detection!.coordinateSpace, isNotNull);
    });

    test('API error — status=error in JSON body', () async {
      final client = _FakeClient((request) async {
        return _jsonStreamed({
          'status': 'error',
          'error': {
            'code': 'invalid_image',
            'message': 'Image illisible ou corrompue.',
          },
        });
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
      );

      expect(
        () => api.analyzeRadiograph(
          bytes: Uint8List.fromList([1, 2, 3]),
          filename: 'x.png',
        ),
        throwsA(
          isA<ApiException>().having(
            (e) => e.kind,
            'kind',
            ApiExceptionKind.analysisError,
          ),
        ),
      );
    });

    test('HTTP 422 client error', () async {
      final client = _FakeClient((request) async {
        return _jsonStreamed(
          {'detail': 'multipart/form-data exige un fichier image'},
          status: 422,
        );
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
      );

      expect(
        () => api.analyzeRadiograph(
          bytes: Uint8List.fromList([1]),
          filename: 'x.png',
        ),
        throwsA(
          isA<ApiException>().having(
            (e) => e.kind,
            'kind',
            ApiExceptionKind.clientError,
          ),
        ),
      );
    });

    test('HTTP 500 server error', () async {
      final client = _FakeClient((request) async {
        return _jsonStreamed({'detail': 'Internal Server Error'}, status: 500);
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
      );

      expect(
        () => api.analyzeRadiograph(
          bytes: Uint8List.fromList([1]),
          filename: 'x.png',
        ),
        throwsA(
          isA<ApiException>().having(
            (e) => e.kind,
            'kind',
            ApiExceptionKind.serverError,
          ),
        ),
      );
    });

    test('invalid JSON body', () async {
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

      expect(
        () => api.analyzeRadiograph(
          bytes: Uint8List.fromList([1]),
          filename: 'x.png',
        ),
        throwsA(
          isA<ApiException>().having(
            (e) => e.kind,
            'kind',
            ApiExceptionKind.invalidJson,
          ),
        ),
      );
    });

    test('file too large rejected client-side', () async {
      final api = ApiService(baseUrl: 'http://example.test');
      final oversized = Uint8List(ApiService.maxUploadBytes + 1);

      expect(
        () => api.analyzeRadiograph(bytes: oversized, filename: 'big.png'),
        throwsA(
          isA<ApiException>().having(
            (e) => e.kind,
            'kind',
            ApiExceptionKind.fileTooLarge,
          ),
        ),
      );
    });

    test('status ok + valid measurements succeeds', () async {
      final client = _FakeClient((request) async => _jsonStreamed(_okBody()));
      final api = ApiService(httpClient: client, baseUrl: 'http://example.test');

      final result = await api.analyzeRadiograph(
        bytes: Uint8List.fromList([1, 2, 3]),
        filename: 'radio.png',
      );

      expect(result.isOk, isTrue);
      expect(result.measurements, isNotNull);
      expect(result.measurements!.right.vce.valueDeg, 25);
    });

    test('status ok + missing measurements throws invalidResponse', () async {
      final body = _okBody()..remove('measurements');
      final client = _FakeClient((request) async => _jsonStreamed(body));
      final api = ApiService(httpClient: client, baseUrl: 'http://example.test');

      expect(
        () => api.analyzeRadiograph(
          bytes: Uint8List.fromList([1]),
          filename: 'x.png',
        ),
        throwsA(
          isA<ApiException>()
              .having((e) => e.kind, 'kind', ApiExceptionKind.invalidResponse)
              .having(
                (e) => e.message,
                'message',
                contains('mesures absentes'),
              ),
        ),
      );
    });

    test('status ok + malformed measurements throws invalidResponse', () async {
      final body = Map<String, dynamic>.from(_okBody());
      body['measurements'] = {
        'right': {'vce': 'not-a-measurement'},
      };
      final client = _FakeClient((request) async => _jsonStreamed(body));
      final api = ApiService(httpClient: client, baseUrl: 'http://example.test');

      expect(
        () => api.analyzeRadiograph(
          bytes: Uint8List.fromList([1]),
          filename: 'x.png',
        ),
        throwsA(
          isA<ApiException>().having(
            (e) => e.kind,
            'kind',
            ApiExceptionKind.invalidResponse,
          ),
        ),
      );
    });

    test('timeout throws ApiException', () async {
      final client = _FakeClient((request) async {
        await Future<void>.delayed(const Duration(seconds: 2));
        return _jsonStreamed(_okBody());
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
        timeout: const Duration(milliseconds: 50),
      );

      expect(
        () => api.analyzeRadiograph(
          bytes: Uint8List.fromList([1]),
          filename: 'x.png',
        ),
        throwsA(
          isA<ApiException>().having(
            (e) => e.kind,
            'kind',
            ApiExceptionKind.timeout,
          ),
        ),
      );
    });

    test('computeMeasurements posts JSON landmarks to /measurements', () async {
      http.Request? captured;
      final client = _FakeClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, '/measurements');
        captured = request as http.Request;
        return _jsonStreamed({
          'status': 'ok',
          'mode': 'landmarks',
          'source': 'manual_landmarks',
          'sides': {
            'R': {
              'side': 'R',
              'vce': {
                'name': 'VCE',
                'side': 'R',
                'value_deg': 22.0,
                'available': true,
                'reason': null,
              },
              'tonnis': {
                'name': 'Tönnis',
                'side': 'R',
                'value_deg': 11.0,
                'available': true,
                'reason': null,
              },
              'ccd': {
                'name': 'CCD',
                'side': 'R',
                'value_deg': 131.0,
                'available': true,
                'reason': null,
              },
            },
            'L': {
              'side': 'L',
              'vce': {
                'name': 'VCE',
                'side': 'L',
                'value_deg': 28.0,
                'available': true,
                'reason': null,
              },
              'tonnis': {
                'name': 'Tönnis',
                'side': 'L',
                'value_deg': 9.0,
                'available': true,
                'reason': null,
              },
              'ccd': {
                'name': 'CCD',
                'side': 'L',
                'value_deg': 127.0,
                'available': true,
                'reason': null,
              },
            },
          },
        });
      });

      final api = ApiService(
        httpClient: client,
        baseUrl: 'http://example.test',
      );

      final measured = await api.computeMeasurements(
        landmarks: const [
          Landmark(name: 'ASL_L', x: 760.0, y: 340.0, visibility: 2),
          Landmark(name: 'TD_R', x: 300.0, y: 500.0),
          Landmark(name: 'IT_L', x: 1, y: 2),
        ],
      );

      expect(captured, isNotNull);
      expect(captured!.headers['Content-Type'], contains('application/json'));
      final payload = jsonDecode(captured!.body) as Map<String, dynamic>;
      expect(payload['mode'], 'landmarks');
      final landmarks = payload['landmarks'] as List;
      expect(landmarks, hasLength(2));
      expect(landmarks.first['x'], 760.0);
      expect(landmarks.first['y'], 340.0);
      expect(landmarks.first['name'], 'ASL_L');
      expect(measured.right.vce.valueDeg, 22.0);
      expect(measured.left.ccd.valueDeg, 127.0);
    });
  });
}