import 'package:flutter/material.dart';
import '../models/address.dart';

class AddressCard extends StatelessWidget {
  final Address address;
  final VoidCallback? onTap;

  const AddressCard({super.key, required this.address, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          address.addressType.toUpperCase(),
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                        ),
                        if (address.isDefault) ...[
                          const SizedBox(width: 8),
                          Chip(
                            label: const Text('Default', style: TextStyle(fontSize: 10)),
                            visualDensity: VisualDensity.compact,
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(address.addressLine),
                    Text('${address.city}, ${address.postalCode}'),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }
}
