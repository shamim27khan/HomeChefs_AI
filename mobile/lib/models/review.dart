class Review {
  final int id;
  final int? dailyMeal;
  final int? order;
  final String? customerUsername;
  final int rating;
  final String? comment;
  final DateTime? createdAt;

  Review({
    required this.id,
    this.dailyMeal,
    this.order,
    this.customerUsername,
    required this.rating,
    this.comment,
    this.createdAt,
  });

  factory Review.fromJson(Map<String, dynamic> json) {
    return Review(
      id: json['id'] as int? ?? 0,
      dailyMeal: json['daily_meal'] as int?,
      order: json['daily_order'] as int? ?? json['order'] as int?,
      customerUsername: json['customer_username'] as String?,
      rating: json['rating'] as int? ?? 0,
      comment: json['comment'] as String? ?? json['feedback'] as String?,
      createdAt: _parseDate(json['created_at']),
    );
  }

  static DateTime? _parseDate(dynamic value) {
    if (value == null) return null;
    if (value is String) return DateTime.tryParse(value);
    return null;
  }
}
