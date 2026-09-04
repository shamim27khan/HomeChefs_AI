#!/usr/bin/env python
"""
Debug script to test login functionality step by step
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings')
django.setup()

from django.test import Client
from django.contrib.auth import authenticate
from authentication.models import User
from rest_framework.authtoken.models import Token
import json

def test_login_via_client():
    """Test login using Django test client"""
    print("=== Testing Login via Django Client ===")
    
    client = Client()
    
    # Test POST request to login endpoint
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = client.post(
            '/api/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Content: {response.content.decode()}")
        
        if response.status_code == 200:
            print("Login successful!")
            response_data = json.loads(response.content)
            print(f"Token: {response_data.get('token', 'N/A')}")
            print(f"User: {response_data.get('user', {}).get('username', 'N/A')}")
        else:
            print("Login failed!")
            
    except Exception as e:
        print(f"Exception during login: {e}")
        import traceback
        traceback.print_exc()

def test_manual_login():
    """Test manual login process"""
    print("\n=== Testing Manual Login Process ===")
    
    try:
        # Step 1: Authenticate user
        user = authenticate(username='admin', password='admin123')
        if not user:
            print("Authentication failed")
            return
        
        print(f"Authenticated user: {user.username}")
        
        # Step 2: Create token
        token, created = Token.objects.get_or_create(user=user)
        print(f"Token: {token.key}")
        
        # Step 3: Serialize user
        from authentication.serializers import UserProfileSerializer
        user_serializer = UserProfileSerializer(user)
        user_data = user_serializer.data
        
        # Step 4: Create response
        response_data = {
            'user': user_data,
            'profile': None,  # Admin doesn't have profile
            'token': token.key,
            'message': 'Login successful'
        }
        
        print("Manual login process successful!")
        print(f"Response data keys: {list(response_data.keys())}")
        
    except Exception as e:
        print(f"Exception in manual login: {e}")
        import traceback
        traceback.print_exc()

def test_login_serializer():
    """Test the login serializer directly"""
    print("\n=== Testing Login Serializer ===")
    
    try:
        from authentication.serializers import UserLoginSerializer
        
        data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        serializer = UserLoginSerializer(data=data)
        
        if serializer.is_valid():
            print("Serializer validation successful")
            print(f"Validated data: {serializer.validated_data}")
        else:
            print("Serializer validation failed")
            print(f"Errors: {serializer.errors}")
            
    except Exception as e:
        print(f"Exception in serializer test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("=" * 60)
    print("LOGIN DEBUG TESTS")
    print("=" * 60)
    
    test_login_serializer()
    test_manual_login()
    test_login_via_client()
    
    print("\n" + "=" * 60)
    print("DEBUG TESTS COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    main()
