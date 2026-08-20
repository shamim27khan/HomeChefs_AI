# Admin Dashboard Troubleshooting Guide

## Issue: Admin Dashboard Not Loading Completely

### Symptoms
- Admin page loads partially
- Some sections missing
- JavaScript errors
- CSS not loading properly
- Infinite loading spinner

### Root Causes & Solutions

## 1. Static Files Issue

### Problem
Static files (CSS, JS) not being served properly.

### Solution
```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear static files cache
python manage.py collectstatic --clear --noinput

# Check static files settings
```

### Check Settings
Ensure these are in `settings.py`:
```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
```

## 2. Database Connection Issues

### Problem
Database queries timing out or failing.

### Solution
```bash
# Check database connection
python manage.py dbshell

# Run migrations
python manage.py migrate

# Check for database locks
python manage.py check --database default
```

## 3. Admin Configuration Issues

### Problem
Admin models not properly configured.

### Solution
We've already fixed the admin.py file with proper methods:
- Custom display methods for relationships
- Proper queryset optimization
- Safe field access with null checks

## 4. Template Loading Issues

### Problem
Admin templates not loading properly.

### Solution
```bash
# Check template settings
python manage.py check --templates

# Clear template cache
# Delete __pycache__ folders
find . -name "__pycache__" -type d -exec rm -rf {} +
```

## 5. Memory/Performance Issues

### Problem
Too much data loading causing memory issues.

### Solution
Add pagination to admin models:
```python
# In admin.py
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_per_page = 25  # Add this
    show_full_result_count = False  # Add this for performance
```

## 6. JavaScript Errors

### Problem
JavaScript conflicts or errors.

### Solution
Check browser console for errors:
1. Open admin in browser
2. Press F12 (Developer Tools)
3. Check Console tab for errors
4. Check Network tab for failed requests

## Quick Fix Steps

### Step 1: Restart Server
```bash
# Stop current server (Ctrl+C)
# Start fresh
python manage.py runserver
```

### Step 2: Clear Caches
```bash
# Clear Django cache
python manage.py clear_cache

# Clear browser cache
# Press Ctrl+Shift+R (hard refresh)
```

### Step 3: Check Admin URLs
```bash
python manage.py show_urls | grep admin
```

### Step 4: Test Individual Admin Pages
Try these URLs individually:
- http://127.0.0.1:8000/admin/
- http://127.0.0.1:8000/admin/delivery/deliverypartner/
- http://127.0.0.1:8000/admin/delivery/deliveryrequest/
- http://127.0.0.1:8000/admin/delivery/deliveryassignment/
- http://127.0.0.1:8000/admin/delivery/deliveryrating/

## Advanced Troubleshooting

### 1. Enable Debug Mode
```python
# In settings.py
DEBUG = True
```

### 2. Check Admin Logs
```bash
# Check Django logs
tail -f logs/django.log

# Or check server output for errors
```

### 3. Test with Different Browser
Try accessing admin in:
- Chrome
- Firefox
- Edge
- Incognito mode

### 4. Check System Resources
```bash
# Check memory usage
python manage.py shell
import psutil
print(f"Memory: {psutil.virtual_memory().percent}%")
```

## Specific Delivery Module Admin Issues

### Fixed Issues:
1. **Relationship Display**: Added custom methods to safely display related objects
2. **Query Optimization**: Added select_related to reduce database queries
3. **Null Safety**: Added null checks for all relationship fields

### Current Admin Configuration:
```python
# DeliveryPartnerAdmin - Safe and optimized
# DeliveryRequestAdmin - Custom display methods
# DeliveryAssignmentAdmin - Optimized queries
# DeliveryRatingAdmin - Safe relationship access
```

## Testing Admin Functionality

### Run Admin Tests:
```bash
python test_admin_simple.py
```

### Expected Output:
```
Testing Admin Registration...
DeliveryPartner Admin: OK
DeliveryRequest Admin: OK
DeliveryAssignment Admin: OK
DeliveryRating Admin: OK

Testing Admin URLs...
admin:index -> /admin/
admin:delivery_deliverypartner_changelist -> /admin/delivery/deliverypartner/

Testing Data Integrity...
Delivery Partners: 2
Delivery Requests: 0
Delivery Assignments: 1
Delivery Ratings: 0
```

## If Issues Persist

### 1. Create Superuser
```bash
python manage.py createsuperuser
```

### 2. Test with Minimal Admin
```python
# Temporarily simplify admin.py
@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'phone_number', 'status']
    list_filter = ['status', 'verification_status']
```

### 3. Check Dependencies
```bash
pip install --upgrade django
pip install --upgrade djangorestframework
```

### 4. Database Check
```bash
python manage.py check
python manage.py check --deploy
```

## Contact Support

If none of these solutions work:
1. Check browser console for specific errors
2. Run `python manage.py check` for system issues
3. Check server logs for error messages
4. Provide error details when asking for help

---

## Quick Recovery Commands

```bash
# Complete reset sequence
python manage.py collectstatic --clear --noinput
python manage.py migrate
python manage.py check
python manage.py runserver
```

This should resolve most admin dashboard loading issues.
