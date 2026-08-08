from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random

class User(AbstractUser):
    USER_ROLES = (
        ('chef', 'Chef'),
        ('customer', 'Customer'),
        ('delivery_partner', 'Delivery Partner'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    
    # Rating fields (for customers and delivery partners)
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        help_text="Average rating received (1-5)"
    )
    total_ratings = models.PositiveIntegerField(
        default=0,
        help_text="Total number of ratings received"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def update_rating(self):
        """Update average rating based on received ratings"""
        from django.db.models import Avg
        
        if self.role == 'customer':
            # Update based on ratings from chefs
            from customers.models import CustomerRating
            ratings = CustomerRating.objects.filter(customer=self)
            if ratings.exists():
                self.average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
                self.total_ratings = ratings.count()
                self.save()
        elif self.role == 'delivery_partner':
            # Update based on delivery ratings
            from delivery.models import DeliveryRating
            ratings = DeliveryRating.objects.filter(delivery_assignment__delivery_partner__user=self)
            if ratings.exists():
                self.average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
                self.total_ratings = ratings.count()
                self.save()

class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.phone_number}"
    
    @classmethod
    def generate_otp(cls, phone_number):
        """Generate and save a new OTP for the given phone number"""
        # Delete any existing unverified OTPs for this phone number
        cls.objects.filter(phone_number=phone_number, is_verified=False).delete()
        
        # Generate 6-digit OTP
        otp_code = f"{random.randint(100000, 999999)}"
        
        # Set expiry time (10 minutes from now)
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        
        # Create new OTP record
        otp = cls.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at
        )
        
        return otp
    
    @classmethod
    def verify_otp(cls, phone_number, otp_code):
        """Verify the OTP for the given phone number"""
        try:
            otp = cls.objects.get(
                phone_number=phone_number,
                otp_code=otp_code,
                is_verified=False
            )
            
            # Check if OTP has expired
            if timezone.now() > otp.expires_at:
                otp.delete()
                return False, "OTP has expired. Please request a new one."
            
            # Check attempts (max 3 attempts)
            if otp.attempts >= 2:  # Allow 3 attempts total (0, 1, 2)
                otp.delete()
                return False, "Too many attempts. Please request a new OTP."
            
            # Mark as verified and increment attempts
            otp.is_verified = True
            otp.attempts += 1
            otp.save()
            return True, "Phone number verified successfully!"
            
        except cls.DoesNotExist:
            # Handle case where OTP doesn't exist (wrong code)
            # Check if there are any recent attempts for this phone number
            recent_otps = cls.objects.filter(
                phone_number=phone_number, 
                is_verified=False
            ).order_by('-created_at')
            
            if recent_otps.exists():
                recent_otp = recent_otps.first()
                recent_otp.attempts += 1
                recent_otp.save()
                
                if recent_otp.attempts >= 3:
                    recent_otp.delete()
                    return False, "Too many attempts. Please request a new OTP."
                else:
                    remaining = 3 - recent_otp.attempts
                    return False, f"Invalid OTP. {remaining} attempts remaining."
            
            return False, "Invalid OTP. Please request a new one."

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
