import requests
import json

def test_register():
    url = 'http://localhost:8000/api/auth/register/'
    data = {
        'username': 'testuser' + str(int(time.time())),
        'email': 'test@example.com',
        'password': 'test12345',
        'confirm_password': 'test12345',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'customer'
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        if response.status_code == 201:
            json_data = response.json()
            print(f"Registration Successful!")
            print(f"User: {json_data['user']['username']}")
            print(f"Token: {json_data['token'][:20]}...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request Error: {e}")

import time
if __name__ == '__main__':
    test_register()
