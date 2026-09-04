class Order {
  final int id;
  final String? orderId;
  final dynamic dailyMeal;
  final String? mealDetails;
  final String? mealType;
  final String? chefUsername;
  final String? chefArea;
  final String? customerUsername;
  final int portions;
  final double pricePerPortion;
  final double totalAmount;
  final String? deliveryType;
  final String? deliveryAddress;
  final double? deliveryFee;
  final String orderStatus;
  final String paymentStatus;
  final DateTime? orderTime;
  final DateTime? createdAt;
  final DateTime? estimatedReadyTime;
  final DateTime? pickupTime;
  final DateTime? deliveryTime;
  final String? specialInstructions;
  final double? chefEarnings;

  Order({
    required this.id,
    this.orderId,
    this.dailyMeal,
    this.mealDetails,
    this.mealType,
    this.chefUsername,
    this.chefArea,
    this.customerUsername,
    this.portions = 1,
    this.pricePerPortion = 0,
    this.totalAmount = 0,
    this.deliveryType,
    this.deliveryAddress,
    this.deliveryFee,
    this.orderStatus = 'pending',
    this.paymentStatus = 'pending',
    this.orderTime,
    this.createdAt,
    this.estimatedReadyTime,
    this.pickupTime,
    this.deliveryTime,
    this.specialInstructions,
    this.chefEarnings,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] as int? ?? 0,
      orderId: json['order_id'] as String?,
      dailyMeal: json['daily_meal'],
      mealDetails: json['meal_details'] as String?,
      mealType: json['meal_type'] as String?,
      chefUsername: json['chef_username'] as String?,
      chefArea: json['chef_area'] as String?,
      customerUsername: json['customer_username'] as String?,
      portions: json['portions'] as int? ?? 1,
      pricePerPortion: _parseDouble(json['price_per_portion']),
      totalAmount: _parseDouble(json['total_amount']),
      deliveryType: json['delivery_type'] as String?,
      deliveryAddress: json['delivery_address'] as String?,
      deliveryFee: _parseDoubleOrNull(json['delivery_fee']),
      orderStatus: json['order_status'] as String? ?? 'pending',
      paymentStatus: json['payment_status'] as String? ?? 'pending',
      orderTime: _parseDate(json['order_time']),
      createdAt: _parseDate(json['created_at']),
      estimatedReadyTime: _parseDate(json['estimated_ready_time']),
      pickupTime: _parseDate(json['pickup_time']),
      deliveryTime: _parseDate(json['delivery_time']),
      specialInstructions: json['special_instructions'] as String?,
      chefEarnings: _parseDoubleOrNull(json['chef_earnings']),
    );
  }

  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  static double? _parseDoubleOrNull(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  static DateTime? _parseDate(dynamic value) {
    if (value == null) return null;
    if (value is String) return DateTime.tryParse(value);
    return null;
  }
}
