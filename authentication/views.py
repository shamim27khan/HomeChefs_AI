from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from .models import User, ChefProfile, CustomerProfile
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, ChefProfileSerializer, CustomerProfileSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_description="Register a new user for HomeChefs platform. Choose between 'chef' or 'customer' role.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'email', 'password', 'confirm_password', 'role'],
        properties={
            'username': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Unique username for login (3-30 characters)',
                example='john_doe123'
            ),
            'email': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Valid email address for account verification',
                example='john@example.com'
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Password (minimum 8 characters, must contain letters and numbers)',
                example='password123'
            ),
            'confirm_password': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Re-enter password for confirmation',
                example='password123'
            ),
            'first_name': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='First name (optional)',
                example='John'
            ),
            'last_name': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Last name (optional)',
                example='Doe'
            ),
            'role': openapi.Schema(
                type=openapi.TYPE_STRING, 
                enum=['chef', 'customer'], 
                description='User role: chef (can sell food) or customer (can buy food)',
                example='customer'
            ),
            'phone_number': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Phone number for delivery and communication (optional)',
                example='+1234567890'
            ),
        }
    ),
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
    operation_description="Login to HomeChefs platform using username and password. Returns authentication token for API access.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Your registered username',
                example='customer_anjali'
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Your account password',
                example='customer123'
            ),
        }
    ),
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
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
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
    operation_description="Get user profile information",
    responses={200: openapi.Response('Profile data'), 401: openapi.Response('Unauthorized')}
)
@swagger_auto_schema(
    method='put',
    operation_description="Update user profile information",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user': openapi.Schema(type=openapi.TYPE_OBJECT, description='User data'),
            'profile': openapi.Schema(type=openapi.TYPE_OBJECT, description='Role-specific profile data'),
        }
    ),
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
