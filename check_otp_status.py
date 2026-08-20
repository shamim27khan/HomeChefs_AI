#!/usr/bin/env python
"""
Simple check for OTP functionality status
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from authentication.models import User, PhoneOTP

def check_otp_status():
    """Check if OTP functionality is properly configured"""
    
    print("HomeChefs AI - OTP Status Check")
    print("=" * 40)
    
    # Check models
    try:
        otp_count = PhoneOTP.objects.count()
        user_count = User.objects.count()
        
        print(f"Database Status:")
        print(f"  - PhoneOTP records: {otp_count}")
        print(f"  - User records: {user_count}")
        
        if otp_count > 0:
            print(f"\nRecent OTP records:")
            recent_otps = PhoneOTP.objects.order_by('-created_at')[:3]
            for otp in recent_otps:
                print(f"  - {otp.phone_number}: {otp.otp_code} (Verified: {otp.is_verified})")
        
    except Exception as e:
        print(f"Database error: {e}")
        return False
    
    # Check URLs
    try:
        from django.urls import reverse
        
        try:
            otp_request_url = reverse('request_otp')
            print(f"\nURL Configuration:")
            print(f"  - OTP Request URL: {otp_request_url}")
        except:
            print("  - OTP Request URL: NOT FOUND")
        
        try:
            otp_verify_url = reverse('verify_otp')
            print(f"  - OTP Verify URL: {otp_verify_url}")
        except:
            print("  - OTP Verify URL: NOT FOUND")
        
    except Exception as e:
        print(f"URL check error: {e}")
    
    # Check template
    try:
        template_path = "HomeChefs/templates/HomeChefs/base.html"
        with open(template_path, 'r') as f:
            content = f.read()
        
        print(f"\nTemplate Check:")
        if 'id="otp-tab"' in content:
            print("  - OTP tab: FOUND")
        else:
            print("  - OTP tab: NOT FOUND")
        
        if 'id="otp-login"' in content:
            print("  - OTP login form: FOUND")
        else:
            print("  - OTP login form: NOT FOUND")
        
        if 'function sendLoginOTP()' in content:
            print("  - sendLoginOTP function: FOUND")
        else:
            print("  - sendLoginOTP function: NOT FOUND")
        
    except Exception as e:
        print(f"Template check error: {e}")
    
    print(f"\nTroubleshooting:")
    print("  1. Open browser and go to http://localhost:8000")
    print("  2. Click login button")
    print("  3. Check if 'OTP' tab is visible")
    print("  4. Click OTP tab and test functionality")
    print("  5. Check browser console for JavaScript errors")

if __name__ == '__main__':
    check_otp_status()
