from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Sum, Avg, Count
from datetime import timedelta, date
from ..models import Order, OrderItem, Delivery, DailyMealOrder, CustomerRating
from ..serializers import OrderSerializer, OrderCreateSerializer, DeliverySerializer
from ..serializers_mvp import (
    DailyMealOrderSerializer, DailyMealOrderCreateSerializer,
    CustomerRatingSerializer, OrderStatusUpdateSerializer,
    CustomerOrderListSerializer, ChefOrderListSerializer
)
from chefs.models import FoodItem, DailyMeal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
