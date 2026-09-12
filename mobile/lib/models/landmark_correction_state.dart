import 'landmark.dart';

/// Statut d'un landmark dans le bridge de correction manuelle (Phase 10H).
///
/// - [ai] : position identique à la prédiction initiale (`refined_landmarks`).
/// - [corrected] : position modifiée manuellement.
enum LandmarkStatus {
  ai,
  corrected;

  /// Valeur stable pour UI / sérialisation.
  String get wireName => switch (this) {
        LandmarkStatus.ai => 'AI',
        LandmarkStatus.corrected => 'CORRECTED',
      };

  static LandmarkStatus? fromWireName(String? raw) {
    switch (raw) {
      case 'AI':
        return LandmarkStatus.ai;
      case 'CORRECTED':
        return LandmarkStatus.corrected;
      default:
        return null;
    }
  }
}

/// Statut global de la session de correction.
///
/// - [aiOnly] : aucune position modifiée.
/// - [partiallyCorrected] : au moins un landmark corrigible a été déplacé.
enum CorrectionSessionStatus {
  aiOnly,
  partiallyCorrected;

  String get wireName => switch (this) {
        CorrectionSessionStatus.aiOnly => 'AI_ONLY',
        CorrectionSessionStatus.partiallyCorrected => 'PARTIALLY_CORRECTED',
      };
}

/// État éditable des landmarks après inférence IA.
///
/// Architecture (Phase 10H) :
/// - [originalAiLandmarks] : clone immuable de `detection.refined_landmarks`
/// - [currentLandmarks] : copie éditable
/// - correction exclusive manuelle (pas d'heuristique)
///
/// Ne touche ni au modèle V5, ni à `mvp_geometry`, ni à `/analyze`.
class LandmarkCorrectionState {
  /// Landmarks explicitement corrigibles en Phase 10H.
  static const Set<String> correctableNames = {
    'ASL_L',
    'ASL_R',
    'FSP_L',
    'FSP_R',
    'FSD_L',
    'FSD_R',
  };

  /// Nombre max d'états undo (évite une croissance illimitée).
  static const int maxUndoLevels = 32;

  LandmarkCorrectionState._({
    required List<Landmark> originalAiLandmarks,
    required List<Landmark> currentLandmarks,
    required Map<String, LandmarkStatus> statuses,
    List<_CorrectionSnapshot>? undoStack,
  })  : _originalAiLandmarks = List.unmodifiable(originalAiLandmarks),
        _currentLandmarks = currentLandmarks,
        _statuses = statuses,
        _undoStack = undoStack ?? <_CorrectionSnapshot>[];

  /// Point d'entrée : clone immuable de `refined_landmarks` (pas `raw_landmarks`).
  factory LandmarkCorrectionState.fromRefinedLandmarks(
    List<Landmark> refinedLandmarks,
  ) {
    final originals = _cloneList(refinedLandmarks);
    final current = _cloneList(refinedLandmarks);
    final statuses = <String, LandmarkStatus>{
      for (final lm in originals) lm.name: LandmarkStatus.ai,
    };
    return LandmarkCorrectionState._(
      originalAiLandmarks: originals,
      currentLandmarks: current,
      statuses: statuses,
    );
  }

  final List<Landmark> _originalAiLandmarks;
  List<Landmark> _currentLandmarks;
  Map<String, LandmarkStatus> _statuses;
  final List<_CorrectionSnapshot> _undoStack;

  /// Prédictions IA initiales — jamais mutées après construction.
  List<Landmark> get originalAiLandmarks => _originalAiLandmarks;

  /// Positions courantes (affichage, mesures, PDF).
  List<Landmark> get currentLandmarks =>
      List.unmodifiable(_currentLandmarks);

  /// Nombre de landmarks dont la position diffère de l'IA.
  int get correctedCount =>
      _statuses.values.where((s) => s == LandmarkStatus.corrected).length;

  CorrectionSessionStatus get globalStatus => correctedCount == 0
      ? CorrectionSessionStatus.aiOnly
      : CorrectionSessionStatus.partiallyCorrected;

  bool get canUndo => _undoStack.isNotEmpty;

  bool get hasCorrections => correctedCount > 0;

  bool isCorrectable(String name) => correctableNames.contains(name);

  LandmarkStatus statusOf(String name) =>
      _statuses[name] ?? LandmarkStatus.ai;

  Landmark? originalByName(String name) {
    for (final lm in _originalAiLandmarks) {
      if (lm.name == name) return lm;
    }
    return null;
  }

  Landmark? currentByName(String name) {
    for (final lm in _currentLandmarks) {
      if (lm.name == name) return lm;
    }
    return null;
  }

  /// Déplace un landmark corrigible en coordonnées image originales.
  ///
  /// Empile un undo avant mutation. Retourne `false` si le nom n'est pas
  /// corrigible ou absent de la liste courante.
  bool moveLandmark(String name, double x, double y) {
    if (!_canEdit(name)) return false;
    _pushUndo();
    return _applyPosition(name, x, y);
  }

  /// Empile un undo une fois au début d'un drag (évite un undo par pixel).
  bool beginLandmarkEdit(String name) {
    if (!_canEdit(name)) return false;
    _pushUndo();
    return true;
  }

  /// Met à jour la position pendant un drag — sans empiler d'undo.
  ///
  /// Les coordonnées doivent être en `original_image_pixels`.
  bool updateLandmarkPosition(String name, double x, double y) {
    if (!_canEdit(name)) return false;
    return _applyPosition(name, x, y);
  }

  bool _canEdit(String name) {
    if (!isCorrectable(name)) return false;
    return _indexOfName(_currentLandmarks, name) >= 0;
  }

  bool _applyPosition(String name, double x, double y) {
    if (!x.isFinite || !y.isFinite) return false;

    final index = _indexOfName(_currentLandmarks, name);
    if (index < 0) return false;

    final previous = _currentLandmarks[index];
    final updated = Landmark(
      name: previous.name,
      x: x,
      y: y,
      confidence: previous.confidence,
      visibility: previous.visibility,
    );

    _currentLandmarks = List<Landmark>.from(_currentLandmarks);
    _currentLandmarks[index] = updated;
    _statuses = Map<String, LandmarkStatus>.from(_statuses);
    _statuses[name] = _statusFromPositions(
      original: originalByName(name),
      current: updated,
    );
    return true;
  }

  /// Restaure exactement les prédictions IA et vide l'historique undo.
  void reset() {
    _currentLandmarks = _cloneList(_originalAiLandmarks);
    _statuses = {
      for (final lm in _originalAiLandmarks) lm.name: LandmarkStatus.ai,
    };
    _undoStack.clear();
  }

  /// Annule la dernière correction. Retourne `false` si la pile est vide.
  bool undo() {
    if (_undoStack.isEmpty) return false;
    final snapshot = _undoStack.removeLast();
    _currentLandmarks = snapshot.landmarks;
    _statuses = snapshot.statuses;
    return true;
  }

  void _pushUndo() {
    _undoStack.add(
      _CorrectionSnapshot(
        landmarks: _cloneList(_currentLandmarks),
        statuses: Map<String, LandmarkStatus>.from(_statuses),
      ),
    );
    while (_undoStack.length > maxUndoLevels) {
      _undoStack.removeAt(0);
    }
  }

  static LandmarkStatus _statusFromPositions({
    required Landmark? original,
    required Landmark current,
  }) {
    if (original == null) return LandmarkStatus.corrected;
    if (_samePoint(original.x, original.y, current.x, current.y)) {
      return LandmarkStatus.ai;
    }
    return LandmarkStatus.corrected;
  }

  static bool _samePoint(
    double? ax,
    double? ay,
    double? bx,
    double? by,
  ) {
    if (ax == null || ay == null || bx == null || by == null) {
      return ax == bx && ay == by;
    }
    return ax == bx && ay == by;
  }

  static int _indexOfName(List<Landmark> list, String name) {
    for (var i = 0; i < list.length; i++) {
      if (list[i].name == name) return i;
    }
    return -1;
  }

  static Landmark _cloneLandmark(Landmark landmark) {
    return Landmark(
      name: landmark.name,
      x: landmark.x,
      y: landmark.y,
      confidence: landmark.confidence,
      visibility: landmark.visibility,
    );
  }

  static List<Landmark> _cloneList(List<Landmark> source) {
    return source.map(_cloneLandmark).toList(growable: false);
  }
}

class _CorrectionSnapshot {
  const _CorrectionSnapshot({
    required this.landmarks,
    required this.statuses,
  });

  final List<Landmark> landmarks;
  final Map<String, LandmarkStatus> statuses;
}
