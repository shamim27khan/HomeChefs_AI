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
from .models import FoodItem, FoodSchedule, ChefReview, CustomerReview, DailyMeal, ChefProfile, DailyEarning
from .serializers import FoodItemSerializer, FoodItemCreateSerializer, FoodScheduleSerializer, FoodScheduleCreateSerializer, ChefReviewSerializer
from .serializers_mvp import (
    DailyMealSerializer, DailyMealCreateSerializer, ChefProfileSerializer,
    PublicChefSerializer, AdminChefSerializer, TodayMealsSerializer, 
    CustomerReviewSerializer, DailyEarningSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Get food items for the authenticated chef. Only chefs can access this endpoint.",
    responses={
        200: openapi.Response(
            'List of chef food items', 
            examples={
                'application/json': [
                    {
                        'id': 1,
                        'name': 'Butter Chicken',
                        'description': 'Tender chicken in rich, creamy tomato-based gravy',
                        'cuisine_type': 'North Indian',
                        'meal_type': 'dinner',
                        'price': '250.00',
                        'available_quantity': 5,
                        'preparation_time': 45,
                        'ingredients': 'Chicken, Butter, Cream, Tomatoes, Onions, Garlic, Ginger, Spices',
                        'is_vegetarian': False,
                        'is_available': True
                    }
                ]
            }
        ),
        403: openapi.Response('Forbidden - Only chefs can access this endpoint')
    }
)
@swagger_auto_schema(
    method='post',
    tags=['Chefs'],
    operation_description="Create a new food item. Only chefs can access this endpoint.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name', 'description', 'cuisine_type', 'meal_type', 'price', 'available_quantity', 'preparation_time', 'ingredients'],
        properties={
            'name': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Food item name',
                example='Butter Chicken'
            ),
            'description': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Detailed description of the food item',
                example='Tender chicken in rich, creamy tomato-based gravy with butter and cream'
            ),
            'cuisine_type': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Type of cuisine',
                example='North Indian'
            ),
            'meal_type': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Meal type (breakfast, lunch, dinner, snacks, desserts)',
                example='dinner'
            ),
            'price': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Price in rupees',
                example='250.00'
            ),
            'available_quantity': openapi.Schema(
                type=openapi.TYPE_INTEGER, 
                description='Number of portions available',
                example=5
            ),
            'preparation_time': openapi.Schema(
                type=openapi.TYPE_INTEGER, 
                description='Preparation time in minutes',
                example=45
            ),
            'ingredients': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='List of ingredients',
                example='Chicken, Butter, Cream, Tomatoes, Onions, Garlic, Ginger, Spices'
            ),
            'is_vegetarian': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, 
                description='Whether the item is vegetarian',
                example=False
            ),
            'is_available': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, 
                description='Whether the item is currently available',
                example=True
            ),
        }
    ),
    responses={
        201: openapi.Response(
            description='Food item created successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'chef': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                    'cuisine_type': openapi.Schema(type=openapi.TYPE_STRING),
                    'meal_type': openapi.Schema(type=openapi.TYPE_STRING),
                    'price': openapi.Schema(type=openapi.TYPE_STRING),
                    'available_quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'preparation_time': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'ingredients': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_vegetarian': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'is_available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'id': 1,
                    'chef': 2,
                    'name': 'Butter Chicken',
                    'description': 'Tender chicken in rich, creamy tomato-based gravy with butter and cream',
                    'cuisine_type': 'North Indian',
                    'meal_type': 'dinner',
                    'price': '250.00',
                    'available_quantity': 5,
                    'preparation_time': 45,
                    'ingredients': 'Chicken, Butter, Cream, Tomatoes, Onions, Garlic, Ginger, Spices',
                    'is_vegetarian': False,
                    'is_available': True,
                    'created_at': '2024-01-15T10:30:00Z'
                }
            }
        ),
        400: openapi.Response(
            description='Bad request - validation errors',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            ),
            examples={
                'application/json': {
                    'price': ['This field is required.'],
                    'available_quantity': ['This field is required.']
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only chefs can access this endpoint',
            examples={
                'application/json': {
                    'error': 'Only chefs can access this endpoint'
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def food_items(request):
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        food_items = FoodItem.objects.filter(chef=request.user)
        serializer = FoodItemSerializer(food_items, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = FoodItemCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            food_item = serializer.save()
            return Response(FoodItemSerializer(food_item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def food_item_detail(request, food_id):
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    food_item = get_object_or_404(FoodItem, id=food_id, chef=request.user)
    
    if request.method == 'GET':
        serializer = FoodItemSerializer(food_item)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = FoodItemCreateSerializer(food_item, data=request.data, partial=True)
        if serializer.is_valid():
            updated_food = serializer.save()
            return Response(FoodItemSerializer(updated_food).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        food_item.delete()
        return Response({'message': 'Food item deleted successfully'})

@swagger_auto_schema(
    method='post',
    tags=['Chefs'],
    operation_description="Create a new food schedule for availability. Only chefs can access this endpoint.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['day_of_week', 'start_time', 'end_time'],
        properties={
            'day_of_week': openapi.Schema(
                type=openapi.TYPE_INTEGER, 
                description='Day of week (0=Monday, 6=Sunday)',
                minimum=0,
                maximum=6,
                example=1
            ),
            'start_time': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Start time in HH:MM format',
                example='09:00'
            ),
            'end_time': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='End time in HH:MM format',
                example='14:00'
            ),
            'is_available': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, 
                description='Whether this schedule is active',
                example=True
            )
        }
    ),
    responses={
        201: openapi.Response(
            description='Food schedule created successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'food_item': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'day_of_week': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'start_time': openapi.Schema(type=openapi.TYPE_STRING),
                    'end_time': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'id': 1,
                    'food_item': 1,
                    'day_of_week': 1,
                    'start_time': '09:00',
                    'end_time': '14:00',
                    'is_available': True,
                    'created_at': '2024-01-15T10:30:00Z'
                }
            }
        ),
        400: openapi.Response(
            description='Bad request - validation errors',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            ),
            examples={
                'application/json': {
                    'start_time': ['This field is required.'],
                    'end_time': ['This field is required.']
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only chefs can access this endpoint',
            examples={
                'application/json': {
                    'error': 'Only chefs can access this endpoint'
                }
            }
        ),
        404: openapi.Response(
            description='Food item not found',
            examples={
                'application/json': {
                    'detail': 'Not found.'
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def food_schedules(request, food_id):
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    food_item = get_object_or_404(FoodItem, id=food_id, chef=request.user)
    
    if request.method == 'GET':
        schedules = FoodSchedule.objects.filter(food_item=food_item)
        serializer = FoodScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = FoodScheduleCreateSerializer(data=request.data)
        if serializer.is_valid():
            schedule = serializer.save(food_item=food_item)
            return Response(FoodScheduleSerializer(schedule).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Get reviews for the authenticated chef."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_reviews(request):
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    reviews = ChefReview.objects.filter(chef=request.user)
    serializer = ChefReviewSerializer(reviews, many=True)
    return Response(serializer.data)

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

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Get detailed information about a specific chef."
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_chef_detail(request, chef_id):
    chef = get_object_or_404(ChefProfile, user__id=chef_id, is_verified=True)
    
    # Get chef's food items
    food_items = FoodItem.objects.filter(chef=chef.user, is_available=True)
    
    # Get reviews
    reviews = ChefReview.objects.filter(chef=chef.user)
    
    chef_data = {
        'id': chef.user.id,
        'username': chef.user.username,
        'first_name': chef.user.first_name,
        'last_name': chef.user.last_name,
        'bio': chef.bio,
        'cuisine_specialties': chef.cuisine_specialties,
        'experience_years': chef.experience_years,
        'rating': chef.rating,
        'delivery_radius': chef.delivery_radius,
        'kitchen_address': chef.kitchen_address,
        'profile_picture': chef.user.profile_picture.url if chef.user.profile_picture else None,
        'food_items': FoodItemSerializer(food_items, many=True).data,
        'reviews': ChefReviewSerializer(reviews, many=True).data
    }
    
    return Response(chef_data)

@swagger_auto_schema(
    method='post',
    tags=['Chefs'],
    operation_description="Rate a daily meal (customer endpoint)."
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rate_meal(request, meal_id):
    """Rate a daily meal (customer endpoint)"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can rate meals'}, status=status.HTTP_403_FORBIDDEN)
    
    from .models import DailyMeal
    meal = get_object_or_404(DailyMeal, id=meal_id)
    
    # Check if customer has ordered this meal
    from orders.models import DailyMealOrder
    has_ordered = DailyMealOrder.objects.filter(
        daily_meal=meal,
        customer=request.user,
        order_status='delivered'
    ).exists()
    
    if not has_ordered:
        return Response({'error': 'You can only rate meals you have ordered and received'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if already rated
    if CustomerReview.objects.filter(daily_meal=meal, customer=request.user).exists():
        return Response({'error': 'You have already rated this meal'}, status=status.HTTP_400_BAD_REQUEST)
    
    rating = request.data.get('rating')
    comment = request.data.get('comment', '')
    
    if not rating or int(rating) < 1 or int(rating) > 5:
        return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create review
    review = CustomerReview.objects.create(
        daily_meal=meal,
        customer=request.user,
        rating=rating,
        comment=comment
    )
    
    return Response({'message': 'Meal rated successfully', 'rating': review.rating})

# Custom decorator to bypass CSRF for API views
def csrf_exempt_api_view(view_func):
    """Custom decorator to bypass CSRF for DRF API views"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Manually disable CSRF protection for this view
        request._dont_enforce_csrf_checks = True
        return view_func(request, *args, **kwargs)
    return wrapped_view

# Chef Dashboard Views (formerly MVP)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def chef_daily_meals(request):
    """Chef can view and manage their daily meals"""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        target_date = request.GET.get('date', date.today())
        meals = DailyMeal.objects.filter(chef=request.user, date=target_date)
        serializer = DailyMealSerializer(meals, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = DailyMealCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                meal = serializer.save(chef=request.user)
                return Response(DailyMealSerializer(meal).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def chef_daily_meal_detail(request, meal_id):
    """Chef can manage a specific daily meal"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    meal = get_object_or_404(DailyMeal, id=meal_id, chef=request.user)
    
    if request.method == 'GET':
        serializer = DailyMealSerializer(meal)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = DailyMealCreateSerializer(meal, data=request.data, partial=True)
        if serializer.is_valid():
            updated_meal = serializer.save()
            return Response(DailyMealSerializer(updated_meal).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if meal.current_orders > 0:
            return Response(
                {'error': 'Cannot delete meal with existing orders'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        meal.delete()
        return Response({'message': 'Meal deleted successfully'})

@api_view(['GET', 'POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def chef_profile(request):
    """Chef can view and update their profile"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        profile = request.user.chefprofile
    except ChefProfile.DoesNotExist:
        profile = ChefProfile.objects.create(
            user=request.user,
            phone_number=f"TEMP{request.user.id}{request.user.id}",
            address_line1="Address to be updated",
            area="Not set",
            city="Not set", 
            pincode="000000"
        )
    
    if request.method == 'GET':
        serializer = ChefProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ChefProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        serializer = ChefProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Chef can view their daily earnings."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_earnings(request):
    """Chef can view their daily earnings"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    start_date = request.GET.get('start_date', date.today() - timedelta(days=30))
    end_date = request.GET.get('end_date', date.today())
    
    earnings = DailyEarning.objects.filter(
        chef=request.user,
        date__range=[start_date, end_date]
    ).order_by('-date')
    
    serializer = DailyEarningSerializer(earnings, many=True)
    
    total_earnings = sum(e.net_earnings for e in earnings)
    total_orders = sum(e.total_orders for e in earnings)
    
    return Response({
        'earnings': serializer.data,
        'summary': {
            'total_earnings': total_earnings,
            'total_orders': total_orders,
            'period': f"{start_date} to {end_date}"
        }
    })

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Chef can view their orders."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_orders(request):
    """Chef can view their orders"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    target_date = request.GET.get('date', date.today())
    
    from orders.models import DailyMealOrder
    orders = DailyMealOrder.objects.filter(
        daily_meal__chef=request.user,
        daily_meal__date=target_date
    ).order_by('-order_time')
    
    from orders.serializers_mvp import ChefOrderListSerializer
    serializer = ChefOrderListSerializer(orders, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Customers can browse nearby chefs with comprehensive filters."
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_chefs(request):
    """Customers can browse nearby chefs with comprehensive filters"""
    area = request.GET.get('area', '')
    city = request.GET.get('city', '')
    cuisine = request.GET.get('cuisine', '')
    search = request.GET.get('search', '')
    radius = request.GET.get('radius', '')
    meal_type = request.GET.get('meal_type', '')
    dietary = request.GET.get('dietary', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    chefs = User.objects.filter(role='chef')
    
    if area:
        chefs = chefs.filter(
            Q(chefprofile__area__icontains=area) |
            Q(username__icontains=area) |
            Q(first_name__icontains=area) |
            Q(last_name__icontains=area)
        )
    if city:
        chefs = chefs.filter(chefprofile__city__icontains=city)
    
    if cuisine:
        cuisine_list = [c.strip() for c in cuisine.split(',') if c.strip()]
        cuisine_filter = Q()
        for c in cuisine_list:
            cuisine_filter |= Q(chefprofile__cuisine_specialties__icontains=c)
        chefs = chefs.filter(cuisine_filter)
    
    if search:
        search_words = search.lower().split()
        search_filter = Q()
        for word in search_words:
            search_filter |= (
                Q(username__icontains=word) |
                Q(first_name__icontains=word) |
                Q(last_name__icontains=word) |
                Q(chefprofile__cuisine_specialties__icontains=word)
            )
        chefs = chefs.filter(search_filter)
    
    if meal_type:
        meal_type_list = [m.strip() for m in meal_type.split(',') if m.strip()]
        pass
    
    if dietary:
        dietary_list = [d.strip() for d in dietary.split(',') if d.strip()]
        dietary_filter = Q()
        for d in dietary_list:
            if d.lower() == 'vegetarian':
                dietary_filter |= Q(chefprofile__cuisine_specialties__icontains='Vegetarian')
            elif d.lower() == 'non-vegetarian':
                dietary_filter |= Q(chefprofile__cuisine_specialties__icontains='Non-Vegetarian')
        chefs = chefs.filter(dietary_filter)
    
    if min_price or max_price:
        pass
    
    if radius:
        pass
    
    chefs = chefs.filter(chefprofile__isnull=False)
    
    for chef in User.objects.filter(role='chef'):
        try:
            chef.chefprofile
        except ChefProfile.DoesNotExist:
            ChefProfile.objects.create(
                user=chef,
                phone_number=f"TEMP{chef.id}{chef.id}",
                address_line1="Address to be updated",
                area="Not set",
                city="Not set", 
                pincode="000000"
            )
    
    serializer = PublicChefSerializer(chefs, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Customers can browse today's available meals."
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def today_meals(request):
    """Customers can browse today's available meals"""
    today = date.today()
    
    area = request.GET.get('area', '')
    meal_type = request.GET.get('meal_type', '')
    
    meals = DailyMeal.objects.filter(
        date=today,
        is_active=True
    ).select_related('chef', 'chef__chefprofile')
    
    orderable_meals = [meal for meal in meals if meal.is_orderable]
    
    meal_ids = [meal.id for meal in orderable_meals]
    meals = DailyMeal.objects.filter(id__in=meal_ids).select_related('chef', 'chef__chefprofile')
    
    if area:
        meals = meals.filter(chef__chefprofile__area__icontains=area)
    if meal_type:
        meals = meals.filter(meal_type=meal_type)

    serializer = TodayMealsSerializer(meals, many=True)
    return Response(serializer.data)

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

@swagger_auto_schema(
    method='post',
    tags=['Chefs'],
    operation_description="Customers can rate completed orders."
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def customer_review(request, order_id):
    """Customers can rate completed orders"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    from orders.models import DailyMealOrder
    order = get_object_or_404(DailyMealOrder, id=order_id, customer=request.user)
    
    if order.order_status not in ['ready', 'delivered']:
        return Response(
            {'error': 'Can only rate completed orders'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if hasattr(order, 'rating'):
        return Response(
            {'error': 'Order already rated'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = CustomerReviewSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        review = serializer.save(daily_order=order, customer=request.user)
        return Response(CustomerReviewSerializer(review).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAdminUser])
def admin_chef_verification(request):
    """Admin can verify chefs"""
    if request.method == 'GET':
        pending_chefs = ChefProfile.objects.filter(is_verified=False)
        chefs = User.objects.filter(
            role='chef',
            chefprofile__in=pending_chefs
        )
        serializer = AdminChefSerializer(chefs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        chef_id = request.data.get('chef_id')
        chef = get_object_or_404(User, id=chef_id, role='chef')
        
        chef.chefprofile.is_verified = True
        chef.chefprofile.verification_date = timezone.now()
        chef.chefprofile.save()
        
        return Response({'message': f'Chef {chef.username} verified successfully'})

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Admin can view complete chef information."
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_chefs(request):
    """Admin can view complete chef information"""
    chefs = User.objects.filter(role='chef').order_by('-date_joined')
    serializer = AdminChefSerializer(chefs, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Admin can view delivery partner information."
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_delivery_partners(request):
    """Admin can view delivery partner information"""
    from delivery.models import DeliveryPartner
    
    delivery_partners = DeliveryPartner.objects.select_related('user').all().order_by('-created_at')
    
    partners_data = []
    for partner in delivery_partners:
        partners_data.append({
            'id': partner.id,
            'user': {
                'id': partner.user.id,
                'username': partner.user.username,
                'first_name': partner.user.first_name,
                'last_name': partner.user.last_name,
                'email': partner.user.email,
            },
            'phone_number': partner.phone_number,
            'vehicle_type': partner.vehicle_type,
            'vehicle_number': partner.vehicle_number,
            'license_number': partner.license_number,
            'current_latitude': partner.current_latitude,
            'current_longitude': partner.current_longitude,
            'current_location': f"{partner.current_latitude}, {partner.current_longitude}" if partner.current_latitude and partner.current_longitude else None,
            'last_location_update': partner.last_location_update,
            'status': partner.status,
            'verification_status': partner.verification_status,
            'is_available': partner.is_available,
            'total_deliveries': partner.total_deliveries,
            'completed_orders': partner.total_deliveries,
            'average_rating': partner.average_rating,
            'completion_rate': partner.completion_rate,
            'service_areas': partner.service_areas,
            'max_delivery_distance': partner.max_delivery_distance,
            'created_at': partner.created_at,
        })
    
    return Response(partners_data)

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Admin dashboard with key metrics."
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard(request):
    """Admin dashboard with key metrics"""
    from django.db.models import Count, Sum, Q
    from orders.models import DailyMealOrder
    
    today = date.today()
    
    total_chefs = User.objects.filter(role='chef').count()
    verified_chefs = User.objects.filter(role='chef', chefprofile__is_verified=True).count()
    total_customers = User.objects.filter(role='customer').count()
    total_delivery_partners = User.objects.filter(role='delivery_partner').count()
    verified_delivery_partners = User.objects.filter(
        role='delivery_partner', 
        delivery_partner__verification_status='verified'
    ).count()
    
    today_meals = DailyMeal.objects.filter(date=today).count()
    today_orders = DailyMealOrder.objects.filter(order_time__date=today).count()
    today_revenue = DailyMealOrder.objects.filter(
        order_time__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    today_commission = DailyMealOrder.objects.filter(
        order_time__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('platform_commission'))['total'] or 0
    
    return Response({
        'overview': {
            'total_chefs': total_chefs,
            'verified_chefs': verified_chefs,
            'total_customers': total_customers,
            'total_delivery_partners': total_delivery_partners,
            'verified_delivery_partners': verified_delivery_partners,
            'chef_verification_rate': round((verified_chefs / total_chefs * 100) if total_chefs > 0 else 0, 1),
            'delivery_partner_verification_rate': round((verified_delivery_partners / total_delivery_partners * 100) if total_delivery_partners > 0 else 0, 1)
        },
        'today': {
            'meals_posted': today_meals,
            'orders_received': today_orders,
            'revenue': today_revenue,
            'platform_commission': today_commission
        }
    })

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Find dishes available within 3km radius of user's location."
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def nearby_dishes(request):
    """Find dishes available within 3km radius of user's location"""
    try:
        user_lat = float(request.GET.get('latitude'))
        user_lon = float(request.GET.get('longitude'))
        radius_km = float(request.GET.get('radius', 3.0))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Valid latitude and longitude are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if radius_km > 10:
        radius_km = 10
    
    meals = DailyMeal.objects.filter(
        date=date.today(),
        is_active=True,
        current_orders__lt=F('extra_portions')
    ).select_related('chef', 'chef__chefprofile')
    
    orderable_meals = [meal for meal in meals if meal.is_orderable]
    
    meal_ids = [meal.id for meal in orderable_meals]
    meals = DailyMeal.objects.filter(id__in=meal_ids).select_related('chef', 'chef__chefprofile')
    
    nearby_meals = []
    for meal in meals:
        try:
            chef_lat = float(meal.chef.chefprofile.latitude)
            chef_lon = float(meal.chef.chefprofile.longitude)
            
            distance = calculate_distance(user_lat, user_lon, chef_lat, chef_lon)
            
            if distance <= radius_km:
                meal_data = TodayMealsSerializer(meal).data
                meal_data['distance'] = round(distance, 2)
                nearby_meals.append(meal_data)
                
        except (TypeError, ValueError):
            meal_data = TodayMealsSerializer(meal).data
            meal_data['distance'] = None
            nearby_meals.append(meal_data)
    
    nearby_meals.sort(key=lambda x: (x['distance'] is None, x['distance'] or float('inf')))
    
    return Response({
        'dishes': nearby_meals,
        'total_found': len(nearby_meals),
        'search_location': {
            'latitude': user_lat,
            'longitude': user_lon,
            'radius_km': radius_km
        }
    })

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
    operation_description="Get chef's meals for today."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_meals(request):
    """Get chef's meals for today"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    today = date.today()
    
    meals = DailyMeal.objects.filter(
        chef=request.user,
        date=today
    ).order_by('meal_type')
    
    serializer = TodayMealsSerializer(meals, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    tags=['Chefs'],
    operation_description="Toggle meal active/inactive status."
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_meal_status(request, meal_id):
    """Toggle meal active/inactive status"""
    try:
        meal = DailyMeal.objects.get(id=meal_id, chef=request.user)
        meal.is_active = not meal.is_active
        meal.save()
        
        return Response({
            'success': True,
            'is_active': meal.is_active,
            'message': f'Meal {"activated" if meal.is_active else "deactivated"} successfully'
        })
    except DailyMeal.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Meal not found or you do not have permission to modify it'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

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

@swagger_auto_schema(
    method='put',
    tags=['Chefs'],
    operation_description="Update meal details."
)
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_meal(request, meal_id):
    """Update meal details"""
    try:
        meal = DailyMeal.objects.get(id=meal_id, chef=request.user)
        
        update_data = request.data
        
        allowed_fields = [
            'main_dish', 'side_dish', 'additional_items',
            'extra_portions', 'price_per_portion', 'order_cutoff_time',
            'pickup_available', 'delivery_available', 'delivery_radius'
        ]
        
        for field in allowed_fields:
            if field in update_data:
                setattr(meal, field, update_data[field])
        
        meal.save()
        
        serializer = DailyMealSerializer(meal)
        return Response({
            'success': True,
            'meal': serializer.data,
            'message': 'Meal updated successfully'
        })
    except DailyMeal.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Meal not found or you do not have permission to modify it'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
