import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Cadre de guidage visuel uniquement — ne recadre ni ne transforme l'image.
///
/// Aide au cadrage de la radiographie ; ce n'est pas une limite de mesure clinique.
class CameraFramingGuide extends StatelessWidget {
  const CameraFramingGuide({super.key});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Guide de cadrage de la radiographie',
      child: LayoutBuilder(
        builder: (context, constraints) {
          final maxW = constraints.maxWidth.isFinite ? constraints.maxWidth : 280.0;
          final maxH = constraints.maxHeight.isFinite ? constraints.maxHeight : 180.0;
          final side = math.min(maxW, maxH);
          if (side <= 0) return const SizedBox.shrink();

          final frameW = side * 0.92;
          final frameH = math.min(frameW * 0.72, maxH * 0.95);

          return Center(
            child: SizedBox(
              width: frameW,
              height: frameH,
              child: CustomPaint(painter: _FramingGuidePainter()),
            ),
          );
        },
      ),
    );
  }
}

/// Overlay décoratif sur l'aperçu capturé — n'altère pas les octets.
class CameraFramingOverlay extends StatelessWidget {
  const CameraFramingOverlay({super.key});

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: CustomPaint(
          painter: _FramingGuidePainter(strokeOpacity: 0.55),
          child: const SizedBox.expand(),
        ),
      ),
    );
  }
}

class _FramingGuidePainter extends CustomPainter {
  _FramingGuidePainter({this.strokeOpacity = 0.9});

  final double strokeOpacity;

  @override
  void paint(Canvas canvas, Size size) {
    if (size.width <= 0 || size.height <= 0) return;

    final rect = Offset.zero & size;
    final rrect = RRect.fromRectAndRadius(rect, const Radius.circular(8));

    final border = Paint()
      ..color = Colors.white.withValues(alpha: strokeOpacity * 0.55)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    final corner = Paint()
      ..color = AppColors.primary.withValues(alpha: strokeOpacity)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.square;

    canvas.drawRRect(rrect, border);

    final len = math.min(22.0, math.min(size.width, size.height) * 0.2);
    const inset = 2.0;
    final left = inset;
    final top = inset;
    final right = size.width - inset;
    final bottom = size.height - inset;

    canvas.drawLine(Offset(left, top), Offset(left + len, top), corner);
    canvas.drawLine(Offset(left, top), Offset(left, top + len), corner);

    canvas.drawLine(Offset(right, top), Offset(right - len, top), corner);
    canvas.drawLine(Offset(right, top), Offset(right, top + len), corner);

    canvas.drawLine(Offset(left, bottom), Offset(left + len, bottom), corner);
    canvas.drawLine(Offset(left, bottom), Offset(left, bottom - len), corner);

    canvas.drawLine(Offset(right, bottom), Offset(right - len, bottom), corner);
    canvas.drawLine(Offset(right, bottom), Offset(right, bottom - len), corner);
  }

  @override
  bool shouldRepaint(covariant _FramingGuidePainter oldDelegate) {
    return oldDelegate.strokeOpacity != strokeOpacity;
  }
}
