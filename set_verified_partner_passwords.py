import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Set passwords for verified partners
guddu = User.objects.get(username='guddu')
guddu.set_password('delivery123')
guddu.save()
print(f'Set password for {guddu.username}')

test = User.objects.get(username='test_delivery_partner')
test.set_password('delivery123')
test.save()
print(f'Set password for {test.username}')

print('\nVerified delivery partners with passwords:')
partners = User.objects.filter(role='delivery_partner')
for user in partners:
    print(f'Username: {user.username}, Role: {user.role}, Active: {user.is_active}')
