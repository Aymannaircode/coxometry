import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:path/path.dart' as p;

import '../config/api_config.dart';
import '../models/analysis_result.dart';
import '../models/landmark.dart';
import '../models/measurements_api_mapper.dart';

/// Client HTTP vers `POST /analyze` (multipart) et `POST /measurements` (JSON).
class ApiService {
  /// Timeout dédié au health check (plus court que l'analyse).
  static const Duration healthTimeout = Duration(seconds: 15);

  /// Timeout analyse radiographique (YOLO + géométrie).
  static const Duration analyzeTimeout = Duration(seconds: 120);

  /// Timeout recalcul géométrique depuis landmarks manuels.
  static const Duration measurementsTimeout = Duration(seconds: 30);

  ApiService({
    http.Client? httpClient,
    Duration? timeout,
    Duration? healthCheckTimeout,
    Duration? measurementsCheckTimeout,
    String? baseUrl,
  })  : _client = httpClient ?? http.Client(),
        _timeout = timeout ?? analyzeTimeout,
        _healthTimeout = healthCheckTimeout ?? healthTimeout,
        _measurementsTimeout =
            measurementsCheckTimeout ?? measurementsTimeout,
        _baseUrl = baseUrl ?? ApiConfig.baseUrl;

  final http.Client _client;
  final Duration _timeout;
  final Duration _healthTimeout;
  final Duration _measurementsTimeout;
  final String _baseUrl;

  /// Taille max alignée sur le backend (25 Mo).
  static const int maxUploadBytes = 25 * 1024 * 1024;

  Uri get _analyzeUri => Uri.parse('$_baseUrl/analyze');

  Uri get _measurementsUri => Uri.parse('$_baseUrl/measurements');

  Uri get _healthUri => Uri.parse('$_baseUrl/health');

  String get baseUrl => _baseUrl;

  /// Vérifie la connectivité via `GET /health` (sans appeler `/analyze`).
  Future<HealthCheckResult> checkHealth() async {
    final started = DateTime.now();
    try {
      final response = await _client.get(_healthUri).timeout(_healthTimeout);
      final latency = DateTime.now().difference(started);

      Map<String, dynamic>? body;
      if (response.body.isNotEmpty) {
        try {
          final decoded = jsonDecode(response.body);
          if (decoded is Map<String, dynamic>) body = decoded;
        } on FormatException {
          return HealthCheckResult.failure(
            latency: latency,
            statusCode: response.statusCode,
            message: 'Réponse /health non JSON.',
          );
        }
      }

      if (response.statusCode != 200) {
        return HealthCheckResult.failure(
          latency: latency,
          statusCode: response.statusCode,
          message: 'HTTP ${response.statusCode}',
          body: body,
        );
      }

      return HealthCheckResult.success(
        latency: latency,
        status: body?['status']?.toString() ?? 'ok',
        service: body?['service']?.toString(),
        version: body?['version']?.toString(),
        modelVersion: body?['model_version']?.toString(),
        body: body,
      );
    } on TimeoutException {
      return HealthCheckResult.failure(
        latency: DateTime.now().difference(started),
        message: 'Délai dépassé (${_healthTimeout.inSeconds} s).',
        kind: ApiExceptionKind.timeout,
      );
    } on SocketException {
      return HealthCheckResult.failure(
        latency: DateTime.now().difference(started),
        message:
            'Serveur inaccessible à $_baseUrl. Vérifiez le réseau Wi‑Fi, '
            'le pare-feu Windows et --dart-define=API_BASE_URL.',
        kind: ApiExceptionKind.network,
      );
    } on HttpException catch (e) {
      return HealthCheckResult.failure(
        latency: DateTime.now().difference(started),
        message: 'Erreur réseau : ${e.message}',
        kind: ApiExceptionKind.network,
      );
    }
  }

  /// Envoie une radiographie PNG/JPG/JPEG au backend.
  Future<AnalysisResult> analyzeRadiograph({
    required Uint8List bytes,
    required String filename,
  }) async {
    if (bytes.isEmpty) {
      throw const ApiException(
        'Fichier image vide.',
        kind: ApiExceptionKind.invalidRequest,
      );
    }
    if (bytes.length > maxUploadBytes) {
      throw ApiException(
        'Fichier trop volumineux (max ${maxUploadBytes ~/ (1024 * 1024)} Mo).',
        kind: ApiExceptionKind.fileTooLarge,
        errorCode: 'file_too_large',
      );
    }

    final request = http.MultipartRequest('POST', _analyzeUri);
    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: filename,
        contentType: _mediaTypeForFilename(filename),
      ),
    );

    http.StreamedResponse streamed;
    try {
      streamed = await _client.send(request).timeout(_timeout);
    } on TimeoutException {
      throw const ApiException(
        'Délai d\'attente dépassé. Le serveur met trop de temps à répondre.',
        kind: ApiExceptionKind.timeout,
      );
    } on SocketException {
      throw ApiException(
        'Serveur inaccessible à $_baseUrl. Vérifiez que le backend est démarré '
        'et que l\'URL est correcte pour votre appareil.',
        kind: ApiExceptionKind.network,
      );
    } on HttpException catch (e) {
      throw ApiException(
        'Erreur réseau : ${e.message}',
        kind: ApiExceptionKind.network,
      );
    }

    final response = await http.Response.fromStream(streamed).timeout(_timeout);
    return _parseResponse(response);
  }

  AnalysisResult _parseResponse(http.Response response) {
    Map<String, dynamic>? body;

    if (response.body.isNotEmpty) {
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is! Map<String, dynamic>) {
          throw const FormatException('Objet JSON attendu.');
        }
        body = decoded;
      } on FormatException {
        throw ApiException(
          'Réponse JSON invalide (HTTP ${response.statusCode}).',
          kind: ApiExceptionKind.invalidJson,
          statusCode: response.statusCode,
        );
      }
    }

    if (response.statusCode == 422) {
      final detail = _extractDetail(body);
      throw ApiException(
        detail ?? 'Requête invalide (HTTP 422).',
        kind: ApiExceptionKind.clientError,
        statusCode: 422,
        body: body,
      );
    }

    if (response.statusCode >= 400 && response.statusCode < 500) {
      throw ApiException(
        _extractDetail(body) ?? 'Erreur client HTTP ${response.statusCode}.',
        kind: ApiExceptionKind.clientError,
        statusCode: response.statusCode,
        body: body,
      );
    }

    if (response.statusCode >= 500) {
      throw ApiException(
        _extractDetail(body) ?? 'Erreur serveur HTTP ${response.statusCode}.',
        kind: ApiExceptionKind.serverError,
        statusCode: response.statusCode,
        body: body,
      );
    }

    if (body == null) {
      throw ApiException(
        'Réponse vide (HTTP ${response.statusCode}).',
        kind: ApiExceptionKind.invalidJson,
        statusCode: response.statusCode,
      );
    }

    final status = body['status'];
    if (status is! String) {
      throw ApiException(
        'Réponse serveur invalide : champ status absent.',
        kind: ApiExceptionKind.invalidResponse,
        statusCode: response.statusCode,
        body: body,
      );
    }

    if (status == 'error') {
      final result = AnalysisResult.fromJson(body);
      throw ApiException(
        result.error?.message ?? 'Analyse impossible.',
        kind: ApiExceptionKind.analysisError,
        statusCode: response.statusCode,
        errorCode: result.error?.code,
        body: body,
      );
    }

    if (status == 'ok') {
      final validationError = AnalysisResponseValidator.validateOkResponse(body);
      if (validationError != null) {
        throw ApiException(
          validationError,
          kind: ApiExceptionKind.invalidResponse,
          statusCode: response.statusCode,
          body: body,
        );
      }
    } else {
      throw ApiException(
        'Statut de réponse inconnu : $status.',
        kind: ApiExceptionKind.invalidResponse,
        statusCode: response.statusCode,
        body: body,
      );
    }

    return AnalysisResult.fromJson(body);
  }

  /// Recalcule VCE / Tönnis / CCD via `POST /measurements` (mode landmarks).
  ///
  /// Envoie des coordonnées image originales — aucune détection IA.
  Future<AnalysisMeasurements> computeMeasurements({
    required List<Landmark> landmarks,
  }) async {
    final body = MeasurementsApiMapper.requestBody(landmarks);
    final list = body['landmarks'] as List;
    if (list.isEmpty) {
      throw const ApiException(
        'Aucun landmark exploitable pour le recalcul.',
        kind: ApiExceptionKind.invalidRequest,
      );
    }

    http.Response response;
    try {
      response = await _client
          .post(
            _measurementsUri,
            headers: const {'Content-Type': 'application/json'},
            body: jsonEncode(body),
          )
          .timeout(_measurementsTimeout);
    } on TimeoutException {
      throw ApiException(
        'Délai d\'attente dépassé lors du recalcul '
        '(${_measurementsTimeout.inSeconds} s).',
        kind: ApiExceptionKind.timeout,
      );
    } on SocketException {
      throw ApiException(
        'Serveur inaccessible à $_baseUrl. Vérifiez que le backend est démarré '
        'et que l\'URL est correcte pour votre appareil.',
        kind: ApiExceptionKind.network,
      );
    } on HttpException catch (e) {
      throw ApiException(
        'Erreur réseau : ${e.message}',
        kind: ApiExceptionKind.network,
      );
    }

    return _parseMeasurementsResponse(response);
  }

  AnalysisMeasurements _parseMeasurementsResponse(http.Response response) {
    Map<String, dynamic>? body;

    if (response.body.isNotEmpty) {
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is! Map<String, dynamic>) {
          throw const FormatException('Objet JSON attendu.');
        }
        body = decoded;
      } on FormatException {
        throw ApiException(
          'Réponse JSON invalide (HTTP ${response.statusCode}).',
          kind: ApiExceptionKind.invalidJson,
          statusCode: response.statusCode,
        );
      }
    }

    if (response.statusCode == 422) {
      throw ApiException(
        _extractDetail(body) ?? 'Requête invalide (HTTP 422).',
        kind: ApiExceptionKind.clientError,
        statusCode: 422,
        body: body,
      );
    }

    if (response.statusCode >= 400 && response.statusCode < 500) {
      throw ApiException(
        _extractDetail(body) ?? 'Erreur client HTTP ${response.statusCode}.',
        kind: ApiExceptionKind.clientError,
        statusCode: response.statusCode,
        body: body,
      );
    }

    if (response.statusCode >= 500) {
      throw ApiException(
        _extractDetail(body) ?? 'Erreur serveur HTTP ${response.statusCode}.',
        kind: ApiExceptionKind.serverError,
        statusCode: response.statusCode,
        body: body,
      );
    }

    if (body == null) {
      throw ApiException(
        'Réponse vide (HTTP ${response.statusCode}).',
        kind: ApiExceptionKind.invalidJson,
        statusCode: response.statusCode,
      );
    }

    final status = body['status'];
    if (status == 'error' || status == 'not_implemented') {
      throw ApiException(
        body['message']?.toString() ??
            _extractDetail(body) ??
            'Recalcul impossible.',
        kind: ApiExceptionKind.analysisError,
        statusCode: response.statusCode,
        body: body,
      );
    }

    try {
      return MeasurementsApiMapper.fromResponseJson(body);
    } on FormatException catch (e) {
      throw ApiException(
        e.message,
        kind: ApiExceptionKind.invalidResponse,
        statusCode: response.statusCode,
        body: body,
      );
    }
  }

  String? _extractDetail(Map<String, dynamic>? body) {
    if (body == null) return null;
    final detail = body['detail'];
    if (detail is String) return detail;
    if (detail is List && detail.isNotEmpty) {
      final first = detail.first;
      if (first is Map && first['msg'] != null) {
        return first['msg'].toString();
      }
    }
    final error = body['error'];
    if (error is Map && error['message'] != null) {
      return error['message'].toString();
    }
    return null;
  }

  MediaType _mediaTypeForFilename(String filename) {
    switch (p.extension(filename).toLowerCase()) {
      case '.jpg':
      case '.jpeg':
        return MediaType('image', 'jpeg');
      case '.png':
        return MediaType('image', 'png');
      default:
        return MediaType('application', 'octet-stream');
    }
  }

  void close() => _client.close();
}

class HealthCheckResult {
  const HealthCheckResult._({
    required this.ok,
    required this.latency,
    this.status,
    this.service,
    this.version,
    this.modelVersion,
    this.statusCode,
    this.message,
    this.kind,
    this.body,
  });

  final bool ok;
  final Duration latency;
  final String? status;
  final String? service;
  final String? version;

  /// Valeur brute de `model_version` depuis `GET /health` (ex. `v5_phase2`).
  final String? modelVersion;
  final int? statusCode;
  final String? message;
  final ApiExceptionKind? kind;
  final Map<String, dynamic>? body;

  factory HealthCheckResult.success({
    required Duration latency,
    required String status,
    String? service,
    String? version,
    String? modelVersion,
    Map<String, dynamic>? body,
  }) {
    return HealthCheckResult._(
      ok: true,
      latency: latency,
      status: status,
      service: service,
      version: version,
      modelVersion: modelVersion,
      statusCode: 200,
      body: body,
    );
  }

  factory HealthCheckResult.failure({
    required Duration latency,
    required String message,
    int? statusCode,
    ApiExceptionKind? kind,
    Map<String, dynamic>? body,
  }) {
    return HealthCheckResult._(
      ok: false,
      latency: latency,
      message: message,
      statusCode: statusCode,
      kind: kind,
      body: body,
    );
  }
}

enum ApiExceptionKind {
  network,
  timeout,
  clientError,
  serverError,
  invalidJson,
  invalidResponse,
  invalidRequest,
  fileTooLarge,
  analysisError,
}

class ApiException implements Exception {
  const ApiException(
    this.message, {
    required this.kind,
    this.statusCode,
    this.errorCode,
    this.body,
  });

  final String message;
  final ApiExceptionKind kind;
  final int? statusCode;
  final String? errorCode;
  final Map<String, dynamic>? body;

  @override
  String toString() =>
      'ApiException($kind, $statusCode, $errorCode): $message';
}
