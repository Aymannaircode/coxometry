/// Mapping présentation : codes QC IT backend → libellés français.
///
/// Les codes API (`quality_reasons`) restent inchangés ; seul l'affichage change.
String formatItQualityReason(String code) {
  switch (code) {
    case 'model_v0':
      return 'Repère non identifiable par le modèle';
    case 'out_of_image_bounds':
      return 'Position hors des limites de l\'image';
    case 'midline_unreliable':
      return 'Ligne médiane pelvienne peu fiable';
    case 'wrong_patient_side':
      return 'Côté patient incohérent';
    case 'weak_lateral_placement':
      return 'Placement latéral peu marqué';
    case 'insufficient_caudal_vs_teardrop':
      return 'Position trop haute par rapport au teardrop';
    case 'insufficient_caudal_vs_fhc':
      return 'Position trop haute par rapport à la tête fémorale';
    case 'low_model_confidence':
      return 'Confiance du modèle trop basse';
    case 'high_confidence_marginal_it_fsd':
      return 'Confiance élevée mais position IT–diaphyse marginale';
    case 'bilateral_vertical_asymmetry':
      return 'Asymétrie verticale entre IT droit et gauche';
    case 'bilateral_horizontal_asymmetry':
      return 'Asymétrie horizontale entre IT droit et gauche';
    case 'bilateral_order_violation':
      return 'Ordre gauche/droite des IT incohérent';
    default:
      return 'Contrôle de qualité non satisfait';
  }
}

/// Formate une liste de codes pour l'UI (libellés FR, sans codes techniques).
String formatItQualityReasons(Iterable<String> codes) {
  final labels = codes
      .map((c) => c.trim())
      .where((c) => c.isNotEmpty)
      .map(formatItQualityReason)
      .toList(growable: false);
  if (labels.isEmpty) return '';
  return labels.join(' · ');
}
