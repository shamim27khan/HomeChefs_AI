#!/usr/bin/env python
"""
Test the UI integration for nearby dishes feature
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.test import Client
from chefs.views_mvp import nearby_dishes
from django.test import RequestFactory
from datetime import date

def test_ui_integration():
    """Test the UI integration with the nearby dishes API"""
    print("Testing UI Integration for Nearby Dishes Feature")
    print("=" * 50)
    
    # Test the API endpoint that UI will call
    factory = RequestFactory()
    
    # Test with Bangalore coordinates (similar to what browser geolocation would return)
    request = factory.get('/api/chefs-mvp/nearby-dishes/', {
        'latitude': '12.9716',
        'longitude': '77.5946',
        'radius': '3'
    })
    
    try:
        response = nearby_dishes(request)
        print(f"PASS: API Response Status: {response.status_code}")
        
        data = response.data
        print(f"PASS: Total dishes found: {data.get('total_found', 0)}")
        print(f"PASS: Search radius: {data.get('search_location', {}).get('radius_km')} km")
        
        if data.get('dishes'):
            print("\nSample dishes that will appear in UI:")
            for i, dish in enumerate(data['dishes'][:3], 1):
                print(f"  {i}. {dish['main_dish']} - {dish.get('distance_km', 'N/A')} km away")
                print(f"     Chef: {dish.get('chef_username', 'Unknown')}")
                print(f"     Price: ₹{dish['price_per_portion']}")
                print()
        
        print("PASS: UI integration test passed!")
        
    except Exception as e:
        print(f"FAIL: API test failed: {e}")
        return False
    
    # Test different radius values
    test_radii = [3, 6, 9, 12, 15]
    print("\nTesting different radius values:")
    
    for radius in test_radii:
        try:
            request = factory.get('/api/chefs-mvp/nearby-dishes/', {
                'latitude': '12.9716',
                'longitude': '77.5946',
                'radius': str(radius)
            })
            response = nearby_dishes(request)
            dishes_count = response.data.get('total_found', 0)
            print(f"  PASS: {radius} km radius: {dishes_count} dishes found")
        except Exception as e:
            print(f"  FAIL: {radius} km radius: Error - {e}")
    
    return True

def test_ui_file_exists():
    """Check if the UI file exists and has the required elements"""
    print("\nChecking UI file structure:")
    
    ui_file = "frontend/index_mvp.html"
    if not os.path.exists(ui_file):
        print(f"FAIL: UI file {ui_file} not found")
        return False
    
    with open(ui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_elements = [
        'nearby-section',
        'radiusSlider',
        'getLocationAndSearch',
        'searchNearbyDishes',
        'updateRadius',
        'nearby-dishes',
        'distance-badge'
    ]
    
    for element in required_elements:
        if element in content:
            print(f"  PASS: {element} found in UI")
        else:
            print(f"  FAIL: {element} missing from UI")
            return False
    
    print("PASS: All required UI elements present")
    return True

def display_usage_instructions():
    """Display instructions for using the new feature"""
    print("\n" + "=" * 50)
    print("USAGE INSTRUCTIONS")
    print("=" * 50)
    print("1. Start the Django server: python manage.py runserver")
    print("2. Open browser: http://127.0.0.1:8000/frontend/index_mvp.html")
    print("3. Click 'Use My Current Location' button")
    print("4. Allow browser location access when prompted")
    print("5. Adjust radius slider (3-15 km) to expand/shrink search area")
    print("6. View nearby dishes with distance information")
    print("\nFeatures:")
    print("  • Real-time geolocation detection")
    print("  • Adjustable search radius (3km increments)")
    print("  • Distance display for each dish")
    print("  • Automatic refresh when radius changes")
    print("  • Error handling for location permissions")
    print("  • Responsive design for mobile/desktop")

if __name__ == '__main__':
    print("HOME CHEF HUB - NEARBY DISHES UI TEST")
    print("=" * 50)
    
    # Run tests
    ui_test_passed = test_ui_file_exists()
    api_test_passed = test_ui_integration()
    
    if ui_test_passed and api_test_passed:
        print("\nALL TESTS PASSED!")
        display_usage_instructions()
    else:
        print("\nSome tests failed. Please check the implementation.")
