from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
import json

from ..models import DeliveryPartner, DeliveryRequest, DeliveryAssignment, DeliveryRating
from ..notifications import DeliveryNotificationSystem, DeliveryLocationTracker
from orders.models import DailyMealOrder
from authentication.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
