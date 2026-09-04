import 'api_client.dart';
import '../config/constants.dart';

class AuthService {
  final ApiClient _client = ApiClient(baseUrl: AppConstants.baseUrl);

  void setToken(String? token) => _client.setToken(token);

  Future<Map<String, dynamic>> register({
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
    final body = {
      'username': username,
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
      'first_name': firstName,
      'last_name': lastName,
      'phone_number': phoneNumber,
      'role': role,
      'chef_profile': ?chefProfile,
    };

    final response = await _client.post('${AppConstants.apiPrefix}/auth/register/', body: body);
    return _client.decoded(response) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await _client.post(
      '${AppConstants.apiPrefix}/auth/login/',
      body: {'username': username, 'password': password},
    );
    return _client.decoded(response) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> loginWithOtp(String phoneNumber, String otpCode) async {
    final response = await _client.post(
      '${AppConstants.apiPrefix}/auth/login/',
      body: {'phone_number': phoneNumber, 'otp_code': otpCode},
    );
    return _client.decoded(response) as Map<String, dynamic>;
  }

  Future<void> logout() async {
    try {
      await _client.post('${AppConstants.apiPrefix}/auth/logout/');
    } catch (_) {}
  }

  Future<Map<String, dynamic>> getProfile() async {
    final response = await _client.get('${AppConstants.apiPrefix}/auth/profile/');
    return _client.decoded(response) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> data) async {
    final response = await _client.put('${AppConstants.apiPrefix}/auth/profile/', body: data);
    return _client.decoded(response) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> requestOtp(String phoneNumber) async {
    final response = await _client.post(
      '${AppConstants.apiPrefix}/auth/request-otp/',
      body: {'phone_number': phoneNumber},
    );
    return _client.decoded(response) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> verifyOtp(String phoneNumber, String otpCode) async {
    final response = await _client.post(
      '${AppConstants.apiPrefix}/auth/verify-otp/',
      body: {'phone_number': phoneNumber, 'otp_code': otpCode},
    );
    return _client.decoded(response) as Map<String, dynamic>;
  }
}
