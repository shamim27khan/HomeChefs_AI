from django.urls import path
from . import views

urlpatterns = [
    path('', views.orders, name='orders'),
    path('<str:order_id>/', views.order_detail, name='order_detail'),
    path('<str:order_id>/delivery/', views.delivery_detail, name='delivery_detail'),
    path('history/', views.order_history, name='order_history'),
    path('chef/today/', views.chef_orders, name='chef_orders'),
    path('customer/', views.customer_orders, name='customer_orders'),
]
