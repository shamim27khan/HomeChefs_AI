import 'package:flutter/material.dart';
import '../services/customer_service.dart';
import '../widgets/loading_indicator.dart';

class AddAddressScreen extends StatefulWidget {
  const AddAddressScreen({super.key});

  @override
  State<AddAddressScreen> createState() => _AddAddressScreenState();
}

class _AddAddressScreenState extends State<AddAddressScreen> {
  final _formKey = GlobalKey<FormState>();
  final _addressLineController = TextEditingController();
  final _landmarkController = TextEditingController();
  final _identifierController = TextEditingController();
  final _cityController = TextEditingController();
  final _stateController = TextEditingController();
  final _postalController = TextEditingController();
  String _addressType = 'home';
  bool _isDefault = false;
  bool _isSubmitting = false;
  String? _error;

  final List<String> _types = ['home', 'work', 'other'];

  @override
  void dispose() {
    _addressLineController.dispose();
    _landmarkController.dispose();
    _identifierController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _postalController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSubmitting = true);
    try {
      final service = CustomerService();
      await service.addAddress({
        'address_type': _addressType,
        'address_line': _addressLineController.text.trim(),
        'landmark': _landmarkController.text.trim().isEmpty ? null : _landmarkController.text.trim(),
        'address_identifier': _identifierController.text.trim().isEmpty ? null : _identifierController.text.trim(),
        'city': _cityController.text.trim(),
        'state': _stateController.text.trim().isEmpty ? null : _stateController.text.trim(),
        'postal_code': _postalController.text.trim(),
        'is_default': _isDefault,
      });
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add Address')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              DropdownButtonFormField<String>(
                initialValue: _addressType,
                decoration: const InputDecoration(labelText: 'Address Type'),
                items: _types.map((t) => DropdownMenuItem(value: t, child: Text(t.toUpperCase()))).toList(),
                onChanged: (value) => setState(() => _addressType = value!),
              ),
              const SizedBox(height: 12),
              TextFormField(controller: _addressLineController, decoration: const InputDecoration(labelText: 'Address Line'), validator: _required),
              const SizedBox(height: 12),
              TextFormField(controller: _cityController, decoration: const InputDecoration(labelText: 'City'), validator: _required),
              const SizedBox(height: 12),
              TextFormField(controller: _stateController, decoration: const InputDecoration(labelText: 'State')),
              const SizedBox(height: 12),
              TextFormField(controller: _postalController, decoration: const InputDecoration(labelText: 'Postal Code'), validator: _required),
              const SizedBox(height: 12),
              TextFormField(controller: _landmarkController, decoration: const InputDecoration(labelText: 'Landmark (optional)')),
              const SizedBox(height: 12),
              TextFormField(controller: _identifierController, decoration: const InputDecoration(labelText: 'Identifier (optional)')),
              const SizedBox(height: 12),
              SwitchListTile(
                title: const Text('Set as default'),
                value: _isDefault,
                onChanged: (value) => setState(() => _isDefault = value),
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
              ],
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _save,
                  child: _isSubmitting ? const LoadingIndicator() : const Text('Save Address'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String? _required(String? value) => value == null || value.isEmpty ? 'Required' : null;
}
