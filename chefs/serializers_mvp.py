from rest_framework import serializers
from django.db.models import Avg, Count, F
from authentication.models import User
from .models import DailyMeal, ChefProfile, DailyEarning, CustomerReview, FoodItem, ChefReview

class ChefProfileSerializer(serializers.ModelSerializer):
    """Simple chef profile serializer for MVP"""
    username = serializers.CharField(source='user.username', read_only=True)
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = ChefProfile
        fields = [
            'user', 'username', 'phone_number', 'address_line1', 'address_line2',
            'area', 'city', 'pincode', 'cooking_experience', 'cuisine_specialties',
            'is_verified', 'kitchen_type', 'full_address', 'created_at'
        ]
        read_only_fields = ['user', 'is_verified', 'verification_date', 'created_at']

class DailyMealSerializer(serializers.ModelSerializer):
    """Daily meal serializer for MVP"""
    chef_username = serializers.CharField(source='chef.username', read_only=True)
    chef_area = serializers.CharField(source='chef.chefprofile.area', read_only=True)
    available_portions = serializers.ReadOnlyField()
    is_orderable = serializers.ReadOnlyField()
    
    class Meta:
        model = DailyMeal
        fields = [
            'id', 'chef', 'chef_username', 'chef_area', 'date', 'meal_type',
            'main_dish', 'side_dish', 'additional_items', 'extra_portions',
            'price_per_portion', 'order_cutoff_time', 'max_orders', 'current_orders',
            'available_portions', 'pickup_available', 'delivery_available',
            'delivery_radius', 'is_active', 'is_orderable', 'created_at'
        ]
        read_only_fields = ['chef', 'current_orders', 'created_at']

class DailyMealCreateSerializer(serializers.ModelSerializer):
    """Serializer for chefs to create daily meals"""
    
    class Meta:
        model = DailyMeal
        fields = [
            'date', 'meal_type', 'main_dish', 'side_dish', 'additional_items',
            'extra_portions', 'price_per_portion', 'order_cutoff_time',
            'pickup_available', 'delivery_available', 'delivery_radius'
        ]
    
    def validate_extra_portions(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError("Extra portions must be between 1 and 20.")
        return value
    
    def validate_price_per_portion(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
    
    def validate(self, data):
        """
        Check that at least one delivery option is available
        """
        if not data.get('pickup_available', False) and not data.get('delivery_available', False):
            raise serializers.ValidationError("At least one of pickup or delivery must be available.")
        
        if data.get('delivery_available', False) and not data.get('delivery_radius'):
            raise serializers.ValidationError("Delivery radius is required when delivery is available.")
        
        return data

class DailyEarningSerializer(serializers.ModelSerializer):
    """Daily earnings summary for chefs"""
    
    class Meta:
        model = DailyEarning
        fields = [
            'date', 'total_orders', 'total_earnings', 'platform_commission',
            'net_earnings'
        ]
        read_only_fields = ['date', 'total_orders', 'total_earnings', 
                          'platform_commission', 'net_earnings']

class CustomerReviewSerializer(serializers.ModelSerializer):
    """Customer review serializer for daily meals"""
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    
    class Meta:
        model = CustomerReview
        fields = [
            'id', 'daily_meal', 'customer', 'customer_username', 'rating',
            'comment', 'created_at'
        ]
        read_only_fields = ['customer', 'created_at']

class PublicChefSerializer(serializers.ModelSerializer):
    """Public chef information for customers"""
    username = serializers.CharField(read_only=True)
    area = serializers.CharField(source='chefprofile.area', read_only=True)
    cuisine_specialties = serializers.CharField(source='chefprofile.cuisine_specialties', read_only=True)
    cooking_experience = serializers.IntegerField(source='chefprofile.cooking_experience', read_only=True)
    is_verified = serializers.BooleanField(source='chefprofile.is_verified', read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    completed_orders = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'area', 'cuisine_specialties', 'cooking_experience',
            'is_verified', 'average_rating', 'total_ratings', 'completed_orders'
        ]
    
    def get_average_rating(self, obj):
        # Calculate average rating from customer ratings
        from orders.models import CustomerRating
        ratings = CustomerRating.objects.filter(
            daily_order__daily_meal__chef=obj
        ).aggregate(Avg('rating'))
        return round(ratings['rating__avg'], 1) if ratings['rating__avg'] else 0
    
    def get_total_ratings(self, obj):
        # Count total ratings for this chef
        from orders.models import CustomerRating
        return CustomerRating.objects.filter(
            daily_order__daily_meal__chef=obj
        ).count()
    
    def get_completed_orders(self, obj):
        # Count completed orders for this chef (ready or delivered status)
        from orders.models import DailyMealOrder
        return DailyMealOrder.objects.filter(
            daily_meal__chef=obj,
            order_status__in=['ready', 'delivered']
        ).count()

class TodayMealsSerializer(serializers.ModelSerializer):
    """Serializer for today's available meals"""
    chef_info = PublicChefSerializer(source='chef', read_only=True)
    chef_username = serializers.CharField(source='chef.username', read_only=True)
    available_portions = serializers.ReadOnlyField()
    is_orderable = serializers.ReadOnlyField()
    
    class Meta:
        model = DailyMeal
        fields = [
            'id', 'chef_info', 'chef_username', 'meal_type', 'main_dish', 'side_dish',
            'additional_items', 'extra_portions', 'available_portions',
            'price_per_portion', 'order_cutoff_time', 'pickup_available',
            'delivery_available', 'delivery_radius', 'is_orderable'
        ]

# Legacy serializers for backward compatibility
class FoodItemSerializer(serializers.ModelSerializer):
    """Legacy serializer - use DailyMealSerializer instead"""
    
    class Meta:
        model = FoodItem
        fields = '__all__'

class ChefReviewSerializer(serializers.ModelSerializer):
    """Legacy serializer - use CustomerReviewSerializer instead"""
    
    class Meta:
        model = ChefReview
        fields = '__all__'
