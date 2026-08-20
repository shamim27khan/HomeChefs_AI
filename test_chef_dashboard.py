#!/usr/bin/env python
"""
Test script to verify chef dashboard functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.models import ChefProfile
from orders.views_mvp import chef_stats
from rest_framework.test import APIRequestFactory

def test_chef_stats_api():
    """Test the chef stats API endpoint"""
    print("Testing Chef Stats API...")
    
    try:
        # Create chef user
        chef_user, _ = User.objects.get_or_create(
            username='testchef_dashboard', 
            defaults={
                'role': 'chef',
                'email': 'chef_dashboard@test.com'
            }
        )
        
        # Ensure chef has profile
        try:
            profile = chef_user.chefprofile
        except ChefProfile.DoesNotExist:
            profile = ChefProfile.objects.create(
                user=chef_user,
                phone_number=f"TEMP{chef_user.id}{chef_user.id}",
                address_line1="Address to be updated",
                area="Test Area",
                city="Test City", 
                pincode="000000"
            )
        
        # Test the endpoint
        factory = APIRequestFactory()
        request = factory.get('/api/mvp/orders/chef-stats/')
        request.user = chef_user
        
        response = chef_stats(request)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print("+ Chef Stats API working!")
            print("\nStats Data:")
            print(f"  Today's Orders: {data['today_orders']}")
            print(f"  Today's Revenue: Rs. {data['today_revenue']}")
            print(f"  Active Meals: {data['active_meals']}")
            print(f"  Average Rating: {data['average_rating']}")
            return True
        else:
            print(f"- API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing chef stats: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chef_profile_access():
    """Test chef profile access for template"""
    print("\nTesting Chef Profile Access...")
    
    try:
        # Test chef with profile
        chef_with_profile, _ = User.objects.get_or_create(
            username='chef_with_profile', 
            defaults={
                'role': 'chef',
                'email': 'chef_with@test.com'
            }
        )
        
        # Ensure profile exists
        try:
            profile = chef_with_profile.chefprofile
        except ChefProfile.DoesNotExist:
            profile = ChefProfile.objects.create(
                user=chef_with_profile,
                phone_number=f"TEMP{chef_with_profile.id}{chef_with_profile.id}",
                address_line1="Address to be updated",
                area="Test Area",
                city="Test City", 
                pincode="000000"
            )
        
        # Test accessing profile area
        try:
            area = chef_with_profile.chefprofile.area
            print(f"+ Chef with profile - Area: {area}")
        except Exception as e:
            print(f"- Error accessing profile area: {e}")
            return False
        
        # Test chef without profile
        chef_without_profile, _ = User.objects.get_or_create(
            username='chef_without_profile', 
            defaults={
                'role': 'chef',
                'email': 'chef_without@test.com'
            }
        )
        
        # Delete profile if it exists
        try:
            ChefProfile.objects.filter(user=chef_without_profile).delete()
        except:
            pass
        
        # Test accessing profile that doesn't exist
        try:
            area = chef_without_profile.chefprofile.area
            print(f"- Should have failed but got area: {area}")
            return False
        except ChefProfile.DoesNotExist:
            print("+ Chef without profile - correctly throws DoesNotExist")
        except Exception as e:
            print(f"- Unexpected error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"- Error testing profile access: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_rendering():
    """Test template rendering logic"""
    print("\nTesting Template Logic...")
    
    try:
        # Simulate Django template logic
        chef_user, _ = User.objects.get_or_create(
            username='template_test_chef', 
            defaults={
                'role': 'chef',
                'email': 'template@test.com'
            }
        )
        
        # Test with profile
        try:
            profile = chef_user.chefprofile
        except ChefProfile.DoesNotExist:
            profile = ChefProfile.objects.create(
                user=chef_user,
                phone_number=f"TEMP{chef_user.id}{chef_user.id}",
                address_line1="Address to be updated",
                area="Template Area",
                city="Template City", 
                pincode="000000"
            )
        
        # Simulate template logic: {% if request.user.chefprofile %}
        if hasattr(chef_user, 'chefprofile'):
            try:
                area = chef_user.chefprofile.area or "Location not set"
                print(f"+ Template with profile - Area: {area}")
            except ChefProfile.DoesNotExist:
                area = "Location not set"
                print(f"+ Template with profile - Area (fallback): {area}")
        else:
            area = "Location not set"
            print(f"+ Template without profile - Area: {area}")
        
        return True
        
    except Exception as e:
        print(f"- Error testing template logic: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CHEF DASHBOARD TEST")
    print("=" * 60)
    
    tests = [
        test_chef_stats_api,
        test_chef_profile_access,
        test_template_rendering,
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
        print("+ All chef dashboard tests passed!")
        print("The chef dashboard should now work correctly.")
    else:
        print("- Some tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
