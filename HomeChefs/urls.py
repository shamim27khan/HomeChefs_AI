"""HomeChefs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="HomeChefs API",
        default_version='v1',
        description="API documentation for HomeChefs - Homemade Food Delivery Platform\n\n**Authentication:**\n- Use Token Authentication\n- Header: Authorization: Token <your-token>\n- Get token by logging in at /api/auth/login/\n\n**Important Notes:**\n- Some endpoints require specific user roles (chef/customer)\n- Public endpoints can be accessed without authentication\n- Chef endpoints require chef role and authentication",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@homechefs.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    validators=['ssv', 'flex'],
)

urlpatterns = [
    path('', views.home, name='home'),
    path('mvp/', views.index_mvp, name='index_mvp'),
    path('zomato/', views.index_zomato_style, name='index_zomato_style'),
    path('search/', views.search_page, name='search_page'),
    path('chef/', views.chef_detail, name='chef_detail'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('order-meal/<int:meal_id>/', views.order_meal, name='order_meal'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('cart/', views.cart_page, name='cart_page'),
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/auth/', include('authentication.urls')),
    path('api/chefs/', include('chefs.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    # MVP URLs
    path('api/mvp/chefs/', include('chefs.urls_mvp')),
    path('api/mvp/orders/', include('orders.urls_mvp')),
    path('test/', views.test_page, name='test_page'),
    # Frontend static files
    path('frontend/<path:path>', views.serve_frontend_file, name='serve_frontend_file'),
    # Catch-all for frontend files
    re_path(r'^.*/index_zomato_style\.html$', views.search_page, name='catch_zomato_html'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
