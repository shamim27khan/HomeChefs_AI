import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../models/order.dart';

/// Order card mirroring the web my-orders card: order id + date on top with a
/// Bootstrap-style status badge, meal name with portions, chef and delivery
/// type meta line, total amount, and the web action buttons
/// (Details / Track / Confirm Delivery / Rate).
class OrderCard extends StatelessWidget {
  final Order order;
  final VoidCallback? onTap;
  final VoidCallback? onTrack;
  final VoidCallback? onConfirmDelivery;
  final VoidCallback? onRate;

  const OrderCard({
    super.key,
    required this.order,
    this.onTap,
    this.onTrack,
    this.onConfirmDelivery,
    this.onRate,
  });

  static const _trackableStatuses = [
    'pending',
    'confirmed',
    'preparing',
    'ready',
    'out_for_delivery',
    'picked_up',
    'in_transit',
  ];

  /// Badge colors matching the web statusColors map
  /// (pending=warning, confirmed=info, preparing=primary,
  ///  ready/delivered=success, cancelled=danger).
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
    if (date == null) return '';
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

  @override
  Widget build(BuildContext context) {
    final statusColor = _statusColor(order.orderStatus);
    final statusLabel = order.orderStatus
        .replaceAll('_', ' ')
        .split(' ')
        .map((w) => w.isEmpty ? w : w[0].toUpperCase() + w.substring(1))
        .join(' ');

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: Column(
        children: [
          InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Order #${order.orderId ?? order.id}',
                                style: Theme.of(context)
                                    .textTheme
                                    .titleSmall
                                    ?.copyWith(fontWeight: FontWeight.w700),
                              ),
                              if (order.createdAt != null)
                                Text(
                                  _formatDate(order.createdAt),
                                  style: const TextStyle(
                                      fontSize: 11, color: Colors.black45),
                                ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: statusColor,
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
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            order.mealDetails ?? 'Meal',
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                        ),
                        Text(
                          'x ${order.portions} portions',
                          style: const TextStyle(
                              fontSize: 12, color: Colors.black54),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        const Icon(Icons.person_outline,
                            size: 14, color: Colors.black45),
                        const SizedBox(width: 4),
                        Flexible(
                          child: Text(
                            order.chefUsername ?? '',
                            style: const TextStyle(
                                fontSize: 12, color: Colors.black54),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 8),
                          child:
                              Text('-', style: TextStyle(color: Colors.black38)),
                        ),
                        const Icon(Icons.local_shipping_outlined,
                            size: 14, color: Colors.black45),
                        const SizedBox(width: 4),
                        Text(
                          order.deliveryType ?? '',
                          style: const TextStyle(
                              fontSize: 12, color: Colors.black54),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    'Rs. ${order.totalAmount.toStringAsFixed(0)}',
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 15,
                      color: AppColors.secondary,
                    ),
                  ),
                ],
              ),
            ],
              ),
            ),
          ),
          _actionButtons(context),
        ],
      ),
    );
  }

  /// Web btn-group: Details / Track / Confirm Delivery / Rate buttons
  /// rendered under the card content, matching createOrderCard().
  Widget _actionButtons(BuildContext context) {
    final trackable = _trackableStatuses.contains(order.orderStatus);
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 0, 12, 10),
      child: Wrap(
        spacing: 8,
        runSpacing: 4,
        children: [
          _actionButton(
            icon: Icons.visibility_outlined,
            label: 'Details',
            color: AppColors.primary,
            onPressed: onTap,
          ),
          _actionButton(
            icon: Icons.map_outlined,
            label: 'Track',
            color: AppColors.success,
            onPressed: trackable ? onTrack : null,
          ),
          if (order.orderStatus == 'ready')
            _actionButton(
              icon: Icons.check_circle_outline,
              label: 'Confirm Delivery',
              color: AppColors.info,
              onPressed: onConfirmDelivery,
            ),
          if (order.orderStatus == 'delivered')
            _actionButton(
              icon: Icons.star_outline,
              label: 'Rate',
              color: AppColors.warning,
              onPressed: onRate,
            ),
        ],
      ),
    );
  }

  Widget _actionButton({
    required IconData icon,
    required String label,
    required Color color,
    VoidCallback? onPressed,
  }) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 14),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        disabledBackgroundColor: Colors.grey.shade300,
        disabledForegroundColor: Colors.white70,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        minimumSize: Size.zero,
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
        textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
      ),
    );
  }
}