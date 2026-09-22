import 'package:flutter/foundation.dart';

class AppConstants {
  static const String appName = 'HomeChefs';

  /// Base URL for the HomeChefs Django backend API.
  /// Defaults are set for the Android emulator and iOS simulator.
  /// Update this to point at your deployed backend (e.g. https://homechefhub.in).
  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000';
    return 'https://homechefhub.in';
  }

  static const String apiPrefix = '/api';
  static const String tokenKey = 'auth_token';
}
