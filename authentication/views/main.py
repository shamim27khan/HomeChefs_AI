from .common import *

@swagger_auto_schema(
    method='post',
    tags=['Authentication'],
    operation_description="Register a new user for HomeChefs platform. Choose between 'chef' or 'customer' role.",
    request_body=UserRegistrationSerializer,
    responses={
        201: openapi.Response(
            description='Registration successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'role': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            examples={
                'application/json': {
                    'user': {
                        'id': 1,
                        'username': 'john_doe123',
                        'email': 'john@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'role': 'customer'
                    },
                    'token': 'abc123def456ghi789',
                    'message': 'Registration successful'
                }
            }
        ), 
        400: openapi.Response(
            description='Bad request - validation errors',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            ),
            examples={
                'application/json': {
                    'username': ['This field is required.'],
                    'password': ['Password must be at least 8 characters.']
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    tags=['Authentication'],
    operation_description="Login to HomeChefs platform using username and password. Returns authentication token for API access.",
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            description='Login successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'role': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                    'profile': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'user': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'address': openapi.Schema(type=openapi.TYPE_STRING),
                            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            examples={
                'application/json': {
                    'user': {
                        'id': 1,
                        'username': 'customer_anjali',
                        'email': 'anjali@example.com',
                        'first_name': 'Anjali',
                        'last_name': 'Sharma',
                        'role': 'customer'
                    },
                    'profile': {
                        'id': 1,
                        'user': 1,
                        'address': '123 Main St, Mumbai',
                        'phone_number': '+919876543210'
                    },
                    'token': 'abc123def456ghi789',
                    'message': 'Login successful'
                }
            }
        ), 
        400: openapi.Response(
            description='Invalid credentials',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'non_field_errors': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING)
                    )
                }
            ),
            examples={
                'application/json': {
                    'non_field_errors': ['Unable to log in with provided credentials.']
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    """Handle user login with either username/password or phone/OTP"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        phone_number = serializer.validated_data.get('phone_number')
        otp_code = serializer.validated_data.get('otp_code')
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        
        if phone_number and otp_code:
            # OTP-based login
            try:
                # Verify OTP first
                is_valid, message = PhoneOTP.verify_otp(phone_number, otp_code)
                
                if not is_valid:
                    return Response({
                        'message': message,
                        'error': 'invalid_otp'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get user by phone number
                try:
                    user = User.objects.get(phone_number=phone_number)
                    if not user.is_active:
                        return Response({
                            'message': 'User account is disabled',
                            'error': 'account_disabled'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Login the user
                    login(request, user)
                    
                    # Get or create token
                    token, created = Token.objects.get_or_create(user=user)
                    
                    return Response({
                        'user': UserProfileSerializer(user).data,
                        'token': token.key,
                        'message': 'Login successful'
                    }, status=status.HTTP_200_OK)
                    
                except User.DoesNotExist:
                    return Response({
                        'message': 'No account found with this phone number',
                        'error': 'user_not_found'
                    }, status=status.HTTP_400_BAD_REQUEST)
                except User.MultipleObjectsReturned:
                    return Response({
                        'message': 'Multiple accounts found with this phone number. Please contact support.',
                        'error': 'multiple_users'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'message': f'Error during OTP login: {str(e)}',
                    'error': 'server_error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif username and password:
            # Username/password login (case-insensitive)
            user = User.objects.filter(username__iexact=username).first()
            if not user or not user.check_password(password):
                return Response({
                    'message': 'Invalid credentials',
                    'error': 'invalid_credentials'
                }, status=status.HTTP_400_BAD_REQUEST)
            if not user.is_active:
                return Response({
                    'message': 'User account is disabled',
                    'error': 'account_disabled'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'message': 'Invalid login method',
                'error': 'invalid_method'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Common login logic for both methods
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        
        # Get profile data based on role
        profile_data = None
        if user.role == 'chef':
            try:
                chef_profile = user.chef_profile
                profile_data = ChefProfileSerializer(chef_profile).data
            except ChefProfile.DoesNotExist:
                ChefProfile.objects.create(user=user)
                chef_profile = user.chef_profile
                profile_data = ChefProfileSerializer(chef_profile).data
        elif user.role == 'customer':
            try:
                customer_profile = user.customer_profile
                profile_data = CustomerProfileSerializer(customer_profile).data
            except CustomerProfile.DoesNotExist:
                CustomerProfile.objects.create(user=user)
                customer_profile = user.customer_profile
                profile_data = CustomerProfileSerializer(customer_profile).data
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'profile': profile_data,
            'token': token.key,
            'message': 'Login successful'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    tags=['Authentication'],
    operation_description="Logout from HomeChefs platform. Invalidates the authentication token.",
    responses={
        200: openapi.Response(
            description='Logout successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            examples={
                'application/json': {
                    'message': 'Logout successful'
                }
            }
        ),
        401: openapi.Response(
            description='Unauthorized - Authentication required',
            examples={
                'application/json': {
                    'detail': 'Authentication credentials were not provided.'
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def user_logout(request):
    try:
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'Logout successful'})
    except:
        return Response({'message': 'Logout successful'})


@swagger_auto_schema(
    method='get',
    tags=['Authentication'],
    operation_description="Get user profile information",
    responses={200: openapi.Response('Profile data'), 401: openapi.Response('Unauthorized')}
)
@swagger_auto_schema(
    method='put',
    tags=['Authentication'],
    operation_description="Update user profile information",
    request_body=UserProfileSerializer,
    responses={200: openapi.Response('Profile updated'), 400: openapi.Response('Bad request'), 401: openapi.Response('Unauthorized')}
)
@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    user = request.user
    
    if request.method == 'GET':
        profile_data = None
        if user.role == 'chef':
            try:
                chef_profile = user.chef_profile
                profile_data = ChefProfileSerializer(chef_profile).data
            except ChefProfile.DoesNotExist:
                ChefProfile.objects.create(user=user)
                chef_profile = user.chef_profile
                profile_data = ChefProfileSerializer(chef_profile).data
        elif user.role == 'customer':
            try:
                customer_profile = user.customer_profile
                profile_data = CustomerProfileSerializer(customer_profile).data
            except CustomerProfile.DoesNotExist:
                CustomerProfile.objects.create(user=user)
                customer_profile = user.customer_profile
                profile_data = CustomerProfileSerializer(customer_profile).data
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'profile': profile_data
        })
    
    elif request.method == 'PUT':
        # Update user profile
        user_serializer = UserProfileSerializer(user, data=request.data.get('user', {}), partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        
        # Update role-specific profile
        if user.role == 'chef':
            try:
                chef_profile = user.chef_profile
                chef_serializer = ChefProfileSerializer(chef_profile, data=request.data.get('profile', {}), partial=True)
                if chef_serializer.is_valid():
                    chef_serializer.save()
            except ChefProfile.DoesNotExist:
                ChefProfile.objects.create(user=user)
        
        elif user.role == 'customer':
            try:
                customer_profile = user.customer_profile
                customer_serializer = CustomerProfileSerializer(customer_profile, data=request.data.get('profile', {}), partial=True)
                if customer_serializer.is_valid():
                    customer_serializer.save()
            except CustomerProfile.DoesNotExist:
                CustomerProfile.objects.create(user=user)
        
        return Response({'message': 'Profile updated successfully'})
    
    return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='post',
    tags=['Authentication'],
    operation_description="Request OTP for phone number verification.",
    request_body=OTPRequestSerializer
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_otp(request):
    """Send OTP to phone number for verification"""
    serializer = OTPRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        
        # Generate OTP
        otp = PhoneOTP.generate_otp(phone_number)
        
        # For development, return the OTP in response
        # In production, you would send this via SMS service
        return Response({
            'message': 'OTP sent successfully',
            'otp_code': otp.otp_code,  # Remove this in production
            'expires_at': otp.expires_at
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='post',
    tags=['Authentication'],
    operation_description="Verify OTP code for phone number verification.",
    request_body=OTPVerifySerializer
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    """Verify OTP for phone number"""
    serializer = OTPVerifySerializer(data=request.data)
    
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            # Verify OTP
            is_valid, message = PhoneOTP.verify_otp(phone_number, otp_code)
            
            if is_valid:
                # Mark phone as verified for user if exists
                try:
                    user = User.objects.get(phone_number=phone_number)
                    user.is_phone_verified = True
                    user.save()
                except User.DoesNotExist:
                    pass  # User doesn't exist yet, that's okay
                except User.MultipleObjectsReturned:
                    # Multiple users found with same phone number - data integrity issue
                    return Response({
                        'message': 'Phone number verification failed: Multiple accounts found with this phone number. Please contact support.',
                        'is_verified': False,
                        'error_code': 'MULTIPLE_USERS'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({
                    'message': message,
                    'is_verified': True
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': message,
                    'is_verified': False
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': f'Error during verification: {str(e)}',
                'is_verified': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)