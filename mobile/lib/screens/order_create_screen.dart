import 'package:flutter/material.dart';
import '../models/address.dart';
import '../models/daily_meal.dart';
import '../services/customer_service.dart';
import '../services/order_service.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';

class OrderCreateScreen extends StatefulWidget {
  final DailyMeal meal;

  const OrderCreateScreen({super.key, required this.meal});

  @override
  State<OrderCreateScreen> createState() => _OrderCreateScreenState();
}

class _OrderCreateScreenState extends State<OrderCreateScreen> {
  final OrderService _orderService = OrderService();
  final CustomerService _customerService = CustomerService();
  int _portions = 1;
  String _deliveryType = 'pickup';
  String? _deliveryAddress;
  List<Address> _addresses = [];
  bool _loadingAddresses = true;
  bool _isSubmitting = false;
  String? _error;
  final _instructionsController = TextEditingController();
  final _addressController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadAddresses();
  }

  @override
  void dispose() {
    _instructionsController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  Future<void> _loadAddresses() async {
    try {
      final addresses = await _customerService.getAddresses();
      if (mounted) {
        setState(() {
          _addresses = addresses;
          _loadingAddresses = false;
          if (addresses.isNotEmpty) {
            _deliveryAddress = addresses.firstWhere((a) => a.isDefault, orElse: () => addresses.first).addressLine;
          }
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loadingAddresses = false);
    }
  }

  Future<void> _placeOrder() async {
    if (_deliveryType == 'delivery' && _deliveryAddress == null && _addressController.text.isEmpty) {
      setState(() => _error = 'Please provide a delivery address.');
      return;
    }
    setState(() => _isSubmitting = true);
    try {
      final address = _deliveryType == 'delivery'
          ? (_deliveryAddress ?? _addressController.text.trim())
          : null;
      await _orderService.createDailyMealOrder(
        dailyMealId: widget.meal.id,
        portions: _portions,
        deliveryType: _deliveryType,
        deliveryAddress: address,
        specialInstructions: _instructionsController.text.trim().isEmpty ? null : _instructionsController.text.trim(),
      );
      if (mounted) {
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Order Placed'),
            content: const Text('Your order has been placed successfully.'),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  Navigator.of(context).pop();
                },
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  double get total => widget.meal.pricePerPortion * _portions;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Place Order')),
      body: _loadingAddresses ? const LoadingIndicator() : Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.meal.mainDish, style: Theme.of(context).textTheme.headlineSmall),
            Text('₹${widget.meal.pricePerPortion.toStringAsFixed(0)} per portion'),
            const SizedBox(height: 16),
            Row(
              children: [
                IconButton(onPressed: _portions > 1 ? () => setState(() => _portions--) : null, icon: const Icon(Icons.remove_circle_outline)),
                Text('$_portions', style: Theme.of(context).textTheme.headlineSmall),
                IconButton(onPressed: () => setState(() => _portions++), icon: const Icon(Icons.add_circle_outline)),
                const Spacer(),
                Text('Total: ₹${total.toStringAsFixed(0)}', style: Theme.of(context).textTheme.titleLarge),
              ],
            ),
            const SizedBox(height: 16),
            const Text('Delivery Type'),
            Row(
              children: [
                Expanded(
                  child: ChoiceChip(
                    label: const Text('Pickup'),
                    selected: _deliveryType == 'pickup',
                    onSelected: (selected) => setState(() => _deliveryType = 'pickup'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ChoiceChip(
                    label: const Text('Delivery'),
                    selected: _deliveryType == 'delivery',
                    onSelected: (selected) => setState(() => _deliveryType = 'delivery'),
                  ),
                ),
              ],
            ),
            if (_deliveryType == 'delivery') ...[
              const SizedBox(height: 12),
              if (_addresses.isNotEmpty)
                DropdownButtonFormField<String>(
                  initialValue: _deliveryAddress,
                  decoration: const InputDecoration(labelText: 'Select address'),
                  items: _addresses
                      .map((a) => DropdownMenuItem(value: a.addressLine, child: Text(a.shortDisplay)))
                      .toList(),
                  onChanged: (value) => setState(() => _deliveryAddress = value),
                )
              else
                TextField(
                  controller: _addressController,
                  decoration: const InputDecoration(labelText: 'Delivery address'),
                  maxLines: 2,
                ),
            ],
            const SizedBox(height: 16),
            TextField(
              controller: _instructionsController,
              decoration: const InputDecoration(labelText: 'Special instructions (optional)'),
              maxLines: 2,
            ),
            if (_error != null) ...[
              const SizedBox(height: 12),
              ErrorMessage(message: _error!),
            ],
            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _placeOrder,
                child: _isSubmitting ? const LoadingIndicator() : const Text('Place Order'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
