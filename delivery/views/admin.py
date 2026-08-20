from .common import *

@api_view(['POST'])
@permission_classes([IsAdminUser])
def verify_delivery_partner(request, partner_id):
    """Admin can verify a delivery partner"""
    partner = get_object_or_404(DeliveryPartner, id=partner_id)
    partner.verification_status = 'verified'
    partner.save()
    return Response({'message': f'Delivery partner {partner.user.username} verified successfully'})