from django.urls import path
from . import views_mvp

app_name = 'orders_mvp'

urlpatterns = [
    # Order Management
    path('create/', views_mvp.create_daily_meal_order, name='create_daily_meal_order'),
    path('<int:order_id>/', views_mvp.order_detail, name='order_detail'),
    path('<int:order_id>/status/', views_mvp.update_order_status, name='update_order_status'),
    path('<int:order_id>/cancel/', views_mvp.cancel_order, name='cancel_order'),
    path('<int:order_id>/confirm/', views_mvp.confirm_order, name='confirm_order'),
    
    # Customer Order Views
    path('customer/', views_mvp.customer_orders, name='customer_orders'),
    path('customer/history/', views_mvp.customer_order_history, name='customer_order_history'),
    
    # Chef Order Views
    path('chef/', views_mvp.chef_orders, name='chef_orders'),
    path('chef/summary/', views_mvp.chef_order_summary, name='chef_order_summary'),
    path('chef/stats/', views_mvp.chef_stats, name='chef_stats'),
    
    # Chef Order Views (with hyphens for frontend compatibility)
    path('chef-orders/', views_mvp.chef_orders, name='chef_orders_hyphen'),
    path('chef-stats/', views_mvp.chef_stats, name='chef_stats_hyphen'),
    
    # Rating and Reviews
    path('<int:order_id>/rate/', views_mvp.rate_order, name='rate_order'),
    path('<int:order_id>/deliver/', views_mvp.mark_as_delivered, name='mark_as_delivered'),
    path('customer/ratings/', views_mvp.customer_ratings, name='customer_ratings'),
    path('chef/ratings/', views_mvp.chef_ratings, name='chef_ratings'),
    path('chef/<int:chef_id>/ratings/', views_mvp.public_chef_ratings, name='public_chef_ratings'),
    
    # Admin Views
    path('admin/', views_mvp.admin_orders, name='admin_orders'),
    path('admin/stats/', views_mvp.admin_order_stats, name='admin_order_stats'),
]
