#!/usr/bin/env python
"""
Test script to verify admin chef details functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.views_mvp import admin_chefs, public_chefs
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.authtoken.models import Token

def test_admin_chefs_endpoint():
    """Test the new admin chefs endpoint"""
    print("Testing Admin Chefs Endpoint...")
    
    try:
        # Get admin user and token
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        # Test with admin token
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = client.get('/api/mvp/chefs/admin/chefs/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            chefs = response.data
            print(f"+ Admin chefs endpoint working! Found {len(chefs)} chefs")
            
            # Test chef_amit specifically
            chef_amit = next((c for c in chefs if c['username'] == 'chef_amit'), None)
            if chef_amit:
                print("\nChef Amit Complete Data:")
                print(f"  ID: {chef_amit['id']}")
                print(f"  Name: {chef_amit['first_name']} {chef_amit['last_name']}")
                print(f"  Username: @{chef_amit['username']}")
                print(f"  Email: {chef_amit['email']}")
                print(f"  Member Since: {chef_amit['date_joined']}")
                
                if chef_amit['chef_info']:
                    info = chef_amit['chef_info']
                    print(f"  Phone: {info['phone_number']}")
                    print(f"  Area: {info['area']}")
                    print(f"  City: {info['city']}")
                    print(f"  Cuisines: {info['cuisine_specialties']}")
                    print(f"  Experience: {info['cooking_experience']} years")
                    print(f"  Verified: {info['is_verified']}")
                
                # Check no undefined values
                undefined_fields = []
                for key, value in chef_amit.items():
                    if key in ['first_name', 'last_name', 'email'] and (value == 'undefined' or value is None or value == ''):
                        undefined_fields.append(key)
                
                if undefined_fields:
                    print(f"\n- Warning: Found undefined fields: {undefined_fields}")
                    return False
                else:
                    print("\n+ No undefined values in critical fields!")
                    return True
            else:
                print("- Chef Amit not found")
                return False
        else:
            print(f"- API returned status {response.status_code}")
            print(f"Response: {response.data}")
            return False
            
    except Exception as e:
        print(f"- Error testing admin chefs: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_public_vs_admin_difference():
    """Test the difference between public and admin endpoints"""
    print("\nTesting Public vs Admin Endpoint Difference...")
    
    try:
        # Test public endpoint
        factory = APIRequestFactory()
        request = factory.get('/api/mvp/chefs/public/')
        public_response = public_chefs(request)
        
        # Test admin endpoint
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        admin_response = client.get('/api/mvp/chefs/admin/chefs/')
        
        if public_response.status_code == 200 and admin_response.status_code == 200:
            public_chef = public_response.data[0] if public_response.data else None
            admin_chef = admin_response.data[0] if admin_response.data else None
            
            if public_chef and admin_chef:
                print("Public endpoint fields:", list(public_chef.keys()))
                print("Admin endpoint fields:", list(admin_chef.keys()))
                
                # Check if admin has more fields
                admin_extra_fields = set(admin_chef.keys()) - set(public_chef.keys())
                if admin_extra_fields:
                    print(f"+ Admin endpoint has extra fields: {admin_extra_fields}")
                    return True
                else:
                    print("- No extra fields found in admin endpoint")
                    return False
            else:
                print("- No chefs found to compare")
                return False
        else:
            print(f"- Error: Public {public_response.status_code}, Admin {admin_response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error comparing endpoints: {e}")
        return False

def test_unauthorized_access():
    """Test that non-admin users can't access admin endpoint"""
    print("\nTesting Unauthorized Access...")
    
    try:
        # Test without authentication
        client = APIClient()
        response = client.get('/api/mvp/chefs/admin/chefs/')
        
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
    print("ADMIN CHEF DETAILS TEST")
    print("=" * 60)
    
    tests = [
        test_admin_chefs_endpoint,
        test_public_vs_admin_difference,
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
        print("+ All admin chef details tests passed!")
        print("The admin dashboard should now show complete chef information.")
    else:
        print("- Some tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
