import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'meals_tab.dart';
import 'chefs_tab.dart';
import 'orders_tab.dart';
import 'profile_tab.dart';
import 'chef_dashboard_tab.dart';
import 'chef_meals_tab.dart';
import 'chef_orders_tab.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _NavItem {
  final Widget screen;
  final IconData icon;
  final String label;

  _NavItem({required this.screen, required this.icon, required this.label});
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final role = context.watch<AuthProvider>().user?.role ?? 'customer';
    final isChef = role == 'chef';

    final items = isChef
        ? [
            _NavItem(screen: const ChefDashboardTab(), icon: Icons.dashboard, label: 'Dashboard'),
            _NavItem(screen: const ChefMealsTab(), icon: Icons.set_meal, label: 'My Meals'),
            _NavItem(screen: const ChefOrdersTab(), icon: Icons.receipt_long, label: 'Orders'),
            _NavItem(screen: const ProfileTab(), icon: Icons.person, label: 'Profile'),
          ]
        : [
            _NavItem(screen: const MealsTab(), icon: Icons.restaurant_menu, label: 'Meals'),
            _NavItem(screen: const ChefsTab(), icon: Icons.search, label: 'Chefs'),
            _NavItem(screen: const OrdersTab(), icon: Icons.receipt_long, label: 'Orders'),
            _NavItem(screen: const ProfileTab(), icon: Icons.person, label: 'Profile'),
          ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: items.map((e) => e.screen).toList(),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        items: items
            .map((e) => BottomNavigationBarItem(icon: Icon(e.icon), label: e.label))
            .toList(),
      ),
    );
  }
}
