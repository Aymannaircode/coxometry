/// Espacements et rayons du design system médical.
abstract final class AppSpacing {
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
  static const double xxl = 32;

  static const double pagePadding = 20;
  static const double contentMaxWidth = 720;
  static const double radiographHeight = 260;

  /// Hauteur overlay Results — bornes pour MediaQuery responsive.
  static const double radiographOverlayMin = 280;
  static const double radiographOverlayMax = 520;

  static const double radiusSm = 8;
  static const double radiusMd = 12;
  static const double radiusLg = 16;

  /// Hauteur radiographie Results (~45 % de l'écran, bornée).
  static double radiographOverlayHeight(double screenHeight) {
    return (screenHeight * 0.45)
        .clamp(radiographOverlayMin, radiographOverlayMax)
        .toDouble();
  }
}
