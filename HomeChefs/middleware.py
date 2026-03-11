from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import status
import time

class CSRFExemptMiddleware(MiddlewareMixin):
    """
    Middleware to exempt API endpoints from CSRF protection
    """
    def process_request(self, request):
        # Exempt all API endpoints from CSRF protection
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rate limit API endpoints
        if request.path.startswith('/api/'):
            client_ip = self.get_client_ip(request)
            cache_key = f"rate_limit_{client_ip}"
            
            # Get current count
            count = cache.get(cache_key, 0)
            
            # Allow 100 requests per minute
            if count > 100:
                return HttpResponse(
                    '{"error": "Rate limit exceeded. Please try again later."}',
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                    content_type='application/json'
                )
            
            # Increment counter
            cache.set(cache_key, count + 1, 60)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
