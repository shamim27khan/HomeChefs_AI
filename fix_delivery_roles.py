import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.contrib.auth import get_user_model
from delivery.models import DeliveryPartner

User = get_user_model()

# Fix the role for delivery partners
delivery_users = User.objects.filter(username__startswith='delivery_partner')
for user in delivery_users:
    user.role = 'delivery_partner'
    user.save()
    print(f'Updated {user.username} role to delivery_partner')

# Verify the changes
print('\nUpdated delivery users:')
delivery_users = User.objects.filter(username__startswith='delivery_partner')
for user in delivery_users:
    print(f'Username: {user.username}, Role: {user.role}, Active: {user.is_active}')
