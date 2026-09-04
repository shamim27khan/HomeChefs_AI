import 'package:flutter/foundation.dart';

class AppConstants {
  static const String appName = 'HomeChefs';

  /// Base URL for the HomeChefs Django backend API.
  /// Defaults are set for the Android emulator and iOS simulator.
  /// Update this to point at your deployed backend (e.g. https://homechefhub.in).
  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000';
    if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }
    if (defaultTargetPlatform == TargetPlatform.iOS) {
      return 'http://127.0.0.1:8000';
    }
    return 'http://localhost:8000';
  }

  static const String apiPrefix = '/api';
  static const String tokenKey = 'auth_token';
}
