import 'package:flutter/material.dart';
import '../models/order.dart';
import '../services/order_service.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';
import '../widgets/order_card.dart';
import 'order_detail_screen.dart';

class ChefOrdersTab extends StatefulWidget {
  const ChefOrdersTab({super.key});

  @override
  State<ChefOrdersTab> createState() => _ChefOrdersTabState();
}

class _ChefOrdersTabState extends State<ChefOrdersTab> with AutomaticKeepAliveClientMixin {
  final OrderService _service = OrderService();
  List<Order> _orders = [];
  bool _isLoading = true;
  String? _error;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final orders = await _service.getChefOrders();
      if (mounted) setState(() => _orders = orders);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _updateStatus(Order order, String status) async {
    try {
      await _service.updateOrderStatus(order.id, status);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Status updated to $status')));
        await _loadOrders();
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Orders'),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _loadOrders)],
      ),
      body: _isLoading
          ? const LoadingIndicator()
          : _error != null
              ? ErrorMessage(message: _error!, onRetry: _loadOrders)
              : _orders.isEmpty
                  ? const Center(child: Text('No orders yet.'))
                  : ListView.builder(
                      itemCount: _orders.length,
                      itemBuilder: (context, index) => OrderCard(
                        order: _orders[index],
                        onTap: () => _showActions(_orders[index]),
                      ),
                    ),
    );
  }

  void _showActions(Order order) {
    final statuses = ['pending', 'confirmed', 'preparing', 'ready', 'cancelled'];
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text('Update Status', style: TextStyle(fontWeight: FontWeight.bold)),
            ),
            ...statuses.map((status) => ListTile(
                  title: Text(status.toUpperCase()),
                  leading: order.orderStatus == status ? const Icon(Icons.check_circle, color: Colors.green) : const Icon(Icons.circle_outlined),
                  onTap: () {
                    Navigator.of(context).pop();
                    _updateStatus(order, status);
                  },
                )),
            ListTile(
              title: const Text('View details'),
              leading: const Icon(Icons.info_outline),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => OrderDetailScreen(order: order))).then((_) => _loadOrders());
              },
            ),
          ],
        ),
      ),
    );
  }
}
