import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';

import '../models/it_landmark.dart';
import '../models/landmark.dart';
import '../models/landmark_correction_state.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import 'image_contain_layout.dart';
import 'landmark_hit_test.dart';

/// Superpose les landmarks MVP (0–13) et IT (14–15) sur une radiographie.
///
/// Les coordonnées sont en pixels image ; l'affichage utilise `BoxFit.contain`
/// pour adapter correctement à la taille du widget.
///
/// Zoom/pan via [InteractiveViewer] sur l'arbre image + peinture commun —
/// pas de transform séparée (alignement conservé).
///
/// Mode correction (Phase 10H) : pan/zoom désactivés ; drag des 6 landmarks
/// corrigibles en convertissant via [ImageContainLayout.toImage].
class LandmarkOverlay extends StatefulWidget {
  const LandmarkOverlay({
    super.key,
    required this.bytes,
    required this.imageSize,
    this.landmarks = const [],
    this.itLandmarks = const [],
    this.fit = BoxFit.contain,
    this.showLabels = true,
    this.pointRadius = 4.5,
    this.height = AppSpacing.radiographHeight,
    this.backgroundColor = AppColors.radiographBg,
    this.borderRadius = AppSpacing.radiusSm,
    this.enableInteraction = true,
    this.correctionMode = false,
    this.landmarkStatuses = const {},
    this.selectedLandmarkName,
    this.onSelectedLandmarkChanged,
    this.onLandmarkEditBegin,
    this.onLandmarkDrag,
    this.onLandmarkEditEnd,
  }) : assert(
          fit == BoxFit.contain,
          'Seul BoxFit.contain est supporté pour l\'instant.',
        );

  final Uint8List bytes;
  final Size imageSize;
  final List<Landmark> landmarks;
  final List<ITLandmark> itLandmarks;
  final BoxFit fit;
  final bool showLabels;
  final double pointRadius;
  final double height;
  final Color backgroundColor;
  final double borderRadius;

  /// Active pinch-zoom / pan ([InteractiveViewer]) hors mode correction.
  final bool enableInteraction;

  /// Active la sélection / drag des landmarks corrigibles.
  final bool correctionMode;

  /// Statuts AI / CORRECTED indexés par nom.
  final Map<String, LandmarkStatus> landmarkStatuses;

  final String? selectedLandmarkName;
  final ValueChanged<String?>? onSelectedLandmarkChanged;

  /// Appelé une fois au début d'un drag (pour undo).
  final ValueChanged<String>? onLandmarkEditBegin;

  /// Appelé à chaque déplacement avec des coordonnées **image**.
  final void Function(String name, double imageX, double imageY)? onLandmarkDrag;

  final VoidCallback? onLandmarkEditEnd;

  @override
  State<LandmarkOverlay> createState() => LandmarkOverlayState();
}

/// État public pour les tests (hit-test / drag programmatique).
class LandmarkOverlayState extends State<LandmarkOverlay> {
  String? _draggingName;
  ImageContainLayout? _lastLayout;

  List<Landmark> get drawableMvpLandmarks =>
      widget.landmarks.where((l) => l.isDrawable).toList(growable: false);

  List<ITLandmark> get drawableItLandmarks =>
      widget.itLandmarks.where((l) => l.isDrawable).toList(growable: false);

  bool get hasDrawableLandmarks =>
      drawableMvpLandmarks.isNotEmpty || drawableItLandmarks.isNotEmpty;

  bool get isDragging => _draggingName != null;

  ImageContainLayout? get lastLayout => _lastLayout;

  /// Hit-test en coordonnées locales du canvas contain (pour tests).
  String? hitTestLocal(Offset localDisplay) {
    final layout = _lastLayout;
    if (layout == null) return null;
    return findCorrectableLandmarkAt(
      localDisplay: localDisplay,
      landmarks: widget.landmarks,
      layout: layout,
    );
  }

  /// Simule un drag jusqu'à [localDisplay] (espace contain) — tests.
  bool applyDragToLocalDisplay(Offset localDisplay, {String? name}) {
    final dragName =
        name ?? _draggingName ?? widget.selectedLandmarkName;
    final layout = _lastLayout;
    if (dragName == null || layout == null) return false;
    if (!LandmarkCorrectionState.correctableNames.contains(dragName)) {
      return false;
    }

    final image = localDisplayToImage(layout, localDisplay);
    widget.onLandmarkDrag?.call(dragName, image.dx, image.dy);
    return true;
  }

  void _onPointerDown(Offset local, ImageContainLayout layout) {
    final hit = findCorrectableLandmarkAt(
      localDisplay: local,
      landmarks: widget.landmarks,
      layout: layout,
    );
    if (hit == null) {
      widget.onSelectedLandmarkChanged?.call(null);
      return;
    }
    setState(() => _draggingName = hit);
    widget.onSelectedLandmarkChanged?.call(hit);
    widget.onLandmarkEditBegin?.call(hit);
  }

  void _onPointerMove(Offset local, ImageContainLayout layout) {
    final name = _draggingName;
    if (name == null) return;
    final image = localDisplayToImage(layout, local);
    widget.onLandmarkDrag?.call(name, image.dx, image.dy);
  }

  void _onPointerUp() {
    if (_draggingName == null) return;
    setState(() => _draggingName = null);
    widget.onLandmarkEditEnd?.call();
  }

  @override
  Widget build(BuildContext context) {
    final panZoomEnabled = widget.enableInteraction &&
        !widget.correctionMode &&
        _draggingName == null;

    final semanticsLabel = widget.correctionMode
        ? 'Radiographie en mode correction des repères. '
            'Toucher un repère corrigible pour le sélectionner et le déplacer.'
        : 'Radiographie avec repères anatomiques. '
            'Pincer pour zoomer, faire glisser pour déplacer.';

    final canvas = _OverlayCanvas(
      bytes: widget.bytes,
      imageSize: widget.imageSize,
      fit: widget.fit,
      showLabels: widget.showLabels,
      pointRadius: widget.pointRadius,
      mvp: drawableMvpLandmarks,
      it: drawableItLandmarks,
      hasDrawable: hasDrawableLandmarks,
      correctionMode: widget.correctionMode,
      landmarkStatuses: widget.landmarkStatuses,
      selectedLandmarkName: widget.selectedLandmarkName,
      onLayoutComputed: (layout) => _lastLayout = layout,
      onPointerDown: widget.correctionMode
          ? (local, layout) => _onPointerDown(local, layout)
          : null,
      onPointerMove: widget.correctionMode
          ? (local, layout) => _onPointerMove(local, layout)
          : null,
      onPointerUp: widget.correctionMode ? (_) => _onPointerUp() : null,
    );

    return Semantics(
      label: semanticsLabel,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(widget.borderRadius),
        child: ColoredBox(
          color: widget.backgroundColor,
          child: SizedBox(
            height: widget.height,
            width: double.infinity,
            child: widget.enableInteraction || widget.correctionMode
                ? InteractiveViewer(
                    key: const Key('landmark_interactive_viewer'),
                    minScale: 1.0,
                    maxScale: 4.0,
                    clipBehavior: Clip.hardEdge,
                    panEnabled: panZoomEnabled,
                    scaleEnabled: panZoomEnabled,
                    child: canvas,
                  )
                : canvas,
          ),
        ),
      ),
    );
  }
}

class _OverlayCanvas extends StatelessWidget {
  const _OverlayCanvas({
    required this.bytes,
    required this.imageSize,
    required this.fit,
    required this.showLabels,
    required this.pointRadius,
    required this.mvp,
    required this.it,
    required this.hasDrawable,
    required this.correctionMode,
    required this.landmarkStatuses,
    required this.selectedLandmarkName,
    required this.onLayoutComputed,
    this.onPointerDown,
    this.onPointerMove,
    this.onPointerUp,
  });

  final Uint8List bytes;
  final Size imageSize;
  final BoxFit fit;
  final bool showLabels;
  final double pointRadius;
  final List<Landmark> mvp;
  final List<ITLandmark> it;
  final bool hasDrawable;
  final bool correctionMode;
  final Map<String, LandmarkStatus> landmarkStatuses;
  final String? selectedLandmarkName;
  final ValueChanged<ImageContainLayout> onLayoutComputed;
  final void Function(Offset local, ImageContainLayout layout)? onPointerDown;
  final void Function(Offset local, ImageContainLayout layout)? onPointerMove;
  final ValueChanged<Offset>? onPointerUp;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final boxSize = Size(constraints.maxWidth, constraints.maxHeight);
        final layout = ImageContainLayout.compute(
          boxSize: boxSize,
          imageSize: imageSize,
        );
        onLayoutComputed(layout);

        Widget stack = Stack(
          fit: StackFit.expand,
          children: [
            Image.memory(
              bytes,
              fit: fit,
              gaplessPlayback: true,
              errorBuilder: (_, __, ___) => const Center(
                child: Icon(
                  Icons.broken_image_outlined,
                  color: Colors.white54,
                ),
              ),
            ),
            if (hasDrawable)
              CustomPaint(
                key: const Key('landmark_painter'),
                painter: LandmarkPainter(
                  mvpLandmarks: mvp,
                  itLandmarks: it,
                  layout: layout,
                  showLabels: showLabels,
                  pointRadius: pointRadius,
                  landmarkStatuses: landmarkStatuses,
                  selectedLandmarkName: selectedLandmarkName,
                  correctionMode: correctionMode,
                ),
              ),
          ],
        );

        if (correctionMode &&
            (onPointerDown != null ||
                onPointerMove != null ||
                onPointerUp != null)) {
          stack = Listener(
            key: const Key('landmark_correction_listener'),
            behavior: HitTestBehavior.opaque,
            onPointerDown: (event) =>
                onPointerDown?.call(event.localPosition, layout),
            onPointerMove: (event) =>
                onPointerMove?.call(event.localPosition, layout),
            onPointerUp: (event) => onPointerUp?.call(event.localPosition),
            onPointerCancel: (event) => onPointerUp?.call(event.localPosition),
            child: stack,
          );
        }

        return stack;
      },
    );
  }
}

/// Peint les landmarks dans l'espace widget via [ImageContainLayout].
class LandmarkPainter extends CustomPainter {
  LandmarkPainter({
    required this.mvpLandmarks,
    required this.itLandmarks,
    required this.layout,
    required this.showLabels,
    required this.pointRadius,
    this.landmarkStatuses = const {},
    this.selectedLandmarkName,
    this.correctionMode = false,
  });

  final List<Landmark> mvpLandmarks;
  final List<ITLandmark> itLandmarks;
  final ImageContainLayout layout;
  final bool showLabels;
  final double pointRadius;
  final Map<String, LandmarkStatus> landmarkStatuses;
  final String? selectedLandmarkName;
  final bool correctionMode;

  /// Rétrocompatibilité tests : union MVP + IT convertis en [Landmark].
  List<Landmark> get landmarks => [
        ...mvpLandmarks,
        ...itLandmarks.map(
          (it) => Landmark(
            name: it.name,
            x: it.x,
            y: it.y,
            confidence: it.confidence,
            visibility: it.v,
          ),
        ),
      ];

  @override
  void paint(Canvas canvas, Size size) {
    for (final landmark in mvpLandmarks) {
      _paintMvpLandmark(canvas, landmark);
    }
    for (final it in itLandmarks) {
      _paintItLandmark(canvas, it);
    }
  }

  void _paintMvpLandmark(Canvas canvas, Landmark landmark) {
    final x = landmark.x;
    final y = landmark.y;
    if (x == null || y == null) return;
    if (!x.isFinite || !y.isFinite) return;

    final point = layout.toDisplay(x, y);
    final status = landmarkStatuses[landmark.name] ?? LandmarkStatus.ai;
    final isCorrected = status == LandmarkStatus.corrected;
    final isSelected = landmark.name == selectedLandmarkName;
    final isCorrectable =
        LandmarkCorrectionState.correctableNames.contains(landmark.name);

    final fillColor =
        isCorrected ? AppColors.landmarkCorrected : AppColors.landmark;

    final fillPaint = Paint()
      ..color = fillColor
      ..style = PaintingStyle.fill;
    final strokePaint = Paint()
      ..color = AppColors.landmarkStroke
      ..style = PaintingStyle.stroke
      ..strokeWidth = isSelected ? 2.0 : 1.5;

    final radius = isSelected ? pointRadius + 1.5 : pointRadius;
    canvas.drawCircle(point, radius, fillPaint);
    canvas.drawCircle(point, radius, strokePaint);

    if (isSelected) {
      final ring = Paint()
        ..color = AppColors.landmarkSelectedRing
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0;
      canvas.drawCircle(point, radius + 4, ring);
    } else if (correctionMode && isCorrectable && !isCorrected) {
      final affordance = Paint()
        ..color = AppColors.landmark.withValues(alpha: 0.35)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.0;
      canvas.drawCircle(point, pointRadius + 3, affordance);
    }

    if (showLabels && landmark.name.isNotEmpty) {
      final label = isCorrected ? '${landmark.name} · Corrigé' : landmark.name;
      _drawLabel(canvas, point, label, radius);
    }
  }

  void _paintItLandmark(Canvas canvas, ITLandmark it) {
    final x = it.x;
    final y = it.y;
    if (x == null || y == null) return;
    if (!x.isFinite || !y.isFinite) return;

    final point = layout.toDisplay(x, y);
    final isReview = it.isReview;
    final fillColor = isReview ? AppColors.itLandmarkReview : AppColors.itLandmark;

    final fillPaint = Paint()
      ..color = fillColor
      ..style = PaintingStyle.fill;
    final strokePaint = Paint()
      ..color = AppColors.landmarkStroke
      ..style = PaintingStyle.stroke
      ..strokeWidth = isReview ? 2.0 : 1.5;

    canvas.drawCircle(point, pointRadius, fillPaint);
    canvas.drawCircle(point, pointRadius, strokePaint);

    if (isReview) {
      final ringPaint = Paint()
        ..color = AppColors.warning
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5;
      canvas.drawCircle(point, pointRadius + 3, ringPaint);
    }

    if (showLabels && it.name.isNotEmpty) {
      final label = isReview ? '${it.name} ⚠' : it.name;
      _drawLabel(canvas, point, label, pointRadius);
    }
  }

  void _drawLabel(Canvas canvas, Offset point, String name, double radius) {
    final builder = ui.ParagraphBuilder(
      ui.ParagraphStyle(fontSize: 10, maxLines: 1),
    )
      ..pushStyle(ui.TextStyle(color: const Color(0xFFFFFFFF)))
      ..addText(name);
    final paragraph = builder.build()
      ..layout(const ui.ParagraphConstraints(width: 140));

    final labelOrigin = Offset(
      point.dx + radius + 4,
      point.dy - paragraph.height / 2,
    );
    final rect = RRect.fromRectAndRadius(
      Rect.fromLTWH(
        labelOrigin.dx - 3,
        labelOrigin.dy - 1,
        paragraph.maxIntrinsicWidth + 6,
        paragraph.height + 2,
      ),
      const Radius.circular(3),
    );
    canvas.drawRRect(rect, Paint()..color = AppColors.landmarkLabelBg);
    canvas.drawParagraph(paragraph, labelOrigin);
  }

  @override
  bool shouldRepaint(covariant LandmarkPainter oldDelegate) {
    return oldDelegate.mvpLandmarks != mvpLandmarks ||
        oldDelegate.itLandmarks != itLandmarks ||
        oldDelegate.layout.scale != layout.scale ||
        oldDelegate.layout.offset != layout.offset ||
        oldDelegate.showLabels != showLabels ||
        oldDelegate.pointRadius != pointRadius ||
        oldDelegate.landmarkStatuses != landmarkStatuses ||
        oldDelegate.selectedLandmarkName != selectedLandmarkName ||
        oldDelegate.correctionMode != correctionMode;
  }
}
