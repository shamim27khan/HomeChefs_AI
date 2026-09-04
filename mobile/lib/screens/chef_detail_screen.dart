import 'package:flutter/material.dart';
import '../models/chef.dart';
import '../models/daily_meal.dart';
import '../services/chef_service.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';
import '../widgets/meal_card.dart';
import 'meal_detail_screen.dart';

class ChefDetailScreen extends StatefulWidget {
  final Chef chef;

  const ChefDetailScreen({super.key, required this.chef});

  @override
  State<ChefDetailScreen> createState() => _ChefDetailScreenState();
}

class _ChefDetailScreenState extends State<ChefDetailScreen> {
  final ChefService _service = ChefService();
  Chef? _chef;
  List<DailyMeal> _meals = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadChef();
  }

  Future<void> _loadChef() async {
    setState(() => _isLoading = true);
    try {
      _chef = await _service.getChefDetail(widget.chef.id);
      // Also load today's meals and filter by this chef
      final meals = await _service.getTodayMeals();
      _meals = meals.where((m) => m.chefInfo?.id == widget.chef.id).toList();
      if (mounted) setState(() => _error = null);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final chef = _chef ?? widget.chef;
    return Scaffold(
      appBar: AppBar(title: Text(chef.displayName)),
      body: _isLoading
          ? const LoadingIndicator()
          : _error != null
              ? ErrorMessage(message: _error!, onRetry: _loadChef)
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    Text(chef.displayName, style: Theme.of(context).textTheme.headlineSmall),
                    if (chef.cuisineSpecialties != null && chef.cuisineSpecialties!.isNotEmpty)
                      Text('Cuisines: ${chef.cuisineSpecialties}', style: Theme.of(context).textTheme.bodyLarge),
                    if (chef.fullAddress != null && chef.fullAddress!.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Row(children: [const Icon(Icons.location_on, size: 18), const SizedBox(width: 6), Expanded(child: Text(chef.fullAddress!))]),
                    ],
                    if (chef.averageRating != null && chef.averageRating! > 0) ...[
                      const SizedBox(height: 8),
                      Row(children: [
                        const Icon(Icons.star, color: Colors.amber, size: 18),
                        Text(' ${chef.averageRating} (${chef.totalRatings} ratings)'),
                      ]),
                    ],
                    if (chef.isVerified) ...[
                      const SizedBox(height: 8),
                      const Row(children: [Icon(Icons.verified, color: Colors.green, size: 18), SizedBox(width: 6), Text('Verified Chef')]),
                    ],
                    const Divider(height: 32),
                    Text('Today\'s Meals', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    if (_meals.isEmpty)
                      const Center(child: Text('No meals from this chef today.'))
                    else
                      ..._meals.map((meal) => MealCard(
                            meal: meal,
                            onTap: () => Navigator.of(context).push(
                              MaterialPageRoute(builder: (_) => MealDetailScreen(meal: meal)),
                            ),
                          )),
                  ],
                ),
    );
  }
}
