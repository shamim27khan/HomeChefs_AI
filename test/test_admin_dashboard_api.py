#!/usr/bin/env python
"""
Test script to verify admin dashboard API is working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.views_mvp import admin_dashboard
from rest_framework.test import APIRequestFactory

def test_admin_dashboard():
    """Test the admin dashboard API endpoint"""
    print("Testing Admin Dashboard API...")
    
    try:
        # Create admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin', 
            defaults={
                'is_superuser': True, 
                'is_staff': True,
                'email': 'admin@test.com'
            }
        )
        
        # Test the endpoint
        factory = APIRequestFactory()
        request = factory.get('/api/mvp/chefs/admin/dashboard/')
        request.user = admin_user
        
        response = admin_dashboard(request)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print("+ Admin Dashboard API working!")
            print("\nDashboard Data:")
            print(f"  Total Chefs: {data['overview']['total_chefs']}")
            print(f"  Verified Chefs: {data['overview']['verified_chefs']}")
            print(f"  Total Customers: {data['overview']['total_customers']}")
            print(f"  Total Delivery Partners: {data['overview']['total_delivery_partners']}")
            print(f"  Verified Delivery Partners: {data['overview']['verified_delivery_partners']}")
            print(f"  Chef Verification Rate: {data['overview']['chef_verification_rate']}%")
            print(f"  Delivery Partner Verification Rate: {data['overview']['delivery_partner_verification_rate']}%")
            print(f"  Today's Meals: {data['today']['meals_posted']}")
            print(f"  Today's Orders: {data['today']['orders_received']}")
            print(f"  Today's Revenue: Rs. {data['today']['revenue']}")
            return True
        else:
            print(f"- API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing admin dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_non_admin_access():
    """Test that non-admin users can't access the dashboard"""
    print("\nTesting Non-Admin Access...")
    
    try:
        # Create regular user
        regular_user, _ = User.objects.get_or_create(
            username='regular',
            defaults={'email': 'regular@test.com'}
        )
        
        # Test the endpoint
        factory = APIRequestFactory()
        request = factory.get('/api/mvp/chefs/admin/dashboard/')
        request.user = regular_user
        
        response = admin_dashboard(request)
        
        if response.status_code == 403:
            print("+ Non-admin access properly denied")
            return True
        else:
            print(f"- Expected 403, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing non-admin access: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ADMIN DASHBOARD API TEST")
    print("=" * 60)
    
    tests = [
        test_admin_dashboard,
        test_non_admin_access,
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
        print("The main page should now load properly.")
    else:
        print("- Some tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
