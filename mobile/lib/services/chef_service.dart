import 'api_client.dart';
import '../config/constants.dart';
import '../models/daily_meal.dart';
import '../models/chef.dart';

class ChefService {
  final ApiClient _client = ApiClient(baseUrl: AppConstants.baseUrl);

  void setToken(String? token) => _client.setToken(token);

  Future<List<DailyMeal>> getTodayMeals({String? area, String? mealType}) async {
    final queryParams = <String, String>{};
    if (area != null && area.isNotEmpty) queryParams['area'] = area;
    if (mealType != null && mealType.isNotEmpty) queryParams['meal_type'] = mealType;

    final uri = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiPrefix}/chefs/today-meals/')
        .replace(queryParameters: queryParams.isNotEmpty ? queryParams : null);

    final response = await _client.get('${AppConstants.apiPrefix}/chefs/today-meals/?${uri.query}');
    // Note: _client.get appends the path as-is; building a full query here.
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => DailyMeal.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<Chef>> getPublicChefs({String? area, String? city, String? cuisine, String? search}) async {
    final queryParams = <String, String>{};
    if (area != null && area.isNotEmpty) queryParams['area'] = area;
    if (city != null && city.isNotEmpty) queryParams['city'] = city;
    if (cuisine != null && cuisine.isNotEmpty) queryParams['cuisine'] = cuisine;
    if (search != null && search.isNotEmpty) queryParams['search'] = search;

    final query = queryParams.entries.map((e) => '${Uri.encodeComponent(e.key)}=${Uri.encodeComponent(e.value)}').join('&');
    final path = '${AppConstants.apiPrefix}/chefs/public/${query.isNotEmpty ? '?$query' : ''}';
    final response = await _client.get(path);
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => Chef.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Chef> getChefDetail(int chefId) async {
    final response = await _client.get('${AppConstants.apiPrefix}/chefs/public/$chefId/');
    return Chef.fromJson(_client.decoded(response) as Map<String, dynamic>);
  }

  Future<List<DailyMeal>> getNearbyDishes(double latitude, double longitude, {double radius = 3.0}) async {
    final response = await _client.get(
      '${AppConstants.apiPrefix}/chefs/nearby-dishes/?latitude=$latitude&longitude=$longitude&radius=$radius',
    );
    final decoded = _client.decoded(response) as Map<String, dynamic>;
    final dishes = decoded['dishes'] as List<dynamic>? ?? [];
    return dishes.map((e) => DailyMeal.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<DailyMeal>> getMyMeals() async {
    final response = await _client.get('${AppConstants.apiPrefix}/chefs/dashboard/my-meals/');
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => DailyMeal.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<DailyMeal> addDailyMeal(Map<String, dynamic> body) async {
    final response = await _client.post('${AppConstants.apiPrefix}/chefs/dashboard/meals/', body: body);
    return DailyMeal.fromJson(_client.decoded(response) as Map<String, dynamic>);
  }

  Future<void> toggleMealStatus(int mealId) async {
    await _client.post('${AppConstants.apiPrefix}/chefs/dashboard/meals/$mealId/toggle-status/');
  }
}
