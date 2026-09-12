import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';

import '../utils/camera_user_messages.dart';
import '../utils/image_normalizer.dart';

/// Image radiographique sélectionnée localement.
class SelectedRadiograph {
  const SelectedRadiograph({
    required this.bytes,
    required this.filename,
    this.width,
    this.height,
    this.orientationCorrected = false,
  });

  final Uint8List bytes;
  final String filename;
  final int? width;
  final int? height;
  final bool orientationCorrected;

  int get sizeBytes => bytes.length;

  String get sizeLabel {
    final kb = sizeBytes / 1024;
    if (kb < 1024) return '${kb.toStringAsFixed(0)} Ko';
    return '${(kb / 1024).toStringAsFixed(1)} Mo';
  }
}

enum RadiographSource { gallery, camera }

abstract class RadiographPicker {
  Future<SelectedRadiograph?> pickFromGallery();
  Future<SelectedRadiograph?> pickFromCamera();
}

/// Galerie et caméra — normalisation EXIF, lecture fichier haute résolution.
///
/// Caméra et galerie partagent [_normalize] → mêmes octets canoniques pour
/// Preview → /analyze (aucun pipeline d'inférence séparé).
class FileRadiographPicker implements RadiographPicker {
  FileRadiographPicker({
    ImagePicker? imagePicker,
  }) : _imagePickerOverride = imagePicker;

  final ImagePicker? _imagePickerOverride;

  ImagePicker get _imagePicker => _imagePickerOverride ?? ImagePicker();

  @override
  Future<SelectedRadiograph?> pickFromGallery() async {
    final file = await FilePicker.pickFile(
      type: FileType.custom,
      allowedExtensions: const ['jpg', 'jpeg', 'png'],
    );

    if (file == null) return null;

    final bytes = await _readFileBytes(file);
    final name = file.name.isNotEmpty ? file.name : 'radiograph.png';
    return _normalize(bytes, name);
  }

  @override
  Future<SelectedRadiograph?> pickFromCamera() async {
    if (kIsWeb) {
      throw const RadiographPickerException(
        CameraUserMessages.cameraUnavailable,
      );
    }

    try {
      final photo = await _imagePicker.pickImage(
        source: ImageSource.camera,
        imageQuality: 100,
        preferredCameraDevice: CameraDevice.rear,
      );
      if (photo == null) return null;

      final bytes = await photo.readAsBytes();
      if (bytes.isEmpty) {
        throw const RadiographPickerException(CameraUserMessages.emptyCapture);
      }

      final name = photo.name.isNotEmpty ? photo.name : 'capture.jpg';
      return _normalize(bytes, name);
    } on RadiographPickerException {
      rethrow;
    } on PlatformException catch (e) {
      throw RadiographPickerException(mapCameraPlatformException(e));
    } on MissingPluginException {
      throw const RadiographPickerException(
        CameraUserMessages.cameraUnavailable,
      );
    } catch (_) {
      throw const RadiographPickerException(CameraUserMessages.captureFailed);
    }
  }

  Future<Uint8List> _readFileBytes(PlatformFile file) async {
    final read = await file.readAsBytes();
    if (read.isEmpty) {
      throw const RadiographPickerException('Fichier image vide.');
    }
    return read;
  }

  SelectedRadiograph _normalize(Uint8List bytes, String filename) {
    try {
      final normalized = normalizeRadiographBytes(
        bytes: bytes,
        filename: filename,
      );
      return SelectedRadiograph(
        bytes: normalized.bytes,
        filename: normalized.filename,
        width: normalized.width,
        height: normalized.height,
        orientationCorrected: normalized.orientationCorrected,
      );
    } on RadiographPickerException {
      rethrow;
    } catch (_) {
      throw const RadiographPickerException(CameraUserMessages.loadFailed);
    }
  }
}

class RadiographPickerException implements Exception {
  const RadiographPickerException(this.message);
  final String message;

  @override
  String toString() => 'RadiographPickerException: $message';
}
