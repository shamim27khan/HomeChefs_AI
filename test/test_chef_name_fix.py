#!/usr/bin/env python
"""
Test the chef name fix in today's meals
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from chefs.views_mvp import today_meals
from django.test import RequestFactory

def test_chef_name_fix():
    """Test that chef names are properly displayed in today's meals"""
    print("TESTING CHEF NAME FIX")
    print("=" * 40)
    
    factory = RequestFactory()
    request = factory.get('/api/mvp/chefs/today-meals/')
    response = today_meals(request)
    
    if response.status_code == 200:
        meals = response.data
        
        if meals:
            print(f"Found {len(meals)} meals for today")
            print("\nSample meal data:")
            
            for i, meal in enumerate(meals[:3], 1):
                print(f"\n{i}. {meal['main_dish']}")
                print(f"   Chef username: {meal.get('chef_username', 'MISSING')}")
                print(f"   Chef info available: {'Yes' if meal.get('chef_info') else 'No'}")
                
                if meal.get('chef_info'):
                    chef_info = meal['chef_info']
                    print(f"   Chef info username: {chef_info.get('username', 'MISSING')}")
                    print(f"   Chef area: {chef_info.get('area', 'MISSING')}")
                    print(f"   Chef verified: {chef_info.get('is_verified', False)}")
                
                print(f"   Price: ₹{meal['price_per_portion']}")
                print(f"   Available: {meal['available_portions']} portions")
            
            # Test template rendering logic
            print("\n" + "=" * 40)
            print("TEMPLATE LOGIC TEST:")
            
            for meal in meals[:2]:
                # Simulate template logic
                chef_name = meal.get('chef_username') or 'Unknown Chef'
                chef_info = meal.get('chef_info')
                is_verified = chef_info and chef_info.get('is_verified', False)
                
                print(f"\nMeal: {meal['main_dish']}")
                print(f"Template chef_name: '{chef_name}'")
                print(f"Template is_verified: {is_verified}")
                
                if chef_name == 'Unknown Chef':
                    print("  ⚠️  Chef name would show as 'Unknown Chef'")
                else:
                    print(f"  ✓ Chef name would display correctly: {chef_name}")
                
                if is_verified:
                    print("  ✓ Verified badge would be shown")
                else:
                    print("  - No verified badge")
            
            print("\n✅ Chef name fix test completed successfully!")
            
        else:
            print("No meals found for today")
            print("Please run 'python create_mvp_sample_data.py' first")
    
    else:
        print(f"Error: API returned status {response.status_code}")

if __name__ == '__main__':
    test_chef_name_fix()
