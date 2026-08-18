from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import Payment, Wallet, WalletTransaction, Refund
from .serializers import PaymentSerializer, PaymentCreateSerializer, WalletSerializer, WalletTransactionSerializer, RefundSerializer, RefundCreateSerializer
from orders.models import Order
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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

@swagger_auto_schema(
    method='post',
    tags=['Payments'],
    operation_description="Add money to customer's wallet. Only customers can access this endpoint.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['amount'],
        properties={
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount to add to wallet (must be greater than 0)', minimum=0.01)
        }
    ),
    responses={
        200: openapi.Response(
            description='Money added to wallet successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'new_balance': openapi.Schema(type=openapi.TYPE_NUMBER)
                }
            ),
            examples={
                'application/json': {
                    'message': 'Added 500.0 to wallet',
                    'new_balance': 1500.0
                }
            }
        ),
        400: openapi.Response(
            description='Bad request - invalid amount',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'error': 'Invalid amount'
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - Only customers have wallets',
            examples={
                'application/json': {
                    'error': 'Only customers have wallets'
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def wallet(request):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers have wallets'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=request.user)
    
    if request.method == 'GET':
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Add money to wallet
        amount = request.data.get('amount')
        if not amount or float(amount) <= 0:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        # In a real implementation, you would process payment here
        # For now, we'll just add the money
        
        wallet.balance += float(amount)
        wallet.save()
        
        # Create transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_id=f"ADD{wallet.id}{int(wallet.balance)}",
            amount=float(amount),
            transaction_type='credit',
            description='Wallet recharge',
            reference_id=f"RECHARGE{wallet.id}"
        )
        
        return Response({'message': f'Added {amount} to wallet', 'new_balance': wallet.balance})

@swagger_auto_schema(
    method='get',
    tags=['Payments'],
    operation_description="Get wallet transaction history."
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def wallet_transactions(request):
    if request.user.role != 'customer':
        return Response({'error': 'Only customers have wallets'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        wallet = Wallet.objects.get(user=request.user)
        transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    except Wallet.DoesNotExist:
        return Response([])

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
