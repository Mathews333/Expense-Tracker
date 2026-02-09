import csv
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.contrib import messages
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm
from collections import defaultdict

# --- UTILS & PERMISSIONS ---

def is_admin(user):
    return user.is_staff

# --- USER VIEWS ---

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    count = expenses.count()

    # Category Data
    category_data = expenses.values('category__name').annotate(total=Sum('amount'))
    labels = [item['category__name'] or "General" for item in category_data]
    data = [float(item['total']) for item in category_data]

    # Trend Data (Python-based to prevent SQLite TruncDate errors)
    daily_sums = defaultdict(float)
    for exp in expenses:
        if exp.date:
            day_str = exp.date.strftime('%m/%d')
            daily_sums[day_str] += float(exp.amount)
    
    sorted_days = sorted(daily_sums.items())
    date_labels = [d[0] for d in sorted_days]
    date_values = [v[1] for v in sorted_days]

    return render(request, 'app/dashboard.html', {
        'expenses': expenses,
        'total': total,
        'count': count,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'date_labels': json.dumps(date_labels),
        'date_values': json.dumps(date_values),
    })
    
@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect('index') # Redirects to your dashboard
    else:
        form = ExpenseForm()
    return render(request, 'app/add_expense.html', {'form': form})

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated!")
            return redirect('index')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'app/edit_expense.html', {'form': form, 'expense': expense})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    messages.success(request, "Expense deleted successfully!")
    return redirect('index')

@login_required
def export_expenses(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Category', 'Amount', 'Date', 'Description'])
    
    expenses = Expense.objects.filter(user=request.user)
    for e in expenses:
        writer.writerow([e.category.name if e.category else "General", e.amount, e.date, e.description])
    return response

# --- ADMIN VIEWS ---

@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Overview for staff users to see global platform stats.
    """
    users = User.objects.all()
    expenses = Expense.objects.all().order_by('-date')
    
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    category_data = expenses.values('category__name').annotate(total=Sum('amount'))
    
    labels = [item['category__name'] or "General" for item in category_data]
    data = [float(item['total']) for item in category_data]

    return render(request, 'app/admin_dashboard.html', {
        'users': users,
        'expenses': expenses,
        'total_spent': total_spent,
        'total_users': users.count(),
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    })

@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New category added!")
            return redirect('admin-dashboard')
    else:
        form = CategoryForm()
    return render(request, 'app/add_category.html', {'form': form})