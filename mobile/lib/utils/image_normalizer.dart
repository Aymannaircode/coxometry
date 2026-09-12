import 'dart:typed_data';

import 'package:image/image.dart' as img;
import 'package:path/path.dart' as p;

import '../services/radiograph_picker.dart';

/// Image normalisée : orientation EXIF appliquée aux pixels.
class NormalizedImage {
  const NormalizedImage({
    required this.bytes,
    required this.filename,
    required this.width,
    required this.height,
    this.orientationCorrected = false,
  });

  final Uint8List bytes;
  final String filename;
  final int width;
  final int height;

  /// `true` si l'orientation EXIF a modifié les pixels.
  final bool orientationCorrected;
}

/// Applique l'orientation EXIF pour aligner affichage, upload et landmarks.
///
/// Le backend ne corrige pas l'EXIF ; cette étape garantit que les coordonnées
/// renvoyées correspondent aux pixels affichés.
///
/// Mémoire : décode et ré-encode l'image entière en RAM (jusqu'à 25 Mo côté
/// upload). Les radiographies très volumineuses peuvent solliciter la RAM ;
/// un redimensionnement pré-upload reste une optimisation future si nécessaire.
NormalizedImage normalizeRadiographBytes({
  required Uint8List bytes,
  required String filename,
}) {
  final decoded = img.decodeImage(bytes);
  if (decoded == null) {
    throw const RadiographPickerException(
      'Image illisible ou format non supporté.',
    );
  }

  final beforeW = decoded.width;
  final beforeH = decoded.height;
  final oriented = img.bakeOrientation(decoded);
  final corrected = _hadExifOrientation(decoded) ||
      oriented.width != beforeW ||
      oriented.height != beforeH;

  final ext = p.extension(filename).toLowerCase();
  final Uint8List outputBytes;
  final String outputName;

  if (ext == '.png') {
    outputBytes = Uint8List.fromList(img.encodePng(oriented));
    outputName = filename;
  } else {
    outputBytes = Uint8List.fromList(img.encodeJpg(oriented, quality: 95));
    outputName = (ext == '.jpg' || ext == '.jpeg') ? filename : '$filename.jpg';
  }

  return NormalizedImage(
    bytes: outputBytes,
    filename: outputName,
    width: oriented.width,
    height: oriented.height,
    orientationCorrected: corrected,
  );
}

bool _hadExifOrientation(img.Image decoded) {
  try {
    if (!decoded.exif.imageIfd.hasOrientation) return false;
    final o = decoded.exif.imageIfd.orientation;
    return o != null && o != 1;
  } catch (_) {
    return false;
  }
}
