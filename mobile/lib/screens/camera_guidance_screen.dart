import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../services/radiograph_picker.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import '../utils/camera_user_messages.dart';
import '../widgets/camera_framing_guide.dart';
import 'camera_confirm_screen.dart';

/// Guidage avant ouverture de la caméra système (Option B — sans package camera).
///
/// Le cadre est une aide visuelle uniquement ; la capture utilise [RadiographPicker]
/// puis le même chemin EXIF → aperçu → /analyze que la galerie.
class CameraGuidanceScreen extends StatefulWidget {
  const CameraGuidanceScreen({
    super.key,
    required this.picker,
  });

  final RadiographPicker picker;

  @override
  State<CameraGuidanceScreen> createState() => _CameraGuidanceScreenState();
}

class _CameraGuidanceScreenState extends State<CameraGuidanceScreen> {
  String? _error;
  bool _busy = false;

  Future<void> _openCamera() async {
    if (_busy) return;
    setState(() {
      _busy = true;
      _error = null;
    });

    try {
      final selected = await widget.picker.pickFromCamera();
      if (!mounted) return;
      if (selected == null) {
        // Annulation utilisateur — rester sur le guidage, pas d'erreur.
        return;
      }

      await Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => CameraConfirmScreen(
            picker: widget.picker,
            radiograph: selected,
          ),
        ),
      );
    } on RadiographPickerException catch (e) {
      if (!mounted) return;
      setState(() => _error = e.message);
    } on PlatformException catch (e) {
      if (!mounted) return;
      setState(() => _error = mapCameraPlatformException(e));
    } catch (_) {
      if (!mounted) return;
      setState(() => _error = CameraUserMessages.captureFailed);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Photo de radiographie'),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: AppSpacing.contentMaxWidth),
            child: LayoutBuilder(
              builder: (context, constraints) {
                final frameHeight =
                    (constraints.maxHeight * 0.32).clamp(140.0, 260.0);
                return SingleChildScrollView(
                  padding: const EdgeInsets.all(AppSpacing.pagePadding),
                  child: ConstrainedBox(
                    constraints: BoxConstraints(minHeight: constraints.maxHeight),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        SizedBox(
                          height: frameHeight,
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              color: AppColors.radiographBg,
                              borderRadius:
                                  BorderRadius.circular(AppSpacing.radiusMd),
                            ),
                            child: const Padding(
                              padding: EdgeInsets.all(AppSpacing.lg),
                              child: CameraFramingGuide(),
                            ),
                          ),
                        ),
                        const SizedBox(height: AppSpacing.md),
                        Text(
                          'Cadrez la radiographie',
                          key: const Key('camera_framing_title'),
                          textAlign: TextAlign.center,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: AppSpacing.sm),
                        Text(
                          'Placez la radiographie entière dans le cadre et évitez les reflets.',
                          textAlign: TextAlign.center,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: AppSpacing.md),
                        _GuidanceBullets(
                          items: const [
                            'Tenez le téléphone bien droit, parallèle au négatoscope',
                            'Incluez toute la radiographie du bassin',
                            'Évitez les reflets et l\'éblouissement',
                            'Stabilisez l\'image avant de photographier',
                          ],
                        ),
                        const SizedBox(height: AppSpacing.md),
                        const _PrototypeNotice(),
                        if (_error != null) ...[
                          const SizedBox(height: AppSpacing.md),
                          _CameraErrorBanner(
                            message: _error!,
                            onRetry: _busy ? null : _openCamera,
                          ),
                        ],
                        const SizedBox(height: AppSpacing.lg),
                        Semantics(
                          button: true,
                          label: 'Prendre une photo',
                          child: FilledButton.icon(
                            key: const Key('camera_open_button'),
                            onPressed: _busy ? null : _openCamera,
                            icon: _busy
                                ? const SizedBox(
                                    width: 18,
                                    height: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : const Icon(Icons.photo_camera_outlined),
                            label: Text(
                              _busy ? 'Ouverture…' : 'Prendre une photo',
                            ),
                          ),
                        ),
                        const SizedBox(height: AppSpacing.sm),
                        TextButton(
                          key: const Key('camera_guidance_cancel_button'),
                          onPressed:
                              _busy ? null : () => Navigator.of(context).pop(),
                          child: const Text('Annuler'),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}

class _GuidanceBullets extends StatelessWidget {
  const _GuidanceBullets({required this.items});

  final List<String> items;

  @override
  Widget build(BuildContext context) {
    final style = Theme.of(context).textTheme.bodySmall?.copyWith(
          color: AppColors.textSecondary,
        );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final item in items)
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('•  ', style: TextStyle(color: AppColors.textMuted)),
                Expanded(child: Text(item, style: style)),
              ],
            ),
          ),
      ],
    );
  }
}

class _PrototypeNotice extends StatelessWidget {
  const _PrototypeNotice();

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Avertissement prototype photo',
      child: Container(
        key: const Key('camera_prototype_notice'),
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: AppColors.warningSoft,
          borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
          border: Border.all(color: AppColors.warning.withValues(alpha: 0.25)),
        ),
        child: Text(
          CameraUserMessages.prototypeDisclaimer,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppColors.warning,
                height: 1.35,
              ),
        ),
      ),
    );
  }
}

class _CameraErrorBanner extends StatelessWidget {
  const _CameraErrorBanner({
    required this.message,
    this.onRetry,
  });

  final String message;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.errorSoft,
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: AppColors.error.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
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
          if (onRetry != null) ...[
            const SizedBox(height: AppSpacing.sm),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                key: const Key('camera_error_retry_button'),
                onPressed: onRetry,
                child: const Text('Réessayer'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
