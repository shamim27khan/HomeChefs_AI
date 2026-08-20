#!/usr/bin/env python
"""
Script to manually create delivery requests for existing orders
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from orders.models import DailyMealOrder
from delivery.models import DeliveryPartner, DeliveryRequest

def create_delivery_requests_for_order(order_id):
    """Create delivery requests for a specific order"""
    try:
        order = DailyMealOrder.objects.get(id=order_id)
        print(f"Processing Order #{order.id}: {order.daily_meal.main_dish}")
        print(f"Status: {order.order_status}")
        print(f"Customer: {order.customer.username}")
        print(f"Chef: {order.daily_meal.chef.username}")
        
        # Get available delivery partners
        available_partners = DeliveryPartner.objects.filter(
            is_available=True,
            verification_status='verified'
        )
        
        print(f"Available delivery partners: {available_partners.count()}")
        
        # Create delivery requests
        delivery_requests_created = 0
        for partner in available_partners:
            print(f"  - Creating request for {partner.user.username}")
            
            # Check if request already exists
            existing_request = DeliveryRequest.objects.filter(
                order=order,
                delivery_partner=partner,
                status='pending'
            ).first()
            
            if not existing_request:
                from django.utils import timezone
                from datetime import timedelta
                from decimal import Decimal
                
                # Calculate estimated times and fees
                estimated_pickup_time = order.estimated_ready_time or (timezone.now() + timedelta(minutes=15))
                estimated_delivery_time = estimated_pickup_time + timedelta(minutes=30)
                delivery_fee = order.delivery_fee or Decimal('50.00')  # Default delivery fee
                
                DeliveryRequest.objects.create(
                    order=order,
                    delivery_partner=partner,
                    status='pending',
                    estimated_pickup_time=estimated_pickup_time,
                    estimated_delivery_time=estimated_delivery_time,
                    delivery_fee=delivery_fee
                )
                delivery_requests_created += 1
                print(f"    ✓ Request created")
            else:
                print(f"    - Request already exists")
        
        # Update order status if needed
        if delivery_requests_created > 0 and order.order_status == 'ready':
            order.order_status = 'out_for_delivery'
            order.save()
            print(f"✓ Order status updated to 'out_for_delivery'")
        
        print(f"\nCreated {delivery_requests_created} delivery requests for Order #{order.id}")
        return delivery_requests_created
        
    except DailyMealOrder.DoesNotExist:
        print(f"Order #{order_id} not found")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def create_delivery_requests_for_all_ready_orders():
    """Create delivery requests for all orders that need delivery"""
    try:
        # Get orders that need delivery
        orders_needing_delivery = DailyMealOrder.objects.filter(
            order_status__in=['ready', 'preparing']
        )
        
        print(f"Found {orders_needing_delivery.count()} orders needing delivery")
        
        total_requests_created = 0
        for order in orders_needing_delivery:
            print(f"\n{'='*50}")
            requests_created = create_delivery_requests_for_order(order.id)
            total_requests_created += requests_created
        
        print(f"\n{'='*50}")
        print(f"Total delivery requests created: {total_requests_created}")
        return total_requests_created
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

def main():
    """Main function"""
    print("=" * 60)
    print("DELIVERY REQUESTS CREATION")
    print("=" * 60)
    
    print("\n1. Creating delivery requests for Order #9 (ready for pickup)...")
    requests_created = create_delivery_requests_for_order(9)
    
    print("\n2. Creating delivery requests for all orders needing delivery...")
    total_created = create_delivery_requests_for_all_ready_orders()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Delivery requests for Order #9: {requests_created}")
    print(f"Total delivery requests created: {total_created}")
    
    if total_created > 0:
        print("✅ Delivery partners should now see pending requests in their dashboard")
    else:
        print("❌ No delivery requests created")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
