from django.urls import path
from . import views

urlpatterns = [
    path('food-items/', views.food_items, name='food_items'),
    path('food-items/<int:food_id>/', views.food_item_detail, name='food_item_detail'),
    path('food-items/<int:food_id>/schedules/', views.food_schedules, name='food_schedules'),
    path('reviews/', views.chef_reviews, name='chef_reviews'),
    path('public/', views.public_chef_list, name='public_chef_list'),
    path('public/<int:chef_id>/', views.public_chef_detail, name='public_chef_detail'),
    path('rate-meal/<int:meal_id>/', views.rate_meal, name='rate_meal'),
]
