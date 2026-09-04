import 'package:flutter/material.dart';
import '../models/order.dart';

class OrderCard extends StatelessWidget {
  final Order order;
  final VoidCallback? onTap;

  const OrderCard({super.key, required this.order, this.onTap});

  Color _statusColor(String status) {
    switch (status) {
      case 'delivered':
      case 'ready':
        return Colors.green;
      case 'preparing':
      case 'confirmed':
        return Colors.orange;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.blueGrey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    order.orderId ?? 'Order #${order.id}',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  Chip(
                    label: Text(order.orderStatus, style: const TextStyle(fontSize: 11)),
                    backgroundColor: _statusColor(order.orderStatus).withAlpha(30),
                    side: BorderSide.none,
                    visualDensity: VisualDensity.compact,
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(order.mealDetails ?? 'Meal', style: Theme.of(context).textTheme.bodyMedium),
              const SizedBox(height: 4),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Qty: ${order.portions}', style: Theme.of(context).textTheme.bodySmall),
                  Text('₹${order.totalAmount.toStringAsFixed(0)}', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
