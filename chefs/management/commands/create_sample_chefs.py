import random
from datetime import date, time

from django.core.management.base import BaseCommand
from authentication.models import User
from chefs.models import ChefProfile, DailyMeal

class Command(BaseCommand):
    help = 'Create sample chef profiles with geolocations and today\'s meals for nearby-dishes testing'

    def handle(self, *args, **options):
        # Create sample chefs with different cuisine specialties
        # Bengaluru/Koramangala/HSR coordinates around 12.906693, 77.634619
        sample_chefs = [
            {
                'username': 'chef_kora_1',
                'email': 'kora1@example.com',
                'first_name': 'Ravi',
                'last_name': 'Kumar',
                'cuisine_specialties': 'South Indian, Vegetarian',
                'area': 'Koramangala 6th Block',
                'city': 'Bengaluru',
                'pincode': '560095',
                'cooking_experience': 8,
                'latitude': 12.9075,
                'longitude': 77.6335,
            },
            {
                'username': 'chef_kora_2',
                'email': 'kora2@example.com',
                'first_name': 'Amit',
                'last_name': 'Sharma',
                'cuisine_specialties': 'North Indian, Non-Vegetarian',
                'area': 'Koramangala 5th Block',
                'city': 'Bengaluru',
                'pincode': '560095',
                'cooking_experience': 10,
                'latitude': 12.9038,
                'longitude': 77.6372,
            },
            {
                'username': 'chef_hsr_1',
                'email': 'hsr1@example.com',
                'first_name': 'Wei',
                'last_name': 'Chen',
                'cuisine_specialties': 'South Indian, Chinese',
                'area': 'HSR Layout Sector 1',
                'city': 'Bengaluru',
                'pincode': '560102',
                'cooking_experience': 6,
                'latitude': 12.9060,
                'longitude': 77.6445,
            },
            # Slightly farther away to test radius cutoff
            {
                'username': 'chef_btm_1',
                'email': 'btm1@example.com',
                'first_name': 'Pierre',
                'last_name': 'Dubois',
                'cuisine_specialties': 'Hyderabadi, Biryani',
                'area': 'BTM Layout',
                'city': 'Bengaluru',
                'pincode': '560076',
                'cooking_experience': 12,
                'latitude': 12.9145,
                'longitude': 77.6030,
            },
        ]

        self.stdout.write(self.style.SUCCESS('Creating sample chef profiles and today\'s meals...'))

        for chef_data in sample_chefs:
            # Check if user already exists
            if User.objects.filter(username=chef_data['username']).exists():
                self.stdout.write(self.style.WARNING(f"User {chef_data['username']} already exists, skipping..."))
                continue
            
            # Create user
            user = User.objects.create_user(
                username=chef_data['username'],
                email=chef_data['email'],
                first_name=chef_data['first_name'],
                last_name=chef_data['last_name'],
                role='chef'
            )

            # Create chef profile with unique phone number and geolocation
            profile = ChefProfile.objects.create(
                user=user,
                phone_number=f'9876543{random.randint(1000, 9999)}',  # Unique-ish phone number
                address_line1='123 Test Street',
                address_line2='',
                area=chef_data['area'],
                city=chef_data['city'],
                pincode=chef_data['pincode'],
                latitude=chef_data.get('latitude'),
                longitude=chef_data.get('longitude'),
                cooking_experience=chef_data['cooking_experience'],
                cuisine_specialties=chef_data['cuisine_specialties'],
                is_verified=True,
                kitchen_type='home'
            )

            # Create today's active, deliverable meal with capacity
            meal_defaults = {
                'meal_type': 'lunch',
                'main_dish': 'Masala Dosa',
                'side_dish': 'Sambar & Chutney',
                'additional_items': 'Papad, Pickle',
                'extra_portions': 5,
                'price_per_portion': 120.00,
                'order_cutoff_time': time(22, 0, 0),
                'max_orders': 5,
                'current_orders': 0,
                'pickup_available': True,
                'delivery_available': True,
                'delivery_radius': 3,
                'is_active': True,
            }

            meal, _ = DailyMeal.objects.get_or_create(
                chef=user,
                date=date.today(),
                meal_type=meal_defaults['meal_type'],
                defaults=meal_defaults,
            )

            # Ensure it is active and with capacity
            changed = False
            for k, v in meal_defaults.items():
                if hasattr(meal, k) and getattr(meal, k) != v:
                    setattr(meal, k, v)
                    changed = True
            if changed:
                meal.save()

            self.stdout.write(self.style.SUCCESS(
                f"Created chef: {user.username} at ({profile.latitude}, {profile.longitude}) with meal #{meal.id}"
            ))

        self.stdout.write(self.style.SUCCESS('Sample chef profiles and meals created successfully!'))
