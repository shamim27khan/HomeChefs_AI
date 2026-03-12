from django.contrib import admin
from .models import FoodItem, FoodSchedule, ChefReview, ChefProfile

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'chef', 'cuisine_type', 'meal_type', 'price', 'is_available', 'created_at']
    list_filter = ['cuisine_type', 'meal_type', 'is_available', 'is_vegetarian']
    search_fields = ['name', 'chef__username', 'cuisine_type']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(FoodSchedule)
class FoodScheduleAdmin(admin.ModelAdmin):
    list_display = ['food_item', 'date', 'available_from', 'available_to', 'max_orders', 'current_orders']
    list_filter = ['date']
    search_fields = ['food_item__name']

@admin.register(ChefReview)
class ChefReviewAdmin(admin.ModelAdmin):
    list_display = ['chef', 'customer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['chef__username', 'customer__username']
    readonly_fields = ['created_at']

@admin.register(ChefProfile)
class ChefProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'cuisine_specialties', 'cooking_experience', 'area', 'city', 'is_verified']
    list_filter = ['is_verified', 'cooking_experience', 'kitchen_type']
    search_fields = ['user__username', 'cuisine_specialties', 'area', 'city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'phone_number')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'area', 'city', 'pincode')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Professional Details', {
            'fields': ('cooking_experience', 'cuisine_specialties', 'kitchen_type')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
