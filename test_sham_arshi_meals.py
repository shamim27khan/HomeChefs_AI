#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.test import RequestFactory
from chefs.views_mvp import today_meals, nearby_dishes

def test_meals_display():
    """Test that Sham Khan and Arshi meals are showing up"""
    print("Testing meal display for Sham Khan and Arshi...")
    
    try:
        factory = RequestFactory()
        
        # Test today's meals
        print("\n=== TODAY'S MEALS API ===")
        request = factory.get('/api/mvp/chefs/today-meals/')
        response = today_meals(request)
        
        if response.status_code == 200:
            meals = response.data
            print(f"Total meals found: {len(meals)}")
            
            sham_found = False
            arshi_found = False
            
            for meal in meals:
                chef_name = meal.get('chef_username', 'unknown')
                meal_name = meal.get('main_dish', 'unknown')
                price = meal.get('price_per_portion', 0)
                orderable = meal.get('is_orderable', False)
                
                print(f"  - {meal_name} by {chef_name} (Price: {price}, Orderable: {orderable})")
                
                if chef_name == 'sham':
                    sham_found = True
                    print(f"    ✓ Sham Khan meal found!")
                elif chef_name == 'Arshi':
                    arshi_found = True
                    print(f"    ✓ Arshi meal found!")
            
            print(f"\nSham Khan meals showing: {sham_found}")
            print(f"Arshi meals showing: {arshi_found}")
        else:
            print(f"ERROR: Today's meals API returned {response.status_code}")
        
        # Test nearby dishes
        print("\n=== NEARBY DISHES API ===")
        request = factory.get('/api/mvp/chefs/nearby-dishes/?latitude=12.9716&longitude=77.5946&radius=10')
        response = nearby_dishes(request)
        
        if response.status_code == 200:
            data = response.data
            dishes = data.get('dishes', [])
            print(f"Total dishes found: {len(dishes)}")
            
            sham_found = False
            arshi_found = False
            
            for dish in dishes:
                chef_name = dish.get('chef_username', 'unknown')
                dish_name = dish.get('main_dish', 'unknown')
                distance = dish.get('distance', 'unknown')
                
                print(f"  - {dish_name} by {chef_name} (Distance: {distance} km)")
                
                if chef_name == 'sham':
                    sham_found = True
                    print(f"    ✓ Sham Khan dish found!")
                elif chef_name == 'Arshi':
                    arshi_found = True
                    print(f"    ✓ Arshi dish found!")
            
            print(f"\nSham Khan dishes showing: {sham_found}")
            print(f"Arshi dishes showing: {arshi_found}")
        else:
            print(f"ERROR: Nearby dishes API returned {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    test_meals_display()
