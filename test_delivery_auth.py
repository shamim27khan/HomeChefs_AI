import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.contrib.auth import authenticate

# Test authentication
user = authenticate(username='delivery_partner_1', password='delivery123')
print(f'Authentication result: {user}')
if user:
    print('Authentication successful')
    print(f'User: {user.username}, Email: {user.email}, Active: {user.is_active}')
else:
    print('Authentication failed')
    
# Test with existing verified partner
user2 = authenticate(username='guddu', password='delivery123')
print(f'\nGuddu authentication: {user2}')
