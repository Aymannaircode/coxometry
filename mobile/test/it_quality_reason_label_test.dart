import 'package:coxometrie/utils/it_quality_reason_label.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('formatItQualityReason', () {
    test('maps known review codes to French', () {
      expect(
        formatItQualityReason('high_confidence_marginal_it_fsd'),
        'Confiance élevée mais position IT–diaphyse marginale',
      );
      expect(
        formatItQualityReason('low_model_confidence'),
        'Confiance du modèle trop basse',
      );
      expect(
        formatItQualityReason('insufficient_caudal_vs_teardrop'),
        'Position trop haute par rapport au teardrop',
      );
    });

    test('maps known unavailable codes to French', () {
      expect(
        formatItQualityReason('model_v0'),
        'Repère non identifiable par le modèle',
      );
      expect(
        formatItQualityReason('wrong_patient_side'),
        'Côté patient incohérent',
      );
      expect(
        formatItQualityReason('bilateral_order_violation'),
        'Ordre gauche/droite des IT incohérent',
      );
    });

    test('unknown code gets generic French fallback', () {
      expect(
        formatItQualityReason('some_future_code'),
        'Contrôle de qualité non satisfait',
      );
    });

    test('formatItQualityReasons joins French labels', () {
      expect(
        formatItQualityReasons([
          'model_v0',
          'out_of_image_bounds',
        ]),
        'Repère non identifiable par le modèle · '
        'Position hors des limites de l\'image',
      );
    });
  });
}
