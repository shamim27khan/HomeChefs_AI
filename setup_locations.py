#!/usr/bin/env python
"""
Setup location data for existing chefs and enable delivery
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.models import ChefProfile, DailyMeal
from datetime import date

def setup_chef_locations():
    """Setup location data for existing chefs"""
    print("Setting up chef locations and enabling delivery...")
    
    # Update chef_anjali (Indiranagar location)
    try:
        user = User.objects.get(username='chef_anjali')
        if hasattr(user, 'chefprofile'):
            profile = user.chefprofile
            profile.latitude = 12.9719  # Indiranagar
            profile.longitude = 77.6412
            profile.area = "Indiranagar"
            profile.city = "Bangalore"
            profile.save()
            print(f"Updated location for chef_anjali (Indiranagar)")
            
            # Enable delivery for their meals
            meals = DailyMeal.objects.filter(chef=user, date=date.today())
            for meal in meals:
                meal.delivery_available = True
                meal.delivery_radius = 5
                meal.save()
                print(f"Enabled delivery for {meal.main_dish}")
        else:
            print("chef_anjali has no profile")
    except User.DoesNotExist:
        print("chef_anjali not found")
    
    # Update chef_priya (Koramangala location)
    try:
        user = User.objects.get(username='chef_priya')
        if hasattr(user, 'chefprofile'):
            profile = user.chefprofile
            profile.latitude = 12.9352  # Koramangala
            profile.longitude = 77.6244
            profile.area = "Koramangala"
            profile.city = "Bangalore"
            profile.save()
            print(f"Updated location for chef_priya (Koramangala)")
            
            # Enable delivery for their meals
            meals = DailyMeal.objects.filter(chef=user, date=date.today())
            for meal in meals:
                meal.delivery_available = True
                meal.delivery_radius = 5
                meal.save()
                print(f"Enabled delivery for {meal.main_dish}")
        else:
            print("chef_priya has no profile")
    except User.DoesNotExist:
        print("chef_priya not found")

def test_nearby_search():
    """Test the nearby search with actual data"""
    print("\nTesting nearby search with Bangalore coordinates...")
    
    from chefs.views_mvp import nearby_dishes
    from django.test import RequestFactory
    
    factory = RequestFactory()
    
    # Test from Bangalore city center
    request = factory.get('/api/chefs-mvp/nearby-dishes/', {
        'latitude': '12.9716',
        'longitude': '77.5946',
        'radius': '10.0'  # 10km radius to catch both chefs
    })
    
    response = nearby_dishes(request)
    print(f"Response status: {response.status_code}")
    print(f"Dishes found: {response.data.get('total_found', 0)}")
    
    if response.data.get('dishes'):
        print("Available dishes:")
        for dish in response.data['dishes']:
            chef_name = dish.get('chef_username', dish.get('chef_info', {}).get('username', 'Unknown'))
            print(f"  - {dish['main_dish']} by {chef_name} ({dish['distance_km']}km away)")
    
    # Test from closer to Indiranagar
    request2 = factory.get('/api/chefs-mvp/nearby-dishes/', {
        'latitude': '12.9719',
        'longitude': '77.6412',
        'radius': '3.0'  # 3km radius
    })
    
    response2 = nearby_dishes(request2)
    print(f"\nFrom Indiranagar (3km radius):")
    print(f"Dishes found: {response2.data.get('total_found', 0)}")
    
    if response2.data.get('dishes'):
        print("Available dishes:")
        for dish in response2.data['dishes']:
            chef_name = dish.get('chef_username', dish.get('chef_info', {}).get('username', 'Unknown'))
            print(f"  - {dish['main_dish']} by {chef_name} ({dish['distance_km']}km away)")

if __name__ == '__main__':
    setup_chef_locations()
    test_nearby_search()
    print("\nSetup complete! You can now test the API at:")
    print("http://127.0.0.1:8000/api/chefs-mvp/nearby-dishes/?latitude=12.9716&longitude=77.5946&radius=3")
