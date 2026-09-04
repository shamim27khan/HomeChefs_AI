import 'api_client.dart';
import '../config/constants.dart';
import '../models/address.dart';

class CustomerService {
  final ApiClient _client = ApiClient(baseUrl: AppConstants.baseUrl);

  void setToken(String? token) => _client.setToken(token);

  Future<List<ChefStub>> getFavoriteChefs() async {
    final response = await _client.get('${AppConstants.apiPrefix}/customers/favorite-chefs/');
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => ChefStub.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> addFavoriteChef(int chefId) async {
    await _client.post('${AppConstants.apiPrefix}/customers/favorite-chefs/', body: {'chef': chefId});
  }

  Future<void> removeFavoriteChef(int chefId) async {
    await _client.delete('${AppConstants.apiPrefix}/customers/favorite-chefs/$chefId/');
  }

  Future<List<Address>> getAddresses() async {
    final response = await _client.get('${AppConstants.apiPrefix}/customers/addresses/');
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => Address.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Address> addAddress(Map<String, dynamic> body) async {
    final response = await _client.post('${AppConstants.apiPrefix}/customers/addresses/', body: body);
    return Address.fromJson(_client.decoded(response) as Map<String, dynamic>);
  }

  Future<List<DailyMealStub>> searchFood({String? query, String? area, String? mealType}) async {
    final params = <String, String>{};
    if (query != null && query.isNotEmpty) params['q'] = query;
    if (area != null && area.isNotEmpty) params['area'] = area;
    if (mealType != null && mealType.isNotEmpty) params['meal_type'] = mealType;

    final queryString = params.entries.map((e) => '${Uri.encodeComponent(e.key)}=${Uri.encodeComponent(e.value)}').join('&');
    final path = '${AppConstants.apiPrefix}/customers/search/food/${queryString.isNotEmpty ? '?$queryString' : ''}';
    final response = await _client.get(path);
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => DailyMealStub.fromJson(e as Map<String, dynamic>)).toList();
  }
}

class ChefStub {
  final int id;
  final String username;
  final String? firstName;
  final String? lastName;

  ChefStub({required this.id, required this.username, this.firstName, this.lastName});

  factory ChefStub.fromJson(Map<String, dynamic> json) {
    return ChefStub(
      id: json['id'] as int? ?? 0,
      username: json['username'] as String? ?? '',
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
    );
  }
}

class DailyMealStub {
  final int id;
  final String mainDish;
  final double price;

  DailyMealStub({required this.id, required this.mainDish, required this.price});

  factory DailyMealStub.fromJson(Map<String, dynamic> json) {
    return DailyMealStub(
      id: json['id'] as int? ?? 0,
      mainDish: json['main_dish'] as String? ?? json['name'] as String? ?? '',
      price: (json['price_per_portion'] ?? json['price'] ?? 0).toDouble(),
    );
  }
}
