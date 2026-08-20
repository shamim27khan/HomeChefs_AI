from django.urls import path
from . import views

urlpatterns = [
    # Main order endpoints
    path('', views.orders, name='orders'),
    path('history/', views.order_history, name='order_history'),
    path('chef/', views.chef_orders, name='chef_orders'),
    path('customer/', views.customer_orders, name='customer_orders'),

    # Daily meal order endpoints
    path('daily/create/', views.create_daily_meal_order, name='create_daily_meal_order'),
    path('daily/customer/', views.daily_meal_customer_orders, name='daily_meal_customer_orders'),
    path('daily/customer/history/', views.daily_meal_customer_order_history, name='daily_meal_customer_order_history'),
    path('daily/customer/ratings/', views.daily_meal_customer_ratings, name='daily_meal_customer_ratings'),
    path('daily/chef/', views.daily_meal_chef_orders, name='daily_meal_chef_orders'),
    path('daily/chef/summary/', views.daily_meal_chef_order_summary, name='daily_meal_chef_order_summary'),
    path('daily/chef/stats/', views.daily_meal_chef_stats, name='daily_meal_chef_stats'),
    path('daily/chef-stats/', views.daily_meal_chef_stats, name='daily_meal_chef_stats_hyphen'),
    path('daily/chef/ratings/', views.daily_meal_chef_ratings, name='daily_meal_chef_ratings'),
    path('daily/chef-orders/', views.daily_meal_chef_orders, name='daily_meal_chef_orders_hyphen'),
    path('daily/<int:order_id>/', views.daily_meal_order_detail, name='daily_meal_order_detail'),
    path('daily/<int:order_id>/confirm/', views.confirm_daily_meal_order, name='confirm_daily_meal_order'),
    path('daily/<int:order_id>/status/', views.update_daily_meal_order_status, name='update_daily_meal_order_status'),
    path('daily/<int:order_id>/deliver/', views.mark_daily_meal_as_delivered, name='mark_daily_meal_as_delivered'),
    path('daily/<int:order_id>/cancel/', views.cancel_daily_meal_order, name='cancel_daily_meal_order'),
    path('daily/<int:order_id>/rate/', views.rate_daily_meal_order, name='rate_daily_meal_order'),

    # Public chef ratings
    path('chef/<int:chef_id>/ratings/', views.daily_meal_public_chef_ratings, name='daily_meal_public_chef_ratings'),

    # Admin daily meal orders
    path('admin/daily-meals/', views.daily_meal_admin_orders, name='daily_meal_admin_orders'),
    path('admin/daily-meals/stats/', views.daily_meal_admin_order_stats, name='daily_meal_admin_order_stats'),

    # Generic order detail (must come after static paths)
    path('<str:order_id>/', views.order_detail, name='order_detail'),
    path('<str:order_id>/delivery/', views.delivery_detail, name='delivery_detail'),
]
