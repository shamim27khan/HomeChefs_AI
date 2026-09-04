class Address {
  final int id;
  final String addressType;
  final String addressLine;
  final String? landmark;
  final String? addressIdentifier;
  final String city;
  final String? state;
  final String postalCode;
  final bool isDefault;

  Address({
    required this.id,
    required this.addressType,
    required this.addressLine,
    this.landmark,
    this.addressIdentifier,
    required this.city,
    this.state,
    required this.postalCode,
    this.isDefault = false,
  });

  factory Address.fromJson(Map<String, dynamic> json) {
    return Address(
      id: json['id'] as int? ?? 0,
      addressType: json['address_type'] as String? ?? 'home',
      addressLine: json['address_line'] as String? ?? '',
      landmark: json['landmark'] as String?,
      addressIdentifier: json['address_identifier'] as String?,
      city: json['city'] as String? ?? '',
      state: json['state'] as String?,
      postalCode: json['postal_code'] as String? ?? '',
      isDefault: json['is_default'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'address_type': addressType,
      'address_line': addressLine,
      'landmark': landmark,
      'address_identifier': addressIdentifier,
      'city': city,
      'state': state,
      'postal_code': postalCode,
      'is_default': isDefault,
    };
  }

  String get shortDisplay => '$addressType - $addressLine, $city';
}
