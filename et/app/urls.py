from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('add/', views.add_expense, name='add-expense'),
    path('delete/<int:id>/', views.delete_expense, name='delete-expense'),
    path('my-custom-admin/', views.admin_dashboard, name='admin-dashboard'),
    path('my-custom-admin/add-category/', views.add_category, name='add-category'),
]