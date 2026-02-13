from rest_framework import serializers
from .models import FoodItem, FoodSchedule, ChefReview
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
