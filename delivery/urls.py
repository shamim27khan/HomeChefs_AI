from django.urls import path
from . import views, registration_views

app_name = 'delivery'

urlpatterns = [
    # Registration and Profile
    path('register/', registration_views.DeliveryPartnerRegistrationView.as_view(), name='register'),
    path('registration-success/', registration_views.delivery_partner_registration_success, name='registration_success'),
    path('profile/', registration_views.delivery_partner_profile, name='profile'),
    path('verification-status/', registration_views.delivery_partner_verification_status, name='verification_status'),
    
    # Dashboard and Main Views
    path('dashboard/', views.delivery_dashboard, name='dashboard'),
    
    # API Endpoints
    path('api/requests/', views.get_delivery_requests, name='get_requests'),
    path('api/requests/<int:request_id>/accept/', views.accept_delivery_request, name='accept_request'),
    path('api/available-orders/', views.available_delivery_orders, name='available_orders'),
    path('api/available-orders/<int:order_id>/accept/', views.accept_available_order, name='accept_available_order'),
    path('api/requests/<int:request_id>/decline/', views.decline_delivery_request, name='decline_request'),
    path('api/delivery/<int:assignment_id>/', views.get_delivery_details, name='delivery_details'),
    path('api/delivery/<int:assignment_id>/status/', views.update_delivery_status, name='update_status'),
    path('api/location/', views.update_location, name='update_location'),
    path('api/history/', views.get_delivery_history, name='delivery_history'),
    path('api/stats/', views.get_partner_stats, name='partner_stats'),
    path('api/toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('api/delivery/<int:assignment_id>/rate/', views.rate_delivery, name='rate_delivery'),
    
    # Admin endpoints
    path('admin/verify-partner/<int:partner_id>/', views.verify_delivery_partner, name='verify_delivery_partner'),
]
