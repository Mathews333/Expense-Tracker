import csv
import json
from django.core.paginator import Paginator
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login

from .models import Expense, Category, MonthlyBudget
from .forms import ExpenseForm, CategoryForm, RegisterForm
from django.core.paginator import Paginator



# --------------------------------
# UTILS
# --------------------------------

def is_admin(user):
    return user.is_staff


# --------------------------------
# DASHBOARD
# --------------------------------

@login_required
def dashboard(request):
    selected_year = request.GET.get('year')
    selected_year = int(selected_year) if selected_year else date.today().year

    expenses = Expense.objects.filter(
        user=request.user,
        date__year=selected_year
    )

    # -------------------------------
    # MONTHLY BUDGET
    # -------------------------------
    today = date.today()

    current_month_expenses = expenses.filter(
        date__month=today.month,
        type='expense'
    )

    monthly_spent = current_month_expenses.aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    budget_obj = MonthlyBudget.objects.filter(
        user=request.user,
        year=today.year,
        month=today.month
    ).first()

    budget_amount = budget_obj.amount if budget_obj else 0
    remaining_budget = budget_amount - monthly_spent
    budget_percentage = (
        (monthly_spent / budget_amount * 100)
        if budget_amount > 0 else 0
    )

    # -------------------------------
    # Income / Expense Totals
    # -------------------------------
    income_total = expenses.filter(type='income').aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    expense_total = expenses.filter(type='expense').aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    profit = income_total - expense_total
    savings_rate = (profit / income_total * 100) if income_total > 0 else 0

    # -------------------------------
    # Category Chart
    # -------------------------------
    category_data = (
        expenses.filter(type='expense')
        .values('category__name')
        .annotate(total=Sum('amount'))
    )

    labels = [item['category__name'] or "General" for item in category_data]
    data = [float(item['total']) for item in category_data]

    # -------------------------------
    # Monthly Income vs Expense Chart
    # -------------------------------
    monthly_data = (
        expenses
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(
            income=Sum('amount', filter=Q(type='income')),
            expense=Sum('amount', filter=Q(type='expense')),
        )
        .order_by('month')
    )

    monthly_labels = []
    monthly_income = []
    monthly_expense = []

    for item in monthly_data:
        monthly_labels.append(item['month'].strftime('%b'))
        monthly_income.append(float(item['income'] or 0))
        monthly_expense.append(float(item['expense'] or 0))

    # -------------------------------
    # Pagination
    # -------------------------------
    expenses = expenses.order_by('-date')
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'app/dashboard.html', {
        'income_total': income_total,
        'expense_total': expense_total,
        'profit': profit,
        'savings_rate': round(savings_rate, 2),

        'budget_amount': budget_amount,
        'monthly_spent': monthly_spent,
        'remaining_budget': remaining_budget,
        'budget_percentage': round(budget_percentage, 2),

        'labels': json.dumps(labels),
        'data': json.dumps(data),

        'monthly_labels': json.dumps(monthly_labels),
        'monthly_income': json.dumps(monthly_income),
        'monthly_expense': json.dumps(monthly_expense),

        'selected_year': selected_year,
        'page_obj': page_obj,
    })



# --------------------------------
# EXPENSE CRUD
# --------------------------------

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect('index')
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

    return render(request, 'app/edit_expense.html', {
        'form': form,
        'expense': expense
    })


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully!")
        return redirect('index')

    return redirect('index')



@login_required
def export_expenses(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Category', 'Amount', 'Date', 'Description'])

    expenses = Expense.objects.filter(user=request.user)

    for e in expenses:
        writer.writerow([
            e.category.name if e.category else "General",
            e.amount,
            e.date,
            e.description
        ])

    return response


# --------------------------------
# ADMIN
# --------------------------------

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()
    expenses = Expense.objects.all().order_by('-date')

    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent = round(total_spent, 2)


    return render(request, 'app/admin_dashboard.html', {
        'users': users,
        'expenses': expenses,
        'total_spent': total_spent,
        'total_users': users.count(),
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


# --------------------------------
# AUTH
# --------------------------------

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin-dashboard')
        return redirect('index')
    return redirect('login')


@login_required
def login_success(request):
    return redirect('index')


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})
