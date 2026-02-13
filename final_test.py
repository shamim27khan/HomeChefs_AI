import requests
import json

def test_all_endpoints():
    base_url = 'http://localhost:8000/api'
    
    print("Testing HomeChefs API Endpoints")
    print("=" * 50)
    
    # Test 1: Public Chefs
    try:
        response = requests.get(f'{base_url}/chefs/public/')
        print(f"[OK] Public Chefs: {response.status_code} - Found {len(response.json())} chefs")
    except Exception as e:
        print(f"[FAIL] Public Chefs: {e}")
    
    # Test 2: Food Search
    try:
        response = requests.get(f'{base_url}/customers/search/food/')
        print(f"[OK] Food Search: {response.status_code} - Found {len(response.json())} items")
    except Exception as e:
        print(f"[FAIL] Food Search: {e}")
    
    # Test 3: Login
    try:
        response = requests.post(f'{base_url}/auth/login/', json={
            'username': 'customer_anjali',
            'password': 'customer123'
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"[OK] Login: {response.status_code} - Token: {token[:10]}...")
            
            # Test 4: Authenticated endpoint with token
            headers = {'Authorization': f'Token {token}'}
            try:
                response = requests.get(f'{base_url}/customers/favorite-chefs/', headers=headers)
                print(f"[OK] Favorite Chefs: {response.status_code} - {len(response.json())} favorites")
            except Exception as e:
                print(f"[FAIL] Favorite Chefs: {e}")
        else:
            print(f"[FAIL] Login: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Login: {e}")
    
    # Test 5: Registration
    try:
        import time
        response = requests.post(f'{base_url}/auth/register/', json={
            'username': f'testuser{int(time.time())}',
            'email': 'test@example.com',
            'password': 'test12345',
            'confirm_password': 'test12345',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'customer'
        })
        if response.status_code == 201:
            print(f"[OK] Registration: {response.status_code} - User created")
        else:
            print(f"[FAIL] Registration: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Registration: {e}")
    
    # Test 6: Swagger Documentation
    try:
        response = requests.get('http://localhost:8000/swagger/')
        print(f"[OK] Swagger Docs: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Swagger Docs: {e}")
    
    # Test 7: ReDoc Documentation
    try:
        response = requests.get('http://localhost:8000/redoc/')
        print(f"[OK] ReDoc: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] ReDoc: {e}")
    
    # Test 8: Frontend Home Page
    try:
        response = requests.get('http://localhost:8000/')
        print(f"[OK] Frontend Home: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Frontend Home: {e}")
    
    # Test 9: Test Page
    try:
        response = requests.get('http://localhost:8000/test/')
        print(f"[OK] Test Page: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Test Page: {e}")
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("\nAccess URLs:")
    print("Frontend: http://localhost:8000/")
    print("Test Page: http://localhost:8000/test/")
    print("Swagger: http://localhost:8000/swagger/")
    print("ReDoc: http://localhost:8000/redoc/")
    print("Admin: http://localhost:8000/admin/")

if __name__ == '__main__':
    test_all_endpoints()
