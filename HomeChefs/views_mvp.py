from django.shortcuts import render
from django.http import HttpResponse
import os

def home_mvp(request):
    """Serve the MVP homepage for HomeChefHub"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    # Try to serve the MVP homepage first
    mvp_file = os.path.join(frontend_path, 'index_mvp.html')
    if os.path.exists(mvp_file):
        with open(mvp_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    # Fallback to Zomato-style homepage
    zomato_file = os.path.join(frontend_path, 'index_zomato_style.html')
    if os.path.exists(zomato_file):
        with open(zomato_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    # Fallback to original frontend
    original_file = os.path.join(frontend_path, 'index.html')
    if os.path.exists(original_file):
        with open(original_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse("""
    <html>
    <head><title>HomeChefHub</title></head>
    <body>
        <h1>Welcome to HomeChefHub!</h1>
        <p>Homemade food delivery platform</p>
        <ul>
            <li><a href="/frontend/index_mvp.html" target="_blank">MVP Frontend</a></li>
            <li><a href="/frontend/index_zomato_style.html" target="_blank">Zomato Style Frontend</a></li>
            <li><a href="/frontend/test.html" target="_blank">Test Frontend</a></li>
            <li><a href="/swagger/" target="_blank">API Documentation</a></li>
            <li><a href="/admin/" target="_blank">Admin Panel</a></li>
        </ul>
    </body>
    </html>
    """)
