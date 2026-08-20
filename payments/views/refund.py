from .common import *

@swagger_auto_schema(
    method='post',
    tags=['Payments'],
    operation_description="Request a refund for a payment. Only customers can request refunds.",
    request_body=RefundCreateSerializer,
    responses={
        201: openapi.Response(
            description='Refund request created successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'refund_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'payment': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'amount': openapi.Schema(type=openapi.TYPE_STRING),
                    'reason': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'id': 1,
                    'refund_id': 'REF001',
                    'payment': 1,
                    'amount': '250.00',
                    'reason': 'Food quality was not as expected',
                    'status': 'pending',
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
                    'payment': ['This field is required.'],
                    'reason': ['This field is required.']
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only customers can request refunds',
            examples={
                'application/json': {
                    'error': 'Only customers can request refunds'
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def refunds(request):
    if request.user.role not in ['customer', 'admin']:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        if request.user.role == 'customer':
            refunds = Refund.objects.filter(payment__order__customer=request.user).order_by('-created_at')
        else:  # admin
            refunds = Refund.objects.all().order_by('-created_at')
        
        serializer = RefundSerializer(refunds, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'customer':
            return Response({'error': 'Only customers can request refunds'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RefundCreateSerializer(data=request.data)
        if serializer.is_valid():
            refund = serializer.save()
            return Response(RefundSerializer(refund).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def refund_detail(request, refund_id):
    refund = get_object_or_404(Refund, refund_id=refund_id)
    
    # Check permissions
    if request.user.role == 'customer' and refund.payment.order.customer != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = RefundSerializer(refund)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if request.user.role != 'admin':
            return Response({'error': 'Only admins can process refunds'}, status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get('action')
        if action == 'approve':
            with transaction.atomic():
                refund.status = 'completed'
                refund.processed_by = request.user
                refund.processed_at = timezone.now()
                refund.save()
                
                # Process refund to wallet or original payment method
                payment = refund.payment
                if payment.payment_method == 'wallet':
                    # Refund to wallet
                    try:
                        wallet = Wallet.objects.get(user=payment.order.customer, is_active=True)
                        wallet.balance += refund.amount
                        wallet.save()
                        
                        WalletTransaction.objects.create(
                            wallet=wallet,
                            transaction_id=f"REF{refund.refund_id[3:]}",
                            amount=refund.amount,
                            transaction_type='credit',
                            description=f'Refund for order {payment.order.order_id}',
                            reference_id=refund.refund_id
                        )
                    except Wallet.DoesNotExist:
                        pass
                
                # Update payment status
                payment.status = 'refunded'
                payment.save()
                
                return Response({'message': 'Refund processed successfully'})
        
        elif action == 'reject':
            refund.status = 'rejected'
            refund.processed_by = request.user
            refund.processed_at = timezone.now()
            refund.save()
            return Response({'message': 'Refund rejected'})
        
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)