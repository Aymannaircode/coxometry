import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/services.dart';
import 'package:pdf/widgets.dart' as pw;

/// Charge une police Unicode pour le PDF (accents FR).
///
/// Ordre : assets optionnels → polices système (Roboto/Arial) → Helvetica.
class ReportPdfFonts {
  ReportPdfFonts._();

  static pw.Font? _base;
  static pw.Font? _bold;
  static bool _loaded = false;

  static Future<void> ensureLoaded() async {
    if (_loaded) return;

    final fromAssets = await _tryAssets();
    if (fromAssets) {
      _loaded = true;
      return;
    }

    final fromSystem = await _trySystemFonts();
    if (fromSystem) {
      _loaded = true;
      return;
    }

    // Helvetica : pas d'accents complets — dernier recours.
    _base = pw.Font.helvetica();
    _bold = pw.Font.helveticaBold();
    _loaded = true;
  }

  /// Pour les tests : réinitialiser le cache.
  static void resetForTest() {
    _base = null;
    _bold = null;
    _loaded = false;
  }

  static pw.ThemeData theme() {
    return pw.ThemeData.withFont(
      base: _base ?? pw.Font.helvetica(),
      bold: _bold ?? pw.Font.helveticaBold(),
    );
  }

  static Future<bool> _tryAssets() async {
    try {
      final regular = await rootBundle.load(
        'assets/fonts/NotoSans-Regular.ttf',
      );
      ByteData? bold;
      try {
        bold = await rootBundle.load('assets/fonts/NotoSans-Bold.ttf');
      } on Object {
        bold = null;
      }
      _base = pw.Font.ttf(regular);
      _bold = bold != null ? pw.Font.ttf(bold) : _base;
      return true;
    } on Object {
      return false;
    }
  }

  static Future<bool> _trySystemFonts() async {
    final pairs = <List<String>>[
      // Android
      ['/system/fonts/Roboto-Regular.ttf', '/system/fonts/Roboto-Bold.ttf'],
      ['/system/fonts/NotoSans-Regular.ttf', '/system/fonts/NotoSans-Bold.ttf'],
      // Windows
      [r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\arialbd.ttf'],
      [r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\segoeuib.ttf'],
      // Linux
      ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'],
      // macOS
      ['/System/Library/Fonts/Supplemental/Arial.ttf',
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf'],
    ];

    for (final pair in pairs) {
      final regularFile = File(pair[0]);
      if (!await regularFile.exists()) continue;
      try {
        final regularBytes = await regularFile.readAsBytes();
        _base = pw.Font.ttf(regularBytes.buffer.asByteData());
        final boldFile = File(pair[1]);
        if (await boldFile.exists()) {
          final boldBytes = await boldFile.readAsBytes();
          _bold = pw.Font.ttf(boldBytes.buffer.asByteData());
        } else {
          _bold = _base;
        }
        return true;
      } on Object {
        continue;
      }
    }
    return false;
  }
}
