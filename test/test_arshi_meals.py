#!/usr/bin/env python
"""
Test script to check Arshi's meals visibility to customers
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.models import DailyMeal
from chefs.views_mvp import today_meals
from rest_framework.test import APIRequestFactory

def test_arshi_meals():
    """Test Arshi's meals and their visibility"""
    print("=" * 60)
    print("ARSHI'S MEALS VISIBILITY TEST")
    print("=" * 60)
    
    try:
        # Check Arshi's profile
        print("1. Checking Arshi's Profile...")
        arshi = User.objects.get(username='Arshi')
        print(f"   User: {arshi.username} ({arshi.first_name} {arshi.last_name})")
        print(f"   Role: {arshi.role}")
        print(f"   Chef Verified: {arshi.chef_profile.is_verified}")
        
        # Check Arshi's meals in database
        print("\n2. Checking Arshi's Meals in Database...")
        meals = DailyMeal.objects.filter(chef=arshi)
        print(f"   Total meals: {meals.count()}")
        
        for meal in meals:
            print(f"   - {meal.main_dish} ({meal.meal_type})")
            print(f"     Date: {meal.date}")
            print(f"     Available portions: {meal.extra_portions}")
            print(f"     Price: {meal.price_per_portion}")
            print(f"     Is available: {getattr(meal, 'is_available', 'N/A')}")
            print()
        
        # Check available meals API
        print("3. Testing Today's Meals API...")
        factory = APIRequestFactory()
        request = factory.get('/api/mvp/meals/today/')
        response = today_meals(request)
        
        print(f"   API Status: {response.status_code}")
        
        if response.status_code == 200:
            meals_data = response.data
            print(f"   Total available meals from API: {len(meals_data)}")
            
            # Check if Arshi's meals are in the response
            arshi_meals_in_api = [meal for meal in meals_data if meal['chef']['username'] == 'Arshi']
            print(f"   Arshi's meals in API response: {len(arshi_meals_in_api)}")
            
            if arshi_meals_in_api:
                print("   Arshi's meals found in API:")
                for meal in arshi_meals_in_api:
                    print(f"     - {meal['main_dish']} by {meal['chef']['username']}")
                    print(f"       Date: {meal.get('date', 'N/A')}")
                    print(f"       Available: {meal.get('extra_portions', 'N/A')} portions")
            else:
                print("   ❌ Arshi's meals NOT found in API response!")
                
                # Show some meals that are in the API for comparison
                if meals_data:
                    print("   Sample meals in API:")
                    for meal in meals_data[:3]:
                        print(f"     - {meal['main_dish']} by {meal['chef']['username']}")
        else:
            print(f"   ❌ API Error: {response.data}")
        
        # Check meal filtering criteria
        print("\n4. Checking Meal Filtering Criteria...")
        today_meals_db = DailyMeal.objects.filter(chef=arshi, date='2026-04-29')
        print(f"   Arshi's meals for today (2026-04-29): {today_meals_db.count()}")
        
        for meal in today_meals_db:
            print(f"   - {meal.main_dish} ({meal.meal_type})")
            print(f"     Available: {meal.extra_portions} portions")
        
        # Check if there are any filtering issues
        print("\n5. Checking Potential Issues...")
        
        # Check chef verification
        if not arshi.chef_profile.is_verified:
            print("   [X] Chef is NOT verified - meals won't show to customers")
        else:
            print("   [OK] Chef is verified")
        
        # Check meal dates
        today = '2026-04-29'
        today_meals_count = DailyMeal.objects.filter(chef=arshi, date=today).count()
        if today_meals_count == 0:
            print(f"   [X] No meals for today ({today}) - only today's meals show to customers")
        else:
            print(f"   [OK] Has {today_meals_count} meals for today")
        
        # Check meal availability
        unavailable_meals = DailyMeal.objects.filter(chef=arshi)
        if hasattr(DailyMeal, 'is_available'):
            unavailable_count = unavailable_meals.filter(is_available=False).count()
            if unavailable_count > 0:
                print(f"   [X] {unavailable_count} meals marked as unavailable")
            else:
                print("   [OK] All meals appear to be available")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    success = test_arshi_meals()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)
    
    if success:
        print("[OK] Test completed successfully")
        print("Check the output above to identify why Arshi's meals aren't showing")
    else:
        print("[ERROR] Test failed with errors")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
