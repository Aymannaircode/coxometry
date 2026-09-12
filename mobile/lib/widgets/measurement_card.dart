import 'package:flutter/material.dart';

import '../models/measurement.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';

/// Carte affichant une mesure coxométrique (VCE, Tönnis ou CCD).
class MeasurementCard extends StatelessWidget {
  const MeasurementCard({
    super.key,
    required this.label,
    required this.measurement,
  });

  final String label;
  final Measurement measurement;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final available = measurement.available && measurement.valueDeg != null;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.sm + 2,
      ),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: theme.textTheme.titleSmall,
            ),
          ),
          Text(
            measurement.displayValue,
            key: Key('${label}_value'),
            style: theme.textTheme.titleMedium?.copyWith(
              color: available ? AppColors.primary : AppColors.textMuted,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
        ],
      ),
    );
  }
}

/// Groupe de mesures pour une hanche (VCE, Tönnis, CCD).
class SideMeasurementsSection extends StatelessWidget {
  const SideMeasurementsSection({
    super.key,
    required this.title,
    required this.side,
  });

  final String title;
  final SideMeasurements side;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(title, style: theme.textTheme.titleMedium),
        const SizedBox(height: AppSpacing.sm),
        MeasurementCard(label: 'VCE', measurement: side.vce),
        const SizedBox(height: AppSpacing.sm),
        MeasurementCard(label: 'Tönnis', measurement: side.tonnis),
        const SizedBox(height: AppSpacing.sm),
        MeasurementCard(label: 'CCD', measurement: side.ccd),
        if (_unavailableReasons.isNotEmpty) ...[
          const SizedBox(height: AppSpacing.sm),
          for (final entry in _unavailableReasons.entries)
            Padding(
              padding: const EdgeInsets.only(top: AppSpacing.xs),
              child: Text(
                '${entry.key} : ${entry.value}',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: AppColors.warning,
                ),
              ),
            ),
        ],
      ],
    );
  }

  Map<String, String> get _unavailableReasons {
    final reasons = <String, String>{};
    _maybeAdd(reasons, 'VCE', side.vce);
    _maybeAdd(reasons, 'Tönnis', side.tonnis);
    _maybeAdd(reasons, 'CCD', side.ccd);
    return reasons;
  }

  void _maybeAdd(Map<String, String> map, String label, Measurement m) {
    if (!m.available && m.reason != null && m.reason!.isNotEmpty) {
      map[label] = m.reason!;
    }
  }
}
