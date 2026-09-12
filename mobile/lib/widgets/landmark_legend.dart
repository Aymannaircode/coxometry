import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';

/// Légende compacte pour l'overlay landmarks (clinique, non diagnostique).
class LandmarkLegend extends StatelessWidget {
  const LandmarkLegend({
    super.key,
    this.showIt = false,
    this.showReview = false,
    this.showUnavailableNote = false,
    this.showCorrected = false,
    this.correctionMode = false,
  });

  final bool showIt;
  final bool showReview;

  /// Indique qu'un landmark IT est indisponible (non affiché sur l'image).
  final bool showUnavailableNote;

  /// Affiche la couleur « Corrigé manuellement ».
  final bool showCorrected;

  /// Indique que le mode correction est actif.
  final bool correctionMode;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Semantics(
      label: 'Légende des repères anatomiques',
      child: Container(
        key: const Key('landmark_legend'),
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: AppColors.surfaceCard,
          borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Légende',
              style: theme.textTheme.titleSmall,
            ),
            const SizedBox(height: AppSpacing.sm),
            const _LegendRow(
              color: AppColors.landmark,
              label: 'Repères anatomiques (IA)',
            ),
            if (showCorrected) ...[
              const SizedBox(height: AppSpacing.xs),
              const _LegendRow(
                color: AppColors.landmarkCorrected,
                label: 'Corrigé manuellement',
              ),
            ],
            if (showIt) ...[
              const SizedBox(height: AppSpacing.xs),
              const _LegendRow(
                color: AppColors.itLandmark,
                label: 'Repères IT (tubérosité ischiatique)',
              ),
            ],
            if (showReview) ...[
              const SizedBox(height: AppSpacing.xs),
              const _LegendRow(
                color: AppColors.itLandmarkReview,
                icon: Icons.warning_amber_rounded,
                label: 'À revoir — vérification manuelle',
              ),
            ],
            if (showUnavailableNote) ...[
              const SizedBox(height: AppSpacing.xs),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.hide_source_outlined,
                    size: 14,
                    color: AppColors.textMuted,
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  Expanded(
                    child: Text(
                      'Indisponible : non affiché sur l\'image',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: AppColors.textMuted,
                      ),
                    ),
                  ),
                ],
              ),
            ],
            if (correctionMode) ...[
              const SizedBox(height: AppSpacing.sm),
              Text(
                key: const Key('correction_mode_hint'),
                'Mode correction : déplacez ASL, FSP ou FSD. Zoom désactivé.',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _LegendRow extends StatelessWidget {
  const _LegendRow({
    required this.color,
    required this.label,
    this.icon,
  });

  final Color color;
  final String label;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        if (icon != null)
          Icon(icon, size: 14, color: color)
        else
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.landmarkStroke, width: 1),
            ),
          ),
        const SizedBox(width: AppSpacing.sm),
        Expanded(
          child: Text(
            label,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
      ],
    );
  }
}
