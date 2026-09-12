import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/models/landmark.dart';
import 'package:coxometrie/models/measurement.dart';
import 'package:flutter_test/flutter_test.dart';

import 'fixtures/analysis_fixtures.dart';

/// Réponse JSON minimale alignée sur `backend/app/schemas/analyze.py`.
Map<String, dynamic> _sampleSuccessJson({
  bool vceRightAvailable = true,
  double? vceRightValue = 25.0,
  bool refinementApplied = true,
}) {
  final json = v2SuccessJson(refinementApplied: refinementApplied);
  if (!vceRightAvailable) {
    final right = (json['measurements'] as Map)['right'] as Map;
    final vce = right['vce'] as Map;
    vce['value_deg'] = null;
    vce['available'] = false;
    vce['reason'] = 'Landmark ASL_R manquant.';
  } else if (vceRightValue != null) {
    final right = (json['measurements'] as Map)['right'] as Map;
    (right['vce'] as Map)['value_deg'] = vceRightValue;
  }
  return json;
}

void main() {
  group('Measurement', () {
    test('parse available measure with value_deg', () {
      final m = Measurement.fromJson({
        'value_deg': 25.0,
        'available': true,
        'reason': null,
        'landmarks_used': ['FHC_R', 'ASL_R'],
      });
      expect(m.available, isTrue);
      expect(m.valueDeg, 25.0);
      expect(m.displayValue, '25.0°');
    });

    test('unavailable measure never displays 0°', () {
      final m = Measurement.fromJson({
        'value_deg': null,
        'available': false,
        'reason': 'Landmark ASL_R manquant.',
        'landmarks_used': null,
      });
      expect(m.displayValue, '—');
      expect(m.displayValue, isNot(contains('0°')));
    });

    test('unavailable with null value_deg even if zero in JSON edge case', () {
      final m = Measurement.fromJson({
        'value_deg': 0,
        'available': false,
        'reason': 'indisponible',
      });
      expect(m.displayValue, '—');
    });
  });

  group('Landmark', () {
    test('parse backend landmark with confidence', () {
      final lm = Landmark.fromJson({
        'name': 'ASL_L',
        'x': 12.5,
        'y': 30.0,
        'confidence': 0.9,
      });
      expect(lm.name, 'ASL_L');
      expect(lm.x, 12.5);
      expect(lm.y, 30.0);
      expect(lm.confidence, 0.9);
      expect(lm.isDrawable, isTrue);
    });

    test('coordinates validation', () {
      expect(
        const Landmark(name: 'X', x: null, y: 1).isDrawable,
        isFalse,
      );
      expect(
        const Landmark(name: 'X', x: 10, y: 20, visibility: 0).isDrawable,
        isFalse,
      );
      expect(
        const Landmark(name: 'X', x: 10, y: 20).isDrawable,
        isTrue,
      );
    });
  });

  group('AnalysisResult', () {
    test('parse success response', () {
      final result = AnalysisResult.fromJson(_sampleSuccessJson());
      expect(result.isOk, isTrue);
      expect(result.isError, isFalse);
      expect(result.modelVersion, 'v2');
      expect(result.detection!.itLandmarks, isEmpty);
      expect(result.measurements, isNotNull);
      expect(result.detection, isNotNull);
      expect(result.measurements!.right.vce.available, isTrue);
      expect(result.measurements!.right.vce.valueDeg, 25.0);
    });

    test('parse error response status=error', () {
      final result = AnalysisResult.fromJson({
        'status': 'error',
        'error': {
          'code': 'no_detection',
          'message': 'Aucune détection pelvis.',
        },
      });
      expect(result.isError, isTrue);
      expect(result.error?.code, 'no_detection');
      expect(result.measurements, isNull);
    });

    test('measurement unavailable in partial success', () {
      final result = AnalysisResult.fromJson(
        _sampleSuccessJson(vceRightAvailable: false, vceRightValue: null),
      );
      expect(result.isOk, isTrue);
      final vce = result.measurements!.right.vce;
      expect(vce.available, isFalse);
      expect(vce.valueDeg, isNull);
      expect(vce.displayValue, '—');
      expect(vce.reason, contains('ASL_R'));
    });

    test('refinement flag parsed from detection', () {
      final result = AnalysisResult.fromJson(_sampleSuccessJson());
      expect(result.detection!.refinementEnabled, isTrue);
      expect(result.detection!.refinementApplied, isTrue);
      expect(result.detection!.landmarkCount, 2);
    });

    test('refined vs raw landmark coordinates differ', () {
      final result = AnalysisResult.fromJson(_sampleSuccessJson());
      final raw = result.detection!.rawLandmarks.single;
      final refined = result.detection!.refinedLandmarks
          .firstWhere((l) => l.name == 'ASL_L');
      expect(raw.x, 100.0);
      expect(refined.x, 105.0);
      expect(refined.y, 203.0);
    });
  });

  group('AnalysisMeasurements.isValidJson', () {
    test('valid measurements block', () {
      final json = v2SuccessJson();
      expect(
        AnalysisMeasurements.isValidJson(json['measurements']),
        isTrue,
      );
    });

    test('missing measurements', () {
      expect(AnalysisMeasurements.isValidJson(null), isFalse);
    });

    test('malformed measurements', () {
      expect(
        AnalysisMeasurements.isValidJson({'right': 'invalid'}),
        isFalse,
      );
    });
  });

  group('AnalysisResponseValidator', () {
    test('ok response with valid data passes', () {
      expect(
        AnalysisResponseValidator.validateOkResponse(v2SuccessJson()),
        isNull,
      );
    });

    test('ok response without measurements fails', () {
      final json = v2SuccessJson()..remove('measurements');
      expect(
        AnalysisResponseValidator.validateOkResponse(json),
        contains('mesures absentes'),
      );
    });
  });
}
