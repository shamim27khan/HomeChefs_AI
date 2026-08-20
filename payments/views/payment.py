from .common import *

@swagger_auto_schema(
    method='post',
    tags=['Payments'],
    operation_description="Process payment for an order. Only customers can make payments.",
    request_body=PaymentCreateSerializer,
    responses={
        201: openapi.Response(
            description='Payment processed successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'payment_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'order': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'amount': openapi.Schema(type=openapi.TYPE_STRING),
                    'payment_method': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'transaction_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'id': 1,
                    'payment_id': 'PAY001',
                    'order': 1,
                    'amount': '250.00',
                    'payment_method': 'wallet',
                    'status': 'completed',
                    'transaction_id': 'WLT001',
                    'created_at': '2024-01-15T10:30:00Z'
                }
            }
        ),
        400: openapi.Response(
            description='Bad request - validation errors or payment failed',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'error': 'Insufficient wallet balance'
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only customers can make payments',
            examples={
                'application/json': {
                    'error': 'Only customers can make payments'
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def payments(request):
    if request.user.role not in ['customer', 'admin']:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        if request.user.role == 'customer':
            payments = Payment.objects.filter(order__customer=request.user).order_by('-created_at')
        else:  # admin
            payments = Payment.objects.all().order_by('-created_at')
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'customer':
            return Response({'error': 'Only customers can make payments'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Process payment based on method
            payment_method = payment.payment_method
            
            if payment_method == 'wallet':
                # Process wallet payment
                try:
                    wallet = Wallet.objects.get(user=request.user, is_active=True)
                    if wallet.balance >= payment.amount:
                        # Deduct from wallet
                        wallet.balance -= payment.amount
                        wallet.save()
                        
                        # Create wallet transaction
                        WalletTransaction.objects.create(
                            wallet=wallet,
                            transaction_id=f"WLT{payment.payment_id[3:]}",
                            amount=payment.amount,
                            transaction_type='debit',
                            description=f"Payment for order {payment.order.order_id}",
                            reference_id=payment.payment_id
                        )
                        
                        payment.status = 'completed'
                        payment.transaction_id = f"WLT{payment.payment_id[3:]}"
                        payment.save()
                        
                        # Update order payment status
                        payment.order.payment_status = 'paid'
                        payment.order.save()
                        
                        return Response(PaymentSerializer(payment).data)
                    else:
                        payment.status = 'failed'
                        payment.save()
                        return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
                
                except Wallet.DoesNotExist:
                    payment.status = 'failed'
                    payment.save()
                    return Response({'error': 'Wallet not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            elif payment_method == 'cash_on_delivery':
                payment.status = 'pending'
                payment.save()
                return Response(PaymentSerializer(payment).data)
            
            else:
                # Simulate other payment methods (credit card, debit card, UPI)
                # In a real implementation, you would integrate with payment gateways
                payment.status = 'processing'
                payment.transaction_id = f"TXN{payment.payment_id[3:]}"
                payment.gateway_response = "{'status': 'processing', 'message': 'Payment initiated'}"
                payment.save()
                
                # Simulate successful payment (in real implementation, this would be async)
                payment.status = 'completed'
                payment.save()
                
                # Update order payment status
                payment.order.payment_status = 'paid'
                payment.order.save()
                
                return Response(PaymentSerializer(payment).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    tags=['Payments'],
    operation_description="Get payment details by payment ID."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id)
    
    # Check permissions
    if request.user.role == 'customer' and payment.order.customer != request.user:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'chef':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = PaymentSerializer(payment)
    return Response(serializer.data)
