from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, ChefProfile, CustomerProfile, PhoneOTP

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if phone number already exists
        phone_number = attrs.get('phone_number')
        if phone_number:
            if User.objects.filter(phone_number=phone_number).exists():
                raise serializers.ValidationError("This phone number is already registered. Please use a different phone number or login with your existing account.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        
        # Create profile based on role
        if user.role == 'chef':
            ChefProfile.objects.create(user=user)
        elif user.role == 'customer':
            CustomerProfile.objects.create(user=user)
        
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    otp_code = serializers.CharField(required=False)
    
    def validate(self, attrs):
        # Check if this is OTP-based login or username/password login
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code')
        username = attrs.get('username')
        password = attrs.get('password')
        
        if phone_number and otp_code:
            # OTP-based login
            if not phone_number or not otp_code:
                raise serializers.ValidationError('Phone number and OTP are required for OTP login')
        elif username and password:
            # Username/password login
            if not username or not password:
                raise serializers.ValidationError('Username and password are required for password login')
        else:
            raise serializers.ValidationError('Either provide username/password or phone_number/OTP')
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'profile_picture']
        read_only_fields = ['id', 'username', 'role']

class ChefProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ChefProfile
        fields = ['user', 'bio', 'cuisine_specialties', 'experience_years', 'rating', 'is_verified', 'fssai_license', 'kitchen_address', 'delivery_radius']

class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomerProfile
        fields = ['user', 'preferred_cuisines', 'dietary_restrictions', 'default_delivery_address']

class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        # Basic phone number validation
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Please enter a valid phone number")
        return value

class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric")
        return value
