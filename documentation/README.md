# HomeChefs - Homemade Food Delivery Platform

A web application similar to Zomato that connects home chefs with customers, built with Django microservices architecture.

## Features

### For Chefs
- Profile management with bio, cuisine specialties, and experience
- Food item management with pricing, availability, and scheduling
- Order management and status updates
- Customer reviews and ratings
- Delivery radius configuration

### For Customers
- Browse and search for chefs and food items
- Place orders with multiple payment options
- Track order status and delivery
- Review chefs and food items
- Manage favorite chefs and food items
- Multiple delivery addresses

### For Admins
- User management and verification
- Order monitoring and management
- Payment processing and refund handling
- Customer support operations
- Analytics and reporting

## Tech Stack

- **Backend**: Django 3.2.25 with Django REST Framework
- **Database**: SQLite (development)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Architecture**: Microservices with separate apps for:
  - Authentication (user management)
  - Chefs (food and chef management)
  - Customers (customer-specific features)
  - Orders (order processing)
  - Payments (payment handling)

## Project Structure

```
HomeChefs_AI/
├── HomeChefs/                 # Main Django project
│   ├── settings.py            # Django settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── authentication/           # User authentication and profiles
│   ├── models.py             # User, ChefProfile, CustomerProfile
│   ├── views.py              # Login, register, profile management
│   ├── serializers.py        # API serializers
│   └── urls.py              # Authentication URLs
├── chefs/                   # Chef and food management
│   ├── models.py             # FoodItem, FoodSchedule, ChefReview
│   ├── views.py              # Chef operations, food management
│   ├── serializers.py        # Chef and food serializers
│   └── urls.py              # Chef URLs
├── customers/               # Customer features
│   ├── models.py             # Favorites, reviews, addresses
│   ├── views.py              # Customer operations, search
│   ├── serializers.py        # Customer serializers
│   └── urls.py              # Customer URLs
├── orders/                  # Order management
│   ├── models.py             # Order, OrderItem, Delivery
│   ├── views.py              # Order processing, tracking
│   ├── serializers.py        # Order serializers
│   └── urls.py              # Order URLs
├── payments/                # Payment processing
│   ├── models.py             # Payment, Wallet, Refund
│   ├── views.py              # Payment processing, wallet management
│   ├── serializers.py        # Payment serializers
│   └── urls.py              # Payment URLs
├── frontend/                # Frontend interface
│   └── index.html           # Main web interface
├── requirements.txt          # Python dependencies
└── manage.py               # Django management script
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HomeChefs_AI
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Frontend: Open `frontend/index.html` in your browser
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET/PUT /api/auth/profile/` - User profile management

### Chefs
- `GET/POST /api/chefs/food-items/` - Chef's food items
- `GET/PUT/DELETE /api/chefs/food-items/<id>/` - Food item details
- `GET /api/chefs/public/` - Public chef listing
- `GET /api/chefs/public/<id>/` - Chef details

### Customers
- `GET/POST /api/customers/favorite-chefs/` - Favorite chefs
- `GET/POST /api/customers/favorite-foods/` - Favorite food items
- `GET/POST /api/customers/reviews/` - Food reviews
- `GET/POST /api/customers/addresses/` - Delivery addresses
- `GET /api/customers/search/chefs/` - Search chefs
- `GET /api/customers/search/food/` - Search food

### Orders
- `GET/POST /api/orders/` - Order management
- `GET/PUT /api/orders/<order_id>/` - Order details
- `GET/PUT /api/orders/<order_id>/delivery/` - Delivery tracking

### Payments
- `GET/POST /api/payments/` - Payment processing
- `GET /api/payments/wallet/` - Wallet management
- `GET/POST /api/payments/refunds/` - Refund requests

## Default Admin Credentials

- **Username**: admin
- **Password**: admin123
- **Email**: admin@homechefs.com

## Usage

1. **For Chefs**:
   - Register as a chef
   - Complete your profile with cuisine specialties
   - Add food items with pricing and availability
   - Manage orders and update status
   - View customer reviews

2. **For Customers**:
   - Register as a customer
   - Browse chefs and food items
   - Place orders with preferred payment method
   - Track order delivery
   - Leave reviews for chefs and food

3. **For Admins**:
   - Access admin panel for user management
   - Monitor orders and payments
   - Process refunds and handle disputes
   - Verify chef profiles

## Features Implemented

✅ User authentication and role-based access
✅ Chef profile and food management
✅ Customer features (favorites, reviews, addresses)
✅ Order processing and tracking
✅ Payment handling with wallet support
✅ Search functionality for chefs and food
✅ Admin interface for operations
✅ Responsive frontend design
✅ RESTful API with Django REST Framework

## Future Enhancements

- Real-time order tracking with WebSocket
- Push notifications for order updates
- Advanced search and filtering
- Image upload for food items
- Delivery partner integration
- Analytics dashboard for chefs
- Mobile app development
- Payment gateway integration (Stripe, Razorpay)
- Email/SMS notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
