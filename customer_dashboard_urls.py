# Customer Dashboard URL Configuration

# Add this to your HomeChefs/urls.py to handle the customer dashboard

from django.urls import path
from . import views

urlpatterns = [
    # Customer Dashboard
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    
    # Existing URLs...
]
