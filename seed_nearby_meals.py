from datetime import date, time
from django.utils import timezone

# This script assumes Django settings are configured via manage.py execution:
#   python manage.py shell -c "exec(open('seed_nearby_meals.py').read())"

from authentication.models import User
from chefs.models import ChefProfile, DailyMeal


def get_or_create_chef(username, phone, lat, lon, area, city, specialties, verified=True):
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={
            'role': 'chef',
            'email': f'{username}@example.com',
        }
    )
    # Ensure role is chef
    if user.role != 'chef':
        user.role = 'chef'
        user.save(update_fields=['role'])

    profile, created = ChefProfile.objects.get_or_create(
        user=user,
        defaults={
            'phone_number': phone,
            'address_line1': 'Test Address 1',
            'address_line2': '',
            'area': area,
            'city': city,
            'pincode': '560001',
            'latitude': lat,
            'longitude': lon,
            'cooking_experience': 5,
            'cuisine_specialties': specialties,
            'is_verified': verified,
        }
    )

    # Update location/verification if profile existed
    changed = False
    for field, val in {
        'area': area,
        'city': city,
        'latitude': lat,
        'longitude': lon,
        'cuisine_specialties': specialties,
        'is_verified': verified,
    }.items():
        if getattr(profile, field) != val:
            setattr(profile, field, val)
            changed = True
    if changed:
        profile.save()

    return user


def seed_meals():
    today = date.today()

    # Coordinates near 12.906693, 77.634619 (Koramangala, Bangalore)
    chefs_data = [
        {
            'username': 'chef_kora_1',
            'phone': '9000000001',
            'lat': 12.9075,
            'lon': 77.6335,
            'area': 'Koramangala 6th Block',
            'city': 'Bengaluru',
            'specialties': 'South Indian, Vegetarian'
        },
        {
            'username': 'chef_kora_2',
            'phone': '9000000002',
            'lat': 12.9038,
            'lon': 77.6372,
            'area': 'Koramangala 5th Block',
            'city': 'Bengaluru',
            'specialties': 'North Indian, Non-Vegetarian'
        },
        {
            'username': 'chef_hsr_1',
            'phone': '9000000003',
            'lat': 12.9060,
            'lon': 77.6445,
            'area': 'HSR Layout Sector 1',
            'city': 'Bengaluru',
            'specialties': 'South Indian, Chinese'
        },
        # One slightly outside 3km to validate radius cutoff
        {
            'username': 'chef_btm_1',
            'phone': '9000000004',
            'lat': 12.9145,
            'lon': 77.6030,
            'area': 'BTM Layout',
            'city': 'Bengaluru',
            'specialties': 'Hyderabadi, Biryani'
        },
    ]

    created_meals = []

    for idx, cd in enumerate(chefs_data, start=1):
        chef = get_or_create_chef(
            username=cd['username'],
            phone=cd['phone'],
            lat=cd['lat'],
            lon=cd['lon'],
            area=cd['area'],
            city=cd['city'],
            specialties=cd['specialties'],
            verified=True
        )

        defaults = {
            'meal_type': 'lunch',
            'main_dish': 'Masala Dosa' if idx == 1 else 'Thali',
            'side_dish': 'Sambar & Chutney' if idx == 1 else 'Raita',
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

        meal, created = DailyMeal.objects.get_or_create(
            chef=chef,
            date=today,
            meal_type=defaults['meal_type'],
            defaults=defaults,
        )

        # Ensure active and with capacity
        updates = {}
        for k in ['is_active', 'current_orders', 'extra_portions', 'delivery_available', 'delivery_radius']:
            if getattr(meal, k) != defaults[k]:
                updates[k] = defaults[k]
        if updates:
            for k, v in updates.items():
                setattr(meal, k, v)
            meal.save()

        created_meals.append(meal.id)

    return created_meals


if __name__ == '__main__':
    ids = seed_meals()
    print({'created_meal_ids': ids})
