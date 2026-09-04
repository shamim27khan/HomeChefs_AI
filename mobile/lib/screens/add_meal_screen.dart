import 'package:flutter/material.dart';
import '../services/chef_service.dart';
import '../widgets/loading_indicator.dart';

class AddMealScreen extends StatefulWidget {
  const AddMealScreen({super.key});

  @override
  State<AddMealScreen> createState() => _AddMealScreenState();
}

class _AddMealScreenState extends State<AddMealScreen> {
  final _formKey = GlobalKey<FormState>();
  final _mainDishController = TextEditingController();
  final _sideDishController = TextEditingController();
  final _additionalController = TextEditingController();
  final _priceController = TextEditingController();
  final _portionsController = TextEditingController();
  final _radiusController = TextEditingController();
  String _mealType = 'lunch';
  bool _pickup = true;
  bool _delivery = false;
  bool _isSubmitting = false;
  String? _error;

  final List<String> _mealTypes = ['breakfast', 'lunch', 'dinner', 'snacks'];

  @override
  void dispose() {
    _mainDishController.dispose();
    _sideDishController.dispose();
    _additionalController.dispose();
    _priceController.dispose();
    _portionsController.dispose();
    _radiusController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    if (!_pickup && !_delivery) {
      setState(() => _error = 'Select at least one delivery option.');
      return;
    }
    setState(() => _isSubmitting = true);
    try {
      final service = ChefService();
      final body = {
        'date': DateTime.now().toIso8601String().split('T').first,
        'meal_type': _mealType,
        'main_dish': _mainDishController.text.trim(),
        'side_dish': _sideDishController.text.trim().isEmpty ? null : _sideDishController.text.trim(),
        'additional_items': _additionalController.text.trim().isEmpty ? null : _additionalController.text.trim(),
        'extra_portions': int.parse(_portionsController.text.trim()),
        'price_per_portion': double.parse(_priceController.text.trim()),
        'pickup_available': _pickup,
        'delivery_available': _delivery,
        'delivery_radius': _delivery ? int.tryParse(_radiusController.text.trim()) ?? 3 : 3,
      };
      await service.addDailyMeal(body);
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
      appBar: AppBar(title: const Text('Add Daily Meal')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              DropdownButtonFormField<String>(
                initialValue: _mealType,
                decoration: const InputDecoration(labelText: 'Meal Type'),
                items: _mealTypes.map((t) => DropdownMenuItem(value: t, child: Text(t[0].toUpperCase() + t.substring(1)))).toList(),
                onChanged: (value) => setState(() => _mealType = value!),
              ),
              const SizedBox(height: 12),
              TextFormField(controller: _mainDishController, decoration: const InputDecoration(labelText: 'Main Dish'), validator: _required),
              const SizedBox(height: 12),
              TextFormField(controller: _sideDishController, decoration: const InputDecoration(labelText: 'Side Dish (optional)')),
              const SizedBox(height: 12),
              TextFormField(controller: _additionalController, decoration: const InputDecoration(labelText: 'Additional Items (optional)'), maxLines: 2),
              const SizedBox(height: 12),
              TextFormField(
                controller: _priceController,
                decoration: const InputDecoration(labelText: 'Price per portion (₹)'),
                keyboardType: TextInputType.number,
                validator: _numberValidator,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _portionsController,
                decoration: const InputDecoration(labelText: 'Extra portions available'),
                keyboardType: TextInputType.number,
                validator: _numberValidator,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: CheckboxListTile(
                      title: const Text('Pickup'),
                      value: _pickup,
                      onChanged: (value) => setState(() => _pickup = value!),
                    ),
                  ),
                  Expanded(
                    child: CheckboxListTile(
                      title: const Text('Delivery'),
                      value: _delivery,
                      onChanged: (value) => setState(() => _delivery = value!),
                    ),
                  ),
                ],
              ),
              if (_delivery)
                TextFormField(
                  controller: _radiusController,
                  decoration: const InputDecoration(labelText: 'Delivery radius (km)'),
                  keyboardType: TextInputType.number,
                  validator: (value) {
                    if (_delivery && (value == null || value.isEmpty)) return 'Required for delivery';
                    return null;
                  },
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
                  child: _isSubmitting ? const LoadingIndicator() : const Text('Add Meal'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String? _required(String? value) => value == null || value.isEmpty ? 'Required' : null;

  String? _numberValidator(String? value) {
    if (value == null || value.isEmpty || double.tryParse(value) == null) return 'Enter a valid number';
    return null;
  }
}
