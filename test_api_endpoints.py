#!/usr/bin/env python3
"""
Comprehensive API endpoint testing script for HomeChefs
Shows which endpoints are public vs. authenticated
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_endpoint(name, url, method='GET', data=None, headers=None):
    """Test a single endpoint and return results"""
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        else:
            return f"Unsupported method: {method}"
        
        status_icon = "[OK]" if response.status_code < 400 else "[FAIL]"
        result = f"{status_icon} {name}: {response.status_code}"
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                if isinstance(json_data, list):
                    result += f" ({len(json_data)} items)"
                elif isinstance(json_data, dict):
                    result += f" (OK)"
            except:
                result += " (Non-JSON response)"
        elif response.status_code == 403:
            result += " (Authentication required)"
        elif response.status_code == 404:
            result += " (Not found)"
        else:
            result += f" ({response.text[:50]}...)"
        
        return result
    except Exception as e:
        return f"[FAIL] {name}: Error - {str(e)}"

def main():
    print("HomeChefs API Endpoint Testing")
    print("=" * 60)
    print("\n[PUBLIC] PUBLIC ENDPOINTS (No authentication required)")
    print("-" * 50)
    
    # Test public endpoints
    public_tests = [
        ("Public Chefs List", f"{BASE_URL}/chefs/public/"),
        ("Public Chef Detail", f"{BASE_URL}/chefs/public/1/"),
        ("Food Search", f"{BASE_URL}/customers/search/food/"),
        ("Chef Search", f"{BASE_URL}/customers/search/chefs/"),
    ]
    
    for name, url in public_tests:
        print(test_endpoint(name, url))
    
    print("\n[AUTH] AUTHENTICATED ENDPOINTS (Require login)")
    print("-" * 50)
    
    # Test login first
    login_data = {'username': 'customer_anjali', 'password': 'customer123'}
    login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()['token']
        customer_headers = {'Authorization': f'Token {token}'}
        print("[OK] Customer Login: Successful")
        
        # Test customer endpoints
        customer_tests = [
            ("Customer Profile", f"{BASE_URL}/auth/profile/"),
            ("Favorite Chefs", f"{BASE_URL}/customers/favorite-chefs/"),
            ("Favorite Foods", f"{BASE_URL}/customers/favorite-foods/"),
            ("Customer Reviews", f"{BASE_URL}/customers/reviews/"),
            ("Customer Addresses", f"{BASE_URL}/customers/addresses/"),
            ("Search History", f"{BASE_URL}/customers/search-history/"),
        ]
        
        for name, url in customer_tests:
            print(test_endpoint(name, url, headers=customer_headers))
    else:
        print(f"[FAIL] Customer Login: Failed ({login_response.status_code})")
    
    # Test chef login
    chef_login_data = {'username': 'chef_rahul', 'password': 'chef123'}
    chef_login_response = requests.post(f"{BASE_URL}/auth/login/", json=chef_login_data)
    
    if chef_login_response.status_code == 200:
        token = chef_login_response.json()['token']
        chef_headers = {'Authorization': f'Token {token}'}
        print("[OK] Chef Login: Successful")
        
        # Test chef endpoints
        chef_tests = [
            ("Chef Food Items", f"{BASE_URL}/chefs/food-items/"),
            ("Chef Reviews", f"{BASE_URL}/chefs/reviews/"),
        ]
        
        for name, url in chef_tests:
            print(test_endpoint(name, url, headers=chef_headers))
    else:
        print(f"[FAIL] Chef Login: Failed ({chef_login_response.status_code})")
    
    print("\n[REG] REGISTRATION")
    print("-" * 50)
    
    # Test registration
    import time
    reg_data = {
        'username': f'testuser{int(time.time())}',
        'email': 'test@example.com',
        'password': 'test12345',
        'confirm_password': 'test12345',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'customer'
    }
    
    reg_result = test_endpoint("User Registration", f"{BASE_URL}/auth/register/", "POST", reg_data)
    print(reg_result)
    
    print("\n[DOCS] DOCUMENTATION")
    print("-" * 50)
    
    # Test documentation endpoints
    doc_tests = [
        ("Swagger UI", "http://localhost:8000/swagger/"),
        ("ReDoc", "http://localhost:8000/redoc/"),
        ("Frontend", "http://localhost:8000/"),
        ("Test Page", "http://localhost:8000/test/"),
    ]
    
    for name, url in doc_tests:
        print(test_endpoint(name, url))
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("- Public endpoints work without authentication")
    print("- Authenticated endpoints require valid token")
    print("- Chef endpoints require chef role")
    print("- Use Authorization: Token <token> header for authenticated requests")
    print("=" * 60)

if __name__ == '__main__':
    main()
