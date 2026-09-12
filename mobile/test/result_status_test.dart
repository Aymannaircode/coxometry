import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/utils/result_status.dart';
import 'package:flutter_test/flutter_test.dart';

import 'fixtures/analysis_fixtures.dart';

void main() {
  group('ResultPresentationStatus', () {
    test('review takes priority over partial measures', () {
      final result = AnalysisResult.fromJson(v5SuccessJson(
        itRQuality: 'review',
        itRReasons: ['high_confidence_marginal_it_fsd'],
      ));
      final status = ResultPresentationStatus.fromAnalysis(result);
      expect(status.kind, ResultPresentationKind.review);
      expect(status.title, 'Vérification recommandée');
      expect(status.detail, contains('IT_R'));
    });

    test('partial measures yield incomplete without inventing failure', () {
      final result = AnalysisResult.fromJson(v5SuccessJson());
      final status = ResultPresentationStatus.fromAnalysis(result);
      expect(status.kind, ResultPresentationKind.incomplete);
      expect(status.title, contains('partielles'));
    });

    test('fully available V5 is success', () {
      final result = AnalysisResult.fromJson(v5FullyAvailableJson());
      final status = ResultPresentationStatus.fromAnalysis(result);
      expect(status.kind, ResultPresentationKind.success);
      expect(status.title, 'Analyse terminée');
    });

    test('unavailable IT yields incomplete', () {
      final json = v5FullyAvailableJson();
      json['detection'] = v5SuccessJson(
        itRQuality: 'unavailable',
        itRReasons: ['low_visibility'],
        itLQuality: 'accept',
      )['detection'];
      final result = AnalysisResult.fromJson(json);
      final status = ResultPresentationStatus.fromAnalysis(result);
      expect(status.kind, ResultPresentationKind.incomplete);
      expect(status.detail, contains('IT_R'));
    });
  });
}
