from .common import *
__all__ = ['DeliveryPartnerRegistrationView', 'accept_available_order', 'accept_delivery_request', 'available_delivery_orders', 'decline_delivery_request', 'delivery_dashboard', 'delivery_partner_profile', 'delivery_partner_registration_success', 'delivery_partner_verification_status', 'get_delivery_details', 'get_delivery_history', 'get_delivery_requests', 'get_partner_stats', 'rate_delivery', 'toggle_availability', 'update_delivery_status', 'update_location', 'verify_delivery_partner']
from .admin import (verify_delivery_partner)
from .api import (accept_available_order, accept_delivery_request, available_delivery_orders, decline_delivery_request, get_delivery_details, get_delivery_history, get_delivery_requests, get_partner_stats, rate_delivery, toggle_availability, update_delivery_status, update_location)
from .dashboard import (delivery_dashboard)
