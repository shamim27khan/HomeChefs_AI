from django.utils.deprecation import MiddlewareMixin

class CSRFExemptMiddleware(MiddlewareMixin):
    """
    Middleware to exempt API endpoints from CSRF protection
    """
    def process_request(self, request):
        # Exempt all API endpoints from CSRF protection
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
            print(f"CSRF exempted for: {request.path}")  # Debug line
        return None
