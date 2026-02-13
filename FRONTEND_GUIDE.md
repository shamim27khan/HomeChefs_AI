# HomeChefs Frontend Guide

## 🚀 Quick Access URLs

### **Frontend Applications**
- **Main App**: `http://localhost:8000/`
- **Test Page**: `http://localhost:8000/test/`

### **API Documentation**
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`

### **Admin Panel**
- **Admin**: `http://localhost:8000/admin/`

### **API Endpoints**
- **Chefs**: `http://localhost:8000/api/chefs/public/`
- **Food**: `http://localhost:8000/api/customers/search/food/`
- **Auth**: `http://localhost:8000/api/auth/login/`

## 🚀 Quick Start

### 1. Start the Backend Server
```bash
cd C:\Users\shami\IdeaProjects\HomeChefs_AI
python manage.py runserver 0.0.0.0:8000
```

The server should be running on: `http://localhost:8000`

### 2. Access the Frontend

#### **Main Frontend (Improved Version)**
- **URL**: `http://localhost:8000/`
- **Features**: Full application with improved UI/UX
- **Access**: Open directly in browser

#### **Test Frontend**
- **URL**: `http://localhost:8000/test/`
- **Features**: API testing interface
- **Access**: Open directly in browser

#### **Static HTML Files (Alternative)**
- **Improved**: Open `frontend/index_improved.html` directly in browser
- **Test**: Open `frontend/test.html` directly in browser
- **Original**: Open `frontend/index.html` directly in browser

## 🔐 Login Credentials

### **Admin Access**
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Admin

### **Chef Accounts**
- **Username**: `chef_rahul`
- **Password**: `chef123`
- **Role**: Chef

- **Username**: `chef_priya`
- **Password**: `chef123`
- **Role**: Chef

- **Username**: `chef_amit`
- **Password**: `chef123`
- **Role**: Chef

### **Customer Accounts**
- **Username**: `customer_anjali`
- **Password**: `customer123`
- **Role**: Customer

- **Username**: `customer_raj`
- **Password**: `customer123`
- **Role**: Customer

## 📚 API Documentation

### **Swagger UI**
- **URL**: `http://localhost:8000/swagger/`
- **Features**: Interactive API testing
- **Usage**: Try API endpoints directly from browser

### **ReDoc**
- **URL**: `http://localhost:8000/redoc/`
- **Features**: Clean API documentation
- **Usage**: Readable API reference

### **Admin Panel**
- **URL**: `http://localhost:8000/admin/`
- **Features**: Database management
- **Login**: Use admin credentials

## 🛠️ Frontend Features

### **Authentication**
- ✅ User registration
- ✅ Login/Logout
- ✅ Role-based access
- ✅ Profile management

### **Customer Features**
- ✅ Browse chefs
- ✅ Search food items
- ✅ View food details
- ✅ Place orders (mock)
- ✅ Add to favorites (mock)

### **Chef Features**
- ✅ View chef profiles
- ✅ Browse food items
- ✅ Rating system
- ✅ Experience display

### **UI/UX Improvements**
- ✅ Responsive design
- ✅ Loading indicators
- ✅ Error messages
- ✅ Success notifications
- ✅ Smooth transitions

## 🔧 Troubleshooting

### **CORS Issues**
If you see CORS errors in the browser console:
1. Make sure the Django server is running
2. Check the CORS settings in `HomeChefs/settings.py`
3. Try using the improved frontend version

### **API Not Responding**
1. Check if Django server is running: `http://localhost:8000`
2. Test API endpoints: `http://localhost:8000/api/chefs/public/`
3. Check server logs for errors

### **Login Issues**
1. Verify credentials are correct
2. Check if user exists in database
3. Try creating a new user via registration

### **Frontend Not Loading**
1. Open browser developer tools (F12)
2. Check console for JavaScript errors
3. Verify API calls are being made
4. Check network tab for failed requests

## 📱 Mobile Access

The frontend is fully responsive and works on:
- ✅ Desktop browsers
- ✅ Tablets
- ✅ Mobile phones

## 🎯 Next Steps

### **For Development**
1. Add real order functionality
2. Implement payment processing
3. Add real-time notifications
4. Create mobile app

### **For Testing**
1. Test all user flows
2. Verify API endpoints
3. Check error handling
4. Test responsive design

## 📞 Support

If you encounter issues:
1. Check the Django server logs
2. Use the test frontend for debugging
3. Verify API documentation
4. Check browser console for errors

## 🎉 Success Indicators

You know everything is working when:
- ✅ Django server runs without errors
- ✅ Frontend loads chefs and food items
- ✅ Login/Registration works
- ✅ API documentation is accessible
- ✅ Admin panel is functional

---

**Happy Cooking! 🍳👨‍🍳👩‍🍳**
