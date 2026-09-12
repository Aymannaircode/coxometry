import 'package:flutter/material.dart';

import '../models/it_landmark.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import '../utils/it_quality_reason_label.dart';

/// Section IT_R / IT_L avec état de qualité QC V5.
class ITStatusSection extends StatelessWidget {
  const ITStatusSection({
    super.key,
    required this.itLandmarks,
  });

  final List<ITLandmark> itLandmarks;

  @override
  Widget build(BuildContext context) {
    if (itLandmarks.isEmpty) return const SizedBox.shrink();

    final theme = Theme.of(context);
    final sorted = List<ITLandmark>.from(itLandmarks)
      ..sort((a, b) => a.name.compareTo(b.name));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('Landmarks IT', style: theme.textTheme.titleMedium),
        const SizedBox(height: AppSpacing.sm),
        for (final it in sorted) ...[
          _ITStatusCard(it: it),
          if (it != sorted.last) const SizedBox(height: AppSpacing.sm),
        ],
      ],
    );
  }
}

class _ITStatusCard extends StatelessWidget {
  const _ITStatusCard({required this.it});

  final ITLandmark it;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final quality = it.quality;

    return Container(
      key: Key('it_status_${it.name}'),
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                it.name,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              _QualityBadge(quality: quality),
            ],
          ),
          if (it.confidence != null) ...[
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Confiance : ${it.confidence!.toStringAsFixed(2)}',
              style: theme.textTheme.bodyMedium,
            ),
          ],
          if (quality == ITQuality.review &&
              it.primaryQualityReason != null) ...[
            const SizedBox(height: AppSpacing.xs),
            Text(
              key: Key('it_reason_${it.name}'),
              'Motif de vérification : '
              '${formatItQualityReason(it.primaryQualityReason!)}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: AppColors.warning,
              ),
            ),
          ],
          if (quality == ITQuality.unavailable &&
              it.qualityReasons.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.xs),
            Text(
              key: Key('it_reason_${it.name}'),
              'Motif : ${formatItQualityReasons(it.qualityReasons)}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: AppColors.textMuted,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _QualityBadge extends StatelessWidget {
  const _QualityBadge({required this.quality});

  final ITQuality? quality;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    switch (quality) {
      case ITQuality.accept:
        return Semantics(
          label: 'Qualité : accepté',
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.circle, size: 10, color: AppColors.success),
              const SizedBox(width: AppSpacing.xs),
              Text(
                'Accepté',
                key: const Key('it_quality_accept'),
                style: theme.textTheme.labelMedium?.copyWith(
                  color: AppColors.success,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        );
      case ITQuality.review:
        return Semantics(
          label: 'Qualité : à revoir',
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.warning_amber_rounded,
                  size: 14, color: AppColors.warning),
              const SizedBox(width: AppSpacing.xs),
              Text(
                'À revoir',
                key: const Key('it_quality_review'),
                style: theme.textTheme.labelMedium?.copyWith(
                  color: AppColors.warning,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        );
      case ITQuality.unavailable:
      case null:
        return Semantics(
          label: 'Qualité : indisponible',
          child: Text(
            'Indisponible',
            key: const Key('it_quality_unavailable'),
            style: theme.textTheme.labelMedium?.copyWith(
              color: AppColors.textMuted,
              fontWeight: FontWeight.w600,
            ),
          ),
        );
    }
  }
}
