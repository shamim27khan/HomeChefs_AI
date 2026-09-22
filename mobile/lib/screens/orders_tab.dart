import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../models/order.dart';
import '../services/order_service.dart';
import '../widgets/app_logo.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';
import '../widgets/order_card.dart';
import 'order_detail_screen.dart';
import 'track_order_screen.dart';

/// Mirrors the web my-orders page: a "My Orders" heading with a refresh
/// button, clickable stat cards that filter the list, and
/// All / Active / Completed tabs.
class OrdersTab extends StatefulWidget {
  const OrdersTab({super.key});

  @override
  State<OrdersTab> createState() => _OrdersTabState();
}

class _OrdersTabState extends State<OrdersTab>
    with AutomaticKeepAliveClientMixin, SingleTickerProviderStateMixin {
  final OrderService _service = OrderService();
  late final TabController _tabController;
  List<Order> _orders = [];
  bool _isLoading = true;
  String? _error;
  String _statFilter = 'all';

  static const _activeStatuses = [
    'pending',
    'confirmed',
    'preparing',
    'ready',
    'out_for_delivery',
    'picked_up',
    'in_transit',
  ];
  static const _preparingStatuses = ['confirmed', 'preparing', 'ready'];
  static const _completedStatuses = ['delivered', 'cancelled'];

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadOrders();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadOrders() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final orders = await _service.getCustomerOrders();
      orders.sort((a, b) =>
          (b.createdAt ?? DateTime(0)).compareTo(a.createdAt ?? DateTime(0)));
      if (mounted) setState(() => _orders = orders);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _filterFromStat(String filter) {
    setState(() => _statFilter = filter);
    _tabController.animateTo(0);
  }

  List<Order> get _allFiltered {
    switch (_statFilter) {
      case 'pending':
        return _orders.where((o) => o.orderStatus == 'pending').toList();
      case 'preparing':
        return _orders
            .where((o) => _preparingStatuses.contains(o.orderStatus))
            .toList();
      case 'completed':
        return _orders.where((o) => o.orderStatus == 'delivered').toList();
      default:
        return _orders;
    }
  }

  List<Order> get _activeOrders =>
      _orders.where((o) => _activeStatuses.contains(o.orderStatus)).toList();

  List<Order> get _completedOrders =>
      _orders.where((o) => _completedStatuses.contains(o.orderStatus)).toList();

  void _openOrder(Order order) {
    Navigator.of(context)
        .push(MaterialPageRoute(builder: (_) => OrderDetailScreen(order: order)))
        .then((_) => _loadOrders());
  }

  void _trackOrder(Order order) {
    Navigator.of(context)
        .push(MaterialPageRoute(builder: (_) => TrackOrderScreen(order: order)))
        .then((_) => _loadOrders());
  }

  /// Web: confirmDelivery() - customer confirms a 'ready' order arrived.
  Future<void> _confirmDelivery(Order order) async {
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
    if (confirmed != true || !mounted) return;
    try {
      await _service.confirmDelivery(order.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text(
                'Thank you for confirming delivery! You can now rate your order.')));
        _loadOrders();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  /// Web: showRatingModal() - star rating + optional feedback.
  Future<void> _rateOrder(Order order) async {
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
    if (submitted != true || !mounted) return;
    try {
      await _service.rateOrder(order.id, rating,
          comment: feedbackController.text.trim().isEmpty
              ? null
              : feedbackController.text.trim());
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Thank you for your rating!')));
        _loadOrders();
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
    super.build(context);
    return Scaffold(
      backgroundColor: AppColors.lightBg,
      appBar: brandedAppBar(
        automaticallyImplyLeading: false,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadOrders),
        ],
      ),
      body: _isLoading
          ? const LoadingIndicator()
          : _error != null
              ? ErrorMessage(message: _error!, onRetry: _loadOrders)
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.receipt_long,
                                  color: AppColors.secondary, size: 22),
                              SizedBox(width: 8),
                              Text(
                                'My Orders',
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.secondary,
                                ),
                              ),
                            ],
                          ),
                          OutlinedButton.icon(
                            onPressed: _loadOrders,
                            icon: const Icon(Icons.sync, size: 16),
                            label: const Text('Refresh'),
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 6),
                              textStyle: const TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      child: Row(
                        children: [
                          _statCard('Total Orders', _orders.length,
                              AppColors.info, 'all'),
                          _statCard(
                              'Pending',
                              _orders
                                  .where((o) => o.orderStatus == 'pending')
                                  .length,
                              AppColors.warning,
                              'pending'),
                          _statCard(
                              'Preparing',
                              _orders
                                  .where((o) => _preparingStatuses
                                      .contains(o.orderStatus))
                                  .length,
                              AppColors.primary,
                              'preparing'),
                          _statCard(
                              'Completed',
                              _orders
                                  .where((o) => o.orderStatus == 'delivered')
                                  .length,
                              AppColors.success,
                              'completed'),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      child: Container(
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppColors.border),
                        ),
                        child: TabBar(
                          controller: _tabController,
                          labelColor: AppColors.primary,
                          unselectedLabelColor: Colors.black54,
                          indicatorColor: AppColors.primary,
                          indicatorSize: TabBarIndicatorSize.tab,
                          dividerColor: Colors.transparent,
                          tabs: const [
                            Tab(text: 'All Orders'),
                            Tab(text: 'Active'),
                            Tab(text: 'Completed'),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Expanded(
                      child: TabBarView(
                        controller: _tabController,
                        children: [
                          _orderList(_allFiltered, 'No orders yet.'),
                          _orderList(_activeOrders, 'No active orders'),
                          _orderList(_completedOrders, 'No completed orders'),
                        ],
                      ),
                    ),
                  ],
                ),
    );
  }

  Widget _statCard(String label, int count, Color color, String filter) {
    final selected = _statFilter == filter;
    return Expanded(
      child: Card(
        elevation: selected ? 3 : 1,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: selected ? color : Colors.transparent,
            width: 1.5,
          ),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () => _filterFromStat(filter),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Column(
              children: [
                Text(
                  '$count',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: color,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  label,
                  style: const TextStyle(fontSize: 11, color: Colors.black54),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _orderList(List<Order> orders, String emptyMessage) {
    if (orders.isEmpty) {
      return Center(
        child:
            Text(emptyMessage, style: const TextStyle(color: Colors.black54)),
      );
    }
    return RefreshIndicator(
      onRefresh: _loadOrders,
      child: ListView.builder(
        itemCount: orders.length,
        itemBuilder: (context, index) => OrderCard(
          order: orders[index],
          onTap: () => _openOrder(orders[index]),
          onTrack: () => _trackOrder(orders[index]),
          onConfirmDelivery: () => _confirmDelivery(orders[index]),
          onRate: () => _rateOrder(orders[index]),
        ),
      ),
    );
  }
}
