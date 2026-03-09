#!/usr/bin/env python
"""
Test the chef page data loading
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

def test_chef_page_data():
    """Test that chef page data loads correctly"""
    print("TESTING CHEF PAGE DATA LOADING")
    print("=" * 40)
    
    factory = RequestFactory()
    
    # Test 1: Check chefs API
    print("\n1. Testing Chefs API:")
    try:
        request = factory.get('/api/mvp/chefs/public/')
        response = public_chefs(request)
        
        if response.status_code == 200:
            chefs = response.data
            print(f"   Found {len(chefs)} chefs")
            
            if chefs:
                sample_chef = chefs[0]
                print(f"   Sample chef: {sample_chef.get('username', 'NO USERNAME')}")
                print(f"   Area: {sample_chef.get('area', 'NO AREA')}")
                print(f"   Specialties: {sample_chef.get('cuisine_specialties', 'NO SPECIALTIES')}")
                print(f"   Experience: {sample_chef.get('cooking_experience', 'NO EXPERIENCE')}")
                print(f"   Rating: {sample_chef.get('average_rating', 'NO RATING')}")
                print(f"   Verified: {sample_chef.get('is_verified', 'NOT VERIFIED')}")
                
                # Test 2: Check today's meals for this chef
                print(f"\n2. Testing Today's Meals for Chef {sample_chef['username']}:")
                meals_request = factory.get('/api/mvp/chefs/today-meals/')
                meals_response = today_meals(meals_request)
                
                if meals_response.status_code == 200:
                    meals = meals_response.data
                    chef_meals = [meal for meal in meals if meal.get('chef') == sample_chef['id']]
                    print(f"   Found {len(chef_meals)} meals for this chef")
                    
                    for meal in chef_meals[:2]:
                        print(f"     - {meal.get('main_dish', 'Unknown')} (₹{meal.get('price_per_portion', '0')})")
                else:
                    print(f"   Error loading meals: {meals_response.status_code}")
                
            else:
                print("   No chefs found")
        else:
            print(f"   API returned status {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 40)
    print("EXPECTED CHEF PAGE BEHAVIOR:")
    print("1. Page loads with 'Loading...' text")
    print("2. JavaScript calls API to get chef data")
    print("3. DOM elements are updated with real data")
    print("4. 'Loading...' should be replaced with actual values")
    
    print("\n🔧 DEBUGGING TIPS:")
    print("1. Open browser developer tools (F12)")
    print("2. Go to Console tab")
    print("3. Look for JavaScript errors")
    print("4. Check Network tab for API calls")
    print("5. Verify API responses contain data")
    
    print("\n🚀 Test URLs:")
    print("   • http://127.0.0.1:8000/chef/?chef_id=3")
    print("   • http://127.0.0.1:8000/chef/?chef_id=11")
    print("   • http://127.0.0.1:8000/api/mvp/chefs/public/")

if __name__ == '__main__':
    test_chef_page_data()
