#!/usr/bin/env python
"""
Test script to verify OTP login functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User, PhoneOTP
from authentication.views import request_otp, user_login
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth import authenticate
import json

def test_otp_request_endpoint():
    """Test the OTP request endpoint"""
    print("Testing OTP Request Endpoint...")
    
    try:
        factory = APIRequestFactory()
        
        # Test with a valid phone number
        phone_number = "+919876543210"
        request_data = {
            'phone_number': phone_number
        }
        
        request = factory.post('/api/auth/request-otp/', 
                              data=json.dumps(request_data), 
                              content_type='application/json')
        
        response = request_otp(request)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data}")
        
        if response.status_code == 200:
            print("+ OTP request successful!")
            
            # Check if OTP was created
            try:
                otp_record = PhoneOTP.objects.filter(phone_number=phone_number).first()
                if otp_record:
                    print(f"+ OTP created for {phone_number}")
                    print(f"  OTP Code: {otp_record.otp_code}")
                    print(f"  Expires At: {otp_record.expires_at}")
                    return otp_record.otp_code
                else:
                    print("- No OTP record found")
                    return None
            except Exception as e:
                print(f"- Error checking OTP record: {e}")
                return None
        else:
            print(f"- OTP request failed: {response.data}")
            return None
            
    except Exception as e:
        print(f"- Error testing OTP request: {e}")
        return None

def test_otp_login_endpoint():
    """Test the OTP login endpoint"""
    print("\nTesting OTP Login Endpoint...")
    
    try:
        # First request an OTP
        otp_code = test_otp_request_endpoint()
        
        if not otp_code:
            print("- Cannot test OTP login without OTP")
            return False
        
        factory = APIRequestFactory()
        phone_number = "+919876543210"
        
        # Test OTP login
        login_data = {
            'phone_number': phone_number,
            'otp_code': otp_code
        }
        
        request = factory.post('/api/auth/login/', 
                              data=json.dumps(login_data), 
                              content_type='application/json')
        
        response = user_login(request)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data}")
        
        if response.status_code == 200:
            print("+ OTP login successful!")
            
            # Check if token was generated
            if 'token' in response.data:
                print(f"+ Token generated: {response.data['token'][:20]}...")
            
            # Check if user data is returned
            if 'user' in response.data:
                user_data = response.data['user']
                print(f"+ User data: {user_data.get('username', 'N/A')} ({user_data.get('role', 'N/A')})")
            
            return True
        else:
            print(f"- OTP login failed: {response.data}")
            return False
            
    except Exception as e:
        print(f"- Error testing OTP login: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_existing_user_otp_login():
    """Test OTP login with existing user"""
    print("\nTesting OTP Login with Existing User...")
    
    try:
        # Check if we have any users with phone numbers
        users_with_phone = User.objects.exclude(phone_number__isnull=True).exclude(phone_number='')
        
        if users_with_phone.exists():
            user = users_with_phone.first()
            print(f"Testing with existing user: {user.username}")
            print(f"Phone: {user.phone_number}")
            print(f"Role: {user.role}")
            
            # Request OTP for this user
            factory = APIRequestFactory()
            request_data = {'phone_number': user.phone_number}
            
            request = factory.post('/api/auth/request-otp/', 
                                  data=json.dumps(request_data), 
                                  content_type='application/json')
            
            otp_response = request_otp(request)
            
            if otp_response.status_code == 200:
                print("+ OTP requested successfully for existing user")
                
                # Get the OTP code
                otp_record = PhoneOTP.objects.filter(phone_number=user.phone_number).first()
                if otp_record:
                    # Test login with this OTP
                    login_data = {
                        'phone_number': user.phone_number,
                        'otp_code': otp_record.otp_code
                    }
                    
                    login_request = factory.post('/api/auth/login/', 
                                              data=json.dumps(login_data), 
                                              content_type='application/json')
                    
                    login_response = user_login(login_request)
                    
                    if login_response.status_code == 200:
                        print("+ OTP login successful for existing user!")
                        print(f"  User: {login_response.data['user']['username']}")
                        print(f"  Role: {login_response.data['user']['role']}")
                        return True
                    else:
                        print(f"- OTP login failed: {login_response.data}")
                        return False
                else:
                    print("- No OTP record found")
                    return False
            else:
                print(f"- OTP request failed: {otp_response.data}")
                return False
        else:
            print("- No users with phone numbers found")
            return False
            
    except Exception as e:
        print(f"- Error testing existing user OTP login: {e}")
        return False

def test_otp_verification_flow():
    """Test complete OTP verification flow"""
    print("\nTesting Complete OTP Verification Flow...")
    
    try:
        phone_number = "+919876543210"
        
        # Step 1: Request OTP
        factory = APIRequestFactory()
        request_data = {'phone_number': phone_number}
        
        request = factory.post('/api/auth/request-otp/', 
                              data=json.dumps(request_data), 
                              content_type='application/json')
        
        otp_response = request_otp(request)
        
        if otp_response.status_code != 200:
            print(f"- Step 1 failed: OTP request - {otp_response.data}")
            return False
        
        print("+ Step 1: OTP requested successfully")
        
        # Step 2: Get OTP code
        otp_record = PhoneOTP.objects.filter(phone_number=phone_number).first()
        if not otp_record:
            print("- Step 2 failed: No OTP record found")
            return False
        
        print(f"+ Step 2: OTP code retrieved: {otp_record.otp_code}")
        
        # Step 3: Verify OTP
        login_data = {
            'phone_number': phone_number,
            'otp_code': otp_record.otp_code
        }
        
        login_request = factory.post('/api/auth/login/', 
                                    data=json.dumps(login_data), 
                                    content_type='application/json')
        
        login_response = user_login(login_request)
        
        if login_response.status_code != 200:
            print(f"- Step 3 failed: OTP verification - {login_response.data}")
            return False
        
        print("+ Step 3: OTP verification successful")
        
        # Step 4: Check response data
        response_data = login_response.data
        required_fields = ['user', 'token', 'message']
        
        for field in required_fields:
            if field not in response_data:
                print(f"- Step 4 failed: Missing field {field}")
                return False
        
        print("+ Step 4: Response data complete")
        print(f"  User: {response_data['user']['username']}")
        print(f"  Token: {response_data['token'][:20]}...")
        print(f"  Message: {response_data['message']}")
        
        return True
        
    except Exception as e:
        print(f"- Error in OTP verification flow: {e}")
        return False

def main():
    """Run all OTP tests"""
    print("=" * 60)
    print("OTP LOGIN FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        test_otp_request_endpoint,
        test_otp_login_endpoint,
        test_existing_user_otp_login,
        test_otp_verification_flow,
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
    else:
        print("- Some OTP tests failed.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
