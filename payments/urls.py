from django.urls import path
from . import views

urlpatterns = [
    # Wallet endpoints
    path('wallet/', views.wallet, name='wallet'),
    path('wallet/transactions/', views.wallet_transactions, name='wallet_transactions'),
    # Refund endpoints
    path('refunds/', views.refunds, name='refunds'),
    path('refunds/<int:refund_id>/', views.refund_detail, name='refund_detail'),
    # Payment endpoints
    path('', views.payments, name='payments'),
    path('<str:payment_id>/', views.payment_detail, name='payment_detail'),
]
