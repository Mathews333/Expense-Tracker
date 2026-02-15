from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_custom_admin(request):
    return redirect('admin-dashboard')

urlpatterns = [
    path('hidden-admin/', admin.site.urls), # The real Django admin
    path('admin-panel/', redirect_to_custom_admin), # Your custom redirect
    
    path('', include('app.urls')), # This handles dashboard, add, etc.
]