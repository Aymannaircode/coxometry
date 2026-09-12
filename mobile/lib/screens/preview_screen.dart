import 'package:flutter/material.dart';

import '../services/radiograph_picker.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import '../widgets/radiograph_image_view.dart';
import 'analysis_screen.dart';

/// Aperçu de la radiographie avant lancement de l'analyse.
class PreviewScreen extends StatelessWidget {
  const PreviewScreen({
    super.key,
    required this.radiograph,
  });

  final SelectedRadiograph radiograph;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Aperçu'),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: AppSpacing.contentMaxWidth),
            child: Padding(
              padding: const EdgeInsets.all(AppSpacing.pagePadding),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(
                    child: Center(
                      child: RadiographImageView(
                        bytes: radiograph.bytes,
                        height: 360,
                      ),
                    ),
                  ),
                  if (radiograph.width != null && radiograph.height != null) ...[
                    const SizedBox(height: AppSpacing.md),
                    Text(
                      '${radiograph.width} × ${radiograph.height} px · '
                      '${radiograph.sizeLabel}'
                      '${radiograph.orientationCorrected ? ' · orientation corrigée' : ''}',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppColors.textMuted,
                          ),
                    ),
                  ],
                  const SizedBox(height: AppSpacing.xl),
                  FilledButton.icon(
                    key: const Key('analyze_button'),
                    onPressed: () {
                      Navigator.of(context).pushReplacement(
                        MaterialPageRoute(
                          builder: (_) => AnalysisScreen(radiograph: radiograph),
                        ),
                      );
                    },
                    icon: const Icon(Icons.biotech_outlined),
                    label: const Text('Analyser'),
                  ),
                  const SizedBox(height: AppSpacing.md),
                  OutlinedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Retour'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
