import 'package:flutter/material.dart';

import '../services/radiograph_picker.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import 'camera_guidance_screen.dart';
import 'preview_screen.dart';
import 'server_connection_screen.dart';

/// Écran d'accueil — import galerie ou flux caméra guidé.
class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    required this.picker,
  });

  final RadiographPicker picker;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String? _error;
  bool _busy = false;

  Future<void> _pickGallery() async {
    if (_busy) return;
    setState(() {
      _busy = true;
      _error = null;
    });

    try {
      final selected = await widget.picker.pickFromGallery();
      if (!mounted) return;
      if (selected == null) return;

      await Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => PreviewScreen(radiograph: selected),
        ),
      );
    } on RadiographPickerException catch (e) {
      if (!mounted) return;
      setState(() => _error = e.message);
    } catch (_) {
      if (!mounted) return;
      setState(
        () => _error =
            'Échec de la sélection. Réessayez ou choisissez une autre image.',
      );
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _openCameraFlow() async {
    if (_busy) return;
    setState(() => _error = null);

    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => CameraGuidanceScreen(picker: widget.picker),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Coxométrie'),
        actions: [
          IconButton(
            key: const Key('server_connection_button'),
            tooltip: 'Connexion serveur',
            icon: const Icon(Icons.settings_ethernet_outlined),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => const ServerConnectionScreen(),
                ),
              );
            },
          ),
        ],
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
                  const Spacer(flex: 2),
                  Icon(
                    Icons.monitor_heart_outlined,
                    size: 64,
                    color: AppColors.primary.withValues(alpha: 0.85),
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  Text(
                    'Analyse coxométrique',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.headlineSmall,
                  ),
                  const SizedBox(height: AppSpacing.md),
                  Text(
                    'Importez une radiographie du bassin pour calculer '
                    'VCE, Tönnis et CCD à partir de la détection automatique '
                    'des landmarks.',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                  const Spacer(flex: 3),
                  Semantics(
                    button: true,
                    label: 'Importer une image',
                    child: FilledButton.icon(
                      key: const Key('import_gallery_button'),
                      onPressed: _busy ? null : _pickGallery,
                      icon: const Icon(Icons.photo_library_outlined),
                      label: const Text('Importer une image'),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.md),
                  Semantics(
                    button: true,
                    label: 'Prendre une photo',
                    child: OutlinedButton.icon(
                      key: const Key('import_camera_button'),
                      onPressed: _busy ? null : _openCameraFlow,
                      icon: const Icon(Icons.photo_camera_outlined),
                      label: const Text('Prendre une photo'),
                    ),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: AppSpacing.lg),
                    _ErrorBanner(message: _error!),
                  ],
                  const Spacer(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.errorSoft,
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: AppColors.error.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.error_outline, color: AppColors.error, size: 20),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.error,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}
