from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Function to kick people from /admin/ to your custom dashboard
def redirect_to_custom_admin(request):
    return redirect('admin-dashboard')

urlpatterns = [
    # 1. The Trap: Anyone going to /admin/ gets sent to your custom page
    path('admin/', redirect_to_custom_admin), 
    
    # 2. The Real Admin: Moved to a secret path so it doesn't conflict
    path('hidden-admin/', admin.site.urls), 
    
    # 3. Your App
    path('', include('app.urls')), 
    path('accounts/', include('django.contrib.auth.urls')),
]