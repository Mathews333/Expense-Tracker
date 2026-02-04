from django.urls import path
from .views import dashboard, add_expense, delete_expense, admin_dashboard, add_category

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('add/', add_expense, name='add_expense'),
    path('delete/<int:id>/', delete_expense, name='delete_expense'),
     path('adminpage/', admin_dashboard, name='admin_dashboard'),
     path('adminpage/add-category/', add_category, name='add_category'),

]
