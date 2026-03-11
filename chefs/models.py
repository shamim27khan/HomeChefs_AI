from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from authentication.models import User

class DailyMeal(models.Model):
    """Daily meal uploaded by home chef - MVP Core Feature"""
    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
    )
    
    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_meals')
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    
    # Menu details (what they're already cooking)
    main_dish = models.CharField(max_length=100, help_text="Main dish (e.g., Dal, Sabzi)")
    side_dish = models.CharField(max_length=100, blank=True, help_text="Side dish (e.g., Roti, Rice)")
    additional_items = models.TextField(blank=True, help_text="Additional items (e.g., Salad, Pickle)")
    
    # MVP constraints
    extra_portions = models.PositiveIntegerField(
        default=1, 
        help_text="Extra portions available (1-5)",
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    price_per_portion = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Fixed price per extra portion"
    )
    
    # Order management
    order_cutoff_time = models.TimeField(
        default='20:00:00',  # Default to 8 PM
        help_text="Last time to order this meal"
    )
    max_orders = models.PositiveIntegerField(default=5)
    current_orders = models.PositiveIntegerField(default=0)
    
    # Delivery options
    pickup_available = models.BooleanField(default=True)
    delivery_available = models.BooleanField(default=False)
    delivery_radius = models.PositiveIntegerField(
        default=3, 
        help_text="Delivery radius in km"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Removed unique_together to allow multiple meals per chef per date per meal_type
        # unique_together = ['chef', 'date', 'meal_type']
        ordering = ['-date', 'meal_type']
    
    def __str__(self):
        return f"{self.get_meal_type_display()} - {self.chef.username} ({self.date})"
    
    @property
    def available_portions(self):
        return self.extra_portions - self.current_orders
    
    @property
    def is_orderable(self):
        from django.utils import timezone
        from datetime import datetime, time as time_class
        
        now = timezone.now()
        
        # Convert order_cutoff_time from string to time if needed
        if isinstance(self.order_cutoff_time, str):
            try:
                cutoff_time = datetime.strptime(self.order_cutoff_time, '%H:%M:%S').time()
            except ValueError:
                # Try with just hours:minutes format
                cutoff_time = datetime.strptime(self.order_cutoff_time, '%H:%M').time()
        else:
            cutoff_time = self.order_cutoff_time
        
        # Create cutoff datetime for today's date
        if self.date == timezone.now().date():
            # For today's meals, use cutoff time with today's date
            cutoff_datetime = timezone.now().replace(
                hour=cutoff_time.hour,
                minute=cutoff_time.minute,
                second=cutoff_time.second,
                microsecond=0
            )
            return (
                self.is_active and 
                self.available_portions > 0 and 
                now <= cutoff_datetime
            )
        elif self.date > timezone.now().date():
            # For future meals, always orderable
            return (
                self.is_active and 
                self.available_portions > 0
            )
        else:
            # For past meals, not orderable
            return False

class ChefProfile(models.Model):
    """Simple chef profile for MVP"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    
    # Address for local delivery
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Geospatial location for precise distance calculation
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Latitude for location-based searches"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Longitude for location-based searches"
    )
    
    # Chef details
    cooking_experience = models.PositiveIntegerField(
        default=5,
        help_text="Years of cooking experience"
    )
    cuisine_specialties = models.CharField(
        max_length=200,
        help_text="e.g., North Indian, South Indian, Chinese"
    )
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Kitchen details (simple for MVP)
    kitchen_type = models.CharField(
        max_length=50,
        choices=[
            ('home', 'Home Kitchen'),
            ('dedicated', 'Dedicated Kitchen Space'),
        ],
        default='home'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.area}"
    
    @property
    def full_address(self):
        parts = [self.address_line1, self.address_line2, self.area, self.city, self.pincode]
        return ', '.join(filter(None, parts))

class DailyEarning(models.Model):
    """Daily earnings summary for chefs"""
    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_earnings')
    date = models.DateField()
    total_orders = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    platform_commission = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    net_earnings = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['chef', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.chef.username} - {self.date} - ₹{self.net_earnings}"

class CustomerReview(models.Model):
    """Simple customer review system"""
    daily_meal = models.ForeignKey(DailyMeal, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_reviews')
    rating = models.PositiveIntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(
        blank=True,
        max_length=200,
        help_text="Optional feedback (max 200 chars)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['daily_meal', 'customer']
    
    def __str__(self):
        return f"{self.daily_meal} - {self.customer.username} ({self.rating} stars)"

# Legacy models for backward compatibility (will be phased out)
class FoodItem(models.Model):
    """Legacy model - use DailyMeal instead"""
    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
        ('desserts', 'Desserts'),
    )
    
    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    cuisine_type = models.CharField(max_length=50)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available_quantity = models.PositiveIntegerField(default=1)
    preparation_time = models.PositiveIntegerField(help_text="Preparation time in minutes")
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    ingredients = models.TextField(help_text="List of ingredients")
    is_vegetarian = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} by {self.chef.username}"

class FoodSchedule(models.Model):
    """Legacy model - use DailyMeal instead"""
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    available_from = models.TimeField()
    available_to = models.TimeField()
    max_orders = models.PositiveIntegerField(default=10)
    current_orders = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['food_item', 'date']
    
    def __str__(self):
        return f"{self.food_item.name} - {self.date}"

class ChefReview(models.Model):
    """Legacy model - use CustomerReview instead"""
    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['chef', 'customer']
    
    def __str__(self):
        return f"Review for {self.chef.username} by {self.customer.username}"
