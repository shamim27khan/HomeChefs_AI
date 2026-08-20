#!/usr/bin/env python
"""
Test script to verify admin delivery partner functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.views_mvp import admin_delivery_partners, admin_dashboard
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.authtoken.models import Token

def test_admin_delivery_partners_endpoint():
    """Test the admin delivery partners endpoint"""
    print("Testing Admin Delivery Partners Endpoint...")
    
    try:
        # Get admin user and token
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        # Test admin delivery partners endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = client.get('/api/mvp/chefs/admin/delivery-partners/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            partners = response.data
            print(f"+ Admin delivery partners endpoint working! Found {len(partners)} partners")
            
            if partners:
                partner = partners[0]
                print(f"\nFirst Delivery Partner:")
                print(f"  Name: {partner['user']['first_name']} {partner['user']['last_name']}")
                print(f"  Username: @{partner['user']['username']}")
                print(f"  Email: {partner['user']['email']}")
                print(f"  Phone: {partner['phone_number']}")
                print(f"  Vehicle: {partner['vehicle_type']}")
                print(f"  Status: {partner['status']}")
                print(f"  Verification: {partner['verification_status']}")
                print(f"  Available: {partner['is_available']}")
                print(f"  Completed Orders: {partner['completed_orders']}")
                
                # Check for undefined values
                undefined_fields = []
                user_fields = ['first_name', 'last_name', 'email']
                for field in user_fields:
                    if partner['user'][field] == 'undefined' or partner['user'][field] is None or partner['user'][field] == '':
                        undefined_fields.append(f"user.{field}")
                
                if undefined_fields:
                    print(f"- Found undefined fields: {undefined_fields}")
                    return False
                else:
                    print("+ No undefined values in critical fields!")
                    return True
            else:
                print("+ No delivery partners found (this is OK)")
                return True
        else:
            print(f"- API returned status {response.status_code}")
            print(f"Response: {response.data}")
            return False
            
    except Exception as e:
        print(f"- Error testing admin delivery partners: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_dashboard_delivery_metrics():
    """Test that admin dashboard includes delivery partner metrics"""
    print("\nTesting Admin Dashboard Delivery Metrics...")
    
    try:
        # Get admin user and token
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        # Test admin dashboard endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = client.get('/api/mvp/chefs/admin/dashboard/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            overview = data.get('overview', {})
            
            print("Dashboard Overview:")
            for key, value in overview.items():
                print(f"  {key}: {value}")
            
            # Check for delivery partner metrics
            delivery_fields = ['total_delivery_partners', 'verified_delivery_partners', 'delivery_partner_verification_rate']
            missing_fields = []
            
            for field in delivery_fields:
                if field not in overview:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"- Missing delivery partner fields: {missing_fields}")
                return False
            else:
                print("+ All delivery partner metrics present!")
                
                # Check values are reasonable
                total_partners = overview.get('total_delivery_partners', 0)
                verified_partners = overview.get('verified_delivery_partners', 0)
                verification_rate = overview.get('delivery_partner_verification_rate', 0)
                
                print(f"\nDelivery Partner Summary:")
                print(f"  Total Partners: {total_partners}")
                print(f"  Verified Partners: {verified_partners}")
                print(f"  Verification Rate: {verification_rate}%")
                
                return True
        else:
            print(f"- API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing dashboard metrics: {e}")
        return False

def test_unauthorized_access():
    """Test that non-admin users can't access delivery partner data"""
    print("\nTesting Unauthorized Access...")
    
    try:
        # Test without authentication
        client = APIClient()
        response = client.get('/api/mvp/chefs/admin/delivery-partners/')
        
        if response.status_code == 403:
            print("+ Correctly denied access without authentication")
            return True
        else:
            print(f"- Expected 403, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing unauthorized access: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ADMIN DELIVERY PARTNERS TEST")
    print("=" * 60)
    
    tests = [
        test_admin_delivery_partners_endpoint,
        test_admin_dashboard_delivery_metrics,
        test_unauthorized_access,
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
        print("+ All admin delivery partner tests passed!")
        print("The admin dashboard should now show delivery partner details.")
    else:
        print("- Some tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
