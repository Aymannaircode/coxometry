import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../services/radiograph_picker.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import '../utils/camera_user_messages.dart';
import '../widgets/camera_framing_guide.dart';
import 'preview_screen.dart';

/// Aperçu après capture — confirmation explicite avant le pipeline d'analyse.
class CameraConfirmScreen extends StatefulWidget {
  const CameraConfirmScreen({
    super.key,
    required this.picker,
    required this.radiograph,
  });

  final RadiographPicker picker;
  final SelectedRadiograph radiograph;

  @override
  State<CameraConfirmScreen> createState() => _CameraConfirmScreenState();
}

class _CameraConfirmScreenState extends State<CameraConfirmScreen> {
  late SelectedRadiograph _radiograph;
  String? _error;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _radiograph = widget.radiograph;
  }

  Future<void> _retake() async {
    if (_busy) return;
    setState(() {
      _busy = true;
      _error = null;
    });

    try {
      final selected = await widget.picker.pickFromCamera();
      if (!mounted) return;
      if (selected == null) {
        // Annulation : conserver la photo actuelle, pas d'analyse.
        return;
      }
      setState(() => _radiograph = selected);
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

  void _usePhoto() {
    if (_busy) return;
    // Même chemin galerie : PreviewScreen → AnalysisScreen → /analyze.
    // Retire guidage/confirm pour éviter une pile caméra obsolète.
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(
        builder: (_) => PreviewScreen(radiograph: _radiograph),
      ),
      (route) => route.isFirst,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final media = MediaQuery.sizeOf(context);
    final previewHeight = (media.height * 0.42).clamp(220.0, 420.0);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Aperçu de la photo'),
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
                      child: ClipRRect(
                        borderRadius:
                            BorderRadius.circular(AppSpacing.radiusSm),
                        child: ColoredBox(
                          color: AppColors.radiographBg,
                          child: SizedBox(
                            height: previewHeight,
                            width: double.infinity,
                            child: Stack(
                              fit: StackFit.expand,
                              children: [
                                Image.memory(
                                  _radiograph.bytes,
                                  fit: BoxFit.contain,
                                  gaplessPlayback: true,
                                  errorBuilder: (_, __, ___) => const Center(
                                    child: Icon(
                                      Icons.broken_image_outlined,
                                      color: Colors.white54,
                                      size: 48,
                                    ),
                                  ),
                                ),
                                const CameraFramingOverlay(),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                  if (_radiograph.width != null &&
                      _radiograph.height != null) ...[
                    const SizedBox(height: AppSpacing.sm),
                    Text(
                      '${_radiograph.width} × ${_radiograph.height} px · '
                      '${_radiograph.sizeLabel}'
                      '${_radiograph.orientationCorrected ? ' · orientation corrigée' : ''}',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: AppColors.textMuted,
                      ),
                    ),
                  ],
                  const SizedBox(height: AppSpacing.md),
                  Text(
                    CameraUserMessages.prototypeDisclaimerShort,
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: AppColors.textSecondary,
                      height: 1.35,
                    ),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: AppSpacing.md),
                    Text(
                      _error!,
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: AppColors.error,
                      ),
                    ),
                  ],
                  const SizedBox(height: AppSpacing.xl),
                  Semantics(
                    button: true,
                    label: 'Utiliser cette photo',
                    child: FilledButton.icon(
                      key: const Key('camera_use_photo_button'),
                      onPressed: _busy ? null : _usePhoto,
                      icon: const Icon(Icons.check_outlined),
                      label: const Text('Utiliser cette photo'),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.md),
                  Semantics(
                    button: true,
                    label: 'Reprendre',
                    child: OutlinedButton.icon(
                      key: const Key('camera_retake_button'),
                      onPressed: _busy ? null : _retake,
                      icon: _busy
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.refresh_outlined),
                      label: Text(_busy ? 'Ouverture…' : 'Reprendre'),
                    ),
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
