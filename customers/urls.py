from django.urls import path
from . import views

urlpatterns = [
    # Customer favorites
    path('favorite-chefs/', views.favorite_chefs, name='favorite_chefs'),
    path('favorite-chefs/<int:chef_id>/', views.remove_favorite_chef, name='remove_favorite_chef'),
    path('favorite-foods/', views.favorite_foods, name='favorite_foods'),
    path('favorite-foods/<int:food_id>/', views.remove_favorite_food, name='remove_favorite_food'),
    # Customer reviews and ratings
    path('reviews/', views.food_reviews, name='food_reviews'),
    path('ratings/', views.get_customer_ratings, name='customer_ratings'),
    # Customer address
    path('addresses/', views.addresses, name='addresses'),
    # Customer search
    path('search/chefs/', views.search_chefs, name='search_chefs'),
    path('search/food/', views.search_food, name='search_food'),
    path('search-history/', views.search_history, name='search_history'),
    # Chef rating customer
    path('rate/<int:order_id>/', views.rate_customer, name='rate_customer'),
]
