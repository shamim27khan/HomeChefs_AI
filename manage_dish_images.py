#!/usr/bin/env python
"""
Dish Image Management Script for HomeChefs AI
This script helps manage dish images based on food names
"""

import os
import django
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import hashlib

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from chefs.models import FoodItem, DailyMeal
from authentication.models import User

class DishImageManager:
    """Manages dish images based on food names"""
    
    def __init__(self):
        self.image_cache = {}
        self.default_image_url = "https://picsum.photos/seed/default-dish/400/300.jpg"
        
    def get_image_for_dish_name(self, dish_name, cuisine_type="", width=400, height=300):
        """
        Get appropriate image URL based on dish name and cuisine type
        Uses a deterministic approach to ensure same dish gets same image
        """
        # Create a consistent seed based on dish name and cuisine
        seed_data = f"{dish_name.lower().strip()}_{cuisine_type.lower().strip()}"
        seed = hashlib.md5(seed_data.encode()).hexdigest()[:8]
        
        # Try to match dish patterns for better images
        image_patterns = self._get_dish_image_patterns(dish_name, cuisine_type)
        
        if image_patterns:
            return f"https://picsum.photos/seed/{image_patterns}_{seed}/{width}/{height}.jpg"
        else:
            return f"https://picsum.photos/seed/{seed}/{width}/{height}.jpg"
    
    def _get_dish_image_patterns(self, dish_name, cuisine_type):
        """
        Get appropriate image patterns based on dish name patterns
        """
        name_lower = dish_name.lower()
        cuisine_lower = cuisine_type.lower()
        
        # Indian dishes patterns
        if any(keyword in name_lower for keyword in ['biryani', 'pulao']):
            return 'indian-biryani-rice'
        elif any(keyword in name_lower for keyword in ['curry', 'masala', 'gravy']):
            return 'indian-curry-gravy'
        elif any(keyword in name_lower for keyword in ['dal', 'lentil']):
            return 'indian-dal-lentil'
        elif any(keyword in name_lower for keyword in ['sabzi', 'vegetable']):
            return 'indian-sabzi-vegetable'
        elif any(keyword in name_lower for keyword in ['roti', 'naan', 'paratha']):
            return 'indian-bread-roti'
        elif any(keyword in name_lower for keyword in ['paneer', 'cheese']):
            return 'indian-paneer-cottage'
        elif any(keyword in name_lower for keyword in ['chicken', 'mutton', 'meat']):
            return 'indian-meat-chicken'
        elif any(keyword in name_lower for keyword in ['fish', 'seafood']):
            return 'indian-fish-seafood'
        
        # South Indian patterns
        elif any(keyword in name_lower for keyword in ['dosa', 'idli', 'uttapam']):
            return 'south-indian-dosa-idli'
        elif any(keyword in name_lower for keyword in ['sambar', 'rasam']):
            return 'south-indian-sambar-rasam'
        
        # Chinese patterns
        elif 'chinese' in cuisine_lower or any(keyword in name_lower for keyword in ['noodle', 'fried rice']):
            return 'chinese-noodle-rice'
        elif any(keyword in name_lower for keyword in ['manchurian', 'chili']):
            return 'chinese-manchurian-chili'
        
        # General patterns
        elif any(keyword in name_lower for keyword in ['soup', 'shorba']):
            return 'soup-bowl'
        elif any(keyword in name_lower for keyword in ['salad', 'raita']):
            return 'salad-healthy'
        elif any(keyword in name_lower for keyword in ['rice', 'pulao']):
            return 'rice-dish'
        elif any(keyword in name_lower for keyword in ['breakfast', 'morning']):
            return 'breakfast-meal'
        elif any(keyword in name_lower for keyword in ['dessert', 'sweet']):
            return 'dessert-sweet'
        
        return None
    
    def download_image(self, image_url):
        """Download image from URL"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            return BytesIO(response.content)
        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
            return None
    
    def update_food_item_images(self, limit=None):
        """
        Update images for all FoodItem records based on their names
        """
        food_items = FoodItem.objects.all()
        if limit:
            food_items = food_items[:limit]
        
        print(f"Updating images for {len(food_items)} food items...")
        
        updated_count = 0
        for food_item in food_items:
            try:
                # Get appropriate image URL for this dish
                image_url = self.get_image_for_dish_name(
                    food_item.name, 
                    food_item.cuisine_type
                )
                
                print(f"Processing: {food_item.name} -> {image_url}")
                
                # Download image
                image_data = self.download_image(image_url)
                if image_data:
                    # Save image to the food item
                    filename = f"{food_item.name.lower().replace(' ', '_')}.jpg"
                    food_item.image.save(filename, ContentFile(image_data.read()), save=True)
                    updated_count += 1
                    print(f"✅ Updated image for: {food_item.name}")
                else:
                    print(f"❌ Failed to download image for: {food_item.name}")
                    
            except Exception as e:
                print(f"❌ Error processing {food_item.name}: {e}")
        
        print(f"\n✅ Successfully updated {updated_count} food item images")
        return updated_count
    
    def update_daily_meal_images(self, limit=None):
        """
        Add image support to DailyMeal (if needed) and update images
        Note: DailyMeal doesn't have image field by default, this shows how to add it
        """
        print("DailyMeal model doesn't have image field by default.")
        print("To add image support to DailyMeal, you need to:")
        print("1. Add image field to DailyMeal model")
        print("2. Run migrations")
        print("3. Then run this function")
        
        # This would work if DailyMeal had an image field
        # daily_meals = DailyMeal.objects.all()
        # if limit:
        #     daily_meals = daily_meals[:limit]
        
        # for meal in daily_meals:
        #     image_url = self.get_image_for_dish_name(
        #         f"{meal.main_dish} {meal.side_dish}",
        #         meal.chef.chefprofile.cuisine_specialties
        #     )
        #     # Download and save image...
    
    def generate_image_report(self):
        """Generate a report of current image status"""
        print("\n" + "="*60)
        print("DISH IMAGE STATUS REPORT")
        print("="*60)
        
        # Food Items with images
        food_with_images = FoodItem.objects.exclude(image='').exclude(image__isnull=True)
        food_without_images = FoodItem.objects.filter(image='') | FoodItem.objects.filter(image__isnull=True)
        
        print(f"\n📊 Food Items:")
        print(f"   Total: {FoodItem.objects.count()}")
        print(f"   With Images: {food_with_images.count()}")
        print(f"   Without Images: {food_without_images.count()}")
        
        if food_without_images.exists():
            print(f"\n📋 Items needing images:")
            for food in food_without_images[:10]:  # Show first 10
                print(f"   - {food.name} ({food.cuisine_type})")
        
        # Show sample image URLs for items without images
        print(f"\n🖼️ Sample Image URLs for items without images:")
        for food in food_without_images[:5]:
            image_url = self.get_image_for_dish_name(food.name, food.cuisine_type)
            print(f"   {food.name}: {image_url}")
    
    def create_sample_images_batch(self, limit=20):
        """Create sample images for a batch of food items"""
        print(f"Creating sample images for {limit} food items...")
        return self.update_food_item_images(limit=limit)

def main():
    """Main function to run the image management"""
    manager = DishImageManager()
    
    print("🍽️ HomeChefs AI - Dish Image Manager")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. Generate Image Report")
        print("2. Update All Food Item Images")
        print("3. Update Limited Food Item Images")
        print("4. Create Sample Images (20 items)")
        print("5. Generate Image URLs for Specific Dish")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            manager.generate_image_report()
        
        elif choice == '2':
            confirm = input("This will update ALL food item images. Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                manager.update_food_item_images()
        
        elif choice == '3':
            try:
                limit = int(input("Enter number of items to update: "))
                manager.update_food_item_images(limit=limit)
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == '4':
            manager.create_sample_images_batch()
        
        elif choice == '5':
            dish_name = input("Enter dish name: ").strip()
            cuisine_type = input("Enter cuisine type (optional): ").strip()
            image_url = manager.get_image_for_dish_name(dish_name, cuisine_type)
            print(f"Image URL: {image_url}")
        
        elif choice == '6':
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
