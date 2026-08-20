#!/usr/bin/env python
"""
Test script to verify admin chef list displays correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.views_mvp import admin_chefs, admin_chef_verification
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.authtoken.models import Token

def test_admin_chefs_list():
    """Test the admin chefs list endpoint"""
    print("Testing Admin Chefs List Endpoint...")
    
    try:
        # Get admin user and token
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        # Test admin chefs endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = client.get('/api/mvp/chefs/admin/chefs/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            chefs = response.data
            print(f"+ Admin chefs list working! Found {len(chefs)} chefs")
            
            # Test chef_amit specifically
            chef_amit = next((c for c in chefs if c['username'] == 'chef_amit'), None)
            if chef_amit:
                print(f"\nChef Amit in List:")
                print(f"  Name: {chef_amit['first_name']} {chef_amit['last_name']}")
                print(f"  Email: {chef_amit['email']}")
                print(f"  Username: @{chef_amit['username']}")
                
                # Check for undefined values
                undefined_fields = []
                for key, value in chef_amit.items():
                    if key in ['first_name', 'last_name', 'email'] and (value == 'undefined' or value is None or value == ''):
                        undefined_fields.append(key)
                
                if undefined_fields:
                    print(f"- Found undefined fields: {undefined_fields}")
                    return False
                else:
                    print("+ No undefined values in critical fields!")
                    return True
            else:
                print("- Chef Amit not found in list")
                return False
        else:
            print(f"- API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing admin chefs list: {e}")
        return False

def test_pending_chefs_list():
    """Test the pending chefs list endpoint"""
    print("\nTesting Pending Chefs List Endpoint...")
    
    try:
        # Get admin user and token
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        # Test admin verification endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = client.get('/api/mvp/chefs/admin/verification/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            chefs = response.data
            print(f"+ Pending chefs list working! Found {len(chefs)} pending chefs")
            
            if chefs:
                chef = chefs[0]
                print(f"\nFirst Pending Chef:")
                print(f"  Name: {chef['first_name']} {chef['last_name']}")
                print(f"  Email: {chef['email']}")
                print(f"  Username: @{chef['username']}")
                print(f"  Verified: {chef['chef_info']['is_verified'] if chef['chef_info'] else 'No profile'}")
                
                # Check for undefined values
                undefined_fields = []
                for key, value in chef.items():
                    if key in ['first_name', 'last_name', 'email'] and (value == 'undefined' or value is None or value == ''):
                        undefined_fields.append(key)
                
                if undefined_fields:
                    print(f"- Found undefined fields: {undefined_fields}")
                    return False
                else:
                    print("+ No undefined values in critical fields!")
                    return True
            else:
                print("+ No pending chefs (this is OK)")
                return True
        else:
            print(f"- API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing pending chefs list: {e}")
        return False

def test_data_structure_consistency():
    """Test that both endpoints return consistent data structure"""
    print("\nTesting Data Structure Consistency...")
    
    try:
        # Get admin user and token
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Test both endpoints
        all_response = client.get('/api/mvp/chefs/admin/chefs/')
        pending_response = client.get('/api/mvp/chefs/admin/verification/')
        
        if all_response.status_code == 200 and pending_response.status_code == 200:
            all_chefs = all_response.data
            pending_chefs = pending_response.data
            
            # Check field consistency
            if all_chefs:
                all_fields = set(all_chefs[0].keys())
                if pending_chefs:
                    pending_fields = set(pending_chefs[0].keys())
                    
                    print(f"All chefs fields: {all_fields}")
                    print(f"Pending chefs fields: {pending_fields}")
                    
                    if all_fields == pending_fields:
                        print("+ Both endpoints return consistent data structure")
                        return True
                    else:
                        print("- Data structures differ between endpoints")
                        return False
                else:
                    print("+ All chefs endpoint has proper structure")
                    return True
            else:
                print("- No chefs found to test structure")
                return False
        else:
            print(f"- Error: All {all_response.status_code}, Pending {pending_response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing consistency: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ADMIN CHEF LIST DISPLAY FIX TEST")
    print("=" * 60)
    
    tests = [
        test_admin_chefs_list,
        test_pending_chefs_list,
        test_data_structure_consistency,
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
        print("+ All admin chef list tests passed!")
        print("The admin dashboard should now show chef names correctly.")
    else:
        print("- Some tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
