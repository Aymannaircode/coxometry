import 'package:coxometrie/config/api_config.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ApiConfig', () {
    test('physicalDeviceRunCommand uses placeholder IP', () {
      final cmd = ApiConfig.physicalDeviceRunCommand();
      expect(cmd, contains('--dart-define=API_BASE_URL=http://<PC-IP>:8001'));
      expect(cmd, isNot(contains('192.168')));
    });

    test('physicalDeviceRunCommand supports optional device id', () {
      final cmd = ApiConfig.physicalDeviceRunCommand(deviceId: 'emulator-5554');
      expect(cmd, contains('-d emulator-5554'));
    });

    test('androidEmulatorUrl uses 10.0.2.2', () {
      expect(ApiConfig.androidEmulatorUrl, 'http://10.0.2.2:8001');
    });

    test('localhostUrl uses 127.0.0.1', () {
      expect(ApiConfig.localhostUrl, 'http://127.0.0.1:8001');
    });
  });
}
