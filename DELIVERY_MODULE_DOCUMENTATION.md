# Delivery Partners Module Documentation

## Overview

The Delivery Partners module provides a complete delivery management system for the HomeChefs platform. It handles delivery partner registration, order notifications, request acceptance, and real-time delivery tracking.

## Features Implemented

### 1. Delivery Partner Registration
- **Registration Form**: Complete registration form with vehicle details, service areas, and verification requirements
- **Profile Management**: Partners can update their profile information and service areas
- **Verification System**: Admin verification process for new delivery partners

### 2. Order Notification System
- **Automatic Notifications**: When an order status changes to 'ready', all available delivery partners in the area are notified
- **Smart Matching**: Partners are matched based on service area and delivery distance
- **Request Expiration**: Delivery requests expire after 5 minutes if not accepted

### 3. Request Acceptance
- **Real-time Requests**: Partners can view and accept delivery requests in real-time
- **Request Details**: Complete order information including pickup and delivery locations
- **One-Click Acceptance**: Simple accept/decline interface for delivery requests

### 4. Delivery Management
- **Status Tracking**: Complete delivery lifecycle (assigned -> picked_up -> in_transit -> delivered)
- **Location Details**: Partners can view chef pickup location and customer delivery details
- **Real-time Updates**: Live status updates throughout the delivery process

### 5. Order Status Integration
- **Enhanced Statuses**: Added delivery-specific order statuses:
  - `out_for_delivery`: Order assigned to delivery partner
  - `picked_up`: Order picked up from chef
  - `in_transit`: Order on the way to customer
  - `delivered`: Order successfully delivered

### 6. Performance Tracking
- **Delivery History**: Complete history of all deliveries
- **Earnings Tracking**: Automatic calculation of partner earnings (80% of delivery fee)
- **Statistics Dashboard**: Performance metrics and completion rates
- **Rating System**: Customer ratings for delivery partners

## Models

### DeliveryPartner
Manages delivery partner profiles and availability
- **Fields**: user, phone_number, vehicle_type, vehicle_number, license_number
- **Location Tracking**: current_latitude, current_longitude, last_location_update
- **Status Management**: status, verification_status, is_available
- **Performance Metrics**: total_deliveries, average_rating, completion_rate
- **Service Area**: service_areas, max_delivery_distance

### DeliveryRequest
Represents delivery requests sent to partners
- **Fields**: order, delivery_partner, status, delivery_fee, distance_km
- **Time Management**: estimated_pickup_time, estimated_delivery_time, expires_at
- **Methods**: accept_request(), decline_request(), is_expired()

### DeliveryAssignment
Active delivery assignments
- **Fields**: order, delivery_partner, status, pickup_address, delivery_address
- **Financial**: delivery_fee, partner_earnings
- **Location Tracking**: pickup/delivery coordinates
- **Methods**: mark_picked_up(), mark_in_transit(), mark_delivered()

### DeliveryRating
Customer ratings for delivery partners
- **Fields**: delivery_assignment, customer, rating, feedback
- **Auto-calculation**: Updates partner's average rating automatically

## API Endpoints

### Registration & Profile
- `POST /delivery/register/` - Register as delivery partner
- `GET /delivery/profile/` - View partner profile
- `POST /delivery/profile/` - Update partner profile

### Dashboard & Notifications
- `GET /delivery/dashboard/` - Delivery partner dashboard
- `GET /delivery/api/requests/` - Get pending delivery requests
- `POST /delivery/api/requests/{id}/accept/` - Accept delivery request
- `POST /delivery/api/requests/{id}/decline/` - Decline delivery request

### Delivery Management
- `GET /delivery/api/delivery/{id}/` - Get delivery details
- `POST /delivery/api/delivery/{id}/status/` - Update delivery status
- `POST /delivery/api/location/` - Update partner location
- `POST /delivery/api/toggle-availability/` - Toggle availability status

### History & Statistics
- `GET /delivery/api/history/` - Get delivery history
- `GET /delivery/api/stats/` - Get partner statistics
- `POST /delivery/api/delivery/{id}/rate/` - Rate delivery (customer endpoint)

## Notification System

### DeliveryNotificationSystem
Core notification management class

**Key Methods:**
- `notify_available_partners(order)` - Notify partners when order is ready
- `check_expired_requests()` - Clean up expired requests
- `auto_reassign_order(order)` - Reassign if no partners accept

**Smart Matching Logic:**
1. Filter partners by verification status and availability
2. Check service area compatibility
3. Calculate delivery distance
4. Sort by distance (closest first)
5. Send requests to top 5 eligible partners

### DeliveryLocationTracker
Real-time location tracking system

**Key Methods:**
- `update_partner_location(partner_id, lat, lng)` - Update partner location
- `send_location_update(delivery, lat, lng)` - Send location to customer

## Frontend Templates

### Dashboard (`delivery/dashboard.html`)
- Real-time delivery requests with countdown timers
- Active deliveries management
- Availability toggle
- Performance statistics
- One-click status updates

### Registration (`delivery/register.html`)
- Comprehensive registration form
- Vehicle information
- Service area configuration
- Terms and conditions

### Profile Management
- Profile update forms
- Verification status display
- Performance metrics

## Integration Points

### Order Status Updates
The module integrates with the orders app through signals:
```python
@receiver(post_save, sender=DailyMealOrder)
def order_status_changed(sender, instance, created, **kwargs):
    if not created and instance.delivery_type == 'delivery':
        if old_instance.order_status != 'ready' and instance.order_status == 'ready':
            DeliveryNotificationSystem.notify_available_partners(instance)
```

### User Model Updates
Added `delivery_partner` role to User model choices.

### Order Status Enhancement
Extended DailyMealOrder.ORDER_STATUS to include delivery stages.

## Admin Interface

### DeliveryPartner Admin
- Bulk actions: verify, activate, deactivate partners
- Performance metrics display
- Status management

### DeliveryRequest Admin
- Request tracking and management
- Expiration monitoring

### DeliveryAssignment Admin
- Complete delivery lifecycle tracking
- Location and timing information

### DeliveryRating Admin
- Rating management
- Partner performance analysis

## Management Commands

### Check Expired Requests
```bash
python manage.py check_delivery_requests
```
Automated command to clean up expired requests and handle reassignments.

## Security Features

### Role-Based Access
- Only verified delivery partners can accept requests
- Customer-only rating endpoints
- Admin verification required for new partners

### Data Validation
- Phone number validation
- Vehicle number uniqueness
- Service area validation

### CSRF Protection
All API endpoints include CSRF protection for web requests.

## Performance Considerations

### Database Optimization
- Efficient querying with select_related
- Indexed fields for fast lookups
- Optimized notification queries

### Real-time Features
- WebSocket-ready architecture for future real-time updates
- Efficient location tracking
- Minimal database queries for dashboard

## Future Enhancements

### Real-time Tracking
- WebSocket integration for live location updates
- Customer-facing tracking interface
- GPS integration for mobile apps

### Advanced Matching
- Machine learning for optimal partner matching
- Traffic-aware routing
- Dynamic pricing based on demand

### Mobile App Support
- Dedicated delivery partner mobile app
- Push notifications for new requests
- Offline mode support

## Testing

### Test Coverage
- Unit tests for all models and methods
- Integration tests for API endpoints
- End-to-end workflow testing

### Test Script
Run comprehensive tests with:
```bash
python test_delivery_module.py
```

## Configuration

### Settings
Add to INSTALLED_APPS:
```python
'delivery',
```

### URLs
Include delivery URLs:
```python
path('delivery/', include('delivery.urls')),
```

### Static Files
Dashboard templates use Bootstrap 5 and Bootstrap Icons.

## Deployment Notes

### Database Migrations
Run migrations after installation:
```bash
python manage.py makemigrations delivery
python manage.py migrate
```

### Cron Jobs
Set up expired request checking:
```bash
*/5 * * * * python manage.py check_delivery_requests
```

### Environment Variables
No additional environment variables required.

## Support

For issues or questions about the delivery module:
1. Check the documentation
2. Run the test script for verification
3. Check admin interface for partner management
4. Review order status integration

---

**Module Status**: Complete and Tested
**Last Updated**: April 22, 2026
**Version**: 1.0.0
