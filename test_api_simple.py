import requests
import json

API_BASE = 'http://localhost:8000/api'

def test_api():
    print("Testing HomeChefs API...")
    
    # Test public chefs endpoint
    try:
        response = requests.get(f'{API_BASE}/chefs/public/')
        print(f"\n1. Public Chefs API:")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            chefs = response.json()
            print(f"   Number of chefs: {len(chefs)}")
            if chefs:
                print(f"   First chef: {chefs[0]['username']} - Rating: {chefs[0]['rating']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test public food search
    try:
        response = requests.get(f'{API_BASE}/customers/search/food/')
        print(f"\n2. Food Search API:")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            foods = response.json()
            print(f"   Number of food items: {len(foods)}")
            if foods:
                print(f"   First food: {foods[0]['name']} - Price: {foods[0]['price']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*50)
    print("API Testing Complete!")
    print("\nFrontend Access:")
    print("1. Open frontend/index.html in your browser")
    print("2. Use the sample credentials to test different user roles")
    print("\nAdmin Panel:")
    print("URL: http://localhost:8000/admin/")
    print("Username: admin, Password: admin123")

if __name__ == '__main__':
    test_api()
