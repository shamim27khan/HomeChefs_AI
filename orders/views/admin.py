from .common import *

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