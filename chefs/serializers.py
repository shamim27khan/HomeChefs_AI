from rest_framework import serializers
from .models import FoodItem, FoodSchedule, ChefReview, DailyMeal
from authentication.serializers import UserProfileSerializer

class FoodItemSerializer(serializers.ModelSerializer):
    chef = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = FoodItem
        fields = ['id', 'chef', 'name', 'description', 'cuisine_type', 'meal_type', 'price', 'available_quantity', 'preparation_time', 'image', 'ingredients', 'is_vegetarian', 'is_available', 'created_at', 'updated_at']
        read_only_fields = ['id', 'chef', 'created_at', 'updated_at']

class FoodScheduleSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)
    
    class Meta:
        model = FoodSchedule
        fields = ['id', 'food_item', 'date', 'available_from', 'available_to', 'max_orders', 'current_orders']
        read_only_fields = ['id', 'current_orders']

class ChefReviewSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ChefReview
        fields = ['id', 'chef', 'customer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'chef', 'customer', 'created_at']

class FoodItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['name', 'description', 'cuisine_type', 'meal_type', 'price', 'available_quantity', 'preparation_time', 'image', 'ingredients', 'is_vegetarian', 'is_available']
    
    def create(self, validated_data):
        validated_data['chef'] = self.context['request'].user
        return super().create(validated_data)

class FoodScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodSchedule
        fields = ['food_item', 'date', 'available_from', 'available_to', 'max_orders']

class DailyMealSerializer(serializers.ModelSerializer):
    chef_info = serializers.SerializerMethodField()
    available_portions = serializers.SerializerMethodField()
    is_orderable = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyMeal
        fields = [
            'id', 'chef', 'chef_info', 'chef_username', 'date', 'meal_type',
            'main_dish', 'side_dish', 'additional_items', 'extra_portions',
            'price_per_portion', 'order_cutoff_time', 'pickup_available',
            'delivery_available', 'delivery_radius', 'max_orders',
            'current_orders', 'is_active', 'available_portions', 'is_orderable'
        ]
        read_only_fields = ['id', 'chef', 'current_orders']
    
    def get_chef_info(self, obj):
        """Get chef information for API response"""
        if hasattr(obj.chef, 'chefprofile'):
            return {
                'id': obj.chef.id,
                'username': obj.chef.username,
                'area': obj.chef.chefprofile.area,
                'cuisine_specialties': obj.chef.chefprofile.cuisine_specialties,
                'cooking_experience': obj.chef.chefprofile.cooking_experience,
                'is_verified': obj.chef.chefprofile.is_verified,
                'average_rating': obj.chef.chefprofile.average_rating,
                'total_ratings': obj.chef.chefprofile.total_ratings,
                'completed_orders': obj.chef.chefprofile.completed_orders
            }
        return {
            'id': obj.chef.id,
            'username': obj.chef.username,
            'area': 'Not set',
            'cuisine_specialties': '',
            'cooking_experience': 5,
            'is_verified': False,
            'average_rating': 0,
            'total_ratings': 0,
            'completed_orders': 0
        }
    
    def get_chef_username(self, obj):
        return obj.chef.username
    
    def get_available_portions(self, obj):
        return obj.extra_portions - obj.current_orders
    
    def get_is_orderable(self, obj):
        from django.utils import timezone
        now = timezone.now().time()
        
        # Convert order_cutoff_time to time if it's a string
        if isinstance(obj.order_cutoff_time, str):
            try:
                from datetime import datetime
                cutoff_time = datetime.strptime(obj.order_cutoff_time, '%H:%M:%S').time()
            except ValueError:
                try:
                    cutoff_time = datetime.strptime(obj.order_cutoff_time, '%H:%M').time()
                except ValueError:
                    cutoff_time = obj.order_cutoff_time
        else:
            cutoff_time = obj.order_cutoff_time
        
        return (
            obj.is_active and 
            (obj.extra_portions - obj.current_orders) > 0 and 
            now <= cutoff_time
        )
