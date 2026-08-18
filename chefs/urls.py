from django.urls import path
from . import views

urlpatterns = [
    # Regular food item endpoints
    path('food-items/', views.food_items, name='food_items'),
    path('food-items/<int:food_id>/', views.food_item_detail, name='food_item_detail'),
    path('food-items/<int:food_id>/schedules/', views.food_schedules, name='food_schedules'),
    path('reviews/', views.chef_reviews, name='chef_reviews'),
    path('public/', views.public_chef_list, name='public_chef_list'),
    path('public/<int:chef_id>/', views.public_chef_detail, name='public_chef_detail'),
    path('rate-meal/<int:meal_id>/', views.rate_meal, name='rate_meal'),
    
    # Chef dashboard endpoints (formerly MVP)
    path('dashboard/meals/', views.chef_daily_meals, name='chef_daily_meals'),
    path('dashboard/meals/<int:meal_id>/', views.chef_daily_meal_detail, name='chef_daily_meal_detail'),
    path('dashboard/meals/<int:meal_id>/toggle-status/', views.toggle_meal_status, name='toggle_meal_status'),
    path('dashboard/meals/<int:meal_id>/update/', views.update_meal, name='update_meal'),
    path('dashboard/my-meals/', views.my_meals, name='my_meals'),
    path('dashboard/profile/', views.chef_profile, name='chef_profile'),
    path('dashboard/earnings/', views.chef_earnings, name='chef_earnings'),
    path('dashboard/orders/', views.chef_orders, name='chef_orders'),
    
    # Customer endpoints (formerly MVP)
    path('browse/', views.public_chefs, name='public_chefs'),
    path('today-meals/', views.today_meals, name='today_meals'),
    path('nearby-dishes/', views.nearby_dishes, name='nearby_dishes'),
    path('customer-orders/', views.customer_orders, name='customer_orders'),
    path('customer-review/<int:order_id>/', views.customer_review, name='customer_review'),
    
    # Admin endpoints (formerly MVP)
    path('admin/verification/', views.admin_chef_verification, name='admin_chef_verification'),
    path('admin/chefs/', views.admin_chefs, name='admin_chefs'),
    path('admin/delivery-partners/', views.admin_delivery_partners, name='admin_delivery_partners'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
