from .common import *

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
