class Payment {
  final int id;
  final String? paymentId;
  final dynamic order;
  final double amount;
  final String? paymentMethod;
  final String status;
  final String? transactionId;
  final DateTime? createdAt;

  Payment({
    required this.id,
    this.paymentId,
    this.order,
    this.amount = 0,
    this.paymentMethod,
    this.status = 'pending',
    this.transactionId,
    this.createdAt,
  });

  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['id'] as int? ?? 0,
      paymentId: json['payment_id'] as String?,
      order: json['order'],
      amount: _parseDouble(json['amount']),
      paymentMethod: json['payment_method'] as String?,
      status: json['status'] as String? ?? 'pending',
      transactionId: json['transaction_id'] as String?,
      createdAt: _parseDate(json['created_at']),
    );
  }

  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  static DateTime? _parseDate(dynamic value) {
    if (value == null) return null;
    if (value is String) return DateTime.tryParse(value);
    return null;
  }
}
