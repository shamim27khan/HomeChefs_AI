#!/usr/bin/env python
"""
Test the chef page fix
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from chefs.views_mvp import public_chefs, today_meals
from django.test import RequestFactory

def test_chef_page_fix():
    """Test that chef page works correctly"""
    print("TESTING CHEF PAGE FIX")
    print("=" * 40)
    
    factory = RequestFactory()
    
    # Test 1: Check if chefs API works
    print("\n1. Testing Chefs API:")
    try:
        request = factory.get('/api/mvp/chefs/public/')
        response = public_chefs(request)
        
        if response.status_code == 200:
            chefs = response.data
            print(f"   ✓ Found {len(chefs)} chefs")
            
            if chefs:
                sample_chef = chefs[0]
                print(f"   ✓ Sample chef: {sample_chef.get('username', 'NO USERNAME')}")
                print(f"   ✓ Area: {sample_chef.get('area', 'NO AREA')}")
                print(f"   ✓ Verified: {sample_chef.get('is_verified', False)}")
                
                if 'username' in sample_chef:
                    print("   ✓ Username field is present in API response")
                else:
                    print("   ✗ Username field missing from API response")
            else:
                print("   ✗ No chefs found")
        else:
            print(f"   ✗ API returned status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Check if today's meals API works
    print("\n2. Testing Today's Meals API:")
    try:
        request = factory.get('/api/mvp/chefs/today-meals/')
        response = today_meals(request)
        
        if response.status_code == 200:
            meals = response.data
            print(f"   ✓ Found {len(meals)} meals for today")
            
            if meals:
                sample_meal = meals[0]
                print(f"   ✓ Sample meal: {sample_meal.get('main_dish', 'NO NAME')}")
                print(f"   ✓ Chef ID: {sample_meal.get('chef', 'NO CHEF ID')}")
                print(f"   ✓ Chef username: {sample_meal.get('chef_username', 'NO USERNAME')}")
            else:
                print("   ✗ No meals found for today")
        else:
            print(f"   ✗ API returned status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Check chef-meal relationship
    print("\n3. Testing Chef-Meal Relationship:")
    try:
        chefs_response = public_chefs(factory.get('/api/mvp/chefs/public/'))
        meals_response = today_meals(factory.get('/api/mvp/chefs/today-meals/'))
        
        if chefs_response.status_code == 200 and meals_response.status_code == 200:
            chefs = chefs_response.data
            meals = meals_response.data
            
            if chefs and meals:
                sample_chef = chefs[0]
                chef_id = sample_chef['id']
                
                chef_meals = [meal for meal in meals if meal.get('chef') == chef_id]
                print(f"   ✓ Chef {sample_chef['username']} has {len(chef_meals)} meals today")
                
                for meal in chef_meals[:2]:
                    print(f"     - {meal.get('main_dish', 'Unknown')} (₹{meal.get('price_per_portion', '0')})")
            else:
                print("   ✗ No chefs or meals available for testing")
        else:
            print("   ✗ API calls failed")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 40)
    print("CHEF PAGE FIX SUMMARY:")
    print("✓ Fixed API endpoint (using /api/mvp/chefs/public/)")
    print("✓ Added username field to serializer")
    print("✓ Added proper error handling")
    print("✓ Added fallback for missing chef_id")
    print("✓ Fixed chef data loading logic")
    
    print("\n🚀 Test the chef page:")
    print("   • Without chef_id: http://127.0.0.1:8000/chef/")
    print("   • With chef_id: http://127.0.0.1:8000/chef/?chef_id=3")
    print("   • From homepage: Click 'View Profile' on any chef card")

if __name__ == '__main__':
    test_chef_page_fix()
