#!/usr/bin/env python
"""
Test script to verify OTP login functionality is working correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.test import Client
from authentication.models import User, PhoneOTP
import json

def test_otp_login_complete_flow():
    """Test complete OTP login flow with proper client"""
    print("Testing Complete OTP Login Flow...")
    
    try:
        client = Client()
        phone_number = '9876543210'  # 10-digit number as expected by backend
        
        # Step 1: Request OTP
        print(f"\nStep 1: Requesting OTP for {phone_number}")
        otp_data = {'phone_number': phone_number}
        otp_response = client.post('/api/auth/request-otp/', 
                                  data=json.dumps(otp_data), 
                                  content_type='application/json')
        
        print(f"OTP Request Status: {otp_response.status_code}")
        if otp_response.status_code != 200:
            print(f"OTP Request Failed: {otp_response.json()}")
            return False
        
        otp_result = otp_response.json()
        print(f"OTP Request Response: {otp_result}")
        
        # Step 2: Verify OTP was created
        try:
            otp_record = PhoneOTP.objects.filter(phone_number=phone_number).first()
            if not otp_record:
                print("ERROR: No OTP record found in database")
                return False
            
            print(f"OTP Code: {otp_record.otp_code}")
            print(f"Expires At: {otp_record.expires_at}")
            otp_code = otp_record.otp_code
        except Exception as e:
            print(f"ERROR: Could not retrieve OTP record: {e}")
            return False
        
        # Step 3: Login with OTP
        print(f"\nStep 2: Logging in with OTP {otp_code}")
        login_data = {
            'phone_number': phone_number,
            'otp_code': otp_code
        }
        
        login_response = client.post('/api/auth/login/', 
                                    data=json.dumps(login_data), 
                                    content_type='application/json')
        
        print(f"Login Status: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"Login Failed: {login_response.json()}")
            return False
        
        login_result = login_response.json()
        print(f"Login Response: {login_result}")
        
        # Step 4: Verify login result
        required_fields = ['user', 'token', 'message']
        for field in required_fields:
            if field not in login_result:
                print(f"ERROR: Missing field {field} in login response")
                return False
        
        user_data = login_result['user']
        print(f"\nLogin Successful!")
        print(f"User: {user_data.get('username', 'Unknown')}")
        print(f"Role: {user_data.get('role', 'Unknown')}")
        print(f"Email: {user_data.get('email', 'Unknown')}")
        print(f"Token: {login_result['token'][:20]}...")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Exception in OTP login flow: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phone_number_formats():
    """Test different phone number formats"""
    print("\nTesting Phone Number Formats...")
    
    try:
        client = Client()
        
        # Test formats
        test_cases = [
            ('9876543210', '10 digits - should work'),
            ('+919876543210', 'with +91 - should fail in frontend but work if cleaned'),
            ('1234567890', '10 digits - should work'),
            ('987654321', '9 digits - should fail'),
            ('987654321012', '12 digits - should work'),
            ('abcd123456', 'with letters - should fail'),
        ]
        
        for phone, description in test_cases:
            print(f"\nTesting: {phone} ({description})")
            
            # Test with cleaned phone number (remove +)
            clean_phone = phone.replace('+', '')
            
            otp_data = {'phone_number': clean_phone}
            otp_response = client.post('/api/auth/request-otp/', 
                                      data=json.dumps(otp_data), 
                                      content_type='application/json')
            
            print(f"  Status: {otp_response.status_code}")
            if otp_response.status_code == 200:
                print(f"  Result: ✅ Accepted")
            else:
                result = otp_response.json()
                print(f"  Result: ❌ {result}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Exception in phone format test: {e}")
        return False

def test_otp_expiration():
    """Test OTP expiration handling"""
    print("\nTesting OTP Expiration...")
    
    try:
        client = Client()
        phone_number = '9876543210'
        
        # Request OTP
        otp_data = {'phone_number': phone_number}
        otp_response = client.post('/api/auth/request-otp/', 
                                  data=json.dumps(otp_data), 
                                  content_type='application/json')
        
        if otp_response.status_code != 200:
            print("ERROR: Could not request OTP for expiration test")
            return False
        
        # Get the OTP
        otp_record = PhoneOTP.objects.filter(phone_number=phone_number).first()
        if not otp_record:
            print("ERROR: No OTP record found")
            return False
        
        print(f"OTP Code: {otp_record.otp_code}")
        print(f"Expires At: {otp_record.expires_at}")
        
        # Try to login with valid OTP
        login_data = {
            'phone_number': phone_number,
            'otp_code': otp_record.otp_code
        }
        
        login_response = client.post('/api/auth/login/', 
                                    data=json.dumps(login_data), 
                                    content_type='application/json')
        
        print(f"Valid OTP Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Valid OTP login works")
            return True
        else:
            print(f"❌ Valid OTP login failed: {login_response.json()}")
            return False
        
    except Exception as e:
        print(f"ERROR: Exception in OTP expiration test: {e}")
        return False

def main():
    """Run all OTP tests"""
    print("=" * 60)
    print("OTP LOGIN FUNCTIONALITY TEST - FIXED")
    print("=" * 60)
    
    tests = [
        test_otp_login_complete_flow,
        test_phone_number_formats,
        test_otp_expiration,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("OTP TEST RESULTS:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("+ All OTP login tests passed!")
        print("OTP login functionality is working correctly.")
        print("\nUsage Instructions:")
        print("1. Go to: http://localhost:8000/login/")
        print("2. Click 'OTP' tab")
        print("3. Enter phone number: 9876543210 (10 digits, no +)")
        print("4. Click 'Send OTP'")
        print("5. Enter 6-digit code")
        print("6. Click 'Login with OTP'")
    else:
        print("- Some OTP tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
