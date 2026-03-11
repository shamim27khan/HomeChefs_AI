from rest_framework import serializers
from authentication.models import User
from .models import DailyMealOrder, CustomerRating
from chefs.models import DailyMeal
from orders.models import Order, OrderItem

class DailyMealOrderSerializer(serializers.ModelSerializer):
    """Daily meal order serializer for MVP"""
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    chef_username = serializers.CharField(source='daily_meal.chef.username', read_only=True)
    meal_details = serializers.CharField(source='daily_meal.main_dish', read_only=True)
    meal_type = serializers.CharField(source='daily_meal.get_meal_type_display', read_only=True)
    
    class Meta:
        model = DailyMealOrder
        fields = [
            'id', 'order_id', 'daily_meal', 'customer', 'customer_username',
            'chef_username', 'meal_details', 'meal_type', 'portions',
            'price_per_portion', 'total_amount', 'delivery_type',
            'delivery_address', 'delivery_fee', 'order_status',
            'payment_status', 'order_time', 'estimated_ready_time',
            'pickup_time', 'delivery_time', 'special_instructions',
            'platform_commission', 'chef_earnings', 'created_at'
        ]
        read_only_fields = [
            'order_id', 'customer', 'total_amount', 'platform_commission',
            'chef_earnings', 'order_time', 'created_at'
        ]

class DailyMealOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating daily meal orders"""
    
    class Meta:
        model = DailyMealOrder
        fields = [
            'daily_meal', 'portions', 'delivery_type', 'delivery_address',
            'special_instructions'
        ]
    
    def validate_portions(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Portions must be between 1 and 5.")
        return value
    
    def validate(self, data):
        daily_meal = data['daily_meal']
        portions = data['portions']
        
        # Check if meal is still orderable
        if not daily_meal.is_orderable:
            raise serializers.ValidationError("This meal is no longer available for ordering.")
        
        # Check if enough portions are available
        if portions > daily_meal.available_portions:
            raise serializers.ValidationError(
                f"Only {daily_meal.available_portions} portions available."
            )
        
        # Validate delivery address for delivery orders
        if data.get('delivery_type') == 'delivery' and not data.get('delivery_address'):
            raise serializers.ValidationError("Delivery address is required for delivery orders.")
        
        return data
    
    def create(self, validated_data):
        # Set price from daily meal
        daily_meal = validated_data['daily_meal']
        validated_data['price_per_portion'] = daily_meal.price_per_portion
        validated_data['customer'] = self.context['request'].user
        
        # Update daily meal order count
        daily_meal.current_orders += validated_data['portions']
        daily_meal.save()
        
        return super().create(validated_data)

class CustomerRatingSerializer(serializers.ModelSerializer):
    """Customer rating serializer for completed orders"""
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    
    class Meta:
        model = CustomerRating
        fields = [
            'id', 'daily_order', 'customer', 'customer_username', 'rating',
            'feedback', 'created_at'
        ]
        read_only_fields = ['customer', 'daily_order', 'created_at']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if not isinstance(value, int) or value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be an integer between 1 and 5.")
        return value
    
    def validate_feedback(self, value):
        """Validate feedback length and sanitize"""
        if value:
            # Strip whitespace and check length
            value = value.strip()
            if len(value) > 200:
                raise serializers.ValidationError("Feedback cannot exceed 200 characters.")
            # Basic sanitization - remove any potential HTML tags
            import re
            value = re.sub(r'<[^>]+>', '', value)
        return value

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status (chefs only)"""
    
    class Meta:
        model = DailyMealOrder
        fields = ['order_status']
    
    def validate_order_status(self, value):
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        return value

class CustomerOrderListSerializer(serializers.ModelSerializer):
    """Serializer for customers to view their orders"""
    meal_details = serializers.CharField(source='daily_meal.main_dish', read_only=True)
    meal_type = serializers.CharField(source='daily_meal.get_meal_type_display', read_only=True)
    chef_username = serializers.CharField(source='daily_meal.chef.username', read_only=True)
    chef_area = serializers.CharField(source='daily_meal.chef.chefprofile.area', read_only=True)
    
    class Meta:
        model = DailyMealOrder
        fields = [
            'id', 'order_id', 'meal_details', 'meal_type', 'chef_username',
            'chef_area', 'portions', 'total_amount', 'delivery_type',
            'order_status', 'payment_status', 'order_time', 'created_at',
            'estimated_ready_time', 'pickup_time', 'special_instructions'
        ]

class ChefOrderListSerializer(serializers.ModelSerializer):
    """Serializer for chefs to view their orders"""
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    meal_name = serializers.CharField(source='daily_meal.main_dish', read_only=True)
    meal_type = serializers.CharField(source='daily_meal.get_meal_type_display', read_only=True)
    delivery_address = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyMealOrder
        fields = [
            'id', 'order_id', 'customer_username', 'meal_name', 'meal_type', 'portions',
            'total_amount', 'delivery_type', 'delivery_address',
            'order_status', 'payment_status', 'order_time',
            'special_instructions', 'chef_earnings'
        ]
    
    def get_delivery_address(self, obj):
        if obj.delivery_type == 'pickup':
            return "Customer will pickup"
        return obj.delivery_address

# Legacy serializers for backward compatibility
class OrderSerializer(serializers.ModelSerializer):
    """Legacy serializer - use DailyMealOrderSerializer instead"""
    
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    """Legacy serializer - use DailyMealOrderSerializer instead"""
    
    class Meta:
        model = OrderItem
        fields = '__all__'
