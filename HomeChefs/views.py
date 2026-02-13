from django.shortcuts import render
from django.http import HttpResponse
import os

def home(request):
    """Serve the main frontend page"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    # Try to serve the improved frontend first
    improved_file = os.path.join(frontend_path, 'index_zomato_style.html')
    if os.path.exists(improved_file):
        with open(improved_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    # Fallback to original frontend
    original_file = os.path.join(frontend_path, 'index.html')
    if os.path.exists(original_file):
        with open(original_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse("""
    <html>
    <head><title>HomeChefs</title></head>
    <body>
        <h1>Welcome to HomeChefs!</h1>
        <p>Please open the frontend files directly:</p>
        <ul>
            <li><a href="/frontend/index_improved.html" target="_blank">Improved Frontend</a></li>
            <li><a href="/frontend/test.html" target="_blank">Test Frontend</a></li>
            <li><a href="/swagger/" target="_blank">API Documentation</a></li>
            <li><a href="/admin/" target="_blank">Admin Panel</a></li>
        </ul>
    </body>
    </html>
    """)

def test_page(request):
    """Serve the test frontend page"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    test_file = os.path.join(frontend_path, 'test.html')
    
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse("Test page not found", status=404)

def search_page(request):
    """Serve the search page"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    search_file = os.path.join(frontend_path, 'search.html')
    
    if os.path.exists(search_file):
        with open(search_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse("Search page not found", status=404)

def chef_detail(request):
    """Serve the chef detail page"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    chef_file = os.path.join(frontend_path, 'chef.html')
    
    if os.path.exists(chef_file):
        with open(chef_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse("Chef page not found", status=404)

def cart_page(request):
    """Serve the cart page"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    cart_file = os.path.join(frontend_path, 'cart.html')
    
    if os.path.exists(cart_file):
        with open(cart_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse("Cart page not found", status=404)
