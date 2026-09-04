import 'package:flutter/material.dart';
import '../models/daily_meal.dart';
import 'order_create_screen.dart';

class MealDetailScreen extends StatelessWidget {
  final DailyMeal meal;

  const MealDetailScreen({super.key, required this.meal});

  @override
  Widget build(BuildContext context) {
    final available = meal.availablePortions ?? meal.extraPortions;
    final canOrder = meal.isOrderable ?? available > 0;
    return Scaffold(
      appBar: AppBar(title: Text(meal.mainDish)),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(meal.mainDish, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 12),
            if (meal.sideDish != null && meal.sideDish!.isNotEmpty)
              Text('Side: ${meal.sideDish}', style: Theme.of(context).textTheme.titleMedium),
            if (meal.additionalItems != null && meal.additionalItems!.isNotEmpty)
              Text('Extras: ${meal.additionalItems}', style: Theme.of(context).textTheme.bodyLarge),
            const SizedBox(height: 16),
            Row(
              children: [
                const Icon(Icons.person_outline),
                const SizedBox(width: 8),
                Text('Chef: ${meal.chefUsername ?? 'Chef'}'),
              ],
            ),
            if (meal.chefArea != null && meal.chefArea!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Row(children: [const Icon(Icons.location_on_outlined), const SizedBox(width: 8), Text('Area: ${meal.chefArea}')]),
            ],
            const SizedBox(height: 16),
            Row(
              children: [
                const Icon(Icons.schedule),
                const SizedBox(width: 8),
                Text('Cut-off: ${meal.orderCutoffTime ?? 'N/A'}'),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('₹${meal.pricePerPortion.toStringAsFixed(0)} / portion', style: Theme.of(context).textTheme.titleLarge),
                Text('$available portions left', style: Theme.of(context).textTheme.titleMedium),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              children: [
                if (meal.pickupAvailable) Chip(label: const Text('Pickup available'), backgroundColor: Colors.green[50]),
                if (meal.deliveryAvailable) Chip(label: const Text('Delivery available'), backgroundColor: Colors.blue[50]),
              ],
            ),
            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: canOrder
                    ? () => Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => OrderCreateScreen(meal: meal)),
                        )
                    : null,
                child: Text(canOrder ? 'Order Now' : 'Not available'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
