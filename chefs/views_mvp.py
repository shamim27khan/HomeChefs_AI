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
from .models import DailyMeal, ChefProfile, DailyEarning, CustomerReview
from .serializers_mvp import (
    DailyMealSerializer, DailyMealCreateSerializer, ChefProfileSerializer,
    PublicChefSerializer, AdminChefSerializer, TodayMealsSerializer, 
    CustomerReviewSerializer, DailyEarningSerializer
)

# Custom decorator to bypass CSRF for API views
def csrf_exempt_api_view(view_func):
    """Custom decorator to bypass CSRF for DRF API views"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Manually disable CSRF protection for this view
        request._dont_enforce_csrf_checks = True
        return view_func(request, *args, **kwargs)
    return wrapped_view

# Chef MVP Views
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def chef_daily_meals(request):
    """Chef can view and manage their daily meals"""
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    print(f"CSRF checks enforced: {getattr(request, '_dont_enforce_csrf_checks', False)}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user}")
    print(f"User role: {getattr(request.user, 'role', 'No role')}")
    
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        # Get today's meals or specific date
        target_date = request.GET.get('date', date.today())
        meals = DailyMeal.objects.filter(chef=request.user, date=target_date)
        serializer = DailyMealSerializer(meals, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        print(f"POST request - Data: {request.data}")
        # Create new daily meal
        serializer = DailyMealCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                meal = serializer.save(chef=request.user)
                print(f"Meal saved successfully!")
                print(f"Saved meal: {meal.main_dish}")
                print(f"Saved meal date: {meal.date}")
                print(f"Saved meal chef: {meal.chef}")
                print(f"Saved meal chef username: {meal.chef.username}")
                print(f"Current user: {request.user}")
                print(f"Current user username: {request.user.username}")
                print(f"Today's date: {date.today()}")
                return Response(DailyMealSerializer(meal).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Error creating meal: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print(f"Serializer errors: {serializer.errors}")
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
        # Only allow deletion if no orders placed
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
        # Create profile if it doesn't exist - provide default values for required fields
        profile = ChefProfile.objects.create(
            user=request.user,
            phone_number=f"TEMP{request.user.id}{request.user.id}",  # Temporary unique phone
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

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_earnings(request):
    """Chef can view their daily earnings"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get date range
    start_date = request.GET.get('start_date', date.today() - timedelta(days=30))
    end_date = request.GET.get('end_date', date.today())
    
    earnings = DailyEarning.objects.filter(
        chef=request.user,
        date__range=[start_date, end_date]
    ).order_by('-date')
    
    serializer = DailyEarningSerializer(earnings, many=True)
    
    # Calculate totals
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

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_orders(request):
    """Chef can view their orders"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get date filter
    target_date = request.GET.get('date', date.today())
    
    orders = DailyMealOrder.objects.filter(
        daily_meal__chef=request.user,
        daily_meal__date=target_date
    ).order_by('-order_time')
    
    from orders.serializers_mvp import ChefOrderListSerializer
    serializer = ChefOrderListSerializer(orders, many=True)
    return Response(serializer.data)

# Customer MVP Views
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_chefs(request):
    """Customers can browse nearby chefs with comprehensive filters"""
    # Get all filters
    area = request.GET.get('area', '')
    city = request.GET.get('city', '')
    cuisine = request.GET.get('cuisine', '')
    search = request.GET.get('search', '')
    radius = request.GET.get('radius', '')
    meal_type = request.GET.get('meal_type', '')
    dietary = request.GET.get('dietary', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    print(f"Public chefs search - area: '{area}', search: '{search}'")
    
    chefs = User.objects.filter(role='chef')
    print(f"Total chefs found: {chefs.count()}")
    
    # Apply location filters
    if area:
        # Search in both area and chef name
        chefs = chefs.filter(
            Q(chefprofile__area__icontains=area) |
            Q(username__icontains=area) |
            Q(first_name__icontains=area) |
            Q(last_name__icontains=area)
        )
        print(f"After area filter '{area}': {chefs.count()} chefs")
    if city:
        chefs = chefs.filter(chefprofile__city__icontains=city)
        print(f"After city filter '{city}': {chefs.count()} chefs")
    
    # Apply cuisine filter (can be multiple cuisines)
    if cuisine:
        cuisine_list = [c.strip() for c in cuisine.split(',') if c.strip()]
        cuisine_filter = Q()
        for c in cuisine_list:
            cuisine_filter |= Q(chefprofile__cuisine_specialties__icontains=c)
        chefs = chefs.filter(cuisine_filter)
        print(f"After cuisine filter '{cuisine}': {chefs.count()} chefs")
    
    # Apply general search (search in username, name and cuisine specialties)
    if search:
        print(f"Searching for: '{search}'")
        
        # Split search into words for better matching
        search_words = search.lower().split()
        
        # Debug each chef's data
        for chef in chefs:
            username_match = any(word in chef.username.lower() for word in search_words)
            first_name_match = chef.first_name and any(word in chef.first_name.lower() for word in search_words)
            last_name_match = chef.last_name and any(word in chef.last_name.lower() for word in search_words)
            full_name_match = chef.first_name and chef.last_name and search.lower() in f"{chef.first_name} {chef.last_name}".lower()
            print(f"Chef {chef.username}: username={username_match}, first_name={first_name_match}, last_name={last_name_match}, full_name={full_name_match}")
            print(f"  -> username='{chef.username}', first_name='{chef.first_name}', last_name='{chef.last_name}'")
        
        # Build Q filter for multi-word search
        search_filter = Q()
        for word in search_words:
            search_filter |= (
                Q(username__icontains=word) |
                Q(first_name__icontains=word) |
                Q(last_name__icontains=word) |
                Q(chefprofile__cuisine_specialties__icontains=word)
            )
        
        chefs = chefs.filter(search_filter)
        print(f"After search filter '{search}': {chefs.count()} chefs")
    
    # Apply meal type filter (if we had meal types in chef profile)
    # For now, this would filter based on available meals
    if meal_type:
        meal_type_list = [m.strip() for m in meal_type.split(',') if m.strip()]
        # This would need to be implemented based on available meals
        # For now, we'll skip this as it requires meal data
        pass
    
    # Apply dietary preference filter
    if dietary:
        dietary_list = [d.strip() for d in dietary.split(',') if d.strip()]
        dietary_filter = Q()
        for d in dietary_list:
            if d.lower() == 'vegetarian':
                dietary_filter |= Q(chefprofile__cuisine_specialties__icontains='Vegetarian')
            elif d.lower() == 'non-vegetarian':
                dietary_filter |= Q(chefprofile__cuisine_specialties__icontains='Non-Vegetarian')
        chefs = chefs.filter(dietary_filter)
    
    # Apply price range filter (if we had price data)
    # This would need to be implemented based on meal prices
    # For now, we'll skip this as it requires meal data
    if min_price or max_price:
        # This would filter based on meal prices
        # For now, we'll skip this as it requires meal data
        pass
    
    # Apply radius filter (if we had location coordinates)
    if radius:
        # This would require geolocation data
        # For now, we'll just log it
        print(f"Radius filter requested: {radius} km")
    
    # Only show verified chefs (for MVP, show all chefs)
    # chefs = chefs.filter(chefprofile__is_verified=True)
    
    # For MVP, show all chefs who have a profile
    chefs = chefs.filter(chefprofile__isnull=False)
    
    # Debug: Create profiles for chefs who don't have them
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
            print(f"Created profile for chef: {chef.username}")
    
    print(f"After profile filter: {chefs.count()} chefs")
    
    # Debug: Show final chef list
    for chef in chefs:
        print(f"Final chef: {chef.username} - {chef.first_name} {chef.last_name}")
    
    serializer = PublicChefSerializer(chefs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def today_meals(request):
    """Customers can browse today's available meals"""
    from datetime import date
    today = date.today()
    
    print(f"=== TODAY'S MEALS DEBUG ===")
    print(f"Today's date: {today}")
    
    # Get filters
    area = request.GET.get('area', '')
    meal_type = request.GET.get('meal_type', '')
    
    meals = DailyMeal.objects.filter(
        date=today,
        is_active=True
    ).select_related('chef', 'chef__chefprofile')
    
    print(f"Initial query: date={today}, is_active=True")
    print(f"Found {meals.count()} meals")
    
    # Filter out meals that are past their cutoff time
    orderable_meals = [meal for meal in meals if meal.is_orderable]
    print(f"After cutoff time filter: {len(orderable_meals)} orderable meals")
    
    # Convert back to queryset for further filtering
    meal_ids = [meal.id for meal in orderable_meals]
    meals = DailyMeal.objects.filter(id__in=meal_ids).select_related('chef', 'chef__chefprofile')
    
    # Apply filters
    if area:
        meals = meals.filter(chef__chefprofile__area__icontains=area)
        print(f"Filtered by area: {area}")
    if meal_type:
        meals = meals.filter(meal_type=meal_type)
        print(f"Filtered by meal_type: {meal_type}")
    
    print(f"Final meal count: {meals.count()}")

    serializer = TodayMealsSerializer(meals, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def customer_orders(request):
    """Customers can view their orders"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    orders = DailyMealOrder.objects.filter(
        customer=request.user
    ).order_by('-order_time')
    
    from orders.serializers_mvp import CustomerOrderListSerializer
    serializer = CustomerOrderListSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def customer_review(request, order_id):
    """Customers can rate completed orders"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    order = get_object_or_404(DailyMealOrder, id=order_id, customer=request.user)
    
    # Only allow rating for completed orders
    if order.order_status not in ['ready', 'delivered']:
        return Response(
            {'error': 'Can only rate completed orders'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already rated
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

# Admin MVP Views
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAdminUser])
def admin_chef_verification(request):
    """Admin can verify chefs"""
    if request.method == 'GET':
        # Get pending verifications
        pending_chefs = ChefProfile.objects.filter(is_verified=False)
        chefs = User.objects.filter(
            role='chef',
            chefprofile__in=pending_chefs
        )
        serializer = AdminChefSerializer(chefs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Verify a chef
        chef_id = request.data.get('chef_id')
        chef = get_object_or_404(User, id=chef_id, role='chef')
        
        chef.chefprofile.is_verified = True
        chef.chefprofile.verification_date = timezone.now()
        chef.chefprofile.save()
        
        return Response({'message': f'Chef {chef.username} verified successfully'})

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_chefs(request):
    """Admin can view complete chef information"""
    chefs = User.objects.filter(role='chef').order_by('-date_joined')
    serializer = AdminChefSerializer(chefs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_delivery_partners(request):
    """Admin can view delivery partner information"""
    from delivery.models import DeliveryPartner
    
    delivery_partners = DeliveryPartner.objects.select_related('user').all().order_by('-created_at')
    
    # Manual serialization since delivery app doesn't have serializers
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
            'completed_orders': partner.total_deliveries,  # Alias for compatibility
            'average_rating': partner.average_rating,
            'completion_rate': partner.completion_rate,
            'service_areas': partner.service_areas,
            'max_delivery_distance': partner.max_delivery_distance,
            'created_at': partner.created_at,
        })
    
    return Response(partners_data)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard(request):
    """Admin dashboard with key metrics"""
    from django.db.models import Count, Sum, Q
    from datetime import date
    from orders.models import DailyMealOrder
    from chefs.models import DailyMeal
    
    today = date.today()
    
    # Key metrics
    total_chefs = User.objects.filter(role='chef').count()
    verified_chefs = User.objects.filter(role='chef', chefprofile__is_verified=True).count()
    total_customers = User.objects.filter(role='customer').count()
    total_delivery_partners = User.objects.filter(role='delivery_partner').count()
    verified_delivery_partners = User.objects.filter(
        role='delivery_partner', 
        delivery_partner__verification_status='verified'
    ).count()
    
    # Today's metrics
    today_meals = DailyMeal.objects.filter(date=today).count()
    today_orders = DailyMealOrder.objects.filter(order_time__date=today).count()
    today_revenue = DailyMealOrder.objects.filter(
        order_time__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Platform commission today
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

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def nearby_dishes(request):
    """Find dishes available within 3km radius of user's location"""
    # Get user location from query parameters
    try:
        user_lat = float(request.GET.get('latitude'))
        user_lon = float(request.GET.get('longitude'))
        radius_km = float(request.GET.get('radius', 3.0))  # Default 3km
    except (TypeError, ValueError):
        return Response(
            {'error': 'Valid latitude and longitude are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate radius
    if radius_km > 10:  # Cap at 10km for performance
        radius_km = 10
    
    # Get today's meals with location data
    meals = DailyMeal.objects.filter(
        date=date.today(),
        is_active=True,
        current_orders__lt=F('extra_portions')
    ).select_related('chef', 'chef__chefprofile')
    
    # Filter out meals that are past their cutoff time
    orderable_meals = [meal for meal in meals if meal.is_orderable]
    print(f"Nearby dishes: {len(orderable_meals)} orderable meals from {meals.count()} total meals")
    
    # Convert back to queryset for distance filtering
    meal_ids = [meal.id for meal in orderable_meals]
    meals = DailyMeal.objects.filter(id__in=meal_ids).select_related('chef', 'chef__chefprofile')
    
    # Only from verified chefs (for MVP, show all chefs)
    # meals = meals.filter(chef__chefprofile__is_verified=True)
    
    # Filter by distance if chef has coordinates
    nearby_meals = []
    for meal in meals:
        try:
            chef_lat = float(meal.chef.chefprofile.latitude)
            chef_lon = float(meal.chef.chefprofile.longitude)
            
            # Calculate distance
            distance = calculate_distance(user_lat, user_lon, chef_lat, chef_lon)
            
            if distance <= radius_km:
                meal_data = TodayMealsSerializer(meal).data
                meal_data['distance'] = round(distance, 2)
                nearby_meals.append(meal_data)
                
        except (TypeError, ValueError):
            # Chef doesn't have coordinates, include them without distance
            meal_data = TodayMealsSerializer(meal).data
            meal_data['distance'] = None
            nearby_meals.append(meal_data)
    
    # Sort by distance (put None distances at the end)
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
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_meals(request):
    """Get chef's meals for today"""
    print("my_meals view called!")
    print(f"User: {request.user}")
    print(f"User role: {getattr(request.user, 'role', 'No role')}")
    
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    from datetime import date
    
    today = date.today()
    print(f"Today's date: {today}")
    
    meals = DailyMeal.objects.filter(
        chef=request.user,
        date=today
    ).order_by('meal_type')
    
    print(f"Found {meals.count()} meals for today")
    for meal in meals:
        print(f"Meal: {meal.main_dish} - {meal.meal_type} - {meal.date}")
    
    serializer = TodayMealsSerializer(meals, many=True)
    print(f"Serialized data: {serializer.data}")
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_meal_status(request, meal_id):
    """Toggle meal active/inactive status"""
    try:
        from .models import DailyMeal
        
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

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_meal_detail(request, meal_id):
    """Get detailed meal information for editing"""
    try:
        from .models import DailyMeal
        from .serializers_mvp import DailyMealSerializer
        
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

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_meal(request, meal_id):
    """Update meal details"""
    try:
        from .models import DailyMeal
        from .serializers_mvp import DailyMealSerializer
        
        meal = DailyMeal.objects.get(id=meal_id, chef=request.user)
        
        # Get update data from request
        update_data = request.data
        
        # Update allowed fields
        allowed_fields = [
            'main_dish', 'side_dish', 'additional_items',
            'extra_portions', 'price_per_portion', 'order_cutoff_time',
            'pickup_available', 'delivery_available', 'delivery_radius'
        ]
        
        for field in allowed_fields:
            if field in update_data:
                setattr(meal, field, update_data[field])
        
        meal.save()
        
        # Return updated meal data
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

