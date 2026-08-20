#!/usr/bin/env python
"""
Bulk Dish Image Updater for HomeChefs AI
This script provides utilities to bulk update dish images based on names
"""

import os
import django
import requests
import json
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import hashlib
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from chefs.models import FoodItem, DailyMeal
from authentication.models import User

class BulkDishImageUpdater:
    """Bulk updater for dish images with intelligent matching"""
    
    def __init__(self):
        self.dish_image_mapping = self._load_dish_image_mapping()
        self.updated_count = 0
        self.failed_count = 0
        self.skipped_count = 0
    
    def _load_dish_image_mapping(self):
        """Load predefined dish-to-image mappings"""
        return {
            # Indian Main Dishes
            'butter chicken': 'indian-butter-chicken-curry',
            'chicken tikka': 'indian-chicken-tikka-grilled',
            'paneer tikka': 'indian-paneer-tikka-grilled',
            'dal makhani': 'indian-dal-makhani-lentil',
            'palak paneer': 'indian-palak-paneer-spinach',
            'aloo gobi': 'indian-aloo-gobi-potato-cauliflower',
            'chana masala': 'indian-chana-masala-chickpea',
            'rajma': 'indian-rajma-kidney-bean',
            'malai kofta': 'indian-malai-kofta-dumplings',
            'kadhai paneer': 'indian-kadhai-paneer-curry',
            
            # Rice Dishes
            'biryani': 'indian-biryani-rice',
            'hyderabadi biryani': 'indian-hyderabadi-biryani',
            'veg biryani': 'indian-veg-biryani',
            'chicken biryani': 'indian-chicken-biryani',
            'pulao': 'indian-vegetable-pulao',
            'jeera rice': 'indian-jeera-cumin-rice',
            'curd rice': 'indian-curd-rice-yogurt',
            
            # Bread/Roti
            'roti': 'indian-roti-bread',
            'naan': 'indian-naan-bread',
            'paratha': 'indian-paratha-bread',
            'kulcha': 'indian-kulcha-bread',
            'puri': 'indian-puri-fried-bread',
            
            # South Indian
            'dosa': 'south-indian-dosa',
            'masala dosa': 'south-indian-masala-dosa',
            'idli': 'south-indian-idli-steamed',
            'medu vada': 'south-indian-medu-vada',
            'uttapam': 'south-indian-uttapam-pancake',
            'sambar': 'south-indian-sambar-lentil',
            'rasam': 'south-indian-rasam-soup',
            'upma': 'south-indian-upma-semolina',
            
            # Chinese
            'noodles': 'chinese-noodles-stir-fry',
            'fried rice': 'chinese-fried-rice',
            'manchurian': 'chinese-manchurian-balls',
            'chili chicken': 'chinese-chili-chicken',
            'hakka noodles': 'chinese-hakka-noodles',
            'spring rolls': 'chinese-spring-rolls',
            'momos': 'chinese-momos-dumplings',
            
            # Snacks
            'samosa': 'indian-samosa-snack',
            'pakora': 'indian-pakora-fritter',
            'kachori': 'indian-kachori-snack',
            'dhokla': 'indian-dhokla-steamed',
            'vada pav': 'indian-vada-pav-burger',
            
            # Soups
            'tomato soup': 'tomato-soup-bowl',
            'manchow soup': 'manchow-soup-bowl',
            'sweet corn soup': 'sweet-corn-soup-bowl',
            
            # Salads
            'salad': 'fresh-salad-bowl',
            'raita': 'indian-raita-yogurt',
            'kachumber': 'indian-kachumber-salad',
            
            # Desserts
            'gulab jamun': 'indian-gulab-jamun-sweet',
            'rasgulla': 'indian-rasgulla-sweet',
            'kheer': 'indian-kheer-rice-pudding',
            'halwa': 'indian-halwa-sweet',
            'barfi': 'indian-barfi-sweet',
            'lassi': 'indian-lassi-drink',
            
            # Breakfast
            'poha': 'indian-poha-breakfast',
            'upma': 'indian-upma-breakfast',
            'dalia': 'indian-dalia-porridge',
            'besan chilla': 'indian-besan-chilla-pancake',
        }
    
    def get_image_for_dish(self, dish_name, cuisine_type=""):
        """
        Get appropriate image URL for dish based on name matching
        """
        dish_name_lower = dish_name.lower().strip()
        cuisine_type_lower = cuisine_type.lower().strip()
        
        # Try exact match first
        if dish_name_lower in self.dish_image_mapping:
            return self.dish_image_mapping[dish_name_lower]
        
        # Try partial matches
        for pattern, image_key in self.dish_image_mapping.items():
            if pattern in dish_name_lower:
                return image_key
        
        # Try cuisine-based fallback
        if 'indian' in cuisine_type_lower or any(indian_keyword in dish_name_lower for indian_keyword in ['dal', 'sabzi', 'curry', 'masala']):
            return 'indian-curry-general'
        elif 'chinese' in cuisine_type_lower or any(chinese_keyword in dish_name_lower for chinese_keyword in ['noodle', 'rice', 'manchurian']):
            return 'chinese-dish-general'
        elif 'south indian' in cuisine_type_lower or any(south_keyword in dish_name_lower for south_keyword in ['dosa', 'idli', 'sambar']):
            return 'south-indian-dish-general'
        
        # Generate unique fallback
        seed = hashlib.md5(f"{dish_name}_{cuisine_type}".encode()).hexdigest()[:8]
        return f'generic-dish-{seed}'
    
    def generate_image_url(self, image_key, width=400, height=300):
        """Generate full image URL from image key"""
        return f"https://picsum.photos/seed/{image_key}/{width}/{height}.jpg"
    
    def download_and_validate_image(self, image_url, max_retries=3):
        """Download image with retry logic and validation"""
        for attempt in range(max_retries):
            try:
                response = requests.get(image_url, timeout=10, stream=True)
                response.raise_for_status()
                
                # Validate it's actually an image
                image_data = BytesIO()
                for chunk in response.iter_content(chunk_size=8192):
                    image_data.write(chunk)
                
                image_data.seek(0)
                try:
                    img = Image.open(image_data)
                    img.verify()  # Verify it's a valid image
                    image_data.seek(0)
                    return image_data
                except Exception as e:
                    print(f"Invalid image data for {image_url}: {e}")
                    continue
                    
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {image_url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def update_food_item_images(self, batch_size=50, dry_run=False):
        """
        Update FoodItem images in batches
        """
        print(f"🔄 Updating FoodItem images (batch size: {batch_size})")
        print(f"🔍 Dry run: {dry_run}")
        print("-" * 50)
        
        food_items = FoodItem.objects.all()
        total_items = food_items.count()
        
        for i in range(0, total_items, batch_size):
            batch = food_items[i:i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1}/{(total_items-1)//batch_size + 1}")
            
            for food_item in batch:
                self._process_single_food_item(food_item, dry_run)
            
            print(f"Batch complete. Updated: {self.updated_count}, Failed: {self.failed_count}, Skipped: {self.skipped_count}")
            
            if not dry_run:
                time.sleep(1)  # Rate limiting
    
    def _process_single_food_item(self, food_item, dry_run=False):
        """Process a single food item"""
        try:
            # Skip if already has image
            if food_item.image and food_item.image.name:
                self.skipped_count += 1
                print(f"⏭️  Skipped (has image): {food_item.name}")
                return
            
            # Get appropriate image
            image_key = self.get_image_for_dish(food_item.name, food_item.cuisine_type)
            image_url = self.generate_image_url(image_key)
            
            print(f"📸 Processing: {food_item.name} -> {image_key}")
            
            if dry_run:
                print(f"   Would download: {image_url}")
                self.updated_count += 1
                return
            
            # Download and save image
            image_data = self.download_and_validate_image(image_url)
            if image_data:
                filename = f"{food_item.name.lower().replace(' ', '_').replace('/', '_')}.jpg"
                food_item.image.save(filename, ContentFile(image_data.read()), save=True)
                self.updated_count += 1
                print(f"✅ Updated: {food_item.name}")
            else:
                self.failed_count += 1
                print(f"❌ Failed: {food_item.name}")
                
        except Exception as e:
            self.failed_count += 1
            print(f"❌ Error processing {food_item.name}: {e}")
    
    def export_image_mapping(self):
        """Export current image mapping to JSON file"""
        mapping_data = {}
        
        for food_item in FoodItem.objects.all():
            image_key = self.get_image_for_dish(food_item.name, food_item.cuisine_type)
            mapping_data[food_item.name] = {
                'cuisine_type': food_item.cuisine_type,
                'image_key': image_key,
                'image_url': self.generate_image_url(image_key),
                'has_image': bool(food_item.image and food_item.image.name)
            }
        
        with open('dish_image_mapping.json', 'w') as f:
            json.dump(mapping_data, f, indent=2)
        
        print(f"✅ Exported {len(mapping_data)} mappings to dish_image_mapping.json")
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*60)
        print("📊 DISH IMAGE UPDATE REPORT")
        print("="*60)
        
        total_food_items = FoodItem.objects.count()
        food_with_images = FoodItem.objects.exclude(image='').exclude(image__isnull=True).count()
        food_without_images = total_food_items - food_with_images
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Food Items: {total_food_items}")
        print(f"   With Images: {food_with_images} ({food_with_images/total_food_items*100:.1f}%)")
        print(f"   Without Images: {food_without_images} ({food_without_images/total_food_items*100:.1f}%)")
        
        print(f"\n🔄 Session Results:")
        print(f"   Updated: {self.updated_count}")
        print(f"   Failed: {self.failed_count}")
        print(f"   Skipped: {self.skipped_count}")
        
        # Show items without images
        if food_without_images > 0:
            print(f"\n📋 Items Still Needing Images:")
            items_without = FoodItem.objects.filter(image='') | FoodItem.objects.filter(image__isnull=True)
            for item in items_without[:10]:  # Show first 10
                image_key = self.get_image_for_dish(item.name, item.cuisine_type)
                print(f"   - {item.name} ({item.cuisine_type}) -> {image_key}")
            
            if food_without_images > 10:
                print(f"   ... and {food_without_images - 10} more items")

def main():
    """Main function"""
    updater = BulkDishImageUpdater()
    
    print("🍽️ HomeChefs AI - Bulk Dish Image Updater")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. Update All Food Item Images")
        print("2. Dry Run (Preview Updates)")
        print("3. Update Limited Batch")
        print("4. Generate Report")
        print("5. Export Image Mapping")
        print("6. Test Image for Specific Dish")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            updater.update_food_item_images(dry_run=False)
            updater.generate_report()
        
        elif choice == '2':
            updater.update_food_item_images(dry_run=True)
            updater.generate_report()
        
        elif choice == '3':
            try:
                batch_size = int(input("Enter batch size (default 50): ") or "50")
                updater.update_food_item_images(batch_size=batch_size, dry_run=False)
                updater.generate_report()
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == '4':
            updater.generate_report()
        
        elif choice == '5':
            updater.export_image_mapping()
        
        elif choice == '6':
            dish_name = input("Enter dish name: ").strip()
            cuisine_type = input("Enter cuisine type (optional): ").strip()
            
            image_key = updater.get_image_for_dish(dish_name, cuisine_type)
            image_url = updater.generate_image_url(image_key)
            
            print(f"\n📸 Image Analysis:")
            print(f"   Dish: {dish_name}")
            print(f"   Cuisine: {cuisine_type}")
            print(f"   Image Key: {image_key}")
            print(f"   Image URL: {image_url}")
        
        elif choice == '7':
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
