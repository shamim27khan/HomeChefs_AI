from django.urls import path
from . import views_mvp

app_name = 'chefs_mvp'

urlpatterns = [
    # Chef MVP URLs
    path('daily-meals/', views_mvp.chef_daily_meals, name='chef_daily_meals'),
    path('daily-meals/<int:meal_id>/', views_mvp.chef_daily_meal_detail, name='chef_daily_meal_detail'),
    path('my-meals/', views_mvp.my_meals, name='my_meals'),
    path('profile/', views_mvp.chef_profile, name='chef_profile'),
    path('earnings/', views_mvp.chef_earnings, name='chef_earnings'),
    path('orders/', views_mvp.chef_orders, name='chef_orders'),
    
    # Customer MVP URLs
    path('public/', views_mvp.public_chefs, name='public_chefs'),
    path('today-meals/', views_mvp.today_meals, name='today_meals'),
    path('nearby-dishes/', views_mvp.nearby_dishes, name='nearby_dishes'),
    path('customer-orders/', views_mvp.customer_orders, name='customer_orders'),
    path('review/<int:order_id>/', views_mvp.customer_review, name='customer_review'),
    
    # Admin MVP URLs
    path('admin/verification/', views_mvp.admin_chef_verification, name='admin_chef_verification'),
    path('admin/dashboard/', views_mvp.admin_dashboard, name='admin_dashboard'),
]
