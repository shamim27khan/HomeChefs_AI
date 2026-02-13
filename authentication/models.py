from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_ROLES = (
        ('chef', 'Chef'),
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class ChefProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chef_profile')
    bio = models.TextField(blank=True, null=True)
    cuisine_specialties = models.CharField(max_length=200, help_text="Comma-separated list of cuisines")
    experience_years = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    fssai_license = models.CharField(max_length=50, blank=True, null=True)
    kitchen_address = models.TextField()
    delivery_radius = models.PositiveIntegerField(help_text="Delivery radius in km", default=5)
    
    def __str__(self):
        return f"Chef: {self.user.username}"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    preferred_cuisines = models.CharField(max_length=200, blank=True, help_text="Comma-separated list")
    dietary_restrictions = models.TextField(blank=True, null=True)
    default_delivery_address = models.TextField()
    
    def __str__(self):
        return f"Customer: {self.user.username}"
