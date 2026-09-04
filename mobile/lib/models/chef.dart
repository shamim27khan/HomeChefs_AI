import 'user.dart';

class Chef {
  final int id;
  final String username;
  final String? firstName;
  final String? lastName;
  final String? email;
  final String? phoneNumber;
  final String? area;
  final String? city;
  final String? addressLine1;
  final String? addressLine2;
  final String? pincode;
  final String? fullAddress;
  final String? bio;
  final String? cuisineSpecialties;
  final int cookingExperience;
  final double? averageRating;
  final int totalRatings;
  final int completedOrders;
  final bool isVerified;
  final String? kitchenAddress;
  final String? kitchenType;
  final int? deliveryRadius;
  final User? user;

  Chef({
    required this.id,
    required this.username,
    this.firstName,
    this.lastName,
    this.email,
    this.phoneNumber,
    this.area,
    this.city,
    this.addressLine1,
    this.addressLine2,
    this.pincode,
    this.fullAddress,
    this.bio,
    this.cuisineSpecialties,
    this.cookingExperience = 0,
    this.averageRating,
    this.totalRatings = 0,
    this.completedOrders = 0,
    this.isVerified = false,
    this.kitchenAddress,
    this.kitchenType,
    this.deliveryRadius,
    this.user,
  });

  factory Chef.fromJson(Map<String, dynamic> json) {
    final userJson = json['user'];
    return Chef(
      id: json['id'] as int? ?? 0,
      username: json['username'] as String? ?? json['user']?['username'] as String? ?? '',
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      email: json['email'] as String?,
      phoneNumber: json['phone_number'] as String?,
      area: json['area'] as String?,
      city: json['city'] as String?,
      addressLine1: json['address_line1'] as String?,
      addressLine2: json['address_line2'] as String?,
      pincode: json['pincode'] as String?,
      fullAddress: json['full_address'] as String?,
      bio: json['bio'] as String?,
      cuisineSpecialties: json['cuisine_specialties'] as String?,
      cookingExperience: json['cooking_experience'] as int? ?? json['experience_years'] as int? ?? 0,
      averageRating: _parseDouble(json['average_rating']) ?? _parseDouble(json['rating']),
      totalRatings: json['total_ratings'] as int? ?? 0,
      completedOrders: json['completed_orders'] as int? ?? 0,
      isVerified: json['is_verified'] as bool? ?? false,
      kitchenAddress: json['kitchen_address'] as String?,
      kitchenType: json['kitchen_type'] as String?,
      deliveryRadius: json['delivery_radius'] as int?,
      user: userJson is Map<String, dynamic> ? User.fromJson(userJson) : null,
    );
  }

  static double? _parseDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  String get displayName {
    if (firstName != null && firstName!.isNotEmpty) {
      return lastName != null && lastName!.isNotEmpty
          ? '$firstName $lastName'
          : firstName!;
    }
    return username;
  }
}
