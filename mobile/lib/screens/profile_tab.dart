import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../providers/auth_provider.dart';
import '../widgets/app_logo.dart';
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
      appBar: brandedAppBar(automaticallyImplyLeading: false),
      body: auth.isLoading
          ? const LoadingIndicator()
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Center(
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: AppColors.primary, width: 2.5),
                      boxShadow: const [
                        BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, 4)),
                      ],
                    ),
                    child: CircleAvatar(
                      radius: 44,
                      backgroundColor: AppColors.primary,
                      child: Text(
                        (user?.displayName ?? 'U')[0].toUpperCase(),
                        style: const TextStyle(
                          fontSize: 34,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  user?.displayName ?? '',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: AppColors.secondary,
                      ),
                ),
                Text(
                  user?.email ?? '',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.black54),
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
                // Addresses and Wallet are customer-only features; the backend
                // returns 403 for other roles, so hide them for chefs/admins.
                if (user?.role == 'customer') ...[
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
                ],
                const SizedBox(height: 24),
                Center(
                  child: OutlinedButton.icon(
                    onPressed: () => _logout(context),
                    icon: const Icon(Icons.logout, size: 18),
                    label: const Text('Logout'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.primary,
                      side: const BorderSide(color: AppColors.primary),
                      padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                    ),
                  ),
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
