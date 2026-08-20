#!/usr/bin/env python
"""
Add image fields to models that don't have them yet
This script adds image support to DailyMeal model
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

def add_image_field_to_daily_meal():
    """
    This function shows how to add image field to DailyMeal model
    Note: This requires manual migration creation
    """
    
    print("🔧 Adding Image Field to DailyMeal Model")
    print("="*50)
    
    print("""
To add image support to DailyMeal, follow these steps:

1. Update the DailyMeal model in chefs/models.py:

Add this field to DailyMeal class:
    # Image field for meal photos
    image = models.ImageField(
        upload_to='meal_images/', 
        blank=True, 
        null=True,
        help_text="Photo of the prepared meal"
    )

2. Create and run migration:
   python manage.py makemigrations chefs
   python manage.py migrate

3. Update serializers to include image field

4. Update templates to display meal images

Example model update:

class DailyMeal(models.Model):
    # ... existing fields ...
    
    # Image field for meal photos
    image = models.ImageField(
        upload_to='meal_images/', 
        blank=True, 
        null=True,
        help_text="Photo of the prepared meal"
    )
    
    # ... rest of the model ...
""")

def create_migration_file():
    """Create the migration file content for adding image field"""
    
    migration_content = '''# Generated migration for adding image field to DailyMeal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chefs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailymeal',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text='Photo of the prepared meal',
                null=True,
                upload_to='meal_images/'
            ),
        ),
    ]
'''
    
    print("📝 Migration File Content:")
    print("="*30)
    print(migration_content)
    
    # Save to file
    migration_path = "chefs/migrations/0002_dailymeal_image.py"
    try:
        with open(migration_path, 'w') as f:
            f.write(migration_content)
        print(f"✅ Migration file saved to: {migration_path}")
        print("Run 'python manage.py migrate' to apply the migration")
    except Exception as e:
        print(f"❌ Error saving migration file: {e}")

def update_serializers():
    """Show how to update serializers to include image field"""
    
    print("\n🔄 Updating Serializers")
    print("="*30)
    
    serializer_update = '''
# Add to chefs/serializers.py

class DailyMealSerializer(serializers.ModelSerializer):
    chef_name = serializers.CharField(source='chef.username', read_only=True)
    meal_type_display = serializers.CharField(source='get_meal_type_display', read_only=True)
    image_url = serializers.ImageField(source='image', read_only=True)
    
    class Meta:
        model = DailyMeal
        fields = [
            'id', 'chef', 'chef_name', 'date', 'meal_type', 'meal_type_display',
            'main_dish', 'side_dish', 'additional_items', 'extra_portions',
            'price_per_portion', 'order_cutoff_time', 'max_orders', 'current_orders',
            'pickup_available', 'delivery_available', 'delivery_radius',
            'is_active', 'created_at', 'updated_at', 'image', 'image_url'
        ]
        read_only_fields = ['id', 'chef', 'created_at', 'updated_at']

class DailyMealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMeal
        fields = [
            'date', 'meal_type', 'main_dish', 'side_dish', 'additional_items',
            'extra_portions', 'price_per_portion', 'order_cutoff_time',
            'max_orders', 'pickup_available', 'delivery_available',
            'delivery_radius', 'image'
        ]
    
    def create(self, validated_data):
        validated_data['chef'] = self.context['request'].user
        return super().create(validated_data)
'''
    
    print(serializer_update)

def update_templates():
    """Show how to update templates to display meal images"""
    
    print("\n🎨 Template Updates")
    print("="*30)
    
    template_updates = '''
<!-- Add to daily_meal_card.html or similar templates -->

<div class="meal-card">
    {% if daily_meal.image %}
        <img src="{{ daily_meal.image.url }}" 
             alt="{{ daily_meal.main_dish }}" 
             class="meal-image">
    {% else %}
        <img src="https://picsum.photos/seed/{{ daily_meal.main_dish|slugify }}/400/300.jpg" 
             alt="{{ daily_meal.main_dish }}" 
             class="meal-image placeholder">
    {% endif %}
    
    <div class="meal-details">
        <h4>{{ daily_meal.main_dish }}</h4>
        {% if daily_meal.side_dish %}
            <p class="side-dish">{{ daily_meal.side_dish }}</p>
        {% endif %}
        <p class="price">₹{{ daily_meal.price_per_portion }}/portion</p>
        <p class="chef">by {{ daily_meal.chef.username }}</p>
    </div>
</div>

<style>
.meal-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.meal-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.placeholder {
    opacity: 0.8;
}

.meal-details {
    padding: 1rem;
}

.meal-details h4 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.side-dish {
    color: #666;
    font-size: 0.9rem;
    margin: 0.25rem 0;
}

.price {
    font-weight: bold;
    color: #e74c3c;
    margin: 0.5rem 0;
}

.chef {
    color: #7f8c8d;
    font-size: 0.85rem;
    margin: 0;
}
</style>
'''
    
    print(template_updates)

def main():
    """Main function"""
    print("🍽️ HomeChefs AI - Add Images to Models")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. Show DailyMeal Model Update Instructions")
        print("2. Create Migration File")
        print("3. Show Serializer Updates")
        print("4. Show Template Updates")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            add_image_field_to_daily_meal()
        
        elif choice == '2':
            create_migration_file()
        
        elif choice == '3':
            update_serializers()
        
        elif choice == '4':
            update_templates()
        
        elif choice == '5':
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
