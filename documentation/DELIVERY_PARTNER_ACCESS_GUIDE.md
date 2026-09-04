# Delivery Partner UI Access Guide

## 🎯 How to Access Delivery Partner Dashboard

### **Quick Access URLs:**
- **Registration**: `http://localhost:8000/delivery/register/`
- **Login**: Use main login page with delivery partner credentials
- **Dashboard**: `http://localhost:8000/delivery/dashboard/`

---

## 📋 Step-by-Step Guide

### Step 1: Register as Delivery Partner (if not registered)
1. **Go to**: `http://localhost:8000/delivery/register/`
2. **Fill Registration Form**:
   - Username, Email, First Name, Last Name
   - Password, Confirm Password
   - Phone Number (with country code)
   - Address
   - Vehicle Type (Bike/Scooter/Car/Bicycle)
   - Vehicle Number, License Number
3. **Submit Registration**
4. **Wait for Verification** (admin will verify your documents)

### Step 2: Login as Delivery Partner
1. **Go to**: `http://localhost:8000/login/`
2. **Enter Credentials**:
   - Username: Your delivery partner username
   - Password: Your delivery partner password
3. **Click Login**

### Step 3: Access Delivery Dashboard
After successful login, delivery partners are automatically redirected to their dashboard.

**Direct Dashboard URL**: `http://localhost:8000/delivery/dashboard/`

---

## 🎛️ Delivery Dashboard Features

### Main Sections:

#### 1. Statistics Cards (Top)
- **Active**: Current deliveries in progress
- **Today**: Completed deliveries today
- **Pending**: Delivery requests waiting response
- **Earnings**: Today's total earnings

#### 2. Availability Toggle
- **Switch**: Toggle your availability ON/OFF
- **OFF**: Won't receive delivery requests
- **ON**: Will receive requests from your service area

#### 3. Pending Delivery Requests
- **Shows**: Active delivery requests in your area
- **Each request displays**:
  - Order ID and meal details
  - Customer information
  - Distance and delivery fee
  - Time remaining to accept/decline

#### 4. Active Deliveries
- **Shows**: Currently accepted deliveries
- **Each delivery displays**:
  - Order status and details
  - Action buttons for status updates

---

## 📱 How to Accept Orders

### Step 1: Check Pending Requests
1. **Dashboard**: Look at "Pending Delivery Requests" section
2. **Review Request**: Check order details, customer info, distance
3. **Time Limit**: Each request has a countdown timer

### Step 2: Accept or Decline
1. **Accept**: Click "Accept" button if you can deliver
2. **Decline**: Click "Decline" if you cannot deliver
3. **Confirmation**: You'll get confirmation of your choice

### Step 3: Manage Active Deliveries
1. **View**: Check "Active Deliveries" section
2. **Update Status**: Use action buttons to update delivery status
3. **Complete**: Mark delivery as completed when finished

---

## 🔧 Troubleshooting

### Issue: "I don't see delivery partner UI"

#### Check 1: Are you registered as delivery partner?
- **Registration URL**: `http://localhost:8000/delivery/register/`
- **If not registered**: Complete registration first

#### Check 2: Are you using correct login?
- **Login URL**: `http://localhost:8000/login/`
- **Use**: Delivery partner credentials (not chef/customer)

#### Check 3: Are you verified?
- **Check Status**: `http://localhost:8000/delivery/verification-status/`
- **Admin Verification**: Required before accessing dashboard

#### Check 4: Direct Dashboard Access
- **Try Direct URL**: `http://localhost:8000/delivery/dashboard/`
- **If redirected**: Check login status

### Issue: "Login says network error but shows logged in after refresh"

#### Solution: Clear Browser Cache
1. **Clear Cache**: Ctrl+Shift+Delete (Chrome) or Ctrl+F5
2. **Try Incognito Mode**: Open login in private window
3. **Check Credentials**: Ensure correct username/password

---

## 📱 Mobile Access

### Responsive Design
- **Mobile Friendly**: Dashboard works on smartphones
- **Touch Buttons**: Large buttons for easy tapping
- **GPS Integration**: Location tracking on mobile

---

## 🎯 Quick Start Summary

### For New Delivery Partners:
1. **Register**: `http://localhost:8000/delivery/register/`
2. **Wait for Verification** (admin approval)
3. **Login**: `http://localhost:8000/login/`
4. **Dashboard**: Automatically redirected to delivery dashboard

### For Existing Delivery Partners:
1. **Login**: `http://localhost:8000/login/`
2. **Dashboard**: `http://localhost:8000/delivery/dashboard/`
3. **Accept Orders**: Check pending requests section

---

## 🔗 Important URLs

| Purpose | URL |
|----------|-------|
| Registration | `/delivery/register/` |
| Login | `/login/` |
| Dashboard | `/delivery/dashboard/` |
| Profile | `/delivery/profile/` |
| Verification Status | `/delivery/verification-status/` |
| API Requests | `/delivery/api/requests/` |
| Accept Request | `/delivery/api/requests/<id>/accept/` |
| Decline Request | `/delivery/api/requests/<id>/decline/` |

---

## 📞 Support

### If Issues Persist:
1. **Check Registration**: Ensure you're registered as delivery partner
2. **Check Login**: Use correct delivery partner credentials
3. **Check Verification**: Admin must verify your account first
4. **Clear Cache**: Browser cache can cause login issues
5. **Try Different Browser**: Chrome, Firefox, Edge

### Expected Workflow:
1. **Register** → **Get Verified** → **Login** → **Access Dashboard** → **Accept Orders** → **Complete Deliveries** → **Earn Money**

The delivery partner UI is fully functional and ready for use!
