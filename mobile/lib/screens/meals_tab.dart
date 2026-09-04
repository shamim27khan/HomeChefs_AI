import 'package:flutter/material.dart';
import '../models/daily_meal.dart';
import '../services/chef_service.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';
import '../widgets/meal_card.dart';
import 'meal_detail_screen.dart';

class MealsTab extends StatefulWidget {
  const MealsTab({super.key});

  @override
  State<MealsTab> createState() => _MealsTabState();
}

class _MealsTabState extends State<MealsTab> with AutomaticKeepAliveClientMixin {
  final ChefService _service = ChefService();
  List<DailyMeal> _meals = [];
  bool _isLoading = true;
  String? _error;
  String _areaFilter = '';

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
      final meals = await _service.getTodayMeals(area: _areaFilter.isEmpty ? null : _areaFilter);
      if (mounted) setState(() => _meals = meals);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Today\'s Meals'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadMeals),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: TextField(
              decoration: const InputDecoration(
                labelText: 'Filter by area',
                prefixIcon: Icon(Icons.location_on_outlined),
                border: OutlineInputBorder(),
              ),
              onChanged: (value) => _areaFilter = value,
              onSubmitted: (_) => _loadMeals(),
            ),
          ),
          Expanded(
            child: _isLoading
                ? const LoadingIndicator()
                : _error != null
                    ? ErrorMessage(message: _error!, onRetry: _loadMeals)
                    : _meals.isEmpty
                        ? const Center(child: Text('No meals available today.'))
                        : ListView.builder(
                            itemCount: _meals.length,
                            itemBuilder: (context, index) => MealCard(
                              meal: _meals[index],
                              onTap: () => Navigator.of(context).push(
                                MaterialPageRoute(builder: (_) => MealDetailScreen(meal: _meals[index])),
                              ),
                            ),
                          ),
          ),
        ],
      ),
    );
  }
}
