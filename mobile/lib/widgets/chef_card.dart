import 'package:flutter/material.dart';
import '../models/chef.dart';

class ChefCard extends StatelessWidget {
  final Chef chef;
  final VoidCallback? onTap;

  const ChefCard({super.key, required this.chef, this.onTap});

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
                  Expanded(
                    child: Text(
                      chef.displayName,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ),
                  if (chef.isVerified) const Icon(Icons.verified, size: 18, color: Colors.green),
                ],
              ),
              const SizedBox(height: 4),
              if (chef.area != null && chef.area!.isNotEmpty)
                Text('${chef.area}${chef.city != null ? ', ${chef.city}' : ''}', style: Theme.of(context).textTheme.bodySmall),
              if (chef.cuisineSpecialties != null && chef.cuisineSpecialties!.isNotEmpty)
                Text(chef.cuisineSpecialties!, style: Theme.of(context).textTheme.bodySmall),
              if (chef.averageRating != null && chef.averageRating! > 0)
                Row(
                  children: [
                    const Icon(Icons.star, size: 16, color: Colors.amber),
                    Text(' ${chef.averageRating} (${chef.totalRatings})'),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}
