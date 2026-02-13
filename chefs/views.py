from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import FoodItem, FoodSchedule, ChefReview
from .serializers import FoodItemSerializer, FoodItemCreateSerializer, FoodScheduleSerializer, FoodScheduleCreateSerializer, ChefReviewSerializer
from authentication.models import ChefProfile
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
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
    operation_description="Get list of all verified home chefs available on the platform. Includes ratings, specialties, and delivery information.",
    responses={
        200: openapi.Response(
            'List of verified chefs', 
            examples={
                'application/json': [
                    {
                        'id': 2,
                        'username': 'chef_rahul',
                        'first_name': 'Rahul',
                        'last_name': 'Kumar',
                        'bio': 'Expert in North Indian and Mughlai cuisine with 10 years of experience',
                        'cuisine_specialties': 'North Indian, Mughlai, Chinese',
                        'experience_years': 10,
                        'rating': 5.0,
                        'delivery_radius': 5,
                        'profile_picture': None
                    }
                ]
            }
        )
    }
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
