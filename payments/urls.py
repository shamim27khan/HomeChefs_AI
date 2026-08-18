from django.urls import path
from . import views

urlpatterns = [
    path('wallet/', views.wallet, name='wallet'),
    path('wallet/transactions/', views.wallet_transactions, name='wallet_transactions'),
    path('refunds/', views.refunds, name='refunds'),
]
