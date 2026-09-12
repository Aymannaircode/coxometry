/// Libellé discret pour l'affichage de [model_version] backend.
String formatModelVersion(String? modelVersion) {
  switch (modelVersion) {
    case 'v5_phase2':
      return 'V5 Phase 2';
    case 'v2':
      return 'V2';
    case null:
    case '':
      return 'V2';
    default:
      return modelVersion!;
  }
}
