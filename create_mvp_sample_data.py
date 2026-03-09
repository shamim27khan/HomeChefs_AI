#!/usr/bin/env python
import os
import django
from django.utils import timezone
from datetime import date, time, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.models import ChefProfile, DailyMeal, DailyEarning

def create_sample_mvp_data():
    """Create sample data for MVP testing"""
    
    print("Creating sample MVP data...")
    
    # Create sample home chefs
    chefs_data = [
        {
            'username': 'chef_anjali',
            'email': 'anjali@homechefhub.com',
            'password': 'chef123',
            'first_name': 'Anjali',
            'last_name': 'Sharma',
            'role': 'chef',
            'phone': '9876543210',
            'address': '123 Main St, Andheri',
            'area': 'Andheri West',
            'city': 'Mumbai',
            'pincode': '400053',
            'cooking_experience': 8,
            'cuisine_specialties': 'North Indian, Punjabi',
            'is_verified': True
        },
        {
            'username': 'chef_priya',
            'email': 'priya@homechefhub.com',
            'password': 'chef123',
            'first_name': 'Priya',
            'last_name': 'Patel',
            'role': 'chef',
            'phone': '9876543211',
            'address': '456 Park Ave, Bandra',
            'area': 'Bandra West',
            'city': 'Mumbai',
            'pincode': '400050',
            'cooking_experience': 5,
            'cuisine_specialties': 'Gujarati, Rajasthani',
            'is_verified': True
        },
        {
            'username': 'chef_meena',
            'email': 'meena@homechefhub.com',
            'password': 'chef123',
            'first_name': 'Meena',
            'last_name': 'Kumar',
            'role': 'chef',
            'phone': '9876543212',
            'address': '789 Linking Rd, Powai',
            'area': 'Powai',
            'city': 'Mumbai',
            'pincode': '400076',
            'cooking_experience': 10,
            'cuisine_specialties': 'South Indian, Chinese',
            'is_verified': False  # Pending verification
        }
    ]
    
    for chef_data in chefs_data:
        user, created = User.objects.get_or_create(
            username=chef_data['username'],
            defaults={
                'email': chef_data['email'],
                'first_name': chef_data['first_name'],
                'last_name': chef_data['last_name'],
                'role': chef_data['role'],
            }
        )
        
        if created:
            user.set_password(chef_data['password'])
            user.save()
            print(f"Created chef: {user.username}")
        
        # Create or update chef profile
        profile, created = ChefProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': chef_data['phone'],
                'address_line1': chef_data['address'],
                'area': chef_data['area'],
                'city': chef_data['city'],
                'pincode': chef_data['pincode'],
                'cooking_experience': chef_data['cooking_experience'],
                'cuisine_specialties': chef_data['cuisine_specialties'],
                'is_verified': chef_data['is_verified'],
                'verification_date': timezone.now() if chef_data['is_verified'] else None
            }
        )
        
        if created:
            print(f"Created profile for: {user.username}")
    
    # Create sample daily meals for today
    today = date.today()
    meals_data = [
        {
            'chef': User.objects.get(username='chef_anjali'),
            'date': today,
            'meal_type': 'lunch',
            'main_dish': 'Dal Makhani',
            'side_dish': 'Roti & Rice',
            'additional_items': 'Salad & Pickle',
            'extra_portions': 3,
            'price_per_portion': 80.00,
            'order_cutoff_time': time(11, 30),
            'pickup_available': True,
            'delivery_available': True,
            'delivery_radius': 3
        },
        {
            'chef': User.objects.get(username='chef_anjali'),
            'date': today,
            'meal_type': 'dinner',
            'main_dish': 'Paneer Butter Masala',
            'side_dish': 'Naan & Jeera Rice',
            'additional_items': 'Raita',
            'extra_portions': 2,
            'price_per_portion': 120.00,
            'order_cutoff_time': time(18, 30),
            'pickup_available': True,
            'delivery_available': False,
            'delivery_radius': 0
        },
        {
            'chef': User.objects.get(username='chef_priya'),
            'date': today,
            'meal_type': 'lunch',
            'main_dish': 'Gujarati Thali',
            'side_dish': 'Roti & Dal',
            'additional_items': 'Kadhi & Farsan',
            'extra_portions': 4,
            'price_per_portion': 100.00,
            'order_cutoff_time': time(12, 0),
            'pickup_available': True,
            'delivery_available': True,
            'delivery_radius': 2
        },
        {
            'chef': User.objects.get(username='chef_priya'),
            'date': today,
            'meal_type': 'dinner',
            'main_dish': 'Dhokla',
            'side_dish': 'Roti & Ghee',
            'additional_items': 'Chutney',
            'extra_portions': 2,
            'price_per_portion': 90.00,
            'order_cutoff_time': time(19, 0),
            'pickup_available': True,
            'delivery_available': False,
            'delivery_radius': 0
        }
    ]
    
    for meal_data in meals_data:
        meal, created = DailyMeal.objects.get_or_create(
            chef=meal_data['chef'],
            date=meal_data['date'],
            meal_type=meal_data['meal_type'],
            defaults={
                'main_dish': meal_data['main_dish'],
                'side_dish': meal_data['side_dish'],
                'additional_items': meal_data['additional_items'],
                'extra_portions': meal_data['extra_portions'],
                'price_per_portion': meal_data['price_per_portion'],
                'order_cutoff_time': meal_data['order_cutoff_time'],
                'pickup_available': meal_data['pickup_available'],
                'delivery_available': meal_data['delivery_available'],
                'delivery_radius': meal_data['delivery_radius'],
                'is_active': True
            }
        )
        
        if created:
            print(f"Created meal: {meal.main_dish} by {meal.chef.username}")
    
    # Create sample customers
    customers_data = [
        {
            'username': 'customer_rahul',
            'email': 'rahul@homechefhub.com',
            'password': 'cust123',
            'first_name': 'Rahul',
            'last_name': 'Verma',
            'role': 'customer'
        },
        {
            'username': 'customer_sneha',
            'email': 'sneha@homechefhub.com',
            'password': 'cust123',
            'first_name': 'Sneha',
            'last_name': 'Patel',
            'role': 'customer'
        }
    ]
    
    for customer_data in customers_data:
        user, created = User.objects.get_or_create(
            username=customer_data['username'],
            defaults={
                'email': customer_data['email'],
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name'],
                'role': customer_data['role'],
            }
        )
        
        if created:
            user.set_password(customer_data['password'])
            user.save()
            print(f"Created customer: {user.username}")
    
    print("\n✅ Sample MVP data created successfully!")
    print("\n📋 Test Accounts:")
    print("Chefs:")
    print("- chef_anjali / chef123 (Verified)")
    print("- chef_priya / chef123 (Verified)")
    print("- chef_meena / chef123 (Pending Verification)")
    print("\nCustomers:")
    print("- customer_rahul / cust123")
    print("- customer_sneha / cust123")
    print("\n🍽️ Today's Meals Available:")
    print("- Dal Makhani by Anjali (Lunch, ₹80, 3 portions)")
    print("- Paneer Butter Masala by Anjali (Dinner, ₹120, 2 portions)")
    print("- Gujarati Thali by Priya (Lunch, ₹100, 4 portions)")
    print("- Dhokla by Priya (Dinner, ₹90, 2 portions)")

if __name__ == '__main__':
    create_sample_mvp_data()
