from .common import *

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
    
    # Analytics request (period in days)
    period = request.GET.get('period')
    if period:
        try:
            period_days = max(1, int(period))
        except (ValueError, TypeError):
            period_days = 30
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days - 1)
        analytics_orders = DailyMealOrder.objects.filter(
            daily_meal__chef=request.user,
            order_time__date__range=[start_date, end_date]
        )
        total_revenue = analytics_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = analytics_orders.count()
        unique_customers = analytics_orders.values('customer').distinct().count()
        avg_order_value = float(total_revenue) / total_orders if total_orders else 0
        day_orders = {}
        day_revenue = {}
        for order in analytics_orders.values('order_time', 'total_amount'):
            d = order['order_time'].date()
            day_orders[d] = day_orders.get(d, 0) + 1
            day_revenue[d] = day_revenue.get(d, 0) + float(order['total_amount'] or 0)
        daily_data = []
        for i in range(period_days - 1, -1, -1):
            d = end_date - timedelta(days=i)
            daily_data.append({
                'date': d.isoformat(),
                'orders': day_orders.get(d, 0),
                'revenue': round(day_revenue.get(d, 0), 2)
            })
        return Response({
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'avg_order_value': round(avg_order_value, 2),
            'unique_customers': unique_customers,
            'period_days': period_days,
            'daily_data': daily_data
        })
    
    date_param = request.GET.get('date', '')
    try:
        target_date = date.fromisoformat(date_param) if date_param else timezone.now().date()
    except (ValueError, TypeError):
        target_date = timezone.now().date()
    
    today_orders = DailyMealOrder.objects.filter(
        daily_meal__chef=request.user,
        order_time__date=target_date
    )
    
    today_revenue = today_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    active_meals = DailyMeal.objects.filter(
        chef=request.user,
        date=target_date,
        is_active=True
    )
    
    avg_rating = CustomerRating.objects.filter(
        daily_order__daily_meal__chef=request.user
    ).aggregate(Avg('rating'))['rating__avg'] or 0.0
    avg_rating = round(float(avg_rating), 1)
    
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
