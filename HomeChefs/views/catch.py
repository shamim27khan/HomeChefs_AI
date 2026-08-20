from .common import *

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
