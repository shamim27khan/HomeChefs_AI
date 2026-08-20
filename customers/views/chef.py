from .common import *

@swagger_auto_schema(
    method='post',
    tags=['Customers'],
    operation_description="Rate a customer (chef endpoint).",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['rating'],
        properties={
            'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rating from 1 to 5', minimum=1, maximum=5),
            'feedback': openapi.Schema(type=openapi.TYPE_STRING, description='Optional feedback about the customer')
        }
    )
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rate_customer(request, order_id):
    """Rate a customer (chef endpoint)"""
    if request.user.role != 'chef':
        return Response({'error': 'Only chefs can rate customers'}, status=status.HTTP_403_FORBIDDEN)
    
    from orders.models import DailyMealOrder
    order = get_object_or_404(DailyMealOrder, id=order_id, daily_meal__chef=request.user)
    
    # Check if order is delivered
    if order.order_status != 'delivered':
        return Response({'error': 'You can only rate customers for delivered orders'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if already rated
    if CustomerRating.objects.filter(customer=order.customer, order=order).exists():
        return Response({'error': 'You have already rated this customer for this order'}, status=status.HTTP_400_BAD_REQUEST)
    
    rating = request.data.get('rating')
    feedback = request.data.get('feedback', '')
    
    if not rating or int(rating) < 1 or int(rating) > 5:
        return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create rating
    customer_rating = CustomerRating.objects.create(
        customer=order.customer,
        chef=request.user,
        order=order,
        rating=rating,
        feedback=feedback
    )
    
    return Response({'message': 'Customer rated successfully', 'rating': customer_rating.rating})
