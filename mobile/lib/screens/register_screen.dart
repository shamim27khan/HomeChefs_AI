import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/loading_indicator.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  String _role = 'customer';
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  final _areaController = TextEditingController();
  final _cityController = TextEditingController();
  final _pincodeController = TextEditingController();
  final _cuisineController = TextEditingController();
  bool _obscurePassword = true;
  String? _error;

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    _areaController.dispose();
    _cityController.dispose();
    _pincodeController.dispose();
    _cuisineController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _error = null);

    Map<String, dynamic>? chefProfile;
    if (_role == 'chef') {
      chefProfile = {
        'address_line1': _addressController.text.trim(),
        'address_line2': '',
        'area': _areaController.text.trim(),
        'city': _cityController.text.trim(),
        'pincode': _pincodeController.text.trim(),
        'cuisine_specialties': _cuisineController.text.trim(),
        'cooking_experience': 0,
        'kitchen_type': 'home',
      };
    }

    final auth = Provider.of<AuthProvider>(context, listen: false);
    try {
      final success = await auth.register(
        username: _usernameController.text.trim(),
        email: _emailController.text.trim(),
        password: _passwordController.text.trim(),
        confirmPassword: _confirmPasswordController.text.trim(),
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        phoneNumber: _phoneController.text.trim(),
        role: _role,
        chefProfile: chefProfile,
      );
      if (!mounted) return;
      if (success) {
        Navigator.of(context).pushReplacementNamed('/home');
      } else {
        setState(() => _error = 'Registration failed. Please try again.');
      }
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Create Account')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SegmentedButton<String>(
                  segments: const [
                    ButtonSegment(value: 'customer', label: Text('Customer')),
                    ButtonSegment(value: 'chef', label: Text('Chef')),
                  ],
                  selected: {_role},
                  onSelectionChanged: (value) => setState(() => _role = value.first),
                ),
                const SizedBox(height: 16),
                _buildTextField(_firstNameController, 'First Name'),
                const SizedBox(height: 12),
                _buildTextField(_lastNameController, 'Last Name'),
                const SizedBox(height: 12),
                _buildTextField(_usernameController, 'Username'),
                const SizedBox(height: 12),
                _buildTextField(_emailController, 'Email', keyboardType: TextInputType.emailAddress, validator: _emailValidator),
                const SizedBox(height: 12),
                _buildTextField(_phoneController, 'Phone Number', keyboardType: TextInputType.phone, validator: _phoneValidator),
                const SizedBox(height: 12),
                _buildPasswordField(_passwordController, 'Password'),
                const SizedBox(height: 12),
                _buildPasswordField(_confirmPasswordController, 'Confirm Password', validator: _confirmPasswordValidator),
                if (_role == 'chef') ...[
                  const SizedBox(height: 24),
                  const Text('Chef details', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  _buildTextField(_addressController, 'Kitchen Address Line 1', validator: _requiredValidator),
                  const SizedBox(height: 12),
                  _buildTextField(_areaController, 'Area', validator: _requiredValidator),
                  const SizedBox(height: 12),
                  _buildTextField(_cityController, 'City', validator: _requiredValidator),
                  const SizedBox(height: 12),
                  _buildTextField(_pincodeController, 'Pincode', validator: _requiredValidator),
                  const SizedBox(height: 12),
                  _buildTextField(_cuisineController, 'Cuisine Specialties', hint: 'e.g. North Indian, South Indian', validator: _requiredValidator),
                ],
                if (_error != null) ...[
                  const SizedBox(height: 16),
                  Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                ],
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: auth.isLoading ? null : _register,
                  child: auth.isLoading ? const LoadingIndicator() : const Text('Register'),
                ),
                const SizedBox(height: 12),
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Already have an account? Login'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(
    TextEditingController controller,
    String label, {
    TextInputType? keyboardType,
    String? hint,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      decoration: InputDecoration(labelText: label, hintText: hint),
      validator: validator ?? _requiredValidator,
    );
  }

  Widget _buildPasswordField(
    TextEditingController controller,
    String label, {
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: _obscurePassword,
      decoration: InputDecoration(
        labelText: label,
        suffixIcon: IconButton(
          icon: Icon(_obscurePassword ? Icons.visibility : Icons.visibility_off),
          onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
        ),
      ),
      validator: validator ?? _passwordValidator,
    );
  }

  String? _requiredValidator(String? value) => value == null || value.isEmpty ? 'Required' : null;

  String? _passwordValidator(String? value) {
    if (value == null || value.length < 8) return 'Password must be at least 8 characters';
    return null;
  }

  String? _confirmPasswordValidator(String? value) {
    if (value != _passwordController.text) return 'Passwords do not match';
    return null;
  }

  String? _emailValidator(String? value) {
    if (value == null || value.isEmpty) return 'Email is required';
    if (!RegExp(r'^\S+@\S+\.\S+$').hasMatch(value)) return 'Enter a valid email';
    return null;
  }

  String? _phoneValidator(String? value) {
    if (value == null || value.length < 10) return 'Enter a valid phone number';
    return null;
  }
}
