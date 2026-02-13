from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem, Delivery
from .serializers import OrderSerializer, OrderCreateSerializer, DeliverySerializer
from chefs.models import FoodItem
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_description="Place a new food order. Only customers can place orders.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['chef', 'items', 'delivery_address'],
        properties={
            'chef': openapi.Schema(
                type=openapi.TYPE_INTEGER, 
                description='Chef ID to order from',
                example=2
            ),
            'items': openapi.Schema(
                type=openapi.TYPE_ARRAY, 
                description='List of food items to order',
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'food_item': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Food item ID',
                            example=1
                        ),
                        'quantity': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Quantity to order',
                            minimum=1,
                            example=2
                        )
                    }
                ),
                example=[
                    {'food_item': 1, 'quantity': 2},
                    {'food_item': 3, 'quantity': 1}
                ]
            ),
            'delivery_address': openapi.Schema(
                type=openapi.TYPE_INTEGER, 
                description='Delivery address ID from customer addresses',
                example=1
            ),
            'special_instructions': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Special cooking or delivery instructions (optional)',
                example='Extra spicy, no onions please'
            )
        }
    ),
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
