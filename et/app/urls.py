from django.urls import path
from . import views

urlpatterns = [
    # Give the empty path the name 'index'
    path('', views.dashboard, name='index'), 
    path('add/', views.add_expense, name='add-expense'),
    path('edit/<int:pk>/', views.edit_expense, name='edit-expense'),
    path('delete/<int:pk>/', views.delete_expense, name='delete-expense'),
]