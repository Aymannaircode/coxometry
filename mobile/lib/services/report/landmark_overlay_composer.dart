import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';

import '../../models/it_landmark.dart';
import '../../models/landmark.dart';
import '../../widgets/image_contain_layout.dart';
import '../../widgets/landmark_overlay.dart';

/// Compose une image PNG (radiographie + landmarks) pour le rapport PDF.
///
/// Réutilise [ImageContainLayout] et [LandmarkPainter] — même mapping
/// pixels image originale → affichage que l'écran Results.
class LandmarkOverlayComposer {
  const LandmarkOverlayComposer();

  /// Génère un PNG avec aspect ratio préservé (pas d'étirement).
  ///
  /// [imageSize] doit être la taille résolue via [resolveOverlayImageSize]
  /// (préférence `coordinate_space` backend).
  Future<OverlayComposeResult> composePng({
    required Uint8List imageBytes,
    required Size imageSize,
    List<Landmark> landmarks = const [],
    List<ITLandmark> itLandmarks = const [],
    double maxEdge = 1600,
    bool showLabels = true,
    double pointRadius = 4.5,
  }) async {
    final codec = await ui.instantiateImageCodec(imageBytes);
    final frame = await codec.getNextFrame();
    final decoded = frame.image;

    final srcW = imageSize.width > 0 && imageSize.width.isFinite
        ? imageSize.width
        : decoded.width.toDouble();
    final srcH = imageSize.height > 0 && imageSize.height.isFinite
        ? imageSize.height
        : decoded.height.toDouble();

    final longest = srcW > srcH ? srcW : srcH;
    final outScale = longest > maxEdge ? maxEdge / longest : 1.0;
    final outW = srcW * outScale;
    final outH = srcH * outScale;

    final layout = ImageContainLayout.compute(
      boxSize: Size(outW, outH),
      imageSize: Size(srcW, srcH),
    );

    final mvp = landmarks.where((l) => l.isDrawable).toList(growable: false);
    final it = itLandmarks.where((l) => l.isDrawable).toList(growable: false);

    final recorder = ui.PictureRecorder();
    final canvas = Canvas(recorder);

    // Fond clinique (letterbox éventuel — normalement offset nul si ratios égaux).
    canvas.drawRect(
      Rect.fromLTWH(0, 0, outW, outH),
      Paint()..color = const Color(0xFF12171C),
    );

    // Même principe que Results : image en contain dans la boîte.
    paintImage(
      canvas: canvas,
      rect: Rect.fromLTWH(0, 0, outW, outH),
      image: decoded,
      fit: BoxFit.contain,
      filterQuality: FilterQuality.medium,
    );

    final scaledRadius = (pointRadius * outScale).clamp(2.5, 8.0);
    LandmarkPainter(
      mvpLandmarks: mvp,
      itLandmarks: it,
      layout: layout,
      showLabels: showLabels,
      pointRadius: scaledRadius,
    ).paint(canvas, Size(outW, outH));

    final picture = recorder.endRecording();
    final rendered = await picture.toImage(outW.ceil(), outH.ceil());
    final byteData = await rendered.toByteData(format: ui.ImageByteFormat.png);
    decoded.dispose();
    rendered.dispose();

    if (byteData == null) {
      throw StateError('Échec de la composition de l\'image du rapport.');
    }

    return OverlayComposeResult(
      pngBytes: byteData.buffer.asUint8List(),
      width: outW.ceil(),
      height: outH.ceil(),
      sourceWidth: srcW,
      sourceHeight: srcH,
      drawableMvpCount: mvp.length,
      drawableItCount: it.length,
      layout: layout,
    );
  }
}

/// Résultat de composition overlay (tests + embedding PDF).
class OverlayComposeResult {
  const OverlayComposeResult({
    required this.pngBytes,
    required this.width,
    required this.height,
    required this.sourceWidth,
    required this.sourceHeight,
    required this.drawableMvpCount,
    required this.drawableItCount,
    required this.layout,
  });

  final Uint8List pngBytes;
  final int width;
  final int height;
  final double sourceWidth;
  final double sourceHeight;
  final int drawableMvpCount;
  final int drawableItCount;
  final ImageContainLayout layout;

  /// Ratio de sortie ≈ ratio source (tolérance pour arrondi pixels).
  bool get aspectRatioPreserved {
    if (sourceWidth <= 0 || sourceHeight <= 0 || width <= 0 || height <= 0) {
      return false;
    }
    final src = sourceWidth / sourceHeight;
    final out = width / height;
    return (src - out).abs() < 0.02;
  }
}
