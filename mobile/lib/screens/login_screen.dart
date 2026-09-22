import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../providers/auth_provider.dart';
import '../widgets/app_logo.dart';
import '../widgets/loading_indicator.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  String? _error;
  bool _isOtpMode = false;
  final _phoneController = TextEditingController();
  final _otpController = TextEditingController();

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _phoneController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _error = null);
    final auth = Provider.of<AuthProvider>(context, listen: false);
    try {
      final bool success;
      if (_isOtpMode) {
        success = await auth.loginWithOtp(
          _phoneController.text.trim(),
          _otpController.text.trim(),
        );
      } else {
        success = await auth.login(
          _usernameController.text.trim(),
          _passwordController.text.trim(),
        );
      }
      if (!mounted) return;
      if (success) {
        Navigator.of(context).pushReplacementNamed('/home');
      } else {
        setState(() => _error = 'Login failed. Please check your credentials.');
      }
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  Future<void> _requestOtp() async {
    final phone = _phoneController.text.trim();
    if (phone.isEmpty) {
      setState(() => _error = 'Phone number is required');
      return;
    }
    setState(() => _error = null);
    final auth = Provider.of<AuthProvider>(context, listen: false);
    try {
      final response = await auth.requestOtp(phone);
      if (!mounted) return;
      final message = response['message'] ?? 'OTP sent';
      final otpCode = response['otp_code']?.toString() ?? '';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$message${otpCode.isNotEmpty ? ' (Code: $otpCode)' : ''}')),
      );
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    return Scaffold(
      backgroundColor: AppColors.lightBg,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Card(
                elevation: 6,
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Center(child: AppLogo(height: 56)),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            TextButton(
                              onPressed: () => setState(() => _isOtpMode = false),
                              child: Text(
                                'Password',
                                style: TextStyle(
                                  fontWeight: _isOtpMode ? FontWeight.normal : FontWeight.bold,
                                  color: _isOtpMode ? Colors.black54 : AppColors.primary,
                                ),
                              ),
                            ),
                            const Text('|', style: TextStyle(color: Colors.black54)),
                            TextButton(
                              onPressed: () => setState(() => _isOtpMode = true),
                              child: Text(
                                'OTP',
                                style: TextStyle(
                                  fontWeight: _isOtpMode ? FontWeight.bold : FontWeight.normal,
                                  color: _isOtpMode ? AppColors.primary : Colors.black54,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        TextFormField(
                          controller: _isOtpMode ? _phoneController : _usernameController,
                          decoration: InputDecoration(
                            labelText: _isOtpMode ? 'Phone Number' : 'Username or Email',
                            prefixIcon: Icon(
                              _isOtpMode ? Icons.phone_outlined : Icons.person_outline,
                            ),
                          ),
                          keyboardType: _isOtpMode ? TextInputType.phone : TextInputType.text,
                          validator: (value) =>
                              value == null || value.isEmpty ? 'Required' : null,
                        ),
                        const SizedBox(height: 16),
                        if (_isOtpMode)
                          TextButton(
                            onPressed: auth.isLoading ? null : _requestOtp,
                            child: const Text('Send OTP'),
                          ),
                        TextFormField(
                          controller: _isOtpMode ? _otpController : _passwordController,
                          obscureText: _isOtpMode ? false : _obscurePassword,
                          decoration: InputDecoration(
                            labelText: _isOtpMode ? 'OTP Code' : 'Password',
                            prefixIcon: Icon(
                              _isOtpMode ? Icons.sms_outlined : Icons.lock_outline,
                            ),
                            suffixIcon: _isOtpMode
                                ? null
                                : IconButton(
                                    icon: Icon(_obscurePassword
                                        ? Icons.visibility_outlined
                                        : Icons.visibility_off_outlined),
                                    onPressed: () =>
                                        setState(() => _obscurePassword = !_obscurePassword),
                                  ),
                          ),
                          keyboardType: _isOtpMode ? TextInputType.number : TextInputType.text,
                          validator: (value) =>
                              value == null || value.isEmpty ? 'Required' : null,
                        ),
                        if (_error != null) ...[
                          const SizedBox(height: 12),
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: AppColors.primary.withValues(alpha: 0.08),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              _error!,
                              style: const TextStyle(color: AppColors.primary),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        ],
                        const SizedBox(height: 24),
                        SizedBox(
                          height: 48,
                          child: ElevatedButton.icon(
                            onPressed: auth.isLoading ? null : _login,
                            icon: auth.isLoading
                                ? const SizedBox.shrink()
                                : const Icon(Icons.login, size: 18),
                            label: auth.isLoading
                                ? const LoadingIndicator()
                                : Text(_isOtpMode ? 'Login with OTP' : 'Login', style: const TextStyle(fontSize: 16)),
                          ),
                        ),
                        const SizedBox(height: 20),
                        Wrap(
                          alignment: WrapAlignment.center,
                          children: [
                            const Text("Don't have an account? ",
                                style: TextStyle(color: Colors.black54)),
                            GestureDetector(
                              onTap: () =>
                                  Navigator.of(context).pushNamed('/register'),
                              child: const Text(
                                'Register here',
                                style: TextStyle(
                                  color: AppColors.primary,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}