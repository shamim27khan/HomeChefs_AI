import 'package:flutter/material.dart';
import '../models/order.dart';
import '../services/order_service.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';
import '../widgets/order_card.dart';
import 'order_detail_screen.dart';

class OrdersTab extends StatefulWidget {
  const OrdersTab({super.key});

  @override
  State<OrdersTab> createState() => _OrdersTabState();
}

class _OrdersTabState extends State<OrdersTab> with AutomaticKeepAliveClientMixin {
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
      final orders = await _service.getCustomerOrders();
      if (mounted) setState(() => _orders = orders);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
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
                        onTap: () => Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => OrderDetailScreen(order: _orders[index])),
                        ).then((_) => _loadOrders()),
                      ),
                    ),
    );
  }
}
