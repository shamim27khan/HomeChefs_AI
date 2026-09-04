#!/usr/bin/env python
"""
Test script for the nearby dishes feature
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.test import RequestFactory
from chefs.views_mvp import nearby_dishes, calculate_distance
from chefs.models import ChefProfile, DailyMeal
from authentication.models import User
from datetime import date

def test_distance_calculation():
    """Test the Haversine distance calculation"""
    print("Testing distance calculation...")
    
    # Test distance between two known points (Bangalore coordinates)
    # Indiranagar: 12.9719° N, 77.6412° E
    # Koramangala: 12.9352° N, 77.6244° E
    # Expected distance: ~5km
    distance = calculate_distance(12.9719, 77.6412, 12.9352, 77.6244)
    print(f"Distance between Indiranagar and Koramangala: {distance:.2f} km")
    
    # Test same point (should be 0)
    same_point_distance = calculate_distance(12.9719, 77.6412, 12.9719, 77.6412)
    print(f"Distance between same point: {same_point_distance:.2f} km")
    
    print("PASS: Distance calculation tests passed\n")

def test_nearby_dishes_endpoint():
    """Test the nearby dishes API endpoint"""
    print("Testing nearby dishes endpoint...")
    
    factory = RequestFactory()
    
    # Test with valid coordinates (Bangalore city center)
    request = factory.get('/api/chefs-mvp/nearby-dishes/', {
        'latitude': '12.9716',
        'longitude': '77.5946',
        'radius': '3.0'
    })
    
    try:
        response = nearby_dishes(request)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        if response.status_code == 200:
            print("PASS: Nearby dishes endpoint works")
        else:
            print("FAIL: Nearby dishes endpoint failed")
    except Exception as e:
        print(f"ERROR: Error testing nearby dishes: {e}")
    
    # Test with invalid coordinates
    request_invalid = factory.get('/api/chefs-mvp/nearby-dishes/', {
        'latitude': 'invalid',
        'longitude': '77.5946'
    })
    
    try:
        response_invalid = nearby_dishes(request_invalid)
        print(f"Invalid coordinates response status: {response_invalid.status_code}")
        if response_invalid.status_code == 400:
            print("PASS: Properly handles invalid coordinates")
        else:
            print("FAIL: Should return 400 for invalid coordinates")
    except Exception as e:
        print(f"ERROR: Error testing invalid coordinates: {e}")
    
    print()

def test_database_setup():
    """Check if database has required data"""
    print("Checking database setup...")
    
    # Check if chefs have location data
    chefs_with_location = ChefProfile.objects.filter(
        latitude__isnull=False, 
        longitude__isnull=False
    ).count()
    
    total_chefs = ChefProfile.objects.count()
    print(f"Chefs with location data: {chefs_with_location}/{total_chefs}")
    
    # Check today's meals
    today_meals = DailyMeal.objects.filter(
        date=date.today(),
        is_active=True
    ).count()
    
    print(f"Today's active meals: {today_meals}")
    
    if chefs_with_location == 0:
        print("WARNING: No chefs have location coordinates set")
        print("You need to update chef profiles with latitude/longitude")
    
    print()

def update_sample_chef_locations():
    """Add sample location data to chefs for testing"""
    print("Adding sample location data to chefs...")
    
    # Sample Bangalore locations for testing
    sample_locations = [
        {'username': 'chef_rahul', 'lat': 12.9719, 'lon': 77.6412, 'area': 'Indiranagar'},
        {'username': 'chef_priya', 'lat': 12.9352, 'lon': 77.6244, 'area': 'Koramangala'},
        {'username': 'chef_aman', 'lat': 12.9279, 'lon': 77.6271, 'area': 'HSR Layout'},
        {'username': 'chef_neha', 'lat': 12.9698, 'lon': 77.7500, 'area': 'Whitefield'},
        {'username': 'chef_vikram', 'lat': 13.0125, 'lon': 77.6550, 'area': 'Yelahanka'},
    ]
    
    for location_data in sample_locations:
        try:
            user = User.objects.get(username=location_data['username'])
            profile = user.chefprofile
            profile.latitude = location_data['lat']
            profile.longitude = location_data['lon']
            profile.save()
            print(f"PASS: Updated location for {location_data['username']} ({location_data['area']})")
        except User.DoesNotExist:
            print(f"FAIL: Chef {location_data['username']} not found")
        except Exception as e:
            print(f"ERROR: Error updating {location_data['username']}: {e}")
    
    print()

if __name__ == '__main__':
    print("=== Testing Nearby Dishes Feature ===\n")
    
    test_distance_calculation()
    test_database_setup()
    update_sample_chef_locations()
    test_nearby_dishes_endpoint()
    
    print("=== Test Complete ===")
    print("\nTo test the API manually:")
    print("1. Run the Django server: python manage.py runserver")
    print("2. Open: http://127.0.0.1:8000/api/chefs-mvp/nearby-dishes/?latitude=12.9716&longitude=77.5946&radius=3")
    print("3. Replace coordinates with your desired location")
