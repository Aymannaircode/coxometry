import 'package:flutter/material.dart';

import '../config/api_config.dart';
import '../services/api_service.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import '../utils/model_version_label.dart';

/// Vérifie `GET /health` sans modifier `/analyze`.
class ServerConnectionScreen extends StatefulWidget {
  const ServerConnectionScreen({
    super.key,
    this.api,
  });

  final ApiService? api;

  @override
  State<ServerConnectionScreen> createState() => _ServerConnectionScreenState();
}

class _ServerConnectionScreenState extends State<ServerConnectionScreen> {
  late final ApiService _api;
  HealthCheckResult? _result;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? ApiService();
  }

  Future<void> _runHealthCheck() async {
    if (_loading) return;
    setState(() {
      _loading = true;
      _result = null;
    });

    final result = await _api.checkHealth();
    if (!mounted) return;
    setState(() {
      _loading = false;
      _result = result;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final result = _result;

    return Scaffold(
      appBar: AppBar(title: const Text('Connexion serveur')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(AppSpacing.pagePadding),
          children: [
            Text(
              'Diagnostic réseau',
              style: theme.textTheme.headlineSmall,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Teste uniquement GET /health — n\'envoie aucune radiographie '
              'et n\'appelle pas POST /analyze.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: AppSpacing.xl),
            _ConfigCard(),
            const SizedBox(height: AppSpacing.lg),
            FilledButton.icon(
              key: const Key('health_check_button'),
              onPressed: _loading ? null : _runHealthCheck,
              icon: _loading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.wifi_tethering),
              label: Text(_loading ? 'Test en cours…' : 'Tester GET /health'),
            ),
            if (result != null) ...[
              const SizedBox(height: AppSpacing.lg),
              _ResultCard(result: result),
            ],
            const SizedBox(height: AppSpacing.xl),
            Text(
              'Démarrage backend (démo V5)',
              style: theme.textTheme.titleSmall,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Recommandé — depuis la racine du dépôt :\n'
              '   .\\backend\\run_demo.ps1\n'
              'Ce script force MODEL_VERSION=v5_phase2 '
              '(16 landmarks + IT).\n\n'
              'Vérifier ensuite ici : « Modèle : V5 Phase 2 ».\n'
              'Sans run_demo.ps1 ni MODEL_VERSION=v5_phase2, '
              'le backend démarre en V2 (pas d\'IT).',
              style: theme.textTheme.bodySmall?.copyWith(height: 1.5),
            ),
            const SizedBox(height: AppSpacing.lg),
            Text(
              'Plateformes',
              style: theme.textTheme.titleSmall,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Démo sans téléphone (recommandé aujourd\'hui) :\n'
              '   Windows desktop : flutter run -d windows\n'
              '   ou émulateur Android (URL défaut '
              '${ApiConfig.androidEmulatorUrl}).\n'
              '   Import d\'une radiographie DICOM→PNG du dataset '
              '(pas la caméra).\n\n'
              'Appareil physique (quand disponible) :\n'
              '1. PC et appareil sur le même Wi‑Fi.\n'
              '2. Backend : .\\backend\\run_demo.ps1\n'
              '3. IP PC : ipconfig (Windows) ou ifconfig (macOS)\n'
              '4. Lancer l\'app :\n'
              '   ${ApiConfig.physicalDeviceRunCommand()}\n'
              '5. iOS simulateur : défaut ${ApiConfig.localhostUrl}\n'
              '   (projet iOS : voir docs/IOS_SETUP.md sur macOS)',
              style: theme.textTheme.bodySmall?.copyWith(height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}

class _ConfigCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _Row(label: 'URL', value: ApiConfig.baseUrl),
          const SizedBox(height: AppSpacing.xs),
          _Row(label: 'Source', value: ApiConfig.sourceLabel),
          const SizedBox(height: AppSpacing.xs),
          _Row(label: 'Health', value: ApiConfig.healthUri.toString()),
          const SizedBox(height: AppSpacing.xs),
          _Row(label: 'Analyze', value: ApiConfig.analyzeUri.toString()),
          if (!ApiConfig.isFromDartDefine) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Sur téléphone réel, définir API_BASE_URL via --dart-define.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: AppColors.warning,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  const _ResultCard({required this.result});

  final HealthCheckResult result;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final ok = result.ok;
    final color = ok ? AppColors.success : AppColors.error;
    final bg = ok ? AppColors.success.withValues(alpha: 0.08) : AppColors.errorSoft;
    final modelRaw = result.modelVersion;
    final hasModel =
        modelRaw != null && modelRaw.trim().isNotEmpty;

    return Container(
      key: const Key('health_check_result'),
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                ok ? Icons.check_circle_outline : Icons.error_outline,
                color: color,
              ),
              const SizedBox(width: AppSpacing.sm),
              Expanded(
                child: Text(
                  ok ? 'Serveur accessible' : 'Serveur inaccessible',
                  style: theme.textTheme.titleSmall?.copyWith(color: color),
                ),
              ),
            ],
          ),
          if (ok && hasModel) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Modèle : ${formatModelVersion(modelRaw)}',
              key: const Key('health_model_version'),
              style: theme.textTheme.titleSmall?.copyWith(
                color: AppColors.textPrimary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
          const SizedBox(height: AppSpacing.sm),
          _Row(
            label: 'Latence',
            value: '${result.latency.inMilliseconds} ms',
          ),
          if (result.statusCode != null) ...[
            const SizedBox(height: AppSpacing.xs),
            _Row(label: 'HTTP', value: '${result.statusCode}'),
          ],
          if (result.status != null) ...[
            const SizedBox(height: AppSpacing.xs),
            _Row(label: 'status', value: result.status!),
          ],
          if (result.service != null) ...[
            const SizedBox(height: AppSpacing.xs),
            _Row(label: 'service', value: result.service!),
          ],
          if (result.version != null) ...[
            const SizedBox(height: AppSpacing.xs),
            _Row(label: 'version', value: result.version!),
          ],
          if (result.message != null && !ok) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(
              result.message!,
              key: const Key('health_error_message'),
              style: theme.textTheme.bodyMedium?.copyWith(color: AppColors.error),
            ),
          ],
        ],
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 72,
          child: Text(
            label,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
        Expanded(
          child: SelectableText(
            value,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ),
      ],
    );
  }
}
