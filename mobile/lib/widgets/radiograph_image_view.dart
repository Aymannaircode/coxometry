import 'dart:typed_data';

import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';

/// Aperçu d'une radiographie avec fond sombre clinique.
class RadiographImageView extends StatelessWidget {
  const RadiographImageView({
    super.key,
    required this.bytes,
    this.height = AppSpacing.radiographHeight,
    this.fit = BoxFit.contain,
  });

  final Uint8List bytes;
  final double height;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
      child: ColoredBox(
        color: AppColors.radiographBg,
        child: SizedBox(
          height: height,
          width: double.infinity,
          child: Image.memory(
            bytes,
            fit: fit,
            gaplessPlayback: true,
            errorBuilder: (_, __, ___) => const Center(
              child: Icon(
                Icons.broken_image_outlined,
                color: Colors.white54,
                size: 48,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
