from django.contrib import admin
from .models import FavoriteChef, FavoriteFood, FoodReview, CustomerAddress, SearchHistory

@admin.register(FavoriteChef)
class FavoriteChefAdmin(admin.ModelAdmin):
    list_display = ['customer', 'chef', 'created_at']
    list_filter = ['created_at']
    search_fields = ['customer__username', 'chef__username']
    readonly_fields = ['created_at']

@admin.register(FavoriteFood)
class FavoriteFoodAdmin(admin.ModelAdmin):
    list_display = ['customer', 'food_item', 'created_at']
    list_filter = ['created_at']
    search_fields = ['customer__username', 'food_item__name']
    readonly_fields = ['created_at']

@admin.register(FoodReview)
class FoodReviewAdmin(admin.ModelAdmin):
    list_display = ['food_item', 'customer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['food_item__name', 'customer__username']
    readonly_fields = ['created_at']

@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'address_type', 'city', 'state', 'is_default']
    list_filter = ['address_type', 'is_default', 'city', 'state']
    search_fields = ['customer__username', 'city', 'state']
    readonly_fields = ['created_at']

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'query', 'searched_at']
    list_filter = ['searched_at']
    search_fields = ['customer__username', 'query']
    readonly_fields = ['searched_at']
