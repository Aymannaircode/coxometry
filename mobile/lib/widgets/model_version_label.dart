import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../utils/model_version_label.dart';

/// Affichage discret de la version du modèle backend.
class ModelVersionLabel extends StatelessWidget {
  const ModelVersionLabel({
    super.key,
    required this.modelVersion,
  });

  final String? modelVersion;

  @override
  Widget build(BuildContext context) {
    return Text(
      'Modèle : ${formatModelVersion(modelVersion)}',
      key: const Key('model_version_label'),
      style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: AppColors.textMuted,
          ),
    );
  }
}
