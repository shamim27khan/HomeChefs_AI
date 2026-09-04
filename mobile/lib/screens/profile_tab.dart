import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/loading_indicator.dart';
import 'addresses_screen.dart';
import 'wallet_screen.dart';

class ProfileTab extends StatelessWidget {
  const ProfileTab({super.key});

  Future<void> _logout(BuildContext context) async {
    await context.read<AuthProvider>().logout();
    if (context.mounted) {
      Navigator.of(context).pushReplacementNamed('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final user = auth.user;
    final profile = auth.profile;
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: auth.isLoading
          ? const LoadingIndicator()
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                CircleAvatar(
                  radius: 48,
                  child: Text(
                    (user?.displayName ?? 'U')[0].toUpperCase(),
                    style: const TextStyle(fontSize: 36),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  user?.displayName ?? '',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                Text(
                  user?.email ?? '',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 8),
                Chip(
                  label: Text('Role: ${user?.role ?? 'customer'}'),
                  avatar: const Icon(Icons.person_outline),
                ),
                const Divider(height: 32),
                if (profile != null) ...[
                  const Text('Profile Details', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  if (profile['phone_number'] != null) _infoTile(Icons.phone, 'Phone', profile['phone_number'].toString()),
                  if (profile['area'] != null) _infoTile(Icons.location_on, 'Area', profile['area'].toString()),
                  if (profile['city'] != null) _infoTile(Icons.location_city, 'City', profile['city'].toString()),
                  if (profile['cuisine_specialties'] != null)
                    _infoTile(Icons.restaurant_menu, 'Cuisines', profile['cuisine_specialties'].toString()),
                ],
                const SizedBox(height: 16),
                ListTile(
                  leading: const Icon(Icons.location_on_outlined),
                  title: const Text('Addresses'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AddressesScreen())),
                ),
                ListTile(
                  leading: const Icon(Icons.account_balance_wallet_outlined),
                  title: const Text('Wallet'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const WalletScreen())),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () => _logout(context),
                  icon: const Icon(Icons.logout),
                  label: const Text('Logout'),
                  style: ElevatedButton.styleFrom(backgroundColor: Theme.of(context).colorScheme.error, foregroundColor: Colors.white),
                ),
              ],
            ),
    );
  }

  Widget _infoTile(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [Icon(icon, size: 18), const SizedBox(width: 8), Text('$label: '), Expanded(child: Text(value, style: const TextStyle(fontWeight: FontWeight.bold)))],
      ),
    );
  }
}
