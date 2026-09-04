#!/usr/bin/env python
"""
Test admin dashboard API with browser-like authentication
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.views_mvp import admin_dashboard
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.authtoken.models import Token

def test_admin_dashboard_with_token():
    """Test admin dashboard with token authentication"""
    print("Testing Admin Dashboard with Token Authentication...")
    
    try:
        # Get or create admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_superuser': True,
                'is_staff': True,
                'role': 'admin',
                'email': 'admin@homechefs.com'
            }
        )
        
        # Ensure admin user has proper permissions
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        
        # Get or create token for admin user
        token, _ = Token.objects.get_or_create(user=admin_user)
        print(f"Admin token: {token.key}")
        
        # Test with APIClient (simulates browser request)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = client.get('/api/mvp/chefs/admin/dashboard/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print("+ Admin Dashboard API working with token!")
            print("\nDashboard Data:")
            print(f"  Total Chefs: {data['overview']['total_chefs']}")
            print(f"  Verified Chefs: {data['overview']['verified_chefs']}")
            print(f"  Total Customers: {data['overview']['total_customers']}")
            print(f"  Total Delivery Partners: {data['overview']['total_delivery_partners']}")
            print(f"  Today's Meals: {data['today']['meals_posted']}")
            print(f"  Today's Orders: {data['today']['orders_received']}")
            print(f"  Today's Revenue: Rs. {data['today']['revenue']}")
            return True
        else:
            print(f"- API returned status {response.status_code}")
            print(f"Response: {response.data}")
            return False
            
    except Exception as e:
        print(f"- Error testing admin dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_dashboard_without_token():
    """Test admin dashboard without token (should fail)"""
    print("\nTesting Admin Dashboard without Token...")
    
    try:
        # Test without authentication
        client = APIClient()
        
        response = client.get('/api/mvp/chefs/admin/dashboard/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401 or response.status_code == 403:
            print("+ Correctly denied access without token")
            return True
        else:
            print(f"- Expected 401/403, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing unauthenticated access: {e}")
        return False

def test_admin_dashboard_with_invalid_token():
    """Test admin dashboard with invalid token"""
    print("\nTesting Admin Dashboard with Invalid Token...")
    
    try:
        # Test with invalid token
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token invalid_token_12345')
        
        response = client.get('/api/mvp/chefs/admin/dashboard/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("+ Correctly denied access with invalid token")
            return True
        else:
            print(f"- Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing invalid token: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ADMIN DASHBOARD BROWSER TEST")
    print("=" * 60)
    
    tests = [
        test_admin_dashboard_with_token,
        test_admin_dashboard_without_token,
        test_admin_dashboard_with_invalid_token,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("+ All admin dashboard tests passed!")
        print("The API should work correctly in browser.")
    else:
        print("- Some tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
