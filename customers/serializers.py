from rest_framework import serializers
from .models import FavoriteChef, FavoriteFood, FoodReview, CustomerAddress, SearchHistory
from chefs.models import FoodItem
from authentication.serializers import UserProfileSerializer

class FavoriteChefSerializer(serializers.ModelSerializer):
    chef = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = FavoriteChef
        fields = ['id', 'chef', 'created_at']
        read_only_fields = ['id', 'customer', 'created_at']

class FavoriteFoodSerializer(serializers.ModelSerializer):
    food_item = serializers.SerializerMethodField()
    
    class Meta:
        model = FavoriteFood
        fields = ['id', 'food_item', 'created_at']
        read_only_fields = ['id', 'customer', 'created_at']
    
    def get_food_item(self, obj):
        from chefs.serializers import FoodItemSerializer
        return FoodItemSerializer(obj.food_item).data

class FoodReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodReview
        fields = ['food_item', 'rating', 'comment']

class FoodReviewSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializer(read_only=True)
    food_item = serializers.SerializerMethodField()
    
    class Meta:
        model = FoodReview
        fields = ['id', 'food_item', 'customer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'customer', 'created_at']
    
    def get_food_item(self, obj):
        from chefs.serializers import FoodItemSerializer
        return FoodItemSerializer(obj.food_item).data

class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = ['id', 'address_type', 'address_line', 'landmark', 'address_identifier', 'city', 'state', 'postal_code', 'is_default', 'created_at']
        read_only_fields = ['id', 'customer', 'created_at']

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'searched_at']
        read_only_fields = ['id', 'customer', 'searched_at']
