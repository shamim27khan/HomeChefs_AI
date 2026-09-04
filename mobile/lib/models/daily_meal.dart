import 'chef.dart';

class DailyMeal {
  final int id;
  final DateTime? date;
  final String? mealType;
  final String mainDish;
  final String? sideDish;
  final String? additionalItems;
  final int extraPortions;
  final int? availablePortions;
  final double pricePerPortion;
  final String? orderCutoffTime;
  final int? maxOrders;
  final int? currentOrders;
  final bool pickupAvailable;
  final bool deliveryAvailable;
  final int? deliveryRadius;
  final bool isActive;
  final bool? isOrderable;
  final Chef? chefInfo;
  final String? chefUsername;
  final String? chefArea;

  DailyMeal({
    required this.id,
    this.date,
    this.mealType,
    required this.mainDish,
    this.sideDish,
    this.additionalItems,
    this.extraPortions = 1,
    this.availablePortions,
    required this.pricePerPortion,
    this.orderCutoffTime,
    this.maxOrders,
    this.currentOrders,
    this.pickupAvailable = false,
    this.deliveryAvailable = false,
    this.deliveryRadius,
    this.isActive = true,
    this.isOrderable,
    this.chefInfo,
    this.chefUsername,
    this.chefArea,
  });

  factory DailyMeal.fromJson(Map<String, dynamic> json) {
    final chefJson = json['chef_info'] ?? json['chef'];
    return DailyMeal(
      id: json['id'] as int? ?? 0,
      date: _parseDate(json['date']),
      mealType: json['meal_type'] as String?,
      mainDish: json['main_dish'] as String? ?? 'Meal',
      sideDish: json['side_dish'] as String?,
      additionalItems: json['additional_items'] as String?,
      extraPortions: json['extra_portions'] as int? ?? 1,
      availablePortions: json['available_portions'] as int?,
      pricePerPortion: _parseDouble(json['price_per_portion']),
      orderCutoffTime: json['order_cutoff_time'] as String?,
      maxOrders: json['max_orders'] as int?,
      currentOrders: json['current_orders'] as int?,
      pickupAvailable: json['pickup_available'] as bool? ?? false,
      deliveryAvailable: json['delivery_available'] as bool? ?? false,
      deliveryRadius: json['delivery_radius'] as int?,
      isActive: json['is_active'] as bool? ?? true,
      isOrderable: json['is_orderable'] as bool?,
      chefInfo: chefJson is Map<String, dynamic> ? Chef.fromJson(chefJson) : null,
      chefUsername: json['chef_username'] as String?,
      chefArea: json['chef_area'] as String?,
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
