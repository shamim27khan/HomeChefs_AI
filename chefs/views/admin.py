from .common import *

@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Admin can view pending chefs for verification."
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_pending_chefs(request):
    """Admin can view pending chefs for verification"""
    pending_chefs = ChefProfile.objects.filter(is_verified=False)
    chefs = User.objects.filter(
        role='chef',
        chefprofile__in=pending_chefs
    )
    serializer = AdminChefSerializer(chefs, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    tags=['Chefs'],
    operation_description="Admin can verify a chef by chef_id.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['chef_id'],
        properties={
            'chef_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the chef to verify')
        }
    )
)
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def admin_verify_chef(request):
    """Admin can verify a chef"""
    chef_id = request.data.get('chef_id')
    chef = get_object_or_404(User, id=chef_id, role='chef')
    
    chef.chefprofile.is_verified = True
    chef.chefprofile.verification_date = timezone.now()
    chef.chefprofile.save()
    
    return Response({'message': f'Chef {chef.username} verified successfully'})


@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Admin can view complete chef information."
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_chefs(request):
    """Admin can view complete chef information"""
    chefs = User.objects.filter(role='chef').order_by('-date_joined')
    serializer = AdminChefSerializer(chefs, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Admin can view delivery partner information."
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_delivery_partners(request):
    """Admin can view delivery partner information"""
    from delivery.models import DeliveryPartner
    
    delivery_partners = DeliveryPartner.objects.select_related('user').all().order_by('-created_at')
    
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
            'completed_orders': partner.total_deliveries,
            'average_rating': partner.average_rating,
            'completion_rate': partner.completion_rate,
            'service_areas': partner.service_areas,
            'max_delivery_distance': partner.max_delivery_distance,
            'created_at': partner.created_at,
        })
    
    return Response(partners_data)


@swagger_auto_schema(
    method='get',
    tags=['Chefs'],
    operation_description="Admin dashboard with key metrics."
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard(request):
    """Admin dashboard with key metrics"""
    from django.db.models import Count, Sum, Q
    from orders.models import DailyMealOrder
    
    today = date.today()
    
    total_chefs = User.objects.filter(role='chef').count()
    verified_chefs = User.objects.filter(role='chef', chefprofile__is_verified=True).count()
    total_customers = User.objects.filter(role='customer').count()
    total_delivery_partners = User.objects.filter(role='delivery_partner').count()
    verified_delivery_partners = User.objects.filter(
        role='delivery_partner', 
        delivery_partner__verification_status='verified'
    ).count()
    
    today_meals = DailyMeal.objects.filter(date=today).count()
    today_orders = DailyMealOrder.objects.filter(order_time__date=today).count()
    today_revenue = DailyMealOrder.objects.filter(
        order_time__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
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
