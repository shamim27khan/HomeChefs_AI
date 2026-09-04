import 'api_client.dart';
import '../config/constants.dart';
import '../models/payment.dart';

class PaymentService {
  final ApiClient _client = ApiClient(baseUrl: AppConstants.baseUrl);

  void setToken(String? token) => _client.setToken(token);

  Future<Map<String, dynamic>> getWallet() async {
    final response = await _client.get('${AppConstants.apiPrefix}/payments/wallet/');
    return _client.decoded(response) as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> getWalletTransactions() async {
    final response = await _client.get('${AppConstants.apiPrefix}/payments/wallet/transactions/');
    final data = _client.decoded(response) as List<dynamic>;
    return data.cast<Map<String, dynamic>>();
  }

  Future<Payment> createPayment({required int orderId, required String paymentMethod}) async {
    final body = {'order': orderId, 'payment_method': paymentMethod};
    final response = await _client.post('${AppConstants.apiPrefix}/payments/', body: body);
    return Payment.fromJson(_client.decoded(response) as Map<String, dynamic>);
  }

  Future<List<Payment>> getPayments() async {
    final response = await _client.get('${AppConstants.apiPrefix}/payments/');
    final data = _client.decoded(response) as List<dynamic>;
    return data.map((e) => Payment.fromJson(e as Map<String, dynamic>)).toList();
  }
}
