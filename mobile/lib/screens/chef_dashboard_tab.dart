import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../providers/auth_provider.dart';
import '../services/chef_service.dart';
import '../services/order_service.dart';
import '../widgets/app_logo.dart';
import '../widgets/loading_indicator.dart';

class ChefDashboardTab extends StatefulWidget {
  const ChefDashboardTab({super.key});

  @override
  State<ChefDashboardTab> createState() => _ChefDashboardTabState();
}

class _ChefDashboardTabState extends State<ChefDashboardTab> {
  final ChefService _chefService = ChefService();
  final OrderService _orderService = OrderService();

  Map<String, dynamic>? _summary;
  int _mealCount = 0;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      // Load stats in parallel so the dashboard renders quickly.
      final results = await Future.wait([
        _orderService.getChefOrderSummary(),
        _chefService.getMyMeals(),
      ]);
      if (mounted) {
        setState(() {
          _summary = results[0] as Map<String, dynamic>;
          _mealCount = (results[1] as List).length;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().user;
    final profile = context.watch<AuthProvider>().profile;
    final isVerified = profile != null && profile['is_verified'] == true;
    final summary = _summary?['summary'] as Map<String, dynamic>?;

    return Scaffold(
      backgroundColor: AppColors.lightBg,
      appBar: brandedAppBar(title: 'Chef Dashboard', automaticallyImplyLeading: false),
      body: RefreshIndicator(
        onRefresh: _loadDashboard,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Hero welcome banner (mirrors the web hero-section gradient)
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.primary, AppColors.primaryLight],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Hello, ${user?.displayName ?? 'Chef'}!',
                    style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Manage your meals, orders and earnings.',
                    style: TextStyle(color: Colors.white70),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: isVerified ? AppColors.success : AppColors.warning,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(isVerified ? Icons.verified : Icons.pending, color: Colors.white, size: 14),
                        const SizedBox(width: 4),
                        Text(
                          isVerified ? 'Verified' : 'Pending Verification',
                          style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w600),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            const SectionTitle('Today at a glance'),
            const SizedBox(height: 16),
            if (_isLoading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: LoadingIndicator(),
              )
            else if (_error != null)
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Text(_error!, textAlign: TextAlign.center),
                    TextButton(onPressed: _loadDashboard, child: const Text('Retry')),
                  ],
                ),
              )
            else
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 1.6,
                children: [
                  _StatCard(
                    icon: Icons.set_meal,
                    label: 'Meals Today',
                    value: '$_mealCount',
                    color: AppColors.primary,
                  ),
                  _StatCard(
                    icon: Icons.receipt_long,
                    label: 'Orders',
                    value: '${summary?['total_orders'] ?? 0}',
                    color: AppColors.info,
                  ),
                  _StatCard(
                    icon: Icons.currency_rupee,
                    label: 'Earnings',
                    value: 'Rs. ${summary?['total_earnings'] ?? 0}',
                    color: AppColors.success,
                  ),
                  _StatCard(
                    icon: Icons.hourglass_top,
                    label: 'Pending',
                    value: '${summary?['pending_orders'] ?? 0}',
                    color: AppColors.warning,
                  ),
                ],
              ),
            const SizedBox(height: 20),
            Card(
              child: ListTile(
                leading: const Icon(Icons.lightbulb_outline, color: AppColors.warning),
                title: const Text('Quick tip'),
                subtitle: const Text('Add a new meal from the My Meals tab and set portions for the day.'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatCard({required this.icon, required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 26),
            const Spacer(),
            Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: AppColors.secondary)),
            Text(label, style: const TextStyle(fontSize: 12, color: Colors.black54)),
          ],
        ),
      ),
    );
  }
}