from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Sum, Avg, Count
from datetime import timedelta, date
from .models import Order, OrderItem, Delivery, DailyMealOrder, CustomerRating
from .serializers import OrderSerializer, OrderCreateSerializer, DeliverySerializer
from .serializers_mvp import (
    DailyMealOrderSerializer, DailyMealOrderCreateSerializer,
    CustomerRatingSerializer, OrderStatusUpdateSerializer,
    CustomerOrderListSerializer, ChefOrderListSerializer
)
from chefs.models import FoodItem, DailyMeal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    tags=['Orders'],
    operation_description="Place a new food order. Only customers can place orders.",
    request_body=OrderCreateSerializer,
    responses={
        201: openapi.Response(
            description='Order placed successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'order_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'customer': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'chef': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'items': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    ),
                    'total_amount': openapi.Schema(type=openapi.TYPE_STRING),
                    'order_status': openapi.Schema(type=openapi.TYPE_STRING),
                    'payment_status': openapi.Schema(type=openapi.TYPE_STRING),
                    'estimated_delivery_time': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'id': 1,
                    'order_id': 'ORD001',
                    'customer': 1,
                    'chef': 2,
                    'items': [
                        {
                            'id': 1,
                            'food_item': 1,
                            'quantity': 2,
                            'price_at_time': '250.00',
                            'subtotal': '500.00'
                        }
                    ],
                    'total_amount': '500.00',
                    'order_status': 'pending',
                    'payment_status': 'pending',
                    'estimated_delivery_time': '2024-01-15T11:15:00Z',
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
                    'chef': ['This field is required.'],
                    'items': ['This field is required.']
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only customers can place orders',
            examples={
                'application/json': {
                    'error': 'Only customers can place orders'
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def orders(request):
    if request.user.role not in ['customer', 'chef']:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        if request.user.role == 'customer':
            orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        else:  # chef
            orders = Order.objects.filter(chef=request.user).order_by('-created_at')
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'customer':
            return Response({'error': 'Only customers can place orders'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            
            # Set estimated delivery time (e.g., 45 minutes from now)
            order.estimated_delivery_time = timezone.now() + timedelta(minutes=45)
            order.save()
            
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    
    # Check permissions
    if request.user.role == 'customer' and order.customer != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'chef' and order.chef != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if request.user.role == 'chef':
            # Chef can update order status
            new_status = request.data.get('order_status')
            if new_status in ['confirmed', 'preparing', 'ready']:
                order.order_status = new_status
                order.save()
                return Response({'message': f'Order status updated to {new_status}'})
            else:
                return Response({'error': 'Invalid status transition'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.user.role == 'customer':
            # Customer can cancel order
            if order.order_status in ['pending', 'confirmed']:
                order.order_status = 'cancelled'
                order.save()
                return Response({'message': 'Order cancelled'})
            else:
                return Response({'error': 'Order cannot be cancelled at this stage'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def delivery_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    
    # Check permissions
    if request.user.role == 'customer' and order.customer != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'chef' and order.chef != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        delivery = order.delivery
    except Delivery.DoesNotExist:
        delivery = None
    
    if request.method == 'GET':
        if delivery:
            serializer = DeliverySerializer(delivery)
            return Response(serializer.data)
        else:
            return Response({'message': 'Delivery not assigned yet'})
    
    elif request.method == 'PUT':
        if request.user.role == 'chef' and order.order_status == 'ready':
            # Chef can mark as out for delivery
            if not delivery:
                delivery = Delivery.objects.create(order=order)
            delivery.status = 'out_for_delivery'
            delivery.pickup_time = timezone.now()
            delivery.save()
            
            # Update order status
            order.order_status = 'out_for_delivery'
            order.save()
            
            return Response({'message': 'Order marked as out for delivery'})
        
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="Get order history with optional filters by status and date."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_history(request):
    if request.user.role not in ['customer', 'chef']:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get query parameters for filtering
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if request.user.role == 'customer':
        orders = Order.objects.filter(customer=request.user)
    else:  # chef
        orders = Order.objects.filter(chef=request.user)
    
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    
    if date_to:
        orders = orders.filter(created_at__lte=date_to)
    
    orders = orders.order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="Get today's orders for the authenticated chef."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chef_orders(request):
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get today's orders
    today = timezone.now().date()
    orders = Order.objects.filter(
        chef=request.user,
        created_at__date=today
    ).order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="Get all orders for the authenticated customer."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def customer_orders(request):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get customer's orders
    orders = Order.objects.filter(
        customer=request.user
    ).order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

# Daily Meal Order Views (formerly MVP)
@swagger_auto_schema(
    method='post',
    tags=['Orders'],
    operation_description="Create a new daily meal order. Only customers can place orders.",
    request_body=DailyMealOrderCreateSerializer
)
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

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="View daily meal order details."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_meal_order_detail(request, order_id):
    """View daily meal order details"""
    order = get_object_or_404(DailyMealOrder, id=order_id)
    
    if request.user.role == 'customer' and order.customer != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'chef' and order.daily_meal.chef != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DailyMealOrderSerializer(order)
    return Response(serializer.data)

@swagger_auto_schema(
    method='put',
    tags=['Orders'],
    operation_description="Update daily meal order status (chefs only)."
)
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_daily_meal_order_status(request, order_id):
    """Update daily meal order status (chefs only)"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can update order status'}, status=status.HTTP_403_FORBIDDEN)
    
    order = get_object_or_404(DailyMealOrder, id=order_id, daily_meal__chef=request.user)
    
    serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        updated_order = serializer.save()
        
        if updated_order.order_status == 'confirmed':
            updated_order.estimated_ready_time = timezone.now() + timedelta(minutes=45)
            updated_order.save()
        
        return Response(DailyMealOrderSerializer(updated_order).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='put',
    tags=['Orders'],
    operation_description="Cancel daily meal order (customers only)."
)
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def cancel_daily_meal_order(request, order_id):
    """Cancel daily meal order (customers only)"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can cancel orders'}, status=status.HTTP_403_FORBIDDEN)
    
    order = get_object_or_404(DailyMealOrder, id=order_id, customer=request.user)
    
    if order.order_status not in ['pending']:
        return Response(
            {'error': 'Cannot cancel order after confirmation'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    order.daily_meal.current_orders -= order.portions
    order.daily_meal.save()
    
    order.order_status = 'cancelled'
    order.save()
    
    return Response({'message': 'Order cancelled successfully'})

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="View customer's daily meal orders with filters."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_meal_customer_orders(request):
    """View customer's daily meal orders"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    orders = DailyMealOrder.objects.filter(customer=request.user)
    
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    if date_from:
        orders = orders.filter(order_time__date__gte=date_from)
    if date_to:
        orders = orders.filter(order_time__date__lte=date_to)
    
    orders = orders.order_by('-order_time')
    serializer = CustomerOrderListSerializer(orders, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="Customer daily meal order history with statistics."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_meal_customer_order_history(request):
    """Customer daily meal order history with statistics"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    orders = DailyMealOrder.objects.filter(customer=request.user)
    
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    completed_orders = orders.filter(order_status='ready').count()
    
    favorite_meals = orders.values('daily_meal__meal_type').annotate(
        count=Count('id')
    ).order_by('-count')[:3]
    
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

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="View chef's daily meal orders with filters."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_meal_chef_orders(request):
    """View chef's daily meal orders"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    date_filter = request.GET.get('date', '')
    status_filter = request.GET.get('status', '')
    
    orders = DailyMealOrder.objects.filter(daily_meal__chef=request.user)
    
    if date_filter:
        orders = orders.filter(daily_meal__date=date_filter)
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    orders = orders.order_by('-order_time')
    serializer = ChefOrderListSerializer(orders, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    tags=['Orders'],
    operation_description="Chef can confirm a pending daily meal order.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'estimated_ready_time': openapi.Schema(type=openapi.TYPE_STRING, description='Estimated ready time in minutes (optional)')
        }
    )
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_daily_meal_order(request, order_id):
    """Chef can confirm a pending daily meal order"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = DailyMealOrder.objects.get(id=order_id, daily_meal__chef=request.user)
        
        if order.order_status != 'pending':
            return Response({'error': 'Only pending orders can be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.order_status = 'confirmed'
        order.save()
        
        return Response({'message': 'Order confirmed successfully', 'order_status': 'confirmed'})
        
    except DailyMealOrder.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="Chef's daily meal dashboard statistics."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_meal_chef_stats(request):
    """Chef's daily meal dashboard statistics"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    today = date.today()
    
    today_orders = DailyMealOrder.objects.filter(
        daily_meal__chef=request.user,
        daily_meal__date=today
    )
    
    today_revenue = today_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    active_meals = DailyMeal.objects.filter(
        chef=request.user,
        date=today,
        is_active=True
    )
    
    avg_rating = 0.0
    
    stats_data = {
        'today_orders': today_orders.count(),
        'today_revenue': float(today_revenue),
        'active_meals': active_meals.count(),
        'average_rating': avg_rating
    }
    
    return Response(stats_data)

@swagger_auto_schema(
    method='post',
    tags=['Orders'],
    operation_description="Mark a daily meal order as delivered.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'delivery_notes': openapi.Schema(type=openapi.TYPE_STRING, description='Optional delivery notes')
        }
    )
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_daily_meal_as_delivered(request, order_id):
    """Mark a daily meal order as delivered"""
    order = get_object_or_404(DailyMealOrder, id=order_id)
    
    if request.user.role == 'chef':
        if order.daily_meal.chef != request.user:
            return Response({'error': 'You can only mark your own orders as delivered'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'customer':
        if order.customer != request.user:
            return Response({'error': 'You can only mark your own orders as delivered'}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({'error': 'Invalid role'}, status=status.HTTP_403_FORBIDDEN)
    
    if order.order_status != 'ready':
        return Response(
            {'error': 'Can only mark ready orders as delivered'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    order.order_status = 'delivered'
    order.save()
    
    return Response({
        'message': 'Order marked as delivered successfully',
        'order_status': order.order_status
    })

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="Chef's daily meal order summary by date."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_meal_chef_order_summary(request):
    """Chef's daily meal order summary"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    target_date = request.GET.get('date', date.today())
    
    orders = DailyMealOrder.objects.filter(
        daily_meal__chef=request.user,
        daily_meal__date=target_date
    )
    
    total_orders = orders.count()
    total_earnings = orders.aggregate(total=Sum('chef_earnings'))['total'] or 0
    pending_orders = orders.filter(order_status='pending').count()
    confirmed_orders = orders.filter(order_status='confirmed').count()
    ready_orders = orders.filter(order_status='ready').count()
    
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

@swagger_auto_schema(
    method='post',
    tags=['Orders'],
    operation_description="Rate a completed daily meal order (customers only).",
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
def rate_daily_meal_order(request, order_id):
    """Rate a completed daily meal order"""
    if request.user.role != 'customer':
        return Response({
            'error': 'Only customers can rate orders',
            'code': 'PERMISSION_DENIED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = DailyMealOrder.objects.get(id=order_id, customer=request.user)
    except DailyMealOrder.DoesNotExist:
        return Response({
            'error': 'Order not found',
            'code': 'ORDER_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if order.order_status not in ['delivered']:
        return Response({
            'error': f'Can only rate delivered orders. Current status: {order.order_status}',
            'code': 'INVALID_ORDER_STATUS'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if hasattr(order, 'rating'):
        return Response({
            'error': 'Order already rated',
            'code': 'ALREADY_RATED'
        }, status=status.HTTP_400_BAD_REQUEST)
    
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

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="View customer's daily meal ratings."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_meal_customer_ratings(request):
    """View customer's daily meal ratings"""
    if request.user.role != 'customer':
        return Response({'error': 'Only customers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    ratings = CustomerRating.objects.filter(customer=request.user).order_by('-created_at')
    serializer = CustomerRatingSerializer(ratings, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="View chef's daily meal ratings."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_meal_chef_ratings(request):
    """View chef's daily meal ratings"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    ratings = CustomerRating.objects.filter(
        daily_order__daily_meal__chef=request.user
    ).order_by('-created_at')
    
    serializer = CustomerRatingSerializer(ratings, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="Public endpoint to view a specific chef's daily meal ratings."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_meal_public_chef_ratings(request, chef_id):
    """Public endpoint to view a specific chef's daily meal ratings"""
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

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="Admin can view all daily meal orders for monitoring."
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def daily_meal_admin_orders(request):
    """Admin can view all daily meal orders for monitoring"""
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    status_filter = request.GET.get('status', '')
    
    orders = DailyMealOrder.objects.all()
    
    if date_from:
        orders = orders.filter(order_time__date__gte=date_from)
    if date_to:
        orders = orders.filter(order_time__date__lte=date_to)
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    orders = orders.order_by('-order_time')[:100]
    
    serializer = DailyMealOrderSerializer(orders, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    tags=['Orders'],
    operation_description="Admin daily meal order statistics."
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def daily_meal_admin_order_stats(request):
    """Admin daily meal order statistics"""
    today = date.today()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    today_orders = DailyMealOrder.objects.filter(order_time__date=today).count()
    last_7_days_orders = DailyMealOrder.objects.filter(order_time__date__gte=last_7_days).count()
    last_30_days_orders = DailyMealOrder.objects.filter(order_time__date__gte=last_30_days).count()
    
    today_revenue = DailyMealOrder.objects.filter(
        order_time__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    last_7_days_revenue = DailyMealOrder.objects.filter(
        order_time__date__gte=last_7_days,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    today_commission = DailyMealOrder.objects.filter(
        order_time__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('platform_commission'))['total'] or 0
    
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
