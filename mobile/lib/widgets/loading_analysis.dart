import 'dart:typed_data';

import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import 'radiograph_image_view.dart';

/// Écran de chargement pendant l'analyse — empêche les doubles requêtes côté parent.
class LoadingAnalysis extends StatelessWidget {
  const LoadingAnalysis({
    super.key,
    required this.imageBytes,
    this.message = 'Analyse de la radiographie…',
  });

  final Uint8List imageBytes;
  final String message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        RadiographImageView(bytes: imageBytes),
        const SizedBox(height: AppSpacing.xl),
        const Center(
          child: SizedBox(
            width: 40,
            height: 40,
            child: CircularProgressIndicator(strokeWidth: 3),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        Text(
          message,
          key: const Key('analysis_loading_message'),
          textAlign: TextAlign.center,
          style: theme.textTheme.bodyLarge?.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(
          'Détection des repères anatomiques et calcul des mesures en cours.',
          key: const Key('analysis_loading_subtitle'),
          textAlign: TextAlign.center,
          style: theme.textTheme.bodySmall,
        ),
      ],
    );
  }
}
