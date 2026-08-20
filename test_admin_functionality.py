#!/usr/bin/env python
"""
Test script to check admin functionality and identify potential issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.contrib import admin
from django.test import RequestFactory
from django.contrib.auth.models import User
from delivery.models import DeliveryPartner, DeliveryRequest, DeliveryAssignment, DeliveryRating
from delivery.admin import DeliveryPartnerAdmin, DeliveryRequestAdmin, DeliveryAssignmentAdmin, DeliveryRatingAdmin

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
        
        print(f"+ DeliveryPartner Admin: {'Registered' if delivery_partner_admin else 'NOT REGISTERED'}")
        print(f"+ DeliveryRequest Admin: {'Registered' if delivery_request_admin else 'NOT REGISTERED'}")
        print(f"+ DeliveryAssignment Admin: {'Registered' if delivery_assignment_admin else 'NOT REGISTERED'}")
        print(f"+ DeliveryRating Admin: {'Registered' if delivery_rating_admin else 'NOT REGISTERED'}")
        
        return all([
            delivery_partner_admin,
            delivery_request_admin,
            delivery_assignment_admin,
            delivery_rating_admin
        ])
        
    except Exception as e:
        print(f"- Error checking admin registration: {e}")
        return False

def test_admin_list_display():
    """Test admin list_display methods"""
    print("\nTesting Admin List Display...")
    
    try:
        # Create mock request
        factory = RequestFactory()
        request = factory.get('/admin/')
        
        # Test DeliveryPartnerAdmin
        partner_admin = DeliveryPartnerAdmin(DeliveryPartner, admin.site)
        partner_admin.request = request
        
        # Test DeliveryRequestAdmin
        request_admin = DeliveryRequestAdmin(DeliveryRequest, admin.site)
        request_admin.request = request
        
        # Test DeliveryAssignmentAdmin
        assignment_admin = DeliveryAssignmentAdmin(DeliveryAssignment, admin.site)
        assignment_admin.request = request
        
        # Test DeliveryRatingAdmin
        rating_admin = DeliveryRatingAdmin(DeliveryRating, admin.site)
        rating_admin.request = request
        
        print("✓ All admin classes instantiated successfully")
        
        # Test custom methods
        if hasattr(request_admin, 'order_id'):
            print("✓ DeliveryRequestAdmin.order_id method exists")
        if hasattr(request_admin, 'partner_name'):
            print("✓ DeliveryRequestAdmin.partner_name method exists")
            
        if hasattr(assignment_admin, 'order_id'):
            print("✓ DeliveryAssignmentAdmin.order_id method exists")
        if hasattr(assignment_admin, 'partner_name'):
            print("✓ DeliveryAssignmentAdmin.partner_name method exists")
            
        if hasattr(rating_admin, 'order_id'):
            print("✓ DeliveryRatingAdmin.order_id method exists")
        if hasattr(rating_admin, 'customer_name'):
            print("✓ DeliveryRatingAdmin.customer_name method exists")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing admin list display: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_queryset():
    """Test admin queryset methods"""
    print("\nTesting Admin QuerySets...")
    
    try:
        # Test DeliveryRequestAdmin queryset
        request_admin = DeliveryRequestAdmin(DeliveryRequest, admin.site)
        queryset = request_admin.get_queryset(None)
        print("✓ DeliveryRequestAdmin queryset works")
        
        # Test DeliveryAssignmentAdmin queryset
        assignment_admin = DeliveryAssignmentAdmin(DeliveryAssignment, admin.site)
        queryset = assignment_admin.get_queryset(None)
        print("✓ DeliveryAssignmentAdmin queryset works")
        
        # Test DeliveryRatingAdmin queryset
        rating_admin = DeliveryRatingAdmin(DeliveryRating, admin.site)
        queryset = rating_admin.get_queryset(None)
        print("✓ DeliveryRatingAdmin queryset works")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing admin querysets: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_actions():
    """Test admin actions"""
    print("\nTesting Admin Actions...")
    
    try:
        # Create test user and partner
        user, _ = User.objects.get_or_create(
            username='test_admin_user',
            defaults={'email': 'admin@test.com', 'role': 'delivery_partner'}
        )
        
        partner, _ = DeliveryPartner.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': '+1234567890',
                'vehicle_type': 'bike',
                'vehicle_number': 'TEST123',
                'license_number': 'LICENSE123',
                'service_areas': 'Test Area',
                'verification_status': 'pending'
            }
        )
        
        # Test DeliveryPartnerAdmin actions
        partner_admin = DeliveryPartnerAdmin(DeliveryPartner, admin.site)
        
        # Test verify action
        queryset = DeliveryPartner.objects.filter(id=partner.id)
        partner_admin.verify_partners(None, queryset)
        print("✓ verify_partners action works")
        
        # Test activate action
        partner_admin.activate_partners(None, queryset)
        print("✓ activate_partners action works")
        
        # Test deactivate action
        partner_admin.deactivate_partners(None, queryset)
        print("✓ deactivate_partners action works")
        
        # Clean up
        partner.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing admin actions: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_urls():
    """Test admin URL configuration"""
    print("\nTesting Admin URLs...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        # Test admin URLs
        admin_urls = [
            'admin:index',
            'admin:delivery_deliverypartner_changelist',
            'admin:delivery_deliveryrequest_changelist',
            'admin:delivery_deliveryassignment_changelist',
            'admin:delivery_deliveryrating_changelist',
        ]
        
        client = Client()
        
        for url_name in admin_urls:
            try:
                url = reverse(url_name)
                print(f"✓ {url_name} -> {url}")
            except Exception as e:
                print(f"✗ {url_name} -> ERROR: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing admin URLs: {e}")
        return False

def main():
    """Run all admin tests"""
    print("=" * 60)
    print("ADMIN FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        test_admin_registration,
        test_admin_list_display,
        test_admin_queryset,
        test_admin_actions,
        test_admin_urls,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All admin tests passed! Admin should work correctly.")
    else:
        print("✗ Some tests failed. Admin may have issues.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
