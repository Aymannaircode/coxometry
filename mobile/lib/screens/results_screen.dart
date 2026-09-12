import 'dart:ui' show Size;

import 'package:flutter/material.dart';

import '../models/analysis_result.dart';
import '../models/landmark.dart';
import '../models/landmark_correction_state.dart';
import '../services/api_service.dart';
import '../services/radiograph_picker.dart';
import '../services/report/report_display_snapshot.dart';
import '../services/report/report_export_service.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import '../utils/image_size.dart';
import '../utils/overlay_image_size.dart';
import '../utils/result_status.dart';
import '../widgets/it_status_section.dart';
import '../widgets/landmark_legend.dart';
import '../widgets/landmark_overlay.dart';
import '../widgets/measurement_card.dart';
import '../widgets/model_version_label.dart';

/// Affiche les mesures, la détection et l'overlay landmarks.
class ResultsScreen extends StatefulWidget {
  const ResultsScreen({
    super.key,
    required this.radiograph,
    required this.result,
    this.exportService,
    this.apiService,
  });

  final SelectedRadiograph radiograph;
  final AnalysisResult result;

  /// Injection tests — export PDF / partage.
  final ReportExportService? exportService;

  /// Injection tests — `POST /measurements` pour recalcul.
  final ApiService? apiService;

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  OverlayImageSizeResult? _overlaySize;
  bool _exporting = false;
  bool _correctionMode = false;
  LandmarkCorrectionState? _correctionState;
  String? _selectedLandmarkName;

  /// Mesures issues de `/analyze` — jamais écrasées.
  late final AnalysisMeasurements? _originalMeasurements =
      widget.result.measurements;

  /// Mesures affichées (IA ou recalculées après correction).
  AnalysisMeasurements? _displayedMeasurements;

  bool _recomputing = false;
  String? _recomputeError;
  int _recomputeGeneration = 0;

  late final ReportExportService _exportService =
      widget.exportService ?? ReportExportService();
  late final ApiService _apiService = widget.apiService ?? ApiService();

  @override
  void initState() {
    super.initState();
    _displayedMeasurements = _originalMeasurements;
    _loadImageSize();
  }

  void _ensureCorrectionState() {
    if (_correctionState != null) return;
    final refined = widget.result.detection?.refinedLandmarks;
    if (refined == null || refined.isEmpty) return;
    _correctionState = LandmarkCorrectionState.fromRefinedLandmarks(refined);
  }

  void _toggleCorrectionMode() {
    setState(() {
      if (!_correctionMode) {
        _ensureCorrectionState();
        if (_correctionState == null) return;
        _correctionMode = true;
      } else {
        _correctionMode = false;
        _selectedLandmarkName = null;
      }
    });
  }

  void _undoCorrection() {
    final state = _correctionState;
    if (state == null || !state.canUndo) return;
    setState(() {
      state.undo();
    });
    _onCorrectionSettled();
  }

  Future<void> _confirmAndResetCorrection() async {
    final state = _correctionState;
    if (state == null) return;
    if (!state.hasCorrections && !state.canUndo) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          key: const Key('reset_correction_dialog'),
          title: const Text('Réinitialiser les corrections ?'),
          content: const Text(
            'Les positions IA d\'origine seront restaurées. '
            'L\'historique d\'annulation sera effacé.',
          ),
          actions: [
            TextButton(
              key: const Key('reset_correction_dismiss'),
              onPressed: () => Navigator.of(ctx).pop(false),
              child: const Text('Retour'),
            ),
            FilledButton(
              key: const Key('reset_correction_confirm'),
              onPressed: () => Navigator.of(ctx).pop(true),
              child: const Text('Réinitialiser'),
            ),
          ],
        );
      },
    );

    if (confirmed != true || !mounted) return;
    _recomputeGeneration++;
    setState(() {
      state.reset();
      _selectedLandmarkName = null;
      _displayedMeasurements = _originalMeasurements;
      _recomputing = false;
      _recomputeError = null;
    });
  }

  /// Après drag / undo : recalcul si corrigé, sinon mesures `/analyze`.
  Future<void> _onCorrectionSettled() async {
    final state = _correctionState;
    if (state == null) return;

    if (!state.hasCorrections) {
      _recomputeGeneration++;
      if (!mounted) return;
      setState(() {
        _displayedMeasurements = _originalMeasurements;
        _recomputing = false;
        _recomputeError = null;
      });
      return;
    }

    await _recomputeFromCurrentLandmarks();
  }

  Future<void> _recomputeFromCurrentLandmarks() async {
    final state = _correctionState;
    if (state == null) return;

    final generation = ++_recomputeGeneration;
    setState(() {
      _recomputing = true;
      _recomputeError = null;
    });

    try {
      final measured = await _apiService.computeMeasurements(
        landmarks: state.currentLandmarks,
      );
      if (!mounted || generation != _recomputeGeneration) return;
      setState(() {
        _displayedMeasurements = measured;
        _recomputing = false;
        _recomputeError = null;
      });
    } on ApiException catch (e) {
      if (!mounted || generation != _recomputeGeneration) return;
      setState(() {
        _recomputing = false;
        _recomputeError = e.message;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          key: const Key('recompute_error_snackbar'),
          content: Text(
            'Recalcul impossible : ${e.message}. '
            'Les mesures précédentes et les corrections sont conservées.',
          ),
          backgroundColor: AppColors.error,
          duration: const Duration(seconds: 4),
          action: SnackBarAction(
            key: const Key('recompute_retry_action'),
            label: 'Réessayer',
            textColor: Colors.white,
            onPressed: () {
              _recomputeFromCurrentLandmarks();
            },
          ),
        ),
      );
    } catch (_) {
      if (!mounted || generation != _recomputeGeneration) return;
      setState(() {
        _recomputing = false;
        _recomputeError =
            'Une erreur inattendue s\'est produite lors du recalcul.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          key: Key('recompute_error_snackbar'),
          content: Text(
            'Recalcul impossible. Les mesures précédentes et les '
            'corrections sont conservées.',
          ),
          backgroundColor: AppColors.error,
          duration: Duration(seconds: 4),
        ),
      );
    }
  }

  Map<String, LandmarkStatus> _statusMap(LandmarkCorrectionState state) {
    return {
      for (final lm in state.currentLandmarks) lm.name: state.statusOf(lm.name),
    };
  }

  Future<void> _exportReport() async {
    if (_exporting) return;
    setState(() => _exporting = true);

    try {
      Size? local;
      if (widget.radiograph.width != null && widget.radiograph.height != null) {
        local = Size(
          widget.radiograph.width!.toDouble(),
          widget.radiograph.height!.toDouble(),
        );
      }

      final display = ReportDisplaySnapshot.fromCorrectionState(
        result: widget.result,
        correctionState: _correctionState,
        displayedMeasurements: _displayedMeasurements,
      );

      await _exportService.exportAndShare(
        radiographBytes: widget.radiograph.bytes,
        result: widget.result,
        localImageSize: local ?? _overlaySize?.size,
        display: display,
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Rapport PDF généré.'),
          duration: Duration(seconds: 2),
        ),
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Impossible de générer ou partager le rapport. Réessayez.',
          ),
          backgroundColor: AppColors.error,
          duration: Duration(seconds: 3),
        ),
      );
    } finally {
      if (mounted) setState(() => _exporting = false);
    }
  }

  Future<void> _loadImageSize() async {
    Size? local;
    if (widget.radiograph.width != null && widget.radiograph.height != null) {
      local = Size(
        widget.radiograph.width!.toDouble(),
        widget.radiograph.height!.toDouble(),
      );
    } else {
      local = await decodeImageSize(widget.radiograph.bytes);
    }

    if (!mounted) return;
    final resolved = resolveOverlayImageSize(
      coordinateSpace: widget.result.detection?.coordinateSpace,
      localSize: local,
    );
    setState(() => _overlaySize = resolved);
  }

  @override
  Widget build(BuildContext context) {
    final measurements = _displayedMeasurements;
    final detection = widget.result.detection;
    final overlaySize = _overlaySize?.size ?? const Size(1, 1);
    final correction = _correctionState;
    final displayLandmarks = correction?.currentLandmarks ??
        detection?.refinedLandmarks ??
        const <Landmark>[];
    final hasLandmarks = detection != null &&
        (displayLandmarks.isNotEmpty || detection.hasItLandmarks);
    final overlayHeight = AppSpacing.radiographOverlayHeight(
      MediaQuery.sizeOf(context).height,
    );

    final itLandmarks = detection?.itLandmarks ?? const [];
    final hasIt = itLandmarks.isNotEmpty;
    final hasReview = itLandmarks.any((l) => l.isReview);
    final hasUnavailableIt = itLandmarks.any((l) => l.isUnavailable);
    final showCorrected = correction?.hasCorrections ?? false;
    final canCorrect = detection != null &&
        detection.refinedLandmarks.any(
          (lm) => LandmarkCorrectionState.correctableNames.contains(lm.name),
        );

    return Scaffold(
      key: const Key('results_screen'),
      appBar: AppBar(title: const Text('Résultats')),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(AppSpacing.pagePadding),
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(
                      maxWidth: AppSpacing.contentMaxWidth,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        if (hasLandmarks)
                          LandmarkOverlay(
                            key: const Key('results_landmark_overlay'),
                            bytes: widget.radiograph.bytes,
                            imageSize: overlaySize,
                            landmarks: displayLandmarks,
                            itLandmarks: detection!.itLandmarks,
                            height: overlayHeight,
                            correctionMode: _correctionMode,
                            landmarkStatuses: correction == null
                                ? const {}
                                : _statusMap(correction),
                            selectedLandmarkName: _selectedLandmarkName,
                            onSelectedLandmarkChanged: (name) {
                              setState(() => _selectedLandmarkName = name);
                            },
                            onLandmarkEditBegin: (name) {
                              correction?.beginLandmarkEdit(name);
                            },
                            onLandmarkDrag: (name, imageX, imageY) {
                              final state = _correctionState;
                              if (state == null) return;
                              state.updateLandmarkPosition(name, imageX, imageY);
                              setState(() {});
                            },
                            onLandmarkEditEnd: () {
                              _onCorrectionSettled();
                            },
                          )
                        else
                          ClipRRect(
                            borderRadius: BorderRadius.circular(
                              AppSpacing.radiusSm,
                            ),
                            child: ColoredBox(
                              color: AppColors.radiographBg,
                              child: SizedBox(
                                height: overlayHeight,
                                child: InteractiveViewer(
                                  minScale: 1.0,
                                  maxScale: 4.0,
                                  child: Image.memory(
                                    widget.radiograph.bytes,
                                    fit: BoxFit.contain,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        if (canCorrect) ...[
                          const SizedBox(height: AppSpacing.sm),
                          OutlinedButton.icon(
                            key: const Key('toggle_correction_mode_button'),
                            onPressed: _toggleCorrectionMode,
                            icon: Icon(
                              _correctionMode
                                  ? Icons.check_outlined
                                  : Icons.edit_outlined,
                            ),
                            label: Text(
                              _correctionMode
                                  ? 'Terminer la correction'
                                  : 'Corriger les landmarks',
                            ),
                          ),
                        ],
                        if (_correctionMode && correction != null) ...[
                          const SizedBox(height: AppSpacing.sm),
                          _CorrectionStatusBar(
                            selectedName: _selectedLandmarkName,
                            globalStatus: correction.globalStatus,
                            correctedCount: correction.correctedCount,
                          ),
                          const SizedBox(height: AppSpacing.sm),
                          Row(
                            children: [
                              Expanded(
                                child: OutlinedButton.icon(
                                  key: const Key('undo_correction_button'),
                                  onPressed: correction.canUndo
                                      ? _undoCorrection
                                      : null,
                                  icon: const Icon(Icons.undo),
                                  label: const Text('Annuler'),
                                ),
                              ),
                              const SizedBox(width: AppSpacing.sm),
                              Expanded(
                                child: OutlinedButton.icon(
                                  key: const Key('reset_correction_button'),
                                  onPressed: (correction.hasCorrections ||
                                          correction.canUndo)
                                      ? _confirmAndResetCorrection
                                      : null,
                                  icon: const Icon(Icons.restart_alt),
                                  label: const Text('Réinitialiser'),
                                ),
                              ),
                            ],
                          ),
                        ],
                        const SizedBox(height: AppSpacing.sm),
                        LandmarkLegend(
                          showIt: hasIt,
                          showReview: hasReview,
                          showUnavailableNote: hasUnavailableIt,
                          showCorrected: showCorrected || _correctionMode,
                          correctionMode: _correctionMode,
                        ),
                        if (_overlaySize?.dimensionMismatch == true) ...[
                          const SizedBox(height: AppSpacing.sm),
                          _DimensionMismatchBanner(
                            detail: _overlaySize!.mismatchDetail!,
                          ),
                        ],
                        const SizedBox(height: AppSpacing.sm),
                        ModelVersionLabel(
                          modelVersion: widget.result.modelVersion,
                        ),
                        const SizedBox(height: AppSpacing.lg),
                        _StatusBanner(result: widget.result),
                        const SizedBox(height: AppSpacing.xl),
                        if (measurements != null) ...[
                          Text(
                            'Mesures',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          if (_recomputing) ...[
                            const SizedBox(height: AppSpacing.sm),
                            const Row(
                              key: Key('recompute_loading_row'),
                              children: [
                                SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                ),
                                SizedBox(width: AppSpacing.sm),
                                Expanded(
                                  child: Text('Recalcul des mesures…'),
                                ),
                              ],
                            ),
                          ],
                          if (_recomputeError != null) ...[
                            const SizedBox(height: AppSpacing.sm),
                            Text(
                              key: const Key('recompute_error_text'),
                              _recomputeError!,
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(color: AppColors.error),
                            ),
                          ],
                          const SizedBox(height: AppSpacing.md),
                          SideMeasurementsSection(
                            title: 'Hanche droite',
                            side: measurements.right,
                          ),
                          const SizedBox(height: AppSpacing.xl),
                          SideMeasurementsSection(
                            title: 'Hanche gauche',
                            side: measurements.left,
                          ),
                        ],
                        if (detection != null && detection.hasItLandmarks) ...[
                          const SizedBox(height: AppSpacing.xl),
                          ITStatusSection(itLandmarks: detection.itLandmarks),
                        ],
                        if (detection != null) ...[
                          const SizedBox(height: AppSpacing.xl),
                          _DetectionSection(detection: detection),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
            ),
            DecoratedBox(
              decoration: const BoxDecoration(
                color: AppColors.surfaceCard,
                border: Border(top: BorderSide(color: AppColors.border)),
              ),
              child: SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(
                    AppSpacing.pagePadding,
                    AppSpacing.md,
                    AppSpacing.pagePadding,
                    AppSpacing.lg,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      OutlinedButton.icon(
                        key: const Key('export_report_button'),
                        onPressed: _exporting ? null : _exportReport,
                        icon: Icon(
                          _exporting
                              ? Icons.hourglass_top
                              : Icons.picture_as_pdf_outlined,
                        ),
                        label: Text(
                          _exporting
                              ? 'Génération du rapport…'
                              : 'Exporter le rapport',
                        ),
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      FilledButton.icon(
                        key: const Key('new_import_button'),
                        onPressed: _exporting
                            ? null
                            : () {
                                Navigator.of(context)
                                    .popUntil((route) => route.isFirst);
                              },
                        icon: const Icon(Icons.upload_file_outlined),
                        label: const Text('Nouvelle radiographie'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CorrectionStatusBar extends StatelessWidget {
  const _CorrectionStatusBar({
    required this.selectedName,
    required this.globalStatus,
    required this.correctedCount,
  });

  final String? selectedName;
  final CorrectionSessionStatus globalStatus;
  final int correctedCount;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final sessionLabel = globalStatus == CorrectionSessionStatus.aiOnly
        ? 'IA uniquement'
        : 'Corrigés : $correctedCount';
    final selectionLabel = selectedName == null
        ? 'Aucun repère sélectionné'
        : 'Sélection : $selectedName';

    return Container(
      key: const Key('correction_status_bar'),
      padding: const EdgeInsets.all(AppSpacing.sm),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: AppColors.border),
      ),
      child: Text(
        '$selectionLabel · $sessionLabel',
        style: theme.textTheme.bodySmall?.copyWith(
          color: AppColors.textSecondary,
        ),
      ),
    );
  }
}

class _DimensionMismatchBanner extends StatelessWidget {
  const _DimensionMismatchBanner({required this.detail});

  final String detail;

  @override
  Widget build(BuildContext context) {
    return Container(
      key: const Key('dimension_mismatch_banner'),
      padding: const EdgeInsets.all(AppSpacing.sm),
      decoration: BoxDecoration(
        color: AppColors.warningSoft,
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: AppColors.warning.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.info_outline, size: 16, color: AppColors.warning),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              detail,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.warning,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusBanner extends StatelessWidget {
  const _StatusBanner({required this.result});

  final AnalysisResult result;

  @override
  Widget build(BuildContext context) {
    final status = ResultPresentationStatus.fromAnalysis(result);
    final Color color;
    final IconData icon;
    final Key bannerKey;

    switch (status.kind) {
      case ResultPresentationKind.success:
        color = AppColors.success;
        icon = Icons.check_circle_outline;
        bannerKey = const Key('results_status_success');
      case ResultPresentationKind.review:
        color = AppColors.warning;
        icon = Icons.warning_amber_rounded;
        bannerKey = const Key('results_status_review');
      case ResultPresentationKind.incomplete:
        color = AppColors.textSecondary;
        icon = Icons.info_outline;
        bannerKey = const Key('results_status_incomplete');
    }

    return Semantics(
      liveRegion: true,
      label: status.detail == null
          ? status.title
          : '${status.title}. ${status.detail}',
      child: Container(
        key: bannerKey,
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color),
            const SizedBox(width: AppSpacing.sm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    status.title,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: color,
                        ),
                  ),
                  if (status.detail != null) ...[
                    const SizedBox(height: AppSpacing.xs),
                    Text(
                      status.detail!,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: color,
                          ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DetectionSection extends StatelessWidget {
  const _DetectionSection({required this.detection});

  final DetectionInfo detection;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final bbox = detection.boundingBox;
    final itCount = detection.itLandmarks.length;

    return Theme(
      data: theme.copyWith(dividerColor: Colors.transparent),
      child: Material(
        key: const Key('detection_section'),
        color: AppColors.surfaceCard,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
          side: const BorderSide(color: AppColors.border),
        ),
        clipBehavior: Clip.antiAlias,
        child: ExpansionTile(
          key: const Key('detection_expansion_tile'),
          initiallyExpanded: false,
          tilePadding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
          childrenPadding: const EdgeInsets.fromLTRB(
            AppSpacing.md,
            0,
            AppSpacing.md,
            AppSpacing.md,
          ),
          title: Text(
            'Détails techniques',
            style: theme.textTheme.titleSmall,
          ),
          subtitle: Text(
            'Informations de détection avancées',
            style: theme.textTheme.bodySmall,
          ),
          children: [
            _InfoRow(
              label: 'Landmarks MVP',
              value: '${detection.landmarkCount}',
            ),
            if (itCount > 0) ...[
              const SizedBox(height: AppSpacing.xs),
              _InfoRow(
                label: 'Landmarks IT',
                value: '$itCount (IT_R, IT_L)',
              ),
            ],
            const SizedBox(height: AppSpacing.xs),
            _InfoRow(
              label: 'BBox',
              value: bbox != null
                  ? 'x1=${bbox['x1']?.toStringAsFixed(0)}, '
                      'y1=${bbox['y1']?.toStringAsFixed(0)}, '
                      'x2=${bbox['x2']?.toStringAsFixed(0)}, '
                      'y2=${bbox['y2']?.toStringAsFixed(0)}'
                  : '—',
            ),
            const SizedBox(height: AppSpacing.xs),
            _InfoRow(
              label: 'Refinement ASL_L',
              value: detection.refinementEnabled
                  ? (detection.refinementApplied ? 'Activé' : 'Non appliqué')
                  : 'Désactivé',
            ),
            if (detection.coordinateSpace != null) ...[
              const SizedBox(height: AppSpacing.xs),
              _InfoRow(
                label: 'Espace coordonnées',
                value:
                    '${detection.coordinateSpace!.imageWidth}×'
                    '${detection.coordinateSpace!.imageHeight} px',
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Flexible(
          flex: 2,
          child: Text(
            label,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
        const SizedBox(width: AppSpacing.sm),
        Expanded(
          flex: 3,
          child: Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ),
      ],
    );
  }
}
