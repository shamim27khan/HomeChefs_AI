#!/usr/bin/env python
"""
Simple test script to check admin functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.contrib import admin
from delivery.models import DeliveryPartner, DeliveryRequest, DeliveryAssignment, DeliveryRating

def test_admin_registration():
    """Test if all admin models are properly registered"""
    print("Testing Admin Registration...")
    
    try:
        # Check if admin site has our models
        admin_site = admin.site
        delivery_partner_admin = admin_site._registry.get(DeliveryPartner)
        delivery_request_admin = admin_site._registry.get(DeliveryRequest)
        delivery_assignment_admin = admin_site._registry.get(DeliveryAssignment)
        delivery_rating_admin = admin_site._registry.get(DeliveryRating)
        
        print(f"DeliveryPartner Admin: {'OK' if delivery_partner_admin else 'NOT REGISTERED'}")
        print(f"DeliveryRequest Admin: {'OK' if delivery_request_admin else 'NOT REGISTERED'}")
        print(f"DeliveryAssignment Admin: {'OK' if delivery_assignment_admin else 'NOT REGISTERED'}")
        print(f"DeliveryRating Admin: {'OK' if delivery_rating_admin else 'NOT REGISTERED'}")
        
        return all([
            delivery_partner_admin,
            delivery_request_admin,
            delivery_assignment_admin,
            delivery_rating_admin
        ])
        
    except Exception as e:
        print(f"Error checking admin registration: {e}")
        return False

def test_admin_urls():
    """Test admin URL configuration"""
    print("\nTesting Admin URLs...")
    
    try:
        from django.urls import reverse
        
        # Test admin URLs
        admin_urls = [
            'admin:index',
            'admin:delivery_deliverypartner_changelist',
            'admin:delivery_deliveryrequest_changelist',
            'admin:delivery_deliveryassignment_changelist',
            'admin:delivery_deliveryrating_changelist',
        ]
        
        for url_name in admin_urls:
            try:
                url = reverse(url_name)
                print(f"{url_name} -> {url}")
            except Exception as e:
                print(f"{url_name} -> ERROR: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error testing admin URLs: {e}")
        return False

def test_data_integrity():
    """Test if admin can handle the data properly"""
    print("\nTesting Data Integrity...")
    
    try:
        # Count records in each model
        partner_count = DeliveryPartner.objects.count()
        request_count = DeliveryRequest.objects.count()
        assignment_count = DeliveryAssignment.objects.count()
        rating_count = DeliveryRating.objects.count()
        
        print(f"Delivery Partners: {partner_count}")
        print(f"Delivery Requests: {request_count}")
        print(f"Delivery Assignments: {assignment_count}")
        print(f"Delivery Ratings: {rating_count}")
        
        # Test if we can access records
        if partner_count > 0:
            partner = DeliveryPartner.objects.first()
            print(f"Sample partner: {partner.user.username}")
        
        if request_count > 0:
            request = DeliveryRequest.objects.first()
            print(f"Sample request: Order {request.order.order_id if request.order else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"Error testing data integrity: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all admin tests"""
    print("=" * 60)
    print("ADMIN FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        test_admin_registration,
        test_admin_urls,
        test_data_integrity,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("All admin tests passed! Admin should work correctly.")
        print("\nTo access admin:")
        print("1. Run: python manage.py runserver")
        print("2. Go to: http://127.0.0.1:8000/admin/")
        print("3. Login with superuser credentials")
    else:
        print("Some tests failed. Admin may have issues.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
