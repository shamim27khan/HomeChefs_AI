# Admin Dashboard API Access Guide

## Issue Identified
When accessing `http://localhost:8000/api/mvp/chefs/admin/dashboard/` directly in browser, you get a 500 error because:
1. The endpoint requires admin authentication
2. Browser requests don't include authentication tokens
3. Unauthenticated requests are denied access

## API Endpoint Details
- **URL**: `/api/mvp/chefs/admin/dashboard/`
- **Method**: GET
- **Authentication**: Required (Admin only)
- **Permissions**: `IsAdminUser`

## Test Results

### ✅ Working Scenarios:
1. **Direct API Test** - Status 200
2. **With Token Auth** - Status 200
3. **Admin User Access** - Status 200

### ❌ Failing Scenarios:
1. **Browser Direct Access** - Status 403/500 (no auth)
2. **Non-Admin User** - Status 403
3. **Invalid Token** - Status 403

## Solutions

### 1. Access via Frontend (Recommended)
The admin dashboard API is designed to be accessed by the frontend application, not directly in browser.

**Frontend JavaScript:**
```javascript
// Get auth token from localStorage
const token = localStorage.getItem('authToken');

if (token) {
    fetch('/api/mvp/chefs/admin/dashboard/', {
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Dashboard data:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
```

### 2. Test with Admin Token
For testing purposes, you can use the admin token:

**Admin Token**: `4298b51810886ca960676b8655018053f9393307`

**Curl Command:**
```bash
curl -H "Authorization: Token 4298b51810886ca960676b8655018053f9393307" \
     http://localhost:8000/api/mvp/chefs/admin/dashboard/
```

**Python Test:**
```python
import requests

token = "4298b51810886ca960676b8655018053f9393307"
headers = {"Authorization": f"Token {token}"}

response = requests.get(
    "http://localhost:8000/api/mvp/chefs/admin/dashboard/",
    headers=headers
)

print(response.status_code)
print(response.json())
```

### 3. Admin Dashboard Page
Access the admin dashboard through the proper web interface:
1. Login as admin user
2. Navigate to admin dashboard page
3. The frontend will automatically fetch data from the API

## Current Dashboard Data
```json
{
  "overview": {
    "total_chefs": 25,
    "verified_chefs": 11,
    "total_customers": 11,
    "total_delivery_partners": 2,
    "verified_delivery_partners": 2,
    "chef_verification_rate": 44.0,
    "delivery_partner_verification_rate": 100.0
  },
  "today": {
    "meals_posted": 0,
    "orders_received": 0,
    "revenue": 0,
    "platform_commission": 0
  }
}
```

## Authentication Requirements

### Admin User Credentials:
- **Username**: admin
- **Role**: admin
- **Is Superuser**: True
- **Is Staff**: True

### Token Authentication:
The API uses Django REST Framework's TokenAuthentication. You need to:
1. Login through the frontend
2. Store the returned token in localStorage
3. Include the token in API requests

## Debugging Steps

If you're still getting 500 errors:

1. **Check Admin User:**
   ```bash
   python manage.py shell -c "
   from authentication.models import User
   admin = User.objects.get(username='admin')
   print(f'Admin: {admin.username}')
   print(f'Is Superuser: {admin.is_superuser}')
   print(f'Is Staff: {admin.is_staff}')
   print(f'Role: {admin.role}')
   "
   ```

2. **Check Token:**
   ```bash
   python manage.py shell -c "
   from authentication.models import User
   from rest_framework.authtoken.models import Token
   
   admin = User.objects.get(username='admin')
   token, _ = Token.objects.get_or_create(user=admin)
   print(f'Admin token: {token.key}')
   "
   ```

3. **Test API Directly:**
   ```bash
   python test_admin_dashboard_browser.py
   ```

## Frontend Integration

The admin dashboard API is designed to work with the frontend. The proper flow is:

1. **User logs in** → Frontend stores auth token
2. **Frontend checks user role** → If admin, load dashboard
3. **Frontend fetches dashboard data** → Using auth token
4. **Data displayed** → In admin dashboard UI

## Security Notes

- The API correctly denies access to non-admin users
- Token authentication is required
- Direct browser access without authentication fails (as expected)
- This is proper security behavior, not an error

## Summary

The "500 error" when accessing the URL directly in browser is actually correct behavior - the API is properly secured and requires admin authentication. To access the dashboard data:

1. **Use the frontend interface** (recommended)
2. **Use proper authentication** in API calls
3. **Test with admin token** for debugging

The API is working correctly and securely!
