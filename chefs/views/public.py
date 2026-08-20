from .common import *
from django.core.paginator import Paginator

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
    operation_description="Rate a daily meal (customer endpoint).",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['rating'],
        properties={
            'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rating from 1 to 5', minimum=1, maximum=5),
            'comment': openapi.Schema(type=openapi.TYPE_STRING, description='Optional comment about the meal')
        }
    )
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
    
    chefs = chefs.filter(chefprofile__is_verified=True)

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
    
    page = request.GET.get('page')
    if page is not None:
        try:
            page = int(page)
        except ValueError:
            page = 1
        page_size = int(request.GET.get('page_size', 12))

        paginator = Paginator(chefs, page_size)
        page_obj = paginator.get_page(page)
        serializer = PublicChefSerializer(page_obj, many=True)

        def build_page_url(page_num):
            params = request.GET.copy()
            params['page'] = page_num
            base = request.build_absolute_uri(request.path)
            return f"{base}?{params.urlencode()}"

        return Response({
            'count': paginator.count,
            'next': build_page_url(page_obj.next_page_number()) if page_obj.has_next() else None,
            'previous': build_page_url(page_obj.previous_page_number()) if page_obj.has_previous() else None,
            'results': serializer.data
        })

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
    method='post',
    tags=['Chefs'],
    operation_description="Customers can rate completed orders.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['rating'],
        properties={
            'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rating from 1 to 5', minimum=1, maximum=5),
            'feedback': openapi.Schema(type=openapi.TYPE_STRING, description='Optional feedback about the order')
        }
    )
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
