from .common import *
from rest_framework.authtoken.models import Token
from datetime import datetime, time, timedelta

@login_required
def delivery_dashboard(request):
    """Delivery partner dashboard"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return JsonResponse({'error': 'Delivery partner profile not found'}, status=404)
    
    # Get active deliveries
    active_deliveries = partner.get_active_deliveries()
    
    # Get pending requests
    pending_requests = DeliveryNotificationSystem.get_partner_notifications(partner)
    
    # Get all ready delivery orders that are not yet assigned
    available_orders = DailyMealOrder.objects.filter(
        delivery_type='delivery',
        order_status='ready',
        delivery_assignment__isnull=True
    ).order_by('-order_time')
    
    # Get today's completed deliveries (local Asia/Kolkata day)
    today = timezone.localdate()
    today_start = timezone.make_aware(datetime.combine(today, time.min))
    today_end = today_start + timedelta(days=1)
    today_completed = partner.deliveries.filter(
        status='delivered',
        actual_delivery_time__gte=today_start,
        actual_delivery_time__lt=today_end
    )
    
    # Get API token for dashboard fetch calls
    token, _ = Token.objects.get_or_create(user=request.user)
    
    context = {
        'partner': partner,
        'active_deliveries': active_deliveries,
        'pending_requests': pending_requests,
        'available_orders': available_orders,
        'today_completed': today_completed,
        'total_earnings': sum(d.partner_earnings for d in today_completed),
        'auth_token': token.key,
    }
    
    return render(request, 'delivery/dashboard.html', context)
