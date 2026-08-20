from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout, authenticate
from ..models import User, ChefProfile, CustomerProfile, PhoneOTP
from ..serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, ChefProfileSerializer, CustomerProfileSerializer, OTPRequestSerializer, OTPVerifySerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
