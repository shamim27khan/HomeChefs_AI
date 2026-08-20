from .common import *

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
