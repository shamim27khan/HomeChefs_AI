import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/constants.dart';
import '../models/user.dart';
import '../services/auth_service.dart';
import '../services/chef_service.dart';
import '../services/customer_service.dart';
import '../services/order_service.dart';
import '../services/payment_service.dart';

class AuthProvider extends ChangeNotifier {
  final SharedPreferences _prefs;
  final AuthService _authService = AuthService();
  final ChefService _chefService = ChefService();
  final CustomerService _customerService = CustomerService();
  final OrderService _orderService = OrderService();
  final PaymentService _paymentService = PaymentService();

  bool isLoading = false;
  String? _token;
  User? user;
  Map<String, dynamic>? profile;

  AuthProvider(this._prefs);

  String? get token => _token;

  bool get isAuthenticated => _token != null && user != null;

  Future<void> initialize() async {
    _token = _prefs.getString(AppConstants.tokenKey);
    _syncToken(_token);
    if (_token != null && _token!.isNotEmpty) {
      try {
        await loadProfile();
      } catch (_) {
        await logout();
      }
    }
  }

  void _syncToken(String? value) {
    _authService.setToken(value);
    _chefService.setToken(value);
    _customerService.setToken(value);
    _orderService.setToken(value);
    _paymentService.setToken(value);
  }

  Future<bool> login(String username, String password) async {
    return _setBusy(() async {
      final response = await _authService.login(username, password);
      return _handleAuthResponse(response);
    });
  }

  Future<bool> loginWithOtp(String phoneNumber, String otpCode) async {
    return _setBusy(() async {
      final response = await _authService.loginWithOtp(phoneNumber, otpCode);
      return _handleAuthResponse(response);
    });
  }

  Future<bool> register({
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
    required String firstName,
    required String lastName,
    required String phoneNumber,
    required String role,
    Map<String, dynamic>? chefProfile,
  }) async {
    return _setBusy(() async {
      final response = await _authService.register(
        username: username,
        email: email,
        password: password,
        confirmPassword: confirmPassword,
        firstName: firstName,
        lastName: lastName,
        phoneNumber: phoneNumber,
        role: role,
        chefProfile: chefProfile,
      );
      return _handleAuthResponse(response);
    });
  }

  bool _handleAuthResponse(Map<String, dynamic> response) {
    final tokenValue = response['token'] as String?;
    if (tokenValue == null || tokenValue.isEmpty) {
      return false;
    }
    _token = tokenValue;
    _prefs.setString(AppConstants.tokenKey, tokenValue);
    _syncToken(tokenValue);
    final userJson = response['user'] as Map<String, dynamic>?;
    if (userJson != null) {
      user = User.fromJson(userJson);
    }
    profile = response['profile'] as Map<String, dynamic>?;
    notifyListeners();
    return true;
  }

  Future<void> loadProfile() async {
    await _setBusy(() async {
      final data = await _authService.getProfile();
      final userJson = data['user'] as Map<String, dynamic>?;
      if (userJson != null) {
        user = User.fromJson(userJson);
      }
      profile = data['profile'] as Map<String, dynamic>?;
    });
  }

  Future<bool> updateProfile(Map<String, dynamic> data) async {
    return _setBusy(() async {
      await _authService.updateProfile(data);
      await loadProfile();
      return true;
    });
  }

  Future<void> logout() async {
    await _setBusy(() async {
      try {
        await _authService.logout();
      } catch (_) {}
      _token = null;
      user = null;
      profile = null;
      await _prefs.remove(AppConstants.tokenKey);
      _syncToken(null);
      notifyListeners();
    });
  }

  Future<T> _setBusy<T>(Future<T> Function() action) async {
    isLoading = true;
    notifyListeners();
    try {
      return await action();
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
