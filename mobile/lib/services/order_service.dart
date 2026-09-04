import 'api_client.dart';
import '../config/constants.dart';
import '../models/order.dart';
import '../models/review.dart';

class OrderService {
  final ApiClient _client = ApiClient(baseUrl: AppConstants.baseUrl);

  void setToken(String? token) => _client.setToken(token);

  Future<Order> createDailyMealOrder({
    required int dailyMealId,
    required int portions,
    required String deliveryType,
    String? deliveryAddress,
    String? specialInstructions,
  }) async {
    final body = {
      'daily_meal': dailyMealId,
      'portions': portions,
      'delivery_type': deliveryType,
      'delivery_address': ?deliveryAddress,
      'special_instructions': ?specialInstructions,
    };
    final response = await _client.post('${AppConstants.apiPrefix}/orders/daily/create/', body: body);
    return Order.fromJson(_client.decoded(response) as Map<String, dynamic>);
  }

  Future<List<Order>> getCustomerOrders() async {
    final response = await _client.get('${AppConstants.apiPrefix}/orders/daily/customer/');
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => Order.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<Order>> getCustomerOrderHistory() async {
    final response = await _client.get('${AppConstants.apiPrefix}/orders/daily/customer/history/');
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => Order.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<Order>> getChefOrders() async {
    final response = await _client.get('${AppConstants.apiPrefix}/orders/daily/chef/');
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => Order.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Order> getOrderDetail(int orderId) async {
    final response = await _client.get('${AppConstants.apiPrefix}/orders/daily/$orderId/');
    return Order.fromJson(_client.decoded(response) as Map<String, dynamic>);
  }

  Future<Order> updateOrderStatus(int orderId, String status) async {
    final response = await _client.put(
      '${AppConstants.apiPrefix}/orders/daily/$orderId/status/',
      body: {'order_status': status},
    );
    return Order.fromJson(_client.decoded(response) as Map<String, dynamic>);
  }

  Future<void> cancelOrder(int orderId) async {
    await _client.post('${AppConstants.apiPrefix}/orders/daily/$orderId/cancel/');
  }

  Future<Review> rateOrder(int orderId, int rating, {String? comment}) async {
    final body = {'rating': rating, 'feedback': ?comment};
    final response = await _client.post('${AppConstants.apiPrefix}/orders/daily/$orderId/rate/', body: body);
    return Review.fromJson(_client.decoded(response) as Map<String, dynamic>);
  }
}
