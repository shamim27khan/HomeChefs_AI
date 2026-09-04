import 'package:flutter/material.dart';
import '../models/order.dart';
import '../services/order_service.dart';
import '../widgets/loading_indicator.dart';

class OrderDetailScreen extends StatefulWidget {
  final Order order;

  const OrderDetailScreen({super.key, required this.order});

  @override
  State<OrderDetailScreen> createState() => _OrderDetailScreenState();
}

class _OrderDetailScreenState extends State<OrderDetailScreen> {
  final OrderService _service = OrderService();
  late Order _order;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _order = widget.order;
    _refresh();
  }

  Future<void> _refresh() async {
    setState(() => _isLoading = true);
    try {
      final updated = await _service.getOrderDetail(_order.id);
      if (mounted) setState(() => _order = updated);
    } catch (_) {}
    if (mounted) setState(() => _isLoading = false);
  }

  Future<void> _cancel() async {
    try {
      await _service.cancelOrder(_order.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Order cancelled')));
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  Future<void> _rate() async {
    int rating = 5;
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Rate Order'),
        content: StatefulBuilder(
          builder: (context, setDialogState) => Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('How was your meal?'),
              Slider(
                value: rating.toDouble(),
                min: 1,
                max: 5,
                divisions: 4,
                label: rating.toString(),
                onChanged: (value) => setDialogState(() => rating = value.toInt()),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () {
            if (mounted) Navigator.of(context).pop();
          }, child: const Text('Cancel')),
          TextButton(
            onPressed: () async {
              final messenger = ScaffoldMessenger.of(context);
              Navigator.of(context).pop();
              try {
                await _service.rateOrder(_order.id, rating);
                if (!mounted) return;
                messenger.showSnackBar(const SnackBar(content: Text('Rating submitted')));
              } catch (e) {
                if (!mounted) return;
                messenger.showSnackBar(SnackBar(content: Text(e.toString())));
              }
            },
            child: const Text('Submit'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Order ${_order.orderId ?? '#${_order.id}'}}')),
      body: _isLoading
          ? const LoadingIndicator()
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: ListView(
                children: [
                  _infoRow('Meal', _order.mealDetails ?? 'N/A'),
                  _infoRow('Status', _order.orderStatus),
                  _infoRow('Payment', _order.paymentStatus),
                  _infoRow('Portions', '${_order.portions}'),
                  _infoRow('Total', '₹${_order.totalAmount.toStringAsFixed(0)}'),
                  _infoRow('Delivery', _order.deliveryType ?? 'N/A'),
                  if (_order.deliveryAddress != null && _order.deliveryAddress!.isNotEmpty)
                    _infoRow('Address', _order.deliveryAddress!),
                  if (_order.specialInstructions != null && _order.specialInstructions!.isNotEmpty)
                    _infoRow('Instructions', _order.specialInstructions!),
                  const SizedBox(height: 24),
                  if (_order.orderStatus == 'pending')
                    ElevatedButton.icon(
                      onPressed: _cancel,
                      icon: const Icon(Icons.cancel_outlined),
                      label: const Text('Cancel Order'),
                    ),
                  if (_order.orderStatus == 'delivered')
                    ElevatedButton.icon(
                      onPressed: _rate,
                      icon: const Icon(Icons.star_outline),
                      label: const Text('Rate Order'),
                    ),
                ],
              ),
            ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 110, child: Text(label, style: const TextStyle(fontWeight: FontWeight.bold))),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
