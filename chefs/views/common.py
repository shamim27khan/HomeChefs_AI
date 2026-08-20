from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from functools import wraps
from django.utils import timezone
from django.db.models import F, Q
from datetime import date, time, timedelta
import math

from authentication.models import User
from ..models import FoodItem, FoodSchedule, ChefReview, CustomerReview, DailyMeal, ChefProfile, DailyEarning
from ..serializers import FoodItemSerializer, FoodItemCreateSerializer, FoodScheduleSerializer, FoodScheduleCreateSerializer, ChefReviewSerializer
from ..serializers_mvp import (
    DailyMealSerializer, DailyMealCreateSerializer, ChefProfileSerializer,
    PublicChefSerializer, AdminChefSerializer, TodayMealsSerializer, 
    CustomerReviewSerializer, DailyEarningSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Get list of all verified home chefs."
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_chef_list(request):
    chefs = ChefProfile.objects.filter(is_verified=True).select_related('user')
    chef_data = []
    
    for chef_profile in chefs:
        reviews = ChefReview.objects.filter(chef=chef_profile.user)
        avg_rating = sum(review.rating for review in reviews) / len(reviews) if reviews else 0
        
        chef_data.append({
            'id': chef_profile.user.id,
            'username': chef_profile.user.username,
            'first_name': chef_profile.user.first_name,
            'last_name': chef_profile.user.last_name,
            'bio': chef_profile.bio,
            'cuisine_specialties': chef_profile.cuisine_specialties,
            'experience_years': chef_profile.experience_years,
            'rating': chef_profile.rating,
            'delivery_radius': chef_profile.delivery_radius,
            'profile_picture': chef_profile.user.profile_picture.url if chef_profile.user.profile_picture else None
        })
    
    return Response(chef_data)


def csrf_exempt_api_view(view_func):
    """Custom decorator to bypass CSRF for DRF API views"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Manually disable CSRF protection for this view
        request._dont_enforce_csrf_checks = True
        return view_func(request, *args, **kwargs)
    return wrapped_view

# Chef Dashboard Views (formerly MVP)

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Customers can view their orders."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def customer_orders(request):
    """Customers can view their orders"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    from orders.models import DailyMealOrder
    orders = DailyMealOrder.objects.filter(
        customer=request.user
    ).order_by('-order_time')
    
    from orders.serializers_mvp import CustomerOrderListSerializer
    serializer = CustomerOrderListSerializer(orders, many=True)
    return Response(serializer.data)


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    r = 6371
    
    return c * r


@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Get detailed meal information for editing."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_meal_detail(request, meal_id):
    """Get detailed meal information for editing"""
    try:
        meal = DailyMeal.objects.get(id=meal_id, chef=request.user)
        serializer = DailyMealSerializer(meal)
        
        return Response({
            'success': True,
            'meal': serializer.data
        })
    except DailyMeal.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Meal not found or you do not have permission to access it'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
