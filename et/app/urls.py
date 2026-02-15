from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 1. THE DASHBOARDS
    path('', views.home, name='home'),

    path('dashboard/', views.dashboard, name='index'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),

    # 2. THE LOGIN SYSTEM
    # Standard User Login
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # Staff/Admin Login
    # path('staff/login/', views.AdminLoginView.as_view(), name='staff-login'),
    
    # The 'Traffic Controller' that decides where to send you after login
    path('login-success/', views.login_success, name='login-success'),
    
    # Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 3. EXPENSE ACTIONS
    path('add/', views.add_expense, name='add-expense'),
    path('edit/<int:pk>/', views.edit_expense, name='edit-expense'),
    path('delete/<int:pk>/', views.delete_expense, name='delete-expense'),
    
    # 4. CATEGORY ACTIONS (Admin only)
    path('category/add/', views.add_category, name='add-category'),
    
    path('register/', views.register, name='register'),

]