#!/usr/bin/env python
"""
Test script to verify OTP functionality is working
"""

import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User, PhoneOTP

def test_otp_endpoints():
    """Test OTP API endpoints"""
    
    base_url = "http://localhost:8000/api/auth"
    
    print("Testing OTP Functionality")
    print("=" * 50)
    
    # Test 1: Request OTP
    print("\n1. Testing OTP Request Endpoint")
    print("-" * 30)
    
    test_phone = "+919876543210"
    
    try:
        response = requests.post(f"{base_url}/request-otp/", json={
            "phone_number": test_phone
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            otp_code = result.get('otp_code')
            print(f"✅ OTP generated: {otp_code}")
            return otp_code, test_phone
        else:
            print(f"❌ OTP request failed: {response.text}")
            return None, test_phone
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure Django is running on localhost:8000")
        return None, test_phone
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, test_phone

def test_otp_verification(otp_code, phone_number):
    """Test OTP verification endpoint"""
    
    base_url = "http://localhost:8000/api/auth"
    
    print("\n2. Testing OTP Verification Endpoint")
    print("-" * 35)
    
    if not otp_code:
        print("❌ No OTP code to test")
        return False
    
    try:
        response = requests.post(f"{base_url}/verify-otp/", json={
            "phone_number": phone_number,
            "otp_code": otp_code
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ OTP verification successful")
            return True
        else:
            print(f"❌ OTP verification failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_otp_login(otp_code, phone_number):
    """Test OTP login endpoint"""
    
    base_url = "http://localhost:8000/api/auth"
    
    print("\n3. Testing OTP Login Endpoint")
    print("-" * 30)
    
    if not otp_code:
        print("❌ No OTP code to test")
        return False
    
    try:
        response = requests.post(f"{base_url}/login/", json={
            "phone_number": phone_number,
            "otp_code": otp_code
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ OTP login successful")
            return True
        else:
            print(f"❌ OTP login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_database_models():
    """Check if OTP models exist in database"""
    
    print("\n4. Checking Database Models")
    print("-" * 25)
    
    try:
        # Check PhoneOTP model
        otp_count = PhoneOTP.objects.count()
        print(f"✅ PhoneOTP model exists - {otp_count} records in database")
        
        # Check User model
        user_count = User.objects.count()
        print(f"✅ User model exists - {user_count} records in database")
        
        # Show recent OTP records
        recent_otps = PhoneOTP.objects.order_by('-created_at')[:5]
        if recent_otps:
            print("\nRecent OTP records:")
            for otp in recent_otps:
                print(f"  - {otp.phone_number}: {otp.otp_code} (Verified: {otp.is_verified})")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_urls():
    """Check if OTP URLs are registered"""
    
    print("\n5. Checking URL Configuration")
    print("-" * 28)
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        # Test URL resolution
        try:
            otp_request_url = reverse('request_otp')
            print(f"✅ OTP Request URL: {otp_request_url}")
        except:
            print("❌ OTP Request URL not found")
        
        try:
            otp_verify_url = reverse('verify_otp')
            print(f"✅ OTP Verify URL: {otp_verify_url}")
        except:
            print("❌ OTP Verify URL not found")
        
        return True
        
    except Exception as e:
        print(f"❌ URL check error: {e}")
        return False

def check_template_elements():
    """Check if OTP elements exist in template"""
    
    print("\n6. Checking Template Elements")
    print("-" * 30)
    
    template_path = "HomeChefs/templates/HomeChefs/base.html"
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for OTP tab
        if 'id="otp-tab"' in content:
            print("✅ OTP tab found in template")
        else:
            print("❌ OTP tab not found in template")
        
        # Check for OTP login form
        if 'id="otp-login"' in content:
            print("✅ OTP login form found in template")
        else:
            print("❌ OTP login form not found in template")
        
        # Check for OTP JavaScript functions
        if 'function sendLoginOTP()' in content:
            print("✅ sendLoginOTP function found")
        else:
            print("❌ sendLoginOTP function not found")
        
        if 'function verifyLoginOTP()' in content:
            print("✅ verifyLoginOTP function found")
        else:
            print("❌ verifyLoginOTP function not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Template check error: {e}")
        return False

def main():
    """Main test function"""
    print("HomeChefs AI - OTP Functionality Test")
    print("=" * 50)
    
    # Run all tests
    check_database_models()
    check_urls()
    check_template_elements()
    
    # Test API endpoints (if server is running)
    print("\n" + "="*50)
    print("API ENDPOINT TESTS (requires server running)")
    print("="*50)
    
    otp_code, phone_number = test_otp_endpoints()
    
    if otp_code:
        test_otp_verification(otp_code, phone_number)
        test_otp_login(otp_code, phone_number)
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    print("\nIf OTP is not visible in the UI:")
    print("1. Check browser console for JavaScript errors")
    print("2. Verify Bootstrap CSS is loaded properly")
    print("3. Check if OTP tab is hidden by CSS")
    print("4. Test by clicking the OTP tab in login modal")
    
    print("\nTo manually test OTP in browser:")
    print("1. Open login modal")
    print("2. Click on 'OTP' tab")
    print("3. Enter phone number and click 'Send OTP'")
    print("4. Check console for OTP code (development)")
    print("5. Enter OTP and click 'Login with OTP'")

if __name__ == '__main__':
    main()
