from django.urls import path
from . import views

urlpatterns = [
    path('favorite-chefs/', views.favorite_chefs, name='favorite_chefs'),
    path('favorite-chefs/<int:chef_id>/', views.remove_favorite_chef, name='remove_favorite_chef'),
    path('favorite-foods/', views.favorite_foods, name='favorite_foods'),
    path('favorite-foods/<int:food_id>/', views.remove_favorite_food, name='remove_favorite_food'),
    path('reviews/', views.food_reviews, name='food_reviews'),
    path('addresses/', views.addresses, name='addresses'),
    path('search-history/', views.search_history, name='search_history'),
    path('search/chefs/', views.search_chefs, name='search_chefs'),
    path('search/food/', views.search_food, name='search_food'),
]
