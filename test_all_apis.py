#!/usr/bin/env python
"""Smoke-test all grouped HomeChefs API endpoints without starting a live server.

Run with:  python test_all_apis.py
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client(content_type='application/json')

BASE = '/api'

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def call(method, url, data=None, token=None):
    headers = {}
    if token:
        # Force token auth by clearing any existing session login
        client.logout()
        headers['HTTP_AUTHORIZATION'] = f'Token {token}'
    if method == 'GET':
        return client.get(url, **headers)
    elif method == 'POST':
        return client.post(url, data=data, content_type='application/json', **headers)
    elif method == 'PUT':
        return client.put(url, data=data, content_type='application/json', **headers)
    elif method == 'DELETE':
        return client.delete(url, **headers)
    raise ValueError(f'Unsupported method {method}')


def login(username, password):
    resp = client.post(f'{BASE}/auth/login/', data={'username': username, 'password': password}, content_type='application/json')
    if resp.status_code == 200:
        return resp.json().get('token')
    return None


def test_group(name, endpoints, token=None):
    print(f'\n[{name}]')
    print('-' * 60)
    for method, url, data in endpoints:
        full = url if url.startswith('/delivery/') else f'{BASE}{url}'
        try:
            r = call(method, full, data, token)
            icon = 'OK' if r.status_code < 500 else 'ERR'
            print(f'{icon:>3} {method:6} {r.status_code:3} {full}')
        except Exception as e:
            print(f'ERR {method:6} --- {full} : {e}')


# ---------------------------------------------------------------------------
# Sample user logins (if present in DB)
# ---------------------------------------------------------------------------
customer_token = login('customer_anjali', 'customer123')
chef_token = login('chef_rahul', 'chef123')
admin_token = login('admin_sample', 'adminpass123')

if customer_token:
    print('\nCustomer login: OK')
else:
    print('\nCustomer login: FAIL (or user does not exist)')
if chef_token:
    print('Chef login: OK')
else:
    print('Chef login: FAIL (or user does not exist)')
if admin_token:
    print('Admin login: OK')
else:
    print('Admin login: FAIL (or user does not exist)')

# ---------------------------------------------------------------------------
# Public / customer-facing endpoints
# ---------------------------------------------------------------------------
test_group('Public / Customer', [
    ('GET', '/chefs/public/', None),
    ('GET', '/chefs/public/1/', None),
    ('GET', '/chefs/today-meals/', None),
    ('GET', '/chefs/nearby-dishes/?latitude=19.076&longitude=72.877&radius=5', None),
    ('GET', '/customers/search/chefs/?q=rahul', None),
    ('GET', '/customers/search/food/?q=biryani', None),
])

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
test_group('Authentication', [
    ('POST', '/auth/register/', {'username': f'testuser_{os.urandom(4).hex()}', 'email': 'test@example.com', 'password': 'testpass123', 'confirm_password': 'testpass123', 'first_name': 'Test', 'last_name': 'User', 'role': 'customer'}),
    ('POST', '/auth/request-otp/', {'phone_number': '+1234567890'}),
    ('GET', '/auth/profile/', None),
])

# ---------------------------------------------------------------------------
# Customer endpoints
# ---------------------------------------------------------------------------
customer_endpoints = [
    ('GET', '/customers/favorite-chefs/', None),
    ('POST', '/customers/favorite-chefs/', {'chef_id': 1}),
    ('GET', '/customers/favorite-foods/', None),
    ('POST', '/customers/favorite-foods/', {'food_item_id': 1}),
    ('GET', '/customers/reviews/', None),
    ('GET', '/customers/ratings/', None),
    ('GET', '/customers/addresses/', None),
    ('GET', '/customers/search-history/', None),
    ('GET', '/customers/search/chefs/?q=indian', None),
    ('GET', '/customers/search/food/?q=curry', None),
]
test_group('Customer', customer_endpoints, token=customer_token)

# ---------------------------------------------------------------------------
# Chef endpoints
# ---------------------------------------------------------------------------
chef_endpoints = [
    ('GET', '/chefs/food-items/', None),
    ('GET', '/chefs/reviews/', None),
    ('GET', '/chefs/dashboard/meals/', None),
    ('GET', '/chefs/dashboard/profile/', None),
    ('GET', '/chefs/dashboard/earnings/', None),
    ('GET', '/chefs/dashboard/orders/', None),
    ('GET', '/chefs/dashboard/my-meals/', None),
]
test_group('Chef', chef_endpoints, token=chef_token)

# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------
admin_endpoints = [
    ('GET', '/chefs/admin/dashboard/', None),
    ('GET', '/chefs/admin/pending-chefs/', None),
    ('POST', '/chefs/admin/verify-chef/', {'chef_id': 1}),
    ('GET', '/chefs/admin/chefs/', None),
    ('GET', '/chefs/admin/delivery-partners/', None),
    ('GET', '/orders/admin/daily-meals/', None),
    ('GET', '/orders/admin/daily-meals/stats/', None),
]
test_group('Admin', admin_endpoints, token=admin_token)

# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
order_endpoints = [
    ('GET', '/orders/', None),
    ('GET', '/orders/history/', None),
    ('GET', '/orders/customer/', None),
    ('GET', '/orders/chef/', None),
    ('GET', '/orders/daily/customer/', None),
    ('GET', '/orders/daily/chef/', None),
    ('GET', '/orders/daily/chef/stats/', None),
    ('GET', '/orders/chef/1/ratings/', None),
]
test_group('Orders', order_endpoints, token=customer_token)

# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------
payment_endpoints = [
    ('GET', '/payments/', None),
    ('GET', '/payments/wallet/', None),
    ('GET', '/payments/wallet/transactions/', None),
    ('GET', '/payments/refunds/', None),
]
test_group('Payments', payment_endpoints, token=customer_token)

# ---------------------------------------------------------------------------
# Delivery
# ---------------------------------------------------------------------------
delivery_endpoints = [
    ('GET', '/delivery/api/requests/', None),
    ('GET', '/delivery/api/history/', None),
    ('GET', '/delivery/api/stats/', None),
    ('GET', '/delivery/api/delivery/1/', None),
]
test_group('Delivery', delivery_endpoints, token=admin_token)

print('\n' + '=' * 60)
print('Smoke test complete. Any 5xx errors above need investigation.')
