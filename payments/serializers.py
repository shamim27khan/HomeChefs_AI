from rest_framework import serializers
from .models import Payment, Wallet, WalletTransaction, Refund
from orders.serializers import OrderSerializer

class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'payment_id', 'order', 'amount', 'payment_method', 'status', 'transaction_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'payment_id', 'created_at', 'updated_at']

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['order', 'payment_method']
    
    def create(self, validated_data):
        import uuid
        payment_id = f"PAY{uuid.uuid4().hex[:8].upper()}"
        
        payment = Payment.objects.create(
            payment_id=payment_id,
            **validated_data
        )
        
        return payment

class WalletSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        from authentication.serializers import UserProfileSerializer
        return UserProfileSerializer(obj.user).data

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_id', 'amount', 'transaction_type', 'description', 'reference_id', 'created_at']
        read_only_fields = ['id', 'transaction_id', 'created_at']

class RefundSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    processed_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Refund
        fields = ['id', 'refund_id', 'payment', 'amount', 'reason', 'status', 'processed_by', 'processed_at', 'created_at']
        read_only_fields = ['id', 'refund_id', 'processed_by', 'processed_at', 'created_at']
    
    def get_processed_by(self, obj):
        if obj.processed_by:
            from authentication.serializers import UserProfileSerializer
            return UserProfileSerializer(obj.processed_by).data
        return None

class RefundCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['payment', 'amount', 'reason']
    
    def create(self, validated_data):
        import uuid
        refund_id = f"REF{uuid.uuid4().hex[:8].upper()}"
        
        refund = Refund.objects.create(
            refund_id=refund_id,
            **validated_data
        )
        
        return refund
