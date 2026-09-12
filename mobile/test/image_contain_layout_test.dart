import 'dart:ui' show Offset, Size;

import 'package:coxometrie/widgets/image_contain_layout.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ImageContainLayout.toImage', () {
    test('is the inverse of toDisplay (square image, centered pillarbox)', () {
      final layout = ImageContainLayout.compute(
        boxSize: const Size(200, 100),
        imageSize: const Size(100, 100),
      );
      expect(layout.scale, 1.0);
      expect(layout.offset, const Offset(50, 0));

      const imagePoint = Offset(50, 50);
      final display = layout.toDisplay(imagePoint.dx, imagePoint.dy);
      expect(display, const Offset(100, 50));

      final back = layout.toImage(display.dx, display.dy);
      expect(back.dx, closeTo(imagePoint.dx, 1e-9));
      expect(back.dy, closeTo(imagePoint.dy, 1e-9));
    });

    test('round-trip corners and edges under letterbox', () {
      // Image landscape in taller box → horizontal letterbox (vertical padding).
      final layout = ImageContainLayout.compute(
        boxSize: const Size(200, 400),
        imageSize: const Size(400, 200),
      );
      expect(layout.scale, 0.5);
      expect(layout.offset.dx, closeTo(0, 1e-9));
      expect(layout.offset.dy, closeTo(150, 1e-9));

      final points = <Offset>[
        Offset.zero,
        const Offset(400, 0),
        const Offset(0, 200),
        const Offset(400, 200),
        const Offset(200, 100),
        const Offset(12.5, 87.25),
      ];
      for (final image in points) {
        final display = layout.toDisplay(image.dx, image.dy);
        final back = layout.toImage(display.dx, display.dy);
        expect(back.dx, closeTo(image.dx, 1e-9), reason: 'x for $image');
        expect(back.dy, closeTo(image.dy, 1e-9), reason: 'y for $image');
      }
    });

    test('round-trip under pillarbox (portrait image in wide box)', () {
      final layout = ImageContainLayout.compute(
        boxSize: const Size(800, 400),
        imageSize: const Size(300, 600),
      );
      // scale limited by height: 400/600
      expect(layout.scale, closeTo(400 / 600, 1e-12));
      expect(layout.offset.dy, closeTo(0, 1e-9));
      expect(layout.offset.dx, greaterThan(0));

      for (final image in const [
        Offset(0, 0),
        Offset(300, 600),
        Offset(150, 300),
      ]) {
        final display = layout.toDisplay(image.dx, image.dy);
        final back = layout.toImage(display.dx, display.dy);
        expect(back.dx, closeTo(image.dx, 1e-9));
        expect(back.dy, closeTo(image.dy, 1e-9));
      }
    });

    test('BoxFit.contain keeps aspect ratio (no stretch)', () {
      final layout = ImageContainLayout.compute(
        boxSize: const Size(320, 180),
        imageSize: const Size(1920, 1080),
      );
      expect(layout.displayedSize.width / layout.displayedSize.height,
          closeTo(1920 / 1080, 1e-9));
      expect(layout.scale, closeTo(320 / 1920, 1e-12));
    });

    test('different resolutions produce image coords independent of box size', () {
      const imageSize = Size(1024, 768);
      const imagePoint = Offset(512, 384);

      final small = ImageContainLayout.compute(
        boxSize: const Size(200, 150),
        imageSize: imageSize,
      );
      final large = ImageContainLayout.compute(
        boxSize: const Size(1024, 768),
        imageSize: imageSize,
      );
      final phone = ImageContainLayout.compute(
        boxSize: const Size(390, 280),
        imageSize: imageSize,
      );

      for (final layout in [small, large, phone]) {
        final display = layout.toDisplay(imagePoint.dx, imagePoint.dy);
        final back = layout.toImage(display.dx, display.dy);
        expect(back.dx, closeTo(512, 1e-9));
        expect(back.dy, closeTo(384, 1e-9));
      }
    });

    test('extreme aspect ratios still round-trip', () {
      final wide = ImageContainLayout.compute(
        boxSize: const Size(500, 100),
        imageSize: const Size(4000, 200),
      );
      final tall = ImageContainLayout.compute(
        boxSize: const Size(100, 500),
        imageSize: const Size(200, 4000),
      );

      for (final layout in [wide, tall]) {
        final display = layout.toDisplay(100, 50);
        final back = layout.toImage(display.dx, display.dy);
        expect(back.dx, closeTo(100, 1e-9));
        expect(back.dy, closeTo(50, 1e-9));
      }
    });

    test('saved coordinates remain in original image pixel space', () {
      // Simulate a drag ending at a display point after letterbox.
      final layout = ImageContainLayout.compute(
        boxSize: const Size(300, 200),
        imageSize: const Size(1000, 800),
      );
      final displayTap = layout.toDisplay(640.0, 400.0);
      final image = layout.toImage(displayTap.dx, displayTap.dy);

      expect(image.dx, closeTo(640.0, 1e-9));
      expect(image.dy, closeTo(400.0, 1e-9));
      // Must not be equal to widget/display coordinates when scale != 1.
      expect(layout.scale, isNot(1.0));
      expect(image.dx, isNot(closeTo(displayTap.dx, 1e-6)));
    });

    test('composes with an external zoom transform (InteractiveViewer-like)', () {
      // Layout space is the child of InteractiveViewer. Pointer events arrive
      // in parent space; invert zoom first, then toImage.
      final layout = ImageContainLayout.compute(
        boxSize: const Size(200, 200),
        imageSize: const Size(100, 100),
      );
      const zoom = 2.0;
      const imagePoint = Offset(40, 60);
      final layoutDisplay = layout.toDisplay(imagePoint.dx, imagePoint.dy);

      // Uniform scale about origin of the viewer child (simplified).
      final parentDisplay = Offset(
        layoutDisplay.dx * zoom,
        layoutDisplay.dy * zoom,
      );
      final localDisplay = Offset(
        parentDisplay.dx / zoom,
        parentDisplay.dy / zoom,
      );
      final recovered = layout.toImage(localDisplay.dx, localDisplay.dy);

      expect(recovered.dx, closeTo(40, 1e-9));
      expect(recovered.dy, closeTo(60, 1e-9));
    });

    test('degenerate scale returns Offset.zero without throwing', () {
      const layout = ImageContainLayout(
        scale: 0,
        offset: Offset.zero,
        displayedSize: Size.zero,
        boxSize: Size(10, 10),
        imageSize: Size(10, 10),
      );
      expect(layout.toImage(5, 5), Offset.zero);
    });

    test('existing toDisplay behavior is unchanged', () {
      final layout = ImageContainLayout.compute(
        boxSize: const Size(100, 50),
        imageSize: const Size(200, 200),
      );
      expect(layout.scale, 0.25);
      expect(layout.toDisplay(200, 200), const Offset(75, 50));
      expect(layout.toDisplay(0, 0), const Offset(25, 0));
    });
  });
}
