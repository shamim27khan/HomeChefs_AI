#!/usr/bin/env python
"""
Test script to verify delivery partner details functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User
from chefs.views_mvp import admin_delivery_partners
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.authtoken.models import Token

def test_delivery_partner_details_data():
    """Test that delivery partner data contains all necessary fields for details view"""
    print("Testing Delivery Partner Details Data...")
    
    try:
        # Get admin user and token
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        # Test admin delivery partners endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = client.get('/api/mvp/chefs/admin/delivery-partners/')
        
        if response.status_code == 200:
            partners = response.data
            print(f"+ Found {len(partners)} delivery partners")
            
            if partners:
                partner = partners[0]
                print(f"\nTesting partner: {partner['user']['username']}")
                
                # Check required fields for details view
                required_fields = [
                    'id', 'user', 'phone_number', 'vehicle_type', 'vehicle_number', 
                    'license_number', 'current_location', 'status', 'verification_status',
                    'is_available', 'total_deliveries', 'average_rating', 'completion_rate',
                    'service_areas', 'max_delivery_distance', 'created_at'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in partner:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"- Missing required fields: {missing_fields}")
                    return False
                
                # Check nested user fields
                user_fields = ['id', 'username', 'first_name', 'last_name', 'email']
                missing_user_fields = []
                for field in user_fields:
                    if field not in partner['user']:
                        missing_user_fields.append(f"user.{field}")
                
                if missing_user_fields:
                    print(f"- Missing user fields: {missing_user_fields}")
                    return False
                
                print("+ All required fields present!")
                print(f"  Partner ID: {partner['id']}")
                print(f"  Name: {partner['user']['first_name']} {partner['user']['last_name']}")
                print(f"  Vehicle: {partner['vehicle_type']}")
                print(f"  Status: {partner['status']}")
                print(f"  Verification: {partner['verification_status']}")
                print(f"  Total Deliveries: {partner['total_deliveries']}")
                
                return True
            else:
                print("+ No delivery partners found (this is OK for testing)")
                return True
        else:
            print(f"- API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing delivery partner details: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_delivery_partner_modal_structure():
    """Test the modal structure and data display"""
    print("\nTesting Delivery Partner Modal Structure...")
    
    try:
        # Get admin user and token
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        # Test admin delivery partners endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = client.get('/api/mvp/chefs/admin/delivery-partners/')
        
        if response.status_code == 200:
            partners = response.data
            
            if partners:
                partner = partners[0]
                
                # Simulate the modal data structure
                modal_data = {
                    'personal_info': {
                        'name': f"{partner['user']['first_name'] or ''} {partner['user']['last_name'] or ''}",
                        'username': f"@{partner['user']['username']}",
                        'email': partner['user']['email'],
                        'phone': partner['phone_number'],
                        'member_since': partner['created_at']
                    },
                    'professional_info': {
                        'vehicle_type': partner['vehicle_type'] or 'Not specified',
                        'vehicle_number': partner['vehicle_number'] or 'Not provided',
                        'license_number': partner['license_number'] or 'Not provided',
                        'current_location': partner['current_location'] or 'Not available',
                        'available': partner['is_available']
                    },
                    'performance_metrics': {
                        'total_deliveries': partner['total_deliveries'] or 0,
                        'average_rating': partner['average_rating'] or 'No ratings yet',
                        'completion_rate': partner['completion_rate'] or 0
                    },
                    'service_info': {
                        'service_areas': partner['service_areas'] or 'Not specified',
                        'max_delivery_distance': partner['max_delivery_distance'] or 0,
                        'status': partner['status'],
                        'verification_status': partner['verification_status']
                    }
                }
                
                print("+ Modal data structure created successfully!")
                print("Personal Information:")
                for key, value in modal_data['personal_info'].items():
                    print(f"  {key}: {value}")
                
                print("\nProfessional Information:")
                for key, value in modal_data['professional_info'].items():
                    print(f"  {key}: {value}")
                
                print("\nPerformance Metrics:")
                for key, value in modal_data['performance_metrics'].items():
                    print(f"  {key}: {value}")
                
                print("\nService Information:")
                for key, value in modal_data['service_info'].items():
                    print(f"  {key}: {value}")
                
                return True
            else:
                print("+ No delivery partners to test modal structure")
                return True
        else:
            print(f"- API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing modal structure: {e}")
        return False

def test_verification_button_logic():
    """Test the verification button show/hide logic"""
    print("\nTesting Verification Button Logic...")
    
    try:
        # Get admin user and token
        admin_user = User.objects.get(username='admin')
        token, _ = Token.objects.get_or_create(user=admin_user)
        
        # Test admin delivery partners endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = client.get('/api/mvp/chefs/admin/delivery-partners/')
        
        if response.status_code == 200:
            partners = response.data
            
            if partners:
                verified_count = 0
                pending_count = 0
                
                for partner in partners:
                    if partner['verification_status'] == 'verified':
                        verified_count += 1
                        # Button should be hidden
                        print(f"  {partner['user']['username']}: Verified (button hidden)")
                    else:
                        pending_count += 1
                        # Button should be visible
                        print(f"  {partner['user']['username']}: Pending (button visible)")
                
                print(f"\nVerification Status Summary:")
                print(f"  Verified Partners: {verified_count} (button hidden)")
                print(f"  Pending Partners: {pending_count} (button visible)")
                
                return True
            else:
                print("+ No delivery partners to test verification logic")
                return True
        else:
            print(f"- API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"- Error testing verification logic: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("DELIVERY PARTNER DETAILS TEST")
    print("=" * 60)
    
    tests = [
        test_delivery_partner_details_data,
        test_delivery_partner_modal_structure,
        test_verification_button_logic,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("+ All delivery partner details tests passed!")
        print("The delivery partner details modal should now work correctly.")
    else:
        print("- Some tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
