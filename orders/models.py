from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from authentication.models import User
from chefs.models import DailyMeal

class DailyMealOrder(models.Model):
    """Order for daily meal - MVP Core Feature"""
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    DELIVERY_TYPE = (
        ('pickup', 'Pickup'),
        ('delivery', 'Local Delivery'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )
    
    order_id = models.CharField(max_length=20, unique=True)
    daily_meal = models.ForeignKey(DailyMeal, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_orders')
    
    # Order details
    portions = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    price_per_portion = models.DecimalField(max_digits=6, decimal_places=2)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Delivery options
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPE, default='pickup')
    delivery_address = models.TextField(blank=True, help_text="Required for delivery orders")
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    # Order management
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Timestamps
    order_time = models.DateTimeField(auto_now_add=True)
    estimated_ready_time = models.DateTimeField(blank=True, null=True)
    pickup_time = models.DateTimeField(blank=True, null=True)
    delivery_time = models.DateTimeField(blank=True, null=True)
    
    # Customer notes
    special_instructions = models.TextField(
        blank=True,
        max_length=200,
        help_text="Special instructions (max 200 chars)"
    )
    
    # Platform commission
    platform_commission = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    chef_earnings = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_id} - {self.daily_meal.get_meal_type_display()}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount
        self.total_amount = self.portions * self.price_per_portion
        
        # Auto-calculate chef earnings (85% after platform commission)
        from decimal import Decimal
        self.platform_commission = self.total_amount * Decimal('0.15')  # 15% platform fee
        self.chef_earnings = self.total_amount - self.platform_commission
        
        # Auto-generate order ID if not provided
        if not self.order_id:
            from django.utils import timezone
            import random
            timestamp = timezone.now().strftime('%Y%m%d')
            random_num = random.randint(1000, 9999)
            self.order_id = f"ORD{timestamp}{random_num}"
        
        super().save(*args, **kwargs)

class CustomerRating(models.Model):
    """Simple rating system for daily meals"""
    daily_order = models.OneToOneField(
        DailyMealOrder, 
        on_delete=models.CASCADE, 
        related_name='rating'
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rating = models.PositiveIntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    feedback = models.TextField(
        blank=True,
        max_length=200,
        help_text="Optional feedback (max 200 chars)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Rating for {self.daily_order.order_id} - {self.rating} stars"

# Legacy models for backward compatibility
class Order(models.Model):
    """Legacy model - use DailyMealOrder instead"""
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )
    
    order_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_orders')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_address = models.TextField()
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    special_instructions = models.TextField(blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Order {self.order_id} by {self.customer.username}"

class OrderItem(models.Model):
    """Legacy model - use DailyMealOrder instead"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey('chefs.FoodItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.food_item.name} in Order {self.order.order_id}"

class Delivery(models.Model):
    """Legacy model - simplified delivery for MVP"""
    DELIVERY_STATUS = (
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='assigned')
    pickup_time = models.DateTimeField(blank=True, null=True)
    delivery_time = models.DateTimeField(blank=True, null=True)
    tracking_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Delivery for Order {self.order.order_id}"


# Signal handler for automatic delivery request creation
@receiver(post_save, sender=DailyMealOrder)
def create_delivery_requests_for_ready_orders(sender, instance, created, **kwargs):
    """
    Automatically create delivery requests when order reaches 'ready' or 'preparing' status
    """
    # Only create requests for existing orders, not new ones
    if created:
        return
    
    # Create delivery requests for orders that need delivery
    if instance.order_status in ['ready', 'preparing']:
        try:
            # Import here to avoid circular imports
            from delivery.models import DeliveryPartner, DeliveryRequest
            
            # Get available delivery partners
            available_partners = DeliveryPartner.objects.filter(
                is_available=True,
                verification_status='verified'
            )
            
            # Create delivery requests for each available partner
            delivery_requests_created = 0
            for partner in available_partners:
                # Check if request already exists
                existing_request = DeliveryRequest.objects.filter(
                    order=instance,
                    delivery_partner=partner,
                    status='pending'
                ).first()
                
                if not existing_request:
                    from django.utils import timezone
                    from datetime import timedelta
                    
                    # Calculate estimated times and fees
                    estimated_pickup_time = instance.estimated_ready_time or (timezone.now() + timedelta(minutes=15))
                    estimated_delivery_time = estimated_pickup_time + timedelta(minutes=30)
                    delivery_fee = instance.delivery_fee or Decimal('50.00')  # Default delivery fee
                    
                    DeliveryRequest.objects.create(
                        order=instance,
                        delivery_partner=partner,
                        status='pending',
                        estimated_pickup_time=estimated_pickup_time,
                        estimated_delivery_time=estimated_delivery_time,
                        delivery_fee=delivery_fee
                    )
                    delivery_requests_created += 1
            
            # Update order status to show it's awaiting delivery assignment
            if delivery_requests_created > 0 and instance.order_status == 'ready':
                instance.order_status = 'out_for_delivery'
                instance.save()
            
            print(f"Created {delivery_requests_created} delivery requests for order #{instance.order_id}")
            
        except Exception as e:
            print(f"Error creating delivery requests for order #{instance.order_id}: {e}")
