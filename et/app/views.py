from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum

from .models import Expense, Category
from .forms import ExpenseForm
from .forms import CategoryForm



@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    category_data = (
        expenses
        .values('category__name')
        .annotate(total=Sum('amount'))
    )

    labels = [item['category__name'] or 'No Category' for item in category_data]
    data = [item['total'] for item in category_data]

    return render(request, 'app/dashboard.html', {
        'expenses': expenses,
        'total': total,
        'labels': labels,
        'data': data,
    })


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()

    return render(request, 'app/add_expense.html', {'form': form})


@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    return redirect('dashboard')


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()
    expenses = Expense.objects.all()
    categories = Category.objects.all()

    return render(request, 'app/admin_dashboard.html', {
        'users': users,
        'expenses': expenses,
        'categories': categories,
    })

@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = CategoryForm()

    return render(request, 'app/add_category.html', {'form': form})
