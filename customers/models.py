from django.db import models
from authentication.models import User
from chefs.models import FoodItem

class FavoriteChef(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_chefs')
    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'chef']
    
    def __str__(self):
        return f"{self.customer.username} favorites {self.chef.username}"

class FavoriteFood(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_foods')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'food_item']
    
    def __str__(self):
        return f"{self.customer.username} favorites {self.food_item.name}"

class FoodReview(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_reviews')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'food_item']
    
    def __str__(self):
        return f"Review for {self.food_item.name} by {self.customer.username}"

class CustomerAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=[
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ])
    address_line = models.TextField()
    landmark = models.CharField(max_length=200, blank=True, null=True)
    address_identifier = models.CharField(max_length=100, blank=True, null=True, help_text="Custom address identifier like 'Near Central Park'")
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.username}'s {self.get_address_type_display()} address"

class SearchHistory(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=200)
    searched_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Search '{self.query}' by {self.customer.username}"

class CustomerRating(models.Model):
    """Rating system for chefs to rate customers"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_ratings')
    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_customer_ratings')
    order = models.ForeignKey('orders.DailyMealOrder', on_delete=models.CASCADE, related_name='customer_ratings')
    rating = models.PositiveIntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    feedback = models.TextField(
        blank=True,
        max_length=300,
        help_text="Optional feedback about the customer (max 300 chars)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'order']
    
    def __str__(self):
        return f"Rating for {self.customer.username} by {self.chef.username} ({self.rating} stars)"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update customer's rating when rating is saved
        self.customer.update_rating()
