from django.db import models
from authentication.models import User

class FoodItem(models.Model):
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
    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['chef', 'customer']
    
    def __str__(self):
        return f"Review for {self.chef.username} by {self.customer.username}"
