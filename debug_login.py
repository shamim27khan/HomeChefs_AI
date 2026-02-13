import requests
import json

def test_login():
    url = 'http://localhost:8000/api/auth/login/'
    data = {
        'username': 'customer_anjali',
        'password': 'customer123'
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"Response Length: {len(response.text)}")
        print(f"Response Preview: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"JSON Response: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == '__main__':
    test_login()
