import 'package:flutter/material.dart';
import '../models/daily_meal.dart';

class MealCard extends StatelessWidget {
  final DailyMeal meal;
  final VoidCallback? onTap;

  const MealCard({super.key, required this.meal, this.onTap});

  @override
  Widget build(BuildContext context) {
    final available = meal.availablePortions ?? meal.extraPortions;
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
                  Expanded(
                    child: Text(
                      meal.mainDish,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ),
                  Chip(
                    label: Text('₹${meal.pricePerPortion.toStringAsFixed(0)}'),
                    backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                  ),
                ],
              ),
              if (meal.sideDish != null && meal.sideDish!.isNotEmpty)
                Text('Side: ${meal.sideDish}', style: Theme.of(context).textTheme.bodySmall),
              if (meal.additionalItems != null && meal.additionalItems!.isNotEmpty)
                Text('Extras: ${meal.additionalItems}', style: Theme.of(context).textTheme.bodySmall),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('${meal.chefUsername ?? 'Chef'} • ${meal.chefArea ?? ''}', style: Theme.of(context).textTheme.bodySmall),
                  Text('$available left', style: Theme.of(context).textTheme.bodySmall),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
