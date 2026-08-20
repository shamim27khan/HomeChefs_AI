import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.contrib.auth import authenticate
from delivery.models import DeliveryPartner

# Test all delivery partner credentials
test_credentials = [
    ('delivery_partner_1', 'delivery123'),
    ('delivery_partner_2', 'delivery123'),
    ('guddu', 'delivery123'),
    ('test_delivery_partner', 'delivery123'),
]

print('Testing delivery partner credentials:\n')
for username, password in test_credentials:
    user = authenticate(username=username, password=password)
    if user:
        partner = DeliveryPartner.objects.filter(user=user).first()
        verification_status = partner.verification_status if partner else 'No partner profile'
        print(f'[OK] {username}: SUCCESS (Role: {user.role}, Verification: {verification_status})')
    else:
        print(f'[FAIL] {username}: FAILED')

print('\nAll delivery partners in system:')
partners = DeliveryPartner.objects.all()
for partner in partners:
    print(f'Username: {partner.user.username}, Verification: {partner.verification_status}, Status: {partner.status}')
