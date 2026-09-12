import 'package:coxometrie/models/analysis_result.dart';
import 'package:coxometrie/models/landmark.dart';
import 'package:coxometrie/models/landmark_correction_state.dart';
import 'package:flutter_test/flutter_test.dart';

import 'fixtures/analysis_fixtures.dart';

List<Landmark> _sampleRefined() {
  return const [
    Landmark(name: 'TD_R', x: 300.0, y: 500.0, confidence: 0.9),
    Landmark(name: 'TD_L', x: 700.0, y: 510.0, confidence: 0.91),
    Landmark(name: 'ASL_R', x: 250.0, y: 320.0, confidence: 0.88),
    Landmark(name: 'ASL_L', x: 750.0, y: 330.0, confidence: 0.87),
    Landmark(name: 'FSP_R', x: 220.0, y: 480.0, confidence: 0.85),
    Landmark(name: 'FSP_L', x: 780.0, y: 490.0, confidence: 0.84),
    Landmark(name: 'FSD_R', x: 210.0, y: 560.0, confidence: 0.83),
    Landmark(name: 'FSD_L', x: 790.0, y: 570.0, confidence: 0.82),
    Landmark(name: 'ASM_R', x: 280.0, y: 340.0, confidence: 0.8),
  ];
}

void main() {
  group('LandmarkStatus / CorrectionSessionStatus wire names', () {
    test('LandmarkStatus wire names', () {
      expect(LandmarkStatus.ai.wireName, 'AI');
      expect(LandmarkStatus.corrected.wireName, 'CORRECTED');
      expect(LandmarkStatus.fromWireName('AI'), LandmarkStatus.ai);
      expect(LandmarkStatus.fromWireName('CORRECTED'), LandmarkStatus.corrected);
      expect(LandmarkStatus.fromWireName('MANUAL'), isNull);
    });

    test('CorrectionSessionStatus wire names', () {
      expect(CorrectionSessionStatus.aiOnly.wireName, 'AI_ONLY');
      expect(
        CorrectionSessionStatus.partiallyCorrected.wireName,
        'PARTIALLY_CORRECTED',
      );
    });
  });

  group('LandmarkCorrectionState.fromRefinedLandmarks', () {
    test('clones refined landmarks as immutable AI originals', () {
      final refined = _sampleRefined();
      final state = LandmarkCorrectionState.fromRefinedLandmarks(refined);

      expect(state.originalAiLandmarks.length, refined.length);
      expect(state.currentLandmarks.length, refined.length);
      expect(state.globalStatus, CorrectionSessionStatus.aiOnly);
      expect(state.correctedCount, 0);
      expect(state.hasCorrections, isFalse);
      expect(state.canUndo, isFalse);

      for (final lm in state.originalAiLandmarks) {
        expect(state.statusOf(lm.name), LandmarkStatus.ai);
      }

      // Mutating the source list must not affect cloned originals.
      final mutableSource = List<Landmark>.from(refined);
      final isolated = LandmarkCorrectionState.fromRefinedLandmarks(mutableSource);
      mutableSource[0] = const Landmark(name: 'TD_R', x: 1, y: 1);
      expect(isolated.originalByName('TD_R')!.x, 300.0);
      expect(isolated.currentByName('TD_R')!.x, 300.0);
    });

    test('uses refined_landmarks from AnalysisResult, not raw', () {
      final json = v2SuccessJson();
      final result = AnalysisResult.fromJson(json);
      final detection = result.detection!;
      final state = LandmarkCorrectionState.fromRefinedLandmarks(
        detection.refinedLandmarks,
      );

      final aslL = state.originalByName('ASL_L');
      expect(aslL, isNotNull);
      // Fixture: raw ASL_L=(100,200), refined=(105,203)
      expect(aslL!.x, 105.0);
      expect(aslL.y, 203.0);
      expect(aslL.x, isNot(detection.rawLandmarks.first.x));
    });

    test('currentLandmarks getter returns an unmodifiable view', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      expect(
        () => (state.currentLandmarks as List).add(
          const Landmark(name: 'X', x: 0, y: 0),
        ),
        throwsUnsupportedError,
      );
    });
  });

  group('correctable landmarks', () {
    test('only Phase 10H priority landmarks are correctable', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      for (final name in LandmarkCorrectionState.correctableNames) {
        expect(state.isCorrectable(name), isTrue);
      }
      expect(state.isCorrectable('TD_R'), isFalse);
      expect(state.isCorrectable('ASM_R'), isFalse);
      expect(state.isCorrectable('IT_R'), isFalse);
    });

    test('moveLandmark rejects non-correctable landmarks', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      expect(state.moveLandmark('TD_R', 10, 20), isFalse);
      expect(state.currentByName('TD_R')!.x, 300.0);
      expect(state.statusOf('TD_R'), LandmarkStatus.ai);
      expect(state.globalStatus, CorrectionSessionStatus.aiOnly);
      expect(state.canUndo, isFalse);
    });

    test('moveLandmark rejects unknown or non-finite coordinates', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      expect(state.moveLandmark('ASL_L', double.nan, 1), isFalse);
      expect(state.moveLandmark('MISSING', 1, 1), isFalse);
    });
  });

  group('moveLandmark status and positions', () {
    test('moving ASL_L marks CORRECTED and PARTIALLY_CORRECTED', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      final ok = state.moveLandmark('ASL_L', 760.0, 340.0);
      expect(ok, isTrue);

      expect(state.currentByName('ASL_L')!.x, 760.0);
      expect(state.currentByName('ASL_L')!.y, 340.0);
      expect(state.originalByName('ASL_L')!.x, 750.0);
      expect(state.originalByName('ASL_L')!.y, 330.0);
      expect(state.statusOf('ASL_L'), LandmarkStatus.corrected);
      expect(state.statusOf('ASL_R'), LandmarkStatus.ai);
      expect(state.correctedCount, 1);
      expect(state.globalStatus, CorrectionSessionStatus.partiallyCorrected);
      expect(state.canUndo, isTrue);
    });

    test('AI originals remain unchanged after several corrections', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      state.moveLandmark('ASL_L', 761, 341);
      state.moveLandmark('ASL_R', 251, 321);
      state.moveLandmark('FSP_L', 781, 491);
      state.moveLandmark('FSD_R', 211, 561);

      expect(state.originalByName('ASL_L')!.x, 750.0);
      expect(state.originalByName('ASL_R')!.x, 250.0);
      expect(state.originalByName('FSP_L')!.x, 780.0);
      expect(state.originalByName('FSD_R')!.x, 210.0);
      expect(state.correctedCount, 4);
      expect(state.globalStatus, CorrectionSessionStatus.partiallyCorrected);
    });

    test('moving back to exact AI coordinates restores AI status', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      state.moveLandmark('FSP_R', 999, 999);
      expect(state.statusOf('FSP_R'), LandmarkStatus.corrected);

      state.moveLandmark('FSP_R', 220.0, 480.0);
      expect(state.statusOf('FSP_R'), LandmarkStatus.ai);
      expect(state.correctedCount, 0);
      expect(state.globalStatus, CorrectionSessionStatus.aiOnly);
    });

    test('preserves confidence and visibility on move', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(const [
        Landmark(
          name: 'ASL_L',
          x: 10,
          y: 20,
          confidence: 0.77,
          visibility: 2,
        ),
      ]);
      state.moveLandmark('ASL_L', 11, 21);
      final current = state.currentByName('ASL_L')!;
      expect(current.confidence, 0.77);
      expect(current.visibility, 2);
    });
    test('beginLandmarkEdit + updateLandmarkPosition avoid undo flood', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      expect(state.beginLandmarkEdit('ASL_L'), isTrue);
      expect(state.canUndo, isTrue);
      state.updateLandmarkPosition('ASL_L', 761, 341);
      state.updateLandmarkPosition('ASL_L', 762, 342);
      state.updateLandmarkPosition('ASL_L', 763, 343);
      expect(state.currentByName('ASL_L')!.x, 763);
      expect(state.statusOf('ASL_L'), LandmarkStatus.corrected);
      // One undo restores pre-drag position (single beginLandmarkEdit).
      expect(state.undo(), isTrue);
      expect(state.currentByName('ASL_L')!.x, 750.0);
      expect(state.canUndo, isFalse);
    });
  });

  group('reset', () {
    test('restores AI coordinates, statuses, and clears undo', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      state.moveLandmark('ASL_L', 800, 400);
      state.moveLandmark('FSD_L', 810, 580);
      expect(state.hasCorrections, isTrue);
      expect(state.canUndo, isTrue);

      state.reset();

      expect(state.currentByName('ASL_L')!.x, 750.0);
      expect(state.currentByName('ASL_L')!.y, 330.0);
      expect(state.currentByName('FSD_L')!.x, 790.0);
      expect(state.statusOf('ASL_L'), LandmarkStatus.ai);
      expect(state.statusOf('FSD_L'), LandmarkStatus.ai);
      expect(state.correctedCount, 0);
      expect(state.globalStatus, CorrectionSessionStatus.aiOnly);
      expect(state.canUndo, isFalse);
      expect(state.originalByName('ASL_L')!.x, 750.0);
    });
  });

  group('undo', () {
    test('single-level undo restores previous position and status', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      state.moveLandmark('ASL_R', 260, 330);
      expect(state.undo(), isTrue);

      expect(state.currentByName('ASL_R')!.x, 250.0);
      expect(state.currentByName('ASL_R')!.y, 320.0);
      expect(state.statusOf('ASL_R'), LandmarkStatus.ai);
      expect(state.globalStatus, CorrectionSessionStatus.aiOnly);
      expect(state.canUndo, isFalse);
      expect(state.undo(), isFalse);
    });

    test('multi-level undo restores intermediate corrections', () {
      final state = LandmarkCorrectionState.fromRefinedLandmarks(_sampleRefined());
      state.moveLandmark('ASL_L', 760, 340);
      state.moveLandmark('FSP_L', 785, 495);
      state.moveLandmark('FSD_L', 795, 575);

      expect(state.correctedCount, 3);
      expect(state.undo(), isTrue);
      expect(state.currentByName('FSD_L')!.x, 790.0);
      expect(state.statusOf('FSD_L'), LandmarkStatus.ai);
      expect(state.correctedCount, 2);

      expect(state.undo(), isTrue);
      expect(state.currentByName('FSP_L')!.x, 780.0);
      expect(state.correctedCount, 1);

      expect(state.undo(), isTrue);
      expect(state.currentByName('ASL_L')!.x, 750.0);
      expect(state.correctedCount, 0);
      expect(state.globalStatus, CorrectionSessionStatus.aiOnly);
    });
  });
}
