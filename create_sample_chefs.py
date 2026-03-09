# Create sample chef profiles with different cuisine specialties

from authentication.models import User
from chefs.models import ChefProfile

# Create sample chefs with different cuisine specialties
sample_chefs = [
    {
        'username': 'south_indian_chef',
        'email': 'south@example.com',
        'first_name': 'Ravi',
        'last_name': 'Kumar',
        'cuisine_specialties': 'South Indian, Tamil, Kerala',
        'area': 'T Nagar',
        'city': 'Chennai',
        'pincode': '600017',
        'cooking_experience': 8,
        'bio': 'Expert in traditional South Indian cuisine with 8 years of experience'
    },
    {
        'username': 'north_indian_chef',
        'email': 'north@example.com',
        'first_name': 'Amit',
        'last_name': 'Sharma',
        'cuisine_specialties': 'North Indian, Punjabi, Mughlai',
        'area': 'Connaught Place',
        'city': 'New Delhi',
        'pincode': '110001',
        'cooking_experience': 10,
        'bio': 'Specialist in North Indian and Mughlai cuisine with 10 years of experience'
    },
    {
        'username': 'chinese_chef',
        'email': 'chinese@example.com',
        'first_name': 'Wei',
        'last_name': 'Chen',
        'cuisine_specialties': 'Chinese, Thai, Asian',
        'area': 'China Town',
        'city': 'Mumbai',
        'pincode': '400050',
        'cooking_experience': 6,
        'bio': 'Expert in Chinese and Asian cuisine with 6 years of experience'
    },
    {
        'username': 'continental_chef',
        'email': 'continental@example.com',
        'first_name': 'Pierre',
        'last_name': 'Dubois',
        'cuisine_specialties': 'Continental, Italian, French',
        'area': 'Bandra',
        'city': 'Mumbai',
        'pincode': '400050',
        'cooking_experience': 12,
        'bio': 'Continental cuisine specialist with 12 years of experience'
    }
]

print("Creating sample chef profiles...")

for chef_data in sample_chefs:
    # Check if user already exists
    if User.objects.filter(username=chef_data['username']).exists():
        print(f"User {chef_data['username']} already exists, skipping...")
        continue
    
    # Create user
    user = User.objects.create_user(
        username=chef_data['username'],
        email=chef_data['email'],
        first_name=chef_data['first_name'],
        last_name=chef_data['last_name'],
        role='chef'
    )
    
    # Create chef profile
    profile = ChefProfile.objects.create(
        user=user,
        phone_number='9876543210',
        address_line1='123 Main Street',
        area=chef_data['area'],
        city=chef_data['city'],
        pincode=chef_data['pincode'],
        cooking_experience=chef_data['cooking_experience'],
        cuisine_specialties=chef_data['cuisine_specialties'],
        is_verified=True,
        kitchen_type='home'
    )
    
    print(f"Created chef: {user.username} with specialties: {profile.cuisine_specialties}")

print("Sample chef profiles created successfully!")
