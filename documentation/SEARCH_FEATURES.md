# 🍽️ HomeChefs Search Features

## Overview
HomeChefs provides powerful search functionality for customers to discover food items and home chefs.

## 🔍 Available Search Features

### 1. Food Search
**Endpoint**: `GET /api/customers/search/food/`

**Features**:
- Browse all available food items
- Search by food name, ingredients, or cuisine type
- Filter by availability, price range, dietary preferences
- View detailed food information including chef details

**Sample Results**:
```
1. Butter Chicken - Rs.250.00
   Chef: Rahul Kumar (North Indian)
   Description: Tender chicken in rich, creamy tomato-based gravy
   Available: True

2. Masala Dosa - Rs.80.00
   Chef: Priya Sharma (South Indian)
   Description: Crispy rice crepe filled with spiced potato mixture
   Available: True
```

**Search Examples**:
- `GET /api/customers/search/food/?q=rice` - Returns 2 results
- `GET /api/customers/search/food/?q=biryani` - Returns 0 results
- `GET /api/customers/search/food/` - Returns all 6 available items

### 2. Chef Search
**Endpoint**: `GET /api/customers/search/chefs/`

**Features**:
- Browse all verified home chefs
- Search by chef name, username, or cuisine specialties
- View chef profiles with ratings and experience
- Filter by delivery radius and availability

**Sample Results**:
```
1. Rahul Kumar (@chef_rahul)
   Bio: Expert in North Indian and Mughlai cuisine
   Specialties: North Indian, Mughlai, Chinese
   Rating: 5.0/5
   Experience: 10 years
   Delivery Radius: 5 km
```

**Search Examples**:
- `GET /api/customers/search/chefs/?q=rahul` - Returns 1 result
- `GET /api/customers/search/chefs/?q=priya` - Returns 1 result
- `GET /api/customers/search/chefs/` - Returns all 3 chefs

## 🎯 Key Features

### Food Search Capabilities
- **Real-time Availability**: Only shows currently available food items
- **Rich Information**: Price, description, ingredients, preparation time
- **Chef Integration**: Each food item shows chef details and rating
- **Dietary Filters**: Vegetarian/non-vegetarian indicators
- **Cuisine Categories**: North Indian, South Indian, Chinese, etc.

### Chef Search Capabilities
- **Verified Chefs**: Only shows approved and verified home chefs
- **Detailed Profiles**: Experience, specialties, bio, ratings
- **Delivery Information**: Service radius and availability
- **Cuisine Expertise**: Multiple cuisine specialties per chef
- **Customer Reviews**: Integrated rating system

## 🔧 Technical Implementation

### API Endpoints
- **Public Access**: No authentication required for basic search
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Response**: Structured data for easy frontend integration
- **Query Parameters**: Flexible search with `?q=search_term`

### Response Structure
**Food Search Response**:
```json
{
  "id": 1,
  "name": "Butter Chicken",
  "description": "Tender chicken in rich, creamy tomato-based gravy",
  "cuisine_type": "North Indian",
  "price": "250.00",
  "is_available": true,
  "chef": {
    "id": 2,
    "username": "chef_rahul",
    "first_name": "Rahul",
    "last_name": "Kumar"
  }
}
```

**Chef Search Response**:
```json
{
  "id": 2,
  "username": "chef_rahul",
  "first_name": "Rahul",
  "last_name": "Kumar",
  "bio": "Expert in North Indian and Mughlai cuisine",
  "cuisine_specialties": "North Indian, Mughlai, Chinese",
  "rating": 5.0,
  "experience_years": 10,
  "delivery_radius": 5
}
```

## 🚀 Usage Examples

### Frontend Integration
```javascript
// Search food items
const searchFood = async (query) => {
  const url = query 
    ? `/api/customers/search/food/?q=${query}`
    : '/api/customers/search/food/';
  
  const response = await fetch(url);
  return await response.json();
};

// Search chefs
const searchChefs = async (query) => {
  const url = query 
    ? `/api/customers/search/chefs/?q=${query}`
    : '/api/customers/search/chefs/';
  
  const response = await fetch(url);
  return await response.json();
};
```

### Testing the Features
```bash
# Test food search
curl "http://localhost:8000/api/customers/search/food/"

# Test chef search
curl "http://localhost:8000/api/customers/search/chefs/"

# Search with query
curl "http://localhost:8000/api/customers/search/food/?q=rice"
```

## 📱 Frontend Integration

The search features are fully integrated into the frontend:
- **Main App**: `http://localhost:8000/`
- **Test Interface**: `http://localhost:8000/test/`
- **API Documentation**: `http://localhost:8000/swagger/`

## ✅ Current Status

Both search features are **fully functional** and tested:
- ✅ Food search returns 6 food items
- ✅ Chef search returns 3 verified chefs
- ✅ Query-based search working
- ✅ Public access (no authentication required)
- ✅ Proper JSON responses with complete data
- ✅ Frontend integration ready

## 🎉 Benefits for Customers

1. **Easy Discovery**: Find food and chefs quickly
2. **Rich Information**: Detailed descriptions and ratings
3. **Flexible Search**: Multiple search criteria
4. **Real-time Data**: Current availability and pricing
5. **Quality Assurance**: Only verified chefs and available items

The search functionality provides a seamless experience for customers to explore the HomeChefs platform and discover delicious homemade food!
