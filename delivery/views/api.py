from .common import *
from decimal import Decimal

@swagger_auto_schema(
    method='get',
    tags=['Delivery'],
    operation_description="Get pending delivery requests for the authenticated delivery partner."
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_delivery_requests(request):
    """Get pending delivery requests for the partner"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    pending_requests = DeliveryNotificationSystem.get_partner_notifications(partner)
    
    requests_data = []
    for req in pending_requests:
        requests_data.append({
            'id': req.id,
            'order_id': req.order.order_id,
            'customer_name': req.order.customer.username,
            'meal_name': req.order.daily_meal.main_dish,
            'portions': req.order.portions,
            'pickup_address': req.order.daily_meal.chef.chef_profile.kitchen_address,
            'delivery_address': req.order.delivery_address,
            'distance_km': req.distance_km,
            'delivery_fee': req.delivery_fee,
            'estimated_pickup_time': req.estimated_pickup_time,
            'estimated_delivery_time': req.estimated_delivery_time,
            'expires_at': req.expires_at,
        })
    
    return Response(requests_data)


@swagger_auto_schema(
    method='post',
    tags=['Delivery'],
    operation_description="Accept a pending delivery request. Only delivery partners can accept requests.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'estimated_arrival': openapi.Schema(type=openapi.TYPE_STRING, description='Estimated arrival time in minutes (optional)')
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
@require_http_methods(['POST'])
def accept_delivery_request(request, request_id):
    """Accept a delivery request"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    try:
        delivery_request = DeliveryRequest.objects.get(
            id=request_id,
            delivery_partner=partner,
            status='pending'
        )
    except DeliveryRequest.DoesNotExist:
        return Response({'error': 'Delivery request not found or already processed'}, status=404)
    
    if delivery_request.accept_request():
        return Response({
            'message': 'Delivery request accepted successfully',
            'assignment_id': delivery_request.order.delivery_assignment.id
        })
    else:
        return Response({'error': 'Cannot accept this request'}, status=400)


@swagger_auto_schema(
    method='post',
    tags=['Delivery'],
    operation_description="Decline a pending delivery request. Only delivery partners can decline requests.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Reason for declining (optional)')
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
@require_http_methods(['POST'])
def decline_delivery_request(request, request_id):
    """Decline a delivery request"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    try:
        delivery_request = DeliveryRequest.objects.get(
            id=request_id,
            delivery_partner=partner,
            status='pending'
        )
    except DeliveryRequest.DoesNotExist:
        return Response({'error': 'Delivery request not found or already processed'}, status=404)
    
    if delivery_request.decline_request():
        return Response({'message': 'Delivery request declined'})
    else:
        return Response({'error': 'Cannot decline this request'}, status=400)


@swagger_auto_schema(
    method='get',
    tags=['Delivery'],
    operation_description="Get detailed information about a specific delivery assignment."
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_delivery_details(request, assignment_id):
    """Get detailed information about a delivery assignment"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    try:
        delivery = DeliveryAssignment.objects.get(
            id=assignment_id,
            delivery_partner=partner
        )
    except DeliveryAssignment.DoesNotExist:
        return Response({'error': 'Delivery assignment not found'}, status=404)
    
    pickup_details = delivery.get_pickup_location()
    delivery_details = delivery.get_delivery_location()
    
    return Response({
        'assignment_id': delivery.id,
        'order_id': delivery.order.order_id,
        'status': delivery.status,
        'delivery_fee': delivery.delivery_fee,
        'partner_earnings': delivery.partner_earnings,
        'estimated_pickup_time': delivery.estimated_pickup_time,
        'estimated_delivery_time': delivery.estimated_delivery_time,
        'pickup_details': pickup_details,
        'delivery_details': delivery_details,
        'special_instructions': delivery.order.special_instructions,
    })


@swagger_auto_schema(
    method='post',
    tags=['Delivery'],
    operation_description="Update delivery status (picked_up, in_transit, delivered). Only delivery partners can update status.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['status'],
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['picked_up', 'in_transit', 'delivered'], description='New delivery status'),
            'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Optional notes about the status update')
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
@require_http_methods(['POST'])
def update_delivery_status(request, assignment_id):
    """Update delivery status"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    try:
        delivery = DeliveryAssignment.objects.get(
            id=assignment_id,
            delivery_partner=partner
        )
    except DeliveryAssignment.DoesNotExist:
        return Response({'error': 'Delivery assignment not found'}, status=404)
    
    new_status = request.data.get('status')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    notes = request.data.get('notes', '')
    
    if new_status == 'picked_up':
        delivery.mark_picked_up(latitude, longitude)
        message = 'Order marked as picked up'
        
    elif new_status == 'in_transit':
        delivery.mark_in_transit()
        message = 'Order marked as in transit'
        
    elif new_status == 'delivered':
        delivery.mark_delivered(latitude, longitude, notes)
        message = 'Order marked as delivered'
        
    else:
        return Response({'error': 'Invalid status'}, status=400)
    
    # Send notification to customer
    DeliveryNotificationSystem.send_delivery_update_notification(delivery, new_status)
    
    return Response({
        'message': message,
        'status': delivery.status,
        'timestamp': timezone.now()
    })


@swagger_auto_schema(
    method='post',
    tags=['Delivery'],
    operation_description="Update delivery partner's current location for real-time tracking.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['latitude', 'longitude'],
        properties={
            'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='Current latitude coordinate'),
            'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='Current longitude coordinate')
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
@require_http_methods(['POST'])
def update_location(request):
    """Update delivery partner's current location"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    try:
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
    except (TypeError, ValueError):
        return Response({'error': 'Invalid coordinates'}, status=400)
    
    if DeliveryLocationTracker.update_partner_location(partner.id, latitude, longitude):
        return Response({'message': 'Location updated successfully'})
    else:
        return Response({'error': 'Failed to update location'}, status=400)


@swagger_auto_schema(
    method='get',
    tags=['Delivery'],
    operation_description="Get delivery partner's delivery history with optional filters."
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_delivery_history(request):
    """Get delivery partner's delivery history"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    # Get query parameters
    status_filter = request.query_params.get('status')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    deliveries = partner.deliveries.all()
    
    # Apply filters
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    
    if date_from:
        deliveries = deliveries.filter(created_at__date__gte=date_from)
    
    if date_to:
        deliveries = deliveries.filter(created_at__date__lte=date_to)
    
    deliveries = deliveries.order_by('-created_at')
    
    deliveries_data = []
    for delivery in deliveries:
        deliveries_data.append({
            'id': delivery.id,
            'order_id': delivery.order.order_id,
            'customer_name': delivery.order.customer.username,
            'meal_name': delivery.order.daily_meal.main_dish,
            'status': delivery.status,
            'delivery_fee': delivery.delivery_fee,
            'partner_earnings': delivery.partner_earnings,
            'created_at': delivery.created_at,
            'actual_pickup_time': delivery.actual_pickup_time,
            'actual_delivery_time': delivery.actual_delivery_time,
        })
    
    return Response(deliveries_data)


@swagger_auto_schema(
    method='get',
    tags=['Delivery'],
    operation_description="Get delivery partner's performance statistics and earnings."
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_partner_stats(request):
    """Get delivery partner's performance statistics"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    # Calculate statistics
    total_deliveries = partner.deliveries.count()
    completed_deliveries = partner.deliveries.filter(status='delivered').count()
    
    # Calculate completion rate
    completion_rate = (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Calculate earnings
    total_earnings = sum(d.partner_earnings for d in partner.deliveries.filter(status='delivered'))
    
    # Get today's stats
    today_deliveries = partner.deliveries.filter(
        created_at__date=timezone.now().date()
    )
    today_earnings = sum(d.partner_earnings for d in today_deliveries.filter(status='delivered'))
    
    # Get this month's stats
    current_month = timezone.now().replace(day=1)
    month_deliveries = partner.deliveries.filter(created_at__gte=current_month)
    month_earnings = sum(d.partner_earnings for d in month_deliveries.filter(status='delivered'))
    
    return Response({
        'total_deliveries': total_deliveries,
        'completed_deliveries': completed_deliveries,
        'completion_rate': round(completion_rate, 2),
        'average_rating': partner.average_rating,
        'total_earnings': total_earnings,
        'today_deliveries': today_deliveries.count(),
        'today_earnings': today_earnings,
        'month_deliveries': month_deliveries.count(),
        'month_earnings': month_earnings,
        'current_status': partner.status,
        'is_available': partner.is_available,
    })


@swagger_auto_schema(
    method='post',
    tags=['Delivery'],
    operation_description="Toggle delivery partner availability to receive new delivery requests.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'is_available': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Set availability status')
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
@require_http_methods(['POST'])
def toggle_availability(request):
    """Toggle delivery partner availability"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    partner.is_available = not partner.is_available
    partner.save()
    
    return Response({
        'message': f'Availability {"enabled" if partner.is_available else "disabled"}',
        'is_available': partner.is_available
    })


@swagger_auto_schema(
    method='post',
    tags=['Delivery'],
    operation_description="Rate a completed delivery. Only customers can rate deliveries.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['rating'],
        properties={
            'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rating from 1 to 5', minimum=1, maximum=5),
            'feedback': openapi.Schema(type=openapi.TYPE_STRING, description='Optional feedback about the delivery')
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
@require_http_methods(['POST'])
def rate_delivery(request, assignment_id):
    """Rate a completed delivery (customer endpoint)"""
    try:
        delivery = DeliveryAssignment.objects.get(
            id=assignment_id,
            status='delivered'
        )
    except DeliveryAssignment.DoesNotExist:
        return Response({'error': 'Delivery assignment not found or not completed'}, status=404)
    
    # Check if user is the customer
    if request.user != delivery.order.customer:
        return Response({'error': 'Only the customer can rate the delivery'}, status=403)
    
    # Check if already rated
    try:
        existing_rating = delivery.rating
        return Response({'error': 'Delivery already rated'}, status=400)
    except DeliveryRating.DoesNotExist:
        pass
    
    rating = request.data.get('rating')
    feedback = request.data.get('feedback', '')
    
    if not rating or int(rating) < 1 or int(rating) > 5:
        return Response({'error': 'Rating must be between 1 and 5'}, status=400)
    
    # Create rating
    DeliveryRating.objects.create(
        delivery_assignment=delivery,
        customer=request.user,
        rating=rating,
        feedback=feedback
    )
    
    return Response({'message': 'Delivery rated successfully'})


@swagger_auto_schema(
    method='get',
    tags=['Delivery'],
    operation_description="List all ready delivery orders available to accept."
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_delivery_orders(request):
    """List all ready delivery orders available for any active partner to accept"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    ready_orders = DailyMealOrder.objects.filter(
        delivery_type='delivery',
        order_status='ready',
        delivery_assignment__isnull=True
    ).order_by('-order_time')
    
    orders_data = []
    for order in ready_orders:
        try:
            pickup_address = order.daily_meal.chef.chef_profile.kitchen_address
        except AttributeError:
            pickup_address = ''
        
        distance = DeliveryNotificationSystem._calculate_distance(pickup_address, order.delivery_address)
        delivery_fee = DeliveryNotificationSystem._calculate_delivery_fee(distance)
        estimated_pickup = timezone.now() + timezone.timedelta(minutes=15)
        estimated_delivery = estimated_pickup + timezone.timedelta(minutes=int(distance * 3))
        
        orders_data.append({
            'id': order.id,
            'order_id': order.order_id,
            'customer_name': order.customer.username,
            'meal_name': order.daily_meal.main_dish,
            'portions': order.portions,
            'pickup_address': pickup_address,
            'delivery_address': order.delivery_address,
            'distance_km': distance,
            'delivery_fee': delivery_fee,
            'estimated_pickup_time': estimated_pickup,
            'estimated_delivery_time': estimated_delivery,
        })
    
    return Response(orders_data)


@swagger_auto_schema(
    method='post',
    tags=['Delivery'],
    operation_description="Accept a ready delivery order directly by order ID."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
@require_http_methods(['POST'])
def accept_available_order(request, order_id):
    """Accept a ready delivery order directly"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return Response({'error': 'Delivery partner profile not found'}, status=404)
    
    if not partner.is_available:
        return Response({'error': 'You must be available to accept orders'}, status=400)
    
    order = get_object_or_404(DailyMealOrder, id=order_id, delivery_type='delivery', order_status='ready')
    
    if DeliveryAssignment.objects.filter(order=order).exists():
        return Response({'error': 'Order has already been assigned'}, status=400)
    
    try:
        pickup_address = order.daily_meal.chef.chef_profile.kitchen_address
    except AttributeError:
        pickup_address = ''
    
    distance = DeliveryNotificationSystem._calculate_distance(pickup_address, order.delivery_address)
    delivery_fee = DeliveryNotificationSystem._calculate_delivery_fee(distance)
    partner_earnings = delivery_fee * Decimal('0.80')
    
    now = timezone.now()
    estimated_pickup_time = now + timezone.timedelta(minutes=15)
    estimated_delivery_time = estimated_pickup_time + timezone.timedelta(minutes=int(distance * 3))
    
    assignment = DeliveryAssignment.objects.create(
        order=order,
        delivery_partner=partner,
        pickup_address=pickup_address,
        delivery_address=order.delivery_address,
        estimated_pickup_time=estimated_pickup_time,
        estimated_delivery_time=estimated_delivery_time,
        delivery_fee=delivery_fee,
        partner_earnings=partner_earnings,
    )
    
    order.order_status = 'out_for_delivery'
    order.save()
    
    partner.is_available = False
    partner.save()
    
    return Response({
        'message': 'Order accepted successfully',
        'assignment_id': assignment.id
    })

