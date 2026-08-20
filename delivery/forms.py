from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import DeliveryPartner

class DeliveryPartnerRegistrationForm(UserCreationForm):
    """Registration form for delivery partners"""
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        validators=[phone_regex],
        max_length=15,
        required=True,
        help_text="Enter your phone number with country code"
    )
    
    # Delivery partner specific fields
    vehicle_type = forms.ChoiceField(
        choices=[
            ('bike', 'Bike'),
            ('scooter', 'Scooter'),
            ('car', 'Car'),
            ('cycle', 'Bicycle'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    vehicle_number = forms.CharField(
        max_length=20,
        required=True,
        help_text="Vehicle registration number"
    )
    license_number = forms.CharField(
        max_length=50,
        required=True,
        help_text="Driving license number"
    )
    
    # Service area
    service_areas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Comma-separated list of areas you can serve (e.g., 'Downtown, Uptown, Suburbia')"
    )
    max_delivery_distance = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=10,
        help_text="Maximum delivery distance in kilometers"
    )
    
    # Address
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Your current address"
    )
    
    # Profile picture
    profile_picture = forms.ImageField(
        required=False,
        help_text="Optional: Upload your profile picture"
    )
    
    # Terms agreement
    agree_terms = forms.BooleanField(
        required=True,
        help_text="I agree to the terms and conditions for delivery partners"
    )
    
    class Meta:
        from authentication.models import User
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'password1', 'password2'
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'delivery_partner'
        
        if commit:
            user.save()
            
            # Handle profile picture if provided
            profile_picture = self.cleaned_data.get('profile_picture')
            if profile_picture:
                user.profile_picture = profile_picture
                user.save()
            
            # Create delivery partner profile
            DeliveryPartner.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                vehicle_type=self.cleaned_data['vehicle_type'],
                vehicle_number=self.cleaned_data['vehicle_number'],
                license_number=self.cleaned_data['license_number'],
                service_areas=self.cleaned_data['service_areas'],
                max_delivery_distance=self.cleaned_data['max_delivery_distance'],
                verification_status='pending'  # Requires admin verification
            )
        
        return user

class DeliveryPartnerProfileUpdateForm(forms.ModelForm):
    """Form for delivery partners to update their profile"""
    
    service_areas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Comma-separated list of areas you can serve"
    )
    
    class Meta:
        model = DeliveryPartner
        fields = [
            'phone_number', 'vehicle_type', 'vehicle_number', 
            'service_areas', 'max_delivery_distance'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={'readonly': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].widget.attrs['readonly'] = True
