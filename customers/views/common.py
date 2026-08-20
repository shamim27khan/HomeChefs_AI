from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from ..models import FavoriteChef, FavoriteFood, FoodReview, CustomerAddress, SearchHistory, CustomerRating
from ..serializers import FavoriteChefSerializer, FavoriteFoodSerializer, FoodReviewCreateSerializer, FoodReviewSerializer, CustomerAddressSerializer, SearchHistorySerializer
from chefs.models import FoodItem, ChefReview
from chefs.serializers import FoodItemSerializer
from authentication.models import ChefProfile
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
