#!/usr/bin/env python
"""
Test script to verify chef profile data is correctly returned
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.views_mvp import chef_profile
from rest_framework.test import APIRequestFactory

def test_chef_profile_data():
    """Test the chef profile API returns correct data"""
    print("Testing Chef Profile Data...")
    
    try:
        # Get the chef_amit user
        chef_user = User.objects.get(username='chef_amit')
        print(f"Testing with user: {chef_user.username}")
        
        # Test the chef profile API
        factory = APIRequestFactory()
        request = factory.get('/api/mvp/chefs/profile/')
        request.user = chef_user
        
        response = chef_profile(request)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print("+ Chef Profile API working!")
            print("\nProfile Data:")
            print(f"  Name: {data.get('full_name', 'N/A')}")
            print(f"  Username: @{data.get('username', 'N/A')}")
            print(f"  Email: {data.get('email', 'N/A')}")
            print(f"  Phone: {data.get('phone_number', 'N/A')}")
            print(f"  Member Since: {data.get('created_at', 'N/A')}")
            print(f"  Area: {data.get('area', 'N/A')}")
            print(f"  City: {data.get('city', 'N/A')}")
            print(f"  Experience: {data.get('cooking_experience', 'N/A')} years")
            print(f"  Specialties: {data.get('cuisine_specialties', 'N/A')}")
            print(f"  Verified: {data.get('is_verified', 'N/A')}")
            
            # Check for undefined values in critical fields
            undefined_fields = []
            critical_fields = ['first_name', 'last_name', 'email', 'phone_number']
            for key, value in data.items():
                if key in critical_fields and (value == 'undefined' or value is None or value == ''):
                    undefined_fields.append(key)
            
            if undefined_fields:
                print(f"\n- Warning: Found undefined/empty critical fields: {undefined_fields}")
                return False
            else:
                print("\n+ No undefined values in critical fields!")
                return True
        else:
            print(f"- API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing chef profile: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_chefs():
    """Test profile data for multiple chefs"""
    print("\nTesting Multiple Chefs...")
    
    try:
        chef_users = User.objects.filter(role='chef')
        print(f"Found {chef_users.count()} chef users")
        
        all_good = True
        for chef in chef_users:
            try:
                factory = APIRequestFactory()
                request = factory.get('/api/mvp/chefs/profile/')
                request.user = chef
                
                response = chef_profile(request)
                
                if response.status_code == 200:
                    data = response.data
                    name = data.get('full_name', chef.username)
                    email = data.get('email', 'N/A')
                    
                    # Check for undefined values
                    has_undefined = any(
                        value == 'undefined' or value is None 
                        for key, value in data.items() 
                        if key in ['first_name', 'last_name', 'email', 'phone_number']
                    )
                    
                    if has_undefined:
                        print(f"- {chef.username}: Has undefined values")
                        all_good = False
                    else:
                        print(f"+ {chef.username}: {name} - {email}")
                else:
                    print(f"- {chef.username}: API error {response.status_code}")
                    all_good = False
                    
            except Exception as e:
                print(f"- {chef.username}: Error {e}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"- Error testing multiple chefs: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CHEF PROFILE DATA TEST")
    print("=" * 60)
    
    tests = [
        test_chef_profile_data,
        test_multiple_chefs,
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
        print("+ All chef profile data tests passed!")
        print("The chef profile should now display correctly.")
    else:
        print("- Some tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
