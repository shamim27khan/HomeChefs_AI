from django.contrib import admin
from .models import Order, OrderItem, Delivery

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'chef', 'total_amount', 'order_status', 'payment_status', 'created_at']
    list_filter = ['order_status', 'payment_status', 'created_at']
    search_fields = ['order_id', 'customer__username', 'chef__username']
    readonly_fields = ['order_id', 'created_at', 'updated_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'food_item', 'quantity', 'price_at_order']
    search_fields = ['order__order_id', 'food_item__name']

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['order', 'delivery_person', 'status', 'pickup_time', 'delivery_time']
    list_filter = ['status', 'pickup_time', 'delivery_time']
    search_fields = ['order__order_id', 'delivery_person__username']
