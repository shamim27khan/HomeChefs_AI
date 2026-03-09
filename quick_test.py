import requests

# Test login
r = requests.post('http://127.0.0.1:8000/api/auth/login/', json={'username':'chef_anjali','password':'chef123'})
print(f'Login: {r.status_code}')
if r.status_code == 200:
    token = r.json().get('token')
    print(f'Token: Yes')
    
    # Test chef endpoint with auth
    headers = {'Authorization': f'Token {token}'}
    r = requests.get('http://127.0.0.1:8000/api/mvp/chefs/daily-meals/', headers=headers)
    print(f'Chef daily meals: {r.status_code} - {len(r.json())} meals')
else:
    print('Token: No')
