import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User, ChefProfile, CustomerProfile
from chefs.models import FoodItem, ChefReview
from customers.models import FavoriteChef, FavoriteFood, FoodReview
from decimal import Decimal

def create_sample_data():
    print("Creating sample data...")
    
    # Create sample chefs
    chefs_data = [
        {
            'username': 'chef_rahul',
            'email': 'rahul@homechefs.com',
            'first_name': 'Rahul',
            'last_name': 'Kumar',
            'password': 'chef123',
            'phone_number': '9876543210',
            'bio': 'Expert in North Indian and Mughlai cuisine with 10 years of experience',
            'cuisine_specialties': 'North Indian, Mughlai, Chinese',
            'experience_years': 10,
            'kitchen_address': '123 Main St, Delhi, India',
            'delivery_radius': 5,
            'is_verified': True
        },
        {
            'username': 'chef_priya',
            'email': 'priya@homechefs.com',
            'first_name': 'Priya',
            'last_name': 'Sharma',
            'password': 'chef123',
            'phone_number': '9876543211',
            'bio': 'Specialist in South Indian and Continental dishes',
            'cuisine_specialties': 'South Indian, Continental, Italian',
            'experience_years': 8,
            'kitchen_address': '456 Park Ave, Mumbai, India',
            'delivery_radius': 7,
            'is_verified': True
        },
        {
            'username': 'chef_amit',
            'email': 'amit@homechefs.com',
            'first_name': 'Amit',
            'last_name': 'Singh',
            'password': 'chef123',
            'phone_number': '9876543212',
            'bio': 'Master of Chinese and Thai cuisine',
            'cuisine_specialties': 'Chinese, Thai, Japanese',
            'experience_years': 12,
            'kitchen_address': '789 Cross Rd, Bangalore, India',
            'delivery_radius': 6,
            'is_verified': True
        }
    ]
    
    created_chefs = []
    for chef_data in chefs_data:
        # Extract user data
        user_data = {
            'username': chef_data['username'],
            'email': chef_data['email'],
            'first_name': chef_data['first_name'],
            'last_name': chef_data['last_name'],
            'password': chef_data['password'],
            'phone_number': chef_data['phone_number'],
            'role': 'chef'
        }
        
        # Create user
        user, created = User.objects.get_or_create(
            username=chef_data['username'],
            defaults=user_data
        )
        
        if created:
            user.set_password(chef_data['password'])
            user.save()
        
        # Create or update chef profile
        chef_profile, created = ChefProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': chef_data['bio'],
                'cuisine_specialties': chef_data['cuisine_specialties'],
                'experience_years': chef_data['experience_years'],
                'kitchen_address': chef_data['kitchen_address'],
                'delivery_radius': chef_data['delivery_radius'],
                'is_verified': chef_data['is_verified']
            }
        )
        
        created_chefs.append(user)
        print(f"Created chef: {user.username}")
    
    # Create sample food items
    food_items_data = [
        {
            'chef': created_chefs[0],
            'name': 'Butter Chicken',
            'description': 'Tender chicken in rich, creamy tomato-based gravy with butter and cream',
            'cuisine_type': 'North Indian',
            'meal_type': 'dinner',
            'price': Decimal('250.00'),
            'available_quantity': 5,
            'preparation_time': 45,
            'ingredients': 'Chicken, Butter, Cream, Tomatoes, Onions, Garlic, Ginger, Spices',
            'is_vegetarian': False,
            'is_available': True
        },
        {
            'chef': created_chefs[0],
            'name': 'Paneer Tikka',
            'description': 'Soft cottage cheese marinated in spices and grilled to perfection',
            'cuisine_type': 'North Indian',
            'meal_type': 'lunch',
            'price': Decimal('180.00'),
            'available_quantity': 8,
            'preparation_time': 30,
            'ingredients': 'Paneer, Yogurt, Spices, Onion, Capsicum, Tomato',
            'is_vegetarian': True,
            'is_available': True
        },
        {
            'chef': created_chefs[1],
            'name': 'Masala Dosa',
            'description': 'Crispy rice crepe filled with spiced potato mixture',
            'cuisine_type': 'South Indian',
            'meal_type': 'breakfast',
            'price': Decimal('80.00'),
            'available_quantity': 10,
            'preparation_time': 20,
            'ingredients': 'Rice, Lentils, Potatoes, Onions, Spices',
            'is_vegetarian': True,
            'is_available': True
        },
        {
            'chef': created_chefs[1],
            'name': 'Idli Sambar',
            'description': 'Soft steamed rice cakes served with lentil soup',
            'cuisine_type': 'South Indian',
            'meal_type': 'breakfast',
            'price': Decimal('60.00'),
            'available_quantity': 15,
            'preparation_time': 15,
            'ingredients': 'Rice, Lentils, Vegetables, Spices',
            'is_vegetarian': True,
            'is_available': True
        },
        {
            'chef': created_chefs[2],
            'name': 'Hakka Noodles',
            'description': 'Stir-fried noodles with vegetables and Chinese spices',
            'cuisine_type': 'Chinese',
            'meal_type': 'dinner',
            'price': Decimal('120.00'),
            'available_quantity': 7,
            'preparation_time': 25,
            'ingredients': 'Noodles, Vegetables, Soy Sauce, Vinegar, Spices',
            'is_vegetarian': True,
            'is_available': True
        },
        {
            'chef': created_chefs[2],
            'name': 'Spring Rolls',
            'description': 'Crispy fried rolls filled with vegetables',
            'cuisine_type': 'Chinese',
            'meal_type': 'snacks',
            'price': Decimal('90.00'),
            'available_quantity': 12,
            'preparation_time': 20,
            'ingredients': 'Spring Roll Sheets, Cabbage, Carrots, Beans, Spices',
            'is_vegetarian': True,
            'is_available': True
        }
    ]
    
    for food_data in food_items_data:
        food_item, created = FoodItem.objects.get_or_create(
            name=food_data['name'],
            chef=food_data['chef'],
            defaults=food_data
        )
        if created:
            print(f"Created food item: {food_item.name}")
    
    # Create sample customers
    customers_data = [
        {
            'username': 'customer_anjali',
            'email': 'anjali@email.com',
            'first_name': 'Anjali',
            'last_name': 'Patel',
            'password': 'customer123',
            'phone_number': '9876543213',
            'preferred_cuisines': 'North Indian, Chinese',
            'dietary_restrictions': 'No beef',
            'default_delivery_address': '123 Apartment Block, Delhi, India'
        },
        {
            'username': 'customer_raj',
            'email': 'raj@email.com',
            'first_name': 'Raj',
            'last_name': 'Verma',
            'password': 'customer123',
            'phone_number': '9876543214',
            'preferred_cuisines': 'South Indian, Italian',
            'dietary_restrictions': 'Vegetarian',
            'default_delivery_address': '456 Housing Society, Mumbai, India'
        }
    ]
    
    created_customers = []
    for customer_data in customers_data:
        # Extract user data
        user_data = {
            'username': customer_data['username'],
            'email': customer_data['email'],
            'first_name': customer_data['first_name'],
            'last_name': customer_data['last_name'],
            'password': customer_data['password'],
            'phone_number': customer_data['phone_number'],
            'role': 'customer'
        }
        
        # Create user
        user, created = User.objects.get_or_create(
            username=customer_data['username'],
            defaults=user_data
        )
        
        if created:
            user.set_password(customer_data['password'])
            user.save()
        
        # Create or update customer profile
        customer_profile, created = CustomerProfile.objects.get_or_create(
            user=user,
            defaults={
                'preferred_cuisines': customer_data['preferred_cuisines'],
                'dietary_restrictions': customer_data['dietary_restrictions'],
                'default_delivery_address': customer_data['default_delivery_address']
            }
        )
        
        created_customers.append(user)
        print(f"Created customer: {user.username}")
    
    # Create some sample reviews
    reviews_data = [
        {
            'chef': created_chefs[0],
            'customer': created_customers[0],
            'rating': 5,
            'comment': 'Amazing butter chicken! Very authentic taste and generous portions.'
        },
        {
            'chef': created_chefs[1],
            'customer': created_customers[1],
            'rating': 4,
            'comment': 'Great dosa and sambar. Very fresh and tasty.'
        },
        {
            'chef': created_chefs[2],
            'customer': created_customers[0],
            'rating': 4,
            'comment': 'Good hakka noodles, but could be a bit more spicy.'
        }
    ]
    
    for review_data in reviews_data:
        review, created = ChefReview.objects.get_or_create(
            chef=review_data['chef'],
            customer=review_data['customer'],
            defaults={
                'rating': review_data['rating'],
                'comment': review_data['comment']
            }
        )
        if created:
            print(f"Created review by {review.customer.username} for {review.chef.username}")
    
    # Update chef ratings based on reviews
    for chef in created_chefs:
        reviews = ChefReview.objects.filter(chef=chef)
        if reviews.exists():
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
            chef.chef_profile.rating = round(avg_rating, 2)
            chef.chef_profile.save()
            print(f"Updated {chef.username}'s rating to {avg_rating}")
    
    print("\nSample data creation completed!")
    print("\nLogin credentials:")
    print("Admin - Username: admin, Password: admin123")
    print("Chef 1 - Username: chef_rahul, Password: chef123")
    print("Chef 2 - Username: chef_priya, Password: chef123")
    print("Chef 3 - Username: chef_amit, Password: chef123")
    print("Customer 1 - Username: customer_anjali, Password: customer123")
    print("Customer 2 - Username: customer_raj, Password: customer123")

if __name__ == '__main__':
    create_sample_data()
