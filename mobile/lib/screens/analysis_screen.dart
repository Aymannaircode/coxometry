import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/radiograph_picker.dart';
import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';
import '../widgets/loading_analysis.dart';
import 'results_screen.dart';

/// Lance `POST /analyze` et affiche le chargement.
///
/// Une seule requête à la fois ; navigation automatique vers les résultats
/// ou affichage d'erreur.
class AnalysisScreen extends StatefulWidget {
  const AnalysisScreen({
    super.key,
    required this.radiograph,
    this.api,
  });

  final SelectedRadiograph radiograph;
  final ApiService? api;

  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen> {
  late final ApiService _api;
  String? _error;
  bool _analyzing = true;
  bool _requestStarted = false;

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? ApiService();
    WidgetsBinding.instance.addPostFrameCallback((_) => _runAnalysis());
  }

  Future<void> _runAnalysis() async {
    if (_requestStarted) return;
    _requestStarted = true;

    try {
      final result = await _api.analyzeRadiograph(
        bytes: widget.radiograph.bytes,
        filename: widget.radiograph.filename,
      );
      if (!mounted) return;

      await Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => ResultsScreen(
            radiograph: widget.radiograph,
            result: result,
          ),
        ),
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _analyzing = false;
        _error = _friendlyMessage(e);
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _analyzing = false;
        _error =
            'Une erreur inattendue s\'est produite. Réessayez ou vérifiez la connexion serveur.';
      });
    }
  }

  String _friendlyMessage(ApiException e) {
    switch (e.kind) {
      case ApiExceptionKind.network:
        return e.message;
      case ApiExceptionKind.timeout:
        return e.message;
      case ApiExceptionKind.fileTooLarge:
        return e.message;
      case ApiExceptionKind.invalidJson:
        return e.message;
      case ApiExceptionKind.invalidResponse:
        return e.message;
      case ApiExceptionKind.clientError:
        return 'Requête refusée${e.statusCode != null ? ' (HTTP ${e.statusCode})' : ''} : ${e.message}';
      case ApiExceptionKind.serverError:
        return 'Erreur serveur${e.statusCode != null ? ' (HTTP ${e.statusCode})' : ''}. Réessayez plus tard.';
      case ApiExceptionKind.analysisError:
        return e.message;
      case ApiExceptionKind.invalidRequest:
        return e.message;
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: !_analyzing,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Analyse'),
          automaticallyImplyLeading: !_analyzing,
        ),
        body: SafeArea(
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: AppSpacing.contentMaxWidth),
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.pagePadding),
                child: _analyzing
                    ? LoadingAnalysis(imageBytes: widget.radiograph.bytes)
                    : _ErrorView(
                        message: _error ?? 'Erreur inconnue.',
                        onRetry: () {
                          setState(() {
                            _analyzing = true;
                            _error = null;
                            _requestStarted = false;
                          });
                          _runAnalysis();
                        },
                        onBack: () => Navigator.of(context).pop(),
                      ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({
    required this.message,
    required this.onRetry,
    required this.onBack,
  });

  final String message;
  final VoidCallback onRetry;
  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Icon(Icons.error_outline, color: AppColors.error, size: 48),
        const SizedBox(height: AppSpacing.lg),
        Text(
          message,
          key: const Key('analysis_error_message'),
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.error,
              ),
        ),
        const SizedBox(height: AppSpacing.xl),
        FilledButton(onPressed: onRetry, child: const Text('Réessayer')),
        const SizedBox(height: AppSpacing.md),
        OutlinedButton(onPressed: onBack, child: const Text('Retour à l\'aperçu')),
      ],
    );
  }
}
