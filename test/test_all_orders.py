#!/usr/bin/env python
"""
Test script to check all orders in the system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from orders.models import DailyMealOrder
from authentication.models import User

def test_all_orders():
    """Check all orders in the system"""
    print("=" * 60)
    print("ALL ORDERS SYSTEM DEBUG")
    print("=" * 60)
    
    try:
        # Check all orders
        print("\n1. Checking all orders...")
        all_orders = DailyMealOrder.objects.all().order_by('-created_at')[:20]
        print(f"Total orders: {all_orders.count()}")
        
        # Group by status
        status_counts = {}
        for order in all_orders:
            status = order.order_status
            if status not in status_counts:
                status_counts[status] = 0
            status_counts[status] += 1
        
        print("Orders by status:")
        for status, count in status_counts.items():
            print(f"  - {status}: {count}")
        
        # Show recent orders with details
        print("\n2. Recent orders with details:")
        for order in all_orders[:10]:
            print(f"  Order #{order.id}:")
            print(f"    Customer: {order.customer.username if order.customer else 'None'}")
            print(f"    Chef: {order.daily_meal.chef.username}")
            print(f"    Meal: {order.daily_meal.main_dish}")
            print(f"    Status: {order.order_status}")
            print(f"    Created: {order.created_at}")
            print(f"    Price: {order.total_amount}")
            print()
        
        return True
        
    except Exception as e:
        print(f"Error checking all orders: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all orders test"""
    success = test_all_orders()
    
    print("\n" + "=" * 60)
    print("ALL ORDERS TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("[OK] Test completed successfully")
    else:
        print("[ERROR] Test failed with errors")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
