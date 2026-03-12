from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, FileResponse
from django.contrib.auth import logout as django_logout
import os
import mimetypes

def home(request):
    """Serve the main homepage with role-based routing"""
    # Check if user is authenticated and their role
    if request.user.is_authenticated:
        if request.user.role == 'chef':
            # Show chef dashboard
            return render(request, 'HomeChefs/chef_dashboard.html')
        elif request.user.role == 'admin':
            # Show admin dashboard
            return render(request, 'HomeChefs/admin_dashboard.html')
        # Default to customer homepage for 'customer' role
    
    # Show customer homepage for non-authenticated users or customers
    return render(request, 'HomeChefs/index_mvp.html')

def customer_dashboard(request):
    """Customer dashboard with order functionality"""
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    if request.user.role != 'customer':
        return redirect('/')
    
    # Get pending order from localStorage (handled in frontend)
    return render(request, 'HomeChefs/my_orders.html')

def logout_view(request):
    """Proper logout that clears Django session and redirects to home"""
    if request.user.is_authenticated:
        django_logout(request)
    return redirect('home')

def index_mvp(request):
    """Serve the MVP homepage (alternative URL)"""
    return render(request, 'HomeChefs/index_mvp.html')

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

def search_page(request):
    """Serve the search page with chef search functionality"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'HomeChefs/search.html')
    
    # Search for chefs by username or business name
    from authentication.models import User
    from chefs.models import ChefProfile
    
    chefs = User.objects.filter(
        role='chef',
        username__icontains=query
    ).select_related('chefprofile')
    
    # If only one chef found, redirect to chef profile
    if chefs.count() == 1:
        chef = chefs.first()
        return redirect(f'/chef/?chef_id={chef.id}')
    
    # If multiple chefs found, show search results
    return render(request, 'HomeChefs/search.html', {
        'query': query,
        'chefs': chefs
    })

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

def serve_frontend_file(request, path):
    """Serve static files from frontend directory"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    file_path = os.path.join(frontend_path, path)
    
    # Security check - ensure file is within frontend directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(frontend_path)):
        raise Http404("File not found")
    
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        raise Http404("File not found")
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # Serve the file
    try:
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    except Exception:
        raise Http404("File not found")
