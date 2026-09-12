import 'package:coxometrie/models/landmark.dart';
import 'package:coxometrie/models/measurements_api_mapper.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('MeasurementsApiMapper', () {
    test('requestBody keeps original_image_pixels and MVP landmarks only', () {
      const landmarks = [
        Landmark(name: 'ASL_L', x: 105.5, y: 203.25, visibility: 2),
        Landmark(name: 'TD_R', x: 300, y: 500, confidence: 0.9),
        Landmark(name: 'IT_R', x: 10, y: 20, visibility: 2),
        Landmark(name: 'ASL_R', x: null, y: null),
      ];

      final body = MeasurementsApiMapper.requestBody(landmarks);
      expect(body['mode'], 'landmarks');
      final list = body['landmarks'] as List;
      expect(list, hasLength(2));
      expect(list[0], {
        'name': 'ASL_L',
        'x': 105.5,
        'y': 203.25,
        'v': 2,
      });
      expect(list[1]['name'], 'TD_R');
      expect(list.any((e) => (e as Map)['name'] == 'IT_R'), isFalse);
    });

    test('fromResponseJson maps sides.R/L to AnalysisMeasurements', () {
      final measured = MeasurementsApiMapper.fromResponseJson({
        'status': 'ok',
        'mode': 'landmarks',
        'source': 'manual_landmarks',
        'sides': {
          'R': {
            'side': 'R',
            'vce': {
              'name': 'VCE',
              'side': 'R',
              'value_deg': 21.5,
              'available': true,
              'reason': null,
            },
            'tonnis': {
              'name': 'Tönnis',
              'side': 'R',
              'value_deg': 8.0,
              'available': true,
              'reason': null,
            },
            'ccd': {
              'name': 'CCD',
              'side': 'R',
              'value_deg': null,
              'available': false,
              'reason': 'missing',
            },
          },
          'L': {
            'side': 'L',
            'vce': {
              'name': 'VCE',
              'side': 'L',
              'value_deg': 30.0,
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
              'value_deg': 128.0,
              'available': true,
              'reason': null,
            },
          },
        },
      });

      expect(measured.right.vce.valueDeg, 21.5);
      expect(measured.right.ccd.available, isFalse);
      expect(measured.right.ccd.displayValue, '—');
      expect(measured.left.vce.valueDeg, 30.0);
      expect(measured.left.ccd.valueDeg, 128.0);
    });
  });
}
