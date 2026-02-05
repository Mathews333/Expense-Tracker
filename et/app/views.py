from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm

def is_admin(user):
    return user.is_staff

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    category_data = expenses.values('category__name').annotate(total=Sum('amount'))
    labels = [item['category__name'] or 'No Category' for item in category_data]
    data = [item['total'] for item in category_data]
    return render(request, 'app/dashboard.html', {
        'expenses': expenses, 'total': total, 'labels': labels, 'data': data,
    })

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()
    expenses = Expense.objects.all().order_by('-date')
    categories = Category.objects.all()
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'app/admin_dashboard.html', {
        'users': users, 'expenses': expenses, 'categories': categories,
        'total_spent': total_spent, 'total_users': users.count(),
    })

@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin-dashboard')
    else:
        form = CategoryForm()
    return render(request, 'app/add_category.html', {'form': form})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('index')
    return render(request, 'app/add_expense.html', {'form': ExpenseForm()})

@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    return redirect('index')

from django.shortcuts import redirect

def redirect_to_custom_admin(request):
    return redirect('admin-dashboard')

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()
    expenses = Expense.objects.all()
    categories = Category.objects.all()
    
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Chart Data: Grouping total spending by category name
    category_data = expenses.values('category__name').annotate(total=Sum('amount'))
    
    # Prepare lists for the chart
    labels = [item['category__name'] if item['category__name'] else "Uncategorized" for item in category_data]
    data = [float(item['total']) for item in category_data] # Convert Decimal to float for JS

    return render(request, 'app/admin_dashboard.html', {
        'users': users,
        'expenses': expenses,
        'categories': categories,
        'total_spent': total_spent,
        'total_users': users.count(),
        'labels': labels,
        'data': data,
    })
    
    from django.shortcuts import render
from django.db.models import Sum
from .models import Expense, Category

@login_required
def dashboard(request):
    # Get current user's expenses
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    # Calculate spending by category for the Chart
    category_data = expenses.values('category__name').annotate(total=Sum('amount'))
    
    # Prepare lists for the Pie Chart
    labels = [item['category__name'] if item['category__name'] else "General" for item in category_data]
    data = [float(item['total']) for item in category_data]
    
    total_spend = sum(data)

    return render(request, 'app/dashboard.html', {
        'expenses': expenses,
        'total': total_spend,
        'labels': labels,
        'data': data,
    })

@user_passes_test(is_admin)
def admin_dashboard(request):
    expenses = Expense.objects.all().order_by('-date')
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_users = User.objects.count()
    
    return render(request, 'app/admin_dashboard.html', {
        'expenses': expenses,
        'total_spent': total_spent,
        'total_users': total_users,
    })
    
from django.db.models.functions import TruncDate

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    # 1. Pie Chart Data (Categories)
    category_data = expenses.values('category__name').annotate(total=Sum('amount'))
    labels = [item['category__name'] or "General" for item in category_data]
    data = [float(item['total']) for item in category_data]

    # 2. Line Chart Data (Daily Trend - last 7 entries)
    trend_data = expenses.values('date').annotate(total=Sum('amount')).order_by('date')[:7]
    date_labels = [item['date'].strftime('%m/%d') for item in trend_data]
    date_values = [float(item['total']) for item in trend_data]

    return render(request, 'app/dashboard.html', {
        'expenses': expenses,
        'total': sum(data),
        'labels': labels,
        'data': data,
        'date_labels': date_labels,
        'date_values': date_values,
    })