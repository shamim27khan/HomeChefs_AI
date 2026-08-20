from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from .models import DeliveryPartner, DeliveryRequest, DeliveryAssignment
from orders.models import DailyMealOrder
from chefs.models import ChefProfile
import math

class DeliveryNotificationSystem:
    """System to manage delivery notifications and assignments"""
    
    @staticmethod
    def notify_available_partners(order):
        """
        Notify all available delivery partners when food is ready for delivery
        """
        if order.delivery_type != 'delivery' or order.order_status != 'ready':
            return False
        
        # Get chef's location for distance calculation
        try:
            chef_profile = order.daily_meal.chef.chef_profile
            chef_location = chef_profile.kitchen_address
        except:
            return False
        
        # Find available partners
        available_partners = DeliveryPartner.objects.filter(
            status='active',
            is_available=True,
            verification_status='verified'
        )
        
        # Filter partners within service area and distance
        eligible_partners = []
        for partner in available_partners:
            if partner.is_within_service_area(order.delivery_address):
                # Calculate distance (simplified - in production use proper geocoding)
                distance = DeliveryNotificationSystem._calculate_distance(
                    chef_location, order.delivery_address
                )
                
                if distance <= partner.max_delivery_distance:
                    eligible_partners.append((partner, distance))
        
        # Sort by distance (closest first)
        eligible_partners.sort(key=lambda x: x[1])
        
        # Create delivery requests for eligible partners
        requests_created = 0
        for partner, distance in eligible_partners[:5]:  # Limit to 5 closest partners
            delivery_fee = DeliveryNotificationSystem._calculate_delivery_fee(distance)
            
            # Calculate time estimates
            estimated_pickup_time = timezone.now() + timezone.timedelta(minutes=15)
            estimated_delivery_time = estimated_pickup_time + timezone.timedelta(minutes=int(distance * 3))
            
            # Create delivery request
            DeliveryRequest.objects.create(
                order=order,
                delivery_partner=partner,
                estimated_pickup_time=estimated_pickup_time,
                estimated_delivery_time=estimated_delivery_time,
                delivery_fee=delivery_fee,
                distance_km=distance,
                expires_at=timezone.now() + timezone.timedelta(minutes=5)  # 5 minutes to respond
            )
            
            requests_created += 1
        
        return requests_created
    
    @staticmethod
    def _calculate_distance(origin_address, destination_address):
        """
        Calculate distance between two addresses
        This is a simplified calculation - in production, use Google Maps API or similar
        """
        # For now, return a random distance between 1-10 km
        # In production, implement proper geocoding and distance calculation
        import random
        return round(random.uniform(1, 10), 2)
    
    @staticmethod
    def _calculate_delivery_fee(distance_km):
        """Calculate delivery fee based on distance"""
        base_fee = Decimal('20.00')  # Base fee
        per_km_fee = Decimal('5.00')  # Fee per km
        
        total_fee = base_fee + (per_km_fee * Decimal(str(distance_km)))
        
        # Apply minimum and maximum fees
        total_fee = max(total_fee, Decimal('25.00'))  # Minimum fee
        total_fee = min(total_fee, Decimal('100.00'))  # Maximum fee
        
        return total_fee.quantize(Decimal('2'))
    
    @staticmethod
    def check_expired_requests():
        """Check and mark expired delivery requests"""
        expired_requests = DeliveryRequest.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        )
        
        count = expired_requests.count()
        expired_requests.update(status='expired')
        
        return count
    
    @staticmethod
    def auto_reassign_order(order):
        """Automatically reassign order if no partners accepted"""
        # Check if all requests are expired/declined
        active_requests = DeliveryRequest.objects.filter(
            order=order,
            status='pending'
        )
        
        if not active_requests.exists():
            # Check if there are any accepted requests
            accepted_requests = DeliveryRequest.objects.filter(
                order=order,
                status='accepted'
            )
            
            if not accepted_requests.exists():
                # Try to notify partners again
                return DeliveryNotificationSystem.notify_available_partners(order)
        
        return 0
    
    @staticmethod
    def get_partner_notifications(partner):
        """Get all pending notifications for a partner"""
        return DeliveryRequest.objects.filter(
            delivery_partner=partner,
            status='pending',
            expires_at__gt=timezone.now()
        ).order_by('-sent_at')
    
    @staticmethod
    def send_delivery_update_notification(delivery_assignment, status):
        """Send delivery status updates to customer"""
        # This would integrate with push notifications, SMS, or email
        # For now, we'll just log the update
        
        customer = delivery_assignment.order.customer
        order_id = delivery_assignment.order.order_id
        
        messages = {
            'assigned': f"Your order {order_id} has been assigned to a delivery partner",
            'picked_up': f"Your order {order_id} has been picked up and is on the way",
            'in_transit': f"Your order {order_id} is in transit",
            'delivered': f"Your order {order_id} has been delivered",
        }
        
        message = messages.get(status, f"Your order {order_id} status has been updated to {status}")
        
        # In production, send actual notification via:
        # - Push notification (Firebase/OneSignal)
        # - SMS (Twilio)
        # - Email (SendGrid)
        # - WebSocket for real-time updates
        
        return {
            'customer': customer.username,
            'message': message,
            'status': status,
            'timestamp': timezone.now()
        }

class DeliveryLocationTracker:
    """Track real-time location of delivery partners"""
    
    @staticmethod
    def update_partner_location(partner_id, latitude, longitude):
        """Update partner's current location"""
        try:
            partner = DeliveryPartner.objects.get(id=partner_id)
            partner.update_location(latitude, longitude)
            
            # Notify customers about partner location (if in transit)
            active_deliveries = partner.get_active_deliveries()
            for delivery in active_deliveries:
                if delivery.status == 'in_transit':
                    # Send location update to customer
                    DeliveryNotificationSystem.send_location_update(
                        delivery, latitude, longitude
                    )
            
            return True
        except DeliveryPartner.DoesNotExist:
            return False
    
    @staticmethod
    def send_location_update(delivery_assignment, latitude, longitude):
        """Send real-time location update to customer"""
        # This would integrate with real-time tracking systems
        # For now, just return the location data
        
        return {
            'order_id': delivery_assignment.order.order_id,
            'partner_name': delivery_assignment.delivery_partner.user.username,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': timezone.now()
        }
