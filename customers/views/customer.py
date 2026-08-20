from .common import *

@swagger_auto_schema(
    method='post',
    tags=['Customers'],
    operation_description="Add a chef to customer's favorites list. Only customers can access this endpoint.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['chef_id'],
        properties={
            'chef_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the chef to add to favorites')
        }
    ),
    responses={
        201: openapi.Response(
            description='Chef added to favorites successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'message': 'Chef added to favorites'
                }
            }
        ),
        200: openapi.Response(
            description='Chef already in favorites',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'message': 'Chef already in favorites'
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only customers can access this endpoint',
            examples={
                'application/json': {
                    'error': 'Only customers can access this endpoint'
                }
            }
        ),
        404: openapi.Response(
            description='Chef not found or not verified',
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
def favorite_chefs(request):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        favorites = FavoriteChef.objects.filter(customer=request.user)
        serializer = FavoriteChefSerializer(favorites, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        chef_id = request.data.get('chef_id')
        chef = get_object_or_404(ChefProfile, user__id=chef_id, is_verified=True)
        
        favorite, created = FavoriteChef.objects.get_or_create(
            customer=request.user,
            chef=chef.user
        )
        
        if created:
            return Response({'message': 'Chef added to favorites'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Chef already in favorites'}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='delete',
    tags=['Customers'],
    operation_description="Remove a chef from customer's favorites list."
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_favorite_chef(request, chef_id):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        favorite = FavoriteChef.objects.get(customer=request.user, chef__id=chef_id)
        favorite.delete()
        return Response({'message': 'Chef removed from favorites'})
    except FavoriteChef.DoesNotExist:
        return Response({'error': 'Chef not in favorites'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='post',
    tags=['Customers'],
    operation_description="Add a food item to customer's favorites list. Only customers can access this endpoint.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['food_item_id'],
        properties={
            'food_item_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the food item to add to favorites')
        }
    ),
    responses={
        201: openapi.Response(
            description='Food item added to favorites successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'message': 'Food item added to favorites'
                }
            }
        ),
        200: openapi.Response(
            description='Food item already in favorites',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'message': 'Food item already in favorites'
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only customers can access this endpoint',
            examples={
                'application/json': {
                    'error': 'Only customers can access this endpoint'
                }
            }
        ),
        404: openapi.Response(
            description='Food item not found or not available',
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
def favorite_foods(request):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        favorites = FavoriteFood.objects.filter(customer=request.user)
        serializer = FavoriteFoodSerializer(favorites, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        food_id = request.data.get('food_item_id')
        food_item = get_object_or_404(FoodItem, id=food_id, is_available=True)
        
        favorite, created = FavoriteFood.objects.get_or_create(
            customer=request.user,
            food_item=food_item
        )
        
        if created:
            return Response({'message': 'Food item added to favorites'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Food item already in favorites'}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='delete',
    tags=['Customers'],
    operation_description="Remove a food item from customer's favorites list."
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_favorite_food(request, food_id):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        favorite = FavoriteFood.objects.get(customer=request.user, food_item__id=food_id)
        favorite.delete()
        return Response({'message': 'Food item removed from favorites'})
    except FavoriteFood.DoesNotExist:
        return Response({'error': 'Food item not in favorites'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='post',
    tags=['Customers'],
    operation_description="Create a food review. Only customers can access this endpoint.",
    request_body=FoodReviewCreateSerializer,
    responses={
        201: openapi.Response(
            description='Food review created successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'food_item': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'rating': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'comment': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'id': 1,
                    'customer': 1,
                    'food_item': 1,
                    'rating': 5,
                    'comment': 'Amazing butter chicken! Perfect blend of spices and tender meat.',
                    'created_at': '2024-01-15T10:30:00Z'
                }
            }
        ),
        400: openapi.Response(
            description='Bad request - validation errors or already reviewed',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'error': 'You have already reviewed this food item'
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only customers can access this endpoint',
            examples={
                'application/json': {
                    'error': 'Only customers can access this endpoint'
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def food_reviews(request):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        reviews = FoodReview.objects.filter(customer=request.user)
        serializer = FoodReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = FoodReviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            food_item = serializer.validated_data['food_item']
            
            # Check if customer has ordered this food item (you might want to add this validation)
            # For now, we'll allow any review
            
            review, created = FoodReview.objects.get_or_create(
                customer=request.user,
                food_item=food_item,
                defaults=serializer.validated_data
            )
            
            if created:
                return Response(FoodReviewSerializer(review).data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'You have already reviewed this food item'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    tags=['Customers'],
    operation_description="Create a new delivery address. Only customers can access this endpoint.",
    request_body=CustomerAddressSerializer,
    responses={
        201: openapi.Response(
            description='Address created successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'address_line1': openapi.Schema(type=openapi.TYPE_STRING),
                    'address_line2': openapi.Schema(type=openapi.TYPE_STRING),
                    'city': openapi.Schema(type=openapi.TYPE_STRING),
                    'state': openapi.Schema(type=openapi.TYPE_STRING),
                    'postal_code': openapi.Schema(type=openapi.TYPE_STRING),
                    'landmark': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_default': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'id': 1,
                    'customer': 1,
                    'address_line1': '123 Main Street, Apartment 4B',
                    'address_line2': 'Near Central Park',
                    'city': 'Mumbai',
                    'state': 'Maharashtra',
                    'postal_code': '400001',
                    'landmark': 'Opposite City Mall',
                    'is_default': True,
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
                    'city': ['This field is required.'],
                    'postal_code': ['This field is required.']
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only customers can access this endpoint',
            examples={
                'application/json': {
                    'error': 'Only customers can access this endpoint'
                }
            }
        )
    }
)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def addresses(request):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        addresses = CustomerAddress.objects.filter(customer=request.user)
        serializer = CustomerAddressSerializer(addresses, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CustomerAddressSerializer(data=request.data)
        if serializer.is_valid():
            # If this is set as default, unset other default addresses
            if serializer.validated_data.get('is_default', False):
                CustomerAddress.objects.filter(customer=request.user, is_default=True).update(is_default=False)
            
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        address_id = request.data.get('address_id')
        address = get_object_or_404(CustomerAddress, id=address_id, customer=request.user)
        
        serializer = CustomerAddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            # If this is set as default, unset other default addresses
            if serializer.validated_data.get('is_default', False):
                CustomerAddress.objects.filter(customer=request.user, is_default=True).update(is_default=False)
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        address_id = request.data.get('address_id')
        address = get_object_or_404(CustomerAddress, id=address_id, customer=request.user)
        address.delete()
        return Response({'message': 'Address deleted successfully'})


@swagger_auto_schema(
    method='get',
    tags=['Customers'],
    operation_description="Get customer's search history."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_history(request):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    history = SearchHistory.objects.filter(customer=request.user).order_by('-searched_at')[:20]
    serializer = SearchHistorySerializer(history, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    tags=['Customers'],
    operation_description="Search for verified home chefs by name, username, or cuisine specialties."
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_chefs(request):
    query = request.GET.get('q', '')
    cuisine = request.GET.get('cuisine', '')
    
    chefs = ChefProfile.objects.filter(is_verified=True).select_related('user')
    
    if query:
        chefs = chefs.filter(
            models.Q(user__username__icontains=query) |
            models.Q(user__first_name__icontains=query) |
            models.Q(user__last_name__icontains=query) |
            models.Q(cuisine_specialties__icontains=query)
        )
    
    if cuisine:
        chefs = chefs.filter(cuisine_specialties__icontains=cuisine)
    
    chef_data = []
    for chef_profile in chefs:
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
    tags=['Customers'],
    operation_description="Search for available food items with advanced filtering."
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_food(request):
    query = request.GET.get('q', '')
    cuisine = request.GET.get('cuisine', '')
    meal_type = request.GET.get('meal_type', '')
    is_vegetarian = request.GET.get('vegetarian', '')
    
    food_items = FoodItem.objects.filter(is_available=True).select_related('chef')
    
    if query:
        food_items = food_items.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(cuisine_type__icontains=query)
        )
    
    if cuisine:
        food_items = food_items.filter(cuisine_type__icontains=cuisine)
    
    if meal_type:
        food_items = food_items.filter(meal_type=meal_type)
    
    if is_vegetarian == 'true':
        food_items = food_items.filter(is_vegetarian=True)
    elif is_vegetarian == 'false':
        food_items = food_items.filter(is_vegetarian=False)
    
    serializer = FoodItemSerializer(food_items, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    tags=['Customers'],
    operation_description="Get ratings for the authenticated customer."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_customer_ratings(request):
    """Get ratings for the authenticated customer"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access their ratings'}, status=status.HTTP_403_FORBIDDEN)
    
    ratings = CustomerRating.objects.filter(customer=request.user).select_related('chef', 'order')
    ratings_data = []
    
    for rating in ratings:
        ratings_data.append({
            'id': rating.id,
            'chef': {
                'id': rating.chef.id,
                'username': rating.chef.username,
                'first_name': rating.chef.first_name,
                'last_name': rating.chef.last_name
            },
            'order_id': rating.order.order_id,
            'rating': rating.rating,
            'feedback': rating.feedback,
            'created_at': rating.created_at
        })
    
    return Response(ratings_data)