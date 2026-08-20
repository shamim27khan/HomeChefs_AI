from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from authentication.models import User
from orders.models import DailyMealOrder

class DeliveryPartner(models.Model):
    """Delivery partner model for managing delivery personnel"""
    PARTNER_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
    )
    
    VERIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_partner')
    phone_number = models.CharField(max_length=15, unique=True)
    vehicle_type = models.CharField(
        max_length=20,
        choices=[
            ('bike', 'Bike'),
            ('scooter', 'Scooter'),
            ('car', 'Car'),
            ('cycle', 'Bicycle'),
        ],
        default='bike'
    )
    vehicle_number = models.CharField(max_length=20, unique=True)
    license_number = models.CharField(max_length=50, unique=True)
    
    # Location tracking
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Status and verification
    status = models.CharField(max_length=20, choices=PARTNER_STATUS, default='inactive')
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    is_available = models.BooleanField(default=True)
    
    # Performance metrics
    total_deliveries = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Service area
    service_areas = models.TextField(help_text="Comma-separated list of areas/zip codes")
    max_delivery_distance = models.PositiveIntegerField(default=10, help_text="Maximum delivery distance in km")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery Partner: {self.user.username}"
    
    def update_location(self, latitude, longitude):
        """Update partner's current location"""
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.last_location_update = timezone.now()
        self.save()
    
    def get_active_deliveries(self):
        """Get currently active deliveries"""
        return self.deliveries.filter(status__in=['assigned', 'picked_up', 'in_transit'])
    
    def is_within_service_area(self, delivery_address):
        """Check if delivery address is within service area (simplified)"""
        # This is a simplified check - in production, you'd use geocoding
        service_area_list = [area.strip() for area in self.service_areas.split(',')]
        return any(area.lower() in delivery_address.lower() for area in service_area_list)

class DeliveryRequest(models.Model):
    """Delivery request sent to available partners"""
    REQUEST_STATUS = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    )
    
    order = models.ForeignKey(DailyMealOrder, on_delete=models.CASCADE, related_name='delivery_requests')
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE, related_name='delivery_requests')
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='pending')
    
    # Request details
    estimated_pickup_time = models.DateTimeField()
    estimated_delivery_time = models.DateTimeField()
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    distance_km = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-sent_at']
        unique_together = ['order', 'delivery_partner']
    
    def __str__(self):
        return f"Delivery Request for {self.order.order_id} to {self.delivery_partner.user.username}"
    
    def is_expired(self):
        """Check if request has expired"""
        return timezone.now() > self.expires_at
    
    def accept_request(self):
        """Accept the delivery request"""
        if self.status == 'pending' and not self.is_expired():
            self.status = 'accepted'
            self.responded_at = timezone.now()
            self.save()
            
            # Create delivery assignment
            # Partner earns 80% of delivery fee
            partner_earnings = self.delivery_fee * Decimal('0.80')
            
            DeliveryAssignment.objects.create(
                order=self.order,
                delivery_partner=self.delivery_partner,
                pickup_address=self.order.daily_meal.chef.chef_profile.kitchen_address,
                delivery_address=self.order.delivery_address,
                estimated_pickup_time=self.estimated_pickup_time,
                estimated_delivery_time=self.estimated_delivery_time,
                delivery_fee=self.delivery_fee,
                partner_earnings=partner_earnings
            )
            
            # Update order status
            self.order.order_status = 'out_for_delivery'
            self.order.save()
            
            # Update partner availability
            self.delivery_partner.is_available = False
            self.delivery_partner.save()
            
            return True
        return False
    
    def decline_request(self):
        """Decline the delivery request"""
        if self.status == 'pending':
            self.status = 'declined'
            self.responded_at = timezone.now()
            self.save()
            return True
        return False

class DeliveryAssignment(models.Model):
    """Active delivery assignment"""
    DELIVERY_STATUS = (
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    )
    
    order = models.OneToOneField(DailyMealOrder, on_delete=models.CASCADE, related_name='delivery_assignment')
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE, related_name='deliveries')
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='assigned')
    
    # Addresses
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    
    # Timing
    estimated_pickup_time = models.DateTimeField()
    estimated_delivery_time = models.DateTimeField()
    actual_pickup_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Financial
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    partner_earnings = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Tracking
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Notes
    pickup_notes = models.TextField(blank=True)
    delivery_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery Assignment for {self.order.order_id}"
    
    def mark_picked_up(self, latitude=None, longitude=None):
        """Mark order as picked up"""
        self.status = 'picked_up'
        self.actual_pickup_time = timezone.now()
        if latitude and longitude:
            self.pickup_latitude = latitude
            self.pickup_longitude = longitude
        self.save()
        
        # Update order status
        self.order.order_status = 'picked_up'
        self.order.save()
    
    def mark_in_transit(self):
        """Mark delivery as in transit"""
        self.status = 'in_transit'
        self.save()
        
        # Update order status
        self.order.order_status = 'in_transit'
        self.order.save()
    
    def mark_delivered(self, latitude=None, longitude=None, notes=None):
        """Mark delivery as completed"""
        self.status = 'delivered'
        self.actual_delivery_time = timezone.now()
        if latitude and longitude:
            self.delivery_latitude = latitude
            self.delivery_longitude = longitude
        if notes:
            self.delivery_notes = notes
        self.save()
        
        # Update order status
        self.order.order_status = 'delivered'
        self.order.delivery_time = timezone.now()
        self.order.save()
        
        # Update partner stats
        partner = self.delivery_partner
        partner.total_deliveries += 1
        partner.is_available = True
        partner.save()
    
    def get_pickup_location(self):
        """Get chef pickup location details"""
        chef = self.order.daily_meal.chef
        return {
            'name': chef.username,
            'phone': chef.phone_number,
            'address': self.pickup_address,
            'kitchen_address': chef.chef_profile.kitchen_address,
            'order_details': {
                'order_id': self.order.order_id,
                'meal_name': self.order.daily_meal.main_dish,
                'portions': self.order.portions,
                'special_instructions': self.order.special_instructions
            }
        }
    
    def get_delivery_location(self):
        """Get customer delivery location details"""
        customer = self.order.customer
        return {
            'name': customer.username,
            'phone': customer.phone_number,
            'address': self.delivery_address,
            'order_details': {
                'order_id': self.order.order_id,
                'meal_name': self.order.daily_meal.main_dish,
                'portions': self.order.portions,
                'special_instructions': self.order.special_instructions,
                'total_amount': self.order.total_amount
            }
        }

class DeliveryRating(models.Model):
    """Rating for delivery partners"""
    delivery_assignment = models.OneToOneField(DeliveryAssignment, on_delete=models.CASCADE, related_name='rating')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_ratings')
    rating = models.PositiveIntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    feedback = models.TextField(blank=True, max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Delivery Rating for {self.delivery_assignment.order.order_id} - {self.rating} stars"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update partner's average rating
        partner = self.delivery_assignment.delivery_partner
        ratings = DeliveryRating.objects.filter(delivery_assignment__delivery_partner=partner)
        if ratings.exists():
            avg_rating = ratings.aggregate(models.Avg('rating'))['rating__avg']
            partner.average_rating = round(avg_rating, 2)
            partner.save()
