from .common import *

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
