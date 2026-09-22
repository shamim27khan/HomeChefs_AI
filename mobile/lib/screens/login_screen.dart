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

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _error = null);
    final auth = Provider.of<AuthProvider>(context, listen: false);
    try {
      final success = await auth.login(
        _usernameController.text.trim(),
        _passwordController.text.trim(),
      );
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
                        const SizedBox(height: 28),
                        TextFormField(
                          controller: _usernameController,
                          decoration: const InputDecoration(
                            labelText: 'Username or Email',
                            prefixIcon: Icon(Icons.person_outline),
                          ),
                          validator: (value) =>
                              value == null || value.isEmpty ? 'Username is required' : null,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _passwordController,
                          obscureText: _obscurePassword,
                          decoration: InputDecoration(
                            labelText: 'Password',
                            prefixIcon: const Icon(Icons.lock_outline),
                            suffixIcon: IconButton(
                              icon: Icon(_obscurePassword
                                  ? Icons.visibility_outlined
                                  : Icons.visibility_off_outlined),
                              onPressed: () =>
                                  setState(() => _obscurePassword = !_obscurePassword),
                            ),
                          ),
                          validator: (value) =>
                              value == null || value.isEmpty ? 'Password is required' : null,
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
                                : const Text('Login', style: TextStyle(fontSize: 16)),
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