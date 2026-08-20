from .common import *

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
    request_body=FoodItemCreateSerializer,
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
    request_body=FoodScheduleCreateSerializer,
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


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def chef_daily_meals(request):
    """Chef can view and manage their daily meals"""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        target_date = request.GET.get('date')
        if target_date:
            # Parse the date from string if provided
            from datetime import datetime
            try:
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            except ValueError:
                target_date = date.today()
        else:
            target_date = date.today()
        
        print(f"DEBUG: Chef {request.user.username} requesting meals for date: {target_date}")
        meals = DailyMeal.objects.filter(chef=request.user, date=target_date)
        print(f"DEBUG: Found {meals.count()} meals for date {target_date}")
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
        return Response({'success': True, 'meal': serializer.data})
    
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
    operation_description="Toggle meal active/inactive status.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Set meal active status')
        }
    )
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
    method='put',
    tags=['Chefs'],
    operation_description="Update meal details.",
    request_body=DailyMealCreateSerializer
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