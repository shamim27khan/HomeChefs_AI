#!/usr/bin/env python
"""
Test script for the delivery partners module
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User, ChefProfile
from chefs.models import DailyMeal
from orders.models import DailyMealOrder
from delivery.models import DeliveryPartner, DeliveryRequest, DeliveryAssignment
from delivery.notifications import DeliveryNotificationSystem
from decimal import Decimal

def create_test_data():
    """Create test data for delivery module testing"""
    print("Creating test data...")
    
    # Create test customer
    customer, created = User.objects.get_or_create(
        username='test_customer',
        defaults={
            'email': 'customer@test.com',
            'phone_number': '+1234567890',
            'role': 'customer'
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
        print("Created test customer")
    
    # Create test chef
    chef_user, created = User.objects.get_or_create(
        username='test_chef',
        defaults={
            'email': 'chef@test.com',
            'phone_number': '+1234567891',
            'role': 'chef'
        }
    )
    if created:
        chef_user.set_password('testpass123')
        chef_user.save()
        
        # Create chef profile
        ChefProfile.objects.create(
            user=chef_user,
            bio='Test chef for delivery module',
            cuisine_specialties='Italian, Chinese',
            experience_years=5,
            kitchen_address='123 Chef Street, Test City',
            delivery_radius=10
        )
        print("Created test chef")
    
    # Create test delivery partner
    partner_user, created = User.objects.get_or_create(
        username='test_delivery_partner',
        defaults={
            'email': 'partner@test.com',
            'phone_number': '+1234567892',
            'role': 'delivery_partner'
        }
    )
    if created:
        partner_user.set_password('testpass123')
        partner_user.save()
        
        # Create delivery partner profile
        DeliveryPartner.objects.create(
            user=partner_user,
            phone_number='+1234567892',
            vehicle_type='bike',
            vehicle_number='TEST123',
            license_number='LICENSE123',
            service_areas='Test City, Downtown',
            max_delivery_distance=10,
            status='active',
            verification_status='verified',
            is_available=True
        )
        print("Created test delivery partner")
    
    return customer, chef_user, partner_user

def create_test_order(customer, chef):
    """Create a test order for delivery"""
    # Create daily meal
    daily_meal, _ = DailyMeal.objects.get_or_create(
        chef=chef,
        date='2026-04-22',
        meal_type='lunch',
        defaults={
            'main_dish': 'Test Main Dish',
            'price_per_portion': Decimal('150.00'),
            'extra_portions': 10
        }
    )
    
    # Create order
    order, created = DailyMealOrder.objects.get_or_create(
        order_id='TEST001',
        defaults={
            'daily_meal': daily_meal,
            'customer': customer,
            'portions': 2,
            'price_per_portion': Decimal('150.00'),
            'delivery_type': 'delivery',
            'delivery_address': '456 Customer Street, Test City',
            'order_status': 'ready'
        }
    )
    
    if created:
        print("Created test order")
    else:
        # Update existing order to ready status
        order.order_status = 'ready'
        order.save()
        print("Updated test order to ready status")
    
    return order

def test_delivery_notification():
    """Test the delivery notification system"""
    print("\nTesting delivery notification system...")
    
    customer, chef, partner = create_test_data()
    order = create_test_order(customer, chef)
    
    # Clear existing requests for this order
    DeliveryRequest.objects.filter(order=order).delete()
    
    # Test notification
    requests_created = DeliveryNotificationSystem.notify_available_partners(order)
    print(f"Created {requests_created} delivery requests")
    
    # Check if requests were created
    pending_requests = DeliveryRequest.objects.filter(
        order=order,
        status='pending'
    )
    
    print(f"Found {pending_requests.count()} pending requests")
    
    for request in pending_requests:
        print(f"Request for partner {request.delivery_partner.user.username}")
        print(f"  - Distance: {request.distance_km} km")
        print(f"  - Fee: Rs. {request.delivery_fee}")
        print(f"  - Expires: {request.expires_at}")
    
    return pending_requests.first()

def test_request_acceptance():
    """Test accepting a delivery request"""
    print("\nTesting request acceptance...")
    
    request = test_delivery_notification()
    if not request:
        print("No delivery request found to test acceptance")
        return
    
    print(f"Accepting request {request.id}")
    success = request.accept_request()
    
    if success:
        print("Request accepted successfully!")
        
        # Check if delivery assignment was created
        try:
            assignment = DeliveryAssignment.objects.get(order=request.order)
            print(f"Created delivery assignment {assignment.id}")
            print(f"  - Status: {assignment.status}")
            print(f"  - Fee: Rs. {assignment.delivery_fee}")
            print(f"  - Partner earnings: Rs. {assignment.partner_earnings}")
            
            # Test pickup location details
            pickup_details = assignment.get_pickup_location()
            print(f"  - Pickup: {pickup_details['name']} at {pickup_details['address']}")
            
            # Test delivery location details
            delivery_details = assignment.get_delivery_location()
            print(f"  - Delivery: {delivery_details['name']} at {delivery_details['address']}")
            
        except DeliveryAssignment.DoesNotExist:
            print("No delivery assignment found")
    else:
        print("Failed to accept request")

def test_delivery_status_updates():
    """Test delivery status updates"""
    print("\nTesting delivery status updates...")
    
    # Get an active delivery assignment
    try:
        assignment = DeliveryAssignment.objects.filter(status='assigned').first()
        if not assignment:
            print("No active delivery assignment found")
            return
        
        print(f"Testing status updates for assignment {assignment.id}")
        
        # Test picked up
        assignment.mark_picked_up()
        print(f"  - Marked as picked up at {assignment.actual_pickup_time}")
        
        # Test in transit
        assignment.mark_in_transit()
        print(f"  - Marked as in transit")
        
        # Test delivered
        assignment.mark_delivered(notes="Delivered successfully")
        print(f"  - Marked as delivered at {assignment.actual_delivery_time}")
        print(f"  - Notes: {assignment.delivery_notes}")
        
        # Check partner stats
        partner = assignment.delivery_partner
        print(f"  - Partner total deliveries: {partner.total_deliveries}")
        print(f"  - Partner is available: {partner.is_available}")
        
    except Exception as e:
        print(f"Error testing status updates: {e}")

def test_partner_stats():
    """Test partner statistics"""
    print("\nTesting partner statistics...")
    
    partners = DeliveryPartner.objects.all()
    for partner in partners:
        print(f"\nPartner: {partner.user.username}")
        print(f"  - Status: {partner.status}")
        print(f"  - Verification: {partner.verification_status}")
        print(f"  - Available: {partner.is_available}")
        print(f"  - Total deliveries: {partner.total_deliveries}")
        print(f"  - Average rating: {partner.average_rating}")
        print(f"  - Completion rate: {partner.completion_rate}")
        print(f"  - Service areas: {partner.service_areas}")

def main():
    """Main test function"""
    print("=" * 50)
    print("DELIVERY MODULE TEST")
    print("=" * 50)
    
    try:
        # Run tests
        test_delivery_notification()
        test_request_acceptance()
        test_delivery_status_updates()
        test_partner_stats()
        
        print("\n" + "=" * 50)
        print("TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
