import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiException implements Exception {
  final int statusCode;
  final String body;
  final String message;

  ApiException(this.statusCode, this.body, {this.message = 'API request failed'});

  @override
  String toString() {
    final decoded = _safeDecode(body);
    if (decoded is Map) {
      final detail = decoded['detail'] ?? decoded['message'] ?? decoded['error'];
      if (detail != null) return detail.toString();
    }
    return message;
  }

  dynamic _safeDecode(String source) {
    try {
      return jsonDecode(source);
    } catch (_) {
      return null;
    }
  }
}

class ApiClient {
  static String? _globalToken;
  final String baseUrl;
  String? _token;

  ApiClient({required this.baseUrl});

  void setToken(String? token) {
    _token = token;
    _globalToken = token;
  }

  Map<String, String> _headers() {
    final token = _token ?? _globalToken;
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (token != null && token.isNotEmpty) 'Authorization': 'Token $token',
    };
  }

  Future<http.Response> get(String path) async {
    final response = await http.get(
      Uri.parse('$baseUrl$path'),
      headers: _headers(),
    );
    return _handleResponse(response);
  }

  Future<http.Response> post(String path, {Map<String, dynamic>? body}) async {
    final response = await http.post(
      Uri.parse('$baseUrl$path'),
      headers: _headers(),
      body: body != null ? jsonEncode(body) : null,
    );
    return _handleResponse(response);
  }

  Future<http.Response> put(String path, {Map<String, dynamic>? body}) async {
    final response = await http.put(
      Uri.parse('$baseUrl$path'),
      headers: _headers(),
      body: body != null ? jsonEncode(body) : null,
    );
    return _handleResponse(response);
  }

  Future<http.Response> patch(String path, {Map<String, dynamic>? body}) async {
    final response = await http.patch(
      Uri.parse('$baseUrl$path'),
      headers: _headers(),
      body: body != null ? jsonEncode(body) : null,
    );
    return _handleResponse(response);
  }

  Future<http.Response> delete(String path) async {
    final response = await http.delete(
      Uri.parse('$baseUrl$path'),
      headers: _headers(),
    );
    return _handleResponse(response);
  }

  http.Response _handleResponse(http.Response response) {
    if (response.statusCode >= 400) {
      throw ApiException(
        response.statusCode,
        response.body,
        message: 'Request failed with status ${response.statusCode}',
      );
    }
    return response;
  }

  dynamic decoded(http.Response response) {
    final body = utf8.decode(response.bodyBytes);
    if (body.isEmpty) return null;
    return jsonDecode(body);
  }
}
