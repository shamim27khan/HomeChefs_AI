from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Sum, Avg

from authentication.models import User
from .models import DailyMealOrder, CustomerRating
from .serializers_mvp import (
    DailyMealOrderSerializer, DailyMealOrderCreateSerializer,
    CustomerRatingSerializer, OrderStatusUpdateSerializer,
    CustomerOrderListSerializer, ChefOrderListSerializer
)
from chefs.models import DailyMeal

# Order Management Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def create_daily_meal_order(request):
    """Create a new daily meal order"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can place orders'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DailyMealOrderCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        order = serializer.save()
        return Response(DailyMealOrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(DailyMealOrder, id=order_id)
    
    # Check permissions
    if request.user.role == 'customer' and order.customer != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'chef' and order.daily_meal.chef != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DailyMealOrderSerializer(order)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status (chefs only)"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can update order status'}, status=status.HTTP_403_FORBIDDEN)
    
    order = get_object_or_404(DailyMealOrder, id=order_id, daily_meal__chef=request.user)
    
    serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        updated_order = serializer.save()
        
        # Auto-set estimated ready time when confirmed
        if updated_order.order_status == 'confirmed':
            from datetime import timedelta
            updated_order.estimated_ready_time = timezone.now() + timedelta(minutes=45)
            updated_order.save()
        
        return Response(DailyMealOrderSerializer(updated_order).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, order_id):
    """Cancel order (customers only)"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can cancel orders'}, status=status.HTTP_403_FORBIDDEN)
    
    order = get_object_or_404(DailyMealOrder, id=order_id, customer=request.user)
    
    # Only allow cancellation before order is confirmed
    if order.order_status not in ['pending']:
        return Response(
            {'error': 'Cannot cancel order after confirmation'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Restore available portions
    order.daily_meal.current_orders -= order.portions
    order.daily_meal.save()
    
    # Update order status
    order.order_status = 'cancelled'
    order.save()
    
    return Response({'message': 'Order cancelled successfully'})

# Customer Order Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def customer_orders(request):
    """View customer's orders"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    orders = DailyMealOrder.objects.filter(customer=request.user)
    
    # Apply filters
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    if date_from:
        orders = orders.filter(order_time__date__gte=date_from)
    if date_to:
        orders = orders.filter(order_time__date__lte=date_to)
    
    orders = orders.order_by('-order_time')
    serializer = CustomerOrderListSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def customer_order_history(request):
    """Customer order history with statistics"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get order statistics
    orders = DailyMealOrder.objects.filter(customer=request.user)
    
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    completed_orders = orders.filter(order_status='ready').count()
    
    # Favorite meal types
    favorite_meals = orders.values('daily_meal__meal_type').annotate(
        count=Count('id')
    ).order_by('-count')[:3]
    
    # Favorite chefs
    favorite_chefs = orders.values('daily_meal__chef__username').annotate(
        count=Count('id')
    ).order_by('-count')[:3]
    
    return Response({
        'statistics': {
            'total_orders': total_orders,
            'total_spent': total_spent,
            'completed_orders': completed_orders,
            'completion_rate': round((completed_orders / total_orders * 100) if total_orders > 0 else 0, 1)
        },
        'favorite_meals': favorite_meals,
        'favorite_chefs': favorite_chefs
    })

# Chef Order Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_orders(request):
    """View chef's orders"""
    print("chef_orders view called!")
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get filter parameters
    date = request.GET.get('date', '')
    status_filter = request.GET.get('status', '')
    
    orders = DailyMealOrder.objects.filter(daily_meal__chef=request.user)
    
    # Apply filters
    if date:
        orders = orders.filter(daily_meal__date=date)
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    orders = orders.order_by('-order_time')
    serializer = ChefOrderListSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_order(request, order_id):
    """Chef can confirm a pending order"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = DailyMealOrder.objects.get(id=order_id, daily_meal__chef=request.user)
        
        if order.order_status != 'pending':
            return Response({'error': 'Only pending orders can be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order status
        order.order_status = 'confirmed'
        order.save()
        
        return Response({'message': 'Order confirmed successfully', 'order_status': 'confirmed'})
        
    except DailyMealOrder.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_stats(request):
    """Chef's dashboard statistics"""
    print("chef_stats view called!")
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.utils import timezone
    from django.db.models import Sum, Avg, Count
    from datetime import date
    
    today = date.today()
    print(f"Today's date: {today}")
    
    # Today's orders
    today_orders = DailyMealOrder.objects.filter(
        daily_meal__chef=request.user,
        daily_meal__date=today
    )
    print(f"Today's orders query: chef={request.user.username}, date={today}")
    print(f"Found {today_orders.count()} today's orders")

    for order in today_orders:
        print(f"  Order: {order.id}, amount: {order.total_amount}, status: {order.order_status}")
    
    # Today's revenue
    today_revenue = today_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    print(f"Today's revenue: {today_revenue}")
    
    # Active meals today
    active_meals = DailyMeal.objects.filter(
        chef=request.user,
        date=today,
        is_active=True
    )
    print(f"Active meals query: chef={request.user.username}, date={today}, active=True")
    print(f"Found {active_meals.count()} active meals")
    
    for meal in active_meals:
        print(f"  Meal: {meal.main_dish}, portions: {meal.available_portions}, orders: {meal.current_orders}")
    
    # Average rating - for now, return 0 as rating system not implemented
    avg_rating = 0.0
    
    stats_data = {
        'today_orders': today_orders.count(),
        'today_revenue': float(today_revenue),
        'active_meals': active_meals.count(),
        'average_rating': avg_rating
    }
    
    print(f"Stats data: {stats_data}")
    return Response(stats_data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_as_delivered(request, order_id):
    """Mark an order as delivered (chef or customer)"""
    order = get_object_or_404(DailyMealOrder, id=order_id)
    
    # Check permissions
    if request.user.role == 'chef':
        # Chef can only mark their own orders as delivered
        if order.daily_meal.chef != request.user:
            return Response({'error': 'You can only mark your own orders as delivered'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'customer':
        # Customer can only mark their own orders as delivered
        if order.customer != request.user:
            return Response({'error': 'You can only mark your own orders as delivered'}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({'error': 'Invalid role'}, status=status.HTTP_403_FORBIDDEN)
    
    # Only allow marking ready orders as delivered
    if order.order_status != 'ready':
        return Response(
            {'error': 'Can only mark ready orders as delivered'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update order status
    order.order_status = 'delivered'
    order.save()
    
    return Response({
        'message': 'Order marked as delivered successfully',
        'order_status': order.order_status
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_order_summary(request):
    """Chef's daily order summary"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    from datetime import date
    
    target_date = request.GET.get('date', date.today())
    
    orders = DailyMealOrder.objects.filter(
        daily_meal__chef=request.user,
        daily_meal__date=target_date
    )
    
    # Calculate summary
    total_orders = orders.count()
    total_earnings = orders.aggregate(total=Sum('chef_earnings'))['total'] or 0
    pending_orders = orders.filter(order_status='pending').count()
    confirmed_orders = orders.filter(order_status='confirmed').count()
    ready_orders = orders.filter(order_status='ready').count()
    
    # Delivery breakdown
    pickup_orders = orders.filter(delivery_type='pickup').count()
    delivery_orders = orders.filter(delivery_type='delivery').count()
    
    return Response({
        'date': target_date,
        'summary': {
            'total_orders': total_orders,
            'total_earnings': total_earnings,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'ready_orders': ready_orders
        },
        'delivery_breakdown': {
            'pickup_orders': pickup_orders,
            'delivery_orders': delivery_orders
        }
    })

# Rating and Review Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rate_order(request, order_id):
    """Rate a completed order"""
    # Validate user role
    if request.user.role != 'customer':
        return Response({
            'error': 'Only customers can rate orders',
            'code': 'PERMISSION_DENIED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get and validate order
    try:
        order = DailyMealOrder.objects.get(id=order_id, customer=request.user)
    except DailyMealOrder.DoesNotExist:
        return Response({
            'error': 'Order not found',
            'code': 'ORDER_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Validate order status
    if order.order_status not in ['delivered']:
        return Response({
            'error': f'Can only rate delivered orders. Current status: {order.order_status}',
            'code': 'INVALID_ORDER_STATUS'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if already rated
    if hasattr(order, 'rating'):
        return Response({
            'error': 'Order already rated',
            'code': 'ALREADY_RATED'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate and save rating
    serializer = CustomerRatingSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response({
            'error': 'Invalid rating data',
            'code': 'VALIDATION_ERROR',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        rating = serializer.save(daily_order=order, customer=request.user)
        return Response(CustomerRatingSerializer(rating).data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            'error': 'Failed to save rating',
            'code': 'SAVE_ERROR',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def customer_ratings(request):
    """View customer's ratings"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    ratings = CustomerRating.objects.filter(customer=request.user).order_by('-created_at')
    serializer = CustomerRatingSerializer(ratings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_ratings(request):
    """View chef's ratings"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    ratings = CustomerRating.objects.filter(
        daily_order__daily_meal__chef=request.user
    ).order_by('-created_at')
    
    serializer = CustomerRatingSerializer(ratings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def public_chef_ratings(request, chef_id):
    """Public endpoint to view a specific chef's ratings"""
    try:
        from authentication.models import User
        chef = User.objects.get(id=chef_id, role='chef')
    except User.DoesNotExist:
        return Response({'error': 'Chef not found'}, status=status.HTTP_404_NOT_FOUND)
    
    ratings = CustomerRating.objects.filter(
        daily_order__daily_meal__chef=chef
    ).order_by('-created_at')
    
    serializer = CustomerRatingSerializer(ratings, many=True)
    return Response(serializer.data)

# Admin Views
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_orders(request):
    """Admin can view all orders for monitoring"""
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    status_filter = request.GET.get('status', '')
    
    orders = DailyMealOrder.objects.all()
    
    # Apply filters
    if date_from:
        orders = orders.filter(order_time__date__gte=date_from)
    if date_to:
        orders = orders.filter(order_time__date__lte=date_to)
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    orders = orders.order_by('-order_time')[:100]  # Limit to 100 most recent
    
    serializer = DailyMealOrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_order_stats(request):
    """Admin order statistics"""
    from datetime import date, timedelta
    
    today = date.today()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # Order counts
    today_orders = DailyMealOrder.objects.filter(order_time__date=today).count()
    last_7_days_orders = DailyMealOrder.objects.filter(order_time__date__gte=last_7_days).count()
    last_30_days_orders = DailyMealOrder.objects.filter(order_time__date__gte=last_30_days).count()
    
    # Revenue
    today_revenue = DailyMealOrder.objects.filter(
        order_time__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    last_7_days_revenue = DailyMealOrder.objects.filter(
        order_time__date__gte=last_7_days,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Platform commission
    today_commission = DailyMealOrder.objects.filter(
        order_time__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('platform_commission'))['total'] or 0
    
    # Order status breakdown
    status_breakdown = DailyMealOrder.objects.filter(
        order_time__date__gte=last_7_days
    ).values('order_status').annotate(count=Count('id'))
    
    return Response({
        'order_counts': {
            'today': today_orders,
            'last_7_days': last_7_days_orders,
            'last_30_days': last_30_days_orders
        },
        'revenue': {
            'today': today_revenue,
            'last_7_days': last_7_days_revenue
        },
        'platform_commission': {
            'today': today_commission
        },
        'status_breakdown': list(status_breakdown)
    })
