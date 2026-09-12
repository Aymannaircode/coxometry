/// Fixtures JSON partagées pour les tests V2 / V5.
library;

Map<String, dynamic> coordinateSpaceJson({
  int imageWidth = 1024,
  int imageHeight = 768,
}) {
  return {
    'image_width': imageWidth,
    'image_height': imageHeight,
    'preprocessed_width': 640,
    'preprocessed_height': 640,
    'scale': 0.625,
    'pad_x': 0,
    'pad_y': 80,
    'landmark_coordinate_space': 'original_image_pixels',
  };
}

Map<String, dynamic> itLandmarkJson({
  required String name,
  required int kpIndex,
  int v = 2,
  double? x,
  double? y,
  double? confidence,
  String? quality,
  List<String>? qualityReasons,
}) {
  return {
    'name': name,
    'kp_index': kpIndex,
    'v': v,
    'x': x,
    'y': y,
    'confidence': confidence,
    'quality': quality,
    'quality_reasons': qualityReasons,
  };
}

/// Réponse V2 minimale (it_landmarks vide, pas de coordinate_space requis).
Map<String, dynamic> v2SuccessJson({
  bool refinementApplied = true,
}) {
  return {
    'status': 'ok',
    'model_version': 'v2',
    'detection': {
      'bounding_box': {'x1': 10.0, 'y1': 20.0, 'x2': 500.0, 'y2': 400.0},
      'raw_landmarks': [
        {'name': 'ASL_L', 'x': 100.0, 'y': 200.0, 'confidence': 0.9},
      ],
      'refined_landmarks': [
        {'name': 'ASL_L', 'x': 105.0, 'y': 203.0, 'confidence': 0.95},
        {'name': 'TD_R', 'x': 300.0, 'y': 500.0, 'confidence': 0.92},
      ],
      'it_landmarks': [],
      'refinement_enabled': true,
      'refinement_applied': refinementApplied,
    },
    'measurements': _measurementsBlock(),
    'audit': {'landmark_count': 14},
  };
}

/// Réponse V5 Phase 2 complète avec IT accept.
Map<String, dynamic> v5SuccessJson({
  String itRQuality = 'accept',
  String itLQuality = 'accept',
  List<String>? itRReasons,
  List<String>? itLReasons,
  int? imageWidth,
  int? imageHeight,
}) {
  return {
    'status': 'ok',
    'model_version': 'v5_phase2',
    'detection': {
      'bounding_box': {'x1': 10.0, 'y1': 20.0, 'x2': 500.0, 'y2': 400.0},
      'raw_landmarks': [
        {'name': 'TD_R', 'x': 300.0, 'y': 500.0, 'confidence': 0.9},
      ],
      'refined_landmarks': [
        {'name': 'TD_R', 'x': 300.0, 'y': 500.0, 'confidence': 0.92},
        {'name': 'TD_L', 'x': 700.0, 'y': 510.0, 'confidence': 0.91},
      ],
      'it_landmarks': [
        itLandmarkJson(
          name: 'IT_R',
          kpIndex: 14,
          v: 2,
          x: 320.0,
          y: 480.0,
          confidence: 0.82,
          quality: itRQuality,
          qualityReasons: itRReasons,
        ),
        itLandmarkJson(
          name: 'IT_L',
          kpIndex: 15,
          v: 2,
          x: 680.0,
          y: 490.0,
          confidence: 0.83,
          quality: itLQuality,
          qualityReasons: itLReasons,
        ),
      ],
      'refinement_enabled': true,
      'refinement_applied': true,
      'coordinate_space': coordinateSpaceJson(
        imageWidth: imageWidth ?? 1024,
        imageHeight: imageHeight ?? 768,
      ),
    },
    'measurements': _measurementsBlock(),
    'audit': {'landmark_count': 14, 'it_landmarks_qc': true},
  };
}

Map<String, dynamic> _measurementsBlock({bool allAvailable = false}) {
  return {
    'right': {
      'vce': {
        'value_deg': 25.0,
        'available': true,
        'reason': null,
        'landmarks_used': ['FHC_R', 'ASL_R', 'TD_R', 'TD_L'],
      },
      'tonnis': {
        'value_deg': 10.5,
        'available': true,
        'reason': null,
        'landmarks_used': null,
      },
      'ccd': {
        'value_deg': 130.0,
        'available': true,
        'reason': null,
        'landmarks_used': null,
      },
    },
    'left': {
      'vce': {
        'value_deg': 30.0,
        'available': true,
        'reason': null,
        'landmarks_used': null,
      },
      'tonnis': {
        'value_deg': allAvailable ? 9.5 : null,
        'available': allAvailable,
        'reason': allAvailable ? null : 'Géométrie indéterminée.',
        'landmarks_used': null,
      },
      'ccd': {
        'value_deg': 128.0,
        'available': true,
        'reason': null,
        'landmarks_used': null,
      },
    },
  };
}

/// Variante V5 avec toutes les mesures disponibles (bannière succès).
Map<String, dynamic> v5FullyAvailableJson() {
  final json = v5SuccessJson();
  json['measurements'] = _measurementsBlock(allAvailable: true);
  return json;
}
