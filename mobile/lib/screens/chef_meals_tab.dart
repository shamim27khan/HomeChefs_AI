import 'package:flutter/material.dart';
import '../models/daily_meal.dart';
import '../services/chef_service.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';
import '../widgets/meal_card.dart';
import 'add_meal_screen.dart';

class ChefMealsTab extends StatefulWidget {
  const ChefMealsTab({super.key});

  @override
  State<ChefMealsTab> createState() => _ChefMealsTabState();
}

class _ChefMealsTabState extends State<ChefMealsTab> with AutomaticKeepAliveClientMixin {
  final ChefService _service = ChefService();
  List<DailyMeal> _meals = [];
  bool _isLoading = true;
  String? _error;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _loadMeals();
  }

  Future<void> _loadMeals() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final meals = await _service.getMyMeals();
      if (mounted) setState(() => _meals = meals);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _toggleMeal(int mealId) async {
    try {
      await _service.toggleMealStatus(mealId);
      await _loadMeals();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Meals'),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _loadMeals)],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AddMealScreen())).then((_) => _loadMeals()),
        icon: const Icon(Icons.add),
        label: const Text('Meal'),
      ),
      body: _isLoading
          ? const LoadingIndicator()
          : _error != null
              ? ErrorMessage(message: _error!, onRetry: _loadMeals)
              : _meals.isEmpty
                  ? const Center(child: Text('No meals added yet. Add your first meal!'))
                  : ListView.builder(
                      itemCount: _meals.length,
                      itemBuilder: (context, index) {
                        final meal = _meals[index];
                        return MealCard(
                          meal: meal,
                          onTap: () => _showMealActions(meal),
                        );
                      },
                    ),
    );
  }

  void _showMealActions(DailyMeal meal) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              title: const Text('Toggle active status'),
              leading: const Icon(Icons.toggle_on),
              onTap: () {
                Navigator.of(context).pop();
                _toggleMeal(meal.id);
              },
            ),
            ListTile(
              title: const Text('View details'),
              leading: const Icon(Icons.info_outline),
              onTap: () => Navigator.of(context).pop(),
            ),
          ],
        ),
      ),
    );
  }
}
