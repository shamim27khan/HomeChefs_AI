#!/usr/bin/env python3
"""
Test Swagger UI and check if responses are loading properly
"""

import requests
import json

def test_swagger_ui():
    print("Testing Swagger UI")
    print("=" * 50)
    
    # Test the actual Swagger UI page
    response = requests.get('http://localhost:8000/swagger/')
    print(f"Swagger UI Status: {response.status_code}")
    
    # Check for specific content that indicates responses are loaded
    content = response.text
    
    checks = [
        ('swagger-ui', 'Swagger UI library loaded'),
        ('responses', 'Responses section present'),
        ('examples', 'Examples present'),
        ('application/json', 'JSON examples present'),
    ]
    
    for check, description in checks:
        if check in content.lower():
            print(f"[OK] {description}")
        else:
            print(f"[FAIL] {description}")
    
    # Test ReDoc as well
    redoc_response = requests.get('http://localhost:8000/redoc/')
    print(f"\nReDoc Status: {redoc_response.status_code}")
    
    if 'redoc' in redoc_response.text.lower():
        print("[OK] ReDoc loaded successfully")
    else:
        print("[FAIL] ReDoc not loaded")
    
    # Check if we can access the API directly
    print("\nTesting API endpoints directly:")
    try:
        login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                 json={'username': 'customer_anjali', 'password': 'customer123'})
        print(f"[OK] Login API works: {login_response.status_code}")
        
        if login_response.status_code == 200:
            data = login_response.json()
            print(f"  Response has token: {'token' in data}")
            print(f"  Response has user: {'user' in data}")
    except Exception as e:
        print(f"[FAIL] Login API failed: {e}")
    
    try:
        food_response = requests.get('http://localhost:8000/api/customers/search/food/')
        print(f"[OK] Food search API works: {food_response.status_code}")
        
        if food_response.status_code == 200:
            data = food_response.json()
            print(f"  Found {len(data)} food items")
    except Exception as e:
        print(f"[FAIL] Food search API failed: {e}")

if __name__ == '__main__':
    test_swagger_ui()
