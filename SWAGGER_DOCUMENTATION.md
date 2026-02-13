# 📚 HomeChefs API Documentation - Swagger Updates

## Overview
The HomeChefs API documentation has been significantly enhanced with detailed descriptions, examples, and proper payload structures for all endpoints.

## 🔧 Authentication Documentation

### 1. User Registration
**Endpoint**: `POST /api/auth/register/`

**Enhanced Features**:
- ✅ Detailed field descriptions with examples
- ✅ Role-based registration (chef/customer)
- ✅ Validation error examples
- ✅ Complete response structure

**Request Example**:
```json
{
  "username": "john_doe123",
  "email": "john@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer",
  "phone_number": "+1234567890"
}
```

**Response Example**:
```json
{
  "user": {
    "id": 1,
    "username": "john_doe123",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "customer"
  },
  "token": "abc123def456ghi789",
  "message": "Registration successful"
}
```

### 2. User Login
**Endpoint**: `POST /api/auth/login/`

**Enhanced Features**:
- ✅ Clear authentication flow description
- ✅ Token-based authentication details
- ✅ Profile data included in response
- ✅ Error handling examples

**Request Example**:
```json
{
  "username": "customer_anjali",
  "password": "customer123"
}
```

**Response Example**:
```json
{
  "user": {
    "id": 1,
    "username": "customer_anjali",
    "email": "anjali@example.com",
    "first_name": "Anjali",
    "last_name": "Sharma",
    "role": "customer"
  },
  "profile": {
    "id": 1,
    "user": 1,
    "address": "123 Main St, Mumbai",
    "phone_number": "+919876543210"
  },
  "token": "abc123def456ghi789",
  "message": "Login successful"
}
```

## 👨‍🍳 Chef Documentation

### 1. Get Chef Food Items
**Endpoint**: `GET /api/chefs/food-items/`

**Enhanced Features**:
- ✅ Chef-only access clearly documented
- ✅ Complete food item structure
- ✅ Real examples with actual data
- ✅ Permission error handling

**Response Example**:
```json
[
  {
    "id": 1,
    "name": "Butter Chicken",
    "description": "Tender chicken in rich, creamy tomato-based gravy",
    "cuisine_type": "North Indian",
    "meal_type": "dinner",
    "price": "250.00",
    "available_quantity": 5,
    "preparation_time": 45,
    "ingredients": "Chicken, Butter, Cream, Tomatoes, Onions, Garlic, Ginger, Spices",
    "is_vegetarian": false,
    "is_available": true
  }
]
```

### 2. Create Food Item
**Endpoint**: `POST /api/chefs/food-items/`

**Enhanced Features**:
- ✅ Comprehensive field descriptions
- ✅ Required fields clearly marked
- ✅ Example values for all fields
- ✅ Validation error examples

**Request Example**:
```json
{
  "name": "Butter Chicken",
  "description": "Tender chicken in rich, creamy tomato-based gravy with butter and cream",
  "cuisine_type": "North Indian",
  "meal_type": "dinner",
  "price": "250.00",
  "available_quantity": 5,
  "preparation_time": 45,
  "ingredients": "Chicken, Butter, Cream, Tomatoes, Onions, Garlic, Ginger, Spices",
  "is_vegetarian": false,
  "is_available": true
}
```

### 3. Public Chef List
**Endpoint**: `GET /api/chefs/public/`

**Enhanced Features**:
- ✅ Detailed chef information
- ✅ Rating and experience details
- ✅ Delivery radius information
- ✅ Real data examples

**Response Example**:
```json
[
  {
    "id": 2,
    "username": "chef_rahul",
    "first_name": "Rahul",
    "last_name": "Kumar",
    "bio": "Expert in North Indian and Mughlai cuisine with 10 years of experience",
    "cuisine_specialties": "North Indian, Mughlai, Chinese",
    "experience_years": 10,
    "rating": 5.0,
    "delivery_radius": 5,
    "profile_picture": null
  }
]
```

## 🍽️ Customer Documentation

### 1. Food Search
**Endpoint**: `GET /api/customers/search/food/`

**Enhanced Features**:
- ✅ Advanced filtering parameters
- ✅ Search query examples
- ✅ Cuisine and meal type filters
- ✅ Vegetarian filter option
- ✅ Complete food item details

**Query Parameters**:
- `q` - Search query for food name, description, or ingredients
- `cuisine` - Filter by cuisine type
- `meal_type` - Filter by meal type
- `vegetarian` - Filter by vegetarian preference

**Example Requests**:
```
GET /api/customers/search/food/?q=biryani
GET /api/customers/search/food/?cuisine=North%20Indian
GET /api/customers/search/food/?meal_type=dinner&vegetarian=true
```

**Response Example**:
```json
[
  {
    "id": 1,
    "chef": {
      "id": 2,
      "username": "chef_rahul",
      "first_name": "Rahul",
      "last_name": "Kumar"
    },
    "name": "Butter Chicken",
    "description": "Tender chicken in rich, creamy tomato-based gravy with butter and cream",
    "cuisine_type": "North Indian",
    "meal_type": "dinner",
    "price": "250.00",
    "available_quantity": 5,
    "preparation_time": 45,
    "ingredients": "Chicken, Butter, Cream, Tomatoes, Onions, Garlic, Ginger, Spices",
    "is_vegetarian": false,
    "is_available": true
  }
]
```

### 2. Chef Search
**Endpoint**: `GET /api/customers/search/chefs/`

**Enhanced Features**:
- ✅ Search by name, username, or specialties
- ✅ Cuisine filtering
- ✅ Complete chef profiles
- ✅ Rating and experience information

**Query Parameters**:
- `q` - Search query for chef name, username, or cuisine specialties
- `cuisine` - Filter by cuisine type

**Example Requests**:
```
GET /api/customers/search/chefs/?q=rahul
GET /api/customers/search/chefs/?cuisine=North%20Indian
```

**Response Example**:
```json
[
  {
    "id": 2,
    "username": "chef_rahul",
    "first_name": "Rahul",
    "last_name": "Kumar",
    "bio": "Expert in North Indian and Mughlai cuisine with 10 years of experience",
    "cuisine_specialties": "North Indian, Mughlai, Chinese",
    "experience_years": 10,
    "rating": 5.0,
    "delivery_radius": 5,
    "profile_picture": null
  }
]
```

## 🔐 Authentication Headers

For authenticated endpoints, include the following header:
```
Authorization: Token <your_token>
```

**Example**:
```
Authorization: Token abc123def456ghi789
```

## 📊 Error Handling

### Common Error Responses

**400 Bad Request**:
```json
{
  "username": ["This field is required."],
  "password": ["Password must be at least 8 characters."]
}
```

**403 Forbidden**:
```json
{
  "error": "Only chefs can access this endpoint"
}
```

**404 Not Found**:
```json
{
  "detail": "Not found."
}
```

## 🚀 Access Points

### Swagger UI
- **URL**: `http://localhost:8000/swagger/`
- **Features**: Interactive API testing with examples
- **Authentication**: Token-based auth support

### ReDoc
- **URL**: `http://localhost:8000/redoc/`
- **Features**: Clean, readable API documentation

### Frontend
- **URL**: `http://localhost:8000/`
- **Features**: Complete web application

## ✅ Improvements Made

1. **Enhanced Descriptions**: All endpoints now have detailed, user-friendly descriptions
2. **Complete Examples**: Real request/response examples for all endpoints
3. **Parameter Documentation**: Detailed query parameter documentation with examples
4. **Error Examples**: Common error responses with examples
5. **Authentication Flow**: Clear token-based authentication documentation
6. **Role-based Access**: Clear documentation of chef vs customer endpoints
7. **Data Validation**: Field requirements and validation rules documented
8. **Real Data**: Examples use actual data from the application

## 🎯 Usage Tips

1. **Start with Registration**: Create an account using the registration endpoint
2. **Get Token**: Login to receive authentication token
3. **Use Token**: Include token in Authorization header for protected endpoints
4. **Test Public Endpoints**: Food and chef search work without authentication
5. **Check Examples**: Use provided examples as templates for requests
6. **Handle Errors**: Refer to error examples for troubleshooting

The enhanced Swagger documentation now provides a complete, developer-friendly API reference with real examples and clear instructions!
