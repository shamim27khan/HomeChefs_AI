from django.urls import path
from . import views

urlpatterns = [
    # Daily meal order endpoints (MVP)
    path('daily/create/', views.create_daily_meal_order, name='create_daily_meal_order'),
    path('daily/<int:order_id>/', views.daily_meal_order_detail, name='daily_meal_order_detail'),
    path('daily/<int:order_id>/deliver/', views.mark_daily_meal_as_delivered, name='mark_daily_meal_as_delivered'),
    path('daily/customer/', views.daily_meal_customer_orders, name='daily_meal_customer_orders'),
    
    # Chef daily meal order views (with hyphens for frontend compatibility)
    path('daily/chef/', views.daily_meal_chef_orders, name='daily_meal_chef_orders'),
    path('daily/chef-stats/', views.daily_meal_chef_stats, name='daily_meal_chef_stats'),
    path('daily/chef-orders/', views.daily_meal_chef_orders, name='daily_meal_chef_orders_hyphen'),
]
