from rest_framework import serializers
from .models import Order, OrderItem, Delivery
from chefs.models import FoodItem
from authentication.serializers import UserProfileSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    food_item = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'quantity', 'price_at_order']
        read_only_fields = ['id', 'price_at_order']
    
    def get_food_item(self, obj):
        from chefs.serializers import FoodItemSerializer
        return FoodItemSerializer(obj.food_item).data

class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(write_only=True)
    
    class Meta:
        model = Order
        fields = ['chef', 'delivery_address', 'delivery_fee', 'special_instructions', 'items']
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        customer = self.context['request'].user
        
        # Generate unique order ID
        import uuid
        order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
        
        order = Order.objects.create(
            order_id=order_id,
            customer=customer,
            **validated_data
        )
        
        # Calculate total amount
        total_amount = 0
        for item_data in items_data:
            food_item = item_data['food_item']
            quantity = item_data['quantity']
            
            # Get current price
            food_item_obj = FoodItem.objects.get(id=food_item.id)
            price_at_order = food_item_obj.price
            
            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=quantity,
                price_at_order=price_at_order
            )
            
            total_amount += price_at_order * quantity
        
        # Add delivery fee
        total_amount += validated_data.get('delivery_fee', 0)
        order.total_amount = total_amount
        order.save()
        
        return order

class OrderSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializer(read_only=True)
    chef = UserProfileSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer', 'chef', 'total_amount', 'delivery_address', 'delivery_fee', 'special_instructions', 'order_status', 'payment_status', 'created_at', 'updated_at', 'estimated_delivery_time', 'items']
        read_only_fields = ['id', 'order_id', 'customer', 'created_at', 'updated_at']

class DeliverySerializer(serializers.ModelSerializer):
    delivery_person = UserProfileSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Delivery
        fields = ['id', 'order', 'delivery_person', 'status', 'pickup_time', 'delivery_time', 'tracking_link', 'notes']
        read_only_fields = ['id', 'order']
