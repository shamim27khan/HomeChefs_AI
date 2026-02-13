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
