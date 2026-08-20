#!/usr/bin/env python
"""
Test script to debug delivery assignment system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from delivery.models import DeliveryPartner, DeliveryRequest, DeliveryAssignment
from authentication.models import User
from orders.models import DailyMealOrder
from chefs.models import DailyMeal

def test_delivery_system():
    """Debug delivery assignment system"""
    print("=" * 60)
    print("DELIVERY ASSIGNMENT SYSTEM DEBUG")
    print("=" * 60)
    
    try:
        # Check Arshia's orders
        print("\n1. Checking Arshia's orders...")
        try:
            arshia_user = User.objects.get(username='Arshi')
            arshia_orders = DailyMealOrder.objects.filter(customer=arshia_user).order_by('-created_at')[:5]
            print(f"Arshia user ID: {arshia_user.id}")
            print(f"Arshia orders: {arshia_orders.count()}")
            
            for order in arshia_orders:
                print(f"  - Order #{order.id}: {order.daily_meal.main_dish}")
                print(f"    Status: {order.order_status}")
                print(f"    Created: {order.created_at}")
                print(f"    Has delivery assignment: {hasattr(order, 'deliveryassignment')}")
                
                # Check if this order should be assigned for delivery
                if order.order_status == 'confirmed':
                    print(f"    [PENDING DELIVERY ASSIGNMENT]")
                elif hasattr(order, 'deliveryassignment'):
                    print(f"    [ASSIGNED TO: {order.deliveryassignment.delivery_partner.user.username}]")
                else:
                    print(f"    [NO DELIVERY ASSIGNMENT]")
        except Exception as e:
            print(f"Error checking Arshia orders: {e}")
        
        # Check all recent orders that need delivery
        print("\n2. Checking all orders needing delivery...")
        orders_needing_delivery = DailyMealOrder.objects.filter(
            order_status__in=['confirmed', 'preparing']
        ).order_by('-created_at')[:10]
        
        print(f"Orders needing delivery: {orders_needing_delivery.count()}")
        
        for order in orders_needing_delivery:
            print(f"  - Order #{order.id}: {order.daily_meal.main_dish}")
            print(f"    Customer: {order.customer.username if order.customer else 'None'}")
            print(f"    Chef: {order.daily_meal.chef.username}")
            print(f"    Status: {order.order_status}")
            
            # Check delivery assignment
            if hasattr(order, 'deliveryassignment'):
                print(f"    [ASSIGNED TO: {order.deliveryassignment.delivery_partner.user.username}]")
            else:
                print(f"    [NOT ASSIGNED - NEEDS DELIVERY PARTNER]")
        
        # Check delivery partners
        print("\n3. Checking delivery partners...")
        partners = DeliveryPartner.objects.all()
        print(f"Total delivery partners: {partners.count()}")
        
        for partner in partners:
            print(f"  - {partner.user.username}:")
            print(f"    Status: {partner.status}")
            print(f"    Available: {partner.is_available}")
            print(f"    Verified: {partner.verification_status}")
        
        # Check delivery assignments
        print("\n4. Checking delivery assignments...")
        assignments = DeliveryAssignment.objects.all()
        print(f"Total assignments: {assignments.count()}")
        
        for assignment in assignments:
            print(f"  - Assignment #{assignment.id}:")
            print(f"    Order #{assignment.order.id}")
            print(f"    Delivery Partner: {assignment.delivery_partner.user.username}")
            print(f"    Status: {assignment.status}")
            print(f"    Created: {assignment.created_at}")
        
        # Check delivery requests
        print("\n5. Checking delivery requests...")
        requests = DeliveryRequest.objects.all()
        print(f"Total requests: {requests.count()}")
        
        for request in requests:
            print(f"  - Request #{request.id}:")
            print(f"    Order #{request.order.id}")
            print(f"    Delivery Partner: {request.delivery_partner.user.username}")
            print(f"    Status: {request.status}")
            print(f"    Created: {request.created_at}")
        
        return True
        
    except Exception as e:
        print(f"Error in delivery system test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run delivery system test"""
    success = test_delivery_system()
    
    print("\n" + "=" * 60)
    print("DELIVERY SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("[OK] Test completed successfully")
        print("Check output above to identify delivery assignment issues")
    else:
        print("[ERROR] Test failed with errors")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
