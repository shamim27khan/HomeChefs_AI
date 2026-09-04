import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class ChefDashboardTab extends StatelessWidget {
  const ChefDashboardTab({super.key});

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().user;
    final profile = context.watch<AuthProvider>().profile;
    return Scaffold(
      appBar: AppBar(title: const Text('Chef Dashboard')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Hello, ${user?.displayName ?? 'Chef'}!', style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            const Text('Manage your meals, orders and earnings from the tabs below.'),
            const SizedBox(height: 24),
            if (profile != null && profile['is_verified'] == true)
              const Chip(
                avatar: Icon(Icons.verified, color: Colors.white, size: 18),
                label: Text('Verified'),
                backgroundColor: Colors.green,
                labelStyle: TextStyle(color: Colors.white),
              )
            else
              const Chip(
                avatar: Icon(Icons.pending, color: Colors.white, size: 18),
                label: Text('Pending Verification'),
                backgroundColor: Colors.orange,
                labelStyle: TextStyle(color: Colors.white),
              ),
            const SizedBox(height: 24),
            const LinearProgressIndicator(value: null),
            const SizedBox(height: 8),
            const Text('Quick tip: Add a new meal and set portions for the day.'),
          ],
        ),
      ),
    );
  }
}
