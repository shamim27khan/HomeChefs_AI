import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../models/order.dart';
import '../services/order_service.dart';
import '../widgets/app_logo.dart';
import '../widgets/loading_indicator.dart';
import 'track_order_screen.dart';

/// Mirrors the web "Order Details" modal from my_orders.html: an
/// Order Information section, a Meal Details section, optional
/// Delivery Address / Special Instructions blocks, and footer
/// actions (Track Order, Confirm Delivery, Rate, Cancel).
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

  static const _trackableStatuses = [
    'pending',
    'confirmed',
    'preparing',
    'ready',
    'out_for_delivery',
    'picked_up',
    'in_transit',
  ];

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

  Color _statusColor(String status) {
    switch (status) {
      case 'pending':
        return AppColors.warning;
      case 'confirmed':
        return AppColors.info;
      case 'preparing':
        return AppColors.primary;
      case 'ready':
        return AppColors.success;
      case 'out_for_delivery':
      case 'picked_up':
      case 'in_transit':
        return const Color(0xFF007BFF);
      case 'delivered':
        return AppColors.success;
      case 'cancelled':
        return const Color(0xFFDC3545);
      default:
        return Colors.blueGrey;
    }
  }

  String _formatDate(DateTime? date) {
    if (date == null) return 'Date not available';
    final d = date.toLocal();
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    final hour = d.hour % 12 == 0 ? 12 : d.hour % 12;
    final ampm = d.hour < 12 ? 'AM' : 'PM';
    final minute = d.minute.toString().padLeft(2, '0');
    return '${months[d.month - 1]} ${d.day}, ${d.year} $hour:$minute $ampm';
  }

  void _trackOrder() {
    Navigator.of(context)
        .push(MaterialPageRoute(
            builder: (_) => TrackOrderScreen(order: _order)))
        .then((_) => _refresh());
  }

  Future<void> _cancel() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancel Order'),
        content: const Text('Are you sure you want to cancel this order?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('No'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Yes, Cancel',
                style: TextStyle(color: Color(0xFFDC3545))),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await _service.cancelOrder(_order.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Order cancelled')));
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  /// Web: confirmDelivery() - customer confirms a 'ready' order arrived.
  Future<void> _confirmDelivery() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Confirm Delivery'),
        content: const Text('Have you received this order?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('No'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Yes'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await _service.confirmDelivery(_order.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text(
                'Thank you for confirming delivery! You can now rate your order.')));
        _refresh();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  /// Web: showRatingModal() - star rating + optional feedback (200 chars).
  Future<void> _rate() async {
    int rating = 0;
    final feedbackController = TextEditingController();
    final submitted = await showDialog<bool>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Rate Your Order'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Rating',
                  style: TextStyle(fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              Row(
                children: [
                  for (var i = 1; i <= 5; i++)
                    IconButton(
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                      icon: Icon(
                        Icons.star,
                        size: 30,
                        color: i <= rating
                            ? AppColors.warning
                            : const Color(0xFFDDDDDD),
                      ),
                      onPressed: () => setDialogState(() => rating = i),
                    ),
                ],
              ),
              const Text('Click on stars to rate',
                  style: TextStyle(fontSize: 11, color: Colors.black45)),
              const SizedBox(height: 12),
              const Text('Feedback (Optional)',
                  style: TextStyle(fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              TextField(
                controller: feedbackController,
                maxLines: 3,
                maxLength: 200,
                decoration: const InputDecoration(
                  hintText: 'Share your experience...',
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: rating == 0
                  ? null
                  : () => Navigator.of(context).pop(true),
              child: const Text('Submit Rating'),
            ),
          ],
        ),
      ),
    );
    if (submitted != true) return;
    try {
      await _service.rateOrder(_order.id, rating,
          comment: feedbackController.text.trim().isEmpty
              ? null
              : feedbackController.text.trim());
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Thank you for your rating!')));
        _refresh();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final statusLabel = _order.orderStatus
        .replaceAll('_', ' ')
        .split(' ')
        .map((w) => w.isEmpty ? w : w[0].toUpperCase() + w.substring(1))
        .join(' ');
    final trackable = _trackableStatuses.contains(_order.orderStatus);

    return Scaffold(
      backgroundColor: AppColors.lightBg,
      appBar: brandedAppBar(title: 'Order Details'),
      body: _isLoading
          ? const LoadingIndicator()
          : RefreshIndicator(
              onRefresh: _refresh,
              child: ListView(
                padding: const EdgeInsets.all(12),
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Order Information',
                              style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.secondary)),
                          const SizedBox(height: 10),
                          _infoRow('Order ID',
                              '#${_order.orderId ?? _order.id}'),
                          _infoRowWidget(
                            'Status',
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 3),
                              decoration: BoxDecoration(
                                color: _statusColor(_order.orderStatus),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                statusLabel,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ),
                          _infoRow('Placed on',
                              _formatDate(_order.createdAt)),
                          _infoRow('Payment', _order.paymentStatus),
                          _infoRow('Total Amount',
                              'Rs. ${_order.totalAmount.toStringAsFixed(0)}'),
                          const Divider(height: 28),
                          const Text('Meal Details',
                              style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.secondary)),
                          const SizedBox(height: 10),
                          _infoRow('Meal', _order.mealDetails ?? 'N/A'),
                          _infoRow('Chef', _order.chefUsername ?? 'N/A'),
                          _infoRow('Portions', '${_order.portions}'),
                          _infoRow('Price per portion',
                              'Rs. ${_order.pricePerPortion.toStringAsFixed(0)}'),
                          _infoRow(
                              'Delivery Type', _order.deliveryType ?? 'N/A'),
                        ],
                      ),
                    ),
                  ),
                  if (_order.deliveryAddress != null &&
                      _order.deliveryAddress!.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    _textBlockCard(
                        'Delivery Address', _order.deliveryAddress!),
                  ],
                  if (_order.specialInstructions != null &&
                      _order.specialInstructions!.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    _textBlockCard('Special Instructions',
                        _order.specialInstructions!),
                  ],
                  const SizedBox(height: 16),
                  if (trackable)
                    ElevatedButton.icon(
                      onPressed: _trackOrder,
                      icon: const Icon(Icons.map_outlined),
                      label: const Text('Track Order'),
                    ),
                  if (_order.orderStatus == 'ready') ...[
                    const SizedBox(height: 8),
                    ElevatedButton.icon(
                      onPressed: _confirmDelivery,
                      icon: const Icon(Icons.check_circle_outline),
                      label: const Text('Confirm Delivery'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.info,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                  if (_order.orderStatus == 'delivered') ...[
                    const SizedBox(height: 8),
                    ElevatedButton.icon(
                      onPressed: _rate,
                      icon: const Icon(Icons.star_outline),
                      label: const Text('Rate Order'),
                      style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.success),
                    ),
                  ],
                  if (_order.orderStatus == 'pending') ...[
                    const SizedBox(height: 8),
                    OutlinedButton.icon(
                      onPressed: _cancel,
                      icon: const Icon(Icons.cancel_outlined),
                      label: const Text('Cancel Order'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFFDC3545),
                        side: const BorderSide(color: Color(0xFFDC3545)),
                      ),
                    ),
                  ],
                  const SizedBox(height: 12),
                ],
              ),
            ),
    );
  }

  Widget _textBlockCard(String title, String body) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: AppColors.secondary)),
            const SizedBox(height: 6),
            Text(body,
                style:
                    const TextStyle(fontSize: 13, color: Colors.black87)),
          ],
        ),
      ),
    );
  }

  Widget _infoRow(String label, String value) =>
      _infoRowWidget(label, Text(value));

  Widget _infoRowWidget(String label, Widget value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 130,
            child: Text('$label:',
                style: const TextStyle(fontWeight: FontWeight.w600)),
          ),
          Expanded(child: value),
        ],
      ),
    );
  }
}
