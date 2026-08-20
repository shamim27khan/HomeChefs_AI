from .common import *
from .common import _chef_dashboard_context

def home(request):
    """Serve the main homepage with role-based routing"""
    # Check if user is authenticated and their role
    if request.user.is_authenticated:
        if request.user.role == 'chef':
            # Show chef dashboard
            return render(request, 'HomeChefs/chef_dashboard.html', _chef_dashboard_context(request, request.user))
        elif request.user.role == 'admin':
            # Show admin dashboard
            return render(request, 'HomeChefs/admin_dashboard.html')
        elif request.user.role == 'delivery_partner':
            # Show delivery partner dashboard
            return redirect('/delivery/dashboard/')
        else:
            # Customer dashboard
            return redirect('/customer-dashboard/')
    
    # Show customer homepage for non-authenticated users
    return render(request, 'HomeChefs/customer_dashboard.html')


def chef_dashboard(request):
    """Chef dashboard with meal management functionality"""
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.user.role != 'chef':
        return redirect('/')
    return render(request, 'HomeChefs/chef_dashboard.html', _chef_dashboard_context(request, request.user))


def customer_dashboard(request):
    """Customer dashboard with order functionality"""
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    if request.user.role != 'customer':
        return redirect('/')
    
    # Get pending order from localStorage (handled in frontend)
    return render(request, 'HomeChefs/customer_dashboard.html')


def logout_view(request):
    """Proper logout that clears Django session, token, and redirects to login page"""
    if request.user.is_authenticated:
        # Delete the authentication token if it exists
        try:
            from rest_framework.authtoken.models import Token
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass
        
        # Clear Django session
        django_logout(request)
    
    return redirect('/login/')


def index_mvp(request):
    """Serve the MVP homepage (alternative URL)"""
    return render(request, 'HomeChefs/customer_dashboard.html')


def register_page(request):
    """Serve the registration page"""
    return render(request, 'HomeChefs/register.html')


def login_page(request):
    """Serve the login page"""
    return render(request, 'HomeChefs/login.html')


def admin_dashboard(request):
    """Admin dashboard with chef verification functionality"""
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    if request.user.role != 'admin':
        return redirect('/')
    
    return render(request, 'HomeChefs/admin_dashboard.html')


def index_zomato_style(request):
    """Serve the Zomato-style homepage"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    zomato_file = os.path.join(frontend_path, 'index_zomato_style.html')
    
    if os.path.exists(zomato_file):
        with open(zomato_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse("Zomato-style page not found", status=404)


def test_page(request):
    """Serve the test frontend page"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    test_file = os.path.join(frontend_path, 'test.html')
    
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse("Test page not found", status=404)


def chef_detail(request):
    """Serve the chef detail page"""
    # Always use Django template for consistency
    return render(request, 'HomeChefs/chef.html')


def cart_page(request):
    """Serve the cart page"""
    # Always use Django template for consistency
    return render(request, 'HomeChefs/cart.html')


def order_meal(request, meal_id):
    """Serve the meal ordering page"""
    # Always use Django template for consistency
    return render(request, 'HomeChefs/order_meal.html', {'meal_id': meal_id})


def checkout(request):
    """Serve the checkout page"""
    # Always use Django template for consistency
    return render(request, 'HomeChefs/checkout.html')


def my_orders(request):
    """Serve the my orders page"""
    # Always use Django template for consistency
    return render(request, 'HomeChefs/my_orders.html')


def track_order(request, order_id):
    """Serve the track order page"""
    # Always use Django template for consistency
    return render(request, 'HomeChefs/track_order.html', {'order_id': order_id})


def order_confirmation(request, order_id):
    """Serve the order confirmation page"""
    # Always use Django template for consistency
    return render(request, 'HomeChefs/order_confirmation.html', {'order_id': order_id})
